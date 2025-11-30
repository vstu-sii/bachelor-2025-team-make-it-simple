import json
import time
from models.baseline import BaselineModel
from evaluation.evaluator import ModelEvaluator

def demo_entry_test_generation():
    print("=== ДЕМО: Генерация входного тестирования ===")
    
    model = BaselineModel()
    
    test_input = {
        "course_title": "Английский язык для начинающих",
        "topics": [
            "Present Simple",
            "Артикли a/an/the", 
            "Базовая лексика: семья, работа, хобби"
        ],
        "materials": "Базовые правила английского языка для начинающих..."
    }
    
    print("Входные данные:")
    print(json.dumps(test_input, ensure_ascii=False, indent=2))
    print("\nГенерируем тест...")
    
    start_time = time.time()
    result = model.generate_entry_test(test_input)
    generation_time = time.time() - start_time
    
    print(f"\nРезультат (время генерации: {generation_time:.2f} сек):")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def demo_course_graph_generation():
    print("\n=== ДЕМО: Генерация графа курса ===")
    
    model = BaselineModel()
    
    graph_input = {
        "student_profile": {
            "interests": ["видеоигры", "футбол", "технологии"],
            "knowledge_gaps": ["prepositions", "present_simple"]
        },
        "course_title": "Английский язык для начинающих",
        "topics": [
            "Present Simple",
            "Артикли a/an/the",
            "Базовая лексика",
            "Предлоги места и времени", 
            "Вопросы с do/does"
        ]
    }
    
    print("Входные данные:")
    print(json.dumps(graph_input, ensure_ascii=False, indent=2))
    print("\nГенерируем граф...")
    
    start_time = time.time()
    result = model.generate_course_graph(graph_input)
    generation_time = time.time() - start_time
    
    print(f"\nРезультат (время генерации: {generation_time:.2f} сек):")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def demo_lesson_plan_generation():
    print("\n=== ДЕМО: Генерация плана урока ===")
    
    model = BaselineModel()
    
    lesson_input = {
        "lesson_parameters": {
            "topic": "Present Simple",
            "student_profile": {
                "interests": ["видеоигры", "футбол", "технологии"],
                "knowledge_gaps": ["present_simple", "prepositions"]
            }
        },
        "type": "theory"
    }
    
    print("Входные данные:")
    print(json.dumps(lesson_input, ensure_ascii=False, indent=2))
    print("\nГенерируем план урока...")
    
    start_time = time.time()
    result = model.generate_lesson_plan(lesson_input, "theory")
    generation_time = time.time() - start_time
    
    print(f"\nРезультат (время генерации: {generation_time:.2f} сек):")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def demo_lesson_evaluation():
    print("\n=== ДЕМО: Оценка результатов урока ===")
    
    model = BaselineModel()
    
    evaluation_input = {
        "teachers_notes_about_speaking": "Студент хорошо описывал свой игровой распорядок, но делал ошибки в окончаниях",
        "teachers_notes_about_reading": "Текст прочитал уверенно, ответил на вопросы правильно",
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
    
    print("Входные данные:")
    print(json.dumps(evaluation_input, ensure_ascii=False, indent=2))
    print("\nОцениваем результаты...")
    
    start_time = time.time()
    result = model.evaluate_lesson_results(evaluation_input)
    generation_time = time.time() - start_time
    
    print(f"\nРезультат (время генерации: {generation_time:.2f} сек):")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def run_evaluation():
    print("\n=== ОЦЕНКА КАЧЕСТВА МОДЕЛИ ===")
    
    model = BaselineModel()
    evaluator = ModelEvaluator(model)
    
    # Тестовые данные для оценки
    test_cases = [
        {
            'input': {
                'course_title': 'Test Course',
                'topics': ['Topic 1', 'Topic 2'],
                'materials': 'Test materials'
            },
            'expected_output_structure': {
                'questions': [
                    {
                        'question_id': 'string',
                        'type': 'string',
                        'question': 'string'
                    }
                ]
            }
        }
    ]
    
    results = evaluator.evaluate_entry_test_generation(test_cases)
    print("Результаты оценки:")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    print("Запуск демонстрации системы AI-репетитора...")
    
    try:
        demo_entry_test_generation()
        demo_course_graph_generation() 
        demo_lesson_plan_generation()
        demo_lesson_evaluation()
        run_evaluation()
        
        print("\n Демонстрация завершена успешно!")
        
    except Exception as e:
        print(f"\n Ошибка при демонстрации: {str(e)}")
