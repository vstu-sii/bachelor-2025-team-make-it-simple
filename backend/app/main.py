from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.routes.course_routes import router as course_router
from app.routes.lesson_routes import router as lesson_router
from app.routes.topic_routes import router as topic_router
from app.routes.material_routes import router as material_router
from app.database import init_db
from .config import settings

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(course_router)
app.include_router(lesson_router)
app.include_router(topic_router)
app.include_router(material_router)

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")