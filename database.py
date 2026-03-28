"""
database.py
-----------
SQLAlchemy engine + session factory.

Like opening your Excel workbook — this file establishes the connection
so every other file can read/write to the database.

engine      = the connection to PostgreSQL (like opening the .xlsx file)
SessionLocal = a factory that creates individual sessions (like opening a sheet)
Base        = the parent class all models inherit from
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes.
    Opens a session, yields it, then closes — like a 'with' block.
    
    Usage in a route:
        @app.get("/something")
        def read_something(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
