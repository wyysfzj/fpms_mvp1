from __future__ import annotations

import importlib
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403

PACKAGE_TABLES = {
    "t_official_work_package",
    "t_official_work_package_checklist",
    "t_official_work_package_manifest",
    "t_official_work_package_receipt",
    "t_official_work_package_override",
}
PACKAGE_STATUSES = {
    "PREPARING",
    "NEEDS_MAINTENANCE",
    "NEEDS_CONFIRMATION",
    "READY_FOR_EXTERNAL_SUBMIT",
    "SUBMITTED",
    "WAITING_RECEIPT",
    "ARCHIVED",
    "EXCEPTION",
    "OVERRIDE",
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


def _models_module():
    return importlib.import_module("app.modules.official_workflows.models")


def _schemas_module():
    return importlib.import_module("app.modules.official_workflows.schemas")


def test_official_work_package_models_create_required_tables(tmp_path) -> None:
    models = _models_module()
    db_path = tmp_path / "official_work_package_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert models.OfficialWorkPackage.__tablename__ == "t_official_work_package"
    inspector = inspect(engine)
    assert PACKAGE_TABLES <= set(inspector.get_table_names())

    package_columns = {
        column["name"] for column in inspector.get_columns("t_official_work_package")
    }
    assert {
        "case_id",
        "package_kind",
        "status",
        "source_document_id",
        "reply_document_id",
        "external_system",
        "remark",
    } <= package_columns

    receipt_columns = {
        column["name"] for column in inspector.get_columns("t_official_work_package_receipt")
    }
    assert {
        "package_id",
        "receipt_kind",
        "receipt_attachment_id",
        "receiving_case_no",
        "submitter",
        "received_at",
        "received_file_list",
    } <= receipt_columns

    override_columns = {
        column["name"] for column in inspector.get_columns("t_official_work_package_override")
    }
    assert {"override_reason", "override_by", "override_at", "follow_up_note"} <= override_columns

    engine.dispose()


def test_official_work_package_schemas_support_required_kinds_and_statuses() -> None:
    schemas = _schemas_module()

    assert {"FILING_PREP", "OA_REPLY"} <= set(schemas.OFFICIAL_WORK_PACKAGE_KINDS)
    assert PACKAGE_STATUSES <= set(schemas.OFFICIAL_WORK_PACKAGE_STATUSES)

    package = schemas.OfficialWorkPackageOut(
        id="pkg-1",
        case_id="case-1",
        package_kind="OA_REPLY",
        status="WAITING_RECEIPT",
        source_document_id="oa-in-1",
        reply_document_id="oa-out-1",
        external_system="CNIPA_WEB",
        remark="等待电子申请回执",
    )
    receipt = schemas.OfficialWorkPackageReceiptOut(
        id="receipt-1",
        package_id="pkg-1",
        receipt_kind="ELECTRONIC_APPLICATION_RECEIPT",
        receipt_attachment_id="att-1",
        receiving_case_no="202605310001",
        submitter="流程人员A",
        received_at=datetime(2026, 5, 31, 10, 30, 0),
        received_file_list='["意见陈述书","权利要求书"]',
    )

    assert package.package_kind == "OA_REPLY"
    assert package.status == "WAITING_RECEIPT"
    assert receipt.receipt_attachment_id == "att-1"
    assert receipt.received_file_list == '["意见陈述书","权利要求书"]'


def test_official_work_package_migration_creates_tables(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "official_work_package_migration.db"
    db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parents[1] / "alembic"),
    )
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = _sqlite_engine(db_path)
    inspector = inspect(engine)
    assert PACKAGE_TABLES <= set(inspector.get_table_names())

    receipt_columns = {
        column["name"] for column in inspector.get_columns("t_official_work_package_receipt")
    }
    assert {
        "receipt_attachment_id",
        "receiving_case_no",
        "submitter",
        "received_at",
        "received_file_list",
    } <= receipt_columns

    engine.dispose()
