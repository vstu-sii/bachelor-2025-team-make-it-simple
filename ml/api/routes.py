from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import time

router = APIRouter()

# Модели запросов
class TestGenerationRequest(BaseModel):
    course_topics: list
    student_interests: str = None

class GraphGenerationRequest(BaseModel):
    course_topics: list
    knowledge_gaps: list
    interests: str

class LessonGenerationRequest(BaseModel):
    lesson_topic: str
    course_materials: str
    interests: str
    student_level: str

class ProgressReportRequest(BaseModel):
    student_performance: dict
    lesson_feedback: str
    test_results: dict

@router.post("/generate-test")
async def generate_placement_test(request: TestGenerationRequest):
    """Генерация входного тестирования"""
    try:
        from ml.api.server import llm_model
        
        if not llm_model or not llm_model.model_available:
            raise HTTPException(status_code=503, detail="LLM модель не доступна")
        
        start_time = time.time()
        result = llm_model.generate_placement_test(
            request.course_topics,
            request.student_interests
        )
        end_time = time.time()
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Ошибка генерации'))
        
        return {
            "success": True,
            "data": result['parsed_data'],
            "metadata": {
                "latency": result['latency'],
                "total_time": end_time - start_time,
                "tokens_used": result.get('tokens_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-graph")
async def generate_learning_graph(request: GraphGenerationRequest):
    """Генерация графа обучения"""
    try:
        from ml.api.server import llm_model
        
        if not llm_model or not llm_model.model_available:
            raise HTTPException(status_code=503, detail="LLM модель не доступна")
        
        start_time = time.time()
        result = llm_model.generate_learning_graph(
            request.course_topics,
            request.knowledge_gaps,
            request.interests
        )
        end_time = time.time()
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Ошибка генерации'))
        
        return {
            "success": True,
            "data": result['parsed_data'],
            "metadata": {
                "latency": result['latency'],
                "total_time": end_time - start_time,
                "tokens_used": result.get('tokens_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-lesson")
async def generate_lesson_plan(request: LessonGenerationRequest):
    """Генерация плана урока"""
    try:
        from ml.api.server import llm_model
        
        if not llm_model or not llm_model.model_available:
            raise HTTPException(status_code=503, detail="LLM модель не доступна")
        
        start_time = time.time()
        result = llm_model.generate_lesson_plan(
            request.lesson_topic,
            request.course_materials,
            request.interests,
            request.student_level
        )
        end_time = time.time()
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Ошибка генерации'))
        
        return {
            "success": True,
            "data": result['parsed_data'],
            "metadata": {
                "latency": result['latency'],
                "total_time": end_time - start_time,
                "tokens_used": result.get('tokens_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report")
async def generate_progress_report(request: ProgressReportRequest):
    """Генерация отчёта о прогрессе"""
    try:
        from ml.api.server import llm_model
        
        if not llm_model or not llm_model.model_available:
            raise HTTPException(status_code=503, detail="LLM модель не доступна")
        
        start_time = time.time()
        result = llm_model.generate_progress_report(
            request.student_performance,
            request.lesson_feedback,
            request.test_results
        )
        end_time = time.time()
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Ошибка генерации'))
        
        return {
            "success": True,
            "data": result['parsed_data'],
            "metadata": {
                "latency": result['latency'],
                "total_time": end_time - start_time,
                "tokens_used": result.get('tokens_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-status")
async def get_model_status():
    """Получение статуса модели"""
    from ml.api.server import llm_model
    
    status = "available" if llm_model and llm_model.model_available else "unavailable"
    
    return {
        "model_status": status,
        "model_name": getattr(llm_model, 'model_name', 'unknown') if llm_model else 'unknown',
        "timestamp": datetime.now().isoformat()
    }
