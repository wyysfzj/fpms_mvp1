from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EvidenceRole(str, Enum):
    FILING_FULL_WORD = "FILING_FULL_WORD"
    TRACKED_REVISED_WORD = "TRACKED_REVISED_WORD"
    FILING_COMPONENT = "FILING_COMPONENT"
    EXTERNAL_XML_PACKAGE = "EXTERNAL_XML_PACKAGE"
    OFFICIAL_SUBMISSION_LIST = "OFFICIAL_SUBMISSION_LIST"
    OFFICIAL_FINAL_PDF = "OFFICIAL_FINAL_PDF"
    SUBMITTED_XML = "SUBMITTED_XML"
    OFFICIAL_RECEIPT = "OFFICIAL_RECEIPT"
    CLIENT_LETTER_WORD = "CLIENT_LETTER_WORD"
    RAW_ATTACHMENT = "RAW_ATTACHMENT"
    GENERATED_ATTACHMENT = "GENERATED_ATTACHMENT"
    OA_STRUCTURED_ATTACHMENT = "OA_STRUCTURED_ATTACHMENT"


class EvidenceVersionState(str, Enum):
    DRAFT = "DRAFT"
    FINAL = "FINAL"


class EvidenceReviewState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class EvidenceDerivationType(str, Enum):
    REVISION = "REVISION"
    COMPONENT_EXTRACTION = "COMPONENT_EXTRACTION"
    FORMAT_CONVERSION = "FORMAT_CONVERSION"
    OFFICIAL_RECOGNITION = "OFFICIAL_RECOGNITION"
    EXTERNAL_SUBMISSION = "EXTERNAL_SUBMISSION"
    RECEIPT_LINK = "RECEIPT_LINK"
    CUSTOMER_LETTER_RENDER = "CUSTOMER_LETTER_RENDER"


@dataclass(frozen=True, slots=True)
class RegisterEvidenceVersionCommand:
    case_id: str
    document_id: str
    attachment_id: str
    lineage_key: str
    role: EvidenceRole
    state: EvidenceVersionState
    creator_id: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class EvidenceVersionResult:
    evidence_version_id: str
    case_id: str
    document_id: str
    attachment_id: str
    lineage_key: str
    role: EvidenceRole
    version_number: int
    state: EvidenceVersionState
    creator_id: str
    review_state: EvidenceReviewState
    reviewer_id: str | None
    reviewed_at: datetime | None
    final_submitted_at: datetime | None
    content_hash: str
    is_current: bool
    is_final: bool


@dataclass(frozen=True, slots=True)
class RegisterEvidenceDerivationCommand:
    case_id: str
    parent_evidence_version_id: str
    child_evidence_version_id: str
    derivation_type: EvidenceDerivationType
    actor_id: str
    derived_at: datetime
    source_snapshot: str


@dataclass(frozen=True, slots=True)
class EvidenceDerivationResult:
    evidence_derivation_id: str
    case_id: str
    parent_evidence_version_id: str
    child_evidence_version_id: str
    derivation_type: EvidenceDerivationType
    actor_id: str
    derived_at: datetime
    source_snapshot: str


__all__ = [
    "EvidenceRole",
    "EvidenceVersionState",
    "EvidenceReviewState",
    "EvidenceDerivationType",
    "RegisterEvidenceVersionCommand",
    "EvidenceVersionResult",
    "RegisterEvidenceDerivationCommand",
    "EvidenceDerivationResult",
]
