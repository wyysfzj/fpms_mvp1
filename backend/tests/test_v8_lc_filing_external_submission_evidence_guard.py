from dataclasses import replace
from datetime import datetime, timezone
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

CASE_ID = "case-filing-external-submission"
CAPTURED_AT = datetime(2026, 7, 15, 10, 59)
CONTENT_HASH = f"sha256:{'a' * 64}"
FILING_PREPARATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.FILING_PREPARATION,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
WAITING_RECEIPT_PROJECTION = replace(
    FILING_PREPARATION_PROJECTION,
    business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
    official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"FILING_EXTERNAL_SUBMISSION_RECORDED rule must not access transaction.{name}"
        )


class OtherEvidenceReference(EvidenceReference):
    pass


def _evidence(
    *,
    evidence_kind: str,
    object_type: str,
    object_id: str,
    case_id: str = CASE_ID,
    content_hash: str = CONTENT_HASH,
    captured_at: datetime = CAPTURED_AT,
) -> EvidenceReference:
    return EvidenceReference(
        case_id=case_id,
        evidence_kind=evidence_kind,
        object_type=object_type,
        object_id=object_id,
        content_hash=content_hash,
        captured_at=captured_at,
    )


def _evidence_refs() -> tuple[EvidenceReference, ...]:
    return (
        _evidence(
            evidence_kind="FINAL_SUBMISSION_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id="final-submission-version-1",
        ),
        _evidence(
            evidence_kind="MANUAL_EXTERNAL_SUBMISSION_RECORD",
            object_type="CaseActivityEvent",
            object_id="manual-external-submission-record-1",
        ),
    )


def _command(evidence_refs: object = _evidence_refs()) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type="FILING_EXTERNAL_SUBMISSION_RECORDED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 15, 11, 0),
        evidence_refs=cast(tuple[EvidenceReference, ...], evidence_refs),
        actor_id="actor-filing-external-submission",
        idempotency_key="filing-external-submission-evidence-guard-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def test_external_submission_rejects_wrong_manual_record_object_type() -> None:
    rule = get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED")
    evidence_refs = _evidence_refs()
    command = _command(
        (
            evidence_refs[0],
            replace(evidence_refs[1], object_type="SubmissionEvidence"),
        )
    )

    assert rule is not None
    decision = rule(command, FILING_PREPARATION_PROJECTION, InteractionForbidden())

    assert decision is None


@pytest.mark.parametrize(
    "evidence_refs",
    (
        _evidence_refs(),
        tuple(reversed(_evidence_refs())),
    ),
)
def test_external_submission_accepts_exact_unordered_tuple_deterministically(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED")
    command = _command(evidence_refs)
    assert rule is not None

    first_decision = rule(command, FILING_PREPARATION_PROJECTION, InteractionForbidden())
    second_decision = rule(command, FILING_PREPARATION_PROJECTION, InteractionForbidden())

    expected = LifecycleRuleDecision(
        current_projection=WAITING_RECEIPT_PROJECTION,
        oa_sequence=None,
    )
    assert type(first_decision) is LifecycleRuleDecision
    assert first_decision == expected
    assert second_decision == expected


FINAL_REFERENCE, MANUAL_REFERENCE = _evidence_refs()
UNKNOWN_REFERENCE = _evidence(
    evidence_kind="UNKNOWN_EXTERNAL_SUBMISSION_EVIDENCE",
    object_type="UnknownEvidence",
    object_id="unknown-external-submission-evidence-1",
)
SUBCLASS_REFERENCE = OtherEvidenceReference(
    case_id=CASE_ID,
    evidence_kind="FINAL_SUBMISSION_VERSION",
    object_type="DocumentEvidenceVersion",
    object_id="final-submission-version-subclass",
    content_hash=CONTENT_HASH,
    captured_at=CAPTURED_AT,
)


@pytest.mark.parametrize(
    "evidence_refs",
    (
        None,
        [],
        (),
        (FINAL_REFERENCE,),
        (MANUAL_REFERENCE,),
        (FINAL_REFERENCE, MANUAL_REFERENCE, UNKNOWN_REFERENCE),
        (FINAL_REFERENCE, FINAL_REFERENCE),
        (MANUAL_REFERENCE, MANUAL_REFERENCE),
        (FINAL_REFERENCE, UNKNOWN_REFERENCE),
        (SUBCLASS_REFERENCE, MANUAL_REFERENCE),
        (cast(EvidenceReference, object()), MANUAL_REFERENCE),
        (
            replace(FINAL_REFERENCE, object_type="DocumentEvidence"),
            MANUAL_REFERENCE,
        ),
        (replace(FINAL_REFERENCE, case_id="different-case"), MANUAL_REFERENCE),
        (FINAL_REFERENCE, replace(MANUAL_REFERENCE, case_id="different-case")),
        (
            FINAL_REFERENCE,
            replace(MANUAL_REFERENCE, object_id=FINAL_REFERENCE.object_id),
        ),
        (
            replace(FINAL_REFERENCE, content_hash=f"sha256:{'A' * 64}"),
            MANUAL_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, content_hash=f"sha256:{'a' * 63}"),
            MANUAL_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(MANUAL_REFERENCE, content_hash=f"sha256:{'a' * 63}g"),
        ),
        (
            FINAL_REFERENCE,
            replace(MANUAL_REFERENCE, content_hash=f"{'a' * 64}"),
        ),
        (
            replace(FINAL_REFERENCE, content_hash=cast(str, None)),
            MANUAL_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, captured_at=cast(datetime, None)),
            MANUAL_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, captured_at=cast(datetime, "not-a-datetime")),
            MANUAL_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(MANUAL_REFERENCE, captured_at=CAPTURED_AT.replace(tzinfo=timezone.utc)),
        ),
    ),
)
def test_external_submission_fails_closed_for_invalid_evidence_matrix(
    evidence_refs: object,
) -> None:
    rule = get_lifecycle_rule("FILING_EXTERNAL_SUBMISSION_RECORDED")
    assert rule is not None

    decision = rule(
        _command(cast(tuple[EvidenceReference, ...], evidence_refs)),
        FILING_PREPARATION_PROJECTION,
        InteractionForbidden(),
    )

    assert decision is None
