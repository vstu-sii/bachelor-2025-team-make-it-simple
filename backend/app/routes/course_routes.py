from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import date

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
from app.models.material import Material
from app.models.course_topic import CourseTopic
from app.models.course_material import CourseMaterial
from app.models.user_course import UserCourse
from app.models.user import User

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
    
    # Связываем материалы с курсом
    if course_data.materials_ids:
        for material_id in course_data.materials_ids:
            # Проверяем, что материал существует
            material = db.query(Material).filter(Material.material_id == material_id).first()
            if not material:
                continue  # Пропускаем несуществующие материалы
            
            course_material = CourseMaterial(
                course_id=new_course.course_id,
                material_id=material_id
            )
            db.add(course_material)
    
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
    print(f"   Материалов: {len(course_data.materials_ids) if course_data.materials_ids else 0}")
    
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
            # Парсим JSON графа
            if isinstance(user_course.graph_json, str):
                graph_data = json.loads(user_course.graph_json)
            else:
                graph_data = user_course.graph_json
            
            # Только если у узлов нет статусов, устанавливаем по умолчанию
            if "nodes" in graph_data:
                for node in graph_data["nodes"]:
                    if "group" not in node:
                        # Проверяем, есть ли lesson_id у узла
                        lesson_id = node.get("data", {}).get("lesson_id")
                        if lesson_id:
                            node["group"] = 2  # Доступен
                        else:
                            node["group"] = 3  # Недоступен
            
            # Убедимся, что поле 'type' установлено для всех узлов (нужно для Vue Flow)
            if "nodes" in graph_data:
                for node in graph_data["nodes"]:
                    if "type" not in node:
                        node["type"] = "custom"
            
            return {"graph_data": graph_data}
        else:
            # Если графа нет, возвращаем пустой
            return {"graph_data": {"nodes": [], "edges": []}}
            
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
        student_course.graph_json = json.dumps(graph_data)
        db.commit()
        db.refresh(student_course)
        
        return {"message": "Граф успешно обновлен", "graph_data": graph_data}
        
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

@router.get("/{course_id}/materials")
async def get_course_materials(
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
        
        # Получаем материалы курса
        materials = db.query(Material).join(
            CourseMaterial, Material.material_id == CourseMaterial.material_id
        ).filter(
            CourseMaterial.course_id == course_id
        ).all()
        
        return {"materials": materials}
        
    except Exception as e:
        print(f"Error getting course materials: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении материалов курса")

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