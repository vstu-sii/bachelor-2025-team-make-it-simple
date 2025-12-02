from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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