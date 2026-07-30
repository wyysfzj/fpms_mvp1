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

GRANT_REGISTRATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
PATENT_IN_FORCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
EFFECTIVE_AT = datetime(2026, 7, 23)
OCCURRED_AT = datetime(2026, 7, 23, 10, 30)
CONTENT_HASH = f"sha256:{'b' * 64}"


class InteractionForbidden:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(
            f"GRANT_ANNOUNCEMENT_CONFIRMED rule must not access transaction.{name}"
        )


class StringSubclass(str):
    pass


class CommandSubclass(LifecycleEventCommand):
    pass


class EvidenceSubclass(EvidenceReference):
    pass


class ProjectionSubclass(LifecycleProjection):
    pass


def _source_snapshot(**overrides: object) -> str:
    snapshot = {
        "schema": "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1",
        "announcement_date": "2026-07-23",
        "source_document_id": "grant-announcement-document-1",
        "source_evidence_version_id": "grant-announcement-version-1",
        "source_evidence_content_hash": CONTENT_HASH,
        "source_provenance_id": "grant-announcement-review-1",
        **overrides,
    }
    return json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _payload() -> dict[str, object]:
    snapshot = _source_snapshot()
    return {
        "schema": "FPMS_GRANT_ANNOUNCEMENT_CONFIRMED_V1",
        "case_id": "case-grant-announcement",
        "announcement_date": "2026-07-23",
        "source_document_id": "grant-announcement-document-1",
        "source_evidence_version_id": "grant-announcement-version-1",
        "source_evidence_content_hash": CONTENT_HASH,
        "source_provenance_id": "grant-announcement-review-1",
        "source_snapshot_schema": "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1",
        "source_snapshot": snapshot,
        "source_snapshot_hash": hashlib.sha256(snapshot.encode()).hexdigest(),
        "predecessor_source_snapshot_hash": None,
        "supersedes_activity_id": None,
    }


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-grant-announcement",
        evidence_kind="DOCUMENT_EVIDENCE_VERSION",
        object_type="DocumentEvidenceVersion",
        object_id="grant-announcement-version-1",
        content_hash=CONTENT_HASH,
        captured_at=EFFECTIVE_AT,
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-grant-announcement",
        event_type="GRANT_ANNOUNCEMENT_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=EFFECTIVE_AT,
        occurred_at=OCCURRED_AT,
        evidence_refs=(_evidence(),),
        actor_id="actor-grant-announcement",
        reviewer_id="reviewer-grant-announcement",
        idempotency_key="grant-announcement:announcement-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=_payload(),
    )


def _replacement_command() -> LifecycleEventCommand:
    payload = _payload()
    payload["predecessor_source_snapshot_hash"] = "a" * 64
    payload["supersedes_activity_id"] = "grant-announcement-activity-previous"
    return replace(
        _command(),
        payload=payload,
        supersedes_event_id="grant-announcement-activity-previous",
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
    return get_lifecycle_rule("GRANT_ANNOUNCEMENT_CONFIRMED")


def test_registry_resolves_only_exact_grant_announcement_confirmed() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "transaction",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_lifecycle_rule("grant_announcement_confirmed") is None
    assert get_lifecycle_rule("GRANT_ANNOUNCEMENT_CONFIRMED ") is None
    assert get_lifecycle_rule(StringSubclass("GRANT_ANNOUNCEMENT_CONFIRMED")) is None
    assert get_lifecycle_rule(None) is None


def test_controlled_announcement_enters_patent_in_force_on_announcement_date() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(),
        GRANT_REGISTRATION_PROJECTION,
        InteractionForbidden(),
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PATENT_IN_FORCE_PROJECTION,
        oa_sequence=None,
    )


def test_linked_replacement_preserves_patent_in_force_projection() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _replacement_command(),
        PATENT_IN_FORCE_PROJECTION,
        InteractionForbidden(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=PATENT_IN_FORCE_PROJECTION,
        oa_sequence=None,
    )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        replace(_command(), event_type="PATENT_REGISTER_STATUS_CONFIRMED"),
        replace(
            _command(),
            event_type=StringSubclass("GRANT_ANNOUNCEMENT_CONFIRMED"),
        ),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" case-grant-announcement"),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="actor-grant-announcement "),
        replace(_command(), reviewer_id=None),
        replace(_command(), reviewer_id=" reviewer-grant-announcement"),
        replace(_command(), reviewer_id="actor-grant-announcement"),
        replace(_command(), idempotency_key="announcement-1"),
        replace(_command(), idempotency_key="grant-announcement:"),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "2026-07-23")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        ),
        replace(_command(), occurred_at=None),
        replace(_command(), occurred_at=cast(datetime, "2026-07-23T10:30:00")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 23, 10, 30, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=()),
        replace(_command(), evidence_refs=(_evidence(), _evidence())),
        replace(_command(), payload={}),
        replace(_command(), source_activity_id="inferred-grant-registration"),
    ),
)
def test_grant_announcement_fails_closed_for_non_exact_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            command,
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("schema", "FPMS_GRANT_ANNOUNCEMENT_CONFIRMED_V2"),
        ("case_id", "another-case"),
        ("announcement_date", "2026-07-24"),
        ("announcement_date", "23-07-2026"),
        ("source_document_id", ""),
        ("source_document_id", " source-document"),
        ("source_evidence_version_id", "another-version"),
        ("source_evidence_content_hash", f"sha256:{'B' * 64}"),
        ("source_provenance_id", ""),
        ("source_provenance_id", " provenance"),
        ("source_snapshot_schema", "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V2"),
        ("source_snapshot", ""),
        ("source_snapshot_hash", "A" * 64),
        ("predecessor_source_snapshot_hash", "a" * 64),
        ("supersedes_activity_id", "unexpected-activity"),
    ),
)
def test_grant_announcement_requires_exact_payload(
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
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_grant_announcement_rejects_extra_payload_key() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["inferred_grant"] = True

    assert (
        rule(
            replace(_command(), payload=payload),
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "snapshot",
    (
        _source_snapshot(schema="FPMS_GRANT_ANNOUNCEMENT_SOURCE_V2"),
        _source_snapshot(announcement_date="2026-07-24"),
        _source_snapshot(source_document_id="another-document"),
        _source_snapshot(source_evidence_version_id="another-version"),
        _source_snapshot(source_evidence_content_hash=f"sha256:{'c' * 64}"),
        _source_snapshot(source_provenance_id="another-provenance"),
        json.dumps(json.loads(_source_snapshot()), ensure_ascii=False),
        '{"schema":"FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1","schema":"duplicate"}',
        '{"announcement_date":NaN}',
    ),
)
def test_grant_announcement_binds_canonical_source_snapshot(snapshot: str) -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["source_snapshot"] = snapshot
    payload["source_snapshot_hash"] = hashlib.sha256(snapshot.encode()).hexdigest()

    assert (
        rule(
            replace(_command(), payload=payload),
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_grant_announcement_rejects_source_snapshot_hash_mismatch() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["source_snapshot_hash"] = "0" * 64

    assert (
        rule(
            replace(_command(), payload=payload),
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "evidence",
    (
        EvidenceSubclass(
            case_id=_evidence().case_id,
            evidence_kind=_evidence().evidence_kind,
            object_type=_evidence().object_type,
            object_id=_evidence().object_id,
            content_hash=_evidence().content_hash,
            captured_at=_evidence().captured_at,
        ),
        replace(_evidence(), case_id="another-case"),
        replace(_evidence(), evidence_kind="SOURCE_DOCUMENT"),
        replace(_evidence(), object_type="Document"),
        replace(_evidence(), object_id="another-version"),
        replace(_evidence(), content_hash=f"sha256:{'c' * 64}"),
        replace(_evidence(), captured_at=datetime(2026, 7, 23, 0, 0, 1)),
        replace(
            _evidence(),
            captured_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        ),
    ),
)
def test_grant_announcement_requires_exact_effective_evidence(
    evidence: EvidenceReference,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            replace(_command(), evidence_refs=(evidence,)),
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        ProjectionSubclass(
            business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        replace(
            GRANT_REGISTRATION_PROJECTION,
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
        ),
        replace(
            GRANT_REGISTRATION_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.REEXAMINATION,
        ),
        replace(
            GRANT_REGISTRATION_PROJECTION,
            legal_status=LegalStatus.PATENT_IN_FORCE,
        ),
        replace(
            GRANT_REGISTRATION_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_initial_grant_announcement_requires_exact_grant_registration_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command(),
            previous_projection,
            InteractionForbidden(),
        )
        is None
    )


@pytest.mark.parametrize(
    "command",
    (
        replace(_replacement_command(), supersedes_event_id=None),
        replace(_replacement_command(), supersedes_event_id="other-activity"),
        replace(_replacement_command(), payload=_payload()),
    ),
)
def test_replacement_requires_complete_matching_linkage(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            command,
            PATENT_IN_FORCE_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_replacement_rejects_current_snapshot_as_predecessor() -> None:
    rule = _rule()
    assert rule is not None
    command = _replacement_command()
    payload = dict(command.payload)
    payload["predecessor_source_snapshot_hash"] = payload["source_snapshot_hash"]

    assert (
        rule(
            replace(command, payload=payload),
            PATENT_IN_FORCE_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )


def test_replacement_rejects_non_current_patent_projection() -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _replacement_command(),
            GRANT_REGISTRATION_PROJECTION,
            InteractionForbidden(),
        )
        is None
    )
