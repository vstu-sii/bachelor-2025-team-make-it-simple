-- Очистка таблиц --
TRUNCATE TABLE course_material CASCADE;
TRUNCATE TABLE course_topic CASCADE;
TRUNCATE TABLE user_course CASCADE;
TRUNCATE TABLE material CASCADE;
TRUNCATE TABLE topic CASCADE;
TRUNCATE TABLE lesson CASCADE;
TRUNCATE TABLE course CASCADE;

-- 1. Заполняем курсы
INSERT INTO course (title, created_at, link_to_vector_db, input_test_json) VALUES 
('Английский для начинающих (A1)', '2024-01-15', '/vector_db/courses/beginner_a1', '{"test_type": "placement", "questions": 20}'),
('Разговорный английский (A2-B1)', '2024-02-10', '/vector_db/courses/conversational_a2', '{"test_type": "placement", "questions": 25}'),
('Бизнес английский (B1-B2)', '2024-02-28', '/vector_db/courses/business_b1', '{"test_type": "business_skills", "questions": 30}'),
('Подготовка к IELTS (B2-C1)', '2024-03-15', '/vector_db/courses/ielts_b2', '{"test_type": "ielts_practice", "questions": 40}'),
('Английский для IT-специалистов (B1)', '2024-03-20', '/vector_db/courses/it_english_b1', '{"test_type": "technical", "questions": 35}'),
('Английский для путешествий (A2)', '2024-04-01', '/vector_db/courses/travel_a2', '{"test_type": "travel_scenarios", "questions": 25}');

-- 2. Заполняем материалы
INSERT INTO material (file_path) VALUES
('/materials/beginner/grammar_basics.pdf'),
('/materials/beginner/vocabulary_a1.zip'),
('/materials/conversational/dialogues_mp3.zip'),
('/materials/business/presentations.pptx'),
('/materials/business/emails_templates.docx'),
('/materials/ielts/writing_samples.pdf'),
('/materials/ielts/listening_tests.zip'),
('/materials/it/technical_terms.pdf'),
('/materials/travel/phrasebook.pdf'),
('/materials/travel/airport_dialogues.mp3'),
('/materials/common/irregular_verbs.pdf'),
('/materials/common/prepositions_exercises.pdf');

-- 3. Заполняем темы
INSERT INTO topic (title, description_text) VALUES
('Present Simple', 'Настоящее простое время: базовые правила и употребление'),
('Past Simple', 'Прошедшее простое время: правильные и неправильные глаголы'),
('Future Tenses', 'Будущие времена: will, going to, present continuous'),
('Modal Verbs', 'Модальные глаголы: can, could, should, must, have to'),
('Articles', 'Артикли a/an/the: правила употребления'),
('Business Vocabulary', 'Деловая лексика: переговоры, презентации, встречи'),
('IELTS Writing Task 1', 'Академическое письмо: описание графиков и диаграмм'),
('IELTS Speaking Part 2', 'Монолог на заданную тему в течение 2 минут'),
('IT Terminology', 'Техническая терминология: разработка, тестирование, deployment'),
('Travel Phrases', 'Фразы для путешествий: аэропорт, отель, ресторан'),
('Phrasal Verbs', 'Фразовые глаголы с примерами употребления'),
('Conditionals', 'Условные предложения: zero, first, second, third conditional');

-- 4. Связываем курсы с материалами
INSERT INTO course_material (course_id, material_id) VALUES
(1, 1), (1, 2), (1, 11), (1, 12),
(2, 3), (2, 11), (2, 12),
(3, 4), (3, 5), (3, 6),
(4, 6), (4, 7),
(5, 8), (5, 9),
(6, 9), (6, 10);

-- 5. Связываем курсы с темами
INSERT INTO course_topic (course_id, topic_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
(2, 1), (2, 2), (2, 3), (2, 11),
(3, 4), (3, 6),
(4, 7), (4, 8), (4, 12),
(5, 9), (5, 4),
(6, 10), (6, 1), (6, 2);

-- 6. Заполняем уроки (по 3 урока на курс)
INSERT INTO lesson (theory_text, reading_text, speaking_text, lesson_test_json, is_access, is_ended) VALUES
-- Курс 1: Английский для начинающих
('Present Simple: теория и примеры', 'Текст о ежедневных привычках', 'Обсуждение вашего распорядка дня', '{"questions": ["Что такое Present Simple?", "Приведите 3 примера"]}', true, false),
('Past Simple: правильные глаголы', 'История о вчерашнем дне', 'Рассказ о том, что вы делали вчера', '{"questions": ["Как образуется Past Simple?", "Назовите 5 правильных глаголов"]}', true, true),
('Future with "will"', 'Планы на будущее', 'Обсуждение ваших целей', '{"questions": ["Когда используется will?", "Создайте 3 предложения"]}', false, false),

-- Курс 2: Разговорный английский
('Модальные глаголы: can/could', 'Диалоги о возможностях', 'Что вы умеете делать', '{"questions": ["В чем разница между can и could?"]}', true, false),
('Фразовые глаголы', 'Текст с фразовыми глаголами', 'Использование в речи', '{"questions": ["Объясните get up, give up"]}', true, false),
('Present Perfect', 'Опыт и достижения', 'Рассказ о вашем опыте', '{"questions": ["Когда используется Present Perfect?"]}', false, false),

-- Курс 3: Бизнес английский
('Деловая лексика', 'Бизнес-письмо', 'Презентация проекта', '{"questions": ["Назовите 10 бизнес-терминов"]}', true, false),
('Переговоры на английском', 'Сценарий переговоров', 'Ролевая игра: переговоры', '{"questions": ["Какие фразы использовать?"]}', true, false),
('Подготовка резюме', 'Примеры резюме', 'Обсуждение вашего CV', '{"questions": ["Как написать сильное резюме?"]}', false, false),

-- Курс 4: IELTS
('IELTS Writing Task 1', 'Пример описания графика', 'Анализ данных', '{"questions": ["Структура Task 1"]}', true, false),
('IELTS Speaking Part 2', 'Карточка с темой', '2-минутный монолог', '{"questions": ["Структура ответа"]}', true, false),
('Лексика для IELTS', 'Академические тексты', 'Использование в контексте', '{"questions": ["Сложные слова для IELTS"]}', false, false),

-- Курс 5: IT английский
('IT терминология', 'Техническая документация', 'Обсуждение проекта', '{"questions": ["Объясните agile, sprint"]}', true, false),
('Работа в команде', 'Кейс разработки', 'Совещание по проекту', '{"questions": ["Фразы для команды"]}', true, false),
('Техническое интервью', 'Вопросы на интервью', 'Подготовка к интервью', '{"questions": ["Как отвечать на технические вопросы?"]}', false, false),

-- Курс 6: Английский для путешествий
('В аэропорту', 'Диалоги в аэропорту', 'Ролевая игра: регистрация', '{"questions": ["Фразы для аэропорта"]}', true, false),
('В отеле', 'Бронирование отеля', 'Обсуждение проживания', '{"questions": ["Как заказать номер?"]}', true, false),
('В ресторане', 'Меню и заказ еды', 'Заказ в ресторане', '{"questions": ["Фразы для ресторана"]}', false, false);

-- 7. Связываем пользователей с курсами (ТОЛЬКО ОДИН КУРС НА УЧЕНИКА!)
INSERT INTO user_course (user_id, course_id, knowledge_gaps, graph_json) VALUES
-- Иван Петров (ученик) - только курс 1
(1, 1, 'Пробелы в Past Simple и артиклях', '{"nodes": ["Present Simple", "Past Simple"], "edges": [{"from": "Present Simple", "to": "Past Simple"}]}'),

-- Илья Маточкин (ученик) - только курс 3
(2, 3, 'Требуется практика делового общения', '{"nodes": ["Business Vocabulary", "Negotiations"], "edges": [{"from": "Business Vocabulary", "to": "Negotiations"}]}'),

-- Максим Язенин (репетитор) - ведет ВСЕ курсы (6 записей)
(3, 1, 'Преподаватель курса', '{"role": "tutor"}'),
(3, 2, 'Преподаватель курса', '{"role": "tutor"}'),
(3, 3, 'Преподаватель курса', '{"role": "tutor"}'),
(3, 4, 'Преподаватель курса', '{"role": "tutor"}'),
(3, 5, 'Преподаватель курса', '{"role": "tutor"}'),
(3, 6, 'Преподаватель курса', '{"role": "tutor"}');

-- 8. Обновляем существующих пользователей
UPDATE "user" SET 
    last_name = 'Петров',
    first_name = 'Иван',
    middle_name = 'Сергеевич',
    birth_date = '2000-01-01',
    phone = '+79990001122',
    telegram = 'ivan_petrov_tg',
    vk = 'ivan_petrov_vk',
    interests = 'Люблю путешествия, изучение языков, чтение книг',
    role = 'Ученик',
    email = 'ivan.petrov@example.com',
    avatar_path = '/avatars/ivan.jpg'
WHERE user_id = 1;

UPDATE "user" SET 
    last_name = 'Маточкин',
    first_name = 'Илья',
    middle_name = 'Александрович',
    birth_date = '2004-10-02',
    phone = '+79876461635',
    telegram = 'matokhin_ilya',
    vk = 'matokhin_vk',
    interests = 'Программирование, видеоигры, спорт',
    role = 'Ученик',
    email = 'matokhin.ilya@yandex.ru',
    avatar_path = '/avatars/ilya.jpg'
WHERE user_id = 2;

UPDATE "user" SET 
    last_name = 'Язенин',
    first_name = 'Максим',
    middle_name = 'Владимирович',
    birth_date = '1999-12-31',
    phone = '+78005553535',
    telegram = 'yazenin_tutor',
    vk = 'maxim_yazenin',
    interests = 'Преподавание английского, лингвистика, педагогика',
    role = 'Репетитор',
    email = 'yazenin@gmail.com',
    avatar_path = '/avatars/maksim.jpg'
WHERE user_id = 3;

-- 9. Добавляем новых пользователей (с одним курсом каждый)
INSERT INTO "user" (last_name, first_name, middle_name, birth_date, phone, telegram, vk, interests, role, email, password, avatar_path) VALUES
('Смирнова', 'Анна', 'Дмитриевна', '2001-05-15', '+79161234567', 'anna_sm', 'anna_smirnova', 'Музыка, искусство, фотография', 'Ученик', 'anna.smirnova@mail.ru', '$2b$12$testhash1', '/avatars/anna.jpg'),
('Козлов', 'Дмитрий', 'Игоревич', '1998-07-22', '+79269876543', 'dmitry_k', 'dmitry_kozlov', 'Спорт, политика, экономика', 'Ученик', 'dmitry.kozlov@gmail.com', '$2b$12$testhash2', '/avatars/dmitry.jpg'),
('Иванова', 'Елена', 'Сергеевна', '1995-03-10', '+79031234567', 'elena_i', 'elena_ivanova', 'Литература, театр, кулинария', 'Репетитор', 'elena.ivanova@yandex.ru', '$2b$12$testhash3', '/avatars/elena.jpg');

-- 10. Связываем новых пользователей с курсами
INSERT INTO user_course (user_id, course_id, knowledge_gaps, graph_json) VALUES
-- Анна Смирнова (новый ученик) - курс 4
(4, 4, 'Сложности с академическим письмом', '{"nodes": ["Writing", "Speaking"], "edges": [{"from": "Writing", "to": "Speaking"}]}'),

-- Дмитрий Козлов (новый ученик) - курс 5  
(5, 5, 'Нужно расширить IT-лексику', '{"nodes": ["IT Terms", "Teamwork"], "edges": [{"from": "IT Terms", "to": "Teamwork"}]}'),

-- Елена Иванова (новый репетитор) - ведет 3 курса
(6, 2, 'Преподаватель курса', '{"role": "tutor"}'),
(6, 4, 'Преподаватель курса', '{"role": "tutor"}'),
(6, 6, 'Преподаватель курса', '{"role": "tutor"}');

-- 11. Проверка данных
SELECT 'Таблица: user' as info, COUNT(*) as count FROM "user"
UNION ALL SELECT 'course', COUNT(*) FROM course
UNION ALL SELECT 'user_course', COUNT(*) FROM user_course
UNION ALL SELECT 'lesson', COUNT(*) FROM lesson
UNION ALL SELECT 'topic', COUNT(*) FROM topic
UNION ALL SELECT 'material', COUNT(*) FROM material
UNION ALL SELECT 'course_topic', COUNT(*) FROM course_topic
UNION ALL SELECT 'course_material', COUNT(*) FROM course_material;

-- 12. Проверка связей ученик-курс
SELECT 
    u.user_id,
    CONCAT(u.last_name, ' ', u.first_name) as ученик,
    u.role,
    c.title as курс,
    uc.knowledge_gaps as пробелы_в_знаниях
FROM "user" u
JOIN user_course uc ON u.user_id = uc.user_id
JOIN course c ON uc.course_id = c.course_id
WHERE u.role = 'Ученик'
ORDER BY u.user_id;

-- 13. Проверка репетиторов и их курсов
SELECT 
    u.user_id,
    CONCAT(u.last_name, ' ', u.first_name) as репетитор,
    COUNT(DISTINCT c.course_id) as количество_курсов,
    STRING_AGG(c.title, ', ' ORDER BY c.course_id) as список_курсов
FROM "user" u
JOIN user_course uc ON u.user_id = uc.user_id
JOIN course c ON uc.course_id = c.course_id
WHERE u.role = 'Репетитор'
GROUP BY u.user_id, u.last_name, u.first_name;