from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Utente(Base):
    __tablename__ = 'utenti'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)  # Assicurati che questo campo sia definito nel database

    # Definizione delle relazioni con Progetto e Task
    progetti = relationship('Progetto', back_populates='responsabile')
    tasks = relationship('Task', secondary='assegnazioni', back_populates='utenti')

    # Flask-Login richiede i seguenti metodi

    def is_authenticated(self):
        # Di solito ritorna True se l'utente ha fornito credenziali valide
        return True

    @property  # Usa la decorazione @property per definire un getter per l'attributo is_active
    def is_active(self):
        # Qui, ritorna l'attributo is_active dell'istanza
        return self.is_active

    def is_anonymous(self):
        # Di solito ritorna False per utenti autenticati
        return False

    def get_id(self):
        # Deve ritornare un id univoco per l'utente come stringa
        return str(self.id)
