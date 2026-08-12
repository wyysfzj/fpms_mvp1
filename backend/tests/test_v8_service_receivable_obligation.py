from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import (
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees import obligation_service as service
from app.modules.fees.models import (
    FeeDraft,
    FeeObligation,
    FeeObligationLine,
    ServicePriceBook,
)
from app.modules.fees.obligation_contracts import FeeDomain, FeeOfficialEvidenceStatus
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateStatus,
    RecordDecisionGateCommand,
    record_decision_gate,
)

NOW = datetime(2026, 8, 13, 16, 0)
CREATOR_ID = "00000000-0000-4000-8000-000000000224"
CASE_A = "case-service-receivable-a"
CASE_B = "case-service-receivable-b"
ITEM_CODE = "S" * 128
PRICE_BOOK_ID = "11111111-1111-4111-8111-111111111228"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _case(case_id: str) -> Case:
    return Case(
        id=case_id,
        case_no=f"NO-{case_id}",
        status="OPEN",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
        lifecycle_revision=0,
    )


def _seed_active_book_and_gate(transaction: Session) -> tuple[ServicePriceBook, str]:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    transaction.add(
        T_User(
            id=CREATOR_ID,
            username=f"service-price-creator-{uuid4()}",
            password_hash="test-only",
            is_active=True,
        )
    )
    transaction.add_all((_case(CASE_A), _case(CASE_B)))
    snapshot = _canonical_json(
        {
            "currency": "CNY",
            "discount_policy": "NONE",
            "items": [{"item_code": ITEM_CODE, "unit_price": "3000.00"}],
            "scope_key": "GLOBAL",
            "tax_policy": "EXCLUSIVE",
        }
    )
    row = ServicePriceBook(
        id=PRICE_BOOK_ID,
        source_classification="PRODUCTION",
        book_version="2026.08",
        scope_key="GLOBAL",
        currency="CNY",
        tax_policy="EXCLUSIVE",
        discount_policy="NONE",
        source_reference="managed://service-price-books/2026-08.json",
        source_content_hash="a" * 64,
        item_snapshot=snapshot,
        item_snapshot_hash=hashlib.sha256(snapshot.encode()).hexdigest(),
        item_count=1,
        status="ACTIVE",
        approved_by=actor_id,
        approved_at=NOW - timedelta(minutes=1),
        approval_reason="客户完整价格版本已独立复核",
        activated_by=actor_id,
        activated_at=NOW - timedelta(minutes=1),
        effective_from=NOW - timedelta(days=1),
        effective_to=NOW + timedelta(days=365),
        idempotency_key="import-service-price-2026-08",
        current_identity_key="GLOBAL",
        created_by=CREATOR_ID,
        updated_by=actor_id,
        updated_at=NOW - timedelta(minutes=1),
    )
    transaction.add(row)
    transaction.flush()
    decision_value = service._activation_snapshot(row)
    record_decision_gate(
        RecordDecisionGateCommand(
            gate_code=DecisionGateCode.SERVICE_RATE_VERSION,
            scope_key="GLOBAL",
            decision_value=decision_value,
            decision_status=DecisionGateStatus.CONFIRMED,
            source_reference=row.source_reference,
            source_version=row.book_version,
            confirmed_by=actor_id,
            effective_at=NOW - timedelta(minutes=1),
            idempotency_key="gate-service-price-2026-08",
            expected_current_gate_id=None,
        ),
        transaction,
    )
    transaction.commit()
    return row, actor_id


def _command(
    actor_id: str,
    *,
    case_id: str = CASE_A,
    recognized_at: datetime = NOW,
) -> service.CreateServiceReceivableObligationCommand:
    return service.CreateServiceReceivableObligationCommand(
        price_book_version_id=PRICE_BOOK_ID,
        item_code=ITEM_CODE,
        case_id=case_id,
        actor_id=actor_id,
        idempotency_key="service-receivable-1",
        recognized_at=recognized_at,
    )


def _count(transaction: Session, model: type) -> int:
    return int(transaction.scalar(select(func.count()).select_from(model)) or 0)


def test_active_item_creates_service_obligation_and_caller_owns_transaction(
    session_factory: sessionmaker,
) -> None:
    with session_factory(expire_on_commit=False) as transaction:
        _book, actor_id = _seed_active_book_and_gate(transaction)
        result = service.create_service_receivable_obligation(
            _command(actor_id),
            transaction,
        )

        header = transaction.get(FeeObligation, result.recognition.obligation.id)
        line = transaction.scalar(
            select(FeeObligationLine).where(
                FeeObligationLine.obligation_id == result.recognition.obligation.id
            )
        )
        source = transaction.get(CaseActivityEvent, result.source_activity_id)
        assert header is not None and line is not None and source is not None
        assert result.item_code == ITEM_CODE
        assert json.loads(source.payload_json)["item_code"] == ITEM_CODE
        assert line.fee_name == ITEM_CODE
        mapped_code = service._service_receivable_fee_code(ITEM_CODE)
        assert mapped_code == service._service_receivable_fee_code(ITEM_CODE)
        assert mapped_code != service._service_receivable_fee_code("T" * 128)
        assert line.fee_code == hashlib.sha256(ITEM_CODE.encode()).hexdigest() == mapped_code
        assert len(line.fee_code) == 64 and line.fee_code != ITEM_CODE[:64]
        assert header.fee_domain == FeeDomain.SERVICE.value
        assert header.official_evidence_status == FeeOfficialEvidenceStatus.NOT_APPLICABLE.value
        assert line.official_full_amount is None
        assert line.payable_amount == line.source_amount == 3000
        assert _count(transaction, FeeDraft) == 0

        obligation_id = header.id
        source_id = source.id
        transaction.rollback()

    with session_factory() as verification:
        assert verification.get(FeeObligation, obligation_id) is None
        assert verification.get(CaseActivityEvent, source_id) is None


def test_idempotency_key_is_globally_owned_across_cases(
    session_factory: sessionmaker,
) -> None:
    with session_factory(expire_on_commit=False) as transaction:
        _book, actor_id = _seed_active_book_and_gate(transaction)
        first = service.create_service_receivable_obligation(_command(actor_id), transaction)
        before = (
            _count(transaction, FeeObligation),
            _count(transaction, FeeObligationLine),
            _count(transaction, CaseActivityEvent),
        )

        with pytest.raises(BusinessError) as caught:
            service.create_service_receivable_obligation(
                _command(actor_id, case_id=CASE_B),
                transaction,
            )

        assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
        assert caught.value.status_code == 409
        assert (
            _count(transaction, FeeObligation),
            _count(transaction, FeeObligationLine),
            _count(transaction, CaseActivityEvent),
        ) == before
        replay = service.create_service_receivable_obligation(
            _command(actor_id, recognized_at=NOW + timedelta(seconds=5)),
            transaction,
        )
        assert replay.reused is True
        assert replay.recognition.obligation.id == first.recognition.obligation.id
        transaction.rollback()


def test_noncanonical_book_hash_is_409_without_receivable_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory(expire_on_commit=False) as transaction:
        _book, actor_id = _seed_active_book_and_gate(transaction)
        transaction.execute(
            update(ServicePriceBook)
            .where(ServicePriceBook.id == PRICE_BOOK_ID)
            .values(item_snapshot_hash="f" * 64)
        )
        transaction.commit()
        before_activities = _count(transaction, CaseActivityEvent)

        with pytest.raises(BusinessError) as caught:
            service.create_service_receivable_obligation(_command(actor_id), transaction)

        assert caught.value.code == "SERVICE_RECEIVABLE_CONFLICT"
        assert caught.value.status_code == 409
        assert _count(transaction, FeeObligation) == 0
        assert _count(transaction, FeeObligationLine) == 0
        assert _count(transaction, CaseActivityEvent) == before_activities
