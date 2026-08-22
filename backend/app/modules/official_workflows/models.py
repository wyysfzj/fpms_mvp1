from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class OfficialWorkPackage(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_work_package"
    __table_args__ = (Index("ux_t_official_work_package_resolve_key", "resolve_key", unique=True),)

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False, index=True
    )
    package_kind: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PREPARING'"), index=True
    )
    source_document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_document.id"), nullable=True, index=True
    )
    reply_document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_document.id"), nullable=True, index=True
    )
    resolve_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    external_system: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


class OfficialWorkPackageChecklist(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_work_package_checklist"

    package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_code: Mapped[str] = mapped_column(String(64), nullable=False)
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    item_label: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class OfficialWorkPackageManifest(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_work_package_manifest"

    package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attachment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_doc_attachment.id"), nullable=True, index=True
    )
    evidence_version_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "t_document_evidence_version.id",
            name="fk_t_official_work_package_manifest_evidence_version_id",
        ),
        nullable=True,
        index=True,
    )
    official_file_role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_role_alias: Mapped[str | None] = mapped_column(String(128), nullable=True)
    external_upload_position: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    present: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class OfficialWorkPackageReceipt(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_work_package_receipt"

    package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receipt_kind: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'RECEIPT_PDF'")
    )
    receipt_attachment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_doc_attachment.id"), nullable=True, index=True
    )
    receiving_case_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    submitter: Mapped[str | None] = mapped_column(String(128), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    received_file_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    archive_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class OfficialWorkPackageOverride(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_work_package_override"

    package_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    override_action: Mapped[str] = mapped_column(String(64), nullable=False)
    override_reason: Mapped[str] = mapped_column(Text, nullable=False)
    override_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    override_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    follow_up_owner: Mapped[str | None] = mapped_column(String(36), nullable=True)
    follow_up_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    follow_up_note: Mapped[str | None] = mapped_column(Text, nullable=True)
