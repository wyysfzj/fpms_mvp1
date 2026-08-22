from __future__ import annotations

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

REVISION = "v8_w1_f1_fee_obligation_01"
DOWN_REVISION = "v8_w1_d3_workpkg_evidence_01"
TABLE = "t_fee_obligation"

COLUMNS = (
    "id",
    "case_id",
    "source_activity_id",
    "source_document_id",
    "fee_domain",
    "obligation_type",
    "obligation_status",
    "due_date",
    "currency",
    "source_status",
    "client_instruction_status",
    "draft_status",
    "payment_status",
    "official_evidence_status",
    "supersedes_obligation_id",
    "supersede_reason",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "case_id": 36,
    "source_activity_id": 36,
    "source_document_id": 36,
    "fee_domain": 16,
    "obligation_type": 64,
    "obligation_status": 32,
    "currency": 8,
    "source_status": 32,
    "client_instruction_status": 32,
    "draft_status": 32,
    "payment_status": 32,
    "official_evidence_status": 32,
    "supersedes_obligation_id": 36,
    "created_by": 36,
    "updated_by": 36,
}

NULLABILITY = {
    "id": False,
    "case_id": False,
    "source_activity_id": False,
    "source_document_id": True,
    "fee_domain": False,
    "obligation_type": False,
    "obligation_status": False,
    "due_date": True,
    "currency": False,
    "source_status": False,
    "client_instruction_status": False,
    "draft_status": False,
    "payment_status": False,
    "official_evidence_status": False,
    "supersedes_obligation_id": True,
    "supersede_reason": True,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

FK_SPECS = {
    "fk_t_fee_obligation_case_id": (
        ("case_id",),
        ("t_case.id",),
        "CASCADE",
    ),
    "fk_t_fee_obligation_source_document_id": (
        ("source_document_id",),
        ("t_document.id",),
        None,
    ),
    "fk_t_fee_obligation_source_activity_same_case": (
        ("case_id", "source_activity_id"),
        ("t_case_activity_event.case_id", "t_case_activity_event.id"),
        None,
    ),
    "fk_t_fee_obligation_supersedes_same_case": (
        ("case_id", "supersedes_obligation_id"),
        ("t_fee_obligation.case_id", "t_fee_obligation.id"),
        None,
    ),
}

UNIQUE_SPECS = {
    "uq_t_fee_obligation_case_id": ("case_id", "id"),
}

F2_OR_LATER_COLUMNS = {
    "amount",
    "official_amount",
    "source_amount",
    "fee_code",
    "fee_name",
    "fee_year",
    "year_no",
    "reduction_rate",
    "reduction_amount",
    "difference_review_status",
    "current_identity_key",
    "fee_draft_item_id",
    "payment_evidence_id",
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


def _insert_activity(connection, *, activity_id: str, case_id: str, sequence: int) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_case_activity_event
                (id, case_id, sequence, lane, activity_type, effective_at,
                 confirmation_status, actor_id, idempotency_key, payload_json)
            VALUES
                (:id, :case_id, :sequence, 'FEE', 'FEE_RECOGNIZED',
                 '2026-07-13 12:00:00', 'CONFIRMED', 'actor-1',
                 :idempotency_key, '{}')
            """
        ),
        {
            "id": activity_id,
            "case_id": case_id,
            "sequence": sequence,
            "idempotency_key": f"fee:{activity_id}",
        },
    )


def _insert_document(connection, *, document_id: str, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_document (id, case_id) VALUES (:id, :case_id)"),
        {"id": document_id, "case_id": case_id},
    )


def _insert_obligation(
    connection,
    *,
    obligation_id: str,
    case_id: str,
    source_activity_id: str,
    source_document_id: str | None = None,
    due_date_value: str | None = None,
    supersedes_obligation_id: str | None = None,
    supersede_reason: str | None = None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, case_id, source_activity_id, source_document_id, fee_domain,
                 obligation_type, obligation_status, due_date, currency,
                 source_status, client_instruction_status, draft_status,
                 payment_status, official_evidence_status,
                 supersedes_obligation_id, supersede_reason)
            VALUES
                (:id, :case_id, :source_activity_id, :source_document_id, 'GOV',
                 'APPLICATION', 'RECOGNIZED', :due_date, 'CNY', 'VERIFIED',
                 'PENDING', 'NOT_CREATED', 'UNPAID', 'PENDING',
                 :supersedes_obligation_id, :supersede_reason)
            """
        ),
        {
            "id": obligation_id,
            "case_id": case_id,
            "source_activity_id": source_activity_id,
            "source_document_id": source_document_id,
            "due_date": due_date_value,
            "supersedes_obligation_id": supersedes_obligation_id,
            "supersede_reason": supersede_reason,
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


def test_fee_obligation_model_matches_frozen_header_contract() -> None:
    model = fee_models.FeeObligation
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert F2_OR_LATER_COLUMNS.isdisjoint(table.columns.keys())
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length

    assert isinstance(table.c.due_date.type, Date)
    assert isinstance(table.c.supersede_reason.type, Text)
    for column_name in ("created_at", "updated_at"):
        assert isinstance(table.c[column_name].type, DateTime)
        assert table.c[column_name].type.timezone is False

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
    assert not any(isinstance(constraint, CheckConstraint) for constraint in table.constraints)
    assert not table.indexes


def test_clean_sqlite_upgrade_matches_frozen_header_contract(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f1_schema.db"
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
        assert F2_OR_LATER_COLUMNS.isdisjoint(by_name)
        for column_name, length in STRING_LENGTHS.items():
            assert isinstance(by_name[column_name]["type"], String)
            assert by_name[column_name]["type"].length == length
        assert isinstance(by_name["due_date"]["type"], Date)
        assert isinstance(by_name["supersede_reason"]["type"], Text)
        for column_name in ("created_at", "updated_at"):
            assert isinstance(by_name[column_name]["type"], DateTime)

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
        assert inspector.get_indexes(TABLE) == []
        assert inspector.get_check_constraints(TABLE) == []
        with engine.connect() as connection:
            triggers = connection.execute(
                text(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'trigger' AND tbl_name = :table_name
                    """
                ),
                {"table_name": TABLE},
            ).all()
        assert triggers == []
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_application_uuid_and_nullable_source_due_and_supersede_fields(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f1_nullable.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _insert_case(connection, case_id="case-nullable")
            _insert_activity(
                connection,
                activity_id="activity-nullable",
                case_id="case-nullable",
                sequence=1,
            )

        with Session(engine) as session:
            obligation = fee_models.FeeObligation(
                case_id="case-nullable",
                source_activity_id="activity-nullable",
                source_document_id=None,
                fee_domain="SERVICE",
                obligation_type="CONSULTING",
                obligation_status="RECOGNIZED",
                due_date=None,
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PENDING",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="NOT_APPLICABLE",
                supersedes_obligation_id=None,
                supersede_reason=None,
            )
            session.add(obligation)
            session.flush()

            assert UUID(obligation.id)
            row = (
                session.execute(
                    text(
                        f"""
                    SELECT source_document_id, due_date, supersedes_obligation_id,
                           supersede_reason, created_at, updated_at
                    FROM {TABLE} WHERE id = :id
                    """
                    ),
                    {"id": obligation.id},
                )
                .mappings()
                .one()
            )
            assert row["source_document_id"] is None
            assert row["due_date"] is None
            assert row["supersedes_obligation_id"] is None
            assert row["supersede_reason"] is None
            assert row["created_at"] is not None
            assert row["updated_at"] is not None
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_source_document_activity_and_supersede_constraints(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f1_constraints.db"
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
            _insert_document(connection, document_id="document-a", case_id="case-a")
            _insert_obligation(
                connection,
                obligation_id="obligation-a",
                case_id="case-a",
                source_activity_id="activity-a",
                source_document_id="document-a",
            )
            _insert_obligation(
                connection,
                obligation_id="obligation-a-correction",
                case_id="case-a",
                source_activity_id="activity-a",
                supersedes_obligation_id="obligation-a",
                supersede_reason="corrected source",
            )

        with engine.connect() as connection:
            correction = (
                connection.execute(
                    text(
                        f"""
                    SELECT supersedes_obligation_id, supersede_reason
                    FROM {TABLE} WHERE id = 'obligation-a-correction'
                    """
                    )
                )
                .mappings()
                .one()
            )
        assert dict(correction) == {
            "supersedes_obligation_id": "obligation-a",
            "supersede_reason": "corrected source",
        }

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_obligation(
                    connection,
                    obligation_id="missing-activity",
                    case_id="case-a",
                    source_activity_id="activity-missing",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_obligation(
                    connection,
                    obligation_id="cross-case-activity",
                    case_id="case-b",
                    source_activity_id="activity-a",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_obligation(
                    connection,
                    obligation_id="missing-document",
                    case_id="case-a",
                    source_activity_id="activity-a",
                    source_document_id="document-missing",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_obligation(
                    connection,
                    obligation_id="cross-case-supersede",
                    case_id="case-b",
                    source_activity_id="activity-b",
                    supersedes_obligation_id="obligation-a",
                    supersede_reason="must remain same-case",
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_fee_obligation_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_f1_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
