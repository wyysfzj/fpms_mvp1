from __future__ import annotations

import subprocess
import sys
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
from app.modules.auth.models import T_Role, T_User
from app.modules.system import models as system_models

REVISION = "v8_grant_manual_review_role_01"
DOWN_REVISION = "v8_future_annuity_exception_01"
TABLE = "t_grant_manual_review_role_config"
USER_ID = "11111111-1111-4111-8111-111111111111"
ROLE_IDS = tuple(f"role-{index}" for index in range(1, 6))
NOW = datetime(2026, 8, 10, 9, 0)
LATER = NOW + timedelta(days=365)
CURRENT_KEY = "DG-GRANT-MANUAL-REVIEW|GLOBAL"

COLUMNS = {
    "id": (String, 36, False, None),
    "gate_code": (String, 32, False, None),
    "scope_key": (String, 64, False, None),
    "official_copy_acquirer_role_id": (String, 36, False, None),
    "first_verifier_role_id": (String, 36, False, None),
    "second_verifier_role_id": (String, 36, False, None),
    "manual_review_proposer_role_id": (String, 36, False, None),
    "manual_review_second_reviewer_role_id": (String, 36, False, None),
    "config_version": (String, 128, False, None),
    "config_status": (String, 32, False, None),
    "effective_from": (DateTime, None, False, None),
    "effective_to": (DateTime, None, True, None),
    "confirmed_by": (String, 36, False, None),
    "published_at": (DateTime, None, False, None),
    "supersedes_config_id": (String, 36, True, None),
    "config_snapshot": (Text, None, False, None),
    "config_snapshot_hash": (String, 64, False, None),
    "idempotency_key": (String, 128, False, None),
    "current_identity_key": (String, 128, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}
UNIQUES = {
    "uq_t_grant_manual_review_role_config_version": ("config_version",),
    "uq_t_grant_manual_review_role_config_idempotency_key": ("idempotency_key",),
    "uq_t_grant_manual_review_role_config_current_identity_key": (
        "current_identity_key",
    ),
}
FKS = {
    "fk_t_grant_manual_role_config_acquirer_role": (
        ("official_copy_acquirer_role_id",),
        ("t_role.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_first_verifier_role": (
        ("first_verifier_role_id",),
        ("t_role.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_second_verifier_role": (
        ("second_verifier_role_id",),
        ("t_role.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_proposer_role": (
        ("manual_review_proposer_role_id",),
        ("t_role.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_second_reviewer_role": (
        ("manual_review_second_reviewer_role_id",),
        ("t_role.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_confirmed_by": (
        ("confirmed_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_manual_role_config_supersedes_config": (
        ("supersedes_config_id",),
        (f"{TABLE}.id",),
        "RESTRICT",
    ),
}
CHECKS = {
    "ck_t_grant_manual_review_role_config_gate",
    "ck_t_grant_manual_review_role_config_status",
    "ck_t_grant_manual_review_role_config_interval",
    "ck_t_grant_manual_review_role_config_hash",
    "ck_t_grant_manual_review_role_config_current_key",
}
INDEXES = {
    "ix_t_grant_manual_review_role_config_interval": (
        "scope_key",
        "config_status",
        "effective_from",
        "effective_to",
    )
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
        "id": f"config-{tag}",
        "gate_code": "DG-GRANT-MANUAL-REVIEW",
        "scope_key": "GLOBAL",
        "official_copy_acquirer_role_id": ROLE_IDS[0],
        "first_verifier_role_id": ROLE_IDS[1],
        "second_verifier_role_id": ROLE_IDS[2],
        "manual_review_proposer_role_id": ROLE_IDS[3],
        "manual_review_second_reviewer_role_id": ROLE_IDS[4],
        "config_version": f"version-{tag}",
        "config_status": "ACTIVE",
        "effective_from": NOW,
        "effective_to": LATER,
        "confirmed_by": USER_ID,
        "published_at": NOW - timedelta(minutes=10),
        "supersedes_config_id": None,
        "config_snapshot": f'{{"test":"{tag}"}}',
        "config_snapshot_hash": "a" * 64,
        "idempotency_key": f"idempotency-{tag}",
        "current_identity_key": None,
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
def role_config_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "grant-manual-review-role.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _engine(db_path)
    try:
        yield engine, config
    finally:
        engine.dispose()
        get_settings.cache_clear()


def _seed_identities(engine) -> None:
    with Session(engine) as session:
        session.add(T_User(id=USER_ID, username="role-config-admin", password_hash="test-only"))
        session.add_all(
            T_Role(id=role_id, code=f"TEST_ROLE_{index}", name=f"测试岗位 {index}")
            for index, role_id in enumerate(ROLE_IDS, start=1)
        )
        session.commit()


def test_exact_orm_and_registry_contract() -> None:
    model = system_models.GrantManualReviewRoleConfig
    table = model.__table__
    assert table.name == TABLE
    assert tuple(table.c.keys()) == tuple(COLUMNS)
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

    backend_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.db.base import Base\n"
            "from app.models import *\n"
            "assert GrantManualReviewRoleConfig.__tablename__ == "
            "'t_grant_manual_review_role_config'\n"
            "assert 't_grant_manual_review_role_config' in Base.metadata.tables\n",
        ],
        cwd=backend_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_migration_reflection_head_and_clean_zero_rows(role_config_db) -> None:
    engine, config = role_config_db
    script = ScriptDirectory.from_config(config)
    assert script.get_heads() == [REVISION]
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
        assert connection.scalar(text("SELECT count(*) FROM t_role")) == 0


def test_valid_same_role_publication_revoked_shadow_and_uuid(role_config_db) -> None:
    engine, _config_value = role_config_db
    _seed_identities(engine)
    model = system_models.GrantManualReviewRoleConfig
    same_role_values = _values(
        "active",
        official_copy_acquirer_role_id=ROLE_IDS[0],
        first_verifier_role_id=ROLE_IDS[0],
        second_verifier_role_id=ROLE_IDS[0],
        manual_review_proposer_role_id=ROLE_IDS[0],
        manual_review_second_reviewer_role_id=ROLE_IDS[0],
        current_identity_key=CURRENT_KEY,
    )
    with Session(engine) as session:
        active = model(**same_role_values)
        generated = model(
            **{
                key: value
                for key, value in _values("uuid", effective_to=None).items()
                if key != "id"
            }
        )
        engine.dialect.insert_returning = False
        session.add_all((active, generated))
        session.flush()
        assert str(UUID(generated.id)) == generated.id
        session.commit()

        active.current_identity_key = None
        session.flush()
        revoked = model(
            **_values(
                "revoked",
                config_status="REVOKED",
                official_copy_acquirer_role_id=ROLE_IDS[0],
                first_verifier_role_id=ROLE_IDS[0],
                second_verifier_role_id=ROLE_IDS[0],
                manual_review_proposer_role_id=ROLE_IDS[0],
                manual_review_second_reviewer_role_id=ROLE_IDS[0],
                supersedes_config_id=active.id,
                current_identity_key=CURRENT_KEY,
            )
        )
        session.add(revoked)
        session.commit()
        assert active.current_identity_key is None
        assert revoked.current_identity_key == CURRENT_KEY


def test_constraints_uniques_foreign_keys_and_restricted_deletes(role_config_db) -> None:
    engine, _config_value = role_config_db
    _seed_identities(engine)
    with engine.begin() as connection:
        _insert(connection, _values("base", current_identity_key=CURRENT_KEY))
        _insert(connection, _values("history-a"))
        _insert(connection, _values("history-b", effective_to=None))
        _insert(
            connection,
            _values("successor", supersedes_config_id="config-base"),
        )

    invalid = (
        {"gate_code": "OTHER"},
        {"scope_key": "case:1"},
        {"config_status": "PENDING"},
        {"effective_to": NOW},
        {"config_snapshot_hash": "short"},
        {"config_snapshot_hash": "A" * 64},
        {"config_snapshot_hash": "g" * 64},
        {"current_identity_key": "wrong"},
        {"official_copy_acquirer_role_id": None},
        {"first_verifier_role_id": "missing-role"},
        {"second_verifier_role_id": "missing-role"},
        {"manual_review_proposer_role_id": "missing-role"},
        {"manual_review_second_reviewer_role_id": "missing-role"},
        {"confirmed_by": "missing-user"},
        {"supersedes_config_id": "missing-config"},
    )
    for index, overrides in enumerate(invalid):
        _expect_integrity(engine, _values(f"invalid-{index}", **overrides))

    _expect_integrity(engine, _values("duplicate-version", config_version="version-base"))
    _expect_integrity(
        engine,
        _values("duplicate-idempotency", idempotency_key="idempotency-base"),
    )
    _expect_integrity(
        engine,
        _values("duplicate-current", current_identity_key=CURRENT_KEY),
    )

    for table, row_id in (
        ("t_role", ROLE_IDS[0]),
        ("t_user", USER_ID),
        (TABLE, "config-base"),
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": row_id})
