from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceVersionResult,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationStatuses,
    FeeSourceStatus,
)
from app.modules.system.decision_gate_service import DecisionGateCode


class OverlayCenterAxis(StrEnum):
    BUSINESS_STAGE = "BUSINESS_STAGE"
    OFFICIAL_PROCEDURE_STAGE = "OFFICIAL_PROCEDURE_STAGE"
    LEGAL_STATUS = "LEGAL_STATUS"


class OverlayWarningKind(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    CUSTOMER_DECISION_GATE = "CUSTOMER_DECISION_GATE"
    CONFLICT = "CONFLICT"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class OverlayFeeRelatedFactKind(StrEnum):
    DRAFT = "DRAFT"
    PAY_LIST = "PAY_LIST"
    PAYMENT = "PAYMENT"
    OFFICIAL_EVIDENCE = "OFFICIAL_EVIDENCE"


class OverlayGateResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleOverlayQuery:
    after_sequence: int
    limit: int
    as_of_revision: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayCenterSnapshot:
    business_stage: BusinessStage | None
    official_procedure_stage: OfficialProcedureStage | None
    legal_status: LegalStatus | None
    effective_at: datetime | None
    verification_status: ConfirmationStatus | None
    source_event_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayCenterAxisChange:
    previous_value: BusinessStage | OfficialProcedureStage | LegalStatus | None
    current_value: BusinessStage | OfficialProcedureStage | LegalStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayDocumentEvidence:
    version: EvidenceVersionResult
    derivations: tuple[EvidenceDerivationResult, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWorkPackageReceipt:
    receipt_id: str
    receipt_kind: str
    receipt_attachment_id: str | None
    receiving_case_no: str | None
    submitter: str | None
    received_at: datetime | None
    archive_status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWorkPackage:
    package_id: str
    package_kind: str
    status: str
    source_document_id: str | None
    reply_document_id: str | None
    manifest_evidence_version_ids: tuple[str, ...]
    receipts: tuple[OverlayWorkPackageReceipt, ...]
    missing_gate_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayTask:
    task_id: str
    document_id: str | None
    task_template_id: str | None
    title: str | None
    due_date: date | None
    internal_due_date: date | None
    status: str
    done_at: datetime | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeLine:
    line_id: str
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: str | None
    reduction_ratio: str
    payable_amount: str
    source_amount: str | None
    source_date: date | None
    difference_review_state: FeeDifferenceReviewState


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeRelatedFact:
    kind: OverlayFeeRelatedFactKind
    object_id: str
    status: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayFeeObligation:
    obligation_id: str
    source_activity_id: str
    source_document_id: str | None
    source_status: FeeSourceStatus
    fee_domain: FeeDomain
    obligation_type: str
    due_date: date | None
    currency: str
    statuses: FeeObligationStatuses
    lines: tuple[OverlayFeeLine, ...]
    related_facts: tuple[OverlayFeeRelatedFact, ...]
    supersedes_obligation_id: str | None
    supersede_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayWarning:
    kind: OverlayWarningKind
    code: str
    message: str
    activity_id: str | None
    source_object_type: str | None
    source_object_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayDecisionGate:
    gate_code: DecisionGateCode
    requested_scope_key: str
    resolution_status: OverlayGateResolutionStatus
    gate_id: str | None
    resolved_scope_key: str | None
    decision_value: str | None
    source_reference: str | None
    source_version: str | None
    confirmed_by: str | None
    effective_at: datetime | None
    unresolved_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayLegacyConflict:
    code: str
    activity_id: str | None
    message: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class OverlayMilestone:
    sequence: int
    activity_id: str
    lane: ActivityLane
    activity_type: str
    source_activity_id: str | None
    effective_at: datetime
    confirmation_status: ConfirmationStatus
    center_changes: Mapping[OverlayCenterAxis, OverlayCenterAxisChange]
    document_evidence: tuple[OverlayDocumentEvidence, ...]
    work_packages: tuple[OverlayWorkPackage, ...]
    tasks: tuple[OverlayTask, ...]
    fee_obligations: tuple[OverlayFeeObligation, ...]
    evidence_summary: tuple[EvidenceReference, ...]
    warnings: tuple[OverlayWarning, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleOverlay:
    case_id: str
    lifecycle_revision: int
    generated_at: datetime
    center_snapshot: OverlayCenterSnapshot
    milestones: tuple[OverlayMilestone, ...]
    decision_gates: tuple[OverlayDecisionGate, ...]
    warnings: tuple[OverlayWarning, ...]
    legacy_conflicts: tuple[OverlayLegacyConflict, ...]
    next_cursor: int | None
    has_more: bool


__all__ = [
    "LifecycleOverlay",
    "LifecycleOverlayQuery",
    "OverlayCenterAxis",
    "OverlayCenterAxisChange",
    "OverlayCenterSnapshot",
    "OverlayDecisionGate",
    "OverlayDocumentEvidence",
    "OverlayFeeLine",
    "OverlayFeeObligation",
    "OverlayFeeRelatedFact",
    "OverlayFeeRelatedFactKind",
    "OverlayGateResolutionStatus",
    "OverlayLegacyConflict",
    "OverlayMilestone",
    "OverlayTask",
    "OverlayWarning",
    "OverlayWarningKind",
    "OverlayWorkPackage",
    "OverlayWorkPackageReceipt",
]
