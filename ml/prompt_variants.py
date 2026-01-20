"""
Варианты промптов для A/B тестирования.
"""

from prompt_templates import PromptTemplates
from ab_testing import PromptVariant
from typing import Dict, Any, List

# ===== ВАРИАНТЫ ДЛЯ ВХОДНОГО ТЕСТА =====

ENTRY_TEST_VARIANTS = {
    PromptVariant.VARIANT_A: PromptTemplates.ENTRY_TEST_PROMPT,  # Базовый вариант
    
    PromptVariant.VARIANT_B: """Сгенерируй входной тест по английскому языку. Возвращай ТОЛЬКО JSON.

КУРС: {course_title}
ТЕМЫ: {topics}

СОЗДАЙ 8 ВОПРОСОВ разных типов:
1. short_answer: вопрос, max_length, правильный ответ
2. single_choice: вопрос, варианты, правильный индекс
3. multiple_choice: вопрос, варианты, правильные индексы
4. gaps_choice: текст с пропусками, варианты для каждого

ФОРМАТ JSON:
{{
  "questions": [
    {{
      "question_id": "1",
      "type": "short_answer",
      "question": "текст вопроса",
      "max_length": число,
      "correct_answer": "правильный ответ"
    }}
  ]
}}

ВАЖНО: Все вопросы на английском. Правильные ответы должны быть точными.""",
    
    PromptVariant.VARIANT_C: """Ты AI-тьютор по английскому. Создай входной тест.

Информация:
- Курс: {course_title}
- Охватываемые темы: {topics}

Требования к тесту:
• 10 вопросов разных форматов
• Вопросы должны проверять базовые знания
• Используй актуальные и практические примеры

Типы вопросов:
A) Краткий ответ (short_answer) - 2 вопроса
B) Один правильный вариант (single_choice) - 4 вопроса  
C) Несколько правильных вариантов (multiple_choice) - 2 вопроса
D) Заполнение пропусков (gaps_choice) - 2 вопроса

Структура ответа (JSON):
{{
  "test_info": {{
    "course": "{course_title}",
    "topics_covered": "{topics}",
    "total_questions": 10
  }},
  "questions": [
    {{
      "id": "1",
      "type": "short_answer",
      "text": "What is your name?",
      "constraints": {{
        "max_length": 50
      }},
      "answer": {{
        "correct": "My name is Alex"
      }}
    }}
  ]
}}

Будь креативным, но практичным. Тест должен быть полезным для оценки уровня студента."""
}

# ===== ВАРИАНТЫ ДЛЯ ГРАФА КУРСА =====

COURSE_GRAPH_VARIANTS = {
    PromptVariant.VARIANT_A: PromptTemplates.COURSE_GRAPH_PROMPT,
    
    PromptVariant.VARIANT_B: """Создай граф зависимостей тем курса. JSON формат.

СТУДЕНТ:
- Интересы: {interests}
- Пробелы: {knowledge_gaps}

КУРС:
- Название: {course_title}
- Темы: {topics}

СОЗДАЙ:
1. Узлы (nodes) для каждой темы с id, label, group
2. Связи (edges) между узлами, показывающие зависимости

ФОРМАТ:
{{
  "metadata": {{
    "course": "{course_title}",
    "student_interests": "{interests}",
    "topics_count": [число тем]
  }},
  "nodes": [
    {{
      "id": "1",
      "label": "Название темы",
      "group": 1,
      "description": "Краткое описание"
    }}
  ],
  "edges": [
    {{
      "from": "id_исходного_узла",
      "to": "id_целевого_узла",
      "type": "prerequisite"  # или "recommended", "corequisite"
    }}
  ]
}}

Сделай граф логичным и полезным для построения учебного плана.""",
    
    PromptVariant.VARIANT_C: """Как эксперт по педагогическому дизайну, создай граф обучения.

КОНТЕКСТ:
• Студент интересуется: {interests}
• Нужно улучшить: {knowledge_gaps}
• Курс: {course_title}
• Темы для изучения: {topics}

ЗАДАЧА:
Разработать визуальную карту обучения в формате JSON, показывающую:
1. Основные модули (nodes)
2. Зависимости между ними (edges)
3. Группы тем по сложности
4. Рекомендуемую последовательность изучения

ОСОБЫЕ ТРЕБОВАНИЯ:
• Начни с самых базовых тем
• Учитывай интересы студента при выборе примеров
• Отметь темы, которые закрывают пробелы в знаниях
• Предложи альтернативные пути изучения

JSON СТРУКТУРА:
{{
  "learning_graph": {{
    "course": "{course_title}",
    "target_audience": "студент с интересами в {interests}",
    "nodes": [
      {{
        "id": "уникальный_id",
        "title": "название темы на русском",
        "level": "beginner|intermediate|advanced",
        "priority": "high|medium|low",
        "estimated_hours": число,
        "covers_gaps": ["пробел1", "пробел2"] или []
      }}
    ],
    "dependencies": [
      {{
        "source": "id_предварительной_темы",
        "target": "id_последующей_темы",
        "strength": "required|recommended|optional"
      }}
    ],
    "learning_paths": [
      {{
        "name": "Основной путь",
        "node_sequence": ["id1", "id2", "id3"]
      }}
    ]
  }}
}}

Создай эффективную и мотивирующую структуру курса."""
}

# ===== ВАРИАНТЫ ДЛЯ ТЕОРИИ УРОКА =====

LESSON_THEORY_VARIANTS = {
    PromptVariant.VARIANT_A: PromptTemplates.LESSON_THEORY_PROMPT,
    
    PromptVariant.VARIANT_B: """Создай теоретическую часть урока. JSON формат.

ТЕМА УРОКА: {topic}
ИНТЕРЕСЫ СТУДЕНТА: {interests}
ПРОБЕЛЫ В ЗНАНИЯХ: {knowledge_gaps}

СТРУКТУРА УРОКА:
1. Заголовок и краткое описание
2. Ключевые концепции
3. Примеры (связанные с интересами студента)
4. Практические советы
5. Частые ошибки и как их избежать

ФОРМАТ:
{{
  "lesson": {{
    "topic": "{topic}",
    "target_audience": "студент с интересами в {interests}",
    "estimated_duration": "45 минут",
    "sections": [
      {{
        "title": "Название раздела",
        "content": "Текст на русском с объяснениями",
        "examples": [
          "Пример на английском",
          "Еще пример"
        ],
        "key_points": ["ключевой момент 1", "ключевой момент 2"]
      }}
    ],
    "common_mistakes": [
      {{
        "mistake": "Описание ошибки",
        "correction": "Как правильно",
        "tip": "Совет по запоминанию"
      }}
    ],
    "practice_exercises": [
      {{
        "type": "drill|application|creative",
        "instruction": "Инструкция на русском",
        "example": "Пример выполнения"
      }}
    ]
  }}
}}

Сделай урок engaging и практичным. Используй примеры из области интересов студента.""",
    
    PromptVariant.VARIANT_C: """Ты - опытный преподаватель английского. Разработай интерактивный урок.

ТЕМА: {topic}
ПРОФИЛЬ СТУДЕНТА:
• Увлечения: {interests}
• Слабые места: {knowledge_gaps}

ЦЕЛЬ УРОКА:
Не просто объяснить теорию, а сделать её применимой в контексте интересов студента.

СТРУКТУРА УРОКА ДОЛЖНА ВКЛЮЧАТЬ:
🎯 Цели обучения (что студент будет уметь после урока)
📚 Теоретическая часть (просто и ясно)
🎮 Практические примеры (используй контекст интересов)
💡 Лайфхаки и мнемонические правила
⚠️ Типичные ошибки и как их избежать
🔍 Мини-кейсы для применения знаний

ФОРМАТ ОТВЕТА:
{{
  "interactive_lesson": {{
    "theme": "{topic}",
    "personalized_for": "{interests}",
    "duration_minutes": 60,
    "learning_objectives": [
      "Цель 1",
      "Цель 2",
      "Цель 3"
    ],
    "content_blocks": [
      {{
        "block_type": "theory|example|exercise|tip",
        "title": "Заголовок блока",
        "content": "Содержание на русском",
        "english_examples": ["Пример 1", "Пример 2"],
        "interactive_element": "вопрос для размышления | мини-задание | quiz вопрос"
      }}
    ],
    "gamification_elements": [
      {{
        "type": "challenge|achievement|progress_tracker",
        "description": "Описание игрового элемента",
        "implementation": "Как использовать в уроке"
      }}
    ],
    "assessment": {{
      "pre_lesson_questions": ["Вопрос 1", "Вопрос 2"],
      "post_lesson_check": "Критерии успешного усвоения"
    }}
  }}
}}

Создай урок, который будет не только информативным, но и увлекательным!"""
}

# ===== РЕГИСТРАЦИЯ ЭКСПЕРИМЕНТОВ =====

def register_all_experiments(ab_manager):
    """Регистрация всех экспериментов."""
    
    # Эксперимент 1: Входные тесты
    ab_manager.register_experiment(
        experiment_id="entry_test_generation",
        variants=ENTRY_TEST_VARIANTS
    )
    
    # Эксперимент 2: Графы курсов
    ab_manager.register_experiment(
        experiment_id="course_graph_generation",
        variants=COURSE_GRAPH_VARIANTS
    )
    
    # Эксперимент 3: Теория уроков
    ab_manager.register_experiment(
        experiment_id="lesson_theory_generation",
        variants=LESSON_THEORY_VARIANTS
    )
    
    print("✅ Все эксперименты зарегистрированы")
    return ab_manager

# ===== УТИЛИТЫ ДЛЯ АНАЛИЗА =====

def analyze_prompt_token_usage(prompt: str) -> Dict[str, Any]:
    """Анализ использования токенов в промпте."""
    words = prompt.split()
    sentences = prompt.split('. ')
    paragraphs = prompt.split('\n\n')
    
    return {
        "total_words": len(words),
        "total_sentences": len(sentences),
        "total_paragraphs": len(paragraphs),
        "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0,
        "readability_score": calculate_readability(prompt),
        "repetition_score": calculate_repetition_score(prompt)
    }

def calculate_readability(text: str) -> float:
    """Оценка читаемости текста (0-100, выше - проще)."""
    # Упрощенная формула
    words = text.split()
    sentences = text.split('. ')
    
    if len(words) == 0 or len(sentences) == 0:
        return 0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Чем короче предложения и слова, тем выше читаемость
    readability = 100 - (avg_sentence_length * 0.5 + avg_word_length * 10)
    return max(0, min(100, readability))

def calculate_repetition_score(text: str) -> float:
    """Оценка повторений в тексте (0-100, ниже - лучше)."""
    words = text.lower().split()
    if len(words) < 10:
        return 0
    
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Игнорируем короткие слова
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Процент уникальных слов
    unique_words = len([w for w, f in word_freq.items() if f == 1])
    repetition_score = 100 - (unique_words / len(words) * 100)
    
    return max(0, min(100, repetition_score))

def compare_prompt_variants(variants: Dict[PromptVariant, str]) -> Dict[str, Any]:
    """Сравнение вариантов промптов."""
    analysis = {}
    
    for variant, prompt in variants.items():
        analysis[variant.value] = {
            "token_analysis": analyze_prompt_token_usage(prompt),
            "length_chars": len(prompt),
            "length_words": len(prompt.split()),
            "instruction_clarity": estimate_instruction_clarity(prompt)
        }
    
    return analysis

def estimate_instruction_clarity(prompt: str) -> float:
    """Оценка четкости инструкций в промпте."""
    clarity_indicators = [
        "возвращай только json",
        "формат:",
        "структура:",
        "пример:",
        "важно:",
        "требования:",
        "создай",
        "сгенерируй",
        "используй"
    ]
    
    prompt_lower = prompt.lower()
    indicator_count = sum(1 for indicator in clarity_indicators if indicator in prompt_lower)
    
    # Максимальная оценка - 100
    clarity_score = (indicator_count / len(clarity_indicators)) * 100
    return min(100, clarity_score)

# ===== BEST PRACTICES =====

PROMPT_BEST_PRACTICES = {
    "clarity": [
        "Используй четкие и конкретные инструкции",
        "Определи формат ответа явно",
        "Укажи, что нужно вернуть только JSON",
        "Давай примеры ожидаемого формата"
    ],
    "efficiency": [
        "Избегай избыточных объяснений",
        "Используй маркированные списки для структурирования",
        "Группируй связанные инструкции",
        "Убирай повторы"
    ],
    "quality": [
        "Учитывай контекст пользователя",
        "Персонализируй примеры",
        "Давай практические советы",
        "Предусматривай edge cases"
    ],
    "token_optimization": [
        "Используй сокращения где это не влияет на ясность",
        "Объединяй похожие инструкции",
        "Убирай приветствия и заключения",
        "Используй стандартные форматы"
    ]
}

def generate_optimized_prompt(base_prompt: str, optimization_rules: List[str] = None) -> str:
    """
    Генерация оптимизированного промпта на основе best practices.
    
    Args:
        base_prompt: Исходный промпт
        optimization_rules: Правила оптимизации
        
    Returns:
        Оптимизированный промпт
    """
    if optimization_rules is None:
        optimization_rules = [
            "Убрать приветствия",
            "Сократить избыточные объяснения",
            "Объединить похожие инструкции",
            "Добавить четкий формат ответа"
        ]
    
    # Простая оптимизация (в реальности нужен более сложный алгоритм)
    optimized = base_prompt
    
    # Убираем приветствия
    greetings = ["привет", "здравствуй", "дорогой", "уважаемый"]
    for greeting in greetings:
        if greeting in optimized.lower():
            # Находим и удаляем строку с приветствием
            lines = optimized.split('\n')
            lines = [line for line in lines if greeting not in line.lower()]
            optimized = '\n'.join(lines)
    
    # Сокращаем избыточные фразы
    redundancy_patterns = {
        "пожалуйста, пожалуйста": "пожалуйста",
        "очень важно отметить, что": "важно:",
        "хотелось бы подчеркнуть, что": "",
        "необходимо отметить, что": ""
    }
    
    for pattern, replacement in redundancy_patterns.items():
        optimized = optimized.replace(pattern, replacement)
    
    # Добавляем четкие инструкции про JSON если их нет
    if "возвращай только json" not in optimized.lower():
        optimized = "Возвращай ТОЛЬКО JSON в указанном формате.\n\n" + optimized
    
    return optimized