from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from typing import get_type_hints
from unittest.mock import patch

import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.lifecycle_contracts import ActivityLane, ConfirmationStatus
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.models import Document
from app.modules.fees import obligation_service
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligationDraftItemLink,
    FeeObligation as FeeObligationModel,
    FeeObligationLine as FeeObligationLineModel,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
    FeePayListStatus,
    FeeSourceStatus,
)
from app.modules.masterdata.clients.models import Client

CASE_ID = "case-obligation-detail"
OTHER_CASE_ID = "case-obligation-detail-other"
CLIENT_ID = "client-obligation-detail"
SOURCE_ID = "source-obligation-detail"
RECOGNITION_ID = "recognition-obligation-detail"
DOCUMENT_ID = "document-obligation-detail"
OBLIGATION_ID = "obligation-detail"
EFFECTIVE_AT = datetime(2026, 7, 14, 12, 0)


def _identity(case_id: str, source_id: str, fee_code: str, fee_year_key: int) -> str:
    raw = f"{case_id}|{source_id}|{fee_code}|{fee_year_key}".encode()
    return hashlib.sha256(raw).hexdigest()


def _line_payload(
    *,
    fee_code: str,
    fee_name: str,
    fee_year_key: int,
    official_full_amount: Decimal | None,
    reduction_ratio: Decimal,
    payable_amount: Decimal,
    source_amount: Decimal | None,
    source_date: date | None,
    difference_review_state: str,
) -> dict[str, object]:
    return {
        "difference_review_state": difference_review_state,
        "fee_code": fee_code,
        "fee_name": fee_name,
        "fee_year_key": fee_year_key,
        "official_full_amount": (
            None if official_full_amount is None else format(official_full_amount, ".2f")
        ),
        "payable_amount": format(payable_amount, ".2f"),
        "reduction_ratio": format(reduction_ratio, ".4f"),
        "source_amount": None if source_amount is None else format(source_amount, ".2f"),
        "source_date": None if source_date is None else source_date.isoformat(),
    }


def _canonical_payload(
    *,
    obligation_id: str = OBLIGATION_ID,
    source_id: str = SOURCE_ID,
    lines: tuple[FeeObligationLineModel, ...],
    supersedes_obligation_id: str | None = None,
    supersede_reason: str | None = None,
) -> str:
    payload = {
        "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
        "obligation_id": obligation_id,
        "obligation": {
            "actor_id": "actor-obligation-detail",
            "case_id": CASE_ID,
            "currency": "CNY",
            "due_date": "2026-08-14",
            "fee_domain": "GOV",
            "lines": [
                _line_payload(
                    fee_code=line.fee_code,
                    fee_name=line.fee_name,
                    fee_year_key=line.fee_year_key,
                    official_full_amount=line.official_full_amount,
                    reduction_ratio=line.reduction_ratio,
                    payable_amount=line.payable_amount,
                    source_amount=line.source_amount,
                    source_date=line.source_date,
                    difference_review_state=line.difference_review_state,
                )
                for line in sorted(lines, key=lambda item: (item.fee_code, item.fee_year_key))
            ],
            "obligation_type": "PATENT_APPLICATION",
            "source_activity_id": source_id,
            "source_document_id": DOCUMENT_ID,
            "source_status": "VERIFIED",
            "supersede_reason": supersede_reason,
            "supersedes_obligation_id": supersedes_obligation_id,
        },
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _line(
    *,
    line_id: str,
    fee_code: str,
    fee_name: str,
    fee_year_key: int,
    obligation_id: str = OBLIGATION_ID,
    case_id: str = CASE_ID,
    source_id: str = SOURCE_ID,
    current: bool = True,
) -> FeeObligationLineModel:
    return FeeObligationLineModel(
        id=line_id,
        obligation_id=obligation_id,
        case_id=case_id,
        source_activity_id=source_id,
        fee_code=fee_code,
        fee_name=fee_name,
        fee_year_key=fee_year_key,
        official_full_amount=Decimal("900.00"),
        reduction_ratio=Decimal("0.8500"),
        payable_amount=Decimal("135.00"),
        source_amount=Decimal("135.00"),
        source_date=date(2026, 7, 14),
        difference_review_state=FeeDifferenceReviewState.MATCHED.value,
        current_identity_key=(
            _identity(case_id, source_id, fee_code, fee_year_key) if current else None
        ),
    )


def _seed_valid(
    transaction: Session,
    *,
    obligation_id: str = OBLIGATION_ID,
    obligation_status: FeeObligationStatus = FeeObligationStatus.RECOGNIZED,
) -> tuple[FeeObligationModel, tuple[FeeObligationLineModel, ...]]:
    transaction.add_all(
        (
            Client(id=CLIENT_ID, client_code="DETAIL", name_cn="详情客户"),
            Case(id=CASE_ID, case_no="DETAIL-1", client_id=CLIENT_ID, status="OPEN"),
            Case(id=OTHER_CASE_ID, case_no="DETAIL-2", client_id=CLIENT_ID, status="OPEN"),
        )
    )
    transaction.flush()
    transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"))
    source = CaseActivityEvent(
        id=SOURCE_ID,
        case_id=CASE_ID,
        sequence=1,
        lane=ActivityLane.DOCUMENT.value,
        activity_type="OFFICIAL_FEE_SOURCE_CONFIRMED",
        occurred_at=EFFECTIVE_AT,
        effective_at=EFFECTIVE_AT,
        confirmation_status=ConfirmationStatus.CONFIRMED.value,
        actor_id="actor-obligation-detail",
        reviewer_id="reviewer-obligation-detail",
        idempotency_key="source:obligation-detail",
        payload_json='{"source":"real"}',
    )
    transaction.add(source)
    transaction.flush()
    header = FeeObligationModel(
        id=obligation_id,
        case_id=CASE_ID,
        source_activity_id=SOURCE_ID,
        source_document_id=DOCUMENT_ID,
        fee_domain=FeeDomain.GOV.value,
        obligation_type="PATENT_APPLICATION",
        obligation_status=obligation_status.value,
        due_date=date(2026, 8, 14),
        currency="CNY",
        source_status=FeeSourceStatus.VERIFIED.value,
        client_instruction_status=FeeClientInstructionStatus.PAY.value,
        draft_status=FeeObligationDraftStatus.CREATED.value,
        payment_status=FeePaymentStatus.PAID.value,
        official_evidence_status=FeeOfficialEvidenceStatus.VERIFIED.value,
    )
    lines = (
        _line(
            line_id="line-detail-z",
            fee_code="GOV-Z",
            fee_name="后置费",
            fee_year_key=2,
            obligation_id=obligation_id,
            current=obligation_status is FeeObligationStatus.RECOGNIZED,
        ),
        _line(
            line_id="line-detail-a",
            fee_code="GOV-A",
            fee_name="前置费",
            fee_year_key=1,
            obligation_id=obligation_id,
            current=obligation_status is FeeObligationStatus.RECOGNIZED,
        ),
    )
    transaction.add_all((header, *lines))
    transaction.flush()
    transaction.add(
        CaseActivityEvent(
            id=RECOGNITION_ID,
            case_id=CASE_ID,
            sequence=2,
            lane=ActivityLane.FEE.value,
            activity_type="FEE_OBLIGATION_RECOGNIZED",
            source_activity_id=SOURCE_ID,
            occurred_at=EFFECTIVE_AT,
            effective_at=EFFECTIVE_AT,
            confirmation_status=ConfirmationStatus.CONFIRMED.value,
            actor_id="actor-obligation-detail",
            reviewer_id="reviewer-obligation-detail",
            idempotency_key="recognize:obligation-detail",
            payload_json=_canonical_payload(
                obligation_id=obligation_id,
                lines=lines,
            ),
        )
    )
    transaction.commit()
    transaction.expunge_all()
    return header, lines


def _seed_pay_list_relation(
    transaction: Session,
    *,
    line_id: str = "line-detail-a",
    draft_case_id: str = CASE_ID,
    draft_currency: str = "CNY",
    item_case_id: str = CASE_ID,
    item_fee_code: str = "GOV-A",
    item_year: int = 1,
    payment_case_id: str = CASE_ID,
    payment_currency: str = "CNY",
    pay_list_currency: str = "CNY",
    include_payment: bool = True,
) -> None:
    draft = FeeDraft(
        id="draft-obligation-detail",
        case_id=draft_case_id,
        client_id=CLIENT_ID,
        draft_type="OFFICIAL",
        currency=draft_currency,
    )
    item = FeeItem(
        id="item-obligation-detail",
        draft_id=draft.id,
        case_id=item_case_id,
        fee_code=item_fee_code,
        fee_name="官费项",
        fee_type="GOV",
        year_no=item_year,
        amount=Decimal("135.00"),
    )
    transaction.add_all(
        (
            draft,
            item,
            FeeObligationDraftItemLink(
                id="link-obligation-detail",
                obligation_line_id=line_id,
                fee_item_id=item.id,
            ),
        )
    )
    if include_payment:
        pay_list = PayList(
            client_id=CLIENT_ID,
            status="CANCELLED",
            currency=pay_list_currency,
            total_amount=Decimal("135.00"),
        )
        transaction.add(pay_list)
        transaction.flush()
        transaction.add(
            GovPayment(
                pay_list_id=pay_list.id,
                case_id=payment_case_id,
                fee_item_id=item.id,
                status="FAILED",
                currency=payment_currency,
                paid_amount=Decimal("0.00"),
            )
        )
    transaction.commit()
    transaction.expunge_all()


def _read(transaction: Session, obligation_id: object = OBLIGATION_ID) -> FeeObligation:
    return obligation_service.get_fee_obligation(obligation_id, transaction)  # type: ignore[arg-type]


def _expect_error(
    action: Callable[[], object],
    *,
    code: str,
    status_code: int,
    details: dict[str, object] | None = None,
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.code == code
    assert captured.value.status_code == status_code
    if details is not None:
        assert captured.value.details == details
    return captured.value


class _SelectSpy:
    def __init__(self, transaction: Session) -> None:
        self.statements: list[str] = []
        self._engine = transaction.get_bind()

    def __enter__(self) -> _SelectSpy:
        event.listen(self._engine, "before_cursor_execute", self._capture)
        return self

    def __exit__(self, *_args: object) -> None:
        event.remove(self._engine, "before_cursor_execute", self._capture)

    def _capture(
        self,
        _connection: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            self.statements.append(statement)


def test_get_fee_obligation_exposes_exact_synchronous_public_contract() -> None:
    service = getattr(obligation_service, "get_fee_obligation", None)

    assert service is not None
    assert not inspect.iscoroutinefunction(service)
    assert tuple(inspect.signature(service).parameters) == (
        "obligation_id",
        "transaction",
    )
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in inspect.signature(service).parameters.values()
    )
    assert get_type_hints(service) == {
        "obligation_id": str,
        "transaction": Session,
        "return": FeeObligation,
    }


@pytest.mark.parametrize(
    "invalid_id",
    (None, 1, b"id", "", " ", " leading", "trailing ", "nul\x00id", "x" * 37),
)
def test_request_validation_is_exact_and_executes_zero_sql(
    session_factory: sessionmaker,
    invalid_id: object,
) -> None:
    with session_factory() as transaction, _SelectSpy(transaction) as spy:
        error = _expect_error(
            lambda: _read(transaction, invalid_id),
            code="FEE_OBLIGATION_DETAIL_INVALID",
            status_code=400,
            details={"field": "obligation_id"},
        )

    assert error.details == {"field": "obligation_id"}
    assert spy.statements == []


def test_valid_length_36_id_reaches_one_header_lookup_unchanged(
    session_factory: sessionmaker,
) -> None:
    requested = "x" * 36
    with session_factory() as transaction, _SelectSpy(transaction) as spy:
        _expect_error(
            lambda: _read(transaction, requested),
            code="FEE_OBLIGATION_NOT_FOUND",
            status_code=404,
        )

    assert len(spy.statements) == 1


def test_missing_header_is_404_after_exactly_one_select(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction, _SelectSpy(transaction) as spy:
        _expect_error(
            lambda: _read(transaction, "missing-obligation"),
            code="FEE_OBLIGATION_NOT_FOUND",
            status_code=404,
        )

    assert len(spy.statements) == 1


def test_valid_gov_detail_returns_exact_projection_sorted_and_unchanged(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)

        with _SelectSpy(transaction) as spy:
            result = _read(transaction)

    assert type(result) is FeeObligation
    assert result.id == OBLIGATION_ID
    assert result.case_id == CASE_ID
    assert result.source.source_activity_id == SOURCE_ID
    assert result.source.source_document_id == DOCUMENT_ID
    assert result.source.status is FeeSourceStatus.VERIFIED
    assert result.fee_domain is FeeDomain.GOV
    assert result.obligation_type == "PATENT_APPLICATION"
    assert result.due_date == date(2026, 8, 14)
    assert result.currency == "CNY"
    assert result.statuses.estimate_status is None
    assert result.statuses.obligation_status is FeeObligationStatus.RECOGNIZED
    assert result.statuses.client_instruction_status is FeeClientInstructionStatus.PAY
    assert result.statuses.draft_status is FeeObligationDraftStatus.CREATED
    assert result.statuses.pay_list_status is FeePayListStatus.NOT_CREATED
    assert result.statuses.payment_status is FeePaymentStatus.PAID
    assert result.statuses.official_evidence_status is FeeOfficialEvidenceStatus.VERIFIED
    assert tuple((line.fee_code, line.fee_year_key, line.id) for line in result.lines) == (
        ("GOV-A", 1, "line-detail-a"),
        ("GOV-Z", 2, "line-detail-z"),
    )
    assert result.lines[0].official_full_amount == Decimal("900.00")
    assert result.lines[0].reduction_ratio == Decimal("0.8500")
    assert result.lines[0].payable_amount == Decimal("135.00")
    assert result.lines[0].source_amount == Decimal("135.00")
    assert result.lines[0].source_date == date(2026, 7, 14)
    assert len(spy.statements) == 4


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    (
        ("fee_domain", "WRONG"),
        ("source_status", "WRONG"),
        ("obligation_status", "WRONG"),
        ("client_instruction_status", "WRONG"),
        ("draft_status", "WRONG"),
        ("payment_status", "WRONG"),
        ("official_evidence_status", "WRONG"),
    ),
)
def test_each_malformed_stored_header_enum_fails_closed(
    session_factory: sessionmaker,
    field: str,
    invalid_value: str,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.execute(
            FeeObligationModel.__table__.update()
            .where(FeeObligationModel.id == OBLIGATION_ID)
            .values({field: invalid_value})
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_zero_lines_fails_as_stored_state_corruption(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.execute(
            FeeObligationLineModel.__table__.delete().where(
                FeeObligationLineModel.obligation_id == OBLIGATION_ID
            )
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


@pytest.mark.parametrize(
    "values",
    (
        {"difference_review_state": "WRONG"},
        {"fee_name": ""},
        {"fee_code": ""},
        {"fee_year_key": -1},
        {"payable_amount": Decimal("-0.01")},
        {"reduction_ratio": Decimal("1.1000")},
        {"current_identity_key": "wrong"},
        {"case_id": OTHER_CASE_ID},
        {"source_activity_id": "wrong-source"},
    ),
)
def test_each_malformed_or_cross_linked_line_fails_closed(
    session_factory: sessionmaker,
    values: dict[str, object],
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.connection().exec_driver_sql("PRAGMA foreign_keys=OFF")
        transaction.execute(
            FeeObligationLineModel.__table__.update()
            .where(FeeObligationLineModel.id == "line-detail-a")
            .values(**values)
        )
        transaction.commit()
        transaction.connection().exec_driver_sql("PRAGMA foreign_keys=ON")

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_duplicate_line_identity_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.execute(
            FeeObligationLineModel.__table__.update()
            .where(FeeObligationLineModel.id == "line-detail-z")
            .values(fee_code="GOV-A", fee_year_key=1, current_identity_key="duplicate-shadow")
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_missing_recognition_is_stored_state_409_not_request_404(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.execute(
            CaseActivityEvent.__table__.delete().where(
                CaseActivityEvent.id == RECOGNITION_ID
            )
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("lane", "DOCUMENT"),
        ("activity_type", "WRONG"),
        ("source_activity_id", None),
        ("payload_json", "{}"),
        ("payload_json", '{"schema":"FPMS_FEE_OBLIGATION_RECOGNIZED_V1"}'),
    ),
)
def test_malformed_recognition_fails_closed(
    session_factory: sessionmaker,
    field: str,
    value: object,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        transaction.execute(
            CaseActivityEvent.__table__.update()
            .where(CaseActivityEvent.id == RECOGNITION_ID)
            .values({field: value})
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_duplicate_recognition_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        stored = transaction.scalar(
            select(CaseActivityEvent).where(CaseActivityEvent.id == RECOGNITION_ID)
        )
        assert stored is not None
        transaction.add(
            CaseActivityEvent(
                id="recognition-obligation-detail-dup",
                case_id=CASE_ID,
                sequence=3,
                lane=stored.lane,
                activity_type=stored.activity_type,
                source_activity_id=stored.source_activity_id,
                occurred_at=stored.occurred_at,
                effective_at=stored.effective_at,
                confirmation_status=stored.confirmation_status,
                actor_id=stored.actor_id,
                reviewer_id=stored.reviewer_id,
                idempotency_key="recognize:obligation-detail:dup",
                payload_json=stored.payload_json,
            )
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_complete_pay_list_chain_sets_created_without_status_inference(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        _seed_pay_list_relation(transaction)

        result = _read(transaction)

    assert result.statuses.pay_list_status is FeePayListStatus.CREATED
    assert result.statuses.payment_status is FeePaymentStatus.PAID
    assert result.statuses.official_evidence_status is FeeOfficialEvidenceStatus.VERIFIED


def test_orphaned_partial_pay_list_chain_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        _seed_pay_list_relation(transaction, include_payment=False)

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


@pytest.mark.parametrize(
    "relation_overrides",
    (
        {"draft_case_id": OTHER_CASE_ID},
        {"draft_currency": "USD"},
        {"item_case_id": OTHER_CASE_ID},
        {"item_fee_code": "GOV-WRONG"},
        {"item_year": 9},
        {"payment_case_id": OTHER_CASE_ID},
        {"payment_currency": "USD"},
        {"pay_list_currency": "USD"},
    ),
)
def test_each_cross_linked_pay_list_relation_fails_closed(
    session_factory: sessionmaker,
    relation_overrides: dict[str, object],
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        _seed_pay_list_relation(transaction, **relation_overrides)  # type: ignore[arg-type]

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )


def test_service_obligation_with_gov_pay_list_relation_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_valid(transaction)
        _seed_pay_list_relation(transaction)
        transaction.execute(
            FeeObligationModel.__table__.update()
            .where(FeeObligationModel.id == OBLIGATION_ID)
            .values(fee_domain=FeeDomain.SERVICE.value)
        )
        transaction.commit()

        _expect_error(
            lambda: _read(transaction),
            code="FEE_OBLIGATION_STORED_STATE_INVALID",
            status_code=409,
        )
