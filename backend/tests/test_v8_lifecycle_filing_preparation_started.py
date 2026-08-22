from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone
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
from app.modules.cases.lifecycle_rules import get_lifecycle_rule
from app.modules.cases.lifecycle_service import LifecycleRuleDecision

OPEN_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.NEW_CASE,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
FILING_PREPARATION_PROJECTION = replace(
    OPEN_PROJECTION,
    business_stage=BusinessStage.FILING_PREPARATION,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"FILING_PREPARATION_STARTED rule must not access transaction.{name}")


def _command(*, event_type: str = "FILING_PREPARATION_STARTED") -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-filing-preparation",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 14, 11, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-filing-preparation",
                evidence_kind="FILING_WORK_PACKAGE",
                object_type="OfficialWorkPackage",
                object_id="work-package-filing-preparation",
                content_hash=f"sha256:{'a' * 64}",
                captured_at=datetime(2026, 7, 14, 10, 59),
            ),
        ),
        actor_id="actor-filing-preparation",
        idempotency_key="filing-preparation-started-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return get_lifecycle_rule("FILING_PREPARATION_STARTED")


def test_registry_resolves_only_exact_filing_preparation_started() -> None:
    rule = get_lifecycle_rule("FILING_PREPARATION_STARTED")

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("filing_preparation_started") is None
    assert get_lifecycle_rule("FILING_PREPARATION_STARTED ") is None
    assert get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["FILING_PREPARATION_STARTED"]) is None


def test_filing_preparation_started_changes_only_business_stage() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), OPEN_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=FILING_PREPARATION_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="CASE_OPENED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(
            _command(),
            confirmation_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(_command(), case_id=""),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 14, 11, 0, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 14, 11, 0, tzinfo=timezone.utc),
        ),
    ),
)
def test_filing_preparation_started_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, OPEN_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(OPEN_PROJECTION, business_stage=BusinessStage.FILING_PREPARATION),
        replace(
            OPEN_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED,
        ),
        replace(OPEN_PROJECTION, legal_status=LegalStatus.APPLICATION_PENDING),
        replace(
            OPEN_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            OPEN_PROJECTION,
            business_stage=cast(BusinessStage, BusinessStage.NEW_CASE.value),
        ),
    ),
)
def test_filing_preparation_started_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
