from sqlalchemy import Column, Integer, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from app.database import Base
from app.models.user import User

class UserCourse(Base):
    __tablename__ = "user_course"

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="idx_user_course_unique"),
        Index("idx_user_course_user_id", "user_id"),
        Index("idx_user_course_course_id", "course_id"),
        Index("idx_one_course_for_student", "user_id", unique=True,
            postgresql_where="""
                EXISTS (
                    SELECT 1 FROM "user" u 
                    WHERE u.user_id = user_course.user_id 
                    AND u.role = 'Ученик'
                ) """
        ),
    )

    user_course_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    knowledge_gaps = Column(Text)
    graph_json = Column(JSON)
    output_test_json = Column(JSON)

    def __repr__(self):
        return f'<UserCourse(id={self.user_course_id}, user_id={self.user_id}, course_id={self.course_id})>'