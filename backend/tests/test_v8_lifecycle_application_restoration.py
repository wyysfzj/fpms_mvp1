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
        raise AssertionError(f"application restoration rule accessed transaction.{name}")


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-application-restoration",
        event_type="APPLICATION_RIGHT_RESTORATION_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 14, 0),
        evidence_refs=(
            EvidenceReference(
                case_id="case-application-restoration",
                evidence_kind="APPLICATION_RIGHT_RESTORATION_DECISION",
                object_type="DocumentEvidenceVersion",
                object_id="application-restoration-decision",
                content_hash=f"sha256:{'b' * 64}",
                captured_at=datetime(2026, 7, 30, 13, 55),
            ),
        ),
        actor_id="actor-application-restoration",
        idempotency_key="application-right-restoration-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={
            "restored_official_procedure_stage": (
                OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
            )
        },
    )


ABANDONED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.CLOSED,
    official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
    legal_status=LegalStatus.APPLICATION_ABANDONED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


@pytest.mark.parametrize(
    ("official_stage", "business_stage"),
    (
        (
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
            BusinessStage.PROSECUTION_MANAGEMENT,
        ),
        (OfficialProcedureStage.ACCEPTED, BusinessStage.PROSECUTION_MANAGEMENT),
        (
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            BusinessStage.PROSECUTION_MANAGEMENT,
        ),
        (
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
            BusinessStage.OA_REPLY_IN_PROGRESS,
        ),
        (OfficialProcedureStage.PUBLISHED, BusinessStage.PROSECUTION_MANAGEMENT),
        (
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            BusinessStage.PROSECUTION_MANAGEMENT,
        ),
        (
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            BusinessStage.OA_REPLY_IN_PROGRESS,
        ),
        (OfficialProcedureStage.REEXAMINATION, BusinessStage.PROSECUTION_MANAGEMENT),
        (
            OfficialProcedureStage.GRANT_REGISTRATION,
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
        ),
    ),
)
def test_official_restoration_returns_abandoned_application_to_confirmed_stage(
    official_stage: OfficialProcedureStage,
    business_stage: BusinessStage,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None

    decision = rule(
        replace(
            _command(),
            payload={"restored_official_procedure_stage": official_stage.value},
        ),
        ABANDONED_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=business_stage,
            official_procedure_stage=official_stage,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(ABANDONED_PROJECTION, legal_status=LegalStatus.APPLICATION_WITHDRAWN),
        replace(ABANDONED_PROJECTION, business_stage=BusinessStage.PROSECUTION_MANAGEMENT),
        replace(
            ABANDONED_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_application_restoration_requires_exact_confirmed_abandoned_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None
    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="PATENT_RIGHT_RESTORATION_CONFIRMED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(
            _command(),
            evidence_refs=(replace(_command().evidence_refs[0], evidence_kind="ARBITRARY"),),
        ),
        replace(_command(), payload={}),
        replace(
            _command(),
            payload={
                "restored_official_procedure_stage": (OfficialProcedureStage.PROCEDURE_CLOSED.value)
            },
        ),
        replace(
            _command(),
            payload={
                "restored_official_procedure_stage": (
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                "default_business_stage": BusinessStage.PROSECUTION_MANAGEMENT.value,
            },
        ),
        replace(
            _command(),
            payload={
                "restored_official_procedure_stage": (
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION
                )
            },
        ),
        replace(_command(), source_activity_id="source"),
    ),
)
def test_application_restoration_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_RIGHT_RESTORATION_CONFIRMED")
    assert rule is not None
    assert rule(command, ABANDONED_PROJECTION, InteractionForbidden()) is None
