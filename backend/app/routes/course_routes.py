from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from app.database import get_db
from app.repositories.course_repository import CourseRepository
from app.schemas.course import (
    CourseCreate, 
    CourseResponse, 
    TutorCourseResponse,
    StudentCourseResponse
)
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/tutors/{tutor_id}/courses", response_model=List[TutorCourseResponse])
def get_tutor_courses(
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить все курсы репетитора
    """
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

@router.post("/tutors/{tutor_id}/courses", response_model=CourseResponse)
def create_tutor_course(
    tutor_id: int,
    course_data: CourseCreate,
    student_id: int = None,  # Можно передать student_id в query параметрах
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Создать новый курс для репетитора
    """
    # Проверяем, что текущий пользователь имеет доступ
    if current_user.user_id != tutor_id:
        raise HTTPException(status_code=403, detail="Нельзя создавать курсы для другого репетитора")
    
    # Проверяем, что пользователь является репетитором
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=400, detail="Только репетиторы могут создавать курсы")
    
    # Если указан student_id, проверяем что он существует и является учеником
    if student_id:
        from app.models.user import User
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
    """
    Получить информацию о курсе по ID
    """
    from app.models.course import Course
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    
    # Проверяем, что у пользователя есть доступ к курсу
    from app.models.user_course import UserCourse
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
    """
    Получить индивидуальный граф курса для ученика
    """
    try:
        # Проверяем доступ пользователя
        if current_user.user_id != student_id and current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Нет доступа к этому графу")
        
        # Ищем запись в user_course для конкретного ученика и курса
        from app.models.user_course import UserCourse
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
            
            # ВАЖНО: НЕ перезаписываем статусы узлов случайными значениями!
            # Вместо этого используем статусы из БД, которые уже установлены в fill_db.py
            
            # Только если у узлов нет статусов, устанавливаем по умолчанию
            if "nodes" in graph_data:
                for node in graph_data["nodes"]:
                    # Если у узла нет поля 'group', устанавливаем по умолчанию
                    # group=2 (желтый, доступен) для обычных узлов
                    # group=3 (серый, недоступен) для узлов без lesson_id
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
    """
    Обновить граф курса для ученика (для репетитора)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут изменять графы")
        
        # Проверяем, что репетитор ведет этот курс
        from app.models.user_course import UserCourse
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
    """
    Получить список всех учеников на курсе (для репетитора)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать список учеников")
        
        # Проверяем, что репетитор ведет этот курс
        from app.models.user_course import UserCourse
        tutor_course = db.query(UserCourse).filter(
            UserCourse.user_id == current_user.user_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not tutor_course:
            raise HTTPException(status_code=403, detail="Вы не ведете этот курс")
        
        # Получаем всех учеников на курсе
        from app.models.user import User
        from app.models.user_course import UserCourse
        
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
    """
    Обновить пробелы в знаниях ученика (для репетитора)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять пробелы в знаниях")
        
        # Находим запись ученика на курсе
        from app.models.user_course import UserCourse
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