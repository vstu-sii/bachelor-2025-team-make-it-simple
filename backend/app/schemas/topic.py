from pydantic import BaseModel
from typing import Optional

class TopicBase(BaseModel):
    title: str
    description_text: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description_text: Optional[str] = None

class TopicResponse(TopicBase):
    topic_id: int
    
    class Config:
        from_attributes = True