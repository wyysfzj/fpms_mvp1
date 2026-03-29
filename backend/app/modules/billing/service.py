from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.billing.models import (
    BadDebtRecovery,
    BadDebtVoucher,
    Bill,
    BillItem,
    CaseReceipt,
    Offset,
    Payment,
    PaymentLine,
)
from app.modules.billing.schemas import (
    BillBadDebtActionSchema,
    BillBadDebtRecoveryActionSchema,
    BillCreateSchema,
    BillFromDraftsRequest,
    BillManualCreateSchema,
    BillStatusSchema,
    CaseReceiptCreate,
    CaseReceiptUpdate,
    OffsetCreateSchema,
    PaymentSchema,
)
from app.modules.commission.service import (
    apply_commission_for_bill,
    recompute_commission_settleable,
)
from app.modules.consulting.service import filter_consulting_search_case_ids
from app.modules.fees.models import FeeDraft, FeeItem

logger = logging.getLogger(__name__)


def _run_commission_hook_non_blocking(db: Session, bill: Bill) -> None:
    """Apply commission in non-blocking mode without changing bill contracts."""
    try:
        summary = apply_commission_for_bill(
            db,
            bill_id=bill.id,
            actor_id=bill.created_by,
            strict=False,
        )
    except Exception:
        logger.exception(
            "Billing commission hook crashed unexpectedly; bill flow remains successful",
            extra={"bill_id": bill.id},
        )
        return

    status = summary.get("status", "FAILED_NON_BLOCKING")
    if status == "FAILED_NON_BLOCKING":
        err = summary.get("error") or {}
        logger.error(
            "Billing commission hook failed non-blocking",
            extra={
                "bill_id": bill.id,
                "status": status,
                "created_count": summary.get("created_count", 0),
                "updated_count": summary.get("updated_count", 0),
                "skipped_count": summary.get("skipped_count", 0),
                "error_code": err.get("code"),
                "error_message": err.get("message"),
            },
        )
        return

    logger.info(
        "Billing commission hook completed",
        extra={
            "bill_id": bill.id,
            "status": status,
            "created_count": summary.get("created_count", 0),
            "updated_count": summary.get("updated_count", 0),
            "skipped_count": summary.get("skipped_count", 0),
        },
    )


def _collect_service_case_ids_for_bill(db: Session, bill_id: str) -> list[str]:
    items = (
        db.query(BillItem).filter(BillItem.bill_id == bill_id, BillItem.case_id.isnot(None)).all()
    )
    service_case_ids: list[str] = []
    seen: set[str] = set()
    for item in items:
        fee_type = (item.fee_type or "").strip().upper()
        if fee_type != "SERVICE":
            continue
        case_id = item.case_id
        if not case_id or case_id in seen:
            continue
        seen.add(case_id)
        service_case_ids.append(case_id)
    return service_case_ids


def load_bill_bad_debt_chain(
    db: Session, bill_id: str
) -> tuple[BadDebtVoucher | None, list[BadDebtRecovery], Decimal, Decimal]:
    voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).first()
    if not voucher:
        return None, [], Decimal("0"), Decimal("0")

    recoveries = (
        db.query(BadDebtRecovery)
        .filter(BadDebtRecovery.voucher_id == voucher.id)
        .order_by(BadDebtRecovery.created_at.asc(), BadDebtRecovery.id.asc())
        .all()
    )
    recovered_total = sum((recovery.recovery_amount for recovery in recoveries), Decimal("0"))
    remaining_amount = voucher.bad_debt_amount - recovered_total
    if remaining_amount < Decimal("0"):
        remaining_amount = Decimal("0")
    return voucher, recoveries, recovered_total, remaining_amount


def _normalize_bad_debt_status_filter(bad_debt_status: str | None) -> str | None:
    if bad_debt_status is None:
        return None
    normalized = bad_debt_status.strip().upper()
    return normalized or None


def _summarize_bad_debt_bills(
    db: Session, bill_rows: list[tuple[str, str | None]]
) -> dict[str, Decimal | int]:
    summary = {
        "bad_debt_bill_count": 0,
        "bad_debt_amount": Decimal("0"),
        "total_recovered_amount": Decimal("0"),
        "remaining_bad_debt_balance": Decimal("0"),
    }
    if not bill_rows:
        return summary

    bad_debt_rows = [
        (bill_id, (bad_debt_status or "NONE").strip().upper())
        for bill_id, bad_debt_status in bill_rows
        if (bad_debt_status or "NONE").strip().upper() != "NONE"
    ]
    if not bad_debt_rows:
        return summary

    bill_ids = [bill_id for bill_id, _ in bad_debt_rows]
    voucher_rows = (
        db.query(
            BadDebtVoucher.bill_id,
            BadDebtVoucher.id,
            BadDebtVoucher.bad_debt_amount,
        )
        .filter(BadDebtVoucher.bill_id.in_(bill_ids))
        .all()
    )
    voucher_map = {voucher.bill_id: voucher for voucher in voucher_rows}
    voucher_ids = [voucher.id for voucher in voucher_rows]

    recovered_map: dict[str, Decimal] = {}
    if voucher_ids:
        recovery_rows = (
            db.query(
                BadDebtRecovery.voucher_id,
                func.coalesce(func.sum(BadDebtRecovery.recovery_amount), Decimal("0")),
            )
            .filter(BadDebtRecovery.voucher_id.in_(voucher_ids))
            .group_by(BadDebtRecovery.voucher_id)
            .all()
        )
        recovered_map = {
            voucher_id: Decimal(recovered_amount or 0)
            for voucher_id, recovered_amount in recovery_rows
        }

    for bill_id, _bad_debt_status in bad_debt_rows:
        summary["bad_debt_bill_count"] += 1
        voucher = voucher_map.get(bill_id)
        if not voucher:
            continue
        bad_debt_amount = Decimal(voucher.bad_debt_amount or 0)
        recovered_amount = recovered_map.get(voucher.id, Decimal("0"))
        remaining_amount = bad_debt_amount - recovered_amount
        if remaining_amount < Decimal("0"):
            remaining_amount = Decimal("0")

        summary["bad_debt_amount"] += bad_debt_amount
        summary["total_recovered_amount"] += recovered_amount
        summary["remaining_bad_debt_balance"] += remaining_amount

    return summary


def list_bills(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    bad_debt_status: str | None = None,
) -> tuple[list[Bill], int, dict[str, Decimal | int]]:
    query = db.query(Bill)
    normalized_bad_debt_status = _normalize_bad_debt_status_filter(bad_debt_status)
    if normalized_bad_debt_status is not None:
        query = query.filter(func.upper(Bill.bad_debt_status) == normalized_bad_debt_status)

    total = query.count()
    bills = (
        query.order_by(Bill.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )
    bill_rows = query.order_by(None).with_entities(Bill.id, Bill.bad_debt_status).all()
    summary = _summarize_bad_debt_bills(db, bill_rows)
    return bills, total, summary


def _get_bill_for_bad_debt_action(db: Session, bill_id: str) -> Bill:
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)
    return bill


def _validate_bad_debt_action_eligibility(
    bill: Bill, *, mode: str, bad_debt_voucher: BadDebtVoucher | None
) -> None:
    if (bill.direction or "").strip().upper() != "AR":
        raise_business_error(
            "BAD_DEBT_NOT_ALLOWED",
            "Only AR bills can be marked as bad debt",
            status_code=400,
        )

    balance = Decimal(bill.balance or 0)
    amount = Decimal(bill.amount or 0)
    if balance <= Decimal("0"):
        raise_business_error(
            "BAD_DEBT_NOT_ALLOWED",
            "Only bills with outstanding balance can be marked bad debt",
            status_code=400,
        )

    if mode == "TRANSFER" and balance >= amount:
        raise_business_error(
            "BAD_DEBT_NOT_ALLOWED",
            "Partial-payment transfer requires a partially settled bill",
            status_code=400,
        )

    if bad_debt_voucher and (bill.bad_debt_status or "NONE").upper() == "OPEN":
        return

    if (bill.status or "").strip().upper() == "SETTLED":
        raise_business_error(
            "BAD_DEBT_NOT_ALLOWED",
            "Settled bills cannot be marked as bad debt",
            status_code=400,
        )


def _ensure_bad_debt_voucher(
    db: Session,
    *,
    bill: Bill,
    bad_debt_date: date | None,
    remark: str | None,
) -> tuple[BadDebtVoucher, bool]:
    voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill.id).first()
    if voucher:
        return voucher, False

    voucher = BadDebtVoucher(
        id=str(uuid4()),
        bill_id=bill.id,
        status="OPEN",
        bad_debt_amount=Decimal(bill.balance or 0),
        recovered_amount=Decimal("0"),
        bad_debt_date=bad_debt_date or bill.bill_date or date.today(),
        remark=remark,
    )
    db.add(voucher)
    db.flush()
    return voucher, True


def apply_bill_bad_debt_action(
    db: Session, bill_id: str, data: BillBadDebtActionSchema | None = None
) -> Bill:
    bill = _get_bill_for_bad_debt_action(db, bill_id)
    mode = (data.mode if data else "MARK").strip().upper()
    bad_debt_voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill.id).first()

    _validate_bad_debt_action_eligibility(bill, mode=mode, bad_debt_voucher=bad_debt_voucher)

    if bad_debt_voucher:
        bill.status = "BAD_DEBT"
        if (bill.bad_debt_status or "NONE").upper() == "NONE":
            bill.bad_debt_status = "OPEN"
        if not bill.bad_debt_substatus:
            bill.bad_debt_substatus = "PARTIAL_TRANSFER" if mode == "TRANSFER" else "MANUAL_MARK"
        db.commit()
        db.refresh(bill)
        return bill

    voucher, _ = _ensure_bad_debt_voucher(
        db,
        bill=bill,
        bad_debt_date=data.bad_debt_date if data else None,
        remark=data.remark if data else None,
    )

    bill.status = "BAD_DEBT"
    bill.bad_debt_status = "OPEN"
    bill.bad_debt_substatus = "PARTIAL_TRANSFER" if mode == "TRANSFER" else "MANUAL_MARK"

    # Keep the master voucher aligned with the bill-level state.
    voucher.status = "OPEN"
    db.commit()
    db.refresh(bill)
    return bill


def apply_bill_bad_debt_recovery(
    db: Session, bill_id: str, data: BillBadDebtRecoveryActionSchema
) -> Bill:
    bill = _get_bill_for_bad_debt_action(db, bill_id)
    if (bill.direction or "").strip().upper() != "AR":
        raise_business_error(
            "BAD_DEBT_RECOVERY_NOT_ALLOWED",
            "Only AR bills can recover bad debt",
            status_code=400,
        )

    voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill.id).first()
    if not voucher:
        raise_business_error(
            "BAD_DEBT_VOUCHER_NOT_FOUND",
            "Bad debt voucher not found",
            status_code=400,
        )

    _, _, recovered_total, remaining_amount = load_bill_bad_debt_chain(db, bill.id)
    recovery_amount = Decimal(data.recovery_amount or 0)
    if recovery_amount > remaining_amount:
        raise_business_error(
            "BAD_DEBT_RECOVERY_EXCEEDS_REMAINING",
            "Recovery amount exceeds remaining bad debt amount",
            status_code=400,
        )

    recovery = BadDebtRecovery(
        id=str(uuid4()),
        voucher_id=voucher.id,
        recovery_amount=recovery_amount,
        recovery_date=data.recovery_date or date.today(),
        remark=data.remark,
    )
    db.add(recovery)

    updated_recovered_total = recovered_total + recovery_amount
    voucher.recovered_amount = updated_recovered_total
    if updated_recovered_total >= Decimal(voucher.bad_debt_amount or 0):
        voucher.status = "CLOSED"
        bill.bad_debt_status = "CLOSED"
        bill.bad_debt_substatus = "FULLY_RECOVERED"
        voucher.recovered_amount = Decimal(voucher.bad_debt_amount or 0)
    else:
        voucher.status = "OPEN"
        bill.bad_debt_status = "OPEN"
        bill.bad_debt_substatus = "PARTIAL_RECOVERY"

    db.commit()
    db.refresh(bill)
    return bill


def _run_commission_settleable_recompute_non_blocking(
    db: Session, *, bill_id: str, as_of_date: date | None
) -> None:
    case_ids = _collect_service_case_ids_for_bill(db, bill_id)
    if not case_ids:
        return

    try:
        summary = recompute_commission_settleable(
            db,
            case_ids=case_ids,
            as_of_date=as_of_date,
            strict=False,
        )
    except Exception:
        logger.exception(
            "Billing commission settleable recompute crashed unexpectedly",
            extra={"bill_id": bill_id, "case_count": len(case_ids)},
        )
        return

    status = summary.get("status", "FAILED_NON_BLOCKING")
    if status == "FAILED_NON_BLOCKING":
        err = summary.get("error") or {}
        logger.error(
            "Billing commission settleable recompute failed non-blocking",
            extra={
                "bill_id": bill_id,
                "status": status,
                "processed_count": summary.get("processed_count", 0),
                "updated_count": summary.get("updated_count", 0),
                "unchanged_count": summary.get("unchanged_count", 0),
                "error_code": err.get("code"),
                "error_message": err.get("message"),
            },
        )
        return

    logger.info(
        "Billing commission settleable recompute completed",
        extra={
            "bill_id": bill_id,
            "status": status,
            "processed_count": summary.get("processed_count", 0),
            "updated_count": summary.get("updated_count", 0),
            "unchanged_count": summary.get("unchanged_count", 0),
        },
    )


def _run_consulting_commission_recompute_non_blocking(
    db: Session, *, bill_id: str, as_of_date: date | None
) -> None:
    service_case_ids = _collect_service_case_ids_for_bill(db, bill_id)
    consulting_case_ids = filter_consulting_search_case_ids(db, service_case_ids)
    if not consulting_case_ids:
        return

    try:
        summary = recompute_commission_settleable(
            db,
            case_ids=consulting_case_ids,
            as_of_date=as_of_date,
            strict=False,
        )
    except Exception:
        logger.exception(
            "Billing consulting commission settleable recompute crashed unexpectedly",
            extra={"bill_id": bill_id, "case_count": len(consulting_case_ids)},
        )
        return

    status = summary.get("status", "FAILED_NON_BLOCKING")
    if status == "FAILED_NON_BLOCKING":
        err = summary.get("error") or {}
        logger.error(
            "Billing consulting commission settleable recompute failed non-blocking",
            extra={
                "bill_id": bill_id,
                "status": status,
                "case_count": len(consulting_case_ids),
                "processed_count": summary.get("processed_count", 0),
                "updated_count": summary.get("updated_count", 0),
                "unchanged_count": summary.get("unchanged_count", 0),
                "error_code": err.get("code"),
                "error_message": err.get("message"),
            },
        )
        return

    logger.info(
        "Billing consulting commission settleable recompute completed",
        extra={
            "bill_id": bill_id,
            "status": status,
            "case_count": len(consulting_case_ids),
            "processed_count": summary.get("processed_count", 0),
            "updated_count": summary.get("updated_count", 0),
            "unchanged_count": summary.get("unchanged_count", 0),
        },
    )


def _validate_single_client(client_ids: list[str | None]) -> str:
    unique_ids = {client_id for client_id in client_ids if client_id}
    if len(unique_ids) != 1:
        raise_business_error(
            "BILL_SINGLE_CLIENT_REQUIRED",
            "Bill must be associated with a single client",
            status_code=400,
        )
    return unique_ids.pop()


def _validate_currency_consistency(bill_currency: str, item_currencies: list[str | None]) -> None:
    unique_currencies = {currency for currency in item_currencies if currency}
    if not unique_currencies:
        return
    if len(unique_currencies) != 1 or bill_currency not in unique_currencies:
        raise_business_error(
            "BILL_CURRENCY_MISMATCH",
            "Bill item currency must match bill currency",
            status_code=400,
        )


def _apply_bill_status(bill: Bill, next_status: str) -> None:
    allowed_statuses = {"UNSETTLED", "PARTIALLY_SETTLED", "SETTLED"}
    if next_status not in allowed_statuses:
        raise_business_error(
            "BILL_STATUS_INVALID",
            "Bill status is invalid",
            status_code=400,
        )

    current_status = bill.status
    if current_status is None:
        bill.status = next_status
        return
    if current_status not in allowed_statuses:
        raise_business_error(
            "BILL_STATUS_INVALID",
            "Bill status is invalid",
            status_code=400,
        )

    allowed_transitions = {
        "UNSETTLED": {"UNSETTLED", "PARTIALLY_SETTLED", "SETTLED"},
        "PARTIALLY_SETTLED": {"PARTIALLY_SETTLED", "SETTLED", "UNSETTLED"},
        "SETTLED": {"SETTLED", "PARTIALLY_SETTLED", "UNSETTLED"},
    }
    if next_status not in allowed_transitions[current_status]:
        raise_business_error(
            "BILL_STATUS_TRANSITION_INVALID",
            "Invalid bill status transition",
            status_code=400,
        )
    bill.status = next_status


def _allocate_offset_to_receipts(
    db: Session, bill: Bill, offset_amt: Decimal, offset_date: date | None
) -> None:
    items = (
        db.query(BillItem).filter(BillItem.bill_id == bill.id, BillItem.case_id.isnot(None)).all()
    )
    if not items or offset_amt <= Decimal("0"):
        return

    total_amount = sum((item.amount for item in items), Decimal("0"))
    if total_amount <= Decimal("0"):
        return

    remaining = offset_amt
    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = remaining
        else:
            share = (offset_amt * item.amount) / total_amount
            remaining -= share
        if share <= Decimal("0"):
            continue

        receipt = (
            db.query(CaseReceipt)
            .filter(CaseReceipt.case_id == item.case_id, CaseReceipt.fee_type == item.fee_type)
            .first()
        )
        if receipt:
            receipt.received_amt = receipt.received_amt + share
            if offset_date:
                receipt.last_receipt_date = offset_date
        else:
            db.add(
                CaseReceipt(
                    id=str(uuid4()),
                    case_id=item.case_id,
                    fee_type=item.fee_type,
                    currency=bill.currency,
                    receivable_amt=item.amount,
                    received_amt=share,
                    last_receipt_date=offset_date,
                )
            )


def _validate_bill_items(
    drafts: list[FeeDraft], items: list[FeeItem]
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    if not items:
        raise_business_error(
            "BILL_ITEM_REQUIRED",
            "Bill items are required",
            status_code=400,
        )

    allowed_fee_types = {"GOV", "SERVICE", "MISC"}
    totals_by_draft: dict[str, dict[str, Decimal]] = {
        draft.id: {"GOV": Decimal("0"), "SERVICE": Decimal("0"), "MISC": Decimal("0")}
        for draft in drafts
    }
    counts_by_draft: dict[str, int] = {draft.id: 0 for draft in drafts}

    for item in items:
        if item.amount is None or item.amount < Decimal("0"):
            raise_business_error(
                "BILL_ITEM_AMOUNT_INVALID",
                "Bill item amount must be non-negative",
                status_code=400,
            )
        if not item.fee_type or item.fee_type not in allowed_fee_types:
            raise_business_error(
                "BILL_ITEM_FEE_TYPE_INVALID",
                "Bill item fee_type is invalid",
                status_code=400,
            )
        totals_by_draft[item.draft_id][item.fee_type] += item.amount
        counts_by_draft[item.draft_id] += 1

    total_gov = Decimal("0")
    total_service = Decimal("0")
    total_misc = Decimal("0")
    total_amount = Decimal("0")
    for draft in drafts:
        draft_totals = totals_by_draft.get(draft.id)
        if draft_totals is None or counts_by_draft.get(draft.id, 0) == 0:
            raise_business_error(
                "BILL_DRAFT_EMPTY",
                "Draft has no bill items",
                status_code=400,
            )
        if draft_totals["GOV"] != draft.total_gov:
            raise_business_error(
                "BILL_ITEM_TOTAL_MISMATCH",
                "Draft gov total does not match item totals",
                status_code=400,
            )
        if draft_totals["SERVICE"] != draft.total_service:
            raise_business_error(
                "BILL_ITEM_TOTAL_MISMATCH",
                "Draft service total does not match item totals",
                status_code=400,
            )
        if draft_totals["MISC"] != draft.total_misc:
            raise_business_error(
                "BILL_ITEM_TOTAL_MISMATCH",
                "Draft misc total does not match item totals",
                status_code=400,
            )
        draft_amount = draft_totals["GOV"] + draft_totals["SERVICE"] + draft_totals["MISC"]
        if draft_amount != draft.amount:
            raise_business_error(
                "BILL_ITEM_TOTAL_MISMATCH",
                "Draft amount does not match item totals",
                status_code=400,
            )
        total_gov += draft_totals["GOV"]
        total_service += draft_totals["SERVICE"]
        total_misc += draft_totals["MISC"]
        total_amount += draft_amount

    return total_gov, total_service, total_misc, total_amount


def generate_bill(
    db: Session, data: BillCreateSchema, item_currencies: list[str | None] | None = None
) -> Bill:
    """Generate a new bill based on input data."""
    client_id = _validate_single_client([data.client_id])
    if item_currencies is not None:
        _validate_currency_consistency(data.currency, item_currencies)
    total_amount = data.total_gov + data.total_service + data.total_misc
    if total_amount < Decimal("0"):
        raise_business_error(
            "BILL_AMOUNT_INVALID",
            "Bill amount cannot be negative",
            status_code=400,
        )

    bill = Bill(
        id=str(uuid4()),
        bill_no=data.bill_no,
        client_id=client_id,
        currency=data.currency,
        direction=data.direction,
        bill_date=data.bill_date,
        due_date=data.due_date,
        total_gov=data.total_gov,
        total_service=data.total_service,
        total_misc=data.total_misc,
        amount=total_amount,
        balance=total_amount,
    )
    _apply_bill_status(bill, data.status)
    db.add(bill)
    db.commit()
    db.refresh(bill)
    _run_commission_hook_non_blocking(db, bill)
    _run_consulting_commission_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=bill.bill_date,
    )
    return bill


def create_manual_bill_record(db: Session, data: BillManualCreateSchema) -> Bill:
    """Create a manual bill using the typed payload."""
    total_amount = sum(Decimal(item.quantity) * item.unit_price for item in data.items)
    if total_amount <= Decimal("0"):
        raise_business_error(
            "BILL_MANUAL_TOTAL_INVALID",
            "Manual bill must include at least one positive item",
            status_code=400,
        )

    bill = Bill(
        id=str(uuid4()),
        client_id=data.client_id,
        currency=data.currency,
        direction=data.direction,
        bill_date=data.bill_date,
        due_date=data.due_date,
        total_gov=Decimal("0"),
        total_service=total_amount,
        total_misc=Decimal("0"),
        amount=total_amount,
        balance=total_amount,
    )
    _apply_bill_status(bill, data.status)
    db.add(bill)
    db.flush()

    for item in data.items:
        bill_item = BillItem(
            bill_id=bill.id,
            case_id=data.case_id,
            fee_name=item.description,
            fee_type=item.fee_type,
            year_no=item.year_no,
            amount=Decimal(item.quantity) * item.unit_price,
        )
        db.add(bill_item)

    db.commit()
    db.refresh(bill)
    _run_commission_hook_non_blocking(db, bill)
    _run_consulting_commission_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=bill.bill_date,
    )
    return bill


def process_payment(db: Session, data: PaymentSchema) -> Payment:
    """Process a payment and persist it."""
    if data.amount < Decimal("0"):
        raise_business_error(
            "PAYMENT_AMOUNT_INVALID",
            "Payment amount cannot be negative",
            status_code=400,
        )

    payment = Payment(
        id=str(uuid4()),
        pay_no=data.pay_no,
        client_id=data.client_id,
        pay_date=data.pay_date,
        currency=data.currency,
        amount=data.amount,
        remark=data.remark,
    )
    payment_line = PaymentLine(
        id=str(uuid4()),
        payment_id=payment.id,
        case_id=None,
        raw_amount=data.amount,
        allocated_amt=Decimal("0"),
        balance_amt=data.amount,
    )
    db.add(payment)
    db.add(payment_line)
    db.commit()
    db.refresh(payment)
    return payment


def generate_bill_from_drafts(db: Session, data: BillFromDraftsRequest) -> Bill:
    """Generate a bill from fee drafts with validation."""
    draft_ids = list(dict.fromkeys(data.draft_ids))
    drafts = db.query(FeeDraft).filter(FeeDraft.id.in_(draft_ids)).all()
    if len(drafts) != len(draft_ids):
        raise_business_error(
            "BILL_DRAFT_NOT_FOUND",
            "One or more drafts not found",
            status_code=404,
        )

    if any(draft.client_id is None for draft in drafts):
        raise_business_error(
            "BILL_CLIENT_REQUIRED",
            "Draft client_id is required",
            status_code=400,
        )

    client_id = _validate_single_client([draft.client_id for draft in drafts])
    _validate_currency_consistency(drafts[0].currency, [draft.currency for draft in drafts])
    currency = drafts[0].currency

    items = db.query(FeeItem).filter(FeeItem.draft_id.in_(draft_ids)).all()
    total_gov, total_service, total_misc, total_amount = _validate_bill_items(drafts, items)

    bill = Bill(
        id=str(uuid4()),
        bill_no=data.bill_no,
        client_id=client_id,
        currency=currency,
        direction="AR",
        total_gov=total_gov,
        total_service=total_service,
        total_misc=total_misc,
        amount=total_amount,
        balance=total_amount,
    )
    _apply_bill_status(bill, "UNSETTLED")
    db.add(bill)
    db.flush()

    for item in items:
        db.add(
            BillItem(
                id=str(uuid4()),
                bill_id=bill.id,
                case_id=item.case_id,
                draft_id=item.draft_id,
                fee_item_id=item.id,
                fee_code=item.fee_code,
                fee_name=item.fee_name,
                fee_type=item.fee_type,
                year_no=item.year_no,
                amount=item.amount,
            )
        )

    db.commit()
    db.refresh(bill)
    _run_commission_hook_non_blocking(db, bill)
    _run_consulting_commission_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=bill.bill_date,
    )
    return bill


def create_offset(db: Session, data: OffsetCreateSchema) -> Offset:
    """Create offset and update balances and receipts."""
    if data.offset_amt <= Decimal("0"):
        raise_business_error(
            "OFFSET_AMOUNT_INVALID",
            "Offset amount must be positive",
            status_code=400,
        )

    payment_line = db.query(PaymentLine).filter(PaymentLine.id == data.payment_line_id).first()
    if not payment_line:
        raise_business_error(
            "PAYMENT_LINE_NOT_FOUND",
            "Payment line not found",
            status_code=404,
        )

    bill = db.query(Bill).filter(Bill.id == data.bill_id).first()
    if not bill:
        raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)

    payment = db.query(Payment).filter(Payment.id == payment_line.payment_id).first()
    if not payment:
        raise_business_error("PAYMENT_NOT_FOUND", "Payment not found", status_code=404)

    if payment.client_id != bill.client_id:
        raise_business_error(
            "OFFSET_CLIENT_MISMATCH",
            "Payment client must match bill client",
            status_code=400,
        )

    if payment.currency != bill.currency:
        raise_business_error(
            "OFFSET_CURRENCY_MISMATCH",
            "Payment currency must match bill currency",
            status_code=400,
        )

    if payment_line.balance_amt < data.offset_amt:
        raise_business_error(
            "OFFSET_EXCEEDS_PAYMENT_BALANCE",
            "Offset amount exceeds payment balance",
            status_code=400,
        )

    if bill.balance < data.offset_amt:
        raise_business_error(
            "OFFSET_EXCEEDS_BILL_BALANCE",
            "Offset amount exceeds bill balance",
            status_code=400,
        )

    offset = Offset(
        id=str(uuid4()),
        payment_line_id=payment_line.id,
        bill_id=bill.id,
        offset_amt=data.offset_amt,
        offset_date=data.offset_date,
        is_reversed=False,
    )
    db.add(offset)

    bill.balance = bill.balance - data.offset_amt
    if bill.balance == Decimal("0"):
        next_status = "SETTLED"
    elif bill.balance < bill.amount:
        next_status = "PARTIALLY_SETTLED"
    else:
        next_status = "UNSETTLED"
    _apply_bill_status(bill, next_status)

    payment_line.allocated_amt = payment_line.allocated_amt + data.offset_amt
    payment_line.balance_amt = payment_line.balance_amt - data.offset_amt

    _allocate_offset_to_receipts(db, bill, data.offset_amt, data.offset_date)

    db.commit()
    db.refresh(offset)
    _run_commission_settleable_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=data.offset_date,
    )
    return offset


def update_bill_status(db: Session, bill_id: str, data: BillStatusSchema) -> Bill:
    """Update bill status."""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)

    _apply_bill_status(bill, data.status)
    db.commit()
    db.refresh(bill)
    return bill


def _reverse_offset_from_receipts(db: Session, bill: Bill, offset_amt: Decimal) -> None:
    """Reverse the proportional receipt allocation for an offset reversal."""
    items = (
        db.query(BillItem).filter(BillItem.bill_id == bill.id, BillItem.case_id.isnot(None)).all()
    )
    if not items or offset_amt <= Decimal("0"):
        return

    total_amount = sum((item.amount for item in items), Decimal("0"))
    if total_amount <= Decimal("0"):
        return

    remaining = offset_amt
    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = remaining
        else:
            share = (offset_amt * item.amount) / total_amount
            remaining -= share
        if share <= Decimal("0"):
            continue

        receipt = (
            db.query(CaseReceipt)
            .filter(CaseReceipt.case_id == item.case_id, CaseReceipt.fee_type == item.fee_type)
            .first()
        )
        if receipt:
            receipt.received_amt = max(receipt.received_amt - share, Decimal("0"))


def reverse_offset(db: Session, offset_id: str, actor_id: str | None = None) -> Offset:
    """Reverse an existing offset, restoring bill and payment line balances."""
    # 1. Load offset
    offset = db.query(Offset).filter(Offset.id == offset_id).first()
    if not offset:
        raise_business_error("OFFSET_NOT_FOUND", "Offset not found", status_code=404)

    # 2. Check already reversed
    if offset.is_reversed:
        raise_business_error(
            "OFFSET_ALREADY_REVERSED",
            "Offset has already been reversed",
            status_code=400,
        )

    # 3. Mark offset as reversed
    offset.is_reversed = True
    offset.reversed_at = datetime.now(timezone.utc)

    # 4. Restore bill balance
    bill = db.query(Bill).filter(Bill.id == offset.bill_id).first()
    if not bill:
        raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)

    bill.balance = bill.balance + offset.offset_amt

    # 5. Update bill status based on new balance
    if bill.balance == bill.amount:
        next_status = "UNSETTLED"
    elif bill.balance > Decimal("0"):
        next_status = "PARTIALLY_SETTLED"
    else:
        next_status = "SETTLED"
    _apply_bill_status(bill, next_status)

    # 6. Restore payment line balances
    payment_line = db.query(PaymentLine).filter(PaymentLine.id == offset.payment_line_id).first()
    if payment_line:
        payment_line.allocated_amt = payment_line.allocated_amt - offset.offset_amt
        payment_line.balance_amt = payment_line.balance_amt + offset.offset_amt

    # 7. Reverse CaseReceipt allocations
    _reverse_offset_from_receipts(db, bill, offset.offset_amt)

    db.commit()
    db.refresh(offset)
    _run_commission_settleable_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=date.today(),
    )
    return offset


def list_offsets(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    bill_id: str | None = None,
    is_reversed: bool | None = None,
) -> tuple[list[Offset], int]:
    """Return paginated offset list with optional filters.

    Returns (items, total) tuple.
    """
    query = db.query(Offset)

    if bill_id is not None:
        query = query.filter(Offset.bill_id == bill_id)
    if is_reversed is not None:
        query = query.filter(Offset.is_reversed == is_reversed)

    total = query.count()
    items = (
        query.order_by(Offset.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def create_case_receipt(db: Session, payload: CaseReceiptCreate) -> CaseReceipt:
    """Create a manual case receipt."""
    from app.modules.cases.models import Case

    case = db.query(Case).filter(Case.id == payload.case_id).first()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "案卷不存在", status_code=404)

    data = payload.model_dump()

    # V-CR-03: auto-set is_arrears if not explicitly provided
    if data.get("is_arrears") is None and data["received_amt"] < data["receivable_amt"]:
        data["is_arrears"] = True

    # V-CR-02: auto-set is_prepayment if not explicitly provided
    if data.get("is_prepayment") is None and data["received_amt"] > data["receivable_amt"]:
        data["is_prepayment"] = True

    receipt = CaseReceipt(**data)
    db.add(receipt)
    db.flush()
    return receipt


def update_case_receipt(db: Session, receipt_id: str, payload: CaseReceiptUpdate) -> CaseReceipt:
    """Update a case receipt (partial)."""
    receipt = db.query(CaseReceipt).filter(CaseReceipt.id == receipt_id).first()
    if not receipt:
        raise_business_error("CASE_RECEIPT_NOT_FOUND", "收款记录不存在", status_code=404)

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(receipt, key, value)

    # Recompute flags if amounts changed but flags not explicitly provided
    new_receivable = changes.get("receivable_amt", receipt.receivable_amt)
    new_received = changes.get("received_amt", receipt.received_amt)

    if "receivable_amt" in changes or "received_amt" in changes:
        if "is_arrears" not in changes and new_received < new_receivable:
            receipt.is_arrears = True
        if "is_prepayment" not in changes and new_received > new_receivable:
            receipt.is_prepayment = True

    db.flush()
    return receipt


def list_case_receipts(
    db: Session,
    *,
    client_id: str | None = None,
    case_no: str | None = None,
    fee_type: str | None = None,
    is_arrears: bool | None = None,
    is_commissionable: bool | None = None,
    currency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List case receipts with cross-case filters."""
    from sqlalchemy import case as sa_case

    from app.modules.cases.models import Case
    from app.modules.masterdata.clients.models import Client

    query = (
        db.query(
            CaseReceipt,
            Case.case_no.label("case_no"),
            Client.name_cn.label("client_name"),
        )
        .join(Case, Case.id == CaseReceipt.case_id)
        .outerjoin(Client, Client.id == Case.client_id)
    )

    if client_id:
        query = query.filter(Case.client_id == client_id)
    if case_no:
        query = query.filter(Case.case_no.contains(case_no))
    if fee_type:
        query = query.filter(CaseReceipt.fee_type == fee_type)
    if is_arrears is not None:
        query = query.filter(CaseReceipt.is_arrears == is_arrears)
    if is_commissionable is not None:
        query = query.filter(CaseReceipt.is_commissionable == is_commissionable)
    if currency:
        query = query.filter(CaseReceipt.currency == currency)
    if date_from:
        query = query.filter(CaseReceipt.last_receipt_date >= date_from)
    if date_to:
        query = query.filter(CaseReceipt.last_receipt_date <= date_to)

    total = query.count()

    null_last = sa_case((CaseReceipt.last_receipt_date.is_(None), 1), else_=0)
    rows = (
        query.order_by(
            null_last, CaseReceipt.last_receipt_date.desc(), CaseReceipt.created_at.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for receipt, c_no, c_name in rows:
        items.append(
            {
                "id": receipt.id,
                "case_id": receipt.case_id,
                "case_no": c_no,
                "client_name": c_name,
                "fee_type": receipt.fee_type,
                "currency": receipt.currency,
                "receivable_amt": receipt.receivable_amt,
                "received_amt": receipt.received_amt,
                "last_receipt_date": receipt.last_receipt_date,
                "fee_code": receipt.fee_code,
                "fee_name": receipt.fee_name,
                "year_no": receipt.year_no,
                "due_date": receipt.due_date,
                "is_arrears": receipt.is_arrears,
                "is_prepayment": receipt.is_prepayment,
                "is_commissionable": receipt.is_commissionable,
                "invoice_no": receipt.invoice_no,
                "remark": receipt.remark,
            }
        )

    return {"items": items, "page": page, "page_size": page_size, "total": total}
