import sys
import os
import pytest
from hypothesis import given, strategies as st
import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app import app, get_db_session
from models.task import Task
from models.progetto import Progetto

# Set recursion limit
sys.setrecursionlimit(1500)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(autouse=True)
def clean_up_db():
    """Ensure the database session is closed after each test."""
    yield
    db_session = get_db_session()
    db_session.close()

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Benvenuti nella Gestione Progetti" in rv.data

def test_add_project(client):
    with app.app_context():
        db_session = get_db_session()
        project_count_before = db_session.query(Progetto).count()
        rv = client.post('/add_project', data=dict(
            project_name="Test Project",
            project_description="Description",
            project_deadline="2024-12-31"
        ), follow_redirects=True)
        project_count_after = db_session.query(Progetto).count()
        print(f"Project count before: {project_count_before}, after: {project_count_after}")
        assert rv.status_code == 200
        assert project_count_after == project_count_before + 1

def test_add_project_invalid_deadline(client):
    rv = client.post('/add_project', data=dict(
        project_name="Test Project",
        project_description="Description",
        project_deadline="2023-12-31"
    ), follow_redirects=True)
    print(rv.data)
    assert rv.status_code == 200
    assert b"Scadenza progetto deve essere maggiore di oggi" in rv.data

def test_add_project_invalid_name(client):
    rv = client.post('/add_project', data=dict(
        project_name="",
        project_description="Description",
        project_deadline="2024-12-31"
    ), follow_redirects=True)
    print(rv.data)
    assert rv.status_code == 200
    assert b"Il nome del progetto deve esserci" in rv.data

def test_add_project_invalid_description(client):
    rv = client.post('/add_project', data=dict(
        project_name="Test Project",
        project_description="",
        project_deadline="2024-12-31"
    ), follow_redirects=True)
    print(rv.data)
    assert rv.status_code == 200
    assert b"La descrizione del progetto deve esserci" in rv.data

@given(
    st.text(), 
    st.text(), 
    st.text(), 
    st.dates(min_value=datetime.date(2024, 1, 1), max_value=datetime.date(2024, 12, 31)), 
    st.integers(min_value=1, max_value=100)
)
def test_add_task_property_based(task_description, task_status, task_priority, task_deadline, project_id):
    with app.test_client() as client:
        with app.app_context():
            db_session = get_db_session()
            task_count_before = db_session.query(Task).count()
            
            # Ensure the project exists for given project_id
            project = db_session.query(Progetto).get(project_id)
            if not project:
                project = Progetto(id=project_id, nome_progetto=f"Test Project {project_id}", descrizione="Description", scadenza=datetime.datetime.now())
                db_session.add(project)
                db_session.commit()
            
            rv = client.post('/add_task', data=dict(
                task_description=task_description,
                task_status=task_status,
                task_priority=task_priority,
                task_deadline=task_deadline.isoformat(),
                project_id=project_id
            ), follow_redirects=True)
            
            task_count_after = db_session.query(Task).count()
            print(f"Task count before: {task_count_before}, after: {task_count_after}")
            assert rv.status_code == 200
            assert task_count_after == task_count_before + 1
