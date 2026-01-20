"""
Основной модуль с функциями обработки и демонстрацией.
Если файл запускается напрямую - выполняется демонстрация.
Если импортируется - доступны функции обработки.
"""

import json
from ai_tutor import AITutor

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
        "materials": ["учебник Unit 1", "рабочая тетрадь Lesson 1"]
    }
    
    try:
        result = tutor.generate_entry_test(entry_test_input)
        print(f"\n✓ Сгенерирован тест с {len(result.get('questions', []))} вопросами")
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
    
    try:
        result = tutor.generate_course_graph(graph_input)
        print(f"\n✓ Сгенерирован граф с {len(result.get('nodes', []))} узлами и {len(result.get('edges', []))} связями")
        
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
    
    try:
        result = tutor.generate_lesson_plan(theory_input)
        print(f"\n✓ Сгенерирована теория урока")
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
    
    try:
        result = tutor.generate_lesson_plan(reading_input)
        print(f"\n✓ Сгенерировано задание на чтение")
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
    
    try:
        result = tutor.generate_lesson_plan(speaking_input)
        print(f"\n✓ Сгенерировано задание на говорение")
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
    
    # Пример 6: Оценка результатов
    print("\n" + "=" * 80)
    print("6. ОЦЕНКА РЕЗУЛЬТАТОВ УРОКА")
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
    
    try:
        result = tutor.evaluate_lesson_results(evaluation_input)
        print(f"\n✓ Оценка урока сгенерирована")
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
