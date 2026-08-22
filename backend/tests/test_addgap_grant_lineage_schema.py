from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.modules.fees.models import T_GrantFeeTask

REVISION = "addgap_grant_lineage_01"
DOWN_REVISION = "addgap_workpkg_resolve_key_01"
TABLE = "t_grant_fee_task"

LINEAGE_COLUMNS = {
    "source_document_id": (36, True),
    "deadline_source": (32, True),
    "deadline_confirmed_at": (None, True),
    "superseded_by_task_id": (36, True),
    "supersede_reason": (None, True),
    "superseded_at": (None, True),
    "superseded_by": (36, True),
    "supersede_request_key": (64, True),
}


def _alembic_config(db_path: Path, monkeypatch) -> Config:
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def _insert_grant_task(connection, *, task_id: str, case_id: str) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE} (id, case_id, due_date, currency)
            VALUES (:task_id, :case_id, '2026-08-31', 'CNY')
            """
        ),
        {"task_id": task_id, "case_id": case_id},
    )


def test_grant_fee_task_model_declares_nullable_lineage_carriers_and_indexes() -> None:
    columns = T_GrantFeeTask.__table__.c

    for name, (length, nullable) in LINEAGE_COLUMNS.items():
        assert columns[name].nullable is nullable
        if length is not None:
            assert columns[name].type.length == length

    assert columns.source_document_id.foreign_keys
    assert columns.superseded_by_task_id.foreign_keys
    indexes = {
        index.name: (index.unique, tuple(column.name for column in index.columns))
        for index in T_GrantFeeTask.__table__.indexes
    }
    assert indexes["ux_t_grant_fee_task_source_document_id"] == (
        True,
        ("source_document_id",),
    )
    assert indexes["ux_t_grant_fee_task_supersede_request_key"] == (
        True,
        ("supersede_request_key",),
    )
    assert indexes["ix_t_grant_fee_task_superseded_by_task_id"] == (
        False,
        ("superseded_by_task_id",),
    )


def test_clean_sqlite_upgrade_adds_lineage_carriers_and_unique_indexes(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "grant_lineage_clean.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
        indexes = {index["name"]: index for index in inspector.get_indexes(TABLE)}
        foreign_keys = {
            tuple(item["constrained_columns"]): (
                item["referred_table"],
                tuple(item["referred_columns"]),
            )
            for item in inspector.get_foreign_keys(TABLE)
        }

        for name, (length, nullable) in LINEAGE_COLUMNS.items():
            assert columns[name]["nullable"] is nullable
            if length is not None:
                assert columns[name]["type"].length == length

        assert foreign_keys[("source_document_id",)] == ("t_document", ("id",))
        assert foreign_keys[("superseded_by_task_id",)] == (TABLE, ("id",))
        assert indexes["ux_t_grant_fee_task_source_document_id"]["unique"] == 1
        assert indexes["ux_t_grant_fee_task_source_document_id"]["column_names"] == [
            "source_document_id"
        ]
        assert indexes["ux_t_grant_fee_task_supersede_request_key"]["unique"] == 1
        assert indexes["ux_t_grant_fee_task_supersede_request_key"]["column_names"] == [
            "supersede_request_key"
        ]
        assert indexes["ix_t_grant_fee_task_superseded_by_task_id"]["unique"] == 0
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_incompatible_preexisting_lineage_schema_fails_before_mutation(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "grant_lineage_incompatible_preexisting.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            for column_name, sql_type in (
                ("source_document_id", "VARCHAR(36)"),
                ("deadline_source", "VARCHAR(32)"),
                ("deadline_confirmed_at", "DATETIME"),
                ("superseded_by_task_id", "VARCHAR(36)"),
                ("supersede_reason", "TEXT"),
                ("superseded_at", "DATETIME"),
                ("superseded_by", "VARCHAR(36)"),
                ("supersede_request_key", "VARCHAR(64)"),
            ):
                connection.execute(text(f"ALTER TABLE {TABLE} ADD COLUMN {column_name} {sql_type}"))

        inspector = inspect(engine)
        columns_before = {item["name"] for item in inspector.get_columns(TABLE)}
        indexes_before = {item["name"] for item in inspector.get_indexes(TABLE)}
        foreign_keys_before = {
            tuple(item["constrained_columns"]) for item in inspector.get_foreign_keys(TABLE)
        }

        with pytest.raises(RuntimeError, match="foreign key"):
            command.upgrade(config, "head")

        inspector = inspect(engine)
        assert {item["name"] for item in inspector.get_columns(TABLE)} == columns_before
        assert {item["name"] for item in inspector.get_indexes(TABLE)} == indexes_before
        assert {
            tuple(item["constrained_columns"]) for item in inspector.get_foreign_keys(TABLE)
        } == foreign_keys_before
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == DOWN_REVISION
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("source_document_id", "document-1"),
        ("supersede_request_key", "replacement-request-1"),
    ],
)
def test_lineage_unique_indexes_allow_legacy_nulls_but_reject_duplicate_values(
    tmp_path,
    monkeypatch,
    column,
    value,
) -> None:
    db_path = tmp_path / f"grant_lineage_unique_{column}.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            _insert_grant_task(connection, task_id="grant-legacy-1", case_id="case-1")
            _insert_grant_task(connection, task_id="grant-legacy-2", case_id="case-1")
            connection.execute(
                text(f"UPDATE {TABLE} SET {column} = :value WHERE id = 'grant-legacy-1'"),
                {"value": value},
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(f"UPDATE {TABLE} SET {column} = :value WHERE id = 'grant-legacy-2'"),
                    {"value": value},
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


@pytest.mark.parametrize(
    ("column", "sql_type", "value"),
    [
        ("source_document_id", "VARCHAR(36)", "document-duplicate"),
        ("source_document_id", "VARCHAR(36)", ""),
        ("supersede_request_key", "VARCHAR(64)", "request-duplicate"),
        ("supersede_request_key", "VARCHAR(64)", ""),
    ],
)
def test_duplicate_lineage_preflight_fails_before_remaining_schema_mutation(
    tmp_path,
    monkeypatch,
    column,
    sql_type,
    value,
) -> None:
    db_path = tmp_path / f"grant_lineage_duplicate_{column}.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, DOWN_REVISION)
        engine = create_engine(f"sqlite:///{db_path}", future=True)
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {TABLE} ADD COLUMN {column} {sql_type}"))
            _insert_grant_task(connection, task_id="grant-1", case_id="case-1")
            _insert_grant_task(connection, task_id="grant-2", case_id="case-1")
            connection.execute(
                text(f"UPDATE {TABLE} SET {column} = :value"),
                {"value": value},
            )

        with pytest.raises(RuntimeError, match=rf"{column}.*{value}"):
            command.upgrade(config, "head")

        assert "deadline_source" not in {
            item["name"] for item in inspect(engine).get_columns(TABLE)
        }
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == DOWN_REVISION
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_migration_is_explicitly_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "grant_lineage_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
