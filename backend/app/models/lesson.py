from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Lesson(Base):
    __tablename__ = "lesson"

    lesson_id = Column(Integer, primary_key=True)
    theory_text = Column(Text)
    reading_text = Column(Text)
    speaking_text = Column(Text)
    lesson_plan_json = Column(JSON)
    lesson_test_results_json = Column(JSON)
    lesson_notes = Column(Text)
    results_json = Column(JSON)
    is_access = Column(Boolean, nullable=False, default=False)
    is_ended = Column(Boolean, nullable=False, default=False)
    topic_id = Column(Integer, ForeignKey("topic.topic_id", ondelete="SET NULL"), nullable=True)
    
    def __repr__(self):
        return f'<Lesson(id={self.lesson_id}, is_ended={self.is_ended}, is_access={self.is_access})>'