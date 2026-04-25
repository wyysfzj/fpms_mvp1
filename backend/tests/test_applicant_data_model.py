from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect, select

from app.core.config import get_settings
from app.db.base import Base
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


def test_applicant_model_exposes_applicant_type_with_entity_default(tmp_path) -> None:
    db_path = tmp_path / "applicant_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert set(Applicant.__table__.columns.keys()) == {
        "id",
        "code",
        "name_cn",
        "name_en",
        "is_active",
        "applicant_type",
    }
    assert getattr(Applicant.__table__.c.applicant_type.server_default.arg, "text", None) in {
        "'ENTITY'"
    }

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_applicant")}
    assert db_columns == {
        "id",
        "code",
        "name_cn",
        "name_en",
        "is_active",
        "applicant_type",
    }

    engine.dispose()


def test_seed_masterdata_applicants_populates_applicant_type_values(session_factory) -> None:
    import scripts.seed_dev as seed_dev

    with session_factory() as db:
        seed_dev.seed_masterdata_applicants(db)
        seed_dev.seed_masterdata_applicants(db)

        applicants = {
            applicant.code: applicant
            for applicant in db.execute(
                select(Applicant).where(Applicant.code.in_(["DS-AP-001", "DS-AP-002"]))
            ).scalars()
        }

    assert applicants["DS-AP-001"].applicant_type == "ENTITY"
    assert applicants["DS-AP-002"].applicant_type == "INDIVIDUAL"


def test_masterdata_prereq_migration_creates_applicant_type_column(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "applicant_model_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    db_columns = {column["name"] for column in inspector.get_columns("t_applicant")}
    assert db_columns == {
        "id",
        "code",
        "name_cn",
        "name_en",
        "is_active",
        "applicant_type",
    }

    engine.dispose()
