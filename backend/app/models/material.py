from sqlalchemy import Column, Integer, String, Index
from app.database import Base


class Material(Base):
    __tablename__ = "material"

    __table_args__ = (
        Index("idx_material_filepath", "file_path", unique=True),
    )

    material_id = Column(Integer, primary_key=True)
    file_path = Column(String(1000), nullable=False)

    def __repr__(self):
        return f'<UserCourse(id={self.material_id}, file_path="{self.file_path}")>'
    