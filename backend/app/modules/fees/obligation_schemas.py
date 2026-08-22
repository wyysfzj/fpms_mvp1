from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeEstimateStatus,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentStatus,
    FeeSourceStatus,
)


class FeeObligationInstructionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instruction: FeeClientInstruction
    idempotency_key: str


class FeeObligationInstructionOut(BaseModel):
    obligation_id: str
    client_instruction_status: FeeClientInstructionStatus
    activity_id: str
    idempotency_key: str
    reused: bool


class FeeObligationSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_activity_id: str
    source_document_id: str | None
    status: FeeSourceStatus


class FeeObligationStatusesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    estimate_status: FeeEstimateStatus | None
    obligation_status: FeeObligationStatus
    client_instruction_status: FeeClientInstructionStatus
    draft_status: FeeObligationDraftStatus
    pay_list_status: FeePayListStatus
    payment_status: FeePaymentStatus
    official_evidence_status: FeeOfficialEvidenceStatus


class FeeObligationLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class FeeObligationDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    source: FeeObligationSourceOut
    fee_domain: FeeDomain
    obligation_type: str
    due_date: date | None
    currency: str
    statuses: FeeObligationStatusesOut
    lines: tuple[FeeObligationLineOut, ...]
    supersedes_obligation_id: str | None
    supersede_reason: str | None


class ServiceReceivableCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price_book_version_id: UUID
    item_code: str = Field(..., min_length=1, max_length=128)
    case_id: UUID
    idempotency_key: str = Field(..., min_length=1, max_length=96)


class ServiceReceivableRecognitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    obligation: FeeObligationDetailOut
    activity_id: str
    idempotency_key: str
    reused: bool
    superseded_obligation_id: str | None


class ServiceReceivableCreateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recognition: ServiceReceivableRecognitionOut
    price_book_version_id: str
    item_code: str
    unit_price: Decimal
    source_activity_id: str
    reused: bool
