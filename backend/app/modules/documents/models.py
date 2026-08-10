from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
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


class DocumentEvidenceVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_document_evidence_version"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_case.id",
            name="fk_t_document_evidence_version_case_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_document.id",
            name="fk_t_document_evidence_version_document_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    attachment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_doc_attachment.id",
            name="fk_t_document_evidence_version_attachment_id",
        ),
        nullable=False,
    )
    lineage_key: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    creator_id: Mapped[str] = mapped_column(String(36), nullable=False)
    review_state: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    final_submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_document_evidence_version_current_identity_key",
        ),
    )


class GrantOfficialCopyVerificationEvent(Base):
    __tablename__ = "t_grant_official_copy_verification_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    evidence_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_config_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(36), nullable=False)
    role_config_id: Mapped[str] = mapped_column(String(36), nullable=False)
    evidence_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    original_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    acquisition_method_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    source_config_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    role_config_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    predecessor_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    event_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    event_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(96), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "evidence_version_id",
            "event_type",
            name="uq_t_grant_official_copy_event_stage",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_official_copy_event_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_official_copy_event_current_identity_key",
        ),
        ForeignKeyConstraint(
            ["evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_grant_official_copy_event_evidence_version",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_official_copy_event_source_config",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_official_copy_event_source_record",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["role_config_id"],
            ["t_grant_manual_review_role_config.id"],
            name="fk_t_grant_official_copy_event_role_config",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["actor_id"],
            ["t_user.id"],
            name="fk_t_grant_official_copy_event_actor",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["predecessor_event_id"],
            ["t_grant_official_copy_verification_event.id"],
            name="fk_t_grant_official_copy_event_predecessor",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_official_copy_event_scope",
        ),
        CheckConstraint(
            "event_type IN ('ACQUIRED', 'FIRST_VERIFIED', 'SECOND_VERIFIED')",
            name="ck_t_grant_official_copy_event_type",
        ),
        CheckConstraint(
            "(event_type = 'ACQUIRED' AND predecessor_event_id IS NULL) OR "
            "(event_type IN ('FIRST_VERIFIED', 'SECOND_VERIFIED') "
            "AND predecessor_event_id IS NOT NULL)",
            name="ck_t_grant_official_copy_event_predecessor_shape",
        ),
        CheckConstraint(
            "length(source_config_snapshot_hash) = 64 "
            "AND source_config_snapshot_hash = lower(source_config_snapshot_hash) "
            "AND source_config_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(source_snapshot_hash) = 64 "
            "AND source_snapshot_hash = lower(source_snapshot_hash) "
            "AND source_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(role_config_snapshot_hash) = 64 "
            "AND role_config_snapshot_hash = lower(role_config_snapshot_hash) "
            "AND role_config_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(event_snapshot_hash) = 64 "
            "AND event_snapshot_hash = lower(event_snapshot_hash) "
            "AND event_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_grant_official_copy_event_hashes",
        ),
        CheckConstraint(
            "length(evidence_content_hash) BETWEEN 1 AND 128 "
            "AND evidence_content_hash = trim(evidence_content_hash) "
            "AND instr(evidence_content_hash, char(0)) = 0",
            name="ck_t_grant_official_copy_event_content_hash",
        ),
        CheckConstraint(
            "current_identity_key IS NULL OR "
            "current_identity_key = 'GRANT_OFFICIAL_COPY|' || evidence_version_id",
            name="ck_t_grant_official_copy_event_current_key",
        ),
        Index(
            "ix_t_grant_official_copy_event_evidence_stage",
            "evidence_version_id",
            "event_type",
            "action_at",
        ),
    )


class GrantEvidenceCandidate(Base):
    __tablename__ = "t_grant_evidence_candidate"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), nullable=False)
    document_id: Mapped[str] = mapped_column(String(36), nullable=False)
    evidence_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_config_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(36), nullable=False)
    evidence_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    source_version_snapshot: Mapped[str] = mapped_column(String(128), nullable=False)
    original_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    acquisition_method_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    acquisition_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    acquisition_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    proposed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    reviewer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflict_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "evidence_version_id",
            name="uq_t_grant_evidence_candidate_evidence_version_id",
        ),
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_grant_evidence_candidate_case_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["document_id"],
            ["t_document.id"],
            name="fk_t_grant_evidence_candidate_document_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_grant_evidence_candidate_evidence_version_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_evidence_candidate_source_config_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_candidate_source_record_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["proposed_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_candidate_proposed_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["reviewer_id"],
            ["t_user.id"],
            name="fk_t_grant_evidence_candidate_reviewer_id",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_candidate_scope",
        ),
        CheckConstraint(
            "length(acquisition_snapshot_hash) = 64",
            name="ck_t_grant_evidence_candidate_acquisition_hash_length",
        ),
        CheckConstraint(
            "length(candidate_snapshot_hash) = 64",
            name="ck_t_grant_evidence_candidate_candidate_hash_length",
        ),
        CheckConstraint(
            "review_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_grant_evidence_candidate_review_status",
        ),
        CheckConstraint(
            "(review_status = 'PENDING' AND reviewer_id IS NULL "
            "AND reviewed_at IS NULL AND review_reason IS NULL) OR "
            "(review_status IN ('APPROVED', 'REJECTED') "
            "AND reviewer_id IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewer_id <> proposed_by)",
            name="ck_t_grant_evidence_candidate_review_tuple",
        ),
        Index(
            "ix_t_grant_evidence_candidate_document_review",
            "document_id",
            "review_status",
            "proposed_at",
        ),
    )


class DocumentEvidenceDerivation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_document_evidence_derivation"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_case.id",
            name="fk_t_document_evidence_derivation_case_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    parent_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_document_evidence_version.id",
            name="fk_t_document_evidence_derivation_parent_evidence_version_id",
        ),
        nullable=False,
    )
    child_evidence_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_document_evidence_version.id",
            name="fk_t_document_evidence_derivation_child_evidence_version_id",
        ),
        nullable=False,
    )
    derivation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    derived_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    source_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
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
