from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.annuity.service import create_pay_list_from_fee_items
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
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

CASE_ID = "case-pay-list-create-activity"
CLIENT_ID = "client-pay-list-create-activity"
ACTOR_ID = "actor-pay-list-create-activity"
SOURCE_ACTIVITY_ID = "activity-pay-list-create-source"
SECOND_SOURCE_ACTIVITY_ID = "activity-pay-list-create-source-2"
OBLIGATION_ID = "obligation-pay-list-create"
SECOND_OBLIGATION_ID = "obligation-pay-list-create-2"
DRAFT_ID = "draft-pay-list-create"
LINE_IDS = ("line-pay-list-create-1", "line-pay-list-create-2")
ITEM_IDS = ("item-pay-list-create-1", "item-pay-list-create-2")


def _seed_pay_list_activity_context(
    transaction: Session,
    *,
    missing_link_item_id: str | None = None,
    split_source_activities: bool = False,
) -> None:
    transaction.add(Client(id=CLIENT_ID, name_cn="缴费清单活动客户"))
    transaction.flush()
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="NO-PAY-LIST-CREATE-ACTIVITY",
            client_id=CLIENT_ID,
            status="OPEN",
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
            legal_status=LegalStatus.APPLICATION_PENDING.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=2 if split_source_activities else 1,
        )
    )
    source_activity_ids = (
        (SOURCE_ACTIVITY_ID, SECOND_SOURCE_ACTIVITY_ID)
        if split_source_activities
        else (SOURCE_ACTIVITY_ID,)
    )
    for sequence, source_activity_id in enumerate(source_activity_ids, start=1):
        transaction.add(
            CaseActivityEvent(
                id=source_activity_id,
                case_id=CASE_ID,
                sequence=sequence,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                occurred_at=datetime(2026, 7, 25, 9, 0),
                effective_at=datetime(2026, 7, 25, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                old_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
                new_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
                old_legal_status=LegalStatus.APPLICATION_PENDING.value,
                new_legal_status=LegalStatus.APPLICATION_PENDING.value,
                actor_id=ACTOR_ID,
                idempotency_key=f"recognize:pay-list-create-activity:{sequence}",
                payload_json="{}",
            )
        )
    obligation_ids = (
        (OBLIGATION_ID, SECOND_OBLIGATION_ID) if split_source_activities else (OBLIGATION_ID,)
    )
    for obligation_id, source_activity_id in zip(obligation_ids, source_activity_ids, strict=True):
        transaction.add(
            FeeObligation(
                id=obligation_id,
                case_id=CASE_ID,
                source_activity_id=source_activity_id,
                fee_domain="GOV",
                obligation_type="PATENT_APPLICATION",
                obligation_status=FeeObligationStatus.RECOGNIZED.value,
                due_date=date(2026, 8, 25),
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
        FeeDraft(
            id=DRAFT_ID,
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            currency="CNY",
            total_gov=Decimal("800.00"),
            amount=Decimal("800.00"),
        )
    )
    for index, (line_id, item_id, amount) in enumerate(
        zip(LINE_IDS, ITEM_IDS, (Decimal("500.00"), Decimal("300.00")), strict=True)
    ):
        source_index = index if split_source_activities else 0
        transaction.add(
            FeeObligationLine(
                id=line_id,
                obligation_id=obligation_ids[source_index],
                case_id=CASE_ID,
                source_activity_id=source_activity_ids[source_index],
                fee_code=f"APPLICATION_FEE_{index + 1}",
                fee_name=f"申请费{index + 1}",
                fee_year_key=index,
                official_full_amount=amount,
                reduction_ratio=Decimal("0.0000"),
                payable_amount=amount,
                source_amount=amount,
                source_date=date(2026, 7, 25),
                difference_review_state=FeeDifferenceReviewState.MATCHED.value,
                current_identity_key=f"pay-list-create-line-{index + 1}",
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        transaction.add(
            FeeItem(
                id=item_id,
                draft_id=DRAFT_ID,
                case_id=CASE_ID,
                fee_code=f"APPLICATION_FEE_{index + 1}",
                fee_name=f"申请费{index + 1}",
                fee_type="GOV",
                amount=amount,
            )
        )
        transaction.flush()
        if item_id != missing_link_item_id:
            transaction.add(
                FeeObligationDraftItemLink(
                    obligation_line_id=line_id,
                    fee_item_id=item_id,
                    created_by=ACTOR_ID,
                    updated_by=ACTOR_ID,
                )
            )
    transaction.commit()


def _assert_no_pay_list_writes(transaction: Session) -> None:
    assert transaction.scalars(select(PayList)).all() == []
    assert transaction.scalars(select(GovPayment)).all() == []
    assert (
        transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.activity_type == "PAY_LIST_CREATED")
        ).all()
        == []
    )


def test_create_pay_list_appends_one_fee_activity_linked_to_obligation_lines(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_pay_list_activity_context(transaction)

        result = create_pay_list_from_fee_items(
            transaction,
            fee_item_ids=list(ITEM_IDS),
            planned_pay_date=date(2026, 8, 20),
            actor_id=ACTOR_ID,
        )

        activities = transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == CASE_ID,
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == "PAY_LIST_CREATED",
            )
        ).all()

        assert result["summary"]["pay_list_created"] is True
        assert len(activities) == 1
        activity = activities[0]
        assert activity.source_activity_id == SOURCE_ACTIVITY_ID
        assert activity.old_business_stage == activity.new_business_stage
        assert activity.old_official_procedure_stage == activity.new_official_procedure_stage
        assert activity.old_legal_status == activity.new_legal_status
        assert json.loads(activity.payload_json) == {
            "actor_id": ACTOR_ID,
            "center_changes": {},
            "fee_item_ids": list(ITEM_IDS),
            "obligation_ids": [OBLIGATION_ID],
            "obligation_line_ids": list(LINE_IDS),
            "pay_list_id": result["pay_list"]["id"],
            "schema": "FPMS_PAY_LIST_CREATED_V1",
        }


def test_create_pay_list_fails_closed_when_any_fee_item_lacks_obligation_link(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_pay_list_activity_context(
            transaction,
            missing_link_item_id=ITEM_IDS[1],
        )

        with pytest.raises(BusinessError) as exc_info:
            create_pay_list_from_fee_items(
                transaction,
                fee_item_ids=list(ITEM_IDS),
                planned_pay_date=date(2026, 8, 20),
                actor_id=ACTOR_ID,
            )

        assert exc_info.value.code == "PAY_LIST_OBLIGATION_LINK_REQUIRED"
        assert exc_info.value.status_code == 409
        _assert_no_pay_list_writes(transaction)


def test_create_pay_list_fails_closed_for_multiple_source_activities_in_one_case(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_pay_list_activity_context(transaction, split_source_activities=True)

        with pytest.raises(BusinessError) as exc_info:
            create_pay_list_from_fee_items(
                transaction,
                fee_item_ids=list(ITEM_IDS),
                planned_pay_date=date(2026, 8, 20),
                actor_id=ACTOR_ID,
            )

        assert exc_info.value.code == "PAY_LIST_SOURCE_ACTIVITY_CONFLICT"
        assert exc_info.value.status_code == 409
        _assert_no_pay_list_writes(transaction)


def test_create_pay_list_leaves_transaction_commit_to_caller(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_pay_list_activity_context(transaction)

        result = create_pay_list_from_fee_items(
            transaction,
            fee_item_ids=list(ITEM_IDS),
            planned_pay_date=date(2026, 8, 20),
            actor_id=ACTOR_ID,
        )
        pay_list_id = result["pay_list"]["id"]
        transaction.rollback()

    with session_factory() as verifier:
        assert verifier.get(PayList, pay_list_id) is None
        _assert_no_pay_list_writes(verifier)
