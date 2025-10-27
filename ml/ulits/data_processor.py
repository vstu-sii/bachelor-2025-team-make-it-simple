import json
import re
import pandas as pd
from datetime import datetime

class EnglishDataProcessor:
    """Обработка и подготовка данных для курса английского языка"""
    
    # Словари для валидации английского контента
    GRAMMAR_TOPICS = {
        'beginner': ['present simple', 'articles', 'basic verbs', 'pronouns', 'prepositions'],
        'elementary': ['past simple', 'present continuous', 'adjectives', 'adverbs'],
        'pre_intermediate': ['present perfect', 'future forms', 'modals', 'comparatives'],
        'intermediate': ['passive voice', 'reported speech', 'conditionals', 'phrasal verbs'],
        'upper_intermediate': ['past perfect', 'used to', 'complex sentences', 'linking words'],
        'advanced': ['inversion', 'mixed conditionals', 'subjunctive', 'idioms']
    }
    
    VOCABULARY_CATEGORIES = [
        'daily routines', 'family', 'food', 'travel', 'work', 'education',
        'technology', 'sports', 'entertainment', 'health', 'environment'
    ]
    
    @staticmethod
    def load_english_dataset(file_path):
        """Загрузка dataset для английского языка"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Валидация структуры данных для английского
            validation_result = EnglishDataProcessor.validate_english_dataset(data)
            if not validation_result['valid']:
                print(f"Предупреждение: {validation_result['message']}")
            
            return data
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
            return None
    
    @staticmethod
    def validate_english_dataset(data):
        """Валидация dataset для английского языка"""
        errors = []
        
        # Проверка наличия обязательных полей
        if 'test_cases' not in data:
            errors.append("Отсутствует 'test_cases'")
        if 'lesson_cases' not in data:
            errors.append("Отсутствует 'lesson_cases'")
        
        # Валидация тестовых случаев
        if 'test_cases' in data:
            for i, test_case in enumerate(data['test_cases']):
                test_errors = EnglishDataProcessor.validate_test_case(test_case, i)
                errors.extend(test_errors)
        
        # Валидация учебных случаев
        if 'lesson_cases' in data:
            for i, lesson_case in enumerate(data['lesson_cases']):
                lesson_errors = EnglishDataProcessor.validate_lesson_case(lesson_case, i)
                errors.extend(lesson_errors)
        
        return {
            'valid': len(errors) == 0,
            'message': '; '.join(errors) if errors else 'Валидация пройдена',
            'error_count': len(errors)
        }
    
    @staticmethod
    def validate_test_case(test_case, index):
        """Валидация тестового случая для английского"""
        errors = []
        
        # Проверка обязательных полей
        required_fields = ['course_topics', 'student_interests', 'reference']
        for field in required_fields:
            if field not in test_case:
                errors.append(f"Тест {index}: отсутствует '{field}'")
        
        if 'reference' in test_case:
            ref = test_case['reference']
            ref_errors = EnglishDataProcessor.validate_test_reference(ref, index)
            errors.extend(ref_errors)
        
        # Проверка грамматических тем
        if 'course_topics' in test_case:
            for topic in test_case['course_topics']:
                if not EnglishDataProcessor.is_valid_grammar_topic(topic.lower()):
                    errors.append(f"Тест {index}: неизвестная грамматическая тема '{topic}'")
        
        return errors
    
    @staticmethod
    def validate_lesson_case(lesson_case, index):
        """Валидация учебного случая"""
        errors = []
        
        required_fields = ['lesson_topic', 'course_materials', 'interests', 'student_level', 'reference']
        for field in required_fields:
            if field not in lesson_case:
                errors.append(f"Урок {index}: отсутствует '{field}'")
        
        # Проверка уровня студента
        if 'student_level' in lesson_case:
            level = lesson_case['student_level'].lower()
            valid_levels = ['beginner', 'elementary', 'pre_intermediate', 'intermediate', 'upper_intermediate', 'advanced']
            if level not in valid_levels:
                errors.append(f"Урок {index}: неверный уровень '{lesson_case['student_level']}'")
        
        if 'reference' in lesson_case:
            ref_errors = EnglishDataProcessor.validate_lesson_reference(lesson_case['reference'], index)
            errors.extend(ref_errors)
        
        return errors
    
    @staticmethod
    def validate_test_reference(reference, index):
        """Валидация reference теста"""
        errors = []
        
        if 'test_title' not in reference:
            errors.append(f"Тест {index}: отсутствует 'test_title'")
        
        if 'questions' not in reference:
            errors.append(f"Тест {index}: отсутствует 'questions'")
        else:
            for q_index, question in enumerate(reference['questions']):
                q_errors = EnglishDataProcessor.validate_english_question(question, q_index, index)
                errors.extend(q_errors)
        
        return errors
    
    @staticmethod
    def validate_lesson_reference(reference, index):
        """Валидация reference урока"""
        errors = []
        
        required_fields = ['lesson_title', 'objectives', 'theory_content', 'practice_questions', 'test_questions']
        for field in required_fields:
            if field not in reference:
                errors.append(f"Урок {index}: отсутствует '{field}'")
        
        # Проверка вопросов практики
        if 'practice_questions' in reference:
            for q_index, question in enumerate(reference['practice_questions']):
                q_errors = EnglishDataProcessor.validate_english_question(question, q_index, index, 'practice')
                errors.extend(q_errors)
        
        # Проверка тестовых вопросов
        if 'test_questions' in reference:
            for q_index, question in enumerate(reference['test_questions']):
                q_errors = EnglishDataProcessor.validate_english_question(question, q_index, index, 'test')
                errors.extend(q_errors)
        
        return errors
    
    @staticmethod
    def validate_english_question(question, q_index, parent_index, question_type='test'):
        """Валидация вопроса для английского языка"""
        errors = []
        
        if 'type' not in question:
            errors.append(f"Вопрос {parent_index}.{q_index} ({question_type}): отсутствует 'type'")
        else:
            valid_types = ['short_answer', 'single_choice', 'multiple_choice', 'matching', 'essay']
            if question['type'] not in valid_types:
                errors.append(f"Вопрос {parent_index}.{q_index}: неверный тип '{question['type']}'")
        
        if 'question' not in question:
            errors.append(f"Вопрос {parent_index}.{q_index}: отсутствует текст вопроса")
        else:
            # Проверка английского текста вопроса
            text_errors = EnglishDataProcessor.validate_english_text(question['question'], f"Вопрос {parent_index}.{q_index}")
            errors.extend(text_errors)
        
        # Валидация в зависимости от типа вопроса
        question_type = question.get('type')
        if question_type == 'single_choice':
            if 'options' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствуют 'options'")
            if 'correct_answer' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствует 'correct_answer'")
        
        elif question_type == 'multiple_choice':
            if 'options' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствуют 'options'")
            if 'correct_answers' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствует 'correct_answers'")
        
        elif question_type == 'matching':
            if 'pairs' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствуют 'pairs'")
        
        elif question_type == 'essay':
            if 'evaluation_criteria' not in question:
                errors.append(f"Вопрос {parent_index}.{q_index}: отсутствуют 'evaluation_criteria'")
        
        return errors
    
    @staticmethod
    def validate_english_text(text, context):
        """Валидация английского текста"""
        errors = []
        
        # Проверка на наличие кириллицы в английском тексте
        if re.search('[а-яА-Я]', text):
            errors.append(f"{context}: кириллица в английском тексте")
        
        # Проверка базовой грамматики (упрощенная)
        if not text.endswith(('.', '?', '!')):
            errors.append(f"{context}: текст должен заканчиваться точкой, вопросительным или восклицательным знаком")
        
        return errors
    
    @staticmethod
    def is_valid_grammar_topic(topic):
        """Проверка валидности грамматической темы"""
        for level_topics in EnglishDataProcessor.GRAMMAR_TOPICS.values():
            for valid_topic in level_topics:
                if valid_topic in topic.lower():
                    return True
        return False
    
    @staticmethod
    def extract_english_metrics(generated_content):
        """Извлечение метрик для английского контента"""
        metrics = {
            'word_count': 0,
            'sentence_count': 0,
            'average_sentence_length': 0,
            'grammar_errors_detected': 0,
            'vocabulary_diversity': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if isinstance(generated_content, dict):
            content_text = json.dumps(generated_content, ensure_ascii=False)
        else:
            content_text = str(generated_content)
        
        # Базовый анализ текста
        words = re.findall(r'\b\w+\b', content_text)
        sentences = re.split(r'[.!?]+', content_text)
        
        metrics['word_count'] = len(words)
        metrics['sentence_count'] = len([s for s in sentences if s.strip()])
        
        if metrics['sentence_count'] > 0:
            metrics['average_sentence_length'] = metrics['word_count'] / metrics['sentence_count']
        
        # Простая проверка грамматики (базовые паттерны)
        metrics['grammar_errors_detected'] = EnglishDataProcessor.detect_basic_grammar_errors(content_text)
        
        # Разнообразие словаря
        if words:
            unique_words = set(words)
            metrics['vocabulary_diversity'] = len(unique_words) / len(words)
        
        return metrics
    
    @staticmethod
    def detect_basic_grammar_errors(text):
        """Обнаружение базовых грамматических ошибок"""
        error_count = 0
        
        # Проверка двойных пробелов
        if '  ' in text:
            error_count += 1
        
        # Проверка заглавных букв после точки
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence[0].isupper():
                error_count += 1
        
        # Проверка основных грамматических паттернов
        common_errors = [
            r'\bi is\b', r'\byou is\b', r'\bhe are\b', r'\bshe are\b', r'\bit are\b',
            r'\bwe is\b', r'\bthey is\b', r'\bdo he\b', r'\bdo she\b', r'\bdo it\b'
        ]
        
        for pattern in common_errors:
            if re.search(pattern, text, re.IGNORECASE):
                error_count += 1
        
        return error_count
    
    @staticmethod
    def analyze_student_level(test_results):
        """Анализ уровня студента на основе результатов теста"""
        if not test_results:
            return 'unknown'
        
        score = test_results.get('score', 0)
        total_questions = test_results.get('total_questions', 1)
        percentage = (score / total_questions) * 100
        
        if percentage >= 90:
            return 'advanced'
        elif percentage >= 75:
            return 'upper_intermediate'
        elif percentage >= 60:
            return 'intermediate'
        elif percentage >= 45:
            return 'pre_intermediate'
        elif percentage >= 30:
            return 'elementary'
        else:
            return 'beginner'
    
    @staticmethod
    def generate_personalized_content(student_profile, course_materials):
        """Генерация персонализированного контента на основе профиля студента"""
        interests = student_profile.get('interests', [])
        level = student_profile.get('level', 'beginner')
        knowledge_gaps = student_profile.get('knowledge_gaps', [])
        
        personalized_data = {
            'level': level,
            'interests': interests,
            'target_topics': [],
            'personalized_examples': [],
            'recommended_materials': []
        }
        
        # Подбор тем на основе пробелов в знаниях
        if knowledge_gaps:
            personalized_data['target_topics'] = knowledge_gaps[:3]  # Берем 3 основные темы
        
        # Создание персонализированных примеров на основе интересов
        for interest in interests[:2]:  # Берем 2 основных интереса
            examples = EnglishDataProcessor.create_interest_examples(interest, level)
            personalized_data['personalized_examples'].extend(examples)
        
        # Рекомендации материалов
        personalized_data['recommended_materials'] = EnglishDataProcessor.filter_materials_by_level(
            course_materials, level
        )
        
        return personalized_data
    
    @staticmethod
    def create_interest_examples(interest, level):
        """Создание примеров на основе интересов студента"""
        examples = []
        
        interest_templates = {
            'sports': {
                'beginner': ["I play {sport} every day", "My favorite team is {team}"],
                'intermediate': ["I have been playing {sport} since I was a child", "The most exciting match I've seen was..."],
                'advanced': ["Had I trained more rigorously, I might have become a professional {sport} player"]
            },
            'music': {
                'beginner': ["I listen to {music} music", "My favorite singer is {singer}"],
                'intermediate': ["I have been learning to play the {instrument} for two years"],
                'advanced': ["Never have I been so moved by a musical performance as when..."]
            },
            'technology': {
                'beginner': ["I use my {device} every day", "My favorite app is {app}"],
                'intermediate': ["Technology has significantly changed the way we {activity}"],
                'advanced': ["Were technology to advance at this pace, we might witness..."]
            }
        }
        
        # Находим подходящие шаблоны для интереса и уровня
        for category, levels in interest_templates.items():
            if category in interest.lower():
                for lev, templates in levels.items():
                    if lev == level:
                        examples.extend(templates)
                        break
                break
        
        # Если не нашли точного совпадения, используем общие шаблоны
        if not examples:
            general_templates = {
                'beginner': ["I like {interest}", "My favorite {interest} is..."],
                'intermediate': ["I enjoy {interest} in my free time", "{interest} has always fascinated me"],
                'advanced': ["My passion for {interest} has led me to explore..."]
            }
            examples = general_templates.get(level, ["I'm interested in {interest}"])
        
        return [example.format(interest=interest) for example in examples]
    
    @staticmethod
    def filter_materials_by_level(materials, level):
        """Фильтрация материалов по уровню студента"""
        level_order = ['beginner', 'elementary', 'pre_intermediate', 'intermediate', 'upper_intermediate', 'advanced']
        
        try:
            current_level_index = level_order.index(level)
            # Возвращаем материалы для текущего и следующего уровня
            recommended_levels = level_order[current_level_index:current_level_index + 2]
            return [m for m in materials if any(lev in m.get('level', '').lower() for lev in recommended_levels)]
        except ValueError:
            return materials
    
    @staticmethod
    def calculate_progress_metrics(student_data):
        """Расчет метрик прогресса студента"""
        if not student_data or 'test_results' not in student_data:
            return {}
        
        test_results = student_data['test_results']
        progress = {
            'current_level': EnglishDataProcessor.analyze_student_level(test_results),
            'improvement_rate': 0,
            'weak_areas': [],
            'strong_areas': []
        }
        
        # Анализ слабых и сильных сторон
        if 'detailed_results' in test_results:
            for topic, score in test_results['detailed_results'].items():
                if score < 60:  # Ниже 60% - слабая область
                    progress['weak_areas'].append(topic)
                elif score > 85:  # Выше 85% - сильная область
                    progress['strong_areas'].append(topic)
        
        # Расчет улучшения (если есть исторические данные)
        if 'previous_scores' in student_data:
            current_score = test_results.get('score', 0)
            previous_score = student_data['previous_scores'][-1] if student_data['previous_scores'] else 0
            if previous_score > 0:
                progress['improvement_rate'] = ((current_score - previous_score) / previous_score) * 100
        
        return progress
    
    @staticmethod
    def create_sample_english_data():
        """Создание примеров данных для английского языка"""
        return {
            "test_cases": [
                {
                    "course_topics": ["Present Simple", "Basic Vocabulary"],
                    "student_interests": "football, music",
                    "reference": {
                        "test_title": "Beginner English Test",
                        "questions": [
                            {
                                "type": "short_answer",
                                "question": "What do you usually do on weekends?",
                                "correct_answer": "I usually play football and listen to music."
                            }
                        ]
                    }
                }
            ],
            "lesson_cases": [
                {
                    "lesson_topic": "Present Simple for Daily Routines",
                    "course_materials": "Present Simple structure, frequency adverbs, daily activities vocabulary",
                    "interests": "sports, games",
                    "student_level": "beginner",
                    "reference": {
                        "lesson_title": "Daily Routines and Hobbies",
                        "objectives": ["Use Present Simple correctly", "Describe daily routines"],
                        "theory_content": "Present Simple is used for habits and routines...",
                        "practice_questions": [
                            {
                                "type": "short_answer",
                                "question": "What time do you usually get up?",
                                "correct_answer": "I usually get up at 7 AM."
                            }
                        ],
                        "test_questions": [
                            {
                                "type": "single_choice",
                                "question": "Which sentence is correct?",
                                "options": ["He play football", "He plays football", "He playing football"],
                                "correct_answer": 1
                            }
                        ]
                    }
                }
            ]
        }
    
    @staticmethod
    def export_english_report(student_data, output_path):
        """Экспорт отчета по студенту на английском языке"""
        report = {
            'student_info': {
                'name': student_data.get('name', 'Unknown'),
                'level': EnglishDataProcessor.analyze_student_level(student_data.get('test_results', {})),
                'interests': student_data.get('interests', [])
            },
            'progress_metrics': EnglishDataProcessor.calculate_progress_metrics(student_data),
            'recommendations': EnglishDataProcessor.generate_recommendations(student_data),
            'generated_date': datetime.now().isoformat()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка экспорта отчета: {e}")
            return False
    
    @staticmethod
    def generate_recommendations(student_data):
        """Генерация рекомендаций для студента"""
        progress = EnglishDataProcessor.calculate_progress_metrics(student_data)
        recommendations = []
        
        # Рекомендации на основе слабых областей
        for weak_area in progress.get('weak_areas', []):
            recommendations.append({
                'type': 'grammar_focus',
                'area': weak_area,
                'action': f'Practice {weak_area} with exercises',
                'priority': 'high'
            })
        
        # Рекомендации на основе уровня
        level = progress.get('current_level', 'beginner')
        if level in ['beginner', 'elementary']:
            recommendations.append({
                'type': 'general',
                'area': 'vocabulary',
                'action': 'Build basic vocabulary with flashcards',
                'priority': 'medium'
            })
        
        # Рекомендации на основе интересов
        interests = student_data.get('interests', [])
        for interest in interests[:2]:
            recommendations.append({
                'type': 'motivation',
                'area': 'engagement',
                'action': f'Find English content about {interest}',
                'priority': 'low'
            })
        
        return recommendations

# Для обратной совместимости
class DataProcessor(EnglishDataProcessor):
    """Унаследованный класс для обратной совместимости"""
    pass

def create_init_files():
    """Создание пустых __init__.py файлов"""
    init_files = [
        "ml/__init__.py",
        "ml/api/__init__.py", 
        "ml/evaluation/__init__.py",
        "ml/models/__init__.py",
        "ml/utils/__init__.py"
    ]
    
    for file_path in init_files:
        with open(file_path, 'w') as f:
            f.write('')

if __name__ == "__main__":
    # Создание структуры проекта
    create_init_files()
    print("Структура проекта создана!")
    
    # Пример использования
    processor = EnglishDataProcessor()
    
    # Создание примеров данных
    sample_data = processor.create_sample_english_data()
    processor.save_dataset(sample_data, "data/samples/english_sample_data.json")
    
    # Валидация данных
    validation_result = processor.validate_english_dataset(sample_data)
    print(f"Результат валидации: {validation_result['message']}")
    
    print("Обработчик данных для английского языка готов!")

    """
    # Загрузка и валидация данных
    processor = EnglishDataProcessor()
    data = processor.load_english_dataset('data/datasets/test_questions.json')

    # Анализ студента
    student_profile = {
        'interests': ['football', 'technology'],
        'test_results': {'score': 75, 'total_questions': 100}
    }
    level = processor.analyze_student_level(student_profile['test_results'])

    # Генерация персонализированного контента
    personalized = processor.generate_personalized_content(student_profile, course_materials)
    """

