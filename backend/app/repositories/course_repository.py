from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.course import Course
from app.models.user_course import UserCourse
from app.models.user import User

class CourseRepository:

    @staticmethod
    def get_courses_by_tutor(db: Session, tutor_id: int):
        """
        Получить все курсы репетитора с информацией об учениках
        """
        # Находим все курсы репетитора
        tutor_courses = db.query(UserCourse.course_id).filter(
            UserCourse.user_id == tutor_id
        ).all()
        
        course_ids = [c[0] for c in tutor_courses]
        
        if not course_ids:
            return []
        
        # Получаем информацию о курсах и учениках
        result = []
        for course_id in course_ids:
            # Получаем информацию о курсе
            course = db.query(Course).filter(Course.course_id == course_id).first()
            if not course:
                continue
                
            # Находим всех учеников на этом курсе
            student_courses = db.query(UserCourse).filter(
                UserCourse.course_id == course_id,
                UserCourse.user_id != tutor_id
            ).all()
            
            for sc in student_courses:
                # Получаем информацию об ученике
                student = db.query(User).filter(User.user_id == sc.user_id).first()
                if student and student.role == "Ученик":
                    result.append({
                        "course_id": course.course_id,
                        "course_name": course.title,
                        "student_id": student.user_id,
                        "student_name": f"{student.last_name} {student.first_name} {student.middle_name}",
                        "created_at": course.created_at,
                        "knowledge_gaps": sc.knowledge_gaps
                    })
        
        return result

    @staticmethod
    def get_course_by_student(db: Session, student_id: int):
        """
        Получить курс ученика с информацией о репетиторе
        """
        # Находим курс ученика
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id
        ).first()
        
        if not student_course:
            return None
        
        # Получаем информацию о курсе
        course = db.query(Course).filter(
            Course.course_id == student_course.course_id
        ).first()
        
        if not course:
            return None
        
        # Находим репетитора этого курса
        tutor_course = db.query(UserCourse).filter(
            UserCourse.course_id == student_course.course_id,
            UserCourse.user_id != student_id
        ).join(User, UserCourse.user_id == User.user_id).filter(
            User.role == "Репетитор"
        ).first()
        
        tutor_info = None
        if tutor_course:
            tutor = db.query(User).filter(
                User.user_id == tutor_course.user_id
            ).first()
            if tutor:
                tutor_info = {
                    "tutor_id": tutor.user_id,
                    "tutor_name": f"{tutor.last_name} {tutor.first_name} {tutor.middle_name}"
                }
        
        return {
            "course_id": course.course_id,
            "course_name": course.title,
            "tutor_id": tutor_info["tutor_id"] if tutor_info else None,
            "tutor_name": tutor_info["tutor_name"] if tutor_info else "Не назначен",
            "created_at": course.created_at,
            "knowledge_gaps": student_course.knowledge_gaps
        }

    @staticmethod
    def search_student_courses(db: Session, tutor_id: int, query: str):
        """
        Поиск курсов репетитора по имени ученика
        """
        # Находим все курсы репетитора
        tutor_courses = db.query(UserCourse.course_id).filter(
            UserCourse.user_id == tutor_id
        ).all()
        
        course_ids = [c[0] for c in tutor_courses]
        
        if not course_ids:
            return []
        
        # Ищем учеников по имени
        search_query = f"%{query}%"
        
        # Находим всех учеников по имени
        students = db.query(User).filter(
            User.role == "Ученик",
            (
                (User.last_name.ilike(search_query)) |
                (User.first_name.ilike(search_query)) |
                (User.middle_name.ilike(search_query))
            )
        ).all()
        
        student_ids = [s.user_id for s in students]
        
        if not student_ids:
            return []
        
        # Получаем курсы этих учеников
        result = []
        for student_id in student_ids:
            student_course = db.query(UserCourse).filter(
                UserCourse.user_id == student_id,
                UserCourse.course_id.in_(course_ids)
            ).first()
            
            if student_course:
                student = db.query(User).filter(User.user_id == student_id).first()
                course = db.query(Course).filter(
                    Course.course_id == student_course.course_id
                ).first()
                
                if student and course:
                    result.append({
                        "course_id": course.course_id,
                        "course_name": course.title,
                        "student_id": student.user_id,
                        "student_name": f"{student.last_name} {student.first_name} {student.middle_name}",
                        "created_at": course.created_at,
                        "knowledge_gaps": student_course.knowledge_gaps
                    })
        
        return result

    @staticmethod
    def create_course_with_tutor_and_student(
        db: Session, 
        tutor_id: int, 
        student_id: int, 
        course_data: dict
    ):
        """
        Создать новый курс и связать его с репетитором и учеником
        """
        # Создаем курс
        course = Course(**course_data)
        db.add(course)
        db.commit()
        db.refresh(course)
        
        # Связываем курс с репетитором
        tutor_course = UserCourse(
            user_id=tutor_id,
            course_id=course.course_id
        )
        db.add(tutor_course)
        
        # Связываем курс с учеником
        student_course = UserCourse(
            user_id=student_id,
            course_id=course.course_id
        )
        db.add(student_course)
        
        db.commit()
        
        return course