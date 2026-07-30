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

OA_RESPONSE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
SUBSTANTIVE_EXAMINATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"OA_RECEIPT_ARCHIVED rule must not access transaction.{name}")


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-oa-receipt",
        evidence_kind="OA_RECEIPT",
        object_type="OfficialWorkPackageReceipt",
        object_id="oa-receipt-1",
        content_hash=f"sha256:{'a' * 64}",
        captured_at=datetime(2026, 7, 23, 14, 55),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-oa-receipt",
        event_type="OA_RECEIPT_ARCHIVED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 23, 15, 0),
        evidence_refs=(_evidence(),),
        actor_id="actor-oa-receipt",
        idempotency_key="oa-receipt-archived-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    rule = get_lifecycle_rule("OA_RECEIPT_ARCHIVED")
    assert rule is not None
    return rule


def test_oa_receipt_archived_returns_to_substantive_examination() -> None:
    rule = _rule()

    decision = rule(_command(), OA_RESPONSE_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=SUBSTANTIVE_EXAMINATION_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "evidence",
    (
        replace(_evidence(), case_id="another-case"),
        replace(_evidence(), evidence_kind="VALID_FILING_RECEIPT"),
        replace(_evidence(), object_type="DocumentEvidenceVersion"),
        replace(_evidence(), content_hash="sha256:not-a-valid-hash"),
    ),
)
def test_oa_receipt_archived_rejects_invalid_receipt_evidence(
    evidence: EvidenceReference,
) -> None:
    rule = _rule()
    command = replace(_command(), evidence_refs=(evidence,))

    assert rule(command, OA_RESPONSE_PROJECTION, InteractionForbidden()) is None


def test_oa_receipt_archived_requires_confirmed_command() -> None:
    rule = _rule()
    command = replace(
        _command(),
        confirmation_status=ConfirmationStatus.NEEDS_REVIEW,
    )

    assert rule(command, OA_RESPONSE_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(
            OA_RESPONSE_PROJECTION,
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
        ),
        replace(
            OA_RESPONSE_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
        replace(
            OA_RESPONSE_PROJECTION,
            legal_status=LegalStatus.APPLICATION_REJECTED,
        ),
        replace(
            OA_RESPONSE_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_oa_receipt_archived_rejects_wrong_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
