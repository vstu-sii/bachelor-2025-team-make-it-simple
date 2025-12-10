from sqlalchemy import Column, Integer, String, Date, Text, Index
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base

class Course(Base):
    __tablename__ = "course"

    __table_args__ = (
        Index("idx_course_title", "title"),
        Index("idx_course_created_at", "created_at"),
    )

    course_id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    created_at = Column(Date, nullable=False)
    link_to_vector_db = Column(String(1000), nullable=False)
    input_test_json = Column(JSON)

    def __repr__(self):
        return f'<Course(id={self.course_id}, title={self.title})>'