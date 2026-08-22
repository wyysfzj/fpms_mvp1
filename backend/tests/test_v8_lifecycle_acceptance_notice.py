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

WAITING_ACCEPTANCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=(OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE),
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
ACCEPTED_PROJECTION = replace(
    WAITING_ACCEPTANCE_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.ACCEPTED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"ACCEPTANCE_NOTICE_RECORDED rule must not access transaction.{name}")


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-acceptance-notice",
        evidence_kind="ACCEPTANCE_NOTICE",
        object_type="DocumentEvidenceVersion",
        object_id="acceptance-notice-version-1",
        content_hash=f"sha256:{'a' * 64}",
        captured_at=datetime(2026, 7, 18, 10, 0),
    )


def _command(*, event_type: str = "ACCEPTANCE_NOTICE_RECORDED") -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-acceptance-notice",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 18, 10, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-acceptance-notice",
        idempotency_key="acceptance-notice-recorded-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return get_lifecycle_rule("ACCEPTANCE_NOTICE_RECORDED")


def test_registry_resolves_only_exact_acceptance_notice_recorded() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("acceptance_notice_recorded") is None
    assert get_lifecycle_rule("ACCEPTANCE_NOTICE_RECORDED ") is None
    assert get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["ACCEPTANCE_NOTICE_RECORDED"]) is None


def test_acceptance_notice_changes_only_official_stage() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), WAITING_ACCEPTANCE_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=ACCEPTED_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="FILING_RECEIPT_ARCHIVED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 18, 10, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 18, 10, 5, tzinfo=timezone.utc),
        ),
    ),
)
def test_acceptance_notice_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, WAITING_ACCEPTANCE_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "evidence",
    (
        replace(_evidence(), evidence_kind="OFFICIAL_NOTICE"),
        replace(_evidence(), object_type="Document"),
        replace(_evidence(), case_id="another-case"),
        replace(_evidence(), object_id=""),
        replace(_evidence(), object_id=" "),
        replace(_evidence(), content_hash=f"sha256:{'A' * 64}"),
        replace(_evidence(), content_hash="sha256:abc"),
        replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),
        replace(
            _evidence(),
            captured_at=datetime(2026, 7, 18, 10, 0, tzinfo=timezone.utc),
        ),
    ),
)
def test_acceptance_notice_requires_exact_executable_notice_evidence(
    evidence: EvidenceReference,
) -> None:
    rule = _rule()
    assert rule is not None

    command = replace(_command(), evidence_refs=(evidence,))

    assert rule(command, WAITING_ACCEPTANCE_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            WAITING_ACCEPTANCE_PROJECTION,
            business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
        ),
        replace(
            WAITING_ACCEPTANCE_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED,
        ),
        replace(
            WAITING_ACCEPTANCE_PROJECTION,
            legal_status=LegalStatus.NOT_ESTABLISHED,
        ),
        replace(
            WAITING_ACCEPTANCE_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            WAITING_ACCEPTANCE_PROJECTION,
            business_stage=cast(
                BusinessStage,
                BusinessStage.PROSECUTION_MANAGEMENT.value,
            ),
        ),
    ),
)
def test_acceptance_notice_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
