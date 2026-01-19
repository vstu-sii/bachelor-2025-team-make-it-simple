from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.user_repository import UserRepository

SECRET_KEY = "ilya_SII"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60


def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    Authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if not Authorization:
        raise HTTPException(401, "Missing Authorization header")

    token = Authorization.replace("Bearer ", "").strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "Invalid token")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = UserRepository.get(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    return user
