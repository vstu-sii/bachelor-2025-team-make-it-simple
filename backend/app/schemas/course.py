from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class CourseBase(BaseModel):
    title: str
    created_at: Optional[date] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    course_id: int
    
    class Config:
        from_attributes = True

# Схема для курса с учениками
class CourseWithStudentsResponse(CourseResponse):
    students: List[dict] = []

# Схема для отображения курсов репетитора
class TutorCourseResponse(BaseModel):
    course_id: int
    course_name: str
    student_id: int
    student_name: str
    created_at: Optional[date] = None

# Схема для отображения курсов ученика
class StudentCourseResponse(BaseModel):
    course_id: int
    course_name: str
    tutor_id: int
    tutor_name: str
    created_at: Optional[date] = None
    knowledge_gaps: Optional[str] = None