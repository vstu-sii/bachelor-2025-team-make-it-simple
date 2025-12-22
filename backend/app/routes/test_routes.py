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
from app.models.user_course import UserCourse
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
    
@router.get("/courses/{course_id}/student/{student_id}/test-status")
async def get_student_test_status(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить статус прохождения теста для конкретного ученика
    """
    try:
        # Проверяем доступ к данным
        if current_user.user_id != student_id and current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Нет доступа к этим данным")
        
        # Находим запись ученика на курсе
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not user_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на курсе")
        
        # Проверяем, есть ли результаты теста
        test_status = "не пройден"
        results = None
        
        if user_course.output_test_json:
            try:
                test_data = json.loads(user_course.output_test_json)
                if test_data and test_data.get("results"):
                    test_status = "пройден"
                    results = test_data.get("results")
            except:
                pass
        
        return {
            "student_id": student_id,
            "course_id": course_id,
            "test_status": test_status,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting student test status: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении статуса теста")
    
@router.post("/courses/{course_id}/student/{student_id}/submit")
async def submit_student_test(
    course_id: int,
    student_id: int,
    test_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сохранить результаты теста ученика
    """
    try:
        # Проверяем, что ученик отправляет свои результаты
        if current_user.user_id != student_id:
            raise HTTPException(status_code=403, detail="Нельзя сохранять результаты за другого ученика")
        
        # Проверяем, что пользователь - ученик
        if current_user.role != "Ученик":
            raise HTTPException(status_code=403, detail="Только ученики могут отправлять результаты теста")
        
        # Находим запись ученика на курсе
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not user_course:
            raise HTTPException(status_code=404, detail="Ученик не найден на курсе")
        
        # Получаем тест курса для проверки правильных ответов
        course_test = TestRepository.get_generated_test(db, course_id)
        if not course_test or not course_test.get("questions"):
            raise HTTPException(status_code=400, detail="Тест курса не найден")
        
        # Вычисляем результаты
        results = calculate_test_results(
            student_answers=test_data.get("tasks", []),
            correct_answers=course_test.get("questions", [])
        )
        
        # Сохраняем результаты в user_course
        user_course.output_test_json = json.dumps({
            "submitted_at": datetime.now().isoformat(),
            "test_data": test_data,
            "results": results
        })
        
        db.commit()
        
        return {
            "message": "Результаты теста успешно сохранены",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error submitting student test: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении результатов теста")

def calculate_test_results(student_answers, correct_answers):
    """
    Вычисляет результаты теста на основе ответов ученика и правильных ответов
    """
    total_score = 0
    max_score = len(correct_answers)
    detailed_results = []
    
    # Создаем словарь для быстрого поиска правильных ответов
    correct_answers_dict = {q.get("question_id"): q for q in correct_answers}
    
    for student_answer in student_answers:
        question_id = student_answer.get("question_id")
        correct_answer = correct_answers_dict.get(question_id)
        
        if not correct_answer:
            continue
        
        score = 0
        is_correct = False
        user_answer_to_store = None
        
        # Проверяем ответ в зависимости от типа вопроса
        if student_answer.get("type") == "short_answer":
            user_answer = student_answer.get("userAnswer", "").strip().lower()
            correct = correct_answer.get("correct_answer", "").strip().lower()
            is_correct = user_answer == correct
            score = 1 if is_correct else 0
            user_answer_to_store = user_answer
            
        elif student_answer.get("type") == "single_choice":
            user_answer = student_answer.get("userAnswer")
            # Приводим к строке для сравнения
            user_answer_str = str(user_answer) if user_answer is not None else ""
            correct = str(correct_answer.get("correct_answer"))
            is_correct = user_answer_str == correct
            score = 1 if is_correct else 0
            user_answer_to_store = user_answer_str
            
        elif student_answer.get("type") == "multiple_choice":
            user_answers = student_answer.get("userAnswer", [])
            # Приводим все к строкам для сравнения
            user_answers_set = set(map(str, user_answers))
            correct_answers_set = set(map(str, correct_answer.get("correct_answers", [])))
            is_correct = user_answers_set == correct_answers_set
            score = 1 if is_correct else 0
            user_answer_to_store = list(user_answers_set)
            
        elif student_answer.get("type") == "gaps_choice":
            # Получаем ответы ученика для пропусков
            gaps_user_answers = {}
            if student_answer.get("gaps"):
                for gap in student_answer.get("gaps", []):
                    gap_id = gap.get("gap_id")
                    gap_answer = gap.get("userAnswer", "")
                    gaps_user_answers[gap_id] = str(gap_answer) if gap_answer is not None else ""
            
            # Сравниваем с правильными ответами
            all_correct = True
            if correct_answer.get("gaps"):
                for gap in correct_answer.get("gaps", []):
                    gap_id = gap.get("gap_id")
                    correct_gap_answer = str(gap.get("correct_answer"))
                    user_gap_answer = gaps_user_answers.get(gap_id, "")
                    
                    if correct_gap_answer != user_gap_answer:
                        all_correct = False
                        break
            
            is_correct = all_correct
            score = 1 if is_correct else 0
            user_answer_to_store = gaps_user_answers
        
        total_score += score
        
        detailed_results.append({
            "question_id": question_id,
            "question": correct_answer.get("question", ""),
            "type": student_answer.get("type"),
            "user_answer": user_answer_to_store,
            "correct_answer": correct_answer.get("correct_answer") if student_answer.get("type") != "multiple_choice" else correct_answer.get("correct_answers"),
            "is_correct": is_correct,
            "score": score,
            "max_score": 1
        })
    
    percentage = round((total_score / max_score) * 100) if max_score > 0 else 0
    
    return {
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "completed_at": datetime.now().isoformat(),
        "detailed_results": detailed_results
    }

@router.get("/courses/{course_id}/student/{student_id}/test-answers")
async def get_student_test_answers(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить ответы ученика на тест
    """
    try:
        # Проверяем, что пользователь - репетитор
        if current_user.role != "Репетитор":
            raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать ответы учеников")
        
        # Получаем тест курса
        course_test = TestRepository.get_generated_test(db, course_id)
        if not course_test or not course_test.get("questions"):
            raise HTTPException(status_code=404, detail="Тест курса не найден")
        
        # Получаем результаты теста ученика
        user_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not user_course or not user_course.output_test_json:
            # Если ученик еще не прошел тест, возвращаем тест без ответов
            return {
                "test_data": course_test,
                "student_answers": None,
                "has_answers": False
            }
        
        # Получаем ответы ученика
        student_data = json.loads(user_course.output_test_json)
        student_answers = student_data.get("test_data", {}).get("tasks", [])
        
        # Объединяем вопросы теста с ответами ученика
        combined_questions = []
        for i, question in enumerate(course_test.get("questions", [])):
            student_answer = next(
                (sa for sa in student_answers if sa.get("question_id") == question.get("question_id")), 
                None
            )
            
            combined_question = {
                **question,
                "student_answer": student_answer.get("userAnswer") if student_answer else None
            }
            combined_questions.append(combined_question)
        
        return {
            "test_data": {
                **course_test,
                "questions": combined_questions
            },
            "student_answers": student_answers,
            "has_answers": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting student test answers: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении ответов ученика")