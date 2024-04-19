from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    descrizione = Column(String)
    id_progetto = Column(Integer, ForeignKey('progetti.id'))
    stato = Column(String)
    priorità = Column(String)
    utenti = relationship('Utente', secondary='assegnazioni', back_populates='tasks')
