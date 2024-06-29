class Assegnazione:
    def __init__(self, id_utente, id_task):
        self.id_utente = id_utente
        self.id_task = id_task

    def __repr__(self):
        return f"Assegnazione({self.id_utente}, {self.id_task})"
