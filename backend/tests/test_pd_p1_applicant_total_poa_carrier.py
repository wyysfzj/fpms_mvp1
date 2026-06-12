from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.masterdata.applicants.models import Applicant


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


def test_applicant_model_exposes_total_power_of_attorney_no(tmp_path) -> None:
    db_path = tmp_path / "applicant_total_poa_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    applicant_columns = Applicant.__table__.columns
    assert "total_power_of_attorney_no" in applicant_columns.keys()
    assert applicant_columns["total_power_of_attorney_no"].nullable is True

    assert "total_power_of_attorney_no" not in Case.__table__.columns.keys()
    assert "total_power_of_attorney_no" not in T_CaseApplicant.__table__.columns.keys()

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_applicant")}
    assert "total_power_of_attorney_no" in db_columns

    engine.dispose()


def test_applicant_total_poa_migration_creates_column(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "applicant_total_poa_migration.db"
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

    db_columns = {column["name"] for column in inspector.get_columns("t_applicant")}
    assert "total_power_of_attorney_no" in db_columns

    case_columns = {column["name"] for column in inspector.get_columns("t_case")}
    case_applicant_columns = {
        column["name"] for column in inspector.get_columns("t_case_applicant")
    }
    assert "total_power_of_attorney_no" not in case_columns
    assert "total_power_of_attorney_no" not in case_applicant_columns

    engine.dispose()
