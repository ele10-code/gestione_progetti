import mysql.connector
from mysql.connector import errorcode

db_config = {
    'user': 'admin',
    'password': 'admin_password',
    'host': 'localhost'
}

# Nome del database di test
database_name = 'TestGestioneProgetti'

def create_database():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database {database_name} created successfully")
    except mysql.connector.Error as err:
        print(f"Failed to create database: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_database()
