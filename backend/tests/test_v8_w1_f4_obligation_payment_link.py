from __future__ import annotations

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
    Integer,
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

REVISION = "v8_w1_f4_payment_link_01"
DOWN_REVISION = "v8_w1_f3_draft_item_link_01"
TABLE = "t_fee_obligation_payment_evidence_link"

COLUMNS = (
    "id",
    "obligation_line_id",
    "gov_payment_id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "obligation_line_id": 36,
    "created_by": 36,
    "updated_by": 36,
}

NULLABILITY = {
    "id": False,
    "obligation_line_id": False,
    "gov_payment_id": False,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

FK_SPECS = {
    "fk_t_fee_obligation_payment_evidence_link_obligation_line_id": (
        ("obligation_line_id",),
        ("t_fee_obligation_line.id",),
        "CASCADE",
    ),
    "fk_t_fee_obligation_payment_evidence_link_gov_payment_id": (
        ("gov_payment_id",),
        ("t_gov_payment.id",),
        "CASCADE",
    ),
}

UNIQUE_SPECS = {
    "uq_t_fee_obligation_payment_evidence_link_pair": (
        "obligation_line_id",
        "gov_payment_id",
    ),
}

PROHIBITED_COLUMNS = {
    "case_id",
    "obligation_id",
    "pay_list_id",
    "fee_item_id",
    "receipt_id",
    "receipt_attachment_id",
    "document_id",
    "document_evidence_version_id",
    "object_type",
    "object_id",
    "official_evidence_status",
    "payment_amount",
    "payment_status",
    "linked_at",
    "linked_by",
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


def _insert_activity(connection, *, activity_id: str, case_id: str) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_case_activity_event
                (id, case_id, sequence, lane, activity_type, effective_at,
                 confirmation_status, actor_id, idempotency_key, payload_json)
            VALUES
                (:id, :case_id, 1, 'FEE', 'FEE_RECOGNIZED',
                 '2026-07-13 12:00:00', 'CONFIRMED', 'actor-1',
                 :idempotency_key, '{}')
            """
        ),
        {
            "id": activity_id,
            "case_id": case_id,
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
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_fee_obligation_line
                (id, obligation_id, case_id, source_activity_id, fee_code,
                 fee_name, fee_year_key, reduction_ratio, payable_amount,
                 difference_review_state)
            VALUES
                (:id, :obligation_id, :case_id, :source_activity_id, :fee_code,
                 :fee_name, 0, 1.0000, 100.00, 'MATCHED')
            """
        ),
        {
            "id": line_id,
            "obligation_id": obligation_id,
            "case_id": case_id,
            "source_activity_id": source_activity_id,
            "fee_code": fee_code,
            "fee_name": f"Fee {fee_code}",
        },
    )


def _insert_client(connection, *, client_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_client (id, name_cn) VALUES (:id, :name_cn)"),
        {"id": client_id, "name_cn": client_id},
    )


def _insert_pay_list(connection, *, pay_list_id: int, client_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_pay_list (id, client_id) VALUES (:id, :client_id)"),
        {"id": pay_list_id, "client_id": client_id},
    )


def _insert_gov_payment(
    connection,
    *,
    payment_id: int,
    pay_list_id: int,
    case_id: str,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO t_gov_payment (id, pay_list_id, case_id)
            VALUES (:id, :pay_list_id, :case_id)
            """
        ),
        {"id": payment_id, "pay_list_id": pay_list_id, "case_id": case_id},
    )


def _insert_link(
    connection,
    *,
    link_id: str,
    obligation_line_id: str,
    gov_payment_id: int,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE} (id, obligation_line_id, gov_payment_id)
            VALUES (:id, :obligation_line_id, :gov_payment_id)
            """
        ),
        {
            "id": link_id,
            "obligation_line_id": obligation_line_id,
            "gov_payment_id": gov_payment_id,
        },
    )


def _seed_endpoints(connection) -> None:
    _insert_case(connection, case_id="case-a")
    _insert_activity(connection, activity_id="activity-a", case_id="case-a")
    _insert_obligation(
        connection,
        obligation_id="obligation-a",
        case_id="case-a",
        source_activity_id="activity-a",
    )
    _insert_line(
        connection,
        line_id="line-a",
        obligation_id="obligation-a",
        case_id="case-a",
        source_activity_id="activity-a",
        fee_code="FEE-A",
    )
    _insert_line(
        connection,
        line_id="line-b",
        obligation_id="obligation-a",
        case_id="case-a",
        source_activity_id="activity-a",
        fee_code="FEE-B",
    )
    _insert_client(connection, client_id="client-a")
    _insert_pay_list(connection, pay_list_id=101, client_id="client-a")
    _insert_pay_list(connection, pay_list_id=102, client_id="client-a")
    _insert_gov_payment(connection, payment_id=201, pay_list_id=101, case_id="case-a")
    _insert_gov_payment(connection, payment_id=202, pay_list_id=102, case_id="case-a")


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


def test_payment_evidence_link_model_matches_frozen_contract() -> None:
    model = fee_models.FeeObligationPaymentEvidenceLink
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert PROHIBITED_COLUMNS.isdisjoint(table.columns.keys())
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length
    assert isinstance(table.c.gov_payment_id.type, Integer)
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


def test_clean_sqlite_upgrade_matches_frozen_payment_link_contract(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f4_schema.db"
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
        assert isinstance(by_name["gov_payment_id"]["type"], Integer)
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
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_uuid_parent_constraints_pair_uniqueness_and_carrier_cardinality(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f4_constraints.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_endpoints(connection)

        with Session(engine) as session, session.begin():
            link = fee_models.FeeObligationPaymentEvidenceLink(
                obligation_line_id="line-a",
                gov_payment_id=201,
            )
            session.add(link)
            session.flush()
            assert UUID(link.id)
            assert link.created_at is not None
            assert link.updated_at is not None

        with engine.begin() as connection:
            _insert_link(
                connection,
                link_id="link-line-a-payment-202",
                obligation_line_id="line-a",
                gov_payment_id=202,
            )
            _insert_link(
                connection,
                link_id="link-line-b-payment-201",
                obligation_line_id="line-b",
                gov_payment_id=201,
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-duplicate",
                    obligation_line_id="line-a",
                    gov_payment_id=201,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-missing-line",
                    obligation_line_id="line-missing",
                    gov_payment_id=201,
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-missing-payment",
                    obligation_line_id="line-a",
                    gov_payment_id=999,
                )

        with engine.connect() as connection:
            count = connection.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar_one()
        assert count == 3
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_deleting_either_endpoint_cascades_only_related_links(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f4_cascade.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_endpoints(connection)
            _insert_link(
                connection,
                link_id="link-delete-payment",
                obligation_line_id="line-a",
                gov_payment_id=201,
            )
            _insert_link(
                connection,
                link_id="link-delete-line",
                obligation_line_id="line-b",
                gov_payment_id=202,
            )
            _insert_link(
                connection,
                link_id="link-unrelated-sentinel",
                obligation_line_id="line-a",
                gov_payment_id=202,
            )

            connection.execute(text("DELETE FROM t_gov_payment WHERE id = 201"))
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-delete-payment'")
                ).scalar_one()
                == 0
            )
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-delete-line'")
                ).scalar_one()
                == 1
            )

            connection.execute(text("DELETE FROM t_fee_obligation_line WHERE id = 'line-b'"))
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-delete-line'")
                ).scalar_one()
                == 0
            )
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-unrelated-sentinel'")
                ).scalar_one()
                == 1
            )
            assert (
                connection.execute(
                    text("SELECT COUNT(*) FROM t_gov_payment WHERE id = 202")
                ).scalar_one()
                == 1
            )
            assert (
                connection.execute(
                    text("SELECT COUNT(*) FROM t_fee_obligation_line WHERE id = 'line-a'")
                ).scalar_one()
                == 1
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_payment_evidence_link_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_f4_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
