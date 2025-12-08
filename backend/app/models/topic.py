from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Topic(Base):
    __tablename__ = "topic"

    __table_args__ = (
        Index("idx_topic_title", "title"),
    )

    topic_id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description_text = Column(Text)
    
    def __repr__(self):
        return f'<Topic(id={self.topic_id}, title={self.title})>'