from sqlalchemy import Column, Integer, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base


class UserCourse(Base):
    __tablename__ = "user_course"

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="idx_user_course_unique"),
        Index("idx_user_course_user_id", "user_id"),
        Index("idx_user_course_course_id", "course_id"),
    )

    user_course_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    knowledge_gaps = Column(Text)
    graph_json = Column(JSON)
    output_test_json = Column(JSON)

    def __repr__(self):
        return f'<UserCourse(id={self.user_course_id}, user_id={self.user_id}, course_id={self.course_id})>'
    
    # TODO
    # idx_one_course_for_student просто так не сделать через SQLAlchemy
    # поэтому эту штуку придется потом вручную докинуть через Alembic!!