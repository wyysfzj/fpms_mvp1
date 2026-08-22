from __future__ import annotations

import importlib
import inspect
from datetime import date, datetime
from decimal import Decimal
from types import ModuleType

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)
from app.modules.masterdata.clients.models import Client

CASE_ID = "case-legacy-fee-truth"
CLIENT_ID = "client-legacy-fee-truth"
ACTOR_ID = "actor-legacy-fee-truth"


def _api() -> ModuleType:
    try:
        return importlib.import_module("scripts.backfill_v8_fee_truth")
    except ModuleNotFoundError:
        pytest.fail("legacy fee-truth linker public seam is missing")


def _seed_case(transaction: Session) -> None:
    transaction.add_all(
        [
            Case(id=CASE_ID, case_no="LEGACY-FEE-TRUTH", status="OPEN"),
            Client(id=CLIENT_ID, name_cn="旧费用真值客户"),
        ]
    )
    transaction.flush()
    transaction.add(PayList(id=801, client_id=CLIENT_ID))
    transaction.flush()


def _seed_source(
    transaction: Session,
    *,
    suffix: str,
    fee_code: str,
    fee_year: int,
    candidate_count: int,
    payment_id: int | None,
) -> tuple[str, str]:
    source_activity_id = f"source-{suffix}"
    transaction.add(
        CaseActivityEvent(
            id=source_activity_id,
            case_id=CASE_ID,
            sequence=int(suffix),
            lane="FEE",
            activity_type="LEGACY_FEE_SOURCE",
            occurred_at=datetime(2026, 7, int(suffix), 9, 0),
            effective_at=datetime(2026, 7, int(suffix), 9, 0),
            confirmation_status="CONFIRMED",
            actor_id=ACTOR_ID,
            idempotency_key=f"legacy-fee-source:{suffix}",
            payload_json="{}",
        )
    )
    draft_id = f"draft-{suffix}"
    fee_item_id = f"fee-item-{suffix}"
    transaction.add(
        FeeDraft(
            id=draft_id,
            case_id=CASE_ID,
            draft_type="GENERIC",
            currency="CNY",
            status="OPEN",
            amount=Decimal("500.00"),
        )
    )
    transaction.flush()
    transaction.add(
        FeeItem(
            id=fee_item_id,
            draft_id=draft_id,
            case_id=CASE_ID,
            fee_code=fee_code,
            fee_name="旧费用",
            fee_type="GOV",
            year_no=fee_year,
            amount=Decimal("500.00"),
        )
    )
    for ordinal in range(candidate_count):
        obligation_id = f"obligation-{suffix}-{ordinal}"
        line_id = f"line-{suffix}-{ordinal}"
        transaction.add(
            FeeObligation(
                id=obligation_id,
                case_id=CASE_ID,
                source_activity_id=source_activity_id,
                fee_domain="GOV",
                obligation_type="LEGACY_FEE",
                obligation_status="RECOGNIZED",
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PAY",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="PENDING",
            )
        )
        transaction.flush()
        transaction.add(
            FeeObligationLine(
                id=line_id,
                obligation_id=obligation_id,
                case_id=CASE_ID,
                source_activity_id=source_activity_id,
                fee_code=fee_code,
                fee_name="旧费用",
                fee_year_key=fee_year,
                official_full_amount=Decimal("500.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("500.00"),
                source_amount=Decimal("500.00"),
                source_date=date(2026, 7, int(suffix)),
                difference_review_state="MATCHED",
            )
        )
    if payment_id is not None:
        transaction.add(
            GovPayment(
                id=payment_id,
                pay_list_id=801,
                case_id=CASE_ID,
                fee_item_id=fee_item_id,
                status="RECORDED",
                currency="CNY",
                paid_date=date(2026, 7, int(suffix)),
                paid_amount=Decimal("500.00"),
                fee_code=fee_code,
                year_no=fee_year,
            )
        )
    transaction.commit()
    return source_activity_id, fee_item_id


def _row(
    api: ModuleType,
    *,
    source_activity_id: str,
    fee_item_id: str,
    fee_code: str,
    fee_year_key: int,
    gov_payment_id: int | None,
):
    return api.LegacyFeeTruthMigrationRow(
        case_id=CASE_ID,
        source_activity_id=source_activity_id,
        fee_code=fee_code,
        fee_year_key=fee_year_key,
        fee_item_id=fee_item_id,
        gov_payment_id=gov_payment_id,
    )


def _link_counts(transaction: Session) -> tuple[int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligationDraftItemLink)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationPaymentEvidenceLink)) or 0,
    )


def test_public_seam_is_exact_keyword_only_and_synchronous() -> None:
    api = _api()
    signature = inspect.signature(api.link_legacy_fee_truth)

    assert tuple(signature.parameters) == (
        "transaction",
        "rows",
        "dry_run",
        "expected_plan_sha256",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert signature.parameters["expected_plan_sha256"].default is None


def test_dry_run_links_only_unique_same_case_source_fee_and_year(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        unique_source, unique_item = _seed_source(
            transaction,
            suffix="1",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=811,
        )
        ambiguous_source, ambiguous_item = _seed_source(
            transaction,
            suffix="2",
            fee_code="ANNUITY",
            fee_year=2,
            candidate_count=2,
            payment_id=None,
        )
        unmatched_source, unmatched_item = _seed_source(
            transaction,
            suffix="3",
            fee_code="RESTORATION",
            fee_year=0,
            candidate_count=0,
            payment_id=None,
        )
        obligation_count = transaction.scalar(select(func.count()).select_from(FeeObligation))
        rows = (
            _row(
                api,
                source_activity_id=unmatched_source,
                fee_item_id=unmatched_item,
                fee_code="RESTORATION",
                fee_year_key=0,
                gov_payment_id=None,
            ),
            _row(
                api,
                source_activity_id=unique_source,
                fee_item_id=unique_item,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=811,
            ),
            _row(
                api,
                source_activity_id=ambiguous_source,
                fee_item_id=ambiguous_item,
                fee_code="ANNUITY",
                fee_year_key=2,
                gov_payment_id=None,
            ),
        )

        result = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )
        repeated = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        assert result == repeated
        assert tuple(row.fee_item_id for row in result.rows) == (
            unique_item,
            ambiguous_item,
            unmatched_item,
        )
        assert tuple(row.classification for row in result.rows) == (
            "LINKED",
            "AMBIGUOUS",
            "UNMATCHED",
        )
        assert (
            result.scanned,
            result.linked,
            result.unchanged,
            result.invalid,
            result.unmatched,
            result.ambiguous,
            result.planned_writes,
        ) == (3, 1, 0, 0, 1, 1, 2)
        assert all(
            len(value) == 64
            for value in (
                result.input_sha256,
                result.plan_sha256,
                result.output_sha256,
            )
        )
        assert _link_counts(transaction) == (0, 0)
        assert (
            transaction.scalar(select(func.count()).select_from(FeeObligation)) == obligation_count
        )


def test_apply_requires_exact_plan_is_idempotent_and_keeps_transaction_caller_owned(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        source_activity_id, fee_item_id = _seed_source(
            transaction,
            suffix="4",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=812,
        )
        rows = (
            _row(
                api,
                source_activity_id=source_activity_id,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=812,
            ),
        )
        plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )
        with monkeypatch.context() as caller_owned:
            caller_owned.setattr(transaction, "commit", lambda: pytest.fail("commit called"))
            caller_owned.setattr(transaction, "rollback", lambda: pytest.fail("rollback called"))
            caller_owned.setattr(transaction, "close", lambda: pytest.fail("close called"))

            applied = api.link_legacy_fee_truth(
                transaction=transaction,
                rows=rows,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            )
            replay = api.link_legacy_fee_truth(
                transaction=transaction,
                rows=rows,
                dry_run=True,
            )

            assert applied.rows[0].classification == "LINKED"
            assert applied.planned_writes == 2
            assert _link_counts(transaction) == (1, 1)
            assert replay.rows[0].classification == "UNCHANGED"
            assert replay.planned_writes == 0
            header = transaction.get(FeeObligation, "obligation-4-0")
            assert header is not None
            assert (
                header.draft_status,
                header.payment_status,
                header.official_evidence_status,
            ) == ("NOT_CREATED", "UNPAID", "PENDING")


def test_apply_rejects_mixed_plan_before_writing_valid_links(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        unique_source, unique_item = _seed_source(
            transaction,
            suffix="8",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=816,
        )
        unmatched_source, unmatched_item = _seed_source(
            transaction,
            suffix="9",
            fee_code="RESTORATION",
            fee_year=0,
            candidate_count=0,
            payment_id=None,
        )
        rows = (
            _row(
                api,
                source_activity_id=unique_source,
                fee_item_id=unique_item,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=816,
            ),
            _row(
                api,
                source_activity_id=unmatched_source,
                fee_item_id=unmatched_item,
                fee_code="RESTORATION",
                fee_year_key=0,
                gov_payment_id=None,
            ),
        )
        plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        with pytest.raises(BusinessError) as captured:
            api.link_legacy_fee_truth(
                transaction=transaction,
                rows=rows,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            )

        assert captured.value.status_code == 409
        assert captured.value.code == "LEGACY_FEE_TRUTH_PLAN_UNRESOLVED"
        assert _link_counts(transaction) == (0, 0)


def test_apply_rejects_a_stale_plan_without_writes(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        source_activity_id, fee_item_id = _seed_source(
            transaction,
            suffix="5",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=None,
        )
        rows = (
            _row(
                api,
                source_activity_id=source_activity_id,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=None,
            ),
        )
        plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )
        transaction.get(FeeItem, fee_item_id).fee_code = "CHANGED"
        transaction.flush()

        with pytest.raises(BusinessError) as captured:
            api.link_legacy_fee_truth(
                transaction=transaction,
                rows=rows,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            )

        assert captured.value.status_code == 409
        assert captured.value.code == "LEGACY_FEE_TRUTH_PLAN_STALE"
        assert _link_counts(transaction) == (0, 0)


def test_dry_run_rejects_cross_domain_fee_truth_link(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        source_activity_id, fee_item_id = _seed_source(
            transaction,
            suffix="6",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=813,
        )
        transaction.get(FeeItem, fee_item_id).fee_type = "SERVICE"
        transaction.commit()
        rows = (
            _row(
                api,
                source_activity_id=source_activity_id,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=813,
            ),
        )

        result = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        assert result.rows[0].classification == "INVALID"
        assert result.planned_writes == 0
        assert _link_counts(transaction) == (0, 0)


def test_apply_links_one_fee_item_to_multiple_payments_without_duplicate_draft_link(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        source_activity_id, fee_item_id = _seed_source(
            transaction,
            suffix="7",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=814,
        )
        transaction.add(
            GovPayment(
                id=815,
                pay_list_id=801,
                case_id=CASE_ID,
                fee_item_id=fee_item_id,
                status="RECORDED",
                currency="CNY",
                paid_date=date(2026, 7, 7),
                paid_amount=Decimal("500.00"),
                fee_code="APPLICATION_FEE",
                year_no=0,
            )
        )
        transaction.commit()
        rows = tuple(
            _row(
                api,
                source_activity_id=source_activity_id,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=payment_id,
            )
            for payment_id in (814, 815)
        )

        plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        assert tuple(row.planned_writes for row in plan.rows) == (2, 1)
        applied = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )
        replay = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        assert applied.planned_writes == 3
        assert _link_counts(transaction) == (1, 2)
        assert tuple(row.classification for row in replay.rows) == (
            "UNCHANGED",
            "UNCHANGED",
        )
        assert replay.planned_writes == 0


def test_payment_row_order_is_canonical_for_hashes_and_draft_link_ownership(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        source_activity_id, fee_item_id = _seed_source(
            transaction,
            suffix="7",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=814,
        )
        transaction.add(
            GovPayment(
                id=815,
                pay_list_id=801,
                case_id=CASE_ID,
                fee_item_id=fee_item_id,
                status="RECORDED",
                currency="CNY",
                paid_date=date(2026, 7, 7),
                paid_amount=Decimal("500.00"),
                fee_code="APPLICATION_FEE",
                year_no=0,
            )
        )
        transaction.commit()
        rows = tuple(
            _row(
                api,
                source_activity_id=source_activity_id,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=payment_id,
            )
            for payment_id in (814, 815)
        )

        forward = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )
        reversed_plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=tuple(reversed(rows)),
            dry_run=True,
        )

        assert reversed_plan == forward
        assert tuple(row.gov_payment_id for row in forward.rows) == (814, 815)
        assert tuple(row.planned_writes for row in forward.rows) == (2, 1)


def test_apply_rejects_one_fee_item_resolving_to_different_obligation_authorities(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_case(transaction)
        first_source, fee_item_id = _seed_source(
            transaction,
            suffix="8",
            fee_code="APPLICATION_FEE",
            fee_year=0,
            candidate_count=1,
            payment_id=816,
        )
        second_source = "source-9"
        transaction.add(
            CaseActivityEvent(
                id=second_source,
                case_id=CASE_ID,
                sequence=9,
                lane="FEE",
                activity_type="LEGACY_FEE_SOURCE",
                occurred_at=datetime(2026, 7, 9, 9, 0),
                effective_at=datetime(2026, 7, 9, 9, 0),
                confirmation_status="CONFIRMED",
                actor_id=ACTOR_ID,
                idempotency_key="legacy-fee-source:9",
                payload_json="{}",
            )
        )
        transaction.add(
            FeeObligation(
                id="obligation-9-0",
                case_id=CASE_ID,
                source_activity_id=second_source,
                fee_domain="GOV",
                obligation_type="LEGACY_FEE",
                obligation_status="RECOGNIZED",
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PAY",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="PENDING",
            )
        )
        transaction.flush()
        transaction.add(
            FeeObligationLine(
                id="line-9-0",
                obligation_id="obligation-9-0",
                case_id=CASE_ID,
                source_activity_id=second_source,
                fee_code="APPLICATION_FEE",
                fee_name="旧费用",
                fee_year_key=0,
                official_full_amount=Decimal("500.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("500.00"),
                source_amount=Decimal("500.00"),
                source_date=date(2026, 7, 9),
                difference_review_state="MATCHED",
            )
        )
        transaction.add(
            GovPayment(
                id=817,
                pay_list_id=801,
                case_id=CASE_ID,
                fee_item_id=fee_item_id,
                status="RECORDED",
                currency="CNY",
                paid_date=date(2026, 7, 9),
                paid_amount=Decimal("500.00"),
                fee_code="APPLICATION_FEE",
                year_no=0,
            )
        )
        transaction.commit()
        rows = (
            _row(
                api,
                source_activity_id=first_source,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=816,
            ),
            _row(
                api,
                source_activity_id=second_source,
                fee_item_id=fee_item_id,
                fee_code="APPLICATION_FEE",
                fee_year_key=0,
                gov_payment_id=817,
            ),
        )
        plan = api.link_legacy_fee_truth(
            transaction=transaction,
            rows=rows,
            dry_run=True,
        )

        assert tuple(row.classification for row in plan.rows) == (
            "LINKED",
            "AMBIGUOUS",
        )
        with pytest.raises(BusinessError) as captured:
            api.link_legacy_fee_truth(
                transaction=transaction,
                rows=rows,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            )

        assert captured.value.status_code == 409
        assert captured.value.code == "LEGACY_FEE_TRUTH_PLAN_UNRESOLVED"
        assert _link_counts(transaction) == (0, 0)
