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
PUBLISHED_PROJECTION = replace(
    PRELIMINARY_EXAMINATION_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.PUBLISHED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"PUBLICATION_NOTICE_RECORDED rule must not access transaction.{name}")


class StringSubclass(str):
    pass


class DatetimeSubclass(datetime):
    pass


class DictSubclass(dict[str, object]):
    pass


class CommandSubclass(LifecycleEventCommand):
    pass


class EvidenceSubclass(EvidenceReference):
    pass


class ProjectionSubclass(LifecycleProjection):
    pass


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-publication-notice",
        evidence_kind="PUBLICATION_NOTICE",
        object_type="DocumentEvidenceVersion",
        object_id="publication-notice-version-1",
        content_hash=f"sha256:{'e' * 64}",
        captured_at=datetime(2026, 7, 19, 13, 0),
    )


def _command(
    *,
    event_type: str = "PUBLICATION_NOTICE_RECORDED",
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-publication-notice",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 19, 13, 5),
        evidence_refs=(_evidence(),),
        actor_id="actor-publication-notice",
        idempotency_key="publication-notice-recorded-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={},
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


def _rule():
    return get_lifecycle_rule("PUBLICATION_NOTICE_RECORDED")


def test_registry_resolves_only_exact_publication_notice_recorded() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("publication_notice_recorded") is None
    assert get_lifecycle_rule("PUBLICATION_NOTICE_RECORDED ") is None
    assert get_lifecycle_rule(StringSubclass("PUBLICATION_NOTICE_RECORDED")) is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["PUBLICATION_NOTICE_RECORDED"]) is None


def test_publication_notice_enters_published_and_keeps_application_pending() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(),
        PRELIMINARY_EXAMINATION_PROJECTION,
        InteractionForbidden(),
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PUBLISHED_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        _command(event_type="RECTIFICATION_NOTICE_RECORDED"),
        replace(_command(), event_type=StringSubclass("PUBLICATION_NOTICE_RECORDED")),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), lane=cast(ActivityLane, StringSubclass("LIFECYCLE"))),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" case-publication-notice"),
        replace(_command(), case_id="case-publication-notice "),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id=" actor-publication-notice"),
        replace(_command(), actor_id="actor-publication-notice "),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key=" publication-notice-recorded-1"),
        replace(_command(), idempotency_key="publication-notice-recorded-1 "),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(_command(), effective_at=DatetimeSubclass(2026, 7, 19, 13, 5)),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 19, 13, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=cast(tuple[EvidenceReference, ...], [])),
        replace(_command(), evidence_refs=(_evidence(), _evidence())),
        replace(_command(), payload={"unexpected": True}),
        replace(_command(), payload=DictSubclass()),
        replace(_command(), payload=MappingProxyType({})),
        replace(_command(), payload=cast(Mapping[str, object], [])),
        replace(_command(), occurred_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 19, 13, 1, tzinfo=timezone.utc),
        ),
    ),
)
def test_publication_notice_fails_closed_for_non_exact_command(
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
        (
            EvidenceSubclass(
                case_id=_evidence().case_id,
                evidence_kind=_evidence().evidence_kind,
                object_type=_evidence().object_type,
                object_id=_evidence().object_id,
                content_hash=_evidence().content_hash,
                captured_at=_evidence().captured_at,
            ),
        ),
        (replace(_evidence(), evidence_kind="OFFICIAL_NOTICE"),),
        (replace(_evidence(), evidence_kind=StringSubclass("PUBLICATION_NOTICE")),),
        (replace(_evidence(), object_type="Document"),),
        (replace(_evidence(), object_type=StringSubclass("DocumentEvidenceVersion")),),
        (replace(_evidence(), case_id="another-case"),),
        (replace(_evidence(), object_id=""),),
        (replace(_evidence(), object_id=" publication-notice-version-1"),),
        (replace(_evidence(), object_id="publication-notice-version-1 "),),
        (replace(_evidence(), object_id="x" * 37),),
        (replace(_evidence(), content_hash=f"sha256:{'E' * 64}"),),
        (replace(_evidence(), content_hash=f"sha256:{'e' * 63}"),),
        (replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),),
        (
            replace(
                _evidence(),
                captured_at=datetime(2026, 7, 19, 13, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_publication_notice_requires_exact_confirmed_evidence(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            replace(_command(), evidence_refs=evidence_refs),
            PRELIMINARY_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        ProjectionSubclass(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.RECTIFICATION_RESPONSE,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            legal_status=LegalStatus.NOT_ESTABLISHED,
        ),
        replace(
            PRELIMINARY_EXAMINATION_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_publication_notice_rejects_non_exact_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
