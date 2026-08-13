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
from app.models import OfficialPaymentWorkbookInputVersion
from app.modules.auth.models import T_User

REVISION = "v8_payment_workbook_input_01"
DOWN_REVISION = "v8_grant_official_copy_01"
CURRENT_HEAD = "v8_w6_service_price_book_01"
TABLE = "t_official_payment_workbook_input_version"
NOW = datetime(2026, 8, 13, 9, 0)
LATER = NOW + timedelta(days=365)
USER_IDS = tuple(f"00000000-0000-4000-8000-{index:012d}" for index in range(1, 7))

COLUMNS = (
    "id",
    "scope_key",
    "source_classification",
    "template_version",
    "template_storage_path",
    "template_content_hash",
    "upload_proof_storage_path",
    "upload_proof_content_hash",
    "structure_snapshot",
    "structure_snapshot_hash",
    "workflow_status",
    "validated_by",
    "validated_at",
    "validation_reason",
    "reviewed_by",
    "reviewed_at",
    "review_reason",
    "activation_status",
    "activated_by",
    "activated_at",
    "retired_by",
    "retired_at",
    "retirement_reason",
    "effective_from",
    "effective_to",
    "supersedes_version_id",
    "idempotency_key",
    "current_identity_key",
    "created_by",
    "created_at",
    "updated_by",
    "updated_at",
)
COLUMN_SPECS = {
    "id": (String, 36, False),
    "scope_key": (String, 36, False),
    "source_classification": (String, 24, False),
    "template_version": (String, 128, False),
    "template_storage_path": (Text, None, False),
    "template_content_hash": (String, 64, False),
    "upload_proof_storage_path": (Text, None, False),
    "upload_proof_content_hash": (String, 64, False),
    "structure_snapshot": (Text, None, False),
    "structure_snapshot_hash": (String, 64, False),
    "workflow_status": (String, 24, False),
    "validated_by": (String, 36, True),
    "validated_at": (DateTime, None, True),
    "validation_reason": (Text, None, True),
    "reviewed_by": (String, 36, True),
    "reviewed_at": (DateTime, None, True),
    "review_reason": (Text, None, True),
    "activation_status": (String, 24, False),
    "activated_by": (String, 36, True),
    "activated_at": (DateTime, None, True),
    "retired_by": (String, 36, True),
    "retired_at": (DateTime, None, True),
    "retirement_reason": (Text, None, True),
    "effective_from": (DateTime, None, False),
    "effective_to": (DateTime, None, True),
    "supersedes_version_id": (String, 36, True),
    "idempotency_key": (String, 128, False),
    "current_identity_key": (String, 128, True),
    "created_by": (String, 36, False),
    "created_at": (DateTime, None, False),
    "updated_by": (String, 36, False),
    "updated_at": (DateTime, None, False),
}
CHECKS = {
    "ck_t_official_payment_workbook_input_scope",
    "ck_t_official_payment_workbook_input_source_classification",
    "ck_t_official_payment_workbook_input_workflow_status",
    "ck_t_official_payment_workbook_input_activation_status",
    "ck_t_official_payment_workbook_input_hashes",
    "ck_t_official_payment_workbook_input_effective_interval",
    "ck_t_official_payment_workbook_input_workflow_tuple",
    "ck_t_official_payment_workbook_input_activation_tuple",
}
UNIQUES = {
    "uq_t_official_payment_workbook_input_scope_version",
    "uq_t_official_payment_workbook_input_idempotency_key",
    "uq_t_official_payment_workbook_input_current_identity_key",
}
FKS = {
    "fk_t_official_payment_workbook_input_validated_by",
    "fk_t_official_payment_workbook_input_reviewed_by",
    "fk_t_official_payment_workbook_input_activated_by",
    "fk_t_official_payment_workbook_input_retired_by",
    "fk_t_official_payment_workbook_input_created_by",
    "fk_t_official_payment_workbook_input_updated_by",
    "fk_t_official_payment_workbook_input_supersedes",
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
def workbook_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "workbook-input.db"
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
            T_User(id=user_id, username=f"workbook-user-{index}", password_hash="test-only")
            for index, user_id in enumerate(USER_IDS, start=1)
        )
        session.commit()


def _values(tag: str, **overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "id": f"workbook-input-{tag}",
        "scope_key": "GLOBAL",
        "source_classification": "PRODUCTION",
        "template_version": f"template-{tag}",
        "template_storage_path": f"managed/templates/{tag}.xlsm",
        "template_content_hash": "a" * 64,
        "upload_proof_storage_path": f"managed/proofs/{tag}.json",
        "upload_proof_content_hash": "b" * 64,
        "structure_snapshot": '{"sheets":["缴费信息"]}',
        "structure_snapshot_hash": "c" * 64,
        "workflow_status": "DRAFT",
        "validated_by": None,
        "validated_at": None,
        "validation_reason": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "review_reason": None,
        "activation_status": "INACTIVE",
        "activated_by": None,
        "activated_at": None,
        "retired_by": None,
        "retired_at": None,
        "retirement_reason": None,
        "effective_from": NOW,
        "effective_to": LATER,
        "supersedes_version_id": None,
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
        workflow_status="APPROVED",
        validated_by=USER_IDS[1],
        validated_at=NOW,
        validation_reason="结构和哈希核对通过",
        reviewed_by=USER_IDS[2],
        reviewed_at=NOW + timedelta(minutes=5),
        review_reason="独立复核通过",
    )
    values.update(overrides)
    return values


def _reviewed(tag: str, status: str, **overrides: object) -> dict[str, object]:
    values = _approved(tag, **overrides)
    values["workflow_status"] = status
    return values


def _insert(connection, values: dict[str, object]) -> None:
    columns = ", ".join(values)
    parameters = ", ".join(f":{column}" for column in values)
    connection.execute(text(f"INSERT INTO {TABLE} ({columns}) VALUES ({parameters})"), values)


def _expect_integrity(engine, values: dict[str, object]) -> None:
    with pytest.raises(IntegrityError), engine.begin() as connection:
        _insert(connection, values)


def test_exact_model_schema_and_migration_chain() -> None:
    table = OfficialPaymentWorkbookInputVersion.__table__
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
        "ix_t_official_payment_workbook_input_scope_status_effective": (
            "scope_key",
            "workflow_status",
            "activation_status",
            "effective_from",
            "effective_to",
        )
    }

    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(config).get_revision(REVISION)
    assert script is not None
    assert script.down_revision == DOWN_REVISION
    assert "raise NotImplementedError" in Path(script.path).read_text(encoding="utf-8")


def test_clean_upgrade_reflects_exact_schema_and_has_no_seed(workbook_db) -> None:
    engine, config = workbook_db
    script = ScriptDirectory.from_config(config)
    assert tuple(script.get_heads()) == (CURRENT_HEAD,)
    assert REVISION in {
        item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
    }
    inspector = inspect(engine)
    assert tuple(column["name"] for column in inspector.get_columns(TABLE)) == COLUMNS
    assert {constraint["name"] for constraint in inspector.get_check_constraints(TABLE)} == CHECKS
    assert {constraint["name"] for constraint in inspector.get_unique_constraints(TABLE)} == UNIQUES
    assert {constraint["name"] for constraint in inspector.get_foreign_keys(TABLE)} == FKS
    with engine.connect() as connection:
        assert connection.scalar(text(f"SELECT count(*) FROM {TABLE}")) == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"scope_key": "CLIENT-1"},
        {"source_classification": "UNCLASSIFIED"},
        {"workflow_status": "PUBLISHED"},
        {"activation_status": "ENABLED"},
        {"template_content_hash": "short"},
        {"upload_proof_content_hash": "short"},
        {"structure_snapshot_hash": "short"},
        {"effective_to": NOW},
        {"workflow_status": "DRAFT", "validated_by": USER_IDS[1]},
        {
            "workflow_status": "VALIDATED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": None,
        },
        {
            "workflow_status": "APPROVED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": USER_IDS[0],
            "reviewed_at": NOW,
            "review_reason": "same user",
        },
        {
            "workflow_status": "APPROVED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": None,
            "reviewed_at": NOW,
            "review_reason": "missing reviewer",
        },
        {
            "workflow_status": "APPROVED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": USER_IDS[2],
            "reviewed_at": None,
            "review_reason": "missing time",
        },
        {
            "workflow_status": "APPROVED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": USER_IDS[2],
            "reviewed_at": NOW,
            "review_reason": None,
        },
        {
            "workflow_status": "REJECTED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": None,
            "reviewed_at": NOW,
            "review_reason": "missing reviewer",
        },
        {
            "workflow_status": "REJECTED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": USER_IDS[2],
            "reviewed_at": None,
            "review_reason": "missing time",
        },
        {
            "workflow_status": "REJECTED",
            "validated_by": USER_IDS[1],
            "validated_at": NOW,
            "validation_reason": "valid",
            "reviewed_by": USER_IDS[2],
            "reviewed_at": NOW,
            "review_reason": None,
        },
    ],
)
def test_invalid_scope_hash_interval_and_workflow_tuples_fail_closed(
    workbook_db, overrides: dict[str, object]
) -> None:
    engine, _ = workbook_db
    _seed_users(engine)
    _expect_integrity(engine, _values("invalid", **overrides))


def test_test_only_cannot_activate_and_only_one_global_version_can_be_active(workbook_db) -> None:
    engine, _ = workbook_db
    _seed_users(engine)
    activation = {
        "activation_status": "ACTIVE",
        "activated_by": USER_IDS[3],
        "activated_at": NOW + timedelta(minutes=10),
        "current_identity_key": "GLOBAL",
    }
    _expect_integrity(
        engine,
        _approved("test-only", source_classification="TEST_ONLY", **activation),
    )
    _expect_integrity(
        engine,
        _approved("active-without-identity", **{**activation, "current_identity_key": None}),
    )

    with engine.begin() as connection:
        _insert(connection, _approved("active-one", **activation))
    _expect_integrity(engine, _approved("active-two", **activation))


def test_exact_validated_approved_and_rejected_workflow_shapes_are_accepted(workbook_db) -> None:
    engine, _ = workbook_db
    _seed_users(engine)
    validated = _values(
        "validated",
        workflow_status="VALIDATED",
        validated_by=USER_IDS[1],
        validated_at=NOW,
        validation_reason="结构核对通过",
    )
    approved = _reviewed("approved", "APPROVED")
    rejected = _reviewed("rejected", "REJECTED", review_reason="独立复核拒绝")
    with engine.begin() as connection:
        for values in (validated, approved, rejected):
            _insert(connection, values)


def test_retired_version_retains_activation_and_retirement_lineage(workbook_db) -> None:
    engine, _ = workbook_db
    _seed_users(engine)
    retired = _approved(
        "retired",
        activation_status="RETIRED",
        activated_by=USER_IDS[3],
        activated_at=NOW + timedelta(minutes=10),
        retired_by=USER_IDS[4],
        retired_at=NOW + timedelta(days=1),
        retirement_reason="由新版本替代",
        current_identity_key=None,
    )
    with engine.begin() as connection:
        _insert(connection, retired)
    _expect_integrity(engine, {**retired, "id": "retired-without-actor", "retired_by": None})
