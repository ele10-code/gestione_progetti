# models/progetto.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base

class Progetto(Base):
    __tablename__ = 'progetti'
    
    id = Column(Integer, primary_key=True, index=True)
    nome_progetto = Column(String(255), nullable=False)
    descrizione = Column(String(255))  
    id_responsabile = Column(Integer, ForeignKey('utenti.id'))
    scadenza = Column(DateTime)
    responsabile = relationship('Utente', back_populates='progetti')
    tasks = relationship('Task', back_populates='progetto')
