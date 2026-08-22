from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import GovPayment, PayList
from app.modules.annuity.service import register_gov_payment
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
)
from app.modules.masterdata.clients.models import Client

CASE_ID = "case-gov-payment-adapter"
CLIENT_ID = "client-gov-payment-adapter"
ACTOR_ID = "actor-gov-payment-adapter"
SOURCE_ACTIVITY_ID = "activity-gov-payment-source"
OBLIGATION_ID = "obligation-gov-payment"
OBLIGATION_LINE_ID = "line-gov-payment"
FEE_DRAFT_ID = "draft-gov-payment"
FEE_ITEM_ID = "item-gov-payment"


def test_registration_links_payment_and_appends_one_fee_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        transaction.add(Client(id=CLIENT_ID, name_cn="缴费活动客户"))
        transaction.flush()
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="NO-GOV-PAYMENT-ACTIVITY",
                client_id=CLIENT_ID,
                status="OPEN",
                lifecycle_revision=1,
            )
        )
        transaction.flush()
        transaction.add(
            CaseActivityEvent(
                id=SOURCE_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane="FEE",
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                occurred_at=datetime(2026, 7, 15, 9, 0),
                effective_at=datetime(2026, 7, 15, 9, 0),
                confirmation_status="CONFIRMED",
                actor_id=ACTOR_ID,
                idempotency_key="recognize:gov-payment-adapter",
                payload_json="{}",
            )
        )
        transaction.add(
            FeeObligation(
                id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_domain="GOV",
                obligation_type="PATENT_APPLICATION",
                obligation_status=FeeObligationStatus.RECOGNIZED.value,
                due_date=date(2026, 8, 15),
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status=FeeClientInstructionStatus.PAY.value,
                draft_status=FeeObligationDraftStatus.CREATED.value,
                payment_status=FeePaymentStatus.UNPAID.value,
                official_evidence_status=FeeOfficialEvidenceStatus.PENDING.value,
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        transaction.add(
            FeeObligationLine(
                id=OBLIGATION_LINE_ID,
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_code="APPLICATION_FEE",
                fee_name="申请费",
                fee_year_key=0,
                official_full_amount=Decimal("500.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("500.00"),
                source_amount=Decimal("500.00"),
                source_date=date(2026, 7, 15),
                difference_review_state=FeeDifferenceReviewState.MATCHED.value,
                current_identity_key="gov-payment-adapter-line",
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        transaction.add(
            FeeDraft(
                id=FEE_DRAFT_ID,
                case_id=CASE_ID,
                client_id=CLIENT_ID,
                currency="CNY",
                total_gov=Decimal("500.00"),
                amount=Decimal("500.00"),
            )
        )
        transaction.add(
            FeeItem(
                id=FEE_ITEM_ID,
                draft_id=FEE_DRAFT_ID,
                case_id=CASE_ID,
                fee_code="APPLICATION_FEE",
                fee_name="申请费",
                fee_type="GOV",
                amount=Decimal("500.00"),
            )
        )
        transaction.flush()
        transaction.add(
            FeeObligationDraftItemLink(
                obligation_line_id=OBLIGATION_LINE_ID,
                fee_item_id=FEE_ITEM_ID,
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        pay_list = PayList(
            client_id=CLIENT_ID,
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("500.00"),
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
        transaction.add(pay_list)
        transaction.flush()
        payment = GovPayment(
            pay_list_id=pay_list.id,
            case_id=CASE_ID,
            fee_item_id=FEE_ITEM_ID,
            status="PLANNED",
            currency="CNY",
            paid_amount=Decimal("500.00"),
            planned_amt=Decimal("500.00"),
            planned_currency="CNY",
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
        transaction.add(payment)
        transaction.commit()

        result = register_gov_payment(
            transaction,
            pay_list_id=pay_list.id,
            fee_item_id=FEE_ITEM_ID,
            paid_date=date(2026, 7, 15),
            paid_amount=Decimal("500.00"),
            actor_id=ACTOR_ID,
        )

        evidence_links = transaction.scalars(select(FeeObligationPaymentEvidenceLink)).all()
        payment_activities = transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == CASE_ID,
                CaseActivityEvent.lane == "FEE",
                CaseActivityEvent.activity_type == "PAYMENT_RECORDED",
            )
        ).all()
        obligation = transaction.get(FeeObligation, OBLIGATION_ID)

        assert result["gov_payment"]["id"] == payment.id
        assert len(evidence_links) == 1
        assert evidence_links[0].obligation_line_id == OBLIGATION_LINE_ID
        assert evidence_links[0].gov_payment_id == payment.id
        assert len(payment_activities) == 1
        activity = payment_activities[0]
        assert activity.source_activity_id == SOURCE_ACTIVITY_ID
        assert activity.old_business_stage is None
        assert activity.new_business_stage is None
        assert activity.old_official_procedure_stage is None
        assert activity.new_official_procedure_stage is None
        assert activity.old_legal_status is None
        assert activity.new_legal_status is None
        assert json.loads(activity.payload_json) == {
            "gov_payment_id": payment.id,
            "obligation_id": OBLIGATION_ID,
            "obligation_line_ids": [OBLIGATION_LINE_ID],
            "schema": "FPMS_GOV_PAYMENT_RECORDED_V1",
        }
        assert obligation is not None
        assert obligation.payment_status == FeePaymentStatus.PAID.value
        assert obligation.official_evidence_status == FeeOfficialEvidenceStatus.PENDING.value
