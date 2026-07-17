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

FILING_PREPARATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.FILING_PREPARATION,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
WAITING_RECEIPT_PROJECTION = replace(
    FILING_PREPARATION_PROJECTION,
    business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
    official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"FILING_EXTERNAL_SUBMISSION_RECORDED rule must not access transaction.{name}"
        )


def _evidence_refs() -> tuple[EvidenceReference, ...]:
    return (
        EvidenceReference(
            case_id="case-filing-external-submission",
            evidence_kind="FINAL_SUBMISSION_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id="evidence-version-final-1",
            content_hash=f"sha256:{'a' * 64}",
            captured_at=datetime(2026, 7, 14, 12, 0),
        ),
        EvidenceReference(
            case_id="case-filing-external-submission",
            evidence_kind="MANUAL_EXTERNAL_SUBMISSION_RECORD",
            object_type="CaseActivityEvent",
            object_id="submission-evidence-1",
            content_hash=f"sha256:{'b' * 64}",
            captured_at=datetime(2026, 7, 14, 12, 1),
        ),
    )


def _command(*, event_type: str = "FILING_EXTERNAL_SUBMISSION_RECORDED") -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-filing-external-submission",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 14, 12, 5),
        evidence_refs=_evidence_refs(),
        actor_id="actor-filing-external-submission",
        idempotency_key="filing-external-submission-recorded-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED")


def test_registry_resolves_only_exact_filing_external_submission_recorded() -> None:
    rule = get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED")

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("filing_external_submission_recorded") is None
    assert get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED ") is None
    assert get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["FILING_EXTERNAL_SUBMISSION_RECORDED"]) is None


def test_filing_external_submission_moves_to_waiting_receipt() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), FILING_PREPARATION_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=WAITING_RECEIPT_PROJECTION,
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
        replace(_command(), case_id=""),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 14, 12, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 14, 12, 5, tzinfo=timezone.utc),
        ),
    ),
)
def test_filing_external_submission_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, FILING_PREPARATION_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            FILING_PREPARATION_PROJECTION,
            business_stage=BusinessStage.NEW_CASE,
        ),
        replace(
            FILING_PREPARATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
        ),
        replace(
            FILING_PREPARATION_PROJECTION,
            legal_status=LegalStatus.APPLICATION_PENDING,
        ),
        replace(
            FILING_PREPARATION_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            FILING_PREPARATION_PROJECTION,
            business_stage=cast(BusinessStage, BusinessStage.FILING_PREPARATION.value),
        ),
    ),
)
def test_filing_external_submission_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
