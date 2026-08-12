from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
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
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    event,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDPrimaryKeyMixin


class PayList(Base):
    __tablename__ = "t_pay_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="RESTRICT"), nullable=False
    )
    pay_list_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'DRAFT'"))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    planned_pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    list_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    flow_dir: Mapped[str | None] = mapped_column(String(32), nullable=True)
    invoice_no_from: Mapped[str | None] = mapped_column(String(64), nullable=True)
    invoice_no_to: Mapped[str | None] = mapped_column(String(64), nullable=True)
    official_upload_template_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    official_upload_template_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    official_upload_batch_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    official_pay_list_boundary_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class PayListExportArtifact(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_pay_list_export_artifact"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    pay_list_id: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    managed_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    template_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    generated_by: Mapped[str] = mapped_column(String(36), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    official_acceptance_evidence_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    official_acceptance_evidence_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    official_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["pay_list_id"],
            ["t_pay_list.id"],
            name="fk_t_pay_list_export_artifact_pay_list_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["generated_by"],
            ["t_user.id"],
            name="fk_t_pay_list_export_artifact_generated_by",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "pay_list_id",
            "idempotency_key",
            name="uq_t_pay_list_export_artifact_pay_list_idempotency_key",
        ),
        CheckConstraint(
            "kind IN ('INTERNAL_XLSX', 'OFFICIAL_XLSM')",
            name="ck_t_pay_list_export_artifact_kind",
        ),
        CheckConstraint(
            "status IN ('GENERATED', 'OFFICIAL_SITE_ACCEPTED')",
            name="ck_t_pay_list_export_artifact_status",
        ),
        CheckConstraint(
            "length(content_sha256) = 64",
            name="ck_t_pay_list_export_artifact_content_sha256",
        ),
        CheckConstraint(
            "official_acceptance_evidence_hash IS NULL "
            "OR length(official_acceptance_evidence_hash) = 64",
            name="ck_t_pay_list_export_artifact_acceptance_hash",
        ),
        CheckConstraint(
            "(kind = 'INTERNAL_XLSX' AND template_version IS NULL) "
            "OR (kind = 'OFFICIAL_XLSM' AND template_version IS NOT NULL)",
            name="ck_t_pay_list_export_artifact_kind_payload",
        ),
        CheckConstraint(
            "(status = 'GENERATED' "
            "AND official_acceptance_evidence_ref IS NULL "
            "AND official_acceptance_evidence_hash IS NULL "
            "AND official_accepted_at IS NULL) "
            "OR (status = 'OFFICIAL_SITE_ACCEPTED' "
            "AND kind = 'OFFICIAL_XLSM' "
            "AND official_acceptance_evidence_ref IS NOT NULL "
            "AND official_acceptance_evidence_hash IS NOT NULL "
            "AND official_accepted_at IS NOT NULL)",
            name="ck_t_pay_list_export_artifact_acceptance_tuple",
        ),
        Index(
            "ix_t_pay_list_export_artifact_pay_list_generated_at",
            "pay_list_id",
            "generated_at",
        ),
    )


class OfficialPaymentWorkbookInputVersion(Base):
    __tablename__ = "t_official_payment_workbook_input_version"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scope_key: Mapped[str] = mapped_column(String(36), nullable=False)
    source_classification: Mapped[str] = mapped_column(String(24), nullable=False)
    template_version: Mapped[str] = mapped_column(String(128), nullable=False)
    template_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    template_content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    upload_proof_storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    upload_proof_content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    structure_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    structure_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    workflow_status: Mapped[str] = mapped_column(String(24), nullable=False)
    validated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    validation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    activation_status: Mapped[str] = mapped_column(String(24), nullable=False)
    activated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    retired_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    retirement_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    supersedes_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_by: Mapped[str] = mapped_column(String(36), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["validated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_validated_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["reviewed_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_reviewed_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_activated_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["retired_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_retired_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["created_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_created_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["updated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_updated_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["supersedes_version_id"],
            ["t_official_payment_workbook_input_version.id"],
            name="fk_t_official_payment_workbook_input_supersedes",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "scope_key",
            "template_version",
            name="uq_t_official_payment_workbook_input_scope_version",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_official_payment_workbook_input_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_official_payment_workbook_input_current_identity_key",
        ),
        CheckConstraint(
            "scope_key = 'GLOBAL'",
            name="ck_t_official_payment_workbook_input_scope",
        ),
        CheckConstraint(
            "source_classification IN ('PRODUCTION', 'TEST_ONLY')",
            name="ck_t_official_payment_workbook_input_source_classification",
        ),
        CheckConstraint(
            "workflow_status IN ('DRAFT', 'VALIDATED', 'APPROVED', 'REJECTED')",
            name="ck_t_official_payment_workbook_input_workflow_status",
        ),
        CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_official_payment_workbook_input_activation_status",
        ),
        CheckConstraint(
            "length(template_content_hash) = 64 "
            "AND length(upload_proof_content_hash) = 64 "
            "AND length(structure_snapshot_hash) = 64",
            name="ck_t_official_payment_workbook_input_hashes",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_official_payment_workbook_input_effective_interval",
        ),
        CheckConstraint(
            "(workflow_status = 'DRAFT' "
            "AND validated_by IS NULL AND validated_at IS NULL AND validation_reason IS NULL "
            "AND reviewed_by IS NULL AND reviewed_at IS NULL AND review_reason IS NULL) "
            "OR (workflow_status = 'VALIDATED' "
            "AND validated_by IS NOT NULL AND validated_at IS NOT NULL "
            "AND validation_reason IS NOT NULL "
            "AND reviewed_by IS NULL AND reviewed_at IS NULL AND review_reason IS NULL) "
            "OR (workflow_status IN ('APPROVED', 'REJECTED') "
            "AND validated_by IS NOT NULL AND validated_at IS NOT NULL "
            "AND validation_reason IS NOT NULL "
            "AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewed_by <> created_by)",
            name="ck_t_official_payment_workbook_input_workflow_tuple",
        ),
        CheckConstraint(
            "(activation_status = 'INACTIVE' "
            "AND activated_by IS NULL AND activated_at IS NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NULL) "
            "OR (activation_status = 'ACTIVE' "
            "AND source_classification = 'PRODUCTION' AND workflow_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NOT NULL AND current_identity_key = 'GLOBAL') "
            "OR (activation_status = 'RETIRED' "
            "AND source_classification = 'PRODUCTION' AND workflow_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NOT NULL AND retired_at IS NOT NULL "
            "AND retirement_reason IS NOT NULL AND current_identity_key IS NULL)",
            name="ck_t_official_payment_workbook_input_activation_tuple",
        ),
        Index(
            "ix_t_official_payment_workbook_input_scope_status_effective",
            "scope_key",
            "workflow_status",
            "activation_status",
            "effective_from",
            "effective_to",
        ),
    )


class GovPayment(Base):
    __tablename__ = "t_gov_payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pay_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_pay_list.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="RESTRICT"), nullable=False
    )
    fee_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_item.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'RECORDED'")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    official_receipt_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_amt: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    planned_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    paid_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    voucher_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    invoice_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class AnnuityTask(Base):
    __tablename__ = "t_annuity_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="RESTRICT"), nullable=False
    )
    year_no: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    client_instruction: Mapped[str | None] = mapped_column(String(24), nullable=True)
    instruction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notice_status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'PENDING'")
    )
    notice_sent_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'OPEN'"))
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    gov_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    service_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    notify_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    pay_next_year: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    draft_generated: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    notice_sent: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    source_activity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_evidence_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source_evidence_content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fee_obligation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    grant_fee_year_key: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["source_activity_id"],
            ["t_case_activity_event.id"],
            name="fk_t_annuity_task_source_activity_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_document_id"],
            ["t_document.id"],
            name="fk_t_annuity_task_source_document_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["source_evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_annuity_task_source_evidence_version_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["fee_obligation_id"],
            ["t_fee_obligation.id"],
            name="fk_t_annuity_task_fee_obligation_id",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "fee_obligation_id",
            name="uq_t_annuity_task_fee_obligation_id",
        ),
        CheckConstraint(
            "(source_activity_id IS NULL AND source_document_id IS NULL "
            "AND source_evidence_version_id IS NULL "
            "AND source_evidence_content_hash IS NULL "
            "AND fee_obligation_id IS NULL AND grant_fee_year_key IS NULL) "
            "OR (source_activity_id IS NOT NULL AND source_document_id IS NOT NULL "
            "AND source_evidence_version_id IS NOT NULL "
            "AND source_evidence_content_hash IS NOT NULL "
            "AND fee_obligation_id IS NOT NULL "
            "AND grant_fee_year_key IS NOT NULL AND grant_fee_year_key >= 1)",
            name="ck_t_annuity_task_lineage_tuple",
        ),
        CheckConstraint(
            "source_evidence_content_hash IS NULL OR "
            "(length(source_evidence_content_hash) = 71 "
            "AND substr(source_evidence_content_hash, 1, 7) = 'sha256:' "
            "AND substr(source_evidence_content_hash, 8) "
            "NOT GLOB '*[^0-9a-f]*')",
            name="ck_t_annuity_task_source_evidence_hash",
        ),
    )


class FutureAnnuityReductionLineage(Base):
    __tablename__ = "t_future_annuity_reduction_lineage"

    annuity_task_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_obligation_line_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reduction_input_provenance: Mapped[str] = mapped_column(String(32), nullable=False)
    reduction_approval_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(
            "annuity_task_id",
            name="pk_t_future_annuity_reduction_lineage",
        ),
        ForeignKeyConstraint(
            ["annuity_task_id"],
            ["t_annuity_task.id"],
            name="fk_t_future_annuity_reduction_lineage_annuity_task_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["fee_obligation_line_id"],
            ["t_fee_obligation_line.id"],
            name="fk_t_future_annuity_reduction_lineage_fee_obligation_line_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["reduction_approval_id"],
            ["t_fee_reduction_approval.id"],
            name="fk_t_future_annuity_reduction_lineage_reduction_approval_id",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "fee_obligation_line_id",
            name="uq_t_future_annuity_reduction_lineage_fee_obligation_line_id",
        ),
        CheckConstraint(
            "reduction_input_provenance IN "
            "('EXPLICIT_ENTRY', 'CONFIRMED_MIGRATION')",
            name="ck_t_future_annuity_reduction_lineage_provenance",
        ),
        CheckConstraint(
            "reduction_input_provenance != 'CONFIRMED_MIGRATION' "
            "OR reduction_approval_id IS NOT NULL",
            name="ck_t_future_annuity_reduction_lineage_approval_shape",
        ),
    )


@event.listens_for(FutureAnnuityReductionLineage, "before_update")
def reject_future_annuity_reduction_lineage_update(
    _mapper, _connection, _target: FutureAnnuityReductionLineage
) -> None:
    raise ValueError("future annuity reduction lineage is immutable")


@event.listens_for(FutureAnnuityReductionLineage, "before_delete")
def reject_future_annuity_reduction_lineage_delete(
    _mapper, _connection, _target: FutureAnnuityReductionLineage
) -> None:
    raise ValueError("future annuity reduction lineage is immutable")
