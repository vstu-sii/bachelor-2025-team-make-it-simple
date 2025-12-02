import psycopg2
import json
from datetime import date

def fill_database():
    """Проверяет существование пользователей 1-4 и заполняет остальные таблицы"""
    
    conn = psycopg2.connect(
        host="localhost",
        database="english_courses",
        user="postgres",
        password="1234"  # Вставьте ваш пароль
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        # 1. Проверяем существование пользователей 1-4
        print("\n1. Проверка существования пользователей...")
        
        cursor.execute("SELECT user_id, email, role FROM \"user\" WHERE user_id IN (1, 2, 3, 4) ORDER BY user_id")
        existing_users = cursor.fetchall()
        
        if len(existing_users) < 4:
            print(f"  ⚠ Найдено только {len(existing_users)} из 4 пользователей!")
            print("  Создайте пользователей с ID 1, 2, 3, 4 перед запуском этого скрипта.")
            print("  ID=3 должен быть репетитором, остальные - учениками.")
            return
        
        users_data = {}
        for user_id, email, role in existing_users:
            users_data[user_id] = {'email': email, 'role': role}
            print(f"  ✓ Пользователь ID={user_id}: {email} ({role})")
        
        # Проверяем, что ID=3 - репетитор, остальные - ученики
        if users_data[3]['role'] != 'Репетитор':
            print(f"\n  ❌ ОШИБКА: Пользователь ID=3 должен быть репетитором, а он {users_data[3]['role']}!")
            return
        
        for user_id in [1, 2, 4]:
            if users_data[user_id]['role'] != 'Ученик':
                print(f"  ⚠ Предупреждение: Пользователь ID={user_id} должен быть учеником, а он {users_data[user_id]['role']}")
        
        print("\n2. Очистка старых данных (кроме пользователей)...")
        
        # Очищаем все таблицы кроме user
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
                pass  # Игнорируем ошибки если sequence не существует
        
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
        # Ученик 2 (ID=2) -> Курс 3 (Business English)  
        # Ученик 4 (ID=4) -> Курс 4 (IELTS Preparation)
        # Репетитор 3 (ID=3) -> ВСЕ курсы (1-6)
        
        user_courses = [
            # Ученики
            (1, 1, 'Gaps in Past Simple and articles', 
             '{"nodes": ["Present Simple", "Past Simple"], "edges": [{"from": "Present Simple", "to": "Past Simple"}]}'),
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
            
            user_email = users_data[user_id]['email']
            user_role = users_data[user_id]['role']
            course_name = course_map.get(course_id, f"Course {course_id}")
            
            if user_role == 'Репетитор':
                print(f"  ✓ Репетитор {user_email} -> {course_name}")
            else:
                print(f"  ✓ Ученик {user_email} -> {course_name}: {knowledge_gaps[:30]}...")
        
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
        
        # Проверка связей для API
        print("\nДанные для тестирования API:")
        print("=" * 50)
        
        # Для ученика ID=1
        cursor.execute("""
            SELECT u.user_id, u.email, u.role, c.title, uc.knowledge_gaps
            FROM "user" u
            LEFT JOIN user_course uc ON u.user_id = uc.user_id
            LEFT JOIN course c ON uc.course_id = c.course_id
            WHERE u.user_id = 1
        """)
        
        row = cursor.fetchone()
        if row and row[3]:
            print(f"✓ Ученик ID=1 ({row[1]}) имеет курс: {row[3]}")
        else:
            print(f"✗ Ученик ID=1 НЕ ИМЕЕТ КУРСА!")
        
        # Для репетитора ID=3
        cursor.execute("""
            SELECT u.user_id, u.email, u.role, COUNT(DISTINCT uc.course_id) as course_count
            FROM "user" u
            LEFT JOIN user_course uc ON u.user_id = uc.user_id
            WHERE u.user_id = 3
            GROUP BY u.user_id, u.email, u.role
        """)
        
        row = cursor.fetchone()
        if row:
            print(f"✓ Репетитор ID=3 ({row[1]}) ведет {row[3]} курсов")
        
        print("\n" + "=" * 60)
        print("БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА!")
        print("=" * 60)
        print("\nТеперь можно тестировать API:")
        print("  - Ученик ID=1: GET /auth/1/with_course")
        print("  - Ученик ID=2: GET /auth/2/with_course")
        print("  - Репетитор ID=3: GET /auth/3/with_course")
        print("  - Ученик ID=4: GET /auth/4/with_course")
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fill_database()