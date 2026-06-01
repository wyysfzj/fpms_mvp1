from __future__ import annotations

from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403
from app.modules.annuity.models import PayList
from app.modules.documents.models import LetterHandoff, LetterHandoffAttachment
from app.modules.documents.schemas import (
    LETTER_HANDOFF_STATUSES,
    LetterHandoffAttachmentOut,
    LetterHandoffOut,
)
from app.modules.templates.models import FormatLetterMapping
from app.modules.templates.schemas import FormatLetterMappingOut

FORMAT_LETTER_MAPPING_COLUMNS = {
    "official_doc_template_id",
    "official_doc_template_code",
    "official_doc_name_pattern",
    "format_letter_template_id",
    "format_letter_template_code",
    "output_name_rule",
    "salutation_rule_code",
    "contact_rule_code",
    "enabled",
    "remark",
}
LETTER_HANDOFF_COLUMNS = {
    "source_document_id",
    "generated_document_id",
    "format_letter_mapping_id",
    "format_letter_template_id",
    "client_contact_id",
    "contact_selection_source",
    "salutation_source",
    "salutation_text",
    "generated_word_path",
    "mail_subject",
    "mail_body_draft",
    "longxia_handoff_status",
    "longxia_handoff_payload",
    "handoff_at",
    "remark",
}
LETTER_HANDOFF_ATTACHMENT_COLUMNS = {
    "handoff_id",
    "attachment_id",
    "file_name",
    "file_path",
    "attachment_role",
    "required",
    "included",
    "sort_order",
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


def test_letter_handoff_models_create_required_carrier_tables(tmp_path) -> None:
    db_path = tmp_path / "letter_handoff_model.db"
    engine = _sqlite_engine(db_path)

    Base.metadata.create_all(engine)

    assert FormatLetterMapping.__tablename__ == "t_format_letter_mapping"
    assert LetterHandoff.__tablename__ == "t_letter_handoff"
    assert LetterHandoffAttachment.__tablename__ == "t_letter_handoff_attachment"
    assert PayList.__tablename__ == "t_pay_list"

    inspector = inspect(engine)
    assert FORMAT_LETTER_MAPPING_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_format_letter_mapping")
    }
    assert LETTER_HANDOFF_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_letter_handoff")
    }
    assert LETTER_HANDOFF_ATTACHMENT_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_letter_handoff_attachment")
    }

    engine.dispose()


def test_letter_handoff_schemas_preserve_mapping_and_longxia_metadata() -> None:
    assert {"PENDING", "READY", "HANDED_OFF", "FAILED"} <= set(LETTER_HANDOFF_STATUSES)

    mapping = FormatLetterMappingOut(
        id="mapping-1",
        official_doc_template_id="doc-template-1",
        official_doc_template_code="FIRST_OA_NOTICE",
        official_doc_name_pattern="第一次审查意见通知书",
        format_letter_template_id="template-1",
        format_letter_template_code="官文转发-国内客户-一通",
        output_name_rule="{case_no}-一通格式函.docx",
        salutation_rule_code="PRIMARY_CONTACT_TITLE",
        contact_rule_code="CLIENT_PRIMARY_CONTACT",
        enabled=True,
        remark="客户反馈映射种子",
    )
    handoff = LetterHandoffOut(
        id="handoff-1",
        source_document_id="official-doc-1",
        generated_document_id="letter-doc-1",
        format_letter_mapping_id="mapping-1",
        format_letter_template_id="template-1",
        client_contact_id="contact-1",
        contact_selection_source="CLIENT_PRIMARY_CONTACT",
        salutation_source="PRIMARY_CONTACT_TITLE",
        salutation_text="张老师：您好",
        generated_word_path="storage/letters/case-1-letter.docx",
        mail_subject="一通转发",
        mail_body_draft="请查收附件。",
        longxia_handoff_status="READY",
        longxia_handoff_payload='{"attachments":["case-1-letter.docx"]}',
        handoff_at=datetime(2026, 5, 31, 10, 0, 0),
        remark="等待龙虾系统发送",
    )
    attachment = LetterHandoffAttachmentOut(
        id="handoff-att-1",
        handoff_id="handoff-1",
        attachment_id="att-1",
        file_name="case-1-letter.docx",
        file_path="storage/letters/case-1-letter.docx",
        attachment_role="FORMAT_LETTER_WORD",
        required=True,
        included=True,
        sort_order=1,
    )

    assert mapping.format_letter_template_code == "官文转发-国内客户-一通"
    assert handoff.longxia_handoff_status == "READY"
    assert attachment.attachment_role == "FORMAT_LETTER_WORD"


def test_letter_handoff_migration_creates_mapping_and_handoff_tables(
    tmp_path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "letter_handoff_migration.db"
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
    assert {
        "t_format_letter_mapping",
        "t_letter_handoff",
        "t_letter_handoff_attachment",
    } <= set(inspector.get_table_names())
    assert FORMAT_LETTER_MAPPING_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_format_letter_mapping")
    }
    assert LETTER_HANDOFF_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_letter_handoff")
    }
    assert LETTER_HANDOFF_ATTACHMENT_COLUMNS <= {
        column["name"] for column in inspector.get_columns("t_letter_handoff_attachment")
    }

    engine.dispose()
