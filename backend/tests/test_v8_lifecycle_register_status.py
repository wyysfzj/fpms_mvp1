from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Iterator
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from inspect import Parameter, signature
from typing import cast, get_type_hints

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

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
from app.modules.cases.lifecycle_service import (
    LifecycleRuleDecision,
    PatentRegisterStatusRuleContext,
    apply_lifecycle_event,
)
from app.modules.cases.models import Case, CaseActivityEvent

PATENT_IN_FORCE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
    legal_status=LegalStatus.PATENT_IN_FORCE,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
PATENT_TERMINATED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.CLOSED,
    official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
    legal_status=LegalStatus.PATENT_TERMINATED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
EFFECTIVE_AT = datetime(2026, 7, 23)
OCCURRED_AT = datetime(2026, 7, 23, 11, 15)
CONTENT_HASH = f"sha256:{'c' * 64}"
REGISTER_EVENT = "PATENT_REGISTER_STATUS_CONFIRMED"
CONFLICT_CODES = ("PATENT_REGISTER_STATUS_REQUIRES_SPECIFIC_EVENT",)
INITIAL_CONTEXT = PatentRegisterStatusRuleContext(
    predecessor_event_type=None,
    predecessor_status_snapshot_hash=None,
)


@pytest.fixture(scope="module", autouse=True)
def _restore_lazy_rule_import_after_module() -> Iterator[None]:
    yield
    sys.modules.pop("app.modules.cases.lifecycle_rules", None)


class StringSubclass(str):
    pass


class CommandSubclass(LifecycleEventCommand):
    pass


class EvidenceSubclass(EvidenceReference):
    pass


class ProjectionSubclass(LifecycleProjection):
    pass


def _status_snapshot(**overrides: object) -> str:
    snapshot = {
        "schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
        "register_status": "PATENT_IN_FORCE",
        "source_document_id": "patent-register-document-1",
        "source_evidence_version_id": "patent-register-version-1",
        "source_evidence_content_hash": CONTENT_HASH,
        "source_provenance_id": "patent-register-review-1",
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
    snapshot = _status_snapshot()
    return {
        "schema": "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V1",
        "case_id": "case-patent-register",
        "register_status": "PATENT_IN_FORCE",
        "source_document_id": "patent-register-document-1",
        "source_evidence_version_id": "patent-register-version-1",
        "source_evidence_content_hash": CONTENT_HASH,
        "source_provenance_id": "patent-register-review-1",
        "status_snapshot_schema": "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1",
        "status_snapshot": snapshot,
        "status_snapshot_hash": hashlib.sha256(snapshot.encode()).hexdigest(),
        "predecessor_status_snapshot_hash": None,
        "supersedes_activity_id": None,
    }


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        case_id="case-patent-register",
        evidence_kind="DOCUMENT_EVIDENCE_VERSION",
        object_type="DocumentEvidenceVersion",
        object_id="patent-register-version-1",
        content_hash=CONTENT_HASH,
        captured_at=EFFECTIVE_AT,
    )


def _command() -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id="case-patent-register",
        event_type="PATENT_REGISTER_STATUS_CONFIRMED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=EFFECTIVE_AT,
        occurred_at=OCCURRED_AT,
        evidence_refs=(_evidence(),),
        actor_id="actor-patent-register",
        reviewer_id="reviewer-patent-register",
        idempotency_key="patent-register-status:register-1",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=_payload(),
    )


def _command_for_status(register_status: str) -> LifecycleEventCommand:
    payload = _payload()
    payload["register_status"] = register_status
    snapshot = _status_snapshot(register_status=register_status)
    payload["status_snapshot"] = snapshot
    payload["status_snapshot_hash"] = hashlib.sha256(snapshot.encode()).hexdigest()
    return replace(_command(), payload=payload)


def _replacement_command() -> LifecycleEventCommand:
    payload = _payload()
    payload["predecessor_status_snapshot_hash"] = "a" * 64
    payload["supersedes_activity_id"] = "patent-register-activity-previous"
    return replace(
        _command(),
        payload=payload,
        supersedes_event_id="patent-register-activity-previous",
    )


def _replacement_context(
    predecessor_hash: str = "a" * 64,
) -> PatentRegisterStatusRuleContext:
    return PatentRegisterStatusRuleContext(
        predecessor_event_type=REGISTER_EVENT,
        predecessor_status_snapshot_hash=predecessor_hash,
    )


def _case() -> Case:
    return Case(
        id=_command().case_id,
        case_no="NO-PATENT-REGISTER",
        status="GRANTED",
        business_stage=BusinessStage.POST_GRANT_MAINTENANCE.value,
        official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED.value,
        legal_status=LegalStatus.PATENT_IN_FORCE.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=0,
    )


def _activity_count(transaction: Session) -> int:
    return int(
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == _command().case_id)
        )
        or 0
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
    return get_lifecycle_rule("PATENT_REGISTER_STATUS_CONFIRMED")


def test_registry_resolves_exact_pure_immutable_patent_register_rule() -> None:
    rule = _rule()

    assert callable(rule)
    parameters = tuple(signature(rule).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "previous_projection",
        "context",
    )
    assert all(parameter.kind is Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)
    assert get_type_hints(rule)["context"] is PatentRegisterStatusRuleContext
    assert not hasattr(INITIAL_CONTEXT, "__dict__")
    with pytest.raises(TypeError):
        PatentRegisterStatusRuleContext(None, None)  # type: ignore[misc]
    with pytest.raises((AttributeError, FrozenInstanceError)):
        INITIAL_CONTEXT.predecessor_event_type = REGISTER_EVENT  # type: ignore[misc]
    assert get_lifecycle_rule("patent_register_status_confirmed") is None
    assert get_lifecycle_rule("PATENT_REGISTER_STATUS_CONFIRMED ") is None
    assert (
        get_lifecycle_rule(StringSubclass("PATENT_REGISTER_STATUS_CONFIRMED")) is None
    )
    assert get_lifecycle_rule(None) is None


def test_same_register_status_records_verification_without_central_change() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _command(),
        PATENT_IN_FORCE_PROJECTION,
        INITIAL_CONTEXT,
    )

    assert type(decision) is LifecycleRuleDecision
    assert decision == LifecycleRuleDecision(
        current_projection=PATENT_IN_FORCE_PROJECTION,
        oa_sequence=None,
        conflict_codes=(),
    )


@pytest.mark.parametrize(
    ("previous_projection", "register_status"),
    (
        (PATENT_IN_FORCE_PROJECTION, "PATENT_TERMINATED"),
        (PATENT_IN_FORCE_PROJECTION, "PATENT_EXPIRED"),
        (PATENT_IN_FORCE_PROJECTION, "PATENT_INVALIDATED"),
        (PATENT_TERMINATED_PROJECTION, "PATENT_IN_FORCE"),
    ),
)
def test_closed_differing_status_pairs_return_exact_non_dispatching_conflict(
    previous_projection: LifecycleProjection,
    register_status: str,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(
        _command_for_status(register_status),
        previous_projection,
        INITIAL_CONTEXT,
    ) == LifecycleRuleDecision(
        current_projection=previous_projection,
        oa_sequence=None,
        conflict_codes=CONFLICT_CODES,
    )


def test_linked_replacement_binds_context_and_preserves_same_patent_projection() -> None:
    rule = _rule()
    assert rule is not None

    decision = rule(
        _replacement_command(),
        PATENT_IN_FORCE_PROJECTION,
        _replacement_context(),
    )

    assert decision == LifecycleRuleDecision(
        current_projection=PATENT_IN_FORCE_PROJECTION,
        oa_sequence=None,
        conflict_codes=(),
    )


@pytest.mark.parametrize(
    ("previous_projection", "register_status"),
    (
        (PATENT_IN_FORCE_PROJECTION, "APPLICATION_PENDING"),
        (PATENT_TERMINATED_PROJECTION, "PATENT_TERMINATED"),
        (PATENT_TERMINATED_PROJECTION, "PATENT_EXPIRED"),
        (PATENT_TERMINATED_PROJECTION, "PATENT_INVALIDATED"),
        (
            LifecycleProjection(
                business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
                official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
                legal_status=LegalStatus.APPLICATION_PENDING,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
            ),
            "PATENT_IN_FORCE",
        ),
        (
            PATENT_IN_FORCE_PROJECTION,
            StringSubclass("PATENT_TERMINATED"),
        ),
    ),
)
def test_unsupported_status_pairs_and_string_subclasses_fail_closed(
    previous_projection: LifecycleProjection,
    register_status: str,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command_for_status(register_status),
            previous_projection,
            INITIAL_CONTEXT,
        )
        is None
    )


@pytest.mark.parametrize(
    "context",
    (
        cast(PatentRegisterStatusRuleContext, object()),
        PatentRegisterStatusRuleContext(
            predecessor_event_type="PATENT_TERMINATION_CONFIRMED",
            predecessor_status_snapshot_hash="a" * 64,
        ),
        PatentRegisterStatusRuleContext(
            predecessor_event_type=REGISTER_EVENT,
            predecessor_status_snapshot_hash="b" * 64,
        ),
        PatentRegisterStatusRuleContext(
            predecessor_event_type=REGISTER_EVENT,
            predecessor_status_snapshot_hash=None,
        ),
    ),
)
def test_replacement_rejects_wrong_context_without_interaction(
    context: PatentRegisterStatusRuleContext,
) -> None:
    rule = _rule()
    assert rule is not None

    assert rule(_replacement_command(), PATENT_IN_FORCE_PROJECTION, context) is None


def test_initial_confirmation_requires_null_context_markers() -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command(),
            PATENT_IN_FORCE_PROJECTION,
            PatentRegisterStatusRuleContext(
                predecessor_event_type=REGISTER_EVENT,
                predecessor_status_snapshot_hash="a" * 64,
            ),
        )
        is None
    )


def test_real_apply_appends_one_conflict_revision_replays_and_never_dispatches(
    session_factory: sessionmaker,
) -> None:
    command = _command_for_status("PATENT_TERMINATED")
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        first = apply_lifecycle_event(command, transaction)
        transaction.commit()
        replay = apply_lifecycle_event(command, transaction)

        assert first.reused is False
        assert replay.reused is True
        assert first.activity_id == replay.activity_id
        assert first.sequence == first.lifecycle_revision == 1
        assert replay.sequence == replay.lifecycle_revision == 1
        assert first.conflict_codes == replay.conflict_codes == CONFLICT_CODES
        assert first.previous_projection == first.current_projection
        assert replay.previous_projection == replay.current_projection
        assert first.current_projection == PATENT_IN_FORCE_PROJECTION
        assert _activity_count(transaction) == 1
        assert transaction.scalars(
            select(CaseActivityEvent.activity_type).where(
                CaseActivityEvent.case_id == command.case_id
            )
        ).all() == [REGISTER_EVENT]
        stored_case = transaction.get(Case, command.case_id)
        assert stored_case is not None
        assert stored_case.lifecycle_revision == 1
        assert stored_case.status == "GRANTED"
        assert stored_case.business_stage == BusinessStage.POST_GRANT_MAINTENANCE.value
        assert (
            stored_case.official_procedure_stage
            == OfficialProcedureStage.GRANT_ANNOUNCED.value
        )
        assert stored_case.legal_status == LegalStatus.PATENT_IN_FORCE.value
        assert (
            stored_case.lifecycle_verification_status
            == ConfirmationStatus.CONFIRMED.value
        )


@pytest.mark.parametrize(
    "command",
    (
        cast(LifecycleEventCommand, object()),
        _subclassed_command(),
        replace(_command(), event_type="PATENT_TERMINATION_CONFIRMED"),
        replace(
            _command(),
            event_type=StringSubclass("PATENT_REGISTER_STATUS_CONFIRMED"),
        ),
        replace(_command(), lane=ActivityLane.DOCUMENT),
        replace(_command(), confirmation_status=ConfirmationStatus.NEEDS_REVIEW),
        replace(_command(), case_id=""),
        replace(_command(), case_id=" case-patent-register"),
        replace(_command(), case_id="x" * 37),
        replace(_command(), actor_id=""),
        replace(_command(), actor_id="actor-patent-register "),
        replace(_command(), reviewer_id=None),
        replace(_command(), reviewer_id=" reviewer-patent-register"),
        replace(_command(), reviewer_id="actor-patent-register"),
        replace(_command(), idempotency_key="register-1"),
        replace(_command(), idempotency_key="patent-register-status:"),
        replace(_command(), idempotency_key="x" * 129),
        replace(_command(), effective_at=cast(datetime, "2026-07-23")),
        replace(
            _command(),
            effective_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        ),
        replace(_command(), occurred_at=None),
        replace(_command(), occurred_at=cast(datetime, "2026-07-23T11:15:00")),
        replace(
            _command(),
            occurred_at=datetime(2026, 7, 23, 11, 15, tzinfo=timezone.utc),
        ),
        replace(_command(), evidence_refs=()),
        replace(_command(), evidence_refs=(_evidence(), _evidence())),
        replace(_command(), payload={}),
        replace(_command(), source_activity_id="inferred-register-status"),
    ),
)
def test_patent_register_status_fails_closed_for_non_exact_command(
    command: LifecycleEventCommand,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            command,
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
        )
        is None
    )


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("schema", "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V2"),
        ("case_id", "another-case"),
        ("register_status", "APPLICATION_PENDING"),
        ("source_document_id", ""),
        ("source_document_id", " source-document"),
        ("source_evidence_version_id", "another-version"),
        ("source_evidence_content_hash", f"sha256:{'C' * 64}"),
        ("source_provenance_id", ""),
        ("source_provenance_id", " provenance"),
        ("status_snapshot_schema", "FPMS_PATENT_REGISTER_STATUS_SOURCE_V2"),
        ("status_snapshot", ""),
        ("status_snapshot_hash", "A" * 64),
        ("predecessor_status_snapshot_hash", "a" * 64),
        ("supersedes_activity_id", "unexpected-activity"),
    ),
)
def test_patent_register_status_requires_exact_payload(
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
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
        )
        is None
    )


def test_patent_register_status_rejects_extra_payload_key() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["inferred_legal_state"] = "PATENT_IN_FORCE"

    assert (
        rule(
            replace(_command(), payload=payload),
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
        )
        is None
    )


@pytest.mark.parametrize(
    "snapshot",
    (
        _status_snapshot(schema="FPMS_PATENT_REGISTER_STATUS_SOURCE_V2"),
        _status_snapshot(register_status="PATENT_TERMINATED"),
        _status_snapshot(source_document_id="another-document"),
        _status_snapshot(source_evidence_version_id="another-version"),
        _status_snapshot(source_evidence_content_hash=f"sha256:{'d' * 64}"),
        _status_snapshot(source_provenance_id="another-provenance"),
        json.dumps(json.loads(_status_snapshot()), ensure_ascii=False),
        '{"schema":"FPMS_PATENT_REGISTER_STATUS_SOURCE_V1","schema":"duplicate"}',
        '{"register_status":NaN}',
    ),
)
def test_patent_register_status_binds_canonical_status_snapshot(snapshot: str) -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["status_snapshot"] = snapshot
    payload["status_snapshot_hash"] = hashlib.sha256(snapshot.encode()).hexdigest()

    assert (
        rule(
            replace(_command(), payload=payload),
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
        )
        is None
    )


def test_patent_register_status_rejects_snapshot_hash_mismatch() -> None:
    rule = _rule()
    assert rule is not None
    payload = _payload()
    payload["status_snapshot_hash"] = "0" * 64

    assert (
        rule(
            replace(_command(), payload=payload),
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
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
        replace(_evidence(), evidence_kind="PATENT_REGISTER"),
        replace(_evidence(), object_type="Document"),
        replace(_evidence(), object_id="another-version"),
        replace(_evidence(), content_hash=f"sha256:{'d' * 64}"),
        replace(_evidence(), captured_at=datetime(2026, 7, 23, 0, 0, 1)),
        replace(
            _evidence(),
            captured_at=datetime(2026, 7, 23, tzinfo=timezone.utc),
        ),
    ),
)
def test_patent_register_status_requires_exact_effective_evidence(
    evidence: EvidenceReference,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            replace(_command(), evidence_refs=(evidence,)),
            PATENT_IN_FORCE_PROJECTION,
            INITIAL_CONTEXT,
        )
        is None
    )


@pytest.mark.parametrize(
    "previous_projection",
    (
        cast(LifecycleProjection, object()),
        ProjectionSubclass(
            business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
            official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
            legal_status=LegalStatus.PATENT_IN_FORCE,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        replace(
            PATENT_IN_FORCE_PROJECTION,
            business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
        ),
        replace(
            PATENT_IN_FORCE_PROJECTION,
            official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
        ),
        replace(
            PATENT_IN_FORCE_PROJECTION,
            legal_status=LegalStatus.PATENT_TERMINATED,
        ),
        replace(
            PATENT_IN_FORCE_PROJECTION,
            lifecycle_verification_status=ConfirmationStatus.NEEDS_REVIEW,
        ),
    ),
)
def test_patent_register_status_requires_exact_current_projection(
    previous_projection: LifecycleProjection,
) -> None:
    rule = _rule()
    assert rule is not None

    assert (
        rule(
            _command(),
            previous_projection,
            INITIAL_CONTEXT,
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
            _replacement_context(),
        )
        is None
    )


def test_replacement_rejects_current_snapshot_as_predecessor() -> None:
    rule = _rule()
    assert rule is not None
    command = _replacement_command()
    payload = dict(command.payload)
    payload["predecessor_status_snapshot_hash"] = payload["status_snapshot_hash"]

    assert (
        rule(
            replace(command, payload=payload),
            PATENT_IN_FORCE_PROJECTION,
            _replacement_context(cast(str, payload["predecessor_status_snapshot_hash"])),
        )
        is None
    )
