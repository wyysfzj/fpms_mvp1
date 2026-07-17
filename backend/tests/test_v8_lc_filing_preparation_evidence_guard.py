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

CASE_ID = "case-filing-preparation"
CAPTURED_AT = datetime(2026, 7, 15, 9, 59)
CONTENT_HASH = f"sha256:{'a' * 64}"
OPEN_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.NEW_CASE,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
FILING_PREPARATION_PROJECTION = replace(
    OPEN_PROJECTION,
    business_stage=BusinessStage.FILING_PREPARATION,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"FILING_PREPARATION_STARTED rule must not access transaction.{name}")


class OtherEvidenceReference(EvidenceReference):
    pass


def _evidence(
    *,
    case_id: str = CASE_ID,
    evidence_kind: str = "FILING_WORK_PACKAGE",
    object_type: str = "OfficialWorkPackage",
    object_id: str = "work-package-1",
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


def _command(evidence_refs: object = (_evidence(),)) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type="FILING_PREPARATION_STARTED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 15, 10, 0),
        evidence_refs=cast(tuple[EvidenceReference, ...], evidence_refs),
        actor_id="actor-filing-preparation",
        idempotency_key="filing-preparation-evidence-guard-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def test_filing_preparation_rejects_tuple_without_exact_work_package_reference() -> None:
    rule = get_lifecycle_rule("FILING_PREPARATION_STARTED")
    command = _command((_evidence(evidence_kind="DOCUMENT"),))

    assert rule is not None
    decision = rule(command, OPEN_PROJECTION, InteractionForbidden())

    assert decision is None


def test_filing_preparation_accepts_exact_work_package_reference_deterministically() -> None:
    rule = get_lifecycle_rule("FILING_PREPARATION_STARTED")
    command = _command()
    assert rule is not None

    first_decision = rule(command, OPEN_PROJECTION, InteractionForbidden())
    second_decision = rule(command, OPEN_PROJECTION, InteractionForbidden())

    expected = LifecycleRuleDecision(
        current_projection=FILING_PREPARATION_PROJECTION,
        oa_sequence=None,
    )
    assert type(first_decision) is LifecycleRuleDecision
    assert first_decision == expected
    assert second_decision == expected


VALID_AND_EXTRA = (
    _evidence(),
    _evidence(
        evidence_kind="DOCUMENT",
        object_type="Document",
        object_id="document-extra",
    ),
)
SUBCLASS_REFERENCE = OtherEvidenceReference(
    case_id=CASE_ID,
    evidence_kind="FILING_WORK_PACKAGE",
    object_type="OfficialWorkPackage",
    object_id="work-package-subclass",
    content_hash=CONTENT_HASH,
    captured_at=CAPTURED_AT,
)


@pytest.mark.parametrize(
    "evidence_refs",
    (
        None,
        [],
        (),
        (
            _evidence(object_id="work-package-a"),
            _evidence(object_id="work-package-b"),
        ),
        VALID_AND_EXTRA,
        tuple(reversed(VALID_AND_EXTRA)),
        (_evidence(), _evidence()),
        (_evidence(object_type="Document"),),
        (_evidence(case_id="different-case"),),
        (_evidence(object_id=""),),
        (_evidence(object_id="   "),),
        (_evidence(object_id=cast(str, None)),),
        (_evidence(content_hash=f"sha256:{'A' * 64}"),),
        (_evidence(content_hash=f"sha256:{'a' * 63}"),),
        (_evidence(content_hash=f"sha256:{'a' * 63}g"),),
        (_evidence(content_hash=f"{'a' * 64}"),),
        (_evidence(content_hash=f"sha256:{'a' * 64} "),),
        (_evidence(content_hash=cast(str, None)),),
        (_evidence(captured_at=cast(datetime, None)),),
        (_evidence(captured_at=cast(datetime, "not-a-datetime")),),
        (_evidence(captured_at=CAPTURED_AT.replace(tzinfo=timezone.utc)),),
        (SUBCLASS_REFERENCE,),
        (cast(EvidenceReference, object()),),
    ),
)
def test_filing_preparation_fails_closed_for_invalid_evidence_matrix(
    evidence_refs: object,
) -> None:
    rule = get_lifecycle_rule("FILING_PREPARATION_STARTED")
    assert rule is not None

    decision = rule(
        _command(evidence_refs),
        OPEN_PROJECTION,
        InteractionForbidden(),
    )

    assert decision is None
