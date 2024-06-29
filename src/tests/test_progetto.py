import unittest
from models.progetto import Progetto

class TestProgetto(unittest.TestCase):

    def setUp(self):
        self.progetto = Progetto(id=1, nome_progetto="Progetto Alpha", descrizione="Descrizione del progetto", id_responsabile=1)

    def test_project_attributes(self):
        self.assertEqual(self.progetto.id, 1)
        self.assertEqual(self.progetto.nome_progetto, "Progetto Alpha")
        self.assertEqual(self.progetto.descrizione, "Descrizione del progetto")
        self.assertEqual(self.progetto.id_responsabile, 1)

if __name__ == '__main__':
    unittest.main()
