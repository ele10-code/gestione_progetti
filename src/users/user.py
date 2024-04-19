class Utente:
    def __init__(self, id_utente, nome, email):
        self.id_utente = id_utente
        self.nome = nome
        self.email = email

    def __repr__(self):
        return f"Utente({self.id_utente}, '{self.nome}', '{self.email}')"
