import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_database():
    """Удаляет и создает БД заново"""
    
    # Подключаемся к postgres БД
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        print("Удаление БД english_courses...")
        cursor.execute("DROP DATABASE IF EXISTS english_courses")
        print("  ✓ БД удалена")
        
        print("Создание новой БД english_courses...")
        cursor.execute("CREATE DATABASE english_courses")
        print("  ✓ БД создана")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_database()
    print("\nТеперь запустите: python fill_db.py")