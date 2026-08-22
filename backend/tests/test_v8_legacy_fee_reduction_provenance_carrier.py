from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
)
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.fees import models as fee_models

REVISION = "v8_d4_legacy_fee_provenance_01"
DOWN_REVISION = "v8_d4_annuity_lineage_01"
TABLE_NAME = "t_legacy_fee_reduction_provenance"
COLUMNS = (
    "id",
    "case_id",
    "legacy_value",
    "source_reference",
    "source_version",
    "source_snapshot_hash",
    "manifest_hash",
    "confirmed_by",
    "confirmed_at",
    "approval_id",
)
STRING_LENGTHS = {
    "id": 36,
    "case_id": 36,
    "source_snapshot_hash": 64,
    "manifest_hash": 64,
    "confirmed_by": 36,
    "approval_id": 36,
}
NULLABILITY = {name: name == "approval_id" for name in COLUMNS}
FOREIGN_KEYS = {
    "fk_t_legacy_fee_reduction_provenance_case_id": (
        ("case_id",),
        ("t_case.id",),
        "RESTRICT",
    ),
    "fk_t_legacy_fee_reduction_provenance_confirmed_by": (
        ("confirmed_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_legacy_fee_reduction_provenance_approval_id": (
        ("approval_id",),
        ("t_fee_reduction_approval.id",),
        "RESTRICT",
    ),
}
UNIQUE_CONSTRAINTS = {
    "uq_t_legacy_fee_reduction_provenance_case_manifest": (
        "case_id",
        "manifest_hash",
    ),
}
LEGACY_VALUE_CHECK = (
    "typeof(legacy_value) = 'text' AND legacy_value IN ('0', '0.7', '0.85')"
)
APPROVAL_CHECK = (
    "(legacy_value = '0' AND approval_id IS NULL) OR "
    "(legacy_value IN ('0.7', '0.85') AND approval_id IS NOT NULL)"
)
PROHIBITED_COLUMNS = {
    "fee_schedule_item_id",
    "source_system",
    "source_record_id",
    "payload",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
}


def _normalized_sql(value: object) -> str:
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
    for table_name in ("t_case", "t_user", "t_fee_reduction_approval"):
        Table(table_name, metadata, Column("id", String(36), primary_key=True))
    fee_models.LegacyFeeReductionProvenance.__table__.to_metadata(metadata)
    engine = _sqlite_engine()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(metadata.tables["t_case"].insert().values(id="case-1"))
        connection.execute(metadata.tables["t_case"].insert().values(id="case-2"))
        connection.execute(metadata.tables["t_user"].insert().values(id="user-1"))
        connection.execute(metadata.tables["t_user"].insert().values(id="user-2"))
        connection.execute(
            metadata.tables["t_fee_reduction_approval"].insert().values(id="approval-1")
        )
        connection.execute(
            metadata.tables["t_fee_reduction_approval"].insert().values(id="approval-2")
        )
    return engine, metadata.tables[TABLE_NAME]


def _values(**overrides):
    values = {
        "id": "carrier-1",
        "case_id": "case-1",
        "legacy_value": "0.7",
        "source_reference": "legacy-workbook/fee-reduction",
        "source_version": "2026-06-26",
        "source_snapshot_hash": "s" * 64,
        "manifest_hash": "m" * 64,
        "confirmed_by": "user-1",
        "confirmed_at": datetime(2026, 7, 15, 9, 30, 0),
        "approval_id": "approval-1",
    }
    values.update(overrides)
    return values


def _model_foreign_keys(table):
    return {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }


def test_model_matches_exact_append_only_frozen_contract() -> None:
    model = fee_models.LegacyFeeReductionProvenance
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert PROHIBITED_COLUMNS.isdisjoint(table.columns.keys())
    assert not model.__mapper__.relationships
    assert {column.name: column.nullable for column in table.columns} == NULLABILITY
    assert tuple(table.primary_key.columns.keys()) == ("id",)

    for name, length in STRING_LENGTHS.items():
        assert isinstance(table.c[name].type, String)
        assert table.c[name].type.length == length
    for name in ("legacy_value", "source_reference", "source_version"):
        assert isinstance(table.c[name].type, String)
    assert table.c.legacy_value.type.compile(dialect=sqlite_dialect()) == "BLOB"
    assert isinstance(table.c.confirmed_at.type, DateTime)
    assert table.c.confirmed_at.type.timezone is False

    assert table.c.id.default is not None
    assert table.c.id.server_default is None
    assert all(column.default is None for column in table.columns if column.name != "id")
    assert all(column.server_default is None for column in table.columns)
    assert _model_foreign_keys(table) == FOREIGN_KEYS
    assert {
        constraint.name: tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    } == UNIQUE_CONSTRAINTS
    assert {
        constraint.name: _normalized_sql(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } == {
        "ck_t_legacy_fee_reduction_provenance_legacy_value": LEGACY_VALUE_CHECK,
        "ck_t_legacy_fee_reduction_provenance_approval": APPROVAL_CHECK,
    }
    assert not table.indexes


def test_parent_to_child_migration_has_exact_sqlite_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _alembic_config(tmp_path / "legacy-fee-provenance.db", monkeypatch)
    script = ScriptDirectory.from_config(config)
    revision = script.get_revision(REVISION)
    assert revision is not None
    assert revision.down_revision == DOWN_REVISION

    command.upgrade(config, REVISION)
    engine = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
    inspector = inspect(engine)
    columns = inspector.get_columns(TABLE_NAME)
    by_name = {column["name"]: column for column in columns}

    assert tuple(column["name"] for column in columns) == COLUMNS
    assert {name: column["nullable"] for name, column in by_name.items()} == NULLABILITY
    assert inspector.get_pk_constraint(TABLE_NAME)["constrained_columns"] == ["id"]
    assert all(column["default"] is None for column in columns)
    for name, length in STRING_LENGTHS.items():
        assert isinstance(by_name[name]["type"], String)
        assert by_name[name]["type"].length == length
    assert by_name["legacy_value"]["type"].compile(dialect=engine.dialect) == "BLOB"
    assert isinstance(by_name["confirmed_at"]["type"], DateTime)
    assert {
        item["name"]: (
            tuple(item["constrained_columns"]),
            tuple(f"{item['referred_table']}.{name}" for name in item["referred_columns"]),
            item.get("options", {}).get("ondelete"),
        )
        for item in inspector.get_foreign_keys(TABLE_NAME)
    } == FOREIGN_KEYS
    assert {
        item["name"]: tuple(item["column_names"])
        for item in inspector.get_unique_constraints(TABLE_NAME)
    } == UNIQUE_CONSTRAINTS
    assert {
        item["name"]: _normalized_sql(item["sqltext"])
        for item in inspector.get_check_constraints(TABLE_NAME)
    } == {
        "ck_t_legacy_fee_reduction_provenance_legacy_value": LEGACY_VALUE_CHECK,
        "ck_t_legacy_fee_reduction_provenance_approval": APPROVAL_CHECK,
    }
    assert inspector.get_indexes(TABLE_NAME) == []
    engine.dispose()
    get_settings.cache_clear()


def test_database_enforces_grammar_approval_identity_and_restricted_references() -> None:
    engine, table = _carrier_engine()
    with engine.begin() as connection:
        connection.execute(table.insert().values(**_values()))
        connection.execute(
            table.insert().values(
                **_values(
                    id="carrier-zero",
                    case_id="case-2",
                    legacy_value="0",
                    manifest_hash="z" * 64,
                    confirmed_by="user-2",
                    approval_id=None,
                )
            )
        )
        connection.execute(
            table.insert().values(
                **_values(
                    id="carrier-eighty-five",
                    case_id="case-2",
                    legacy_value="0.85",
                    manifest_hash="e" * 64,
                    confirmed_by="user-2",
                    approval_id="approval-2",
                )
            )
        )

    for index, legacy_value in enumerate(
        ("70%", "85%", "0.70", ".7", "+0.7", "-0.7", " 0.7", "0.7 "),
        1,
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    **_values(
                        id=f"carrier-invalid-value-{index}",
                        manifest_hash=f"{index:064x}",
                        legacy_value=legacy_value,
                    )
                )
            )

    for index, (legacy_value, approval_id) in enumerate(
        ((0, None), (0.7, "approval-1"), (0.85, "approval-1")),
        10,
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    **_values(
                        id=f"carrier-raw-numeric-{index}",
                        manifest_hash=f"{index:064x}",
                        legacy_value=legacy_value,
                        approval_id=approval_id,
                    )
                )
            )

    invalid_approval_pairs = (
        ("0", "approval-1"),
        ("0.7", None),
        ("0.85", None),
    )
    for index, (legacy_value, approval_id) in enumerate(invalid_approval_pairs, 20):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    **_values(
                        id=f"carrier-invalid-approval-{index}",
                        manifest_hash=f"{index:064x}",
                        legacy_value=legacy_value,
                        approval_id=approval_id,
                    )
                )
            )

    required_field_overrides = (
        {"source_reference": None},
        {"source_version": None},
        {"source_snapshot_hash": None},
        {"confirmed_by": None},
        {"confirmed_at": None},
    )
    for index, override in enumerate(required_field_overrides, 30):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    **_values(
                        id=f"carrier-missing-confirmation-{index}",
                        manifest_hash=f"{index:064x}",
                        **override,
                    )
                )
            )

    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            table.insert().values(
                **_values(id="carrier-duplicate", source_reference="different-source")
            )
        )

    for referenced_table, referenced_id in (
        ("t_case", "case-1"),
        ("t_user", "user-1"),
        ("t_fee_reduction_approval", "approval-1"),
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.metadata.tables[referenced_table]
                .delete()
                .where(table.metadata.tables[referenced_table].c.id == referenced_id)
            )


def test_orm_generates_uuid_and_rejects_coercion_timezone_update_and_delete() -> None:
    model = fee_models.LegacyFeeReductionProvenance
    engine, _table = _carrier_engine()
    insert_parameters: list[object] = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture_insert(_conn, _cursor, statement, parameters, _context, _executemany) -> None:
        if statement.lstrip().startswith(f"INSERT INTO {TABLE_NAME}"):
            insert_parameters.append(parameters)

    row_values = _values(id=None)
    row_values.pop("id")
    row = model(**row_values)
    assert row.id is None
    with Session(engine) as session:
        session.add(row)
        session.flush()
        assert UUID(row.id)
        assert insert_parameters
        assert row.id in repr(insert_parameters[-1])
        assert row.confirmed_at.tzinfo is None
        persisted_id = row.id
        session.commit()

    for invalid_value in (0, 0.7, 0.85, "70%", "0.70", "+0.7", " 0.7", "0.7 "):
        with pytest.raises((TypeError, ValueError)):
            model(**{**row_values, "legacy_value": invalid_value})
    with pytest.raises((TypeError, ValueError)):
        model(
            **{
                **row_values,
                "confirmed_at": datetime(2026, 7, 15, 9, 30, tzinfo=timezone.utc),
            }
        )

    with Session(engine) as session:
        persisted = session.get(model, persisted_id)
        assert persisted is not None
        assert type(persisted.legacy_value) is str
        assert persisted.legacy_value == "0.7"
        persisted.source_reference = "changed-source"
        with pytest.raises(ValueError, match="immutable"):
            session.flush()
        session.rollback()

    with Session(engine) as session:
        persisted = session.get(model, persisted_id)
        assert persisted is not None
        session.delete(persisted)
        with pytest.raises(ValueError, match="immutable"):
            session.flush()
