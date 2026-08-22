from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone
from inspect import Parameter, signature
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

CASE_ID = "case-filing-receipt"
CAPTURED_AT = datetime(2026, 7, 15, 13, 0)
FINAL_CONTENT_HASH = f"sha256:{'a' * 64}"
RECEIPT_CONTENT_HASH = f"sha256:{'b' * 64}"
WAITING_RECEIPT_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
    official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
PROSECUTION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=(OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE),
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"FILING_RECEIPT_ARCHIVED rule must not access transaction.{name}")


class OtherEvidenceReference(EvidenceReference):
    pass


def _evidence(
    *,
    evidence_kind: str,
    object_type: str,
    object_id: str,
    case_id: str = CASE_ID,
    content_hash: str = FINAL_CONTENT_HASH,
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
            object_id="evidence-version-final-1",
        ),
        _evidence(
            evidence_kind="VALID_FILING_RECEIPT",
            object_type="OfficialWorkPackageReceipt",
            object_id="filing-receipt-1",
            content_hash=RECEIPT_CONTENT_HASH,
            captured_at=datetime(2026, 7, 15, 13, 1),
        ),
    )


def _command(
    *,
    event_type: str = "FILING_RECEIPT_ARCHIVED",
    evidence_refs: object = _evidence_refs(),
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 14, 13, 5),
        evidence_refs=cast(tuple[EvidenceReference, ...], evidence_refs),
        actor_id="actor-filing-receipt",
        idempotency_key="filing-receipt-archived-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _rule():
    return get_lifecycle_rule("FILING_RECEIPT_ARCHIVED")


def test_registry_resolves_only_exact_filing_receipt_archived() -> None:
    rule = get_lifecycle_rule("FILING_RECEIPT_ARCHIVED")

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("filing_receipt_archived") is None
    assert get_lifecycle_rule("FILING_RECEIPT_ARCHIVED ") is None
    assert get_lifecycle_rule("UNREGISTERED_EVENT") is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["FILING_RECEIPT_ARCHIVED"]) is None


def test_filing_receipt_archived_moves_to_prosecution_pending_acceptance() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), WAITING_RECEIPT_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PROSECUTION_PROJECTION,
        oa_sequence=None,
    )


def test_filing_receipt_archived_rejects_wrong_receipt_object_type() -> None:
    rule = _rule()
    evidence_refs = _evidence_refs()
    command = _command(
        evidence_refs=(
            evidence_refs[0],
            replace(evidence_refs[1], object_type="WorkPackageReceipt"),
        )
    )
    assert rule is not None

    assert rule(command, WAITING_RECEIPT_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "evidence_refs",
    (
        _evidence_refs(),
        tuple(reversed(_evidence_refs())),
    ),
)
def test_filing_receipt_archived_accepts_exact_unordered_tuple_deterministically(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = _rule()
    command = _command(evidence_refs=evidence_refs)
    assert rule is not None

    first_decision = rule(command, WAITING_RECEIPT_PROJECTION, InteractionForbidden())
    second_decision = rule(command, WAITING_RECEIPT_PROJECTION, InteractionForbidden())

    expected = LifecycleRuleDecision(
        current_projection=PROSECUTION_PROJECTION,
        oa_sequence=None,
    )
    assert first_decision == expected
    assert second_decision == expected


FINAL_REFERENCE, RECEIPT_REFERENCE = _evidence_refs()
UNKNOWN_REFERENCE = _evidence(
    evidence_kind="UNKNOWN_RECEIPT_EVIDENCE",
    object_type="UnknownEvidence",
    object_id="unknown-receipt-evidence-1",
)
SUBCLASS_REFERENCE = OtherEvidenceReference(
    case_id=CASE_ID,
    evidence_kind="FINAL_SUBMISSION_VERSION",
    object_type="DocumentEvidenceVersion",
    object_id="evidence-version-final-subclass",
    content_hash=FINAL_CONTENT_HASH,
    captured_at=CAPTURED_AT,
)


@pytest.mark.parametrize(
    "evidence_refs",
    (
        None,
        [],
        (),
        (FINAL_REFERENCE,),
        (RECEIPT_REFERENCE,),
        (FINAL_REFERENCE, RECEIPT_REFERENCE, UNKNOWN_REFERENCE),
        (FINAL_REFERENCE, FINAL_REFERENCE),
        (
            FINAL_REFERENCE,
            replace(FINAL_REFERENCE, object_id="evidence-version-final-2"),
        ),
        (RECEIPT_REFERENCE, RECEIPT_REFERENCE),
        (
            RECEIPT_REFERENCE,
            replace(RECEIPT_REFERENCE, object_id="filing-receipt-2"),
        ),
        (FINAL_REFERENCE, UNKNOWN_REFERENCE),
        tuple(reversed((FINAL_REFERENCE, UNKNOWN_REFERENCE))),
        (SUBCLASS_REFERENCE, RECEIPT_REFERENCE),
        (cast(EvidenceReference, object()), RECEIPT_REFERENCE),
        (
            replace(FINAL_REFERENCE, evidence_kind="FINAL_SUBMISSION_DOCUMENT"),
            RECEIPT_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, object_type="DocumentEvidence"),
            RECEIPT_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(RECEIPT_REFERENCE, evidence_kind="FILING_RECEIPT"),
        ),
        (
            FINAL_REFERENCE,
            replace(RECEIPT_REFERENCE, object_type="WorkPackageReceipt"),
        ),
        (replace(FINAL_REFERENCE, case_id="different-case"), RECEIPT_REFERENCE),
        (FINAL_REFERENCE, replace(RECEIPT_REFERENCE, case_id="different-case")),
        (replace(FINAL_REFERENCE, object_id=""), RECEIPT_REFERENCE),
        (FINAL_REFERENCE, replace(RECEIPT_REFERENCE, object_id="   ")),
        (
            replace(FINAL_REFERENCE, object_id=cast(str, None)),
            RECEIPT_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(RECEIPT_REFERENCE, object_id=FINAL_REFERENCE.object_id),
        ),
        (
            replace(FINAL_REFERENCE, content_hash=f"sha256:{'A' * 64}"),
            RECEIPT_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, content_hash=f"sha256:{'a' * 63}"),
            RECEIPT_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(RECEIPT_REFERENCE, content_hash=f"sha256:{'b' * 63}g"),
        ),
        (
            FINAL_REFERENCE,
            replace(RECEIPT_REFERENCE, content_hash=f"{'b' * 64}"),
        ),
        (
            replace(FINAL_REFERENCE, content_hash=cast(str, None)),
            RECEIPT_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, captured_at=cast(datetime, None)),
            RECEIPT_REFERENCE,
        ),
        (
            replace(FINAL_REFERENCE, captured_at=cast(datetime, "not-a-datetime")),
            RECEIPT_REFERENCE,
        ),
        (
            FINAL_REFERENCE,
            replace(
                RECEIPT_REFERENCE,
                captured_at=CAPTURED_AT.replace(tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_filing_receipt_archived_fails_closed_for_invalid_evidence_matrix(
    evidence_refs: object,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(evidence_refs=evidence_refs),
        WAITING_RECEIPT_PROJECTION,
        InteractionForbidden(),
    )

    assert decision is None


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="FILING_EXTERNAL_SUBMISSION_RECORDED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(
            _command(),
            confirmation_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(_command(), case_id=""),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 14, 13, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 14, 13, 5, tzinfo=timezone.utc),
        ),
    ),
)
def test_filing_receipt_archived_fails_closed_for_malformed_or_different_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, WAITING_RECEIPT_PROJECTION, InteractionForbidden()) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            WAITING_RECEIPT_PROJECTION,
            business_stage=BusinessStage.FILING_PREPARATION,
        ),
        replace(
            WAITING_RECEIPT_PROJECTION,
            official_procedure_stage=(
                OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE
            ),
        ),
        replace(
            WAITING_RECEIPT_PROJECTION,
            legal_status=LegalStatus.APPLICATION_PENDING,
        ),
        replace(
            WAITING_RECEIPT_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            WAITING_RECEIPT_PROJECTION,
            business_stage=cast(
                BusinessStage,
                BusinessStage.WAITING_EXTERNAL_RECEIPT.value,
            ),
        ),
    ),
)
def test_filing_receipt_archived_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
