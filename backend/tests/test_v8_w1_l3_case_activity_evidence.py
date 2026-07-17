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
    String,
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

REVISION = "v8_w1_l3_activity_evidence_01"
DOWN_REVISION = "v8_w1_l2_case_activity_event_01"
TABLE = "t_case_activity_event_evidence"

COLUMN_SPECS = {
    "id": (String, 36, False, None),
    "case_id": (String, 36, False, None),
    "activity_id": (String, 36, False, None),
    "evidence_kind": (String, 32, False, None),
    "object_type": (String, 64, False, None),
    "object_id": (String, 36, False, None),
    "content_hash": (String, 128, False, None),
    "captured_at": (DateTime, None, False, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

UNIQUE_SPECS = {
    "uq_t_case_activity_event_evidence_link": (
        "case_id",
        "activity_id",
        "evidence_kind",
        "object_type",
        "object_id",
    )
}

FOREIGN_KEY_SPECS = {
    "fk_t_case_activity_event_evidence_activity_same_case": (
        ("case_id", "activity_id"),
        "t_case_activity_event",
        ("case_id", "id"),
        None,
    )
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
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_case_activity_event
                (id, case_id, sequence, lane, activity_type, effective_at,
                 confirmation_status, actor_id, idempotency_key, payload_json)
            VALUES
                (:id, :case_id, :sequence, 'DOCUMENT', 'EVIDENCE_CAPTURED',
                 :effective_at, 'CONFIRMED', 'actor-1', :idempotency_key, '{}')
            """
        ),
        {
            "id": activity_id,
            "case_id": case_id,
            "sequence": sequence,
            "effective_at": datetime(2026, 7, 13, 11, 0, 0),
            "idempotency_key": f"{case_id}-{sequence}",
        },
    )


def _insert_evidence(
    connection,
    *,
    evidence_id: str,
    case_id: str,
    activity_id: str,
    evidence_kind: str = "DOCUMENT",
    object_type: str = "Document",
    object_id: str = "document-1",
    content_hash: str = "sha256:abc",
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, case_id, activity_id, evidence_kind, object_type,
                 object_id, content_hash, captured_at)
            VALUES
                (:id, :case_id, :activity_id, :evidence_kind, :object_type,
                 :object_id, :content_hash, :captured_at)
            """
        ),
        {
            "id": evidence_id,
            "case_id": case_id,
            "activity_id": activity_id,
            "evidence_kind": evidence_kind,
            "object_type": object_type,
            "object_id": object_id,
            "content_hash": content_hash,
            "captured_at": datetime(2026, 7, 13, 11, 1, 0),
        },
    )


def test_activity_evidence_model_matches_frozen_physical_contract(tmp_path) -> None:
    model = getattr(case_models, "CaseActivityEventEvidence", None)
    assert model is not None
    assert model.__tablename__ == TABLE
    assert set(model.__table__.columns.keys()) == set(COLUMN_SPECS)

    columns = model.__table__.c
    for name, (expected_type, length, nullable, server_default) in COLUMN_SPECS.items():
        column = columns[name]
        assert isinstance(column.type, expected_type)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert getattr(column.type, "timezone", False) is False
        if server_default is None:
            assert column.server_default is None
        else:
            assert column.server_default is not None
            assert getattr(column.server_default.arg, "text", None) == server_default

    assert columns.id.default is not None
    assert columns.object_id.foreign_keys == set()

    unique_specs = {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in model.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert unique_specs == UNIQUE_SPECS

    foreign_key_specs = {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            constraint.referred_table.name,
            tuple(element.column.name for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in model.__table__.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert foreign_key_specs == FOREIGN_KEY_SPECS
    assert not any(
        isinstance(constraint, CheckConstraint) for constraint in model.__table__.constraints
    )
    assert not model.__table__.indexes

    engine = _sqlite_engine(tmp_path / "v8_w1_l3_model.db")
    try:
        Base.metadata.create_all(engine)
        assert TABLE in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_clean_sqlite_upgrade_creates_exact_activity_evidence_schema(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_l3_migration.db"
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
        } == FOREIGN_KEY_SPECS
        assert inspector.get_indexes(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_activity_fk_accepts_same_case_and_rejects_missing_or_cross_case(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_l3_activity_fk.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-a")
            _insert_case(connection, case_id="case-b")
            _insert_activity(connection, activity_id="activity-a", case_id="case-a", sequence=1)
            _insert_activity(connection, activity_id="activity-b", case_id="case-b", sequence=1)
            _insert_evidence(
                connection,
                evidence_id="evidence-same-case",
                case_id="case-a",
                activity_id="activity-a",
            )

        for evidence_id, activity_id in (
            ("evidence-missing", "missing-activity"),
            ("evidence-cross-case", "activity-b"),
        ):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_evidence(
                        connection,
                        evidence_id=evidence_id,
                        case_id="case-a",
                        activity_id=activity_id,
                        object_id=evidence_id,
                    )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_exact_evidence_link_identity_is_unique(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_l3_unique_identity.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-a")
            _insert_activity(connection, activity_id="activity-a", case_id="case-a", sequence=1)
            _insert_evidence(
                connection,
                evidence_id="evidence-original",
                case_id="case-a",
                activity_id="activity-a",
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_evidence(
                    connection,
                    evidence_id="evidence-duplicate",
                    case_id="case-a",
                    activity_id="activity-a",
                    content_hash="sha256:different",
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_activity_evidence_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_l3_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
