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

ACCEPTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.ACCEPTED,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
PRELIMINARY_EXAMINATION_PROJECTION = replace(
    ACCEPTED_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"PRELIMINARY_EXAMINATION_STARTED rule must not access transaction.{name}"
        )


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-preliminary-examination",
        evidence_kind="PRELIMINARY_EXAMINATION_SOURCE",
        object_type="DocumentEvidenceVersion",
        object_id="preliminary-examination-source-version-1",
        content_hash=f"sha256:{'b' * 64}",
        captured_at=datetime(2026, 7, 18, 11, 0),
    )


def _command(
    *,
    event_type: str = "PRELIMINARY_EXAMINATION_STARTED",
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-preliminary-examination",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 18, 11, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-preliminary-examination",
        idempotency_key="preliminary-examination-started-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return get_lifecycle_rule("PRELIMINARY_EXAMINATION_STARTED")


def test_registry_resolves_only_exact_preliminary_examination_started() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("preliminary_examination_started") is None
    assert get_lifecycle_rule("PRELIMINARY_EXAMINATION_STARTED ") is None
    assert get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["PRELIMINARY_EXAMINATION_STARTED"]) is None


def test_preliminary_examination_started_changes_only_official_stage() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), ACCEPTED_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PRELIMINARY_EXAMINATION_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="ACCEPTANCE_NOTICE_RECORDED"),
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
            effective_at=datetime(2026, 7, 18, 11, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 18, 11, 5, tzinfo=timezone.utc),
        ),
    ),
)
def test_preliminary_examination_started_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, ACCEPTED_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "evidence",
    (
        replace(_evidence(), evidence_kind="OFFICIAL_NOTICE"),
        replace(_evidence(), object_type="Document"),
        replace(_evidence(), case_id="another-case"),
        replace(_evidence(), object_id=""),
        replace(_evidence(), object_id=" "),
        replace(_evidence(), content_hash=f"sha256:{'B' * 64}"),
        replace(_evidence(), content_hash="sha256:abc"),
        replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),
        replace(
            _evidence(),
            captured_at=datetime(2026, 7, 18, 11, 0, tzinfo=timezone.utc),
        ),
    ),
)
def test_preliminary_examination_started_requires_exact_confirmed_source_evidence(
    evidence: EvidenceReference,
) -> None:
    rule = _rule()
    assert rule is not None

    command = replace(_command(), evidence_refs=(evidence,))

    assert rule(command, ACCEPTED_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            ACCEPTED_PROJECTION,
            business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
        ),
        replace(
            ACCEPTED_PROJECTION,
            official_procedure_stage=(
                OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE
            ),
        ),
        replace(
            ACCEPTED_PROJECTION,
            legal_status=LegalStatus.NOT_ESTABLISHED,
        ),
        replace(
            ACCEPTED_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            ACCEPTED_PROJECTION,
            business_stage=cast(
                BusinessStage,
                BusinessStage.PROSECUTION_MANAGEMENT.value,
            ),
        ),
    ),
)
def test_preliminary_examination_started_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
