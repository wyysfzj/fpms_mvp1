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
from app.modules.system import models as system_models

REVISION = "v8_grant_source_carrier_01"
DOWN_REVISION = "v8_d31_overlay_conflict_01"
CURRENT_HEAD = "v8_w6_service_price_book_01"
SOURCE_TABLE = "t_grant_evidence_source_record"
CONFIG_TABLE = "t_grant_evidence_source_config"
CANDIDATE_TABLE = "t_grant_evidence_candidate"
TABLES = (SOURCE_TABLE, CONFIG_TABLE, CANDIDATE_TABLE)

SOURCE_COLUMNS = {
    "id": (String, 36, False, None),
    "source_authority": (String, 32, False, None),
    "source_code": (String, 64, False, None),
    "source_version": (String, 128, False, None),
    "evidence_scope": (String, 32, False, None),
    "source_reference_kind": (String, 32, False, None),
    "source_reference_value": (String, 512, False, None),
    "acquisition_method": (String, 64, False, None),
    "effective_from": (DateTime, None, False, None),
    "effective_to": (DateTime, None, True, None),
    "source_snapshot": (Text, None, False, None),
    "source_snapshot_hash": (String, 64, False, None),
    "review_status": (String, 32, False, "'PENDING'"),
    "reviewed_by": (String, 36, True, None),
    "reviewed_at": (DateTime, None, True, None),
    "review_reason": (Text, None, True, None),
    "activation_status": (String, 32, False, "'INACTIVE'"),
    "activated_by": (String, 36, True, None),
    "activated_at": (DateTime, None, True, None),
    "supersedes_source_id": (String, 36, True, None),
    "current_identity_key": (String, 128, True, None),
    "idempotency_key": (String, 128, False, None),
    "created_by": (String, 36, False, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_by": (String, 36, False, None),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}
CONFIG_COLUMNS = {
    "id": (String, 36, False, None),
    "gate_code": (String, 32, False, None),
    "scope_key": (String, 64, False, None),
    "evidence_scope": (String, 32, False, None),
    "source_record_id": (String, 36, False, None),
    "config_version": (String, 128, False, None),
    "config_status": (String, 32, False, None),
    "effective_from": (DateTime, None, False, None),
    "effective_to": (DateTime, None, True, None),
    "selected_by": (String, 36, False, None),
    "published_at": (DateTime, None, False, None),
    "selection_reason": (Text, None, False, None),
    "supersedes_config_id": (String, 36, True, None),
    "config_snapshot": (Text, None, False, None),
    "config_snapshot_hash": (String, 64, False, None),
    "idempotency_key": (String, 128, False, None),
    "current_identity_key": (String, 160, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}
CANDIDATE_COLUMNS = {
    "id": (String, 36, False, None),
    "case_id": (String, 36, False, None),
    "document_id": (String, 36, False, None),
    "evidence_version_id": (String, 36, False, None),
    "source_config_id": (String, 36, False, None),
    "source_record_id": (String, 36, False, None),
    "evidence_scope": (String, 32, False, None),
    "source_version_snapshot": (String, 128, False, None),
    "original_reference": (String, 512, False, None),
    "acquisition_method_snapshot": (String, 64, False, None),
    "acquired_at": (DateTime, None, False, None),
    "acquisition_snapshot": (Text, None, False, None),
    "acquisition_snapshot_hash": (String, 64, False, None),
    "candidate_snapshot": (Text, None, False, None),
    "candidate_snapshot_hash": (String, 64, False, None),
    "proposed_by": (String, 36, False, None),
    "proposed_at": (DateTime, None, False, None),
    "review_status": (String, 32, False, "'PENDING'"),
    "reviewer_id": (String, 36, True, None),
    "reviewed_at": (DateTime, None, True, None),
    "review_reason": (Text, None, True, None),
    "conflict_snapshot": (Text, None, True, None),
    "created_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
    "updated_at": (DateTime, None, False, "CURRENT_TIMESTAMP"),
}

SOURCE_UNIQUES = {
    "uq_t_grant_evidence_source_record_series_version": (
        "source_authority",
        "evidence_scope",
        "source_code",
        "source_version",
    ),
    "uq_t_grant_evidence_source_record_idempotency_key": ("idempotency_key",),
    "uq_t_grant_evidence_source_record_current_identity_key": ("current_identity_key",),
}
CONFIG_UNIQUES = {
    "uq_t_grant_evidence_source_config_version": (
        "gate_code",
        "scope_key",
        "evidence_scope",
        "config_version",
    ),
    "uq_t_grant_evidence_source_config_idempotency_key": ("idempotency_key",),
    "uq_t_grant_evidence_source_config_current_identity_key": ("current_identity_key",),
}
CANDIDATE_UNIQUES = {
    "uq_t_grant_evidence_candidate_evidence_version_id": ("evidence_version_id",),
}

SOURCE_FKS = {
    "fk_t_grant_evidence_source_record_created_by": (
        ("created_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_record_updated_by": (
        ("updated_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_record_reviewed_by": (
        ("reviewed_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_record_activated_by": (
        ("activated_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_record_supersedes_source_id": (
        ("supersedes_source_id",),
        (f"{SOURCE_TABLE}.id",),
        "RESTRICT",
    ),
}
CONFIG_FKS = {
    "fk_t_grant_evidence_source_config_source_record_id": (
        ("source_record_id",),
        (f"{SOURCE_TABLE}.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_config_selected_by": (
        ("selected_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_source_config_supersedes_config_id": (
        ("supersedes_config_id",),
        (f"{CONFIG_TABLE}.id",),
        "RESTRICT",
    ),
}
CANDIDATE_FKS = {
    "fk_t_grant_evidence_candidate_case_id": (
        ("case_id",),
        ("t_case.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_document_id": (
        ("document_id",),
        ("t_document.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_evidence_version_id": (
        ("evidence_version_id",),
        ("t_document_evidence_version.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_source_config_id": (
        ("source_config_id",),
        (f"{CONFIG_TABLE}.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_source_record_id": (
        ("source_record_id",),
        (f"{SOURCE_TABLE}.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_proposed_by": (
        ("proposed_by",),
        ("t_user.id",),
        "RESTRICT",
    ),
    "fk_t_grant_evidence_candidate_reviewer_id": (
        ("reviewer_id",),
        ("t_user.id",),
        "RESTRICT",
    ),
}

SOURCE_CHECKS = {
    "ck_t_grant_evidence_source_record_authority",
    "ck_t_grant_evidence_source_record_scope",
    "ck_t_grant_evidence_source_record_reference_kind",
    "ck_t_grant_evidence_source_record_hash_length",
    "ck_t_grant_evidence_source_record_interval",
    "ck_t_grant_evidence_source_record_review_status",
    "ck_t_grant_evidence_source_record_review_tuple",
    "ck_t_grant_evidence_source_record_activation_status",
    "ck_t_grant_evidence_source_record_activation_tuple",
}
CONFIG_CHECKS = {
    "ck_t_grant_evidence_source_config_gate",
    "ck_t_grant_evidence_source_config_scope",
    "ck_t_grant_evidence_source_config_status",
    "ck_t_grant_evidence_source_config_interval",
    "ck_t_grant_evidence_source_config_hash_length",
    "ck_t_grant_evidence_source_config_current_key",
}
CANDIDATE_CHECKS = {
    "ck_t_grant_evidence_candidate_scope",
    "ck_t_grant_evidence_candidate_acquisition_hash_length",
    "ck_t_grant_evidence_candidate_candidate_hash_length",
    "ck_t_grant_evidence_candidate_review_status",
    "ck_t_grant_evidence_candidate_review_tuple",
}
SOURCE_INDEXES = {
    "ix_t_grant_evidence_source_record_scope_interval": (
        "evidence_scope",
        "activation_status",
        "effective_from",
        "effective_to",
    )
}
CONFIG_INDEXES = {
    "ix_t_grant_evidence_source_config_scope_interval": (
        "scope_key",
        "evidence_scope",
        "config_status",
        "effective_from",
        "effective_to",
    )
}
CANDIDATE_INDEXES = {
    "ix_t_grant_evidence_candidate_document_review": (
        "document_id",
        "review_status",
        "proposed_at",
    )
}

NOW = datetime(2026, 8, 10, 12, 0, 0)
LATER = NOW + timedelta(days=1)
HASH_A = "a" * 64
HASH_B = "b" * 64


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


def _normalized_default(value) -> str | None:
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


def _reflected_fks(inspector, table: str):
    return {
        item["name"]: (
            tuple(item["constrained_columns"]),
            tuple(f"{item['referred_table']}.{column}" for column in item["referred_columns"]),
            item.get("options", {}).get("ondelete"),
        )
        for item in inspector.get_foreign_keys(table)
    }


def _assert_columns(table, specs) -> None:
    assert set(table.c) == {table.c[name] for name in specs}
    for name, (expected_type, length, nullable, server_default) in specs.items():
        column = table.c[name]
        assert isinstance(column.type, expected_type)
        assert getattr(column.type, "length", None) == length
        assert column.nullable is nullable
        assert getattr(column.type, "timezone", False) is False
        assert (
            _normalized_default(
                column.server_default.arg if column.server_default is not None else None
            )
            == server_default
        )


def _assert_reflected_table(
    inspector,
    table_name: str,
    columns,
    uniques,
    fks,
    checks,
    indexes,
) -> None:
    reflected = {column["name"]: column for column in inspector.get_columns(table_name)}
    assert set(reflected) == set(columns)
    for name, (expected_type, length, nullable, server_default) in columns.items():
        column = reflected[name]
        assert isinstance(column["type"], expected_type)
        assert getattr(column["type"], "length", None) == length
        assert column["nullable"] is nullable
        assert _normalized_default(column["default"]) == server_default
    assert tuple(inspector.get_pk_constraint(table_name)["constrained_columns"]) == ("id",)
    assert {
        item["name"]: tuple(item["column_names"])
        for item in inspector.get_unique_constraints(table_name)
    } == uniques
    assert _reflected_fks(inspector, table_name) == fks
    assert {item["name"] for item in inspector.get_check_constraints(table_name)} == checks
    assert {
        item["name"]: tuple(item["column_names"]) for item in inspector.get_indexes(table_name)
    } == indexes


def _insert_user(connection, user_id: str) -> None:
    connection.execute(
        text(
            "INSERT INTO t_user (id, username, password_hash, created_at, updated_at) "
            "VALUES (:id, :id, 'test-only', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {"id": user_id},
    )


def _source_values(source_id: str, **overrides):
    values = {
        "id": source_id,
        "source_authority": "CNIPA",
        "source_code": f"TEST-{source_id}",
        "source_version": "test-v1",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "source_reference_kind": "DATA",
        "source_reference_value": "TEST-ONLY-NO-OFFICIAL-CLAIM",
        "acquisition_method": "TEST_ONLY",
        "effective_from": NOW,
        "effective_to": None,
        "source_snapshot": "{}",
        "source_snapshot_hash": HASH_A,
        "review_status": "PENDING",
        "reviewed_by": None,
        "reviewed_at": None,
        "review_reason": None,
        "activation_status": "INACTIVE",
        "activated_by": None,
        "activated_at": None,
        "supersedes_source_id": None,
        "current_identity_key": None,
        "idempotency_key": f"source:{source_id}",
        "created_by": "creator",
        "updated_by": "updater",
    }
    values.update(overrides)
    return values


def _insert_source(connection, source_id: str, **overrides) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {SOURCE_TABLE}
                (id, source_authority, source_code, source_version, evidence_scope,
                 source_reference_kind, source_reference_value, acquisition_method,
                 effective_from, effective_to, source_snapshot, source_snapshot_hash,
                 review_status, reviewed_by, reviewed_at, review_reason,
                 activation_status, activated_by, activated_at, supersedes_source_id,
                 current_identity_key, idempotency_key, created_by, updated_by)
            VALUES
                (:id, :source_authority, :source_code, :source_version, :evidence_scope,
                 :source_reference_kind, :source_reference_value, :acquisition_method,
                 :effective_from, :effective_to, :source_snapshot, :source_snapshot_hash,
                 :review_status, :reviewed_by, :reviewed_at, :review_reason,
                 :activation_status, :activated_by, :activated_at, :supersedes_source_id,
                 :current_identity_key, :idempotency_key, :created_by, :updated_by)
            """
        ),
        _source_values(source_id, **overrides),
    )


def _config_values(config_id: str, **overrides):
    values = {
        "id": config_id,
        "gate_code": "DG-GRANT-EVIDENCE-SOURCE",
        "scope_key": "GLOBAL",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "source_record_id": "source-active",
        "config_version": f"test-{config_id}",
        "config_status": "ACTIVE",
        "effective_from": NOW,
        "effective_to": None,
        "selected_by": "selector",
        "published_at": NOW,
        "selection_reason": "TEST ONLY",
        "supersedes_config_id": None,
        "config_snapshot": "{}",
        "config_snapshot_hash": HASH_A,
        "idempotency_key": f"config:{config_id}",
        "current_identity_key": None,
    }
    values.update(overrides)
    return values


def _insert_config(connection, config_id: str, **overrides) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {CONFIG_TABLE}
                (id, gate_code, scope_key, evidence_scope, source_record_id,
                 config_version, config_status, effective_from, effective_to,
                 selected_by, published_at, selection_reason, supersedes_config_id,
                 config_snapshot, config_snapshot_hash, idempotency_key,
                 current_identity_key)
            VALUES
                (:id, :gate_code, :scope_key, :evidence_scope, :source_record_id,
                 :config_version, :config_status, :effective_from, :effective_to,
                 :selected_by, :published_at, :selection_reason, :supersedes_config_id,
                 :config_snapshot, :config_snapshot_hash, :idempotency_key,
                 :current_identity_key)
            """
        ),
        _config_values(config_id, **overrides),
    )


def _candidate_values(candidate_id: str, **overrides):
    values = {
        "id": candidate_id,
        "case_id": "case-1",
        "document_id": "document-1",
        "evidence_version_id": "evidence-1",
        "source_config_id": "config-active",
        "source_record_id": "source-active",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "source_version_snapshot": "test-v1",
        "original_reference": "TEST-ONLY-NO-OFFICIAL-CLAIM",
        "acquisition_method_snapshot": "TEST_ONLY",
        "acquired_at": NOW,
        "acquisition_snapshot": "{}",
        "acquisition_snapshot_hash": HASH_A,
        "candidate_snapshot": "{}",
        "candidate_snapshot_hash": HASH_B,
        "proposed_by": "proposer",
        "proposed_at": NOW,
        "review_status": "PENDING",
        "reviewer_id": None,
        "reviewed_at": None,
        "review_reason": None,
        "conflict_snapshot": None,
    }
    values.update(overrides)
    return values


def _insert_candidate(connection, candidate_id: str, **overrides) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {CANDIDATE_TABLE}
                (id, case_id, document_id, evidence_version_id, source_config_id,
                 source_record_id, evidence_scope, source_version_snapshot,
                 original_reference, acquisition_method_snapshot, acquired_at,
                 acquisition_snapshot, acquisition_snapshot_hash, candidate_snapshot,
                 candidate_snapshot_hash, proposed_by, proposed_at, review_status,
                 reviewer_id, reviewed_at, review_reason, conflict_snapshot)
            VALUES
                (:id, :case_id, :document_id, :evidence_version_id, :source_config_id,
                 :source_record_id, :evidence_scope, :source_version_snapshot,
                 :original_reference, :acquisition_method_snapshot, :acquired_at,
                 :acquisition_snapshot, :acquisition_snapshot_hash, :candidate_snapshot,
                 :candidate_snapshot_hash, :proposed_by, :proposed_at, :review_status,
                 :reviewer_id, :reviewed_at, :review_reason, :conflict_snapshot)
            """
        ),
        _candidate_values(candidate_id, **overrides),
    )


def _expect_integrity(engine, insert) -> None:
    with pytest.raises(IntegrityError), engine.begin() as connection:
        insert(connection)


def _insert_document_lineage(connection, *, suffix: str = "1") -> None:
    connection.execute(
        text(
            "INSERT INTO t_case (id, case_no, created_at, updated_at) "
            "VALUES (:id, :case_no, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {"id": f"case-{suffix}", "case_no": f"TEST-CASE-{suffix}"},
    )
    connection.execute(
        text(
            "INSERT INTO t_document (id, case_id, created_at, updated_at) "
            "VALUES (:id, :case_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {"id": f"document-{suffix}", "case_id": f"case-{suffix}"},
    )
    connection.execute(
        text(
            "INSERT INTO t_doc_attachment "
            "(id, document_id, file_name, file_path, created_at, updated_at) "
            "VALUES (:id, :document_id, 'test-only.pdf', '/test-only', "
            "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {"id": f"attachment-{suffix}", "document_id": f"document-{suffix}"},
    )
    connection.execute(
        text(
            "INSERT INTO t_document_evidence_version "
            "(id, case_id, document_id, attachment_id, lineage_key, role, "
            "version_number, state, creator_id, review_state, content_hash) "
            "VALUES (:id, :case_id, :document_id, :attachment_id, :lineage_key, "
            "'OFFICIAL_RAW', 1, 'ARCHIVED', 'test-only', 'PENDING', :content_hash)"
        ),
        {
            "id": f"evidence-{suffix}",
            "case_id": f"case-{suffix}",
            "document_id": f"document-{suffix}",
            "attachment_id": f"attachment-{suffix}",
            "lineage_key": f"test-lineage-{suffix}",
            "content_hash": f"test-content-{suffix}",
        },
    )


def test_orm_metadata_matches_the_exact_three_carrier_contract() -> None:
    source_model = getattr(system_models, "GrantEvidenceSourceRecord", None)
    config_model = getattr(system_models, "GrantEvidenceSourceConfig", None)
    candidate_model = getattr(document_models, "GrantEvidenceCandidate", None)
    assert source_model is not None, "GrantEvidenceSourceRecord ORM carrier is absent"
    assert config_model is not None, "GrantEvidenceSourceConfig ORM carrier is absent"
    assert candidate_model is not None, "GrantEvidenceCandidate ORM carrier is absent"

    tables = (
        (
            source_model.__table__,
            SOURCE_TABLE,
            SOURCE_COLUMNS,
            SOURCE_UNIQUES,
            SOURCE_FKS,
            SOURCE_CHECKS,
            SOURCE_INDEXES,
        ),
        (
            config_model.__table__,
            CONFIG_TABLE,
            CONFIG_COLUMNS,
            CONFIG_UNIQUES,
            CONFIG_FKS,
            CONFIG_CHECKS,
            CONFIG_INDEXES,
        ),
        (
            candidate_model.__table__,
            CANDIDATE_TABLE,
            CANDIDATE_COLUMNS,
            CANDIDATE_UNIQUES,
            CANDIDATE_FKS,
            CANDIDATE_CHECKS,
            CANDIDATE_INDEXES,
        ),
    )
    for table, name, columns, uniques, fks, checks, indexes in tables:
        assert table.name == name
        _assert_columns(table, columns)
        assert table.c.id.default is not None
        assert _model_uniques(table) == uniques
        assert _model_fks(table) == fks
        assert _model_checks(table) == checks
        assert _model_indexes(table) == indexes


def test_standard_model_bootstrap_registers_and_exports_source_carriers() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    command_text = """
from app.db.base import Base
from app.models import *

names = {table.name for table in Base.metadata.sorted_tables}
assert {
    "t_grant_evidence_source_record",
    "t_grant_evidence_source_config",
    "t_grant_evidence_candidate",
} <= names
assert GrantEvidenceSourceRecord.__tablename__ == "t_grant_evidence_source_record"
assert GrantEvidenceSourceConfig.__tablename__ == "t_grant_evidence_source_config"
"""
    completed = subprocess.run(
        [sys.executable, "-c", command_text],
        cwd=backend_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_clean_upgrade_and_sqlite_constraints_preserve_fail_closed_lineage(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "grant_evidence_source_carrier.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
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

        command.upgrade(config, DOWN_REVISION)
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_user(connection, "preserved-user")
        engine.dispose()
        engine = None

        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)
        _assert_reflected_table(
            inspector,
            SOURCE_TABLE,
            SOURCE_COLUMNS,
            SOURCE_UNIQUES,
            SOURCE_FKS,
            SOURCE_CHECKS,
            SOURCE_INDEXES,
        )
        _assert_reflected_table(
            inspector,
            CONFIG_TABLE,
            CONFIG_COLUMNS,
            CONFIG_UNIQUES,
            CONFIG_FKS,
            CONFIG_CHECKS,
            CONFIG_INDEXES,
        )
        _assert_reflected_table(
            inspector,
            CANDIDATE_TABLE,
            CANDIDATE_COLUMNS,
            CANDIDATE_UNIQUES,
            CANDIDATE_FKS,
            CANDIDATE_CHECKS,
            CANDIDATE_INDEXES,
        )
        with engine.begin() as connection:
            assert (
                connection.scalar(text("SELECT count(*) FROM t_user WHERE id = 'preserved-user'"))
                == 1
            )
            assert all(
                connection.scalar(text(f"SELECT count(*) FROM {table}")) == 0 for table in TABLES
            )
            for user_id in (
                "creator",
                "updater",
                "reviewer",
                "activator",
                "selector",
                "proposer",
                "candidate-reviewer",
            ):
                _insert_user(connection, user_id)

        source_model = system_models.GrantEvidenceSourceRecord
        engine.dialect.insert_returning = False
        with Session(engine) as session:
            uuid_values = _source_values("orm-uuid")
            uuid_values.pop("id")
            row = source_model(**uuid_values)
            assert row.id is None
            session.add(row)
            session.flush()
            assert str(UUID(row.id)) == row.id
            session.rollback()

        with engine.begin() as connection:
            for kind in ("DATA", "QUERY_CHANNEL", "FILE"):
                _insert_source(
                    connection,
                    f"kind-{kind.lower()}",
                    source_reference_kind=kind,
                )
            _insert_source(
                connection,
                "scope-a",
                source_code="SAME-SERIES",
                source_version="v1",
            )
            _insert_source(
                connection,
                "scope-b",
                source_code="SAME-SERIES",
                source_version="v1",
                evidence_scope="PATENT_REGISTER",
            )
            _insert_source(
                connection,
                "source-active",
                source_code="ACTIVE-SOURCE",
                review_status="APPROVED",
                reviewed_by="reviewer",
                reviewed_at=NOW,
                review_reason="TEST ONLY",
                activation_status="ACTIVE",
                activated_by="activator",
                activated_at=NOW,
                current_identity_key="CNIPA|GRANT_ANNOUNCEMENT|ACTIVE-SOURCE",
            )
            _insert_source(
                connection,
                "source-retired",
                source_code="RETIRED-SOURCE",
                review_status="APPROVED",
                reviewed_by="reviewer",
                reviewed_at=NOW,
                review_reason="TEST ONLY",
                activation_status="RETIRED",
                activated_by="activator",
                activated_at=NOW,
            )

        source_invalid = (
            {"source_authority": "OTHER"},
            {"evidence_scope": "OTHER"},
            {"source_reference_kind": "URL"},
            {"source_snapshot_hash": "short"},
            {"effective_to": NOW},
            {"review_status": "UNKNOWN"},
            {"reviewed_by": "reviewer"},
            {
                "review_status": "APPROVED",
                "reviewed_by": "reviewer",
                "reviewed_at": NOW,
                "review_reason": None,
            },
            {
                "review_status": "APPROVED",
                "reviewed_by": "creator",
                "reviewed_at": NOW,
                "review_reason": "SELF REVIEW",
            },
            {"activation_status": "UNKNOWN"},
            {
                "review_status": "REJECTED",
                "reviewed_by": "reviewer",
                "reviewed_at": NOW,
                "review_reason": "TEST REJECT",
                "activation_status": "ACTIVE",
                "activated_by": "activator",
                "activated_at": NOW,
                "current_identity_key": "CNIPA|GRANT_ANNOUNCEMENT|X",
            },
            {"created_by": "missing-user"},
            {"updated_by": "missing-user"},
            {"supersedes_source_id": "missing-source"},
        )
        for index, overrides in enumerate(source_invalid):
            _expect_integrity(
                engine,
                lambda connection, i=index, values=overrides: _insert_source(
                    connection,
                    f"invalid-source-{i}",
                    **values,
                ),
            )
        _expect_integrity(
            engine,
            lambda connection: _insert_source(
                connection,
                "duplicate-series",
                source_code="SAME-SERIES",
                source_version="v1",
            ),
        )
        _expect_integrity(
            engine,
            lambda connection: _insert_source(
                connection,
                "duplicate-idempotency",
                idempotency_key="source:scope-a",
            ),
        )
        _expect_integrity(
            engine,
            lambda connection: _insert_source(
                connection,
                "duplicate-current",
                source_code="OTHER-ACTIVE",
                review_status="APPROVED",
                reviewed_by="reviewer",
                reviewed_at=NOW,
                review_reason="TEST ONLY",
                activation_status="ACTIVE",
                activated_by="activator",
                activated_at=NOW,
                current_identity_key="CNIPA|GRANT_ANNOUNCEMENT|ACTIVE-SOURCE",
            ),
        )

        with engine.begin() as connection:
            _insert_config(
                connection,
                "config-active",
                current_identity_key=("DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT"),
            )
            _insert_config(
                connection,
                "config-revoked",
                evidence_scope="PATENT_REGISTER",
                source_record_id="scope-b",
                config_status="REVOKED",
                current_identity_key=("DG-GRANT-EVIDENCE-SOURCE|GLOBAL|PATENT_REGISTER"),
            )
            _insert_config(
                connection,
                "config-history",
                config_version="history-v1",
                supersedes_config_id="config-active",
            )

        config_invalid = (
            {"gate_code": "OTHER"},
            {"scope_key": "CASE:1"},
            {"evidence_scope": "OTHER"},
            {"config_status": "PENDING"},
            {"config_snapshot_hash": "short"},
            {"effective_to": NOW},
            {"current_identity_key": "wrong"},
            {"source_record_id": "missing-source"},
            {"selected_by": "missing-user"},
            {"supersedes_config_id": "missing-config"},
        )
        for index, overrides in enumerate(config_invalid):
            _expect_integrity(
                engine,
                lambda connection, i=index, values=overrides: _insert_config(
                    connection,
                    f"invalid-config-{i}",
                    **values,
                ),
            )
        _expect_integrity(
            engine,
            lambda connection: _insert_config(
                connection,
                "duplicate-version",
                config_version="test-config-active",
            ),
        )
        _expect_integrity(
            engine,
            lambda connection: _insert_config(
                connection,
                "duplicate-config-idempotency",
                idempotency_key="config:config-active",
            ),
        )
        _expect_integrity(
            engine,
            lambda connection: _insert_config(
                connection,
                "duplicate-config-current",
                config_version="different",
                current_identity_key=("DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT"),
            ),
        )

        with engine.begin() as connection:
            _insert_document_lineage(connection)
            _insert_document_lineage(connection, suffix="2")
            _insert_candidate(connection, "candidate-pending")
            _insert_candidate(
                connection,
                "candidate-approved",
                case_id="case-2",
                document_id="document-2",
                evidence_version_id="evidence-2",
                review_status="APPROVED",
                reviewer_id="candidate-reviewer",
                reviewed_at=LATER,
                review_reason="TEST ONLY",
                conflict_snapshot='{"test_only":true}',
            )

        candidate_invalid = (
            {"evidence_scope": "OTHER"},
            {"acquisition_snapshot_hash": "short"},
            {"candidate_snapshot_hash": "short"},
            {"review_status": "UNKNOWN"},
            {"reviewer_id": "candidate-reviewer"},
            {
                "review_status": "APPROVED",
                "reviewer_id": "candidate-reviewer",
                "reviewed_at": LATER,
                "review_reason": None,
            },
            {
                "review_status": "APPROVED",
                "reviewer_id": "proposer",
                "reviewed_at": LATER,
                "review_reason": "SELF REVIEW",
            },
            {"case_id": "missing-case"},
            {"document_id": "missing-document"},
            {"evidence_version_id": "missing-evidence"},
            {"source_config_id": "missing-config"},
            {"source_record_id": "missing-source"},
            {"proposed_by": "missing-user"},
        )
        for index, overrides in enumerate(candidate_invalid):
            _expect_integrity(
                engine,
                lambda connection, i=index, values=overrides: _insert_candidate(
                    connection,
                    f"invalid-candidate-{i}",
                    **{"evidence_version_id": f"invalid-evidence-{i}", **values},
                ),
            )
        _expect_integrity(
            engine,
            lambda connection: _insert_candidate(
                connection,
                "duplicate-evidence",
                evidence_version_id="evidence-1",
            ),
        )

        restricted_deletes = (
            ("t_case", "case-2"),
            ("t_document", "document-2"),
            ("t_document_evidence_version", "evidence-2"),
            (SOURCE_TABLE, "source-active"),
            (CONFIG_TABLE, "config-active"),
            ("t_user", "proposer"),
            ("t_user", "candidate-reviewer"),
        )
        for table, row_id in restricted_deletes:
            _expect_integrity(
                engine,
                lambda connection, name=table, value=row_id: connection.execute(
                    text(f"DELETE FROM {name} WHERE id = :id"), {"id": value}
                ),
            )

        with engine.begin() as connection:
            assert (
                connection.scalar(text("SELECT status FROM t_case WHERE id = 'case-2'"))
                == "NOT_FILED"
            )
            assert (
                connection.scalar(
                    text("SELECT count(*) FROM t_case_activity_event WHERE case_id = 'case-2'")
                )
                == 0
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()
