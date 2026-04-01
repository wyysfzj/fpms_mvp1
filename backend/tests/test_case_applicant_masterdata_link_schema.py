from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.cases.models import T_CaseApplicant


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


def test_case_applicant_model_exposes_applicant_id_carrier(tmp_path) -> None:
    db_path = tmp_path / "case_applicant_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    applicant_columns = T_CaseApplicant.__table__.columns
    assert "applicant_id" in applicant_columns.keys()
    assert applicant_columns["applicant_id"].nullable is True
    assert applicant_columns["applicant_id"].index is True

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_case_applicant")}
    assert "applicant_id" in db_columns

    case_applicant_fks = {
        (
            tuple(fk.get("constrained_columns") or []),
            fk.get("referred_table"),
            tuple(fk.get("referred_columns") or []),
        )
        for fk in inspector.get_foreign_keys("t_case_applicant")
    }
    assert (("applicant_id",), "t_applicant", ("id",)) in case_applicant_fks

    case_applicant_indexes = {idx["name"] for idx in inspector.get_indexes("t_case_applicant")}
    assert "ix_t_case_applicant_applicant_id" in case_applicant_indexes

    engine.dispose()


def test_case_applicant_migration_creates_applicant_id_link(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_applicant_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    db_columns = {column["name"] for column in inspector.get_columns("t_case_applicant")}
    assert "applicant_id" in db_columns

    case_applicant_fks = {
        (
            tuple(fk.get("constrained_columns") or []),
            fk.get("referred_table"),
            tuple(fk.get("referred_columns") or []),
        )
        for fk in inspector.get_foreign_keys("t_case_applicant")
    }
    assert (("applicant_id",), "t_applicant", ("id",)) in case_applicant_fks

    case_applicant_indexes = {idx["name"] for idx in inspector.get_indexes("t_case_applicant")}
    assert "ix_t_case_applicant_applicant_id" in case_applicant_indexes

    engine.dispose()
