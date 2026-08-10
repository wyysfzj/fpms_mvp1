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
from app.modules.documents import models as document_models

REVISION = "v8_grant_official_copy_01"
DOWN_REVISION = "v8_grant_manual_review_role_01"
TABLE = "t_grant_official_copy_verification_event"
NOW = datetime(2026, 8, 10, 9, 0, 0, 123456)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
EVIDENCE_ID = "evidence-official-copy-1"
CURRENT_KEY = f"GRANT_OFFICIAL_COPY|{EVIDENCE_ID}"

COLUMNS = {
    "id": (String, 36, False, None),
    "evidence_version_id": (String, 36, False, None),
    "source_config_id": (String, 36, False, None),
    "source_record_id": (String, 36, False, None),
    "role_config_id": (String, 36, False, None),
    "evidence_scope": (String, 32, False, None),
    "event_type": (String, 32, False, None),
    "actor_id": (String, 36, False, None),
    "action_at": (DateTime, None, False, None),
    "reason": (Text, None, False, None),
    "original_reference": (String, 512, False, None),
    "acquisition_method_snapshot": (String, 64, False, None),
    "evidence_content_hash": (String, 128, False, None),
    "source_config_snapshot_hash": (String, 64, False, None),
    "source_snapshot_hash": (String, 64, False, None),
    "role_config_snapshot_hash": (String, 64, False, None),
    "predecessor_event_id": (String, 36, True, None),
    "event_snapshot": (Text, None, False, None),
    "event_snapshot_hash": (String, 64, False, None),
    "idempotency_key": (String, 128, False, None),
    "current_identity_key": (String, 96, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}
UNIQUES = {
    "uq_t_grant_official_copy_event_stage": ("evidence_version_id", "event_type"),
    "uq_t_grant_official_copy_event_idempotency_key": ("idempotency_key",),
    "uq_t_grant_official_copy_event_current_identity_key": ("current_identity_key",),
}
FKS = {
    "fk_t_grant_official_copy_event_evidence_version": (
        ("evidence_version_id",),
        ("t_document_evidence_version.id",),
        "RESTRICT",
    ),
    "fk_t_grant_official_copy_event_source_config": (
        ("source_config_id",),
        ("t_grant_evidence_source_config.id",),
        "RESTRICT",
    ),
    "fk_t_grant_official_copy_event_source_record": (
        ("source_record_id",),
        ("t_grant_evidence_source_record.id",),
        "RESTRICT",
    ),
    "fk_t_grant_official_copy_event_role_config": (
        ("role_config_id",),
        ("t_grant_manual_review_role_config.id",),
        "RESTRICT",
    ),
    "fk_t_grant_official_copy_event_actor": (
        ("actor_id",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_official_copy_event_predecessor": (
        ("predecessor_event_id",),
        (f"{TABLE}.id",),
        "RESTRICT",
    ),
}
CHECKS = {
    "ck_t_grant_official_copy_event_scope",
    "ck_t_grant_official_copy_event_type",
    "ck_t_grant_official_copy_event_predecessor_shape",
    "ck_t_grant_official_copy_event_hashes",
    "ck_t_grant_official_copy_event_content_hash",
    "ck_t_grant_official_copy_event_current_key",
}
INDEXES = {
    "ix_t_grant_official_copy_event_evidence_stage": (
        "evidence_version_id",
        "event_type",
        "action_at",
    )
}


def _normalized_default(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip("()'")


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
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url)
    return config


@pytest.fixture
def carrier_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "grant-official-copy.db"
    config = _config(db_path, monkeypatch)
    command.upgrade(config, "head")
    engine = _engine(db_path)
    try:
        yield engine, config
    finally:
        engine.dispose()
        get_settings.cache_clear()


def _values(tag: str, **overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "id": f"official-event-{tag}",
        "evidence_version_id": EVIDENCE_ID,
        "source_config_id": "source-config-1",
        "source_record_id": "source-record-1",
        "role_config_id": "role-config-1",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "event_type": "ACQUIRED",
        "actor_id": "actor-acquirer",
        "action_at": NOW,
        "reason": "TEST ONLY",
        "original_reference": "TEST-ONLY-NO-OFFICIAL-CLAIM",
        "acquisition_method_snapshot": "TEST_ONLY",
        "evidence_content_hash": "e" * 64,
        "source_config_snapshot_hash": HASH_A,
        "source_snapshot_hash": HASH_B,
        "role_config_snapshot_hash": HASH_C,
        "predecessor_event_id": None,
        "event_snapshot": f'{{"test":"{tag}"}}',
        "event_snapshot_hash": HASH_D,
        "idempotency_key": f"official-event-{tag}",
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


def _seed(connection) -> None:
    for user_id in ("actor-acquirer", "selector", "creator", "updater", "role-admin"):
        connection.execute(
            text(
                "INSERT INTO t_user (id, username, password_hash, created_at, updated_at) "
                "VALUES (:id, :id, 'test-only', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"id": user_id},
        )
    for index in range(1, 6):
        connection.execute(
            text(
                "INSERT INTO t_role (id, code, name, created_at, updated_at) "
                "VALUES (:id, :code, :code, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"id": f"role-{index}", "code": f"TEST_ROLE_{index}"},
        )
    connection.execute(
        text(
            "INSERT INTO t_case (id, case_no, created_at, updated_at) "
            "VALUES ('case-1', 'TEST-CASE-1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )
    connection.execute(
        text(
            "INSERT INTO t_document (id, case_id, created_at, updated_at) "
            "VALUES ('document-1', 'case-1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )
    connection.execute(
        text(
            "INSERT INTO t_doc_attachment "
            "(id, document_id, file_name, file_path, created_at, updated_at) VALUES "
            "('attachment-1', 'document-1', 'official.pdf', '/test/official.pdf', "
            "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )
    connection.execute(
        text(
            "INSERT INTO t_document_evidence_version "
            "(id, case_id, document_id, attachment_id, lineage_key, role, version_number, "
            "state, creator_id, review_state, content_hash, current_identity_key) VALUES "
            "(:id, 'case-1', 'document-1', 'attachment-1', 'official-copy', "
            "'RAW_ATTACHMENT', 1, 'FINAL', 'creator', 'PENDING', :hash, 'official-copy|1')"
        ),
        {"id": EVIDENCE_ID, "hash": "e" * 64},
    )
    connection.execute(
        text(
            "INSERT INTO t_grant_evidence_source_record "
            "(id, source_authority, source_code, source_version, evidence_scope, "
            "source_reference_kind, source_reference_value, acquisition_method, effective_from, "
            "source_snapshot, source_snapshot_hash, review_status, activation_status, "
            "idempotency_key, created_by, updated_by) VALUES "
            "('source-record-1', 'CNIPA', 'TEST-SOURCE', 'v1', 'GRANT_ANNOUNCEMENT', "
            "'DATA', 'TEST ONLY', 'TEST_ONLY', :now, '{}', :hash, 'PENDING', 'INACTIVE', "
            "'source-record-1', 'creator', 'updater')"
        ),
        {"now": NOW, "hash": HASH_B},
    )
    connection.execute(
        text(
            "INSERT INTO t_grant_evidence_source_config "
            "(id, gate_code, scope_key, evidence_scope, source_record_id, config_version, "
            "config_status, effective_from, selected_by, published_at, selection_reason, "
            "config_snapshot, config_snapshot_hash, idempotency_key) VALUES "
            "('source-config-1', 'DG-GRANT-EVIDENCE-SOURCE', 'GLOBAL', "
            "'GRANT_ANNOUNCEMENT', 'source-record-1', 'v1', 'ACTIVE', :now, 'selector', :now, "
            "'TEST ONLY', '{}', :hash, 'source-config-1')"
        ),
        {"now": NOW, "hash": HASH_A},
    )
    connection.execute(
        text(
            "INSERT INTO t_grant_manual_review_role_config "
            "(id, gate_code, scope_key, official_copy_acquirer_role_id, first_verifier_role_id, "
            "second_verifier_role_id, manual_review_proposer_role_id, "
            "manual_review_second_reviewer_role_id, config_version, config_status, "
            "effective_from, confirmed_by, published_at, config_snapshot, config_snapshot_hash, "
            "idempotency_key) VALUES "
            "('role-config-1', 'DG-GRANT-MANUAL-REVIEW', 'GLOBAL', 'role-1', 'role-2', "
            "'role-3', 'role-4', 'role-5', 'v1', 'ACTIVE', :now, 'role-admin', :now, '{}', "
            ":hash, 'role-config-1')"
        ),
        {"now": NOW, "hash": HASH_C},
    )


def test_exact_orm_and_registry_contract() -> None:
    model = document_models.GrantOfficialCopyVerificationEvent
    table = model.__table__
    assert table.name == TABLE
    assert tuple(table.c.keys()) == tuple(COLUMNS)
    for name, (type_class, length, nullable, default) in COLUMNS.items():
        column = table.c[name]
        assert isinstance(column.type, type_class)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert _normalized_default(
            column.server_default.arg if column.server_default else None
        ) == default
    assert table.c.id.default is not None
    assert _model_uniques(table) == UNIQUES
    assert _model_fks(table) == FKS
    assert {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } == CHECKS
    assert {
        index.name: tuple(column.name for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index)
    } == INDEXES

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.db.base import Base\n"
            "from app.models import *\n"
            "assert GrantOfficialCopyVerificationEvent.__tablename__ == "
            "'t_grant_official_copy_verification_event'\n"
            "assert 't_grant_official_copy_verification_event' in Base.metadata.tables\n",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_migration_reflection_head_and_clean_zero_rows(carrier_db) -> None:
    engine, config = carrier_db
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
    columns = inspector.get_columns(TABLE)
    assert tuple(column["name"] for column in columns) == tuple(COLUMNS)
    for column in columns:
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


def test_valid_three_stage_chain_and_application_uuid(carrier_db) -> None:
    engine, _ = carrier_db
    with engine.begin() as connection:
        _seed(connection)
    model = document_models.GrantOfficialCopyVerificationEvent
    with Session(engine) as session:
        acquired = model(**{key: value for key, value in _values("acquired").items() if key != "id"})
        engine.dialect.insert_returning = False
        session.add(acquired)
        session.flush()
        assert str(UUID(acquired.id)) == acquired.id
        acquired.current_identity_key = None
        first = model(
            **_values(
                "first",
                event_type="FIRST_VERIFIED",
                actor_id="selector",
                action_at=NOW + timedelta(minutes=1),
                predecessor_event_id=acquired.id,
            )
        )
        session.add(first)
        session.flush()
        first.current_identity_key = None
        second = model(
            **_values(
                "second",
                event_type="SECOND_VERIFIED",
                actor_id="creator",
                action_at=NOW + timedelta(minutes=2),
                predecessor_event_id=first.id,
                current_identity_key=CURRENT_KEY,
            )
        )
        session.add(second)
        session.commit()
        assert second.current_identity_key == CURRENT_KEY


def test_constraints_uniques_foreign_keys_and_restricted_deletes(carrier_db) -> None:
    engine, _ = carrier_db
    with engine.begin() as connection:
        _seed(connection)
        _insert(connection, _values("base", current_identity_key=CURRENT_KEY))

    invalid = (
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": None},
        {"event_type": "OTHER", "predecessor_event_id": "official-event-base"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "missing-event"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "evidence_scope": "OTHER"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "source_config_snapshot_hash": "A" * 64},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "source_snapshot_hash": "short"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "role_config_snapshot_hash": "g" * 64},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "event_snapshot_hash": "short"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "evidence_content_hash": " bad"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "current_identity_key": "wrong"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "actor_id": "missing-user"},
        {"event_type": "FIRST_VERIFIED", "predecessor_event_id": "official-event-base", "source_config_id": "missing-config"},
    )
    for index, overrides in enumerate(invalid):
        _expect_integrity(engine, _values(f"invalid-{index}", **overrides))

    _expect_integrity(engine, _values("duplicate-stage"))
    _expect_integrity(
        engine,
        _values(
            "duplicate-idempotency",
            event_type="FIRST_VERIFIED",
            predecessor_event_id="official-event-base",
            idempotency_key="official-event-base",
        ),
    )
    _expect_integrity(
        engine,
        _values(
            "duplicate-current",
            event_type="FIRST_VERIFIED",
            predecessor_event_id="official-event-base",
            current_identity_key=CURRENT_KEY,
        ),
    )

    with engine.begin() as connection:
        connection.execute(
            text(f"UPDATE {TABLE} SET current_identity_key = NULL WHERE id = 'official-event-base'")
        )
        _insert(
            connection,
            _values(
                "first-valid",
                event_type="FIRST_VERIFIED",
                actor_id="selector",
                predecessor_event_id="official-event-base",
                current_identity_key=CURRENT_KEY,
            ),
        )

    for table, row_id in (
        ("t_document_evidence_version", EVIDENCE_ID),
        ("t_grant_evidence_source_config", "source-config-1"),
        ("t_grant_evidence_source_record", "source-record-1"),
        ("t_grant_manual_review_role_config", "role-config-1"),
        ("t_user", "actor-acquirer"),
        (TABLE, "official-event-base"),
    ):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": row_id})
