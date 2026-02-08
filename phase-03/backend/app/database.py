"""
Database connection module.
Manages PostgreSQL connection using SQLModel.
"""

from sqlmodel import create_engine, Session
from app.config import DATABASE_URL

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size (increased for Phase-3 chat workload)
    max_overflow=20,  # Maximum overflow connections (increased for concurrent requests)
)


def get_session():
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    with Session(engine) as session:
        yield session
