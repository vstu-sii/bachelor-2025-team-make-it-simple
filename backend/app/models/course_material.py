from sqlalchemy import Column, Integer, ForeignKey, Index, UniqueConstraint
from app.database import Base


class CourseMaterial(Base):
    __tablename__ = "course_material"

    __table_args__ = (
        UniqueConstraint("course_id", "material_id", name="idx_course_material_unique"),
        Index("idx_course_material_course_id", "course_id"),
        Index("idx_course_material_material_id", "material_id"),
    )

    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), primary_key=True)
    material_id = Column(Integer, ForeignKey("material.material_id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f'<CourseMaterial(course_id={self.course_id}, material_id={self.material_id})>'