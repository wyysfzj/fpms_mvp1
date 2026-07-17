from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.db.base import Base
from app.modules.cases import models as case_models

REVISION = "v8_w1_l2_case_activity_event_01"
DOWN_REVISION = "v8_w1_l1_case_lifecycle_01"
TABLE = "t_case_activity_event"

COLUMN_SPECS = {
    "id": (String, 36, False, None),
    "case_id": (String, 36, False, None),
    "sequence": (Integer, None, False, None),
    "lane": (String, 16, False, None),
    "activity_type": (String, 64, False, None),
    "source_activity_id": (String, 36, True, None),
    "occurred_at": (DateTime, None, True, None),
    "effective_at": (DateTime, None, False, None),
    "recorded_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "confirmation_status": (String, 32, False, None),
    "old_business_stage": (String, 32, True, None),
    "new_business_stage": (String, 32, True, None),
    "old_official_procedure_stage": (String, 64, True, None),
    "new_official_procedure_stage": (String, 64, True, None),
    "old_legal_status": (String, 32, True, None),
    "new_legal_status": (String, 32, True, None),
    "actor_id": (String, 36, False, None),
    "reviewer_id": (String, 36, True, None),
    "idempotency_key": (String, 128, False, None),
    "supersedes_event_id": (String, 36, True, None),
    "payload_json": (Text, None, False, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

UNIQUE_SPECS = {
    "uq_t_case_activity_event_case_sequence": ("case_id", "sequence"),
    "uq_t_case_activity_event_case_idempotency_key": (
        "case_id",
        "idempotency_key",
    ),
    "uq_t_case_activity_event_case_id": ("case_id", "id"),
}


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


def _insert_case(connection, *, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_case (id, case_no) VALUES (:id, :case_no)"),
        {"id": case_id, "case_no": case_id},
    )


def _insert_activity(
    connection,
    *,
    activity_id: str,
    case_id: str,
    sequence: int,
    idempotency_key: str,
    source_activity_id: str | None = None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, case_id, sequence, lane, activity_type, source_activity_id,
                 effective_at, confirmation_status, actor_id, idempotency_key,
                 payload_json)
            VALUES
                (:id, :case_id, :sequence, 'LIFECYCLE', 'CASE_OPENED',
                 :source_activity_id, :effective_at, 'CONFIRMED', 'actor-1',
                 :idempotency_key, '{{}}')
            """
        ),
        {
            "id": activity_id,
            "case_id": case_id,
            "sequence": sequence,
            "source_activity_id": source_activity_id,
            "effective_at": datetime(2026, 7, 13, 10, 0, 0),
            "idempotency_key": idempotency_key,
        },
    )


def test_case_activity_event_model_matches_frozen_physical_contract(tmp_path) -> None:
    model = getattr(case_models, "CaseActivityEvent", None)
    assert model is not None
    assert model.__tablename__ == TABLE
    assert set(model.__table__.columns.keys()) == set(COLUMN_SPECS)

    columns = model.__table__.c
    for name, (expected_type, length, nullable, server_default) in COLUMN_SPECS.items():
        column = columns[name]
        assert isinstance(column.type, expected_type)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert getattr(column.server_default, "arg", None) is None or (
            getattr(column.server_default.arg, "text", None) == server_default
        )
        if server_default is None:
            assert column.server_default is None

    assert columns.id.default is not None
    assert columns.supersedes_event_id.foreign_keys == set()

    unique_specs = {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert unique_specs == UNIQUE_SPECS

    foreign_key_specs = {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in model.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert foreign_key_specs == {
        "fk_t_case_activity_event_case_id": (
            ("case_id",),
            ("t_case.id",),
            "CASCADE",
        ),
        "fk_t_case_activity_event_source_same_case": (
            ("case_id", "source_activity_id"),
            (f"{TABLE}.case_id", f"{TABLE}.id"),
            None,
        ),
    }
    assert not any(
        isinstance(constraint, CheckConstraint) for constraint in model.__table__.constraints
    )
    assert not model.__table__.indexes

    engine = _sqlite_engine(tmp_path / "v8_w1_l2_model.db")
    try:
        Base.metadata.create_all(engine)
        assert TABLE in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_clean_sqlite_upgrade_creates_exact_event_schema(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_l2_migration.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)
        columns = {column["name"]: column for column in inspector.get_columns(TABLE)}
        assert set(columns) == set(COLUMN_SPECS)

        for name, (expected_type, length, nullable, server_default) in COLUMN_SPECS.items():
            column = columns[name]
            assert isinstance(column["type"], expected_type)
            assert getattr(column["type"], "length", None) == length
            assert column["nullable"] is nullable
            assert column["default"] == server_default

        assert tuple(inspector.get_pk_constraint(TABLE)["constrained_columns"]) == ("id",)
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == UNIQUE_SPECS
        assert {
            item["name"]: (
                tuple(item["constrained_columns"]),
                item["referred_table"],
                tuple(item["referred_columns"]),
                item.get("options", {}).get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        } == {
            "fk_t_case_activity_event_case_id": (
                ("case_id",),
                "t_case",
                ("id",),
                "CASCADE",
            ),
            "fk_t_case_activity_event_source_same_case": (
                ("case_id", "source_activity_id"),
                TABLE,
                ("case_id", "id"),
                None,
            ),
        }
        assert inspector.get_indexes(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_source_activity_fk_accepts_null_and_same_case_but_rejects_invalid_sources(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_l2_source_fk.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-a")
            _insert_case(connection, case_id="case-b")
            _insert_activity(
                connection,
                activity_id="activity-a-1",
                case_id="case-a",
                sequence=1,
                idempotency_key="case-a-1",
            )
            _insert_activity(
                connection,
                activity_id="activity-b-1",
                case_id="case-b",
                sequence=1,
                idempotency_key="case-b-1",
            )
            _insert_activity(
                connection,
                activity_id="activity-a-null",
                case_id="case-a",
                sequence=2,
                idempotency_key="case-a-null",
            )
            _insert_activity(
                connection,
                activity_id="activity-a-child",
                case_id="case-a",
                sequence=3,
                idempotency_key="case-a-child",
                source_activity_id="activity-a-1",
            )

        for source_activity_id, sequence, idempotency_key in (
            ("missing-activity", 4, "case-a-missing"),
            ("activity-b-1", 5, "case-a-cross-case"),
        ):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_activity(
                        connection,
                        activity_id=f"rejected-{sequence}",
                        case_id="case-a",
                        sequence=sequence,
                        idempotency_key=idempotency_key,
                        source_activity_id=source_activity_id,
                    )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_sequence_and_idempotency_are_unique_per_case(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_l2_uniqueness.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-a")
            _insert_case(connection, case_id="case-b")
            _insert_activity(
                connection,
                activity_id="activity-a-1",
                case_id="case-a",
                sequence=1,
                idempotency_key="shared-key",
            )
            _insert_activity(
                connection,
                activity_id="activity-b-1",
                case_id="case-b",
                sequence=1,
                idempotency_key="shared-key",
            )

        for activity_id, sequence, idempotency_key in (
            ("duplicate-sequence", 1, "different-key"),
            ("duplicate-key", 2, "shared-key"),
        ):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_activity(
                        connection,
                        activity_id=activity_id,
                        case_id="case-a",
                        sequence=sequence,
                        idempotency_key=idempotency_key,
                    )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_case_activity_event_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_l2_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
