from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

__all__ = (
    "FeeDomain",
    "FeeEstimateStatus",
    "FeeObligationStatus",
    "FeeClientInstructionStatus",
    "FeeObligationDraftStatus",
    "FeePayListStatus",
    "FeePaymentStatus",
    "FeeOfficialEvidenceStatus",
    "FeeClientInstruction",
    "FeeDraftAuthority",
    "FeeSourceStatus",
    "FeeDifferenceReviewState",
    "FeeEstimateContext",
    "FeeEstimateSource",
    "FeeObligationSource",
    "FeeObligationStatuses",
    "FeeObligationLineInput",
    "FeeObligationLine",
    "FeeEstimateCandidate",
    "FeeEstimate",
    "FeeObligation",
    "FeeDraftItemLinkResult",
    "FeePaymentEvidenceLinkResult",
    "PreviewFeeEstimateCommand",
    "RecognizeFeeObligationCommand",
    "RecognizeFeeObligationResult",
    "RecordFeeObligationInstructionCommand",
    "RecordFeeObligationInstructionResult",
    "PrepareFeeObligationDraftCommand",
    "PrepareFeeObligationDraftResult",
    "RecordFeePaymentEvidenceCommand",
    "RecordFeePaymentEvidenceResult",
)


class FeeDomain(str, Enum):
    GOV = "GOV"
    SERVICE = "SERVICE"


class FeeEstimateStatus(str, Enum):
    ESTIMATE = "ESTIMATE"


class FeeObligationStatus(str, Enum):
    RECOGNIZED = "RECOGNIZED"
    SUPERSEDED = "SUPERSEDED"


class FeeClientInstructionStatus(str, Enum):
    PENDING = "PENDING"
    PAY = "PAY"
    HOLD = "HOLD"
    ABANDON = "ABANDON"


class FeeObligationDraftStatus(str, Enum):
    NOT_CREATED = "NOT_CREATED"
    CREATED = "CREATED"


class FeePayListStatus(str, Enum):
    NOT_CREATED = "NOT_CREATED"
    CREATED = "CREATED"


class FeePaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"


class FeeOfficialEvidenceStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FeeClientInstruction(str, Enum):
    PAY = "PAY"
    HOLD = "HOLD"
    ABANDON = "ABANDON"


class FeeDraftAuthority(str, Enum):
    CLIENT_PAY_INSTRUCTION = "CLIENT_PAY_INSTRUCTION"
    REVIEWED_APPLICATION_FEE_NOTICE = "REVIEWED_APPLICATION_FEE_NOTICE"


class FeeSourceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"


class FeeDifferenceReviewState(str, Enum):
    MATCHED = "MATCHED"
    SOURCE_PENDING = "SOURCE_PENDING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class FeeEstimateContext:
    trigger: str
    source_document_id: str | None


@dataclass(frozen=True, slots=True)
class FeeEstimateSource:
    rate_id: str | None
    source_document_id: str | None
    source_doc: str | None
    source_url: str | None
    source_policy: str | None
    source_version: str | None
    status: FeeSourceStatus


@dataclass(frozen=True, slots=True)
class FeeObligationSource:
    source_activity_id: str
    source_document_id: str | None
    status: FeeSourceStatus


@dataclass(frozen=True, slots=True)
class FeeObligationStatuses:
    estimate_status: FeeEstimateStatus | None
    obligation_status: FeeObligationStatus
    client_instruction_status: FeeClientInstructionStatus
    draft_status: FeeObligationDraftStatus
    pay_list_status: FeePayListStatus
    payment_status: FeePaymentStatus
    official_evidence_status: FeeOfficialEvidenceStatus


@dataclass(frozen=True, slots=True)
class FeeObligationLineInput:
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: Decimal | None
    reduction_ratio: Decimal
    payable_amount: Decimal
    source_amount: Decimal | None
    source_date: date | None
    difference_review_state: FeeDifferenceReviewState


@dataclass(frozen=True, slots=True)
class FeeObligationLine:
    id: str
    obligation_id: str
    case_id: str
    source_activity_id: str
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: Decimal | None
    reduction_ratio: Decimal
    payable_amount: Decimal
    source_amount: Decimal | None
    source_date: date | None
    difference_review_state: FeeDifferenceReviewState
    current_identity_key: str | None


@dataclass(frozen=True, slots=True)
class FeeEstimateCandidate:
    line: FeeObligationLineInput
    source: FeeEstimateSource


@dataclass(frozen=True, slots=True)
class FeeEstimate:
    case_id: str
    estimate_status: FeeEstimateStatus
    trigger_context: FeeEstimateContext
    currency: str
    candidates: tuple[FeeEstimateCandidate, ...]
    total_payable_amount: Decimal


@dataclass(frozen=True, slots=True)
class FeeObligation:
    id: str
    case_id: str
    source: FeeObligationSource
    fee_domain: FeeDomain
    obligation_type: str
    due_date: date | None
    currency: str
    statuses: FeeObligationStatuses
    lines: tuple[FeeObligationLine, ...]
    supersedes_obligation_id: str | None
    supersede_reason: str | None


@dataclass(frozen=True, slots=True)
class FeeDraftItemLinkResult:
    id: str
    obligation_line_id: str
    fee_item_id: str
    reused: bool


@dataclass(frozen=True, slots=True)
class FeePaymentEvidenceLinkResult:
    id: str
    obligation_line_id: str
    gov_payment_id: int
    reused: bool


@dataclass(frozen=True, slots=True)
class PreviewFeeEstimateCommand:
    case_id: str
    trigger_context: FeeEstimateContext
    currency: str


@dataclass(frozen=True, slots=True)
class RecognizeFeeObligationCommand:
    case_id: str
    source_activity_id: str
    source_document_id: str | None
    fee_domain: FeeDomain
    obligation_type: str
    due_date: date | None
    currency: str
    source_status: FeeSourceStatus
    lines: tuple[FeeObligationLineInput, ...]
    actor_id: str
    idempotency_key: str
    supersedes_obligation_id: str | None
    supersede_reason: str | None


@dataclass(frozen=True, slots=True)
class RecognizeFeeObligationResult:
    obligation: FeeObligation
    activity_id: str
    idempotency_key: str
    reused: bool
    superseded_obligation_id: str | None


@dataclass(frozen=True, slots=True)
class RecordFeeObligationInstructionCommand:
    obligation_id: str
    instruction: FeeClientInstruction
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecordFeeObligationInstructionResult:
    obligation: FeeObligation
    activity_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class PrepareFeeObligationDraftCommand:
    obligation_id: str
    actor_id: str
    idempotency_key: str
    authority: FeeDraftAuthority = FeeDraftAuthority.CLIENT_PAY_INSTRUCTION


@dataclass(frozen=True, slots=True)
class PrepareFeeObligationDraftResult:
    obligation_id: str
    draft_id: str
    links: tuple[FeeDraftItemLinkResult, ...]
    activity_id: str
    activity_reused: bool
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecordFeePaymentEvidenceCommand:
    obligation_id: str
    obligation_line_ids: tuple[str, ...]
    gov_payment_id: int
    actor_id: str


@dataclass(frozen=True, slots=True)
class RecordFeePaymentEvidenceResult:
    obligation: FeeObligation
    links: tuple[FeePaymentEvidenceLinkResult, ...]
