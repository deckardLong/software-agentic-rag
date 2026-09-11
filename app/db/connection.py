# Connect database (PostgreSQL)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import config

# Initialize engine
engine = create_engine(
    config.postgres.connection_string,
    pool_size=config.postgres.pool_size,
    max_overflow=config.postgres.max_overflow,
    pool_timeout=config.postgres.pool_timeout,
    pool_pre_ping=True  # self-check connection if it's available
) 

# Get database session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

@contextmanager
def get_db_session():
    """Start session"""
    session: Session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()