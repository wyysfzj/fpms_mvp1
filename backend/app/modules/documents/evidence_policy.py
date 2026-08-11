from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time
from enum import Enum
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User, T_UserRole
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    EvidenceReference,
    LifecycleEventCommand,
    LifecycleTransitionResult,
)
from app.modules.cases.lifecycle_service import apply_lifecycle_event
from app.modules.documents import grant_evidence_review_service as grant_review
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)
from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    GrantEvidenceSourceResolution,
    ResolveGrantEvidenceSourceCommand,
    resolve_grant_evidence_source,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleResolution,
    ResolveGrantManualReviewRoleConfigCommand,
    resolve_grant_manual_review_role_config,
)

__all__ = (
    "CopyableOaAttachmentEvidence",
    "CopyableOaAttachmentErrorCode",
    "CopyableOaAttachmentPolicyError",
    "FilingXmlDerivationErrorCode",
    "FilingXmlDerivationPolicyError",
    "NoncopyableOaAppendixErrorCode",
    "NoncopyableOaAppendixPolicyError",
    "apply_grant_announcement_evidence",
    "apply_patent_register_evidence",
    "is_filing_full_word_ready",
    "require_copyable_oa_attachment_combination",
    "require_filing_xml_reviewed_word_source",
    "require_noncopyable_oa_appendix_derivation",
)


_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_OA_APPENDIX_SOURCE_SNAPSHOT = (
    '{"component":"OA_STATEMENT_APPENDIX","schema":"FPMS_OA_NONCOPYABLE_APPENDIX_V1"}'
)
_COPYABLE_OA_ATTACHMENT_ROLES = frozenset(
    {
        "OA_STATEMENT_WORD",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    }
)


def _grant_announcement_conflict() -> None:
    raise_business_error(
        "GRANT_ANNOUNCEMENT_EVIDENCE_CONFLICT",
        "Grant announcement evidence conflict",
        status_code=409,
    )


def _patent_register_conflict() -> None:
    raise_business_error(
        "PATENT_REGISTER_EVIDENCE_CONFLICT",
        "Patent register evidence conflict",
        status_code=409,
    )


def _grant_uuid(value: object) -> str:
    if type(value) is not str:
        _grant_announcement_conflict()
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _grant_announcement_conflict()
    if str(parsed) != value:
        _grant_announcement_conflict()
    return value


def _grant_hash(value: object) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _grant_announcement_conflict()
    return value


def _grant_payload(snapshot: object, digest: object) -> dict[str, object]:
    if type(snapshot) is not str or hashlib.sha256(snapshot.encode()).hexdigest() != digest:
        _grant_announcement_conflict()
    try:
        payload = json.loads(snapshot)
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _grant_announcement_conflict()
    if type(payload) is not dict or canonical != snapshot:
        _grant_announcement_conflict()
    return payload


def _active_role_member(
    transaction: Session,
    user_id: str,
    role_id: str,
) -> bool:
    return (
        transaction.scalar(
            select(T_UserRole.user_id)
            .join(T_User, T_User.id == T_UserRole.user_id)
            .where(
                T_UserRole.user_id == user_id,
                T_UserRole.role_id == role_id,
                T_User.is_active.is_(True),
            )
        )
        == user_id
    )


def _grant_authority(
    candidate: GrantEvidenceCandidate,
    acquisition: dict[str, object],
    review_role_config_id: str,
    review_role_config_snapshot_hash: str,
    transaction: Session,
    *,
    evidence_scope: GrantEvidenceScope = GrantEvidenceScope.GRANT_ANNOUNCEMENT,
) -> None:
    try:
        source = resolve_grant_evidence_source(
            ResolveGrantEvidenceSourceCommand(
                evidence_scope=evidence_scope,
                as_of=candidate.reviewed_at,
            ),
            transaction,
        )
        proposal_roles = resolve_grant_manual_review_role_config(
            ResolveGrantManualReviewRoleConfigCommand(as_of=candidate.proposed_at),
            transaction,
        )
        review_roles = resolve_grant_manual_review_role_config(
            ResolveGrantManualReviewRoleConfigCommand(as_of=candidate.reviewed_at),
            transaction,
        )
    except BusinessError:
        _grant_announcement_conflict()
    if (
        type(source) is not GrantEvidenceSourceResolution
        or source.config_id != candidate.source_config_id
        or source.config_snapshot_hash != acquisition["source_config_snapshot_hash"]
        or source.source_record_id != candidate.source_record_id
        or source.evidence_scope is not evidence_scope
        or source.source_version != candidate.source_version_snapshot
        or source.source_snapshot_hash != acquisition["source_snapshot_hash"]
        or source.source_reference_value != candidate.original_reference
        or source.acquisition_method != candidate.acquisition_method_snapshot
        or type(proposal_roles) is not GrantManualReviewRoleResolution
        or proposal_roles.config_id != acquisition["proposal_role_config_id"]
        or proposal_roles.config_snapshot_hash != acquisition["proposal_role_config_snapshot_hash"]
        or type(review_roles) is not GrantManualReviewRoleResolution
        or review_roles.config_id != review_role_config_id
        or review_roles.config_snapshot_hash != review_role_config_snapshot_hash
        or not _active_role_member(
            transaction,
            candidate.proposed_by,
            proposal_roles.manual_review_proposer_role_id,
        )
        or not _active_role_member(
            transaction,
            candidate.reviewer_id,
            review_roles.manual_review_second_reviewer_role_id,
        )
    ):
        _grant_announcement_conflict()


def apply_grant_announcement_evidence(
    candidate: GrantEvidenceCandidate,
    *,
    review_role_config_id: str,
    review_role_config_snapshot_hash: str,
    transaction: Session,
) -> LifecycleTransitionResult:
    if type(candidate) is not GrantEvidenceCandidate or not isinstance(transaction, Session):
        _grant_announcement_conflict()
    _grant_uuid(review_role_config_id)
    _grant_hash(review_role_config_snapshot_hash)
    try:
        grant_review._validate_candidate(candidate)
    except BusinessError:
        _grant_announcement_conflict()
    if (
        candidate.evidence_scope != GrantEvidenceScope.GRANT_ANNOUNCEMENT.value
        or candidate.review_status != "APPROVED"
        or candidate.reviewer_id == candidate.proposed_by
        or type(candidate.reviewed_at) is not datetime
        or candidate.reviewed_at.utcoffset() is not None
        or candidate.conflict_snapshot is not None
    ):
        _grant_announcement_conflict()
    candidate_payload = _grant_payload(
        candidate.candidate_snapshot,
        candidate.candidate_snapshot_hash,
    )
    acquisition = _grant_payload(
        candidate.acquisition_snapshot,
        candidate.acquisition_snapshot_hash,
    )
    facts = candidate_payload.get("facts")
    if (
        type(facts) is not list
        or len(facts) != 1
        or type(facts[0]) is not dict
        or set(facts[0]) != {"name", "raw_value"}
        or facts[0]["name"] != "announcement_date"
        or candidate_payload.get("conflicts") != []
    ):
        _grant_announcement_conflict()
    announcement_date = facts[0]["raw_value"]
    if type(announcement_date) is not str:
        _grant_announcement_conflict()
    try:
        parsed_date = date.fromisoformat(announcement_date)
    except ValueError:
        _grant_announcement_conflict()
    if parsed_date.isoformat() != announcement_date:
        _grant_announcement_conflict()
    evidence_hash = acquisition.get("evidence_content_hash")
    if (
        type(evidence_hash) is not str
        or re.fullmatch(r"sha256:[0-9a-f]{64}", evidence_hash) is None
    ):
        _grant_announcement_conflict()
    _grant_authority(
        candidate,
        acquisition,
        review_role_config_id,
        review_role_config_snapshot_hash,
        transaction,
    )
    effective_at = datetime.combine(parsed_date, time())
    source_snapshot = json.dumps(
        {
            "schema": "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1",
            "announcement_date": announcement_date,
            "source_document_id": candidate.document_id,
            "source_evidence_version_id": candidate.evidence_version_id,
            "source_evidence_content_hash": evidence_hash,
            "source_provenance_id": candidate.id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=candidate.case_id,
            event_type="GRANT_ANNOUNCEMENT_CONFIRMED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=effective_at,
            occurred_at=candidate.reviewed_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=candidate.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=candidate.evidence_version_id,
                    content_hash=evidence_hash,
                    captured_at=effective_at,
                ),
            ),
            actor_id=candidate.proposed_by,
            reviewer_id=candidate.reviewer_id,
            idempotency_key=f"grant-announcement:{candidate.id}",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "schema": "FPMS_GRANT_ANNOUNCEMENT_CONFIRMED_V1",
                "case_id": candidate.case_id,
                "announcement_date": announcement_date,
                "source_document_id": candidate.document_id,
                "source_evidence_version_id": candidate.evidence_version_id,
                "source_evidence_content_hash": evidence_hash,
                "source_provenance_id": candidate.id,
                "source_snapshot_schema": "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1",
                "source_snapshot": source_snapshot,
                "source_snapshot_hash": hashlib.sha256(source_snapshot.encode()).hexdigest(),
                "predecessor_source_snapshot_hash": None,
                "supersedes_activity_id": None,
            },
        ),
        transaction,
    )


def apply_patent_register_evidence(
    candidate: GrantEvidenceCandidate,
    *,
    review_role_config_id: str,
    review_role_config_snapshot_hash: str,
    transaction: Session,
) -> LifecycleTransitionResult:
    if type(candidate) is not GrantEvidenceCandidate or not isinstance(transaction, Session):
        _patent_register_conflict()
    try:
        _grant_uuid(review_role_config_id)
        _grant_hash(review_role_config_snapshot_hash)
        grant_review._validate_candidate(candidate)
        candidate_payload = _grant_payload(
            candidate.candidate_snapshot,
            candidate.candidate_snapshot_hash,
        )
        acquisition = _grant_payload(
            candidate.acquisition_snapshot,
            candidate.acquisition_snapshot_hash,
        )
    except BusinessError:
        _patent_register_conflict()
    if (
        candidate.evidence_scope != GrantEvidenceScope.PATENT_REGISTER.value
        or candidate.review_status != "APPROVED"
        or candidate.reviewer_id == candidate.proposed_by
        or type(candidate.reviewed_at) is not datetime
        or candidate.reviewed_at.utcoffset() is not None
        or candidate.conflict_snapshot is not None
    ):
        _patent_register_conflict()
    facts = candidate_payload.get("facts")
    if (
        type(facts) is not list
        or len(facts) != 2
        or any(type(fact) is not dict for fact in facts)
        or any(set(fact) != {"name", "raw_value"} for fact in facts)
        or [fact["name"] for fact in facts] != ["observed_at", "register_status"]
        or candidate_payload.get("conflicts") != []
    ):
        _patent_register_conflict()
    observed_at = facts[0]["raw_value"]
    register_status = facts[1]["raw_value"]
    if type(observed_at) is not str or type(register_status) is not str:
        _patent_register_conflict()
    try:
        effective_at = datetime.fromisoformat(observed_at)
    except ValueError:
        _patent_register_conflict()
    if (
        effective_at.utcoffset() is not None
        or effective_at.isoformat(timespec="microseconds") != observed_at
        or register_status
        not in {
            "PATENT_IN_FORCE",
            "PATENT_TERMINATED",
            "PATENT_EXPIRED",
            "PATENT_INVALIDATED",
        }
    ):
        _patent_register_conflict()
    evidence_hash = acquisition.get("evidence_content_hash")
    if (
        type(evidence_hash) is not str
        or re.fullmatch(r"sha256:[0-9a-f]{64}", evidence_hash) is None
    ):
        _patent_register_conflict()
    try:
        _grant_authority(
            candidate,
            acquisition,
            review_role_config_id,
            review_role_config_snapshot_hash,
            transaction,
            evidence_scope=GrantEvidenceScope.PATENT_REGISTER,
        )
    except BusinessError:
        _patent_register_conflict()
    if register_status == "PATENT_INVALIDATED":
        _patent_register_conflict()
    specific_event = {
        "PATENT_TERMINATED": (
            "PATENT_TERMINATION_CONFIRMED",
            "patent-termination:",
        ),
        "PATENT_EXPIRED": (
            "PATENT_EXPIRY_CONFIRMED",
            "patent-expiry:",
        ),
    }.get(register_status)
    if specific_event is not None:
        event_type, idempotency_prefix = specific_event
        return apply_lifecycle_event(
            LifecycleEventCommand(
                case_id=candidate.case_id,
                event_type=event_type,
                lane=ActivityLane.LIFECYCLE,
                effective_at=effective_at,
                occurred_at=candidate.reviewed_at,
                evidence_refs=(
                    EvidenceReference(
                        case_id=candidate.case_id,
                        evidence_kind="PATENT_REGISTER_STATUS_EVIDENCE",
                        object_type="DocumentEvidenceVersion",
                        object_id=candidate.evidence_version_id,
                        content_hash=evidence_hash,
                        captured_at=effective_at,
                    ),
                ),
                actor_id=candidate.proposed_by,
                reviewer_id=candidate.reviewer_id,
                idempotency_key=f"{idempotency_prefix}{candidate.id}",
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={},
            ),
            transaction,
        )
    status_snapshot = json.dumps(
        {
            "schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
            "register_status": register_status,
            "source_document_id": candidate.document_id,
            "source_evidence_version_id": candidate.evidence_version_id,
            "source_evidence_content_hash": evidence_hash,
            "source_provenance_id": candidate.id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=candidate.case_id,
            event_type="PATENT_REGISTER_STATUS_CONFIRMED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=effective_at,
            occurred_at=candidate.reviewed_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=candidate.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=candidate.evidence_version_id,
                    content_hash=evidence_hash,
                    captured_at=effective_at,
                ),
            ),
            actor_id=candidate.proposed_by,
            reviewer_id=candidate.reviewer_id,
            idempotency_key=f"patent-register-status:{candidate.id}",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "schema": "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V1",
                "case_id": candidate.case_id,
                "register_status": register_status,
                "source_document_id": candidate.document_id,
                "source_evidence_version_id": candidate.evidence_version_id,
                "source_evidence_content_hash": evidence_hash,
                "source_provenance_id": candidate.id,
                "status_snapshot_schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
                "status_snapshot": status_snapshot,
                "status_snapshot_hash": hashlib.sha256(status_snapshot.encode()).hexdigest(),
                "predecessor_status_snapshot_hash": None,
                "supersedes_activity_id": None,
            },
        ),
        transaction,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class CopyableOaAttachmentEvidence:
    evidence_version: EvidenceVersionResult
    manifest_id: str
    manifest_case_id: str
    manifest_package_id: str
    manifest_role: str
    manifest_evidence_version_id: str
    manifest_content_hash: str


class CopyableOaAttachmentErrorCode(str, Enum):
    INVALID_CONTEXT = "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT"
    CASE_MISMATCH = "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH"
    PACKAGE_MISMATCH = "OA_COPYABLE_ATTACHMENT_PACKAGE_MISMATCH"
    DUPLICATE_EVIDENCE = "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE"
    DUPLICATE_MANIFEST = "OA_COPYABLE_ATTACHMENT_DUPLICATE_MANIFEST"
    ROLE_NOT_PERMITTED = "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED"
    NOT_STRUCTURED = "OA_COPYABLE_ATTACHMENT_NOT_STRUCTURED"
    NOT_CURRENT = "OA_COPYABLE_ATTACHMENT_NOT_CURRENT"
    NOT_APPROVED = "OA_COPYABLE_ATTACHMENT_NOT_APPROVED"
    NOT_INDEPENDENTLY_REVIEWED = "OA_COPYABLE_ATTACHMENT_NOT_INDEPENDENTLY_REVIEWED"
    STATE_MISMATCH = "OA_COPYABLE_ATTACHMENT_STATE_MISMATCH"
    LINK_MISMATCH = "OA_COPYABLE_ATTACHMENT_LINK_MISMATCH"
    HASH_MISMATCH = "OA_COPYABLE_ATTACHMENT_HASH_MISMATCH"
    STATEMENT_WORD_REQUIRED = "OA_COPYABLE_STATEMENT_WORD_REQUIRED"
    MULTIPLE_STATEMENT_WORDS = "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS"
    MODIFIED_CLAIMS_REQUIRED = "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED"
    MULTIPLE_MODIFIED_CLAIMS = "OA_COPYABLE_MULTIPLE_MODIFIED_CLAIMS"
    MULTIPLE_COMPARISON_PAGES = "OA_COPYABLE_MULTIPLE_COMPARISON_PAGES"


class CopyableOaAttachmentPolicyError(ValueError):
    def __init__(self, code: CopyableOaAttachmentErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> CopyableOaAttachmentErrorCode:
        return self._code


class NoncopyableOaAppendixErrorCode(str, Enum):
    INVALID_CONTEXT = "OA_NONCOPYABLE_APPENDIX_INVALID_CONTEXT"
    FULL_REPLY_PDF_REQUIRED = "OA_NONCOPYABLE_FULL_REPLY_PDF_REQUIRED"
    EXTRACTED_APPENDIX_REQUIRED = "OA_NONCOPYABLE_EXTRACTED_APPENDIX_REQUIRED"
    CASE_MISMATCH = "OA_NONCOPYABLE_APPENDIX_CASE_MISMATCH"
    DERIVATION_MISMATCH = "OA_NONCOPYABLE_APPENDIX_DERIVATION_MISMATCH"
    OTHER_PROOF_NOT_APPENDIX = "OA_NONCOPYABLE_OTHER_PROOF_NOT_APPENDIX"


class NoncopyableOaAppendixPolicyError(ValueError):
    def __init__(self, code: NoncopyableOaAppendixErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> NoncopyableOaAppendixErrorCode:
        return self._code


class FilingXmlDerivationErrorCode(str, Enum):
    INVALID_CONTEXT = "FILING_XML_DERIVATION_INVALID_CONTEXT"
    SOURCE_NOT_FILING_WORD = "FILING_XML_SOURCE_NOT_FILING_WORD"
    SOURCE_NOT_CURRENT = "FILING_XML_SOURCE_NOT_CURRENT"
    SOURCE_NOT_APPROVED = "FILING_XML_SOURCE_NOT_APPROVED"
    SOURCE_NOT_INDEPENDENTLY_REVIEWED = "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED"
    TARGET_NOT_XML = "FILING_XML_TARGET_NOT_XML"
    CASE_MISMATCH = "FILING_XML_DERIVATION_CASE_MISMATCH"
    LINEAGE_MISMATCH = "FILING_XML_DERIVATION_LINEAGE_MISMATCH"
    PATH_SHAPE_MISMATCH = "FILING_XML_DERIVATION_PATH_SHAPE_MISMATCH"
    EDGE_MISMATCH = "FILING_XML_DERIVATION_EDGE_MISMATCH"
    TYPE_MISMATCH = "FILING_XML_DERIVATION_TYPE_MISMATCH"


class FilingXmlDerivationPolicyError(ValueError):
    def __init__(self, code: FilingXmlDerivationErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> FilingXmlDerivationErrorCode:
        return self._code


def _raise(code: FilingXmlDerivationErrorCode) -> None:
    raise FilingXmlDerivationPolicyError(code)


def _is_exact_text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def is_filing_full_word_ready(
    *,
    case_id: str,
    evidence_version: DocumentEvidenceVersion,
) -> bool:
    if (
        not _is_exact_text(case_id)
        or type(evidence_version) is not DocumentEvidenceVersion
        or not _is_exact_text(evidence_version.id)
        or not _is_exact_text(evidence_version.case_id)
        or not _is_exact_text(evidence_version.lineage_key)
        or not _is_exact_text(evidence_version.creator_id)
    ):
        return False
    return (
        evidence_version.case_id == case_id
        and evidence_version.role == EvidenceRole.FILING_FULL_WORD.value
        and evidence_version.current_identity_key == f"{case_id}|{evidence_version.lineage_key}"
        and evidence_version.review_state == EvidenceReviewState.APPROVED.value
        and _is_exact_text(evidence_version.reviewer_id)
        and evidence_version.reviewer_id != evidence_version.creator_id
        and type(evidence_version.reviewed_at) is datetime
        and evidence_version.reviewed_at.tzinfo is None
    )


def _raise_copyable(code: CopyableOaAttachmentErrorCode) -> None:
    raise CopyableOaAttachmentPolicyError(code)


def _raise_noncopyable(code: NoncopyableOaAppendixErrorCode) -> None:
    raise NoncopyableOaAppendixPolicyError(code)


def _has_valid_copyable_evidence_shape(evidence: object) -> bool:
    return (
        type(evidence) is EvidenceVersionResult
        and _is_exact_text(evidence.evidence_version_id)
        and _is_exact_text(evidence.case_id)
        and _is_exact_text(evidence.document_id)
        and _is_exact_text(evidence.attachment_id)
        and _is_exact_text(evidence.lineage_key)
        and type(evidence.role) is EvidenceRole
        and type(evidence.version_number) is int
        and evidence.version_number > 0
        and type(evidence.state) is EvidenceVersionState
        and _is_exact_text(evidence.creator_id)
        and type(evidence.review_state) is EvidenceReviewState
        and (
            evidence.reviewer_id is None
            or _is_exact_text(evidence.reviewer_id)
        )
        and (
            evidence.reviewed_at is None
            or type(evidence.reviewed_at) is datetime
        )
        and (
            evidence.final_submitted_at is None
            or type(evidence.final_submitted_at) is datetime
        )
        and _is_exact_text(evidence.content_hash)
        and _CONTENT_HASH_PATTERN.fullmatch(evidence.content_hash) is not None
        and type(evidence.is_current) is bool
        and type(evidence.is_final) is bool
    )


def require_copyable_oa_attachment_combination(
    *,
    case_id: str,
    package_id: str,
    attachments: tuple[CopyableOaAttachmentEvidence, ...],
) -> None:
    if (
        not _is_exact_text(case_id)
        or not _is_exact_text(package_id)
        or type(attachments) is not tuple
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(
        type(attachment) is not CopyableOaAttachmentEvidence
        or not _has_valid_copyable_evidence_shape(attachment.evidence_version)
        or not _is_exact_text(attachment.manifest_id)
        or not _is_exact_text(attachment.manifest_case_id)
        or not _is_exact_text(attachment.manifest_package_id)
        or not _is_exact_text(attachment.manifest_role)
        or not _is_exact_text(attachment.manifest_evidence_version_id)
        or not _is_exact_text(attachment.manifest_content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(attachment.manifest_content_hash) is None
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(
        attachment.evidence_version.case_id != case_id
        or attachment.manifest_case_id != case_id
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.CASE_MISMATCH)
    if any(attachment.manifest_package_id != package_id for attachment in attachments):
        _raise_copyable(CopyableOaAttachmentErrorCode.PACKAGE_MISMATCH)

    evidence_ids = [
        attachment.evidence_version.evidence_version_id for attachment in attachments
    ]
    if len(evidence_ids) != len(set(evidence_ids)):
        _raise_copyable(CopyableOaAttachmentErrorCode.DUPLICATE_EVIDENCE)
    manifest_ids = [attachment.manifest_id for attachment in attachments]
    if len(manifest_ids) != len(set(manifest_ids)):
        _raise_copyable(CopyableOaAttachmentErrorCode.DUPLICATE_MANIFEST)
    if any(
        attachment.manifest_role not in _COPYABLE_OA_ATTACHMENT_ROLES
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.ROLE_NOT_PERMITTED)
    if any(
        attachment.evidence_version.role is not EvidenceRole.OA_STRUCTURED_ATTACHMENT
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_STRUCTURED)
    if any(not attachment.evidence_version.is_current for attachment in attachments):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_CURRENT)
    if any(
        attachment.evidence_version.review_state is not EvidenceReviewState.APPROVED
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_APPROVED)
    if any(
        not _is_exact_text(attachment.evidence_version.reviewer_id)
        or attachment.evidence_version.reviewer_id
        == attachment.evidence_version.creator_id
        or type(attachment.evidence_version.reviewed_at) is not datetime
        or attachment.evidence_version.reviewed_at.tzinfo is not None
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_INDEPENDENTLY_REVIEWED)
    if any(
        attachment.evidence_version.is_final
        is not (attachment.evidence_version.state is EvidenceVersionState.FINAL)
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.STATE_MISMATCH)
    if any(
        attachment.manifest_evidence_version_id
        != attachment.evidence_version.evidence_version_id
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.LINK_MISMATCH)
    if any(
        attachment.manifest_content_hash != attachment.evidence_version.content_hash
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.HASH_MISMATCH)

    roles = [attachment.manifest_role for attachment in attachments]
    statement_word_count = roles.count("OA_STATEMENT_WORD")
    if statement_word_count == 0:
        _raise_copyable(CopyableOaAttachmentErrorCode.STATEMENT_WORD_REQUIRED)
    if statement_word_count > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_STATEMENT_WORDS)
    modified_claims_count = roles.count("OA_MODIFIED_CLAIMS")
    if modified_claims_count == 0:
        _raise_copyable(CopyableOaAttachmentErrorCode.MODIFIED_CLAIMS_REQUIRED)
    if modified_claims_count > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_MODIFIED_CLAIMS)
    if roles.count("OA_AMENDMENT_COMPARISON") > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_COMPARISON_PAGES)


def _has_coherent_noncopyable_review_tuple(
    evidence: DocumentEvidenceVersion,
) -> bool:
    try:
        review_state = EvidenceReviewState(evidence.review_state)
    except ValueError:
        return False
    if review_state is EvidenceReviewState.PENDING:
        return evidence.reviewer_id is None and evidence.reviewed_at is None
    return (
        _is_exact_text(evidence.reviewer_id)
        and len(evidence.reviewer_id) <= 36
        and evidence.reviewer_id != evidence.creator_id
        and type(evidence.reviewed_at) is datetime
        and evidence.reviewed_at.tzinfo is None
    )


def require_noncopyable_oa_appendix_derivation(
    *,
    case_id: str,
    package: OfficialWorkPackage,
    full_reply_pdf: DocumentEvidenceVersion,
    full_reply_attachment: DocAttachment,
    full_reply_manifest: OfficialWorkPackageManifest,
    extracted_appendix: DocumentEvidenceVersion,
    appendix_attachment: DocAttachment,
    appendix_manifest: OfficialWorkPackageManifest,
    derivation: DocumentEvidenceDerivation,
    other_proof_evidence_version_id: str,
) -> None:
    if (
        not _is_exact_text(case_id)
        or type(package) is not OfficialWorkPackage
        or type(full_reply_pdf) is not DocumentEvidenceVersion
        or type(full_reply_attachment) is not DocAttachment
        or type(full_reply_manifest) is not OfficialWorkPackageManifest
        or type(extracted_appendix) is not DocumentEvidenceVersion
        or type(appendix_attachment) is not DocAttachment
        or type(appendix_manifest) is not OfficialWorkPackageManifest
        or type(derivation) is not DocumentEvidenceDerivation
        or not _is_exact_text(package.id)
        or not _is_exact_text(package.case_id)
        or not _is_exact_text(package.package_kind)
        or not _is_exact_text(full_reply_pdf.id)
        or not _is_exact_text(full_reply_pdf.case_id)
        or not _is_exact_text(full_reply_pdf.document_id)
        or not _is_exact_text(full_reply_pdf.attachment_id)
        or not _is_exact_text(full_reply_pdf.lineage_key)
        or not _is_exact_text(full_reply_pdf.role)
        or type(full_reply_pdf.version_number) is not int
        or not _is_exact_text(full_reply_pdf.state)
        or not _is_exact_text(full_reply_pdf.creator_id)
        or not _is_exact_text(full_reply_pdf.review_state)
        or (
            full_reply_pdf.reviewer_id is not None
            and not _is_exact_text(full_reply_pdf.reviewer_id)
        )
        or (
            full_reply_pdf.reviewed_at is not None
            and type(full_reply_pdf.reviewed_at) is not datetime
        )
        or (
            full_reply_pdf.final_submitted_at is not None
            and type(full_reply_pdf.final_submitted_at) is not datetime
        )
        or not _is_exact_text(full_reply_pdf.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(full_reply_pdf.content_hash) is None
        or (
            full_reply_pdf.current_identity_key is not None
            and not _is_exact_text(full_reply_pdf.current_identity_key)
        )
        or not _is_exact_text(full_reply_attachment.id)
        or not _is_exact_text(full_reply_attachment.document_id)
        or not _is_exact_text(full_reply_attachment.mime_type)
        or not _is_exact_text(full_reply_attachment.official_file_role)
        or not _is_exact_text(full_reply_attachment.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(full_reply_attachment.content_hash) is None
        or not _is_exact_text(full_reply_manifest.id)
        or not _is_exact_text(full_reply_manifest.package_id)
        or not _is_exact_text(full_reply_manifest.attachment_id)
        or not _is_exact_text(full_reply_manifest.evidence_version_id)
        or not _is_exact_text(full_reply_manifest.official_file_role)
        or not _is_exact_text(full_reply_manifest.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(full_reply_manifest.content_hash) is None
        or type(full_reply_manifest.present) is not bool
        or not _is_exact_text(extracted_appendix.id)
        or not _is_exact_text(extracted_appendix.case_id)
        or not _is_exact_text(extracted_appendix.document_id)
        or not _is_exact_text(extracted_appendix.attachment_id)
        or not _is_exact_text(extracted_appendix.lineage_key)
        or not _is_exact_text(extracted_appendix.role)
        or type(extracted_appendix.version_number) is not int
        or not _is_exact_text(extracted_appendix.state)
        or not _is_exact_text(extracted_appendix.creator_id)
        or not _is_exact_text(extracted_appendix.review_state)
        or (
            extracted_appendix.reviewer_id is not None
            and not _is_exact_text(extracted_appendix.reviewer_id)
        )
        or (
            extracted_appendix.reviewed_at is not None
            and type(extracted_appendix.reviewed_at) is not datetime
        )
        or (
            extracted_appendix.final_submitted_at is not None
            and type(extracted_appendix.final_submitted_at) is not datetime
        )
        or not _is_exact_text(extracted_appendix.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(extracted_appendix.content_hash) is None
        or (
            extracted_appendix.current_identity_key is not None
            and not _is_exact_text(extracted_appendix.current_identity_key)
        )
        or not _is_exact_text(appendix_attachment.id)
        or not _is_exact_text(appendix_attachment.document_id)
        or not _is_exact_text(appendix_attachment.official_file_role)
        or not _is_exact_text(appendix_attachment.source_role_alias)
        or not _is_exact_text(appendix_attachment.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(appendix_attachment.content_hash) is None
        or not _is_exact_text(appendix_manifest.id)
        or not _is_exact_text(appendix_manifest.package_id)
        or not _is_exact_text(appendix_manifest.attachment_id)
        or not _is_exact_text(appendix_manifest.evidence_version_id)
        or not _is_exact_text(appendix_manifest.official_file_role)
        or not _is_exact_text(appendix_manifest.source_role_alias)
        or not _is_exact_text(appendix_manifest.content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(appendix_manifest.content_hash) is None
        or type(appendix_manifest.present) is not bool
        or not _is_exact_text(derivation.id)
        or not _is_exact_text(derivation.case_id)
        or not _is_exact_text(derivation.parent_evidence_version_id)
        or not _is_exact_text(derivation.child_evidence_version_id)
        or not _is_exact_text(derivation.derivation_type)
        or not _is_exact_text(derivation.actor_id)
        or type(derivation.derived_at) is not datetime
        or derivation.derived_at.tzinfo is not None
        or not _is_exact_text(derivation.source_snapshot)
        or not _is_exact_text(other_proof_evidence_version_id)
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.INVALID_CONTEXT)
    if (
        package.case_id != case_id
        or full_reply_pdf.case_id != case_id
        or extracted_appendix.case_id != case_id
        or derivation.case_id != case_id
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.CASE_MISMATCH)
    if (
        full_reply_pdf.role != EvidenceRole.GENERATED_ATTACHMENT.value
        or full_reply_pdf.version_number < 1
        or full_reply_pdf.state != EvidenceVersionState.DRAFT.value
        or full_reply_pdf.current_identity_key
        != f"{case_id}|{full_reply_pdf.lineage_key}"
        or not _has_coherent_noncopyable_review_tuple(full_reply_pdf)
        or full_reply_pdf.final_submitted_at is not None
        or full_reply_attachment.mime_type != "application/pdf"
        or full_reply_attachment.official_file_role != "OA_STATEMENT_PDF"
        or full_reply_manifest.official_file_role != "OA_STATEMENT_PDF"
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.FULL_REPLY_PDF_REQUIRED)
    if (
        extracted_appendix.role != EvidenceRole.OA_STRUCTURED_ATTACHMENT.value
        or extracted_appendix.version_number < 1
        or extracted_appendix.state
        not in (
            EvidenceVersionState.DRAFT.value,
            EvidenceVersionState.FINAL.value,
        )
        or extracted_appendix.current_identity_key
        != f"{case_id}|{extracted_appendix.lineage_key}"
        or not _has_coherent_noncopyable_review_tuple(extracted_appendix)
        or appendix_attachment.official_file_role != "OA_OTHER_PROOF"
        or appendix_manifest.official_file_role != "OA_OTHER_PROOF"
        or appendix_attachment.source_role_alias != "OA_STATEMENT_APPENDIX"
        or appendix_manifest.source_role_alias != "OA_STATEMENT_APPENDIX"
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.EXTRACTED_APPENDIX_REQUIRED)
    if (
        package.package_kind != "OA_REPLY"
        or full_reply_manifest.package_id != package.id
        or appendix_manifest.package_id != package.id
        or full_reply_attachment.id != full_reply_pdf.attachment_id
        or full_reply_attachment.document_id != full_reply_pdf.document_id
        or full_reply_manifest.attachment_id != full_reply_attachment.id
        or full_reply_manifest.evidence_version_id != full_reply_pdf.id
        or full_reply_manifest.present is not True
        or appendix_attachment.id != extracted_appendix.attachment_id
        or appendix_attachment.document_id != extracted_appendix.document_id
        or appendix_manifest.attachment_id != appendix_attachment.id
        or appendix_manifest.evidence_version_id != extracted_appendix.id
        or appendix_manifest.present is not True
        or full_reply_attachment.content_hash != full_reply_pdf.content_hash
        or full_reply_manifest.content_hash != full_reply_pdf.content_hash
        or appendix_attachment.content_hash != extracted_appendix.content_hash
        or appendix_manifest.content_hash != extracted_appendix.content_hash
        or full_reply_pdf.id == extracted_appendix.id
        or full_reply_attachment.id == appendix_attachment.id
        or full_reply_pdf.document_id == extracted_appendix.document_id
        or derivation.parent_evidence_version_id != full_reply_pdf.id
        or derivation.child_evidence_version_id != extracted_appendix.id
        or derivation.derivation_type != EvidenceDerivationType.COMPONENT_EXTRACTION.value
        or derivation.source_snapshot != _OA_APPENDIX_SOURCE_SNAPSHOT
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.DERIVATION_MISMATCH)
    if (
        other_proof_evidence_version_id != extracted_appendix.id
        or other_proof_evidence_version_id == full_reply_pdf.id
    ):
        _raise_noncopyable(NoncopyableOaAppendixErrorCode.OTHER_PROOF_NOT_APPENDIX)


def require_filing_xml_reviewed_word_source(
    *,
    case_id: str,
    source_word: DocumentEvidenceVersion,
    xml_evidence: DocumentEvidenceVersion,
    parent_xml_evidence: DocumentEvidenceVersion | None,
    source_derivation: DocumentEvidenceDerivation,
    submission_derivation: DocumentEvidenceDerivation | None,
) -> None:
    if (
        not _is_exact_text(case_id)
        or type(source_word) is not DocumentEvidenceVersion
        or type(xml_evidence) is not DocumentEvidenceVersion
        or (
            parent_xml_evidence is not None
            and type(parent_xml_evidence) is not DocumentEvidenceVersion
        )
        or type(source_derivation) is not DocumentEvidenceDerivation
        or (
            submission_derivation is not None
            and type(submission_derivation) is not DocumentEvidenceDerivation
        )
        or not _is_exact_text(source_word.id)
        or not _is_exact_text(source_word.case_id)
        or not _is_exact_text(source_word.lineage_key)
        or not _is_exact_text(source_word.creator_id)
        or not _is_exact_text(xml_evidence.id)
        or not _is_exact_text(xml_evidence.case_id)
        or not _is_exact_text(xml_evidence.lineage_key)
        or (
            parent_xml_evidence is not None
            and (
                not _is_exact_text(parent_xml_evidence.id)
                or not _is_exact_text(parent_xml_evidence.case_id)
                or not _is_exact_text(parent_xml_evidence.lineage_key)
            )
        )
        or not _is_exact_text(source_derivation.id)
        or not _is_exact_text(source_derivation.case_id)
        or not _is_exact_text(source_derivation.parent_evidence_version_id)
        or not _is_exact_text(source_derivation.child_evidence_version_id)
        or not _is_exact_text(source_derivation.derivation_type)
        or (
            submission_derivation is not None
            and (
                not _is_exact_text(submission_derivation.id)
                or not _is_exact_text(submission_derivation.case_id)
                or not _is_exact_text(submission_derivation.parent_evidence_version_id)
                or not _is_exact_text(submission_derivation.child_evidence_version_id)
                or not _is_exact_text(submission_derivation.derivation_type)
            )
        )
    ):
        _raise(FilingXmlDerivationErrorCode.INVALID_CONTEXT)

    if source_word.role != EvidenceRole.FILING_FULL_WORD.value:
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_FILING_WORD)
    if source_word.current_identity_key != f"{case_id}|{source_word.lineage_key}":
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT)
    if source_word.review_state != EvidenceReviewState.APPROVED.value:
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_APPROVED)
    if (
        not _is_exact_text(source_word.reviewer_id)
        or source_word.reviewer_id == source_word.creator_id
        or type(source_word.reviewed_at) is not datetime
        or source_word.reviewed_at.tzinfo is not None
    ):
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_INDEPENDENTLY_REVIEWED)

    if xml_evidence.role not in (
        EvidenceRole.EXTERNAL_XML_PACKAGE.value,
        EvidenceRole.SUBMITTED_XML.value,
    ):
        _raise(FilingXmlDerivationErrorCode.TARGET_NOT_XML)

    versions = (source_word, xml_evidence) + (
        (parent_xml_evidence,) if parent_xml_evidence is not None else ()
    )
    derivations = (source_derivation,) + (
        (submission_derivation,) if submission_derivation is not None else ()
    )
    if any(version.case_id != case_id for version in versions) or any(
        derivation.case_id != case_id for derivation in derivations
    ):
        _raise(FilingXmlDerivationErrorCode.CASE_MISMATCH)
    if any(version.lineage_key != source_word.lineage_key for version in versions[1:]):
        _raise(FilingXmlDerivationErrorCode.LINEAGE_MISMATCH)

    if xml_evidence.role == EvidenceRole.EXTERNAL_XML_PACKAGE.value:
        if parent_xml_evidence is not None or submission_derivation is not None:
            _raise(FilingXmlDerivationErrorCode.PATH_SHAPE_MISMATCH)
        if (
            source_derivation.parent_evidence_version_id != source_word.id
            or source_derivation.child_evidence_version_id != xml_evidence.id
        ):
            _raise(FilingXmlDerivationErrorCode.EDGE_MISMATCH)
        if source_derivation.derivation_type != EvidenceDerivationType.FORMAT_CONVERSION.value:
            _raise(FilingXmlDerivationErrorCode.TYPE_MISMATCH)
        return

    if (
        parent_xml_evidence is None
        or submission_derivation is None
        or parent_xml_evidence.role != EvidenceRole.EXTERNAL_XML_PACKAGE.value
    ):
        _raise(FilingXmlDerivationErrorCode.PATH_SHAPE_MISMATCH)
    if (
        source_derivation.parent_evidence_version_id != source_word.id
        or source_derivation.child_evidence_version_id != parent_xml_evidence.id
        or submission_derivation.parent_evidence_version_id != parent_xml_evidence.id
        or submission_derivation.child_evidence_version_id != xml_evidence.id
    ):
        _raise(FilingXmlDerivationErrorCode.EDGE_MISMATCH)
    if (
        source_derivation.derivation_type != EvidenceDerivationType.FORMAT_CONVERSION.value
        or submission_derivation.derivation_type != EvidenceDerivationType.EXTERNAL_SUBMISSION.value
    ):
        _raise(FilingXmlDerivationErrorCode.TYPE_MISMATCH)
