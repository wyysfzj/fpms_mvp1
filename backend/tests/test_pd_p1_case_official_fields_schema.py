from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.cases.models import T_CaseApplicant, T_CaseInventor
from app.modules.cases.schemas import CaseApplicantIn, CaseInventorIn

APPLICANT_OFFICIAL_COLUMNS = {
    "nationality",
    "certificate_type",
    "certificate_no",
    "official_postcode",
    "official_applicant_kind",
}
INVENTOR_OFFICIAL_COLUMNS = {"nationality", "china_id_no"}


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


def test_case_subtable_models_expose_official_field_carriers(tmp_path) -> None:
    db_path = tmp_path / "case_official_fields_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    applicant_columns = set(T_CaseApplicant.__table__.columns.keys())
    inventor_columns = set(T_CaseInventor.__table__.columns.keys())
    assert APPLICANT_OFFICIAL_COLUMNS <= applicant_columns
    assert INVENTOR_OFFICIAL_COLUMNS <= inventor_columns

    inspector = inspect(engine)
    db_applicant_columns = {column["name"] for column in inspector.get_columns("t_case_applicant")}
    db_inventor_columns = {column["name"] for column in inspector.get_columns("t_case_inventor")}
    assert APPLICANT_OFFICIAL_COLUMNS <= db_applicant_columns
    assert INVENTOR_OFFICIAL_COLUMNS <= db_inventor_columns

    engine.dispose()


def test_case_applicant_and_inventor_schemas_preserve_official_fields() -> None:
    applicant = CaseApplicantIn(
        seq=1,
        is_first=True,
        name_cn="测试申请人",
        nationality="CN",
        certificate_type="统一社会信用代码",
        certificate_no="91310000123456789X",
        official_postcode="200000",
        official_applicant_kind="ENTITY",
    )
    inventor = CaseInventorIn(
        seq=1,
        name_cn="测试发明人",
        nationality="CN",
        china_id_no="110101199001011234",
    )

    assert applicant.model_dump(include=APPLICANT_OFFICIAL_COLUMNS) == {
        "nationality": "CN",
        "certificate_type": "统一社会信用代码",
        "certificate_no": "91310000123456789X",
        "official_postcode": "200000",
        "official_applicant_kind": "ENTITY",
    }
    assert inventor.model_dump(include=INVENTOR_OFFICIAL_COLUMNS) == {
        "nationality": "CN",
        "china_id_no": "110101199001011234",
    }


def test_case_official_field_migration_creates_columns(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "case_official_fields_migration.db"
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
    db_applicant_columns = {column["name"] for column in inspector.get_columns("t_case_applicant")}
    db_inventor_columns = {column["name"] for column in inspector.get_columns("t_case_inventor")}

    assert APPLICANT_OFFICIAL_COLUMNS <= db_applicant_columns
    assert INVENTOR_OFFICIAL_COLUMNS <= db_inventor_columns

    engine.dispose()
