""" class Utente:
    def __init__(self, id_utente, nome, email):
        self.id_utente = id_utente
        self.nome = nome
        self.email = email

    def __repr__(self):
        return f"Utente({self.id_utente}, '{self.nome}', '{self.email}')"
 """

from sqlalchemy import Column, Integer, String
from .database import Base

class Utente(Base):
    __tablename__ = 'utenti'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String)
    # altri campi come necessario
