from __future__ import annotations

from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.documents.models import DocAttachment
from app.modules.documents.schemas import DocAttachmentOut

ATTACHMENT_MANIFEST_COLUMNS = {
    "official_file_role",
    "source_role_alias",
    "external_upload_position",
    "content_hash",
    "package_usage_hint",
    "is_archive_evidence",
    "is_receipt_evidence",
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


def test_doc_attachment_model_exposes_official_manifest_carriers(tmp_path) -> None:
    db_path = tmp_path / "attachment_manifest_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    attachment_columns = set(DocAttachment.__table__.columns.keys())
    assert ATTACHMENT_MANIFEST_COLUMNS <= attachment_columns

    inspector = inspect(engine)
    db_columns = {column["name"] for column in inspector.get_columns("t_doc_attachment")}
    assert ATTACHMENT_MANIFEST_COLUMNS <= db_columns

    engine.dispose()


def test_doc_attachment_output_schema_preserves_manifest_metadata() -> None:
    attachment = DocAttachmentOut(
        id="att-1",
        document_id="doc-1",
        file_name="权利要求书.pdf",
        mime_type="application/pdf",
        file_size=128,
        uploaded_at=datetime(2026, 5, 31, 10, 0, 0),
        official_file_role="CLAIMS",
        source_role_alias="权利要求书",
        external_upload_position="OA_REPLY_ATTACHMENTS",
        content_hash="sha256:abc123",
        package_usage_hint="OA_REPLY",
        is_archive_evidence=False,
        is_receipt_evidence=False,
    )

    assert attachment.model_dump(include=ATTACHMENT_MANIFEST_COLUMNS) == {
        "official_file_role": "CLAIMS",
        "source_role_alias": "权利要求书",
        "external_upload_position": "OA_REPLY_ATTACHMENTS",
        "content_hash": "sha256:abc123",
        "package_usage_hint": "OA_REPLY",
        "is_archive_evidence": False,
        "is_receipt_evidence": False,
    }


def test_doc_attachment_output_schema_keeps_legacy_payload_optional() -> None:
    attachment = DocAttachmentOut(
        id="att-legacy",
        document_id="doc-legacy",
        file_name="legacy.docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size=64,
        uploaded_at=datetime(2026, 5, 31, 10, 0, 0),
    )

    assert attachment.official_file_role is None
    assert attachment.source_role_alias is None
    assert attachment.external_upload_position is None
    assert attachment.content_hash is None
    assert attachment.package_usage_hint is None
    assert attachment.is_archive_evidence is False
    assert attachment.is_receipt_evidence is False


def test_attachment_manifest_migration_creates_columns(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "attachment_manifest_migration.db"
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
    db_columns = {column["name"] for column in inspector.get_columns("t_doc_attachment")}

    assert ATTACHMENT_MANIFEST_COLUMNS <= db_columns

    engine.dispose()
