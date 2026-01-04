from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


def get_engine():
    settings = get_settings()
    url = settings.database_url
    connect_args = {}
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        connect_args = {"check_same_thread": False}
    engine = create_engine(url, echo=False, future=True, connect_args=connect_args)
    if is_sqlite:
        # Enforce foreign keys on every SQLite connection for PoC compatibility.
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
