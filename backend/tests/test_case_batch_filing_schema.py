from __future__ import annotations

from sqlalchemy import create_engine, event, inspect

from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.cases.models import Case


def test_case_model_exposes_submitted_date_and_sqlite_column(tmp_path) -> None:
    db_path = tmp_path / "case_batch_filing.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    case_columns = Case.__table__.columns
    assert "submitted_date" in case_columns.keys()

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_case")}
    assert "submitted_date" in db_columns

    engine.dispose()
