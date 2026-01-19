import json

class PromptTemplates:
    
    @staticmethod
    def entry_test_prompt(course_title, topics, materials_context):
        return f"""
        Ты - эксперт по созданию образовательных тестов. Создай входной тест для курса "{course_title}".
        
        ТЕМЫ КУРСА:
        {json.dumps(topics, ensure_ascii=False, indent=2)}
        
        МАТЕРИАЛЫ КУРСА:
        {materials_context}
        
        ТРЕБОВАНИЯ:
        1. Создай 10-15 вопросов разных типов:
           - short_answer (короткий ответ)
           - single_choice (одиночный выбор) 
           - multiple_choice (множественный выбор)
           - gaps_choice (заполнение пропусков)
        
        2. Вопросы должны охватывать все темы курса
        3. Время выполнения: 30 минут
        
        ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
        {{
            "questions": [
                {{
                    "question_id": "1",
                    "type": "short_answer", 
                    "question": "текст вопроса",
                    "max_length": 50,
                    "correct_answer": "правильный ответ"
                }},
                {{
                    "question_id": "2",
                    "type": "single_choice",
                    "question": "текст вопроса", 
                    "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
                    "correct_answer": 1
                }},
                {{
                    "question_id": "3", 
                    "type": "multiple_choice",
                    "question": "текст вопроса",
                    "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
                    "correct_answers": [0, 2]
                }},
                {{
                    "question_id": "4",
                    "type": "gaps_choice", 
                    "question": "текст с [1] пропусками [2]",
                    "gaps": [
                        {{
                            "gap_id": 1,
                            "options": ["вариант1", "вариант2", "вариант3"],
                            "correct_answer": 0
                        }},
                        {{
                            "gap_id": 2, 
                            "options": ["вариант1", "вариант2", "вариант3"],
                            "correct_answer": 1
                        }}
                    ]
                }}
            ]
        }}
        """
    
    @staticmethod
    def course_graph_prompt(student_profile, course_title, topics):
        return f"""
        Ты - эксперт по образовательным траекториям. Создай персонализированный граф обучения.
        
        ПРОФИЛЬ УЧЕНИКА:
        Интересы: {student_profile['interests']}
        Пробелы в знаниях: {student_profile['knowledge_gaps']}
        
        КУРС: {course_title}
        ТЕМЫ: {topics}
        
        ТРЕБОВАНИЯ:
        1. Создай граф зависимостей между темами
        2. Учти пробелы в знаниях ученика
        3. Определи порядок изучения тем
        
        ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
        {{
            "nodes": [
                {{
                    "id": "1",
                    "label": "Название темы"
                }}
            ],
            "edges": [
                {{
                    "from": "1", 
                    "to": "2"
                }}
            ]
        }}
        """
    
    @staticmethod
    def lesson_plan_prompt(lesson_parameters, lesson_type, theory_context=""):
        student_profile = lesson_parameters['student_profile']
        
        base_prompt = f"""
        Ты - опытный преподаватель. Создай персонализированный план урока.
        
        ТЕМА УРОКА: {lesson_parameters['topic']}
        ИНТЕРЕСЫ УЧЕНИКА: {student_profile['interests']}
        ПРОБЕЛЫ В ЗНАНИЯХ: {student_profile['knowledge_gaps']}
        """
        
        if lesson_type == "theory":
            return base_prompt + f"""
            ТИП УРОКА: Теоретическое занятие
            
            ТРЕБОВАНИЯ:
            1. Объясни тему простым языком
            2. Используй примеры из интересов ученика
            3. Учти пробелы в знаниях
            4. Структурируй материал логически
            
            ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
            {{
                "theory_section": {{
                    "title": "Название раздела",
                    "content": "Текст теории с примерами..."
                }}
            }}
            """
        
        elif lesson_type == "reading":
            return base_prompt + f"""
            ТИП УРОКА: Чтение и понимание
            
            ТРЕБОВАНИЯ:
            1. Напиши интересный текст на тему урока
            2. Используй vocabulary из интересов ученика  
            3. Добавь 3-5 вопросов на понимание
            4. Уровень сложности - соответствующий теме
            
            ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
            {{
                "reading_section": {{
                    "title": "Название текста",
                    "text": "Текст для чтения...",
                    "comprehension_questions": [
                        "Вопрос 1?",
                        "Вопрос 2?",
                        "Вопрос 3?"
                    ]
                }}
            }}
            """
        
        elif lesson_type == "speaking":
            return base_prompt + """
            ТИП УРОКА: Разговорная практика
            
            ТРЕБОВАНИЯ:
            1. Создай задание для устной практики
            2. Тема должна быть связана с интересами ученика
            3. Учти пробелы в знаниях
            4. Дай четкие инструкции
            
            ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
            {
                "speaking_section": {
                    "title": "Название задания",
                    "instructions": "Подробные инструкции..."
                }
            }
            """
        
        elif lesson_type == "test":
            return base_prompt + f"""
            ТИП УРОКА: Тестирование
            
            ТЕОРЕТИЧЕСКАЯ ЧАСТЬ (для справки):
            {theory_context}
            
            ТРЕБОВАНИЯ:
            1. Создай тест на 15-20 минут
            2. 5-8 вопросов разных типов
            3. Вопросы должны проверять понимание теории
            4. Учти интересы ученика в формулировках
            
            ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
            {
                "test_section": {
                    "title": "Название теста",
                    "questions": [
                    {{
                        "question_id": "1",
                        "type": "short_answer", 
                        "question": "текст вопроса",
                        "max_length": 50,
                        "correct_answer": "правильный ответ"
                    }},
                    {{
                        "question_id": "2",
                        "type": "single_choice",
                        "question": "текст вопроса", 
                        "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
                        "correct_answer": 1
                    }},
                    {{
                        "question_id": "3", 
                        "type": "multiple_choice",
                        "question": "текст вопроса",
                        "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
                        "correct_answers": [0, 2]
                    }},
                    {{
                        "question_id": "4",
                        "type": "gaps_choice", 
                        "question": "текст с [1] пропусками [2]",
                        "gaps": [
                            {{
                                "gap_id": 1,
                                "options": ["вариант1", "вариант2", "вариант3"],
                                "correct_answer": 0
                            }},
                            {{
                                "gap_id": 2, 
                                "options": ["вариант1", "вариант2", "вариант3"],
                                "correct_answer": 1
                            }}
                        ]
                    }}
                    ]
                }
            }
            """
    
    @staticmethod
    def lesson_evaluation_prompt(teachers_notes, test_results):
        return f"""
        Ты - опытный преподаватель-эксперт. Проанализируй результаты урока и дай оценку.
        
        ЗАМЕТКИ ПРЕПОДАВАТЕЛЯ:
        Говорение: {teachers_notes.get('teachers_notes_about_speaking', 'Нет заметок')}
        Чтение: {teachers_notes.get('teachers_notes_about_reading', 'Нет заметок')}
        
        РЕЗУЛЬТАТЫ ТЕСТА:
        {json.dumps(test_results, ensure_ascii=False, indent=2)}
        
        ТРЕБОВАНИЯ:
        1. Проанализируй ошибки в тесте
        2. Учти заметки преподавателя
        3. Поставь итоговую оценку от 1 до 10
        4. Определи пробелы в знаниях
        5. Рекомендуй нужен ли ещё дополнительный урок
        
        ВЕРНИ ОТВЕТ В ФОРМАТЕ JSON:
        {
            "lesson_score": "8",
            "knowledge_gaps": ["список пробелов"],
            "automated_feedback": "текст обратной связи", 
            "additional_lesson": "True/False"
        }
        """