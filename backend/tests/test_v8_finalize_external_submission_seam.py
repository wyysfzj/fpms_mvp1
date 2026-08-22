from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.dml import Update

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion

SUBMITTED_AT = datetime(2026, 7, 14, 9, 30)
REVIEWED_AT = datetime(2026, 7, 14, 9)
LINEAGE_KEY = "filing-main"
CONTENT_HASH = f"sha256:{'a' * 64}"


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _workflow():
    from app.modules.documents import evidence_workflow_service

    return evidence_workflow_service


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
    creator_id: str = _id(800),
    state: str = EvidenceVersionState.FINAL.value,
    review_state: str = EvidenceReviewState.APPROVED.value,
    reviewer_id: str | None = _id(900),
    reviewed_at: datetime | None = REVIEWED_AT,
    is_current: bool = True,
    final_submitted_at: datetime | None = None,
) -> DocumentEvidenceVersion:
    document_id = _id(100)
    attachment_id = _id(101)
    transaction.add(Document(id=document_id, case_id=case_id))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="filing-final.xml",
            file_path="/evidence/filing-final.xml",
        )
    )
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=version_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=LINEAGE_KEY,
        role=EvidenceRole.SUBMITTED_XML.value,
        version_number=1,
        state=state,
        creator_id=creator_id,
        review_state=review_state,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
        final_submitted_at=final_submitted_at,
        content_hash=CONTENT_HASH,
        current_identity_key=f"{case_id}|{LINEAGE_KEY}" if is_current else None,
    )
    transaction.add(version)
    transaction.flush()
    return version


def _seed_fixture(
    transaction: Session, **version_overrides: object
) -> tuple[Case, DocumentEvidenceVersion]:
    case_id = str(version_overrides.get("case_id", _id(1)))
    case = _seed_case(transaction, case_id=case_id)
    version = _seed_version(transaction, **version_overrides)
    transaction.commit()
    return case, version


def _command(**overrides: object):
    command_type = _workflow().FinalizeExternalSubmissionCommand
    values = {
        "case_id": _id(1),
        "evidence_version_id": _id(2),
        "actor_id": _id(700),
        "submitted_at": SUBMITTED_AT,
        "idempotency_key": "submission-1",
    }
    values.update(overrides)
    return command_type(**values)


def _assert_error(code: str, status: int, callable_: object) -> BusinessError:
    with pytest.raises(BusinessError) as exc_info:
        callable_()  # type: ignore[operator]
    assert (exc_info.value.code, exc_info.value.status_code) == (code, status)
    return exc_info.value


def _counts(transaction: Session) -> tuple[int, int]:
    return (
        len(transaction.scalars(select(CaseActivityEvent)).all()),
        len(transaction.scalars(select(CaseActivityEventEvidence)).all()),
    )


def test_public_contract_is_exact_frozen_slotted_and_keyword_only() -> None:
    workflow = _workflow()
    expected_command_fields = (
        ("case_id", str),
        ("evidence_version_id", str),
        ("actor_id", str),
        ("submitted_at", datetime),
        ("idempotency_key", str),
    )
    expected_result_fields = (
        ("case_id", str),
        ("evidence_version_id", str),
        ("content_hash", str),
        ("submitted_at", datetime),
        ("activity_id", str),
        ("activity_sequence", int),
        ("lifecycle_revision", int),
        ("idempotency_key", str),
        ("reused", bool),
    )
    for data_type, expected_fields in (
        (workflow.FinalizeExternalSubmissionCommand, expected_command_fields),
        (workflow.SubmissionEvidenceResult, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__

    signature = inspect.signature(workflow.finalize_external_submission)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert get_type_hints(workflow.finalize_external_submission)["return"] is (
        workflow.SubmissionEvidenceResult
    )


def test_finalizes_only_exact_evidence_and_appends_document_activity(
    session_factory: sessionmaker[Session], monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        case, version = _seed_fixture(transaction)
        case_before = (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
        )
        immutable_before = (
            version.case_id,
            version.document_id,
            version.attachment_id,
            version.lineage_key,
            version.role,
            version.version_number,
            version.state,
            version.creator_id,
            version.review_state,
            version.reviewer_id,
            version.reviewed_at,
            version.content_hash,
            version.current_identity_key,
        )
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)

        command = _command()
        result = workflow.finalize_external_submission(command, transaction)

        assert result == workflow.SubmissionEvidenceResult(
            case_id=_id(1),
            evidence_version_id=_id(2),
            content_hash=CONTENT_HASH,
            submitted_at=SUBMITTED_AT,
            activity_id=result.activity_id,
            activity_sequence=1,
            lifecycle_revision=1,
            idempotency_key="submission-1",
            reused=False,
        )
        with pytest.raises(FrozenInstanceError):
            result.reused = True  # type: ignore[misc]
        assert commit.call_count == rollback.call_count == 0

        transaction.refresh(version)
        transaction.refresh(case)
        assert version.final_submitted_at == SUBMITTED_AT
        assert immutable_before == (
            version.case_id,
            version.document_id,
            version.attachment_id,
            version.lineage_key,
            version.role,
            version.version_number,
            version.state,
            version.creator_id,
            version.review_state,
            version.reviewer_id,
            version.reviewed_at,
            version.content_hash,
            version.current_identity_key,
        )
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
            activity.actor_id,
            activity.reviewer_id,
            activity.effective_at,
            activity.occurred_at,
            activity.confirmation_status,
            activity.idempotency_key,
            activity.source_activity_id,
            activity.supersedes_event_id,
        ) == (
            _id(1),
            1,
            ActivityLane.DOCUMENT.value,
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            _id(700),
            _id(900),
            SUBMITTED_AT,
            SUBMITTED_AT,
            ConfirmationStatus.CONFIRMED.value,
            "document-external-submission:submission-1",
            None,
            None,
        )
        assert json.loads(activity.payload_json) == {
            "evidence_version_id": _id(2),
            "lineage_key": LINEAGE_KEY,
            "role": EvidenceRole.SUBMITTED_XML.value,
            "submitted_at": SUBMITTED_AT.isoformat(),
        }
        assert all(
            old == new
            for old, new in (
                (activity.old_business_stage, activity.new_business_stage),
                (
                    activity.old_official_procedure_stage,
                    activity.new_official_procedure_stage,
                ),
                (activity.old_legal_status, activity.new_legal_status),
            )
        )
        assert (
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
        ) == (
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.ACCEPTED.value,
            OfficialProcedureStage.ACCEPTED.value,
            LegalStatus.APPLICATION_PENDING.value,
            LegalStatus.APPLICATION_PENDING.value,
        )
        link = transaction.scalars(select(CaseActivityEventEvidence)).one()
        assert (
            link.case_id,
            link.activity_id,
            link.evidence_kind,
            link.object_type,
            link.object_id,
            link.content_hash,
            link.captured_at,
        ) == (
            _id(1),
            result.activity_id,
            "DOCUMENT_EVIDENCE_VERSION",
            "DocumentEvidenceVersion",
            _id(2),
            CONTENT_HASH,
            SUBMITTED_AT,
        )


@pytest.mark.parametrize(
    ("overrides", "code", "status"),
    (
        ({"state": EvidenceVersionState.DRAFT.value}, "EXTERNAL_SUBMISSION_NOT_FINAL", 409),
        (
            {
                "review_state": EvidenceReviewState.PENDING.value,
                "reviewer_id": None,
                "reviewed_at": None,
            },
            "EXTERNAL_SUBMISSION_NOT_APPROVED",
            409,
        ),
        (
            {"reviewer_id": _id(800)},
            "EXTERNAL_SUBMISSION_SELF_REVIEWED",
            409,
        ),
        ({"is_current": False}, "EXTERNAL_SUBMISSION_NOT_CURRENT", 409),
    ),
)
def test_ineligible_evidence_fails_closed_without_write(
    session_factory: sessionmaker[Session],
    overrides: dict[str, object],
    code: str,
    status: int,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _case, version = _seed_fixture(transaction, **overrides)
        before = (version.final_submitted_at, _counts(transaction))
        _assert_error(
            code,
            status,
            lambda: workflow.finalize_external_submission(_command(), transaction),
        )
        assert (version.final_submitted_at, _counts(transaction)) == before


def test_wrong_case_and_invalid_command_fail_before_mutation(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        transaction.add(
            Case(
                id=_id(3),
                case_no="CASE-WRONG",
                status="ACCEPTED",
                lifecycle_revision=0,
            )
        )
        transaction.commit()
        before = _counts(transaction)
        _assert_error(
            "EXTERNAL_SUBMISSION_CASE_MISMATCH",
            400,
            lambda: workflow.finalize_external_submission(_command(case_id=_id(3)), transaction),
        )
        _assert_error(
            "EXTERNAL_SUBMISSION_INVALID",
            400,
            lambda: workflow.finalize_external_submission(
                replace(_command(), submitted_at=datetime(2026, 7, 14, tzinfo=timezone.utc)),
                transaction,
            ),
        )
        assert _counts(transaction) == before


def test_exact_replay_reuses_result_and_changed_key_facts_conflict(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        command = _command()
        first = workflow.finalize_external_submission(command, transaction)
        snapshot = _counts(transaction)

        replay = workflow.finalize_external_submission(command, transaction)
        assert replay == replace(first, reused=True)
        assert _counts(transaction) == snapshot

        _assert_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(
                replace(command, submitted_at=datetime(2026, 7, 14, 9, 31)),
                transaction,
            ),
        )
        _assert_error(
            "EXTERNAL_SUBMISSION_ALREADY_FINALIZED",
            409,
            lambda: workflow.finalize_external_submission(
                replace(command, idempotency_key="submission-2"), transaction
            ),
        )
        assert _counts(transaction) == snapshot


def test_lost_finalize_compare_and_swap_is_exact_and_leaves_transaction_usable(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _case, version = _seed_fixture(transaction)
        before = (version.final_submitted_at, version.updated_at, _counts(transaction))
        original_execute = transaction.execute

        def lose_finalize_update(statement: object, *args: object, **kwargs: object) -> object:
            if isinstance(statement, Update) and statement.table.name == (
                DocumentEvidenceVersion.__tablename__
            ):
                return SimpleNamespace(rowcount=0)
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(transaction, "execute", lose_finalize_update)
        _assert_error(
            "EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(_command(), transaction),
        )
        assert (version.final_submitted_at, version.updated_at, _counts(transaction)) == before
        assert transaction.scalar(select(Case.id).where(Case.id == _id(1))) == _id(1)
        transaction.flush()


def test_replay_rejects_same_key_actor_and_evidence_fact_changes(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        command = _command()
        workflow.finalize_external_submission(command, transaction)
        transaction.commit()
        before = _counts(transaction)

        _assert_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(
                replace(command, actor_id=_id(701)), transaction
            ),
        )

        version = transaction.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        version.content_hash = f"sha256:{'b' * 64}"
        transaction.commit()
        _assert_error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(command, transaction),
        )
        assert _counts(transaction) == before


def test_replay_rejects_tampered_central_projection_as_history_conflict(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        result = workflow.finalize_external_submission(_command(), transaction)
        transaction.commit()

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        activity.new_legal_status = LegalStatus.PATENT_IN_FORCE.value
        transaction.commit()
        _assert_error(
            "EXTERNAL_SUBMISSION_HISTORY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(_command(), transaction),
        )
        assert _counts(transaction) == (1, 1)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("state", EvidenceVersionState.DRAFT.value),
        ("review_state", EvidenceReviewState.REJECTED.value),
        ("final_submitted_at", datetime(2026, 7, 14, 9, 31)),
    ),
)
def test_replay_rejects_carrier_disagreement_as_history_conflict(
    session_factory: sessionmaker[Session],
    field: str,
    value: object,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        workflow.finalize_external_submission(_command(), transaction)
        transaction.commit()

        version = transaction.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        setattr(version, field, value)
        transaction.commit()
        _assert_error(
            "EXTERNAL_SUBMISSION_HISTORY_CONFLICT",
            409,
            lambda: workflow.finalize_external_submission(_command(), transaction),
        )
        assert _counts(transaction) == (1, 1)


def test_caller_rollback_removes_submission_activity_and_version_change(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_fixture(transaction)
        workflow.finalize_external_submission(_command(), transaction)
        transaction.rollback()

    with session_factory() as observer:
        version = observer.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        assert version.final_submitted_at is None
        assert _counts(observer) == (0, 0)
