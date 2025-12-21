from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from app.database import get_db
from app.repositories.test_repository import TestRepository
from app.schemas.test import (
    TestGenerationRequest,
    GeneratedTestResponse,
    TestFinalizationRequest,
    TestStatusResponse
)
from app.utils.jwt import get_current_user
from app.models.course import Course
from app.ml.main import generate_entry_test

router = APIRouter(prefix="/tests", tags=["Tests"])

@router.get("/courses/{course_id}/entry-test/status", response_model=TestStatusResponse)
async def get_entry_test_status(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить статус входного теста для курса
    Теперь тест общий для всех учеников курса
    """
    try:
        # Проверяем доступ к курсу
        status = TestRepository.get_test_status(db, course_id)
        
        return TestStatusResponse(**status)
        
    except Exception as e:
        print(f"Error getting test status: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении статуса теста")

@router.post("/courses/{course_id}/entry-test/generate")
async def generate_entry_test_endpoint(
    course_id: int,
    request: TestGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сгенерировать входной тест для курса с учетом замечаний репетитора
    Тест будет общим для всех учеников курса
    """
    try:
        print(f"\n=== ЗАПРОС НА ГЕНЕРАЦИЮ ТЕСТА ДЛЯ КУРСА ===")
        print(f"  course_id: {course_id}")
        print(f"  feedback: {request.feedback}")
        print(f"  current_user: {current_user.user_id}, role: {current_user.role}")
        
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут генерировать тесты")
        
        # Получаем данные курса
        course_data = TestRepository.get_course_data(db, course_id)
        if not course_data:
            raise HTTPException(status_code=404, detail="Курс не найден")
        
        print(f"  Данные курса получены: {course_data}")
        
        try:
            # Пытаемся импортировать и использовать AI
            from app.ml.main import generate_entry_test as ai_generate_test
            
            print("  Импорт AI модуля успешен")
            
            # Генерируем тест с использованием AI
            print("  Генерация теста через AI...")
            generated_test = ai_generate_test(
                course_data=course_data,
                feedback=request.feedback
            )
            
            print(f"  Сгенерировано вопросов: {len(generated_test.get('questions', []))}")
            
        except ImportError as ie:
            print(f"  Ошибка импорта AI модуля: {ie}")
            # Возвращаем тест-заглушку
            generated_test = {
                "questions": [
                    {
                        "question_id": "1",
                        "type": "single_choice",
                        "question": "What is 2 + 2?",
                        "options": ["3", "4", "5", "6"],
                        "correct_answer": 1
                    },
                    {
                        "question_id": "2",
                        "type": "short_answer",
                        "question": "What is your name?",
                        "max_length": 50,
                        "correct_answer": "My name is Student"
                    }
                ]
            }
            print(f"  Используется демо-тест: {len(generated_test['questions'])} вопроса")
        
        # Сохраняем сгенерированный тест В КУРС
        save_success = TestRepository.save_generated_test(
            db=db,
            course_id=course_id,
            test_data=generated_test,
            feedback=request.feedback,
            finalize=False
        )
        
        if not save_success:
            print("  Ошибка при сохранении теста в базу")
            raise HTTPException(status_code=500, detail="Ошибка при сохранении сгенерированного теста")
        
        # Формируем ответ
        response_data = {
            "questions": generated_test.get("questions", []),
            "generation_id": f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now(),
            "feedback_used": request.feedback
        }
        
        print(f"  Тест успешно сгенерирован и сохранен В КУРС")
        print(f"  Ответ содержит {len(response_data['questions'])} вопросов")
        
        return GeneratedTestResponse(**response_data)
        
    except HTTPException as he:
        print(f"HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print(f"Неизвестная ошибка при генерации теста: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при генерации теста: {str(e)}")
    

@router.put("/courses/{course_id}/entry-test/finalize")
async def finalize_entry_test(
    course_id: int,
    request: TestFinalizationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Зафинализировать входной тест курса (сохранить окончательно)
    Теперь тест будет доступен всем ученикам курса
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут финализировать тесты")
        
        # Получаем существующий тест ИЗ КУРСА
        existing_test = TestRepository.get_generated_test(db, course_id)
        
        if not existing_test or not existing_test.get("questions"):
            raise HTTPException(status_code=400, detail="Нет сгенерированного теста для финализации")
        
        # Проверяем, не финализирован ли уже тест
        if existing_test.get("is_finalized", False):
            raise HTTPException(status_code=400, detail="Тест уже финализирован")
        
        # Финализируем тест В КУРСЕ
        if request.finalize:
            finalize_success = TestRepository.finalize_test(db, course_id)
            
            if not finalize_success:
                raise HTTPException(status_code=500, detail="Ошибка при финализации теста")
        
        return {
            "message": "Тест успешно финализирован и доступен всем ученикам курса",
            "course_id": course_id,
            "questions_count": len(existing_test.get("questions", [])),
            "is_finalized": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finalizing entry test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при финализации теста")

@router.get("/courses/{course_id}/entry-test")
async def get_entry_test(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить сгенерированный входной тест курса
    Теперь тест общий для всех учеников курса
    """
    try:
        # Получаем тест из курса
        test_data = TestRepository.get_generated_test(db, course_id)
        
        if not test_data or not test_data.get("questions"):
            raise HTTPException(status_code=404, detail="Тест не найден или не сгенерирован")
        
        # Проверяем доступ ученика к тесту
        if current_user.role == "Ученик" and test_data.get("is_finalized", False) == False:
            raise HTTPException(status_code=403, detail="Тест еще не опубликован репетитором")
        
        return {
            "test_data": test_data,
            "is_finalized": test_data.get("is_finalized", False),
            "generated_at": test_data.get("generated_at"),
            "questions_count": len(test_data.get("questions", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting entry test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении теста")

@router.delete("/courses/{course_id}/entry-test")
async def reset_entry_test(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сбросить сгенерированный тест курса (если он не финализирован)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут сбрасывать тесты")
        
        # Получаем существующий тест ИЗ КУРСА
        existing_test = TestRepository.get_generated_test(db, course_id)
        
        if not existing_test:
            raise HTTPException(status_code=404, detail="Тест не найден")
        
        # Проверяем, не финализирован ли уже тест
        if existing_test.get("is_finalized", False):
            raise HTTPException(status_code=400, detail="Невозможно сбросить финализированный тест")
        
        # Сбрасываем тест В КУРСЕ
        course = db.query(Course).filter(Course.course_id == course_id).first()
        
        if course:
            course.input_test_json = json.dumps({})
            db.commit()
        
        return {
            "message": "Тест успешно сброшен",
            "course_id": course_id,
            "is_finalized": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resetting entry test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сбросе теста")
    

@router.get("/debug/test-data/{course_id}")
async def debug_test_data(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Отладочный эндпоинт для проверки данных теста в БД (теперь в курсе)
    """
    print(f"\n=== DEBUG: ПРОВЕРКА ДАННЫХ ТЕСТА В КУРСЕ ===")
    print(f"  course_id: {course_id}")
    
    # 1. Проверяем курс
    course = db.query(Course).filter(Course.course_id == course_id).first()
    
    if not course:
        return {"error": "Курс не найден"}
    
    print(f"  Курс найден: ID={course.course_id}, title={course.title}")
    print(f"  input_test_json тип: {type(course.input_test_json)}")
    print(f"  input_test_json длина: {len(str(course.input_test_json)) if course.input_test_json else 0}")
    
    # 2. Проверяем содержимое input_test_json
    if course.input_test_json:
        try:
            test_data = json.loads(course.input_test_json)
            return {
                "course_id": course.course_id,
                "course_title": course.title,
                "has_input_test_json": True,
                "input_test_json": test_data,
                "questions_count": len(test_data.get("questions", [])),
                "is_finalized": test_data.get("is_finalized", False),
                "test_type": test_data.get("test_type"),
                "generation_id": test_data.get("generation_id")
            }
        except json.JSONDecodeError as e:
            return {
                "course_id": course.course_id,
                "has_input_test_json": True,
                "json_decode_error": str(e),
                "input_test_json_preview": str(course.input_test_json)[:500] + "..." if course.input_test_json else ""
            }
    else:
        return {
            "course_id": course.course_id,
            "has_input_test_json": False,
            "input_test_json": None
        }
    
@router.get("/courses/{course_id}/entry-test/questions-count")
async def get_entry_test_questions_count(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить количество вопросов во входном тесте курса
    """
    try:
        # Получаем тест из курса
        test_data = TestRepository.get_generated_test(db, course_id)
        
        if not test_data or not test_data.get("questions"):
            return {"questions_count": 0, "is_finalized": False}
        
        questions_count = len(test_data.get("questions", []))
        is_finalized = test_data.get("is_finalized", False)
        
        return {
            "questions_count": questions_count,
            "is_finalized": is_finalized
        }
        
    except Exception as e:
        print(f"Error getting test questions count: {e}")
        return {"questions_count": 0, "is_finalized": False}