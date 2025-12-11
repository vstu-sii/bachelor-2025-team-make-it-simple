from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicResponse, TopicUpdate
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.get("/", response_model=List[TopicResponse])
def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics

@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    return topic

@router.post("/", response_model=TopicResponse)
def create_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию и роль (только репетиторы могут создавать темы)
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут создавать темы")
    
    # Проверяем, что название не пустое
    if not topic_data.title or not topic_data.title.strip():
        raise HTTPException(status_code=400, detail="Название темы не может быть пустым")
    
    # Создаем новую тему
    new_topic = Topic(
        title=topic_data.title.strip(),
        description_text=topic_data.description_text if topic_data.description_text else None
    )
    
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    print(f"Создана новая тема: ID={new_topic.topic_id}, Title={new_topic.title}")
    return new_topic

@router.put("/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию и роль
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять темы")
    
    # Находим тему
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    # Обновляем данные
    if topic_data.title is not None:
        if not topic_data.title.strip():
            raise HTTPException(status_code=400, detail="Название темы не может быть пустым")
        topic.title = topic_data.title.strip()
    
    if topic_data.description_text is not None:
        topic.description_text = topic_data.description_text
    
    db.commit()
    db.refresh(topic)
    
    print(f"Обновлена тема: ID={topic.topic_id}, Title={topic.title}")
    return topic

@router.delete("/{topic_id}")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию и роль
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут удалять темы")
    
    # Находим тему
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    # Логируем перед удалением
    print(f"Удаление темы: ID={topic.topic_id}, Title={topic.title}")
    
    # Удаляем тему (cascade должно удалить связанные уроки)
    db.delete(topic)
    db.commit()
    
    return {"message": "Тема успешно удалена", "topic_id": topic_id}

@router.get("/search/", response_model=List[TopicResponse])
def search_topics(
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Проверяем авторизацию
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    query = db.query(Topic)
    
    if title:
        query = query.filter(Topic.title.ilike(f"%{title}%"))
    
    topics = query.order_by(Topic.title).all()
    return topics