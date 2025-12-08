import psycopg2
import json
import bcrypt
from datetime import date, datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_users(cursor):
    """Создает пользователей с правильными паролями и русскими ролями"""
    print("\n1. Создание пользователей...")
    
    password = "12345678"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    users = [
        (1, 'Matokhin', 'Ilya', 'Georgievich', date(2004, 10, 2), '+79876461635', 'ilya_tg', 'ilya_vk', 'programming, football', 'Ученик', 'matokhin.ilya@yandex.ru', password_hash),
        (2, 'Molchanova', 'Liana', 'Evgenievna', date(2001, 1, 1), '+79998887755', 'lianaaaaa', 'lianavk', '', 'Ученик', 'liana@bk.ru', password_hash),
        (3, 'Zenin', 'Maxim', 'Aleksandrovich', date(2002, 2, 2), '+79995553535', 'tgzenina', 'vk??novk', '', 'Репетитор', 'yazenin@gmail.com', password_hash),
        (4, 'Bokov', 'Svyatoslav', 'Dmitrievich', date(1955, 4, 4), '+79875553432', 'tgb', 'vkb', '', 'Ученик', 'bokov@yandex.ru', password_hash),
        (5, 'Z', 'Z', 'Z', date(2011, 11, 11), '+79995553333', 'z', 'z', '', 'Ученик', 'z@z.ru', password_hash),
        (6, 'Ivanov', 'Ivan', 'Ivanovich', date(2000, 5, 15), '+79991234567', 'ivan_tg', 'ivan_vk', 'english, music, travel', 'Ученик', 'ivanov@example.com', password_hash),
        (7, 'Novikov', 'Alexey', 'Petrovich', date(1999, 3, 15), '+79994445566', 'alex_novikov', 'alex_vk', 'business, negotiations, presentations', 'Ученик', 'novikov@example.com', password_hash)  # Новый пользователь
    ]
    
    for user_data in users:
        cursor.execute("""
            INSERT INTO "user" (user_id, last_name, first_name, middle_name, birth_date, phone, 
                               telegram, vk, interests, role, email, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                last_name = EXCLUDED.last_name,
                first_name = EXCLUDED.first_name,
                middle_name = EXCLUDED.middle_name,
                birth_date = EXCLUDED.birth_date,
                phone = EXCLUDED.phone,
                telegram = EXCLUDED.telegram,
                vk = EXCLUDED.vk,
                interests = EXCLUDED.interests,
                role = EXCLUDED.role,
                email = EXCLUDED.email,
                password = EXCLUDED.password
        """, user_data)
        print(f"  ✓ Пользователь ID={user_data[0]}: {user_data[10]} ({user_data[9]})")
    
    print(f"  Все пароли установлены: {password}")

def create_database():
    """Удаляет и создает БД заново с правильной структурой"""
    print("=" * 60)
    print("ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ С НОВОЙ СТРУКТУРОЙ")
    print("=" * 60)
    
    # Подключаемся к postgres для удаления/создания БД
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        print("Удаление старой БД english_courses...")
        cursor.execute("DROP DATABASE IF EXISTS english_courses")
        print("  ✓ БД удалена")
        
        print("Создание новой БД english_courses...")
        cursor.execute("CREATE DATABASE english_courses")
        print("  ✓ БД создана")
        
    except Exception as e:
        print(f"Ошибка при пересоздании БД: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
    
    return True

def create_tables(cursor):
    """Создает все таблицы с правильной структурой"""
    print("\nСоздание таблиц...")
    
    # Создаем тип для ролей
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE UserRole AS ENUM ('Ученик', 'Репетитор');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("  ✓ Тип UserRole создан")
    
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            user_id SERIAL PRIMARY KEY,
            last_name VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50),
            birth_date DATE,
            phone VARCHAR(20),
            telegram VARCHAR(100),
            vk VARCHAR(100),
            interests TEXT,
            role UserRole NOT NULL,
            email VARCHAR(250) UNIQUE NOT NULL,
            password VARCHAR(500) NOT NULL,
            avatar_path VARCHAR(500)
        )
    """)
    print("  ✓ Таблица user создана")
    
    # Индексы для пользователей
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_last_name ON \"user\"(last_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_first_name ON \"user\"(first_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_phone ON \"user\"(phone)")
    
    # Таблица курсов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course (
            course_id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            created_at DATE NOT NULL,
            link_to_vector_db VARCHAR(1000) NOT NULL,
            input_test_json JSON
        )
    """)
    print("  ✓ Таблица course создана")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_title ON course(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_created_at ON course(created_at)")
    
    # Таблица материалов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material (
            material_id SERIAL PRIMARY KEY,
            file_path VARCHAR(1000) UNIQUE NOT NULL
        )
    """)
    print("  ✓ Таблица material создана")
    
    # Таблица тем
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic (
            topic_id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            description_text TEXT
        )
    """)
    print("  ✓ Таблица topic создана")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic_title ON topic(title)")
    
    # Таблица уроков - ВАЖНО: с колонкой topic_id!
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson (
            lesson_id SERIAL PRIMARY KEY,
            theory_text TEXT,
            reading_text TEXT,
            speaking_text TEXT,
            lesson_test_json JSON,
            lesson_test_results_json JSON,
            lesson_notes TEXT,
            results_json JSON,
            is_access BOOLEAN NOT NULL DEFAULT FALSE,
            is_ended BOOLEAN NOT NULL DEFAULT FALSE,
            topic_id INTEGER REFERENCES topic(topic_id) ON DELETE SET NULL
        )
    """)
    print("  ✓ Таблица lesson создана (с topic_id!)")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_topic_id ON lesson(topic_id)")
    
    # Таблица связи пользователь-курс
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_course (
            user_course_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
            knowledge_gaps TEXT,
            graph_json JSON,
            output_test_json JSON,
            UNIQUE(user_id, course_id)
        )
    """)
    print("  ✓ Таблица user_course создана")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_course_user_id ON user_course(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_course_course_id ON user_course(course_id)")
    
    # Таблица связи курс-материал
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_material (
            course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
            material_id INTEGER NOT NULL REFERENCES material(material_id) ON DELETE CASCADE,
            PRIMARY KEY (course_id, material_id)
        )
    """)
    print("  ✓ Таблица course_material создана")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_material_course_id ON course_material(course_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_material_material_id ON course_material(material_id)")
    
    # Таблица связи курс-тема
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_topic (
            course_id INTEGER NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
            topic_id INTEGER NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE,
            PRIMARY KEY (course_id, topic_id)
        )
    """)
    print("  ✓ Таблица course_topic создана")
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_topic_course_id ON course_topic(course_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_topic_topic_id ON course_topic(topic_id)")
    
    print("  ✓ Все таблицы успешно созданы!")

def fix_lesson_numbers_in_graphs(graph_json, course_id):
    """Пересчитывает номера уроков в графе так, чтобы всегда начинались с 1"""
    if not graph_json:
        return graph_json
    
    try:
        graph_data = json.loads(graph_json)
        nodes = graph_data.get('nodes', [])
        
        if not nodes:
            return graph_json
        
        # Найдем все lesson_id в графе
        lesson_ids = []
        for node in nodes:
            if 'data' in node and 'lesson_id' in node['data']:
                lesson_ids.append(node['data']['lesson_id'])
        
        if not lesson_ids:
            return graph_json
        
        # Создаем отображение старых lesson_id на новые (начиная с 1)
        lesson_ids = sorted(set(lesson_ids))
        lesson_mapping = {}
        
        # Создаем отображение: старый lesson_id -> новый порядковый номер (начиная с 1)
        for new_number, old_lesson_id in enumerate(lesson_ids, 1):
            lesson_mapping[old_lesson_id] = new_number
        
        # Применяем отображение ко всем узлам
        for node in nodes:
            if 'data' in node and 'lesson_id' in node['data']:
                old_id = node['data']['lesson_id']
                if old_id in lesson_mapping:
                    node['data']['lesson_id'] = lesson_mapping[old_id]
        
        return json.dumps(graph_data)
    
    except Exception as e:
        print(f"  ⚠ Ошибка при пересчете номеров уроков в графе: {e}")
        return graph_json

def fill_database():
    """Полностью заполняет базу данных тестовыми данными"""
    
    # Сначала создаем БД
    if not create_database():
        print("Не удалось создать БД. Выход.")
        return
    
    # Теперь подключаемся к новой БД
    conn = psycopg2.connect(
        host="localhost",
        database="english_courses",
        user="postgres",
        password="1234"
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ С ГРАФАМИ КУРСОВ")
        print("=" * 60)
        
        # Создаем таблицы
        create_tables(cursor)
        conn.commit()
        
        # 1. Создаем пользователей
        create_users(cursor)
        conn.commit()
        
        # 2. Очистка остальных таблиц (на всякий случай)
        print("\n2. Очистка таблиц перед заполнением...")
        
        tables_to_clear = [
            "course_material",
            "course_topic", 
            "user_course",
            "material",
            "topic",
            "lesson", 
            "course"
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print(f"  ✓ Таблица {table} очищена")
            except Exception as e:
                print(f"  ⚠ Ошибка при очистке {table}: {e}")
        
        # Сбрасываем sequence для автоинкремента
        sequences = [
            "course_course_id_seq",
            "user_course_user_course_id_seq",
            "material_material_id_seq",
            "topic_topic_id_seq", 
            "lesson_lesson_id_seq"
        ]
        
        for seq in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
                print(f"  ✓ Sequence {seq} сброшен")
            except:
                pass
        
        conn.commit()
        
        print("\n3. Создание курсов (6 курсов)...")
        
        # Определяем графы для каждого курса (будет использоваться при создании user_course)
        course_graphs = [
            # Курс 1: English for Beginners - обновленный граф
            {
                "nodes": [
                    {"id": "1", "label": "Present Simple Theory", "data": {"lesson_id": 1}, "position": {"x": 100, "y": 50}, "type": "custom"},
                    {"id": "2", "label": "Present Simple Practice", "data": {"lesson_id": 2}, "position": {"x": 100, "y": 150}, "type": "custom"},
                    {"id": "3", "label": "Past Simple: regular", "data": {"lesson_id": 3}, "position": {"x": 100, "y": 250}, "type": "custom"},
                    {"id": "4", "label": "Past Simple: irregular", "data": {"lesson_id": 4}, "position": {"x": 100, "y": 350}, "type": "custom"},
                    {"id": "5", "label": "Future with will", "data": {"lesson_id": 5}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "6", "label": "Future with going to", "data": {"lesson_id": 6}, "position": {"x": 300, "y": 250}, "type": "custom"},
                    {"id": "7", "label": "Modal Verbs can/could", "data": {"lesson_id": 7}, "position": {"x": 500, "y": 150}, "type": "custom"},
                    {"id": "8", "label": "Modal Verbs should/must", "data": {"lesson_id": 8}, "position": {"x": 500, "y": 250}, "type": "custom"},
                    {"id": "9", "label": "Articles a/an/the", "data": {"lesson_id": 9}, "position": {"x": 700, "y": 150}, "type": "custom"},
                    {"id": "10", "label": "Articles Practice", "data": {"lesson_id": 10}, "position": {"x": 700, "y": 250}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e2-3", "source": "2", "target": "3", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"},
                    {"id": "e2-5", "source": "2", "target": "5", "label": "Alternative"},
                    {"id": "e5-6", "source": "5", "target": "6", "label": "Next"},
                    {"id": "e4-7", "source": "4", "target": "7", "label": "Next"},
                    {"id": "e6-7", "source": "6", "target": "7", "label": "Next"},
                    {"id": "e7-8", "source": "7", "target": "8", "label": "Next"},
                    {"id": "e8-9", "source": "8", "target": "9", "label": "Next"},
                    {"id": "e9-10", "source": "9", "target": "10", "label": "Next"}
                ]
            },
            # Курс 2: Conversational English - обновленный граф
            {
                "nodes": [
                    {"id": "1", "label": "Greetings", "data": {"lesson_id": 11}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Daily Conversations", "data": {"lesson_id": 12}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Shopping Dialogues", "data": {"lesson_id": 13}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Restaurant Talk", "data": {"lesson_id": 14}, "position": {"x": 500, "y": 100}, "type": "custom"},
                    {"id": "5", "label": "Phrasal Verbs", "data": {"lesson_id": 15}, "position": {"x": 500, "y": 200}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"},
                    {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
                ]
            },
            # Курс 3: Business English (БАЗОВЫЙ ГРАФ) - обновленный
            {
                "nodes": [
                    {"id": "1", "label": "Business Email", "data": {"lesson_id": 16}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Meetings", "data": {"lesson_id": 17}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Presentations", "data": {"lesson_id": 18}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Negotiations", "data": {"lesson_id": 19}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            },
            # Курс 4: IELTS Preparation - обновленный
            {
                "nodes": [
                    {"id": "1", "label": "IELTS Listening", "data": {"lesson_id": 20}, "position": {"x": 100, "y": 50}, "type": "custom"},
                    {"id": "2", "label": "IELTS Reading", "data": {"lesson_id": 21}, "position": {"x": 100, "y": 150}, "type": "custom"},
                    {"id": "3", "label": "Writing Task 1", "data": {"lesson_id": 22}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "4", "label": "Writing Task 2", "data": {"lesson_id": 23}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "5", "label": "Speaking Part 2", "data": {"lesson_id": 24}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-5", "source": "3", "target": "5", "label": "Next"},
                    {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
                ]
            },
            # Курс 5: English for IT - обновленный
            {
                "nodes": [
                    {"id": "1", "label": "IT Vocabulary", "data": {"lesson_id": 25}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Documentation", "data": {"lesson_id": 26}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Team Communication", "data": {"lesson_id": 27}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Technical Interview", "data": {"lesson_id": 28}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            },
            # Курс 6: English for Travel - обновленный
            {
                "nodes": [
                    {"id": "1", "label": "Airport", "data": {"lesson_id": 29}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Hotel", "data": {"lesson_id": 30}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Restaurant", "data": {"lesson_id": 31}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Sightseeing", "data": {"lesson_id": 32}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            }
        ]
        
        courses = [
            ('English for Beginners (A1)', date(2024, 1, 15), '/vector_db/courses/beginner_a1', 
             json.dumps({"test_type": "placement", "questions": 20})),
            ('Conversational English (A2-B1)', date(2024, 2, 10), '/vector_db/courses/conversational_a2',
             json.dumps({"test_type": "placement", "questions": 25})),
            ('Business English (B1-B2)', date(2024, 2, 28), '/vector_db/courses/business_b1',
             json.dumps({"test_type": "business_skills", "questions": 30})),
            ('IELTS Preparation (B2-C1)', date(2024, 3, 15), '/vector_db/courses/ielts_b2',
             json.dumps({"test_type": "ielts_practice", "questions": 40})),
            ('English for IT Specialists (B1)', date(2024, 3, 20), '/vector_db/courses/it_english_b1',
             json.dumps({"test_type": "technical", "questions": 35})),
            ('English for Travel (A2)', date(2024, 4, 1), '/vector_db/courses/travel_a2',
             json.dumps({"test_type": "travel_scenarios", "questions": 25}))
        ]
        
        for i, course in enumerate(courses, 1):
            cursor.execute(
                """INSERT INTO course (title, created_at, link_to_vector_db, input_test_json) 
                   VALUES (%s, %s, %s, %s)""",
                course
            )
            print(f"  ✓ Курс {i}: {course[0]}")
        
        conn.commit()
        
        # Получаем ID созданных курсов
        cursor.execute("SELECT course_id, title FROM course ORDER BY course_id")
        courses_data = cursor.fetchall()
        course_map = {course_id: title for course_id, title in courses_data}
        
        print("\n4. Связывание пользователей с курсами (с графами)...")
        
        # Создаем УНИКАЛЬНЫЙ граф для нового пользователя (ID=7) на курсе 3
        # Граф с разными статусами: 0 - пройден, 1 - не пройден, 2 - доступен, 3 - недоступен
        unique_graph_for_user_7 = {
            "nodes": [
                {"id": "1", "label": "Business Email", "data": {"lesson_id": 16}, "position": {"x": 100, "y": 100}, "group": 0},  # Пройден успешно
                {"id": "2", "label": "Meetings", "data": {"lesson_id": 17}, "position": {"x": 300, "y": 50}, "group": 0},  # Пройден успешно
                {"id": "3", "label": "Presentations", "data": {"lesson_id": 18}, "position": {"x": 300, "y": 150}, "group": 1},  # Не пройден (завалил)
                {"id": "4", "label": "Presentations Review", "data": {"lesson_id": 18}, "position": {"x": 300, "y": 250}, "group": 0},  # Та же тема, но пройдена после повторения
                {"id": "5", "label": "Negotiations Basics", "data": {"lesson_id": 19}, "position": {"x": 500, "y": 100}, "group": 2},  # Доступен
                {"id": "6", "label": "Advanced Negotiations", "data": {"lesson_id": 33}, "position": {"x": 500, "y": 200}, "group": 3},  # Недоступен
                {"id": "7", "label": "Business Writing", "data": {"lesson_id": 34}, "position": {"x": 500, "y": 300}, "group": 2},  # Доступен
                {"id": "8", "label": "Final Project", "data": {"lesson_id": 35}, "position": {"x": 700, "y": 200}, "group": 3}  # Недоступен
            ],
            "edges": [
                {"id": "e1-2", "source": "1", "target": "2", "label": "Basic → Advanced"},
                {"id": "e2-3", "source": "2", "target": "3", "label": "Next Topic"},
                {"id": "e3-4", "source": "3", "target": "4", "label": "Retry"},
                {"id": "e4-5", "source": "4", "target": "5", "label": "Continue"},
                {"id": "e5-6", "source": "5", "target": "6", "label": "Advanced Path"},
                {"id": "e4-7", "source": "4", "target": "7", "label": "Alternative Path"},
                {"id": "e6-8", "source": "6", "target": "8", "label": "Final Step"},
                {"id": "e7-8", "source": "7", "target": "8", "label": "Final Step"}
            ]
        }
        
        user_courses = [
            # User 1 -> Course 1 с графом курса 1
            (1, 1, 'Gaps in Past Simple and articles', 
            json.dumps(course_graphs[0]),  # Обновленный граф для курса 1
            json.dumps({
                "custom_nodes": [
                    {"id": "1", "label": "Present Simple", "color": "#4CAF50", "completed": True},
                    {"id": "2", "label": "Present Simple Practice", "color": "#4CAF50", "completed": True},
                    {"id": "3", "label": "Past Simple: regular", "color": "#FF9800", "completed": False},
                    {"id": "4", "label": "Past Simple: irregular", "color": "#FF9800", "completed": False}
                ],
                "custom_edges": [
                    {"from": "2", "to": "3", "label": "Focus on this"},
                    {"from": "3", "to": "4", "label": "Next"}
                ]
            })),
            # User 6 -> Course 1 с графом курса 1
            (6, 1, 'Difficulty with Present Continuous and vocabulary',
             json.dumps(course_graphs[0]),  # Граф для курса 1
             json.dumps({
                 "custom_nodes": [
                     {"id": "1", "label": "Present Simple", "color": "#4CAF50", "completed": True},
                     {"id": "2", "label": "Present Continuous", "color": "#FF9800", "completed": False},
                     {"id": "3", "label": "Basic Vocabulary", "color": "#2196F3", "completed": False}
                 ],
                 "custom_edges": [
                     {"from": "1", "to": "2", "label": "Need practice"},
                     {"from": "2", "to": "3", "label": "Next"}
                 ]
             })),
            # User 2 -> Course 3 с графом курса 3 (Molchanova Liana)
            (2, 3, 'Need business communication practice',
             json.dumps(course_graphs[2]),  # Граф для курса 3
             json.dumps({
                 "custom_nodes": [
                     {"id": "1", "label": "Business Email", "color": "#4CAF50", "completed": True},
                     {"id": "2", "label": "Meetings", "color": "#FF9800", "completed": False}
                 ],
                 "custom_edges": [
                     {"from": "1", "to": "2", "label": "Focus area"}
                 ]
             })),
            # User 7 -> Course 3 с УНИКАЛЬНЫМ графом (Novikov Alexey)
            (7, 3, 'Struggling with presentations, good at negotiations',
             json.dumps(unique_graph_for_user_7),  # Уникальный граф
             json.dumps({
                 "custom_nodes": [
                     {"id": "1", "label": "Business Email", "color": "#4CAF50", "completed": True},
                     {"id": "3", "label": "Presentations", "color": "#F44336", "completed": False},
                     {"id": "5", "label": "Negotiations", "color": "#FFC107", "completed": False}
                 ],
                 "custom_edges": [
                     {"from": "1", "to": "3", "label": "Need to retry"},
                     {"from": "3", "to": "5", "label": "Next after review"}
                 ]
             })),
            # User 4 -> Course 4 с графом курса 4
            (4, 4, 'Difficulties with academic writing',
             json.dumps(course_graphs[3]),  # Граф для курса 4
             json.dumps({
                 "custom_nodes": [
                     {"id": "1", "label": "Writing Task 1", "color": "#FF5722", "completed": False},
                     {"id": "2", "label": "Writing Task 2", "color": "#FF5722", "completed": False}
                 ],
                 "custom_edges": [
                     {"from": "1", "to": "2", "label": "Priority"}
                 ]
             })),
            
            # Репетитор ведет все курсы (без графов или с пустыми графами)
            (3, 1, 'Course instructor', '{"role": "tutor"}', '{}'),
            (3, 2, 'Course instructor', '{"role": "tutor"}', '{}'),
            (3, 3, 'Course instructor', '{"role": "tutor"}', '{}'),
            (3, 4, 'Course instructor', '{"role": "tutor"}', '{}'),
            (3, 5, 'Course instructor', '{"role": "tutor"}', '{}'),
            (3, 6, 'Course instructor', '{"role": "tutor"}', '{}')
        ]
        
        # Перед вставкой пересчитываем номера уроков в каждом графе
        print("\n  Пересчет номеров уроков в графах (чтобы всегда начинались с 1)...")
        processed_user_courses = []
        
        for user_id, course_id, knowledge_gaps, graph_json, output_test_json in user_courses:
            # Пересчитываем номера уроков в графе
            fixed_graph_json = fix_lesson_numbers_in_graphs(graph_json, course_id)
            processed_user_courses.append((user_id, course_id, knowledge_gaps, fixed_graph_json, output_test_json))
        
        # Вставляем данные с исправленными графами
        for user_id, course_id, knowledge_gaps, fixed_graph_json, output_test_json in processed_user_courses:
            cursor.execute(
                """INSERT INTO user_course (user_id, course_id, knowledge_gaps, graph_json, output_test_json) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, course_id, knowledge_gaps, fixed_graph_json, output_test_json)
            )
            
            cursor.execute("SELECT email, role FROM \"user\" WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
            user_email, user_role = user_info if user_info else (f"user_{user_id}", "Unknown")
            
            course_name = course_map.get(course_id, f"Course {course_id}")
            
            # Парсим graph_json для подсчета вершин и связей
            try:
                graph_data = json.loads(fixed_graph_json)
                nodes_count = len(graph_data.get('nodes', [])) if isinstance(graph_data, dict) else 0
                edges_count = len(graph_data.get('edges', [])) if isinstance(graph_data, dict) else 0
                
                if user_role == 'Репетитор':
                    print(f"  ✓ Репетитор {user_email} -> {course_name}")
                else:
                    # Проверяем номера уроков в графе
                    lesson_numbers = []
                    if nodes_count > 0 and isinstance(graph_data, dict):
                        for node in graph_data.get('nodes', []):
                            if 'data' in node and 'lesson_id' in node['data']:
                                lesson_numbers.append(node['data']['lesson_id'])
                        
                        lesson_numbers.sort()
                        if lesson_numbers:
                            print(f"  ✓ Ученик {user_email} -> {course_name} ({nodes_count} вершин, {edges_count} связей, уроки: {lesson_numbers[0]}-{lesson_numbers[-1]})")
                        else:
                            print(f"  ✓ Ученик {user_email} -> {course_name} ({nodes_count} вершин, {edges_count} связей)")
                    else:
                        print(f"  ✓ Ученик {user_email} -> {course_name} ({nodes_count} вершин, {edges_count} связей)")
            except Exception as e:
                print(f"  ✓ Ученик {user_email} -> {course_name} (ошибка парсинга графа: {e})")
        
        print(f"  ✓ Ученик z@z.ru (ID=5) не имеет курсов")
        
        conn.commit()
        
        print("\n5. Создание материалов для курсов...")
        
        materials = [
            '/materials/beginner/grammar_basics.pdf',
            '/materials/beginner/vocabulary_a1.zip',
            '/materials/conversational/dialogues_mp3.zip',
            '/materials/business/presentations.pptx',
            '/materials/business/emails_templates.docx',
            '/materials/ielts/writing_samples.pdf',
            '/materials/ielts/listening_tests.zip',
            '/materials/it/technical_terms.pdf',
            '/materials/travel/phrasebook.pdf',
            '/materials/travel/airport_dialogues.mp3',
            '/materials/common/irregular_verbs.pdf',
            '/materials/common/prepositions_exercises.pdf'
        ]
        
        for material in materials:
            cursor.execute("INSERT INTO material (file_path) VALUES (%s)", (material,))
        
        print(f"  ✓ Добавлено {len(materials)} материалов")
        
        # Связь курсов с материалами
        course_materials = [
            (1, 1), (1, 2), (1, 11), (1, 12),
            (2, 3), (2, 11), (2, 12),
            (3, 4), (3, 5), (3, 6),
            (4, 6), (4, 7),
            (5, 8), (5, 9),
            (6, 9), (6, 10)
        ]
        
        for course_id, material_id in course_materials:
            cursor.execute("INSERT INTO course_material (course_id, material_id) VALUES (%s, %s)", 
                          (course_id, material_id))
        
        print(f"  ✓ Создано {len(course_materials)} связей курс-материал")
        
        print("\n6. Создание тем и связей...")
        
        topics = [
            ('Present Simple', 'Basic present simple tense: rules and usage'),
            ('Past Simple', 'Past simple tense: regular and irregular verbs'),
            ('Future Tenses', 'Future tenses: will, going to, present continuous'),
            ('Modal Verbs', 'Modal verbs: can, could, should, must, have to'),
            ('Articles', 'Articles a/an/the: usage rules'),
            ('Business Vocabulary', 'Business vocabulary: negotiations, presentations, meetings'),
            ('IELTS Writing Task 1', 'Academic writing: describing graphs and charts'),
            ('IELTS Speaking Part 2', '2-minute monologue on given topic'),
            ('IT Terminology', 'Technical terminology: development, testing, deployment'),
            ('Travel Phrases', 'Travel phrases: airport, hotel, restaurant'),
            ('Phrasal Verbs', 'Phrasal verbs with usage examples'),
            ('Conditionals', 'Conditional sentences: zero, first, second, third conditional')
        ]
        
        for topic in topics:
            cursor.execute("INSERT INTO topic (title, description_text) VALUES (%s, %s)", topic)
        
        print(f"  ✓ Добавлено {len(topics)} тем")
        
        # Связь курсов с темами
        course_topics = [
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
            (2, 1), (2, 2), (2, 3), (2, 11),
            (3, 4), (3, 6),
            (4, 7), (4, 8), (4, 12),
            (5, 9), (5, 4),
            (6, 10), (6, 1), (6, 2)
        ]
        
        for course_id, topic_id in course_topics:
            cursor.execute("INSERT INTO course_topic (course_id, topic_id) VALUES (%s, %s)", 
                          (course_id, topic_id))
        
        print(f"  ✓ Создано {len(course_topics)} связей курс-тема")
        
        print("\n7. Создание уроков для графа (включая дополнительные для нового графа)...")

        # Сначала узнаем ID тем, которые мы создали
        print("  Получение ID созданных тем...")
        cursor.execute("SELECT topic_id, title FROM topic ORDER BY topic_id")
        topics_data = cursor.fetchall()
        topic_map = {title: topic_id for topic_id, title in topics_data}
        print(f"  ✓ Найдено {len(topic_map)} тем")

        # Теперь создаем уроки с привязкой к темам
        lessons_with_topics = [
            # Курс 1: English for Beginners
            (1, 'Present Simple: theory and examples', 'Text about daily habits', 'Discuss your daily routine', 
            json.dumps({"questions": ["What is Present Simple?", "Give 3 examples"]}), True, False),
            (1, 'Present Simple Practice', 'More exercises', 'Practice simple sentences', 
            json.dumps({"questions": ["Make 5 sentences"]}), True, False),
            
            (2, 'Past Simple: regular verbs', 'Story about yesterday', 'Talk about what you did yesterday', 
            json.dumps({"questions": ["How is Past Simple formed?", "Name 5 regular verbs"]}), True, True),
            (2, 'Past Simple: irregular verbs', 'List of irregular verbs', 'Practice irregular forms', 
            json.dumps({"questions": ["Name 10 irregular verbs"]}), True, False),
            
            (3, 'Future with "will"', 'Future plans', 'Discuss your goals', 
            json.dumps({"questions": ["When is will used?", "Create 3 sentences"]}), False, False),
            (3, 'Future with "going to"', 'Plans and predictions', 'Talk about plans', 
            json.dumps({"questions": ["Difference between will and going to"]}), True, False),
            
            (4, 'Modal Verbs: can/could', 'Ability and permission', 'Practice can/could', 
            json.dumps({"questions": ["When to use can?", "When to use could?"]}), True, False),
            (4, 'Modal Verbs: should/must', 'Advice and obligation', 'Practice should/must', 
            json.dumps({"questions": ["Difference between should and must"]}), True, False),
            
            (5, 'Articles a/an/the', 'Rules and usage', 'Practice with nouns', 
            json.dumps({"questions": ["When to use a/an?", "When to use the?"]}), True, False),
            (5, 'Articles Practice', 'Advanced rules', 'Practice exceptions', 
            json.dumps({"questions": ["Articles with proper nouns"]}), True, False),
            
            # Курс 2: Conversational English
            (1, 'Greetings and Introductions', 'Basic greetings', 'Introduce yourself', 
            json.dumps({"questions": ["How to greet someone?"]}), True, False),
            (2, 'Daily Conversations', 'Everyday dialogues', 'Practice small talk', 
            json.dumps({"questions": ["Common daily questions"]}), True, False),
            (3, 'Shopping Dialogues', 'Store conversations', 'Role play shopping', 
            json.dumps({"questions": ["How to ask for price?"]}), True, False),
            (11, 'Restaurant Conversations', 'Menu and ordering', 'Order food in restaurant', 
            json.dumps({"questions": ["Restaurant phrases"]}), False, False),
            
            # Курс 3: Business English
            (6, 'Business Email Writing', 'Email structure', 'Write business email', 
            json.dumps({"questions": ["Email format"]}), True, False),
            (6, 'Meeting Vocabulary', 'Meeting phrases', 'Participate in meeting', 
            json.dumps({"questions": ["Meeting terms"]}), True, False),
            (6, 'Presentation Skills', 'Presenting ideas', 'Give short presentation', 
            json.dumps({"questions": ["Presentation structure"]}), True, False),
            (6, 'Negotiation Techniques', 'Negotiation phrases', 'Role play negotiation', 
            json.dumps({"questions": ["Negotiation strategies"]}), False, False),
            
            # Курс 4: IELTS Preparation
            (7, 'IELTS Listening Part 1', 'Basic listening', 'Answer questions', 
            json.dumps({"questions": ["Listening tips"]}), True, False),
            (7, 'IELTS Reading Section', 'Reading strategies', 'Practice reading', 
            json.dumps({"questions": ["Reading techniques"]}), True, False),
            (8, 'IELTS Writing Task 1', 'Graph description', 'Describe chart', 
            json.dumps({"questions": ["Task 1 structure"]}), True, False),
            (8, 'IELTS Writing Task 2', 'Essay writing', 'Write essay', 
            json.dumps({"questions": ["Essay structure"]}), True, False),
            (8, 'IELTS Speaking Part 2', '2-minute talk', 'Give monologue', 
            json.dumps({"questions": ["Speaking strategies"]}), False, False),
            
            # Курс 5: English for IT
            (9, 'IT Vocabulary Basics', 'Technical terms', 'Discuss technology', 
            json.dumps({"questions": ["IT terms"]}), True, False),
            (9, 'Reading Documentation', 'Technical docs', 'Explain documentation', 
            json.dumps({"questions": ["Doc understanding"]}), True, False),
            (9, 'Team Communication', 'Team discussions', 'Team meeting practice', 
            json.dumps({"questions": ["Teamwork phrases"]}), True, False),
            (9, 'Technical Interview Prep', 'Interview questions', 'Mock interview', 
            json.dumps({"questions": ["Interview tips"]}), False, False),
            
            # Курс 6: English for Travel
            (10, 'At the Airport', 'Check-in procedures', 'Airport role play', 
            json.dumps({"questions": ["Airport phrases"]}), True, False),
            (10, 'Hotel Check-in', 'Hotel vocabulary', 'Book hotel room', 
            json.dumps({"questions": ["Hotel terms"]}), True, False),
            (10, 'Restaurant Ordering', 'Food vocabulary', 'Order in restaurant', 
            json.dumps({"questions": ["Menu items"]}), True, False),
            (10, 'Sightseeing Vocabulary', 'Tourist places', 'Ask for directions', 
            json.dumps({"questions": ["Tourism phrases"]}), False, False),
            
            # Дополнительные уроки
            (11, 'Phrasal Verbs: get up, look after', 'Common phrasal verbs', 'Practice phrasal verbs', 
            json.dumps({"questions": ["Use in sentences"]}), True, False),
            (12, 'First Conditional', 'If + present, will + infinitive', 'Practice first conditional', 
            json.dumps({"questions": ["Make 3 sentences"]}), True, False),
            
            # Дополнительные уроки для Business English (пользователь 7)
            (6, 'Advanced Negotiation Strategies', 'Complex negotiation scenarios', 'Practice advanced negotiations', 
            json.dumps({"questions": ["Advanced negotiation tactics?", "Handling difficult clients"]}), False, False),
            (6, 'Business Writing Excellence', 'Professional writing techniques', 'Write business report', 
            json.dumps({"questions": ["Report structure?", "Formal language"]}), False, False),
            (6, 'Final Business Project', 'Comprehensive business case study', 'Present business solution', 
            json.dumps({"questions": ["Case analysis?", "Solution presentation"]}), False, False)
        ]

        print(f"  Создание {len(lessons_with_topics)} уроков с привязкой к темам...")

        for topic_id, theory_text, reading_text, speaking_text, lesson_test_json, is_access, is_ended in lessons_with_topics:
            cursor.execute(
                """INSERT INTO lesson (topic_id, theory_text, reading_text, speaking_text, 
                                    lesson_test_json, is_access, is_ended) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (topic_id, theory_text, reading_text, speaking_text, lesson_test_json, is_access, is_ended)
            )

        print(f"  ✓ Добавлено {len(lessons_with_topics)} уроков с привязкой к темам")
        
        conn.commit()
        
        # 8. ФИНАЛЬНАЯ ПРОВЕРКА
        print("\n" + "=" * 60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА ДАННЫХ С ИСПРАВЛЕННЫМИ НОМЕРАМИ УРОКОВ")
        print("=" * 60)
        
        # Проверка графов в user_course
        print("\nПроверка графов в таблице user_course (ученики на курсе 3 - Business English):")
        cursor.execute("""
            SELECT uc.user_course_id, u.email, u.user_id, c.title, 
                   CASE WHEN uc.graph_json IS NULL THEN 'Нет графа' 
                        WHEN LENGTH(uc.graph_json::text) < 50 THEN 'Короткий граф' 
                        ELSE 'Есть граф' END as graph_status
            FROM user_course uc
            JOIN "user" u ON uc.user_id = u.user_id
            JOIN course c ON uc.course_id = c.course_id
            WHERE u.role != 'Репетитор' AND c.course_id = 3
            ORDER BY uc.user_course_id
        """)
        
        user_courses_data = cursor.fetchall()
        for uc_id, email, user_id, title, graph_status in user_courses_data:
            print(f"  UserCourse {uc_id}: {email} (ID={user_id}) -> {title}: {graph_status}")
            
            # Детальная информация о графе
            cursor.execute("""
                SELECT graph_json FROM user_course 
                WHERE user_id = %s AND course_id = 3
            """, (user_id,))
            graph_result = cursor.fetchone()
            if graph_result and graph_result[0]:
                try:
                    graph_data = json.loads(graph_result[0])
                    nodes = graph_data.get('nodes', [])
                    edges = graph_data.get('edges', [])
                    
                    # Собираем информацию о номерах уроков
                    lesson_numbers = []
                    for node in nodes:
                        if 'data' in node and 'lesson_id' in node['data']:
                            lesson_numbers.append(node['data']['lesson_id'])
                    
                    lesson_numbers.sort()
                    
                    # Собираем информацию о статусах
                    groups = {}
                    for node in nodes:
                        group = node.get('group')
                        if group is not None:
                            groups[group] = groups.get(group, 0) + 1
                    
                    groups_str = ', '.join([f"группа {k}: {v} узлов" for k, v in sorted(groups.items())])
                    
                    if lesson_numbers:
                        print(f"    - {len(nodes)} вершин, {len(edges)} связей, номера уроков: {lesson_numbers[0]}-{lesson_numbers[-1]}")
                        print(f"    - Статусы: {groups_str if groups_str else 'не указаны'}")
                    else:
                        print(f"    - {len(nodes)} вершин, {len(edges)} связей. Статусы: {groups_str if groups_str else 'не указаны'}")
                    
                except Exception as e:
                    print(f"    - Ошибка парсинга графа: {e}")
        
        # Общая статистика
        print("\nОбщая статистика:")
        check_queries = [
            ("SELECT COUNT(*) FROM \"user\"", "Пользователи"),
            ("SELECT COUNT(*) FROM course", "Курсы"),
            ("SELECT COUNT(*) FROM user_course", "Связи пользователь-курс"),
            ("SELECT COUNT(*) FROM material", "Материалы"),
            ("SELECT COUNT(*) FROM topic", "Темы"),
            ("SELECT COUNT(*) FROM lesson", "Уроки")
        ]
        
        for query, name in check_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {name}: {count}")
        
        print("\nГЛАВНОЕ ИСПРАВЛЕНИЕ:")
        print("-" * 60)
        print("Теперь у каждого ученика в каждом курсе уроки всегда начинаются с 1!")
        print("Пример: Уроки Novikov Alexey на курсе Business English:")
        print("  - Было: уроки 16, 17, 18, 19, 33, 34, 35 (неправильно!)")
        print("  - Стало: уроки 1, 2, 3, 4, 5, 6, 7 (правильно!)")
        
        print("\nИнформация для тестирования:")
        print("-" * 60)
        print("1. ДВА ученика на одном курсе с РАЗНЫМИ графами:")
        print("   - Molchanova Liana (ID=2): liana@bk.ru - стандартный граф (уроки: 1-4)")
        print("   - Novikov Alexey (ID=7): novikov@example.com - УНИКАЛЬНЫЙ граф (уроки: 1-8)")
        print("\n2. Все пароли: 12345678")
        print("\n3. Репетитор: yazenin@gmail.com (ID=3) - видит все курсы")
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fill_database()