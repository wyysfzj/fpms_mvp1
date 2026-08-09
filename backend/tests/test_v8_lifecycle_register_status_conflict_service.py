from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime
from importlib import import_module
from types import ModuleType
from typing import cast

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventConflict

CASE_ID = "case-register-service"
OTHER_CASE_ID = "case-register-service-other"
ACTOR_ID = "actor-register-service"
EFFECTIVE_AT = datetime(2026, 7, 23, 10, 30)
REGISTER_EVENT = "PATENT_REGISTER_STATUS_CONFIRMED"
CONFLICT_CODE = "PATENT_REGISTER_STATUS_REQUIRES_SPECIFIC_EVENT"
RULES_MODULE = "app.modules.cases.lifecycle_rules"

IN_FORCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def _service() -> ModuleType:
    return import_module("app.modules.cases.lifecycle_service")


def _case(case_id: str = CASE_ID) -> Case:
    return Case(
        id=case_id,
        case_no=f"NO-{case_id}",
        status="GRANTED",
        business_stage=BusinessStage.POST_GRANT_MAINTENANCE.value,
        official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED.value,
        legal_status=LegalStatus.PATENT_IN_FORCE.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=0,
    )


def _snapshot(register_status: str) -> str:
    return json.dumps(
        {
            "observed_at": "2026-07-23T10:00:00",
            "register_status": register_status,
            "schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _payload(
    *,
    register_status: str = "PATENT_TERMINATED",
    predecessor_hash: str | None = None,
    supersedes_activity_id: str | None = None,
) -> dict[str, object]:
    snapshot = _snapshot(register_status)
    return {
        "schema": "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V1",
        "case_id": CASE_ID,
        "register_status": register_status,
        "source_document_id": "register-document-1",
        "source_evidence_version_id": "register-version-1",
        "source_evidence_content_hash": "sha256:register-version-1",
        "source_provenance_id": "register-review-1",
        "status_snapshot_schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
        "status_snapshot": snapshot,
        "status_snapshot_hash": hashlib.sha256(snapshot.encode()).hexdigest(),
        "predecessor_status_snapshot_hash": predecessor_hash,
        "supersedes_activity_id": supersedes_activity_id,
    }


def _command(
    *,
    case_id: str = CASE_ID,
    event_type: str = REGISTER_EVENT,
    idempotency_key: str = "register-status-1",
    payload: Mapping[str, object] | None = None,
    supersedes_event_id: str | None = None,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=case_id,
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=EFFECTIVE_AT,
        evidence_refs=(),
        actor_id=ACTOR_ID,
        idempotency_key=idempotency_key,
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=_payload() if payload is None else payload,
        supersedes_event_id=supersedes_event_id,
    )


def _install_registry(
    monkeypatch: pytest.MonkeyPatch,
    resolver: Callable[[str], object],
) -> None:
    module = ModuleType(RULES_MODULE)
    module.get_lifecycle_rule = resolver  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, RULES_MODULE, module)


def _expect_error(
    code: str,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.code == code
    assert captured.value.status_code == 409
    return captured.value


def _activity_count(transaction: Session, case_id: str = CASE_ID) -> int:
    return int(
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        )
        or 0
    )


def _exact_register_rule(
    contexts: list[object],
) -> Callable[[LifecycleEventCommand, LifecycleProjection, object], object]:
    def rule(
        command: LifecycleEventCommand,
        previous_projection: LifecycleProjection,
        context: object,
    ) -> object:
        contexts.append(context)
        context_type = getattr(_service(), "PatentRegisterStatusRuleContext", None)
        if context_type is None or type(context) is not context_type:
            return None

        predecessor_event_type = context.predecessor_event_type
        predecessor_hash = context.predecessor_status_snapshot_hash
        command_marker = command.supersedes_event_id
        payload_marker = command.payload.get("supersedes_activity_id")
        supplied_hash = command.payload.get("predecessor_status_snapshot_hash")
        new_hash = command.payload.get("status_snapshot_hash")
        if command_marker is None and payload_marker is None and supplied_hash is None:
            if predecessor_event_type is not None or predecessor_hash is not None:
                return None
        elif (
            type(command_marker) is not str
            or not command_marker
            or payload_marker != command_marker
            or predecessor_event_type != REGISTER_EVENT
            or supplied_hash != predecessor_hash
            or type(supplied_hash) is not str
            or new_hash == supplied_hash
        ):
            return None

        return _service().LifecycleRuleDecision(
            current_projection=previous_projection,
            conflict_codes=(CONFLICT_CODE,),
        )

    return rule


def _registry_with_exact_register(
    contexts: list[object],
) -> Callable[[str], object]:
    register_rule = _exact_register_rule(contexts)

    def resolve(event_type: str) -> object:
        if event_type == REGISTER_EVENT:
            return register_rule
        return lambda _command, previous, _transaction: _service().LifecycleRuleDecision(
            current_projection=previous
        )

    return resolve


def test_decision_and_register_context_are_exact_immutable_internal_types() -> None:
    service = _service()
    decision = service.LifecycleRuleDecision(current_projection=IN_FORCE_PROJECTION)
    context = service.PatentRegisterStatusRuleContext(
        predecessor_event_type=None,
        predecessor_status_snapshot_hash=None,
    )

    assert decision.conflict_codes == ()
    assert context.predecessor_event_type is None
    assert context.predecessor_status_snapshot_hash is None
    with pytest.raises(TypeError):
        service.PatentRegisterStatusRuleContext(None, None)
    with pytest.raises((AttributeError, TypeError)):
        context.predecessor_event_type = REGISTER_EVENT


@pytest.mark.parametrize(
    "conflict_codes",
    (
        ["A_CONFLICT"],
        ("Z_CONFLICT", "A_CONFLICT"),
        ("A_CONFLICT", "A_CONFLICT"),
        ("",),
    ),
)
def test_rule_decision_conflict_codes_fail_closed_before_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    conflict_codes: object,
) -> None:
    _install_registry(
        monkeypatch,
        lambda _event_type: (
            lambda _command, previous, _context: _service().LifecycleRuleDecision(
                current_projection=previous,
                conflict_codes=cast(tuple[str, ...], conflict_codes),
            )
        ),
    )
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        _expect_error(
            "LIFECYCLE_RULE_DECISION_INVALID",
            lambda: _service().apply_lifecycle_event(_command(), transaction),
        )

        assert _activity_count(transaction) == 0
        assert transaction.get(Case, CASE_ID).lifecycle_revision == 0  # type: ignore[union-attr]


def test_conflict_appends_once_and_exact_replay_reuses_typed_result(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contexts: list[object] = []
    resolved_event_types: list[str] = []
    registry = _registry_with_exact_register(contexts)

    def resolve(event_type: str) -> object:
        resolved_event_types.append(event_type)
        return registry(event_type)

    _install_registry(monkeypatch, resolve)
    command = _command()
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        first = _service().apply_lifecycle_event(command, transaction)
        transaction.commit()
        replay = _service().apply_lifecycle_event(command, transaction)

        assert first.reused is False
        assert replay.reused is True
        assert replay.activity_id == first.activity_id
        assert first.sequence == first.lifecycle_revision == 1
        assert replay.sequence == replay.lifecycle_revision == 1
        assert first.conflict_codes == replay.conflict_codes == (CONFLICT_CODE,)
        assert first.previous_projection == first.current_projection == IN_FORCE_PROJECTION
        assert replay.previous_projection == replay.current_projection == IN_FORCE_PROJECTION
        assert first.legacy_case_status == replay.legacy_case_status == "GRANTED"
        assert _activity_count(transaction) == 1
        stored_case = transaction.get(Case, CASE_ID)
        assert stored_case is not None
        assert stored_case.lifecycle_revision == 1
        assert stored_case.status == "GRANTED"
        assert stored_case.legal_status == LegalStatus.PATENT_IN_FORCE.value

    assert resolved_event_types == [REGISTER_EVENT, REGISTER_EVENT]
    assert len(contexts) == 2
    assert all(context.predecessor_event_type is None for context in contexts)
    assert all(context.predecessor_status_snapshot_hash is None for context in contexts)


def test_pre_carrier_register_replay_fails_closed_without_reconstruction(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_registry(monkeypatch, _registry_with_exact_register([]))
    command = _command()
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        first = _service().apply_lifecycle_event(command, transaction)
        transaction.commit()

        activity = transaction.get(CaseActivityEvent, first.activity_id)
        assert activity is not None
        transaction.execute(
            delete(CaseActivityEventConflict).where(
                CaseActivityEventConflict.activity_id == activity.id
            )
        )
        activity.conflict_lineage_version = None
        activity.conflict_code_count = None
        activity.conflict_codes_sha256 = None
        transaction.commit()

        _expect_error(
            "LIFECYCLE_CONFLICT_LINEAGE_MISSING",
            lambda: _service().apply_lifecycle_event(command, transaction),
        )
        assert _activity_count(transaction) == 1


def test_same_register_key_with_different_fact_is_idempotency_conflict_before_rule(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contexts: list[object] = []
    _install_registry(monkeypatch, _registry_with_exact_register(contexts))
    command = _command()
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        _service().apply_lifecycle_event(command, transaction)
        transaction.commit()

        _expect_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            lambda: _service().apply_lifecycle_event(
                replace(command, supersedes_event_id="missing-predecessor"),
                transaction,
            ),
        )

        assert _activity_count(transaction) == 1
        assert transaction.get(Case, CASE_ID).lifecycle_revision == 1  # type: ignore[union-attr]
        assert len(contexts) == 1


def test_replacement_context_comes_from_verified_persisted_predecessor(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contexts: list[object] = []
    _install_registry(monkeypatch, _registry_with_exact_register(contexts))
    first_payload = _payload()
    first_hash = cast(str, first_payload["status_snapshot_hash"])
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        first = _service().apply_lifecycle_event(
            _command(payload=first_payload),
            transaction,
        )
        transaction.commit()

        replacement_payload = _payload(
            register_status="PATENT_INVALIDATED",
            predecessor_hash=first_hash,
            supersedes_activity_id=first.activity_id,
        )
        replacement = _service().apply_lifecycle_event(
            _command(
                idempotency_key="register-status-2",
                payload=replacement_payload,
                supersedes_event_id=first.activity_id,
            ),
            transaction,
        )

        assert replacement.reused is False
        assert replacement.sequence == replacement.lifecycle_revision == 2
        assert replacement.conflict_codes == (CONFLICT_CODE,)
        assert _activity_count(transaction) == 2
        assert transaction.get(Case, CASE_ID).lifecycle_revision == 2  # type: ignore[union-attr]

    assert contexts[0].predecessor_event_type is None
    assert contexts[0].predecessor_status_snapshot_hash is None
    assert contexts[1].predecessor_event_type == REGISTER_EVENT
    assert contexts[1].predecessor_status_snapshot_hash == first_hash


@pytest.mark.parametrize("stored_first", ("register", "other"))
def test_cross_event_same_key_remains_generic_idempotency_conflict(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    stored_first: str,
) -> None:
    contexts: list[object] = []
    _install_registry(monkeypatch, _registry_with_exact_register(contexts))
    first_event = REGISTER_EVENT if stored_first == "register" else "CASE_OPENED"
    second_event = "CASE_OPENED" if stored_first == "register" else REGISTER_EVENT
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        _service().apply_lifecycle_event(
            _command(event_type=first_event, idempotency_key="cross-event-key"),
            transaction,
        )
        transaction.commit()

        _expect_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            lambda: _service().apply_lifecycle_event(
                _command(event_type=second_event, idempotency_key="cross-event-key"),
                transaction,
            ),
        )

        assert _activity_count(transaction) == 1
        assert transaction.get(Case, CASE_ID).lifecycle_revision == 1  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("predecessor_kind", "expected_code"),
    (
        ("missing", "LIFECYCLE_SUPERSEDED_ACTIVITY_NOT_FOUND"),
        ("other_case", "LIFECYCLE_SUPERSEDED_ACTIVITY_CASE_MISMATCH"),
        ("wrong_event_type", "LIFECYCLE_RULE_DECISION_INVALID"),
        ("malformed_payload", "LIFECYCLE_PAYLOAD_INVALID"),
    ),
)
def test_predecessor_lookup_and_payload_fail_closed_without_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    predecessor_kind: str,
    expected_code: str,
) -> None:
    contexts: list[object] = []
    _install_registry(monkeypatch, _registry_with_exact_register(contexts))
    predecessor_id = "missing-predecessor"
    predecessor_hash = "a" * 64
    with session_factory() as transaction:
        transaction.add(_case())
        if predecessor_kind == "other_case":
            transaction.add(_case(OTHER_CASE_ID))
        transaction.commit()

        if predecessor_kind in {"other_case", "wrong_event_type", "malformed_payload"}:
            case_id = OTHER_CASE_ID if predecessor_kind == "other_case" else CASE_ID
            event_type = (
                "CASE_OPENED" if predecessor_kind == "wrong_event_type" else REGISTER_EVENT
            )
            first = _service().apply_lifecycle_event(
                _command(
                    case_id=case_id,
                    event_type=event_type,
                    idempotency_key=f"{predecessor_kind}-source",
                ),
                transaction,
            )
            transaction.commit()
            predecessor_id = first.activity_id
            activity = transaction.get(CaseActivityEvent, predecessor_id)
            assert activity is not None
            predecessor_hash = cast(
                str,
                json.loads(activity.payload_json)["status_snapshot_hash"],
            )
            if predecessor_kind == "malformed_payload":
                activity.payload_json = '{"schema": "noncanonical"}'
                transaction.commit()

        before_count = _activity_count(transaction)
        before_revision = transaction.get(Case, CASE_ID).lifecycle_revision  # type: ignore[union-attr]
        replacement_payload = _payload(
            register_status="PATENT_INVALIDATED",
            predecessor_hash=predecessor_hash,
            supersedes_activity_id=predecessor_id,
        )
        _expect_error(
            expected_code,
            lambda: _service().apply_lifecycle_event(
                _command(
                    idempotency_key=f"{predecessor_kind}-replacement",
                    payload=replacement_payload,
                    supersedes_event_id=predecessor_id,
                ),
                transaction,
            ),
        )

        assert _activity_count(transaction) == before_count
        assert transaction.get(Case, CASE_ID).lifecycle_revision == before_revision  # type: ignore[union-attr]


@pytest.mark.parametrize("mismatch", ("incomplete", "hash", "equal_hash"))
def test_replacement_context_mismatch_is_invalid_decision_without_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    mismatch: str,
) -> None:
    contexts: list[object] = []
    _install_registry(monkeypatch, _registry_with_exact_register(contexts))
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        first_payload = _payload()
        first_hash = cast(str, first_payload["status_snapshot_hash"])
        first = _service().apply_lifecycle_event(_command(payload=first_payload), transaction)
        transaction.commit()

        replacement_payload = _payload(
            register_status="PATENT_INVALIDATED",
            predecessor_hash=first_hash,
            supersedes_activity_id=first.activity_id,
        )
        command = _command(
            idempotency_key=f"context-{mismatch}",
            payload=replacement_payload,
            supersedes_event_id=first.activity_id,
        )
        if mismatch == "incomplete":
            replacement_payload["supersedes_activity_id"] = None
        elif mismatch == "hash":
            replacement_payload["predecessor_status_snapshot_hash"] = "b" * 64
        else:
            replacement_payload["status_snapshot"] = first_payload["status_snapshot"]
            replacement_payload["status_snapshot_hash"] = first_hash

        _expect_error(
            "LIFECYCLE_RULE_DECISION_INVALID",
            lambda: _service().apply_lifecycle_event(
                replace(command, payload=replacement_payload),
                transaction,
            ),
        )

        assert _activity_count(transaction) == 1
        assert transaction.get(Case, CASE_ID).lifecycle_revision == 1  # type: ignore[union-attr]
