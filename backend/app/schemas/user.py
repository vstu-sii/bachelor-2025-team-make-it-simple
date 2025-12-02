from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import date, datetime
from typing import List, Optional, Dict, Any

class UserBase(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: str = Field(..., min_length=1, max_length=50)
    birth_date: date
    phone: str = Field(..., max_length=20)
    telegram: Optional[str] = Field(None, max_length=100)
    vk: Optional[str] = Field(None, max_length=100)
    avatar_path: Optional[str] = Field(None, max_length=1000)
    interests: Optional[str] = None
    role: str = Field(..., description="Роль: 'Ученик' или 'Репетитор'")
    email: EmailStr


class UserCreateStep1(BaseModel):
    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    middle_name: str = Field(..., min_length=1, max_length=50)
    birth_date: date
    phone: str = Field(..., max_length=20)
    email: EmailStr


class UserCreateStep2(BaseModel):
    telegram: Optional[str] = Field(None, max_length=100)
    vk: Optional[str] = Field(None, max_length=100)
    interests: Optional[str] = None
    role: str = Field(..., description="Роль: 'Ученик' или 'Репетитор'")

    password: str = Field(..., min_length=8, max_length=20)
    password_repeat: str = Field(..., min_length=8, max_length=20)

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.password_repeat:
            raise ValueError("Пароли не совпадают")
        return self

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=20)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    

class UserResponse(UserBase):
    user_id: int

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=50)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    telegram: Optional[str] = Field(None, max_length=100)
    vk: Optional[str] = Field(None, max_length=100)
    avatar_path: Optional[str] = Field(None, max_length=1000)
    interests: Optional[str] = None


class CourseInfoResponse(BaseModel):
    course_id: int
    course_name: str
    created_at: Optional[str]
    knowledge_gaps: Optional[str]

class TutorCourseInfo(BaseModel):
    course_id: int
    course_name: str
    student_id: int
    student_name: str
    created_at: Optional[str] = None
    knowledge_gaps: Optional[str] = None

class UserWithCourseResponse(BaseModel):
    user_id: int
    email: EmailStr
    last_name: Optional[str]
    first_name: str
    middle_name: Optional[str]
    birth_date: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    vk: Optional[str]
    interests: Optional[str]
    avatar_path: Optional[str]
    role: str
    course_info: Optional[CourseInfoResponse] = None
    courses_info: List[TutorCourseInfo] = []  # Добавили информацию о курсах репетитора
    tutor_full_name: Optional[str] = None
    courses_count: Optional[int] = None
    students_count: Optional[int] = None