# models/task.py
from sqlalchemy import Column, Integer, String, ForeignKey, TEXT
from sqlalchemy.orm import relationship
from src.database.database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    descrizione = Column(TEXT)
    id_progetto = Column(Integer, ForeignKey('progetti.id'))
    stato = Column(String)
    priorità = Column(String)

    # Definizione del back reference
    progetto = relationship("Progetto", back_populates="tasks")