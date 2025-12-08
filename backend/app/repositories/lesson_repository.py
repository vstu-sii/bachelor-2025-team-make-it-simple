from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, text
import json
from typing import Dict, List, Optional, Any
from app.models.lesson import Lesson
from app.models.topic import Topic
from app.models.course_topic import CourseTopic
from app.models.user_course import UserCourse
from app.models.user import User

class LessonRepository:

    @staticmethod
    def get_lesson_by_id(db: Session, lesson_id: int) -> Optional[Lesson]:
        """
        Получить урок по ID
        """
        return db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()

    @staticmethod
    def get_lessons_by_course_via_graph(db: Session, course_id: int, student_id: int) -> Dict[str, Any]:
        """
        Получить уроки курса через граф из user_course
        Возвращает информацию об уроках и прогрессе
        """
        # Получаем user_course для ученика
        user_course = db.query(UserCourse).filter(
            and_(
                UserCourse.user_id == student_id,
                UserCourse.course_id == course_id
            )
        ).first()
        
        if not user_course or not user_course.graph_json:
            return {"lessons": [], "graph": None, "progress": {}}
        
        try:
            # Парсим граф
            graph_data = json.loads(user_course.graph_json) if isinstance(user_course.graph_json, str) else user_course.graph_json
            
            # Извлекаем lesson_id из узлов графа
            lesson_ids = []
            lesson_nodes = {}  # lesson_id -> node_id
            
            for node in graph_data.get('nodes', []):
                node_data = node.get('data', {})
                if node_data and 'lesson_id' in node_data:
                    lesson_id = node_data['lesson_id']
                    lesson_ids.append(lesson_id)
                    lesson_nodes[lesson_id] = node.get('id')
            
            if not lesson_ids:
                return {"lessons": [], "graph": graph_data, "progress": {}}
            
            # Получаем уроки
            lessons = db.query(Lesson).filter(Lesson.lesson_id.in_(lesson_ids)).all()
            
            # Формируем информацию об уроках
            lesson_info = []
            for lesson in lessons:
                # Получаем прогресс из results_json или lesson_test_results_json
                progress_data = {}
                if lesson.results_json:
                    try:
                        progress_data = json.loads(lesson.results_json) if isinstance(lesson.results_json, str) else lesson.results_json
                    except:
                        progress_data = {}
                
                # Определяем статус выполнения
                node_id = lesson_nodes.get(lesson.lesson_id)
                node_status = None
                if node_id:
                    for node in graph_data.get('nodes', []):
                        if node.get('id') == node_id:
                            node_status = node.get('group')  # 0-пройден, 1-не пройден, 2-доступен, 3-недоступен
                            break
                
                lesson_info.append({
                    "lesson_id": lesson.lesson_id,
                    "node_id": node_id,
                    "title": lesson.theory_text[:50] + "..." if lesson.theory_text and len(lesson.theory_text) > 50 else (lesson.theory_text or f"Урок {lesson.lesson_id}"),
                    "theory_text": lesson.theory_text,
                    "reading_text": lesson.reading_text,
                    "speaking_text": lesson.speaking_text,
                    "is_access": lesson.is_access,
                    "is_ended": lesson.is_ended,
                    "lesson_notes": lesson.lesson_notes,
                    "node_status": node_status,  # статус из графа (0,1,2,3)
                    "progress": progress_data,
                    "lesson_test": json.loads(lesson.lesson_test_json) if lesson.lesson_test_json and isinstance(lesson.lesson_test_json, str) else (lesson.lesson_test_json or {}),
                    "test_results": json.loads(lesson.lesson_test_results_json) if lesson.lesson_test_results_json and isinstance(lesson.lesson_test_results_json, str) else (lesson.lesson_test_results_json or {})
                })
            
            # Сортируем уроки по node_id или lesson_id
            lesson_info.sort(key=lambda x: (x["node_id"] or "", x["lesson_id"]))
            
            return {
                "lessons": lesson_info,
                "graph": graph_data,
                "user_course_id": user_course.user_course_id,
                "knowledge_gaps": user_course.knowledge_gaps
            }
            
        except Exception as e:
            print(f"Error parsing graph for course {course_id}, student {student_id}: {e}")
            return {"lessons": [], "graph": None, "progress": {}}

    @staticmethod
    def update_lesson_content(
        db: Session,
        lesson_id: int,
        content_type: str,  # "theory", "reading", "speaking", "test", "notes"
        content: str,
        is_access: bool = None,
        is_ended: bool = None
    ) -> Optional[Lesson]:
        """
        Обновить контент урока
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            return None
        
        try:
            if content_type == "theory":
                lesson.theory_text = content
            elif content_type == "reading":
                lesson.reading_text = content
            elif content_type == "speaking":
                lesson.speaking_text = content
            elif content_type == "test":
                lesson.lesson_test_json = content
            elif content_type == "notes":
                lesson.lesson_notes = content
            
            if is_access is not None:
                lesson.is_access = is_access
            
            if is_ended is not None:
                lesson.is_ended = is_ended
            
            db.commit()
            db.refresh(lesson)
            return lesson
            
        except Exception as e:
            db.rollback()
            print(f"Error updating lesson content: {e}")
            return None

    @staticmethod
    def get_lesson_test(db: Session, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить тест урока
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson or not lesson.lesson_test_json:
            return None
        
        try:
            return json.loads(lesson.lesson_test_json) if isinstance(lesson.lesson_test_json, str) else lesson.lesson_test_json
        except:
            return None

    @staticmethod
    def save_lesson_test_results(
        db: Session,
        lesson_id: int,
        student_id: int,
        answers: List[Dict[str, Any]],
        score: int
    ) -> bool:
        """
        Сохранить результаты теста урока
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            return False
        
        try:
            # Получаем текущие результаты
            current_results = {}
            if lesson.lesson_test_results_json:
                current_results = json.loads(lesson.lesson_test_results_json) if isinstance(lesson.lesson_test_results_json, str) else lesson.lesson_test_results_json
            
            if not isinstance(current_results, dict):
                current_results = {}
            
            # Добавляем результаты ученика
            student_key = str(student_id)
            current_results[student_key] = {
                "score": score,
                "answers": answers,
                "completed_at": text("NOW()")
            }
            
            lesson.lesson_test_results_json = json.dumps(current_results)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving test results: {e}")
            return False
        
    @staticmethod
    def update_lesson_content(
        db: Session,
        lesson_id: int,
        content_type: str,  # "theory", "reading", "speaking", "test", "notes", "access"
        content: str,
        is_access: bool = None,
        is_ended: bool = None
    ) -> Optional[Lesson]:
        """
        Обновить контент урока
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            return None
        
        try:
            if content_type == "theory":
                lesson.theory_text = content
            elif content_type == "reading":
                lesson.reading_text = content
            elif content_type == "speaking":
                lesson.speaking_text = content
            elif content_type == "test":
                lesson.lesson_test_json = content
            elif content_type == "notes":
                lesson.lesson_notes = content
            # Для типа "access" content игнорируется, важен только is_access
            
            if is_access is not None:
                lesson.is_access = is_access
            
            if is_ended is not None:
                lesson.is_ended = is_ended
            
            db.commit()
            db.refresh(lesson)
            return lesson
            
        except Exception as e:
            db.rollback()
            print(f"Error updating lesson content: {e}")
            return None