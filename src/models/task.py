# models/task.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    descrizione = Column(Text)
    id_progetto = Column(Integer, ForeignKey('progetti.id', ondelete='CASCADE'))
    stato = Column(String(100))
    priorita = Column(String(100))
    progetto = relationship('Progetto', back_populates='tasks')
    assegnazioni = relationship('Assegnazione', back_populates='task')
