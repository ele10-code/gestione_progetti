import pytest
from app import app, get_db_session
from models.utente import Utente
from models.progetto import Progetto
from models.task import Task

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with get_db_session() as db_session:
            db_session.query(Assegnazione).delete()
            db_session.query(Task).delete()
            db_session.query(Progetto).delete()
            db_session.query(Utente).delete()
            db_session.commit()
        yield client

def test_integration(client):
    # Test user registration
    response = client.post('/register', data={
        'name': 'Integration Test User',
        'email': 'integrationtest@example.com',
        'password': 'password'
    })
    assert response.status_code == 302

    # Test user login
    response = client.post('/login', data={
        'email': 'integrationtest@example.com',
        'password': 'password'
    })
    assert response.status_code == 302

    # Test add project
    response = client.post('/add_project', data={
        'project_name': 'Integration Test Project',
        'project_description': 'This is a test project for integration testing',
        'project_deadline': '2024-12-31'
    })
    assert response.status_code == 302

    db_session = get_db_session()
    project = db_session.query(Progetto).filter_by(nome_progetto='Integration Test Project').first()
    assert project is not None
    assert project.descrizione == 'This is a test project for integration testing'

    # Test add task
    response = client.post('/add_task', data={
        'task_description': 'Integration Test Task',
        'task_status': 'Pending',
        'task_priority': 'High',
        'task_deadline': '2024-12-31',
        'project_id': project.id
    })
    assert response.status_code == 302

    task = db_session.query(Task).filter_by(descrizione='Integration Test Task').first()
    assert task is not None
    db_session.close()
