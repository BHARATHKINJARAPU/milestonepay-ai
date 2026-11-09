import os
import sys
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure psycopg uses the python implementation and libpq path on Windows
if sys.platform == "win32":
    os.environ.setdefault("PSYCOPG_IMPL", "python")
    libpq_path = r"C:\Users\kinja\AppData\Local\Temp\pgsql_portable\pgsql\bin"
    if os.path.exists(libpq_path) and libpq_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = libpq_path + os.pathsep + os.environ.get("PATH", "")

from app.core.config import settings

# Ensure database URL is compatible with SQLAlchemy by replacing postgres prefix with postgresql
database_url = settings.DATABASE_URL
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Initialize SQLAlchemy synchronous engine with connection pre-ping
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=10,
    echo=False,
)

# Configure session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session and ensures proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

