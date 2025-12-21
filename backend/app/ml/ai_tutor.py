"""
Основной модуль AI-тьютора с функциями работы с Mistral API.
"""

import json
import time
import logging
import re
import requests
from typing import Dict, Optional, Any
from app.ml.config import *

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, validate_config()["log_level"] if "log_level" in globals() else "INFO"),
    format=LOG_FORMAT if "LOG_FORMAT" in globals() else "%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def clean_json_string(json_str: str) -> str:
    """
    Очищает строку JSON от невалидных символов и пытается восстановить структуру.
    
    Args:
        json_str: Строка с возможным JSON
        
    Returns:
        Очищенная строка JSON
    """
    if not json_str:
        return "{}"
    
    # 1. Убираем все управляющие символы кроме \n, \t
    # Заменяем \r, \b, \f на пробелы
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', json_str)
    
    # 2. Убираем markdown блоки
    cleaned = re.sub(r'```json\s*', '', cleaned)
    cleaned = re.sub(r'```\s*', '', cleaned)
    
    # 3. Убираем лишние пробелы в начале строк
    cleaned = '\n'.join([line.strip() for line in cleaned.split('\n')])
    
    # 4. Исправляем проблемы с кавычками
    # Заменяем умные кавычки на обычные
    cleaned = cleaned.replace('"', '"').replace('"', '"')
    cleaned = cleaned.replace("'", "'").replace("'", "'")
    
    # 5. Убираем escape-последовательности в тексте
    cleaned = cleaned.replace('\\n', '\n').replace('\\t', '\t')
    
    # 6. Убираем неожиданные символы в строках
    # Находим строки в JSON и очищаем их
    def clean_string(match):
        content = match.group(1)
        # Убираем управляющие символы из содержимого строк
        content = re.sub(r'[\x00-\x1f\x7f]', ' ', content)
        # Экранируем кавычки внутри строки
        content = content.replace('"', '\\"')
        return f'"{content}"'
    
    # Заменяем содержимое строк в JSON
    cleaned = re.sub(r'"([^"]*)"', clean_string, cleaned)
    
    # 7. Ищем JSON объект в тексте
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, cleaned, re.DOTALL)
    
    if matches:
        # Берем самый длинный найденный JSON
        best_match = max(matches, key=len)
        
        # 8. Проверяем баланс скобок
        open_braces = best_match.count('{')
        close_braces = best_match.count('}')
        
        if open_braces > close_braces:
            # Добавляем недостающие закрывающие скобки
            best_match += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            # Убираем лишние закрывающие скобки с конца
            for _ in range(close_braces - open_braces):
                best_match = best_match[:best_match.rfind('}')]
        
        return best_match.strip()
    
    return cleaned.strip()

def extract_json_from_text(text: str) -> str:
    """
    Извлекает JSON из текста, который может содержать лишние символы.
    
    Args:
        text: Текст, который может содержать JSON
        
    Returns:
        Чистый JSON в виде строки
    """
    # Сначала пытаемся почистить строку
    cleaned = clean_json_string(text)
    
    # Пытаемся распарсить
    try:
        # Проверяем, что это валидный JSON
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        # Пытаемся найти JSON в тексте
        json_pattern = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            # Сортируем по длине (самый длинный скорее всего правильный)
            matches.sort(key=len, reverse=True)
            
            for i, match in enumerate(matches[:3]):  # Проверяем первые 3
                try:
                    # Пытаемся почистить и распарсить
                    cleaned_match = clean_json_string(match)
                    json.loads(cleaned_match)
                    return cleaned_match
                except json.JSONDecodeError:
                    continue
        
        # Если ничего не помогло, возвращаем заглушку
        return '{"error": "Не удалось сгенерировать валидный JSON", "demo_mode": true}'

class MistralClient:
    """Клиент для работы с Mistral API."""
    
    def __init__(self):
        config = validate_config()
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.base_url = config["base_url"]
        self.default_temperature = config["temperature"]
        self.default_max_tokens = config["max_tokens"]
        self.timeout = config["timeout"]
        
        # Заголовки для запросов
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Настройки повторных попыток
        self.max_retries = 5
        self.retry_delay = 2  # секунды
        self.backoff_factor = 1.5  # множитель для экспоненциальной задержки
        
        logger.info(f"Инициализирован клиент Mistral с моделью {self.model}")
    
    def generate(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """
        Генерация текста через Mistral API с повторными попытками при ошибках.
        
        Args:
            prompt: Текст промпта
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов
            
        Returns:
            Сгенерированный текст
        """
        # Используем значения по умолчанию, если не указаны
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        # Логирование промпта
        logger.info(f"Отправка запроса к Mistral API")
        logger.debug(f"Промпт (первые 500 символов): {prompt[:500]}...")

        # Подготовка данных для запроса
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Пытаемся выполнить запрос с повторными попытками
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                logger.debug(f"Попытка {attempt + 1}/{self.max_retries}")
                
                # Отправка запроса
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
                
                # Проверка статуса ответа
                if response.status_code == 429:
                    # Превышен лимит запросов - ждем и пробуем снова
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.info(f"Превышен лимит запросов (429). Жду {delay:.1f} секунд перед повторной попыткой...")
                    time.sleep(delay)
                    continue
                
                response.raise_for_status()
                
                # Парсинг ответа
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]
                
                # Расчет метрик
                latency = time.time() - start_time
                token_count = len(generated_text.split())
                
                # Логирование метрик
                logger.info(f"Запрос выполнен за {latency:.2f} секунд (попытка {attempt + 1})")
                logger.info(f"Сгенерировано токенов: {token_count}")
                
                return generated_text.strip()
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    # Если это не последняя попытка, ждем и пробуем снова
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    logger.warning(f"Ошибка при запросе к Mistral API: {e}. Жду {delay:.1f} секунд перед повторной попыткой...")
                    time.sleep(delay)
                    continue
                else:
                    # Если это последняя попытка, возвращаем ошибку
                    logger.error(f"Все {self.max_retries} попытки завершились ошибкой. Использую демо-режим.")
                    if hasattr(e, 'response') and e.response:
                        logger.error(f"Статус код: {e.response.status_code}")
                        logger.error(f"Ответ: {e.response.text[:500]}...")
                    return self._get_fallback_response(prompt)
            except KeyError as e:
                logger.error(f"Ошибка парсинга ответа от Mistral API: {e}")
                if 'result' in locals():
                    logger.error(f"Полный ответ: {result}")
                return self._get_fallback_response(prompt)
            except Exception as e:
                logger.error(f"Неизвестная ошибка: {e}")
                return self._get_fallback_response(prompt)
        
        # Если все попытки исчерпаны, возвращаем заглушку
        return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """
        Возвращает заглушку для демонстрации, если API не доступен после всех попыток.
        """
        logger.info("Используется заглушка для демонстрации после неудачных попыток")
        
        # Определяем тип запроса по промпту
        if "входной тест" in prompt.lower() or "entry_test" in prompt.lower():
            return '''{
  "questions": [
    {
      "question_id": "1",
      "type": "short_answer",
      "question": "What is your name and how old are you?",
      "max_length": 50,
      "correct_answer": "My name is Alex, I am 25 years old"
    },
    {
      "question_id": "2",
      "type": "single_choice",
      "question": "Choose the correct sentence in Present Simple:",
      "options": [
        "I playing football every day",
        "I plays football every day",
        "I play football every day",
        "I am play football every day"
      ],
      "correct_answer": 2
    },
    {
      "question_id": "3",
      "type": "multiple_choice",
      "question": "Which words are articles in English?",
      "options": ["the", "a", "an", "is", "and"],
      "correct_answers": [0, 1, 2]
    },
    {
      "question_id": "4",
      "type": "gaps_choice",
      "question": "If I [1] enough money, I [2] travel around the world. I [3] to visit Japan for a long time because I [4] fascinated by its culture. When I [5] there, I want to try traditional food and [6] historical temples.",
      "gaps": [
        {
          "gap_id": 1,
          "options": ["have", "had", "will have", "would have"],
          "correct_answer": 1
        },
        {
          "gap_id": 2,
          "options": ["would", "will", "can", "could"],
          "correct_answer": 0
        },
        {
          "gap_id": 3,
          "options": ["have wanted", "want", "wanted", "wanting"],
          "correct_answer": 0
        },
        {
          "gap_id": 4,
          "options": ["am", "was", "have been", "had been"],
          "correct_answer": 0
        },
        {
          "gap_id": 5,
          "options": ["go", "will go", "went", "have gone"],
          "correct_answer": 0
        },
        {
          "gap_id": 6,
          "options": ["visit", "visiting", "visited", "to visit"],
          "correct_answer": 0
        }
      ]
    }
  ]
}'''
        elif "граф зависимостей" in prompt.lower() or "course_graph" in prompt.lower():
            return '''{
  "nodes": [
    {
      "id": "1",
      "label": "Present Simple",
      "group": 2
    },
    {
      "id": "2",
      "label": "Артикли",
      "group": 3
    },
    {
      "id": "3",
      "label": "Предлоги",
      "group": 3
    },
    {
      "id": "4",
      "label": "Базовая лексика",
      "group": 1
    },
    {
      "id": "5",
      "label": "Вопросы",
      "group": 3
    }
  ],
  "edges": [
    {
      "from": "1",
      "to": "2"
    },
    {
      "from": "1",
      "to": "3"
    },
    {
      "from": "4",
      "to": "1"
    },
    {
      "from": "1",
      "to": "5"
    },
    {
      "from": "2",
      "to": "5"
    }
  ]
}'''
        elif "теоретическую часть урока" in prompt.lower() or "theory" in prompt.lower():
            return '''{
  "theory_section": {
    "title": "Present Simple для геймеров",
    "content": "Present Simple используется для описания регулярных действий и привычек.\\n\\nСтруктура:\\n- I/You/We/They + глагол (I play)\\n- He/She/It + глагол + s (He plays)\\n\\nПримеры для геймеров:\\n- I play video games every evening\\n- My friend watches game streams\\n- Technology develops quickly\\n\\nОтрицательные предложения:\\n- I do not (don\\'t) play on weekdays\\n- He does not (doesn\\'t) like football games"
  }
}'''
        elif "задание на чтение" in prompt.lower() or "reading" in prompt.lower():
            return '''{
  "reading_section": {
    "title": "A Day in the Life of a Gamer",
    "text": "My name is Max. I am a student and I love video games. Every day, I wake up at 8 AM. I eat breakfast and go to school. After school, I play games with my friends. We like football games and strategy games. In the evening, I do homework and watch YouTube videos about technology. On Saturday, I play games all day. My favorite game is FIFA.",
    "comprehension_questions": [
      "What time does Max wake up?",
      "What does Max do after school?",
      "When does Max play games all day?",
      "What is Max's favorite game?"
    ]
  }
}'''
        elif "задание на говорение" in prompt.lower() or "speaking" in prompt.lower():
            return '''{
  "speaking_section": {
    "title": "Расскажи о своих игровых привычках",
    "instructions": "Опишите, как вы играете в видеоигры. Расскажите о своих любимых играх и когда вы обычно играете. Используйте Present Simple. Говорите 2-3 минуты.",
    "example_response": "I usually play games in the evening. My favorite games are FIFA and Minecraft. I play with my online friends. Sometimes I watch esports tournaments. Technology changes very fast in gaming."
  }
}'''
        elif "оцените результаты урока" in prompt.lower() or "evaluation" in prompt.lower():
            return '''{
  "lesson_score": "7",
  "knowledge_gaps": ["Time expressions", "Verb endings for he/she/it"],
  "automated_feedback": "Хорошая работа! Студент понимает базовые конструкции Present Simple, но нужно больше практики с окончаниями глаголов для he/she/it и построением вопросов.",
  "additional_lesson": true
}'''
        else:
            # Общая заглушка
            return '{"status": "demo_mode", "message": "API недоступен после нескольких попыток"}'

class AITutor:
    """Основной класс AI-тьютора."""
    
    def __init__(self):
        """Инициализация AI-тьютора."""
        self.llm_client = MistralClient()
        logger.info("AI-тьютор инициализирован")
    
    def generate_entry_test(self, course_data: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Генерация входного теста.
        
        Args:
            course_data: Данные о курсе
            feedback: Замечания репетитора по генерации

        Returns:
            Сгенерированный тест в виде словаря
        """
        logger.info("Генерация входного теста")
        if feedback:
            logger.info(f"Учитываются замечания: {feedback}")

        from app.ml.prompt_templates import PromptTemplates
        
        # Выводим входной JSON
        print("\n" + "="*60)
        print("ВХОДНЫЕ ДАННЫЕ ДЛЯ ТЕСТА:")
        print("="*60)
        print(json.dumps(course_data, ensure_ascii=False, indent=2))
        if feedback:
            print(f"ЗАМЕЧАНИЯ: {feedback}")
    
        prompt = PromptTemplates.ENTRY_TEST_PROMPT.format(
            course_title=course_data.get("course_title", ""),
            topics=", ".join(course_data.get("topics", [])),
            feedback=feedback or ""
        )
        
        response = self.llm_client.generate(prompt)
        
        # Извлекаем JSON из ответа
        json_text = extract_json_from_text(response)
        
        try:
            result = json.loads(json_text)
            
            # Выводим полученный JSON
            print("\n" + "="*60)
            print("ПОЛУЧЕННЫЙ ТЕСТ ОТ МОДЕЛИ:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст для парсинга: {json_text[:500]}...")
            
            # Возвращаем заглушку
            return {
                "questions": []
            }
    
    def generate_course_graph(self, student_data: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Генерация графа курса.
        
        Args:
            student_data: Данные о студенте и курсе
            feedback: Замечания репетитора по генерации

        Returns:
            Граф курса в виде словаря
        """
        logger.info("Генерация графа курса")
        if feedback:
            logger.info(f"Учитываются замечания: {feedback}")
        
        from app.ml.prompt_templates import PromptTemplates
        
        # Выводим входной JSON
        print("\n" + "="*60)
        print("ВХОДНЫЕ ДАННЫЕ ДЛЯ ГРАФА КУРСА:")
        print("="*60)
        print(json.dumps(student_data, ensure_ascii=False, indent=2))
        if feedback:
            print(f"ЗАМЕЧАНИЯ: {feedback}")

        prompt = PromptTemplates.COURSE_GRAPH_PROMPT.format(
            interests=", ".join(student_data["student_profile"]["interests"]),
            knowledge_gaps=", ".join(student_data["student_profile"]["knowledge_gaps"]),
            course_title=student_data["course_title"],
            topics=", ".join(student_data["topics"]),
            feedback=feedback or ""
        )
        
        response = self.llm_client.generate(prompt)
        
        # Извлекаем JSON из ответа
        json_text = extract_json_from_text(response)
        
        try:
            result = json.loads(json_text)
            
            # Выводим полученный JSON
            print("\n" + "="*60)
            print("ПОЛУЧЕННЫЙ ГРАФ ОТ МОДЕЛИ:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст для парсинга: {json_text[:500]}...")
            
            # Возвращаем заглушку
            return {
                "nodes": [],
                "edges": []
            }
    
    def generate_lesson_plan(self, lesson_data: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Генерация плана урока.
        
        Args:
            lesson_data: Данные для урока
            feedback: Замечания репетитора по генерации
            
        Returns:
            План урока в виде словаря
        """
        logger.info(f"Генерация плана урока типа: {lesson_data.get('type')}")
        if feedback:
            logger.info(f"Учитываются замечания: {feedback}")

        from app.ml.prompt_templates import PromptTemplates
        
        # Выводим входной JSON
        print("\n" + "="*60)
        print(f"ВХОДНЫЕ ДАННЫЕ ДЛЯ УРОКА ({lesson_data.get('type')}):")
        print("="*60)
        print(json.dumps(lesson_data, ensure_ascii=False, indent=2))
        if feedback:
            print(f"ЗАМЕЧАНИЯ: {feedback}")

        lesson_type = lesson_data["type"]
        
        if lesson_type == "theory":
            prompt_template = PromptTemplates.LESSON_THEORY_PROMPT
        elif lesson_type == "reading":
            prompt_template = PromptTemplates.LESSON_READING_PROMPT
        elif lesson_type == "speaking":
            prompt_template = PromptTemplates.LESSON_SPEAKING_PROMPT
        elif lesson_type == "test":
            # Для теста используем специальную функцию
            return self.generate_lesson_test(lesson_data)
        else:
            raise ValueError(f"Неизвестный тип урока: {lesson_type}")
        
        prompt = prompt_template.format(
            topic=lesson_data["lesson_parameters"]["topic"],
            interests=", ".join(lesson_data["lesson_parameters"]["student_profile"]["interests"]),
            knowledge_gaps=", ".join(lesson_data["lesson_parameters"]["student_profile"]["knowledge_gaps"]),
            feedback=feedback or ""
        )
        
        response = self.llm_client.generate(prompt)
        
        # Извлекаем JSON из ответа
        json_text = extract_json_from_text(response)
        
        try:
            result = json.loads(json_text)
            
            # Выводим полученный JSON
            print("\n" + "="*60)
            print(f"ПОЛУЧЕННЫЙ УРОК ({lesson_type}) ОТ МОДЕЛИ:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст для парсинга: {json_text[:500]}...")
            
            # Возвращаем заглушку в зависимости от типа
            if lesson_type == "theory":
                return {
                    "theory_section": {
                        "title": "Ошибка генерации",
                        "content": "Не удалось сгенерировать теорию урока."
                    }
                }
            elif lesson_type == "reading":
                return {
                    "reading_section": {
                        "title": "Error",
                        "text": "Failed to generate reading text.",
                        "comprehension_questions": []
                    }
                }
            elif lesson_type == "speaking":
                return {
                    "speaking_section": {
                        "title": "Ошибка",
                        "instructions": "Не удалось сгенерировать задание.",
                        "example_response": ""
                    }
                }
            else:
                return {"error": "Не удалось сгенерировать план урока"}
    
    def generate_lesson_test(self, lesson_data: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Генерация теста для урока.
        
        Args:
            lesson_data: Данные для урока
            feedback: Замечания репетитора по генерации

        Returns:
            Тест в виде словаря
        """
        logger.info("Генерация теста для урока")
        if feedback:
            logger.info(f"Учитываются замечания: {feedback}")

        from app.ml.prompt_templates import PromptTemplates
        
        prompt = PromptTemplates.LESSON_TEST_PROMPT.format(
            topic=lesson_data["lesson_parameters"]["topic"],
            theory=lesson_data.get("theory", ""),
            interests=", ".join(lesson_data["lesson_parameters"]["student_profile"]["interests"]),
            knowledge_gaps=", ".join(lesson_data["lesson_parameters"]["student_profile"]["knowledge_gaps"]),
            feedback=feedback or ""
        )
        
        response = self.llm_client.generate(prompt)
        
        # Извлекаем JSON из ответа
        json_text = extract_json_from_text(response)
        
        try:
            result = json.loads(json_text)
            
            # Выводим полученный JSON
            print("\n" + "="*60)
            print("ПОЛУЧЕННЫЙ ТЕСТ ОТ МОДЕЛИ:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст для парсинга: {json_text[:500]}...")
            
            # Возвращаем заглушку
            return {
                "test_section": {
                    "title": "Тест (демо)",
                    "questions": []
                }
            }
    
    def evaluate_lesson_results(self, results_data: Dict[str, Any], feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Оценка результатов урока.
        
        Args:
            results_data: Данные с результатами
            feedback: Замечания репетитора по оценке
            
        Returns:
            Оценка урока в виде словаря
        """
        logger.info("Оценка результатов урока")
        if feedback:
            logger.info(f"Учитываются замечания: {feedback}")
        
        from app.ml.prompt_templates import PromptTemplates
        
        # Выводим входной JSON
        print("\n" + "="*60)
        print("ВХОДНЫЕ ДАННЫЕ ДЛЯ ОЦЕНКИ РЕЗУЛЬТАТОВ:")
        print("="*60)
        print(json.dumps(results_data, ensure_ascii=False, indent=2))
        if feedback:
            print(f"ЗАМЕЧАНИЯ: {feedback}")

        # Подготовка данных для промпта
        speaking_notes = results_data.get("teachers_notes_about_speaking", "")
        reading_notes = results_data.get("teachers_notes_about_reading", "")
        
        # Анализ ошибок в тесте
        test_results = "Нет данных о тесте"
        if "test" in results_data and "wrong_answer_questions" in results_data["test"]:
            wrong_questions = results_data["test"]["wrong_answer_questions"]
            test_results = f"Количество ошибок в тесте: {len(wrong_questions)}\n"
            
            for i, q in enumerate(wrong_questions[:3], 1):  # Показываем первые 3 ошибки
                test_results += f"{i}. Вопрос {q.get('question_id', '?')}: {q.get('question', '')[:50]}...\n"
        
        prompt = PromptTemplates.LESSON_EVALUATION_PROMPT.format(
            speaking_notes=speaking_notes,
            reading_notes=reading_notes,
            test_results=test_results,
            feedback=feedback or ""
        )
        
        response = self.llm_client.generate(prompt)
        
        # Извлекаем JSON из ответа
        json_text = extract_json_from_text(response)
        
        try:
            result = json.loads(json_text)
            
            # Выводим полученный JSON
            print("\n" + "="*60)
            print("ПОЛУЧЕННАЯ ОЦЕНКА ОТ МОДЕЛИ:")
            print("="*60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст для парсинга: {json_text[:500]}...")
            
            # Возвращаем заглушку
            return {
                "lesson_score": "5",
                "knowledge_gaps": ["JSON parsing", "API connection"],
                "automated_feedback": "Ошибка при обработке результатов. Проверьте соединение с API.",
                "additional_lesson": True
            }
