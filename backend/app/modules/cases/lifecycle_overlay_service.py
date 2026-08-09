from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_schemas import (
    LifecycleOverlay,
    OverlayCenterAxis,
    OverlayCenterAxisChange,
    OverlayCenterSnapshot,
    OverlayMilestone,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence

__all__ = ("read_lifecycle_overlay",)

_EnumT = TypeVar("_EnumT")


def read_lifecycle_overlay(
    *,
    case_id: str,
    after_sequence: int,
    limit: int,
    as_of_revision: int | None,
    transaction: Session,
) -> LifecycleOverlay:
    generated_at = _utc_now()
    case_state = transaction.execute(
        select(
            Case.business_stage,
            Case.official_procedure_stage,
            Case.legal_status,
            Case.lifecycle_verification_status,
            Case.lifecycle_revision,
        ).where(Case.id == case_id)
    ).one_or_none()
    if case_state is None:
        _fail("CASE_NOT_FOUND", "案件不存在", status_code=404)

    current_revision = _current_revision(case_state)
    revision = current_revision if as_of_revision is None else as_of_revision
    if (
        not isinstance(after_sequence, int)
        or isinstance(after_sequence, bool)
        or not isinstance(limit, int)
        or isinstance(limit, bool)
        or not isinstance(revision, int)
        or isinstance(revision, bool)
        or after_sequence < 0
        or limit <= 0
        or revision < 0
        or revision > current_revision
        or after_sequence > revision
    ):
        _fail(
            "LIFECYCLE_OVERLAY_QUERY_INVALID",
            "生命周期视图查询参数无效",
            details={
                "case_id": case_id,
                "after_sequence": after_sequence,
                "limit": limit,
                "as_of_revision": as_of_revision,
                "current_revision": current_revision,
            },
            status_code=400,
        )

    activities = (
        transaction.execute(
            select(CaseActivityEvent)
            .where(
                CaseActivityEvent.case_id == case_id,
                CaseActivityEvent.sequence <= revision,
            )
            .order_by(CaseActivityEvent.sequence, CaseActivityEvent.id)
        )
        .scalars()
        .all()
    )
    if [activity.sequence for activity in activities] != list(range(1, revision + 1)):
        _state_conflict(case_id, "ACTIVITY_SEQUENCE_INVALID")

    parsed = _validate_and_parse_activities(case_id, activities)
    frozen = parsed
    center_activity = next(
        (item for item in reversed(frozen) if item[1] is ActivityLane.LIFECYCLE),
        None,
    )
    center_snapshot = _center_snapshot(case_id, revision, center_activity)
    if revision == current_revision:
        _validate_current_projection(case_id, case_state, center_snapshot, current_revision)

    page = tuple(item for item in frozen if item[0].sequence > after_sequence)
    evidence_by_activity = _read_evidence(
        transaction,
        case_id=case_id,
        activity_ids=tuple(item[0].id for item in page),
    )
    milestones = tuple(
        _milestone(activity, lane, axes, evidence_by_activity.get(activity.id, ()))
        for activity, lane, axes in page
    )
    return LifecycleOverlay(
        case_id=case_id,
        lifecycle_revision=revision,
        generated_at=generated_at,
        center_snapshot=center_snapshot,
        milestones=milestones,
        decision_gates=(),
        warnings=(),
        legacy_conflicts=(),
        next_cursor=None,
        has_more=False,
    )


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _current_revision(case_state: object) -> int:
    revision = case_state.lifecycle_revision
    carriers = (
        case_state.business_stage,
        case_state.official_procedure_stage,
        case_state.legal_status,
        case_state.lifecycle_verification_status,
    )
    if revision is None:
        if any(value is not None for value in carriers):
            _state_conflict(None, "REVISION_MISSING")
        return 0
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        _state_conflict(None, "REVISION_INVALID")
    if revision == 0 and any(value is not None for value in carriers):
        _state_conflict(None, "ZERO_REVISION_HAS_PROJECTION")
    return revision


def _validate_and_parse_activities(
    case_id: str,
    activities: list[CaseActivityEvent],
) -> tuple[
    tuple[
        CaseActivityEvent,
        ActivityLane,
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ],
    ],
    ...,
]:
    result = []
    projection: (
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ]
        | None
    ) = None
    for activity in activities:
        try:
            lane = ActivityLane(activity.lane)
            ConfirmationStatus(activity.confirmation_status)
            old_axes = (
                _parse_optional(activity.old_business_stage, BusinessStage),
                _parse_optional(
                    activity.old_official_procedure_stage,
                    OfficialProcedureStage,
                ),
                _parse_optional(activity.old_legal_status, LegalStatus),
            )
            new_axes = (
                _parse_optional(activity.new_business_stage, BusinessStage),
                _parse_optional(
                    activity.new_official_procedure_stage,
                    OfficialProcedureStage,
                ),
                _parse_optional(activity.new_legal_status, LegalStatus),
            )
        except (TypeError, ValueError):
            _state_conflict(case_id, "ACTIVITY_ENUM_INVALID")
        if projection is not None and old_axes != projection:
            _state_conflict(case_id, "ACTIVITY_PROJECTION_GAP")
        if lane is not ActivityLane.LIFECYCLE and old_axes != new_axes:
            _state_conflict(case_id, "NON_LIFECYCLE_CENTER_CHANGE")
        projection = new_axes
        result.append((activity, lane, (*old_axes, *new_axes)))
    return tuple(result)


def _parse_optional(value: str | None, enum_type: type[_EnumT]) -> _EnumT | None:
    return None if value is None else enum_type(value)


def _center_snapshot(
    case_id: str,
    revision: int,
    center_activity: tuple[
        CaseActivityEvent,
        ActivityLane,
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ],
    ]
    | None,
) -> OverlayCenterSnapshot:
    if center_activity is None:
        if revision != 0:
            _state_conflict(case_id, "LIFECYCLE_ACTIVITY_MISSING")
        return OverlayCenterSnapshot(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=None,
            effective_at=None,
            verification_status=None,
            source_event_id=None,
        )
    activity, _, axes = center_activity
    return OverlayCenterSnapshot(
        business_stage=axes[3],
        official_procedure_stage=axes[4],
        legal_status=axes[5],
        effective_at=activity.effective_at,
        verification_status=_parse_optional(
            activity.confirmation_status,
            ConfirmationStatus,
        ),
        source_event_id=activity.id,
    )


def _validate_current_projection(
    case_id: str,
    case_state: object,
    snapshot: OverlayCenterSnapshot,
    revision: int,
) -> None:
    try:
        stored = (
            _parse_optional(case_state.business_stage, BusinessStage),
            _parse_optional(
                case_state.official_procedure_stage,
                OfficialProcedureStage,
            ),
            _parse_optional(case_state.legal_status, LegalStatus),
            _parse_optional(
                case_state.lifecycle_verification_status,
                ConfirmationStatus,
            ),
        )
    except (TypeError, ValueError):
        _state_conflict(case_id, "CASE_PROJECTION_ENUM_INVALID")
    reconstructed = (
        snapshot.business_stage,
        snapshot.official_procedure_stage,
        snapshot.legal_status,
        snapshot.verification_status,
    )
    if revision == 0:
        if stored != (None, None, None, None):
            _state_conflict(case_id, "ZERO_REVISION_HAS_PROJECTION")
    elif stored != reconstructed:
        _state_conflict(case_id, "CASE_PROJECTION_MISMATCH")


def _read_evidence(
    transaction: Session,
    *,
    case_id: str,
    activity_ids: tuple[str, ...],
) -> dict[str, tuple[EvidenceReference, ...]]:
    if not activity_ids:
        return {}
    rows = transaction.execute(
        select(CaseActivityEventEvidence)
        .where(
            CaseActivityEventEvidence.case_id == case_id,
            CaseActivityEventEvidence.activity_id.in_(activity_ids),
        )
        .order_by(
            CaseActivityEventEvidence.activity_id,
            CaseActivityEventEvidence.evidence_kind,
            CaseActivityEventEvidence.object_type,
            CaseActivityEventEvidence.object_id,
        )
    ).scalars()
    grouped: defaultdict[str, list[EvidenceReference]] = defaultdict(list)
    for row in rows:
        grouped[row.activity_id].append(
            EvidenceReference(
                case_id=row.case_id,
                evidence_kind=row.evidence_kind,
                object_type=row.object_type,
                object_id=row.object_id,
                content_hash=row.content_hash,
                captured_at=row.captured_at,
            )
        )
    return {key: tuple(values) for key, values in grouped.items()}


def _milestone(
    activity: CaseActivityEvent,
    lane: ActivityLane,
    axes: tuple[
        BusinessStage | None,
        OfficialProcedureStage | None,
        LegalStatus | None,
        BusinessStage | None,
        OfficialProcedureStage | None,
        LegalStatus | None,
    ],
    evidence: tuple[EvidenceReference, ...],
) -> OverlayMilestone:
    changes: dict[OverlayCenterAxis, OverlayCenterAxisChange] = {}
    if lane is ActivityLane.LIFECYCLE:
        for axis, old, new in (
            (OverlayCenterAxis.BUSINESS_STAGE, axes[0], axes[3]),
            (OverlayCenterAxis.OFFICIAL_PROCEDURE_STAGE, axes[1], axes[4]),
            (OverlayCenterAxis.LEGAL_STATUS, axes[2], axes[5]),
        ):
            if old != new:
                changes[axis] = OverlayCenterAxisChange(
                    previous_value=old,
                    current_value=new,
                )
    return OverlayMilestone(
        sequence=activity.sequence,
        activity_id=activity.id,
        lane=lane,
        activity_type=activity.activity_type,
        source_activity_id=activity.source_activity_id,
        effective_at=activity.effective_at,
        confirmation_status=ConfirmationStatus(activity.confirmation_status),
        center_changes=changes,
        document_evidence=(),
        work_packages=(),
        tasks=(),
        fee_obligations=(),
        evidence_summary=evidence,
        warnings=(),
    )


def _state_conflict(case_id: str | None, reason: str) -> None:
    _fail(
        "LIFECYCLE_OVERLAY_STATE_CONFLICT",
        "生命周期视图数据不一致",
        details={"case_id": case_id, "reason": reason},
        status_code=409,
    )


def _fail(
    code: str,
    message: str,
    *,
    details: dict[str, object] | None = None,
    status_code: int,
) -> None:
    raise BusinessError(code, message, details=details, status_code=status_code)
