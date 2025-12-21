"""
Шаблоны промптов для всех задач AI-тьютора.
"""

class PromptTemplates:
    """Класс с шаблонами промптов."""
    
    # 1. Промпт для входного тестирования
    ENTRY_TEST_PROMPT = """Сгенерируй входной тест по английскому языку. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ О КУРСЕ:
- Название курса: {course_title}
- Темы курса: {topics}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ТЕСТУ:
1. Создай 12 вопросов разных типов
2. Вопросы должны покрывать все указанные темы
3. Используй ВСЕ следующие типы вопросов:
   - short_answer (краткий ответ студента)
   - single_choice (один правильный вариант)
   - multiple_choice (несколько правильных вариантов)
   - gaps_choice (заполнение пропусков в тексте)

ПРАВИЛА ДЛЯ КАЖДОГО ТИПА ВОПРОСА:

1. short_answer:
   - question: вопрос на английском
   - max_length: число (макс. длина ответа)
   - correct_answer: строка с правильным ответом на английском

2. single_choice:
   - question: вопрос на английском
   - options: массив строк с вариантами ответов на английском
   - correct_answer: ЧИСЛО (индекс правильного варианта, начиная с 0)

3. multiple_choice:
   - question: вопрос на английском
   - options: массив строк с вариантами ответов на английском
   - correct_answers: массив ЧИСЕЛ (индексы правильных вариантов, начиная с 0)

4. gaps_choice:
   - question: текст с пропусками в формате "Текст [1] с [2] пропусками"
   - gaps: массив объектов, каждый с полями:
     * gap_id: номер пропуска (начинается с 1)
     * options: массив строк с вариантами заполнения
     * correct_answer: ЧИСЛО (индекс правильного варианта, начиная с 0)

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "questions": [
    {{
      "question_id": "1",
      "type": "short_answer",
      "question": "What is your name and how old are you?",
      "max_length": 50,
      "correct_answer": "My name is Alex, I am 25 years old"
    }},
    {{
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
    }},
    {{
      "question_id": "3",
      "type": "multiple_choice",
      "question": "Which words are articles in English?",
      "options": ["the", "a", "an", "is", "and"],
      "correct_answers": [0, 1, 2]
    }},
    {{
      "question_id": "4",
      "type": "gaps_choice",
      "question": "If I [1] enough money, I [2] travel around the world. I [3] to visit Japan for a long time because I [4] fascinated by its culture. When I [5] there, I want to try traditional food and [6] historical temples.",
      "gaps": [
        {{
          "gap_id": 1,
          "options": ["have", "had", "will have", "would have"],
          "correct_answer": 1
        }},
        {{
          "gap_id": 2,
          "options": ["would", "will", "can", "could"],
          "correct_answer": 0
        }},
        {{
          "gap_id": 3,
          "options": ["have wanted", "want", "wanted", "wanting"],
          "correct_answer": 0
        }},
        {{
          "gap_id": 4,
          "options": ["am", "was", "have been", "had been"],
          "correct_answer": 0
        }},
        {{
          "gap_id": 5,
          "options": ["go", "will go", "went", "have gone"],
          "correct_answer": 0
        }},
        {{
          "gap_id": 6,
          "options": ["visit", "visiting", "visited", "to visit"],
          "correct_answer": 0
        }}
      ]
    }}
  ]
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. Все поля question должны быть на английском языке
3. correct_answer для single_choice и gaps_choice должно быть ЧИСЛОМ (индексом)
4. correct_answers для multiple_choice должно быть МАССИВОМ ЧИСЕЛ
5. Для gaps_question создай связный текст с 4-6 пропусками
6. gap_id начинаются с 1 и идут по порядку
7. Учти замечания репетитора при генерации: {feedback}"""
    
    # 2. Промпт для графа курса
    COURSE_GRAPH_PROMPT = """Создай граф зависимостей тем курса. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ О СТУДЕНТЕ:
- Интересы: {interests}
- Пробелы в знаниях: {knowledge_gaps}

ИНФОРМАЦИЯ О КУРСЕ:
- Название курса: {course_title}
- Темы курса: {topics}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ГРАФУ:
1. Создай узлы для каждой темы курса
2. Учти замечания репетитора при построении связей
3. Каждому узлу присвой уникальный id (строка)
4. Создай связи (edges) между узлами, показывающие зависимости

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "nodes": [
    {{
      "id": "1",
      "label": "Present Simple"
    }},
    {{
      "id": "2",
      "label": "Артикли a/an/the"
    }},
    {{
      "id": "3",
      "label": "Базовая лексика"
    }},
    {{
      "id": "4",
      "label": "Предлоги места и времени"
    }},
    {{
      "id": "5",
      "label": "Вопросы с do/does"
    }}
  ],
  "edges": [
    {{
      "from": "3",
      "to": "1"
    }},
    {{
      "from": "1",
      "to": "2"
    }},
    {{
      "from": "1",
      "to": "4"
    }},
    {{
      "from": "1",
      "to": "5"
    }},
    {{
      "from": "2",
      "to": "5"
    }}
  ]
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. id должны быть строками ("1", "2", "3" и т.д.)
3. label должны быть на русском языке
4. from и to в edges должны быть строками, ссылающимися на id узлов
5. Создай реалистичные зависимости между темами
6. Учти замечания репетитора: {feedback}"""
    
    # 3. Промпт для теории урока
    LESSON_THEORY_PROMPT = """Создай теоретическую часть урока по английскому языку. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ ДЛЯ УРОКА:
- Тема урока: {topic}
- Интересы студента: {interests}
- Пробелы в знаниях: {knowledge_gaps}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ТЕОРИИ:
1. Объясни тему урока простым и понятным языком
2. Учти замечания репетитора при создании контента
3. Удели особое внимание указанным пробелам в знаниях
4. Используй примеры, связанные с интересами студента
5. Включи основные правила, структуры и исключения
6. Добавь 3-5 примеров предложений
7. Используй русский язык для объяснений, но английский для примеров
8. Разделяй контент на логические части с помощью \\n\\n

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "theory_section": {{
    "title": "Present Simple для описания привычек и регулярных действий",
    "content": "Present Simple используется для описания регулярных действий, привычек, общих истин и постоянных состояний.\\n\\nСТРУКТУРА:\\n- Утвердительные предложения:\\n  I/You/We/They + базовая форма глагола (I play)\\n  He/She/It + базовая форма глагола + s (He plays)\\n\\n- Отрицательные предложения:\\n  I/You/We/They + do not (don't) + глагол (I don't play)\\n  He/She/It + does not (doesn't) + глагол (He doesn't play)\\n\\n- Вопросительные предложения:\\n  Do + I/you/we/they + глагол? (Do you play?)\\n  Does + he/she/it + глагол? (Does he play?)\\n\\nПРАВИЛА ДОБАВЛЕНИЯ -S:\\n1. К большинству глаголов: play -> plays\\n2. К глаголам на -s, -ss, -sh, -ch, -x, -o: add -> adds\\n3. К глаголам на согласная + y: study -> studies\\n\\nПРИМЕРЫ С ИНТЕРЕСАМИ СТУДЕНТА:\\n- I play video games every evening.\\n- My favorite football team plays on Sundays.\\n- New technology appears every year.\\n- She doesn't like strategy games.\\n- Do you watch technology reviews on YouTube?"
  }}
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. title должен быть на русском языке
3. content должен содержать объяснения на русском и примеры на английском
4. Используй \\n для переносов строк внутри content
5. Адаптируй примеры под интересы студента: {interests}
6. Удели внимание пробелам: {knowledge_gaps}
7. Учти замечания репетитора: {feedback}"""
    
    # 4. Промпт для задания на чтение
    LESSON_READING_PROMPT = """Создай задание на чтение для урока английского языка. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ ДЛЯ УРОКА:
- Тема урока: {topic}
- Интересы студента: {interests}
- Пробелы в знаниях: {knowledge_gaps}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ТЕКСТУ:
1. Напиши текст на английском языке (150-200 слов)
2. Текст должен быть связан с интересами студента
3. Учти замечания репетитора при создании текста
4. Используй грамматику и лексику текущей темы урока
5. Текст должен быть увлекательным и информативным
6. Добавь 3-4 вопроса на понимание текста
7. Вопросы должны быть на английском языке
8. Вопросы должны проверять понимание деталей текста

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "reading_section": {{
    "title": "Daily Routine of a Technology Enthusiast",
    "text": "My name is Alex. I am a university student and a big fan of technology and video games. Every morning, I wake up at 7:30 AM. I check my phone for new technology news while having breakfast. Then I go to my university classes. After classes, I usually meet with my friends. We often play online video games together. Our favorite game is a football simulator where we compete against other teams. In the evening, I study for my exams and watch YouTube videos about the latest technological innovations. I am particularly interested in artificial intelligence and how it changes our daily lives. On weekends, I spend more time gaming and sometimes attend local technology meetups. My dream is to work in the gaming industry and develop educational games that make learning more fun and interactive.",
    "comprehension_questions": [
      "What time does Alex wake up every morning?",
      "What does Alex do while having breakfast?",
      "What type of games does Alex play with friends?",
      "What is Alex's dream job?"
    ]
  }}
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. Все поля (title, text, comprehension_questions) должны быть на английском языке
3. Текст должен быть связным рассказом
4. comprehension_questions должны проверять понимание ключевых деталей текста
5. Количество вопросов: 3-4
6. Адаптируй текст под интересы студента: {interests}
7. Учти замечания репетитора: {feedback}"""
    
    # 5. Промпт для задания на говорение
    LESSON_SPEAKING_PROMPT = """Создай задание на говорение для урока английского языка. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ ДЛЯ УРОКА:
- Тема урока: {topic}
- Интересы студента: {interests}
- Пробелы в знаниях: {knowledge_gaps}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ЗАДАНИЮ:
1. Создай тему для монолога или обсуждения
2. Тема должна быть связана с интересами студента
3. Учти замечания репетитора при создании задания
4. Упражнение должно практиковать грамматику и лексику текущей темы
5. Дай четкие и конкретные инструкции студенту
6. Включи пример ответа для вдохновения
7. Укажи рекомендуемую продолжительность речи (2-3 минуты)

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "speaking_section": {{
    "title": "Опишите свой ежедневный распорядок, связанный с технологиями",
    "instructions": "Расскажите о своём ежедневном распорядке дня, уделяя особое внимание тому, как вы используете технологии и видеоигры. Используйте Present Simple для описания регулярных действий. Говорите 2-3 минуты. Постарайтесь включить информацию о том: 1) Когда вы обычно используете технологии, 2) Какие устройства или приложения вы предпочитаете, 3) Как технологии помогают вам в учёбе или отдыхе.",
    "example_response": "I usually start my day by checking my smartphone for messages and news. I often read technology blogs while having breakfast. During my university breaks, I watch short videos about new gadgets or game reviews. In the evening, I play online games with my friends for about an hour. We usually play football games or strategy games. Before going to bed, I sometimes program small applications as a hobby. Technology helps me stay connected with friends and learn new things every day."
  }}
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. title и instructions должны быть на русском языке
3. example_response должен быть на английском языке
4. instructions должны быть четкими и конкретными
5. Упражнение должно длиться 2-3 минуты
6. Адаптируй тему под интересы студента: {interests}
7. Учти замечания репетитора: {feedback}"""
    
    # 6. Промпт для теста урока
    LESSON_TEST_PROMPT = """Создай тест для урока английского языка. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ ДЛЯ УРОКА:
- Тема урока: {topic}
- Теория урока: {theory}
- Интересы студента: {interests}
- Пробелы в знаниях: {knowledge_gaps}

ЗАМЕЧАНИЯ ПО ГЕНЕРАЦИИ:
{feedback}

ТРЕБОВАНИЯ К ТЕСТУ:
1. Создай 7-8 вопросов по теме урока
2. Используй теорию урока как основу для вопросов
3. Учти замечания репетитора при создании вопросов
4. Вопросы должны практиковать указанные пробелы в знаниях
5. Используй разные типы вопросов: single_choice, multiple_choice, short_answer
6. Включи вопросы с примерами из интересов студента
7. Все ответы должны быть правильными и соответствовать теме

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "test_section": {{
    "title": "Тест по Present Simple: Привычки и регулярные действия",
    "questions": [
      {{
        "question_id": "1",
        "type": "single_choice",
        "question": "Choose the correct sentence in Present Simple:",
        "options": [
          "I plays video games every day",
          "I play video games every day",
          "I playing video games every day",
          "I am play video games every day"
        ],
        "correct_answer": 1
      }},
      {{
        "question_id": "2",
        "type": "multiple_choice",
        "question": "Which time expressions are typically used with Present Simple?",
        "options": ["yesterday", "every day", "now", "usually", "last week"],
        "correct_answers": [1, 3]
      }},
      {{
        "question_id": "3",
        "type": "short_answer",
        "question": "What do you usually do in your free time related to your interests?",
        "max_length": 100,
        "correct_answer": "I usually play video games or watch technology reviews in my free time."
      }},
      {{
        "question_id": "4",
        "type": "single_choice",
        "question": "Which sentence correctly uses Present Simple for he/she/it?",
        "options": [
          "He watch football matches every weekend",
          "He watches football matches every weekend",
          "He watching football matches every weekend",
          "He is watch football matches every weekend"
        ],
        "correct_answer": 1
      }}
    ]
  }}
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. title должен быть на русском языке
3. questions и options должны быть на английском
4. question_id должны быть строками ("1", "2", и т.д.)
5. correct_answer для single_choice должно быть ЧИСЛОМ (индекс правильного ответа)
6. correct_answers для multiple_choice должно быть МАССИВОМ ЧИСЕЛ
7. Включи max_length для short_answer вопросов
8. Адаптируй вопросы под интересы студента: {interests}
9. Учти замечания репетитора: {feedback}"""
    
    # 7. Промпт для оценки результатов урока
    LESSON_EVALUATION_PROMPT = """Оцени результаты урока английского языка и дай обратную связь. Возвращай ТОЛЬКО JSON в указанном формате.

ИНФОРМАЦИЯ О РЕЗУЛЬТАТАХ:
- Заметки репетитора по говорению: {speaking_notes}
- Заметки репетитора по чтению: {reading_notes}
- Результаты теста: {test_results}

ЗАМЕЧАНИЯ ПО ОЦЕНКЕ:
{feedback}

ТРЕБОВАНИЯ К ОЦЕНКЕ:
1. Проанализируй все предоставленные данные
2. Учти замечания репетитора при оценке
3. Определи основные пробелы в знаниях студента
4. Оцени понимание темы по шкале от 1 до 10
5. Дай конструктивную обратную связь на русском языке
6. Рекомендуй, нужен ли дополнительный урок по этой теме

КРИТЕРИИ ОЦЕНКИ:
- 1-3: Не понимает тему, требуется полное повторение
- 4-6: Понимает основы, но есть значительные пробелы
- 7-8: Хорошо понимает тему, небольшие ошибки
- 9-10: Отличное понимание, минимальные ошибки

ВОЗВРАЩАЙ ТОЛЬКО JSON В ТОЧНОМ ФОРМАТЕ:

{{
  "lesson_score": "7",
  "knowledge_gaps": ["Time expressions with Present Simple", "Forming questions with do/does"],
  "automated_feedback": "Хорошая работа! Вы показали понимание базовой структуры Present Simple в утвердительных предложениях. Однако нужно поработать с временными выражениями (every day, usually, often) и построением вопросов с do/does. Обратите внимание на добавление -s к глаголам для he/she/it. Рекомендую дополнительную практику с упражнениями на вопросы и отрицания.",
  "additional_lesson": true
}}

ВАЖНО:
1. Возвращай ТОЛЬКО JSON без дополнительного текста
2. lesson_score должен быть строкой с числом от 1 до 10 (например: "7", "8")
3. knowledge_gaps должен быть массивом строк на английском языке
4. automated_feedback должен быть на русском языке
5. additional_lesson должен быть boolean (true/false)
6. Будь объективен и конструктивен в оценке
7. Учитывай все предоставленные данные в оценке
8. Учти замечания репетитора: {feedback}"""
