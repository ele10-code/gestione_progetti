# models/task.py
from sqlalchemy import Column, Integer, String, ForeignKey, TEXT
from sqlalchemy.orm import relationship
from .database import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    descrizione = Column(TEXT)
    id_progetto = Column(Integer, ForeignKey('progetti.id'))
    stato = Column(String(100))
    priorità = Column(String(100))

    # Relazione con Progetto
    progetto = relationship("Progetto", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, descrizione={self.descrizione}, stato={self.stato}, priorità={self.priorità})>"
