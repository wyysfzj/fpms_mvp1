from __future__ import annotations

import sys
from collections.abc import Iterator, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from importlib import import_module
from inspect import Parameter, signature
from typing import cast

import pytest

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_service import LifecycleRuleDecision

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


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"CASE_OPENED rule must not access transaction.{name}")


@pytest.fixture(autouse=True)
def _isolate_lazy_rules_module() -> Iterator[None]:
    sys.modules.pop(RULES_MODULE, None)
    yield
    sys.modules.pop(RULES_MODULE, None)


def _command(*, event_type: str = "CASE_OPENED") -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-lifecycle-opened",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 14, 10, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-lifecycle-opened",
                evidence_kind="CASE_RECORD",
                object_type="Case",
                object_id="case-lifecycle-opened",
                content_hash=f"sha256:{'a' * 64}",
                captured_at=datetime(2026, 7, 14, 9, 59),
            ),
        ),
        actor_id="actor-lifecycle-opened",
        idempotency_key="case-opened-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return import_module(RULES_MODULE).get_lifecycle_rule("CASE_OPENED")


def test_registry_resolves_only_exact_case_opened_with_frozen_signature() -> None:
    module = import_module(RULES_MODULE)
    rule = module.get_lifecycle_rule("CASE_OPENED")

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert module.get_lifecycle_rule("case_opened") is None
    assert module.get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert module.get_lifecycle_rule(None) is None
    assert module.get_lifecycle_rule(["CASE_OPENED"]) is None


def test_case_opened_initializes_exact_projection_without_transaction_interaction() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), EMPTY_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=OPEN_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="FILING_PREPARATION_STARTED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(
            _command(),
            confirmation_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_case_opened_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(command, EMPTY_PROJECTION, InteractionForbidden())

    assert decision is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), case_id=""),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 14, 10, 0, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 14, 10, 0, tzinfo=timezone.utc),
        ),
    ),
)
def test_case_opened_fails_closed_for_invalid_frozen_command_fields(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(command, EMPTY_PROJECTION, InteractionForbidden())

    assert decision is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(EMPTY_PROJECTION, business_stage=BusinessStage.NEW_CASE),
        replace(
            EMPTY_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
        ),
        replace(EMPTY_PROJECTION, legal_status=LegalStatus.NOT_ESTABLISHED),
        replace(
            EMPTY_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
    ),
)
def test_case_opened_rejects_any_initialized_or_malformed_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
