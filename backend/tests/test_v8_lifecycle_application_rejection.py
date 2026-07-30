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

PENDING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
REEXAMINATION_PROJECTION = replace(
    PENDING_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.REEXAMINATION,
)
REJECTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.CLOSED,
    official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
    legal_status=LegalStatus.APPLICATION_REJECTED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"APPLICATION_REJECTION_CONFIRMED rule must not access transaction.{name}"
        )


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


def _evidence(
    *,
    evidence_kind: str = "REJECTION_DECISION",
) -> EvidenceReference:
    return EvidenceReference(
        case_id="case-application-rejection",
        evidence_kind=evidence_kind,
        object_type="DocumentEvidenceVersion",
        object_id="application-rejection-source-1",
        content_hash=f"sha256:{'a' * 64}",
        captured_at=datetime(2026, 7, 25, 9, 0),
    )


def _command(
    *,
    evidence_kind: str = "REJECTION_DECISION",
    event_type: str = "APPLICATION_REJECTION_CONFIRMED",
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-application-rejection",
        event_type=event_type,
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 25, 9, 5),
        evidence_refs=(_evidence(evidence_kind=evidence_kind),),
        actor_id="actor-application-rejection",
        idempotency_key="application-rejection-confirmed-1",
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
    return get_lifecycle_rule("APPLICATION_REJECTION_CONFIRMED")


def test_registry_resolves_only_exact_application_rejection_confirmed() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("application_rejection_confirmed") is None
    assert get_lifecycle_rule("APPLICATION_REJECTION_CONFIRMED ") is None
    assert get_lifecycle_rule(StringSubclass("APPLICATION_REJECTION_CONFIRMED")) is None
    assert get_lifecycle_rule(None) is None
    assert get_lifecycle_rule(["APPLICATION_REJECTION_CONFIRMED"]) is None


@pytest.mark.parametrize(
    ("business_stage", "official_procedure_stage"),
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
        (BusinessStage.OA_REPLY_IN_PROGRESS, OfficialProcedureStage.RECTIFICATION_RESPONSE),
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
def test_rejection_decision_closes_each_coherent_pending_application(
    business_stage: BusinessStage,
    official_procedure_stage: OfficialProcedureStage,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(),
        replace(
            PENDING_PROJECTION,
            business_stage=business_stage,
            official_procedure_stage=official_procedure_stage,
        ),
        InteractionForbidden(),
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=REJECTED_PROJECTION,
        oa_sequence=None,
    )


def test_reexamination_final_rejection_closes_pending_reexamination() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(evidence_kind="REEXAMINATION_FINAL_REJECTION_DECISION"),
        REEXAMINATION_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=REJECTED_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        _command(event_type="REEXAMINATION_STARTED"),
        replace(
            _command(),
            event_type=StringSubclass("APPLICATION_REJECTION_CONFIRMED"),
        ),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), lane=cast(ActivityLane, StringSubclass("LIFECYCLE"))),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" case-application-rejection"),
        replace(_command(), case_id="case-application-rejection "),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id=" actor-application-rejection"),
        replace(_command(), actor_id="actor-application-rejection "),
        replace(_command(), actor_id="x" * 37),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key=" application-rejection-confirmed-1"),
        replace(_command(), idempotency_key="application-rejection-confirmed-1 "),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(_command(), effective_at=DatetimeSubclass(2026, 7, 25, 9, 5)),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 25, 9, 5, tzinfo=timezone.utc),
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
            occurred_at=datetime(2026, 7, 25, 9, 1, tzinfo=timezone.utc),
        ),
    ),
)
def test_application_rejection_fails_closed_for_non_exact_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(command, PENDING_PROJECTION, InteractionForbidden()) is None


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
        (replace(_evidence(), evidence_kind=StringSubclass("REJECTION_DECISION")),),
        (replace(_evidence(), object_type="Document"),),
        (replace(_evidence(), object_type=StringSubclass("DocumentEvidenceVersion")),),
        (replace(_evidence(), case_id="another-case"),),
        (replace(_evidence(), object_id=""),),
        (replace(_evidence(), object_id=" application-rejection-source-1"),),
        (replace(_evidence(), object_id="application-rejection-source-1 "),),
        (replace(_evidence(), object_id="x" * 37),),
        (replace(_evidence(), content_hash=f"sha256:{'A' * 64}"),),
        (replace(_evidence(), content_hash=f"sha256:{'a' * 63}"),),
        (replace(_evidence(), captured_at=cast(datetime, "not-a-datetime")),),
        (
            replace(
                _evidence(),
                captured_at=datetime(2026, 7, 25, 9, 0, tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_application_rejection_requires_exact_effective_decision_evidence(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            replace(_command(), evidence_refs=evidence_refs),
            PENDING_PROJECTION,
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
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        replace(PENDING_PROJECTION, business_stage=BusinessStage.NEW_CASE),
        replace(PENDING_PROJECTION, business_stage=None),
        replace(PENDING_PROJECTION, official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED),
        replace(PENDING_PROJECTION, official_procedure_stage=None),
        replace(
            PENDING_PROJECTION,
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
        ),
        LifecycleProjection(
            business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        replace(PENDING_PROJECTION, legal_status=LegalStatus.APPLICATION_REJECTED),
        replace(
            PENDING_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_application_rejection_requires_confirmed_pending_application(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None


def test_reexamination_final_rejection_requires_reexamination_predecessor() -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command(evidence_kind="REEXAMINATION_FINAL_REJECTION_DECISION"),
            PENDING_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )
