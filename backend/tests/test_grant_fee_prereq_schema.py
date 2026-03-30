from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.fees.models import T_GrantFeeTask


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


def _expected_columns() -> set[str]:
    return {
        "id",
        "case_id",
        "type",
        "due_date",
        "gov_fee_amt",
        "service_fee_amt",
        "currency",
        "client_instruction",
        "notify_count",
        "draft_generated",
        "notice_sent",
        "is_overdue",
        "remark",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }


def test_grant_fee_task_model_exposes_frozen_minimal_columns(tmp_path) -> None:
    db_path = tmp_path / "grant_fee_prereq_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert T_GrantFeeTask.__tablename__ == "t_grant_fee_task"
    assert set(T_GrantFeeTask.__table__.columns.keys()) == _expected_columns()

    columns = T_GrantFeeTask.__table__.columns
    assert getattr(columns["type"].server_default.arg, "text", None) == "'GRANT'"
    assert getattr(columns["client_instruction"].server_default.arg, "text", None) == "'NONE'"
    assert getattr(columns["gov_fee_amt"].server_default.arg, "text", None) == "0"
    assert getattr(columns["service_fee_amt"].server_default.arg, "text", None) == "0"
    assert getattr(columns["notify_count"].server_default.arg, "text", None) == "0"
    assert getattr(columns["draft_generated"].server_default.arg, "text", None) == "0"
    assert getattr(columns["notice_sent"].server_default.arg, "text", None) == "0"
    assert getattr(columns["is_overdue"].server_default.arg, "text", None) == "0"
    assert getattr(columns["created_at"].server_default.arg, "text", None) == "CURRENT_TIMESTAMP"
    assert getattr(columns["updated_at"].server_default.arg, "text", None) == "CURRENT_TIMESTAMP"

    inspector = inspect(engine)
    assert "t_grant_fee_task" in inspector.get_table_names()

    db_columns = {column["name"] for column in inspector.get_columns("t_grant_fee_task")}
    assert db_columns == _expected_columns()

    fk_specs = {
        (
            tuple(fk.get("constrained_columns") or []),
            fk.get("referred_table"),
            tuple(fk.get("referred_columns") or []),
        )
        for fk in inspector.get_foreign_keys("t_grant_fee_task")
    }
    assert (("case_id",), "t_case", ("id",)) in fk_specs

    engine.dispose()


def test_grant_fee_task_migration_creates_expected_schema(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "grant_fee_prereq_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    assert "t_grant_fee_task" in inspector.get_table_names()
    db_columns = {column["name"] for column in inspector.get_columns("t_grant_fee_task")}
    assert db_columns == _expected_columns()

    engine.dispose()
