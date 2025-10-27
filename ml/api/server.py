from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime

from ml.models.baseline import BaselineLLM
from ml.api.routes import router

app = FastAPI(
    title="Tutor AI API",
    description="API для генерации учебных материалов с использованием LLM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router, prefix="/api/v1")

# Глобальная модель
llm_model = None

@app.on_event("startup")
async def startup_event():
    """Инициализация модели при запуске"""
    global llm_model
    llm_model = BaselineLLM()
    print("API сервер запущен")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Tutor AI API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    model_status = "available" if llm_model and llm_model.model_available else "unavailable"
    
    return {
        "status": "healthy",
        "model_status": model_status,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "ml.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
