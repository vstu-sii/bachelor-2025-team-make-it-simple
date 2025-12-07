from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.repositories.lesson_repository import LessonRepository
from app.schemas.lesson import (
    LessonCreate, 
    LessonResponse, 
    LessonUpdate,
    LessonProgress,
    CourseLessonsInfo,
    LessonTestSubmit,
    LessonContentUpdate,
    LessonProgressUpdate
)
from app.utils.jwt import get_current_user
import json

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить информацию об уроке по ID
    """
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Проверяем доступ к уроку (если is_access=False, то только репетитор может видеть)
    if not lesson.is_access and current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Урок недоступен")
    
    return lesson

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

@router.get("/{lesson_id}/progress/{student_id}", response_model=LessonProgress)
def get_lesson_progress(
    lesson_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить прогресс ученика по уроку
    """
    # Получаем урок
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Проверяем права доступа
    if current_user.user_id == student_id:
        # Ученик смотрит свой прогресс
        pass
    elif current_user.role == "Репетитор":
        # Репетитор может смотреть прогресс учеников
        # Нужно проверить, что урок связан с курсом репетитора
        # Это сложно, так как нет прямой связи урок-курс
        # Пока разрешим репетиторам смотреть любой прогресс
        pass
    else:
        raise HTTPException(status_code=403, detail="Нет доступа к этому прогрессу")
    
    progress = LessonRepository.get_lesson_progress_from_json(db, lesson_id, student_id)
    return LessonProgress(**progress)

@router.put("/{lesson_id}/progress/{student_id}")
def update_lesson_progress(
    lesson_id: int,
    student_id: int,
    progress_update: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Обновить прогресс ученика по уроку
    """
    # Проверяем права доступа
    if current_user.user_id == student_id:
        # Ученик обновляет свой прогресс
        pass
    elif current_user.role == "Репетитор":
        # Репетитор может обновлять прогресс учеников
        pass
    else:
        raise HTTPException(status_code=403, detail="Нет доступа для обновления прогресса")
    
    success = LessonRepository.update_lesson_progress_in_json(
        db, lesson_id, student_id, 
        progress_update.progress_type, 
        progress_update.data
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка обновления прогресса")
    
    return {"message": "Прогресс обновлен"}

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

@router.post("/{lesson_id}/generate/{section}")
def generate_lesson_section(
    lesson_id: int,
    section: str,  # theory, reading, speaking
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Сгенерировать контент для раздела урока (через ИИ) - только для репетитора
    """
    # Проверяем, что пользователь - репетитор
    if current_user.role != "Репетитор":
        raise HTTPException(status_code=403, detail="Только репетиторы могут генерировать контент")
    
    lesson = LessonRepository.get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    # Заглушка для генерации через ИИ
    # В реальности здесь будет интеграция с ИИ API
    
    lesson_title = lesson.theory_text[:50] + "..." if lesson.theory_text and len(lesson.theory_text) > 50 else f"Урок {lesson_id}"
    
    generated_content = {
        "theory": f"# Сгенерированная теоретическая часть\n\n**Тема:** {lesson_title}\n**Комментарий:** {comment or 'нет'}\n\n## Основные правила:\n\n1. **Правило 1:** Описание правила 1\n2. **Правило 2:** Описание правила 2\n3. **Примеры использования:**\n   - Пример 1\n   - Пример 2\n   - Пример 3\n\n## Упражнения:\n1. Упражнение 1\n2. Упражнение 2",
        
        "reading": f"# Задание на чтение\n\n**Тема:** {lesson_title}\n**Комментарий:** {comment or 'нет'}\n\n## Текст для чтения:\n\nRead the following text carefully:\n\n\"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\"\n\n## Вопросы:\n\n1. What is the main idea of the text?\n2. Find three key points in the text.\n3. What would be a good title for this text?",
        
        "speaking": f"# Задание на говорение\n\n**Тема:** {lesson_title}\n**Комментарий:** {comment or 'нет'}\n\n## Упражнения для практики говорения:\n\n### Диалоговая практика:\n1. **Role-play:** Practice a conversation about daily routines.\n2. **Discussion:** Discuss your favorite hobbies and activities.\n\n### Монологи:\n1. **Describe:** Describe your last vacation in 2-3 minutes.\n2. **Explain:** Explain how to cook your favorite dish.\n\n### Вопросы для обсуждения:\n1. What are your plans for the weekend?\n2. How do you usually spend your free time?\n3. What was the best day of your life?"
    }
    
    return {
        "section": section,
        "generated_content": generated_content.get(section, ""),
        "comment": comment
    }

@router.get("/{lesson_id}/topic")
def get_lesson_topic(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Получить информацию о теме урока
    """
    from app.models.lesson import Lesson
    from app.models.topic import Topic
    
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    
    if not lesson.topic_id:
        raise HTTPException(status_code=404, detail="Урок не привязан к теме")
    
    topic = db.query(Topic).filter(Topic.topic_id == lesson.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    
    # Находим курсы, к которым относится эта тема
    from app.models.course_topic import CourseTopic
    course_topics = db.query(CourseTopic).filter(
        CourseTopic.topic_id == lesson.topic_id
    ).all()
    
    courses = []
    for ct in course_topics:
        from app.models.course import Course
        course = db.query(Course).filter(Course.course_id == ct.course_id).first()
        if course:
            courses.append({
                "course_id": course.course_id,
                "course_title": course.title
            })
    
    return {
        "topic_id": topic.topic_id,
        "topic_title": topic.title,
        "topic_description": topic.description_text,
        "lesson_id": lesson.lesson_id,
        "courses": courses
    }