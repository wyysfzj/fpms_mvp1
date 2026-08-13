from __future__ import annotations

from datetime import datetime
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
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin
from app.modules.annuity import models as annuity_models

REVISION = "v8_w5_pay_list_export_artifact_01"
DOWN_REVISION = "v8_w4_official_rate_book_01"
CURRENT_HEAD = "v8_w6_service_price_book_01"
TABLE = "t_pay_list_export_artifact"
COLUMNS = (
    "id",
    "pay_list_id",
    "kind",
    "status",
    "content_sha256",
    "managed_storage_path",
    "template_version",
    "generated_by",
    "generated_at",
    "idempotency_key",
    "official_acceptance_evidence_ref",
    "official_acceptance_evidence_hash",
    "official_accepted_at",
    "updated_at",
)
STRING_LENGTHS = {
    "id": 36,
    "kind": 32,
    "status": 32,
    "content_sha256": 64,
    "template_version": 128,
    "generated_by": 36,
    "idempotency_key": 128,
    "official_acceptance_evidence_ref": 512,
    "official_acceptance_evidence_hash": 64,
}
NULLABLE = {
    "id": False,
    "pay_list_id": False,
    "kind": False,
    "status": False,
    "content_sha256": False,
    "managed_storage_path": False,
    "template_version": True,
    "generated_by": False,
    "generated_at": False,
    "idempotency_key": False,
    "official_acceptance_evidence_ref": True,
    "official_acceptance_evidence_hash": True,
    "official_accepted_at": True,
    "updated_at": False,
}
CHECKS = {
    "ck_t_pay_list_export_artifact_kind": "kind IN ('INTERNAL_XLSX', 'OFFICIAL_XLSM')",
    "ck_t_pay_list_export_artifact_status": ("status IN ('GENERATED', 'OFFICIAL_SITE_ACCEPTED')"),
    "ck_t_pay_list_export_artifact_content_sha256": "length(content_sha256) = 64",
    "ck_t_pay_list_export_artifact_acceptance_hash": (
        "official_acceptance_evidence_hash IS NULL "
        "OR length(official_acceptance_evidence_hash) = 64"
    ),
    "ck_t_pay_list_export_artifact_kind_payload": (
        "(kind = 'INTERNAL_XLSX' AND template_version IS NULL) "
        "OR (kind = 'OFFICIAL_XLSM' AND template_version IS NOT NULL)"
    ),
    "ck_t_pay_list_export_artifact_acceptance_tuple": (
        "(status = 'GENERATED' "
        "AND official_acceptance_evidence_ref IS NULL "
        "AND official_acceptance_evidence_hash IS NULL "
        "AND official_accepted_at IS NULL) "
        "OR (status = 'OFFICIAL_SITE_ACCEPTED' "
        "AND kind = 'OFFICIAL_XLSM' "
        "AND official_acceptance_evidence_ref IS NOT NULL "
        "AND official_acceptance_evidence_hash IS NOT NULL "
        "AND official_accepted_at IS NOT NULL)"
    ),
}


def _normalized(value: object) -> str:
    return " ".join(str(value).replace("\n", " ").split())


def _alembic_config(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", db_url)
    return config


def _migrated_engine(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    command.upgrade(_alembic_config(db_path, monkeypatch), "head")
    engine = create_engine(f"sqlite:///{db_path}", future=True)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _seed_parents(engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO t_user "
                "(id, username, password_hash, is_active, created_at, updated_at) "
                "VALUES ('artifact-user', 'artifact-user', 'x', 1, "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO t_client "
                "(id, name_cn, client_type, default_currency, is_active, "
                "created_at, updated_at) VALUES "
                "('artifact-client', '载体测试客户', 'CLIENT', 'CNY', 1, "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO t_pay_list "
                "(id, client_id, status, currency, total_amount, created_at, updated_at) "
                "VALUES (9001, 'artifact-client', 'DRAFT', 'CNY', 0, "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), "
                "(9002, 'artifact-client', 'DRAFT', 'CNY', 0, "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )


def _artifact(**overrides):
    values = {
        "pay_list_id": 9001,
        "kind": "INTERNAL_XLSX",
        "status": "GENERATED",
        "content_sha256": "a" * 64,
        "managed_storage_path": "managed/pay-list.xlsx",
        "template_version": None,
        "generated_by": "artifact-user",
        "idempotency_key": "artifact-key",
        "official_acceptance_evidence_ref": None,
        "official_acceptance_evidence_hash": None,
        "official_accepted_at": None,
    }
    values.update(overrides)
    return annuity_models.PayListExportArtifact(**values)


def test_frozen_model_and_revision_contract() -> None:
    model = annuity_models.PayListExportArtifact
    assert issubclass(model, UUIDPrimaryKeyMixin)
    assert not issubclass(model, AuditMixin)

    table = model.__table__
    assert table.name == TABLE
    assert tuple(table.columns.keys()) == COLUMNS
    assert {column.name: column.nullable for column in table.columns} == NULLABLE
    assert isinstance(table.c.pay_list_id.type, Integer)
    assert isinstance(table.c.managed_storage_path.type, Text)
    assert isinstance(table.c.generated_at.type, DateTime)
    assert table.c.generated_at.type.timezone is False
    assert isinstance(table.c.official_accepted_at.type, DateTime)
    assert table.c.official_accepted_at.type.timezone is False
    assert isinstance(table.c.updated_at.type, DateTime)
    assert table.c.updated_at.type.timezone is False
    assert tuple(column.name for column in table.primary_key.columns) == ("id",)
    assert {name: table.c[name].type.length for name in STRING_LENGTHS} == STRING_LENGTHS
    assert _normalized(table.c.generated_at.server_default.arg) == "CURRENT_TIMESTAMP"
    assert _normalized(table.c.updated_at.server_default.arg) == "CURRENT_TIMESTAMP"
    for name in ("kind", "status", "idempotency_key"):
        assert table.c[name].default is None
        assert table.c[name].server_default is None

    foreign_keys = {
        constraint.name: (
            tuple(element.parent.name for element in constraint.elements),
            tuple(element.target_fullname for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert foreign_keys == {
        "fk_t_pay_list_export_artifact_pay_list_id": (
            ("pay_list_id",),
            ("t_pay_list.id",),
            "CASCADE",
        ),
        "fk_t_pay_list_export_artifact_generated_by": (
            ("generated_by",),
            ("t_user.id",),
            "RESTRICT",
        ),
    }
    assert {
        constraint.name: tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    } == {
        "uq_t_pay_list_export_artifact_pay_list_idempotency_key": (
            "pay_list_id",
            "idempotency_key",
        )
    }
    assert {
        constraint.name: _normalized(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } == {name: _normalized(expression) for name, expression in CHECKS.items()}
    assert {
        index.name: (tuple(column.name for column in index.columns), index.unique)
        for index in table.indexes
    } == {
        "ix_t_pay_list_export_artifact_pay_list_generated_at": (
            ("pay_list_id", "generated_at"),
            False,
        )
    }

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert heads == [CURRENT_HEAD]
    assert REVISION in {
        item.revision for item in script.walk_revisions(base="base", head=CURRENT_HEAD)
    }
    revision = script.get_revision(REVISION)
    assert revision is not None
    assert revision.down_revision == DOWN_REVISION


def test_clean_sqlite_reflection_matches_frozen_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _migrated_engine(tmp_path / "schema.db", monkeypatch)
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(TABLE)
        assert tuple(column["name"] for column in columns) == COLUMNS
        assert {column["name"]: column["nullable"] for column in columns} == NULLABLE
        reflected = {column["name"]: column["type"] for column in columns}
        assert isinstance(reflected["pay_list_id"], Integer)
        assert isinstance(reflected["managed_storage_path"], Text)
        for name in (
            "generated_at",
            "official_accepted_at",
            "updated_at",
        ):
            assert isinstance(reflected[name], DateTime)
            assert reflected[name].timezone is False
        assert {name: reflected[name].length for name in STRING_LENGTHS} == STRING_LENGTHS
        primary_key = inspector.get_pk_constraint(TABLE)
        assert primary_key["name"] is None
        assert tuple(primary_key["constrained_columns"]) == ("id",)
        assert {
            column["name"]: _normalized(column["default"])
            for column in columns
            if column["default"] is not None
        } == {
            "generated_at": "CURRENT_TIMESTAMP",
            "updated_at": "CURRENT_TIMESTAMP",
        }
        assert {
            item["name"]: (
                tuple(item["constrained_columns"]),
                tuple(f"{item['referred_table']}.{column}" for column in item["referred_columns"]),
                item["options"].get("ondelete"),
            )
            for item in inspector.get_foreign_keys(TABLE)
        } == {
            "fk_t_pay_list_export_artifact_pay_list_id": (
                ("pay_list_id",),
                ("t_pay_list.id",),
                "CASCADE",
            ),
            "fk_t_pay_list_export_artifact_generated_by": (
                ("generated_by",),
                ("t_user.id",),
                "RESTRICT",
            ),
        }
        assert {
            item["name"]: tuple(item["column_names"])
            for item in inspector.get_unique_constraints(TABLE)
        } == {
            "uq_t_pay_list_export_artifact_pay_list_idempotency_key": (
                "pay_list_id",
                "idempotency_key",
            )
        }
        assert {
            item["name"]: _normalized(item["sqltext"])
            for item in inspector.get_check_constraints(TABLE)
        } == {name: _normalized(expression) for name, expression in CHECKS.items()}
        assert {
            item["name"]: (tuple(item["column_names"]), item["unique"])
            for item in inspector.get_indexes(TABLE)
        } == {
            "ix_t_pay_list_export_artifact_pay_list_generated_at": (
                ("pay_list_id", "generated_at"),
                0,
            )
        }
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_invalid_payloads_fail_frozen_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_payloads = (
        {"kind": "CSV"},
        {"status": "UPLOADED"},
        {"content_sha256": "a" * 63},
        {"kind": "INTERNAL_XLSX", "template_version": "v1"},
        {"kind": "OFFICIAL_XLSM", "template_version": None},
        {"official_acceptance_evidence_ref": "unexpected"},
        {"official_acceptance_evidence_hash": "b" * 64},
        {"official_accepted_at": datetime(2026, 7, 14)},
        {
            "kind": "OFFICIAL_XLSM",
            "template_version": "v1",
            "status": "OFFICIAL_SITE_ACCEPTED",
        },
        {
            "kind": "OFFICIAL_XLSM",
            "template_version": "v1",
            "status": "OFFICIAL_SITE_ACCEPTED",
            "official_acceptance_evidence_ref": "official/ref",
            "official_acceptance_evidence_hash": "b" * 63,
            "official_accepted_at": datetime(2026, 7, 14),
        },
    )
    engine = _migrated_engine(tmp_path / "invalid.db", monkeypatch)
    try:
        _seed_parents(engine)
        for overrides in invalid_payloads:
            with Session(engine) as transaction:
                transaction.add(_artifact(**overrides))
                with pytest.raises(IntegrityError):
                    transaction.commit()
    finally:
        engine.dispose()
        get_settings.cache_clear()


def test_valid_rows_uuid_uniqueness_foreign_keys_and_delete_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = _migrated_engine(tmp_path / "behavior.db", monkeypatch)
    try:
        _seed_parents(engine)
        with Session(engine) as transaction:
            internal = _artifact(idempotency_key="shared-key")
            official_generated = _artifact(
                pay_list_id=9002,
                kind="OFFICIAL_XLSM",
                template_version="cnipa-v1",
                idempotency_key="shared-key",
            )
            official_accepted = _artifact(
                kind="OFFICIAL_XLSM",
                status="OFFICIAL_SITE_ACCEPTED",
                content_sha256="a" * 64,
                template_version="cnipa-v1",
                idempotency_key="accepted-key",
                official_acceptance_evidence_ref="official/accepted/ref",
                official_acceptance_evidence_hash="b" * 64,
                official_accepted_at=datetime(2026, 7, 14, 9, 30),
            )
            transaction.add_all((internal, official_generated, official_accepted))
            transaction.flush()
            UUID(internal.id)
            assert internal.generated_at is not None
            assert internal.updated_at is not None
            transaction.commit()

        with Session(engine) as transaction:
            transaction.add(_artifact(idempotency_key="shared-key"))
            with pytest.raises(IntegrityError):
                transaction.commit()

        for overrides in (
            {"pay_list_id": 9999, "idempotency_key": "missing-list"},
            {"generated_by": "missing-user", "idempotency_key": "missing-user"},
        ):
            with Session(engine) as transaction:
                transaction.add(_artifact(**overrides))
                with pytest.raises(IntegrityError):
                    transaction.commit()

        with engine.begin() as connection:
            with pytest.raises(IntegrityError):
                connection.execute(text("DELETE FROM t_user WHERE id = 'artifact-user'"))
            connection.execute(text("DELETE FROM t_pay_list WHERE id = 9001"))
            assert (
                connection.scalar(
                    text("SELECT count(*) FROM t_pay_list_export_artifact WHERE pay_list_id = 9001")
                )
                == 0
            )
            assert (
                connection.scalar(
                    text("SELECT count(*) FROM t_pay_list_export_artifact WHERE pay_list_id = 9002")
                )
                == 1
            )
    finally:
        engine.dispose()
        get_settings.cache_clear()
