# models/utente.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base



class Utente(Base):
    __tablename__ = 'utenti'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255))
    email = Column(String(255), unique=True)

    # Se hai relazioni da implementare, puoi decommentare e usare la seguente linea
    # progetti = relationship("Progetto", back_populates="responsabile")

    def __repr__(self):
        return f"<Utente(id={self.id}, nome={self.nome}, email={self.email})>"

