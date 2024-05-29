# models/assegnazione.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Assegnazione(Base):
    __tablename__ = 'assegnazioni'
    
    id_utente = Column(Integer, ForeignKey('utenti.id', ondelete='CASCADE'), primary_key=True)
    id_task = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    utente = relationship('Utente', back_populates='assegnazioni')
    task = relationship('Task', back_populates='assegnazioni')
