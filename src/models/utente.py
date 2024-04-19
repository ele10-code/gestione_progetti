from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class Utente(Base):
    __tablename__ = 'utenti'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)  # Aggiungi questa riga


    # Define the relationship to Progetto
    progetti = relationship('Progetto', back_populates='responsabile')
    tasks = relationship('Task', secondary='assegnazioni', back_populates='utenti')
