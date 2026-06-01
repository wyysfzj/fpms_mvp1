from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.modules.cases.models import Case


class DocAttachment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_doc_attachment"

    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_document.id", ondelete="CASCADE"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    official_file_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_role_alias: Mapped[str | None] = mapped_column(String(128), nullable=True)
    external_upload_position: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    package_usage_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_archive_evidence: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0")
    )
    is_receipt_evidence: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0")
    )

    document: Mapped["Document"] = relationship("Document", back_populates="attachments")


class DocTemplate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_doc_template"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'IN'"))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    # --- B1: SPEC configuration fields ---
    status_effect: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status_restore: Mapped[str | None] = mapped_column(String(32), nullable=True)
    deadline_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_draft_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fee_item_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    need_reply: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    reply_to_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_fields: Mapped[str | None] = mapped_column(Text, nullable=True)


class Document(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_document"

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    doc_template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_doc_template.id"), nullable=True
    )
    doc_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'IN'"))
    doc_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    ref_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    extra_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    outgoing_reg_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    forward_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # --- B2: Reply chain fields ---
    reply_to_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_document.id"), nullable=True
    )
    need_reply: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    reply_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    case: Mapped["Case"] = relationship("Case")
    attachments: Mapped[list["DocAttachment"]] = relationship(
        "DocAttachment", back_populates="document"
    )
    replies: Mapped[list["Document"]] = relationship(
        "Document", back_populates="reply_to_doc", foreign_keys=[reply_to_id]
    )
    reply_to_doc: Mapped["Document | None"] = relationship(
        "Document", back_populates="replies", remote_side="Document.id", foreign_keys=[reply_to_id]
    )


class LetterHandoff(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_letter_handoff"

    source_document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_document.id", ondelete="CASCADE"), nullable=False
    )
    generated_document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_document.id"), nullable=True
    )
    format_letter_mapping_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_format_letter_mapping.id"), nullable=True
    )
    format_letter_template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_template.id"), nullable=True
    )
    client_contact_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client_contact.id"), nullable=True
    )
    contact_selection_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salutation_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salutation_text: Mapped[str | None] = mapped_column(String(256), nullable=True)
    generated_word_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    mail_subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    mail_body_draft: Mapped[str | None] = mapped_column(Text, nullable=True)
    longxia_handoff_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    longxia_handoff_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    handoff_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


class LetterHandoffAttachment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_letter_handoff_attachment"

    handoff_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_letter_handoff.id", ondelete="CASCADE"), nullable=False
    )
    attachment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_doc_attachment.id"), nullable=True
    )
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    included: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)


class DocDispatch(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_doc_dispatch"

    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("t_client.id"), nullable=False)
    dispatch_date: Mapped[date] = mapped_column(Date, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    lines: Mapped[list["DocDispatchLine"]] = relationship(
        "DocDispatchLine", back_populates="dispatch"
    )


class DocDispatchLine(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_doc_dispatch_line"

    dispatch_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_doc_dispatch.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_document.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    doc_name: Mapped[str] = mapped_column(String(256), nullable=False)
    outgoing_reg_no: Mapped[str | None] = mapped_column(String(128), nullable=True)

    dispatch: Mapped["DocDispatch"] = relationship("DocDispatch", back_populates="lines")
    document: Mapped["Document"] = relationship("Document")
