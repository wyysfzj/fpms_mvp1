from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

__all__ = (
    "ActivityLane",
    "BusinessStage",
    "ConfirmationStatus",
    "EvidenceReference",
    "LegalStatus",
    "LifecycleEventCommand",
    "LifecycleProjection",
    "LifecycleTransitionResult",
    "OfficialProcedureStage",
)


class BusinessStage(StrEnum):
    NEW_CASE = "NEW_CASE"
    FILING_PREPARATION = "FILING_PREPARATION"
    WAITING_EXTERNAL_RECEIPT = "WAITING_EXTERNAL_RECEIPT"
    PROSECUTION_MANAGEMENT = "PROSECUTION_MANAGEMENT"
    OA_REPLY_IN_PROGRESS = "OA_REPLY_IN_PROGRESS"
    GRANT_REGISTRATION_IN_PROGRESS = "GRANT_REGISTRATION_IN_PROGRESS"
    POST_GRANT_MAINTENANCE = "POST_GRANT_MAINTENANCE"
    CLOSED = "CLOSED"


class OfficialProcedureStage(StrEnum):
    NOT_SUBMITTED = "NOT_SUBMITTED"
    SUBMITTED_WAITING_RECEIPT = "SUBMITTED_WAITING_RECEIPT"
    SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE = "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE"
    ACCEPTED = "ACCEPTED"
    PRELIMINARY_EXAMINATION = "PRELIMINARY_EXAMINATION"
    RECTIFICATION_RESPONSE = "RECTIFICATION_RESPONSE"
    PUBLISHED = "PUBLISHED"
    SUBSTANTIVE_EXAMINATION = "SUBSTANTIVE_EXAMINATION"
    OFFICE_ACTION_RESPONSE = "OFFICE_ACTION_RESPONSE"
    REEXAMINATION = "REEXAMINATION"
    GRANT_REGISTRATION = "GRANT_REGISTRATION"
    GRANT_ANNOUNCED = "GRANT_ANNOUNCED"
    PROCEDURE_CLOSED = "PROCEDURE_CLOSED"


class LegalStatus(StrEnum):
    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    APPLICATION_PENDING = "APPLICATION_PENDING"
    APPLICATION_REJECTED = "APPLICATION_REJECTED"
    APPLICATION_WITHDRAWN = "APPLICATION_WITHDRAWN"
    APPLICATION_ABANDONED = "APPLICATION_ABANDONED"
    PATENT_IN_FORCE = "PATENT_IN_FORCE"
    PATENT_TERMINATED = "PATENT_TERMINATED"
    PATENT_EXPIRED = "PATENT_EXPIRED"
    PATENT_INVALIDATED = "PATENT_INVALIDATED"
    UNKNOWN = "UNKNOWN"


class ActivityLane(StrEnum):
    LIFECYCLE = "LIFECYCLE"
    DOCUMENT = "DOCUMENT"
    FEE = "FEE"


class ConfirmationStatus(StrEnum):
    NEEDS_REVIEW = "NEEDS_REVIEW"
    CONFIRMED = "CONFIRMED"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleProjection:
    business_stage: BusinessStage | None
    official_procedure_stage: OfficialProcedureStage | None
    legal_status: LegalStatus | None
    lifecycle_verification_status: ConfirmationStatus | None


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceReference:
    case_id: str
    evidence_kind: str
    object_type: str
    object_id: str
    content_hash: str
    captured_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleEventCommand:
    case_id: str
    event_type: str
    lane: ActivityLane
    effective_at: datetime
    evidence_refs: tuple[EvidenceReference, ...]
    actor_id: str
    idempotency_key: str
    confirmation_status: ConfirmationStatus
    payload: Mapping[str, object]
    occurred_at: datetime | None = None
    reviewer_id: str | None = None
    source_activity_id: str | None = None
    supersedes_event_id: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleTransitionResult:
    case_id: str
    activity_id: str
    sequence: int
    lifecycle_revision: int
    lane: ActivityLane
    event_type: str
    confirmation_status: ConfirmationStatus
    previous_projection: LifecycleProjection
    current_projection: LifecycleProjection
    legacy_case_status: str
    idempotency_key: str
    reused: bool
    conflict_codes: tuple[str, ...] = ()
