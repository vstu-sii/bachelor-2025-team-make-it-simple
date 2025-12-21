from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.course import Course
import json
from datetime import datetime
from typing import Dict, Any, Optional

class TestRepository:
    
    @staticmethod
    def get_test_status(db: Session, course_id: int) -> Dict[str, Any]:
        """
        Получить статус входного теста для курса
        """
        course = db.query(Course).filter(Course.course_id == course_id).first()
        
        if not course:
            return {
                "is_test_generated": False,
                "is_test_finalized": False,
                "questions_count": 0,
                "has_feedback": False
            }
        
        # Проверяем, есть ли сгенерированный тест В КУРСЕ
        test_data = None
        try:
            if course.input_test_json:
                test_data = json.loads(course.input_test_json)
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
            "course_id": course_id,
            "is_test_generated": is_test_generated,
            "is_test_finalized": is_test_finalized,
            "last_generation_time": test_data.get("generated_at") if test_data else None,
            "questions_count": questions_count,
            "has_feedback": has_feedback
        }
    
    @staticmethod
    def save_generated_test(
        db: Session, 
        course_id: int, 
        test_data: Dict[str, Any],
        feedback: Optional[str] = None,
        finalize: bool = False
    ) -> bool:
        """
        Сохранить сгенерированный тест В КУРС (в input_test_json)
        """
        try:
            print(f"\n=== СОХРАНЕНИЕ ТЕСТА В КУРС ===")
            print(f"  course_id: {course_id}")
            print(f"  feedback: {feedback}")
            print(f"  finalize: {finalize}")
            print(f"  Количество вопросов: {len(test_data.get('questions', []))}")
            
            course = db.query(Course).filter(Course.course_id == course_id).first()
            
            if not course:
                print(f"  ОШИБКА: Не найден курс с ID={course_id}")
                return False
            
            print(f"  Найден курс: ID={course.course_id}, title={course.title}")
            print(f"  Текущий input_test_json до сохранения: {course.input_test_json}")
            
            # Подготавливаем данные для сохранения
            test_data_to_save = {
                "questions": test_data.get("questions", []),
                "generation_id": f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{course_id}",
                "generated_at": datetime.now().isoformat(),
                "is_finalized": finalize,
                "feedback_used": feedback,
                "questions_count": len(test_data.get("questions", [])),
                "test_type": "entry_test"
            }
            
            print(f"  Данные для сохранения: {json.dumps(test_data_to_save, indent=2)}")
            
            # Сохраняем в поле input_test_json курса
            course.input_test_json = json.dumps(test_data_to_save)
            db.commit()
            
            print(f"  Тест успешно сохранен В КУРС")
            print(f"  Новый input_test_json: {course.input_test_json}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"  ОШИБКА при сохранении теста в курс: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_generated_test(db: Session, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить сгенерированный тест ИЗ КУРСА (из input_test_json)
        """
        try:
            print(f"\n=== ЗАГРУЗКА ТЕСТА ИЗ КУРСА ===")
            print(f"  course_id: {course_id}")
            
            course = db.query(Course).filter(Course.course_id == course_id).first()
            
            if not course:
                print(f"  ОШИБКА: Не найден курс")
                return None
            
            print(f"  Найден курс: ID={course.course_id}, title={course.title}")
            print(f"  input_test_json присутствует: {bool(course.input_test_json)}")
            
            if not course.input_test_json:
                print(f"  input_test_json пустой или None")
                return None
            
            try:
                test_data = json.loads(course.input_test_json)
                print(f"  JSON успешно распарсен")
                print(f"  Количество вопросов: {len(test_data.get('questions', []))}")
                print(f"  is_finalized: {test_data.get('is_finalized', False)}")
                print(f"  test_type: {test_data.get('test_type')}")
                return test_data
            except json.JSONDecodeError as e:
                print(f"  ОШИБКА парсинга JSON: {e}")
                print(f"  Содержимое input_test_json: {course.input_test_json[:500]}...")
                return None
                
        except Exception as e:
            print(f"  ОШИБКА при загрузке теста из курса: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def finalize_test(db: Session, course_id: int) -> bool:
        """
        Зафинализировать тест курса (пометить как окончательный)
        """
        try:
            print(f"\n=== ФИНАЛИЗАЦИЯ ТЕСТА КУРСА ===")
            print(f"  course_id: {course_id}")
            
            course = db.query(Course).filter(Course.course_id == course_id).first()
            
            if not course or not course.input_test_json:
                print(f"  ОШИБКА: Не найден курс или input_test_json пустой")
                return False
            
            print(f"  Найден курс: ID={course.course_id}, title={course.title}")
            print(f"  input_test_json до финализации: {course.input_test_json}")
            
            # Загружаем существующие данные
            test_data = json.loads(course.input_test_json)
            
            print(f"  Текущий is_finalized: {test_data.get('is_finalized', False)}")
            
            # Помечаем как финализированный
            test_data["is_finalized"] = True
            test_data["finalized_at"] = datetime.now().isoformat()
            
            print(f"  Новый is_finalized: {test_data.get('is_finalized', False)}")
            
            # Сохраняем обратно
            course.input_test_json = json.dumps(test_data)
            db.commit()
            
            print(f"  Тест успешно финализирован В КУРСЕ")
            print(f"  input_test_json после финализации: {course.input_test_json}")
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"  ОШИБКА при финализации теста в курсе: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_course_data(db: Session, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить данные курса для генерации теста
        """
        course = db.query(Course).filter(Course.course_id == course_id).first()
        
        if not course:
            return None
        
        return {
            "course_id": course.course_id,
            "course_title": course.title,
            "topics": [],  # Здесь можно добавить логику получения тем курса
            "created_at": course.created_at.isoformat() if course.created_at else None
        }