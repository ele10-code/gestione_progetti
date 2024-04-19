# models/progetto.py
from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.orm import relationship
from .database import Base

class Progetto(Base):
    __tablename__ = 'progetti'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_progetto = Column(String(255))
    id_responsabile = Column(Integer, ForeignKey('utenti.id'))
    scadenza = Column(DATETIME)

    # Relazione inversa con Utente
    responsabile = relationship("Utente", back_populates="progetti")

    def __repr__(self):
        return f"<Progetto(id={self.id}, nome_progetto={self.nome_progetto}, scadenza={self.scadenza})>"
