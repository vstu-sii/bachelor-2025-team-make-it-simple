from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.routes.course_routes import router as course_router
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