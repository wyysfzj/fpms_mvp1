from __future__ import annotations

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

REVISION = "v8_w1_f2_fee_obligation_line_01"
DOWN_REVISION = "v8_w1_f1_fee_obligation_01"
TABLE = "t_fee_obligation_line"

COLUMNS = (
    "id",
    "obligation_id",
    "case_id",
    "source_activity_id",
    "fee_code",
    "fee_name",
    "fee_year_key",
    "official_full_amount",
    "reduction_ratio",
    "payable_amount",
    "source_amount",
    "source_date",
    "difference_review_state",
    "current_identity_key",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "obligation_id": 36,
    "case_id": 36,
    "source_activity_id": 36,
    "fee_code": 64,
    "fee_name": 256,
    "difference_review_state": 32,
    "current_identity_key": 64,
    "created_by": 36,
    "updated_by": 36,
}

NUMERIC_SPECS = {
    "official_full_amount": (18, 2),
    "reduction_ratio": (5, 4),
    "payable_amount": (18, 2),
    "source_amount": (18, 2),
}

NULLABILITY = {
    "id": False,
    "obligation_id": False,
    "case_id": False,
    "source_activity_id": False,
    "fee_code": False,
    "fee_name": False,
    "fee_year_key": False,
    "official_full_amount": True,
    "reduction_ratio": False,
    "payable_amount": False,
    "source_amount": True,
    "source_date": True,
    "difference_review_state": False,
    "current_identity_key": True,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

FK_SPECS = {
    "fk_t_fee_obligation_line_case_id": (
        ("case_id",),
        ("t_case.id",),
        "CASCADE",
    ),
    "fk_t_fee_obligation_line_obligation_same_case": (
        ("case_id", "obligation_id"),
        ("t_fee_obligation.case_id", "t_fee_obligation.id"),
        "CASCADE",
    ),
    "fk_t_fee_obligation_line_source_activity_same_case": (
        ("case_id", "source_activity_id"),
        ("t_case_activity_event.case_id", "t_case_activity_event.id"),
        None,
    ),
}

UNIQUE_SPECS = {
    "uq_t_fee_obligation_line_current_identity_key": ("current_identity_key",),
}

PROHIBITED_COLUMNS = {
    "currency",
    "rate_id",
    "rate_version_id",
    "source_document_id",
    "fee_draft_item_id",
    "payment_evidence_id",
    "supersedes_line_id",
    "supersede_reason",
    "superseded_at",
    "superseded_by",
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


def _insert_obligation(
    connection,
    *,
    obligation_id: str,
    case_id: str,
    source_activity_id: str,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_fee_obligation
                (id, case_id, source_activity_id, fee_domain, obligation_type,
                 obligation_status, currency, source_status,
                 client_instruction_status, draft_status, payment_status,
                 official_evidence_status)
            VALUES
                (:id, :case_id, :source_activity_id, 'GOV', 'APPLICATION',
                 'RECOGNIZED', 'CNY', 'VERIFIED', 'PENDING', 'NOT_CREATED',
                 'UNPAID', 'PENDING')
            """
        ),
        {
            "id": obligation_id,
            "case_id": case_id,
            "source_activity_id": source_activity_id,
        },
    )


def _insert_line(
    connection,
    *,
    line_id: str,
    obligation_id: str,
    case_id: str,
    source_activity_id: str,
    fee_code: str,
    current_identity_key: str | None = None,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE}
                (id, obligation_id, case_id, source_activity_id, fee_code,
                 fee_name, fee_year_key, reduction_ratio, payable_amount,
                 difference_review_state, current_identity_key)
            VALUES
                (:id, :obligation_id, :case_id, :source_activity_id, :fee_code,
                 :fee_name, 0, 1.0000, 100.00, 'MATCHED',
                 :current_identity_key)
            """
        ),
        {
            "id": line_id,
            "obligation_id": obligation_id,
            "case_id": case_id,
            "source_activity_id": source_activity_id,
            "fee_code": fee_code,
            "fee_name": f"Fee {fee_code}",
            "current_identity_key": current_identity_key,
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


def test_fee_obligation_line_model_matches_frozen_contract() -> None:
    model = fee_models.FeeObligationLine
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert PROHIBITED_COLUMNS.isdisjoint(table.columns.keys())
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length
    for column_name, (precision, scale) in NUMERIC_SPECS.items():
        column = table.c[column_name]
        assert isinstance(column.type, Numeric)
        assert (column.type.precision, column.type.scale) == (precision, scale)
    assert isinstance(table.c.fee_year_key.type, Integer)
    assert isinstance(table.c.source_date.type, Date)
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


def test_clean_sqlite_upgrade_matches_frozen_line_contract(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f2_schema.db"
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
        for column_name, (precision, scale) in NUMERIC_SPECS.items():
            column_type = by_name[column_name]["type"]
            assert isinstance(column_type, Numeric)
            assert (column_type.precision, column_type.scale) == (precision, scale)
        assert isinstance(by_name["fee_year_key"]["type"], Integer)
        assert isinstance(by_name["source_date"]["type"], Date)
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


def test_application_uuid_explicit_year_zero_nullable_facts_and_multiple_null_keys(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f2_nullable.db"
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
            _insert_obligation(
                connection,
                obligation_id="obligation-nullable",
                case_id="case-nullable",
                source_activity_id="activity-nullable",
            )

        with Session(engine) as session:
            common = {
                "obligation_id": "obligation-nullable",
                "case_id": "case-nullable",
                "source_activity_id": "activity-nullable",
                "fee_year_key": 0,
                "official_full_amount": None,
                "reduction_ratio": Decimal("1.0000"),
                "payable_amount": Decimal("100.00"),
                "source_amount": None,
                "source_date": None,
                "difference_review_state": "SOURCE_PENDING",
                "current_identity_key": None,
            }
            first = fee_models.FeeObligationLine(
                fee_code="SERVICE-A",
                fee_name="Service A",
                **common,
            )
            second = fee_models.FeeObligationLine(
                fee_code="SERVICE-B",
                fee_name="Service B",
                **common,
            )
            session.add_all([first, second])
            session.flush()

            assert UUID(first.id)
            assert UUID(second.id)
            assert first.fee_year_key == 0
            rows = (
                session.execute(
                    text(
                        f"""
                    SELECT current_identity_key, official_full_amount, source_amount,
                           source_date, created_at, updated_at
                    FROM {TABLE} ORDER BY fee_code
                    """
                    )
                )
                .mappings()
                .all()
            )
            assert len(rows) == 2
            assert all(row["current_identity_key"] is None for row in rows)
            assert all(row["official_full_amount"] is None for row in rows)
            assert all(row["source_amount"] is None for row in rows)
            assert all(row["source_date"] is None for row in rows)
            assert all(row["created_at"] is not None for row in rows)
            assert all(row["updated_at"] is not None for row in rows)
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_same_case_references_identity_uniqueness_and_required_year(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f2_constraints.db"
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
            _insert_obligation(
                connection,
                obligation_id="obligation-a",
                case_id="case-a",
                source_activity_id="activity-a",
            )
            _insert_obligation(
                connection,
                obligation_id="obligation-b",
                case_id="case-b",
                source_activity_id="activity-b",
            )
            _insert_line(
                connection,
                line_id="line-valid",
                obligation_id="obligation-a",
                case_id="case-a",
                source_activity_id="activity-a",
                fee_code="FEE-A",
                current_identity_key="a" * 64,
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_line(
                    connection,
                    line_id="line-missing-obligation",
                    obligation_id="obligation-missing",
                    case_id="case-a",
                    source_activity_id="activity-a",
                    fee_code="MISSING-OBLIGATION",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_line(
                    connection,
                    line_id="line-cross-case-obligation",
                    obligation_id="obligation-a",
                    case_id="case-b",
                    source_activity_id="activity-b",
                    fee_code="CROSS-OBLIGATION",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_line(
                    connection,
                    line_id="line-missing-activity",
                    obligation_id="obligation-a",
                    case_id="case-a",
                    source_activity_id="activity-missing",
                    fee_code="MISSING-ACTIVITY",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_line(
                    connection,
                    line_id="line-cross-case-activity",
                    obligation_id="obligation-b",
                    case_id="case-b",
                    source_activity_id="activity-a",
                    fee_code="CROSS-ACTIVITY",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_line(
                    connection,
                    line_id="line-duplicate-key",
                    obligation_id="obligation-a",
                    case_id="case-a",
                    source_activity_id="activity-a",
                    fee_code="DUPLICATE-KEY",
                    current_identity_key="a" * 64,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        f"""
                        INSERT INTO {TABLE}
                            (id, obligation_id, case_id, source_activity_id,
                             fee_code, fee_name, reduction_ratio, payable_amount,
                             difference_review_state)
                        VALUES
                            ('line-missing-year', 'obligation-a', 'case-a',
                             'activity-a', 'NO-YEAR', 'No year', 1.0000,
                             100.00, 'MATCHED')
                        """
                    )
                )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_fee_obligation_line_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_f2_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
