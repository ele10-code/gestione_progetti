""" from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/GestioneProgetti"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 """
 
 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the base class for the ORM models
Base = declarative_base()

# Database connection URL
DATABASE_URL = "mysql+mysqlconnector://root:password@localhost/GestioneProgetti"

# Create the engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure Base is only defined once
Base = declarative_base()
