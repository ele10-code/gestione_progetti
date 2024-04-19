from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.orm import relationship
from database.database import Base

class Progetto(Base):
    __tablename__ = 'progetti'
    id = Column(Integer, primary_key=True)
    nome_progetto = Column(String)
    id_responsabile = Column(Integer, ForeignKey('utenti.id'))
    scadenza = Column(DATETIME)
    # Define the relationship back to Utente
    responsabile = relationship('Utente', back_populates='progetti')
