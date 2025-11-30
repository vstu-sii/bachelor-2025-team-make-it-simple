from app.database import get_db
from app.repositories.user_repository import UserRepository

db = next(get_db())

user = UserRepository.create(db, {
    "first_name": "Иван",
    "last_name": "Петров",
    "middle_name": "Сергеевич",
    "birth_date": "2000-01-01",
    "phone": "+79990001122",
    "telegram": "tg_ivan",
    "vk": "vk_ivan",
    "interests": "Программирование",
    "role": "Ученик",
    "email": "ivan.petrov@example.com",
    "password": "12345678"
})

print(user.first_name)