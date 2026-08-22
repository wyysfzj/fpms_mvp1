from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Numeric,
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
from app.db.mixins import AuditMixin
from app.modules.fees import models as fee_models

REVISION = "v8_w1_f5_fee_reduction_01"
DOWN_REVISION = "v8_w1_f4_payment_link_01"
TABLE = "t_fee_reduction_approval"

COLUMNS = (
    "id",
    "scope_type",
    "case_id",
    "applicant_set_key",
    "reduction_ratio",
    "fee_scope_snapshot",
    "fee_scope_hash",
    "fee_year_from",
    "fee_year_to",
    "effective_from",
    "effective_to",
    "source_evidence_version_id",
    "confirmation_status",
    "confirmed_at",
    "confirmed_by",
    "eligibility_snapshot",
    "eligibility_snapshot_hash",
    "approval_identity_key",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "scope_type": 32,
    "case_id": 36,
    "applicant_set_key": 64,
    "fee_scope_hash": 64,
    "source_evidence_version_id": 36,
    "confirmation_status": 32,
    "confirmed_by": 36,
    "eligibility_snapshot_hash": 64,
    "approval_identity_key": 64,
    "created_by": 36,
    "updated_by": 36,
}

NULLABILITY = {
    "id": False,
    "scope_type": False,
    "case_id": True,
    "applicant_set_key": True,
    "reduction_ratio": False,
    "fee_scope_snapshot": False,
    "fee_scope_hash": False,
    "fee_year_from": True,
    "fee_year_to": True,
    "effective_from": False,
    "effective_to": True,
    "source_evidence_version_id": False,
    "confirmation_status": False,
    "confirmed_at": True,
    "confirmed_by": True,
    "eligibility_snapshot": False,
    "eligibility_snapshot_hash": False,
    "approval_identity_key": False,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

FK_SPECS = {
    "fk_t_fee_reduction_approval_case_id": (
        ("case_id",),
        ("t_case.id",),
        "CASCADE",
    ),
    "fk_t_fee_reduction_approval_source_evidence_version_id": (
        ("source_evidence_version_id",),
        ("t_document_evidence_version.id",),
        None,
    ),
}

UNIQUE_SPECS = {
    "uq_t_fee_reduction_approval_identity_key": ("approval_identity_key",),
}

SCOPE_CHECK = (
    "(scope_type = 'CASE' AND case_id IS NOT NULL AND applicant_set_key IS NULL) OR "
    "(scope_type = 'APPLICANT_SET' AND case_id IS NULL AND applicant_set_key IS NOT NULL)"
)

PROHIBITED_COLUMNS = {
    "source_document_id",
    "obligation_id",
    "amount",
    "payable_ratio",
    "rate_id",
    "rate_version_id",
    "is_current",
    "supersedes_approval_id",
    "supersede_reason",
    "superseded_at",
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


def _insert_document(connection, *, document_id: str, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_document (id, case_id) VALUES (:id, :case_id)"),
        {"id": document_id, "case_id": case_id},
    )


def _insert_attachment(connection, *, attachment_id: str, document_id: str) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_doc_attachment (id, document_id, file_name, file_path)
            VALUES (:id, :document_id, :file_name, :file_path)
            """
        ),
        {
            "id": attachment_id,
            "document_id": document_id,
            "file_name": f"{attachment_id}.pdf",
            "file_path": f"/evidence/{attachment_id}.pdf",
        },
    )


def _insert_evidence_version(
    connection,
    *,
    evidence_id: str,
    case_id: str,
    document_id: str,
    attachment_id: str,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_document_evidence_version
                (id, case_id, document_id, attachment_id, lineage_key, role,
                 version_number, state, creator_id, review_state, content_hash)
            VALUES
                (:id, :case_id, :document_id, :attachment_id, 'reduction-source',
                 'OFFICIAL_NOTICE', 1, 'FINAL', 'creator-1', 'APPROVED',
                 :content_hash)
            """
        ),
        {
            "id": evidence_id,
            "case_id": case_id,
            "document_id": document_id,
            "attachment_id": attachment_id,
            "content_hash": f"hash:{evidence_id}",
        },
    )


def _seed_evidence(connection) -> None:
    _insert_case(connection, case_id="case-a")
    _insert_document(connection, document_id="document-a", case_id="case-a")
    _insert_attachment(
        connection,
        attachment_id="attachment-a",
        document_id="document-a",
    )
    _insert_evidence_version(
        connection,
        evidence_id="evidence-a",
        case_id="case-a",
        document_id="document-a",
        attachment_id="attachment-a",
    )


def _insert_approval(
    connection,
    *,
    approval_id: str,
    scope_type: str,
    case_id: str | None,
    applicant_set_key: str | None,
    source_evidence_version_id: str,
    approval_identity_key: str | None,
    fee_year_from: int | None = None,
    fee_year_to: int | None = None,
    effective_to: str | None = None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, scope_type, case_id, applicant_set_key, reduction_ratio,
                 fee_scope_snapshot, fee_scope_hash, fee_year_from, fee_year_to,
                 effective_from, effective_to, source_evidence_version_id,
                 confirmation_status, confirmed_at, confirmed_by,
                 eligibility_snapshot, eligibility_snapshot_hash,
                 approval_identity_key)
            VALUES
                (:id, :scope_type, :case_id, :applicant_set_key, 0.7000,
                 '{{"fees":["APPLICATION"]}}', :fee_scope_hash,
                 :fee_year_from, :fee_year_to, '2026-01-01', :effective_to,
                 :source_evidence_version_id, 'CONFIRMED',
                 '2026-07-13 12:00:00', 'reviewer-1',
                 '{{"applicants":["applicant-a"]}}', :eligibility_hash,
                 :approval_identity_key)
            """
        ),
        {
            "id": approval_id,
            "scope_type": scope_type,
            "case_id": case_id,
            "applicant_set_key": applicant_set_key,
            "fee_scope_hash": "f" * 64,
            "fee_year_from": fee_year_from,
            "fee_year_to": fee_year_to,
            "effective_to": effective_to,
            "source_evidence_version_id": source_evidence_version_id,
            "eligibility_hash": "e" * 64,
            "approval_identity_key": approval_identity_key,
        },
    )


def _model_fk_specs(table) -> dict[str, tuple[tuple[str, ...], tuple[str, ...], str | None]]:
    return {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }


def _normalized_default(value) -> str | None:
    if value is None:
        return None
    return str(value).strip("()")


def _normalized_sql(value) -> str:
    return " ".join(str(value).split())


def test_fee_reduction_approval_model_matches_frozen_contract() -> None:
    model = fee_models.FeeReductionApproval
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert PROHIBITED_COLUMNS.isdisjoint(table.columns.keys())
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length
    assert isinstance(table.c.reduction_ratio.type, Numeric)
    assert (table.c.reduction_ratio.type.precision, table.c.reduction_ratio.type.scale) == (5, 4)
    for column_name in ("fee_year_from", "fee_year_to"):
        assert isinstance(table.c[column_name].type, Integer)
    for column_name in ("effective_from", "effective_to"):
        assert isinstance(table.c[column_name].type, Date)
    for column_name in ("confirmed_at", "created_at", "updated_at"):
        assert isinstance(table.c[column_name].type, DateTime)
        assert table.c[column_name].type.timezone is False
    for column_name in ("fee_scope_snapshot", "eligibility_snapshot"):
        assert isinstance(table.c[column_name].type, Text)

    assert {column.name: column.nullable for column in table.columns} == NULLABILITY
    assert table.c.id.default is not None
    assert table.c.id.server_default is None
    for column in table.columns:
        if column.name == "id":
            continue
        assert column.default is None
        expected_default = (
            "CURRENT_TIMESTAMP" if column.name in {"created_at", "updated_at"} else None
        )
        actual_default = (
            _normalized_default(column.server_default.arg)
            if column.server_default is not None
            else None
        )
        assert actual_default == expected_default

    assert tuple(table.primary_key.columns.keys()) == ("id",)
    assert _model_fk_specs(table) == FK_SPECS
    assert {
        constraint.name: tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    } == UNIQUE_SPECS
    assert {
        constraint.name: _normalized_sql(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } == {"ck_t_fee_reduction_approval_scope_exclusive": SCOPE_CHECK}
    assert not table.indexes


def test_clean_sqlite_upgrade_matches_frozen_approval_contract(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f5_schema.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        migration = ScriptDirectory.from_config(config).get_revision(REVISION)
        assert migration is not None
        assert migration.down_revision == DOWN_REVISION

        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        inspector = inspect(engine)
        columns = inspector.get_columns(TABLE)
        by_name = {column["name"]: column for column in columns}

        assert tuple(column["name"] for column in columns) == COLUMNS
        assert PROHIBITED_COLUMNS.isdisjoint(by_name)
        for column_name, length in STRING_LENGTHS.items():
            assert isinstance(by_name[column_name]["type"], String)
            assert by_name[column_name]["type"].length == length
        ratio_type = by_name["reduction_ratio"]["type"]
        assert isinstance(ratio_type, Numeric)
        assert (ratio_type.precision, ratio_type.scale) == (5, 4)
        for column_name in ("fee_year_from", "fee_year_to"):
            assert isinstance(by_name[column_name]["type"], Integer)
        for column_name in ("effective_from", "effective_to"):
            assert isinstance(by_name[column_name]["type"], Date)
        for column_name in ("confirmed_at", "created_at", "updated_at"):
            assert isinstance(by_name[column_name]["type"], DateTime)
        for column_name in ("fee_scope_snapshot", "eligibility_snapshot"):
            assert isinstance(by_name[column_name]["type"], Text)

        assert {name: column["nullable"] for name, column in by_name.items()} == NULLABILITY
        assert {
            name: _normalized_default(column["default"]) for name, column in by_name.items()
        } == {
            name: "CURRENT_TIMESTAMP" if name in {"created_at", "updated_at"} else None
            for name in COLUMNS
        }
        assert inspector.get_pk_constraint(TABLE)["constrained_columns"] == ["id"]

        reflected_fks = {
            item["name"]: (
                tuple(item["constrained_columns"]),
                tuple(f"{item['referred_table']}.{column}" for column in item["referred_columns"]),
                item.get("options", {}).get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        }
        assert reflected_fks == FK_SPECS
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == UNIQUE_SPECS
        assert {
            item["name"]: _normalized_sql(item["sqltext"])
            for item in inspector.get_check_constraints(TABLE)
        } == {"ck_t_fee_reduction_approval_scope_exclusive": SCOPE_CHECK}
        assert inspector.get_indexes(TABLE) == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_uuid_and_valid_case_and_applicant_set_scope_rows(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f5_valid_scopes.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_evidence(connection)

        with Session(engine) as session, session.begin():
            approval = fee_models.FeeReductionApproval(
                scope_type="CASE",
                case_id="case-a",
                applicant_set_key=None,
                reduction_ratio=Decimal("0.7000"),
                fee_scope_snapshot='{"fees":["APPLICATION"]}',
                fee_scope_hash="f" * 64,
                fee_year_from=None,
                fee_year_to=None,
                effective_from=date(2026, 1, 1),
                effective_to=None,
                source_evidence_version_id="evidence-a",
                confirmation_status="CONFIRMED",
                confirmed_at=datetime(2026, 7, 13, 12, 0, 0),
                confirmed_by="reviewer-1",
                eligibility_snapshot='{"case":"case-a"}',
                eligibility_snapshot_hash="e" * 64,
                approval_identity_key="a" * 64,
            )
            session.add(approval)
            session.flush()
            assert UUID(approval.id)
            assert approval.created_at is not None
            assert approval.updated_at is not None

        with engine.begin() as connection:
            _insert_approval(
                connection,
                approval_id="approval-applicant-set",
                scope_type="APPLICANT_SET",
                case_id=None,
                applicant_set_key="s" * 64,
                source_evidence_version_id="evidence-a",
                approval_identity_key="b" * 64,
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_scope_foreign_keys_nonnull_identity_and_identity_uniqueness(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f5_constraints.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_evidence(connection)
            _insert_approval(
                connection,
                approval_id="approval-identity-base",
                scope_type="APPLICANT_SET",
                case_id=None,
                applicant_set_key="s" * 64,
                source_evidence_version_id="evidence-a",
                approval_identity_key="d" * 64,
            )

        invalid_scopes = (
            ("CASE", None, None),
            ("CASE", "case-a", "s" * 64),
            ("CASE", None, "s" * 64),
            ("APPLICANT_SET", None, None),
            ("APPLICANT_SET", "case-a", "s" * 64),
            ("APPLICANT_SET", "case-a", None),
            ("UNKNOWN", "case-a", None),
        )
        for index, (scope_type, case_id, applicant_set_key) in enumerate(invalid_scopes, 1):
            with pytest.raises(IntegrityError):
                with engine.begin() as connection:
                    _insert_approval(
                        connection,
                        approval_id=f"approval-invalid-scope-{index}",
                        scope_type=scope_type,
                        case_id=case_id,
                        applicant_set_key=applicant_set_key,
                        source_evidence_version_id="evidence-a",
                        approval_identity_key=f"{index:064x}",
                    )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_approval(
                    connection,
                    approval_id="approval-missing-case",
                    scope_type="CASE",
                    case_id="case-missing",
                    applicant_set_key=None,
                    source_evidence_version_id="evidence-a",
                    approval_identity_key="c" * 64,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_approval(
                    connection,
                    approval_id="approval-missing-evidence",
                    scope_type="CASE",
                    case_id="case-a",
                    applicant_set_key=None,
                    source_evidence_version_id="evidence-missing",
                    approval_identity_key="e" * 64,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_approval(
                    connection,
                    approval_id="approval-null-identity",
                    scope_type="CASE",
                    case_id="case-a",
                    applicant_set_key=None,
                    source_evidence_version_id="evidence-a",
                    approval_identity_key=None,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_approval(
                    connection,
                    approval_id="approval-duplicate-identity",
                    scope_type="APPLICANT_SET",
                    case_id=None,
                    applicant_set_key="s" * 64,
                    source_evidence_version_id="evidence-a",
                    approval_identity_key="d" * 64,
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_fee_reduction_approval_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_f5_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
