from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime
from importlib import import_module, util
from inspect import Parameter, signature
from types import ModuleType
from typing import cast

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
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
from app.modules.cases.models import Case, CaseActivityEvent

CASE_ID = "case-lifecycle-apply"
ACTOR_ID = "actor-lifecycle-apply"
EFFECTIVE_AT = datetime(2026, 7, 14, 9, 30)
SERVICE_MODULE = "app.modules.cases.lifecycle_service"
RULES_MODULE = "app.modules.cases.lifecycle_rules"

EMPTY_PROJECTION = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=None,
    lifecycle_verification_status=None,
)
OPEN_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.NEW_CASE,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
ACCEPTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.ACCEPTED,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
OA_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
GRANTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def _value(value: object) -> object:
    return value.value if hasattr(value, "value") else value


def _case(
    *,
    projection: LifecycleProjection = EMPTY_PROJECTION,
    status: str = "NOT_FILED",
    revision: int | None = None,
) -> Case:
    return Case(
        id=CASE_ID,
        case_no="NO-LIFECYCLE-APPLY",
        status=status,
        business_stage=_value(projection.business_stage),
        official_procedure_stage=_value(projection.official_procedure_stage),
        legal_status=_value(projection.legal_status),
        lifecycle_verification_status=_value(projection.lifecycle_verification_status),
        lifecycle_revision=revision,
    )


def _command(
    *,
    event_type: str = "CASE_OPENED",
    lane: ActivityLane = ActivityLane.LIFECYCLE,
    confirmation_status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
    idempotency_key: str = "case-opened-1",
    payload: Mapping[str, object] | None = None,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type=event_type,
        lane=lane,
        effective_at=EFFECTIVE_AT,
        evidence_refs=(),
        actor_id=ACTOR_ID,
        idempotency_key=idempotency_key,
        confirmation_status=confirmation_status,
        payload={} if payload is None else payload,
    )


def _service() -> ModuleType:
    return import_module(SERVICE_MODULE)


def _install_registry(
    monkeypatch: pytest.MonkeyPatch,
    resolver: Callable[[str], object],
) -> None:
    module = ModuleType(RULES_MODULE)
    module.get_lifecycle_rule = resolver  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, RULES_MODULE, module)


def _expect_error(
    expected_code: str,
    expected_status: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    error = captured.value
    assert error.code == expected_code
    assert error.status_code == expected_status
    return error


def _activity_count(transaction: Session) -> int:
    return int(
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == CASE_ID)
        )
        or 0
    )


def test_module_exposes_only_the_frozen_public_seam_and_decision_contract() -> None:
    assert util.find_spec(SERVICE_MODULE) is not None, (
        "missing frozen behavior: lifecycle_service.py must expose "
        "apply_lifecycle_event() and LifecycleRuleDecision"
    )
    service = _service()
    parameters = tuple(signature(service.apply_lifecycle_event).parameters.values())

    assert tuple(parameter.name for parameter in parameters) == ("command", "transaction")
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
    )
    decision = service.LifecycleRuleDecision(current_projection=OPEN_PROJECTION)
    assert decision.current_projection == OPEN_PROJECTION
    assert decision.oa_sequence is None
    with pytest.raises(TypeError):
        service.LifecycleRuleDecision(OPEN_PROJECTION)
    with pytest.raises((AttributeError, TypeError)):
        decision.oa_sequence = 1
    assert RULES_MODULE not in sys.modules


def test_new_event_uses_stored_projection_projects_legacy_and_leaves_commit_to_caller(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[LifecycleEventCommand, LifecycleProjection, Session]] = []

    def rule(
        command: LifecycleEventCommand,
        previous_projection: LifecycleProjection,
        transaction: Session,
    ) -> object:
        calls.append((command, previous_projection, transaction))
        return _service().LifecycleRuleDecision(current_projection=OPEN_PROJECTION)

    _install_registry(monkeypatch, lambda event_type: rule if event_type == "CASE_OPENED" else None)
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        result = _service().apply_lifecycle_event(_command(), transaction)

        assert isinstance(result, LifecycleTransitionResult)
        assert result.previous_projection == EMPTY_PROJECTION
        assert result.current_projection == OPEN_PROJECTION
        assert result.legacy_case_status == "NOT_FILED"
        assert result.sequence == result.lifecycle_revision == 1
        assert result.reused is False
        assert calls == [(_command(), EMPTY_PROJECTION, transaction)]
        stored = transaction.get(Case, CASE_ID)
        assert stored is not None
        assert stored.business_stage == BusinessStage.NEW_CASE.value
        assert stored.lifecycle_revision == 1
        assert _activity_count(transaction) == 1
        assert transaction.in_transaction()
        transaction.rollback()

    with session_factory() as transaction:
        stored = transaction.get(Case, CASE_ID)
        assert stored is not None
        assert stored.lifecycle_revision is None
        assert _activity_count(transaction) == 0


def test_oa_sequence_is_persisted_and_replay_uses_stored_fact_after_case_advances(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rule_calls = 0

    def rule(
        _command: LifecycleEventCommand,
        previous_projection: LifecycleProjection,
        _transaction: Session,
    ) -> object:
        nonlocal rule_calls
        rule_calls += 1
        assert previous_projection == ACCEPTED_PROJECTION
        return _service().LifecycleRuleDecision(
            current_projection=OA_PROJECTION,
            oa_sequence=1,
        )

    _install_registry(monkeypatch, lambda _event_type: rule)
    command = _command(
        event_type="OA_NOTICE_RECORDED",
        idempotency_key="oa-notice-1",
        payload={"notice": "first"},
    )
    with session_factory() as transaction:
        transaction.add(
            _case(
                projection=ACCEPTED_PROJECTION,
                status="ACCEPTED",
                revision=0,
            )
        )
        transaction.commit()

        first = _service().apply_lifecycle_event(command, transaction)
        transaction.commit()
        activity = transaction.get(CaseActivityEvent, first.activity_id)
        assert activity is not None
        assert activity.payload_json == '{"notice":"first","oa_sequence":1}'
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        case.business_stage = GRANTED_PROJECTION.business_stage.value
        case.official_procedure_stage = GRANTED_PROJECTION.official_procedure_stage.value
        case.legal_status = GRANTED_PROJECTION.legal_status.value
        case.lifecycle_verification_status = ConfirmationStatus.CONFIRMED.value
        case.status = "GRANTED"
        transaction.commit()

        replay = _service().apply_lifecycle_event(command, transaction)

        assert replay.reused is True
        assert replay.activity_id == first.activity_id
        assert replay.previous_projection == ACCEPTED_PROJECTION
        assert replay.current_projection == OA_PROJECTION
        assert replay.legacy_case_status == "OA1"
        assert rule_calls == 1
        assert _activity_count(transaction) == 1
        assert transaction.get(Case, CASE_ID).status == "GRANTED"  # type: ignore[union-attr]


def test_retained_legacy_projection_conflict_fails_before_append_without_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conflicting = replace(
        OPEN_PROJECTION,
        official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
    )
    _install_registry(
        monkeypatch,
        lambda _event_type: (
            lambda _command, _previous, _transaction: _service().LifecycleRuleDecision(
                current_projection=conflicting
            )
        ),
    )
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        before = transaction.get(Case, CASE_ID)
        assert before is not None
        before_state = (before.status, before.lifecycle_revision)

        _expect_error(
            "LIFECYCLE_LEGACY_PROJECTION_CONFLICT",
            409,
            lambda: _service().apply_lifecycle_event(_command(), transaction),
        )

        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert (case.status, case.lifecycle_revision) == before_state
        assert _activity_count(transaction) == 0
        assert not transaction.new


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(lane=ActivityLane.DOCUMENT),
        _command(confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        _command(confirmation_status=ConfirmationStatus.LEGACY_UNVERIFIED),
    ),
)
def test_invalid_command_lane_or_confirmation_fails_400_before_rule_resolution(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    command: LifecycleEventCommand,
) -> None:
    registry_called = False

    def resolve(_event_type: str) -> object:
        nonlocal registry_called
        registry_called = True
        raise AssertionError("invalid command must not resolve a rule")

    _install_registry(monkeypatch, resolve)
    with session_factory() as transaction:
        _expect_error(
            "LIFECYCLE_EVENT_INVALID",
            400,
            lambda: _service().apply_lifecycle_event(command, transaction),
        )
    assert registry_called is False


def test_missing_case_preserves_append_404_and_does_not_resolve_rule(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_registry(
        monkeypatch,
        lambda _event_type: pytest.fail("missing case must not resolve a rule"),
    )
    with session_factory() as transaction:
        _expect_error(
            "CASE_NOT_FOUND",
            404,
            lambda: _service().apply_lifecycle_event(_command(), transaction),
        )


@pytest.mark.parametrize(
    ("resolver_kind", "expected_code"),
    (
        ("unregistered", "LIFECYCLE_RULE_NOT_REGISTERED"),
        ("resolver_error", "LIFECYCLE_RULE_RESOLUTION_FAILED"),
        ("wrong_decision", "LIFECYCLE_RULE_DECISION_INVALID"),
    ),
)
def test_rule_resolution_and_exact_decision_type_fail_closed(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    resolver_kind: str,
    expected_code: str,
) -> None:
    if resolver_kind == "unregistered":

        def resolver(_event_type: str) -> object:
            return None

    elif resolver_kind == "resolver_error":

        def resolver(_event_type: str) -> object:
            raise RuntimeError("registry unavailable")

    else:

        def resolver(_event_type: str) -> object:
            return lambda _command, _previous, _transaction: object()

    _install_registry(monkeypatch, resolver)

    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        _expect_error(
            expected_code,
            409,
            lambda: _service().apply_lifecycle_event(_command(), transaction),
        )
        assert _activity_count(transaction) == 0
        assert not transaction.new
