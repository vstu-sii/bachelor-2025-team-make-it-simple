from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.schemas.lesson import (
    LessonResponse, 
    CourseLessonsInfo,
    LessonTestSubmit,
    LessonContentUpdate,
    LessonGenerationRequest,
    GeneratedContentResponse
)
from app.utils.jwt import get_current_user
from app.ml.main import (
    generate_lesson_theory,
    generate_lesson_reading,
    generate_lesson_speaking
)

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    include_topic: bool = Query(False, description="Включать ли информацию о теме"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить информацию об уроке по ID
    """
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # ВАЖНОЕ ИСПРАВЛЕНИЕ: Если is_access не установлено, устанавливаем False
    if lesson.is_access is None:
        lesson.is_access = False
        db.commit()
        db.refresh(lesson)
    
    # Проверяем доступ к уроку
    if not lesson.is_access and current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Урок недоступен")
    
    # Вручную преобразуем JSON поля
    lesson_dict = {
        "lesson_id": lesson.lesson_id,
        "theory_text": lesson.theory_text,
        "reading_text": lesson.reading_text,
        "speaking_text": lesson.speaking_text,
        "lesson_notes": lesson.lesson_notes,
        "is_access": lesson.is_access,  # Теперь всегда будет False или True
        "is_ended": lesson.is_ended
    }
    
    # **ИЗМЕНЕНИЕ: Добавляем информацию о теме только если запрошено**
    if include_topic and lesson.topic_id:
        from app.models.topic import Topic
        topic = db.query(Topic).filter(Topic.topic_id == lesson.topic_id).first()
        if topic:
            lesson_dict["topic"] = {
                "topic_id": topic.topic_id,
                "title": topic.title,
                "description_text": topic.description_text
            }
    
    # Обрабатываем JSON поля
    if lesson.lesson_plan_json:
        if isinstance(lesson.lesson_plan_json, str):
            try:
                lesson_dict["lesson_plan_json"] = json.loads(lesson.lesson_plan_json)
            except:
                lesson_dict["lesson_plan_json"] = lesson.lesson_plan_json
        else:
            lesson_dict["lesson_plan_json"] = lesson.lesson_plan_json
    
    if lesson.results_json:
        if isinstance(lesson.results_json, str):
            try:
                lesson_dict["results_json"] = json.loads(lesson.results_json)
            except:
                lesson_dict["results_json"] = lesson.results_json
        else:
            lesson_dict["results_json"] = lesson.results_json
    
    return lesson_dict


@router.get("/course/{course_id}/info", response_model=CourseLessonsInfo)
def get_course_lessons_info(
    course_id: int,
    student_id: Optional[int] = Query(None, description="ID ученика (для репетитора)"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить информацию об уроках курса через граф
    """
    # Проверяем доступ к курсу
    from app.models.user_course import UserCourse
    user_course = db.query(UserCourse).filter(
        UserCourse.user_id == current_user.user_id,
        UserCourse.course_id == course_id
    ).first()
    
    if not user_course:
        raise HTTPException(status_code=403, detail="Нет доступа к этому курсу")
    
    # Определяем student_id для получения прогресса
    target_student_id = student_id if student_id else current_user.user_id
    
    # Проверяем права доступа
    if student_id and current_user.role == "Репетитор":
        # Репетитор может смотреть прогресс своих учеников
        # Проверяем, что ученик на курсе репетитора
        student_course = db.query(UserCourse).filter(
            UserCourse.user_id == student_id,
            UserCourse.course_id == course_id
        ).first()
        
        if not student_course:
            raise HTTPException(status_code=403, detail="Ученик не найден на этом курсе")
    elif student_id and current_user.user_id != student_id:
        raise HTTPException(status_code=403, detail="Нет доступа к прогрессу другого ученика")
    
    return LessonRepository.get_lessons_by_course_via_graph(db, course_id, target_student_id)

@router.put("/{lesson_id}/content")
def update_lesson_content(
    lesson_id: int,
    content_update: LessonContentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Обновить контент урока (только для репетитора)
    """
    # Проверяем, что пользователь - репетитор
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут обновлять контент уроков")
    
    lesson = LessonRepository.update_lesson_content(
        db, lesson_id, 
        content_update.content_type,
        content_update.content,
        content_update.is_access,
        content_update.is_ended
    )
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    return {"message": "Контент обновлен", "lesson": lesson}

@router.get("/{lesson_id}/test")
def get_lesson_test(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить тест урока
    """
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Проверяем доступ
    if not lesson.is_access and current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Тест недоступен")
    
    test_data = LessonRepository.get_lesson_test(db, lesson_id)
    if not test_data:
        raise HTTPException(status_code=404, detail="Тест не найден")
    
    return test_data

@router.post("/{lesson_id}/test/submit/{student_id}")
def submit_lesson_test(
    lesson_id: int,
    student_id: int,
    test_data: LessonTestSubmit,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Отправить результаты теста урока
    """
    # Проверяем права доступа
    if current_user.user_id != student_id:
        raise HTTPException(status_code=403, detail="Можно отправлять только свои результаты")
    
    success = LessonRepository.save_lesson_test_results(
        db, lesson_id, student_id,
        test_data.answers, test_data.score
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка сохранения результатов")
    
    return {"message": "Результаты сохранены", "score": test_data.score}

@router.post("/{lesson_id}/generate/{section}", response_model=GeneratedContentResponse)
async def generate_lesson_section(
    lesson_id: int,
    section: str,  # theory, reading, speaking
    request: LessonGenerationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сгенерировать контент для раздела урока через AI (только для репетитора)
    """
    # Проверяем, что пользователь - репетитор
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут генерировать контент")
    
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # **ВОССТАНАВЛИВАЕМ получение темы урока - она нужна для AI-генератора**
    topic = None
    if lesson.topic_id:
        from app.models.topic import Topic
        topic = db.query(Topic).filter(Topic.topic_id == lesson.topic_id).first()
    
    # Получаем профиль ученика из курса
    from app.models.user_course import UserCourse
    user_courses = db.query(UserCourse).filter(UserCourse.course_id == request.course_id).all()
    
    interests = []
    knowledge_gaps = []
    
    for uc in user_courses:
        # Получаем пользователя
        from app.models.user import User
        user = db.query(User).filter(User.user_id == uc.user_id).first()
        if user and user.interests:
            interests.append(user.interests)
        if uc.knowledge_gaps:
            knowledge_gaps.append(uc.knowledge_gaps)
    
    # Создаём данные для генерации
    lesson_data = {
        "lesson_parameters": {
            "topic": topic.title if topic else "Общая тема",  # **ВОССТАНАВЛИВАЕМ тему**
            "student_profile": {
                "interests": interests[:3] if interests else ["общие интересы"],
                "knowledge_gaps": knowledge_gaps[:3] if knowledge_gaps else ["базовая грамматика"]
            }
        },
        "type": section
    }
    
    try:
        generated_content = ""
        
        if section == "theory":
            # Генерация теоретической части
            ai_response = generate_lesson_theory(lesson_data, request.feedback)
            generated_content = ai_response.get("theory_section", {}).get("content", "")
            
        elif section == "reading":
            # Генерация задания на чтение
            ai_response = generate_lesson_reading(lesson_data, request.feedback)
            reading_section = ai_response.get("reading_section", {})
            text = reading_section.get("text", "")
            questions = reading_section.get("comprehension_questions", [])
            
            # Форматируем для отображения
            generated_content = f"{text}\n\nВопросы на понимание:\n"
            for i, question in enumerate(questions, 1):
                generated_content += f"{i}. {question}\n"
                
        elif section == "speaking":
            # Генерация задания на говорение
            ai_response = generate_lesson_speaking(lesson_data, request.feedback)
            speaking_section = ai_response.get("speaking_section", {})
            title = speaking_section.get("title", "")
            instructions = speaking_section.get("instructions", "")
            example = speaking_section.get("example_response", "")
            
            # Форматируем для отображения
            generated_content = f"{title}\n\n{instructions}\n\nПример ответа:\n{example}"
        
        else:
            raise HTTPException(status_code=400, detail="Некорректный тип раздела")
        
        return GeneratedContentResponse(
            section=section,
            generated_content=generated_content,
            feedback=request.feedback
        )
        
    except Exception as e:
        print(f"Ошибка генерации контента: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации: {str(e)}")

@router.get("/{lesson_id}/students-progress")
def get_lesson_students_progress(
    lesson_id: int,
    course_id: int = Query(..., description="ID курса для фильтрации"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить прогресс учеников для конкретного урока
    """
    # Проверяем, что пользователь - репетитор
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут просматривать прогресс учеников")
    
    # Получаем всех учеников, которые проходят этот курс
    from app.models.user_course import UserCourse
    
    # Находим user_course для учеников на этом курсе
    user_courses = db.query(UserCourse).filter(
        UserCourse.course_id == course_id,
        UserCourse.user_id != current_user.user_id  # исключаем репетитора
    ).all()
    
    # Получаем информацию о пользователях
    from app.models.user import User
    from app.models.lesson import Lesson
    
    result = []
    
    # Берем урок, чтобы проверить результаты
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        return result
    
    for uc in user_courses:
        # Проверяем, что пользователь - ученик
        student = db.query(User).filter(
            User.user_id == uc.user_id,
            User.role == "Ученик"
        ).first()
        
        if student:
            student_data = {
                "student_id": student.user_id,
                "student_name": f"{student.first_name} {student.last_name}",
                "theory_completed": False,
                "reading_completed": False,
                "speaking_completed": False,
                "test_completed": False,
                "test_score": 0,
                "requires_retry": False
            }
            
            # Проверяем результаты урока
            if lesson.results_json:
                try:
                    results = json.loads(lesson.results_json) if isinstance(lesson.results_json, str) else lesson.results_json
                    student_key = str(student.user_id)
                    if student_key in results:
                        student_data.update(results[student_key])
                except:
                    pass
            
            # Проверяем результаты теста
            if lesson.lesson_test_results_json:
                try:
                    test_results = json.loads(lesson.lesson_test_results_json) if isinstance(lesson.lesson_test_results_json, str) else lesson.lesson_test_results_json
                    student_key = str(student.user_id)
                    if student_key in test_results:
                        student_data["test_score"] = test_results[student_key].get("score", 0)
                        student_data["test_completed"] = True
                except:
                    pass
            
            result.append(student_data)
    
    return result