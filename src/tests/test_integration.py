import pytest
import logging
from app import app, db_config, get_db_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import string
from flask import session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@example.com"

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DELETE FROM assegnazioni")
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM progetti")
        cursor.execute("DELETE FROM utenti")
        conn.commit()
        yield conn

test_results = {'total': 0, 'passed': 0}

def run_test(func):
    def wrapper(self, test_client, init_database):
        test_results['total'] += 1
        try:
            func(self, test_client, init_database)
            test_results['passed'] += 1
            logger.info(f"{func.__name__} passed")
        except AssertionError as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper

@pytest.fixture(scope="session", autouse=True)
def print_test_results(request):
    yield
    total = test_results['total']
    passed = test_results['passed']
    percentage = (passed / total) * 100 if total > 0 else 0
    print(f"\nTest Results:")
    print(f"Total Tests: {total}")
    print(f"Passed Tests: {passed}")
    print(f"Success Rate: {percentage:.2f}%")

@pytest.mark.usefixtures("test_client", "init_database")

@pytest.mark.usefixtures("test_client", "init_database")
class TestIntegration:
    @run_test
    def test_registration_login_logout(self, test_client, init_database):
        email = generate_random_email()
        response = test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Dashboard' in response.data
        
        response = test_client.post('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'Register' in response.data
        
        response = test_client.post('/login', data={
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)
        assert b'Dashboard' in response.data
        
        response = test_client.post('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data or b'Register' in response.data

    @run_test
    def test_project_crud(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Test project name validation
        with test_client.session_transaction() as sess:
            sess['_flashes'] = []
        response = test_client.post('/add_project', data={
            'project_name': '',
            'project_description': 'Test description',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert any('Il nome del progetto deve esserci' in msg for category, msg in session.get('_flashes', []))

        # Test successful project creation
        with test_client.session_transaction() as sess:
            sess['_flashes'] = []
        response = test_client.post('/add_project', data={
            'project_name': 'Test Project',
            'project_description': 'This is a test project',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert any('Progetto aggiunto con successo!' in msg for category, msg in session.get('_flashes', []))

        response = test_client.get('/dashboard')
        assert b'Test Project' in response.data

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Test Project'")
            project = cursor.fetchone()
            assert project is not None, "Project was not created in the database"
            project_id = project['id']

        response = test_client.post(f'/delete_project/{project_id}', follow_redirects=True)
        assert any('Project deleted successfully' in msg for category, msg in session.get('_flashes', []))

        response = test_client.get('/dashboard')
        assert b'Test Project' not in response.data

    @run_test
    def test_task_crud(self, test_client, init_database):
        email = generate_random_email()
        
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Create project
        project_data = {
            'project_name': 'Task Test Project',
            'project_description': 'Project for testing tasks',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        test_client.post('/add_project', data=project_data, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = %s", (project_data['project_name'],))
            project = cursor.fetchone()
            assert project is not None, "Project was not created in the database"
            project_id = project['id']

        # Create task
        with test_client.session_transaction() as sess:
            sess['_flashes'] = []
        task_data = {
            'task_description': 'Test Task',
            'task_status': 'Todo',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }
        response = test_client.post('/add_task', data=task_data, follow_redirects=True)
        assert any('Task added successfully' in msg for category, msg in session.get('_flashes', []))

        # Verify task creation
        response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Test Task' in response.data

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM tasks WHERE descrizione = %s", (task_data['task_description'],))
            task = cursor.fetchone()
            assert task is not None, "Task was not created in the database"
            task_id = task['id']

        # Delete task
        with test_client.session_transaction() as sess:
            sess['_flashes'] = []
        response = test_client.post(f'/delete_task/{task_id}', follow_redirects=True)
        assert any('Task deleted successfully' in msg for category, msg in session.get('_flashes', []))

        # Verify task deletion
        response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Test Task' not in response.data

    @run_test
    def test_unauthorized_access(self, test_client, init_database):
        test_client.post('/logout', follow_redirects=True)

        response = test_client.get('/dashboard', follow_redirects=True)
        assert b'Login' in response.data

        response = test_client.post('/add_project', data={
            'project_name': 'Unauthorized Project',
            'project_description': 'This should not be added',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert b'Login' in response.data

        response = test_client.post('/add_task', data={
            'task_description': 'Unauthorized Task',
            'task_status': 'Todo',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': 1
        }, follow_redirects=True)
        assert b'Login' in response.data

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    total = test_results['total']
    passed = test_results['passed']
    percentage = (passed / total) * 100 if total > 0 else 0
    terminalreporter.write_line(f"\nTest Results:")
    terminalreporter.write_line(f"Total Tests: {total}")
    terminalreporter.write_line(f"Passed Tests: {passed}")
    terminalreporter.write_line(f"Success Rate: {percentage:.2f}%")

if __name__ == '__main__':
    pytest.main(['-v', '-s'])