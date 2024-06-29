import pytest
from app import app as flask_app
from database.database import get_db_session
from models.utente import Utente
from models.progetto import Progetto
from models.task import Task

def test_register_user(client):
    print("Testing user registration...")
    response = client.post('/register', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password'
    })
    assert response.status_code == 200

def test_login_user(client):
    print("Testing user login...")
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    assert response.status_code == 200

def test_dashboard_access(client):
    print("Testing dashboard access...")
    client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_add_project(client):
    print("Testing adding a project...")
    client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    response = client.post('/add_project', data={
        'project_name': 'Test Project',
        'project_description': 'This is a test project',
        'project_deadline': '2024-12-31'
    })
    assert response.status_code == 302  # Redirects to dashboard
    db_session = get_db_session()
    project = db_session.query(Progetto).filter_by(nome_progetto='Test Project').first()
    assert project is not None
    assert project.descrizione == 'This is a test project'

def test_add_task(client):
    print("Testing adding a task...")
    db_session = get_db_session()
    project = db_session.query(Progetto).filter_by(nome_progetto='Test Project').first()
    project_id = project.id
    db_session.close()

    client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    response = client.post('/add_task', data={
        'task_description': 'Test Task',
        'task_status': 'Pending',
        'task_priority': 'High',
        'task_deadline': '2024-12-31',
        'project_id': project_id
    })
    assert response.status_code == 302  # Redirects to dashboard
    db_session = get_db_session()
    task = db_session.query(Task).filter_by(descrizione='Test Task').first()
    assert task is not None
