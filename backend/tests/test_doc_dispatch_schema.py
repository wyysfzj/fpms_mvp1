from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.documents.models import DocDispatch, DocDispatchLine, Document


def _sqlite_engine(db_path: Path):
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

    return engine


def test_document_dispatch_models_expose_expected_columns(tmp_path) -> None:
    db_path = tmp_path / "doc_dispatch_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert "outgoing_reg_no" in Document.__table__.columns.keys()
    assert "forward_date" in Document.__table__.columns.keys()
    assert DocDispatch.__tablename__ == "t_doc_dispatch"
    assert DocDispatchLine.__tablename__ == "t_doc_dispatch_line"

    inspector = inspect(engine)
    assert "t_doc_dispatch" in inspector.get_table_names()
    assert "t_doc_dispatch_line" in inspector.get_table_names()

    document_columns = {column["name"] for column in inspector.get_columns("t_document")}
    assert "outgoing_reg_no" in document_columns
    assert "forward_date" in document_columns

    dispatch_columns = {column["name"] for column in inspector.get_columns("t_doc_dispatch")}
    assert {"id", "client_id", "dispatch_date", "remark"}.issubset(dispatch_columns)

    dispatch_line_columns = {
        column["name"] for column in inspector.get_columns("t_doc_dispatch_line")
    }
    assert {"id", "dispatch_id", "document_id", "case_id", "doc_name", "outgoing_reg_no"}.issubset(
        dispatch_line_columns
    )

    dispatch_line_fks = {
        (
            tuple(fk.get("constrained_columns") or []),
            fk.get("referred_table"),
            tuple(fk.get("referred_columns") or []),
        )
        for fk in inspector.get_foreign_keys("t_doc_dispatch_line")
    }
    assert (("dispatch_id",), "t_doc_dispatch", ("id",)) in dispatch_line_fks
    assert (("document_id",), "t_document", ("id",)) in dispatch_line_fks
    assert (("case_id",), "t_case", ("id",)) in dispatch_line_fks

    engine.dispose()


def test_documents_dispatch_migration_creates_expected_schema(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "doc_dispatch_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    document_columns = {column["name"] for column in inspector.get_columns("t_document")}
    assert "outgoing_reg_no" in document_columns
    assert "forward_date" in document_columns

    assert "t_doc_dispatch" in inspector.get_table_names()
    assert "t_doc_dispatch_line" in inspector.get_table_names()

    engine.dispose()
