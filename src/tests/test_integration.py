import pytest
import logging
import sqlite3
from app import app
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

total_tests = 0
successful_tests = 0

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def init_database():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            _is_active INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE progetti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_progetto TEXT NOT NULL,
            descrizione TEXT,
            scadenza DATE,
            id_responsabile INTEGER,
            FOREIGN KEY (id_responsabile) REFERENCES utenti(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descrizione TEXT NOT NULL,
            stato TEXT,
            priorita TEXT,
            scadenza DATE,
            id_progetto INTEGER,
            FOREIGN KEY (id_progetto) REFERENCES progetti(id)
        )
    """)
    yield conn
    conn.close()

def run_test(test_function):
    global total_tests, successful_tests
    total_tests += 1
    try:
        test_function()
        successful_tests += 1
        logger.info(f"{test_function.__name__} passed successfully")
    except AssertionError as e:
        logger.error(f"{test_function.__name__} failed: {str(e)}")

def test_registration_login_logout(test_client, init_database):
    def test():
        # Registrazione
        response = test_client.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Registration completed successfully!' in response.data
        
        # Login
        response = test_client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Login successful!' in response.data
        
        # Logout
        response = test_client.post('/logout', follow_redirects=True)
        assert b'You have logged out.' in response.data
    run_test(test)

def test_project_crud(test_client, init_database):
    def test():
        # Login
        test_client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Creazione progetto
        response = test_client.post('/add_project', data={
            'project_name': 'Test Project',
            'project_description': 'This is a test project',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert b'Progetto aggiunto con successo!' in response.data
        
        # Visualizzazione progetto
        response = test_client.get('/dashboard')
        assert b'Test Project' in response.data
        
        # Aggiornamento progetto (se la funzionalità esiste)
        # response = test_client.post('/update_project/1', data={
        #     'project_name': 'Updated Test Project',
        #     'project_description': 'This is an updated test project',
        #     'project_deadline': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        # }, follow_redirects=True)
        # assert b'Project updated successfully!' in response.data
        
        # Eliminazione progetto
        cursor = init_database.cursor()
        cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Test Project'")
        project_id = cursor.fetchone()[0]
        cursor.close()

        response = test_client.post(f'/delete_project/{project_id}', follow_redirects=True)
        assert b'Project deleted successfully!' in response.data

        # Verifica che il progetto sia stato eliminato
        response = test_client.get('/dashboard')
        assert b'Test Project' not in response.data
    run_test(test)

def test_task_crud(test_client, init_database):
    def test():
        # Login
        login_response = test_client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Login successful!' in login_response.data, "Login failed"
        logger.info("Login successful")

        # Crea un progetto per i test sui task
        project_response = test_client.post('/add_project', data={
            'project_name': 'Task Test Project',
            'project_description': 'Project for testing tasks',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert b'Progetto aggiunto con successo!' in project_response.data, "Project creation failed"
        logger.info("Project created successfully")

        cursor = init_database.cursor()
        cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Task Test Project'")
        result = cursor.fetchone()
        assert result is not None, "Project not found in database"
        project_id = result[0]
        cursor.close()
        logger.info(f"Project ID: {project_id}")

        # Creazione task
        task_response = test_client.post('/add_task', data={
            'task_description': 'Test Task',
            'task_status': 'Todo',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }, follow_redirects=True)
        assert b'Task added successfully!' in task_response.data, "Task creation failed"
        logger.info("Task created successfully")

        # Visualizzazione task
        view_response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Test Task' in view_response.data, "Task not found in project tasks"
        logger.info("Task found in project tasks")

        # Eliminazione task
        cursor = init_database.cursor()
        cursor.execute("SELECT id FROM tasks WHERE descrizione = 'Test Task'")
        task_result = cursor.fetchone()
        assert task_result is not None, "Task not found in database"
        task_id = task_result[0]
        cursor.close()
        logger.info(f"Task ID: {task_id}")

        delete_response = test_client.post(f'/delete_task/{task_id}', follow_redirects=True)
        assert b'Task deleted successfully!' in delete_response.data, "Task deletion failed"
        logger.info("Task deleted successfully")

        # Verifica che il task sia stato eliminato
        final_response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Test Task' not in final_response.data, "Task still present after deletion"
        logger.info("Task confirmed deleted")

    run_test(test)

def test_unauthorized_access(test_client, init_database):
    def test():
        # Logout per assicurarsi che l'utente non sia autenticato
        test_client.post('/logout', follow_redirects=True)

        # Tenta di accedere alla dashboard senza login
        response = test_client.get('/dashboard', follow_redirects=True)
        assert b'Please log in to access this page.' in response.data

        # Tenta di aggiungere un progetto senza login
        response = test_client.post('/add_project', data={
            'project_name': 'Unauthorized Project',
            'project_description': 'This should not be added',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert b'Please log in to access this page.' in response.data

        # Tenta di aggiungere un task senza login
        response = test_client.post('/add_task', data={
            'task_description': 'Unauthorized Task',
            'task_status': 'Todo',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': 1
        }, follow_redirects=True)
        assert b'Please log in to access this page.' in response.data
    run_test(test)

@pytest.fixture(scope="session", autouse=True)
def print_test_stats(request):
    yield
    print("\n=== Test Results ===")
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {successful_tests}")
    if total_tests > 0:
        success_rate = (successful_tests / total_tests) * 100
        print(f"Success rate: {success_rate:.2f}%")
    else:
        print("No tests were run.")

if __name__ == '__main__':
    pytest.main(['-v', '-s'])