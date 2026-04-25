from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.annuity.models import GovPayment, PayList
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
from app.modules.cases.models import Case, T_CaseApplicant
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


_AGING_BUCKETS = ("CURRENT", "0-30", "31-60", "61-90", "90+")


def _normalize_text_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


def _normalize_aging_bucket_filter(aging_bucket: str | None) -> str | None:
    normalized = _normalize_text_filter(aging_bucket)
    if normalized is None:
        return None
    if normalized not in _AGING_BUCKETS:
        raise_business_error(
            "INVALID_AGING_BUCKET",
            "Unsupported aging bucket",
            status_code=400,
        )
    return normalized


def _is_bad_debt_bill(bill: Bill) -> bool:
    return _normalize_bad_debt_status_filter(bill.bad_debt_status) != "NONE"


def _is_receivable_bill(bill: Bill) -> bool:
    return not _is_bad_debt_bill(bill) and Decimal(bill.balance or 0) > Decimal("0")


def _get_bill_days_past_due(bill: Bill, *, today: date) -> int | None:
    if not bill.due_date:
        return None
    return (today - bill.due_date).days


def _get_bill_aging_bucket(days_past_due: int | None) -> str:
    if days_past_due is None or days_past_due <= 0:
        return "CURRENT"
    if days_past_due <= 30:
        return "0-30"
    if days_past_due <= 60:
        return "31-60"
    if days_past_due <= 90:
        return "61-90"
    return "90+"


def _is_bill_overdue(bill: Bill, *, today: date) -> bool:
    return _is_receivable_bill(bill) and bill.due_date is not None and bill.due_date < today


def build_bill_report_item(bill: Bill, *, today: date | None = None) -> dict[str, object]:
    report_today = today or date.today()
    days_past_due = _get_bill_days_past_due(bill, today=report_today)
    balance = Decimal(bill.balance or 0)
    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "status": bill.status,
        "amount": bill.amount,
        "balance": balance,
        "bill_date": bill.bill_date,
        "due_date": bill.due_date,
        "days_past_due": days_past_due,
        "aging_bucket": _get_bill_aging_bucket(days_past_due),
        "is_overdue": _is_bill_overdue(bill, today=report_today),
        "is_bad_debt": _is_bad_debt_bill(bill),
    }


def _bill_matches_report_filters(
    bill: Bill,
    *,
    today: date,
    status: str | None,
    bill_status: str | None,
    client_id: str | None,
    currency: str | None,
    bill_date_from: date | None,
    bill_date_to: date | None,
    aging_bucket: str | None,
    is_overdue: bool | None,
    is_bad_debt: bool | None,
    bad_debt_status: str | None,
) -> bool:
    normalized_bill_status = _normalize_text_filter(bill_status) or _normalize_text_filter(status)
    normalized_currency = _normalize_text_filter(currency)
    normalized_bad_debt_status = _normalize_bad_debt_status_filter(bad_debt_status)
    normalized_aging_bucket = _normalize_aging_bucket_filter(aging_bucket)

    if client_id and bill.client_id != client_id:
        return False
    if (
        normalized_bill_status is not None
        and _normalize_text_filter(bill.status) != normalized_bill_status
    ):
        return False
    if (
        normalized_currency is not None
        and _normalize_text_filter(bill.currency) != normalized_currency
    ):
        return False
    if bill_date_from and bill.bill_date and bill.bill_date < bill_date_from:
        return False
    if bill_date_to and bill.bill_date and bill.bill_date > bill_date_to:
        return False
    if bill_date_from and bill.bill_date is None:
        return False
    if bill_date_to and bill.bill_date is None:
        return False
    if (
        normalized_bad_debt_status is not None
        and _normalize_bad_debt_status_filter(bill.bad_debt_status) != normalized_bad_debt_status
    ):
        return False

    bill_is_bad_debt = _is_bad_debt_bill(bill)
    bill_is_overdue = _is_bill_overdue(bill, today=today)
    bill_aging_bucket = _get_bill_aging_bucket(_get_bill_days_past_due(bill, today=today))

    if is_bad_debt is True and not bill_is_bad_debt:
        return False
    if is_bad_debt is False and bill_is_bad_debt:
        return False
    if is_overdue is True and not bill_is_overdue:
        return False
    if is_overdue is False and bill_is_overdue:
        return False
    if normalized_aging_bucket is not None:
        if bill_is_bad_debt or not _is_receivable_bill(bill):
            return False
        if bill_aging_bucket != normalized_aging_bucket:
            return False
    return True


def _summarize_bill_report_rows(
    db: Session, bills: list[Bill], *, today: date
) -> dict[str, object]:
    receivable_rows = [bill for bill in bills if _is_receivable_bill(bill)]
    overdue_rows = [bill for bill in receivable_rows if _is_bill_overdue(bill, today=today)]

    aging_buckets = {
        bucket: {"bucket": bucket, "bill_count": 0, "amount": Decimal("0")}
        for bucket in _AGING_BUCKETS
    }
    for bill in receivable_rows:
        bucket = _get_bill_aging_bucket(_get_bill_days_past_due(bill, today=today))
        aging_buckets[bucket]["bill_count"] += 1
        aging_buckets[bucket]["amount"] += Decimal(bill.balance or 0)

    bad_debt_summary = _summarize_bad_debt_bills(
        db,
        [(bill.id, bill.bad_debt_status) for bill in bills if _is_bad_debt_bill(bill)],
    )
    return {
        "receivable_bill_count": len(receivable_rows),
        "receivable_amount": sum(
            (Decimal(bill.balance or 0) for bill in receivable_rows), Decimal("0")
        ),
        "overdue_bill_count": len(overdue_rows),
        "overdue_amount": sum((Decimal(bill.balance or 0) for bill in overdue_rows), Decimal("0")),
        "aging_buckets": [aging_buckets[bucket] for bucket in _AGING_BUCKETS],
        **bad_debt_summary,
    }


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


def _resolve_payment_prepayment_status(lines: list[PaymentLine]) -> str:
    if not lines:
        return "UNALLOCATED"
    allocated_total = sum((line.allocated_amt for line in lines), Decimal("0"))
    unapplied_total = sum((line.balance_amt for line in lines), Decimal("0"))
    if allocated_total <= Decimal("0"):
        return "UNALLOCATED"
    if unapplied_total <= Decimal("0"):
        return "FULLY_ALLOCATED"
    return "PARTIALLY_ALLOCATED"


def list_payments(
    db: Session,
    *,
    client_id: str | None = None,
    prepayment_status: str | None = None,
    pay_date_from: date | None = None,
    pay_date_to: date | None = None,
    has_unapplied_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    from app.modules.masterdata.clients.models import Client

    query = db.query(
        Payment,
        func.coalesce(Client.name_cn, Client.name_en).label("client_name"),
    ).outerjoin(Client, Client.id == Payment.client_id)

    if client_id:
        query = query.filter(Payment.client_id == client_id)
    if pay_date_from:
        query = query.filter(Payment.pay_date >= pay_date_from)
    if pay_date_to:
        query = query.filter(Payment.pay_date <= pay_date_to)

    rows = query.order_by(Payment.created_at.desc(), Payment.id.desc()).all()
    if not rows:
        return {
            "items": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "prepayment_count": 0,
            "prepayment_total_amount": Decimal("0"),
            "allocated_total_amount": Decimal("0"),
            "remaining_prepayment_balance": Decimal("0"),
        }

    payment_ids = [payment.id for payment, _client_name in rows]
    payment_line_map: dict[str, list[PaymentLine]] = {}
    payment_lines = (
        db.query(PaymentLine)
        .filter(PaymentLine.payment_id.in_(payment_ids))
        .order_by(PaymentLine.created_at.asc(), PaymentLine.id.asc())
        .all()
    )
    for line in payment_lines:
        payment_line_map.setdefault(line.payment_id, []).append(line)

    normalized_status = prepayment_status.strip().upper() if prepayment_status else None
    report_rows: list[dict[str, object]] = []
    for payment, client_name in rows:
        lines = payment_line_map.get(payment.id, [])
        allocated_amt = sum((line.allocated_amt for line in lines), Decimal("0"))
        unapplied_amt = sum((line.balance_amt for line in lines), Decimal("0"))
        row_status = _resolve_payment_prepayment_status(lines)
        if normalized_status and row_status != normalized_status:
            continue
        if has_unapplied_only and unapplied_amt <= Decimal("0"):
            continue
        report_rows.append(
            {
                "id": payment.id,
                "pay_no": payment.pay_no,
                "client_id": payment.client_id,
                "client_name": client_name,
                "pay_date": payment.pay_date,
                "currency": payment.currency,
                "amount": payment.amount,
                "line_count": len(lines),
                "allocated_amt": allocated_amt,
                "unapplied_amt": unapplied_amt,
                "prepayment_status": row_status,
            }
        )

    total = len(report_rows)
    summary = {
        "prepayment_count": total,
        "prepayment_total_amount": sum(
            (Decimal(row["amount"] or 0) for row in report_rows), Decimal("0")
        ),
        "allocated_total_amount": sum(
            (Decimal(row["allocated_amt"] or 0) for row in report_rows), Decimal("0")
        ),
        "remaining_prepayment_balance": sum(
            (Decimal(row["unapplied_amt"] or 0) for row in report_rows), Decimal("0")
        ),
    }

    start = (page - 1) * page_size
    items = report_rows[start : start + page_size]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        **summary,
    }


def list_bills(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    client_id: str | None = None,
    status: str | None = None,
    bill_status: str | None = None,
    currency: str | None = None,
    bill_date_from: date | None = None,
    bill_date_to: date | None = None,
    aging_bucket: str | None = None,
    is_overdue: bool | None = None,
    is_bad_debt: bool | None = None,
    bad_debt_status: str | None = None,
) -> tuple[list[Bill], int, dict[str, object]]:
    query = db.query(Bill)
    normalized_bad_debt_status = _normalize_bad_debt_status_filter(bad_debt_status)
    normalized_bill_status = _normalize_text_filter(bill_status) or _normalize_text_filter(status)
    normalized_currency = _normalize_text_filter(currency)

    if client_id:
        query = query.filter(Bill.client_id == client_id)
    if normalized_bill_status is not None:
        query = query.filter(func.upper(Bill.status) == normalized_bill_status)
    if normalized_currency is not None:
        query = query.filter(func.upper(Bill.currency) == normalized_currency)
    if bill_date_from is not None:
        query = query.filter(Bill.bill_date >= bill_date_from)
    if bill_date_to is not None:
        query = query.filter(Bill.bill_date <= bill_date_to)
    if normalized_bad_debt_status is not None:
        query = query.filter(func.upper(Bill.bad_debt_status) == normalized_bad_debt_status)

    rows = query.order_by(Bill.created_at.desc(), Bill.id.desc()).all()
    today = date.today()
    report_rows = [
        bill
        for bill in rows
        if _bill_matches_report_filters(
            bill,
            today=today,
            status=status,
            bill_status=bill_status,
            client_id=client_id,
            currency=currency,
            bill_date_from=bill_date_from,
            bill_date_to=bill_date_to,
            aging_bucket=aging_bucket,
            is_overdue=is_overdue,
            is_bad_debt=is_bad_debt,
            bad_debt_status=bad_debt_status,
        )
    ]

    total = len(report_rows)
    bills = report_rows[(page - 1) * page_size : (page - 1) * page_size + page_size]
    summary = _summarize_bill_report_rows(db, report_rows, today=today)
    return bills, total, summary


def _normalize_fee_unified_record_type(record_type: str | None) -> str | None:
    if record_type is None:
        return None
    normalized = record_type.strip().upper()
    if not normalized:
        return None
    if normalized not in {"PAYMENT", "RECEIPT"}:
        raise_business_error(
            "INVALID_RECORD_TYPE",
            "不支持的记录类型",
            status_code=400,
        )
    return normalized


def _resolve_receipt_unified_status(receipt: CaseReceipt) -> str:
    receivable_amt = Decimal(receipt.receivable_amt or 0)
    received_amt = Decimal(receipt.received_amt or 0)
    if received_amt <= Decimal("0"):
        return "UNPAID"
    if receivable_amt <= Decimal("0"):
        return "PREPAYMENT"
    if received_amt > receivable_amt:
        return "PREPAYMENT"
    if received_amt >= receivable_amt:
        return "SETTLED"
    if bool(receipt.is_arrears):
        return "ARREARS"
    return "PARTIAL"


def _validate_fee_unified_query_ranges(
    *,
    date_from: date | None,
    date_to: date | None,
    amount_from: Decimal | None,
    amount_to: Decimal | None,
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise_business_error(
            "INVALID_DATE_RANGE",
            "date_from must be less than or equal to date_to",
            status_code=400,
        )
    if amount_from is not None and amount_to is not None and amount_from > amount_to:
        raise_business_error(
            "INVALID_AMOUNT_RANGE",
            "amount_from must be less than or equal to amount_to",
            status_code=400,
        )


def _collect_unique_payment_case_ids(lines: list[PaymentLine]) -> list[str]:
    case_ids: list[str] = []
    seen: set[str] = set()
    for line in lines:
        case_id = line.case_id
        if not case_id or case_id in seen:
            continue
        seen.add(case_id)
        case_ids.append(case_id)
    return case_ids


def _build_fee_unified_payment_rows(db: Session) -> list[dict[str, object]]:
    from app.modules.masterdata.clients.models import Client

    payment_rows = (
        db.query(Payment, func.coalesce(Client.name_cn, Client.name_en).label("client_name"))
        .outerjoin(Client, Client.id == Payment.client_id)
        .order_by(Payment.created_at.desc(), Payment.id.desc())
        .all()
    )
    if not payment_rows:
        return []

    payment_ids = [payment.id for payment, _client_name in payment_rows]
    payment_line_map: dict[str, list[PaymentLine]] = {}
    payment_lines = (
        db.query(PaymentLine)
        .filter(PaymentLine.payment_id.in_(payment_ids))
        .order_by(PaymentLine.created_at.asc(), PaymentLine.id.asc())
        .all()
    )
    for line in payment_lines:
        payment_line_map.setdefault(line.payment_id, []).append(line)

    rows: list[dict[str, object]] = []
    for payment, client_name in payment_rows:
        lines = payment_line_map.get(payment.id, [])
        case_ids = _collect_unique_payment_case_ids(lines)
        case_id = case_ids[0] if len(case_ids) == 1 else None
        rows.append(
            {
                "record_type": "PAYMENT",
                "record_id": payment.id,
                "case_id": case_id,
                "case_ids": case_ids,
                "biz_no": payment.pay_no or payment.id,
                "party_name": client_name,
                "amount": Decimal(payment.amount or 0),
                "currency": payment.currency,
                "status": _resolve_payment_prepayment_status(lines),
                "biz_date": payment.pay_date,
                "remark": payment.remark,
                "created_at": payment.created_at,
            }
        )
    return rows


def _build_fee_unified_receipt_rows(db: Session) -> list[dict[str, object]]:
    from app.modules.cases.models import Case
    from app.modules.masterdata.clients.models import Client

    receipt_rows = (
        db.query(
            CaseReceipt,
            func.coalesce(Client.name_cn, Client.name_en).label("client_name"),
        )
        .join(Case, Case.id == CaseReceipt.case_id)
        .outerjoin(Client, Client.id == Case.client_id)
        .order_by(CaseReceipt.created_at.desc(), CaseReceipt.id.desc())
        .all()
    )
    if not receipt_rows:
        return []

    rows: list[dict[str, object]] = []
    for receipt, client_name in receipt_rows:
        rows.append(
            {
                "record_type": "RECEIPT",
                "record_id": receipt.id,
                "case_id": receipt.case_id,
                "biz_no": receipt.invoice_no or receipt.id,
                "party_name": client_name,
                "amount": Decimal(receipt.received_amt or 0),
                "currency": receipt.currency,
                "status": _resolve_receipt_unified_status(receipt),
                "biz_date": receipt.last_receipt_date,
                "remark": receipt.remark,
                "created_at": receipt.created_at,
            }
        )
    return rows


def _fee_unified_row_matches(
    row: dict[str, object],
    *,
    record_type: str | None,
    case_id: str | None,
    biz_no: str | None,
    party_name: str | None,
    status: str | None,
    currency: str | None,
    date_from: date | None,
    date_to: date | None,
    amount_from: Decimal | None,
    amount_to: Decimal | None,
) -> bool:
    if record_type is not None and row["record_type"] != record_type:
        return False
    if case_id is not None:
        row_case_ids = row.get("case_ids")
        if row_case_ids is not None:
            if case_id not in row_case_ids:
                return False
        elif row["case_id"] != case_id:
            return False
    if biz_no is not None:
        candidate = str(row["biz_no"] or "").casefold()
        if biz_no.casefold() not in candidate:
            return False
    if party_name is not None:
        candidate = str(row["party_name"] or "").casefold()
        if party_name.casefold() not in candidate:
            return False
    if status is not None and _normalize_text_filter(str(row["status"] or None)) != status:
        return False
    if currency is not None and _normalize_text_filter(str(row["currency"] or None)) != currency:
        return False

    row_biz_date = row["biz_date"]
    if date_from is not None and (row_biz_date is None or row_biz_date < date_from):
        return False
    if date_to is not None and (row_biz_date is None or row_biz_date > date_to):
        return False

    row_amount = Decimal(row["amount"] or 0)
    if amount_from is not None and row_amount < amount_from:
        return False
    if amount_to is not None and row_amount > amount_to:
        return False
    return True


def list_fee_unified_queries(
    db: Session,
    *,
    record_type: str | None = None,
    case_id: str | None = None,
    biz_no: str | None = None,
    party_name: str | None = None,
    status: str | None = None,
    currency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    amount_from: Decimal | None = None,
    amount_to: Decimal | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    normalized_record_type = _normalize_fee_unified_record_type(record_type)
    normalized_status = _normalize_text_filter(status)
    normalized_currency = _normalize_text_filter(currency)
    _validate_fee_unified_query_ranges(
        date_from=date_from,
        date_to=date_to,
        amount_from=amount_from,
        amount_to=amount_to,
    )

    rows = _build_fee_unified_payment_rows(db) + _build_fee_unified_receipt_rows(db)
    filtered_rows = [
        row
        for row in rows
        if _fee_unified_row_matches(
            row,
            record_type=normalized_record_type,
            case_id=case_id,
            biz_no=biz_no,
            party_name=party_name,
            status=normalized_status,
            currency=normalized_currency,
            date_from=date_from,
            date_to=date_to,
            amount_from=amount_from,
            amount_to=amount_to,
        )
    ]

    filtered_rows.sort(
        key=lambda row: (
            row["biz_date"] or date.min,
            row["created_at"] or datetime.min.replace(tzinfo=timezone.utc),
            str(row["record_type"]),
            str(row["record_id"]),
        ),
        reverse=True,
    )

    total = len(filtered_rows)
    start = (page - 1) * page_size
    items = filtered_rows[start : start + page_size]
    return {
        "items": [
            {
                "record_type": row["record_type"],
                "record_id": row["record_id"],
                "case_id": row["case_id"],
                "biz_no": row["biz_no"],
                "party_name": row["party_name"],
                "amount": row["amount"],
                "currency": row["currency"],
                "status": row["status"],
                "biz_date": row["biz_date"],
                "remark": row["remark"],
            }
            for row in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def _normalize_fee_overview_upper_date_range(
    *,
    paid_date_from: date | None,
    paid_date_to: date | None,
) -> None:
    if paid_date_from and paid_date_to and paid_date_from > paid_date_to:
        raise_business_error(
            "FEE_OVERVIEW_DATE_RANGE_INVALID",
            "paid_date_from must be <= paid_date_to",
            status_code=400,
        )


def list_fee_overview_gov_payments(
    db: Session,
    *,
    case_no: str | None = None,
    app_no: str | None = None,
    patent_no: str | None = None,
    client_id: str | None = None,
    applicant_name: str | None = None,
    fee_type: str | None = None,
    paid_date_from: date | None = None,
    paid_date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    _normalize_fee_overview_upper_date_range(
        paid_date_from=paid_date_from,
        paid_date_to=paid_date_to,
    )

    stmt = (
        select(
            GovPayment.id.label("gov_payment_id"),
            GovPayment.pay_list_id.label("pay_list_id"),
            GovPayment.case_id.label("case_id"),
            Case.case_no.label("case_no"),
            Case.app_no.label("app_no"),
            Case.patent_no.label("patent_no"),
            GovPayment.fee_item_id.label("fee_item_id"),
            FeeItem.fee_code.label("fee_code"),
            FeeItem.fee_name.label("fee_name"),
            FeeItem.year_no.label("year_no"),
            FeeItem.amount.label("planned_amt"),
            GovPayment.paid_amount.label("paid_amt"),
            GovPayment.currency.label("currency"),
            PayList.pay_list_no.label("list_no"),
            PayList.planned_pay_date.label("planned_pay_date"),
            GovPayment.paid_date.label("paid_date"),
        )
        .join(PayList, PayList.id == GovPayment.pay_list_id)
        .join(Case, Case.id == GovPayment.case_id)
        .outerjoin(FeeItem, FeeItem.id == GovPayment.fee_item_id)
        .outerjoin(FeeDraft, FeeDraft.id == FeeItem.draft_id)
    )

    if client_id:
        stmt = stmt.where(PayList.client_id == client_id)
    if case_no:
        stmt = stmt.where(Case.case_no == case_no)
    if app_no:
        stmt = stmt.where(Case.app_no == app_no)
    if patent_no:
        stmt = stmt.where(Case.patent_no == patent_no)
    if fee_type:
        stmt = stmt.where(
            func.upper(func.coalesce(FeeDraft.draft_type, "")) == fee_type.strip().upper()
        )
    if paid_date_from:
        stmt = stmt.where(GovPayment.paid_date >= paid_date_from)
    if paid_date_to:
        stmt = stmt.where(GovPayment.paid_date <= paid_date_to)

    normalized_applicant_name = _normalize_text_filter(applicant_name)
    if normalized_applicant_name:
        applicant_expr_cn = func.upper(func.coalesce(T_CaseApplicant.name_cn, ""))
        applicant_expr_en = func.upper(func.coalesce(T_CaseApplicant.name_en, ""))
        applicant_case_ids = select(T_CaseApplicant.case_id).where(
            (applicant_expr_cn.contains(normalized_applicant_name))
            | (applicant_expr_en.contains(normalized_applicant_name))
        )
        stmt = stmt.where(Case.id.in_(applicant_case_ids))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    rows = db.execute(
        stmt.order_by(
            GovPayment.paid_date.desc(),
            GovPayment.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "gov_payment_id": row.gov_payment_id,
                "pay_list_id": row.pay_list_id,
                "case_id": row.case_id,
                "case_no": row.case_no,
                "app_no": row.app_no,
                "patent_no": row.patent_no,
                "fee_item_id": row.fee_item_id,
                "fee_code": row.fee_code,
                "fee_name": row.fee_name,
                "year_no": row.year_no,
                "planned_amt": row.planned_amt or Decimal("0"),
                "paid_amt": row.paid_amt or Decimal("0"),
                "currency": row.currency,
                "list_no": row.list_no,
                "voucher_no": None,
                "invoice_no": None,
                "planned_pay_date": row.planned_pay_date,
                "paid_date": row.paid_date,
            }
            for row in rows
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def _normalize_fee_overview_lower_date_range(
    *,
    receipt_date_from: date | None,
    receipt_date_to: date | None,
) -> None:
    if receipt_date_from and receipt_date_to and receipt_date_from > receipt_date_to:
        raise_business_error(
            "FEE_OVERVIEW_DATE_RANGE_INVALID",
            "receipt_date_from must be <= receipt_date_to",
            status_code=400,
        )


def list_fee_overview_case_receipts(
    db: Session,
    *,
    case_no: str | None = None,
    app_no: str | None = None,
    patent_no: str | None = None,
    client_id: str | None = None,
    applicant_name: str | None = None,
    fee_type: str | None = None,
    receipt_date_from: date | None = None,
    receipt_date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    _normalize_fee_overview_lower_date_range(
        receipt_date_from=receipt_date_from,
        receipt_date_to=receipt_date_to,
    )

    stmt = select(
        CaseReceipt.id.label("receipt_id"),
        CaseReceipt.case_id.label("case_id"),
        Case.case_no.label("case_no"),
        Case.app_no.label("app_no"),
        Case.patent_no.label("patent_no"),
        CaseReceipt.fee_code.label("fee_code"),
        CaseReceipt.fee_name.label("fee_name"),
        CaseReceipt.year_no.label("year_no"),
        CaseReceipt.fee_type.label("fee_type"),
        CaseReceipt.receivable_amt.label("receivable_amt"),
        CaseReceipt.received_amt.label("received_amt"),
        CaseReceipt.currency.label("currency"),
        CaseReceipt.is_arrears.label("is_arrears"),
        CaseReceipt.is_prepayment.label("is_prepayment"),
        CaseReceipt.is_commissionable.label("is_commissionable"),
        CaseReceipt.last_receipt_date.label("receipt_date"),
        CaseReceipt.due_date.label("due_date"),
        CaseReceipt.invoice_no.label("invoice_no"),
    ).join(Case, Case.id == CaseReceipt.case_id)

    if client_id:
        stmt = stmt.where(Case.client_id == client_id)
    if case_no:
        stmt = stmt.where(Case.case_no == case_no)
    if app_no:
        stmt = stmt.where(Case.app_no == app_no)
    if patent_no:
        stmt = stmt.where(Case.patent_no == patent_no)
    if fee_type:
        stmt = stmt.where(
            func.upper(func.coalesce(CaseReceipt.fee_type, "")) == fee_type.strip().upper()
        )
    if receipt_date_from:
        stmt = stmt.where(CaseReceipt.last_receipt_date >= receipt_date_from)
    if receipt_date_to:
        stmt = stmt.where(CaseReceipt.last_receipt_date <= receipt_date_to)

    normalized_applicant_name = _normalize_text_filter(applicant_name)
    if normalized_applicant_name:
        applicant_expr_cn = func.upper(func.coalesce(T_CaseApplicant.name_cn, ""))
        applicant_expr_en = func.upper(func.coalesce(T_CaseApplicant.name_en, ""))
        applicant_case_ids = select(T_CaseApplicant.case_id).where(
            (applicant_expr_cn.contains(normalized_applicant_name))
            | (applicant_expr_en.contains(normalized_applicant_name))
        )
        stmt = stmt.where(Case.id.in_(applicant_case_ids))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    rows = db.execute(
        stmt.order_by(
            CaseReceipt.last_receipt_date.desc(),
            CaseReceipt.created_at.desc(),
            CaseReceipt.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return {
        "items": [
            {
                "receipt_id": row.receipt_id,
                "case_id": row.case_id,
                "case_no": row.case_no,
                "app_no": row.app_no,
                "patent_no": row.patent_no,
                "fee_code": row.fee_code,
                "fee_name": row.fee_name,
                "year_no": row.year_no,
                "fee_type": row.fee_type,
                "receivable_amt": row.receivable_amt or Decimal("0"),
                "received_amt": row.received_amt or Decimal("0"),
                "currency": row.currency,
                "is_arrears": row.is_arrears,
                "is_prepayment": row.is_prepayment,
                "is_commissionable": row.is_commissionable,
                "receipt_date": row.receipt_date,
                "due_date": row.due_date,
                "invoice_no": row.invoice_no,
            }
            for row in rows
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


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

    receivable_by_key: dict[tuple[str, str | None], Decimal] = {}
    for item in items:
        if not item.case_id:
            continue
        key = (item.case_id, item.fee_type)
        receivable_by_key[key] = receivable_by_key.get(key, Decimal("0")) + Decimal(
            item.amount or 0
        )
    receipt_cache: dict[tuple[str, str | None], CaseReceipt] = {
        (receipt.case_id, receipt.fee_type): receipt
        for receipt in db.query(CaseReceipt)
        .filter(CaseReceipt.case_id.in_({case_id for case_id, _fee_type in receivable_by_key}))
        .all()
    }

    remaining = offset_amt
    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = remaining
        else:
            share = (offset_amt * item.amount) / total_amount
            remaining -= share
        if share <= Decimal("0"):
            continue

        key = (item.case_id, item.fee_type)
        receipt = receipt_cache.get(key)
        receivable_amt = receivable_by_key.get(key, Decimal(item.amount or 0))
        if receipt:
            receipt.receivable_amt = max(Decimal(receipt.receivable_amt or 0), receivable_amt)
            receipt.received_amt = receipt.received_amt + share
            if offset_date:
                receipt.last_receipt_date = offset_date
        else:
            receipt = CaseReceipt(
                id=str(uuid4()),
                case_id=item.case_id,
                fee_type=item.fee_type,
                currency=bill.currency,
                receivable_amt=receivable_amt,
                received_amt=share,
                last_receipt_date=offset_date,
            )
            db.add(receipt)
            receipt_cache[key] = receipt


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
    if data.pay_date is not None and data.pay_date > date.today() + timedelta(days=365):
        raise_business_error(
            "PAYMENT_DATE_INVALID",
            "Payment date is too far in the future",
            status_code=400,
            details={"pay_date": data.pay_date.isoformat()},
        )
    if data.pay_no:
        existing = (
            db.query(Payment)
            .filter(Payment.client_id == data.client_id, Payment.pay_no == data.pay_no)
            .first()
        )
        if existing:
            raise_business_error(
                "PAYMENT_PAY_NO_DUPLICATE",
                "Payment number already exists for this client",
                status_code=400,
                details={"client_id": data.client_id, "pay_no": data.pay_no},
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
