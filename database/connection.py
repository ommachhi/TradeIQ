from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from .models import Base

# Database URL configuration
# For local development, we use SQLite. In production, use environment variables for PostgreSQL/MySQL.
DB_URL = os.getenv("DATABASE_URL", "sqlite:///tradeiq_saas.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
