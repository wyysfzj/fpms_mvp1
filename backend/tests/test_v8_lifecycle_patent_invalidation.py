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
        raise AssertionError(f"invalidation rule must not access transaction.{name}")


def _evidence(kind: str, suffix: str) -> EvidenceReference:
    return EvidenceReference(
        case_id="case-invalidation",
        evidence_kind=kind,
        object_type="DocumentEvidenceVersion",
        object_id=f"invalidation-{suffix}",
        content_hash=f"sha256:{suffix[0] * 64}",
        captured_at=datetime(2026, 7, 30, 12, 55),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-invalidation",
        event_type="PATENT_INVALIDATION_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 13, 0),
        evidence_refs=(
            _evidence("EFFECTIVE_PATENT_INVALIDATION_DECISION", "f-decision"),
            _evidence("PATENT_REGISTER_STATUS_EVIDENCE", "a-register"),
        ),
        actor_id="actor-invalidation",
        idempotency_key="patent-invalidation-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


IN_FORCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def test_effective_invalidation_closes_in_force_patent() -> None:
    rule = get_lifecycle_rule("PATENT_INVALIDATION_CONFIRMED")
    assert rule is not None

    decision = rule(
        _command(),
        IN_FORCE_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.PATENT_INVALIDATED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(IN_FORCE_PROJECTION, legal_status=LegalStatus.PATENT_INVALIDATED),
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
def test_invalidation_fails_closed_outside_confirmed_in_force_patent(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("PATENT_INVALIDATION_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), evidence_refs=(_command().evidence_refs[0],)),
        replace(_command(), evidence_refs=tuple(reversed(_command().evidence_refs))),
        replace(
            _command(),
            evidence_refs=(
                _command().evidence_refs[0],
                replace(
                    _command().evidence_refs[1],
                    object_id=_command().evidence_refs[0].object_id,
                ),
            ),
        ),
        replace(
            _command(),
            evidence_refs=(
                _command().evidence_refs[0],
                replace(_command().evidence_refs[1], object_type="Attachment"),
            ),
        ),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), payload={"register_status": "PATENT_INVALIDATED"}),
        replace(_command(), source_activity_id="source"),
        replace(_command(), supersedes_event_id="superseded"),
    ),
)
def test_invalidation_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("PATENT_INVALIDATION_CONFIRMED")
    assert rule is not None
    assert rule(command, IN_FORCE_PROJECTION, InteractionForbidden()) is None
