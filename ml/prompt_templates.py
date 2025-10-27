import json
import re

class PromptTemplates:
    """Шаблоны промптов для различных задач системы"""
    
    @staticmethod
    def generate_placement_test(course_topics, student_interests=None):
        """Генерация входного тестирования"""
        interests_context = ""
        if student_interests:
            interests_context = f"Учти интересы ученика: {student_interests}. "
            
        prompt = f"""
        Ты - опытный преподаватель. Создай входной тест для оценки начальных знаний ученика.
        
        Курс охватывает темы: {course_topics}
        {interests_context}
        
        Создай тест в формате JSON со следующими типами вопросов:
        1. Вопросы с коротким ответом (2-3 вопроса)
        2. Вопросы с однозначным выбором (3-4 вопроса) 
        3. Вопросы с множественным выбором (2-3 вопроса)
        4. Вопросы на соответствие (1-2 вопроса)
        5. Задание с развёрнутым ответом (1 задание)
        
        Требования:
        - Вопросы должны охватывать разные темы курса
        - Уровень сложности - от простого к сложному
        - Включи интересы ученика в формулировки где это уместно
        - Для вопросов с выбором предоставь 3-4 варианта ответа
        - Укажи правильные ответы
        - Для развёрнутого задания опиши критерии оценки
        
        Верни ответ ТОЛЬКО в формате JSON без дополнительного текста.
        
        Пример структуры:
        {{
            "test_title": "Название теста",
            "questions": [
                {{
                    "type": "short_answer",
                    "question": "Текст вопроса",
                    "correct_answer": "правильный ответ"
                }},
                {{
                    "type": "single_choice", 
                    "question": "Текст вопроса",
                    "options": ["вариант1", "вариант2", "вариант3"],
                    "correct_answer": 0
                }},
                {{
                    "type": "multiple_choice",
                    "question": "Текст вопроса", 
                    "options": ["вариант1", "вариант2", "вариант3", "вариант4"],
                    "correct_answers": [0, 2]
                }},
                {{
                    "type": "matching",
                    "question": "Сопоставьте понятия",
                    "pairs": [
                        {{"left": "понятие1", "right": "определение1"}},
                        {{"left": "понятие2", "right": "определение2"}}
                    ]
                }},
                {{
                    "type": "essay",
                    "question": "Текст задания",
                    "evaluation_criteria": ["критерий1", "критерий2", "критерий3"]
                }}
            ]
        }}
        """
        return prompt
    
    @staticmethod
    def generate_learning_graph(course_topics, student_knowledge_gaps, student_interests):
        """Генерация графа обучения"""
        prompt = f"""
        Ты - эксперт по образовательным технологиям. Создай персонализированный граф обучения.
        
        Темы курса: {course_topics}
        Пробелы в знаниях ученика: {student_knowledge_gaps}
        Интересы ученика: {student_interests}
        
        Создай граф в формате JSON для визуализации в vis.js. Граф должен показывать:
        - Узлы (темы для изучения)
        - Связи между темами (зависимости)
        - Рекомендуемую последовательность изучения
        - Приоритетные темы на основе пробелов
        
        Структура графа:
        - nodes: список тем с атрибутами (id, label, level, priority, estimated_time)
        - edges: связи между темами (from, to, type)
        
        Учти:
        - Начинай с базовых тем, которые закрывают пробелы
        - Свяжи темы с интересами ученика
        - Оцени время изучения каждой темы (в часах)
        - Определи приоритеты (high, medium, low)
        
        Верни ответ ТОЛЬКО в формате JSON.
        
        Пример:
        {{
            "nodes": [
                {{"id": 1, "label": "Базовые понятия", "level": "beginner", "priority": "high", "estimated_time": 2}},
                {{"id": 2, "label": "Продвинутые темы", "level": "intermediate", "priority": "medium", "estimated_time": 3}}
            ],
            "edges": [
                {{"from": 1, "to": 2, "type": "prerequisite"}}
            ]
        }}
        """
        return prompt
    
    @staticmethod
    def generate_lesson_plan(lesson_topic, course_materials, student_interests, student_level):
        """Генерация плана урока"""
        prompt = f"""
        Ты - творческий преподаватель. Создай персонализированный план урока.
        
        Тема урока: {lesson_topic}
        Материалы курса: {course_materials}
        Интересы ученика: {student_interests}
        Уровень ученика: {student_level}
        
        Создай план урока в формате JSON включающий:
        1. Цели урока
        2. План занятия (временные отрезки)
        3. Теоретическую часть с примерами из интересов ученика
        4. Практические задания
        5. Тестовые вопросы разных типов
        6. Домашнее задание
        
        Формат вопросов должен быть разнообразным:
        - Короткие ответы
        - Выбор вариантов
        - Соответствия
        - Вопросы с развёрнутым ответом
        
        Верни ответ ТОЛЬКО в формате JSON.
        
        Пример структуры:
        {{
            "lesson_title": "Название урока",
            "objectives": ["цель1", "цель2"],
            "timeline": [
                {{"time": "0-10min", "activity": "Введение", "description": "..."}},
                {{"time": "10-30min", "activity": "Теория", "description": "..."}}
            ],
            "theory_content": "Теоретический материал с примерами...",
            "practice_questions": [
                {{
                    "type": "short_answer",
                    "question": "Вопрос...",
                    "correct_answer": "ответ"
                }}
            ],
            "test_questions": [
                {{
                    "type": "multiple_choice",
                    "question": "Тестовый вопрос...",
                    "options": ["вариант1", "вариант2", "вариант3"],
                    "correct_answers": [0],
                    "explanation": "Объяснение правильного ответа"
                }}
            ],
            "homework": {{
                "tasks": ["задание1", "задание2"],
                "deadline": "1 неделя"
            }}
        }}
        """
        return prompt
    
    @staticmethod
    def generate_progress_report(student_performance, lesson_feedback, test_results):
        """Генерация отчёта о прогрессе"""
        prompt = f"""
        Ты - внимательный педагог. Проанализируй результаты урока и создай отчёт.
        
        Результаты тестирования: {test_results}
        Комментарии преподавателя: {lesson_feedback}
        Общая успеваемость: {student_performance}
        
        Создай детальный отчёт в формате JSON включающий:
        1. Общую оценку прогресса
        2. Анализ ошибок и пробелов
        3. Рекомендации по улучшению
        4. План работы над ошибками
        5. Оценку мотивации и вовлечённости
        
        Будь конкретным в рекомендациях. Укажи конкретные темы для повторения.
        
        Верни ответ ТОЛЬКО в формате JSON.
        
        Пример:
        {{
            "overall_progress": "хороший",
            "strengths": ["сильная сторона1", "сильная сторона2"],
            "weaknesses": ["слабая сторона1", "слабая сторона2"],
            "error_analysis": [
                {{"topic": "тема1", "error_type": "тип ошибки", "recommendation": "рекомендация"}}
            ],
            "improvement_plan": [
                {{"action": "повторить тему X", "priority": "high", "time_estimate": "1 час"}}
            ],
            "motivation_level": "high",
            "next_steps": "рекомендации для следующего урока"
        }}
        """
        return prompt

class ResponseValidator:
    """Валидация ответов LLM"""
    
    @staticmethod
    def validate_json_response(response_text):
        """Проверка и исправление JSON ответа"""
        try:
            # Пытаемся распарсить JSON
            data = json.loads(response_text)
            return data, True
        except json.JSONDecodeError:
            # Пытаемся извлечь JSON из текста
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data, True
                except:
                    pass
            return None, False
    
    @staticmethod
    def validate_test_structure(test_data):
        """Проверка структуры теста"""
        required_fields = ['test_title', 'questions']
        if not all(field in test_data for field in required_fields):
            return False
        
        for question in test_data['questions']:
            if 'type' not in question or 'question' not in question:
                return False
        return True
    
    @staticmethod
    def validate_graph_structure(graph_data):
        """Проверка структуры графа"""
        if 'nodes' not in graph_data or 'edges' not in graph_data:
            return False
        return True
