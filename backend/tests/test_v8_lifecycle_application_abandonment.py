from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

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


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"abandonment rule must not access transaction.{name}")


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-abandonment",
        event_type="APPLICATION_ABANDONMENT_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 10, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-abandonment",
                evidence_kind="DEEMED_ABANDONMENT_NOTICE",
                object_type="DocumentEvidenceVersion",
                object_id="abandonment-notice",
                content_hash=f"sha256:{'c' * 64}",
                captured_at=datetime(2026, 7, 30, 9, 55),
            ),
        ),
        actor_id="actor-abandonment",
        idempotency_key="application-abandonment-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


PENDING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


@pytest.mark.parametrize(
    "evidence_kind",
    ("DEEMED_ABANDONMENT_NOTICE", "RIGHT_ABANDONMENT_CONFIRMATION"),
)
def test_effective_abandonment_closes_ungranted_application(
    evidence_kind: str,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_ABANDONMENT_CONFIRMED")
    assert rule is not None

    decision = rule(
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], evidence_kind=evidence_kind),),
        ),
        PENDING_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_ABANDONED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(PENDING_PROJECTION, legal_status=LegalStatus.APPLICATION_ABANDONED),
        replace(
            PENDING_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            PENDING_PROJECTION,
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
    ),
)
def test_abandonment_fails_closed_for_invalid_predecessor(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_ABANDONMENT_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="APPLICATION_WITHDRAWAL_CONFIRMED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], case_id="another-case"),),
        ),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], evidence_kind="ARBITRARY"),),
        ),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], object_id=" "),),
        ),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], content_hash="bad"),),
        ),
        replace(_command(), payload={"default": True}),
        replace(_command(), effective_at=datetime.now(timezone.utc)),
        replace(_command(), source_activity_id="source"),
        replace(_command(), supersedes_event_id="superseded"),
    ),
)
def test_abandonment_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_ABANDONMENT_CONFIRMED")
    assert rule is not None
    assert rule(command, PENDING_PROJECTION, InteractionForbidden()) is None
