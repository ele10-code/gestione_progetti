""" Per avere una copertura ancora più completa, consideriamo di aggiungere:
1. Test per scenari di errore specifici (ad esempio, tentativo di creare un progetto con una data di scadenza non valida)
2. Test per funzionalità aggiuntive che potrebbero non essere coperte (ad esempio, modifica di progetti o task esistenti)
3. Test per eventuali API o endpoints aggiuntivi non coperti dai test precedenti. """

import pytest
import logging
from app import app, db_config, get_db_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import string
from flask import session
import json
import coverage

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
    cov = coverage.Coverage(source=['app'])
    cov.start()
    
    yield
    
    cov.stop()
    cov.save()
    
    total = test_results['total']
    passed = test_results['passed']
    percentage = (passed / total) * 100 if total > 0 else 0
    print(f"\nTest Results:")
    print(f"Total Tests: {total}")
    print(f"Passed Tests: {passed}")
    print(f"Success Rate: {percentage:.2f}%")
    
    print("\nTest Coverage:")
    cov.report()
    coverage_percentage = cov.report()
    print(f"Overall Coverage: {coverage_percentage:.2f}%")


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

    @run_test
    def test_project_invalid_deadline(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        with test_client.session_transaction() as sess:
            sess['_flashes'] = []
        response = test_client.post('/add_project', data={
            'project_name': 'Invalid Deadline Project',
            'project_description': 'This project has an invalid deadline',
            'project_deadline': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert any('Scadenza progetto deve essere maggiore di oggi' in msg for category, msg in session.get('_flashes', []))

    @run_test
    def test_edit_project(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Create a project
        response = test_client.post('/add_project', data={
            'project_name': 'Project to Edit',
            'project_description': 'This project will be edited',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Project to Edit'")
            project = cursor.fetchone()
            project_id = project['id']

        # Edit the project
        response = test_client.post(f'/edit_project/{project_id}', data={
            'project_name': 'Edited Project',
            'project_description': 'This project has been edited',
            'project_deadline': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Edited Project' in response.data
        assert b'This project has been edited' in response.data

    @run_test
    def test_edit_task(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Create a project
        project_response = test_client.post('/add_project', data={
            'project_name': 'Task Edit Project',
            'project_description': 'Project for editing tasks',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Task Edit Project'")
            project = cursor.fetchone()
            project_id = project['id']

        # Create a task
        task_response = test_client.post('/add_task', data={
            'task_description': 'Task to Edit',
            'task_status': 'Todo',
            'task_priority': 'Medium',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM tasks WHERE descrizione = 'Task to Edit'")
            task = cursor.fetchone()
            task_id = task['id']

        # Edit the task
        edit_response = test_client.post(f'/edit_task/{task_id}', data={
            'task_description': 'Edited Task',
            'task_status': 'In Progress',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }, follow_redirects=True)
        
        assert edit_response.status_code == 200
        
        # Verify the edit
        verify_response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Edited Task' in verify_response.data
        assert b'In Progress' in verify_response.data
        assert b'High' in verify_response.data

    @run_test
    def test_api_get_tasks(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'API Task Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Create a project
        project_response = test_client.post('/add_project', data={
            'project_name': 'API Task Test Project',
            'project_description': 'Project for API task testing',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'API Task Test Project'")
            project = cursor.fetchone()
            project_id = project['id']

        # Create a task
        test_client.post('/add_task', data={
            'task_description': 'API Test Task',
            'task_status': 'Todo',
            'task_priority': 'High',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }, follow_redirects=True)

       # Get tasks via API
        response = test_client.get(f'/get_project_tasks/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tasks' in data
        tasks = data['tasks']
        assert any(task['descrizione'] == 'API Test Task' for task in tasks)
        assert any(task['stato'] == 'Todo' for task in tasks)
        assert any(task['priorita'] == 'High' for task in tasks)

    @run_test
    def test_task_status_update(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Task Status User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        # Create a project
        project_response = test_client.post('/add_project', data={
            'project_name': 'Task Status Project',
            'project_description': 'Project for testing task status updates',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM progetti WHERE nome_progetto = 'Task Status Project'")
            project = cursor.fetchone()
            project_id = project['id']

        # Create a task
        task_response = test_client.post('/add_task', data={
            'task_description': 'Status Update Task',
            'task_status': 'Todo',
            'task_priority': 'Medium',
            'task_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'project_id': project_id
        }, follow_redirects=True)

        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM tasks WHERE descrizione = 'Status Update Task'")
            task = cursor.fetchone()
            task_id = task['id']

        # Update task status
        update_response = test_client.post(f'/update_task_status/{task_id}', data={
            'new_status': 'In Progress'
        }, follow_redirects=True)
        assert update_response.status_code == 200

        # Verify the status update
        verify_response = test_client.get(f'/get_project_tasks/{project_id}')
        assert b'Status Update Task' in verify_response.data
        assert b'In Progress' in verify_response.data

    @run_test
    def test_delete_nonexistent_project(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        response = test_client.post('/delete_project/9999', follow_redirects=True)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Progetto non trovato'

    @run_test
    def test_delete_nonexistent_task(self, test_client, init_database):
      email = generate_random_email()
      test_client.post('/register', data={
          'name': 'Test User',
          'email': email,
          'password': 'password123'
      }, follow_redirects=True)

      response = test_client.post('/delete_task/9999', follow_redirects=True)
      assert response.status_code == 404
      data = json.loads(response.data)
      assert data['error'] == 'Task non trovato'

    @run_test
    def test_get_tasks_nonexistent_project(self, test_client, init_database):
        email = generate_random_email()
        test_client.post('/register', data={
            'name': 'Test User',
            'email': email,
            'password': 'password123'
        }, follow_redirects=True)

        response = test_client.get('/get_project_tasks/9999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Progetto non trovato'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])