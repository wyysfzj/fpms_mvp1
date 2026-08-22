from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.system import models as system_models

REVISION = "v8_future_annuity_exception_01"
DOWN_REVISION = "v8_grant_source_carrier_01"
CURRENT_HEAD = "v8_w6_service_price_book_01"
TABLE = "t_future_annuity_draft_exception_record"
USER_ID = "11111111-1111-4111-8111-111111111111"
CLIENT_ID = "22222222-2222-4222-8222-222222222222"
CASE_ID = "33333333-3333-4333-8333-333333333333"
NOW = datetime(2026, 8, 10, 9, 0)
LATER = NOW + timedelta(days=30)

COLUMNS = {
    "id": (String, 36, False, None),
    "record_type": (String, 16, False, None),
    "scope_type": (String, 16, True, None),
    "client_id": (String, 36, True, None),
    "case_id": (String, 36, True, None),
    "effective_from": (DateTime, None, True, None),
    "effective_to": (DateTime, None, True, None),
    "target_publication_id": (String, 36, True, None),
    "record_version": (String, 128, False, None),
    "source_reference": (String, 512, False, None),
    "source_version": (String, 128, False, None),
    "reason": (Text, None, False, None),
    "record_snapshot": (Text, None, False, None),
    "record_snapshot_hash": (String, 64, False, None),
    "confirmed_by": (String, 36, False, None),
    "published_at": (DateTime, None, False, None),
    "effective_at": (DateTime, None, False, None),
    "idempotency_key": (String, 128, False, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}
UNIQUES = {
    "uq_t_future_annuity_draft_exception_record_version": ("record_version",),
    "uq_t_future_annuity_draft_exception_idempotency_key": ("idempotency_key",),
    "uq_t_future_annuity_draft_exception_target_publication_id": (
        "target_publication_id",
    ),
}
FKS = {
    "fk_t_future_annuity_draft_exception_client_id": (
        ("client_id",),
        ("t_client.id",),
        "RESTRICT",
    ),
    "fk_t_future_annuity_draft_exception_case_id": (
        ("case_id",),
        ("t_case.id",),
        "RESTRICT",
    ),
    "fk_t_future_annuity_draft_exception_target_id": (
        ("target_publication_id",),
        (f"{TABLE}.id",),
        "RESTRICT",
    ),
    "fk_t_future_annuity_draft_exception_confirmed_by": (
        ("confirmed_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
}
CHECKS = {
    "ck_t_future_annuity_draft_exception_record_type",
    "ck_t_future_annuity_draft_exception_hash",
    "ck_t_future_annuity_draft_exception_shape",
}
INDEXES = {
    "ix_t_future_annuity_draft_exception_client_interval": (
        "client_id",
        "record_type",
        "effective_from",
        "effective_to",
        "effective_at",
    ),
    "ix_t_future_annuity_draft_exception_case_interval": (
        "case_id",
        "record_type",
        "effective_from",
        "effective_to",
        "effective_at",
    ),
    "ix_t_future_annuity_draft_exception_target": (
        "target_publication_id",
        "record_type",
        "effective_at",
    ),
}


def _engine(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _config(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _normalized_default(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip("()")


def _model_uniques(table) -> dict[str, tuple[str, ...]]:
    return {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def _model_fks(table) -> dict[str, tuple[tuple[str, ...], tuple[str, ...], str | None]]:
    return {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }


def _model_checks(table) -> set[str]:
    return {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }


def _model_indexes(table) -> dict[str, tuple[str, ...]]:
    return {
        index.name: tuple(column.name for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index)
    }


def _values(tag: str, **overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "id": f"record-{tag}",
        "record_type": "PUBLISHED",
        "scope_type": "CLIENT",
        "client_id": CLIENT_ID,
        "case_id": None,
        "effective_from": NOW,
        "effective_to": LATER,
        "target_publication_id": None,
        "record_version": f"version-{tag}",
        "source_reference": "Scheme A test authority",
        "source_version": "2026-08-10",
        "reason": "TEST ONLY",
        "record_snapshot": f'{{"test":"{tag}"}}',
        "record_snapshot_hash": "a" * 64,
        "confirmed_by": USER_ID,
        "published_at": NOW - timedelta(hours=1),
        "effective_at": NOW - timedelta(minutes=30),
        "idempotency_key": f"idempotency-{tag}",
    }
    values.update(overrides)
    return values


def _insert(connection, values: dict[str, object]) -> None:
    columns = ", ".join(values)
    parameters = ", ".join(f":{name}" for name in values)
    connection.execute(text(f"INSERT INTO {TABLE} ({columns}) VALUES ({parameters})"), values)


def _expect_integrity(engine, values: dict[str, object]) -> None:
    with pytest.raises(IntegrityError), engine.begin() as connection:
        _insert(connection, values)


@pytest.fixture
def exception_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "future-annuity-exception.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _engine(db_path)
    try:
        yield engine, config
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_exact_orm_contract_and_append_only_listeners() -> None:
    model = system_models.FutureAnnuityDraftExceptionRecord
    table = model.__table__
    assert table.name == TABLE
    assert list(table.c) and tuple(table.c.keys()) == tuple(COLUMNS)
    for name, (type_class, length, nullable, default) in COLUMNS.items():
        column = table.c[name]
        assert isinstance(column.type, type_class)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert _normalized_default(column.server_default.arg if column.server_default else None) == default
    assert table.c.id.default is not None
    assert _model_uniques(table) == UNIQUES
    assert _model_fks(table) == FKS
    assert _model_checks(table) == CHECKS
    assert _model_indexes(table) == INDEXES


def test_migration_identity_reflection_and_clean_zero_row_upgrade(exception_db) -> None:
    engine, config = exception_db
    script = ScriptDirectory.from_config(config)
    assert script.get_heads() == [CURRENT_HEAD]
    assert REVISION in {
        item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
    }
    migration = script.get_revision(REVISION)
    assert migration is not None
    assert migration.down_revision == DOWN_REVISION
    assert migration.module.branch_labels is None
    assert migration.module.depends_on is None
    with pytest.raises(NotImplementedError, match="forward-only migration"):
        migration.module.downgrade()

    inspector = inspect(engine)
    reflected = inspector.get_columns(TABLE)
    assert tuple(column["name"] for column in reflected) == tuple(COLUMNS)
    for column in reflected:
        type_class, length, nullable, default = COLUMNS[column["name"]]
        assert isinstance(column["type"], type_class)
        assert getattr(column["type"], "length", None) == length
        assert column["nullable"] is nullable
        assert _normalized_default(column.get("default")) == default
    assert {
        item["name"]: tuple(item["column_names"])
        for item in inspector.get_unique_constraints(TABLE)
    } == UNIQUES
    assert {
        item["name"]: (
            tuple(item["constrained_columns"]),
            tuple(f"{item['referred_table']}.{name}" for name in item["referred_columns"]),
            item.get("options", {}).get("ondelete"),
        )
        for item in inspector.get_foreign_keys(TABLE)
    } == FKS
    assert {item["name"] for item in inspector.get_check_constraints(TABLE)} == CHECKS
    assert {
        item["name"]: tuple(item["column_names"])
        for item in inspector.get_indexes(TABLE)
    } == INDEXES
    with engine.connect() as connection:
        assert connection.scalar(text(f"SELECT count(*) FROM {TABLE}")) == 0


def test_valid_publications_revocation_uuid_and_append_only_behavior(exception_db) -> None:
    engine, _config_value = exception_db
    model = system_models.FutureAnnuityDraftExceptionRecord
    with Session(engine) as session:
        session.add_all(
            (
                T_User(id=USER_ID, username="exception-admin", password_hash="test-only"),
                Client(id=CLIENT_ID, name_cn="测试客户"),
            )
        )
        session.flush()
        session.add(Case(id=CASE_ID, case_no="TEST-EXCEPTION-CASE", client_id=CLIENT_ID))
        session.commit()

        client_row = model(**_values("client"))
        case_row = model(
            **_values(
                "case",
                scope_type="CASE",
                client_id=None,
                case_id=CASE_ID,
                published_at=NOW - timedelta(days=2),
                effective_at=NOW - timedelta(days=1),
                effective_from=NOW,
            )
        )
        generated = model(**{key: value for key, value in _values("uuid").items() if key != "id"})
        session.add_all((client_row, case_row, generated))
        engine.dialect.insert_returning = False
        session.flush()
        assert str(UUID(generated.id)) == generated.id
        session.commit()
        assert case_row.published_at != case_row.effective_at != case_row.effective_from

        before = {column.name: getattr(client_row, column.name) for column in model.__table__.c}
        revoked = model(
            **_values(
                "revoked",
                record_type="REVOKED",
                scope_type=None,
                client_id=None,
                case_id=None,
                effective_from=None,
                effective_to=None,
                target_publication_id=client_row.id,
            )
        )
        session.add(revoked)
        session.commit()
        assert before == {
            column.name: getattr(client_row, column.name) for column in model.__table__.c
        }

        client_row.reason = "forbidden update"
        with pytest.raises(ValueError, match="future annuity draft exception record is append-only"):
            session.flush()
        session.rollback()
        client_row = session.get(model, "record-client")
        assert client_row is not None
        session.delete(client_row)
        with pytest.raises(ValueError, match="future annuity draft exception record is append-only"):
            session.flush()
        session.rollback()


def test_database_constraints_uniques_foreign_keys_and_restricted_deletes(exception_db) -> None:
    engine, _config_value = exception_db
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO t_user "
                "(id, username, password_hash, is_active, created_at, updated_at) "
                "VALUES (:id, 'exception-admin', 'test-only', 1, :now, :now)"
            ),
            {"id": USER_ID, "now": NOW},
        )
        connection.execute(
            text(
                "INSERT INTO t_client (id, name_cn, created_at, updated_at) "
                "VALUES (:id, '测试客户', :now, :now)"
            ),
            {"id": CLIENT_ID, "now": NOW},
        )
        connection.execute(
            text(
                "INSERT INTO t_case (id, case_no, client_id, created_at, updated_at) "
                "VALUES (:id, 'TEST-EXCEPTION-CASE', :client_id, :now, :now)"
            ),
            {"id": CASE_ID, "client_id": CLIENT_ID, "now": NOW},
        )
        _insert(connection, _values("base"))
        _insert(
            connection,
            _values(
                "case-base",
                scope_type="CASE",
                client_id=None,
                case_id=CASE_ID,
            ),
        )
        _insert(
            connection,
            _values(
                "base-revoked",
                record_type="REVOKED",
                scope_type=None,
                client_id=None,
                case_id=None,
                effective_from=None,
                effective_to=None,
                target_publication_id="record-base",
            ),
        )

    invalid = (
        {"record_type": "UNKNOWN"},
        {"record_snapshot_hash": "short"},
        {"record_snapshot_hash": "A" * 64},
        {"record_snapshot_hash": "g" * 64},
        {"scope_type": None},
        {"client_id": CLIENT_ID, "case_id": CASE_ID},
        {"scope_type": "GLOBAL"},
        {"effective_to": None},
        {"effective_to": NOW},
        {"target_publication_id": "record-base"},
        {
            "record_type": "REVOKED",
            "target_publication_id": "record-base",
        },
        {"confirmed_by": "missing-user"},
        {"client_id": "missing-client"},
        {"scope_type": "CASE", "client_id": None, "case_id": "missing-case"},
    )
    for index, overrides in enumerate(invalid):
        _expect_integrity(engine, _values(f"invalid-{index}", **overrides))

    _expect_integrity(engine, _values("duplicate-version", record_version="version-base"))
    _expect_integrity(
        engine,
        _values("duplicate-idempotency", idempotency_key="idempotency-base"),
    )
    _expect_integrity(
        engine,
        _values(
            "duplicate-target",
            record_type="REVOKED",
            scope_type=None,
            client_id=None,
            case_id=None,
            effective_from=None,
            effective_to=None,
            target_publication_id="record-base",
        ),
    )
    _expect_integrity(
        engine,
        _values(
            "missing-target",
            record_type="REVOKED",
            scope_type=None,
            client_id=None,
            case_id=None,
            effective_from=None,
            effective_to=None,
            target_publication_id="missing-publication",
        ),
    )

    for table, row_id in (
        ("t_user", USER_ID),
        ("t_client", CLIENT_ID),
        ("t_case", CASE_ID),
        (TABLE, "record-base"),
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": row_id})
