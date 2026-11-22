from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

database_url = settings.DATABASE_URL

POSTGRES_POOL_CONFIG = {
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 1800,
}


def create_app_engine():
    target_url = settings.DATABASE_URL
    if target_url.startswith("sqlite"):
        return create_engine(
            target_url,
            connect_args={"check_same_thread": False},
            echo=False,
            future=True
        )

    try:
        # Try connecting with a 2-second timeout to check if PostgreSQL is available
        eng = create_engine(
            target_url,
            connect_args={"connect_timeout": 2},
            echo=False,
            future=True,
            **POSTGRES_POOL_CONFIG
        )
        with eng.connect() as conn:
            pass
        return eng
    except Exception as e:
        logger.warning(
            f"PostgreSQL at {target_url} is not currently reachable ({e}). "
            f"Falling back to local SQLite database: sqlite:///./honest_dev.db"
        )
        return create_engine(
            "sqlite:///./honest_dev.db",
            connect_args={"check_same_thread": False},
            echo=False,
            future=True
        )


engine = create_app_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection helper for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
