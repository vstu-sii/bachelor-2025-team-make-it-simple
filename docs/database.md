### **Enum UserRole**
CREATE TYPE UserRole AS ENUM ('Ученик', 'Репетитор');

### **Таблица user**

| Поле           | Тип данных   | Описание                               | Индексы      |
| -------------- | ------------ | -------------------------------------- | ------------ |
| `user_id`      | SERIAL (PK)  | ID пользователя                        | PK           |
| `last_name`    | VARCHAR(50)  | Фамилия пользователя                   | INDEX        |
| `first_name`   | VARCHAR(50)  | Имя пользователя                       | INDEX        |
| `middle_name`  | VARCHAR(50)  | Отчество пользователя                  | -            |
| `birth_date`   | DATE         | Дата рождения пользователя             | -            |
| `phone`        | VARCHAR(20)  | Телефон пользователя                   | INDEX        |
| `telegram`     | VARCHAR(100) | Telegram пользователя                  | -            |
| `vk`           | VARCHAR(100) | Вконтакте пользователя                 | –            |
| `interests`    | TEXT         | Описание интересов пользователя        | –            |
| `role`         | USERROLE     | Роль в системе ("Ученик", "Репетитор") | -            |
| `email`        | VARCHAR(250) | Электронная почта пользователя         | UNIQUE INDEX |
| `password`     | VARCHAR(500) | Пароль пользователя                    | -            |
---

### **Таблица course**

| Поле                | Тип данных    | Описание                                                  | Индексы      |
| ------------------- | ------------- | --------------------------------------------------------- | ------------ |
| `course_id`         | SERIAL (PK)   | ID курса                                                  | PK           |
| `title`             | VARCHAR(150)  | Название курса                                            | INDEX        |
| `created_at`        | DATE          | Дата создания курса                                       | INDEX        |
| `link_to_vector_db` | VARCHAR(1000) | Путь к папке с файлами векторной базой данных             | -            |
| `input_test_json`   | JSON          | JSON файл (выходной) с составленным входным тестированием | -            |
---

### **Таблица user_course**

| Поле                 | Тип данных    | Описание                                                  | Индексы                               |
| -------------------- | ------------- | --------------------------------------------------------- | ------------------------------------- |
| `user_course_id`     | SERIAL (PK)   | ID записи связи между пользователем и курсом              | PK                                    |
| `user_id`            | INT           | ID пользователя                                           | INDEX                                 |
| `course_id`          | INT           | ID курса                                                  | INDEX                                 |
| `knowledge_gaps`     | TEXT          | Описания пробелов в знаниях ученика                       | -                                     |
| `graph_json`         | JSON          | JSON файл (выходной) для графа курса                      | -                                     |
| `output_test_json`   | JSON          | JSON файл с результатами входного тестирования            | -                                     |
| -                    | -             | Уникальная пара (user_id, course_id)                      | UNIQUE INDEX                          |
| -                    | -             | Каждый ученик является учащимся только одного курса       | UNIQUE INDEX (partial, role='Ученик') |
---

### **Таблица material**

| Поле          | Тип данных    | Описание                        | Индексы      |
| ------------- | ------------- | ------------------------------- | ------------ |
| `material_id` | SERIAL (PK)   | ID материала                    | PK           |
| `file_path`   | VARCHAR(1000) | Путь к папке с файлом материала | UNIQUE INDEX |
---

### **Таблица course_material**

| Поле          | Тип данных    | Описание                                 | Индексы      |
| ------------- | ------------- | ---------------------------------------- | ------------ |
| `course_id`   | INT           | ID курса                                 | INDEX        |
| `material_id` | INT           | ID материала                             | INDEX        |
| -             | -             | Уникальная пара (course_id, material_id) | UNIQUE INDEX |
---

### **Таблица topic**

| Поле               | Тип данных    | Описание      | Индексы      |
| ------------------ | ------------- | ------------- | ------------ |
| `topic_id`         | SERIAL (PK)   | ID темы       | PK           |
| `title`            | VARCHAR(150)  | Название темы | INDEX        |
| `description_text` | TEXT          | Описание темы | -            |
---

### **Таблица course_topic**

| Поле          | Тип данных    | Описание                                 | Индексы      |
| ------------- | ------------- | ---------------------------------------- | ------------ |
| `course_id`   | INT           | ID курса                                 | INDEX        |
| `topic_id`    | INT           | ID темы                                  | INDEX        |
| -             | -             | Уникальная пара (course_id, topic_id)    | UNIQUE INDEX |
---

### **Таблица lesson**

| Поле                       | Тип данных    | Описание                                                 | Индексы     |
| -------------------------- | ------------- | -------------------------------------------------------- | ----------- |
| `lesson_id`                | SERIAL (PK)   | ID урока                                                 | PK          |
| `theory_text`              | TEXT          | Текст с теоретическим материалом                         | -           |
| `reading_text`             | TEXT          | Текст задания на чтение                                  | -           |
| `speaking_text`            | TEXT          | Текст задания на говорение                               | -           |
| `lesson_plan_json`         | JSON          | JSON файл (выходной) с заданиями и тестом в рамках урока | -           |
| `lesson_test_results_json` | JSON          | JSON файл с результатами тестирования в рамках урока     | -           |
| `lesson_notes`             | TEXT          | Текст с заметками репетитора по уроку                    | -           |
| `results_json`             | JSON          | JSON файл (выходной) с результатами урока                | -           |
| `is_access`                | BOOLEAN       | Флаг, определяющий доступность урока ученику             | -           |
| `is_ended`                 | BOOLEAN       | Флаг, определяющий завершен ли урок                      | -           |
| `topic_id`                 | INT           | ID темы                                                  | -           |
---

# Взаимодействие с AI-сервисом

### API: POST /ai/<task_type>

- Метод: POST;
- Путь: /ai/<task_type>, где <task_type> — один из типов генерации (например, /ai/course_graph - построение графа курса);
- Заголовок запроса "Content-Type": application/json;
- Заголовок запроса "Authorization": Bearer <api_key> (API-ключ сервиса).

### Логика работы сервера и стандартные коды ответов

#### Общая логика работы сервера
1. Входной HTTP-запрос POST /ai/<task_type> содержит тело с параметрами.
2. Сервер:
- валидирует task_type и тело запроса;
- собирает дополнительные данные из БД;
- формирует messages (system + история чата + task-specific prompt) - массив сообщений для LLM;
- вызывает внешний AI-сервис (POST) с финальным JSON-запросом;
- получает ответ, парсит, извлекает структурированные данные и/или текст;
- сохраняет результат в БД в соответствующие поля;
- возвращает клиенту статус + тело с результатом.

#### Стандартные коды ответов сервера

- 200 OK - результат успешно сформирован и сохранён;
- 202 Accepted - асинхронная обработка;
- 400 Bad Request - ошибка в валидации тела запроса;
- 401 Unauthorized - неверный API key;
- 429 Too Many Requests - rate limit AI или клиент;
- 500 Internal Server Error - ошибка сервера.

## Формат отправляемых данных (Запрос к AI-сервису)

Запрос отправляется как HTTP POST на endpoint AI-сервиса.<br />Телом запроса является JSON-объект.

### Пример JSON-запроса

```json
{
    "model": "model_name",
    "messages": [
        {
            "role": "system",
            "content": "<system prompt with placeholders filled>"
        },
        {
            "role": "user",
            "content": "<optional user message or short prompt>"
        },
        {
            "role": "assistant",
            "content": "<previous assistant replies>"
        },
        // история чата
        {
            "role": "user",
            "content": "<task-specific payload or final instruction>"
        }
    ],
    "max_tokens": 800,
    "temperature": 0.3,
    "stream": false
}
```

-   ***model***: строка, указывающая модель LLM;
-   ***messages***: массив объектов, где каждый объект представляет собой сообщение, где:
    -   ***role***: 'system' (для первого системного промпта), 'user' (для сообщения пользователя), 'assistant' (для ответов модели);
    -   ***content***: текст сообщения.
-   ***max_tokens***: ограничение на число токенов в ответе;
-   ***temperature***: значение от 0 до 1, которое контролирует регулирует степень креативности сообщения;
-   ***stream***: bool значение для потоковой передачи ответа.

## Формат получаемых данных (Ответ от AI-сервиса)

Ответом яляется JSON-объект. Сервер парсит его, извлекает content из choices[0].message.content и сохраняет как новое сообщение в messages с role = 'assistant'.

### Пример JSON-ответа для входного тестирования

```
{
  "id": "<уникальный id ответа>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": {
          "questions": [
            {
              "question_id": "1",
              "type": "short_answer",
              "question": "What is your name and how old are you?",
              "max_length": 50,
              "correct_answer": "My name is Slava, I am 20"
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
        }
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 180,
    "completion_tokens": 320,
    "total_tokens": 500
  },
  "created": 1727548800
}
```

- ***id***: уникальный ID ответа AI;

- ***choices***: массив, обычно состоящий из одного элемента, в котором message.content содержит JSON с вопросами входного тестирования (questions);

- ***message.role***: "assistant";

- ***message.content***: JSON с массивом questions (каждый вопрос с типом, вариантами, правильными ответами и т.д.);

- ***finish_reason***: причина завершения генерации (например, stop/length/max_tokens);

- ***usage***: количество токенов;

- ***created***: timestamp создания ответа.
