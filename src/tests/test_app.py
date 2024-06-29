import unittest
from app import app, db
from models.utente import Utente
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create test user
        self.test_user = Utente(id=1, nome="Mario Rossi", email="mario.rossi@example.com", password_hash=generate_password_hash("password"))

        # Create database and add test user
        with app.app_context():
            db.create_all()
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        # Remove database and test user
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_success(self):
        response = self.app.post('/login', data=dict(email="mario.rossi@example.com", password="password"), follow_redirects=True)
        self.assertIn(b'Login successful!', response.data)

    def test_login_failure(self):
        response = self.app.post('/login', data=dict(email="mario.rossi@example.com", password="wrongpassword"), follow_redirects=True)
        self.assertIn(b'Invalid email or password.', response.data)

    def test_logout(self):
        self.app.post('/login', data=dict(email="mario.rossi@example.com", password="password"), follow_redirects=True)
        response = self.app.post('/logout', follow_redirects=True)
        self.assertIn(b'You have logged out.', response.data)

if __name__ == '__main__':
    unittest.main()
