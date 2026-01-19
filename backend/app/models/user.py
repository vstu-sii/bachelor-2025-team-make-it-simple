from sqlalchemy import Column, Integer, String, Date, Text, Enum, Index
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    Ученик = "Ученик"
    Репетитор = "Репетитор"

class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index("idx_user_lastname", "last_name"),
        Index("idx_user_firstname", "first_name"),
        Index("idx_user_phone", "phone"),
        Index("idx_user_email", "email", unique=True)
    )

    user_id = Column(Integer, primary_key=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20), nullable=False)
    telegram = Column(String(100))
    vk = Column(String(100))
    avatar_path = Column(String(1000))
    interests = Column(Text)
    role = Column(Enum(UserRole, name="UserRole"), nullable=False)
    email = Column(String(250), nullable=False)
    password = Column(String(500), nullable=False)


    def __repr__(self):
        return f'<User(id={self.user_id}, name="{self.last_name} {self.first_name} {self.middle_name}")>'