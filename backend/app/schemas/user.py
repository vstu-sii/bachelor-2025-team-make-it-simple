from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import date
from typing import Optional


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
    

class UserResponse(UserBase): # это ответ API
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
