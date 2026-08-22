from __future__ import annotations

from dataclasses import replace
from datetime import datetime

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
        raise AssertionError(f"expiry rule must not access transaction.{name}")


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-expiry",
        event_type="PATENT_EXPIRY_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 12, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-expiry",
                evidence_kind="PATENT_EXPIRY_CONFIRMATION",
                object_type="DocumentEvidenceVersion",
                object_id="expiry-evidence",
                content_hash=f"sha256:{'e' * 64}",
                captured_at=datetime(2026, 7, 30, 11, 55),
            ),
        ),
        actor_id="actor-expiry",
        idempotency_key="patent-expiry-confirmed-1",
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
    ("PATENT_EXPIRY_CONFIRMATION", "PATENT_REGISTER_STATUS_EVIDENCE"),
)
def test_confirmed_expiry_closes_in_force_patent(evidence_kind: str) -> None:
    rule = get_lifecycle_rule("PATENT_EXPIRY_CONFIRMED")
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
            legal_status=LegalStatus.PATENT_EXPIRED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(IN_FORCE_PROJECTION, legal_status=LegalStatus.PATENT_EXPIRED),
        replace(IN_FORCE_PROJECTION, business_stage=BusinessStage.CLOSED),
        replace(
            IN_FORCE_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_expiry_fails_closed_outside_confirmed_in_force_patent(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("PATENT_EXPIRY_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="PATENT_TERMINATION_CONFIRMED"),
        replace(_command(), lane=ActivityLane.FEE),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], case_id="other"),),
        ),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], content_hash="bad"),),
        ),
        replace(_command(), payload={"expiry": True}),
        replace(_command(), supersedes_event_id="superseded"),
    ),
)
def test_expiry_command_boundary_fails_closed(command: LifecycleEventCommand) -> None:
    rule = get_lifecycle_rule("PATENT_EXPIRY_CONFIRMED")
    assert rule is not None
    assert rule(command, IN_FORCE_PROJECTION, InteractionForbidden()) is None
