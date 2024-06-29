# models/utente.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Utente(Base):
    __tablename__ = 'utenti'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    _is_active = Column(Boolean, default=True)
    assegnazioni = relationship('Assegnazione', back_populates='utente')
    progetti = relationship('Progetto', back_populates='responsabile')

    def __init__(self, id=None, nome=None, email=None, password_hash=None, _is_active=True):
        self.id = id
        self.nome = nome
        self.email = email
        self.password_hash = password_hash
        self._is_active = _is_active

    # Flask-Login richiede i seguenti metodi

    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self._is_active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
