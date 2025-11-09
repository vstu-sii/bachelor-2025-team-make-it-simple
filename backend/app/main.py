from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.database import init_db

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
        allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
