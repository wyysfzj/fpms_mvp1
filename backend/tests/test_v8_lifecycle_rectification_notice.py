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
RECTIFICATION_RESPONSE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.RECTIFICATION_RESPONSE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"RECTIFICATION_NOTICE_RECORDED rule must not access transaction.{name}"
        )


class StringSubclass(str):
    pass


class DatetimeSubclass(datetime):
    pass


class DictSubclass(dict[str, object]):
    pass


class TupleSubclass(tuple[EvidenceReference, ...]):
    pass


class CommandSubclass(LifecycleEventCommand):
    pass


class EvidenceSubclass(EvidenceReference):
    pass


class ProjectionSubclass(LifecycleProjection):
    pass


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-rectification-notice",
        evidence_kind="RECTIFICATION_NOTICE",
        object_type="DocumentEvidenceVersion",
        object_id="rectification-notice-version-1",
        content_hash=f"sha256:{'d' * 64}",
        captured_at=datetime(2026, 7, 18, 13, 0),
    )


def _payload(
    *,
    due_date: object = "2026-06-30",
    source: object = "MANUAL_OFFICIAL_NOTICE",
    status: object = "CONFIRMED",
) -> dict[str, object]:
    return {
        "official_due_date": due_date,
        "official_due_date_source": source,
        "official_due_date_status": status,
    }


def _command(
    *,
    event_type: str = "RECTIFICATION_NOTICE_RECORDED",
    occurred_at: datetime | None = None,
    payload: Mapping[str, object] | None = None,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-rectification-notice",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 18, 13, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-rectification-notice",
        idempotency_key="rectification-notice-recorded-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=_payload() if payload is None else payload,
        occurred_at=occurred_at,
    )


def _subclassed_command() -> LifecycleEventCommand:
    command = _command()
    return CommandSubclass(
        case_id=command.case_id,
        event_type=command.event_type,
        lane=command.lane,
        effective_at=command.effective_at,
        evidence_refs=command.evidence_refs,
        actor_id=command.actor_id,
        idempotency_key=command.idempotency_key,
        confirmation_status=command.confirmation_status,
        payload=command.payload,
        occurred_at=command.occurred_at,
    )


def _subclassed_evidence() -> EvidenceReference:
    evidence = _evidence()
    return EvidenceSubclass(
        case_id=evidence.case_id,
        evidence_kind=evidence.evidence_kind,
        object_type=evidence.object_type,
        object_id=evidence.object_id,
        content_hash=evidence.content_hash,
        captured_at=evidence.captured_at,
    )


def _subclassed_projection() -> LifecycleProjection:
    projection = PRELIMINARY_EXAMINATION_PROJECTION
    return ProjectionSubclass(
        business_stage=projection.business_stage,
        official_procedure_stage=projection.official_procedure_stage,
        legal_status=projection.legal_status,
        lifecycle_verification_status=projection.lifecycle_verification_status,
    )


def _rule():
    return get_lifecycle_rule("RECTIFICATION_NOTICE_RECORDED")


def test_registry_resolves_only_exact_rectification_notice_recorded() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("rectification_notice_recorded") is None
    assert get_lifecycle_rule("RECTIFICATION_NOTICE_RECORDED ") is None
    assert get_lifecycle_rule(StringSubclass("RECTIFICATION_NOTICE_RECORDED")) is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["RECTIFICATION_NOTICE_RECORDED"]) is None


@pytest.mark.parametrize(
    ("source", "occurred_at"),
    (
        ("MANUAL_OFFICIAL_NOTICE", None),
        ("MANUAL_OFFICIAL_NOTICE", datetime(2026, 7, 18, 12, 55)),
        ("IMPORTED_OFFICIAL_NOTICE", None),
        ("IMPORTED_OFFICIAL_NOTICE", datetime(2026, 7, 18, 12, 55)),
    ),
)
def test_rectification_notice_records_confirmed_deadline_and_exact_transition(
    source: str,
    occurred_at: datetime | None,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(
            occurred_at=occurred_at,
            payload=_payload(source=source),
        ),
        PRELIMINARY_EXAMINATION_PROJECTION,
        InteractionForbidden(),
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=RECTIFICATION_RESPONSE_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        _command(event_type="PRELIMINARY_EXAMINATION_PASSED"),
        replace(_command(), event_type=StringSubclass("RECTIFICATION_NOTICE_RECORDED")),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), lane=cast(ActivityLane, StringSubclass("LIFECYCLE"))),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(
            _command(),
            confirmation_status=cast(
                ConfirmationStatus,
                StringSubclass("CONFIRMED"),
            ),
        ),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" "),
        replace(_command(), case_id=" case-rectification-notice"),
        replace(_command(), case_id="case-rectification-notice "),
        replace(_command(), case_id="x" * 37),
        replace(_command(), case_id=StringSubclass("case-rectification-notice")),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id=" "),
        replace(_command(), actor_id=" actor-rectification-notice"),
        replace(_command(), actor_id="actor-rectification-notice "),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), actor_id=StringSubclass("actor-rectification-notice")),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key=" "),
        replace(_command(), idempotency_key=" rectification-notice-recorded-1"),
        replace(_command(), idempotency_key="rectification-notice-recorded-1 "),
        replace(_command(), idempotency_key="x" * 129),
        replace(
            _command(),
            idempotency_key=StringSubclass("rectification-notice-recorded-1"),
        ),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=DatetimeSubclass(2026, 7, 18, 13, 5),
        ),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 18, 13, 5, tzinfo=timezone.utc),
        ),
        replace(
            _command(),
            evidence_refs=cast(
                tuple[EvidenceReference, ...],
                TupleSubclass((_evidence(),)),
            ),
        ),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=DatetimeSubclass(2026, 7, 18, 12, 55),
        ),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 18, 12, 55, tzinfo=timezone.utc),
        ),
    ),
)
def test_rectification_notice_fails_closed_for_non_exact_command(
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
        (_subclassed_evidence(),),
        (replace(_evidence(), evidence_kind="OFFICIAL_NOTICE"),),
        (
            replace(
                _evidence(),
                evidence_kind=StringSubclass("RECTIFICATION_NOTICE"),
            ),
        ),
        (replace(_evidence(), object_type="Document"),),
        (
            replace(
                _evidence(),
                object_type=StringSubclass("DocumentEvidenceVersion"),
            ),
        ),
        (replace(_evidence(), case_id="another-case"),),
        (
            replace(
                _evidence(),
                case_id=StringSubclass("case-rectification-notice"),
            ),
        ),
        (replace(_evidence(), object_id=cast(str, 1)),),
        (replace(_evidence(), object_id=""),),
        (replace(_evidence(), object_id=" "),),
        (replace(_evidence(), object_id=" rectification-notice-version-1"),),
        (replace(_evidence(), object_id="rectification-notice-version-1 "),),
        (replace(_evidence(), object_id="x" * 37),),
        (
            replace(
                _evidence(),
                object_id=StringSubclass("rectification-notice-version-1"),
            ),
        ),
        (replace(_evidence(), content_hash=cast(str, 1)),),
        (replace(_evidence(), content_hash=f"sha256:{'D' * 64}"),),
        (replace(_evidence(), content_hash=f"sha256:{'d' * 63}"),),
        (replace(_evidence(), content_hash=f"sha256:{'d' * 65}"),),
        (replace(_evidence(), content_hash=f"sha512:{'d' * 64}"),),
        (
            replace(
                _evidence(),
                content_hash=StringSubclass(f"sha256:{'d' * 64}"),
            ),
        ),
        (replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),),
        (
            replace(
                _evidence(),
                captured_at=DatetimeSubclass(2026, 7, 18, 13, 0),
            ),
        ),
        (
            replace(
                _evidence(),
                captured_at=datetime(2026, 7, 18, 13, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_rectification_notice_requires_exact_notice_evidence(
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
    "payload",
    (
        {},
        {
            "official_due_date": "2026-06-30",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
        },
        {
            **_payload(),
            "unexpected": True,
        },
        {
            StringSubclass("official_due_date"): "2026-06-30",
            StringSubclass("official_due_date_source"): "MANUAL_OFFICIAL_NOTICE",
            StringSubclass("official_due_date_status"): "CONFIRMED",
        },
        DictSubclass(_payload()),
        MappingProxyType(_payload()),
        cast(Mapping[str, object], []),
        _payload(due_date=cast(str, 20260630)),
        _payload(due_date=StringSubclass("2026-06-30")),
        _payload(due_date="2026-6-30"),
        _payload(due_date="2026-06-30 "),
        _payload(due_date="2026-02-30"),
        _payload(due_date="2026-06-30T00:00:00"),
        _payload(source="OFFICIAL_NOTICE"),
        _payload(source=StringSubclass("MANUAL_OFFICIAL_NOTICE")),
        _payload(status="NEEDS_REVIEW"),
        _payload(status=StringSubclass("CONFIRMED")),
    ),
)
def test_rectification_notice_requires_exact_confirmed_deadline_payload(
    payload: Mapping[str, object],
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command(payload=payload),
            PRELIMINARY_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        _subclassed_projection(),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            business_stage=cast(
                BusinessStage,
                StringSubclass("PROSECUTION_MANAGEMENT"),
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
                StringSubclass("PRELIMINARY_EXAMINATION"),
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
                StringSubclass("APPLICATION_PENDING"),
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
                StringSubclass("CONFIRMED"),
            ),
        ),
    ),
)
def test_rectification_notice_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
