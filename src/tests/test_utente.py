import unittest
from models.utente import Utente

class TestUtente(unittest.TestCase):

    def setUp(self):
        self.utente = Utente(id=1, nome="Mario Rossi", email="mario.rossi@example.com", password_hash="hashed_password")

    def test_is_authenticated(self):
        self.assertTrue(self.utente.is_authenticated())

    def test_is_active(self):
        self.assertTrue(self.utente.is_active)

    def test_is_anonymous(self):
        self.assertFalse(self.utente.is_anonymous())

    def test_get_id(self):
        self.assertEqual(self.utente.get_id(), "1")

if __name__ == '__main__':
    unittest.main()
