from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# Define the base class for the ORM models
Base = declarative_base()

# Database connection URL
DATABASE_URL = "mysql+mysqlconnector://admin:password@localhost/GestioneProgetti"

# Create the engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(SessionLocal)

def get_db_session():
    """
    Return a new session from the SessionLocal factory
    """
    return SessionLocal()

def init_db(app):
    """
    Initialize the database with the application context.
    """
    Base.metadata.create_all(bind=engine)
    app.teardown_appcontext(close_db)

def close_db(exception=None):
    """
    Close the database session.
    """
    db.remove()

# Ensure Base is only defined once
Base = declarative_base()
