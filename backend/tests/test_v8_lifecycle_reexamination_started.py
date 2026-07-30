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
from app.modules.cases.lifecycle_projection import (
    LegacyProjectionDisposition,
    project_legacy_case_status,
)
from app.modules.cases.lifecycle_rules import get_lifecycle_rule
from app.modules.cases.lifecycle_service import LifecycleRuleDecision

PENDING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
REJECTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.CLOSED,
    official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
    legal_status=LegalStatus.APPLICATION_REJECTED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
REEXAMINATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.REEXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"REEXAMINATION_STARTED rule must not access transaction.{name}")


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-reexamination",
        evidence_kind="REEXAMINATION_SOURCE",
        object_type="DocumentEvidenceVersion",
        object_id="reexamination-source-version-1",
        content_hash=f"sha256:{'a' * 64}",
        captured_at=datetime(2026, 7, 23, 16, 0),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-reexamination",
        event_type="REEXAMINATION_STARTED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 23, 16, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-reexamination",
        idempotency_key="reexamination-started-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    rule = get_lifecycle_rule("REEXAMINATION_STARTED")
    assert rule is not None
    return rule


def test_registry_resolves_only_exact_reexamination_started_event() -> None:
    assert callable(_rule())
    assert get_lifecycle_rule("reexamination_started") is None
    assert get_lifecycle_rule("REEXAMINATION_STARTED ") is None
    assert get_lifecycle_rule(None) is None


@pytest.mark.parametrize("previous_projection", (PENDING_PROJECTION, REJECTED_PROJECTION))
def test_reexamination_started_enters_pending_reexamination(
    previous_projection: LifecycleProjection,
) -> None:
    decision = _rule()(_command(), previous_projection, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=REEXAMINATION_PROJECTION,
        oa_sequence=None,
    )


def test_reexamination_started_projects_legacy_reexam_after_rejection() -> None:
    decision = _rule()(_command(), REJECTED_PROJECTION, InteractionForbidden())
    assert type(decision) is LifecycleRuleDecision

    legacy = project_legacy_case_status(
        existing_status="REJECTED",
        projection=decision.current_projection,
        latest_confirmed_lifecycle_event_type="REEXAMINATION_STARTED",
        oa_sequence=decision.oa_sequence,
    )

    assert legacy.derived_case_status == "REEXAM"
    assert legacy.legacy_case_status == "REEXAM"
    assert legacy.disposition is LegacyProjectionDisposition.UPDATE_REQUIRED


@pytest.mark.parametrize(
    "command",
    (
        replace(_command(), event_type="OA_RECEIPT_ARCHIVED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), payload={"unexpected": True}),
    ),
)
def test_reexamination_started_rejects_invalid_command(
    command: LifecycleEventCommand,
) -> None:
    assert _rule()(command, PENDING_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "evidence",
    (
        replace(_evidence(), case_id="another-case"),
        replace(_evidence(), evidence_kind="REJECTION_DECISION"),
        replace(_evidence(), object_type="Document"),
        replace(_evidence(), object_id=""),
        replace(_evidence(), content_hash="sha256:not-a-valid-hash"),
    ),
)
def test_reexamination_started_requires_same_case_source_evidence(
    evidence: EvidenceReference,
) -> None:
    command = replace(_command(), evidence_refs=(evidence,))

    assert _rule()(command, PENDING_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(PENDING_PROJECTION, business_stage=BusinessStage.OA_REPLY_IN_PROGRESS),
        replace(PENDING_PROJECTION, official_procedure_stage=OfficialProcedureStage.PUBLISHED),
        replace(PENDING_PROJECTION, legal_status=LegalStatus.PATENT_IN_FORCE),
        replace(
            REJECTED_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_reexamination_started_rejects_other_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    assert _rule()(_command(), previous_projection, InteractionForbidden()) is None
