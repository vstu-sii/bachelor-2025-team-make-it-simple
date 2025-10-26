import json
import requests
import random

class EnglishTestGenerator:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "deepseek-r1:8b"
        
    def generate_question_with_ollama(self, prompt):
        """Генерация вопроса через Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ошибка при обращении к Ollama: {e}")
            return ""
    
    def generate_placement_test(self, course_topics, num_questions=25):
        """Генерация входного тестирования на основе тем курса"""
        
        # Структура теста с учетом тем курса
        test_structure = [
            {
                "type": "grammar_single_choice",
                "count": 5,
                "prompt": f"Generate a grammar multiple choice question for English placement test related to topics: {', '.join(course_topics)}. Include 4 options with one correct answer. Format: Question: [question] Options: A) [option1] B) [option2] C) [option3] D) [option4] Answer: [correct letter]"
            },
            {
                "type": "vocabulary_single_choice", 
                "count": 5,
                "prompt": f"Generate a vocabulary multiple choice question for English placement test testing word meaning or usage related to topics: {', '.join(course_topics)}. Include 4 options with one correct answer. Format: Question: [question] Options: A) [option1] B) [option2] C) [option3] D) [option4] Answer: [correct letter]"
            },
            {
                "type": "multiple_choice",
                "count": 4,
                "prompt": f"Generate a multiple choice question where more than one answer can be correct, related to topics: {', '.join(course_topics)}. Format: Question: [question] Options: A) [option1] B) [option2] C) [option3] D) [option4] Answer: [comma separated correct letters]"
            },
            {
                "type": "fill_blank",
                "count": 5,
                "prompt": f"Generate a fill-in-the-blank English question with a sentence having one missing word related to topics: {', '.join(course_topics)}. Provide the correct answer. Format: Question: Complete the sentence: [sentence with blank] Answer: [correct word]"
            },
            {
                "type": "matching",
                "count": 3,
                "prompt": f"Generate a matching exercise with 4 items to match related to topics: {', '.join(course_topics)}. Format: Question: Match the words with their definitions: Left: [word1], [word2], [word3], [word4] Right: [def1], [def2], [def3], [def4] Answer: [word1-def1, word2-def2, etc.]"
            },
            {
                "type": "short_answer",
                "count": 3,
                "prompt": f"Generate a short answer grammar or vocabulary question related to topics: {', '.join(course_topics)}. Format: Question: [question] Answer: [short correct answer]"
            }
        ]
        
        questions = []
        question_id = 1
        
        for section in test_structure:
            for i in range(section["count"]):
                print(f"Генерация вопроса {question_id}...")
                
                response = self.generate_question_with_ollama(section["prompt"])
                question_data = self.parse_question_response(response, section["type"], question_id, course_topics)
                
                if question_data:
                    questions.append(question_data)
                    question_id += 1
                else:
                    questions.append(self.create_fallback_question(question_id, section["type"], course_topics))
                    question_id += 1
        
        return questions
    
    def parse_question_response(self, response, question_type, question_id, course_topics):
        """Парсинг ответа от модели в структурированный формат"""
        
        try:
            if question_type in ["grammar_single_choice", "vocabulary_single_choice"]:
                return self.parse_single_choice(response, question_id, question_type, course_topics)
            elif question_type == "multiple_choice":
                return self.parse_multiple_choice(response, question_id, course_topics)
            elif question_type == "fill_blank":
                return self.parse_fill_blank(response, question_id, course_topics)
            elif question_type == "matching":
                return self.parse_matching(response, question_id, course_topics)
            elif question_type == "short_answer":
                return self.parse_short_answer(response, question_id, course_topics)
        except Exception as e:
            print(f"Ошибка парсинга вопроса: {e}")
            return None
        
        return None
    
    def parse_single_choice(self, response, question_id, q_type, course_topics):
        """Парсинг вопросов с единственным выбором"""
        lines = response.split('\n')
        question = ""
        options = []
        answer = ""
        
        for line in lines:
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
            elif line.startswith('Options:') or any(line.startswith(x) for x in ['A)', 'B)', 'C)', 'D)']):
                if 'A)' in line or 'B)' in line or 'C)' in line or 'D)' in line:
                    option_parts = [part.strip() for part in line.split(')') if part.strip()]
                    for i in range(0, len(option_parts)-1, 2):
                        if i+1 < len(option_parts):
                            options.append(f"{option_parts[i]}) {option_parts[i+1]}")
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        if not question:
            return self.create_fallback_question(question_id, q_type, course_topics)
        
        return {
            "id": question_id,
            "question": question,
            "type": "single_choice",
            "options": options,
            "answer": answer,
            "category": q_type,
            "topics": course_topics
        }
    
    def parse_multiple_choice(self, response, question_id, course_topics):
        """Парсинг вопросов с множественным выбором"""
        lines = response.split('\n')
        question = ""
        options = []
        answer = ""
        
        for line in lines:
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
            elif line.startswith('Options:') or any(line.startswith(x) for x in ['A)', 'B)', 'C)', 'D)']):
                if 'A)' in line or 'B)' in line or 'C)' in line or 'D)' in line:
                    option_parts = [part.strip() for part in line.split(')') if part.strip()]
                    for i in range(0, len(option_parts)-1, 2):
                        if i+1 < len(option_parts):
                            options.append(f"{option_parts[i]}) {option_parts[i+1]}")
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        if not question:
            return self.create_fallback_question(question_id, "multiple_choice", course_topics)
        
        return {
            "id": question_id,
            "question": question,
            "type": "multiple_choice",
            "options": options,
            "answer": answer,
            "category": "multiple_choice",
            "topics": course_topics
        }
    
    def parse_fill_blank(self, response, question_id, course_topics):
        """Парсинг вопросов на заполнение пропусков"""
        lines = response.split('\n')
        question = ""
        answer = ""
        
        for line in lines:
            if "Complete the sentence:" in line:
                question = line.replace("Complete the sentence:", "").strip()
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        if not question:
            return self.create_fallback_question(question_id, "fill_blank", course_topics)
        
        return {
            "id": question_id,
            "question": question,
            "type": "fill_blank", 
            "options": [],
            "answer": answer,
            "category": "fill_blank",
            "topics": course_topics
        }
    
    def parse_matching(self, response, question_id, course_topics):
        """Парсинг вопросов на соответствие"""
        lines = response.split('\n')
        question = ""
        left_items = []
        right_items = []
        answer = ""
        
        for line in lines:
            if "Match the words with their definitions:" in line:
                question = line
            elif line.startswith('Left:'):
                left_part = line.replace('Left:', '').strip()
                left_items = [item.strip() for item in left_part.split(',')]
            elif line.startswith('Right:'):
                right_part = line.replace('Right:', '').strip()
                right_items = [item.strip() for item in right_part.split(',')]
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        if not question or len(left_items) < 4:
            return self.create_fallback_question(question_id, "matching", course_topics)
        
        return {
            "id": question_id,
            "question": question,
            "type": "matching",
            "options": {
                "left": left_items[:4],
                "right": right_items[:4]
            },
            "answer": answer,
            "category": "matching",
            "topics": course_topics
        }
    
    def parse_short_answer(self, response, question_id, course_topics):
        """Парсинг вопросов с коротким ответом"""
        lines = response.split('\n')
        question = ""
        answer = ""
        
        for line in lines:
            if line.startswith('Question:'):
                question = line.replace('Question:', '').strip()
            elif line.startswith('Answer:'):
                answer = line.replace('Answer:', '').strip()
        
        if not question:
            return self.create_fallback_question(question_id, "short_answer", course_topics)
        
        return {
            "id": question_id,
            "question": question,
            "type": "short_answer",
            "options": [],
            "answer": answer,
            "category": "short_answer",
            "topics": course_topics
        }
    
    def create_fallback_question(self, question_id, q_type, course_topics):
        """Создание резервного вопроса если генерация не удалась"""
        
        # Базовые вопросы с учетом тем курса
        topic_keywords = " ".join(course_topics[:2]).lower()
        
        fallback_questions = {
            "grammar_single_choice": {
                "question": f"Choose the correct verb form related to {topic_keywords}: She _____ to the store yesterday.",
                "options": ["A) go", "B) went", "C) goes", "D) going"],
                "answer": "B"
            },
            "vocabulary_single_choice": {
                "question": f"What is the synonym for 'happy' in context of {topic_keywords}?",
                "options": ["A) sad", "B) angry", "C) joyful", "D) tired"],
                "answer": "C"
            },
            "multiple_choice": {
                "question": f"Which tenses are used to talk about the past in {topic_keywords} context?",
                "options": ["A) Past Simple", "B) Present Continuous", "C) Past Perfect", "D) Future Simple"],
                "answer": "A,C"
            },
            "fill_blank": {
                "question": f"I _____ reading a book about {topic_keywords} right now.",
                "options": [],
                "answer": "am"
            },
            "matching": {
                "question": f"Match the {topic_keywords} related words with their definitions",
                "options": {
                    "left": ["Noun", "Verb", "Adjective", "Adverb"],
                    "right": ["Names a person, place or thing", "Shows action or state", "Describes a noun", "Describes a verb"]
                },
                "answer": "Noun-Names a person, place or thing, Verb-Shows action or state, Adjective-Describes a noun, Adverb-Describes a verb"
            },
            "short_answer": {
                "question": f"What is the plural form of 'child' in {topic_keywords} context?",
                "options": [],
                "answer": "children"
            }
        }
        
        fallback = fallback_questions.get(q_type, fallback_questions["grammar_single_choice"])
        
        question_type = "single_choice" if q_type in ["grammar_single_choice", "vocabulary_single_choice"] else q_type
        
        return {
            "id": question_id,
            "question": fallback["question"],
            "type": question_type,
            "options": fallback["options"],
            "answer": fallback["answer"],
            "category": q_type,
            "topics": course_topics
        }
    
    def save_test_to_json(self, questions, filename="english_placement_test.json"):
        """Сохранение теста в JSON файл"""
        test_data = {
            "test_name": "English Placement Test",
            "description": "Entrance test to assess initial English language knowledge",
            "course_topics": questions[0]["topics"] if questions else [],
            "estimated_time": "25-30 minutes",
            "total_questions": len(questions),
            "questions": questions
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print(f"Тест сохранен в файл: {filename}")
        return test_data

def main():
    """Основная функция для генерации теста"""

    course_topics = [
        'Приветствия и знакомства'
        'Страны и города'
        'Числа'
        'Семья'
        'Цвета'
        'Питание'
        'Работа и профессии'
        'Дом и жилье'
        'Магазин'
        'Транспорт'
        'Время'
        'Здоровье и болезни'
        'Средства массовой информации'
        'Страны БРИКС и другие англоязычные страны'
        'Идиомы и устойчивые выражения'
        'Современные темы'
        'Глагол "to be" в разных временах.'
        'Глагол "to have".'
        'Простые времена (Present Simple, Past Simple, Future Simple).'
        'Непростые времена (Present Continuous, Past Continuous, Future Continuous, Present Perfect, Past Perfect, 21. Future Perfect, Present Perfect Continuous, Past Perfect Continuous).'
        'Времена модальности (Present Perfect, Past Perfect).'
        'Условные предложения (First, Second, Third Conditional).'
        'Сослагательный залог (Conditional Perfect, Perfect Conditional).'
        'Пассивный залог (Present Perfect, Past Perfect, Future Perfect).'
        'Инфинитив после модальных глаголов (can, could, may, might, must, shall, should, will, would).'
        'Модальные глаголы (Modals).'
        'Местные прилагательные (Adjectives of place).'
        'Моментальные прилагательные (Adjectives of time).'
        'Завершенные прилагательные (Adjectives of state).'
        'Сравнительные и превосходительные степени прилагательных (Comparatives & Superlatives).'
        'Предлоги (Prepositions).'
        'Артикли (Articles).'
        'Местоимения (Pronouns).'
        'Глаголы-связки (Linking Verbs).'
        'Наречия (Adverbs).'
        'Существительные (Nouns) - число, падеж (хотя в английском это не совсем падежи).'
        'Глаголы (Verbs) - вид (совершенный/несовершенный), залог (активный/пассивный), модальность.'
        'Существительные после прилагательных (Nouns after Adjectives).'
        'Правила согласования (Agreement rules).'
        'Вводные слова и фразы (Conjunctions & Phrasal Verbs).'
        'Осложнение главного члена предложения (Clauses: Noun clauses, Relative clauses).'
        'Сложные предложения (Compound & Complex Sentences).'
        'Звуки английского языка (Phonemes).'
        'Правильное произношение слов (Word pronunciation).'
        'Стили произношения (Linking & Reduction).'
        'Имитация интонаций (Intonation).'
        'Правильное произношение фраз и предложений (Connected speech).'
        'Правильное произношение диалогов (Dialogue pronunciation).'
        'Английская культура (British/American culture).'
        'Общество англоговорящих стран (Society).'
        'История (History).'
        'Общепризнанные личности (Famous people).'
        'Каникулы и праздники (Holidays).'
        'СМИ и телевидение (Media & Television).'
        'Интернет и технологии (Internet & Technology).'
        'Экология и охрана окружающей среды (Environment).'
        'Права человека (Human Rights).'
        'Религия (Religion).'
        'Заказ еды в кафе/ресторане (Ordering food/drinks).'
        'Покупки в магазине (Shopping).'
        'Запросить информацию (Asking for information).'
        'Путеводители (Directions & Asking the way).'
        'Поздравления и пожелания (Greetings, congratulations, wishes).'
        'Обсуждение погоды (Talking about weather).'
        'Расставание и прощание (Parting).'
        'Запросить/дать телефонный номер (Asking for/ giving phone numbers).'
    ]
    
    num_questions = 25
    
    generator = EnglishTestGenerator()

    questions = generator.generate_placement_test(course_topics, num_questions)
    test_data = generator.save_test_to_json(questions)
    
    # Статистика по типам вопросов
    type_count = {}
    for q in questions:
        q_type = q.get('type', 'unknown')
        type_count[q_type] = type_count.get(q_type, 0) + 1
    
    print("\nРаспределение по типам вопросов:")
    for q_type, count in type_count.items():
        print(f"  {q_type}: {count} вопросов")
        
    print(f"\nТест сохранен в файл: english_placement_test.json")
        

if __name__ == "__main__":
    main()
