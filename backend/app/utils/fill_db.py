import psycopg2
import json
import bcrypt
from datetime import date, datetime

def create_users(cursor):
    """Создает пользователей с правильными паролями и русскими ролями"""
    print("\n1. Создание пользователей...")
    
    # Пароль для всех пользователей (хешированный)
    password = "12345678"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Список пользователей с русскими ролями (добавили нового пользователя)
    users = [
        # (user_id, last_name, first_name, middle_name, birth_date, phone, telegram, vk, interests, role, email)
        (1, 'Matokhin', 'Ilya', 'Georgievich', date(2004, 10, 2), '+79876461635', 'ilya_tg', 'ilya_vk', 'programming, football', 'Ученик', 'matokhin.ilya@yandex.ru', password_hash),
        (2, 'Molchanova', 'Liana', 'Evgenievna', date(2001, 1, 1), '+79998887755', 'lianaaaaa', 'lianavk', '', 'Ученик', 'liana@bk.ru', password_hash),
        (3, 'Zenin', 'Maxim', 'Aleksandrovich', date(2002, 2, 2), '+79995553535', 'tgzenina', 'vk??novk', '', 'Репетитор', 'yazenin@gmail.com', password_hash),
        (4, 'Bokov', 'Svyatoslav', 'Dmitrievich', date(1955, 4, 4), '+79875553432', 'tgb', 'vkb', '', 'Ученик', 'bokov@yandex.ru', password_hash),
        (5, 'Z', 'Z', 'Z', date(2011, 11, 11), '+79995553333', 'z', 'z', '', 'Ученик', 'z@z.ru', password_hash),
        # НОВЫЙ ПОЛЬЗОВАТЕЛЬ - будет на том же курсе, что и Matokhin
        (6, 'Ivanov', 'Ivan', 'Ivanovich', date(2000, 5, 15), '+79991234567', 'ivan_tg', 'ivan_vk', 'english, music, travel', 'Ученик', 'ivanov@example.com', password_hash)
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

def fill_database():
    """Полностью заполняет базу данных тестовыми данными"""
    
    conn = psycopg2.connect(
        host="localhost",
        database="english_courses",
        user="postgres",
        password="1234"  # Вставьте ваш пароль
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        # 1. Создаем пользователей
        create_users(cursor)
        conn.commit()
        
        # 2. Очистка остальных таблиц
        print("\n2. Очистка таблиц (кроме пользователей)...")
        
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
                "INSERT INTO course (title, created_at, link_to_vector_db, input_test_json) VALUES (%s, %s, %s, %s)",
                course
            )
            print(f"  ✓ Курс {i}: {course[0]}")
        
        conn.commit()
        
        # Получаем ID созданных курсов (они будут 1-6)
        cursor.execute("SELECT course_id, title FROM course ORDER BY course_id")
        courses_data = cursor.fetchall()
        course_map = {course_id: title for course_id, title in courses_data}
        
        print("\n4. Связывание пользователей с курсами...")
        
        # Распределение:
        # Ученик 1 (ID=1) -> Курс 1 (English for Beginners)
        # Ученик 6 (ID=6) -> ТОЖЕ Курс 1 (English for Beginners) - НОВЫЙ УЧЕНИК
        # Ученик 2 (ID=2) -> Курс 3 (Business English)  
        # Ученик 4 (ID=4) -> Курс 4 (IELTS Preparation)
        # Репетитор 3 (ID=3) -> ВСЕ курсы (1-6)
        # Ученик 5 (ID=5) -> НИКАКИХ КУРСОВ
        
        user_courses = [
            # Ученики
            (1, 1, 'Gaps in Past Simple and articles', 
             '{"nodes": ["Present Simple", "Past Simple"], "edges": [{"from": "Present Simple", "to": "Past Simple"}]}'),
            (6, 1, 'Difficulty with Present Continuous and vocabulary',  # НОВЫЙ УЧЕНИК на том же курсе
             '{"nodes": ["Present Continuous", "Basic Vocabulary"], "edges": [{"from": "Present Continuous", "to": "Basic Vocabulary"}]}'),
            (2, 3, 'Need business communication practice',
             '{"nodes": ["Business Vocabulary", "Negotiations"], "edges": [{"from": "Business Vocabulary", "to": "Negotiations"}]}'),
            (4, 4, 'Difficulties with academic writing',
             '{"nodes": ["Writing", "Speaking"], "edges": [{"from": "Writing", "to": "Speaking"}]}'),
            
            # Репетитор ведет все курсы
            (3, 1, 'Course instructor', '{"role": "tutor"}'),
            (3, 2, 'Course instructor', '{"role": "tutor"}'),
            (3, 3, 'Course instructor', '{"role": "tutor"}'),
            (3, 4, 'Course instructor', '{"role": "tutor"}'),
            (3, 5, 'Course instructor', '{"role": "tutor"}'),
            (3, 6, 'Course instructor', '{"role": "tutor"}')
        ]
        
        for user_id, course_id, knowledge_gaps, graph_json in user_courses:
            cursor.execute(
                "INSERT INTO user_course (user_id, course_id, knowledge_gaps, graph_json) VALUES (%s, %s, %s, %s)",
                (user_id, course_id, knowledge_gaps, graph_json)
            )
            
            # Получаем информацию о пользователе из базы
            cursor.execute("SELECT email, role FROM \"user\" WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
            user_email, user_role = user_info if user_info else (f"user_{user_id}", "Unknown")
            
            course_name = course_map.get(course_id, f"Course {course_id}")
            
            if user_role == 'Репетитор':
                print(f"  ✓ Репетитор {user_email} -> {course_name}")
            else:
                print(f"  ✓ Ученик {user_email} -> {course_name}: {knowledge_gaps[:30]}...")
        
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
            (1, 1), (1, 2), (1, 11), (1, 12),  # Курс 1
            (2, 3), (2, 11), (2, 12),          # Курс 2
            (3, 4), (3, 5), (3, 6),            # Курс 3
            (4, 6), (4, 7),                    # Курс 4
            (5, 8), (5, 9),                    # Курс 5
            (6, 9), (6, 10)                    # Курс 6
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
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),  # Курс 1
            (2, 1), (2, 2), (2, 3), (2, 11),         # Курс 2
            (3, 4), (3, 6),                          # Курс 3
            (4, 7), (4, 8), (4, 12),                 # Курс 4
            (5, 9), (5, 4),                          # Курс 5
            (6, 10), (6, 1), (6, 2)                  # Курс 6
        ]
        
        for course_id, topic_id in course_topics:
            cursor.execute("INSERT INTO course_topic (course_id, topic_id) VALUES (%s, %s)", 
                          (course_id, topic_id))
        
        print(f"  ✓ Создано {len(course_topics)} связей курс-тема")
        
        print("\n7. Создание уроков...")
        
        lessons = [
            # Course 1: English for Beginners
            ('Present Simple: theory and examples', 'Text about daily habits', 'Discuss your daily routine', 
             json.dumps({"questions": ["What is Present Simple?", "Give 3 examples"]}), True, False),
            ('Past Simple: regular verbs', 'Story about yesterday', 'Talk about what you did yesterday', 
             json.dumps({"questions": ["How is Past Simple formed?", "Name 5 regular verbs"]}), True, True),
            ('Future with "will"', 'Future plans', 'Discuss your goals', 
             json.dumps({"questions": ["When is will used?", "Create 3 sentences"]}), False, False),
            
            # Course 2: Conversational English
            ('Modal verbs: can/could', 'Dialogues about abilities', 'What you can do', 
             json.dumps({"questions": ["Difference between can and could?"]}), True, False),
            ('Phrasal verbs', 'Text with phrasal verbs', 'Using in speech', 
             json.dumps({"questions": ["Explain get up, give up"]}), True, False),
            ('Present Perfect', 'Experience and achievements', 'Talk about your experience', 
             json.dumps({"questions": ["When is Present Perfect used?"]}), False, False),
            
            # Course 3: Business English
            ('Business vocabulary', 'Business letter', 'Project presentation', 
             json.dumps({"questions": ["Name 10 business terms"]}), True, False),
            ('Negotiations in English', 'Negotiation scenario', 'Role play: negotiations', 
             json.dumps({"questions": ["What phrases to use?"]}), True, False),
            ('CV preparation', 'CV examples', 'Discuss your CV', 
             json.dumps({"questions": ["How to write strong CV?"]}), False, False),
            
            # Course 4: IELTS
            ('IELTS Writing Task 1', 'Graph description example', 'Data analysis', 
             json.dumps({"questions": ["Task 1 structure"]}), True, False),
            ('IELTS Speaking Part 2', 'Topic card', '2-minute monologue', 
             json.dumps({"questions": ["Answer structure"]}), True, False),
            ('IELTS vocabulary', 'Academic texts', 'Using in context', 
             json.dumps({"questions": ["Complex words for IELTS"]}), False, False),
            
            # Course 5: IT English
            ('IT terminology', 'Technical documentation', 'Project discussion', 
             json.dumps({"questions": ["Explain agile, sprint"]}), True, False),
            ('Teamwork', 'Development case', 'Project meeting', 
             json.dumps({"questions": ["Team phrases"]}), True, False),
            ('Technical interview', 'Interview questions', 'Interview preparation', 
             json.dumps({"questions": ["How to answer technical questions?"]}), False, False),
            
            # Course 6: English for Travel
            ('At the airport', 'Airport dialogues', 'Role play: check-in', 
             json.dumps({"questions": ["Airport phrases"]}), True, False),
            ('At the hotel', 'Hotel booking', 'Accommodation discussion', 
             json.dumps({"questions": ["How to book room?"]}), True, False),
            ('At restaurant', 'Menu and food order', 'Ordering at restaurant', 
             json.dumps({"questions": ["Restaurant phrases"]}), False, False)
        ]
        
        for i, lesson in enumerate(lessons, 1):
            cursor.execute(
                "INSERT INTO lesson (theory_text, reading_text, speaking_text, lesson_test_json, is_access, is_ended) VALUES (%s, %s, %s, %s, %s, %s)",
                lesson
            )
        
        print(f"  ✓ Добавлено {len(lessons)} уроков")
        
        # ФИНАЛЬНЫЙ КОММИТ
        conn.commit()
        
        # 8. ФИНАЛЬНАЯ ПРОВЕРКА
        print("\n" + "=" * 60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА ДАННЫХ")
        print("=" * 60)
        
        check_queries = [
            ("SELECT COUNT(*) FROM \"user\"", "Пользователи"),
            ("SELECT COUNT(*) FROM course", "Курсы"),
            ("SELECT COUNT(*) FROM user_course", "Связи пользователь-курс"),
            ("SELECT COUNT(*) FROM material", "Материалы"),
            ("SELECT COUNT(*) FROM topic", "Темы"),
            ("SELECT COUNT(*) FROM lesson", "Уроки"),
            ("SELECT COUNT(*) FROM course_topic", "Связи курс-тема"),
            ("SELECT COUNT(*) FROM course_material", "Связи курс-материал")
        ]
        
        for query, name in check_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {name}: {count}")
        
        # Проверка пользователей
        print("\nИнформация о пользователях:")
        print("=" * 50)
        
        cursor.execute("SELECT user_id, email, role FROM \"user\" ORDER BY user_id")
        users = cursor.fetchall()
        
        for user_id, email, role in users:
            cursor.execute("SELECT COUNT(*) FROM user_course WHERE user_id = %s", (user_id,))
            course_count = cursor.fetchone()[0]
            has_courses = "Есть курсы" if course_count > 0 else "Нет курсов"
            print(f"  ID={user_id}: {email} ({role}) - {has_courses} ({course_count})")
        
        # Проверка сколько учеников на каждом курсе
        print("\nИнформация по курсам:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT c.course_id, c.title, 
                   COUNT(DISTINCT uc.user_id) as total_students,
                   STRING_AGG(u.email, ', ') as student_emails
            FROM course c
            LEFT JOIN user_course uc ON c.course_id = uc.course_id
            LEFT JOIN "user" u ON uc.user_id = u.user_id AND u.role = 'Ученик'
            GROUP BY c.course_id, c.title
            ORDER BY c.course_id
        """)
        
        courses_info = cursor.fetchall()
        for course_id, title, total_students, student_emails in courses_info:
            student_emails = student_emails if student_emails else 'нет учеников'
            print(f"  Курс {course_id}: {title}")
            print(f"    Учеников: {total_students}")
            print(f"    Email учеников: {student_emails}")
            print()
        
        # Информация для тестирования
        print("\n" + "=" * 60)
        print("БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
        print("=" * 60)
        
        print("\nДанные для тестирования:")
        print("-" * 40)
        print("Логины (пароль для всех: 12345678):")
        print("1. matokhin.ilya@yandex.ru (Ученик, курс: English for Beginners)")
        print("2. liana@bk.ru (Ученик, курс: Business English)")
        print("3. yazenin@gmail.com (Репетитор, все курсы)")
        print("4. bokov@yandex.ru (Ученик, курс: IELTS Preparation)")
        print("5. z@z.ru (Ученик, без курсов)")
        print("6. ivanov@example.com (Ученик, курс: English for Beginners) - НОВЫЙ")
        print("\nДля входа на сайт используйте email и пароль 12345678")
        print("\nПримечание: Теперь на курсе 'English for Beginners' 2 ученика!")
        
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