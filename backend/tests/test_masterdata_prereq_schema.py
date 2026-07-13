from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.countries.models import Country


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


def test_masterdata_models_expose_frozen_minimal_columns(tmp_path) -> None:
    db_path = tmp_path / "masterdata_prereq_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    for model, table_name in ((Applicant, "t_applicant"), (Country, "t_country")):
        expected_columns = {
            "id",
            "code",
            "name_cn",
            "name_en",
            "is_active",
        }
        if table_name == "t_applicant":
            expected_columns.add("applicant_type")
            expected_columns.add("total_power_of_attorney_no")
        assert model.__tablename__ == table_name
        assert set(model.__table__.columns.keys()) == expected_columns
        assert getattr(model.__table__.c.is_active.server_default.arg, "text", None) in {"1"}
        if table_name == "t_applicant":
            assert getattr(model.__table__.c.applicant_type.server_default.arg, "text", None) in {
                "'ENTITY'"
            }

    inspector = inspect(engine)
    assert "t_applicant" in inspector.get_table_names()
    assert "t_country" in inspector.get_table_names()

    for table_name in ("t_applicant", "t_country"):
        db_columns = {column["name"] for column in inspector.get_columns(table_name)}
        expected_columns = {"id", "code", "name_cn", "name_en", "is_active"}
        if table_name == "t_applicant":
            expected_columns.add("applicant_type")
            expected_columns.add("total_power_of_attorney_no")
        assert db_columns == expected_columns

        uniques = {
            tuple(constraint["column_names"])
            for constraint in inspector.get_unique_constraints(table_name)
        }
        assert ("code",) in uniques
        assert ("name_cn",) in uniques

    engine.dispose()


def test_masterdata_prereq_migration_creates_expected_schema(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "masterdata_prereq_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)

    assert {"t_applicant", "t_country"}.issubset(set(inspector.get_table_names()))

    for table_name in ("t_applicant", "t_country"):
        db_columns = {column["name"] for column in inspector.get_columns(table_name)}
        expected_columns = {"id", "code", "name_cn", "name_en", "is_active"}
        if table_name == "t_applicant":
            expected_columns.add("applicant_type")
            expected_columns.add("total_power_of_attorney_no")
        assert db_columns == expected_columns

        unique_sets = {
            tuple(constraint["column_names"])
            for constraint in inspector.get_unique_constraints(table_name)
        }
        assert ("code",) in unique_sets
        assert ("name_cn",) in unique_sets

    engine.dispose()
