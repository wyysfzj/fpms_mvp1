from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.models import Document
from app.modules.fees.models import FeeObligation, FeeObligationLine

CASE_ID = "case-overlay-fees"
SOURCE_ACTIVITY_ID = "activity-overlay-fees-source"
RECOGNITION_ACTIVITY_ID = "activity-overlay-fees-recognition"
OBLIGATION_ID = "obligation-overlay-fees"
LINE_ID = "line-overlay-fees"
ACTOR_ID = "actor-overlay-fees"
DOCUMENT_ID = "document-overlay-fees"


def _identity() -> str:
    return hashlib.sha256(f"{CASE_ID}|{SOURCE_ACTIVITY_ID}|APPLICATION|1".encode()).hexdigest()


def _payload() -> str:
    return json.dumps(
        {
            "obligation_id": OBLIGATION_ID,
            "obligation": {
                "actor_id": ACTOR_ID,
                "case_id": CASE_ID,
                "currency": "CNY",
                "due_date": "2026-08-20",
                "fee_domain": "GOV",
                "lines": [
                    {
                        "difference_review_state": "MATCHED",
                        "fee_code": "APPLICATION",
                        "fee_name": "申请费",
                        "fee_year_key": 1,
                        "official_full_amount": "900.00",
                        "payable_amount": "135.00",
                        "reduction_ratio": "0.1500",
                        "source_amount": "135.00",
                        "source_date": "2026-08-01",
                    }
                ],
                "obligation_type": "PATENT_APPLICATION",
                "source_activity_id": SOURCE_ACTIVITY_ID,
                "source_document_id": DOCUMENT_ID,
                "source_status": "VERIFIED",
                "supersede_reason": None,
                "supersedes_obligation_id": None,
            },
            "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _seed(transaction: Session) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="OVERLAY-FEES",
            status="NOT_FILED",
            business_stage=BusinessStage.NEW_CASE.value,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
            legal_status=LegalStatus.NOT_ESTABLISHED.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=2,
        )
    )
    transaction.flush()
    transaction.add_all(
        (
            CaseActivityEvent(
                id=SOURCE_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane=ActivityLane.LIFECYCLE.value,
                activity_type="CASE_OPENED",
                occurred_at=datetime(2026, 8, 1, 9, 0),
                effective_at=datetime(2026, 8, 1, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                new_business_stage=BusinessStage.NEW_CASE.value,
                new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                actor_id=ACTOR_ID,
                idempotency_key="overlay-fees-source",
                payload_json="{}",
            ),
            Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"),
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligation(
            id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=SOURCE_ACTIVITY_ID,
            source_document_id=DOCUMENT_ID,
            fee_domain="GOV",
            obligation_type="PATENT_APPLICATION",
            obligation_status="RECOGNIZED",
            due_date=date(2026, 8, 20),
            currency="CNY",
            source_status="VERIFIED",
            client_instruction_status="PAY",
            draft_status="CREATED",
            payment_status="PAID",
            official_evidence_status="VERIFIED",
        )
    )
    transaction.flush()
    transaction.add_all(
        (
            FeeObligationLine(
                id=LINE_ID,
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_code="APPLICATION",
                fee_name="申请费",
                fee_year_key=1,
                official_full_amount=Decimal("900.00"),
                reduction_ratio=Decimal("0.1500"),
                payable_amount=Decimal("135.00"),
                source_amount=Decimal("135.00"),
                source_date=date(2026, 8, 1),
                difference_review_state="MATCHED",
                current_identity_key=_identity(),
            ),
            CaseActivityEvent(
                id=RECOGNITION_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=2,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                occurred_at=datetime(2026, 8, 1, 9, 0),
                effective_at=datetime(2026, 8, 1, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.NEW_CASE.value,
                new_business_stage=BusinessStage.NEW_CASE.value,
                old_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                old_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                actor_id=ACTOR_ID,
                idempotency_key="overlay-fees-recognition",
                payload_json=_payload(),
            ),
        )
    )
    transaction.commit()


def test_overlay_projects_recognized_fee_obligation_with_exact_money_and_statuses(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

    obligation = result.milestones[1].fee_obligations[0]
    assert obligation.obligation_id == OBLIGATION_ID
    assert obligation.statuses.client_instruction_status.value == "PAY"
    assert obligation.statuses.draft_status.value == "CREATED"
    assert obligation.statuses.pay_list_status.value == "NOT_CREATED"
    assert obligation.statuses.payment_status.value == "PAID"
    assert obligation.statuses.official_evidence_status.value == "VERIFIED"
    assert obligation.lines[0].official_full_amount == "900.00"
    assert obligation.lines[0].reduction_ratio == "0.1500"
    assert obligation.lines[0].payable_amount == "135.00"
    assert obligation.lines[0].source_amount == "135.00"
