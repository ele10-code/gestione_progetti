import pytest
import mysql.connector
from app import app, get_db_connection

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



