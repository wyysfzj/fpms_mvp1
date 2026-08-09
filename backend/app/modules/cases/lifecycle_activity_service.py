from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from typing import TypeVar, cast
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventConflict,
    CaseActivityEventEvidence,
)

__all__ = ("append_case_activity", "read_activity_conflict_codes")

_EnumT = TypeVar("_EnumT", bound=StrEnum)
_CASE_SERVICE_ATTRIBUTES = (
    "business_stage",
    "official_procedure_stage",
    "legal_status",
    "lifecycle_verification_status",
    "lifecycle_revision",
    "status",
)


def append_case_activity(
    command: LifecycleEventCommand,
    transaction: Session,
    *,
    previous_projection: LifecycleProjection,
    current_projection: LifecycleProjection,
    legacy_case_status: str,
    conflict_codes: tuple[str, ...] = (),
) -> LifecycleTransitionResult:
    _validate_general_shape(
        command,
        previous_projection=previous_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=conflict_codes,
    )
    payload_json = _canonical_payload(command)
    evidence_refs = _validate_and_sort_evidence(command.evidence_refs)

    with transaction.no_autoflush:
        case_state = (
            transaction.execute(
                select(
                    Case.business_stage,
                    Case.official_procedure_stage,
                    Case.legal_status,
                    Case.lifecycle_verification_status,
                    Case.lifecycle_revision,
                    Case.status,
                ).where(Case.id == command.case_id)
            )
            .mappings()
            .one_or_none()
        )
        if case_state is None:
            _fail("CASE_NOT_FOUND", "案件不存在", status_code=404)

        existing = (
            transaction.execute(
                select(
                    CaseActivityEvent.id,
                    CaseActivityEvent.sequence,
                    CaseActivityEvent.lane,
                    CaseActivityEvent.activity_type,
                    CaseActivityEvent.source_activity_id,
                    CaseActivityEvent.occurred_at,
                    CaseActivityEvent.effective_at,
                    CaseActivityEvent.confirmation_status,
                    CaseActivityEvent.old_business_stage,
                    CaseActivityEvent.new_business_stage,
                    CaseActivityEvent.old_official_procedure_stage,
                    CaseActivityEvent.new_official_procedure_stage,
                    CaseActivityEvent.old_legal_status,
                    CaseActivityEvent.new_legal_status,
                    CaseActivityEvent.actor_id,
                    CaseActivityEvent.reviewer_id,
                    CaseActivityEvent.supersedes_event_id,
                    CaseActivityEvent.payload_json,
                ).where(
                    CaseActivityEvent.case_id == command.case_id,
                    CaseActivityEvent.idempotency_key == command.idempotency_key,
                )
            )
            .mappings()
            .one_or_none()
        )
        if existing is not None:
            return _replay_existing(
                command,
                transaction,
                existing=existing,
                evidence_refs=evidence_refs,
                payload_json=payload_json,
                previous_projection=previous_projection,
                current_projection=current_projection,
                legacy_case_status=legacy_case_status,
                conflict_codes=conflict_codes,
            )

        stored_projection = _case_projection(case_state)
        if stored_projection != previous_projection:
            _fail(
                "LIFECYCLE_PROJECTION_CONFLICT",
                "案件生命周期投影与预期不一致",
                status_code=409,
            )

        stored_revision = case_state["lifecycle_revision"]
        if stored_revision is not None and (
            type(stored_revision) is not int or stored_revision < 0
        ):
            _fail(
                "LIFECYCLE_REVISION_CONFLICT",
                "案件生命周期修订号无效",
                status_code=409,
            )
        prior_revision = stored_revision or 0
        max_sequence = transaction.scalar(
            select(func.max(CaseActivityEvent.sequence)).where(
                CaseActivityEvent.case_id == command.case_id
            )
        )
        if (max_sequence or 0) != prior_revision:
            _fail(
                "LIFECYCLE_REVISION_CONFLICT",
                "案件生命周期修订号与活动序列不一致",
                status_code=409,
            )

        _validate_centre_change(
            command,
            case_status=cast(str, case_state["status"]),
            previous_projection=previous_projection,
            current_projection=current_projection,
            legacy_case_status=legacy_case_status,
            conflict_codes=conflict_codes,
        )
        _validate_activity_reference(
            transaction,
            activity_id=command.source_activity_id,
            case_id=command.case_id,
            missing_code="LIFECYCLE_SOURCE_ACTIVITY_NOT_FOUND",
            mismatch_code="LIFECYCLE_SOURCE_ACTIVITY_CASE_MISMATCH",
        )
        _validate_activity_reference(
            transaction,
            activity_id=command.supersedes_event_id,
            case_id=command.case_id,
            missing_code="LIFECYCLE_SUPERSEDED_ACTIVITY_NOT_FOUND",
            mismatch_code="LIFECYCLE_SUPERSEDED_ACTIVITY_CASE_MISMATCH",
        )
        if any(reference.case_id != command.case_id for reference in evidence_refs):
            _fail(
                "LIFECYCLE_EVIDENCE_CASE_MISMATCH",
                "证据引用不属于当前案件",
                status_code=409,
            )

        new_revision = prior_revision + 1
        revision_predicate = (
            Case.lifecycle_revision.is_(None)
            if stored_revision is None
            else Case.lifecycle_revision == stored_revision
        )
        changed = transaction.execute(
            update(Case)
            .where(Case.id == command.case_id, revision_predicate)
            .values(
                business_stage=_enum_value(current_projection.business_stage),
                official_procedure_stage=_enum_value(current_projection.official_procedure_stage),
                legal_status=_enum_value(current_projection.legal_status),
                lifecycle_verification_status=_enum_value(
                    current_projection.lifecycle_verification_status
                ),
                lifecycle_revision=new_revision,
                status=legacy_case_status,
            )
            .execution_options(synchronize_session=False)
        )
        if changed.rowcount != 1:
            _fail(
                "LIFECYCLE_CONCURRENCY_CONFLICT",
                "案件生命周期已被并发更新",
                status_code=409,
            )
        _expire_cached_case_service_attributes(transaction, command.case_id)

        activity_id = str(uuid4())
        activity = CaseActivityEvent(
            id=activity_id,
            case_id=command.case_id,
            sequence=new_revision,
            lane=command.lane.value,
            activity_type=command.event_type,
            source_activity_id=command.source_activity_id,
            occurred_at=command.occurred_at,
            effective_at=command.effective_at,
            confirmation_status=command.confirmation_status.value,
            old_business_stage=_enum_value(previous_projection.business_stage),
            new_business_stage=_enum_value(current_projection.business_stage),
            old_official_procedure_stage=_enum_value(previous_projection.official_procedure_stage),
            new_official_procedure_stage=_enum_value(current_projection.official_procedure_stage),
            old_legal_status=_enum_value(previous_projection.legal_status),
            new_legal_status=_enum_value(current_projection.legal_status),
            actor_id=command.actor_id,
            reviewer_id=command.reviewer_id,
            idempotency_key=command.idempotency_key,
            supersedes_event_id=command.supersedes_event_id,
            payload_json=payload_json,
            conflict_lineage_version="V1",
            conflict_code_count=len(conflict_codes),
            conflict_codes_sha256=_conflict_codes_sha256(conflict_codes),
        )
        transaction.add(activity)
        transaction.add_all(
            CaseActivityEventConflict(
                case_id=command.case_id,
                activity_id=activity_id,
                code=code,
            )
            for code in conflict_codes
        )
        transaction.add_all(
            CaseActivityEventEvidence(
                id=str(uuid4()),
                case_id=command.case_id,
                activity_id=activity_id,
                evidence_kind=reference.evidence_kind,
                object_type=reference.object_type,
                object_id=reference.object_id,
                content_hash=reference.content_hash,
                captured_at=reference.captured_at,
            )
            for reference in evidence_refs
        )
        transaction.flush()

    return LifecycleTransitionResult(
        case_id=command.case_id,
        activity_id=activity_id,
        sequence=new_revision,
        lifecycle_revision=new_revision,
        lane=command.lane,
        event_type=command.event_type,
        confirmation_status=command.confirmation_status,
        previous_projection=previous_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        idempotency_key=command.idempotency_key,
        reused=False,
        conflict_codes=conflict_codes,
    )


def _validate_general_shape(
    command: LifecycleEventCommand,
    *,
    previous_projection: LifecycleProjection,
    current_projection: LifecycleProjection,
    legacy_case_status: str,
    conflict_codes: tuple[str, ...],
) -> None:
    if type(command) is not LifecycleEventCommand:
        _invalid("command")
    if type(previous_projection) is not LifecycleProjection:
        _invalid("previous_projection")
    if type(current_projection) is not LifecycleProjection:
        _invalid("current_projection")

    _required_string(command.case_id, 36, "case_id")
    _required_string(command.event_type, 64, "event_type")
    _required_string(command.actor_id, 36, "actor_id")
    _required_string(command.idempotency_key, 128, "idempotency_key")
    _optional_string(command.reviewer_id, 36, "reviewer_id")
    _optional_string(command.source_activity_id, 36, "source_activity_id")
    _optional_string(command.supersedes_event_id, 36, "supersedes_event_id")
    _required_string(legacy_case_status, 32, "legacy_case_status")

    if type(command.lane) is not ActivityLane:
        _invalid("lane")
    if type(command.confirmation_status) is not ConfirmationStatus:
        _invalid("confirmation_status")
    if type(command.evidence_refs) is not tuple:
        _invalid("evidence_refs")
    _validate_projection(previous_projection, "previous_projection")
    _validate_projection(current_projection, "current_projection")

    if type(conflict_codes) is not tuple:
        _invalid("conflict_codes")
    if any(type(code) is not str or not code or len(code) > 128 for code in conflict_codes):
        _invalid("conflict_codes")
    if tuple(sorted(conflict_codes)) != conflict_codes or len(set(conflict_codes)) != len(
        conflict_codes
    ):
        _invalid("conflict_codes")


def _validate_projection(projection: LifecycleProjection, field: str) -> None:
    members = (
        (projection.business_stage, BusinessStage),
        (projection.official_procedure_stage, OfficialProcedureStage),
        (projection.legal_status, LegalStatus),
        (projection.lifecycle_verification_status, ConfirmationStatus),
    )
    if any(value is not None and type(value) is not enum_type for value, enum_type in members):
        _invalid(field)


def _canonical_payload(command: LifecycleEventCommand) -> str:
    payload = command.payload
    if not isinstance(payload, Mapping):
        _payload_invalid()
    try:
        keys_are_strings = _json_object_keys_are_strings(payload)
    except (RecursionError, TypeError, ValueError):
        _payload_invalid()
    if not keys_are_strings:
        _payload_invalid()
    try:
        payload_dict = dict(payload)
    except (RecursionError, TypeError, ValueError):
        _payload_invalid()
    if any(type(key) is not str for key in payload_dict):
        _payload_invalid()
    if not _naive_datetime(command.effective_at):
        _payload_invalid()
    if command.occurred_at is not None and not _naive_datetime(command.occurred_at):
        _payload_invalid()
    try:
        return json.dumps(
            payload_dict,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _payload_invalid()


def _validate_and_sort_evidence(
    evidence_refs: tuple[EvidenceReference, ...],
) -> tuple[EvidenceReference, ...]:
    identities: set[tuple[str, str, str, str]] = set()
    for reference in evidence_refs:
        if type(reference) is not EvidenceReference:
            _evidence_invalid()
        checks = (
            (reference.case_id, 36),
            (reference.evidence_kind, 64),
            (reference.object_type, 64),
            (reference.object_id, 36),
            (reference.content_hash, 128),
        )
        if any(
            type(value) is not str or not value or len(value) > limit for value, limit in checks
        ):
            _evidence_invalid()
        if not _naive_datetime(reference.captured_at):
            _evidence_invalid()
        identity = (
            reference.case_id,
            reference.evidence_kind,
            reference.object_type,
            reference.object_id,
        )
        if identity in identities:
            _fail(
                "LIFECYCLE_EVIDENCE_DUPLICATE",
                "证据引用重复",
                status_code=400,
            )
        identities.add(identity)
    return tuple(
        sorted(
            evidence_refs,
            key=lambda reference: (
                reference.case_id,
                reference.evidence_kind,
                reference.object_type,
                reference.object_id,
                reference.content_hash,
                reference.captured_at,
            ),
        )
    )


def _replay_existing(
    command: LifecycleEventCommand,
    transaction: Session,
    *,
    existing: Mapping[str, object],
    evidence_refs: tuple[EvidenceReference, ...],
    payload_json: str,
    previous_projection: LifecycleProjection,
    current_projection: LifecycleProjection,
    legacy_case_status: str,
    conflict_codes: tuple[str, ...],
) -> LifecycleTransitionResult:
    activity = transaction.get(CaseActivityEvent, cast(str, existing["id"]))
    if activity is None:
        _fail(
            "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
            "生命周期冲突谱系无效",
            status_code=409,
        )
    stored_conflict_codes = read_activity_conflict_codes(transaction, (activity,))[activity.id]
    comparable = (
        (existing["activity_type"], command.event_type),
        (existing["lane"], command.lane.value),
        (existing["effective_at"], command.effective_at),
        (existing["occurred_at"], command.occurred_at),
        (existing["actor_id"], command.actor_id),
        (existing["reviewer_id"], command.reviewer_id),
        (existing["confirmation_status"], command.confirmation_status.value),
        (existing["source_activity_id"], command.source_activity_id),
        (existing["supersedes_event_id"], command.supersedes_event_id),
        (existing["payload_json"], payload_json),
        (
            existing["old_business_stage"],
            _enum_value(previous_projection.business_stage),
        ),
        (
            existing["old_official_procedure_stage"],
            _enum_value(previous_projection.official_procedure_stage),
        ),
        (
            existing["old_legal_status"],
            _enum_value(previous_projection.legal_status),
        ),
        (
            existing["new_business_stage"],
            _enum_value(current_projection.business_stage),
        ),
        (
            existing["new_official_procedure_stage"],
            _enum_value(current_projection.official_procedure_stage),
        ),
        (
            existing["new_legal_status"],
            _enum_value(current_projection.legal_status),
        ),
    )
    stored_evidence_identity = tuple(
        transaction.execute(
            select(
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
                CaseActivityEventEvidence.content_hash,
                CaseActivityEventEvidence.captured_at,
            )
            .where(CaseActivityEventEvidence.activity_id == existing["id"])
            .order_by(
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
                CaseActivityEventEvidence.content_hash,
                CaseActivityEventEvidence.captured_at,
            )
        )
    )
    command_evidence_identity = tuple(
        (
            reference.case_id,
            reference.evidence_kind,
            reference.object_type,
            reference.object_id,
            reference.content_hash,
            reference.captured_at,
        )
        for reference in evidence_refs
    )
    if (
        any(stored != supplied for stored, supplied in comparable)
        or stored_evidence_identity != command_evidence_identity
        or stored_conflict_codes != conflict_codes
    ):
        _fail(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            "幂等键已用于不同的生命周期活动",
            status_code=409,
        )

    return LifecycleTransitionResult(
        case_id=command.case_id,
        activity_id=cast(str, existing["id"]),
        sequence=cast(int, existing["sequence"]),
        lifecycle_revision=cast(int, existing["sequence"]),
        lane=command.lane,
        event_type=command.event_type,
        confirmation_status=command.confirmation_status,
        previous_projection=previous_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        idempotency_key=command.idempotency_key,
        reused=True,
        conflict_codes=conflict_codes,
    )


def _conflict_codes_sha256(conflict_codes: tuple[str, ...]) -> str:
    canonical = json.dumps(
        conflict_codes,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def read_activity_conflict_codes(
    transaction: Session,
    activities: tuple[CaseActivityEvent, ...],
) -> dict[str, tuple[str, ...]]:
    if not activities:
        return {}
    activity_ids = tuple(activity.id for activity in activities)
    rows = transaction.execute(
        select(
            CaseActivityEventConflict.activity_id,
            CaseActivityEventConflict.case_id,
            CaseActivityEventConflict.code,
        )
        .where(CaseActivityEventConflict.activity_id.in_(activity_ids))
        .order_by(CaseActivityEventConflict.activity_id, CaseActivityEventConflict.code)
    ).all()
    grouped: dict[str, list[tuple[str, str]]] = {activity_id: [] for activity_id in activity_ids}
    for activity_id, case_id, code in rows:
        if activity_id not in grouped:
            _conflict_lineage_invalid()
        grouped[activity_id].append((case_id, code))

    result: dict[str, tuple[str, ...]] = {}
    for activity in activities:
        triple = (
            activity.conflict_lineage_version,
            activity.conflict_code_count,
            activity.conflict_codes_sha256,
        )
        if triple == (None, None, None):
            _fail(
                "LIFECYCLE_CONFLICT_LINEAGE_MISSING",
                "生命周期冲突谱系缺失",
                status_code=409,
            )
        version, count, digest = triple
        if (
            version != "V1"
            or type(count) is not int
            or count < 0
            or type(digest) is not str
            or len(digest) != 64
            or digest != digest.lower()
        ):
            _conflict_lineage_invalid()
        codes = tuple(code for case_id, code in grouped[activity.id] if case_id == activity.case_id)
        if (
            len(codes) != len(grouped[activity.id])
            or any(type(code) is not str or not code or len(code) > 128 for code in codes)
            or tuple(sorted(codes)) != codes
            or len(set(codes)) != len(codes)
            or count != len(codes)
            or digest != _conflict_codes_sha256(codes)
        ):
            _conflict_lineage_invalid()
        result[activity.id] = codes
    return result


def _conflict_lineage_invalid() -> None:
    _fail(
        "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
        "生命周期冲突谱系无效",
        status_code=409,
    )


def _case_projection(case_state: Mapping[str, object]) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=_stored_enum(
                BusinessStage,
                cast(str | None, case_state["business_stage"]),
            ),
            official_procedure_stage=_stored_enum(
                OfficialProcedureStage,
                cast(str | None, case_state["official_procedure_stage"]),
            ),
            legal_status=_stored_enum(
                LegalStatus,
                cast(str | None, case_state["legal_status"]),
            ),
            lifecycle_verification_status=_stored_enum(
                ConfirmationStatus,
                cast(str | None, case_state["lifecycle_verification_status"]),
            ),
        )
    except ValueError:
        _fail(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "案件存量生命周期投影无效",
            status_code=409,
        )


def _validate_centre_change(
    command: LifecycleEventCommand,
    *,
    case_status: str,
    previous_projection: LifecycleProjection,
    current_projection: LifecycleProjection,
    legacy_case_status: str,
    conflict_codes: tuple[str, ...],
) -> None:
    projection_changed = previous_projection != current_projection
    legacy_status_changed = case_status != legacy_case_status
    centre_changed = projection_changed or legacy_status_changed

    if command.lane in (ActivityLane.DOCUMENT, ActivityLane.FEE):
        if centre_changed or conflict_codes:
            _centre_change_not_allowed()
        return
    if command.confirmation_status is ConfirmationStatus.NEEDS_REVIEW:
        if centre_changed:
            _centre_change_not_allowed()
        return
    if command.confirmation_status is ConfirmationStatus.CONFIRMED:
        return

    legacy_import_initialization = (
        command.event_type == "LEGACY_IMPORT"
        and command.confirmation_status is ConfirmationStatus.LEGACY_UNVERIFIED
        and previous_projection
        == LifecycleProjection(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=None,
            lifecycle_verification_status=None,
        )
        and current_projection.lifecycle_verification_status is ConfirmationStatus.LEGACY_UNVERIFIED
    )
    if not legacy_import_initialization:
        _centre_change_not_allowed()


def _validate_activity_reference(
    transaction: Session,
    *,
    activity_id: str | None,
    case_id: str,
    missing_code: str,
    mismatch_code: str,
) -> None:
    if activity_id is None:
        return
    activity_case_id = transaction.scalar(
        select(CaseActivityEvent.case_id).where(CaseActivityEvent.id == activity_id)
    )
    if activity_case_id is None:
        _fail(missing_code, "引用的生命周期活动不存在", status_code=409)
    if activity_case_id != case_id:
        _fail(mismatch_code, "引用的生命周期活动不属于当前案件", status_code=409)


def _expire_cached_case_service_attributes(transaction: Session, case_id: str) -> None:
    identity_key = transaction.identity_key(Case, (case_id,))
    cached_case = transaction.identity_map.get(identity_key)
    if cached_case is not None:
        transaction.expire(cached_case, _CASE_SERVICE_ATTRIBUTES)


def _stored_enum(enum_type: type[_EnumT], value: str | None) -> _EnumT | None:
    return None if value is None else enum_type(value)


def _enum_value(value: StrEnum | None) -> str | None:
    return None if value is None else value.value


def _required_string(value: object, limit: int, field: str) -> None:
    if type(value) is not str or not value or len(value) > limit:
        _invalid(field)


def _optional_string(value: object, limit: int, field: str) -> None:
    if value is not None:
        _required_string(value, limit, field)


def _naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.utcoffset() is None


def _json_object_keys_are_strings(value: object) -> bool:
    pending = [value]
    visited: set[int] = set()
    while pending:
        current = pending.pop()
        if not isinstance(current, (Mapping, list, tuple)):
            continue
        marker = id(current)
        if marker in visited:
            continue
        visited.add(marker)
        if isinstance(current, Mapping):
            for key, item in current.items():
                if type(key) is not str:
                    return False
                pending.append(item)
        else:
            pending.extend(current)
    return True


def _invalid(field: str) -> None:
    _fail(
        "LIFECYCLE_ACTIVITY_INVALID",
        "生命周期活动参数无效",
        details={"field": field},
        status_code=400,
    )


def _payload_invalid() -> None:
    _fail(
        "LIFECYCLE_PAYLOAD_INVALID",
        "生命周期活动时间或载荷无效",
        status_code=400,
    )


def _evidence_invalid() -> None:
    _fail(
        "LIFECYCLE_EVIDENCE_INVALID",
        "生命周期活动证据引用无效",
        status_code=400,
    )


def _centre_change_not_allowed() -> None:
    _fail(
        "LIFECYCLE_CENTER_CHANGE_NOT_ALLOWED",
        "当前活动不得修改案件中心生命周期状态",
        status_code=409,
    )


def _fail(
    code: str,
    message: str,
    *,
    details: dict | None = None,
    status_code: int,
) -> None:
    raise BusinessError(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
    )
