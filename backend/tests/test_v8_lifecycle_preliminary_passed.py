from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone
from inspect import Parameter, signature
from types import MappingProxyType
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

PRELIMINARY_EXAMINATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"PRELIMINARY_EXAMINATION_PASSED rule must not access transaction.{name}"
        )


class EventType(str):
    pass


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-preliminary-examination-passed",
        evidence_kind="PRELIMINARY_EXAMINATION_PASS_NOTICE",
        object_type="DocumentEvidenceVersion",
        object_id="preliminary-examination-pass-notice-version-1",
        content_hash=f"sha256:{'c' * 64}",
        captured_at=datetime(2026, 7, 18, 12, 0),
    )


def _command(
    *,
    event_type: str = "PRELIMINARY_EXAMINATION_PASSED",
    occurred_at: datetime | None = None,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-preliminary-examination-passed",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 18, 12, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-preliminary-examination-passed",
        idempotency_key="preliminary-examination-passed-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
        occurred_at=occurred_at,
    )


def _rule():
    return get_lifecycle_rule("PRELIMINARY_EXAMINATION_PASSED")


def test_registry_resolves_only_exact_preliminary_examination_passed() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("preliminary_examination_passed") is None
    assert get_lifecycle_rule("PRELIMINARY_EXAMINATION_PASSED ") is None
    assert get_lifecycle_rule(EventType("PRELIMINARY_EXAMINATION_PASSED")) is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["PRELIMINARY_EXAMINATION_PASSED"]) is None


@pytest.mark.parametrize(
    "occurred_at",
    (
        None,
        datetime(2026, 7, 18, 12, 1),
    ),
)
def test_preliminary_examination_passed_records_fact_without_changing_projection(
    occurred_at: datetime | None,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(occurred_at=occurred_at),
        PRELIMINARY_EXAMINATION_PROJECTION,
        InteractionForbidden(),
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PRELIMINARY_EXAMINATION_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _command(event_type="PRELIMINARY_EXAMINATION_STARTED"),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), lane=cast(ActivityLane, "LIFECYCLE")),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), confirmation_status=cast(ConfirmationStatus, "CONFIRMED")),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" "),
        replace(_command(), case_id=" case-preliminary-examination-passed"),
        replace(_command(), case_id="case-preliminary-examination-passed "),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id=" "),
        replace(_command(), actor_id=" actor-preliminary-examination-passed"),
        replace(_command(), actor_id="actor-preliminary-examination-passed "),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key=" "),
        replace(_command(), idempotency_key=" preliminary-examination-passed-1"),
        replace(_command(), idempotency_key="preliminary-examination-passed-1 "),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 18, 12, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple, [])),
        replace(_command(), payload={"unexpected": True}),
        replace(
            _command(),
            payload=cast(Mapping[str, object], MappingProxyType({})),
        ),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 18, 12, 1, tzinfo=timezone.utc),
        ),
    ),
)
def test_preliminary_examination_passed_fails_closed_for_non_exact_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            command,
            PRELIMINARY_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "evidence_refs",
    (
        (),
        (_evidence(), _evidence()),
        cast(tuple[EvidenceReference, ...], [_evidence()]),
        (cast(EvidenceReference, object()),),
        (replace(_evidence(), evidence_kind="PRELIMINARY_EXAMINATION_SOURCE"),),
        (replace(_evidence(), object_type="Document"),),
        (replace(_evidence(), case_id="another-case"),),
        (replace(_evidence(), object_id=cast(str, 1)),),
        (replace(_evidence(), object_id=""),),
        (replace(_evidence(), object_id=" "),),
        (replace(_evidence(), object_id=" notice-version-1"),),
        (replace(_evidence(), object_id="notice-version-1 "),),
        (replace(_evidence(), content_hash=cast(str, 1)),),
        (replace(_evidence(), content_hash=f"sha256:{'C' * 64}"),),
        (replace(_evidence(), content_hash=f"sha256:{'c' * 63}"),),
        (replace(_evidence(), content_hash=f"sha256:{'c' * 65}"),),
        (replace(_evidence(), content_hash=f"sha512:{'c' * 64}"),),
        (replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),),
        (
            replace(
                _evidence(),
                captured_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_preliminary_examination_passed_requires_exact_pass_notice_evidence(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = _rule()
    assert rule is not None

    command = replace(_command(), evidence_refs=evidence_refs)

    assert (
        rule(
            command,
            PRELIMINARY_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            business_stage=cast(
                BusinessStage,
                BusinessStage.PROSECUTION_MANAGEMENT.value,
            ),
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            official_procedure_stage=cast(
                OfficialProcedureStage,
                OfficialProcedureStage.PRELIMINARY_EXAMINATION.value,
            ),
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            legal_status=LegalStatus.NOT_ESTABLISHED,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            legal_status=cast(
                LegalStatus,
                LegalStatus.APPLICATION_PENDING.value,
            ),
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            lifecycle_verification_status=cast(
                ConfirmationStatus,
                ConfirmationStatus.CONFIRMED.value,
            ),
        ),
    ),
)
def test_preliminary_examination_passed_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
