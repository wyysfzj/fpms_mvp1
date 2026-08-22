from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.evidence_service import register_evidence_version
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)

__all__ = (
    "LegacyDocumentEvidenceImportRowResult",
    "LegacyDocumentEvidenceImportResult",
    "import_legacy_document_evidence",
)

_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyDocumentEvidenceImportRowResult:
    attachment_id: str
    classification: str
    planned_write: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyDocumentEvidenceImportResult:
    scanned: int
    imported: int
    unchanged: int
    invalid: int
    role_conflicts: int
    current_conflicts: int
    planned_writes: int
    input_sha256: str
    plan_sha256: str
    output_sha256: str
    rows: tuple[LegacyDocumentEvidenceImportRowResult, ...]


@dataclass(frozen=True, slots=True)
class _PlannedRow:
    case_id: str
    document_id: str
    attachment_id: str
    content_hash: str | None
    result: LegacyDocumentEvidenceImportRowResult


@dataclass(frozen=True, slots=True)
class _Plan:
    actor_id: str
    input_sha256: str
    plan_sha256: str
    rows: tuple[_PlannedRow, ...]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _conflict(code: str, details: dict[str, object] | None = None) -> None:
    raise_business_error(
        code,
        "Legacy document-evidence import conflict",
        details=details,
        status_code=409,
    )


def _is_exact_text(value: object, *, limit: int) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _version_snapshot(version: DocumentEvidenceVersion) -> dict[str, object]:
    return {
        "attachment_id": version.attachment_id,
        "case_id": version.case_id,
        "content_hash": version.content_hash,
        "creator_id": version.creator_id,
        "current_identity_key": version.current_identity_key,
        "document_id": version.document_id,
        "final_submitted_at": (
            version.final_submitted_at.isoformat(timespec="microseconds")
            if version.final_submitted_at is not None
            else None
        ),
        "lineage_key": version.lineage_key,
        "review_state": version.review_state,
        "reviewed_at": (
            version.reviewed_at.isoformat(timespec="microseconds")
            if version.reviewed_at is not None
            else None
        ),
        "reviewer_id": version.reviewer_id,
        "role": version.role,
        "state": version.state,
        "version_number": version.version_number,
    }


def _related_versions(
    transaction: Session,
    *,
    case_id: str,
    attachment_id: str,
) -> tuple[DocumentEvidenceVersion, ...]:
    lineage_key = f"attachment:{attachment_id}"
    current_identity_key = f"{case_id}|{lineage_key}"
    return tuple(
        transaction.scalars(
            select(DocumentEvidenceVersion)
            .where(
                or_(
                    DocumentEvidenceVersion.attachment_id == attachment_id,
                    DocumentEvidenceVersion.lineage_key == lineage_key,
                    DocumentEvidenceVersion.current_identity_key == current_identity_key,
                )
            )
            .order_by(DocumentEvidenceVersion.id)
        )
    )


def _is_unchanged_import(
    version: DocumentEvidenceVersion,
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    content_hash: str,
) -> bool:
    lineage_key = f"attachment:{attachment_id}"
    return (
        version.case_id == case_id
        and version.document_id == document_id
        and version.attachment_id == attachment_id
        and version.lineage_key == lineage_key
        and version.role == EvidenceRole.RAW_ATTACHMENT.value
        and version.version_number == 1
        and version.state == EvidenceVersionState.DRAFT.value
        and _is_exact_text(version.creator_id, limit=36)
        and version.review_state == EvidenceReviewState.PENDING.value
        and version.reviewer_id is None
        and version.reviewed_at is None
        and version.final_submitted_at is None
        and version.content_hash == content_hash
        and version.current_identity_key == f"{case_id}|{lineage_key}"
    )


def _classify(
    transaction: Session,
    document: Document,
    attachment: DocAttachment,
) -> _PlannedRow:
    versions = _related_versions(
        transaction,
        case_id=document.case_id,
        attachment_id=attachment.id,
    )
    if (
        not _is_exact_text(attachment.id, limit=36)
        or not _is_exact_text(document.id, limit=36)
        or not _is_exact_text(document.case_id, limit=36)
        or type(attachment.content_hash) is not str
        or _CONTENT_HASH_PATTERN.fullmatch(attachment.content_hash) is None
    ):
        classification = "INVALID"
        planned_write = False
    elif any(version.role != EvidenceRole.RAW_ATTACHMENT.value for version in versions):
        classification = "ROLE_CONFLICT"
        planned_write = False
    elif len(versions) == 1 and _is_unchanged_import(
        versions[0],
        case_id=document.case_id,
        document_id=document.id,
        attachment_id=attachment.id,
        content_hash=attachment.content_hash,
    ):
        classification = "UNCHANGED"
        planned_write = False
    elif versions:
        classification = "CURRENT_CONFLICT"
        planned_write = False
    else:
        classification = "IMPORT"
        planned_write = True
    return _PlannedRow(
        case_id=document.case_id,
        document_id=document.id,
        attachment_id=attachment.id,
        content_hash=attachment.content_hash,
        result=LegacyDocumentEvidenceImportRowResult(
            attachment_id=attachment.id,
            classification=classification,
            planned_write=planned_write,
        ),
    )


def _build_plan(transaction: Session, actor_id: str) -> _Plan:
    if not _is_exact_text(actor_id, limit=36):
        _conflict("LEGACY_DOCUMENT_EVIDENCE_ACTOR_INVALID")
    if transaction.get(T_User, actor_id) is None:
        _conflict("LEGACY_DOCUMENT_EVIDENCE_ACTOR_MISSING")

    pairs = tuple(
        transaction.execute(
            select(DocAttachment, Document)
            .join(Document, Document.id == DocAttachment.document_id)
            .order_by(DocAttachment.id)
        ).all()
    )
    input_payload = {
        "actor_id": actor_id,
        "rows": [
            {
                "attachment_id": attachment.id,
                "case_id": document.case_id,
                "content_hash": attachment.content_hash,
                "document_id": document.id,
                "versions": [
                    _version_snapshot(version)
                    for version in _related_versions(
                        transaction,
                        case_id=document.case_id,
                        attachment_id=attachment.id,
                    )
                ],
            }
            for attachment, document in pairs
        ],
        "schema": "FPMS_LEGACY_DOCUMENT_EVIDENCE_INPUT_V1",
    }
    input_sha256 = _digest(input_payload)
    rows = tuple(_classify(transaction, document, attachment) for attachment, document in pairs)
    plan_sha256 = _digest(
        {
            "actor_id": actor_id,
            "input_sha256": input_sha256,
            "rows": [
                {
                    "attachment_id": row.attachment_id,
                    "classification": row.result.classification,
                    "planned_write": row.result.planned_write,
                }
                for row in rows
            ],
            "schema": "FPMS_LEGACY_DOCUMENT_EVIDENCE_PLAN_V1",
        }
    )
    return _Plan(
        actor_id=actor_id,
        input_sha256=input_sha256,
        plan_sha256=plan_sha256,
        rows=rows,
    )


def _counts(rows: tuple[_PlannedRow, ...]) -> dict[str, int]:
    classifications = [row.result.classification for row in rows]
    return {
        "scanned": len(rows),
        "imported": classifications.count("IMPORT"),
        "unchanged": classifications.count("UNCHANGED"),
        "invalid": classifications.count("INVALID"),
        "role_conflicts": classifications.count("ROLE_CONFLICT"),
        "current_conflicts": classifications.count("CURRENT_CONFLICT"),
        "planned_writes": sum(row.result.planned_write for row in rows),
    }


def _output_hash(transaction: Session, rows: tuple[_PlannedRow, ...]) -> str:
    output_rows: list[dict[str, object]] = []
    for row in rows:
        output_rows.append(
            {
                "attachment_id": row.attachment_id,
                "versions": [
                    _version_snapshot(version)
                    for version in _related_versions(
                        transaction,
                        case_id=row.case_id,
                        attachment_id=row.attachment_id,
                    )
                ],
            }
        )
    return _digest(
        {
            "rows": output_rows,
            "schema": "FPMS_LEGACY_DOCUMENT_EVIDENCE_OUTPUT_V1",
        }
    )


def _result(transaction: Session, plan: _Plan) -> LegacyDocumentEvidenceImportResult:
    return LegacyDocumentEvidenceImportResult(
        **_counts(plan.rows),
        input_sha256=plan.input_sha256,
        plan_sha256=plan.plan_sha256,
        output_sha256=_output_hash(transaction, plan.rows),
        rows=tuple(row.result for row in plan.rows),
    )


def _apply(transaction: Session, plan: _Plan) -> None:
    try:
        for row in plan.rows:
            if not row.result.planned_write:
                continue
            if row.content_hash is None:
                _conflict("LEGACY_DOCUMENT_EVIDENCE_SOURCE_INVALID")
            result = register_evidence_version(
                RegisterEvidenceVersionCommand(
                    case_id=row.case_id,
                    document_id=row.document_id,
                    attachment_id=row.attachment_id,
                    lineage_key=f"attachment:{row.attachment_id}",
                    role=EvidenceRole.RAW_ATTACHMENT,
                    state=EvidenceVersionState.DRAFT,
                    creator_id=plan.actor_id,
                    content_hash=row.content_hash,
                ),
                transaction,
            )
            if not result.is_current or result.review_state is not EvidenceReviewState.PENDING:
                _conflict("LEGACY_DOCUMENT_EVIDENCE_CURRENT_CONFLICT")
        transaction.flush()
    except BusinessError:
        raise
    except (IntegrityError, OSError, TypeError, ValueError) as exc:
        _conflict(
            "LEGACY_DOCUMENT_EVIDENCE_WRITE_CONFLICT",
            {"error_type": type(exc).__name__},
        )


def import_legacy_document_evidence(
    *,
    transaction: Session,
    actor_id: str,
    dry_run: bool,
    expected_plan_sha256: str | None = None,
) -> LegacyDocumentEvidenceImportResult:
    if not isinstance(transaction, Session):
        _conflict("LEGACY_DOCUMENT_EVIDENCE_TRANSACTION_INVALID")
    if type(dry_run) is not bool:
        _conflict("LEGACY_DOCUMENT_EVIDENCE_DRY_RUN_INVALID")

    with transaction.no_autoflush:
        plan = _build_plan(transaction, actor_id)
        if dry_run:
            if expected_plan_sha256 is not None:
                _conflict("LEGACY_DOCUMENT_EVIDENCE_DRY_RUN_PLAN_PROHIBITED")
            return _result(transaction, plan)
        if (
            expected_plan_sha256 is None
            or _DIGEST_PATTERN.fullmatch(expected_plan_sha256) is None
            or expected_plan_sha256 != plan.plan_sha256
        ):
            _conflict("LEGACY_DOCUMENT_EVIDENCE_PLAN_MISMATCH")

    _apply(transaction, plan)
    return _result(transaction, plan)
