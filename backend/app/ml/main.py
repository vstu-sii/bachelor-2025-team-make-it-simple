"""
Основной модуль с функциями обработки и демонстрацией.
Если файл запускается напрямую - выполняется демонстрация.
Если импортируется - доступны функции обработки.
"""

import json
from typing import Optional
from app.ml.ai_tutor import AITutor

def run_demo():
    """Запуск демонстрации работы всех функций."""
    
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ AI-ТЬЮТОРА")
    print("=" * 80)
    
    # Инициализация тьютора
    try:
        tutor = AITutor()
    except Exception as e:
        print(f"✗ Ошибка инициализации AI-тьютора: {e}")
        print("Проверьте API ключ в config.py")
        return
    
    # Пример 1: Входной тест
    print("\n" + "=" * 80)
    print("1. ГЕНЕРАЦИЯ ВХОДНОГО ТЕСТА")
    print("=" * 80)
    
    entry_test_input = {
        "course_title": "Английский язык для начинающих",
        "topics": ["Present Simple", "Артикли a/an/the", "Базовая лексика"],
    }
    
    feedback = "Сделать больше вопросов на Present Simple, меньше на артикли. Добавить вопросы по базовой лексике."

    try:
        result = tutor.generate_entry_test(entry_test_input, feedback)
        print(f"\n✓ Сгенерирован тест с {len(result.get('questions', []))} вопросами")
        print(f"✓ Учтены замечания: {feedback}")
        if result.get('questions'):
            for i, q in enumerate(result['questions'][:2], 1):  # Показываем первые 2 вопроса
                q_text = q.get('question', 'Нет вопроса')
                print(f"  Вопрос {i}: {q_text[:60]}...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    # Пример 2: Граф курса
    print("\n" + "=" * 80)
    print("2. ГЕНЕРАЦИЯ ГРАФА КУРСА")
    print("=" * 80)
    
    graph_input = {
        "student_profile": {
            "interests": ["видеоигры", "футбол", "технологии"],
            "knowledge_gaps": ["present_simple", "prepositions"]
        },
        "course_title": "Английский язык для начинающих",
        "topics": [
            "Present Simple",
            "Артикли a/an/the", 
            "Базовая лексика: семья, работа, хобби",
            "Предлоги места и времени",
            "Вопросы с do/does"
        ]
    }
    
    graph_feedback = "Сделать граф более детальным. Добавить связи между темами. Учесть, что ученик интересуется технологиями."

    try:
        result = tutor.generate_course_graph(graph_input, graph_feedback)
        print(f"\n✓ Сгенерирован граф с {len(result.get('nodes', []))} узлами и {len(result.get('edges', []))} связями")
        print(f"✓ Учтены замечания: {graph_feedback}")

        # Покажем группы узлов
        groups = {}
        for node in result.get('nodes', []):
            group = node.get('group', 3)
            groups[group] = groups.get(group, 0) + 1
        
        print(f"  Распределение по группам: {groups}")
        
        # Покажем метки узлов
        print("  Узлы графа:")
        for node in result.get('nodes', []):
            print(f"    - {node.get('label', 'Без метки')} (группа: {node.get('group', '?')})")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    # Пример 3: Теория урока
    print("\n" + "=" * 80)
    print("3. ГЕНЕРАЦИЯ ТЕОРИИ УРОКА")
    print("=" * 80)
    
    theory_input = {
        "lesson_parameters": {
            "topic": "Present Simple",
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            }
        },
        "type": "theory"
    }

    theory_feedback = "Сделать объяснение более простым. Добавить больше примеров с играми и технологиями. Уделить внимание построению вопросов."

    try:
        result = tutor.generate_lesson_plan(theory_input, theory_feedback)
        print(f"\n✓ Сгенерирована теория урока")
        print(f"✓ Учтены замечания: {theory_feedback}")
        title = result.get('theory_section', {}).get('title', 'Нет заголовка')
        print(f"  Заголовок: {title}")
        content = result.get('theory_section', {}).get('content', '')
        print(f"  Длина контента: {len(content)} символов")
        
        # Покажем первые 200 символов контента
        if content and len(content) > 200:
            print(f"  Начало контента: {content[:200]}...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    # Пример 4: Задание на чтение
    print("\n" + "=" * 80)
    print("4. ГЕНЕРАЦИЯ ЗАДАНИЯ НА ЧТЕНИЕ")
    print("=" * 80)
    
    reading_input = {
        "lesson_parameters": {
            "topic": "Present Simple",
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            }
        },
        "type": "reading"
    }
    
    reading_feedback = "Сделать текст про геймера, который учит английский. Добавить детали про технологичные игры. Вопросы должны проверять понимание временных форм."

    try:
        result = tutor.generate_lesson_plan(reading_input, reading_feedback)
        print(f"\n✓ Сгенерировано задание на чтение")
        print(f"✓ Учтены замечания: {reading_feedback}")
        title = result.get('reading_section', {}).get('title', 'Нет заголовка')
        print(f"  Заголовок: {title}")
        text = result.get('reading_section', {}).get('text', '')
        print(f"  Длина текста: {len(text)} символов")
        questions = result.get('reading_section', {}).get('comprehension_questions', [])
        print(f"  Вопросов на понимание: {len(questions)}")
        
        # Покажем первый вопрос
        if questions:
            print(f"  Первый вопрос: {questions[0][:60]}...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    # Пример 5: Задание на говорение
    print("\n" + "=" * 80)
    print("5. ГЕНЕРАЦИЯ ЗАДАНИЯ НА ГОВОРЕНИЕ")
    print("=" * 80)
    
    speaking_input = {
        "lesson_parameters": {
            "topic": "Present Simple",
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            }
        },
        "type": "speaking"
    }
    
    speaking_feedback = "Тема: ежедневный распорядок геймера. Добавить подсказки по использованию наречий времени (usually, often, every day). Пример ответа должен быть развернутым."

    try:
        result = tutor.generate_lesson_plan(speaking_input, speaking_feedback)
        print(f"\n✓ Сгенерировано задание на говорение")
        print(f"✓ Учтены замечания: {speaking_feedback}")        
        title = result.get('speaking_section', {}).get('title', 'Нет заголовка')
        print(f"  Заголовок: {title}")
        instructions = result.get('speaking_section', {}).get('instructions', '')
        print(f"  Длина инструкций: {len(instructions)} символов")
        
        # Покажем пример ответа
        example = result.get('speaking_section', {}).get('example_response', '')
        if example:
            print(f"  Пример ответа: {example[:80]}...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    # Пример 6: Тест урока
    print("\n" + "=" * 80)
    print("6. ГЕНЕРАЦИЯ ТЕСТА УРОКА")
    print("=" * 80)
    
    test_input = {
        "lesson_parameters": {
            "topic": "Present Simple",
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            }
        },
        "theory": "Present Simple используется для описания регулярных действий и привычек. Структура: I/You/We/They + глагол (I play), He/She/It + глагол + s (He plays)."
    }
    
    test_feedback = "Сделать 5 вопросов: 2 на выбор правильной формы, 2 на заполнение пропусков, 1 открытый вопрос про игры."
    
    try:
        result = tutor.generate_lesson_test(test_input, test_feedback)
        print(f"\n✓ Сгенерирован тест урока")
        print(f"✓ Учтены замечания: {test_feedback}")
        
        test_section = result.get('test_section', {})
        questions = test_section.get('questions', [])
        print(f"  Количество вопросов: {len(questions)}")
        print(f"  Заголовок теста: {test_section.get('title', 'Нет заголовка')}")
        
        # Покажем первый вопрос
        if questions:
            first_q = questions[0]
            q_text = first_q.get('question', 'Нет вопроса')
            print(f"  Первый вопрос: {q_text[:60]}...")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

    # Пример 7: Оценка результатов
    print("\n" + "=" * 80)
    print("7. ОЦЕНКА РЕЗУЛЬТАТОВ УРОКА")
    print("=" * 80)
    
    evaluation_input = {
        "teachers_notes_about_speaking": "Студент хорошо описывал свой игровой распорядок, но делал ошибки в произношении окончаний -s для he/she/it. Испытывал трудности с построением вопросов.",
        "teachers_notes_about_reading": "Текст прочитал уверенно, ответил на вопросы по содержанию правильно. Понимание базового материала хорошее.",
        "test": {
            "wrong_answer_questions": [
                {
                    "question_id": "1",
                    "type": "single_choice",
                    "question": "Choose the correct sentence:",
                    "options": [
                        "I plays video games every day",
                        "I play video games every day", 
                        "I playing video games every day"
                    ],
                    "correct_answer": 1,
                    "student_answer": 2
                }
            ]
        }
    }
    
    evaluation_feedback = "Дать более строгую оценку за ошибки в тесте. Рекомендовать дополнительную практику с вопросами. Учесть, что ученик интересуется технологиями - предложить тематические упражнения."

    try:
        result = tutor.evaluate_lesson_results(evaluation_input, evaluation_feedback)
        print(f"\n✓ Оценка урока сгенерирована")
        print(f"✓ Учтены замечания: {evaluation_feedback}")
        print(f"  Оценка: {result.get('lesson_score', 'Нет оценки')}/10")
        gaps = result.get('knowledge_gaps', [])
        print(f"  Пробелы: {', '.join(gaps) if gaps else 'Нет пробелов'}")
        feedback = result.get('automated_feedback', '')
        if feedback and len(feedback) > 100:
            print(f"  Обратная связь: {feedback[:100]}...")
        else:
            print(f"  Обратная связь: {feedback}")
        print(f"  Доп. урок нужен: {result.get('additional_lesson', 'Не указано')}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
    
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)

# Запуск демонстрации только если файл выполняется напрямую
if __name__ == "__main__":
    run_demo()




# Экспортируемые функции для внешнего использования
def generate_entry_test(course_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация входного теста с учетом замечаний.
    
    Args:
        course_data: Данные о курсе
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированный тест
    """
    tutor = AITutor()
    return tutor.generate_entry_test(course_data, feedback)

def generate_course_graph(student_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация графа курса с учетом замечаний.
    
    Args:
        student_data: Данные о студенте и курсе
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированный граф
    """
    tutor = AITutor()
    return tutor.generate_course_graph(student_data, feedback)

def generate_lesson_theory(lesson_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация теории урока с учетом замечаний.
    
    Args:
        lesson_data: Данные для урока
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированная теория
    """
    lesson_data["type"] = "theory"
    tutor = AITutor()
    return tutor.generate_lesson_plan(lesson_data, feedback)

def generate_lesson_reading(lesson_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация задания на чтение с учетом замечаний.
    
    Args:
        lesson_data: Данные для урока
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированное задание на чтение
    """
    lesson_data["type"] = "reading"
    tutor = AITutor()
    return tutor.generate_lesson_plan(lesson_data, feedback)

def generate_lesson_speaking(lesson_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация задания на говорение с учетом замечаний.
    
    Args:
        lesson_data: Данные для урока
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированное задание на говорение
    """
    lesson_data["type"] = "speaking"
    tutor = AITutor()
    return tutor.generate_lesson_plan(lesson_data, feedback)

def generate_lesson_test(lesson_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация теста урока с учетом замечаний.
    
    Args:
        lesson_data: Данные для урока (должно содержать theory поле)
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        Сгенерированный тест
    """
    tutor = AITutor()
    return tutor.generate_lesson_test(lesson_data, feedback)

def evaluate_lesson_results(results_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Оценка результатов урока с учетом замечаний.
    
    Args:
        results_data: Данные с результатами
        feedback: Замечания репетитора по оценке (опционально)
        
    Returns:
        Оценка урока
    """
    tutor = AITutor()
    return tutor.evaluate_lesson_results(results_data, feedback)

# Функция для обратной совместимости
def generate_lesson_plan(lesson_data: dict, feedback: Optional[str] = None) -> dict:
    """
    Генерация плана урока (для обратной совместимости).
    
    Args:
        lesson_data: Данные для урока (должно содержать type поле)
        feedback: Замечания репетитора по генерации (опционально)
        
    Returns:
        План урока
    """
    tutor = AITutor()
    return tutor.generate_lesson_plan(lesson_data, feedback)