# conftest.py

import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Aggiungi il percorso principale al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from app import app as flask_app
from database.database import Base, get_db_session, SessionLocal

# Configurazione del database di test
TEST_DATABASE_URL = "mysql+mysqlconnector://admin:admin_password@localhost/TestGestioneProgetti"

@pytest.fixture(scope='module')
def test_engine():
    print(f"Connecting to test database with URL: {TEST_DATABASE_URL}")
    test_engine = create_engine(TEST_DATABASE_URL, echo=True)
    print("Creating all tables in the test database...")
    try:
        Base.metadata.create_all(test_engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
    yield test_engine
    print("Dropping all tables in the test database...")
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()

@pytest.fixture(scope='module')
def session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = scoped_session(TestingSessionLocal)
    yield session
    session.remove()

@pytest.fixture(scope='module')
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            Base.metadata.create_all(bind=SessionLocal().get_bind())
        yield client
        with flask_app.app_context():
            Base.metadata.drop_all(bind=SessionLocal().get_bind())