class Progetto:
    def __init__(self, id_progetto, nome_progetto, id_responsabile, scadenza):
        self.id_progetto = id_progetto
        self.nome_progetto = nome_progetto
        self.id_responsabile = id_responsabile
        self.scadenza = scadenza

    def __repr__(self):
        return f"Progetto({self.id_progetto}, '{self.nome_progetto}', {self.id_responsabile}, '{self.scadenza}')"
