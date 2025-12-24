from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from app.database import get_db
from app.utils.jwt import get_current_user
from app.models.lesson import Lesson
from app.models.user import User
from app.repositories.lesson_test_repository import LessonTestRepository
from app.schemas.lesson_test import (
    LessonTestGenerationRequest,
    GeneratedLessonTestResponse,
    LessonTestFinalizationRequest,
    LessonTestStatusResponse,
    StudentTestSubmission,
    StudentTestResults,
    LessonTestEvaluation
)
from app.ml.main import generate_lesson_test

router = APIRouter(prefix="/lesson-tests", tags=["Lesson Tests"])

@router.get("/lessons/{lesson_id}/test/status", response_model=LessonTestStatusResponse)
async def get_lesson_test_status(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить статус теста для урока
    """
    try:
        status = LessonTestRepository.get_lesson_test_status(db, lesson_id)
        
        return LessonTestStatusResponse(**status)
        
    except Exception as e:
        print(f"Error getting lesson test status: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении статуса теста урока")

@router.post("/lessons/{lesson_id}/test/generate")
async def generate_lesson_test_endpoint(
    lesson_id: int,
    request: LessonTestGenerationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сгенерировать тест для урока с учетом замечаний репетитора
    """
    try:
        print(f"\n=== ЗАПРОС НА ГЕНЕРАЦИЮ ТЕСТА УРОКА ===")
        print(f"  lesson_id: {lesson_id}")
        print(f"  feedback: {request.feedback}")
        print(f"  current_user: {current_user.user_id}, role: {current_user.role}")
        
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут генерировать тесты уроков")
        
        # Получаем данные урока для генерации
        lesson_data = LessonTestRepository.get_lesson_data_for_test_generation(db, lesson_id)
        if not lesson_data:
            raise HTTPException(status_code=404, detail="Урок не найден")
        
        print(f"  Данные урока получены: {lesson_data}")
        
        try:
            # Генерируем тест с использованием AI
            print("  Генерация теста урока через AI...")
            
            # Подготавливаем данные для AI
            ai_lesson_data = {
                "lesson_parameters": {
                    "topic": f"Урок {lesson_id}",
                    "student_profile": {
                        "interests": [],  # Можно добавить логику получения интересов учеников
                        "knowledge_gaps": []
                    }
                },
                "theory": lesson_data.get("theory", ""),
                "type": "test"
            }
            
            generated_test = generate_lesson_test(
                lesson_data=ai_lesson_data,
                feedback=request.feedback
            )
            
            # Извлекаем вопросы из ответа AI
            questions = generated_test.get("test_section", {}).get("questions", [])
            if not questions:
                questions = generated_test.get("questions", [])
            
            generated_test_data = {
                "questions": questions
            }
            
            print(f"  Сгенерировано вопросов: {len(generated_test_data.get('questions', []))}")
            
        except ImportError as ie:
            print(f"  Ошибка импорта AI модуля: {ie}")
            # Возвращаем тест-заглушку
            generated_test_data = {
                "questions": [
                    {
                        "question_id": "1",
                        "type": "single_choice",
                        "question": "What did you learn in this lesson?",
                        "options": [
                            "Grammar rules",
                            "Vocabulary", 
                            "Speaking practice",
                            "All of the above"
                        ],
                        "correct_answer": 3
                    },
                    {
                        "question_id": "2",
                        "type": "short_answer",
                        "question": "Summarize the main topic of this lesson.",
                        "max_length": 200,
                        "correct_answer": "The lesson covered important concepts about the topic."
                    }
                ]
            }
            print(f"  Используется демо-тест: {len(generated_test_data['questions'])} вопроса")
        
        # Сохраняем сгенерированный тест в урок
        save_success = LessonTestRepository.save_generated_lesson_test(
            db=db,
            lesson_id=lesson_id,
            test_data=generated_test_data,
            feedback=request.feedback,
            finalize=False
        )
        
        if not save_success:
            print("  Ошибка при сохранении теста урока в базу")
            raise HTTPException(status_code=500, detail="Ошибка при сохранении сгенерированного теста урока")
        
        # Формируем ответ
        response_data = {
            "questions": generated_test_data.get("questions", []),
            "generation_id": f"lesson_test_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now(),
            "feedback_used": request.feedback
        }
        
        print(f"  Тест урока успешно сгенерирован и сохранен")
        print(f"  Ответ содержит {len(response_data['questions'])} вопросов")
        
        return GeneratedLessonTestResponse(**response_data)
        
    except HTTPException as he:
        print(f"HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print(f"Неизвестная ошибка при генерации теста урока: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера при генерации теста урока: {str(e)}")

@router.put("/lessons/{lesson_id}/test/finalize")
async def finalize_lesson_test(
    lesson_id: int,
    request: LessonTestFinalizationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Зафинализировать тест урока (сохранить окончательно)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут финализировать тесты уроков")
        
        # Получаем существующий тест урока
        existing_test = LessonTestRepository.get_generated_lesson_test(db, lesson_id)
        
        if not existing_test or not existing_test.get("questions"):
            raise HTTPException(status_code=400, detail="Нет сгенерированного теста урока для финализации")
        
        # Проверяем, не финализирован ли уже тест
        if existing_test.get("is_finalized", False):
            raise HTTPException(status_code=400, detail="Тест урока уже финализирован")
        
        # Финализируем тест
        if request.finalize:
            finalize_success = LessonTestRepository.finalize_lesson_test(db, lesson_id)
            
            if not finalize_success:
                raise HTTPException(status_code=500, detail="Ошибка при финализации теста урока")
        
        return {
            "message": "Тест урока успешно финализирован",
            "lesson_id": lesson_id,
            "questions_count": len(existing_test.get("questions", [])),
            "is_finalized": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finalizing lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при финализации теста урока")

@router.get("/lessons/{lesson_id}/test")
async def get_lesson_test(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить сгенерированный тест урока
    """
    try:
        # Получаем тест урока
        test_data = LessonTestRepository.get_generated_lesson_test(db, lesson_id)
        
        if not test_data or not test_data.get("questions"):
            raise HTTPException(status_code=404, detail="Тест урока не найден или не сгенерирован")
        
        # Получаем урок для проверки доступа
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Урок не найден")
        
        # Проверяем доступ ученика к тесту
        if current_user.role == "Ученик" and not lesson.is_access:
            raise HTTPException(status_code=403, detail="Урок недоступен")
        
        return {
            "test_data": test_data,
            "is_finalized": test_data.get("is_finalized", False),
            "generated_at": test_data.get("generated_at"),
            "questions_count": len(test_data.get("questions", [])),
            "lesson_access": lesson.is_access
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении теста урока")

@router.post("/lessons/{lesson_id}/students/{student_id}/submit-test")
async def submit_student_lesson_test(
    lesson_id: int,
    student_id: int,
    submission: StudentTestSubmission,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сохранить результаты теста урока ученика
    """
    try:
        # Проверяем, что ученик отправляет свои результаты
        if current_user.user_id != student_id:
            raise HTTPException(status_code=403, detail="Нельзя сохранять результаты за другого ученика")
        
        # Проверяем, что пользователь - ученик
        if current_user.role != "Ученик":
            raise HTTPException(status_code=403, detail="Только ученики могут отправлять результаты теста")
        
        # Получаем тест урока для проверки правильных ответов
        lesson_test = LessonTestRepository.get_generated_lesson_test(db, lesson_id)
        if not lesson_test or not lesson_test.get("questions"):
            raise HTTPException(status_code=400, detail="Тест урока не найден")
        
        # Получаем урок для проверки доступа
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson or not lesson.is_access:
            raise HTTPException(status_code=403, detail="Урок недоступен")
        
        # Вычисляем результаты
        results = LessonTestRepository.calculate_test_results(
            student_answers=submission.tasks,
            correct_answers=lesson_test.get("questions", [])
        )
        
        # Сохраняем результаты в lesson_test_results_json
        save_success = LessonTestRepository.save_student_test_results(
            db=db,
            lesson_id=lesson_id,
            student_id=student_id,
            test_results=results
        )
        
        if not save_success:
            raise HTTPException(status_code=500, detail="Ошибка при сохранении результатов теста")
        
        return {
            "message": "Результаты теста урока успешно сохранены",
            "lesson_id": lesson_id,
            "student_id": student_id,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error submitting student lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении результатов теста урока")

@router.get("/lessons/{lesson_id}/students/{student_id}/test-results")
async def get_student_lesson_test_results(
    lesson_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить результаты теста урока конкретного ученика
    """
    try:
        # Проверяем доступ к данным
        if current_user.user_id != student_id and current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Нет доступа к этим данным")
        
        # Получаем результаты ученика
        results = LessonTestRepository.get_student_test_results(db, lesson_id, student_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Результаты теста не найдены")
        
        return {
            "lesson_id": lesson_id,
            "student_id": student_id,
            "results": results,
            "has_results": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting student lesson test results: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении результатов теста")

@router.get("/lessons/{lesson_id}/students/test-results")
async def get_all_students_lesson_test_results(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить результаты теста урока всех учеников (только для репетитора)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать результаты всех учеников")
        
        # Получаем результаты всех учеников
        all_results = LessonTestRepository.get_all_students_test_results(db, lesson_id)
        
        # Получаем информацию об учениках
        students_data = {}
        for student_id_str, results in all_results.items():
            try:
                student_id = int(student_id_str)
                student = db.query(User).filter(User.user_id == student_id).first()
                if student:
                    students_data[student_id_str] = {
                        "student_id": student_id,
                        "student_name": f"{student.last_name} {student.first_name}",
                        "results": results
                    }
                else:
                    students_data[student_id_str] = {
                        "student_id": student_id,
                        "student_name": "Неизвестный ученик",
                        "results": results
                    }
            except ValueError:
                continue
        
        return {
            "lesson_id": lesson_id,
            "students_count": len(students_data),
            "students_results": students_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting all students lesson test results: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении результатов всех учеников")

@router.post("/lessons/{lesson_id}/students/{student_id}/evaluate-test")
async def evaluate_student_lesson_test(
    lesson_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Оценить результаты теста урока ученика (AI оценка)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут оценивать результаты")
        
        # Получаем результаты ученика
        results = LessonTestRepository.get_student_test_results(db, lesson_id, student_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Результаты теста не найдены")
        
        # Получаем ученика
        student = db.query(User).filter(User.user_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Ученик не найден")
        
        # Генерируем рекомендации на основе результатов
        percentage = results.get("percentage", 0)
        recommendations = []
        
        if percentage < 50:
            recommendations = [
                "Рекомендуется повторно изучить теоретический материал урока",
                "Необходима дополнительная практика по теме",
                "Стоит выполнить дополнительные упражнения"
            ]
        elif percentage < 70:
            recommendations = [
                "Хороший результат, но есть над чем поработать",
                "Рекомендуется обратить внимание на допущенные ошибки",
                "Полезна будет дополнительная практика"
            ]
        else:
            recommendations = [
                "Отличный результат!",
                "Можно переходить к следующей теме",
                "Рекомендуется закрепить знания практикой"
            ]
        
        evaluation = {
            "lesson_id": lesson_id,
            "student_id": student_id,
            "results": results,
            "recommendations": recommendations,
            "evaluated_at": datetime.now().isoformat(),
            "student_name": f"{student.last_name} {student.first_name}"
        }
        
        return evaluation
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error evaluating student lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при оценке результатов теста")

@router.delete("/lessons/{lesson_id}/test")
async def reset_lesson_test(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сбросить сгенерированный тест урока (если он не финализирован)
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут сбрасывать тесты уроков")
        
        # Получаем существующий тест урока
        existing_test = LessonTestRepository.get_generated_lesson_test(db, lesson_id)
        
        if not existing_test:
            raise HTTPException(status_code=404, detail="Тест урока не найден")
        
        # Проверяем, не финализирован ли уже тест
        if existing_test.get("is_finalized", False):
            raise HTTPException(status_code=400, detail="Невозможно сбросить финализированный тест")
        
        # Сбрасываем тест урока
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        
        if lesson:
            lesson.lesson_plan_json = json.dumps({})
            db.commit()
        
        return {
            "message": "Тест урока успешно сброшен",
            "lesson_id": lesson_id,
            "is_finalized": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resetting lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сбросе теста урока")

@router.get("/debug/lesson-test-data/{lesson_id}")
async def debug_lesson_test_data(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Отладочный эндпоинт для проверки данных теста урока в БД
    """
    print(f"\n=== DEBUG: ПРОВЕРКА ДАННЫХ ТЕСТА УРОКА ===")
    print(f"  lesson_id: {lesson_id}")
    
    # 1. Проверяем урок
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    
    if not lesson:
        return {"error": "Урок не найден"}
    
    print(f"  Урок найден: ID={lesson.lesson_id}")
    print(f"  lesson_plan_json тип: {type(lesson.lesson_plan_json)}")
    print(f"  lesson_plan_json длина: {len(str(lesson.lesson_plan_json)) if lesson.lesson_plan_json else 0}")
    print(f"  lesson_test_results_json длина: {len(str(lesson.lesson_test_results_json)) if lesson.lesson_test_results_json else 0}")
    
    # 2. Проверяем содержимое lesson_plan_json
    test_data = None
    if lesson.lesson_plan_json:
        try:
            test_data = json.loads(lesson.lesson_plan_json)
            print(f"  Тест урока: {len(test_data.get('questions', []))} вопросов")
            print(f"  is_finalized: {test_data.get('is_finalized', False)}")
        except json.JSONDecodeError as e:
            print(f"  ОШИБКА парсинга lesson_plan_json: {e}")
    
    # 3. Проверяем содержимое lesson_test_results_json
    results_data = None
    if lesson.lesson_test_results_json:
        try:
            results_data = json.loads(lesson.lesson_test_results_json)
            print(f"  Результаты теста: {len(results_data)} учеников")
        except json.JSONDecodeError as e:
            print(f"  ОШИБКА парсинга lesson_test_results_json: {e}")
    
    return {
        "lesson_id": lesson.lesson_id,
        "has_lesson_plan_json": bool(lesson.lesson_plan_json),
        "lesson_plan_json": test_data,
        "has_lesson_test_results_json": bool(lesson.lesson_test_results_json),
        "lesson_test_results_json": results_data,
        "questions_count": len(test_data.get('questions', [])) if test_data else 0,
        "students_count": len(results_data) if results_data else 0,
        "is_access": lesson.is_access
    }

@router.put("/lessons/{lesson_id}/test/save-and-finalize")
async def save_and_finalize_lesson_test(
    lesson_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сохранить и сразу финализировать тест урока (одна операция)
    """
    try:
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут сохранять тесты уроков")
        
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        
        if not lesson:
            raise HTTPException(status_code=404, detail="Урок не найден")
        
        test_data = request.get("test_data", {})
        
        # Сохраняем тест в lesson_plan_json
        lesson.lesson_plan_json = json.dumps(test_data)
        
        # Автоматически финализируем (публикуем) тест
        try:
            existing_data = json.loads(lesson.lesson_plan_json) if lesson.lesson_plan_json else {}
            existing_data["is_finalized"] = True
            existing_data["finalized_at"] = datetime.now().isoformat()
            lesson.lesson_plan_json = json.dumps(existing_data)
        except:
            # Если не удалось распарсить, создаем новую структуру
            lesson.lesson_plan_json = json.dumps({
                **test_data,
                "is_finalized": True,
                "finalized_at": datetime.now().isoformat()
            })
        
        db.commit()
        
        return {
            "message": "Тест урока успешно сохранен и опубликован",
            "lesson_id": lesson_id,
            "questions_count": len(test_data.get("questions", [])),
            "is_finalized": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error saving and finalizing lesson test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении теста урока")