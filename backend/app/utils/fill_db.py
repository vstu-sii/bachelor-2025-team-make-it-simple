import psycopg2
import json
import bcrypt
from datetime import date, datetime

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
        password="1234"
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ С ГРАФАМИ КУРСОВ")
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
        
        # Определяем графы для каждого курса (будет использоваться при создании user_course)
        course_graphs = [
            # Курс 1: English for Beginners
            {
                "nodes": [
                    {"id": "1", "label": "Present Simple", "data": {"lesson_id": 1}, "position": {"x": 100, "y": 50}, "type": "custom"},
                    {"id": "2", "label": "Past Simple", "data": {"lesson_id": 2}, "position": {"x": 100, "y": 200}, "type": "custom"},
                    {"id": "3", "label": "Future Tenses", "data": {"lesson_id": 3}, "position": {"x": 300, "y": 125}, "type": "custom"},
                    {"id": "4", "label": "Articles a/an/the", "data": {"lesson_id": 4}, "position": {"x": 500, "y": 50}, "type": "custom"},
                    {"id": "5", "label": "Basic Vocabulary", "data": {"lesson_id": 5}, "position": {"x": 500, "y": 200}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Alternative"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-5", "source": "3", "target": "5", "label": "Next"},
                    {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
                ]
            },
            # Курс 2: Conversational English
            {
                "nodes": [
                    {"id": "1", "label": "Greetings", "data": {"lesson_id": 6}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Daily Conversations", "data": {"lesson_id": 7}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Shopping Dialogues", "data": {"lesson_id": 8}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Restaurant Talk", "data": {"lesson_id": 9}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            },
            # Курс 3: Business English
            {
                "nodes": [
                    {"id": "1", "label": "Business Email", "data": {"lesson_id": 10}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Meetings", "data": {"lesson_id": 11}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Presentations", "data": {"lesson_id": 12}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Negotiations", "data": {"lesson_id": 13}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            },
            # Курс 4: IELTS Preparation
            {
                "nodes": [
                    {"id": "1", "label": "Listening", "data": {"lesson_id": 14}, "position": {"x": 100, "y": 50}, "type": "custom"},
                    {"id": "2", "label": "Reading", "data": {"lesson_id": 15}, "position": {"x": 100, "y": 150}, "type": "custom"},
                    {"id": "3", "label": "Writing Task 1", "data": {"lesson_id": 16}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "4", "label": "Writing Task 2", "data": {"lesson_id": 17}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "5", "label": "Speaking", "data": {"lesson_id": 18}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-5", "source": "3", "target": "5", "label": "Next"},
                    {"id": "e4-5", "source": "4", "target": "5", "label": "Next"}
                ]
            },
            # Курс 5: English for IT
            {
                "nodes": [
                    {"id": "1", "label": "IT Vocabulary", "data": {"lesson_id": 19}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Documentation", "data": {"lesson_id": 20}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Team Communication", "data": {"lesson_id": 21}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Technical Interview", "data": {"lesson_id": 22}, "position": {"x": 500, "y": 100}, "type": "custom"}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2", "label": "Next"},
                    {"id": "e1-3", "source": "1", "target": "3", "label": "Next"},
                    {"id": "e2-4", "source": "2", "target": "4", "label": "Next"},
                    {"id": "e3-4", "source": "3", "target": "4", "label": "Next"}
                ]
            },
            # Курс 6: English for Travel
            {
                "nodes": [
                    {"id": "1", "label": "Airport", "data": {"lesson_id": 23}, "position": {"x": 100, "y": 100}, "type": "custom"},
                    {"id": "2", "label": "Hotel", "data": {"lesson_id": 24}, "position": {"x": 300, "y": 50}, "type": "custom"},
                    {"id": "3", "label": "Restaurant", "data": {"lesson_id": 25}, "position": {"x": 300, "y": 150}, "type": "custom"},
                    {"id": "4", "label": "Sightseeing", "data": {"lesson_id": 26}, "position": {"x": 500, "y": 100}, "type": "custom"}
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
        
        user_courses = [
            # User 1 -> Course 1 с графом курса 1
            (1, 1, 'Gaps in Past Simple and articles', 
             json.dumps(course_graphs[0]),  # Граф для курса 1
             json.dumps({
                 "custom_nodes": [
                     {"id": "1", "label": "Present Simple", "color": "#4CAF50", "completed": True},
                     {"id": "2", "label": "Past Simple", "color": "#FF9800", "completed": False},
                     {"id": "3", "label": "Future Tenses", "color": "#9C27B0", "completed": False}
                 ],
                 "custom_edges": [
                     {"from": "1", "to": "2", "label": "Focus on this"},
                     {"from": "2", "to": "3", "label": "Next"}
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
            # User 2 -> Course 3 с графом курса 3
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
        
        for user_id, course_id, knowledge_gaps, graph_json, output_test_json in user_courses:
            cursor.execute(
                """INSERT INTO user_course (user_id, course_id, knowledge_gaps, graph_json, output_test_json) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, course_id, knowledge_gaps, graph_json, output_test_json)
            )
            
            cursor.execute("SELECT email, role FROM \"user\" WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
            user_email, user_role = user_info if user_info else (f"user_{user_id}", "Unknown")
            
            course_name = course_map.get(course_id, f"Course {course_id}")
            
            # Парсим graph_json для подсчета вершин и связей
            graph_data = json.loads(graph_json)
            nodes_count = len(graph_data.get('nodes', [])) if isinstance(graph_data, dict) else 0
            edges_count = len(graph_data.get('edges', [])) if isinstance(graph_data, dict) else 0
            
            if user_role == 'Репетитор':
                print(f"  ✓ Репетитор {user_email} -> {course_name}")
            else:
                print(f"  ✓ Ученик {user_email} -> {course_name} ({nodes_count} вершин, {edges_count} связей)")
        
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
        
        print("\n7. Создание уроков для графа...")
        
        lessons = [
            # Course 1 lessons
            ('Present Simple: theory and examples', 'Text about daily habits', 'Discuss your daily routine', 
             json.dumps({"questions": ["What is Present Simple?", "Give 3 examples"]}), True, False),
            ('Past Simple: regular verbs', 'Story about yesterday', 'Talk about what you did yesterday', 
             json.dumps({"questions": ["How is Past Simple formed?", "Name 5 regular verbs"]}), True, True),
            ('Future with "will"', 'Future plans', 'Discuss your goals', 
             json.dumps({"questions": ["When is will used?", "Create 3 sentences"]}), False, False),
            ('Articles a/an/the', 'Rules and usage', 'Practice with nouns', 
             json.dumps({"questions": ["When to use a/an?", "When to use the?"]}), True, False),
            ('Basic Vocabulary: Family', 'Family members', 'Describe your family', 
             json.dumps({"questions": ["Name family members"]}), True, False),
            
            # Course 2 lessons
            ('Greetings and Introductions', 'Basic greetings', 'Introduce yourself', 
             json.dumps({"questions": ["How to greet someone?"]}), True, False),
            ('Daily Conversations', 'Everyday dialogues', 'Practice small talk', 
             json.dumps({"questions": ["Common daily questions"]}), True, False),
            ('Shopping Dialogues', 'Store conversations', 'Role play shopping', 
             json.dumps({"questions": ["How to ask for price?"]}), True, False),
            ('Restaurant Conversations', 'Menu and ordering', 'Order food in restaurant', 
             json.dumps({"questions": ["Restaurant phrases"]}), False, False),
            
            # Course 3 lessons
            ('Business Email Writing', 'Email structure', 'Write business email', 
             json.dumps({"questions": ["Email format"]}), True, False),
            ('Meeting Vocabulary', 'Meeting phrases', 'Participate in meeting', 
             json.dumps({"questions": ["Meeting terms"]}), True, False),
            ('Presentation Skills', 'Presenting ideas', 'Give short presentation', 
             json.dumps({"questions": ["Presentation structure"]}), True, False),
            ('Negotiation Techniques', 'Negotiation phrases', 'Role play negotiation', 
             json.dumps({"questions": ["Negotiation strategies"]}), False, False),
            
            # Course 4 lessons
            ('IELTS Listening Part 1', 'Basic listening', 'Answer questions', 
             json.dumps({"questions": ["Listening tips"]}), True, False),
            ('IELTS Reading Section', 'Reading strategies', 'Practice reading', 
             json.dumps({"questions": ["Reading techniques"]}), True, False),
            ('IELTS Writing Task 1', 'Graph description', 'Describe chart', 
             json.dumps({"questions": ["Task 1 structure"]}), True, False),
            ('IELTS Writing Task 2', 'Essay writing', 'Write essay', 
             json.dumps({"questions": ["Essay structure"]}), True, False),
            ('IELTS Speaking Part 2', '2-minute talk', 'Give monologue', 
             json.dumps({"questions": ["Speaking strategies"]}), False, False),
            
            # Course 5 lessons
            ('IT Vocabulary Basics', 'Technical terms', 'Discuss technology', 
             json.dumps({"questions": ["IT terms"]}), True, False),
            ('Reading Documentation', 'Technical docs', 'Explain documentation', 
             json.dumps({"questions": ["Doc understanding"]}), True, False),
            ('Team Communication', 'Team discussions', 'Team meeting practice', 
             json.dumps({"questions": ["Teamwork phrases"]}), True, False),
            ('Technical Interview Prep', 'Interview questions', 'Mock interview', 
             json.dumps({"questions": ["Interview tips"]}), False, False),
            
            # Course 6 lessons
            ('At the Airport', 'Check-in procedures', 'Airport role play', 
             json.dumps({"questions": ["Airport phrases"]}), True, False),
            ('Hotel Check-in', 'Hotel vocabulary', 'Book hotel room', 
             json.dumps({"questions": ["Hotel terms"]}), True, False),
            ('Restaurant Ordering', 'Food vocabulary', 'Order in restaurant', 
             json.dumps({"questions": ["Menu items"]}), True, False),
            ('Sightseeing Vocabulary', 'Tourist places', 'Ask for directions', 
             json.dumps({"questions": ["Tourism phrases"]}), False, False)
        ]
        
        for lesson in lessons:
            cursor.execute(
                """INSERT INTO lesson (theory_text, reading_text, speaking_text, lesson_test_json, is_access, is_ended) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                lesson
            )
        
        print(f"  ✓ Добавлено {len(lessons)} уроков")
        
        conn.commit()
        
        # 8. ФИНАЛЬНАЯ ПРОВЕРКА
        print("\n" + "=" * 60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА ДАННЫХ С ГРАФАМИ")
        print("=" * 60)
        
        # Проверка графов в user_course
        print("\nПроверка графов в таблице user_course:")
        cursor.execute("""
            SELECT uc.user_course_id, u.email, c.title, uc.graph_json
            FROM user_course uc
            JOIN "user" u ON uc.user_id = u.user_id
            JOIN course c ON uc.course_id = c.course_id
            WHERE u.role != 'Репетитор'
            ORDER BY uc.user_course_id
        """)
        
        user_courses_data = cursor.fetchall()
        for uc_id, email, title, graph_json in user_courses_data:
            if graph_json:
                try:
                    graph_data = json.loads(graph_json)
                    nodes_count = len(graph_data.get('nodes', []))
                    edges_count = len(graph_data.get('edges', []))
                    print(f"  UserCourse {uc_id}: {email} -> {title}: {nodes_count} вершин, {edges_count} связей")
                except:
                    print(f"  UserCourse {uc_id}: {email} -> {title}: граф невалиден")
            else:
                print(f"  UserCourse {uc_id}: {email} -> {title}: граф отсутствует")
        
        # Общая статистика
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
        
        # Проверка связей уроков с узлами графа
        print("\nПроверка соответствия уроков и графов:")
        for i in range(len(course_graphs)):
            course_id = i + 1
            graph = course_graphs[i]
            
            # Получаем уроки для курса
            cursor.execute("SELECT lesson_id FROM lesson ORDER BY lesson_id")
            all_lessons = [row[0] for row in cursor.fetchall()]
            
            # Проверяем соответствие lesson_id в графе
            lesson_ids_in_graph = []
            for node in graph.get('nodes', []):
                data = node.get('data', {})
                lesson_id = data.get('lesson_id')
                if lesson_id:
                    lesson_ids_in_graph.append(lesson_id)
            
            print(f"  Курс {course_id}: {len(lesson_ids_in_graph)} узлов графа ссылаются на уроки")
        
        print("\nИнформация для тестирования графа:")
        print("-" * 40)
        print("1. Графы курсов хранятся в таблице user_course (поле graph_json)")
        print("2. Каждый ученик имеет индивидуальный граф для своего курса")
        print("3. Для тестирования используйте:")
        print("   - Ученик: matokhin.ilya@yandex.ru (ID=1), курс: English for Beginners (ID=1)")
        print("   - Ученик: ivanov@example.com (ID=6), курс: English for Beginners (ID=1)")
        print("4. Репетитор имеет доступ ко всем курсам")
        print("5. Всего создано 26 уроков с lesson_id от 1 до 26")
        
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