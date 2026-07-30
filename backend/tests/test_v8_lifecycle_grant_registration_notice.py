from __future__ import annotations

import hashlib
import json
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

SUBSTANTIVE_EXAMINATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
REEXAMINATION_PROJECTION = replace(
    SUBSTANTIVE_EXAMINATION_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.REEXAMINATION,
)
GRANT_REGISTRATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
REVIEWED_AT = datetime(2026, 7, 23, 17, 0)
CONTENT_HASH = f"sha256:{'a' * 64}"


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            "GRANT_REGISTRATION_NOTICE_RECORDED rule must not access "
            f"transaction.{name}"
        )


class StringSubclass(str):
    pass


class CommandSubclass(LifecycleEventCommand):
    pass


def _fee_snapshot(**overrides: object) -> str:
    payload = {
        "schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
        "source_document_id": "grant-notice-document-1",
        "reviewed_evidence_version_id": "grant-notice-version-1",
        "reviewed_evidence_content_hash": CONTENT_HASH,
        "lines": [
            {
                "fee_name": "授权当年年费",
                "year": 1,
                "amount": "900.00",
                "reduction_ratio": "0.85",
            }
        ],
        **overrides,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _payload() -> dict[str, object]:
    snapshot = _fee_snapshot()
    return {
        "schema": "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1",
        "case_id": "case-grant-registration",
        "grant_fee_task_id": "grant-fee-task-1",
        "source_document_id": "grant-notice-document-1",
        "reviewed_evidence_version_id": "grant-notice-version-1",
        "reviewed_evidence_content_hash": CONTENT_HASH,
        "reviewed_at": REVIEWED_AT.isoformat(),
        "grant_fee_lines_schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
        "grant_fee_lines_snapshot": snapshot,
        "grant_fee_lines_snapshot_hash": hashlib.sha256(snapshot.encode()).hexdigest(),
        "due_date": "2026-09-23",
        "deadline_source": "GRANT_NOTICE",
        "deadline_confirmed_at": datetime(2026, 7, 23, 16, 55).isoformat(),
        "predecessor_grant_fee_task_id": None,
        "supersedes_activity_id": None,
    }


def _evidence_refs() -> tuple[EvidenceReference, EvidenceReference]:
    return (
        EvidenceReference(
            case_id="case-grant-registration",
            evidence_kind="SOURCE_DOCUMENT",
            object_type="Document",
            object_id="grant-notice-document-1",
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        ),
        EvidenceReference(
            case_id="case-grant-registration",
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id="grant-notice-version-1",
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        ),
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-grant-registration",
        event_type="GRANT_REGISTRATION_NOTICE_RECORDED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 23, 17, 5),
        occurred_at=datetime(2026, 7, 23, 17, 5),
        evidence_refs=_evidence_refs(),
        actor_id="actor-grant-registration",
        reviewer_id="reviewer-grant-registration",
        idempotency_key="grant-registration-notice:notice-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=_payload(),
    )


def _subclassed_command() -> LifecycleEventCommand:
    command = _command()
    return CommandSubclass(
        case_id=command.case_id,
        event_type=command.event_type,
        lane=command.lane,
        effective_at=command.effective_at,
        occurred_at=command.occurred_at,
        evidence_refs=command.evidence_refs,
        actor_id=command.actor_id,
        reviewer_id=command.reviewer_id,
        idempotency_key=command.idempotency_key,
        confirmation_status=command.confirmation_status,
        payload=command.payload,
    )


def _rule():
    return get_lifecycle_rule("GRANT_REGISTRATION_NOTICE_RECORDED")


def test_registry_resolves_only_exact_grant_registration_notice_recorded() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("grant_registration_notice_recorded") is None
    assert get_lifecycle_rule("GRANT_REGISTRATION_NOTICE_RECORDED ") is None
    assert (
        get_lifecycle_rule(StringSubclass("GRANT_REGISTRATION_NOTICE_RECORDED"))
        is None
    )
    assert get_lifecycle_rule(None) is None


@pytest.mark.parametrize(
    "previous_projection",
    (
        replace(
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        ),
        SUBSTANTIVE_EXAMINATION_PROJECTION,
        REEXAMINATION_PROJECTION,
    ),
)
def test_grant_notice_enters_registration_and_keeps_application_pending(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(_command(), previous_projection, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=GRANT_REGISTRATION_PROJECTION,
        oa_sequence=None,
    )


def test_grant_notice_correction_keeps_registration_projection() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["predecessor_grant_fee_task_id"] = "grant-fee-task-previous"
    payload["supersedes_activity_id"] = "grant-activity-previous"
    command = replace(
        _command(),
        payload=payload,
        supersedes_event_id="grant-activity-previous",
    )

    decision = rule(command, GRANT_REGISTRATION_PROJECTION, InteractionForbidden())

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=GRANT_REGISTRATION_PROJECTION,
        oa_sequence=None,
    )


def test_grant_notice_rejects_replacement_task_self_cycle() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["predecessor_grant_fee_task_id"] = payload["grant_fee_task_id"]
    payload["supersedes_activity_id"] = "grant-activity-previous"
    command = replace(
        _command(),
        payload=payload,
        supersedes_event_id="grant-activity-previous",
    )

    assert (
        rule(command, GRANT_REGISTRATION_PROJECTION, InteractionForbidden())
        is None
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        replace(_command(), event_type="GRANT_ANNOUNCEMENT_CONFIRMED"),
        replace(
            _command(),
            event_type=StringSubclass("GRANT_REGISTRATION_NOTICE_RECORDED"),
        ),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" case-grant-registration"),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="actor-grant-registration "),
        replace(_command(), reviewer_id=None),
        replace(_command(), reviewer_id=" reviewer-grant-registration"),
        replace(_command(), idempotency_key=""),
        replace(_command(), idempotency_key="notice-1"),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "not-a-datetime")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 23, 17, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), occurred_at=None),
        replace(_command(), occurred_at=datetime(2026, 7, 23, 17, 4)),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 23, 17, 5, tzinfo=timezone.utc),
        ),
        replace(_command(), source_activity_id="unexpected-source"),
    ),
)
def test_grant_notice_fails_closed_for_non_exact_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(command, SUBSTANTIVE_EXAMINATION_PROJECTION, InteractionForbidden())
        is None
    )


@pytest.mark.parametrize(
    "evidence_refs",
    (
        (),
        (_evidence_refs()[0],),
        tuple(reversed(_evidence_refs())),
        (_evidence_refs()[0], _evidence_refs()[1], _evidence_refs()[1]),
        (replace(_evidence_refs()[0], case_id="another-case"), _evidence_refs()[1]),
        (
            replace(_evidence_refs()[0], evidence_kind="OFFICIAL_NOTICE"),
            _evidence_refs()[1],
        ),
        (
            replace(_evidence_refs()[1], object_type="Document"),
            _evidence_refs()[0],
        ),
        (replace(_evidence_refs()[0], object_id=""), _evidence_refs()[1]),
        (
            _evidence_refs()[0],
            replace(_evidence_refs()[1], content_hash=f"sha256:{'A' * 64}"),
        ),
        (
            _evidence_refs()[0],
            replace(
                _evidence_refs()[1],
                captured_at=datetime(2026, 7, 23, 17, tzinfo=timezone.utc),
            ),
        ),
    ),
)
def test_grant_notice_requires_exact_reviewed_source_evidence(
    evidence_refs: tuple[EvidenceReference, ...],
) -> None:
    rule = _rule()
    assert rule is not None

    command = replace(_command(), evidence_refs=evidence_refs)

    assert (
        rule(command, SUBSTANTIVE_EXAMINATION_PROJECTION, InteractionForbidden())
        is None
    )


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("schema", "FPMS_GRANT_NOTICE_V1"),
        ("case_id", "another-case"),
        ("grant_fee_task_id", ""),
        ("source_document_id", "another-document"),
        ("reviewed_evidence_version_id", "another-version"),
        ("reviewed_evidence_content_hash", f"sha256:{'A' * 64}"),
        ("reviewed_at", "2026-07-23T17:00:00+00:00"),
        ("grant_fee_lines_schema", "FPMS_GRANT_NOTICE_FEE_LINES_V2"),
        ("grant_fee_lines_snapshot", ""),
        ("grant_fee_lines_snapshot_hash", "B" * 64),
        ("due_date", "2026/09/23"),
        ("deadline_source", ""),
        ("deadline_confirmed_at", "2026-07-23T16:55:00+00:00"),
        ("predecessor_grant_fee_task_id", "unexpected-predecessor"),
        ("supersedes_activity_id", "unexpected-activity"),
    ),
)
def test_grant_notice_rejects_payload_that_conflicts_with_reviewed_notice(
    key: str,
    value: object,
) -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload[key] = value

    assert (
        rule(
            replace(_command(), payload=payload),
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_grant_notice_rejects_missing_or_extra_payload_field() -> None:
    rule = _rule()
    assert rule is not None
    missing = _payload()
    missing.pop("due_date")
    extra = {**_payload(), "fee_amount": "1000.00"}

    assert (
        rule(
            replace(_command(), payload=missing),
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )
    assert (
        rule(
            replace(_command(), payload=extra),
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "snapshot",
    (
        "{",
        json.dumps(json.loads(_fee_snapshot()), ensure_ascii=False),
        _fee_snapshot(schema="FPMS_GRANT_NOTICE_FEE_LINES_V2"),
        _fee_snapshot(source_document_id="another-document"),
        _fee_snapshot(reviewed_evidence_version_id="another-version"),
        _fee_snapshot(reviewed_evidence_content_hash=f"sha256:{'b' * 64}"),
        _fee_snapshot(lines=[]),
        _fee_snapshot(
            lines=[
                {
                    "fee_name": "授权当年年费",
                    "year": 1,
                    "amount": "900",
                    "reduction_ratio": "0.85",
                }
            ]
        ),
    ),
)
def test_grant_notice_rejects_malformed_or_unbound_fee_snapshot(
    snapshot: str,
) -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["grant_fee_lines_snapshot"] = snapshot
    payload["grant_fee_lines_snapshot_hash"] = hashlib.sha256(snapshot.encode()).hexdigest()

    assert (
        rule(
            replace(_command(), payload=payload),
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_grant_notice_rejects_fee_snapshot_hash_mismatch() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["grant_fee_lines_snapshot_hash"] = "0" * 64

    assert (
        rule(
            replace(_command(), payload=payload),
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        replace(
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
        ),
        replace(
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.PUBLISHED,
        ),
        replace(
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            legal_status=LegalStatus.PATENT_IN_FORCE,
        ),
        replace(
            SUBSTANTIVE_EXAMINATION_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_grant_notice_rejects_other_prior_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_command(), previous_projection, InteractionForbidden()) is None
