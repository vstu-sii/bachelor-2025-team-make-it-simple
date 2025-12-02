from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, UserWithCourseResponse

from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = UserRepository.get_by_email(db, data.email)
    if existing:
        raise HTTPException(400, "Пользователь с такой почтой уже существует")

    user_data = data.model_dump()
    user_data["password"] = hash_password(user_data["password"])

    user = UserRepository.create(db, user_data)
    return user


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Неверный логин или пароль")

    token = create_token({"user_id": user.user_id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(403, "Вы не можете менять чужой профиль")

    user = UserRepository.get(db, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    updated = UserRepository.update(db, user_id, data.model_dump(exclude_unset=True))
    return updated


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserRepository.get(db, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@router.get("/{user_id}/with_course", response_model=UserWithCourseResponse)
def get_user_with_course_info(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить пользователя с дополнительной информацией о курсе
    """
    user = UserRepository.get(db, user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    
    # Преобразуем пользователя в словарь
    user_dict = {
        "user_id": user.user_id,
        "email": user.email,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "phone": user.phone,
        "telegram": user.telegram,
        "vk": user.vk,
        "interests": user.interests,
        "avatar_path": user.avatar_path,
        "role": user.role
    }
    
    course_info = None
    tutor_info = None
    courses_count = None
    students_count = None
    
    # Для ученика: информация о курсе
    if user.role == "Ученик":
        from app.models.user_course import UserCourse
        from app.models.course import Course
        
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == user_id
        ).first()
        
        if user_course:
            course = db.query(Course).filter(
                Course.course_id == user_course.course_id
            ).first()
            
            if course:
                course_info = {
                    "course_id": course.course_id,
                    "course_name": course.title,
                    "created_at": course.created_at.isoformat() if hasattr(course, 'created_at') and course.created_at else None,
                    "knowledge_gaps": user_course.knowledge_gaps
                }
                
                # Находим репетитора этого курса
                from app.models.user import User
                tutor_course = db.query(UserCourse).filter(
                    UserCourse.course_id == user_course.course_id,
                    UserCourse.user_id != user_id  # исключаем самого ученика
                ).join(User, UserCourse.user_id == User.user_id).filter(
                    User.role == "Репетитор"
                ).first()
                
                if tutor_course:
                    tutor = db.query(User).filter(
                        User.user_id == tutor_course.user_id
                    ).first()
                    if tutor:
                        tutor_info = f"{tutor.last_name} {tutor.first_name} {tutor.middle_name}"
    
    # Для репетитора: информация о его курсах и учениках
    elif user.role == "Репетитор":
        from app.models.user_course import UserCourse
        from app.models.course import Course
        from app.models.user import User
        
        # Получаем все курсы репетитора с информацией об учениках
        tutor_courses = db.query(UserCourse.course_id).filter(
            UserCourse.user_id == user_id
        ).all()
        
        course_ids = [c[0] for c in tutor_courses]
        
        courses_count = len(course_ids)
        
        # Собираем информацию о курсах и учениках
        courses_info = []
        if course_ids:
            # Получаем всех учеников на курсах репетитора
            for course_id in course_ids:
                course = db.query(Course).filter(
                    Course.course_id == course_id
                ).first()
                
                if course:
                    # Находим всех учеников на этом курсе
                    student_courses = db.query(UserCourse).filter(
                        UserCourse.course_id == course_id,
                        UserCourse.user_id != user_id
                    ).all()
                    
                    for sc in student_courses:
                        student = db.query(User).filter(
                            User.user_id == sc.user_id,
                            User.role == "Ученик"
                        ).first()
                        
                        if student:
                            courses_info.append({
                                "course_id": course.course_id,
                                "course_name": course.title,
                                "student_id": student.user_id,
                                "student_name": f"{student.last_name} {student.first_name} {student.middle_name}",
                                "created_at": course.created_at.isoformat() if hasattr(course, 'created_at') and course.created_at else None,
                                "knowledge_gaps": sc.knowledge_gaps
                            })
        
        # Сохраняем информацию о курсах для ответа
        # (нужно будет расширить схему ответа)
        user_dict["courses_info"] = courses_info
        students_count = len(courses_info)
    
    return {
        **user_dict,
        "course_info": course_info,
        "tutor_full_name": tutor_info,
        "courses_count": courses_count,
        "students_count": students_count
    }