from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from importlib import import_module
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_activity_service import (
    append_case_activity,
    read_activity_conflict_codes,
)
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_projection import (
    LegacyProjectionDisposition,
    project_legacy_case_status,
)
from app.modules.cases.models import Case, CaseActivityEvent

__all__ = ("LifecycleRuleDecision", "apply_lifecycle_event")

_RULES_MODULE = "app.modules.cases.lifecycle_rules"
_PATENT_REGISTER_STATUS_EVENT = "PATENT_REGISTER_STATUS_CONFIRMED"
_PATENT_REGISTER_STATUS_SCHEMA = "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V1"


@dataclass(frozen=True, slots=True, kw_only=True)
class LifecycleRuleDecision:
    current_projection: LifecycleProjection
    oa_sequence: int | None = None
    conflict_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class PatentRegisterStatusRuleContext:
    predecessor_event_type: str | None
    predecessor_status_snapshot_hash: str | None


def apply_lifecycle_event(
    command: LifecycleEventCommand,
    transaction: Session,
) -> LifecycleTransitionResult:
    _validate_command_boundary(command)

    with transaction.no_autoflush:
        case_state = (
            transaction.execute(
                select(
                    Case.business_stage,
                    Case.official_procedure_stage,
                    Case.legal_status,
                    Case.lifecycle_verification_status,
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
                    CaseActivityEvent.activity_type,
                    CaseActivityEvent.confirmation_status,
                    CaseActivityEvent.old_business_stage,
                    CaseActivityEvent.new_business_stage,
                    CaseActivityEvent.old_official_procedure_stage,
                    CaseActivityEvent.new_official_procedure_stage,
                    CaseActivityEvent.old_legal_status,
                    CaseActivityEvent.new_legal_status,
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
            return _replay(command, transaction, existing=existing)

        previous_projection = _projection_from_case(case_state)
        decision = _resolve_decision(command, previous_projection, transaction)
        command = _command_with_oa_sequence(command, decision.oa_sequence)
        legacy_projection = _project_legacy(
            existing_status=cast(str, case_state["status"]),
            current_projection=decision.current_projection,
            event_type=command.event_type,
            oa_sequence=decision.oa_sequence,
        )
        return append_case_activity(
            command,
            transaction,
            previous_projection=previous_projection,
            current_projection=decision.current_projection,
            legacy_case_status=legacy_projection.legacy_case_status,
            conflict_codes=decision.conflict_codes,
        )


def _replay(
    command: LifecycleEventCommand,
    transaction: Session,
    *,
    existing: Mapping[str, object],
) -> LifecycleTransitionResult:
    payload = _stored_payload(existing["payload_json"])
    stored_oa_sequence = payload.get("oa_sequence")
    if stored_oa_sequence is not None and (
        type(stored_oa_sequence) is not int or stored_oa_sequence < 1
    ):
        _fail(
            "LIFECYCLE_RULE_DECISION_INVALID",
            "已存生命周期活动的 OA 次数无效",
            status_code=409,
        )
    command = _command_with_stored_oa_sequence(
        command,
        cast(int | None, stored_oa_sequence),
    )
    previous_projection = _projection_from_activity(existing, prefix="old")
    current_projection = _projection_from_activity(existing, prefix="new")
    legacy_projection = _project_legacy(
        existing_status="REPLAY_PLACEHOLDER",
        current_projection=current_projection,
        event_type=cast(str, existing["activity_type"]),
        oa_sequence=cast(int | None, stored_oa_sequence),
    )
    conflict_codes: tuple[str, ...] = ()
    if (
        command.event_type == _PATENT_REGISTER_STATUS_EVENT
        and existing["activity_type"] == _PATENT_REGISTER_STATUS_EVENT
    ):
        stored_activity = transaction.get(CaseActivityEvent, cast(str, existing["id"]))
        if stored_activity is None:
            _fail(
                "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
                "生命周期冲突谱系无效",
                status_code=409,
            )
        conflict_codes = read_activity_conflict_codes(transaction, (stored_activity,))[
            stored_activity.id
        ]
        append_case_activity(
            command,
            transaction,
            previous_projection=previous_projection,
            current_projection=current_projection,
            legacy_case_status=legacy_projection.legacy_case_status,
            conflict_codes=conflict_codes,
        )
        decision = _resolve_decision(command, previous_projection, transaction)
        if decision.current_projection != current_projection:
            _invalid_decision()
        if decision.conflict_codes != conflict_codes:
            _invalid_decision()
    return append_case_activity(
        command,
        transaction,
        previous_projection=previous_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_projection.legacy_case_status,
        conflict_codes=conflict_codes,
    )


def _resolve_decision(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision:
    try:
        rules = import_module(_RULES_MODULE)
        get_rule = rules.get_lifecycle_rule
        rule = get_rule(command.event_type)
    except Exception as error:
        raise BusinessError(
            code="LIFECYCLE_RULE_RESOLUTION_FAILED",
            message="生命周期规则解析失败",
            status_code=409,
        ) from error
    if rule is None:
        _fail(
            "LIFECYCLE_RULE_NOT_REGISTERED",
            "生命周期事件规则未注册",
            status_code=409,
        )
    if not callable(rule):
        _fail(
            "LIFECYCLE_RULE_RESOLUTION_FAILED",
            "生命周期规则不可调用",
            status_code=409,
        )

    rule_context: object = transaction
    if command.event_type == _PATENT_REGISTER_STATUS_EVENT:
        rule_context = _patent_register_status_context(command, transaction)

    decision = rule(command, previous_projection, rule_context)
    if type(decision) is not LifecycleRuleDecision:
        _invalid_decision()
    if type(decision.current_projection) is not LifecycleProjection:
        _invalid_decision()
    if decision.oa_sequence is not None and (
        type(decision.oa_sequence) is not int or decision.oa_sequence < 1
    ):
        _invalid_decision()
    if type(decision.conflict_codes) is not tuple:
        _invalid_decision()
    if any(type(code) is not str or not code for code in decision.conflict_codes):
        _invalid_decision()
    if tuple(sorted(decision.conflict_codes)) != decision.conflict_codes or len(
        set(decision.conflict_codes)
    ) != len(decision.conflict_codes):
        _invalid_decision()
    return decision


def _patent_register_status_context(
    command: LifecycleEventCommand,
    transaction: Session,
) -> PatentRegisterStatusRuleContext:
    predecessor_id = command.supersedes_event_id
    if predecessor_id is None:
        return PatentRegisterStatusRuleContext(
            predecessor_event_type=None,
            predecessor_status_snapshot_hash=None,
        )

    predecessor = (
        transaction.execute(
            select(
                CaseActivityEvent.case_id,
                CaseActivityEvent.activity_type,
                CaseActivityEvent.payload_json,
            ).where(CaseActivityEvent.id == predecessor_id)
        )
        .mappings()
        .one_or_none()
    )
    if predecessor is None:
        _fail(
            "LIFECYCLE_SUPERSEDED_ACTIVITY_NOT_FOUND",
            "被替代的生命周期活动不存在",
            status_code=409,
        )
    if predecessor["case_id"] != command.case_id:
        _fail(
            "LIFECYCLE_SUPERSEDED_ACTIVITY_CASE_MISMATCH",
            "被替代的生命周期活动不属于当前案件",
            status_code=409,
        )

    predecessor_event_type = predecessor["activity_type"]
    if type(predecessor_event_type) is not str:
        _invalid_decision()
    if predecessor_event_type != _PATENT_REGISTER_STATUS_EVENT:
        return PatentRegisterStatusRuleContext(
            predecessor_event_type=predecessor_event_type,
            predecessor_status_snapshot_hash=None,
        )

    return PatentRegisterStatusRuleContext(
        predecessor_event_type=predecessor_event_type,
        predecessor_status_snapshot_hash=_verified_register_status_snapshot_hash(
            predecessor["payload_json"]
        ),
    )


def _verified_register_status_snapshot_hash(value: object) -> str:
    payload = _canonical_stored_object(value)
    if payload.get("schema") != _PATENT_REGISTER_STATUS_SCHEMA:
        _stored_register_payload_invalid()

    snapshot = payload.get("status_snapshot")
    snapshot_hash = payload.get("status_snapshot_hash")
    if type(snapshot) is not str or type(snapshot_hash) is not str:
        _stored_register_payload_invalid()
    if len(snapshot_hash) != 64 or any(
        character not in "0123456789abcdef" for character in snapshot_hash
    ):
        _stored_register_payload_invalid()
    _canonical_stored_object(snapshot)
    if hashlib.sha256(snapshot.encode()).hexdigest() != snapshot_hash:
        _stored_register_payload_invalid()
    return snapshot_hash


def _canonical_stored_object(value: object) -> dict[str, object]:
    if type(value) is not str:
        _stored_register_payload_invalid()
    try:
        payload = json.loads(value)
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError, json.JSONDecodeError):
        _stored_register_payload_invalid()
    if type(payload) is not dict or canonical != value:
        _stored_register_payload_invalid()
    return payload


def _stored_register_payload_invalid() -> None:
    _fail(
        "LIFECYCLE_PAYLOAD_INVALID",
        "已存专利登记簿状态载荷无效",
        status_code=409,
    )


def _project_legacy(
    *,
    existing_status: str,
    current_projection: LifecycleProjection,
    event_type: str,
    oa_sequence: int | None,
):
    try:
        result = project_legacy_case_status(
            existing_status=existing_status,
            projection=current_projection,
            latest_confirmed_lifecycle_event_type=event_type,
            oa_sequence=oa_sequence,
        )
    except (TypeError, ValueError) as error:
        raise BusinessError(
            code="LIFECYCLE_RULE_DECISION_INVALID",
            message="生命周期规则决定无效",
            status_code=409,
        ) from error
    if result.disposition is LegacyProjectionDisposition.RETAINED_CONFLICT:
        _fail(
            "LIFECYCLE_LEGACY_PROJECTION_CONFLICT",
            "生命周期投影无法安全映射到兼容案件状态",
            status_code=409,
        )
    return result


def _projection_from_case(case_state: Mapping[str, object]) -> LifecycleProjection:
    return _projection(
        business_stage=case_state["business_stage"],
        official_procedure_stage=case_state["official_procedure_stage"],
        legal_status=case_state["legal_status"],
        verification_status=case_state["lifecycle_verification_status"],
    )


def _projection_from_activity(
    activity: Mapping[str, object],
    *,
    prefix: str,
) -> LifecycleProjection:
    axes = (
        activity[f"{prefix}_business_stage"],
        activity[f"{prefix}_official_procedure_stage"],
        activity[f"{prefix}_legal_status"],
    )
    verification_status = (
        None if all(value is None for value in axes) else (activity["confirmation_status"])
    )
    return _projection(
        business_stage=axes[0],
        official_procedure_stage=axes[1],
        legal_status=axes[2],
        verification_status=verification_status,
    )


def _projection(
    *,
    business_stage: object,
    official_procedure_stage: object,
    legal_status: object,
    verification_status: object,
) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                None if business_stage is None else BusinessStage(cast(str, business_stage))
            ),
            official_procedure_stage=(
                None
                if official_procedure_stage is None
                else OfficialProcedureStage(cast(str, official_procedure_stage))
            ),
            legal_status=(None if legal_status is None else LegalStatus(cast(str, legal_status))),
            lifecycle_verification_status=(
                None
                if verification_status is None
                else ConfirmationStatus(cast(str, verification_status))
            ),
        )
    except (TypeError, ValueError) as error:
        raise BusinessError(
            code="LIFECYCLE_PROJECTION_CONFLICT",
            message="案件存量生命周期投影无效",
            status_code=409,
        ) from error


def _command_with_oa_sequence(
    command: LifecycleEventCommand,
    oa_sequence: int | None,
) -> LifecycleEventCommand:
    if oa_sequence is None:
        return command
    payload = dict(command.payload)
    supplied = payload.get("oa_sequence")
    if supplied is not None and supplied != oa_sequence:
        _fail(
            "LIFECYCLE_EVENT_INVALID",
            "OA 次数与生命周期规则决定不一致",
            status_code=400,
        )
    payload["oa_sequence"] = oa_sequence
    return replace(command, payload=payload)


def _command_with_stored_oa_sequence(
    command: LifecycleEventCommand,
    oa_sequence: int | None,
) -> LifecycleEventCommand:
    if oa_sequence is None or "oa_sequence" in command.payload:
        return command
    payload = dict(command.payload)
    payload["oa_sequence"] = oa_sequence
    return replace(command, payload=payload)


def _stored_payload(value: object) -> dict[str, object]:
    try:
        payload = json.loads(cast(str, value))
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise BusinessError(
            code="LIFECYCLE_PAYLOAD_INVALID",
            message="已存生命周期活动载荷无效",
            status_code=409,
        ) from error
    if type(payload) is not dict or any(type(key) is not str for key in payload):
        _fail(
            "LIFECYCLE_PAYLOAD_INVALID",
            "已存生命周期活动载荷无效",
            status_code=409,
        )
    return payload


def _validate_command_boundary(command: LifecycleEventCommand) -> None:
    if type(command) is not LifecycleEventCommand:
        _invalid_event("command")
    required_strings = (
        (command.case_id, 36, "case_id"),
        (command.event_type, 64, "event_type"),
        (command.actor_id, 36, "actor_id"),
        (command.idempotency_key, 128, "idempotency_key"),
    )
    for value, limit, field in required_strings:
        if type(value) is not str or not value or len(value) > limit:
            _invalid_event(field)
    if type(command.lane) is not ActivityLane or command.lane is not ActivityLane.LIFECYCLE:
        _invalid_event("lane")
    if (
        type(command.confirmation_status) is not ConfirmationStatus
        or command.confirmation_status is not ConfirmationStatus.CONFIRMED
    ):
        _invalid_event("confirmation_status")
    if type(command.evidence_refs) is not tuple:
        _invalid_event("evidence_refs")
    if not isinstance(command.payload, Mapping):
        _invalid_event("payload")
    if not _naive_datetime(command.effective_at):
        _invalid_event("effective_at")
    if command.occurred_at is not None and not _naive_datetime(command.occurred_at):
        _invalid_event("occurred_at")


def _naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.tzinfo is None


def _invalid_event(field: str) -> None:
    _fail(
        "LIFECYCLE_EVENT_INVALID",
        "生命周期事件参数无效",
        details={"field": field},
        status_code=400,
    )


def _invalid_decision() -> None:
    _fail(
        "LIFECYCLE_RULE_DECISION_INVALID",
        "生命周期规则决定无效",
        status_code=409,
    )


def _fail(
    code: str,
    message: str,
    *,
    details: dict[str, object] | None = None,
    status_code: int,
) -> None:
    raise BusinessError(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
    )
