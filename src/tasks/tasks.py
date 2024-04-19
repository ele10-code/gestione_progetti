class Task:
    def __init__(self, id_task, descrizione, id_progetto, stato, priorità):
        self.id_task = id_task
        self.descrizione = descrizione
        self.id_progetto = id_progetto
        self.stato = stato
        self.priorità = priorità

    def __repr__(self):
        return f"Task({self.id_task}, '{self.descrizione}', {self.id_progetto}, '{self.stato}', '{self.priorità}')"
