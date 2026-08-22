from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cases.lifecycle_contracts import (
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_projection import (
    LegacyProjectionDisposition,
    project_legacy_case_status,
)
from app.modules.cases.models import Case, CaseActivityEvent
from scripts.backfill_v8_document_evidence import import_legacy_document_evidence

__all__ = (
    "LegacyStatePreflightCaseRow",
    "LegacyStatePreflightAttachmentRow",
    "LegacyStatePreflightReport",
    "audit_v8_legacy_state",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyStatePreflightCaseRow:
    case_id: str
    legacy_status: str
    classification: str
    derived_status: str | None
    conflict_codes: tuple[str, ...]
    legacy_granted_unresolved: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyStatePreflightAttachmentRow:
    attachment_id: str
    classification: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyStatePreflightReport:
    case_scanned: int
    case_unchanged: int
    case_update_required: int
    case_conflicts: int
    case_invalid: int
    legacy_granted_unresolved: int
    attachment_scanned: int
    attachment_importable: int
    attachment_unchanged: int
    attachment_invalid: int
    attachment_role_conflicts: int
    attachment_current_conflicts: int
    report_sha256: str
    cases: tuple[LegacyStatePreflightCaseRow, ...]
    attachments: tuple[LegacyStatePreflightAttachmentRow, ...]


def _exact_text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip() and "\x00" not in value


def _latest_confirmed_lifecycle_activity(
    transaction: Session,
    case_id: str,
) -> CaseActivityEvent | None:
    return transaction.scalars(
        select(CaseActivityEvent)
        .where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.lane == "LIFECYCLE",
            CaseActivityEvent.confirmation_status == "CONFIRMED",
        )
        .order_by(CaseActivityEvent.sequence.desc(), CaseActivityEvent.id.desc())
        .limit(1)
    ).first()


def _enum_or_code(value: object, enum_type, code: str, conflicts: set[str]):
    if value is None:
        return None
    try:
        return enum_type(value)
    except (TypeError, ValueError):
        conflicts.add(code)
        return None


def _activity_context(
    activity: CaseActivityEvent | None,
    conflicts: set[str],
) -> tuple[str | None, int | None]:
    if activity is None:
        return None, None
    if not _exact_text(activity.activity_type):
        conflicts.add("LEGACY_STATE_ACTIVITY_TYPE_INVALID")
    try:
        payload = json.loads(activity.payload_json)
    except (TypeError, ValueError):
        conflicts.add("LEGACY_STATE_ACTIVITY_PAYLOAD_INVALID")
        return activity.activity_type, None
    if type(payload) is not dict:
        conflicts.add("LEGACY_STATE_ACTIVITY_PAYLOAD_INVALID")
        return activity.activity_type, None
    oa_sequence = payload.get("oa_sequence")
    if "oa_sequence" in payload and (type(oa_sequence) is not int or oa_sequence < 1):
        conflicts.add("LEGACY_STATE_OA_SEQUENCE_INVALID")
        oa_sequence = None
    return activity.activity_type, oa_sequence


def _case_row(transaction: Session, case: Case) -> LegacyStatePreflightCaseRow:
    conflicts: set[str] = set()
    if not _exact_text(case.id):
        conflicts.add("LEGACY_STATE_CASE_ID_INVALID")
    if not _exact_text(case.status):
        conflicts.add("LEGACY_STATE_STATUS_INVALID")
    business = _enum_or_code(
        case.business_stage,
        BusinessStage,
        "LEGACY_STATE_BUSINESS_STAGE_INVALID",
        conflicts,
    )
    official = _enum_or_code(
        case.official_procedure_stage,
        OfficialProcedureStage,
        "LEGACY_STATE_OFFICIAL_STAGE_INVALID",
        conflicts,
    )
    legal = _enum_or_code(
        case.legal_status,
        LegalStatus,
        "LEGACY_STATE_LEGAL_STATUS_INVALID",
        conflicts,
    )
    verification = _enum_or_code(
        case.lifecycle_verification_status,
        ConfirmationStatus,
        "LEGACY_STATE_VERIFICATION_STATUS_INVALID",
        conflicts,
    )
    if case.lifecycle_revision is not None and (
        type(case.lifecycle_revision) is not int or case.lifecycle_revision < 0
    ):
        conflicts.add("LEGACY_STATE_REVISION_INVALID")
    activity = _latest_confirmed_lifecycle_activity(transaction, case.id)
    activity_type, oa_sequence = _activity_context(activity, conflicts)

    derived_status: str | None = None
    classification = "INVALID_CARRIER"
    projection_conflicts: tuple[str, ...] = ()
    if not conflicts:
        projection = project_legacy_case_status(
            existing_status=case.status,
            projection=LifecycleProjection(
                business_stage=business,
                official_procedure_stage=official,
                legal_status=legal,
                lifecycle_verification_status=verification,
            ),
            latest_confirmed_lifecycle_event_type=activity_type,
            oa_sequence=oa_sequence,
        )
        classification = {
            LegacyProjectionDisposition.UNCHANGED: "UNCHANGED",
            LegacyProjectionDisposition.UPDATE_REQUIRED: "UPDATE_REQUIRED",
            LegacyProjectionDisposition.RETAINED_CONFLICT: "RETAINED_CONFLICT",
        }[projection.disposition]
        derived_status = projection.derived_case_status
        projection_conflicts = tuple(code.value for code in projection.conflict_codes)

    managed_granted = (
        classification == "UNCHANGED"
        and derived_status == "GRANTED"
        and verification is ConfirmationStatus.CONFIRMED
        and not projection_conflicts
    )
    legacy_granted_unresolved = case.status == "GRANTED" and not managed_granted
    all_conflicts = set(projection_conflicts) | conflicts
    if legacy_granted_unresolved:
        all_conflicts.add("LEGACY_GRANTED_UNRESOLVED")
        if classification != "INVALID_CARRIER":
            classification = "RETAINED_CONFLICT"

    return LegacyStatePreflightCaseRow(
        case_id=case.id,
        legacy_status=case.status,
        classification=classification,
        derived_status=derived_status,
        conflict_codes=tuple(sorted(all_conflicts)),
        legacy_granted_unresolved=legacy_granted_unresolved,
    )


def _counts(values: tuple[str, ...], expected: str) -> int:
    return values.count(expected)


def _report_hash(report: LegacyStatePreflightReport) -> str:
    payload = asdict(report)
    payload.pop("report_sha256")
    canonical = json.dumps(
        {"schema": "FPMS_V8_LEGACY_STATE_PREFLIGHT_V1", **payload},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audit_v8_legacy_state(
    *,
    transaction: Session,
    actor_id: str,
) -> LegacyStatePreflightReport:
    with transaction.no_autoflush:
        cases = tuple(
            _case_row(transaction, case)
            for case in transaction.scalars(select(Case).order_by(Case.id)).all()
        )
        evidence_report = import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=True,
        )
        attachments = tuple(
            sorted(
                (
                    LegacyStatePreflightAttachmentRow(
                        attachment_id=row.attachment_id,
                        classification=row.classification,
                    )
                    for row in evidence_report.rows
                ),
                key=lambda row: row.attachment_id,
            )
        )

    case_classes = tuple(row.classification for row in cases)
    attachment_classes = tuple(row.classification for row in attachments)
    values = {
        "case_scanned": len(cases),
        "case_unchanged": _counts(case_classes, "UNCHANGED"),
        "case_update_required": _counts(case_classes, "UPDATE_REQUIRED"),
        "case_conflicts": _counts(case_classes, "RETAINED_CONFLICT"),
        "case_invalid": _counts(case_classes, "INVALID_CARRIER"),
        "legacy_granted_unresolved": sum(row.legacy_granted_unresolved for row in cases),
        "attachment_scanned": len(attachments),
        "attachment_importable": _counts(attachment_classes, "IMPORT"),
        "attachment_unchanged": _counts(attachment_classes, "UNCHANGED"),
        "attachment_invalid": _counts(attachment_classes, "INVALID"),
        "attachment_role_conflicts": _counts(attachment_classes, "ROLE_CONFLICT"),
        "attachment_current_conflicts": _counts(
            attachment_classes,
            "CURRENT_CONFLICT",
        ),
    }
    report = LegacyStatePreflightReport(
        **values,
        report_sha256="",
        cases=cases,
        attachments=attachments,
    )
    return LegacyStatePreflightReport(
        **values,
        report_sha256=_report_hash(report),
        cases=cases,
        attachments=attachments,
    )
