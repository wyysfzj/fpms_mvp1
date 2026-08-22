from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.cases.enums import CaseStatus
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence

__all__ = (
    "LegacyLifecycleImportRowResult",
    "LegacyLifecycleImportResult",
    "import_legacy_lifecycle",
)

_SCHEMA = "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1"
_KEY_PREFIX = "v8-legacy-lifecycle-import:"
_CONFLICT_CODES = (
    "LEGACY_STATUS_UNVERIFIED",
    "NO_REVERSE_MAPPING_AUTHORITY",
)
_KNOWN_STATUSES = frozenset(status.value for status in CaseStatus)
_EMPTY_PROJECTION = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=None,
    lifecycle_verification_status=None,
)
_IMPORTED_PROJECTION = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=LegalStatus.UNKNOWN,
    lifecycle_verification_status=ConfirmationStatus.LEGACY_UNVERIFIED,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyLifecycleImportRowResult:
    case_id: str
    legacy_status: str
    classification: str
    planned_write: bool
    activity_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyLifecycleImportResult:
    scanned: int
    imported: int
    unchanged: int
    conflicts: int
    invalid: int
    planned_writes: int
    input_sha256: str
    plan_sha256: str
    output_sha256: str
    rows: tuple[LegacyLifecycleImportRowResult, ...]


@dataclass(frozen=True, slots=True)
class _PlannedRow:
    case_id: str
    legacy_status: str
    classification: str
    planned_write: bool
    activity_id: str | None


@dataclass(frozen=True, slots=True)
class _Plan:
    actor_id: str
    recorded_at: datetime
    input_sha256: str
    plan_sha256: str
    rows: tuple[_PlannedRow, ...]


def _conflict(field: str | None = None) -> None:
    raise_business_error(
        "LEGACY_LIFECYCLE_IMPORT_CONFLICT",
        "旧案件生命周期导入冲突",
        details=None if field is None else {"field": field},
        status_code=409,
    )


def _plan_conflict() -> None:
    raise_business_error(
        "LEGACY_LIFECYCLE_IMPORT_PLAN_CONFLICT",
        "旧案件生命周期导入计划已变化",
        status_code=409,
    )


def _exact_text(value: object, *, limit: int) -> bool:
    return bool(
        type(value) is str
        and value
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _payload(case_id: str, legacy_status: str) -> dict[str, str]:
    return {
        "case_id": case_id,
        "legacy_status": legacy_status,
        "reverse_mapping": "NONE",
        "schema": _SCHEMA,
    }


def _activity_snapshot(
    transaction: Session,
    activity: CaseActivityEvent,
) -> dict[str, object]:
    return {
        "activity_type": activity.activity_type,
        "actor_id": activity.actor_id,
        "case_id": activity.case_id,
        "confirmation_status": activity.confirmation_status,
        "effective_at": activity.effective_at.isoformat(timespec="microseconds"),
        "id": activity.id,
        "idempotency_key": activity.idempotency_key,
        "lane": activity.lane,
        "new_business_stage": activity.new_business_stage,
        "new_legal_status": activity.new_legal_status,
        "new_official_procedure_stage": activity.new_official_procedure_stage,
        "occurred_at": (
            activity.occurred_at.isoformat(timespec="microseconds")
            if activity.occurred_at is not None
            else None
        ),
        "old_business_stage": activity.old_business_stage,
        "old_legal_status": activity.old_legal_status,
        "old_official_procedure_stage": activity.old_official_procedure_stage,
        "payload_json": activity.payload_json,
        "reviewer_id": activity.reviewer_id,
        "sequence": activity.sequence,
        "source_activity_id": activity.source_activity_id,
        "supersedes_event_id": activity.supersedes_event_id,
        "evidence": [
            {
                "captured_at": evidence.captured_at.isoformat(timespec="microseconds"),
                "case_id": evidence.case_id,
                "content_hash": evidence.content_hash,
                "evidence_kind": evidence.evidence_kind,
                "id": evidence.id,
                "object_id": evidence.object_id,
                "object_type": evidence.object_type,
            }
            for evidence in transaction.scalars(
                select(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == activity.id)
                .order_by(CaseActivityEventEvidence.id)
            )
        ],
    }


def _case_snapshot(
    transaction: Session,
    case: Case,
    activities: tuple[CaseActivityEvent, ...],
) -> dict[str, object]:
    return {
        "activities": [_activity_snapshot(transaction, activity) for activity in activities],
        "business_stage": case.business_stage,
        "case_id": case.id,
        "legal_status": case.legal_status,
        "lifecycle_revision": case.lifecycle_revision,
        "lifecycle_verification_status": case.lifecycle_verification_status,
        "official_procedure_stage": case.official_procedure_stage,
        "status": case.status,
    }


def _activities(transaction: Session, case_id: str) -> tuple[CaseActivityEvent, ...]:
    return tuple(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
            .order_by(CaseActivityEvent.sequence, CaseActivityEvent.id)
        )
    )


def _valid_revision_shape(case: Case) -> bool:
    revision = case.lifecycle_revision
    return revision is None or (type(revision) is int and revision >= 0)


def _history_is_consistent(
    case: Case,
    activities: tuple[CaseActivityEvent, ...],
) -> bool:
    revision = case.lifecycle_revision or 0
    sequences = tuple(activity.sequence for activity in activities)
    if any(type(sequence) is not int or sequence < 1 for sequence in sequences):
        return False
    return len(set(sequences)) == len(sequences) and max(sequences, default=0) == revision


def _exact_existing_import(
    transaction: Session,
    case: Case,
    activities: tuple[CaseActivityEvent, ...],
    *,
    actor_id: str,
    recorded_at: datetime,
) -> CaseActivityEvent | None:
    key = f"{_KEY_PREFIX}{case.id}"
    matching = tuple(activity for activity in activities if activity.idempotency_key == key)
    if len(matching) != 1:
        return None
    activity = matching[0]
    if (
        case.business_stage is not None
        or case.official_procedure_stage is not None
        or case.legal_status != LegalStatus.UNKNOWN.value
        or case.lifecycle_verification_status != ConfirmationStatus.LEGACY_UNVERIFIED.value
        or activity.lane != ActivityLane.LIFECYCLE.value
        or activity.activity_type != "LEGACY_IMPORT"
        or activity.confirmation_status != ConfirmationStatus.LEGACY_UNVERIFIED.value
        or activity.actor_id != actor_id
        or activity.occurred_at != recorded_at
        or activity.effective_at != recorded_at
        or activity.old_business_stage is not None
        or activity.new_business_stage is not None
        or activity.old_official_procedure_stage is not None
        or activity.new_official_procedure_stage is not None
        or activity.old_legal_status is not None
        or activity.new_legal_status != LegalStatus.UNKNOWN.value
        or activity.reviewer_id is not None
        or activity.source_activity_id is not None
        or activity.supersedes_event_id is not None
        or activity.payload_json != _canonical_json(_payload(case.id, case.status))
        or transaction.scalar(
            select(CaseActivityEventEvidence.id)
            .where(CaseActivityEventEvidence.activity_id == activity.id)
            .limit(1)
        )
        is not None
    ):
        return None
    return activity


def _classify(
    transaction: Session,
    case: Case,
    activities: tuple[CaseActivityEvent, ...],
    *,
    actor_id: str,
    recorded_at: datetime,
) -> _PlannedRow:
    status = case.status
    if (
        not _exact_text(case.id, limit=36)
        or not _exact_text(status, limit=32)
        or status not in _KNOWN_STATUSES
        or not _valid_revision_shape(case)
    ):
        classification = "INVALID"
        activity_id = None
    elif not _history_is_consistent(case, activities):
        classification = "CONFLICT"
        activity_id = None
    else:
        existing = _exact_existing_import(
            transaction,
            case,
            activities,
            actor_id=actor_id,
            recorded_at=recorded_at,
        )
        if existing is not None:
            classification = "UNCHANGED"
            activity_id = existing.id
        else:
            projection_is_empty = (
                case.business_stage is None
                and case.official_procedure_stage is None
                and case.legal_status is None
                and case.lifecycle_verification_status is None
            )
            has_lifecycle_history = any(
                activity.lane == ActivityLane.LIFECYCLE.value for activity in activities
            )
            has_reserved_key = any(
                activity.idempotency_key == f"{_KEY_PREFIX}{case.id}" for activity in activities
            )
            if projection_is_empty and not has_lifecycle_history and not has_reserved_key:
                classification = "IMPORT"
            else:
                classification = "CONFLICT"
            activity_id = None
    return _PlannedRow(
        case_id=case.id,
        legacy_status=status,
        classification=classification,
        planned_write=classification == "IMPORT",
        activity_id=activity_id,
    )


def _build_plan(
    transaction: Session,
    *,
    actor_id: str,
    recorded_at: datetime,
) -> _Plan:
    cases = tuple(transaction.scalars(select(Case).order_by(Case.id)))
    activity_by_case = {case.id: _activities(transaction, case.id) for case in cases}
    input_sha256 = _digest(
        {
            "actor_id": actor_id,
            "recorded_at": recorded_at.isoformat(timespec="microseconds"),
            "rows": [
                _case_snapshot(transaction, case, activity_by_case[case.id]) for case in cases
            ],
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_INPUT_V1",
        }
    )
    rows = tuple(
        _classify(
            transaction,
            case,
            activity_by_case[case.id],
            actor_id=actor_id,
            recorded_at=recorded_at,
        )
        for case in cases
    )
    plan_sha256 = _digest(
        {
            "actor_id": actor_id,
            "input_sha256": input_sha256,
            "recorded_at": recorded_at.isoformat(timespec="microseconds"),
            "rows": [
                {
                    "case_id": row.case_id,
                    "classification": row.classification,
                    "legacy_status": row.legacy_status,
                    "planned_write": row.planned_write,
                }
                for row in rows
            ],
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_PLAN_V1",
        }
    )
    return _Plan(
        actor_id=actor_id,
        recorded_at=recorded_at,
        input_sha256=input_sha256,
        plan_sha256=plan_sha256,
        rows=rows,
    )


def _counts(rows: tuple[_PlannedRow, ...]) -> dict[str, int]:
    classifications = tuple(row.classification for row in rows)
    return {
        "scanned": len(rows),
        "imported": classifications.count("IMPORT"),
        "unchanged": classifications.count("UNCHANGED"),
        "conflicts": classifications.count("CONFLICT"),
        "invalid": classifications.count("INVALID"),
        "planned_writes": sum(row.planned_write for row in rows),
    }


def _output_sha256(transaction: Session, rows: tuple[_PlannedRow, ...]) -> str:
    output: list[dict[str, object]] = []
    for row in rows:
        case = transaction.get(Case, row.case_id)
        if case is None:
            output.append({"case_id": row.case_id, "missing": True})
            continue
        output.append(_case_snapshot(transaction, case, _activities(transaction, case.id)))
    return _digest({"rows": output, "schema": "FPMS_V8_LEGACY_LIFECYCLE_OUTPUT_V1"})


def _result(transaction: Session, plan: _Plan) -> LegacyLifecycleImportResult:
    rows: list[LegacyLifecycleImportRowResult] = []
    for planned in plan.rows:
        activity_id = planned.activity_id
        if planned.planned_write:
            activity_id = transaction.scalar(
                select(CaseActivityEvent.id).where(
                    CaseActivityEvent.case_id == planned.case_id,
                    CaseActivityEvent.idempotency_key == f"{_KEY_PREFIX}{planned.case_id}",
                )
            )
        rows.append(
            LegacyLifecycleImportRowResult(
                case_id=planned.case_id,
                legacy_status=planned.legacy_status,
                classification=planned.classification,
                planned_write=planned.planned_write,
                activity_id=activity_id,
            )
        )
    return LegacyLifecycleImportResult(
        **_counts(plan.rows),
        input_sha256=plan.input_sha256,
        plan_sha256=plan.plan_sha256,
        output_sha256=_output_sha256(transaction, plan.rows),
        rows=tuple(rows),
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN")


def _apply(transaction: Session, plan: _Plan) -> None:
    _ensure_sqlite_outer_transaction(transaction)
    with transaction.begin_nested():
        for row in plan.rows:
            if not row.planned_write:
                continue
            result = append_case_activity(
                LifecycleEventCommand(
                    case_id=row.case_id,
                    event_type="LEGACY_IMPORT",
                    lane=ActivityLane.LIFECYCLE,
                    effective_at=plan.recorded_at,
                    evidence_refs=(),
                    actor_id=plan.actor_id,
                    idempotency_key=f"{_KEY_PREFIX}{row.case_id}",
                    confirmation_status=ConfirmationStatus.LEGACY_UNVERIFIED,
                    payload=_payload(row.case_id, row.legacy_status),
                    occurred_at=plan.recorded_at,
                    reviewer_id=None,
                    source_activity_id=None,
                    supersedes_event_id=None,
                ),
                transaction,
                previous_projection=_EMPTY_PROJECTION,
                current_projection=_IMPORTED_PROJECTION,
                legacy_case_status=row.legacy_status,
                conflict_codes=_CONFLICT_CODES,
            )
            if (
                result.case_id != row.case_id
                or result.event_type != "LEGACY_IMPORT"
                or result.current_projection != _IMPORTED_PROJECTION
                or result.legacy_case_status != row.legacy_status
                or result.confirmation_status is not ConfirmationStatus.LEGACY_UNVERIFIED
                or result.conflict_codes != _CONFLICT_CODES
            ):
                _conflict("result")


def import_legacy_lifecycle(
    *,
    transaction: Session,
    actor_id: str,
    recorded_at: datetime,
    dry_run: bool,
    expected_plan_sha256: str | None = None,
) -> LegacyLifecycleImportResult:
    if not isinstance(transaction, Session):
        _conflict("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict("transaction")
    if not _exact_text(actor_id, limit=36):
        _conflict("actor_id")
    if type(recorded_at) is not datetime or recorded_at.tzinfo is not None:
        _conflict("recorded_at")
    if type(dry_run) is not bool:
        _conflict("dry_run")
    if expected_plan_sha256 is not None and (
        type(expected_plan_sha256) is not str
        or len(expected_plan_sha256) != 64
        or any(character not in "0123456789abcdef" for character in expected_plan_sha256)
    ):
        _conflict("expected_plan_sha256")
    with transaction.no_autoflush:
        if transaction.get(T_User, actor_id) is None:
            _conflict("actor_id")
        plan = _build_plan(
            transaction,
            actor_id=actor_id,
            recorded_at=recorded_at,
        )
    if dry_run:
        return _result(transaction, plan)
    if expected_plan_sha256 != plan.plan_sha256:
        _plan_conflict()
    _apply(transaction, plan)
    return _result(transaction, plan)
