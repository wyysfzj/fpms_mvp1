from __future__ import annotations

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
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.annuity import models as annuity_models

REVISION = "v8_d27_annuity_reduction_01"
DOWN_REVISION = "v8_d4_evidence_kind_capacity_01"
CURRENT_HEAD = "v8_d31_overlay_conflict_01"
TABLE_NAME = "t_future_annuity_reduction_lineage"
COLUMNS = (
    "annuity_task_id",
    "fee_obligation_line_id",
    "reduction_input_provenance",
    "reduction_approval_id",
)
PK_NAME = "pk_t_future_annuity_reduction_lineage"
FOREIGN_KEYS = {
    "fk_t_future_annuity_reduction_lineage_annuity_task_id": (
        ("annuity_task_id",),
        ("t_annuity_task.id",),
        "RESTRICT",
    ),
    "fk_t_future_annuity_reduction_lineage_fee_obligation_line_id": (
        ("fee_obligation_line_id",),
        ("t_fee_obligation_line.id",),
        "RESTRICT",
    ),
    "fk_t_future_annuity_reduction_lineage_reduction_approval_id": (
        ("reduction_approval_id",),
        ("t_fee_reduction_approval.id",),
        "RESTRICT",
    ),
}
UNIQUE_CONSTRAINTS = {
    "uq_t_future_annuity_reduction_lineage_fee_obligation_line_id": (
        "fee_obligation_line_id",
    )
}
CHECKS = {
    "ck_t_future_annuity_reduction_lineage_provenance": (
        "reduction_input_provenance IN "
        "('EXPLICIT_ENTRY', 'CONFIRMED_MIGRATION')"
    ),
    "ck_t_future_annuity_reduction_lineage_approval_shape": (
        "reduction_input_provenance != 'CONFIRMED_MIGRATION' "
        "OR reduction_approval_id IS NOT NULL"
    ),
}
MODEL = getattr(annuity_models, "FutureAnnuityReductionLineage", None)


def _normalized_sql(value: object) -> str:
    return " ".join(str(value).replace("\n", " ").split())


def _sqlite_engine():
    engine = create_engine("sqlite://", future=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _carrier_engine():
    assert MODEL is not None
    metadata = MetaData()
    Table("t_annuity_task", metadata, Column("id", Integer, primary_key=True))
    Table(
        "t_fee_obligation_line",
        metadata,
        Column("id", String(36), primary_key=True),
    )
    Table(
        "t_fee_reduction_approval",
        metadata,
        Column("id", String(36), primary_key=True),
    )
    MODEL.__table__.to_metadata(metadata)
    engine = _sqlite_engine()
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            metadata.tables["t_annuity_task"].insert(),
            [{"id": 1}, {"id": 2}, {"id": 3}],
        )
        connection.execute(
            metadata.tables["t_fee_obligation_line"].insert(),
            [{"id": "line-1"}, {"id": "line-2"}, {"id": "line-3"}],
        )
        connection.execute(
            metadata.tables["t_fee_reduction_approval"].insert(),
            [{"id": "approval-1"}, {"id": "approval-2"}],
        )
    return engine, metadata.tables[TABLE_NAME]


def _values(**overrides):
    values = {
        "annuity_task_id": 1,
        "fee_obligation_line_id": "line-1",
        "reduction_input_provenance": "EXPLICIT_ENTRY",
        "reduction_approval_id": None,
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


def _alembic_config(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    backend = Path(__file__).resolve().parents[1]
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def test_model_matches_exact_four_column_append_only_contract() -> None:
    assert MODEL is not None
    table = MODEL.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert table.primary_key.name == PK_NAME
    assert tuple(table.primary_key.columns.keys()) == ("annuity_task_id",)
    assert isinstance(table.c.annuity_task_id.type, Integer)
    assert table.c.annuity_task_id.nullable is False
    for name in (
        "fee_obligation_line_id",
        "reduction_input_provenance",
        "reduction_approval_id",
    ):
        assert isinstance(table.c[name].type, String)
    assert table.c.fee_obligation_line_id.type.length == 36
    assert table.c.reduction_input_provenance.type.length == 32
    assert table.c.reduction_approval_id.type.length == 36
    assert table.c.fee_obligation_line_id.nullable is False
    assert table.c.reduction_input_provenance.nullable is False
    assert table.c.reduction_approval_id.nullable is True
    assert all(column.default is None for column in table.columns)
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
    } == CHECKS
    assert not MODEL.__mapper__.relationships
    assert not table.indexes


def test_clean_sqlite_head_has_exact_schema_and_single_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _alembic_config(tmp_path / "future-annuity-lineage.db", monkeypatch)
    engine = None
    try:
        script = ScriptDirectory.from_config(config)
        assert tuple(script.get_heads()) == (CURRENT_HEAD,)
        assert REVISION in {
            item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
        }
        revision = script.get_revision(REVISION)
        assert revision is not None
        assert revision.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = create_engine(config.get_main_option("sqlalchemy.url"), future=True)
        inspector = inspect(engine)
        columns = inspector.get_columns(TABLE_NAME)
        by_name = {column["name"]: column for column in columns}
        assert tuple(column["name"] for column in columns) == COLUMNS
        assert {name: column["nullable"] for name, column in by_name.items()} == {
            "annuity_task_id": False,
            "fee_obligation_line_id": False,
            "reduction_input_provenance": False,
            "reduction_approval_id": True,
        }
        assert inspector.get_pk_constraint(TABLE_NAME) == {
            "constrained_columns": ["annuity_task_id"],
            "name": PK_NAME,
        }
        assert {
            item["name"]: (
                tuple(item["constrained_columns"]),
                tuple(
                    f"{item['referred_table']}.{name}"
                    for name in item["referred_columns"]
                ),
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
        } == CHECKS
        assert inspector.get_indexes(TABLE_NAME) == []
        assert all(column["default"] is None for column in columns)
        with pytest.raises(NotImplementedError, match="forward-only"):
            revision.module.downgrade()
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_database_rejects_invalid_duplicate_and_restricted_lineage() -> None:
    engine, table = _carrier_engine()
    with engine.begin() as connection:
        connection.execute(table.insert().values(**_values()))

    for provenance in ("", "explicit_entry", "MIGRATION"):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    **_values(
                        annuity_task_id=2,
                        fee_obligation_line_id="line-2",
                        reduction_input_provenance=provenance,
                    )
                )
            )

    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            table.insert().values(
                **_values(
                    annuity_task_id=2,
                    fee_obligation_line_id="line-2",
                    reduction_input_provenance="CONFIRMED_MIGRATION",
                    reduction_approval_id=None,
                )
            )
        )
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            table.insert().values(
                **_values(annuity_task_id=1, fee_obligation_line_id="line-2")
            )
        )
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            table.insert().values(
                **_values(annuity_task_id=2, fee_obligation_line_id="line-1")
            )
        )

    with engine.begin() as connection:
        connection.execute(
            table.insert().values(
                **_values(
                    annuity_task_id=2,
                    fee_obligation_line_id="line-2",
                    reduction_input_provenance="CONFIRMED_MIGRATION",
                    reduction_approval_id="approval-1",
                )
            )
        )

    for referenced_table, column, value in (
        ("t_annuity_task", "id", 1),
        ("t_fee_obligation_line", "id", "line-1"),
        ("t_fee_reduction_approval", "id", "approval-1"),
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            reference = table.metadata.tables[referenced_table]
            connection.execute(reference.delete().where(reference.c[column] == value))
    engine.dispose()


def test_orm_rejects_update_and_delete_after_insert() -> None:
    assert MODEL is not None
    engine, _table = _carrier_engine()
    with Session(engine) as session:
        row = MODEL(**_values())
        session.add(row)
        session.commit()

    with Session(engine) as session:
        persisted = session.get(MODEL, 1)
        assert persisted is not None
        persisted.reduction_input_provenance = "CONFIRMED_MIGRATION"
        with pytest.raises(ValueError, match="immutable"):
            session.flush()
        session.rollback()

    with Session(engine) as session:
        persisted = session.get(MODEL, 1)
        assert persisted is not None
        session.delete(persisted)
        with pytest.raises(ValueError, match="immutable"):
            session.flush()
    engine.dispose()


def test_primary_key_constraint_is_named_in_model_metadata() -> None:
    assert MODEL is not None
    assert any(
        isinstance(constraint, PrimaryKeyConstraint)
        and constraint.name == PK_NAME
        for constraint in MODEL.__table__.constraints
    )
