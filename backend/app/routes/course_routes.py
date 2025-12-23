from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import date, datetime

from app.database import get_db
from app.repositories.course_repository import CourseRepository
from app.schemas.course import (
    CourseCreate, 
    CourseResponse, 
    TutorCourseResponse,
    StudentCourseResponse,
    CourseWithRelationsCreate
)
from app.utils.jwt import get_current_user
from app.models.course import Course
from app.models.topic import Topic
from app.models.course_topic import CourseTopic
from app.models.user_course import UserCourse
from app.models.user import User

from app.ml.main import generate_course_graph

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role == "Ученик":
        raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать все курсы")
    
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.get("/tutors/{tutor_id}/courses", response_model=List[TutorCourseResponse])
def get_tutor_courses(
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем, что текущий пользователь имеет доступ
    if current_user.user_id != tutor_id and current_user.role != "Администратор":
        raise HTTPException(status_code=403, detail="Нет доступа к этим курсам")
    
    courses = CourseRepository.get_courses_by_tutor(db, tutor_id)
    return courses

@router.get("/students/{student_id}/course", response_model=StudentCourseResponse)
def get_student_course(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить курс ученика
    """
    # Проверяем, что текущий пользователь имеет доступ
    if current_user.user_id != student_id and current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Нет доступа к этому курсу")
    
    course = CourseRepository.get_course_by_student(db, student_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    return course

@router.get("/tutors/{tutor_id}/courses/search", response_model=List[TutorCourseResponse])
def search_tutor_courses(
    tutor_id: int,
    query: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Поиск курсов репетитора по имени ученика
    """
    # Проверяем, что текущий пользователь имеет доступ
    if current_user.user_id != tutor_id and current_user.role != "Администратор":
        raise HTTPException(status_code=403, detail="Нет доступа к этим курсам")
    
    courses = CourseRepository.search_student_courses(db, tutor_id, query)
    return courses

@router.post("/", response_model=CourseResponse)
def create_course(
    course_data: CourseWithRelationsCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию и роль
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут создавать курсы")
    
    # Проверяем, что название не пустое
    if not course_data.title or not course_data.title.strip():
        raise HTTPException(status_code=400, detail="Название курса не может быть пустым")
    
    # Проверяем, что переданы темы
    if not course_data.topics_ids or len(course_data.topics_ids) == 0:
        raise HTTPException(status_code=400, detail="Курс должен содержать хотя бы одну тему")
    
    # Создаем новый курс
    new_course = Course(
        title=course_data.title.strip(),
        created_at=date.today(),
        link_to_vector_db=course_data.link_to_vector_db or f"/static/vector_dbs/course_{int(date.today().strftime('%Y%m%d'))}_{current_user.user_id}",
        input_test_json=course_data.input_test_json or {}
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    # Связываем темы с курсом
    for topic_id in course_data.topics_ids:
        # Проверяем, что тема существует
        topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
        if not topic:
            continue  # Пропускаем несуществующие темы
        
        course_topic = CourseTopic(
            course_id=new_course.course_id,
            topic_id=topic_id
        )
        db.add(course_topic)
    
    # Связываем репетитора с курсом
    user_course = UserCourse(
        user_id=current_user.user_id,
        course_id=new_course.course_id,
        knowledge_gaps=None,
        graph_json={},
        output_test_json={}
    )
    db.add(user_course)
    
    db.commit()
    
    print(f"✅ Создан курс: ID={new_course.course_id}, Title={new_course.title}")
    print(f"   Тем: {len(course_data.topics_ids)}")
    
    return new_course

@router.post("/tutors/{tutor_id}/courses", response_model=CourseResponse)
def create_tutor_course(
    tutor_id: int,
    course_data: CourseCreate,
    student_id: Optional[int] = None,  # Можно передать student_id в query параметрах
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем, что текущий пользователь имеет доступ
    if current_user.user_id != tutor_id:
        raise HTTPException(status_code=403, detail="Нельзя создавать курсы для другого репетитора")
    
    # Проверяем, что пользователь является репетитором
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=400, detail="Только репетиторы могут создавать курсы")
    
    # Если указан student_id, проверяем что он существует и является учеником
    if student_id:
        student = db.query(User).filter(User.user_id == student_id).first()
        if not student or student.role != "Ученик":
            raise HTTPException(status_code=400, detail="Указанный ученик не найден")
    
    # Создаем курс
    course = CourseRepository.create_course_with_tutor_and_student(
        db, tutor_id, student_id, course_data.dict()
    )
    
    return course

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем, что у пользователя есть доступ к курсу
    user_course = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.user_id,
        UserCourse.course_id == course_id
    ).first()
    
    if not user_course:
        raise HTTPException(status_code=403, detail="Нет доступа к этому курсу")
    
    return course

@router.get("/{course_id}/student/{student_id}/graph")
async def get_student_course_graph(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем доступ пользователя
        if current_user.user_id != student_id and current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Нет доступа к этому графу")
        
        # Ищем запись в user_course для конкретного ученика и курса
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not user_course:
            raise HTTPException(status_code=404, detail="Курс не найден для данного пользователя")
        
        # Если граф есть в базе данных
        if user_course.graph_json:
            graph_dict = json.loads(user_course.graph_json)
            
            # Добавляем флаг финализации в ответ
            graph_data = {
                **graph_dict,
                "is_finalized": graph_dict.get("is_finalized", False)
            }
            
            return {"graph_data": graph_data, "is_finalized": graph_dict.get("is_finalized", False)}
        else:
            return {
                "graph_data": {"nodes": [], "edges": []},
                "is_finalized": False
            }
            
    except Exception as e:
        print(f"Error getting student course graph: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении графа курса")

@router.put("/{course_id}/student/{student_id}/graph")
async def update_student_course_graph(
    course_id: int,
    student_id: int,
    graph_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут изменять графы")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Обновляем граф
        student_course.graph_json = json.dumps({
            **graph_data,
            "is_finalized": graph_data.get("is_finalized", False),
            "last_updated": datetime.now().isoformat(),
            "updated_by": current_user.user_id
        })
        db.commit()
        db.refresh(student_course)
        
        return {
            "message": "Граф успешно обновлен", 
            "graph_data": json.loads(student_course.graph_json),
            "is_finalized": graph_data.get("is_finalized", False)
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error updating student course graph: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении графа")

@router.get("/{course_id}/students")
async def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать список учеников")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Получаем всех учеников на курсе
        students = db.query(User).join(
            UserCourse, User.user_id == UserCourse.user_id
        ).filter(
            UserCourse.course_id == course_id,
            User.role == "Ученик"
        ).all()
        
        # Формируем ответ
        student_list = []
        for student in students:
            student_course = db.query(UserCourse).filter(
                UserCourse.user_id == student.user_id,
                UserCourse.course_id == course_id
            ).first()
            
            student_list.append({
                "student_id": student.user_id,
                "student_name": f"{student.last_name} {student.first_name}",
                "email": student.email,
                "knowledge_gaps": student_course.knowledge_gaps if student_course else ""
            })
        
        return {"students": student_list}
        
    except Exception as e:
        print(f"Error getting course students: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении списка учеников")

@router.put("/{course_id}/student/{student_id}/knowledge-gaps")
async def update_student_knowledge_gaps(
    course_id: int,
    student_id: int,
    knowledge_gaps_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять пробелы в знаниях")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Обновляем пробелы в знаниях
        if "knowledge_gaps" in knowledge_gaps_data:
            student_course.knowledge_gaps = knowledge_gaps_data["knowledge_gaps"]
            db.commit()
            db.refresh(student_course)
        
        return {"message": "Пробелы в знаниях успешно обновлены"}
        
    except Exception as e:
        db.rollback()
        print(f"Error updating student knowledge gaps: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении пробелов в знаниях")

@router.get("/{course_id}/topics")
async def get_course_topics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем доступ к курсу
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not user_course:
            raise HTTPException(status_code=403, detail="Нет доступа к этому курсу")
        
        # Получаем темы курса
        topics = db.query(Topic).join(
            CourseTopic, Topic.topic_id == CourseTopic.topic_id
        ).filter(
            CourseTopic.course_id == course_id
        ).all()
        
        return {"topics": topics}
        
    except Exception as e:
        print(f"Error getting course topics: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении тем курса")

@router.post("/{course_id}/add-student", status_code=201)
async def add_student_to_course(
    course_id: int,
    student_data: Dict[str, str],  # {"email": "student@example.com"}
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Проверяем, что текущий пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут добавлять учеников в курсы")
        
        email = student_data.get("email", "").strip()
        if not email:
            raise HTTPException(status_code=400, detail="Email ученика не указан")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Ищем ученика по email
        student = db.query(User).filter(
            User.email == email,
            User.role == "Ученик"
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Ученик с указанным email не найден")
        
        # Проверяем, что ученик уже не записан на какой-либо курс
        existing_user_course = db.query(UserCourse).filter(
            UserCourse.user_id == student.user_id
        ).first()
        
        if existing_user_course:
            raise HTTPException(status_code=400, detail="Ученик уже записан на другой курс")
        
        # Проверяем, что ученик уже не записан на этот курс (на всякий случай)
        already_enrolled = db.query(UserCourse).filter(
            UserCourse.user_id == student.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if already_enrolled:
            raise HTTPException(status_code=400, detail="Ученик уже записан на этот курс")
        
        # Добавляем ученика в курс
        new_user_course = UserCourse(
            user_id=student.user_id,
            course_id=course_id,
            knowledge_gaps="",
            graph_json=json.dumps({}),
            output_test_json=json.dumps({})
        )
        
        db.add(new_user_course)
        db.commit()
        db.refresh(new_user_course)
        
        return {
            "message": "Ученик успешно добавлен в курс",
            "student": {
                "student_id": student.user_id,
                "student_name": f"{student.last_name} {student.first_name}",
                "email": student.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error adding student to course: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при добавлении ученика в курс")
    
@router.delete("/{course_id}/students/{student_id}")
async def remove_student_from_course(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Удалить ученика из курса
    """
    try:
        # Проверяем, что текущий пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут удалять учеников из курсов")
        
        # Проверяем существование курса
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Проверяем существование ученика
        student = db.query(User).filter(
            User.user_id == student_id,
            User.role == "Ученик"
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Ученик не найден")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Удаляем запись из user_course
        db.delete(student_course)
        db.commit()
        
        return {
            "message": "Ученик успешно удален из курса",
            "student": {
                "student_id": student.user_id,
                "student_name": f"{student.last_name} {student.first_name}",
                "email": student.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error removing student from course: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при удалении ученика из курса")
    

@router.post("/{course_id}/student/{student_id}/generate-graph")
async def generate_student_course_graph(
    course_id: int,
    student_id: int,
    graph_request: Dict[str, Any] = Body(...),  # {"feedback": "текст замечаний"}
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Генерация/обновление графа курса для ученика с учетом замечаний репетитора
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут генерировать графы")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Получаем данные ученика
        student = db.query(User).filter(User.user_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Ученик не найден")
        
        # Получаем данные курса
        course = db.query(Course).filter(Course.course_id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        # Получаем темы курса
        course_topics = db.query(Topic).join(
            CourseTopic, Topic.topic_id == CourseTopic.topic_id
        ).filter(
            CourseTopic.course_id == course_id
        ).all()
        
        # Подготавливаем данные для AI
        ai_student_data = {
            "student_profile": {
                "interests": student.interests.split(",") if student.interests else [],
                "knowledge_gaps": student_course.knowledge_gaps.split(",") if student_course.knowledge_gaps else []
            },
            "course_title": course.title,
            "topics": [topic.title for topic in course_topics]
        }
        
        feedback = graph_request.get("feedback", "")
        
        print(f"\n=== ГЕНЕРАЦИЯ ГРАФА ДЛЯ УЧЕНИКА ===")
        print(f"  course_id: {course_id}")
        print(f"  student_id: {student_id}")
        print(f"  feedback: {feedback}")
        print(f"  Данные для AI: {ai_student_data}")
        
        # Генерируем граф с помощью AI
        try:
            generated_graph = generate_course_graph(
                student_data=ai_student_data,
                feedback=feedback
            )
        except Exception as ai_error:
            print(f"  Ошибка AI при генерации графа: {ai_error}")
            # Используем демо-граф в случае ошибки
            generated_graph = create_demo_graph()
        
        # Устанавливаем группы для узлов
        if generated_graph.get("nodes"):
            for i, node in enumerate(generated_graph["nodes"]):
                # Проверяем, существует ли уже связанный урок
                lesson_id = node.get("data", {}).get("lesson_id")
                lesson_data = None
                
                if lesson_id:
                    # Получаем данные урока из базы
                    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
                    if lesson:
                        lesson_data = {
                            "is_access": lesson.is_access,
                            "is_ended": lesson.is_ended
                        }
                
                # Если это первая вершина (i == 0)
                if i == 0:
                    # Для первой вершины:
                    # - Репетитор всегда видит ее желтой (group=2)
                    # - Ученик видит ее серой (group=3) если урок закрыт
                    # - Но у узла есть специальный флаг is_first_lesson
                    node["is_first_lesson"] = True
                    
                    if lesson_data and lesson_data["is_access"]:
                        # Если урок уже открыт - для ученика желтый
                        node["group"] = 2
                        node["is_access_for_student"] = True
                    else:
                        # По умолчанию урок закрыт для ученика
                        node["group"] = 3  # Серая для ученика
                        node["is_access_for_student"] = False
                    
                    # Добавляем информацию о доступе
                    node["tutor_access"] = True  # Репетитор всегда имеет доступ
                    
                else:
                    # Для остальных вершин
                    if lesson_data and lesson_data["is_access"]:
                        node["group"] = 2  # Желтый если открыт
                        node["is_access_for_student"] = True
                    else:
                        node["group"] = 3  # Серый если закрыт
                        node["is_access_for_student"] = False
        
        print(f"  Сгенерировано узлов: {len(generated_graph.get('nodes', []))}")
        print(f"  Сгенерировано связей: {len(generated_graph.get('edges', []))}")
        
        # Добавляем метаданные в граф
        graph_with_metadata = {
            **generated_graph,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generated_by": current_user.user_id,
                "feedback_used": feedback,
                "is_finalized": False,  # Граф еще не сохранен окончательно
                "version": f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
        
        return {
            "message": "Граф успешно сгенерирован",
            "graph_data": graph_with_metadata,
            "preview": {
                "nodes_count": len(generated_graph.get("nodes", [])),
                "edges_count": len(generated_graph.get("edges", [])),
                "first_node_access": generated_graph.get("nodes", [{}])[0].get("is_access_for_student", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating course graph: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при генерации графа")

@router.post("/{course_id}/student/{student_id}/save-graph")
async def save_final_graph(
    course_id: int,
    student_id: int,
    graph_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сохранить граф курса как окончательный
    После этого кнопки генерации и обновления исчезают
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут сохранять графы")
        
        # Проверяем, что репетитор ведет этот курс
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Проверяем, что граф содержит данные
        if not graph_data.get("nodes") or len(graph_data.get("nodes", [])) == 0:
            raise HTTPException(status_code=400, detail="Граф не может быть пустым")
        
        # Помечаем граф как окончательный
        graph_data["metadata"] = {
            **graph_data.get("metadata", {}),
            "is_finalized": True,
            "finalized_at": datetime.now().isoformat(),
            "finalized_by": current_user.user_id,
            "saved_at": datetime.now().isoformat()
        }
        
        # Сохраняем граф в базу
        student_course.graph_json = json.dumps(graph_data)
        db.commit()
        
        print(f"Граф сохранен как окончательный для ученика {student_id}")
        print(f"Узлов: {len(graph_data.get('nodes', []))}")
        print(f"Связей: {len(graph_data.get('edges', []))}")
        
        return {
            "message": "Граф курса успешно сохранен как окончательный",
            "is_finalized": True,
            "nodes_count": len(graph_data.get("nodes", [])),
            "edges_count": len(graph_data.get("edges", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error saving final graph: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении графа")

def create_demo_graph():
    """Создание демо-графа при ошибке AI"""
    return {
        "nodes": [
            {"id": "1", "label": "Present Simple", "data": {"lesson_id": 1}, "position": {"x": 200, "y": 150}},
            {"id": "2", "label": "Past Simple", "data": {"lesson_id": 2}, "position": {"x": 400, "y": 150}},
            {"id": "3", "label": "Future Tenses", "data": {"lesson_id": 3}, "position": {"x": 200, "y": 350}},
            {"id": "4", "label": "Articles", "data": {"lesson_id": 4}, "position": {"x": 400, "y": 350}},
            {"id": "5", "label": "Basic Vocabulary", "data": {"lesson_id": 5}, "position": {"x": 300, "y": 500}}
        ],
        "edges": [
            {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
            {"id": "e1-3", "source": "1", "target": "3", "label": "Alternative"},
            {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
            {"id": "e3-5", "source": "3", "target": "5", "label": "Next"},
            {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
        ]
    }

@router.put("/{course_id}/student/{student_id}/graph/node/{node_id}")
async def update_graph_node_access(
    course_id: int,
    student_id: int,
    node_id: str,
    access_data: Dict[str, bool] = Body(...),  # {"is_access": true/false}
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Обновить состояние доступа для конкретного узла в графе
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять доступ")
        
        # Находим запись ученика на курсе
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на этом курсе")
        
        # Получаем текущий граф
        if not student_course.graph_json:
            raise HTTPException(status_code=404, detail="Граф не найден")
        
        graph_data = json.loads(student_course.graph_json)
        nodes = graph_data.get("nodes", [])
        
        # Находим нужный узел
        node_to_update = None
        for node in nodes:
            if str(node.get("id")) == node_id:
                node_to_update = node
                break
        
        if not node_to_update:
            raise HTTPException(status_code=404, detail="Узел не найден в графе")
        
        # Обновляем состояние доступа
        is_access = access_data.get("is_access", False)
        
        if is_access:
            node_to_update["group"] = 2  # Желтый - доступен
            node_to_update["is_access_for_student"] = True
        else:
            node_to_update["group"] = 3  # Серый - недоступен
            node_to_update["is_access_for_student"] = False
        
        # Если это первый узел, также обновляем урок в базе данных
        if node_to_update.get("is_first_lesson") and node_to_update.get("data", {}).get("lesson_id"):
            lesson_id = node_to_update["data"]["lesson_id"]
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            if lesson:
                lesson.is_access = is_access
                db.commit()
        
        # Сохраняем обновленный граф
        student_course.graph_json = json.dumps(graph_data)
        db.commit()
        
        return {
            "message": f"Доступ к узлу обновлен: {'открыт' if is_access else 'закрыт'}",
            "node_id": node_id,
            "is_access": is_access,
            "group": node_to_update["group"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating graph node access: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обновлении доступа")