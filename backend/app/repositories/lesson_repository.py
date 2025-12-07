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
    def get_lesson_progress_from_json(db: Session, lesson_id: int, student_id: int) -> Dict[str, Any]:
        """
        Получить прогресс ученика по уроку из JSON полей
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            return {}
        
        # Проверяем результаты в results_json
        progress_data = {}
        if lesson.results_json:
            try:
                results = json.loads(lesson.results_json) if isinstance(lesson.results_json, str) else lesson.results_json
                # Ищем прогресс для конкретного ученика
                if isinstance(results, dict):
                    student_progress = results.get(str(student_id)) or results.get(student_id)
                    if student_progress:
                        progress_data = student_progress
            except:
                pass
        
        # Если нет в results_json, проверяем lesson_test_results_json
        if not progress_data and lesson.lesson_test_results_json:
            try:
                test_results = json.loads(lesson.lesson_test_results_json) if isinstance(lesson.lesson_test_results_json, str) else lesson.lesson_test_results_json
                if isinstance(test_results, dict):
                    student_results = test_results.get(str(student_id)) or test_results.get(student_id)
                    if student_results:
                        progress_data = {
                            "test_completed": True,
                            "test_score": student_results.get("score", 0),
                            "test_answers": student_results.get("answers", [])
                        }
            except:
                pass
        
        # Возвращаем прогресс
        return {
            "theory_completed": lesson.is_ended,  # is_ended может означать завершение теории
            "reading_completed": progress_data.get("reading_completed", False),
            "speaking_completed": progress_data.get("speaking_completed", False),
            "test_completed": progress_data.get("test_completed", False),
            "test_score": progress_data.get("test_score", 0),
            "details": progress_data
        }

    @staticmethod
    def update_lesson_progress_in_json(
        db: Session, 
        lesson_id: int, 
        student_id: int,
        progress_type: str,  # "theory", "reading", "speaking", "test"
        data: Dict[str, Any]
    ) -> bool:
        """
        Обновить прогресс ученика по уроку в JSON полях
        """
        lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
        if not lesson:
            return False
        
        try:
            # Получаем текущие результаты
            current_results = {}
            if lesson.results_json:
                current_results = json.loads(lesson.results_json) if isinstance(lesson.results_json, str) else lesson.results_json
            
            if not isinstance(current_results, dict):
                current_results = {}
            
            # Обновляем прогресс для ученика
            student_key = str(student_id)
            student_progress = current_results.get(student_key, {})
            
            if progress_type == "theory":
                student_progress["theory_completed"] = data.get("completed", True)
                if data.get("completed"):
                    lesson.is_ended = True
            elif progress_type == "reading":
                student_progress["reading_completed"] = data.get("completed", True)
            elif progress_type == "speaking":
                student_progress["speaking_completed"] = data.get("completed", True)
            elif progress_type == "test":
                student_progress["test_completed"] = data.get("completed", True)
                student_progress["test_score"] = data.get("score", 0)
                student_progress["test_answers"] = data.get("answers", [])
                
                # Также обновляем lesson_test_results_json
                test_results = {}
                if lesson.lesson_test_results_json:
                    test_results = json.loads(lesson.lesson_test_results_json) if isinstance(lesson.lesson_test_results_json, str) else lesson.lesson_test_results_json
                
                if not isinstance(test_results, dict):
                    test_results = {}
                
                test_results[student_key] = {
                    "score": data.get("score", 0),
                    "answers": data.get("answers", []),
                    "completed_at": data.get("completed_at")
                }
                lesson.lesson_test_results_json = json.dumps(test_results)
            
            # Обновляем notes если есть
            if "notes" in data:
                student_progress["notes"] = data["notes"]
            
            current_results[student_key] = student_progress
            lesson.results_json = json.dumps(current_results)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error updating lesson progress: {e}")
            return False

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
            
            # Также обновляем общий прогресс
            LessonRepository.update_lesson_progress_in_json(
                db, lesson_id, student_id, "test",
                {"completed": True, "score": score, "answers": answers}
            )
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving test results: {e}")
            return False