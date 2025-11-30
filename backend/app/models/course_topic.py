from sqlalchemy import Column, Integer, ForeignKey, Index, UniqueConstraint
from app.database import Base


class CourseTopic(Base):
    __tablename__ = "course_topic"

    __table_args__ = (
        UniqueConstraint("course_id", "topic_id", name="idx_course_topic_unique"),
        Index("idx_course_topic_course_id", "course_id"),
        Index("idx_course_topic_topic_id", "topic_id"),
    )

    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("topic.topic_id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f'<Course(course_id={self.course_id}, topic_id={self.topic_id})>'