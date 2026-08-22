from __future__ import annotations

from datetime import datetime
from enum import Enum
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import operators, visitors
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import BinaryExpression, BindParameter

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
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
CONTENT_HASH = f"sha256:{'a' * 64}"


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _workflow():
    from app.modules.documents import evidence_workflow_service

    return evidence_workflow_service


def _seed_forward_role_fixture(transaction: Session, *, role: str) -> None:
    case_id = _id(1)
    document_id = _id(100)
    attachment_id = _id(101)
    transaction.add(
        Case(
            id=case_id,
            case_no="CASE-000000000001",
            status="ACCEPTED",
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED.value,
            legal_status=LegalStatus.APPLICATION_PENDING.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=0,
        )
    )
    transaction.flush()
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
    transaction.add(
        DocumentEvidenceVersion(
            id=_id(2),
            case_id=case_id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key="filing-main",
            role=role,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=_id(800),
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=_id(900),
            reviewed_at=REVIEWED_AT,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{case_id}|filing-main",
        )
    )
    transaction.commit()


def _command(workflow: object):
    return workflow.FinalizeExternalSubmissionCommand(  # type: ignore[attr-defined]
        case_id=_id(1),
        evidence_version_id=_id(2),
        actor_id=_id(700),
        submitted_at=SUBMITTED_AT,
        idempotency_key="submission-1",
    )


def _database_snapshot(transaction: Session) -> tuple[object, ...]:
    case = transaction.get(Case, _id(1))
    version = transaction.get(DocumentEvidenceVersion, _id(2))
    assert case is not None
    assert version is not None
    activities = transaction.scalars(select(CaseActivityEvent).order_by(CaseActivityEvent.id)).all()
    links = transaction.scalars(
        select(CaseActivityEventEvidence).order_by(CaseActivityEventEvidence.id)
    ).all()
    return (
        tuple(getattr(case, column.name) for column in Case.__table__.columns),
        tuple(
            getattr(version, column.name) for column in DocumentEvidenceVersion.__table__.columns
        ),
        tuple(
            tuple(getattr(activity, column.name) for column in CaseActivityEvent.__table__.columns)
            for activity in activities
        ),
        tuple(
            tuple(
                getattr(link, column.name) for column in CaseActivityEventEvidence.__table__.columns
            )
            for link in links
        ),
    )


def _block_downstream_collaborators(
    workflow: object,
    transaction: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Mock, Mock, Mock, Mock]:
    projection = Mock(side_effect=AssertionError("projection must not be captured"))
    replay_lookup = Mock(side_effect=AssertionError("replay must not be queried"))
    update_builder = Mock(side_effect=AssertionError("update must not be built"))
    activity_append = Mock(side_effect=AssertionError("activity must not be appended"))
    monkeypatch.setattr(workflow, "_capture_lifecycle_projection", projection)
    monkeypatch.setattr(transaction, "scalar", replay_lookup)
    monkeypatch.setattr(workflow, "update", update_builder)
    monkeypatch.setattr(workflow, "append_case_activity", activity_append)
    return projection, replay_lookup, update_builder, activity_append


def _role_equalities(statement: Update) -> tuple[BinaryExpression, ...]:
    return tuple(
        node
        for node in visitors.iterate(statement.whereclause)
        if isinstance(node, BinaryExpression)
        and node.operator is operators.eq
        and node.left.compare(DocumentEvidenceVersion.__table__.c.role)
    )


@pytest.mark.parametrize(
    "role",
    (
        EvidenceRole.FILING_FULL_WORD,
        EvidenceRole.TRACKED_REVISED_WORD,
        EvidenceRole.FILING_COMPONENT,
        EvidenceRole.EXTERNAL_XML_PACKAGE,
        EvidenceRole.OFFICIAL_SUBMISSION_LIST,
        EvidenceRole.OFFICIAL_FINAL_PDF,
        EvidenceRole.SUBMITTED_XML,
        EvidenceRole.OFFICIAL_RECEIPT,
        EvidenceRole.CLIENT_LETTER_WORD,
    ),
)
@pytest.mark.parametrize("path", ("fresh", "replay"))
def test_each_original_role_supports_public_finalization(
    session_factory: sessionmaker[Session],
    role: EvidenceRole,
    path: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_forward_role_fixture(transaction, role=role.value)

        if path == "replay":
            initial = workflow.finalize_external_submission(_command(workflow), transaction)
            assert initial.reused is False
            transaction.commit()

        result = workflow.finalize_external_submission(
            workflow.FinalizeExternalSubmissionCommand(
                case_id=_id(1),
                evidence_version_id=_id(2),
                actor_id=_id(700),
                submitted_at=SUBMITTED_AT,
                idempotency_key="submission-1",
            ),
            transaction,
        )

        assert (
            result.case_id,
            result.evidence_version_id,
            result.submitted_at,
            result.reused,
        ) == (_id(1), _id(2), SUBMITTED_AT, path == "replay")
        assert transaction.get(DocumentEvidenceVersion, _id(2)).final_submitted_at == (SUBMITTED_AT)


def test_allowed_public_finalize_update_locks_loaded_exact_role(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_forward_role_fixture(transaction, role="OFFICIAL_FINAL_PDF")
        version = transaction.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        loaded_exact_role = version.role
        captured_updates: list[Update] = []
        original_execute = transaction.execute

        def capture_update(statement: object, *args: object, **kwargs: object) -> object:
            if isinstance(statement, Update) and statement.table.name == (
                DocumentEvidenceVersion.__tablename__
            ):
                captured_updates.append(statement)
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(transaction, "execute", capture_update)

        workflow.finalize_external_submission(_command(workflow), transaction)

        assert len(captured_updates) == 1
        statement = captured_updates[0]
        role_equalities = _role_equalities(statement)
        assert len(role_equalities) == 1
        role_equality = role_equalities[0]
        assert isinstance(role_equality.right, BindParameter)
        assert role_equality.right.value == loaded_exact_role


def test_role_change_after_validation_keeps_existing_concurrency_conflict(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_forward_role_fixture(transaction, role="OFFICIAL_FINAL_PDF")
        version = transaction.get(DocumentEvidenceVersion, _id(2))
        assert version is not None
        loaded_exact_role = version.role
        before = _database_snapshot(transaction)
        simulated_row_role = {"value": loaded_exact_role}
        original_projection = workflow._capture_lifecycle_projection
        original_execute = transaction.execute

        def change_role_after_validation(case: Case) -> object:
            simulated_row_role["value"] = "SUBMITTED_XML"
            return original_projection(case)

        def lose_role_compare_and_swap(
            statement: object,
            *args: object,
            **kwargs: object,
        ) -> object:
            if isinstance(statement, Update) and statement.table.name == (
                DocumentEvidenceVersion.__tablename__
            ):
                role_equalities = _role_equalities(statement)
                assert len(role_equalities) == 1
                role_equality = role_equalities[0]
                assert isinstance(role_equality.right, BindParameter)
                assert role_equality.right.value == loaded_exact_role
                assert simulated_row_role["value"] != role_equality.right.value
                return SimpleNamespace(rowcount=0)
            return original_execute(statement, *args, **kwargs)

        monkeypatch.setattr(
            workflow,
            "_capture_lifecycle_projection",
            change_role_after_validation,
        )
        monkeypatch.setattr(transaction, "execute", lose_role_compare_and_swap)

        with pytest.raises(BusinessError) as exc_info:
            workflow.finalize_external_submission(_command(workflow), transaction)

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT",
            409,
        )
        assert simulated_row_role["value"] == "SUBMITTED_XML"
        assert _database_snapshot(transaction) == before
        assert transaction.is_active
        assert transaction.scalar(select(Case.id).where(Case.id == _id(1))) == _id(1)
        transaction.flush()


@pytest.mark.parametrize("role", (EvidenceRole.RAW_ATTACHMENT,))
@pytest.mark.parametrize("path", ("fresh", "replay"))
def test_production_raw_attachment_fails_before_any_downstream_behavior(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    role: EvidenceRole,
    path: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        if path == "replay":
            _seed_forward_role_fixture(
                transaction,
                role=EvidenceRole.SUBMITTED_XML.value,
            )
            workflow.finalize_external_submission(_command(workflow), transaction)
            transaction.commit()
            version = transaction.get(DocumentEvidenceVersion, _id(2))
            assert version is not None
            version.role = role.value
            transaction.commit()
        else:
            _seed_forward_role_fixture(transaction, role=role.value)

        before = _database_snapshot(transaction)
        collaborators = _block_downstream_collaborators(
            workflow,
            transaction,
            monkeypatch,
        )

        with pytest.raises(BusinessError) as exc_info:
            workflow.finalize_external_submission(_command(workflow), transaction)

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            409,
        )
        assert tuple(mock.call_count for mock in collaborators) == (0, 0, 0, 0)
        assert _database_snapshot(transaction) == before


@pytest.mark.parametrize("path", ("fresh", "replay"))
def test_future_unlisted_role_fails_before_any_downstream_behavior(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    class ForwardEvidenceRole(str, Enum):
        FILING_FULL_WORD = EvidenceRole.FILING_FULL_WORD.value
        TRACKED_REVISED_WORD = EvidenceRole.TRACKED_REVISED_WORD.value
        FILING_COMPONENT = EvidenceRole.FILING_COMPONENT.value
        EXTERNAL_XML_PACKAGE = EvidenceRole.EXTERNAL_XML_PACKAGE.value
        OFFICIAL_SUBMISSION_LIST = EvidenceRole.OFFICIAL_SUBMISSION_LIST.value
        OFFICIAL_FINAL_PDF = EvidenceRole.OFFICIAL_FINAL_PDF.value
        SUBMITTED_XML = EvidenceRole.SUBMITTED_XML.value
        OFFICIAL_RECEIPT = EvidenceRole.OFFICIAL_RECEIPT.value
        CLIENT_LETTER_WORD = EvidenceRole.CLIENT_LETTER_WORD.value
        RAW_ATTACHMENT = EvidenceRole.RAW_ATTACHMENT.value
        FUTURE_UNLISTED = "FUTURE_UNLISTED"

    workflow = _workflow()
    role = ForwardEvidenceRole.FUTURE_UNLISTED.value
    with session_factory() as transaction:
        if path == "replay":
            _seed_forward_role_fixture(
                transaction,
                role=EvidenceRole.SUBMITTED_XML.value,
            )
            workflow.finalize_external_submission(_command(workflow), transaction)
            transaction.commit()
            version = transaction.get(DocumentEvidenceVersion, _id(2))
            assert version is not None
            version.role = role
            transaction.commit()
        else:
            _seed_forward_role_fixture(transaction, role=role)

        monkeypatch.setattr(workflow, "EvidenceRole", ForwardEvidenceRole)
        before = _database_snapshot(transaction)
        collaborators = _block_downstream_collaborators(
            workflow,
            transaction,
            monkeypatch,
        )

        with pytest.raises(BusinessError) as exc_info:
            workflow.finalize_external_submission(_command(workflow), transaction)

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            409,
        )
        assert tuple(mock.call_count for mock in collaborators) == (0, 0, 0, 0)
        assert _database_snapshot(transaction) == before


def test_malformed_stored_role_keeps_stored_identity_conflict_surface(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        _seed_forward_role_fixture(transaction, role="MALFORMED_ROLE")
        before = _database_snapshot(transaction)
        collaborators = _block_downstream_collaborators(
            workflow,
            transaction,
            monkeypatch,
        )

        with pytest.raises(BusinessError) as exc_info:
            workflow.finalize_external_submission(_command(workflow), transaction)

        assert (
            exc_info.value.code,
            exc_info.value.message,
            exc_info.value.status_code,
        ) == (
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            "Stored evidence role is invalid",
            409,
        )
        assert tuple(mock.call_count for mock in collaborators) == (0, 0, 0, 0)
        assert _database_snapshot(transaction) == before
