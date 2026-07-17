from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from importlib import import_module, util
from inspect import Parameter, signature
from typing import cast

import pytest
from sqlalchemy import event, func, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence

CASE_A = "case-lifecycle-a"
CASE_B = "case-lifecycle-b"
ACTOR_ID = "actor-lifecycle"
EFFECTIVE_AT = datetime(2026, 7, 13, 9, 30)
CAPTURED_AT = datetime(2026, 7, 13, 9, 25)
SERVICE_MODULE = "app.modules.cases.lifecycle_activity_service"
SERVICE_SPEC = util.find_spec(SERVICE_MODULE)

EMPTY_PROJECTION = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=None,
    lifecycle_verification_status=None,
)
OPEN_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.NEW_CASE,
    official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
    legal_status=LegalStatus.NOT_ESTABLISHED,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
FILING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.FILING_PREPARATION,
    official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
LEGACY_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    legal_status=LegalStatus.UNKNOWN,
    lifecycle_verification_status=ConfirmationStatus.LEGACY_UNVERIFIED,
)


def _value(value: object) -> object:
    return value.value if hasattr(value, "value") else value


def _case(
    *,
    case_id: str = CASE_A,
    projection: LifecycleProjection = EMPTY_PROJECTION,
    status: str = "NOT_FILED",
    revision: int | None = None,
) -> Case:
    return Case(
        id=case_id,
        case_no=f"NO-{case_id}",
        status=status,
        business_stage=_value(projection.business_stage),
        official_procedure_stage=_value(projection.official_procedure_stage),
        legal_status=_value(projection.legal_status),
        lifecycle_verification_status=_value(projection.lifecycle_verification_status),
        lifecycle_revision=revision,
    )


def _evidence(
    *,
    case_id: str = CASE_A,
    evidence_kind: str = "DOCUMENT",
    object_type: str = "Document",
    object_id: str = "document-a",
    content_hash: str = "sha256:document-a",
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
    *,
    case_id: str = CASE_A,
    event_type: str = "CASE_OPENED",
    lane: ActivityLane = ActivityLane.LIFECYCLE,
    evidence_refs: tuple[EvidenceReference, ...] | None = None,
    idempotency_key: str = "case-opened-1",
    confirmation_status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
    payload: Mapping[str, object] | None = None,
    effective_at: datetime = EFFECTIVE_AT,
    occurred_at: datetime | None = None,
    source_activity_id: str | None = None,
    supersedes_event_id: str | None = None,
) -> LifecycleEventCommand:
    if evidence_refs is None:
        evidence_refs = (
            _evidence(),
            _evidence(
                evidence_kind="TASK",
                object_type="Task",
                object_id="task-a",
                content_hash="sha256:task-a",
                captured_at=datetime(2026, 7, 13, 9, 26),
            ),
        )
    if payload is None:
        payload = {"label": "首次", "nested": {"b": 2, "a": 1}}
    return LifecycleEventCommand(
        case_id=case_id,
        event_type=event_type,
        lane=lane,
        effective_at=effective_at,
        evidence_refs=evidence_refs,
        actor_id=ACTOR_ID,
        idempotency_key=idempotency_key,
        confirmation_status=confirmation_status,
        payload=payload,
        occurred_at=occurred_at,
        source_activity_id=source_activity_id,
        supersedes_event_id=supersedes_event_id,
    )


def _append(
    transaction: Session,
    command: LifecycleEventCommand,
    *,
    previous_projection: LifecycleProjection = EMPTY_PROJECTION,
    current_projection: LifecycleProjection = OPEN_PROJECTION,
    legacy_case_status: str = "OPEN",
    conflict_codes: tuple[str, ...] = (),
) -> LifecycleTransitionResult:
    if SERVICE_SPEC is None:
        pytest.skip("append_case_activity service is the intentional RED")
    append_case_activity = import_module(SERVICE_MODULE).append_case_activity
    return append_case_activity(
        command,
        transaction,
        previous_projection=previous_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=conflict_codes,
    )


def _expect_error(
    expected_code: str,
    expected_status: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    error = captured.value
    assert error.code == expected_code
    assert error.status_code == expected_status
    return error


def _counts(transaction: Session, case_id: str = CASE_A) -> tuple[int, int]:
    activity_count = transaction.scalar(
        select(func.count())
        .select_from(CaseActivityEvent)
        .where(CaseActivityEvent.case_id == case_id)
    )
    evidence_count = transaction.scalar(
        select(func.count())
        .select_from(CaseActivityEventEvidence)
        .where(CaseActivityEventEvidence.case_id == case_id)
    )
    return int(activity_count or 0), int(evidence_count or 0)


def _case_state(transaction: Session, case_id: str = CASE_A) -> tuple[object, ...]:
    case = transaction.get(Case, case_id)
    assert case is not None
    return (
        case.business_stage,
        case.official_procedure_stage,
        case.legal_status,
        case.lifecycle_verification_status,
        case.lifecycle_revision,
        case.status,
    )


def _seed_activity(
    transaction: Session,
    *,
    activity_id: str,
    case_id: str,
    sequence: int,
    idempotency_key: str,
) -> CaseActivityEvent:
    activity = CaseActivityEvent(
        id=activity_id,
        case_id=case_id,
        sequence=sequence,
        lane=ActivityLane.LIFECYCLE.value,
        activity_type="SEEDED_ACTIVITY",
        effective_at=EFFECTIVE_AT,
        confirmation_status=ConfirmationStatus.CONFIRMED.value,
        old_business_stage=OPEN_PROJECTION.business_stage.value,
        new_business_stage=OPEN_PROJECTION.business_stage.value,
        old_official_procedure_stage=(OPEN_PROJECTION.official_procedure_stage.value),
        new_official_procedure_stage=(OPEN_PROJECTION.official_procedure_stage.value),
        old_legal_status=OPEN_PROJECTION.legal_status.value,
        new_legal_status=OPEN_PROJECTION.legal_status.value,
        actor_id=ACTOR_ID,
        idempotency_key=idempotency_key,
        payload_json="{}",
    )
    transaction.add(activity)
    return activity


def _assert_no_pending_lifecycle_rows(transaction: Session) -> None:
    assert not any(
        isinstance(row, (CaseActivityEvent, CaseActivityEventEvidence)) for row in transaction.new
    )


def test_service_exposes_the_exact_frozen_public_callable() -> None:
    assert SERVICE_SPEC is not None, (
        "missing frozen behavior: lifecycle_activity_service.py must expose append_case_activity()"
    )
    append_case_activity = import_module(SERVICE_MODULE).append_case_activity
    parameters = tuple(signature(append_case_activity).parameters.values())

    assert tuple(parameter.name for parameter in parameters) == (
        "command",
        "transaction",
        "previous_projection",
        "current_projection",
        "legacy_case_status",
        "conflict_codes",
    )
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.KEYWORD_ONLY,
        Parameter.KEYWORD_ONLY,
        Parameter.KEYWORD_ONLY,
        Parameter.KEYWORD_ONLY,
    )
    assert parameters[-1].default == ()


def test_append_allocates_global_sequence_replays_read_only_and_obeys_caller_rollback(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        first_command = _command()
        first = _append(transaction, first_command)

        assert first.case_id == CASE_A
        assert first.sequence == first.lifecycle_revision == 1
        assert first.lane is ActivityLane.LIFECYCLE
        assert first.event_type == "CASE_OPENED"
        assert first.confirmation_status is ConfirmationStatus.CONFIRMED
        assert first.previous_projection == EMPTY_PROJECTION
        assert first.current_projection == OPEN_PROJECTION
        assert first.legacy_case_status == "OPEN"
        assert first.idempotency_key == first_command.idempotency_key
        assert first.conflict_codes == ()
        assert first.reused is False
        assert _case_state(transaction) == (
            BusinessStage.NEW_CASE.value,
            OfficialProcedureStage.NOT_SUBMITTED.value,
            LegalStatus.NOT_ESTABLISHED.value,
            ConfirmationStatus.CONFIRMED.value,
            1,
            "OPEN",
        )

        activities = transaction.scalars(
            select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
        ).all()
        assert len(activities) == 1
        assert activities[0].id == first.activity_id
        assert activities[0].payload_json == ('{"label":"首次","nested":{"a":1,"b":2}}')
        links = transaction.scalars(
            select(CaseActivityEventEvidence).order_by(
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
            )
        ).all()
        assert [
            (
                link.activity_id,
                link.evidence_kind,
                link.object_type,
                link.object_id,
                link.content_hash,
                link.captured_at,
            )
            for link in links
        ] == [
            (
                first.activity_id,
                "DOCUMENT",
                "Document",
                "document-a",
                "sha256:document-a",
                CAPTURED_AT,
            ),
            (
                first.activity_id,
                "TASK",
                "Task",
                "task-a",
                "sha256:task-a",
                datetime(2026, 7, 13, 9, 26),
            ),
        ]

        with session_factory() as observer:
            assert _counts(observer) == (0, 0)
            assert _case_state(observer) == (None, None, None, None, None, "NOT_FILED")

        second_command = _command(
            event_type="DOCUMENT_CAPTURED",
            lane=ActivityLane.DOCUMENT,
            evidence_refs=(),
            idempotency_key="document-captured-2",
            payload={"document_id": "document-b"},
        )
        second = _append(
            transaction,
            second_command,
            previous_projection=OPEN_PROJECTION,
            current_projection=OPEN_PROJECTION,
            legacy_case_status="OPEN",
        )
        assert second.sequence == second.lifecycle_revision == 2
        assert second.lane is ActivityLane.DOCUMENT
        assert _counts(transaction) == (2, 2)
        assert _case_state(transaction)[4:] == (2, "OPEN")

        flushes: list[None] = []

        def record_flush(*_args: object) -> None:
            flushes.append(None)

        event.listen(transaction, "before_flush", record_flush)
        try:
            replay = _append(
                transaction,
                replace(
                    first_command,
                    evidence_refs=tuple(reversed(first_command.evidence_refs)),
                ),
            )
        finally:
            event.remove(transaction, "before_flush", record_flush)

        assert replay.activity_id == first.activity_id
        assert replay.sequence == replay.lifecycle_revision == 1
        assert replay.reused is True
        assert replay.previous_projection == EMPTY_PROJECTION
        assert replay.current_projection == OPEN_PROJECTION
        assert _counts(transaction) == (2, 2)
        assert _case_state(transaction)[4:] == (2, "OPEN")
        assert flushes == []

        transaction.rollback()

    with session_factory() as observer:
        assert _counts(observer) == (0, 0)
        assert _case_state(observer) == (None, None, None, None, None, "NOT_FILED")


def test_append_reads_persisted_case_state_and_discards_dirty_service_fields_after_cas(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        target = transaction.get(Case, CASE_A)
        assert target is not None
        target.business_stage = BusinessStage.CLOSED.value
        target.official_procedure_stage = OfficialProcedureStage.PROCEDURE_CLOSED.value
        target.legal_status = LegalStatus.PATENT_TERMINATED.value
        target.lifecycle_verification_status = ConfirmationStatus.NEEDS_REVIEW.value
        target.lifecycle_revision = 99
        target.status = "DIRTY_CALLER_VALUE"

        result = _append(transaction, _command(evidence_refs=()))

        assert result.sequence == 1
        assert (
            target.business_stage,
            target.official_procedure_stage,
            target.legal_status,
            target.lifecycle_verification_status,
            target.lifecycle_revision,
            target.status,
        ) == (
            BusinessStage.NEW_CASE.value,
            OfficialProcedureStage.NOT_SUBMITTED.value,
            LegalStatus.NOT_ESTABLISHED.value,
            ConfirmationStatus.CONFIRMED.value,
            1,
            "OPEN",
        )
        assert _counts(transaction) == (1, 0)


def test_validation_failure_preserves_preloaded_dirty_case_state(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        target = transaction.get(Case, CASE_A)
        assert target is not None
        target.business_stage = BusinessStage.NEW_CASE.value
        target.official_procedure_stage = OfficialProcedureStage.NOT_SUBMITTED.value
        target.legal_status = LegalStatus.NOT_ESTABLISHED.value
        target.lifecycle_verification_status = ConfirmationStatus.CONFIRMED.value
        target.lifecycle_revision = 99
        target.status = "DIRTY_CALLER_VALUE"

        _expect_error(
            "LIFECYCLE_PROJECTION_CONFLICT",
            409,
            lambda: _append(
                transaction,
                _command(
                    lane=ActivityLane.DOCUMENT,
                    event_type="DIRTY_CASE_REPLAY",
                    evidence_refs=(),
                ),
                previous_projection=OPEN_PROJECTION,
                current_projection=OPEN_PROJECTION,
                legacy_case_status="DIRTY_CALLER_VALUE",
            ),
        )

        assert (
            target.business_stage,
            target.official_procedure_stage,
            target.legal_status,
            target.lifecycle_verification_status,
            target.lifecycle_revision,
            target.status,
        ) == (
            BusinessStage.NEW_CASE.value,
            OfficialProcedureStage.NOT_SUBMITTED.value,
            LegalStatus.NOT_ESTABLISHED.value,
            ConfirmationStatus.CONFIRMED.value,
            99,
            "DIRTY_CALLER_VALUE",
        )
        assert _counts(transaction) == (0, 0)


def test_replay_compares_persisted_activity_and_evidence_not_dirty_identity_map_facts(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        command = _command()
        original = _append(transaction, command)
        transaction.commit()

        activity = transaction.get(CaseActivityEvent, original.activity_id)
        evidence = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == original.activity_id
            )
        )
        assert activity is not None
        assert evidence is not None
        activity.payload_json = '{"dirty":true}'
        evidence.content_hash = "sha256:dirty-caller-value"

        replay = _append(transaction, command)

        assert replay.reused is True
        assert replay.activity_id == original.activity_id
        assert replay.sequence == 1
        assert activity.payload_json == '{"dirty":true}'
        assert evidence.content_hash == "sha256:dirty-caller-value"
        assert activity in transaction.dirty
        assert evidence in transaction.dirty
        assert _counts(transaction) == (1, 2)


@pytest.mark.parametrize(
    "mutation",
    (
        "payload",
        "event_fact",
        "evidence_set",
        "evidence_hash",
        "evidence_time",
        "old_axis",
        "new_axis",
    ),
)
def test_same_key_with_any_canonical_identity_change_is_a_read_only_conflict(
    session_factory: sessionmaker,
    mutation: str,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        original = _command()
        _append(transaction, original)
        transaction.commit()

        changed = original
        previous_projection = EMPTY_PROJECTION
        current_projection = OPEN_PROJECTION
        if mutation == "payload":
            changed = replace(original, payload={"label": "changed"})
        elif mutation == "event_fact":
            changed = replace(original, event_type="CASE_REOPENED")
        elif mutation == "evidence_set":
            changed = replace(original, evidence_refs=original.evidence_refs[:1])
        elif mutation == "evidence_hash":
            changed = replace(
                original,
                evidence_refs=(
                    replace(original.evidence_refs[0], content_hash="sha256:changed"),
                    original.evidence_refs[1],
                ),
            )
        elif mutation == "evidence_time":
            changed = replace(
                original,
                evidence_refs=(
                    replace(
                        original.evidence_refs[0],
                        captured_at=datetime(2026, 7, 13, 9, 24),
                    ),
                    original.evidence_refs[1],
                ),
            )
        elif mutation == "old_axis":
            previous_projection = replace(
                EMPTY_PROJECTION,
                business_stage=BusinessStage.NEW_CASE,
            )
        elif mutation == "new_axis":
            current_projection = replace(
                OPEN_PROJECTION,
                legal_status=LegalStatus.APPLICATION_PENDING,
            )

        before = (_counts(transaction), _case_state(transaction))
        _expect_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _append(
                transaction,
                changed,
                previous_projection=previous_projection,
                current_projection=current_projection,
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    ("reference_field", "reference_kind", "expected_code"),
    (
        (
            "source_activity_id",
            "missing",
            "LIFECYCLE_SOURCE_ACTIVITY_NOT_FOUND",
        ),
        (
            "source_activity_id",
            "cross_case",
            "LIFECYCLE_SOURCE_ACTIVITY_CASE_MISMATCH",
        ),
        (
            "supersedes_event_id",
            "missing",
            "LIFECYCLE_SUPERSEDED_ACTIVITY_NOT_FOUND",
        ),
        (
            "supersedes_event_id",
            "cross_case",
            "LIFECYCLE_SUPERSEDED_ACTIVITY_CASE_MISMATCH",
        ),
    ),
)
def test_missing_and_cross_case_activity_references_fail_without_mutation(
    session_factory: sessionmaker,
    reference_field: str,
    reference_kind: str,
    expected_code: str,
) -> None:
    with session_factory() as transaction:
        transaction.add_all(
            (
                _case(
                    case_id=CASE_A,
                    projection=OPEN_PROJECTION,
                    status="OPEN",
                    revision=1,
                ),
                _case(
                    case_id=CASE_B,
                    projection=OPEN_PROJECTION,
                    status="OPEN",
                    revision=1,
                ),
            )
        )
        _seed_activity(
            transaction,
            activity_id="activity-a-1",
            case_id=CASE_A,
            sequence=1,
            idempotency_key="seed-a-1",
        )
        _seed_activity(
            transaction,
            activity_id="activity-b-1",
            case_id=CASE_B,
            sequence=1,
            idempotency_key="seed-b-1",
        )
        transaction.commit()

        reference = "missing-activity" if reference_kind == "missing" else "activity-b-1"
        command = _command(
            event_type="DOCUMENT_CORRECTED",
            lane=ActivityLane.DOCUMENT,
            evidence_refs=(),
            idempotency_key=f"{reference_field}-{reference_kind}",
        )
        command = replace(command, **{reference_field: reference})
        before = (_counts(transaction), _case_state(transaction))

        _expect_error(
            expected_code,
            409,
            lambda: _append(
                transaction,
                command,
                previous_projection=OPEN_PROJECTION,
                current_projection=OPEN_PROJECTION,
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


def test_same_prior_activity_may_be_both_source_and_superseded_reference(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(
            _case(
                projection=OPEN_PROJECTION,
                status="OPEN",
                revision=1,
            )
        )
        _seed_activity(
            transaction,
            activity_id="activity-a-1",
            case_id=CASE_A,
            sequence=1,
            idempotency_key="seed-a-1",
        )
        transaction.commit()

        result = _append(
            transaction,
            _command(
                event_type="DOCUMENT_CORRECTED",
                lane=ActivityLane.DOCUMENT,
                evidence_refs=(),
                idempotency_key="document-correction-2",
                source_activity_id="activity-a-1",
                supersedes_event_id="activity-a-1",
            ),
            previous_projection=OPEN_PROJECTION,
            current_projection=OPEN_PROJECTION,
        )
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        assert result.sequence == 2
        assert activity.source_activity_id == "activity-a-1"
        assert activity.supersedes_event_id == "activity-a-1"


def test_wrong_case_and_duplicate_evidence_fail_with_exact_codes_and_no_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(
            _case(
                projection=OPEN_PROJECTION,
                status="OPEN",
            )
        )
        transaction.commit()
        before = (_counts(transaction), _case_state(transaction))

        wrong_case = _command(
            lane=ActivityLane.DOCUMENT,
            event_type="DOCUMENT_CAPTURED",
            idempotency_key="wrong-case-evidence",
            evidence_refs=(_evidence(case_id=CASE_B),),
        )
        _expect_error(
            "LIFECYCLE_EVIDENCE_CASE_MISMATCH",
            409,
            lambda: _append(
                transaction,
                wrong_case,
                previous_projection=OPEN_PROJECTION,
                current_projection=OPEN_PROJECTION,
            ),
        )

        repeated = _evidence()
        duplicate = _command(
            lane=ActivityLane.DOCUMENT,
            event_type="DOCUMENT_CAPTURED",
            idempotency_key="duplicate-evidence",
            evidence_refs=(
                repeated,
                replace(repeated, content_hash="sha256:different"),
            ),
        )
        _expect_error(
            "LIFECYCLE_EVIDENCE_DUPLICATE",
            400,
            lambda: _append(
                transaction,
                duplicate,
                previous_projection=OPEN_PROJECTION,
                current_projection=OPEN_PROJECTION,
            ),
        )

        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    "invalid_shape",
    (
        "command_type",
        "projection_type",
        "lane_enum",
        "empty_actor",
        "long_event_type",
        "empty_legacy_status",
        "unsorted_conflicts",
        "duplicate_conflicts",
    ),
)
def test_general_shape_validation_precedes_case_lookup(
    session_factory: sessionmaker,
    invalid_shape: str,
) -> None:
    command = _command(case_id="missing-case", evidence_refs=())
    previous_projection = EMPTY_PROJECTION
    legacy_case_status = "OPEN"
    conflict_codes: tuple[str, ...] = ()
    if invalid_shape == "command_type":
        command = cast(LifecycleEventCommand, object())
    elif invalid_shape == "projection_type":
        previous_projection = cast(LifecycleProjection, object())
    elif invalid_shape == "lane_enum":
        command = replace(command, lane=cast(ActivityLane, "LIFECYCLE"))
    elif invalid_shape == "empty_actor":
        command = replace(command, actor_id="")
    elif invalid_shape == "long_event_type":
        command = replace(command, event_type="x" * 65)
    elif invalid_shape == "empty_legacy_status":
        legacy_case_status = ""
    elif invalid_shape == "unsorted_conflicts":
        conflict_codes = ("Z_CONFLICT", "A_CONFLICT")
    elif invalid_shape == "duplicate_conflicts":
        conflict_codes = ("A_CONFLICT", "A_CONFLICT")

    with session_factory() as transaction:
        error = _expect_error(
            "LIFECYCLE_ACTIVITY_INVALID",
            400,
            lambda: _append(
                transaction,
                command,
                previous_projection=previous_projection,
                conflict_codes=conflict_codes,
                legacy_case_status=legacy_case_status,
            ),
        )
        assert error.details is not None
        assert isinstance(error.details.get("field"), str)
        assert _counts(transaction, "missing-case") == (0, 0)
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    "invalid_payload",
    (
        "aware_effective_at",
        "aware_occurred_at",
        "non_string_key",
        "non_json_value",
        "nan",
        "infinity",
        "non_object",
        "cyclic_mapping",
    ),
)
def test_timestamp_and_payload_validation_is_exact_and_precedes_case_lookup(
    session_factory: sessionmaker,
    invalid_payload: str,
) -> None:
    command = _command(case_id="missing-case", evidence_refs=())
    if invalid_payload == "aware_effective_at":
        command = replace(command, effective_at=EFFECTIVE_AT.replace(tzinfo=timezone.utc))
    elif invalid_payload == "aware_occurred_at":
        command = replace(command, occurred_at=EFFECTIVE_AT.replace(tzinfo=timezone.utc))
    elif invalid_payload == "non_string_key":
        command = replace(
            command,
            payload=cast(Mapping[str, object], {1: "not-canonical"}),
        )
    elif invalid_payload == "non_json_value":
        command = replace(command, payload={"value": object()})
    elif invalid_payload == "nan":
        command = replace(command, payload={"value": float("nan")})
    elif invalid_payload == "infinity":
        command = replace(command, payload={"value": float("inf")})
    elif invalid_payload == "non_object":
        command = replace(
            command,
            payload=cast(Mapping[str, object], ["not", "an", "object"]),
        )
    elif invalid_payload == "cyclic_mapping":
        cyclic_payload: dict[str, object] = {}
        cyclic_payload["self"] = cyclic_payload
        command = replace(command, payload=cyclic_payload)

    with session_factory() as transaction:
        _expect_error(
            "LIFECYCLE_PAYLOAD_INVALID",
            400,
            lambda: _append(transaction, command),
        )
        assert _counts(transaction, "missing-case") == (0, 0)
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    "invalid_evidence",
    (
        "empty_case_id",
        "long_object_id",
        "empty_kind",
        "long_object_type",
        "long_hash",
        "aware_captured_at",
        "reference_type",
    ),
)
def test_evidence_shape_validation_is_exact_and_precedes_case_lookup(
    session_factory: sessionmaker,
    invalid_evidence: str,
) -> None:
    reference = _evidence(case_id="missing-case")
    if invalid_evidence == "empty_case_id":
        reference = replace(reference, case_id="")
    elif invalid_evidence == "long_object_id":
        reference = replace(reference, object_id="x" * 37)
    elif invalid_evidence == "empty_kind":
        reference = replace(reference, evidence_kind="")
    elif invalid_evidence == "long_object_type":
        reference = replace(reference, object_type="x" * 65)
    elif invalid_evidence == "long_hash":
        reference = replace(reference, content_hash="x" * 129)
    elif invalid_evidence == "aware_captured_at":
        reference = replace(
            reference,
            captured_at=CAPTURED_AT.replace(tzinfo=timezone.utc),
        )
    elif invalid_evidence == "reference_type":
        reference = cast(EvidenceReference, object())

    command = _command(
        case_id="missing-case",
        evidence_refs=(reference,),
    )
    with session_factory() as transaction:
        _expect_error(
            "LIFECYCLE_EVIDENCE_INVALID",
            400,
            lambda: _append(transaction, command),
        )
        assert _counts(transaction, "missing-case") == (0, 0)
        _assert_no_pending_lifecycle_rows(transaction)


def test_missing_case_uses_exact_404_without_any_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _expect_error(
            "CASE_NOT_FOUND",
            404,
            lambda: _append(
                transaction,
                _command(case_id="missing-case", evidence_refs=()),
            ),
        )
        assert _counts(transaction, "missing-case") == (0, 0)
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    ("lane", "confirmation_status", "conflict_codes"),
    (
        (ActivityLane.DOCUMENT, ConfirmationStatus.CONFIRMED, ()),
        (ActivityLane.FEE, ConfirmationStatus.CONFIRMED, ()),
        (ActivityLane.LIFECYCLE, ConfirmationStatus.NEEDS_REVIEW, ()),
        (ActivityLane.DOCUMENT, ConfirmationStatus.CONFIRMED, ("NON_BLOCKING",)),
    ),
)
def test_non_central_lanes_and_needs_review_cannot_change_central_state(
    session_factory: sessionmaker,
    lane: ActivityLane,
    confirmation_status: ConfirmationStatus,
    conflict_codes: tuple[str, ...],
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        before = (_counts(transaction), _case_state(transaction))
        command = _command(
            lane=lane,
            confirmation_status=confirmation_status,
            evidence_refs=(),
            idempotency_key=f"center-change-{lane.value}-{confirmation_status.value}",
        )

        _expect_error(
            "LIFECYCLE_CENTER_CHANGE_NOT_ALLOWED",
            409,
            lambda: _append(
                transaction,
                command,
                conflict_codes=conflict_codes,
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


def test_legacy_import_initializes_only_a_null_unverified_projection(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()

        imported = _append(
            transaction,
            _command(
                event_type="LEGACY_IMPORT",
                confirmation_status=ConfirmationStatus.LEGACY_UNVERIFIED,
                evidence_refs=(),
                idempotency_key="legacy-import-1",
            ),
            current_projection=LEGACY_PROJECTION,
            legacy_case_status="LEGACY",
        )
        assert imported.sequence == 1
        assert imported.current_projection == LEGACY_PROJECTION
        assert imported.confirmation_status is ConfirmationStatus.LEGACY_UNVERIFIED
        transaction.commit()

        before = (_counts(transaction), _case_state(transaction))
        _expect_error(
            "LIFECYCLE_CENTER_CHANGE_NOT_ALLOWED",
            409,
            lambda: _append(
                transaction,
                _command(
                    event_type="LEGACY_IMPORT",
                    confirmation_status=ConfirmationStatus.LEGACY_UNVERIFIED,
                    evidence_refs=(),
                    idempotency_key="legacy-import-2",
                ),
                previous_projection=LEGACY_PROJECTION,
                current_projection=replace(
                    LEGACY_PROJECTION,
                    legal_status=LegalStatus.APPLICATION_PENDING,
                ),
                legacy_case_status="LEGACY_CHANGED",
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    "projection_conflict",
    ("stale_previous", "unknown_stored_code"),
)
def test_stale_or_invalid_stored_projection_fails_without_mutation(
    session_factory: sessionmaker,
    projection_conflict: str,
) -> None:
    stored_projection = OPEN_PROJECTION
    previous_projection = EMPTY_PROJECTION
    case = _case(projection=stored_projection, status="OPEN", revision=0)
    if projection_conflict == "unknown_stored_code":
        case.business_stage = "UNKNOWN_STORED_STAGE"
        previous_projection = OPEN_PROJECTION

    with session_factory() as transaction:
        transaction.add(case)
        transaction.commit()
        before = (_counts(transaction), _case_state(transaction))

        _expect_error(
            "LIFECYCLE_PROJECTION_CONFLICT",
            409,
            lambda: _append(
                transaction,
                _command(evidence_refs=()),
                previous_projection=previous_projection,
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


@pytest.mark.parametrize(
    ("revision", "activity_sequences"),
    (
        (-1, ()),
        (2, (1,)),
        (0, (1,)),
    ),
)
def test_revision_and_activity_sequence_drift_fail_without_mutation(
    session_factory: sessionmaker,
    revision: int,
    activity_sequences: tuple[int, ...],
) -> None:
    with session_factory() as transaction:
        transaction.add(
            _case(
                projection=OPEN_PROJECTION,
                status="OPEN",
                revision=revision,
            )
        )
        for sequence in activity_sequences:
            _seed_activity(
                transaction,
                activity_id=f"activity-{sequence}",
                case_id=CASE_A,
                sequence=sequence,
                idempotency_key=f"seed-{sequence}",
            )
        transaction.commit()
        before = (_counts(transaction), _case_state(transaction))

        _expect_error(
            "LIFECYCLE_REVISION_CONFLICT",
            409,
            lambda: _append(
                transaction,
                _command(
                    lane=ActivityLane.DOCUMENT,
                    event_type="DOCUMENT_CAPTURED",
                    evidence_refs=(),
                    idempotency_key="revision-drift",
                ),
                previous_projection=OPEN_PROJECTION,
                current_projection=OPEN_PROJECTION,
            ),
        )
        assert (_counts(transaction), _case_state(transaction)) == before
        _assert_no_pending_lifecycle_rows(transaction)


def test_compare_and_swap_loss_uses_exact_conflict_and_leaves_no_pending_write(
    session_factory: sessionmaker,
) -> None:
    trigger_name = "test_ignore_lifecycle_revision_update"
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.commit()
        transaction.execute(
            text(
                f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE OF lifecycle_revision ON t_case
                BEGIN
                    SELECT RAISE(IGNORE);
                END
                """
            )
        )
        transaction.commit()

        try:
            before = (_counts(transaction), _case_state(transaction))
            _expect_error(
                "LIFECYCLE_CONCURRENCY_CONFLICT",
                409,
                lambda: _append(transaction, _command(evidence_refs=())),
            )
            assert (_counts(transaction), _case_state(transaction)) == before
            _assert_no_pending_lifecycle_rows(transaction)
        finally:
            transaction.rollback()
            transaction.execute(text(f"DROP TRIGGER IF EXISTS {trigger_name}"))
            transaction.commit()
