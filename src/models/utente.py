# models/utente.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base



class Utente(Base):
    __tablename__ = 'utenti'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)

    # Back reference dalla relazione in Progetto
    progetti = relationship("Progetto", back_populates="responsabile")