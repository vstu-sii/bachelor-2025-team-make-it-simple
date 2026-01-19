from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate

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
