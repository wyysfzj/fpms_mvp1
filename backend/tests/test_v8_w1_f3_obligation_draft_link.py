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

REVISION = "v8_w1_f3_draft_item_link_01"
DOWN_REVISION = "v8_w1_f2_fee_obligation_line_01"
TABLE = "t_fee_obligation_draft_item_link"

COLUMNS = (
    "id",
    "obligation_line_id",
    "fee_item_id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)

STRING_LENGTHS = {
    "id": 36,
    "obligation_line_id": 36,
    "fee_item_id": 36,
    "created_by": 36,
    "updated_by": 36,
}

NULLABILITY = {
    "id": False,
    "obligation_line_id": False,
    "fee_item_id": False,
    "created_at": False,
    "updated_at": False,
    "created_by": True,
    "updated_by": True,
}

FK_SPECS = {
    "fk_t_fee_obligation_draft_item_link_obligation_line_id": (
        ("obligation_line_id",),
        ("t_fee_obligation_line.id",),
        "CASCADE",
    ),
    "fk_t_fee_obligation_draft_item_link_fee_item_id": (
        ("fee_item_id",),
        ("t_fee_item.id",),
        "CASCADE",
    ),
}

UNIQUE_SPECS = {
    "uq_t_fee_obligation_draft_item_link_pair": (
        "obligation_line_id",
        "fee_item_id",
    ),
}

PROHIBITED_COLUMNS = {
    "case_id",
    "draft_id",
    "activity_id",
    "amount",
    "status",
    "source",
    "payload",
    "idempotency_key",
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


def _insert_fee_draft(connection, *, draft_id: str, case_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_fee_draft (id, case_id) VALUES (:id, :case_id)"),
        {"id": draft_id, "case_id": case_id},
    )


def _insert_fee_item(connection, *, item_id: str, draft_id: str) -> None:
    connection.execute(
        text("INSERT INTO t_fee_item (id, draft_id) VALUES (:id, :draft_id)"),
        {"id": item_id, "draft_id": draft_id},
    )


def _insert_link(
    connection,
    *,
    link_id: str,
    obligation_line_id: str,
    fee_item_id: str,
) -> None:
    connection.execute(
        text(
            f"""
            INSERT INTO {TABLE} (id, obligation_line_id, fee_item_id)
            VALUES (:id, :obligation_line_id, :fee_item_id)
            """
        ),
        {
            "id": link_id,
            "obligation_line_id": obligation_line_id,
            "fee_item_id": fee_item_id,
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
    _insert_fee_draft(connection, draft_id="draft-a", case_id="case-a")
    _insert_fee_item(connection, item_id="item-a", draft_id="draft-a")
    _insert_fee_item(connection, item_id="item-b", draft_id="draft-a")


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


def test_draft_item_link_model_matches_frozen_contract() -> None:
    model = fee_models.FeeObligationDraftItemLink
    table = model.__table__

    assert tuple(table.columns.keys()) == COLUMNS
    assert PROHIBITED_COLUMNS.isdisjoint(table.columns.keys())
    assert AuditMixin not in model.__mro__
    assert not model.__mapper__.relationships

    for column_name, length in STRING_LENGTHS.items():
        column = table.c[column_name]
        assert isinstance(column.type, String)
        assert column.type.length == length
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


def test_clean_sqlite_upgrade_matches_frozen_link_contract(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f3_schema.db"
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


def test_uuid_endpoint_constraints_pair_uniqueness_and_carrier_cardinality(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "v8_w1_f3_constraints.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_endpoints(connection)

        with Session(engine) as session, session.begin():
            link = fee_models.FeeObligationDraftItemLink(
                obligation_line_id="line-a",
                fee_item_id="item-a",
            )
            session.add(link)
            session.flush()
            assert UUID(link.id)
            assert link.created_at is not None
            assert link.updated_at is not None

        with engine.begin() as connection:
            _insert_link(
                connection,
                link_id="link-line-a-item-b",
                obligation_line_id="line-a",
                fee_item_id="item-b",
            )
            _insert_link(
                connection,
                link_id="link-line-b-item-a",
                obligation_line_id="line-b",
                fee_item_id="item-a",
            )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-duplicate",
                    obligation_line_id="line-a",
                    fee_item_id="item-a",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-missing-line",
                    obligation_line_id="line-missing",
                    fee_item_id="item-a",
                )

        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                _insert_link(
                    connection,
                    link_id="link-missing-item",
                    obligation_line_id="line-a",
                    fee_item_id="item-missing",
                )

        with engine.connect() as connection:
            count = connection.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar_one()
        assert count == 3
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_deleting_either_endpoint_cascades_only_its_link(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "v8_w1_f3_cascade.db"
    config = _alembic_config(db_path, monkeypatch)
    engine = None
    try:
        command.upgrade(config, "head")
        engine = _sqlite_engine(db_path)
        with engine.begin() as connection:
            _seed_endpoints(connection)
            _insert_link(
                connection,
                link_id="link-delete-item",
                obligation_line_id="line-a",
                fee_item_id="item-a",
            )
            _insert_link(
                connection,
                link_id="link-delete-line",
                obligation_line_id="line-b",
                fee_item_id="item-b",
            )
            _insert_link(
                connection,
                link_id="link-unrelated-sentinel",
                obligation_line_id="line-a",
                fee_item_id="item-b",
            )

            connection.execute(text("DELETE FROM t_fee_item WHERE id = 'item-a'"))
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-delete-item'")
                ).scalar_one()
                == 0
            )
            assert (
                connection.execute(
                    text(f"SELECT COUNT(*) FROM {TABLE} WHERE id = 'link-delete-line'")
                ).scalar_one()
                == 1
            )
            assert (
                connection.execute(
                    text("SELECT COUNT(*) FROM t_fee_obligation_line WHERE id = 'line-a'")
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
                    text("SELECT COUNT(*) FROM t_fee_item WHERE id = 'item-b'")
                ).scalar_one()
                == 1
            )
    finally:
        if engine is not None:
            engine.dispose()
        get_settings.cache_clear()


def test_draft_item_link_migration_is_forward_only(tmp_path, monkeypatch) -> None:
    config = _alembic_config(tmp_path / "v8_w1_f3_forward_only.db", monkeypatch)
    migration = ScriptDirectory.from_config(config).get_revision(REVISION)

    assert migration is not None
    with pytest.raises(NotImplementedError, match="forward-only"):
        migration.module.downgrade()
