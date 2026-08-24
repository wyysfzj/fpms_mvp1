from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.annuity.models import GovPayment, PayList
from app.modules.annuity.service import register_gov_payment
from app.modules.billing.models import (
    BadDebtRecovery,
    BadDebtVoucher,
    Bill,
    BillDraftSource,
    BillItem,
    CaseReceipt,
    DemoFinanceCommand,
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
    DemoBankReceiptRequest,
    DemoBillFromDraftRequest,
    DemoFullOffsetRequest,
    DemoGovPaymentRequest,
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


@dataclass(frozen=True, slots=True)
class DemoBillFromDraftResult:
    bill_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class DemoBankReceiptResult:
    payment_id: str
    line_id: str
    target_bill_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class DemoFullOffsetResult:
    offset_id: str
    bill_id: str
    line_id: str
    receipt_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class DemoGovPaymentResult:
    gov_payment_id: int
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class DemoFinanceReservation:
    command_id: str
    state: str
    result_snapshot: str | None
    created: bool


_DEMO_FINANCE_OPERATIONS = frozenset(
    {"BILL", "PAYMENT", "OFFSET", "GOV_PAYMENT"}
)


def reserve_demo_finance_command(
    db: Session,
    *,
    operation: str,
    idempotency_key: str,
    actor_id: str,
    payload: dict[str, object],
) -> DemoFinanceReservation:
    _demo_finance_scope_or_fail()
    if operation not in _DEMO_FINANCE_OPERATIONS:
        raise ValueError(f"unsupported demo finance operation: {operation}")
    canonical = json.dumps(
        {
            "actor_id": actor_id,
            "operation": operation,
            "payload": payload,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    command_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    existing = db.scalar(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.operation == operation,
            DemoFinanceCommand.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.created_by != actor_id or existing.command_hash != command_hash:
            raise_business_error(
                "DEMO_FINANCE_IDEMPOTENCY_CONFLICT",
                "财务命令幂等键已由其他命令占用",
                status_code=409,
            )
        return DemoFinanceReservation(
            command_id=existing.id,
            state=existing.state,
            result_snapshot=existing.result_snapshot,
            created=False,
        )

    command = DemoFinanceCommand(
        id=str(uuid4()),
        operation=operation,
        idempotency_key=idempotency_key,
        state="IN_PROGRESS",
        command_hash=command_hash,
        command_snapshot=canonical,
        result_snapshot=None,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(command)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(DemoFinanceCommand).where(
                DemoFinanceCommand.operation == operation,
                DemoFinanceCommand.idempotency_key == idempotency_key,
            )
        )
        if (
            existing is None
            or existing.created_by != actor_id
            or existing.command_hash != command_hash
        ):
            raise_business_error(
                "DEMO_FINANCE_IDEMPOTENCY_CONFLICT",
                "财务命令幂等键已由其他命令占用",
                status_code=409,
            )
        return DemoFinanceReservation(
            command_id=existing.id,
            state=existing.state,
            result_snapshot=existing.result_snapshot,
            created=False,
        )
    return DemoFinanceReservation(
        command_id=command.id,
        state=command.state,
        result_snapshot=None,
        created=True,
    )


def get_demo_finance_command(
    db: Session,
    *,
    operation: str,
    idempotency_key: str,
    actor_id: str,
) -> DemoFinanceCommand | None:
    _demo_finance_scope_or_fail()
    return db.scalar(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.operation == operation,
            DemoFinanceCommand.idempotency_key == idempotency_key,
            DemoFinanceCommand.created_by == actor_id,
        )
    )


def complete_demo_finance_command(
    db: Session,
    *,
    command_id: str,
    actor_id: str,
    result_snapshot: str,
) -> None:
    command = db.scalar(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.id == command_id,
            DemoFinanceCommand.created_by == actor_id,
        )
    )
    if command is None:
        raise_business_error(
            "DEMO_FINANCE_COMMAND_NOT_FOUND",
            "未找到财务命令",
            status_code=404,
        )
    if command.state == "COMPLETED":
        if command.result_snapshot != result_snapshot:
            raise_business_error(
                "DEMO_FINANCE_RESULT_IMMUTABLE",
                "财务命令结果已经冻结",
                status_code=409,
            )
        return
    command.state = "COMPLETED"
    command.result_snapshot = result_snapshot
    command.updated_by = actor_id
    db.commit()


def abandon_demo_finance_command(
    db: Session,
    *,
    command_id: str,
    actor_id: str,
) -> None:
    db.rollback()
    command = db.scalar(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.id == command_id,
            DemoFinanceCommand.created_by == actor_id,
            DemoFinanceCommand.state == "IN_PROGRESS",
        )
    )
    if command is not None:
        db.delete(command)
        db.commit()


def _begin_demo_finance_write(db: Session) -> None:
    connection = db.connection()
    if (
        connection.dialect.name != "sqlite"
        or connection.connection.driver_connection.in_transaction
    ):
        return
    try:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
    except OperationalError:
        db.rollback()
        raise_business_error(
            "DEMO_FINANCE_WRITE_BUSY",
            "财务操作暂时繁忙，请重试",
            status_code=409,
        )


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


def _load_bill_payment_context(
    db: Session,
    *,
    bill_id: str | None,
    required: bool,
) -> tuple[Bill | None, set[str]]:
    if not bill_id:
        return None, set()

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if bill is None:
        if required:
            raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)
        return None, set()

    case_ids = {
        row.case_id
        for row in db.query(BillItem.case_id)
        .filter(BillItem.bill_id == bill.id, BillItem.case_id.isnot(None))
        .all()
    }
    return bill, {case_id for case_id in case_ids if case_id}


def list_payments(
    db: Session,
    *,
    bill_id: str | None = None,
    client_id: str | None = None,
    prepayment_status: str | None = None,
    pay_date_from: date | None = None,
    pay_date_to: date | None = None,
    has_unapplied_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    from app.modules.masterdata.clients.models import Client

    target_bill, target_case_ids = _load_bill_payment_context(db, bill_id=bill_id, required=False)
    query = db.query(
        Payment,
        func.coalesce(Client.name_cn, Client.name_en).label("client_name"),
    ).outerjoin(Client, Client.id == Payment.client_id)

    if target_bill is not None:
        query = query.filter(
            Payment.client_id == target_bill.client_id,
            Payment.currency == target_bill.currency,
        )
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
        if target_bill is not None and target_case_ids:
            if not any(line.case_id in target_case_ids for line in lines):
                continue
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
                "bill_id": target_bill.id if target_bill is not None else None,
                "bill_no": target_bill.bill_no if target_bill is not None else None,
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
    bill, bill_case_ids = _load_bill_payment_context(db, bill_id=data.bill_id, required=True)
    effective_client_id = bill.client_id if bill is not None else data.client_id
    effective_currency = bill.currency if bill is not None else data.currency
    if not effective_client_id:
        raise_business_error(
            "PAYMENT_CLIENT_REQUIRED",
            "client_id is required when bill_id is not provided",
            status_code=400,
        )
    if data.client_id and bill is not None and data.client_id != bill.client_id:
        raise_business_error(
            "PAYMENT_BILL_CLIENT_MISMATCH",
            "Payment client must match bill client",
            status_code=400,
        )

    if data.pay_no:
        existing = (
            db.query(Payment)
            .filter(Payment.client_id == effective_client_id, Payment.pay_no == data.pay_no)
            .first()
        )
        if existing:
            raise_business_error(
                "PAYMENT_PAY_NO_DUPLICATE",
                "Payment number already exists for this client",
                status_code=400,
                details={"client_id": effective_client_id, "pay_no": data.pay_no},
            )

    linked_case_id = next(iter(bill_case_ids)) if len(bill_case_ids) == 1 else None
    payment = Payment(
        id=str(uuid4()),
        pay_no=data.pay_no,
        client_id=effective_client_id,
        pay_date=data.pay_date,
        currency=effective_currency,
        amount=data.amount,
        remark=data.remark,
    )
    payment_line = PaymentLine(
        id=str(uuid4()),
        payment_id=payment.id,
        case_id=linked_case_id,
        raw_amount=data.amount,
        allocated_amt=Decimal("0"),
        balance_amt=data.amount,
    )
    db.add(payment)
    db.add(payment_line)
    db.commit()
    db.refresh(payment)
    return payment


def _demo_bill_command_hash(data: DemoBillFromDraftRequest, actor_id: str) -> str:
    canonical = json.dumps(
        {
            "actor_id": actor_id,
            "bill_date": data.bill_date.isoformat(),
            "bill_no": data.bill_no,
            "draft_id": data.draft_id,
            "due_date": data.due_date.isoformat() if data.due_date is not None else None,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_demo_bill_from_draft(
    db: Session,
    data: DemoBillFromDraftRequest,
    *,
    actor_id: str,
) -> DemoBillFromDraftResult:
    if os.environ.get("FPMS_ENV") != "demo" or os.environ.get("FPMS_DEMO_SCOPE") != "LOCAL_ABC_E2E":
        raise_business_error(
            "DEMO_BILL_SCOPE_REQUIRED",
            "本地演示账单命令未启用",
            status_code=409,
        )
    if (
        not actor_id
        or actor_id != actor_id.strip()
        or "\x00" in actor_id
        or not data.idempotency_key
        or data.idempotency_key != data.idempotency_key.strip()
        or "\x00" in data.idempotency_key
        or (data.bill_no is not None and data.bill_no != data.bill_no.strip())
    ):
        raise_business_error(
            "DEMO_BILL_INPUT_INVALID",
            "本地演示账单输入无效",
            status_code=400,
        )
    command_hash = _demo_bill_command_hash(data, actor_id)
    connection = db.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN IMMEDIATE")

    existing_key = db.scalar(
        select(BillDraftSource).where(
            BillDraftSource.idempotency_key == data.idempotency_key
        )
    )
    if existing_key is not None:
        if existing_key.command_hash != command_hash:
            raise_business_error(
                "DEMO_BILL_IDEMPOTENCY_CONFLICT",
                "账单幂等键已用于不同命令",
                status_code=409,
            )
        return DemoBillFromDraftResult(
            bill_id=existing_key.bill_id,
            idempotency_key=data.idempotency_key,
            reused=True,
        )

    draft = db.scalar(select(FeeDraft).where(FeeDraft.id == data.draft_id))
    if draft is None:
        raise_business_error("BILL_DRAFT_NOT_FOUND", "费用草稿不存在", status_code=404)
    if draft.status != "LOCKED":
        raise_business_error(
            "DEMO_BILL_DRAFT_NOT_LOCKED",
            "仅已锁定的费用草稿可以生成演示账单",
            status_code=409,
        )
    if draft.client_id is None or draft.currency != "CNY":
        raise_business_error(
            "DEMO_BILL_DRAFT_SCOPE_INVALID",
            "演示账单仅支持已关联客户的 CNY 草稿",
            status_code=400,
        )
    consumed = db.scalar(
        select(BillDraftSource).where(BillDraftSource.draft_id == draft.id)
    )
    if consumed is not None:
        raise_business_error(
            "DEMO_BILL_DRAFT_ALREADY_CONSUMED",
            "费用草稿已生成账单",
            status_code=409,
        )

    items = tuple(
        db.scalars(select(FeeItem).where(FeeItem.draft_id == draft.id)).all()
    )
    service_total = sum((item.amount or Decimal("0") for item in items), Decimal("0"))
    case_ids = {item.case_id for item in items}
    if (
        not items
        or any(
            item.fee_type != "SERVICE"
            or item.amount is None
            or item.amount <= Decimal("0")
            or item.case_id is None
            for item in items
        )
        or len(case_ids) != 1
        or draft.total_gov != Decimal("0")
        or draft.total_misc != Decimal("0")
        or draft.total_service != service_total
        or draft.amount != service_total
    ):
        raise_business_error(
            "DEMO_BILL_DRAFT_CONTENT_INVALID",
            "演示账单要求同一案件的多行正额服务费项目",
            status_code=400,
        )

    bill_id = str(uuid4())
    bill = Bill(
        id=bill_id,
        bill_no=data.bill_no or f"DEMO-AR-{draft.id[:8].upper()}",
        client_id=draft.client_id,
        currency="CNY",
        direction="AR",
        status="UNSETTLED",
        bill_date=data.bill_date,
        due_date=data.due_date,
        total_gov=Decimal("0"),
        total_service=service_total,
        total_misc=Decimal("0"),
        amount=service_total,
        balance=service_total,
        created_by=actor_id,
        updated_by=actor_id,
    )
    bill_items = tuple(
        BillItem(
            id=str(uuid4()),
            bill_id=bill_id,
            case_id=item.case_id,
            draft_id=draft.id,
            fee_item_id=item.id,
            fee_code=item.fee_code,
            fee_name=item.fee_name,
            fee_type=item.fee_type,
            year_no=item.year_no,
            amount=item.amount,
            created_by=actor_id,
            updated_by=actor_id,
        )
        for item in items
    )
    source = BillDraftSource(
        id=str(uuid4()),
        bill_id=bill_id,
        draft_id=draft.id,
        idempotency_key=data.idempotency_key,
        command_hash=command_hash,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add_all((bill, *bill_items, source))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_business_error(
            "DEMO_BILL_CONCURRENT_CONFLICT",
            "费用草稿已由另一账单命令占用",
            status_code=409,
        )
    return DemoBillFromDraftResult(
        bill_id=bill_id,
        idempotency_key=data.idempotency_key,
        reused=False,
    )


def reconcile_demo_bill_from_draft(
    db: Session, idempotency_key: str, *, actor_id: str
) -> DemoBillFromDraftResult:
    _demo_finance_scope_or_fail()
    command = db.scalar(
        select(BillDraftSource).where(
            BillDraftSource.idempotency_key == idempotency_key,
            BillDraftSource.created_by == actor_id,
        )
    )
    if command is None:
        raise_business_error(
            "DEMO_BILL_COMMAND_NOT_FOUND",
            "未找到可对账的账单命令",
            status_code=404,
        )
    return DemoBillFromDraftResult(
        bill_id=command.bill_id,
        idempotency_key=command.idempotency_key,
        reused=True,
    )


def _demo_finance_scope_or_fail() -> None:
    if os.environ.get("FPMS_ENV") != "demo" or os.environ.get("FPMS_DEMO_SCOPE") != "LOCAL_ABC_E2E":
        raise_business_error(
            "DEMO_FINANCE_SCOPE_REQUIRED",
            "本地演示财务命令未启用",
            status_code=409,
        )


def _demo_finance_payload(
    command: DemoFinanceCommand,
    *,
    operation: str,
    actor_id: str,
) -> dict[str, object]:
    try:
        stored = json.loads(command.command_snapshot)
        canonical = json.dumps(
            stored,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        raise_business_error(
            "DEMO_FINANCE_STORED_STATE_INVALID",
            "财务命令存量状态无效",
            status_code=409,
        )
    if (
        type(stored) is not dict
        or set(stored) != {"actor_id", "operation", "payload"}
        or stored.get("actor_id") != actor_id
        or stored.get("operation") != operation
        or type(stored.get("payload")) is not dict
        or canonical != command.command_snapshot
        or hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        != command.command_hash
    ):
        raise_business_error(
            "DEMO_FINANCE_STORED_STATE_INVALID",
            "财务命令存量状态无效",
            status_code=409,
        )
    return stored["payload"]


def _demo_gov_payment_or_fail(
    db: Session,
    *,
    pay_list_id: int,
    fee_item_id: str,
    paid_date: date,
    paid_amount: Decimal,
    remark: str,
    completed: bool,
) -> GovPayment:
    pay_list = db.get(PayList, pay_list_id)
    if pay_list is None:
        raise_business_error(
            "PAY_LIST_NOT_FOUND",
            "官费清单不存在",
            status_code=404,
        )
    item_row = db.execute(
        select(FeeItem, FeeDraft)
        .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
        .where(FeeItem.id == fee_item_id)
    ).first()
    if item_row is None:
        raise_business_error(
            "FEE_ITEM_NOT_FOUND",
            "费用明细不存在",
            status_code=404,
        )
    item, draft = item_row
    payments = tuple(
        db.scalars(
            select(GovPayment).where(
                GovPayment.pay_list_id == pay_list_id,
                GovPayment.fee_item_id == fee_item_id,
            )
        )
    )
    if len(payments) != 1:
        raise_business_error(
            "DEMO_GOV_PAYMENT_SCOPE_CONFLICT",
            "官费清单明细关联无效",
            status_code=409,
        )
    payment = payments[0]
    expected_status = "PAID" if completed else "PLANNED"
    expected_paid_date = paid_date if completed else None
    expected_remark = remark if completed else f"from_fee_item:{item.id}"
    if (
        item.fee_type != "GOV"
        or item.case_id is None
        or draft.client_id != pay_list.client_id
        or draft.currency != pay_list.currency
        or pay_list.currency != "CNY"
        or item.amount != paid_amount
        or payment.case_id != item.case_id
        or payment.fee_code != item.fee_code
        or payment.status != expected_status
        or payment.paid_date != expected_paid_date
        or payment.paid_amount != paid_amount
        or payment.planned_amt != item.amount
        or payment.currency != "CNY"
        or payment.planned_currency != "CNY"
        or payment.paid_currency != ("CNY" if completed else None)
        or payment.official_receipt_no is not None
        or payment.voucher_no is not None
        or payment.invoice_no is not None
        or payment.remark != expected_remark
    ):
        raise_business_error(
            "DEMO_GOV_PAYMENT_SCOPE_CONFLICT",
            "官费登记与清单权威明细不一致",
            status_code=409,
        )
    return payment


def create_demo_gov_payment(
    db: Session,
    data: DemoGovPaymentRequest,
    *,
    actor_id: str,
) -> DemoGovPaymentResult:
    _demo_finance_scope_or_fail()
    _demo_gov_payment_or_fail(
        db,
        pay_list_id=data.pay_list_id,
        fee_item_id=data.fee_item_id,
        paid_date=data.paid_date,
        paid_amount=data.paid_amount,
        remark=data.remark,
        completed=False,
    )
    register_gov_payment(
        db,
        pay_list_id=data.pay_list_id,
        fee_item_id=data.fee_item_id,
        paid_date=data.paid_date,
        paid_amount=data.paid_amount,
        official_receipt_no=None,
        remark=data.remark,
        paid_currency="CNY",
        voucher_no=None,
        invoice_no=None,
        actor_id=actor_id,
    )
    payment = _demo_gov_payment_or_fail(
        db,
        pay_list_id=data.pay_list_id,
        fee_item_id=data.fee_item_id,
        paid_date=data.paid_date,
        paid_amount=data.paid_amount,
        remark=data.remark,
        completed=True,
    )
    return DemoGovPaymentResult(payment.id, data.idempotency_key, False)


def reconcile_demo_gov_payment(
    db: Session,
    idempotency_key: str,
    *,
    actor_id: str,
) -> DemoGovPaymentResult:
    _demo_finance_scope_or_fail()
    command = get_demo_finance_command(
        db,
        operation="GOV_PAYMENT",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_GOV_PAYMENT_COMMAND_NOT_FOUND",
            "未找到可恢复的官费登记命令",
            status_code=404,
        )
    payload = _demo_finance_payload(
        command,
        operation="GOV_PAYMENT",
        actor_id=actor_id,
    )
    try:
        request = DemoGovPaymentRequest.model_validate(payload)
    except ValueError:
        raise_business_error(
            "DEMO_FINANCE_STORED_STATE_INVALID",
            "财务命令存量状态无效",
            status_code=409,
        )
    planned = db.scalar(
        select(GovPayment).where(
            GovPayment.pay_list_id == request.pay_list_id,
            GovPayment.fee_item_id == request.fee_item_id,
            GovPayment.status == "PLANNED",
            GovPayment.paid_date.is_(None),
        )
    )
    if planned is not None:
        _demo_gov_payment_or_fail(
            db,
            pay_list_id=request.pay_list_id,
            fee_item_id=request.fee_item_id,
            paid_date=request.paid_date,
            paid_amount=request.paid_amount,
            remark=request.remark,
            completed=False,
        )
        raise_business_error(
            "DEMO_GOV_PAYMENT_DOMAIN_RESULT_NOT_FOUND",
            "官费登记命令尚未形成可恢复的业务结果",
            status_code=404,
        )
    payment = _demo_gov_payment_or_fail(
        db,
        pay_list_id=request.pay_list_id,
        fee_item_id=request.fee_item_id,
        paid_date=request.paid_date,
        paid_amount=request.paid_amount,
        remark=request.remark,
        completed=True,
    )
    return DemoGovPaymentResult(payment.id, idempotency_key, True)


def create_demo_bank_receipt(
    db: Session,
    data: DemoBankReceiptRequest,
    *,
    actor_id: str,
) -> DemoBankReceiptResult:
    _demo_finance_scope_or_fail()
    _begin_demo_finance_write(db)
    bill = db.scalar(select(Bill).where(Bill.id == data.target_bill_id))
    if bill is None:
        raise_business_error(
            "DEMO_PAYMENT_BILL_NOT_FOUND",
            "目标账单不存在",
            status_code=404,
        )
    source = db.scalar(
        select(BillDraftSource).where(BillDraftSource.bill_id == data.target_bill_id)
    )
    items = tuple(
        db.scalars(select(BillItem).where(BillItem.bill_id == data.target_bill_id)).all()
    )
    case_ids = {item.case_id for item in items}
    item_total = sum((item.amount or Decimal("0") for item in items), Decimal("0"))
    if (
        source is None
        or not items
        or any(
            item.fee_type != "SERVICE"
            or item.amount is None
            or item.amount <= Decimal("0")
            or item.case_id is None
            for item in items
        )
        or len(case_ids) != 1
        or item_total != bill.amount
        or bill.total_service != bill.amount
        or bill.total_gov != Decimal("0")
        or bill.total_misc != Decimal("0")
    ):
        raise_business_error(
            "DEMO_PAYMENT_BILL_INVALID",
            "目标账单不是可收款的本地演示账单",
            status_code=400,
        )
    if (
        bill.currency != "CNY"
        or bill.direction != "AR"
    ):
        raise_business_error(
            "DEMO_PAYMENT_AMOUNT_OR_BILL_CONFLICT",
            "回款金额或目标账单不符合本地演示边界",
            status_code=400,
        )

    payment_commands = []
    for command in db.scalars(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.operation == "PAYMENT",
        )
    ):
        payload = _demo_finance_payload(
            command,
            operation="PAYMENT",
            actor_id=command.created_by or "",
        )
        if payload.get("target_bill_id") == bill.id:
            payment_commands.append(command)
    active_offset_count = db.scalar(
        select(func.count(Offset.id)).where(
            Offset.bill_id == bill.id,
            Offset.is_reversed.is_(False),
        )
    )
    ordinal = len(payment_commands)
    if ordinal == 1 and not Decimal("0") < data.amount < bill.balance:
        raise_business_error(
            "DEMO_PAYMENT_AMOUNT_OR_BILL_CONFLICT",
            "首笔回款必须为小于账单余额的正额",
            status_code=400,
        )
    if ordinal == 1:
        valid_state = (
            active_offset_count == 0
            and bill.status == "UNSETTLED"
        )
    elif ordinal == 2:
        valid_state = (
            active_offset_count == 1
            and bill.status == "PARTIALLY_SETTLED"
            and data.amount == bill.balance
        )
    else:
        valid_state = False
    if not valid_state:
        raise_business_error(
            "DEMO_PAYMENT_SEQUENCE_CONFLICT",
            "回款金额或顺序与账单权威余额不一致",
            status_code=409,
        )
    if db.scalar(select(Payment.id).where(Payment.pay_no == data.pay_no)) is not None or db.scalar(
        select(Payment.id).where(Payment.bank_ref_no == data.bank_ref_no)
    ) is not None:
        raise_business_error(
            "DEMO_PAYMENT_REFERENCE_DUPLICATE",
            "回款编号或银行参考号已存在",
            status_code=409,
        )

    payment_id = str(uuid4())
    line_id = str(uuid4())
    payment = Payment(
        id=payment_id,
        pay_no=data.pay_no,
        client_id=bill.client_id,
        pay_date=data.pay_date,
        currency="CNY",
        amount=data.amount,
        remark=data.remark,
        pay_method=data.pay_method,
        bank_ref_no=data.bank_ref_no,
        created_by=actor_id,
        updated_by=actor_id,
    )
    line = PaymentLine(
        id=line_id,
        payment_id=payment_id,
        case_id=next(iter(case_ids)),
        raw_amount=data.amount,
        allocated_amt=Decimal("0"),
        balance_amt=data.amount,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add_all((payment, line))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_business_error(
            "DEMO_PAYMENT_CONCURRENT_CONFLICT",
            "回款命令与已存在记录冲突",
            status_code=409,
        )
    return DemoBankReceiptResult(
        payment_id=payment_id,
        line_id=line_id,
        target_bill_id=bill.id,
        idempotency_key=data.idempotency_key,
        reused=False,
    )


def reconcile_demo_bank_receipt(
    db: Session, idempotency_key: str, *, actor_id: str
) -> DemoBankReceiptResult:
    _demo_finance_scope_or_fail()
    command = get_demo_finance_command(
        db,
        operation="PAYMENT",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_PAYMENT_COMMAND_NOT_FOUND",
            "未找到可对账的回款命令",
            status_code=404,
        )
    payload = _demo_finance_payload(command, operation="PAYMENT", actor_id=actor_id)
    try:
        request = DemoBankReceiptRequest.model_validate(payload)
    except ValueError:
        raise_business_error(
            "DEMO_PAYMENT_STORED_STATE_INVALID",
            "回款存量状态无效",
            status_code=409,
        )
    payments = tuple(
        db.scalars(
            select(Payment).where(
                Payment.pay_no == request.pay_no,
                Payment.bank_ref_no == request.bank_ref_no,
            )
        )
    )
    payment = payments[0] if len(payments) == 1 else None
    if payment is None:
        raise_business_error(
            "DEMO_PAYMENT_DOMAIN_RESULT_NOT_FOUND",
            "回款命令尚未形成可恢复的业务结果",
            status_code=404,
        )
    lines = (
        tuple(db.scalars(select(PaymentLine).where(PaymentLine.payment_id == payment.id)))
        if payment is not None
        else ()
    )
    line = lines[0] if len(lines) == 1 else None
    bill = db.get(Bill, request.target_bill_id)
    items = (
        tuple(db.scalars(select(BillItem).where(BillItem.bill_id == bill.id)))
        if bill is not None
        else ()
    )
    case_ids = {item.case_id for item in items}
    if (
        payment is None
        or line is None
        or bill is None
        or not items
        or len(case_ids) != 1
        or None in case_ids
        or any(item.fee_type != "SERVICE" for item in items)
        or payment.client_id != bill.client_id
        or payment.pay_date != request.pay_date
        or payment.currency != request.currency
        or payment.amount != request.amount
        or payment.pay_method != request.pay_method
        or payment.remark != request.remark
        or line.case_id != next(iter(case_ids))
        or line.raw_amount != request.amount
        or line.allocated_amt + line.balance_amt != line.raw_amount
        or line.allocated_amt not in {Decimal("0"), line.raw_amount}
    ):
        raise_business_error(
            "DEMO_PAYMENT_STORED_STATE_INVALID",
            "回款存量状态无效",
            status_code=409,
        )
    return DemoBankReceiptResult(
        payment_id=payment.id,
        line_id=line.id,
        target_bill_id=bill.id,
        idempotency_key=idempotency_key,
        reused=True,
    )


def create_demo_full_offset(
    db: Session,
    data: DemoFullOffsetRequest,
    *,
    actor_id: str,
) -> DemoFullOffsetResult:
    _demo_finance_scope_or_fail()
    _begin_demo_finance_write(db)
    bill = db.get(Bill, data.bill_id)
    if bill is None:
        raise_business_error("DEMO_OFFSET_BILL_NOT_FOUND", "目标账单不存在", status_code=404)
    line = db.get(PaymentLine, data.payment_line_id)
    if line is None:
        raise_business_error("DEMO_OFFSET_LINE_NOT_FOUND", "回款明细不存在", status_code=404)
    payment = db.get(Payment, line.payment_id) if line is not None else None
    if payment is None:
        raise_business_error("DEMO_OFFSET_PAYMENT_NOT_FOUND", "客户回款不存在", status_code=404)
    items = tuple(
        db.scalars(select(BillItem).where(BillItem.bill_id == data.bill_id)).all()
    )
    source = db.scalar(select(BillDraftSource).where(BillDraftSource.bill_id == data.bill_id))
    active_offsets = tuple(
        db.scalars(
            select(Offset).where(
                Offset.bill_id == data.bill_id,
                Offset.is_reversed.is_(False),
            )
        )
    )
    line_offset = db.scalar(
        select(Offset.id).where(
            Offset.payment_line_id == line.id,
            Offset.bill_id == data.bill_id,
            Offset.is_reversed.is_(False),
        )
    )
    case_ids = {item.case_id for item in items}
    item_total = sum((item.amount or Decimal("0") for item in items), Decimal("0"))
    if (
        not items
        or any(
            item.case_id is None
            or item.fee_type != "SERVICE"
            or item.amount is None
            or item.amount <= Decimal("0")
            for item in items
        )
        or len(case_ids) != 1
        or item_total != bill.amount
        or source is None
    ):
        raise_business_error(
            "DEMO_OFFSET_SCOPE_INVALID",
            "账单或回款不属于可核销的本地演示闭环",
            status_code=400,
        )
    expected_status = "UNSETTLED" if len(active_offsets) == 0 else "PARTIALLY_SETTLED"
    if (
        line_offset is not None
        or len(active_offsets) not in {0, 1}
        or bill.status != expected_status
    ):
        raise_business_error(
            "DEMO_OFFSET_STATE_CONFLICT",
            "账单核销顺序或当前状态冲突",
            status_code=409,
        )

    linked_payment_commands = []
    for command in db.scalars(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.operation == "PAYMENT",
        )
    ):
        payload = _demo_finance_payload(
            command,
            operation="PAYMENT",
            actor_id=command.created_by or "",
        )
        if (
            payload.get("target_bill_id") == bill.id
            and payload.get("pay_no") == payment.pay_no
            and payload.get("bank_ref_no") == payment.bank_ref_no
        ):
            linked_payment_commands.append(command)
    if (
        len(linked_payment_commands) != 1
        or bill.client_id != payment.client_id
        or bill.currency != payment.currency
        or bill.currency != "CNY"
        or line.case_id != next(iter(case_ids))
        or bill.balance <= Decimal("0")
        or line.balance_amt <= Decimal("0")
        or data.offset_amt != line.balance_amt
        or data.offset_amt > bill.balance
        or (len(active_offsets) == 1 and data.offset_amt != bill.balance)
    ):
        raise_business_error(
            "DEMO_OFFSET_BALANCE_CONFLICT",
            "核销金额、回款归属或账单权威余额冲突",
            status_code=400,
        )
    receipts_before = tuple(
        db.scalars(
            select(CaseReceipt).where(
                CaseReceipt.case_id == next(iter(case_ids)),
                CaseReceipt.fee_type == "SERVICE",
                CaseReceipt.currency == "CNY",
            )
        )
    )
    active_offset_total = sum(
        (row.offset_amt for row in active_offsets),
        Decimal("0"),
    )
    if (
        len(receipts_before) != len(active_offsets)
        or bill.balance != bill.amount - active_offset_total
        or (
            receipts_before
            and (
                receipts_before[0].receivable_amt != bill.amount
                or receipts_before[0].received_amt != active_offset_total
            )
        )
    ):
        raise_business_error(
            "DEMO_OFFSET_STORED_STATE_INVALID",
            "核销前的案件收款投影无效",
            status_code=409,
        )
    offset = Offset(
        id=str(uuid4()),
        payment_line_id=line.id,
        bill_id=bill.id,
        offset_amt=data.offset_amt,
        offset_date=data.offset_date,
        is_reversed=False,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(offset)
    bill.balance -= data.offset_amt
    _apply_bill_status(
        bill,
        "SETTLED" if bill.balance == Decimal("0") else "PARTIALLY_SETTLED",
    )
    bill.updated_by = actor_id
    line.allocated_amt += data.offset_amt
    line.balance_amt -= data.offset_amt
    line.updated_by = actor_id
    _allocate_offset_to_receipts(db, bill, data.offset_amt, data.offset_date)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise_business_error(
            "DEMO_OFFSET_CONCURRENT_CONFLICT",
            "核销命令与已存在记录冲突",
            status_code=409,
        )
    receipts = tuple(
        db.scalars(
            select(CaseReceipt).where(
                CaseReceipt.case_id == next(iter(case_ids)),
                CaseReceipt.fee_type == "SERVICE",
                CaseReceipt.currency == "CNY",
            )
        )
    )
    receipt = receipts[0] if len(receipts) == 1 else None
    if (
        receipt is None
        or receipt.receivable_amt != bill.amount
        or receipt.received_amt != bill.amount - bill.balance
        or line.allocated_amt != data.offset_amt
        or line.balance_amt != Decimal("0")
    ):
        raise_business_error(
            "DEMO_OFFSET_STORED_STATE_INVALID",
            "核销后的案件收款投影无效",
            status_code=409,
        )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_business_error(
            "DEMO_OFFSET_CONCURRENT_CONFLICT",
            "核销命令与已存在记录冲突",
            status_code=409,
        )
    db.refresh(offset)
    _run_commission_settleable_recompute_non_blocking(
        db,
        bill_id=bill.id,
        as_of_date=data.offset_date,
    )
    return DemoFullOffsetResult(
        offset_id=offset.id,
        bill_id=bill.id,
        line_id=line.id,
        receipt_id=receipt.id,
        idempotency_key=data.idempotency_key,
        reused=False,
    )


def reconcile_demo_full_offset(
    db: Session, idempotency_key: str, *, actor_id: str
) -> DemoFullOffsetResult:
    _demo_finance_scope_or_fail()
    command = get_demo_finance_command(
        db,
        operation="OFFSET",
        idempotency_key=idempotency_key,
        actor_id=actor_id,
    )
    if command is None:
        raise_business_error(
            "DEMO_OFFSET_COMMAND_NOT_FOUND",
            "未找到可对账的核销命令",
            status_code=404,
        )
    payload = _demo_finance_payload(command, operation="OFFSET", actor_id=actor_id)
    try:
        request = DemoFullOffsetRequest.model_validate(payload)
    except ValueError:
        raise_business_error(
            "DEMO_OFFSET_STORED_STATE_INVALID",
            "核销存量状态无效",
            status_code=409,
        )
    offsets = tuple(
        db.scalars(
            select(Offset).where(
                Offset.payment_line_id == request.payment_line_id,
                Offset.bill_id == request.bill_id,
                Offset.offset_amt == request.offset_amt,
                Offset.offset_date == request.offset_date,
                Offset.is_reversed.is_(False),
            )
        )
    )
    offset = offsets[0] if len(offsets) == 1 else None
    line = db.get(PaymentLine, request.payment_line_id)
    bill = db.get(Bill, request.bill_id)
    payment = db.get(Payment, line.payment_id) if line is not None else None
    source = db.scalar(
        select(BillDraftSource).where(BillDraftSource.bill_id == request.bill_id)
    )
    items = (
        tuple(db.scalars(select(BillItem).where(BillItem.bill_id == request.bill_id)))
        if bill is not None
        else ()
    )
    case_ids = {item.case_id for item in items}
    item_total = sum((item.amount or Decimal("0") for item in items), Decimal("0"))
    active_offsets = (
        tuple(
            db.scalars(
                select(Offset).where(
                    Offset.bill_id == request.bill_id,
                    Offset.is_reversed.is_(False),
                )
            )
        )
        if bill is not None
        else ()
    )
    if not offsets and not any(
        row.payment_line_id == request.payment_line_id for row in active_offsets
    ):
        raise_business_error(
            "DEMO_OFFSET_DOMAIN_RESULT_NOT_FOUND",
            "核销命令尚未形成可恢复的业务结果",
            status_code=404,
        )
    active_offset_total = sum(
        (row.offset_amt for row in active_offsets),
        Decimal("0"),
    )
    active_lines = tuple(
        db.get(PaymentLine, row.payment_line_id) for row in active_offsets
    )
    active_payments = tuple(
        db.get(Payment, row.payment_id) if row is not None else None
        for row in active_lines
    )
    payment_requests: list[DemoBankReceiptRequest] = []
    for payment_command in db.scalars(
        select(DemoFinanceCommand).where(
            DemoFinanceCommand.operation == "PAYMENT",
        )
    ):
        payment_payload = _demo_finance_payload(
            payment_command,
            operation="PAYMENT",
            actor_id=payment_command.created_by or "",
        )
        try:
            payment_request = DemoBankReceiptRequest.model_validate(payment_payload)
        except ValueError:
            raise_business_error(
                "DEMO_OFFSET_STORED_STATE_INVALID",
                "核销关联的回款命令无效",
                status_code=409,
            )
        if payment_request.target_bill_id == request.bill_id:
            payment_requests.append(payment_request)
    payment_requests_by_ref = {
        (row.pay_no, row.bank_ref_no): row for row in payment_requests
    }
    expected_balance = (
        bill.amount - active_offset_total if bill is not None else Decimal("-1")
    )
    expected_status = (
        "SETTLED" if expected_balance == Decimal("0") else "PARTIALLY_SETTLED"
    )
    receipts = (
        tuple(
            db.scalars(
                select(CaseReceipt).where(
                    CaseReceipt.case_id == next(iter(case_ids)),
                    CaseReceipt.fee_type == "SERVICE",
                    CaseReceipt.currency == "CNY",
                )
            )
        )
        if len(case_ids) == 1 and None not in case_ids
        else ()
    )
    receipt = receipts[0] if len(receipts) == 1 else None
    if (
        offset is None
        or line is None
        or bill is None
        or payment is None
        or source is None
        or receipt is None
        or not items
        or any(
            item.fee_type != "SERVICE"
            or item.case_id is None
            or item.amount is None
            or item.amount <= Decimal("0")
            for item in items
        )
        or len(case_ids) != 1
        or item_total != bill.amount
        or len(active_offsets) not in {1, 2}
        or len({row.payment_line_id for row in active_offsets}) != len(active_offsets)
        or any(row is None for row in active_lines)
        or any(row is None for row in active_payments)
        or len(payment_requests) != len(active_offsets)
        or len(payment_requests_by_ref) != len(payment_requests)
        or expected_balance < Decimal("0")
        or bill.balance != expected_balance
        or bill.status != expected_status
        or bill.direction != "AR"
        or bill.total_service != bill.amount
        or bill.total_gov != Decimal("0")
        or bill.total_misc != Decimal("0")
        or payment.client_id != bill.client_id
        or payment.currency != bill.currency
        or line.case_id != next(iter(case_ids))
        or receipt.receivable_amt != bill.amount
        or receipt.received_amt != active_offset_total
    ):
        raise_business_error(
            "DEMO_OFFSET_STORED_STATE_INVALID",
            "核销存量状态无效",
            status_code=409,
        )
    for active_offset, active_line, active_payment in zip(
        active_offsets,
        active_lines,
        active_payments,
        strict=True,
    ):
        payment_request = payment_requests_by_ref.get(
            (active_payment.pay_no, active_payment.bank_ref_no)
        )
        if (
            payment_request is None
            or active_payment.client_id != bill.client_id
            or active_payment.pay_date != payment_request.pay_date
            or active_payment.currency != payment_request.currency
            or active_payment.amount != payment_request.amount
            or active_payment.pay_method != payment_request.pay_method
            or active_payment.remark != payment_request.remark
            or active_line.case_id != next(iter(case_ids))
            or active_line.raw_amount != payment_request.amount
            or active_line.allocated_amt != active_offset.offset_amt
            or active_line.balance_amt != Decimal("0")
            or active_offset.offset_amt != payment_request.amount
        ):
            raise_business_error(
                "DEMO_OFFSET_STORED_STATE_INVALID",
                "核销关联的回款与结算金额无效",
                status_code=409,
            )
    return DemoFullOffsetResult(
        offset_id=offset.id,
        bill_id=offset.bill_id,
        line_id=line.id,
        receipt_id=receipt.id,
        idempotency_key=idempotency_key,
        reused=True,
    )


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
