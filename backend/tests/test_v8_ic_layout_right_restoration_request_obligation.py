from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import PayList
from app.modules.billing.models import Payment
from app.modules.cases.models import Case, CaseActivityEvent
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
DOCUMENT_ID = "00000000-0000-0000-0000-000000000100"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000101"
EVIDENCE_ID = "00000000-0000-0000-0000-000000000002"
ACTOR_ID = "00000000-0000-0000-0000-000000000700"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
CONTENT_HASH = f"sha256:{'a' * 64}"
SUBMITTED_AT = datetime(2026, 7, 24, 9, 30)
REVIEWED_AT = datetime(2026, 7, 24, 9)
RESTORATION_LINEAGE = "ic-layout-right-restoration-request-submission"
LOSS_NOTICE_LINEAGE = "ic-layout-loss-of-right-notice"


def _boundary():
    command_type = getattr(
        fee_linking_service,
        "RecognizeIcLayoutRightRestorationRequestObligationCommand",
        None,
    )
    recognize = getattr(
        fee_linking_service,
        "recognize_ic_layout_right_restoration_request_obligation",
        None,
    )
    assert command_type is not None
    assert recognize is not None
    return command_type, recognize


def _seed_reviewed_final_evidence(
    transaction: Session,
    *,
    lineage_key: str,
    direction: str,
) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="IC-LAYOUT-RESTORE-RIGHT-REQUESTED",
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
    transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction=direction))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=ATTACHMENT_ID,
            document_id=DOCUMENT_ID,
            file_name=f"{lineage_key}.xml",
            file_path=f"/evidence/{lineage_key}.xml",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=EVIDENCE_ID,
            case_id=CASE_ID,
            document_id=DOCUMENT_ID,
            attachment_id=ATTACHMENT_ID,
            lineage_key=lineage_key,
            role=EvidenceRole.SUBMITTED_XML.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|{lineage_key}",
        )
    )
    transaction.commit()


def _finalize(transaction: Session) -> str:
    result = evidence_workflow.finalize_external_submission(
        evidence_workflow.FinalizeExternalSubmissionCommand(
            case_id=CASE_ID,
            evidence_version_id=EVIDENCE_ID,
            actor_id=ACTOR_ID,
            submitted_at=SUBMITTED_AT,
            idempotency_key="ic-layout-restoration-submission-1",
        ),
        transaction,
    )
    transaction.commit()
    return result.activity_id


def _command(source_activity_id: str):
    command_type, _ = _boundary()
    return command_type(
        case_id=CASE_ID,
        source_activity_id=source_activity_id,
        source_evidence_version_id=EVIDENCE_ID,
    )


def _fee_counts(transaction: Session) -> tuple[int, ...]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(PayList)) or 0,
        transaction.scalar(select(func.count()).select_from(Payment)) or 0,
    )


def test_reviewed_final_restoration_request_forms_and_reuses_only_owned_obligation(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = session_factory()
    try:
        _seed_reviewed_final_evidence(
            transaction,
            lineage_key=RESTORATION_LINEAGE,
            direction="OUT",
        )
        source_activity_id = _finalize(transaction)

        assert _fee_counts(transaction) == (0, 0, 0, 0, 0)
        assert [
            activity.activity_type
            for activity in transaction.scalars(
                select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
            )
        ] == ["DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED"]

        _, recognize = _boundary()
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(side_effect=AssertionError("service must not close"))
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", commit)
            patch.setattr(transaction, "rollback", rollback)
            patch.setattr(transaction, "close", close)
            created = recognize(_command(source_activity_id), transaction)
            replayed = recognize(_command(source_activity_id), transaction)

        assert created.reused is False
        assert replayed.reused is True
        assert replayed.obligation.id == created.obligation.id
        assert created.idempotency_key == "ic-layout-right-restoration-request"
        assert commit.call_count == rollback.call_count == close.call_count == 0

        obligation = transaction.scalars(select(FeeObligation)).one()
        assert (
            obligation.case_id,
            obligation.source_activity_id,
            obligation.source_document_id,
            obligation.fee_domain,
            obligation.obligation_type,
            obligation.due_date,
            obligation.currency,
            obligation.source_status,
            obligation.created_by,
        ) == (
            CASE_ID,
            source_activity_id,
            DOCUMENT_ID,
            "GOV",
            "IC_LAYOUT_RESTORE_RIGHT_REQUESTED",
            None,
            "CNY",
            "VERIFIED",
            ACTOR_ID,
        )
        line = transaction.scalars(select(FeeObligationLine)).one()
        assert (
            line.fee_code,
            line.fee_name,
            line.fee_year_key,
            line.official_full_amount,
            line.reduction_ratio,
            line.payable_amount,
            line.source_amount,
            line.source_date,
            line.difference_review_state,
        ) == (
            "IC_LAYOUT_RESTORATION_REQUEST_FEE",
            "恢复布图设计登记权利请求费",
            0,
            Decimal("500.00"),
            Decimal("0.0000"),
            Decimal("500.00"),
            None,
            SUBMITTED_AT.date(),
            "MATCHED",
        )
        assert _fee_counts(transaction) == (1, 1, 0, 0, 0)
        assert [
            activity.activity_type
            for activity in transaction.scalars(
                select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
            )
        ] == [
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            "FEE_OBLIGATION_RECOGNIZED",
        ]
    finally:
        transaction.close()


def test_loss_of_right_notice_alone_is_conflict_and_writes_no_fee(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        _seed_reviewed_final_evidence(
            transaction,
            lineage_key=LOSS_NOTICE_LINEAGE,
            direction="IN",
        )
        source_activity_id = _finalize(transaction)
        _, recognize = _boundary()

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "IC_LAYOUT_RESTORE_RIGHT_SOURCE_CONFLICT"
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0)
        assert [
            activity.activity_type
            for activity in transaction.scalars(
                select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
            )
        ] == ["DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED"]
    finally:
        transaction.close()
