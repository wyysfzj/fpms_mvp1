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
        raise AssertionError(f"withdrawal rule must not access transaction.{name}")


def _evidence(kind: str, suffix: str) -> EvidenceReference:
    return EvidenceReference(
        case_id="case-withdrawal",
        evidence_kind=kind,
        object_type="DocumentEvidenceVersion",
        object_id=f"withdrawal-{suffix}",
        content_hash=f"sha256:{suffix[0] * 64}",
        captured_at=datetime(2026, 7, 30, 9, 0),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-withdrawal",
        event_type="APPLICATION_WITHDRAWAL_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 30, 9, 5),
        evidence_refs=(
            _evidence("APPLICATION_WITHDRAWAL_REQUEST", "a-request"),
            _evidence("APPLICATION_WITHDRAWAL_OFFICIAL_CONFIRMATION", "b-confirmation"),
        ),
        actor_id="actor-withdrawal",
        idempotency_key="application-withdrawal-confirmed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


PENDING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


@pytest.mark.parametrize(
    ("business_stage", "official_stage"),
    (
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.ACCEPTED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.PUBLISHED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.REEXAMINATION),
        (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            OfficialProcedureStage.GRANT_REGISTRATION,
        ),
    ),
)
def test_confirmed_withdrawal_closes_each_ungranted_application_stage(
    business_stage: BusinessStage,
    official_stage: OfficialProcedureStage,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_WITHDRAWAL_CONFIRMED")
    assert rule is not None

    decision = rule(
        _command(),
        replace(
            PENDING_PROJECTION,
            business_stage=business_stage,
            official_procedure_stage=official_stage,
        ),
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_WITHDRAWN,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(PENDING_PROJECTION, legal_status=LegalStatus.PATENT_IN_FORCE),
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
def test_withdrawal_fails_closed_outside_confirmed_ungranted_application(
    previous_projection: LifecycleProjection,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_WITHDRAWAL_CONFIRMED")
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="APPLICATION_ABANDONMENT_CONFIRMED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), evidence_refs=(_command().evidence_refs[0],)),
        replace(
            _command(),
            evidence_refs=(
                replace(
                    _command().evidence_refs[0],
                    evidence_kind="APPLICATION_WITHDRAWAL_OFFICIAL_CONFIRMATION",
                ),
                _command().evidence_refs[1],
            ),
        ),
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
                replace(_command().evidence_refs[0], content_hash="not-a-hash"),
                _command().evidence_refs[1],
            ),
        ),
        replace(_command(), payload={"status": "WITHDRAWN"}),
        replace(_command(), effective_at=datetime.now(timezone.utc)),
        replace(_command(), source_activity_id="source-activity"),
        replace(_command(), supersedes_event_id="superseded-event"),
    ),
)
def test_withdrawal_command_boundary_fails_closed(
    command: LifecycleEventCommand,
) -> None:
    rule = get_lifecycle_rule("APPLICATION_WITHDRAWAL_CONFIRMED")
    assert rule is not None

    assert rule(command, PENDING_PROJECTION, InteractionForbidden()) is None


def test_registry_is_exact_for_application_withdrawal() -> None:
    assert get_lifecycle_rule("APPLICATION_WITHDRAWAL_CONFIRMED") is not None
    assert get_lifecycle_rule("application_withdrawal_confirmed") is None
    assert get_lifecycle_rule("APPLICATION_WITHDRAWAL_CONFIRMED ") is None
    assert get_lifecycle_rule(None) is None
