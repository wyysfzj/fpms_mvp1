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
        raise AssertionError(f"termination rule must not access transaction.{name}")


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-termination",
        event_type="PATENT_TERMINATION_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 11, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-termination",
                evidence_kind="PATENT_TERMINATION_NOTICE",
                object_type="DocumentEvidenceVersion",
                object_id="termination-notice",
                content_hash=f"sha256:{'d' * 64}",
                captured_at=datetime(2026, 7, 30, 10, 55),
            ),
        ),
        actor_id="actor-termination",
        idempotency_key="patent-termination-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


IN_FORCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


@pytest.mark.parametrize(
    "evidence_kind",
    ("PATENT_TERMINATION_NOTICE", "PATENT_REGISTER_STATUS_EVIDENCE"),
)
def test_confirmed_termination_closes_in_force_patent(evidence_kind: str) -> None:
    rule = get_lifecycle_rule("PATENT_TERMINATION_CONFIRMED")
    assert rule is not None

    decision = rule(
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], evidence_kind=evidence_kind),),
        ),
        IN_FORCE_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.PATENT_TERMINATED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(IN_FORCE_PROJECTION, legal_status=LegalStatus.PATENT_TERMINATED),
        replace(
            IN_FORCE_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
        ),
        replace(
            IN_FORCE_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_termination_fails_closed_outside_confirmed_in_force_patent(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("PATENT_TERMINATION_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="PATENT_EXPIRY_CONFIRMED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], evidence_kind="UNKNOWN"),),
        ),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], object_id=""),),
        ),
        replace(_command(), payload={"status": "PATENT_TERMINATED"}),
        replace(_command(), effective_at=datetime.now(timezone.utc)),
        replace(_command(), source_activity_id="source"),
    ),
)
def test_termination_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("PATENT_TERMINATION_CONFIRMED")
    assert rule is not None
    assert rule(command, IN_FORCE_PROJECTION, InteractionForbidden()) is None
