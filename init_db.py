import mysql.connector
import os
import time

def wait_for_db():
    max_tries = 30
    for _ in range(max_tries):
        try:
            conn = mysql.connector.connect(
                host=os.getenv('TEST_DB_HOST'),
                user=os.getenv('TEST_DB_USER'),
                password=os.getenv('TEST_DB_PASSWORD'),
                database=os.getenv('TEST_DB_NAME')
            )
            conn.close()
            return True
        except mysql.connector.Error:
            time.sleep(1)
    return False

def init_db():
    if not wait_for_db():
        print("Database connection failed after multiple attempts")
        return False

    conn = mysql.connector.connect(
        host=os.getenv('TEST_DB_HOST'),
        user=os.getenv('TEST_DB_USER'),
        password=os.getenv('TEST_DB_PASSWORD'),
        database=os.getenv('TEST_DB_NAME')
    )
    cursor = conn.cursor()

    # Add your table creation statements here
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assegnazioni (
            id INT AUTO_INCREMENT PRIMARY KEY,
            -- Add other columns as needed
        )
    """)

    # Add more table creation statements as needed

    conn.commit()
    cursor.close()
    conn.close()
    return True

if __name__ == "__main__":
    if init_db():
        print("Database initialized successfully")
    else:
        print("Failed to initialize database")
        exit(1)