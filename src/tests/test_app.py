import pytest
from flask import Flask, request, url_for
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import mysql.connector
from app import app, get_db_connection, add_project

db_config = {
    'user': 'admin',
    'password': 'admin_password',
    'host': 'localhost',
    'database': 'TestGestioneProgetti'
}

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Pulisci le tabelle
            cursor.execute('DELETE FROM assegnazioni')
            cursor.execute('DELETE FROM tasks')
            cursor.execute('DELETE FROM progetti')
            cursor.execute('DELETE FROM utenti')
            conn.commit()
            cursor.close()
        yield client

def test_register_user(client):
    response = client.post('/register', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password'
    })
    assert response.status_code == 302  # Verifica che ci sia una redirezione
    assert response.headers['Location'] == '/dashboard'  # Verifica che la redirezione avvenga alla dashboard

def test_login_user(client):
    # Prima crea un utente da usare per il login
    client.post('/register', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password'
    })
    response = client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password'
    })
    assert response.status_code == 302  # Verifica che ci sia una redirezione
    assert response.headers['Location'] == '/dashboard'  # Verifica che la redirezione avvenga alla dashboard

@pytest.mark.parametrize("data, expected_message, should_add_project", [
    (
        {
            'project_name': 'Test Project',
            'project_description': 'This is a test project',
            'project_deadline': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        },
        b'Progetto aggiunto con successo!',
        True
    ),
    (
        {
            'project_name': '',
            'project_description': 'This is a test project',
            'project_deadline': '2024-12-31'
        },
        b'Il nome del progetto deve esserci',
        False
    ),
    (
        {
            'project_name': 'Test Project',
            'project_description': '',
            'project_deadline': '2024-12-31'
        },
        b'La descrizione del progetto deve esserci',
        False
    ),
    (
        {
            'project_name': 'Test Project',
            'project_description': 'This is a test project',
            'project_deadline': '2024/12/31'
        },
        b'Formato data non valido. Utilizza YYYY-MM-DD',
        False
    ),
    (
        {
            'project_name': 'Test Project',
            'project_description': 'This is a test project',
            'project_deadline': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        },
        b'Scadenza progetto deve essere maggiore di oggi',
        False
    ),
])
def test_add_project(client, data, expected_message, should_add_project):
    with patch('app.get_db_connection') as mock_get_db_connection, \
         patch('app.current_user') as mock_current_user:
        
        mock_current_user.id = 1  # Simulate a logged-in user
        mock_conn = mock_get_db_connection.return_value.__enter__.return_value
        mock_cursor = mock_conn.cursor.return_value

        response = client.post('/add_project', data=data, follow_redirects=True)
        
        assert response.status_code == 200
        assert expected_message in response.data

        if should_add_project:
            # Verify database operations only for successful project addition
            mock_cursor.execute.assert_called_once()
            assert 'INSERT INTO progetti' in mock_cursor.execute.call_args[0][0]
            mock_conn.commit.assert_called_once()
        else:
            mock_cursor.execute.assert_not_called()
            mock_conn.commit.assert_not_called()

@pytest.fixture
def mock_db_connection():
    with patch('app.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

def test_add_task(client, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    task_data = {
        'task_description': 'New Task',
        'task_status': 'In Progress',
        'task_priority': 'High',
        'task_deadline': '2024-12-31',
        'project_id': '1'
    }
    
    with patch('flask_login.utils._get_user') as mock_current_user:
        mock_current_user.return_value.id = 1
        response = client.post('/add_task', data=task_data)
    
    assert response.status_code == 302  # Redirect status code
    mock_cursor.execute.assert_called_once()
    assert 'INSERT INTO tasks' in mock_cursor.execute.call_args[0][0]
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_delete_project(client, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    with patch('flask_login.utils._get_user') as mock_current_user:
        mock_current_user.return_value.id = 1
        response = client.post('/delete_project/1')
    
    assert response.status_code == 302  # Redirect status code
    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM progetti WHERE id = %s AND id_responsabile = %s',
        (1, 1)
    )
    mock_conn.return_value.__enter__.return_value.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

@pytest.mark.parametrize("scenario", ["authorized", "unauthorized", "not_found"])
def test_delete_task(client, mock_db_connection, scenario):
    mock_conn, mock_cursor = mock_db_connection
    
    if scenario == "authorized":
        mock_cursor.fetchone.side_effect = [(1,), (1,)]
        expected_status = 302  # Redirect dopo eliminazione riuscita
    elif scenario == "unauthorized":
        mock_cursor.fetchone.side_effect = [(1,), (2,)]
        expected_status = 404  # Not Found per utente non autorizzato
    else:  # not_found
        mock_cursor.fetchone.side_effect = [None]
        expected_status = 404  # Not Found per task non esistente
    
    with patch('flask_login.utils._get_user') as mock_current_user:
        mock_current_user.return_value.id = 1
        response = client.post('/delete_task/1')
    
    assert response.status_code == expected_status
    
    if scenario == "authorized":
        assert mock_cursor.execute.call_count >= 2
        assert any('DELETE FROM tasks' in call[0][0] for call in mock_cursor.execute.call_args_list)
        mock_conn.return_value.__enter__.return_value.commit.assert_called_once()
    else:
        assert mock_cursor.execute.call_count <= 2
        mock_conn.return_value.__enter__.return_value.commit.assert_not_called()

def test_get_project_tasks(client, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    mock_cursor.fetchone.return_value = (1,)  # Simula che il progetto esista e l'utente sia autorizzato
    mock_cursor.fetchall.return_value = [
        (1, 'Task 1', 'In Progress', 'High', datetime(2024, 12, 31)),
        (2, 'Task 2', 'Todo', 'Medium', None)
    ]
    
    with patch('flask_login.utils._get_user') as mock_current_user:
        mock_current_user.return_value.id = 1
        response = client.get('/get_project_tasks/1')
    
    assert response.status_code == 200
    assert response.json == {
        'tasks': [
            {
                'id': 1,
                'descrizione': 'Task 1',
                'stato': 'In Progress',
                'priorita': 'High',
                'scadenza': '2024-12-31'
            },
            {
                'id': 2,
                'descrizione': 'Task 2',
                'stato': 'Todo',
                'priorita': 'Medium',
                'scadenza': None
            }
        ]
    }
    assert mock_cursor.execute.call_count >= 2
    assert any('SELECT id_responsabile FROM progetti' in call[0][0] for call in mock_cursor.execute.call_args_list)
    assert any('SELECT t.id, t.descrizione, t.stato, t.priorita, t.scadenza' in call[0][0] for call in mock_cursor.execute.call_args_list)
