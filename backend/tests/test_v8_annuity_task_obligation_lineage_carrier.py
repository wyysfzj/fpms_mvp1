from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
)
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.modules.annuity.models import AnnuityTask

REVISION = "v8_d4_annuity_lineage_01"
DOWN_REVISION = "v8_w5_pay_list_export_artifact_01"
TABLE_NAME = "t_annuity_task"
LINEAGE_COLUMNS = (
    "source_activity_id",
    "source_document_id",
    "source_evidence_version_id",
    "source_evidence_content_hash",
    "fee_obligation_id",
    "grant_fee_year_key",
)
FOREIGN_KEYS = {
    "fk_t_annuity_task_source_activity_id": (
        ("source_activity_id",),
        ("t_case_activity_event.id",),
        "RESTRICT",
    ),
    "fk_t_annuity_task_source_document_id": (
        ("source_document_id",),
        ("t_document.id",),
        "RESTRICT",
    ),
    "fk_t_annuity_task_source_evidence_version_id": (
        ("source_evidence_version_id",),
        ("t_document_evidence_version.id",),
        "RESTRICT",
    ),
    "fk_t_annuity_task_fee_obligation_id": (
        ("fee_obligation_id",),
        ("t_fee_obligation.id",),
        "RESTRICT",
    ),
}
TUPLE_CHECK = (
    "(source_activity_id IS NULL AND source_document_id IS NULL "
    "AND source_evidence_version_id IS NULL "
    "AND source_evidence_content_hash IS NULL "
    "AND fee_obligation_id IS NULL AND grant_fee_year_key IS NULL) "
    "OR (source_activity_id IS NOT NULL AND source_document_id IS NOT NULL "
    "AND source_evidence_version_id IS NOT NULL "
    "AND source_evidence_content_hash IS NOT NULL "
    "AND fee_obligation_id IS NOT NULL "
    "AND grant_fee_year_key IS NOT NULL AND grant_fee_year_key >= 1)"
)
HASH_CHECK = (
    "source_evidence_content_hash IS NULL OR "
    "(length(source_evidence_content_hash) = 71 "
    "AND substr(source_evidence_content_hash, 1, 7) = 'sha256:' "
    "AND substr(source_evidence_content_hash, 8) "
    "NOT GLOB '*[^0-9a-f]*')"
)


def _normalized(value: object) -> str:
    return " ".join(str(value).replace("\n", " ").split())


def _alembic_config(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def _sqlite_engine():
    engine = create_engine("sqlite://", future=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _carrier_engine():
    metadata = MetaData()
    for table_name in (
        "t_case",
        "t_client",
        "t_case_activity_event",
        "t_document",
        "t_document_evidence_version",
        "t_fee_obligation",
    ):
        Table(table_name, metadata, Column("id", String(36), primary_key=True))
    AnnuityTask.__table__.to_metadata(metadata)
    engine = _sqlite_engine()
    metadata.create_all(engine)
    with engine.begin() as connection:
        for table_name, row_id in (
            ("t_case", "case-1"),
            ("t_client", "client-1"),
            ("t_case_activity_event", "activity-1"),
            ("t_document", "document-1"),
            ("t_document_evidence_version", "evidence-1"),
            ("t_fee_obligation", "obligation-1"),
            ("t_fee_obligation", "obligation-2"),
            ("t_fee_obligation", "obligation-3"),
            ("t_fee_obligation", "obligation-4"),
            ("t_fee_obligation", "obligation-5"),
        ):
            connection.execute(metadata.tables[table_name].insert().values(id=row_id))
    return engine, metadata.tables[TABLE_NAME]


def _task_values(**overrides):
    values = {
        "case_id": "case-1",
        "client_id": "client-1",
        "year_no": 2,
        "due_date": date(2027, 8, 1),
    }
    values.update(overrides)
    return values


def _lineage(**overrides):
    values = {
        "source_activity_id": "activity-1",
        "source_document_id": "document-1",
        "source_evidence_version_id": "evidence-1",
        "source_evidence_content_hash": f"sha256:{'a' * 64}",
        "fee_obligation_id": "obligation-1",
        "grant_fee_year_key": 2,
    }
    values.update(overrides)
    return values


def test_frozen_model_contract() -> None:
    table = AnnuityTask.__table__
    assert (
        tuple(column.name for column in table.columns if column.name in LINEAGE_COLUMNS)
        == LINEAGE_COLUMNS
    )
    assert all(table.c[name].nullable for name in LINEAGE_COLUMNS)
    assert isinstance(table.c.source_evidence_content_hash.type, String)
    assert table.c.source_evidence_content_hash.type.length == 128
    assert isinstance(table.c.grant_fee_year_key.type, Integer)
    assert all(table.c[name].default is None for name in LINEAGE_COLUMNS)
    assert all(table.c[name].server_default is None for name in LINEAGE_COLUMNS)

    foreign_keys = {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint) and constraint.name in FOREIGN_KEYS
    }
    assert foreign_keys == FOREIGN_KEYS
    assert {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
        and constraint.name == "uq_t_annuity_task_fee_obligation_id"
    } == {"uq_t_annuity_task_fee_obligation_id": ("fee_obligation_id",)}
    checks = {
        constraint.name: _normalized(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
        and constraint.name
        in {
            "ck_t_annuity_task_lineage_tuple",
            "ck_t_annuity_task_source_evidence_hash",
        }
    }
    assert checks == {
        "ck_t_annuity_task_lineage_tuple": _normalized(TUPLE_CHECK),
        "ck_t_annuity_task_source_evidence_hash": _normalized(HASH_CHECK),
    }


def test_carrier_accepts_legacy_and_complete_rows_and_rejects_invalid_links() -> None:
    engine, table = _carrier_engine()
    with engine.begin() as connection:
        connection.execute(table.insert().values(**_task_values()))
        connection.execute(table.insert().values(**_task_values(**_lineage())))

    invalid_rows = (
        _lineage(source_document_id=None, fee_obligation_id="obligation-2"),
        _lineage(grant_fee_year_key=0, fee_obligation_id="obligation-3"),
        _lineage(
            source_evidence_content_hash=f"sha256:{'A' * 64}",
            fee_obligation_id="obligation-4",
        ),
        _lineage(source_activity_id="missing", fee_obligation_id="obligation-5"),
        _lineage(),
    )
    for lineage in invalid_rows:
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(table.insert().values(**_task_values(**lineage)))


def test_sqlite_migration_upgrade_and_reversible_downgrade(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _alembic_config(tmp_path / "annuity-lineage.db", monkeypatch)
    script = ScriptDirectory.from_config(config)
    revision = script.get_revision(REVISION)
    assert revision is not None
    assert revision.down_revision == DOWN_REVISION

    command.upgrade(config, REVISION)
    engine = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    inspector = inspect(engine)
    columns = {column["name"]: column for column in inspector.get_columns(TABLE_NAME)}
    assert set(LINEAGE_COLUMNS) <= columns.keys()
    assert all(columns[name]["nullable"] for name in LINEAGE_COLUMNS)
    assert {
        foreign_key["name"]: (
            tuple(foreign_key["constrained_columns"]),
            foreign_key["referred_table"],
            tuple(foreign_key["referred_columns"]),
            foreign_key["options"].get("ondelete"),
        )
        for foreign_key in inspector.get_foreign_keys(TABLE_NAME)
        if foreign_key["name"] in FOREIGN_KEYS
    } == {
        name: (columns_, target.split(".")[0], ("id",), ondelete)
        for name, (columns_, (target,), ondelete) in FOREIGN_KEYS.items()
    }
    assert any(
        constraint["name"] == "uq_t_annuity_task_fee_obligation_id"
        and tuple(constraint["column_names"]) == ("fee_obligation_id",)
        for constraint in inspector.get_unique_constraints(TABLE_NAME)
    )
    assert {
        constraint["name"]: _normalized(constraint["sqltext"])
        for constraint in inspector.get_check_constraints(TABLE_NAME)
        if constraint["name"]
        in {
            "ck_t_annuity_task_lineage_tuple",
            "ck_t_annuity_task_source_evidence_hash",
        }
    } == {
        "ck_t_annuity_task_lineage_tuple": _normalized(TUPLE_CHECK),
        "ck_t_annuity_task_source_evidence_hash": _normalized(HASH_CHECK),
    }

    engine.dispose()
    command.downgrade(config, DOWN_REVISION)
    downgraded = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    assert not set(LINEAGE_COLUMNS) & {
        column["name"] for column in inspect(downgraded).get_columns(TABLE_NAME)
    }
    downgraded.dispose()
