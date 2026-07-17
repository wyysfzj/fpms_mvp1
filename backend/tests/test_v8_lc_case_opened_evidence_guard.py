from datetime import datetime, timezone
from typing import cast

import pytest

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    EvidenceReference,
    LifecycleEventCommand,
    LifecycleProjection,
)
from app.modules.cases.lifecycle_rules import get_lifecycle_rule

CASE_ID = "case-lifecycle-opened"
CAPTURED_AT = datetime(2026, 7, 15, 9, 59)
CONTENT_HASH = f"sha256:{'a' * 64}"


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"CASE_OPENED rule must not access transaction.{name}")


def _evidence(
    *,
    case_id: str = CASE_ID,
    evidence_kind: str = "CASE_RECORD",
    object_type: str = "Case",
    object_id: str = CASE_ID,
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


def _command(
    evidence_refs: object = (_evidence(),),
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=CASE_ID,
        event_type="CASE_OPENED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 15, 10, 0),
        evidence_refs=cast(tuple[EvidenceReference, ...], evidence_refs),
        actor_id="actor-lifecycle-opened",
        idempotency_key="case-opened-evidence-guard-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
    )


def _empty_projection() -> LifecycleProjection:
    return LifecycleProjection(
        business_stage=None,
        official_procedure_stage=None,
        legal_status=None,
        lifecycle_verification_status=None,
    )


def test_case_opened_rejects_tuple_without_exact_case_record_reference() -> None:
    rule = get_lifecycle_rule("CASE_OPENED")
    command = _command(
        (
            _evidence(
                evidence_kind="DOCUMENT",
            ),
        )
    )

    assert rule is not None
    decision = rule(command, _empty_projection(), InteractionForbidden())

    assert decision is None


VALID_AND_EXTRA = (
    _evidence(),
    _evidence(
        evidence_kind="DOCUMENT",
        object_type="Document",
        object_id="document-extra",
    ),
)


@pytest.mark.parametrize(
    "evidence_refs",
    (
        None,
        [],
        (),
        (_evidence(object_id="case-record-a"), _evidence(object_id="case-record-b")),
        VALID_AND_EXTRA,
        tuple(reversed(VALID_AND_EXTRA)),
        (_evidence(), _evidence()),
        (_evidence(object_type="Document"),),
        (_evidence(case_id="different-case"),),
        (_evidence(object_id=""),),
        (_evidence(object_id="   "),),
        (_evidence(content_hash=f"sha256:{'A' * 64}"),),
        (_evidence(content_hash=f"sha256:{'a' * 63}"),),
        (_evidence(content_hash=f"sha256:{'a' * 63}g"),),
        (_evidence(content_hash=f"{'a' * 64}"),),
        (_evidence(captured_at=cast(datetime, None)),),
        (_evidence(captured_at=CAPTURED_AT.replace(tzinfo=timezone.utc)),),
        (cast(EvidenceReference, object()),),
    ),
)
def test_case_opened_fails_closed_for_invalid_evidence_matrix(
    evidence_refs: object,
) -> None:
    rule = get_lifecycle_rule("CASE_OPENED")
    assert rule is not None

    decision = rule(
        _command(evidence_refs),
        _empty_projection(),
        InteractionForbidden(),
    )

    assert decision is None
