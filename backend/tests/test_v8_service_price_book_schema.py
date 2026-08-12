from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
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
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.modules.auth.models import T_User
from app.modules.fees.models import ServicePriceBook

REVISION = "v8_w6_service_price_book_01"
DOWN_REVISION = "v8_payment_workbook_input_01"
TABLE = "t_service_price_book"
NOW = datetime(2026, 8, 13, 10, 0)
LATER = NOW + timedelta(days=365)
USER_IDS = tuple(f"10000000-0000-4000-8000-{index:012d}" for index in range(1, 7))
COLUMNS = (
    "id",
    "source_classification",
    "book_version",
    "scope_key",
    "currency",
    "tax_policy",
    "discount_policy",
    "source_reference",
    "source_content_hash",
    "item_snapshot",
    "item_snapshot_hash",
    "item_count",
    "status",
    "approved_by",
    "approved_at",
    "approval_reason",
    "activated_by",
    "activated_at",
    "retired_by",
    "retired_at",
    "retirement_reason",
    "effective_from",
    "effective_to",
    "supersedes_price_book_id",
    "idempotency_key",
    "current_identity_key",
    "created_by",
    "created_at",
    "updated_by",
    "updated_at",
)
COLUMN_SPECS = {
    "id": (String, 36, False),
    "source_classification": (String, 24, False),
    "book_version": (String, 128, False),
    "scope_key": (String, 128, False),
    "currency": (String, 8, False),
    "tax_policy": (Text, None, False),
    "discount_policy": (Text, None, False),
    "source_reference": (Text, None, False),
    "source_content_hash": (String, 64, False),
    "item_snapshot": (Text, None, False),
    "item_snapshot_hash": (String, 64, False),
    "item_count": (Integer, None, False),
    "status": (String, 24, False),
    "approved_by": (String, 36, True),
    "approved_at": (DateTime, None, True),
    "approval_reason": (Text, None, True),
    "activated_by": (String, 36, True),
    "activated_at": (DateTime, None, True),
    "retired_by": (String, 36, True),
    "retired_at": (DateTime, None, True),
    "retirement_reason": (Text, None, True),
    "effective_from": (DateTime, None, False),
    "effective_to": (DateTime, None, True),
    "supersedes_price_book_id": (String, 36, True),
    "idempotency_key": (String, 128, False),
    "current_identity_key": (String, 128, True),
    "created_by": (String, 36, False),
    "created_at": (DateTime, None, False),
    "updated_by": (String, 36, False),
    "updated_at": (DateTime, None, False),
}
CHECKS = {
    "ck_t_service_price_book_scope",
    "ck_t_service_price_book_source_classification",
    "ck_t_service_price_book_status",
    "ck_t_service_price_book_hashes",
    "ck_t_service_price_book_item_count",
    "ck_t_service_price_book_effective_interval",
    "ck_t_service_price_book_approval_tuple",
    "ck_t_service_price_book_status_tuple",
}
UNIQUES = {
    "uq_t_service_price_book_scope_version",
    "uq_t_service_price_book_idempotency_key",
    "uq_t_service_price_book_current_identity_key",
}
FKS = {
    "fk_t_service_price_book_approved_by",
    "fk_t_service_price_book_activated_by",
    "fk_t_service_price_book_retired_by",
    "fk_t_service_price_book_created_by",
    "fk_t_service_price_book_updated_by",
    "fk_t_service_price_book_supersedes",
}


def _config(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    backend_root = Path(__file__).resolve().parents[1]
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _engine(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@pytest.fixture
def price_book_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "service-price-book.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _engine(db_path)
    try:
        yield engine, config
    finally:
        engine.dispose()
        get_settings.cache_clear()


def _seed_users(engine) -> None:
    with Session(engine) as session:
        session.add_all(
            T_User(id=user_id, username=f"price-user-{index}", password_hash="test-only")
            for index, user_id in enumerate(USER_IDS, start=1)
        )
        session.commit()


def _values(tag: str, **overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "id": f"price-book-{tag}",
        "source_classification": "PRODUCTION",
        "book_version": f"version-{tag}",
        "scope_key": "GLOBAL",
        "currency": "CNY",
        "tax_policy": '{"tax_inclusive":true,"tax_rate":"0.06"}',
        "discount_policy": '{"mode":"NONE"}',
        "source_reference": f"managed/service-prices/{tag}.json",
        "source_content_hash": "a" * 64,
        "item_snapshot": "[]",
        "item_snapshot_hash": "b" * 64,
        "item_count": 0,
        "status": "DRAFT",
        "approved_by": None,
        "approved_at": None,
        "approval_reason": None,
        "activated_by": None,
        "activated_at": None,
        "retired_by": None,
        "retired_at": None,
        "retirement_reason": None,
        "effective_from": NOW,
        "effective_to": LATER,
        "supersedes_price_book_id": None,
        "idempotency_key": f"idempotency-{tag}",
        "current_identity_key": None,
        "created_by": USER_IDS[0],
        "updated_by": USER_IDS[0],
    }
    values.update(overrides)
    return values


def _approved(tag: str, **overrides: object) -> dict[str, object]:
    values = _values(
        tag,
        item_snapshot='[{"item_code":"SVC-001","unit_price":"100.00"}]',
        item_count=1,
        approved_by=USER_IDS[1],
        approved_at=NOW,
        approval_reason="完整价格版本独立核对通过",
    )
    values.update(overrides)
    return values


def _active(tag: str, **overrides: object) -> dict[str, object]:
    values = _approved(
        tag,
        status="ACTIVE",
        activated_by=USER_IDS[2],
        activated_at=NOW + timedelta(minutes=5),
        current_identity_key="GLOBAL",
    )
    values.update(overrides)
    return values


def _insert(connection, values: dict[str, object]) -> None:
    columns = ", ".join(values)
    parameters = ", ".join(f":{column}" for column in values)
    connection.execute(text(f"INSERT INTO {TABLE} ({columns}) VALUES ({parameters})"), values)


def _expect_integrity(engine, values: dict[str, object]) -> None:
    with pytest.raises(IntegrityError), engine.begin() as connection:
        _insert(connection, values)


def test_exact_orm_schema_and_forward_only_chain() -> None:
    table = ServicePriceBook.__table__
    assert table.name == TABLE
    assert tuple(table.c.keys()) == COLUMNS
    for name, (type_class, length, nullable) in COLUMN_SPECS.items():
        column = table.c[name]
        assert isinstance(column.type, type_class)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
    assert table.c.id.default is not None
    assert table.c.created_at.server_default is not None
    assert table.c.updated_at.server_default is not None
    assert {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } == CHECKS
    assert {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    } == UNIQUES
    foreign_keys = {
        constraint.name: constraint.ondelete
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert set(foreign_keys) == FKS
    assert set(foreign_keys.values()) == {"RESTRICT"}
    assert {
        index.name: tuple(column.name for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index)
    } == {
        "ix_t_service_price_book_scope_status_effective": (
            "scope_key",
            "status",
            "effective_from",
            "effective_to",
        )
    }

    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    revision = ScriptDirectory.from_config(config).get_revision(REVISION)
    assert revision is not None
    assert revision.down_revision == DOWN_REVISION
    assert "raise NotImplementedError" in Path(revision.path).read_text(encoding="utf-8")


def test_clean_upgrade_reflects_schema_and_has_no_seed(price_book_db) -> None:
    engine, config = price_book_db
    assert tuple(ScriptDirectory.from_config(config).get_heads()) == (REVISION,)
    inspector = inspect(engine)
    assert tuple(column["name"] for column in inspector.get_columns(TABLE)) == COLUMNS
    assert {row["name"] for row in inspector.get_check_constraints(TABLE)} == CHECKS
    assert {row["name"] for row in inspector.get_unique_constraints(TABLE)} == UNIQUES
    assert {row["name"] for row in inspector.get_foreign_keys(TABLE)} == FKS
    with engine.connect() as connection:
        assert connection.scalar(text(f"SELECT count(*) FROM {TABLE}")) == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"scope_key": "CLIENT-1"},
        {"source_classification": "UNKNOWN"},
        {"status": "APPROVED"},
        {"source_content_hash": "short"},
        {"item_snapshot_hash": "short"},
        {"item_count": -1},
        {"effective_to": NOW},
        {"approved_by": USER_IDS[1]},
        {"approved_by": USER_IDS[1], "approved_at": NOW},
        {"approved_by": USER_IDS[0], "approved_at": NOW, "approval_reason": "same actor"},
    ],
)
def test_invalid_header_and_approval_tuples_fail_closed(
    price_book_db, overrides: dict[str, object]
) -> None:
    engine, _ = price_book_db
    _seed_users(engine)
    _expect_integrity(engine, _values("invalid", **overrides))


@pytest.mark.parametrize(
    "overrides",
    [
        {"item_count": 0},
        {"item_snapshot": "[]"},
        {"approved_by": None},
        {"approved_at": None},
        {"approval_reason": None},
        {"activated_by": None},
        {"activated_at": None},
        {"current_identity_key": None},
    ],
)
def test_incomplete_active_versions_fail_closed(
    price_book_db, overrides: dict[str, object]
) -> None:
    engine, _ = price_book_db
    _seed_users(engine)
    _expect_integrity(engine, _active("invalid-active", **overrides))


def test_one_current_version_and_retirement_lineage(price_book_db) -> None:
    engine, _ = price_book_db
    _seed_users(engine)
    with engine.begin() as connection:
        _insert(connection, _active("active-one"))
    _expect_integrity(engine, _active("active-two"))

    retired = _approved(
        "retired",
        status="RETIRED",
        activated_by=USER_IDS[2],
        activated_at=NOW + timedelta(minutes=5),
        retired_by=USER_IDS[3],
        retired_at=NOW + timedelta(days=1),
        retirement_reason="由新价格版本替代",
    )
    with engine.begin() as connection:
        _insert(connection, retired)
    _expect_integrity(
        engine, {**retired, "id": "retired-missing-reason", "retirement_reason": None}
    )


def test_test_only_draft_is_a_valid_inactive_carrier(price_book_db) -> None:
    engine, _ = price_book_db
    _seed_users(engine)
    values = _values("test-only-draft", source_classification="TEST_ONLY")
    with engine.begin() as connection:
        _insert(connection, values)
        stored = connection.execute(
            text(
                f"SELECT source_classification, status, current_identity_key "
                f"FROM {TABLE} WHERE id = :id"
            ),
            {"id": values["id"]},
        ).one()
    assert stored == ("TEST_ONLY", "DRAFT", None)
