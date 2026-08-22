from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.dml import Update

from app.core.errors import BusinessError
from app.modules.cases import lifecycle_projection
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.evidence_service import (
    EvidenceReviewDecision,
    ReviewEvidenceVersionCommand,
    ReviewEvidenceVersionResult,
    SwitchCurrentEvidenceVersionCommand,
    review_evidence_version,
    switch_current_evidence_version,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion

REVIEWED_AT = datetime(2026, 7, 13, 14, 30)
LINEAGE_KEY = "filing-main"
CONTENT_HASH = f"sha256:{'a' * 64}"


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _seed_case(transaction: Session, *, case_id: str = _id(1)) -> Case:
    case = Case(
        id=case_id,
        case_no=f"CASE-{case_id[-12:]}",
        status="ACCEPTED",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.ACCEPTED.value,
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=0,
    )
    transaction.add(case)
    transaction.flush()
    return case


def _seed_version(
    transaction: Session,
    *,
    case_id: str = _id(1),
    version_id: str = _id(2),
    ordinal: int = 1,
    creator_id: str = _id(800),
    state: str = EvidenceVersionState.DRAFT.value,
    review_state: str = EvidenceReviewState.PENDING.value,
    reviewer_id: str | None = None,
    reviewed_at: datetime | None = None,
    is_current: bool = True,
) -> DocumentEvidenceVersion:
    version_seed = int(version_id[-12:])
    document_id = _id(100_000 + version_seed * 2)
    attachment_id = _id(100_001 + version_seed * 2)
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"version-{ordinal}.docx",
            file_path=f"/evidence/version-{ordinal}.docx",
        )
    )
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=version_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=LINEAGE_KEY,
        role=EvidenceRole.FILING_FULL_WORD.value,
        version_number=ordinal,
        state=state,
        creator_id=creator_id,
        review_state=review_state,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
        final_submitted_at=None,
        content_hash=CONTENT_HASH,
        current_identity_key=f"{case_id}|{LINEAGE_KEY}" if is_current else None,
    )
    transaction.add(version)
    transaction.flush()
    return version


def _seed_fixture(
    transaction: Session,
    *,
    case_id: str = _id(1),
    version_id: str = _id(2),
    state: str = EvidenceVersionState.DRAFT.value,
    review_state: str = EvidenceReviewState.PENDING.value,
    reviewer_id: str | None = None,
    reviewed_at: datetime | None = None,
    is_current: bool = True,
) -> tuple[Case, DocumentEvidenceVersion]:
    case = _seed_case(transaction, case_id=case_id)
    version = _seed_version(
        transaction,
        case_id=case_id,
        version_id=version_id,
        state=state,
        review_state=review_state,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
        is_current=is_current,
    )
    transaction.commit()
    return case, version


def _command(
    *,
    case_id: str = _id(1),
    version_id: str = _id(2),
    reviewer_id: str = _id(900),
    decision: EvidenceReviewDecision = EvidenceReviewDecision.APPROVE,
    reviewed_at: datetime = REVIEWED_AT,
    idempotency_key: str = "review-1",
) -> ReviewEvidenceVersionCommand:
    return ReviewEvidenceVersionCommand(
        case_id=case_id,
        evidence_version_id=version_id,
        reviewer_id=reviewer_id,
        decision=decision,
        reviewed_at=reviewed_at,
        idempotency_key=idempotency_key,
    )


def _assert_error(
    code: str,
    status: int,
    callable_: object,
) -> BusinessError:
    with pytest.raises(BusinessError) as exc_info:
        callable_()  # type: ignore[operator]
    error = exc_info.value
    assert (error.code, error.status_code) == (code, status)
    return error


def _counts(transaction: Session) -> tuple[int, int]:
    return (
        len(transaction.scalars(select(CaseActivityEvent)).all()),
        len(transaction.scalars(select(CaseActivityEventEvidence)).all()),
    )


def _version_snapshot(version: DocumentEvidenceVersion) -> tuple[object, ...]:
    return (
        version.case_id,
        version.document_id,
        version.attachment_id,
        version.lineage_key,
        version.role,
        version.version_number,
        version.state,
        version.creator_id,
        version.final_submitted_at,
        version.content_hash,
        version.current_identity_key,
    )


def test_public_contract_is_exact_frozen_slotted_and_keyword_only() -> None:
    assert issubclass(EvidenceReviewDecision, str)
    assert issubclass(EvidenceReviewDecision, Enum)
    assert tuple((member.name, member.value) for member in EvidenceReviewDecision) == (
        ("APPROVE", "APPROVE"),
        ("REJECT", "REJECT"),
    )

    expected_command_fields = (
        ("case_id", str),
        ("evidence_version_id", str),
        ("reviewer_id", str),
        ("decision", EvidenceReviewDecision),
        ("reviewed_at", datetime),
        ("idempotency_key", str),
    )
    expected_result_fields = (
        ("case_id", str),
        ("evidence_version_id", str),
        ("creator_id", str),
        ("reviewer_id", str),
        ("decision", EvidenceReviewDecision),
        ("review_state", EvidenceReviewState),
        ("reviewed_at", datetime),
        ("activity_id", str),
        ("activity_sequence", int),
        ("lifecycle_revision", int),
        ("idempotency_key", str),
        ("reused", bool),
    )
    for data_type, expected_fields in (
        (ReviewEvidenceVersionCommand, expected_command_fields),
        (ReviewEvidenceVersionResult, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(data_type).parameters.values()
        )

    signature = inspect.signature(review_evidence_version)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(review_evidence_version)["return"] is ReviewEvidenceVersionResult


@pytest.mark.parametrize(
    ("decision", "expected_state"),
    (
        (EvidenceReviewDecision.APPROVE, EvidenceReviewState.APPROVED),
        (EvidenceReviewDecision.REJECT, EvidenceReviewState.REJECTED),
    ),
)
def test_decision_updates_only_review_tuple_and_appends_exact_document_activity(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    decision: EvidenceReviewDecision,
    expected_state: EvidenceReviewState,
) -> None:
    case_id = _id(10 if decision is EvidenceReviewDecision.APPROVE else 20)
    version_id = _id(11 if decision is EvidenceReviewDecision.APPROVE else 21)
    with session_factory() as transaction:
        case, version = _seed_fixture(
            transaction,
            case_id=case_id,
            version_id=version_id,
            state=EvidenceVersionState.FINAL.value,
        )
        immutable_before = _version_snapshot(version)
        case_before = (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
        )
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)

        def forbidden_projection(*_args: object, **_kwargs: object) -> str:
            raise AssertionError("legacy projection adapter must not be called")

        monkeypatch.setattr(
            lifecycle_projection,
            "project_legacy_case_status",
            forbidden_projection,
        )
        monkeypatch.setattr(
            evidence_service,
            "project_legacy_case_status",
            forbidden_projection,
            raising=False,
        )

        command = _command(
            case_id=case_id,
            version_id=version_id,
            decision=decision,
            idempotency_key=f"review-{decision.value.lower()}",
        )
        result = review_evidence_version(command, transaction)

        assert result == ReviewEvidenceVersionResult(
            case_id=case_id,
            evidence_version_id=version_id,
            creator_id=_id(800),
            reviewer_id=_id(900),
            decision=decision,
            review_state=expected_state,
            reviewed_at=REVIEWED_AT,
            activity_id=result.activity_id,
            activity_sequence=1,
            lifecycle_revision=1,
            idempotency_key=command.idempotency_key,
            reused=False,
        )
        with pytest.raises(FrozenInstanceError):
            result.reused = True  # type: ignore[misc]
        assert commit.call_count == rollback.call_count == 0

        transaction.refresh(version)
        transaction.refresh(case)
        assert (version.review_state, version.reviewer_id, version.reviewed_at) == (
            expected_state.value,
            _id(900),
            REVIEWED_AT,
        )
        assert version.updated_at == REVIEWED_AT
        assert _version_snapshot(version) == immutable_before
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
        ) == case_before
        assert case.lifecycle_revision == 1

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        assert (
            activity.case_id,
            activity.sequence,
            activity.lane,
            activity.activity_type,
            activity.effective_at,
            activity.occurred_at,
            activity.confirmation_status,
            activity.actor_id,
            activity.reviewer_id,
            activity.idempotency_key,
            activity.source_activity_id,
            activity.supersedes_event_id,
        ) == (
            case_id,
            1,
            ActivityLane.DOCUMENT.value,
            "DOCUMENT_EVIDENCE_REVIEW_DECIDED",
            REVIEWED_AT,
            REVIEWED_AT,
            ConfirmationStatus.CONFIRMED.value,
            _id(900),
            _id(900),
            f"document-evidence-review:{command.idempotency_key}",
            None,
            None,
        )
        assert (
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
        ) == (
            case_before[1],
            case_before[1],
            case_before[2],
            case_before[2],
            case_before[3],
            case_before[3],
        )
        assert json.loads(activity.payload_json) == {
            "creator_id": _id(800),
            "decision": decision.value,
            "evidence_version_id": version_id,
            "previous_review_state": EvidenceReviewState.PENDING.value,
            "review_state": expected_state.value,
            "reviewer_id": _id(900),
        }
        links = transaction.scalars(select(CaseActivityEventEvidence)).all()
        assert len(links) == 1
        assert (
            links[0].case_id,
            links[0].activity_id,
            links[0].evidence_kind,
            links[0].object_type,
            links[0].object_id,
            links[0].content_hash,
            links[0].captured_at,
        ) == (
            case_id,
            result.activity_id,
            "DOCUMENT_EVIDENCE_VERSION",
            "DocumentEvidenceVersion",
            version_id,
            CONTENT_HASH,
            REVIEWED_AT,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("case_id", ""),
        ("case_id", "x" * 37),
        ("evidence_version_id", " "),
        ("evidence_version_id", "x" * 37),
        ("reviewer_id", ""),
        ("reviewer_id", "x" * 37),
        ("decision", "APPROVE"),
        ("reviewed_at", "2026-07-13"),
        ("reviewed_at", datetime(2026, 7, 13, tzinfo=timezone.utc)),
        ("idempotency_key", ""),
        ("idempotency_key", "x" * 104),
    ),
)
def test_malformed_commands_fail_in_frozen_field_order_without_lookup_or_write(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    with session_factory() as transaction:

        def forbidden_lookup(*_args: object, **_kwargs: object) -> None:
            pytest.fail("invalid command must fail before database lookup")

        monkeypatch.setattr(transaction, "get", forbidden_lookup)
        error = _assert_error(
            "EVIDENCE_REVIEW_INVALID",
            400,
            lambda: review_evidence_version(
                replace(_command(), **{field: value}),  # type: ignore[arg-type]
                transaction,
            ),
        )
        assert error.details == {"field": field}
        assert list(transaction.new) == []


def test_requires_exact_command_type_before_attribute_access(
    session_factory: sessionmaker[Session],
) -> None:
    class CommandSubclass(ReviewEvidenceVersionCommand):
        pass

    valid = _command()
    subclass = CommandSubclass(
        **{field.name: getattr(valid, field.name) for field in fields(valid)}
    )
    with session_factory() as transaction:
        for invalid in (object(), SimpleNamespace(), subclass):
            error = _assert_error(
                "EVIDENCE_REVIEW_INVALID",
                400,
                lambda invalid=invalid: review_evidence_version(
                    invalid,  # type: ignore[arg-type]
                    transaction,
                ),
            )
            assert error.details == {"field": "command"}
        assert _counts(transaction) == (0, 0)


@pytest.mark.parametrize(
    ("missing", "code"),
    (("case", "CASE_NOT_FOUND"), ("version", "EVIDENCE_VERSION_NOT_FOUND")),
)
def test_lookup_order_uses_exact_not_found_codes(
    session_factory: sessionmaker[Session], missing: str, code: str
) -> None:
    with session_factory() as transaction:
        if missing == "version":
            _seed_case(transaction)
        _assert_error(
            code,
            404,
            lambda: review_evidence_version(_command(), transaction),
        )
        assert _counts(transaction) == (0, 0)


def test_wrong_case_and_self_review_fail_before_projection_or_mutation(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_case(transaction, case_id=_id(30))
        _seed_case(transaction, case_id=_id(31))
        version = _seed_version(
            transaction,
            case_id=_id(31),
            version_id=_id(32),
            is_current=False,
        )
        transaction.commit()
        _assert_error(
            "EVIDENCE_REVIEW_CASE_MISMATCH",
            400,
            lambda: review_evidence_version(
                _command(case_id=_id(30), version_id=version.id), transaction
            ),
        )
        assert _counts(transaction) == (0, 0)

    with session_factory() as transaction:
        case, version = _seed_fixture(
            transaction,
            case_id=_id(33),
            version_id=_id(34),
        )
        case.business_stage = "UNKNOWN_STAGE"
        transaction.flush()
        _assert_error(
            "EVIDENCE_REVIEW_SELF_REVIEW",
            409,
            lambda: review_evidence_version(
                _command(
                    case_id=case.id,
                    version_id=version.id,
                    reviewer_id=version.creator_id,
                ),
                transaction,
            ),
        )
        assert _counts(transaction) == (0, 0)


@pytest.mark.parametrize(
    ("scenario", "code"),
    (
        ("blank_creator", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("long_creator", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("bad_hash", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("bad_state", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("unknown_review", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("pending_reviewer", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("pending_timestamp", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("terminal_no_reviewer", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("terminal_no_timestamp", "EVIDENCE_REVIEW_STATE_CONFLICT"),
        ("bad_projection", "LIFECYCLE_PROJECTION_CONFLICT"),
    ),
)
def test_malformed_persisted_carrier_and_projection_fail_closed_without_activity(
    session_factory: sessionmaker[Session], scenario: str, code: str
) -> None:
    case_id = _id(
        100
        + list(
            {
                "blank_creator",
                "long_creator",
                "bad_hash",
                "bad_state",
                "unknown_review",
                "pending_reviewer",
                "pending_timestamp",
                "terminal_no_reviewer",
                "terminal_no_timestamp",
                "bad_projection",
            }
        ).index(scenario)
    )
    version_id = _id(int(case_id[-12:]) + 100)
    with session_factory() as transaction:
        case, version = _seed_fixture(
            transaction,
            case_id=case_id,
            version_id=version_id,
        )
        if scenario == "blank_creator":
            version.creator_id = " "
        elif scenario == "long_creator":
            version.creator_id = "x" * 37
        elif scenario == "bad_hash":
            version.content_hash = "not-a-hash"
        elif scenario == "bad_state":
            version.state = "UNKNOWN_STATE"
        elif scenario == "unknown_review":
            version.review_state = "UNKNOWN_REVIEW"
        elif scenario == "pending_reviewer":
            version.reviewer_id = _id(901)
        elif scenario == "pending_timestamp":
            version.reviewed_at = REVIEWED_AT
        elif scenario == "terminal_no_reviewer":
            version.review_state = EvidenceReviewState.APPROVED.value
            version.reviewed_at = REVIEWED_AT
        elif scenario == "terminal_no_timestamp":
            version.review_state = EvidenceReviewState.REJECTED.value
            version.reviewer_id = _id(901)
        else:
            case.legal_status = "UNKNOWN_LEGAL_STATUS"
        transaction.flush()

        _assert_error(
            code,
            409,
            lambda: review_evidence_version(
                _command(case_id=case_id, version_id=version_id), transaction
            ),
        )
        assert _counts(transaction) == (0, 0)
        transaction.rollback()


def test_terminal_decision_is_immutable_under_new_keys(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_fixture(transaction)
        first = review_evidence_version(_command(), transaction)
        transaction.commit()

        alternatives = (
            replace(_command(), idempotency_key="review-2"),
            replace(
                _command(),
                decision=EvidenceReviewDecision.REJECT,
                idempotency_key="review-3",
            ),
            replace(_command(), reviewer_id=_id(901), idempotency_key="review-4"),
        )
        for command in alternatives:
            _assert_error(
                "EVIDENCE_REVIEW_ALREADY_DECIDED",
                409,
                lambda command=command: review_evidence_version(command, transaction),
            )
        assert _counts(transaction) == (1, 1)
        assert transaction.get(CaseActivityEvent, first.activity_id) is not None


def test_lost_compare_and_swap_uses_exact_conflict_without_activity(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _seed_fixture(transaction)
        original_execute = transaction.execute

        def lose_review_update(statement: object, *args: object, **kwargs: object) -> object:
            if isinstance(statement, Update) and statement.table.name == (
                DocumentEvidenceVersion.__tablename__
            ):
                return SimpleNamespace(rowcount=0)
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(transaction, "execute", lose_review_update)
        _assert_error(
            "EVIDENCE_REVIEW_CONCURRENCY_CONFLICT",
            409,
            lambda: review_evidence_version(_command(), transaction),
        )
        assert _counts(transaction) == (0, 0)


def test_exact_replay_is_read_only_after_current_switch_and_changed_facts_conflict(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_fixture(transaction)
        first_command = _command()
        first = review_evidence_version(first_command, transaction)
        transaction.commit()

        _seed_version(
            transaction,
            case_id=_id(1),
            version_id=_id(3),
            ordinal=2,
            is_current=False,
        )
        transaction.commit()
        later = switch_current_evidence_version(
            SwitchCurrentEvidenceVersionCommand(
                case_id=_id(1),
                expected_current_evidence_version_id=_id(2),
                target_evidence_version_id=_id(3),
                actor_id=_id(901),
                switched_at=datetime(2026, 7, 13, 15),
                idempotency_key="switch-after-review",
            ),
            transaction,
        )
        transaction.commit()

        before = (
            transaction.get(Case, _id(1)).lifecycle_revision,
            _counts(transaction),
            transaction.get(DocumentEvidenceVersion, _id(2)).current_identity_key,
            transaction.get(DocumentEvidenceVersion, _id(3)).current_identity_key,
        )
        replay = review_evidence_version(first_command, transaction)
        assert replay == replace(first, reused=True)
        assert replay.activity_id != later.activity_id
        assert (
            transaction.get(Case, _id(1)).lifecycle_revision,
            _counts(transaction),
            transaction.get(DocumentEvidenceVersion, _id(2)).current_identity_key,
            transaction.get(DocumentEvidenceVersion, _id(3)).current_identity_key,
        ) == before

        changed_commands = (
            replace(first_command, decision=EvidenceReviewDecision.REJECT),
            replace(first_command, reviewer_id=_id(902)),
            replace(first_command, reviewed_at=datetime(2026, 7, 13, 16)),
            replace(first_command, evidence_version_id=_id(3)),
        )
        for command in changed_commands:
            _assert_error(
                "LIFECYCLE_IDEMPOTENCY_CONFLICT",
                409,
                lambda command=command: review_evidence_version(command, transaction),
            )
        assert (
            transaction.get(Case, _id(1)).lifecycle_revision,
            _counts(transaction),
        ) == before[:2]


def test_replay_fails_closed_when_activity_projection_or_carrier_disagrees(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_fixture(transaction)
        command = _command()
        result = review_evidence_version(command, transaction)
        transaction.commit()

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        activity.new_legal_status = LegalStatus.PATENT_IN_FORCE.value
        transaction.commit()
        _assert_error(
            "EVIDENCE_REVIEW_HISTORY_CONFLICT",
            409,
            lambda: review_evidence_version(command, transaction),
        )
        activity.new_legal_status = activity.old_legal_status
        transaction.commit()

        version = transaction.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        version.reviewer_id = _id(901)
        transaction.commit()
        _assert_error(
            "EVIDENCE_REVIEW_HISTORY_CONFLICT",
            409,
            lambda: review_evidence_version(command, transaction),
        )
        assert _counts(transaction) == (1, 1)


def test_caller_rollback_removes_decision_activity_link_and_revision(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_fixture(transaction)
        result = review_evidence_version(_command(), transaction)
        assert _counts(transaction) == (1, 1)
        transaction.rollback()

    with session_factory() as verification:
        version = verification.get(DocumentEvidenceVersion, _id(2))
        case = verification.get(Case, _id(1))
        assert version is not None and case is not None
        assert (version.review_state, version.reviewer_id, version.reviewed_at) == (
            EvidenceReviewState.PENDING.value,
            None,
            None,
        )
        assert case.lifecycle_revision == 0
        assert verification.get(CaseActivityEvent, result.activity_id) is None
        assert _counts(verification) == (0, 0)


def test_append_error_propagates_and_caller_rollback_restores_decision(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    append_error = BusinessError("APPEND_FAILED", "append failed", status_code=409)
    with session_factory() as transaction:
        _seed_fixture(transaction)
        monkeypatch.setattr(
            evidence_service,
            "append_case_activity",
            Mock(side_effect=append_error),
        )
        with pytest.raises(BusinessError) as exc_info:
            review_evidence_version(_command(), transaction)
        assert exc_info.value is append_error
        transaction.rollback()

    with session_factory() as verification:
        version = verification.get(DocumentEvidenceVersion, _id(2))
        case = verification.get(Case, _id(1))
        assert version is not None and case is not None
        assert (version.review_state, version.reviewer_id, version.reviewed_at) == (
            EvidenceReviewState.PENDING.value,
            None,
            None,
        )
        assert case.lifecycle_revision == 0
        assert _counts(verification) == (0, 0)
