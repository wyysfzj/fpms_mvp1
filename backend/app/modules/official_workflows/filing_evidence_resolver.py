from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_EXTERNAL_SUBMISSION_ELIGIBLE_ROLES = frozenset(
    {
        "FILING_FULL_WORD",
        "TRACKED_REVISED_WORD",
        "FILING_COMPONENT",
        "EXTERNAL_XML_PACKAGE",
        "OFFICIAL_SUBMISSION_LIST",
        "OFFICIAL_FINAL_PDF",
        "SUBMITTED_XML",
        "OFFICIAL_RECEIPT",
        "CLIENT_LETTER_WORD",
    }
)
_ACTIVITY_TYPE = "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED"
_IDEMPOTENCY_NAMESPACE = "document-external-submission:"


@dataclass(frozen=True, slots=True, kw_only=True)
class FilingFinalEvidenceResolution:
    package_id: str
    case_id: str
    evidence_version_id: str
    content_hash: str
    reviewer_id: str
    reviewed_at: datetime
    final_submitted_at: datetime | None
    submission_activity_id: str | None
    submission_activity_hash: str | None

    def __post_init__(self) -> None:
        if (self.submission_activity_id is None) != (self.submission_activity_hash is None):
            _conflict("Submission activity result is incomplete")


def _invalid(message: str) -> None:
    raise_business_error(
        "FILING_FINAL_EVIDENCE_INVALID",
        message,
        status_code=400,
    )


def _conflict(message: str) -> None:
    raise_business_error(
        "FILING_FINAL_EVIDENCE_CONFLICT",
        message,
        status_code=409,
    )


def _valid_text(value: object, *, max_length: int) -> bool:
    return type(value) is str and bool(value.strip()) and len(value) <= max_length


def _valid_naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.tzinfo is None


def _load_exact_payload(value: object) -> dict[str, str]:
    if type(value) is not str:
        _conflict("Submission activity payload is invalid")
    try:
        pairs = json.loads(value, object_pairs_hook=lambda items: items)
    except (TypeError, ValueError):
        _conflict("Submission activity payload is invalid")
    if (
        type(pairs) is not list
        or len(pairs) != 4
        or any(type(pair) is not tuple or len(pair) != 2 for pair in pairs)
    ):
        _conflict("Submission activity payload is invalid")
    payload = dict(pairs)
    if len(payload) != 4:
        _conflict("Submission activity payload is invalid")
    return payload


def _activity_hash(
    *,
    activity: object,
    evidence: object,
    case_id: str,
    version: object,
    payload: dict[str, str],
) -> str:
    submitted_at = version.final_submitted_at
    snapshot = {
        "activity_id": activity.id,
        "activity_type": _ACTIVITY_TYPE,
        "actor_id": activity.actor_id,
        "case_id": case_id,
        "confirmation_status": "CONFIRMED",
        "effective_at": submitted_at.isoformat(),
        "evidence": [
            {
                "captured_at": submitted_at.isoformat(),
                "content_hash": version.content_hash,
                "evidence_kind": "DOCUMENT_EVIDENCE_VERSION",
                "object_id": version.id,
                "object_type": "DocumentEvidenceVersion",
            }
        ],
        "idempotency_key": activity.idempotency_key,
        "lane": "DOCUMENT",
        "occurred_at": submitted_at.isoformat(),
        "payload": payload,
        "reviewer_id": version.reviewer_id,
    }
    exact_bytes = json.dumps(
        snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(exact_bytes).hexdigest()}"


def resolve_filing_final_evidence(
    package_id: str,
    transaction: Session,
) -> FilingFinalEvidenceResolution:
    if not _valid_text(package_id, max_length=36):
        _invalid("Invalid filing package identifier")
    if not isinstance(transaction, Session):
        _invalid("Invalid transaction boundary")
    if transaction.new or transaction.dirty or transaction.deleted:
        _invalid("Transaction boundary must be clean")

    with transaction.no_autoflush:
        packages = transaction.execute(
            select(
                OfficialWorkPackage.id,
                OfficialWorkPackage.case_id,
                OfficialWorkPackage.package_kind,
            )
            .where(OfficialWorkPackage.id == package_id)
            .limit(2)
        ).all()
        if not packages:
            raise_business_error(
                "OFFICIAL_WORK_PACKAGE_NOT_FOUND",
                "Official work package not found",
                status_code=404,
            )
        package = packages[0]
        if len(packages) != 1 or package.package_kind != "FILING_PREP":
            _conflict("Filing work package identity is invalid")
        if not _valid_text(package.case_id, max_length=36):
            _conflict("Filing work package ownership is invalid")

        manifests = transaction.execute(
            select(
                OfficialWorkPackageManifest.id,
                OfficialWorkPackageManifest.package_id,
                OfficialWorkPackageManifest.attachment_id,
                OfficialWorkPackageManifest.evidence_version_id,
                OfficialWorkPackageManifest.content_hash,
            )
            .where(
                OfficialWorkPackageManifest.package_id == package_id,
                OfficialWorkPackageManifest.present.is_(True),
                OfficialWorkPackageManifest.evidence_version_id.is_not(None),
            )
            .limit(2)
        ).all()
        if len(manifests) != 1:
            _conflict("Filing manifest evidence selection is ambiguous")
        manifest = manifests[0]

        versions = transaction.execute(
            select(
                DocumentEvidenceVersion.id,
                DocumentEvidenceVersion.case_id,
                DocumentEvidenceVersion.document_id,
                DocumentEvidenceVersion.attachment_id,
                DocumentEvidenceVersion.lineage_key,
                DocumentEvidenceVersion.role,
                DocumentEvidenceVersion.state,
                DocumentEvidenceVersion.creator_id,
                DocumentEvidenceVersion.review_state,
                DocumentEvidenceVersion.reviewer_id,
                DocumentEvidenceVersion.reviewed_at,
                DocumentEvidenceVersion.final_submitted_at,
                DocumentEvidenceVersion.content_hash,
                DocumentEvidenceVersion.current_identity_key,
            )
            .where(DocumentEvidenceVersion.id == manifest.evidence_version_id)
            .limit(2)
        ).all()
        if not versions:
            raise_business_error(
                "EVIDENCE_VERSION_NOT_FOUND",
                "Evidence version not found",
                status_code=404,
            )
        if len(versions) != 1:
            _conflict("Evidence version selection is ambiguous")
        version = versions[0]

        documents = transaction.execute(
            select(Document.id, Document.case_id).where(Document.id == version.document_id).limit(2)
        ).all()
        attachments = transaction.execute(
            select(DocAttachment.id, DocAttachment.document_id)
            .where(DocAttachment.id == version.attachment_id)
            .limit(2)
        ).all()
        if len(documents) != 1 or len(attachments) != 1:
            _conflict("Evidence document ownership is dangling")
        document = documents[0]
        attachment = attachments[0]

        if (
            version.case_id != package.case_id
            or document.case_id != package.case_id
            or attachment.document_id != document.id
            or manifest.package_id != package.id
            or manifest.attachment_id != version.attachment_id
            or attachment.id != version.attachment_id
            or not _valid_text(version.document_id, max_length=36)
            or not _valid_text(version.attachment_id, max_length=36)
        ):
            _conflict("Evidence ownership or manifest linkage is invalid")
        if (
            type(version.content_hash) is not str
            or _CONTENT_HASH_PATTERN.fullmatch(version.content_hash) is None
            or manifest.content_hash != version.content_hash
        ):
            _conflict("Evidence content hash is invalid")
        if (
            not _valid_text(version.lineage_key, max_length=128)
            or version.current_identity_key != f"{package.case_id}|{version.lineage_key}"
            or version.state != "FINAL"
            or version.review_state != "APPROVED"
            or version.role not in _EXTERNAL_SUBMISSION_ELIGIBLE_ROLES
            or not _valid_text(version.creator_id, max_length=36)
            or not _valid_text(version.reviewer_id, max_length=36)
            or version.reviewer_id == version.creator_id
            or not _valid_naive_datetime(version.reviewed_at)
        ):
            _conflict("Evidence final approval identity is invalid")
        if version.final_submitted_at is not None and not _valid_naive_datetime(
            version.final_submitted_at
        ):
            _conflict("Evidence final submission time is invalid")

        linked_activity_exists = (
            select(CaseActivityEventEvidence.id)
            .where(
                CaseActivityEventEvidence.activity_id == CaseActivityEvent.id,
                CaseActivityEventEvidence.object_id == version.id,
            )
            .exists()
        )
        activities = transaction.execute(
            select(
                CaseActivityEvent.id,
                CaseActivityEvent.case_id,
                CaseActivityEvent.lane,
                CaseActivityEvent.activity_type,
                CaseActivityEvent.occurred_at,
                CaseActivityEvent.effective_at,
                CaseActivityEvent.confirmation_status,
                CaseActivityEvent.actor_id,
                CaseActivityEvent.reviewer_id,
                CaseActivityEvent.idempotency_key,
                CaseActivityEvent.payload_json,
            )
            .where(
                CaseActivityEvent.case_id == package.case_id,
                CaseActivityEvent.activity_type == _ACTIVITY_TYPE,
                linked_activity_exists,
            )
            .limit(2)
        ).all()

        if version.final_submitted_at is None:
            if activities:
                _conflict("Submission activity exists without finalized carrier time")
            return FilingFinalEvidenceResolution(
                package_id=package.id,
                case_id=package.case_id,
                evidence_version_id=version.id,
                content_hash=version.content_hash,
                reviewer_id=version.reviewer_id,
                reviewed_at=version.reviewed_at,
                final_submitted_at=None,
                submission_activity_id=None,
                submission_activity_hash=None,
            )

        if len(activities) != 1:
            _conflict("Finalized submission activity selection is ambiguous")
        activity = activities[0]
        links = transaction.execute(
            select(
                CaseActivityEventEvidence.id,
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.activity_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
                CaseActivityEventEvidence.content_hash,
                CaseActivityEventEvidence.captured_at,
            )
            .where(CaseActivityEventEvidence.activity_id == activity.id)
            .limit(2)
        ).all()
        if len(links) != 1:
            _conflict("Finalized submission evidence link is ambiguous")
        evidence = links[0]
        submitted_at = version.final_submitted_at
        if (
            activity.case_id != package.case_id
            or activity.activity_type != _ACTIVITY_TYPE
            or activity.lane != "DOCUMENT"
            or activity.confirmation_status != "CONFIRMED"
            or not _valid_text(activity.actor_id, max_length=36)
            or activity.reviewer_id != version.reviewer_id
            or not _valid_naive_datetime(activity.effective_at)
            or not _valid_naive_datetime(activity.occurred_at)
            or activity.effective_at != submitted_at
            or activity.occurred_at != submitted_at
            or type(activity.idempotency_key) is not str
            or not activity.idempotency_key.startswith(_IDEMPOTENCY_NAMESPACE)
            or evidence.case_id != package.case_id
            or evidence.activity_id != activity.id
            or evidence.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
            or evidence.object_type != "DocumentEvidenceVersion"
            or evidence.object_id != version.id
            or evidence.content_hash != version.content_hash
            or not _valid_naive_datetime(evidence.captured_at)
            or evidence.captured_at != submitted_at
        ):
            _conflict("Finalized submission activity evidence is invalid")

        payload = _load_exact_payload(activity.payload_json)
        if payload != {
            "evidence_version_id": version.id,
            "lineage_key": version.lineage_key,
            "role": version.role,
            "submitted_at": submitted_at.isoformat(),
        }:
            _conflict("Finalized submission activity payload is invalid")
        activity_hash = _activity_hash(
            activity=activity,
            evidence=evidence,
            case_id=package.case_id,
            version=version,
            payload=payload,
        )
        return FilingFinalEvidenceResolution(
            package_id=package.id,
            case_id=package.case_id,
            evidence_version_id=version.id,
            content_hash=version.content_hash,
            reviewer_id=version.reviewer_id,
            reviewed_at=version.reviewed_at,
            final_submitted_at=submitted_at,
            submission_activity_id=activity.id,
            submission_activity_hash=activity_hash,
        )


__all__ = ("FilingFinalEvidenceResolution", "resolve_filing_final_evidence")
