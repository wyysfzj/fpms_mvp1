from __future__ import annotations

import importlib
from datetime import datetime
from pathlib import Path
from types import ModuleType
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
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
from app.modules.auth import models as auth_models

REVISION = "v8_post_w1_customer_decision_gate_01"
DOWN_REVISION = "v8_w1_f5_fee_reduction_01"
TABLE = "t_customer_decision_gate"

GATE_CODES = (
    "DG-FEE-APPLICATION-DRAFT",
    "DG-FEE-GRANT-YEAR-DRAFT",
    "DG-FEE-FUTURE-ANNUITY",
    "DG-GRANT-EVIDENCE-SOURCE",
    "DG-GRANT-MANUAL-REVIEW",
    "DG-PAYMENT-WORKBOOK",
    "DG-SERVICE-RATE-VERSION",
    "DG-LEGACY-FORM-CLASS",
)

COLUMN_SPECS = {
    "id": (String, 36, False, None),
    "gate_code": (String, 32, False, None),
    "scope_key": (String, 256, False, None),
    "decision_value": (Text, None, True, None),
    "decision_status": (String, 32, False, None),
    "source_reference": (String, 512, False, None),
    "source_version": (String, 128, False, None),
    "confirmed_by": (String, 36, False, None),
    "effective_at": (DateTime, None, False, None),
    "recorded_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "supersedes_gate_id": (String, 36, True, None),
    "decision_snapshot": (Text, None, False, None),
    "idempotency_key": (String, 128, False, None),
    "current_identity_key": (String, 320, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

UNIQUE_SPECS = {
    "uq_t_customer_decision_gate_idempotency_key": ("idempotency_key",),
    "uq_t_customer_decision_gate_current_identity_key": ("current_identity_key",),
}

FOREIGN_KEY_SPECS = {
    "fk_t_customer_decision_gate_confirmed_by": (
        ("confirmed_by",),
        "t_user",
        ("id",),
        None,
    ),
    "fk_t_customer_decision_gate_supersedes_gate_id": (
        ("supersedes_gate_id",),
        TABLE,
        ("id",),
        None,
    ),
}

CHECK_NAMES = {
    "ck_t_customer_decision_gate_gate_code",
    "ck_t_customer_decision_gate_decision_status",
}


def _system_models() -> ModuleType | None:
    try:
        return importlib.import_module("app.modules.system.models")
    except ModuleNotFoundError as exc:
        if exc.name != "app.modules.system.models":
            raise
        return None


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


def _insert_user(connection, *, user_id: str = "confirmer-1") -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_user (id, username, password_hash)
            VALUES (:id, :username, 'not-used')
            """
        ),
        {"id": user_id, "username": user_id},
    )


def _insert_gate(
    connection,
    *,
    gate_id: str,
    gate_code: str = GATE_CODES[0],
    scope_key: str = "GLOBAL",
    decision_status: str = "CONFIRMED",
    confirmed_by: str = "confirmer-1",
    supersedes_gate_id: str | None = None,
    idempotency_key: str | None = None,
    current_identity_key: str | None = None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, gate_code, scope_key, decision_value, decision_status,
                 source_reference, source_version, confirmed_by, effective_at,
                 supersedes_gate_id, decision_snapshot, idempotency_key,
                 current_identity_key)
            VALUES
                (:id, :gate_code, :scope_key, 'PAY', :decision_status,
                 'customer-decision-register', '2026-07-13', :confirmed_by,
                 :effective_at, :supersedes_gate_id, '{{}}', :idempotency_key,
                 :current_identity_key)
            """
        ),
        {
            "id": gate_id,
            "gate_code": gate_code,
            "scope_key": scope_key,
            "decision_status": decision_status,
            "confirmed_by": confirmed_by,
            "effective_at": datetime(2026, 7, 13, 10, 0, 0),
            "supersedes_gate_id": supersedes_gate_id,
            "idempotency_key": idempotency_key or f"request:{gate_id}",
            "current_identity_key": current_identity_key,
        },
    )


def test_customer_decision_gate_model_matches_frozen_contract(tmp_path) -> None:
    system_models = _system_models()
    assert system_models is not None, "customer decision gate ORM module is absent"

    model = getattr(system_models, "CustomerDecisionGate", None)
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

    assert {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    } == CHECK_NAMES
    assert not model.__table__.indexes

    engine = _sqlite_engine(tmp_path / "decision_gate_model.db")
    try:
        Base.metadata.create_all(engine)
        assert TABLE in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def test_clean_sqlite_upgrade_creates_exact_decision_gate_schema(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "decision_gate_migration.db"
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
        assert {item["name"] for item in inspector.get_check_constraints(TABLE)} == CHECK_NAMES
        assert inspector.get_indexes(TABLE) == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_model_generates_application_uuid() -> None:
    system_models = _system_models()
    assert system_models is not None, "customer decision gate ORM module is absent"

    gate = system_models.CustomerDecisionGate(
        gate_code=GATE_CODES[0],
        scope_key="GLOBAL",
        decision_value="PAY",
        decision_status="CONFIRMED",
        source_reference="customer-decision-register",
        source_version="2026-07-13",
        confirmed_by="confirmer-1",
        effective_at=datetime(2026, 7, 13, 10, 0, 0),
        decision_snapshot="{}",
        idempotency_key="request:model-uuid",
        current_identity_key=f"{GATE_CODES[0]}|GLOBAL",
    )
    default = gate.__table__.c.id.default
    assert default is not None

    generated_id = default.arg(None)
    assert str(UUID(generated_id)) == generated_id
    assert len(generated_id) == 36


def test_sqlite_constraints_freeze_gate_capacity_and_append_only_identities(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "decision_gate_constraints.db"
    config = _alembic_config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _sqlite_engine(db_path)
    try:
        with engine.begin() as connection:
            _insert_user(connection)
            for index, gate_code in enumerate(GATE_CODES, start=1):
                _insert_gate(
                    connection,
                    gate_id=f"gate-{index}",
                    gate_code=gate_code,
                    scope_key=f"scope-{index}",
                    current_identity_key=f"{gate_code}|scope-{index}",
                )

        with engine.begin() as connection:
            _insert_gate(
                connection,
                gate_id="superseding-gate",
                supersedes_gate_id="gate-1",
                current_identity_key=None,
            )

        with engine.begin() as connection:
            row = (
                connection.execute(
                    text(
                        f"""
                    SELECT recorded_at, created_at, updated_at
                    FROM {TABLE}
                    WHERE id = 'superseding-gate'
                    """
                    )
                )
                .mappings()
                .one()
            )
            assert all(row[name] is not None for name in row)

        invalid_rows = (
            {"gate_id": "invalid-code", "gate_code": "DG-UNFROZEN"},
            {"gate_id": "invalid-status", "decision_status": "PENDING"},
            {"gate_id": "invalid-user", "confirmed_by": "missing-user"},
            {"gate_id": "invalid-supersedes", "supersedes_gate_id": "missing-gate"},
        )
        for kwargs in invalid_rows:
            with pytest.raises(IntegrityError), engine.begin() as connection:
                _insert_gate(connection, **kwargs)

        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_gate(
                connection,
                gate_id="duplicate-request",
                idempotency_key="request:gate-1",
            )

        with pytest.raises(IntegrityError), engine.begin() as connection:
            _insert_gate(
                connection,
                gate_id="duplicate-current",
                current_identity_key=f"{GATE_CODES[0]}|scope-1",
            )

        with engine.begin() as connection:
            _insert_gate(connection, gate_id="history-null-current-1")
            _insert_gate(connection, gate_id="history-null-current-2")
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_migration_is_forward_only() -> None:
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "v8_post_w1_customer_decision_gate.py"
    )
    spec = importlib.util.spec_from_file_location(
        "v8_post_w1_customer_decision_gate",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    with pytest.raises(RuntimeError, match="forward-only"):
        migration.downgrade()


_ = auth_models
