from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.lesson import Lesson
import json
from datetime import datetime
from typing import Dict, Any, Optional

class LessonTestRepository:
    
    @staticmethod
    def get_lesson_test_status(db: Session, lesson_id: int) -> Dict[str, Any]:
        """
        Получить статус теста для урока
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        
        if not lesson:
            return {
                "is_test_generated": False,
                "is_test_finalized": False,
                "questions_count": 0,
                "has_feedback": False
            }
        
        # Проверяем, есть ли сгенерированный тест в lesson_plan_json
        test_data = None
        try:
            if lesson.lesson_plan_json:
                test_data = json.loads(lesson.lesson_plan_json)
        except:
            test_data = None
        
        is_test_generated = bool(test_data and test_data.get("questions"))
        is_test_finalized = bool(test_data and test_data.get("is_finalized", False))
        
        questions_count = 0
        if is_test_generated and test_data.get("questions"):
            questions_count = len(test_data["questions"])
        
        # Проверяем, есть ли замечания в данных теста
        has_feedback = bool(test_data and test_data.get("feedback_used"))
        
        return {
            "lesson_id": lesson_id,
            "is_test_generated": is_test_generated,
            "is_test_finalized": is_test_finalized,
            "last_generation_time": test_data.get("generated_at") if test_data else None,
            "questions_count": questions_count,
            "has_feedback": has_feedback
        }
    
    @staticmethod
    def save_generated_lesson_test(
        db: Session, 
        lesson_id: int, 
        test_data: Dict[str, Any],
        feedback: Optional[str] = None,
        finalize: bool = False
    ) -> bool:
        """
        Сохранить сгенерированный тест в урок (в lesson_plan_json)
        """
        try:
            print(f"\n=== СОХРАНЕНИЕ ТЕСТА УРОКА ===")
            print(f"  lesson_id: {lesson_id}")
            print(f"  feedback: {feedback}")
            print(f"  finalize: {finalize}")
            print(f"  Количество вопросов: {len(test_data.get('questions', []))}")
            
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson:
                print(f"  ОШИБКА: Не найден урок с ID={lesson_id}")
                return False
            
            print(f"  Найден урок: ID={lesson.lesson_id}")
            print(f"  Текущий lesson_plan_json до сохранения: {lesson.lesson_plan_json}")
            
            # Подготавливаем данные для сохранения
            test_data_to_save = {
                "questions": test_data.get("questions", []),
                "generation_id": f"lesson_test_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{lesson_id}",
                "generated_at": datetime.now().isoformat(),
                "is_finalized": finalize,
                "feedback_used": feedback,
                "questions_count": len(test_data.get("questions", [])),
                "test_type": "lesson_test"
            }
            
            print(f"  Данные для сохранения: {json.dumps(test_data_to_save, indent=2)}")
            
            # Сохраняем в поле lesson_plan_json урока
            lesson.lesson_plan_json = json.dumps(test_data_to_save)
            db.commit()
            
            print(f"  Тест урока успешно сохранен")
            print(f"  Новый lesson_plan_json: {lesson.lesson_plan_json}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"  ОШИБКА при сохранении теста урока: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_generated_lesson_test(db: Session, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить сгенерированный тест из урока (из lesson_plan_json)
        """
        try:
            print(f"\n=== ЗАГРУЗКА ТЕСТА УРОКА ===")
            print(f"  lesson_id: {lesson_id}")
            
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson:
                print(f"  ОШИБКА: Не найден урок")
                return None
            
            print(f"  Найден урок: ID={lesson.lesson_id}")
            print(f"  lesson_plan_json присутствует: {bool(lesson.lesson_plan_json)}")
            
            if not lesson.lesson_plan_json:
                print(f"  lesson_plan_json пустой или None")
                return None
            
            try:
                test_data = json.loads(lesson.lesson_plan_json)
                print(f"  JSON успешно распарсен")
                print(f"  Количество вопросов: {len(test_data.get('questions', []))}")
                print(f"  is_finalized: {test_data.get('is_finalized', False)}")
                print(f"  test_type: {test_data.get('test_type')}")
                return test_data
            except json.JSONDecodeError as e:
                print(f"  ОШИБКА парсинга JSON: {e}")
                print(f"  Содержимое lesson_plan_json: {lesson.lesson_plan_json[:500]}...")
                return None
                
        except Exception as e:
            print(f"  ОШИБКА при загрузке теста урока: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def finalize_lesson_test(db: Session, lesson_id: int) -> bool:
        """
        Зафинализировать тест урока (пометить как окончательный)
        """
        try:
            print(f"\n=== ФИНАЛИЗАЦИЯ ТЕСТА УРОКА ===")
            print(f"  lesson_id: {lesson_id}")
            
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson or not lesson.lesson_plan_json:
                print(f"  ОШИБКА: Не найден урок или lesson_plan_json пустой")
                return False
            
            print(f"  Найден урок: ID={lesson.lesson_id}")
            print(f"  lesson_plan_json до финализации: {lesson.lesson_plan_json}")
            
            # Загружаем существующие данные
            test_data = json.loads(lesson.lesson_plan_json)
            
            print(f"  Текущий is_finalized: {test_data.get('is_finalized', False)}")
            
            # Помечаем как финализированный
            test_data["is_finalized"] = True
            test_data["finalized_at"] = datetime.now().isoformat()
            
            print(f"  Новый is_finalized: {test_data.get('is_finalized', False)}")
            
            # Сохраняем обратно
            lesson.lesson_plan_json = json.dumps(test_data)
            db.commit()
            
            print(f"  Тест урока успешно финализирован")
            print(f"  lesson_plan_json после финализации: {lesson.lesson_plan_json}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"  ОШИБКА при финализации теста урока: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_lesson_data_for_test_generation(db: Session, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить данные урока для генерации теста
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        
        if not lesson:
            return None
        
        # Собираем данные урока для AI-генерации
        return {
            "lesson_id": lesson.lesson_id,
            "theory": lesson.theory_text or "",
            "reading": lesson.reading_text or "",
            "speaking": lesson.speaking_text or "",
            "is_access": lesson.is_access,
            "lesson_notes": lesson.lesson_notes or ""
        }
    
    @staticmethod
    def save_student_test_results(
        db: Session,
        lesson_id: int,
        student_id: int,
        test_results: Dict[str, Any]
    ) -> bool:
        """
        Сохранить результаты теста ученика в lesson_test_results_json
        """
        try:
            print(f"\n=== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ ТЕСТА УЧЕНИКА ===")
            print(f"  lesson_id: {lesson_id}")
            print(f"  student_id: {student_id}")
            
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson:
                print(f"  ОШИБКА: Не найден урок")
                return False
            
            print(f"  Найден урок: ID={lesson.lesson_id}")
            print(f"  Текущий lesson_test_results_json до сохранения: {lesson.lesson_test_results_json}")
            
            # Получаем текущие результаты или создаем новые
            current_results = {}
            if lesson.lesson_test_results_json:
                try:
                    current_results = json.loads(lesson.lesson_test_results_json)
                    print(f"  Загружены существующие результаты")
                except json.JSONDecodeError as e:
                    print(f"  ОШИБКА парсинга JSON: {e}, создаем новые результаты")
                    current_results = {}
            else:
                print(f"  lesson_test_results_json пустой, создаем новые результаты")
            
            # Добавляем результаты текущего ученика
            student_key = str(student_id)
            current_results[student_key] = {
                **test_results,
                "submitted_at": datetime.now().isoformat()
            }
            
            print(f"  Обновленные результаты для ученика {student_id}: {json.dumps(current_results[student_key], indent=2)}")
            
            # Сохраняем обратно
            lesson.lesson_test_results_json = json.dumps(current_results)
            db.commit()
            
            print(f"  Результаты успешно сохранены")
            print(f"  Новый lesson_test_results_json: {lesson.lesson_test_results_json}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"  ОШИБКА при сохранении результатов теста: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_student_test_results(
        db: Session,
        lesson_id: int,
        student_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получить результаты теста конкретного ученика из lesson_test_results_json
        """
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson or not lesson.lesson_test_results_json:
                return None
            
            try:
                results = json.loads(lesson.lesson_test_results_json)
                return results.get(str(student_id))
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            print(f"Ошибка получения результатов теста ученика: {e}")
            return None
    
    @staticmethod
    def get_all_students_test_results(db: Session, lesson_id: int) -> Dict[str, Any]:
        """
        Получить результаты всех учеников для урока
        """
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
            
            if not lesson or not lesson.lesson_test_results_json:
                return {}
            
            try:
                return json.loads(lesson.lesson_test_results_json)
            except json.JSONDecodeError:
                return {}
                
        except Exception as e:
            print(f"Ошибка получения результатов всех учеников: {e}")
            return {}
    
    @staticmethod
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