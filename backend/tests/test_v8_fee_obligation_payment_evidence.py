from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from importlib import import_module, util
from inspect import Parameter, signature
from typing import get_type_hints
from unittest.mock import patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import (
    FeeObligation as FeeObligationModel,
)
from app.modules.fees.models import (
    FeeObligationLine as FeeObligationLineModel,
)
from app.modules.fees.models import (
    FeeObligationPaymentEvidenceLink,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
    RecordFeePaymentEvidenceCommand,
    RecordFeePaymentEvidenceResult,
)
from app.modules.masterdata.clients.models import Client

SERVICE_MODULE = "app.modules.fees.obligation_service"
SERVICE_SPEC = util.find_spec(SERVICE_MODULE)

CASE_ID = "case-payment-evidence"
OTHER_CASE_ID = "case-other-payment-evidence"
ACTIVITY_ID = "activity-payment-evidence"
OBLIGATION_ID = "obligation-payment-evidence"
LINE_ID = "line-payment-evidence"
ACTOR_ID = "actor-payment-evidence"
CLIENT_ID = "client-payment-evidence"
PAY_LIST_ID = 701
GOV_PAYMENT_ID = 702


def _seed_payment(transaction: Session, *, payment_case_id: str = CASE_ID) -> None:
    records = [
        Case(id=CASE_ID, case_no="NO-PAYMENT-EVIDENCE", status="OPEN"),
        Client(id=CLIENT_ID, name_cn="付款证据客户"),
    ]
    if payment_case_id != CASE_ID:
        records.append(
            Case(
                id=payment_case_id,
                case_no="NO-OTHER-PAYMENT-EVIDENCE",
                status="OPEN",
            )
        )
    transaction.add_all(records)
    transaction.flush()
    transaction.add(
        CaseActivityEvent(
            id=ACTIVITY_ID,
            case_id=CASE_ID,
            sequence=1,
            lane="FEE",
            activity_type="FEE_OBLIGATION_RECOGNIZED",
            occurred_at=datetime(2026, 7, 15, 9, 0),
            effective_at=datetime(2026, 7, 15, 9, 0),
            confirmation_status="CONFIRMED",
            actor_id=ACTOR_ID,
            idempotency_key="recognize:payment-evidence",
            payload_json="{}",
        )
    )
    transaction.add(PayList(id=PAY_LIST_ID, client_id=CLIENT_ID))
    transaction.flush()
    transaction.add(
        FeeObligationModel(
            id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=ACTIVITY_ID,
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
        GovPayment(
            id=GOV_PAYMENT_ID,
            pay_list_id=PAY_LIST_ID,
            case_id=payment_case_id,
            status="RECORDED",
            paid_date=date(2026, 7, 15),
            paid_amount=Decimal("500.00"),
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligationLineModel(
            id=LINE_ID,
            obligation_id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=ACTIVITY_ID,
            fee_code="APPLICATION_FEE",
            fee_name="申请费",
            fee_year_key=0,
            official_full_amount=Decimal("500.00"),
            reduction_ratio=Decimal("0.0000"),
            payable_amount=Decimal("500.00"),
            source_amount=Decimal("500.00"),
            source_date=date(2026, 7, 15),
            difference_review_state=FeeDifferenceReviewState.MATCHED.value,
            current_identity_key="payment-evidence-line",
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    transaction.commit()


def _command() -> RecordFeePaymentEvidenceCommand:
    return RecordFeePaymentEvidenceCommand(
        obligation_id=OBLIGATION_ID,
        obligation_line_ids=(LINE_ID,),
        gov_payment_id=GOV_PAYMENT_ID,
        actor_id=ACTOR_ID,
    )


def test_records_same_case_payment_idempotently_without_implying_official_evidence(
    session_factory: sessionmaker,
) -> None:
    assert SERVICE_SPEC is not None
    record_payment_evidence = import_module(SERVICE_MODULE).record_payment_evidence
    parameters = tuple(signature(record_payment_evidence).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == ("command", "transaction")
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
    )
    assert get_type_hints(record_payment_evidence) == {
        "command": RecordFeePaymentEvidenceCommand,
        "transaction": Session,
        "return": RecordFeePaymentEvidenceResult,
    }

    with session_factory() as transaction:
        _seed_payment(transaction)

        created = record_payment_evidence(_command(), transaction)
        replayed = record_payment_evidence(_command(), transaction)

        assert type(created) is RecordFeePaymentEvidenceResult
        assert len(created.links) == 1
        assert created.links[0].obligation_line_id == LINE_ID
        assert created.links[0].gov_payment_id == GOV_PAYMENT_ID
        assert created.links[0].reused is False
        assert replayed.links[0].id == created.links[0].id
        assert replayed.links[0].reused is True
        assert (
            transaction.scalar(select(func.count()).select_from(FeeObligationPaymentEvidenceLink))
            == 1
        )
        assert created.obligation.statuses.payment_status is FeePaymentStatus.PAID
        assert replayed.obligation.statuses.payment_status is FeePaymentStatus.PAID
        assert (
            created.obligation.statuses.official_evidence_status
            is FeeOfficialEvidenceStatus.PENDING
        )
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        assert header.payment_status == FeePaymentStatus.PAID.value
        assert header.official_evidence_status == FeeOfficialEvidenceStatus.PENDING.value


def test_rejects_cross_case_payment_before_flush_without_changing_states(
    session_factory: sessionmaker,
) -> None:
    record_payment_evidence = import_module(SERVICE_MODULE).record_payment_evidence

    with session_factory() as transaction:
        _seed_payment(transaction, payment_case_id=OTHER_CASE_ID)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        before = (header.payment_status, header.official_evidence_status)

        with patch.object(transaction, "flush", wraps=transaction.flush) as flush_spy:
            with pytest.raises(BusinessError) as captured:
                record_payment_evidence(_command(), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "FEE_PAYMENT_EVIDENCE_CASE_MISMATCH"
        flush_spy.assert_not_called()
        assert (
            transaction.scalar(select(func.count()).select_from(FeeObligationPaymentEvidenceLink))
            == 0
        )
        assert (header.payment_status, header.official_evidence_status) == before
        assert before == (
            FeePaymentStatus.UNPAID.value,
            FeeOfficialEvidenceStatus.PENDING.value,
        )
