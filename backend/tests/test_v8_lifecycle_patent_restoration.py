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
        raise AssertionError(f"patent restoration rule accessed transaction.{name}")


def _evidence(kind: str, suffix: str) -> EvidenceReference:
    return EvidenceReference(
        case_id="case-patent-restoration",
        evidence_kind=kind,
        object_type="DocumentEvidenceVersion",
        object_id=f"patent-restoration-{suffix}",
        content_hash=f"sha256:{suffix[0] * 64}",
        captured_at=datetime(2026, 7, 30, 14, 55),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-patent-restoration",
        event_type="PATENT_RIGHT_RESTORATION_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 15, 0),
        evidence_refs=(
            _evidence("PATENT_RIGHT_RESTORATION_DECISION", "c-decision"),
            _evidence("PATENT_REGISTER_STATUS_EVIDENCE", "d-register"),
        ),
        actor_id="actor-patent-restoration",
        idempotency_key="patent-right-restoration-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


TERMINATED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.CLOSED,
    official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
    legal_status=LegalStatus.PATENT_TERMINATED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def test_official_restoration_returns_terminated_patent_to_in_force() -> None:
    rule = get_lifecycle_rule("PATENT_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None

    decision = rule(
        _command(),
        TERMINATED_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
            official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
            legal_status=LegalStatus.PATENT_IN_FORCE,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(TERMINATED_PROJECTION, legal_status=LegalStatus.PATENT_EXPIRED),
        replace(
            TERMINATED_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
        ),
        replace(
            TERMINATED_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_patent_restoration_requires_exact_confirmed_terminated_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("PATENT_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="APPLICATION_RIGHT_RESTORATION_CONFIRMED"),
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
                replace(_command().evidence_refs[1], case_id="other"),
            ),
        ),
        replace(_command(), payload={"restored": True}),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), supersedes_event_id="superseded"),
    ),
)
def test_patent_restoration_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("PATENT_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None
    assert rule(command, TERMINATED_PROJECTION, InteractionForbidden()) is None
