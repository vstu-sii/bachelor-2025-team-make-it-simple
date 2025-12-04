import psycopg2

def clear_all_tables():
    """Полностью очищает ВСЕ таблицы в базе данных"""
    
    conn = psycopg2.connect(
        host="localhost",
        database="english_courses", 
        user="postgres",
        password="1234"  # Вставьте ваш пароль
    )
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("ПОЛНАЯ ОЧИСТКА БАЗЫ ДАННЫХ")
        print("=" * 60)
        
        # Список всех таблиц в правильном порядке (от зависимых к независимым)
        tables = [
            "course_material",    # Зависит от course и material
            "course_topic",       # Зависит от course и topic
            "user_course",        # Зависит от user и course
            "material",           # Независимая
            "topic",              # Независимая
            "lesson",             # Независимая
            "course",             # Независимая
            "\"user\""           # Независимая (user в кавычках, т.к. зарезервированное слово)
        ]
        
        print("\n1. Очистка таблиц...")
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print(f"  ✓ Таблица {table} очищена")
            except Exception as e:
                print(f"  ⚠ Ошибка при очистке {table}: {e}")
        
        print("\n2. Сброс sequence (автоинкремента)...")
        sequences = [
            "course_course_id_seq",
            "user_user_id_seq",
            "user_course_user_course_id_seq",
            "material_material_id_seq",
            "topic_topic_id_seq", 
            "lesson_lesson_id_seq"
        ]
        
        for seq in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
                print(f"  ✓ Sequence {seq} сброшен")
            except Exception as e:
                print(f"  ⚠ Не удалось сбросить {seq}: {e}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("ПРОВЕРКА: Все таблицы должны быть пусты")
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
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                if count == 0:
                    print(f"  ✓ {name}: {count} записей")
                else:
                    print(f"  ⚠ {name}: {count} записей (должно быть 0!)")
            except Exception as e:
                print(f"  ✗ Ошибка при проверке {name}: {e}")
        
        print("\n" + "=" * 60)
        print("БАЗА ДАННЫХ ПОЛНОСТЬЮ ОЧИЩЕНА!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clear_all_tables()