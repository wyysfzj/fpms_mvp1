from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import PayList
from app.modules.billing.models import Payment
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_workflow_service as evidence_workflow
from app.modules.documents import fee_linking_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeDraft, FeeObligation, FeeObligationLine

CASE_ID = "00000000-0000-0000-0000-000000000001"
WRONG_CASE_ID = "00000000-0000-0000-0000-000000000002"
ACTOR_ID = "00000000-0000-0000-0000-000000000700"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
LINEAGE_KEY = "ic-layout-extension-request-submission"
WRONG_LINEAGE_KEY = "ic-layout-bibliographic-change-submission"
REVIEWED_AT = datetime(2026, 7, 25, 9)
SUBMITTED_AT = datetime(2026, 7, 25, 9, 30)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _boundary():
    command_type = getattr(
        fee_linking_service,
        "RecognizeIcLayoutExtensionRequestObligationCommand",
        None,
    )
    recognize = getattr(
        fee_linking_service,
        "recognize_ic_layout_extension_request_obligation",
        None,
    )
    assert command_type is not None
    assert recognize is not None
    return command_type, recognize


def _seed_case(transaction: Session) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="IC-LAYOUT-EXTENSION-REQUEST",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            status="ACCEPTED",
            business_stage="PROSECUTION_MANAGEMENT",
            official_procedure_stage="ACCEPTED",
            legal_status="APPLICATION_PENDING",
            lifecycle_revision=0,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.commit()


def _seed_evidence(
    transaction: Session,
    *,
    ordinal: int,
    lineage_key: str = LINEAGE_KEY,
) -> str:
    document_id = _id(100 + ordinal * 10)
    attachment_id = _id(101 + ordinal * 10)
    evidence_id = _id(102 + ordinal * 10)
    content_hash = f"sha256:{ordinal:064x}"
    transaction.add(Document(id=document_id, case_id=CASE_ID, direction="OUT"))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"extension-request-{ordinal}.xml",
            file_path=f"/evidence/extension-request-{ordinal}.xml",
            content_hash=content_hash,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=CASE_ID,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=lineage_key,
            role=EvidenceRole.SUBMITTED_XML.value,
            version_number=ordinal,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT + timedelta(minutes=ordinal),
            content_hash=content_hash,
            current_identity_key=f"{CASE_ID}|{lineage_key}",
        )
    )
    transaction.commit()
    return evidence_id


def _finalize(
    transaction: Session,
    *,
    evidence_id: str,
    ordinal: int,
) -> str:
    result = evidence_workflow.finalize_external_submission(
        evidence_workflow.FinalizeExternalSubmissionCommand(
            case_id=CASE_ID,
            evidence_version_id=evidence_id,
            actor_id=ACTOR_ID,
            submitted_at=SUBMITTED_AT + timedelta(days=ordinal),
            idempotency_key=f"ic-layout-extension-request-submission-{ordinal}",
        ),
        transaction,
    )
    transaction.commit()
    return result.activity_id


def _command(
    source_activity_id: str,
    evidence_id: str,
    *,
    case_id: str = CASE_ID,
):
    command_type, _ = _boundary()
    return command_type(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_evidence_version_id=evidence_id,
    )


def _counts(transaction: Session) -> tuple[int, ...]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(PayList)) or 0,
        transaction.scalar(select(func.count()).select_from(Payment)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED")
        )
        or 0,
    )


def _expect_conflict(callable_: object) -> None:
    with pytest.raises(BusinessError) as captured:
        callable_()  # type: ignore[operator]
    assert captured.value.status_code == 409
    assert captured.value.code == "IC_LAYOUT_EXTENSION_REQUEST_SOURCE_CONFLICT"


def test_each_reviewed_final_extension_request_forms_and_reuses_only_its_own_fee(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = session_factory()
    try:
        _seed_case(transaction)
        first_evidence_id = _seed_evidence(transaction, ordinal=1)
        first_activity_id = _finalize(
            transaction,
            evidence_id=first_evidence_id,
            ordinal=1,
        )
        _, recognize = _boundary()

        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(side_effect=AssertionError("service must not close"))
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", commit)
            patch.setattr(transaction, "rollback", rollback)
            patch.setattr(transaction, "close", close)
            first = recognize(
                _command(first_activity_id, first_evidence_id),
                transaction,
            )
            first_replay = recognize(
                _command(first_activity_id, first_evidence_id),
                transaction,
            )
        assert first.reused is False
        assert first_replay == replace(first, reused=True)
        assert commit.call_count == rollback.call_count == close.call_count == 0
        transaction.commit()

        first_evidence = transaction.get(DocumentEvidenceVersion, first_evidence_id)
        assert first_evidence is not None
        first_evidence.current_identity_key = None
        transaction.commit()
        second_evidence_id = _seed_evidence(transaction, ordinal=2)
        second_activity_id = _finalize(
            transaction,
            evidence_id=second_evidence_id,
            ordinal=2,
        )

        second = recognize(
            _command(second_activity_id, second_evidence_id),
            transaction,
        )
        second_replay = recognize(
            _command(second_activity_id, second_evidence_id),
            transaction,
        )

        assert second.reused is False
        assert second_replay == replace(second, reused=True)
        assert second.obligation.id != first.obligation.id
        assert second.idempotency_key != first.idempotency_key
        assert first_activity_id in first.idempotency_key
        assert second_activity_id in second.idempotency_key

        obligations = transaction.scalars(
            select(FeeObligation).order_by(FeeObligation.source_activity_id)
        ).all()
        assert {
            (
                item.case_id,
                item.source_activity_id,
                item.obligation_type,
                item.currency,
                item.source_status,
                item.created_by,
            )
            for item in obligations
        } == {
            (
                CASE_ID,
                first_activity_id,
                "IC_LAYOUT_EXTENSION_REQUESTED",
                "CNY",
                "VERIFIED",
                ACTOR_ID,
            ),
            (
                CASE_ID,
                second_activity_id,
                "IC_LAYOUT_EXTENSION_REQUESTED",
                "CNY",
                "VERIFIED",
                ACTOR_ID,
            ),
        }
        lines = transaction.scalars(select(FeeObligationLine)).all()
        assert {
            (
                line.fee_code,
                line.fee_name,
                line.fee_year_key,
                line.official_full_amount,
                line.reduction_ratio,
                line.payable_amount,
                line.source_amount,
                line.source_date,
                line.difference_review_state,
            )
            for line in lines
        } == {
            (
                "IC_LAYOUT_EXTENSION_REQUEST_FEE",
                "布图设计延长期限请求费",
                0,
                Decimal("150.00"),
                Decimal("0.0000"),
                Decimal("150.00"),
                None,
                (SUBMITTED_AT + timedelta(days=1)).date(),
                "MATCHED",
            ),
            (
                "IC_LAYOUT_EXTENSION_REQUEST_FEE",
                "布图设计延长期限请求费",
                0,
                Decimal("150.00"),
                Decimal("0.0000"),
                Decimal("150.00"),
                None,
                (SUBMITTED_AT + timedelta(days=2)).date(),
                "MATCHED",
            ),
        }
        assert _counts(transaction) == (2, 2, 0, 0, 0, 2)
        assert [
            activity.activity_type
            for activity in transaction.scalars(
                select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
            )
        ] == [
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            "FEE_OBLIGATION_RECOGNIZED",
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            "FEE_OBLIGATION_RECOGNIZED",
        ]
    finally:
        transaction.close()


@pytest.mark.parametrize(
    "source_defect",
    (
        "wrong_case",
        "wrong_direction",
        "wrong_state",
        "wrong_review_state",
        "nonindependent_review",
        "wrong_lineage",
        "missing_reference",
        "multiple_reference",
        "wrong_identity",
    ),
)
def test_wrong_case_state_review_lineage_reference_or_identity_is_409_with_zero_write(
    session_factory: sessionmaker[Session],
    source_defect: str,
) -> None:
    transaction = session_factory()
    try:
        _seed_case(transaction)
        evidence_id = _seed_evidence(transaction, ordinal=1)
        activity_id = _finalize(transaction, evidence_id=evidence_id, ordinal=1)
        evidence = transaction.get(DocumentEvidenceVersion, evidence_id)
        assert evidence is not None
        document = transaction.get(Document, evidence.document_id)
        assert document is not None
        reference = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity_id
            )
        ).one()

        case_id = CASE_ID
        if source_defect == "wrong_case":
            case_id = WRONG_CASE_ID
        elif source_defect == "wrong_direction":
            document.direction = "IN"
        elif source_defect == "wrong_state":
            evidence.state = EvidenceVersionState.DRAFT.value
        elif source_defect == "wrong_review_state":
            evidence.review_state = EvidenceReviewState.PENDING.value
        elif source_defect == "nonindependent_review":
            evidence.reviewer_id = CREATOR_ID
        elif source_defect == "wrong_lineage":
            evidence.lineage_key = WRONG_LINEAGE_KEY
            evidence.current_identity_key = f"{CASE_ID}|{WRONG_LINEAGE_KEY}"
        elif source_defect == "missing_reference":
            transaction.delete(reference)
        elif source_defect == "multiple_reference":
            transaction.add(
                CaseActivityEventEvidence(
                    id=_id(500),
                    case_id=CASE_ID,
                    activity_id=activity_id,
                    evidence_kind="UNEXPECTED",
                    object_type="DocumentEvidenceVersion",
                    object_id=evidence_id,
                    content_hash=reference.content_hash,
                    captured_at=reference.captured_at,
                )
            )
        elif source_defect == "wrong_identity":
            evidence.current_identity_key = None
        transaction.commit()
        _, recognize = _boundary()

        _expect_conflict(
            lambda: recognize(
                _command(activity_id, evidence_id, case_id=case_id),
                transaction,
            )
        )

        assert _counts(transaction) == (0, 0, 0, 0, 0, 0)
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
    finally:
        transaction.close()


@pytest.mark.parametrize(
    "activity_type",
    (
        "DEADLINE_APPROACHING",
        "DOCUMENT_EVIDENCE_DRAFT_SAVED",
        "DOCUMENT_EVIDENCE_UPLOADED",
        "IC_LAYOUT_EXTENSION_REQUEST_INTENT_RECORDED",
    ),
)
def test_deadline_draft_upload_or_intent_does_not_trigger_fee(
    session_factory: sessionmaker[Session],
    activity_type: str,
) -> None:
    transaction = session_factory()
    try:
        _seed_case(transaction)
        evidence_id = _seed_evidence(transaction, ordinal=1)
        activity_id = _finalize(transaction, evidence_id=evidence_id, ordinal=1)
        activity = transaction.get(CaseActivityEvent, activity_id)
        assert activity is not None
        activity.activity_type = activity_type
        transaction.commit()
        _, recognize = _boundary()

        _expect_conflict(lambda: recognize(_command(activity_id, evidence_id), transaction))

        assert _counts(transaction) == (0, 0, 0, 0, 0, 0)
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
    finally:
        transaction.close()


def test_replay_identity_conflict_is_409_without_an_additional_write(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        _seed_case(transaction)
        evidence_id = _seed_evidence(transaction, ordinal=1)
        activity_id = _finalize(transaction, evidence_id=evidence_id, ordinal=1)
        _, recognize = _boundary()
        first = recognize(_command(activity_id, evidence_id), transaction)
        transaction.commit()
        before = _counts(transaction)

        obligation = transaction.get(FeeObligation, first.obligation.id)
        assert obligation is not None
        obligation.obligation_type = "CONFLICTING_TYPE"
        transaction.commit()

        _expect_conflict(lambda: recognize(_command(activity_id, evidence_id), transaction))

        assert _counts(transaction) == before
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
    finally:
        transaction.close()
