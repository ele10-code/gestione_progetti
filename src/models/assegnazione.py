from sqlalchemy import Table, Column, Integer, ForeignKey
from database.database import Base

assegnazioni = Table('assegnazioni', Base.metadata,
    Column('id_utente', Integer, ForeignKey('utenti.id'), primary_key=True),
    Column('id_task', Integer, ForeignKey('tasks.id'), primary_key=True)
)
