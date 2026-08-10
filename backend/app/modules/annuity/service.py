from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from hashlib import sha256
from pathlib import Path
from re import fullmatch
from typing import Any
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import BusinessError, raise_business_error
from app.modules.annuity.export_excel import build_pay_list_export_xlsx
from app.modules.annuity.models import (
    AnnuityTask,
    FutureAnnuityReductionLineage,
    GovPayment,
    PayList,
    PayListExportArtifact,
)
from app.modules.billing.models import CaseReceipt
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import Document, DocumentEvidenceVersion
from app.modules.fees.annuity_reduction import (
    AnnuityReductionScopeError,
    validate_annuity_fee_reduction,
)
from app.modules.fees.cnipa_annuity_rate_candidate import select_cnipa_annuity_amount
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationError,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeRate,
    FeeReductionApproval,
    OfficialRateBook,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeDraftAuthority,
    FeeObligationLineInput,
    FeeOfficialEvidenceStatus,
    FeeSourceStatus,
    PrepareFeeObligationDraftCommand,
    PrepareFeeObligationDraftResult,
    RecognizeFeeObligationCommand,
    RecordFeeObligationInstructionCommand,
    RecordFeePaymentEvidenceCommand,
)
from app.modules.fees.obligation_service import (
    _future_annuity_exception_attestation_or_fail,
    calculate_annuity_payable_amount,
    get_fee_obligation,
    prepare_draft,
    recognize_obligation,
    record_client_instruction,
    record_payment_evidence,
)
from app.modules.fees.service import (
    fee_rate_effective_on_conditions,
    fee_rate_source_enabled_condition,
)
from app.modules.masterdata.clients.models import Client
from app.modules.system.future_annuity_exception_authority_service import (
    FutureAnnuityExceptionUseAttestation,
    ResolveFutureAnnuityExceptionCommand,
    resolve_future_annuity_exception,
)

_ALLOWED_INSTRUCTIONS = ("PAY", "ABANDON", "DEFER")
_ANNUITY_DRAFT_TYPE = "ANNUITY_FEE"
_TERMINAL_STATUSES = (
    "DONE",
    "CLOSED",
    "CANCELLED",
    "ABANDONED",
    "PAID",
    "SETTLED",
    "COMPLETED",
)

_ZERO = Decimal("0")
_MONEY_QUANT = Decimal("0.01")


def _coerce_date(value: Any, field_name: str) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise_business_error(
                "ANNUITY_DATE_RANGE_INVALID",
                f"Invalid {field_name}; expected YYYY-MM-DD",
                status_code=400,
            )
    raise_business_error(
        "ANNUITY_DATE_RANGE_INVALID",
        f"Invalid {field_name}; expected YYYY-MM-DD",
        status_code=400,
    )


def _normalize_statuses(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        values = [str(item).strip().upper() for item in value if str(item).strip()]
        return values
    text = str(value).strip()
    return [text.upper()] if text else []


def _normalize_optional_int(value: Any, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise_business_error(
            "ANNUITY_REPORT_FILTER_INVALID",
            f"Invalid {field_name}; expected integer",
            status_code=400,
        )


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_case_ids_for_annuity_filters(
    db: Session,
    *,
    case_id: Any = None,
    case_no: Any = None,
) -> list[str] | None:
    resolved_ids: set[str] | None = None

    normalized_case_id = _normalize_optional_text(case_id)
    if normalized_case_id:
        id_rows = db.execute(
            select(Case.id).where(
                or_(Case.id == normalized_case_id, Case.case_no == normalized_case_id)
            )
        ).scalars()
        resolved_ids = set(id_rows)

    normalized_case_no = _normalize_optional_text(case_no)
    if normalized_case_no:
        no_rows = db.execute(select(Case.id).where(Case.case_no == normalized_case_no)).scalars()
        no_ids = set(no_rows)
        resolved_ids = no_ids if resolved_ids is None else resolved_ids & no_ids

    return sorted(resolved_ids) if resolved_ids is not None else None


def _normalize_pending_mode(value: Any) -> str:
    if value is None:
        return "all"
    if isinstance(value, bool):
        return "pending" if value else "all"

    mode = str(value).strip().lower()
    aliases = {
        "": "all",
        "all": "all",
        "pending": "pending",
        "open": "pending",
        "todo": "pending",
        "processed": "processed",
        "done": "processed",
        "completed": "processed",
        "closed": "processed",
    }
    if mode in aliases:
        return aliases[mode]

    raise_business_error(
        "ANNUITY_PENDING_MODE_INVALID",
        "Invalid pending filter mode",
        details={"pending_mode": value},
        status_code=400,
    )


def list_annuity_tasks(
    db: Session,
    *,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AnnuityTask], int]:
    """List annuity tasks with range/status/pending filters and pagination."""
    filters = filters or {}

    due_from = _coerce_date(
        filters.get("date_from") or filters.get("due_from") or filters.get("due_date_from"),
        "due_from",
    )
    due_to = _coerce_date(
        filters.get("date_to") or filters.get("due_to") or filters.get("due_date_to"),
        "due_to",
    )
    if due_from and due_to and due_from > due_to:
        raise_business_error(
            "ANNUITY_DATE_RANGE_INVALID",
            "due_from must be <= due_to",
            status_code=400,
        )

    status_values = _normalize_statuses(filters.get("task_status", filters.get("status")))
    report_year = _normalize_optional_int(filters.get("annuity_year"), "annuity_year")
    pending_mode = _normalize_pending_mode(
        filters.get("pending_mode", filters.get("pending_filter", filters.get("pending")))
    )

    stmt = select(AnnuityTask)

    case_ids = _resolve_case_ids_for_annuity_filters(
        db,
        case_id=filters.get("case_id"),
        case_no=filters.get("case_no"),
    )
    client_id = filters.get("client_id")
    notice_status_values = _normalize_statuses(filters.get("notice_status"))

    if case_ids is not None:
        stmt = stmt.where(AnnuityTask.case_id.in_(case_ids))
    if client_id:
        stmt = stmt.where(AnnuityTask.client_id == client_id)
    if due_from:
        stmt = stmt.where(AnnuityTask.due_date >= due_from)
    if due_to:
        stmt = stmt.where(AnnuityTask.due_date <= due_to)
    if report_year is not None:
        stmt = stmt.where(AnnuityTask.year_no == report_year)
    if status_values:
        if len(status_values) == 1:
            stmt = stmt.where(func.upper(AnnuityTask.status) == status_values[0])
        else:
            stmt = stmt.where(func.upper(AnnuityTask.status).in_(status_values))
    if notice_status_values:
        if len(notice_status_values) == 1:
            stmt = stmt.where(func.upper(AnnuityTask.notice_status) == notice_status_values[0])
        else:
            stmt = stmt.where(func.upper(AnnuityTask.notice_status).in_(notice_status_values))

    if pending_mode == "pending":
        stmt = stmt.where(
            AnnuityTask.status.is_(None) | (~func.upper(AnnuityTask.status).in_(_TERMINAL_STATUSES))
        )
    elif pending_mode == "processed":
        stmt = stmt.where(func.upper(AnnuityTask.status).in_(_TERMINAL_STATUSES))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    offset = (page - 1) * page_size
    items = (
        db.execute(
            stmt.order_by(
                AnnuityTask.due_date.asc(),
                AnnuityTask.created_at.desc(),
                AnnuityTask.id.asc(),
            )
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return items, total


def extract_annuity_tasks(
    db: Session,
    *,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AnnuityTask], int]:
    """Compatibility alias for task-extraction wording in enhancement runbooks."""
    return list_annuity_tasks(db, filters=filters, page=page, page_size=page_size)


def summarize_annuity_tasks(tasks: list[AnnuityTask]) -> dict[str, Any]:
    today = date.today()
    status_counts: dict[str, int] = {}
    year_counts: dict[str, int] = {}
    open_task_count = 0
    done_task_count = 0
    overdue_task_count = 0

    for task in tasks:
        status = ((task.status or "").strip().upper()) or "UNKNOWN"
        year_key = str(task.year_no)

        status_counts[status] = status_counts.get(status, 0) + 1
        year_counts[year_key] = year_counts.get(year_key, 0) + 1

        if status == "OPEN":
            open_task_count += 1
        if status == "DONE":
            done_task_count += 1
        if task.due_date < today and status == "OPEN":
            overdue_task_count += 1

    return {
        "total_task_count": len(tasks),
        "open_task_count": open_task_count,
        "done_task_count": done_task_count,
        "overdue_task_count": overdue_task_count,
        "monitored_task_count": 0,
        "on_time_paid_count": 0,
        "late_paid_count": 0,
        "success_rate": None,
        "status_counts": [
            {"key": key, "count": status_counts[key]} for key in sorted(status_counts.keys())
        ],
        "year_counts": [
            {"key": key, "count": year_counts[key]} for key in sorted(year_counts.keys(), key=int)
        ],
    }


def _coerce_decimal(value: Decimal | None) -> Decimal:
    return value if value is not None else _ZERO


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_QUANT)


def _build_annuity_grouped_amounts(
    db: Session, tasks: list[AnnuityTask]
) -> dict[str, list[dict[str, Any]]]:
    if not tasks:
        return {
            "client_amounts": [],
            "country_amounts": [],
            "year_amounts": [],
        }

    case_ids = sorted({task.case_id for task in tasks})
    client_ids = sorted({task.client_id for task in tasks if task.client_id})

    case_rows = db.execute(
        select(Case.id, Case.from_country, Case.to_country).where(Case.id.in_(case_ids))
    ).all()
    case_map = {
        row.id: {
            "country": (row.to_country or row.from_country or "未填写"),
        }
        for row in case_rows
    }

    client_rows = db.execute(
        select(Client.id, Client.name_cn).where(Client.id.in_(client_ids))
    ).all()
    client_label_map = {row.id: row.name_cn or row.id for row in client_rows}

    payable_by_case_year: dict[tuple[str, int], Decimal] = defaultdict(lambda: _ZERO)
    case_total_payable: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    case_year_client: dict[tuple[str, int], str] = {}
    client_totals: dict[str, dict[str, Any]] = {}
    country_totals: dict[str, dict[str, Any]] = {}
    year_totals: dict[str, dict[str, Any]] = {}

    for task in tasks:
        case_year_key = (task.case_id, task.year_no)
        task_amount = _coerce_decimal(task.gov_fee_amt) + _coerce_decimal(task.service_fee_amt)
        payable_by_case_year[case_year_key] += task_amount
        case_total_payable[task.case_id] += task_amount
        case_year_client[case_year_key] = task.client_id

        client_key = task.client_id
        client_bucket = client_totals.setdefault(
            client_key,
            {
                "key": client_key,
                "label": client_label_map.get(client_key, client_key),
                "task_count": 0,
                "payable_amount": _ZERO,
                "official_paid_amount": _ZERO,
                "client_received_amount": _ZERO,
            },
        )
        client_bucket["task_count"] += 1
        client_bucket["payable_amount"] += _coerce_decimal(task.gov_fee_amt) + _coerce_decimal(
            task.service_fee_amt
        )

        country_key = case_map.get(task.case_id, {}).get("country", "未填写")
        country_bucket = country_totals.setdefault(
            country_key,
            {
                "key": country_key,
                "label": country_key,
                "task_count": 0,
                "payable_amount": _ZERO,
                "official_paid_amount": _ZERO,
                "client_received_amount": _ZERO,
            },
        )
        country_bucket["task_count"] += 1
        country_bucket["payable_amount"] += _coerce_decimal(task.gov_fee_amt) + _coerce_decimal(
            task.service_fee_amt
        )

        year_key = str(task.year_no)
        year_bucket = year_totals.setdefault(
            year_key,
            {
                "key": year_key,
                "label": f"第 {task.year_no} 年",
                "task_count": 0,
                "payable_amount": _ZERO,
                "official_paid_amount": _ZERO,
                "client_received_amount": _ZERO,
            },
        )
        year_bucket["task_count"] += 1
        year_bucket["payable_amount"] += _coerce_decimal(task.gov_fee_amt) + _coerce_decimal(
            task.service_fee_amt
        )

    gov_payments = db.execute(
        select(GovPayment.case_id, GovPayment.paid_amount)
        .where(GovPayment.case_id.in_(case_ids))
        .where(GovPayment.paid_date.is_not(None))
        .where(func.upper(GovPayment.status).in_(("PAID", "RECORDED")))
    ).all()
    for payment in gov_payments:
        case_id = payment.case_id
        amount = _coerce_decimal(payment.paid_amount)
        total_case_amount = case_total_payable.get(case_id, _ZERO)
        if amount == _ZERO or total_case_amount == _ZERO:
            continue
        for (task_case_id, year_no), task_total in payable_by_case_year.items():
            if task_case_id != case_id or task_total == _ZERO:
                continue
            share = amount * (task_total / total_case_amount)
            client_id = case_year_client[(case_id, year_no)]
            country_key = case_map.get(case_id, {}).get("country", "未填写")
            year_key = str(year_no)
            client_totals[client_id]["official_paid_amount"] += share
            country_totals[country_key]["official_paid_amount"] += share
            year_totals[year_key]["official_paid_amount"] += share

    case_receipts = db.execute(
        select(CaseReceipt.case_id, CaseReceipt.year_no, CaseReceipt.received_amt)
        .where(CaseReceipt.case_id.in_(case_ids))
        .where(CaseReceipt.year_no.is_not(None))
    ).all()
    for receipt in case_receipts:
        case_year_key = (receipt.case_id, int(receipt.year_no))
        if case_year_key not in payable_by_case_year:
            continue
        amount = _coerce_decimal(receipt.received_amt)
        if amount == _ZERO:
            continue
        client_id = case_year_client[case_year_key]
        country_key = case_map.get(receipt.case_id, {}).get("country", "未填写")
        year_key = str(int(receipt.year_no))
        client_totals[client_id]["client_received_amount"] += amount
        country_totals[country_key]["client_received_amount"] += amount
        year_totals[year_key]["client_received_amount"] += amount

    def _normalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
        return {
            **bucket,
            "payable_amount": _quantize_money(bucket["payable_amount"]),
            "official_paid_amount": _quantize_money(bucket["official_paid_amount"]),
            "client_received_amount": _quantize_money(bucket["client_received_amount"]),
        }

    return {
        "client_amounts": [
            _normalize_bucket(item)
            for item in sorted(client_totals.values(), key=lambda item: item["key"])
        ],
        "country_amounts": [
            _normalize_bucket(item)
            for item in sorted(country_totals.values(), key=lambda item: item["key"])
        ],
        "year_amounts": [
            _normalize_bucket(item)
            for item in sorted(year_totals.values(), key=lambda item: int(item["key"]))
        ],
    }


def _build_annuity_success_metrics(db: Session, tasks: list[AnnuityTask]) -> dict[str, Any]:
    monitored_tasks = [
        task for task in tasks if (task.client_instruction or "").strip().upper() == "PAY"
    ]
    monitored_task_count = len(monitored_tasks)
    if monitored_task_count == 0:
        return {
            "monitored_task_count": 0,
            "on_time_paid_count": 0,
            "late_paid_count": 0,
            "success_rate": None,
        }

    case_ids = sorted({task.case_id for task in monitored_tasks})
    lineage_payments = db.execute(
        select(GovPayment.case_id, FeeItem.year_no, GovPayment.paid_date)
        .join(FeeItem, FeeItem.id == GovPayment.fee_item_id)
        .where(GovPayment.case_id.in_(case_ids))
        .where(GovPayment.paid_date.is_not(None))
        .where(FeeItem.year_no.is_not(None))
        .where(func.upper(GovPayment.status).in_(("PAID", "RECORDED")))
    ).all()

    paid_dates_by_case_year: dict[tuple[str, int], list[date]] = defaultdict(list)
    for row in lineage_payments:
        if row.paid_date is None or row.year_no is None:
            continue
        paid_dates_by_case_year[(row.case_id, int(row.year_no))].append(row.paid_date)

    on_time_paid_count = 0
    late_paid_count = 0
    for task in monitored_tasks:
        paid_dates = paid_dates_by_case_year.get((task.case_id, task.year_no), [])
        if not paid_dates:
            continue
        earliest_paid_date = min(paid_dates)
        if earliest_paid_date <= task.due_date:
            on_time_paid_count += 1
        else:
            late_paid_count += 1

    return {
        "monitored_task_count": monitored_task_count,
        "on_time_paid_count": on_time_paid_count,
        "late_paid_count": late_paid_count,
        "success_rate": (
            on_time_paid_count / monitored_task_count if monitored_task_count > 0 else None
        ),
    }


def _build_annuity_payment_truth(
    db: Session, tasks: list[AnnuityTask]
) -> tuple[dict[str, int], dict[tuple[str, int], dict[str, bool]]]:
    if not tasks:
        return (
            {
                "official_paid_task_count": 0,
                "client_received_task_count": 0,
                "collected_not_paid_task_count": 0,
                "outstanding_task_count": 0,
            },
            {},
        )

    case_ids = sorted({task.case_id for task in tasks})
    official_required_by_case_year: dict[tuple[str, int], Decimal] = defaultdict(lambda: _ZERO)
    client_required_by_case_year: dict[tuple[str, int], Decimal] = defaultdict(lambda: _ZERO)

    for task in tasks:
        key = (task.case_id, task.year_no)
        official_required_by_case_year[key] += _coerce_decimal(task.gov_fee_amt)
        client_required_by_case_year[key] += _coerce_decimal(task.gov_fee_amt) + _coerce_decimal(
            task.service_fee_amt
        )

    official_paid_by_case_year: dict[tuple[str, int], Decimal] = defaultdict(lambda: _ZERO)
    gov_payments = db.execute(
        select(GovPayment.case_id, FeeItem.year_no, GovPayment.paid_amount)
        .join(FeeItem, FeeItem.id == GovPayment.fee_item_id)
        .where(GovPayment.case_id.in_(case_ids))
        .where(FeeItem.year_no.is_not(None))
        .where(GovPayment.paid_date.is_not(None))
        .where(func.upper(GovPayment.status).in_(("PAID", "RECORDED")))
    ).all()
    for row in gov_payments:
        if row.year_no is None:
            continue
        official_paid_by_case_year[(row.case_id, int(row.year_no))] += _coerce_decimal(
            row.paid_amount
        )

    client_received_by_case_year: dict[tuple[str, int], Decimal] = defaultdict(lambda: _ZERO)
    case_receipts = db.execute(
        select(CaseReceipt.case_id, CaseReceipt.year_no, CaseReceipt.received_amt)
        .where(CaseReceipt.case_id.in_(case_ids))
        .where(CaseReceipt.year_no.is_not(None))
    ).all()
    for row in case_receipts:
        if row.year_no is None:
            continue
        client_received_by_case_year[(row.case_id, int(row.year_no))] += _coerce_decimal(
            row.received_amt
        )

    truth_map: dict[tuple[str, int], dict[str, bool]] = {}
    summary = {
        "official_paid_task_count": 0,
        "client_received_task_count": 0,
        "collected_not_paid_task_count": 0,
        "outstanding_task_count": 0,
    }

    for task in tasks:
        key = (task.case_id, task.year_no)
        official_paid = (
            official_paid_by_case_year[key] >= official_required_by_case_year[key] > _ZERO
        )
        client_received = (
            client_received_by_case_year[key] >= client_required_by_case_year[key] > _ZERO
        )
        collected_not_paid = client_received and not official_paid
        outstanding = not client_received and not official_paid
        truth = {
            "official_paid": official_paid,
            "client_received": client_received,
            "collected_not_paid": collected_not_paid,
            "outstanding": outstanding,
        }
        truth_map[key] = truth
        if official_paid:
            summary["official_paid_task_count"] += 1
        if client_received:
            summary["client_received_task_count"] += 1
        if collected_not_paid:
            summary["collected_not_paid_task_count"] += 1
        if outstanding:
            summary["outstanding_task_count"] += 1

    return summary, truth_map


def list_annuity_tasks_report(
    db: Session,
    *,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AnnuityTask], int, dict[str, Any]]:
    """List annuity tasks with a report summary across the filtered result set."""
    filters = filters or {}
    stmt = select(AnnuityTask)

    due_from = _coerce_date(
        filters.get("date_from") or filters.get("due_from") or filters.get("due_date_from"),
        "due_from",
    )
    due_to = _coerce_date(
        filters.get("date_to") or filters.get("due_to") or filters.get("due_date_to"),
        "due_to",
    )
    if due_from and due_to and due_from > due_to:
        raise_business_error(
            "ANNUITY_DATE_RANGE_INVALID",
            "due_from must be <= due_to",
            status_code=400,
        )

    status_values = _normalize_statuses(filters.get("task_status", filters.get("status")))
    report_year = _normalize_optional_int(filters.get("annuity_year"), "annuity_year")
    payment_status = _normalize_optional_text(filters.get("payment_status"))
    if payment_status is not None:
        payment_status = payment_status.upper()
        if payment_status not in {"PAID", "UNPAID"}:
            raise_business_error(
                "ANNUITY_PAYMENT_STATUS_INVALID",
                "payment_status must be PAID or UNPAID",
                status_code=400,
            )
    pending_mode = _normalize_pending_mode(
        filters.get("pending_mode", filters.get("pending_filter", filters.get("pending")))
    )

    case_ids = _resolve_case_ids_for_annuity_filters(
        db,
        case_id=filters.get("case_id"),
        case_no=filters.get("case_no"),
    )
    client_id = filters.get("client_id")
    notice_status_values = _normalize_statuses(filters.get("notice_status"))

    if case_ids is not None:
        stmt = stmt.where(AnnuityTask.case_id.in_(case_ids))
    if client_id:
        stmt = stmt.where(AnnuityTask.client_id == client_id)
    if due_from:
        stmt = stmt.where(AnnuityTask.due_date >= due_from)
    if due_to:
        stmt = stmt.where(AnnuityTask.due_date <= due_to)
    if report_year is not None:
        stmt = stmt.where(AnnuityTask.year_no == report_year)
    if status_values:
        if len(status_values) == 1:
            stmt = stmt.where(func.upper(AnnuityTask.status) == status_values[0])
        else:
            stmt = stmt.where(func.upper(AnnuityTask.status).in_(status_values))
    if notice_status_values:
        if len(notice_status_values) == 1:
            stmt = stmt.where(func.upper(AnnuityTask.notice_status) == notice_status_values[0])
        else:
            stmt = stmt.where(func.upper(AnnuityTask.notice_status).in_(notice_status_values))

    if pending_mode == "pending":
        stmt = stmt.where(
            AnnuityTask.status.is_(None) | (~func.upper(AnnuityTask.status).in_(_TERMINAL_STATUSES))
        )
    elif pending_mode == "processed":
        stmt = stmt.where(func.upper(AnnuityTask.status).in_(_TERMINAL_STATUSES))

    ordered_stmt = stmt.order_by(
        AnnuityTask.due_date.asc(),
        AnnuityTask.created_at.desc(),
        AnnuityTask.id.asc(),
    )
    all_items = db.execute(ordered_stmt).scalars().all()
    if payment_status is not None:
        _payment_summary, payment_truth = _build_annuity_payment_truth(db, all_items)
        expect_paid = payment_status == "PAID"
        all_items = [
            task
            for task in all_items
            if payment_truth.get((task.case_id, task.year_no), {}).get("official_paid", False)
            == expect_paid
        ]
    total = len(all_items)
    offset = (page - 1) * page_size
    items = all_items[offset : offset + page_size]
    summary = summarize_annuity_tasks(all_items)
    summary.update(_build_annuity_payment_truth(db, all_items)[0])
    summary.update(_build_annuity_success_metrics(db, all_items))
    summary.update(_build_annuity_grouped_amounts(db, all_items))
    return items, total, summary


def update_annuity_task_instruction(
    db: Session,
    *,
    task_id: int,
    instruction: str,
    instruction_date: date | None = None,
) -> AnnuityTask:
    """Update client instruction with legal transition checks."""
    task = db.execute(select(AnnuityTask).where(AnnuityTask.id == task_id)).scalar_one_or_none()
    if not task:
        raise_business_error("ANNUITY_TASK_NOT_FOUND", "Annuity task not found", status_code=404)

    new_instruction = (instruction or "").strip().upper()
    if new_instruction not in _ALLOWED_INSTRUCTIONS:
        raise_business_error(
            "ANNUITY_INSTRUCTION_INVALID",
            "Invalid instruction; allowed values are PAY/ABANDON/DEFER",
            status_code=400,
        )

    current_status = ((task.status or "") if task.status is not None else "").strip().upper()
    if current_status in _TERMINAL_STATUSES:
        raise_business_error(
            "ANNUITY_STATE_CONFLICT",
            "Instruction update is not allowed for current task state",
            details={"status": task.status},
            status_code=409,
        )

    current_instruction = (
        ((task.client_instruction or "") if task.client_instruction is not None else "")
        .strip()
        .upper()
    )
    if not current_instruction:
        current_instruction = "NONE"

    allowed_transitions = {
        "NONE": {"PAY", "ABANDON", "DEFER"},
        "DEFER": {"PAY", "ABANDON", "DEFER"},
        "PAY": {"PAY"},
        "ABANDON": {"ABANDON"},
    }
    if new_instruction not in allowed_transitions.get(current_instruction, set()):
        raise_business_error(
            "ANNUITY_INSTRUCTION_INVALID",
            "Invalid instruction transition",
            details={"from": current_instruction, "to": new_instruction},
            status_code=400,
        )

    instruction_changed = task.client_instruction != new_instruction
    task.client_instruction = new_instruction
    if instruction_date is not None:
        task.instruction_date = instruction_date
    elif instruction_changed and task.instruction_date is None:
        task.instruction_date = date.today()

    db.commit()
    db.refresh(task)
    return task


def _annuity_marker(task_id: int, year_no: int) -> str:
    return f"ANNUITY_TASK:{task_id};YEAR:{year_no}"


def _money_amount(value: Any) -> Decimal:
    if value is None or value == "":
        return _ZERO
    try:
        return Decimal(str(value)).quantize(_MONEY_QUANT)
    except (InvalidOperation, ValueError):
        return _ZERO


def _rate_amount_for_year(rate: FeeRate, year_no: int | None) -> Decimal:
    default_amount = _money_amount(rate.default_amount)
    if year_no is None or (rate.calc_mode or "").strip().upper() != "TIER":
        return default_amount

    try:
        parsed_params = json.loads(rate.calc_params or "{}")
    except (TypeError, ValueError):
        return default_amount

    if not isinstance(parsed_params, dict):
        return default_amount

    tiers = parsed_params.get("tiers")
    if not isinstance(tiers, list):
        return default_amount

    for tier in tiers:
        if not isinstance(tier, dict):
            continue
        try:
            start_year = int(tier.get("from"))
            end_year = int(tier.get("to", start_year))
        except (TypeError, ValueError):
            continue
        if start_year <= year_no <= end_year:
            return _money_amount(tier.get("amount", default_amount))

    return default_amount


def _rate_amount(
    db: Session,
    *,
    fee_type: str,
    currency: str,
    year_no: int | None = None,
    patent_category: str | None = None,
) -> Decimal:
    conditions = [
        FeeRate.enabled.is_(True),
        FeeRate.rate_group == "ANNUITY",
        FeeRate.fee_type == fee_type,
        FeeRate.currency == currency,
        fee_rate_source_enabled_condition(),
        *fee_rate_effective_on_conditions(date.today()),
    ]

    normalized_patent_category = (patent_category or "").strip() or None
    if normalized_patent_category:
        conditions.append(
            or_(
                FeeRate.patent_category == normalized_patent_category,
                FeeRate.patent_category.is_(None),
                FeeRate.patent_category == "",
            )
        )

    rates = (
        db.execute(select(FeeRate).where(*conditions).order_by(FeeRate.updated_at.desc()))
        .scalars()
        .all()
    )
    if not rates:
        return _ZERO

    if normalized_patent_category:
        for rate in rates:
            if rate.patent_category == normalized_patent_category:
                return _rate_amount_for_year(rate, year_no)
        for rate in rates:
            if not rate.patent_category:
                return _rate_amount_for_year(rate, year_no)
        return _ZERO

    return _rate_amount_for_year(rates[0], year_no)


def _draft_exists_for_target(
    db: Session,
    *,
    task_id: int,
    year_no: int,
) -> bool:
    marker = _annuity_marker(task_id, year_no)
    row = db.execute(
        select(FeeItem.id)
        .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
        .where(
            FeeDraft.draft_type == _ANNUITY_DRAFT_TYPE,
            FeeItem.remark == marker,
        )
        .limit(1)
    ).scalar_one_or_none()
    return row is not None


def _build_generation_targets(
    db: Session,
    *,
    task_ids: list[int],
    pay_next_year: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    failed: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []

    tasks = db.execute(select(AnnuityTask).where(AnnuityTask.id.in_(task_ids))).scalars().all()
    task_map = {task.id: task for task in tasks}

    for task_id in task_ids:
        task = task_map.get(task_id)
        if task is None:
            failed.append(
                {
                    "source_task_id": task_id,
                    "task_id": task_id,
                    "year_no": None,
                    "pay_next_year": False,
                    "code": "ANNUITY_TASK_NOT_FOUND",
                    "message": "Annuity task not found",
                    "status_code": 404,
                }
            )
            continue

        targets.append(
            {
                "source_task_id": task.id,
                "task": task,
                "task_id": task.id,
                "year_no": task.year_no,
                "pay_next_year": False,
            }
        )

        if not pay_next_year:
            continue

        next_task = (
            db.execute(
                select(AnnuityTask)
                .where(
                    AnnuityTask.case_id == task.case_id,
                    AnnuityTask.year_no == task.year_no + 1,
                )
                .order_by(AnnuityTask.due_date.asc(), AnnuityTask.id.asc())
            )
            .scalars()
            .first()
        )
        if next_task is None:
            failed.append(
                {
                    "source_task_id": task.id,
                    "task_id": None,
                    "year_no": task.year_no + 1,
                    "pay_next_year": True,
                    "code": "ANNUITY_TASK_NOT_FOUND",
                    "message": "Next-year annuity task not found",
                    "status_code": 404,
                }
            )
            continue

        targets.append(
            {
                "source_task_id": task.id,
                "task": next_task,
                "task_id": next_task.id,
                "year_no": next_task.year_no,
                "pay_next_year": True,
            }
        )

    return targets, failed


def generate_fee_drafts_from_annuity_tasks(
    db: Session,
    *,
    task_ids: list[int],
    pay_next_year: bool = False,
    currency: str = "CNY",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Generate annuity fee drafts for selected tasks with per-task result details."""
    normalized_currency = (currency or "").strip().upper() or "CNY"

    normalized_task_ids: list[int] = []
    seen_ids: set[int] = set()
    for task_id in task_ids:
        try:
            normalized = int(task_id)
        except (TypeError, ValueError):
            continue
        if normalized in seen_ids:
            continue
        seen_ids.add(normalized)
        normalized_task_ids.append(normalized)

    if not normalized_task_ids:
        raise_business_error(
            "ANNUITY_TASK_REQUIRED",
            "At least one annuity task is required",
            status_code=400,
        )

    targets, failed = _build_generation_targets(
        db,
        task_ids=normalized_task_ids,
        pay_next_year=pay_next_year,
    )

    success: list[dict[str, Any]] = []
    processed_targets: set[tuple[int, int]] = set()

    for target in targets:
        task: AnnuityTask = target["task"]
        task_id = int(target["task_id"])
        year_no = int(target["year_no"])
        key = (task_id, year_no)

        if key in processed_targets:
            failed.append(
                {
                    "source_task_id": target["source_task_id"],
                    "task_id": task_id,
                    "year_no": year_no,
                    "pay_next_year": target["pay_next_year"],
                    "code": "ANNUITY_DRAFT_ALREADY_GENERATED",
                    "message": "Annuity draft already generated in this request",
                    "status_code": 409,
                }
            )
            continue
        processed_targets.add(key)

        try:
            task_status = (task.status or "").strip().upper()
            if task_status in _TERMINAL_STATUSES:
                raise_business_error(
                    "ANNUITY_STATE_CONFLICT",
                    "Cannot generate draft for terminal task status",
                    details={"status": task.status},
                    status_code=409,
                )

            if _draft_exists_for_target(db, task_id=task_id, year_no=year_no):
                raise_business_error(
                    "ANNUITY_DRAFT_ALREADY_GENERATED",
                    "Draft already generated for task/year",
                    status_code=409,
                )

            carrier = (
                task.source_activity_id,
                task.source_document_id,
                task.source_evidence_version_id,
                task.source_evidence_content_hash,
                task.fee_obligation_id,
                task.grant_fee_year_key,
            )
            if all(value is None for value in carrier):
                _annuity_instruction_not_found("年费任务尚未关联费用义务")
            if any(value is None for value in carrier):
                _annuity_instruction_conflict("年费任务费用义务谱系不完整")
            if (
                not all(_annuity_instruction_exact_string(value) for value in carrier[:3])
                or not _annuity_instruction_exact_string(carrier[3], 71)
                or fullmatch(r"sha256:[0-9a-f]{64}", carrier[3]) is None
                or not _annuity_instruction_exact_string(carrier[4])
                or type(carrier[5]) is not int
                or type(carrier[5]) is bool
                or carrier[5] <= 0
            ):
                _annuity_instruction_conflict("年费任务费用义务谱系格式无效")
            obligation = db.get(FeeObligation, task.fee_obligation_id)
            case = db.get(Case, task.case_id)
            if obligation is None:
                _annuity_instruction_not_found("年费任务费用义务不存在")
            if case is None:
                _annuity_instruction_not_found("年费任务案件不存在")
            _validate_annuity_instruction_lineage(
                db,
                task=task,
                obligation=obligation,
                case=case,
            )
            if obligation.currency != normalized_currency:
                _annuity_instruction_conflict("年费任务请款币种与费用义务不一致")

            idempotency_key = f"annuity-draft:{task_id}:{obligation.id}"
            connection = db.connection()
            if (
                connection.dialect.name == "sqlite"
                and not connection.connection.driver_connection.in_transaction
            ):
                connection.exec_driver_sql("BEGIN")
            with db.begin_nested():
                delegated = prepare_draft(
                    PrepareFeeObligationDraftCommand(
                        obligation_id=obligation.id,
                        actor_id=actor_id,
                        idempotency_key=idempotency_key,
                    ),
                    db,
                )
                draft = db.get(FeeDraft, delegated.draft_id)
                if (
                    delegated.obligation_id != obligation.id
                    or delegated.idempotency_key != idempotency_key
                    or not delegated.activity_id
                    or not delegated.links
                    or draft is None
                    or draft.case_id != task.case_id
                    or draft.client_id != task.client_id
                    or draft.currency != normalized_currency
                ):
                    _annuity_instruction_conflict("年费任务请款草稿谱系不一致")
                links: list[dict[str, Any]] = []
                for link in delegated.links:
                    stored_link = db.get(FeeObligationDraftItemLink, link.id)
                    fee_item = db.get(FeeItem, link.fee_item_id)
                    if (
                        stored_link is None
                        or stored_link.obligation_line_id != link.obligation_line_id
                        or stored_link.fee_item_id != link.fee_item_id
                        or fee_item is None
                        or fee_item.draft_id != draft.id
                        or fee_item.case_id != task.case_id
                    ):
                        _annuity_instruction_conflict("年费任务请款草稿谱系不一致")
                    links.append(
                        {
                            "id": link.id,
                            "obligation_line_id": link.obligation_line_id,
                            "fee_item_id": link.fee_item_id,
                            "reused": link.reused,
                        }
                    )
            success.append(
                {
                    "source_task_id": target["source_task_id"],
                    "task_id": task_id,
                    "year_no": year_no,
                    "obligation_id": delegated.obligation_id,
                    "draft_id": draft.id,
                    "links": links,
                    "activity_id": delegated.activity_id,
                    "activity_reused": delegated.activity_reused,
                    "idempotency_key": delegated.idempotency_key,
                    "currency": draft.currency,
                    "amount": str(draft.amount),
                    "pay_next_year": target["pay_next_year"],
                }
            )
        except BusinessError as exc:
            failed.append(
                {
                    "source_task_id": target["source_task_id"],
                    "task_id": task_id,
                    "year_no": year_no,
                    "pay_next_year": target["pay_next_year"],
                    "code": exc.code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                }
            )

    return {
        "summary": {
            "requested": len(normalized_task_ids),
            "targets": len(targets),
            "success": len(success),
            "failed": len(failed),
            "pay_next_year": pay_next_year,
        },
        "success": success,
        "failed": failed,
    }


def create_pay_list_from_fee_items(
    db: Session,
    *,
    fee_item_ids: list[str],
    planned_pay_date: date | None = None,
    remark: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Create pay list + gov payment rows from fee item IDs with scope constraints."""
    normalized_ids: list[str] = []
    seen_ids: set[str] = set()
    for fee_item_id in fee_item_ids:
        value = str(fee_item_id).strip()
        if not value or value in seen_ids:
            continue
        seen_ids.add(value)
        normalized_ids.append(value)

    if not normalized_ids:
        raise_business_error(
            "FEE_ITEM_REQUIRED",
            "At least one fee item is required",
            status_code=400,
        )

    rows = db.execute(
        select(FeeItem, FeeDraft)
        .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
        .where(FeeItem.id.in_(normalized_ids))
    ).all()
    row_map: dict[str, tuple[FeeItem, FeeDraft]] = {row[0].id: (row[0], row[1]) for row in rows}

    existing_payment_ids = set(
        db.execute(
            select(GovPayment.fee_item_id).where(GovPayment.fee_item_id.in_(normalized_ids))
        ).scalars()
    )

    failed: list[dict[str, Any]] = []
    candidates: list[tuple[FeeItem, FeeDraft]] = []

    for fee_item_id in normalized_ids:
        row = row_map.get(fee_item_id)
        if row is None:
            failed.append(
                {
                    "fee_item_id": fee_item_id,
                    "code": "FEE_ITEM_NOT_FOUND",
                    "message": "Fee item not found",
                    "status_code": 404,
                }
            )
            continue

        item, draft = row
        fee_type = (item.fee_type or "").strip().upper()
        if fee_type != "GOV":
            failed.append(
                {
                    "fee_item_id": fee_item_id,
                    "code": "PAY_LIST_SCOPE_INVALID",
                    "message": "Only GOV fee items can be used to create pay list",
                    "status_code": 400,
                }
            )
            continue

        if fee_item_id in existing_payment_ids:
            failed.append(
                {
                    "fee_item_id": fee_item_id,
                    "code": "GOV_PAYMENT_DUPLICATE",
                    "message": "Gov payment already exists for fee item",
                    "status_code": 409,
                }
            )
            continue

        if not draft.client_id or not draft.currency:
            failed.append(
                {
                    "fee_item_id": fee_item_id,
                    "code": "PAY_LIST_SCOPE_INVALID",
                    "message": "Fee item draft is missing client/currency",
                    "status_code": 400,
                }
            )
            continue
        if not item.case_id:
            failed.append(
                {
                    "fee_item_id": fee_item_id,
                    "code": "PAY_LIST_SCOPE_INVALID",
                    "message": "Fee item is missing case_id",
                    "status_code": 400,
                }
            )
            continue

        candidates.append((item, draft))

    baseline_client: str | None = None
    baseline_currency: str | None = None
    scoped_items: list[tuple[FeeItem, FeeDraft]] = []
    candidate_scopes = {(draft.client_id, draft.currency) for _, draft in candidates}
    scope_conflict = len(candidate_scopes) > 1

    if scope_conflict:
        failed.extend(
            {
                "fee_item_id": item.id,
                "code": "PAY_LIST_SCOPE_INVALID",
                "message": "Selected fee items must belong to the same client and currency",
                "status_code": 400,
            }
            for item, _draft in candidates
        )
    else:
        for item, draft in candidates:
            if baseline_client is None:
                baseline_client = draft.client_id
                baseline_currency = draft.currency
            scoped_items.append((item, draft))

    if scope_conflict or not scoped_items or baseline_client is None or baseline_currency is None:
        return {
            "summary": {
                "requested": len(normalized_ids),
                "success": 0,
                "failed": len(failed),
                "pay_list_created": False,
            },
            "pay_list": None,
            "success": [],
            "failed": failed,
        }

    linked_activity_rows: list[tuple[FeeItem, FeeDraft, FeeObligation, tuple[str, ...]]] = []
    for item, draft in scoped_items:
        obligation_context = _gov_payment_obligation_context(db, fee_item_id=item.id)
        if obligation_context is None:
            raise_business_error(
                "PAY_LIST_OBLIGATION_LINK_REQUIRED",
                "Fee item must be linked to a fee obligation",
                status_code=409,
            )
        obligation, obligation_line_ids = obligation_context
        if item.case_id != draft.case_id or obligation.case_id != item.case_id:
            raise_business_error(
                "PAY_LIST_OBLIGATION_SCOPE_MISMATCH",
                "Fee item, draft, and obligation must belong to the same case",
                status_code=409,
            )
        if obligation.client_instruction_status != "PAY":
            raise_business_error(
                "PAY_LIST_CLIENT_INSTRUCTION_REQUIRED",
                "创建缴费清单前必须记录客户缴费指示",
                status_code=409,
            )
        linked_activity_rows.append((item, draft, obligation, obligation_line_ids))

    activity_rows_by_case: dict[
        str, list[tuple[FeeItem, FeeDraft, FeeObligation, tuple[str, ...]]]
    ] = defaultdict(list)
    for row in linked_activity_rows:
        activity_rows_by_case[row[2].case_id].append(row)
    source_activity_by_case: dict[str, str] = {}
    for case_id, activity_rows in activity_rows_by_case.items():
        source_activity_ids = {row[2].source_activity_id for row in activity_rows}
        if None in source_activity_ids or len(source_activity_ids) != 1:
            raise_business_error(
                "PAY_LIST_SOURCE_ACTIVITY_CONFLICT",
                "Fee obligations in one case must share one source activity",
                status_code=409,
            )
        source_activity_by_case[case_id] = next(iter(source_activity_ids))

    total_amount = sum((Decimal(item.amount or 0) for item, _ in scoped_items), Decimal("0"))
    pay_list = PayList(
        client_id=baseline_client,
        status="DRAFT",
        currency=baseline_currency,
        planned_pay_date=planned_pay_date,
        total_amount=total_amount,
        remark=remark,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(pay_list)
    db.flush()
    pay_list.pay_list_no = f"PL-{pay_list.id:06d}"

    success: list[dict[str, Any]] = []
    for item, _draft in scoped_items:
        amount = Decimal(item.amount or 0)
        db.add(
            GovPayment(
                pay_list_id=pay_list.id,
                case_id=item.case_id,
                fee_item_id=item.id,
                status="PLANNED",
                currency=baseline_currency,
                paid_date=None,
                paid_amount=amount,
                official_receipt_no=None,
                remark=f"from_fee_item:{item.id}",
                fee_code=item.fee_code,
                year_no=item.year_no,
                planned_amt=amount,
                planned_currency=baseline_currency,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )
        success.append(
            {
                "fee_item_id": item.id,
                "case_id": item.case_id,
                "amount": str(amount),
                "currency": baseline_currency,
                "pay_list_id": pay_list.id,
            }
        )

    occurred_at = datetime.now(timezone.utc).replace(tzinfo=None)
    for case_id, activity_rows in activity_rows_by_case.items():
        case = db.get(Case, case_id)
        if case is None:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
        resolved_actor_id = next(
            (
                value
                for item, draft, obligation, _line_ids in activity_rows
                for value in (
                    actor_id,
                    item.updated_by,
                    item.created_by,
                    draft.updated_by,
                    draft.created_by,
                    obligation.updated_by,
                    obligation.created_by,
                )
                if value
            ),
            None,
        )
        if resolved_actor_id is None:
            raise_business_error(
                "PAY_LIST_ACTOR_REQUIRED",
                "actor_id is required for obligation-linked pay list creation",
                status_code=409,
            )
        obligation_ids = sorted({row[2].id for row in activity_rows})
        obligation_line_ids = sorted({line_id for row in activity_rows for line_id in row[3]})
        projection = _gov_payment_projection(case)
        append_case_activity(
            LifecycleEventCommand(
                case_id=case_id,
                event_type="PAY_LIST_CREATED",
                lane=ActivityLane.FEE,
                effective_at=occurred_at,
                occurred_at=occurred_at,
                evidence_refs=(),
                actor_id=resolved_actor_id,
                reviewer_id=None,
                idempotency_key=f"pay-list:{pay_list.id}:created",
                source_activity_id=source_activity_by_case[case_id],
                supersedes_event_id=None,
                payload={
                    "actor_id": resolved_actor_id,
                    "center_changes": {},
                    "fee_item_ids": sorted(row[0].id for row in activity_rows),
                    "obligation_ids": obligation_ids,
                    "obligation_line_ids": obligation_line_ids,
                    "pay_list_id": pay_list.id,
                    "schema": "FPMS_PAY_LIST_CREATED_V1",
                },
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            db,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=case.status,
            conflict_codes=(),
        )

    db.flush()
    db.refresh(pay_list)

    return {
        "summary": {
            "requested": len(normalized_ids),
            "success": len(success),
            "failed": len(failed),
            "pay_list_created": True,
        },
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "client_id": pay_list.client_id,
            "currency": pay_list.currency,
            "status": pay_list.status,
            "planned_pay_date": pay_list.planned_pay_date,
            "total_amount": str(pay_list.total_amount),
        },
        "success": success,
        "failed": failed,
    }


def create_historical_pay_list(
    db: Session,
    *,
    client_id: str | None,
    currency: str = "CNY",
    planned_pay_date: date | None = None,
    remark: str | None = None,
    list_type: str | None = None,
    flow_dir: str | None = None,
    invoice_no_from: str | None = None,
    invoice_no_to: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    normalized_client_id = (client_id or "").strip()
    if not normalized_client_id:
        raise_business_error(
            "PAY_LIST_CLIENT_REQUIRED",
            "client_id is required",
            status_code=400,
        )

    client = db.execute(
        select(Client).where(Client.id == normalized_client_id)
    ).scalar_one_or_none()
    if client is None:
        raise_business_error("CLIENT_NOT_FOUND", "Client not found", status_code=404)

    normalized_currency = (currency or "").strip().upper() or "CNY"
    pay_list = PayList(
        client_id=normalized_client_id,
        status="DRAFT",
        currency=normalized_currency,
        planned_pay_date=planned_pay_date,
        total_amount=Decimal("0"),
        remark=remark,
        list_type=_normalize_optional_text(list_type),
        flow_dir=_normalize_optional_text(flow_dir),
        invoice_no_from=_normalize_optional_text(invoice_no_from),
        invoice_no_to=_normalize_optional_text(invoice_no_to),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(pay_list)
    db.flush()
    pay_list.pay_list_no = f"PL-{pay_list.id:06d}"

    db.commit()
    db.refresh(pay_list)

    return {
        "id": pay_list.id,
        "pay_list_no": pay_list.pay_list_no,
        "client_id": pay_list.client_id,
        "status": pay_list.status,
        "currency": pay_list.currency,
        "planned_pay_date": pay_list.planned_pay_date,
        "paid_date": pay_list.paid_date,
        "total_amount": str(pay_list.total_amount),
        "remark": pay_list.remark,
        "list_type": pay_list.list_type,
        "flow_dir": pay_list.flow_dir,
        "invoice_no_from": pay_list.invoice_no_from,
        "invoice_no_to": pay_list.invoice_no_to,
        "created_at": pay_list.created_at,
        "updated_at": pay_list.updated_at,
        "created_by": pay_list.created_by,
        "updated_by": pay_list.updated_by,
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportInternalPayListCommand:
    pay_list_id: int
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ExportInternalPayListResult:
    artifact_id: str
    pay_list_id: int
    filename: str
    content_type: str
    content: bytes
    content_sha256: str
    managed_storage_path: str
    activity_ids: tuple[str, ...]
    generated_at: datetime
    idempotency_key: str
    reused: bool


_PAY_LIST_EXPORT_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _fail_internal_export_conflict() -> None:
    raise_business_error(
        "PAY_LIST_EXPORT_IDEMPOTENCY_CONFLICT",
        "Pay-list export idempotency carrier conflicts with this request",
        status_code=409,
    )


def _validate_internal_export_command(command: ExportInternalPayListCommand) -> None:
    if type(command.pay_list_id) is not int or command.pay_list_id <= 0:
        raise_business_error(
            "PAY_LIST_EXPORT_INPUT_INVALID",
            "pay_list_id must be a positive integer",
            status_code=400,
        )
    if (
        type(command.actor_id) is not str
        or not command.actor_id
        or command.actor_id.strip() != command.actor_id
        or len(command.actor_id) > 36
    ):
        raise_business_error(
            "PAY_LIST_EXPORT_INPUT_INVALID",
            "actor_id must be canonical",
            status_code=400,
        )
    if (
        type(command.idempotency_key) is not str
        or not command.idempotency_key.strip()
        or len(command.idempotency_key) > 128
    ):
        raise_business_error(
            "PAY_LIST_EXPORT_INPUT_INVALID",
            "idempotency_key must be nonblank and at most 128 characters",
            status_code=400,
        )


def _internal_export_relative_path(pay_list_id: int, artifact_id: str) -> Path:
    return Path("pay-list-exports") / str(pay_list_id) / f"{artifact_id}.xlsx"


def _resolve_internal_export_path(
    *,
    pay_list_id: int,
    artifact_id: str,
    managed_storage_path: str,
    storage_dir: str | Path,
) -> Path:
    relative_path = _internal_export_relative_path(pay_list_id, artifact_id)
    if managed_storage_path != relative_path.as_posix():
        _fail_internal_export_conflict()

    storage_root = Path(storage_dir)
    if storage_root.is_symlink():
        _fail_internal_export_conflict()
    resolved_root = storage_root.resolve(strict=False)
    candidate = resolved_root / relative_path
    if not candidate.resolve(strict=False).is_relative_to(resolved_root):
        _fail_internal_export_conflict()

    current = resolved_root
    for part in relative_path.parts:
        current /= part
        if current.is_symlink():
            _fail_internal_export_conflict()
    return candidate


def compensate_internal_pay_list_export(
    managed_storage_path: str,
    *,
    storage_dir: str | Path | None = None,
) -> None:
    parts = Path(managed_storage_path).parts
    if (
        len(parts) != 3
        or parts[0] != "pay-list-exports"
        or not parts[1].isdigit()
        or not parts[2].endswith(".xlsx")
    ):
        raise_business_error(
            "PAY_LIST_EXPORT_STORAGE_COMPENSATION_FAILED",
            "Managed pay-list export path is invalid",
            status_code=500,
        )
    artifact_id = parts[2][:-5]
    try:
        target = _resolve_internal_export_path(
            pay_list_id=int(parts[1]),
            artifact_id=artifact_id,
            managed_storage_path=managed_storage_path,
            storage_dir=storage_dir if storage_dir is not None else get_settings().storage_dir,
        )
        target.unlink(missing_ok=True)
    except (BusinessError, OSError) as exc:
        raise BusinessError(
            "PAY_LIST_EXPORT_STORAGE_COMPENSATION_FAILED",
            "Could not remove managed pay-list export",
            status_code=500,
        ) from exc


def _write_internal_export(
    *,
    pay_list_id: int,
    artifact_id: str,
    content: bytes,
) -> tuple[str, bytes]:
    managed_storage_path = _internal_export_relative_path(pay_list_id, artifact_id).as_posix()
    temporary: Path | None = None
    target: Path | None = None
    try:
        target = _resolve_internal_export_path(
            pay_list_id=pay_list_id,
            artifact_id=artifact_id,
            managed_storage_path=managed_storage_path,
            storage_dir=get_settings().storage_dir,
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
        temporary.write_bytes(content)
        temporary.replace(target)
        stored_content = target.read_bytes()
    except BusinessError:
        raise
    except OSError as exc:
        try:
            if temporary is not None and (temporary.exists() or temporary.is_symlink()):
                temporary.unlink()
            if target is not None and (target.exists() or target.is_symlink()):
                target.unlink()
        except OSError as cleanup_exc:
            raise BusinessError(
                "PAY_LIST_EXPORT_STORAGE_COMPENSATION_FAILED",
                "Could not compensate failed pay-list export storage write",
                status_code=500,
            ) from cleanup_exc
        raise BusinessError(
            "PAY_LIST_EXPORT_STORAGE_WRITE_FAILED",
            "Could not store pay-list export",
            status_code=500,
        ) from exc
    return managed_storage_path, stored_content


def _pay_list_filename(pay_list: PayList) -> str:
    return f"{pay_list.pay_list_no or f'PL-{pay_list.id:06d}'}-export.xlsx"


def _activity_projection(
    transaction: Session,
    case_id: str,
) -> tuple[LifecycleProjection, str]:
    get_case = getattr(transaction, "get", None)
    case = get_case(Case, case_id) if callable(get_case) else None
    if case is None:
        return (
            LifecycleProjection(
                business_stage=None,
                official_procedure_stage=None,
                legal_status=None,
                lifecycle_verification_status=None,
            ),
            "",
        )
    return _gov_payment_projection(case), case.status


def _replayed_internal_export_activity_ids(
    transaction: Session,
    *,
    artifact: PayListExportArtifact,
) -> tuple[str, ...]:
    activity_prefix = f"pay-list-internal-export:{artifact.id}:"
    activities = (
        transaction.execute(
            select(CaseActivityEvent).where(
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == "PAY_LIST_INTERNAL_EXPORTED",
                CaseActivityEvent.idempotency_key.startswith(activity_prefix),
            )
        )
        .scalars()
        .all()
    )
    evidence_rows = (
        transaction.execute(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.evidence_kind == "PAY_LIST_EXPORT_ARTIFACT",
                CaseActivityEventEvidence.object_type == "PayListExportArtifact",
                CaseActivityEventEvidence.object_id == artifact.id,
            )
        )
        .scalars()
        .all()
    )
    activity_ids = [activity.id for activity in activities]
    case_ids = [activity.case_id for activity in activities]
    evidence_activity_ids = [evidence.activity_id for evidence in evidence_rows]
    if (
        not activities
        or len(activity_ids) != len(set(activity_ids))
        or len(case_ids) != len(set(case_ids))
        or len(evidence_activity_ids) != len(set(evidence_activity_ids))
        or set(activity_ids) != set(evidence_activity_ids)
    ):
        _fail_internal_export_conflict()

    expected_payload = json.dumps(
        {
            "artifact_id": artifact.id,
            "content_sha256": artifact.content_sha256,
            "managed_storage_path": artifact.managed_storage_path,
            "pay_list_id": artifact.pay_list_id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    evidence_by_activity = {evidence.activity_id: evidence for evidence in evidence_rows}
    for activity in activities:
        evidence = evidence_by_activity[activity.id]
        if (
            activity.lane != ActivityLane.FEE.value
            or activity.activity_type != "PAY_LIST_INTERNAL_EXPORTED"
            or activity.idempotency_key != f"{activity_prefix}{activity.case_id}"
            or activity.actor_id != artifact.generated_by
            or activity.occurred_at != artifact.generated_at
            or activity.effective_at != artifact.generated_at
            or activity.source_activity_id is not None
            or activity.reviewer_id is not None
            or activity.supersedes_event_id is not None
            or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
            or activity.old_business_stage != activity.new_business_stage
            or activity.old_official_procedure_stage != activity.new_official_procedure_stage
            or activity.old_legal_status != activity.new_legal_status
            or activity.payload_json != expected_payload
            or evidence.case_id != activity.case_id
            or evidence.evidence_kind != "PAY_LIST_EXPORT_ARTIFACT"
            or evidence.object_type != "PayListExportArtifact"
            or evidence.object_id != artifact.id
            or evidence.content_hash != artifact.content_sha256
            or evidence.captured_at != artifact.generated_at
        ):
            _fail_internal_export_conflict()
    return tuple(
        activity.id for activity in sorted(activities, key=lambda item: item.case_id.encode())
    )


def _replay_internal_export(
    command: ExportInternalPayListCommand,
    transaction: Session,
    *,
    pay_list: PayList,
    artifact: PayListExportArtifact,
) -> ExportInternalPayListResult:
    if (
        artifact.pay_list_id != command.pay_list_id
        or artifact.idempotency_key != command.idempotency_key
        or artifact.kind != "INTERNAL_XLSX"
        or artifact.status != "GENERATED"
        or artifact.generated_by != command.actor_id
        or artifact.template_version is not None
        or artifact.official_acceptance_evidence_ref is not None
        or artifact.official_acceptance_evidence_hash is not None
        or artifact.official_accepted_at is not None
    ):
        _fail_internal_export_conflict()
    try:
        path = _resolve_internal_export_path(
            pay_list_id=command.pay_list_id,
            artifact_id=artifact.id,
            managed_storage_path=artifact.managed_storage_path,
            storage_dir=get_settings().storage_dir,
        )
        content = path.read_bytes()
    except (BusinessError, OSError):
        _fail_internal_export_conflict()
    if sha256(content).hexdigest() != artifact.content_sha256:
        _fail_internal_export_conflict()
    return ExportInternalPayListResult(
        artifact_id=artifact.id,
        pay_list_id=command.pay_list_id,
        filename=_pay_list_filename(pay_list),
        content_type=_PAY_LIST_EXPORT_CONTENT_TYPE,
        content=content,
        content_sha256=artifact.content_sha256,
        managed_storage_path=artifact.managed_storage_path,
        activity_ids=_replayed_internal_export_activity_ids(
            transaction,
            artifact=artifact,
        ),
        generated_at=artifact.generated_at,
        idempotency_key=artifact.idempotency_key,
        reused=True,
    )


def export_internal_pay_list(
    command: ExportInternalPayListCommand,
    transaction: Session,
) -> ExportInternalPayListResult:
    _validate_internal_export_command(command)
    artifact = transaction.execute(
        select(PayListExportArtifact).where(
            PayListExportArtifact.pay_list_id == command.pay_list_id,
            PayListExportArtifact.idempotency_key == command.idempotency_key,
        )
    ).scalar_one_or_none()
    pay_list = transaction.execute(
        select(PayList).where(PayList.id == command.pay_list_id)
    ).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)
    if artifact is not None:
        return _replay_internal_export(
            command,
            transaction,
            pay_list=pay_list,
            artifact=artifact,
        )
    client = transaction.execute(
        select(Client).where(Client.id == pay_list.client_id)
    ).scalar_one_or_none()
    payments = (
        transaction.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == command.pay_list_id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )
    case_ids = sorted({payment.case_id for payment in payments}, key=str.encode)
    if not payments or not case_ids:
        raise_business_error(
            "PAY_LIST_EXPORT_NO_CASES",
            "Pay list has no payment cases",
            status_code=409,
        )
    generated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    artifact_id = str(uuid4())
    content = build_pay_list_export_xlsx(
        pay_list=pay_list,
        client_name=client.name_cn if client is not None else None,
        payments=payments,
    )
    managed_storage_path, stored_content = _write_internal_export(
        pay_list_id=command.pay_list_id,
        artifact_id=artifact_id,
        content=content,
    )
    content_hash = sha256(stored_content).hexdigest()
    carrier = PayListExportArtifact(
        id=artifact_id,
        pay_list_id=command.pay_list_id,
        kind="INTERNAL_XLSX",
        status="GENERATED",
        content_sha256=content_hash,
        managed_storage_path=managed_storage_path,
        template_version=None,
        generated_by=command.actor_id,
        generated_at=generated_at,
        idempotency_key=command.idempotency_key,
        official_acceptance_evidence_ref=None,
        official_acceptance_evidence_hash=None,
        official_accepted_at=None,
    )
    activity_ids: list[str] = []
    try:
        transaction.add(carrier)
        transaction.flush()
        for case_id in case_ids:
            projection, legacy_status = _activity_projection(transaction, case_id)
            activity = append_case_activity(
                LifecycleEventCommand(
                    case_id=case_id,
                    event_type="PAY_LIST_INTERNAL_EXPORTED",
                    lane=ActivityLane.FEE,
                    effective_at=generated_at,
                    occurred_at=generated_at,
                    evidence_refs=(
                        EvidenceReference(
                            case_id=case_id,
                            evidence_kind="PAY_LIST_EXPORT_ARTIFACT",
                            object_type="PayListExportArtifact",
                            object_id=artifact_id,
                            content_hash=content_hash,
                            captured_at=generated_at,
                        ),
                    ),
                    actor_id=command.actor_id,
                    reviewer_id=None,
                    idempotency_key=f"pay-list-internal-export:{artifact_id}:{case_id}",
                    source_activity_id=None,
                    supersedes_event_id=None,
                    payload={
                        "artifact_id": artifact_id,
                        "pay_list_id": command.pay_list_id,
                        "content_sha256": content_hash,
                        "managed_storage_path": managed_storage_path,
                    },
                    confirmation_status=ConfirmationStatus.CONFIRMED,
                ),
                transaction,
                previous_projection=projection,
                current_projection=projection,
                legacy_case_status=legacy_status,
                conflict_codes=(),
            )
            activity_ids.append(activity.activity_id)
    except Exception as exc:
        try:
            compensate_internal_pay_list_export(managed_storage_path)
        except BusinessError as cleanup_exc:
            raise cleanup_exc from exc
        raise
    return ExportInternalPayListResult(
        artifact_id=artifact_id,
        pay_list_id=command.pay_list_id,
        filename=_pay_list_filename(pay_list),
        content_type=_PAY_LIST_EXPORT_CONTENT_TYPE,
        content=stored_content,
        content_sha256=content_hash,
        managed_storage_path=managed_storage_path,
        activity_ids=tuple(activity_ids),
        generated_at=generated_at,
        idempotency_key=command.idempotency_key,
        reused=False,
    )


def export_pay_list(
    db: Session,
    *,
    pay_list_id: int,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Generate a single Excel export for a pay list and advance DRAFT to EXPORTED."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    current_status = (pay_list.status or "").strip().upper()
    if current_status != "DRAFT":
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Pay list can only be exported from DRAFT status",
            details={"status": pay_list.status},
            status_code=409,
        )

    client = db.execute(select(Client).where(Client.id == pay_list.client_id)).scalar_one_or_none()
    payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == pay_list.id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )

    pay_list.status = "EXPORTED"
    pay_list.updated_by = actor_id
    export_bytes = build_pay_list_export_xlsx(
        pay_list=pay_list,
        client_name=client.name_cn if client is not None else None,
        payments=payments,
    )

    db.commit()
    db.refresh(pay_list)

    filename = f"{pay_list.pay_list_no or f'PL-{pay_list.id:06d}'}-export.xlsx"
    return {
        "filename": filename,
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "content": export_bytes,
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "status": pay_list.status,
            "currency": pay_list.currency,
            "planned_pay_date": pay_list.planned_pay_date,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "remark": pay_list.remark,
            "updated_by": pay_list.updated_by,
        },
    }


def mark_pay_list_paid(
    db: Session,
    *,
    pay_list_id: int,
    paid_date: date,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Record header paid date after every payment row has payment evidence."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == pay_list.id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )
    if not payments:
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Pay list requires at least one paid row before marking paid",
            details={"reason": "NO_PAYMENT_ROWS"},
            status_code=409,
        )

    unpaid_rows = [
        payment
        for payment in payments
        if ((payment.status or "").strip().upper() not in {"PAID", "RECORDED"})
        or payment.paid_date is None
    ]
    if unpaid_rows:
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "All pay-list rows must already be paid before marking header paid",
            details={"reason": "UNPAID_PAYMENT_ROWS", "unpaid_count": len(unpaid_rows)},
            status_code=409,
        )

    pay_list.status = "PAID"
    pay_list.paid_date = paid_date
    pay_list.updated_by = actor_id
    db.commit()
    db.refresh(pay_list)

    return {
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "status": pay_list.status,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "currency": pay_list.currency,
            "client_id": pay_list.client_id,
            "remark": pay_list.remark,
            "updated_by": pay_list.updated_by,
        }
    }


def list_pay_lists(
    db: Session,
    *,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PayList], int]:
    """List pay-list headers with supported Phase 3 filters and pagination."""
    filters = filters or {}

    pay_list_no = str(filters.get("pay_list_no") or "").strip()
    client_id = str(filters.get("client_id") or "").strip()
    status_values = _normalize_statuses(filters.get("status"))
    currency = str(filters.get("currency") or "").strip().upper()
    case_no = str(filters.get("case_no") or "").strip()
    app_no = str(filters.get("app_no") or "").strip()

    planned_from = _coerce_date(
        filters.get("planned_pay_date_from"),
        "planned_pay_date_from",
    )
    planned_to = _coerce_date(
        filters.get("planned_pay_date_to"),
        "planned_pay_date_to",
    )
    if planned_from and planned_to and planned_from > planned_to:
        raise_business_error(
            "PAY_LIST_DATE_RANGE_INVALID",
            "planned_pay_date_from must be <= planned_pay_date_to",
            status_code=400,
        )

    stmt = select(PayList)
    if pay_list_no:
        stmt = stmt.where(PayList.pay_list_no == pay_list_no)
    if client_id:
        stmt = stmt.where(PayList.client_id == client_id)
    if status_values:
        if len(status_values) == 1:
            stmt = stmt.where(func.upper(PayList.status) == status_values[0])
        else:
            stmt = stmt.where(func.upper(PayList.status).in_(status_values))
    if currency:
        stmt = stmt.where(func.upper(PayList.currency) == currency)
    if planned_from:
        stmt = stmt.where(PayList.planned_pay_date >= planned_from)
    if planned_to:
        stmt = stmt.where(PayList.planned_pay_date <= planned_to)
    list_type = _normalize_optional_text(filters.get("list_type"))
    if list_type:
        stmt = stmt.where(func.upper(PayList.list_type) == list_type.upper())
    flow_dir = _normalize_optional_text(filters.get("flow_dir"))
    if flow_dir:
        stmt = stmt.where(func.upper(PayList.flow_dir) == flow_dir.upper())
    fee_code = _normalize_optional_text(filters.get("fee_code"))
    voucher_no = _normalize_optional_text(filters.get("voucher_no"))
    invoice_no = _normalize_optional_text(filters.get("invoice_no"))
    if fee_code or voucher_no or invoice_no:
        gov_stmt = select(GovPayment.id).where(GovPayment.pay_list_id == PayList.id)
        if fee_code:
            gov_stmt = gov_stmt.where(GovPayment.fee_code == fee_code)
        if voucher_no:
            gov_stmt = gov_stmt.where(GovPayment.voucher_no == voucher_no)
        if invoice_no:
            gov_stmt = gov_stmt.where(GovPayment.invoice_no == invoice_no)
        stmt = stmt.where(gov_stmt.exists())
    if case_no or app_no:
        case_stmt = (
            select(GovPayment.id)
            .join(Case, Case.id == GovPayment.case_id)
            .where(GovPayment.pay_list_id == PayList.id)
        )
        if case_no:
            case_stmt = case_stmt.where(Case.case_no == case_no)
        if app_no:
            case_stmt = case_stmt.where(Case.app_no == app_no)
        stmt = stmt.where(case_stmt.exists())

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    offset = (page - 1) * page_size
    items = (
        db.execute(
            stmt.order_by(PayList.created_at.desc(), PayList.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return items, total


def get_pay_list_detail(db: Session, *, pay_list_id: int) -> dict[str, Any]:
    """Return one pay-list header with its associated gov payment rows."""
    with db.no_autoflush:
        pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
        if pay_list is None:
            raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

        export_artifacts = (
            db.execute(
                select(PayListExportArtifact)
                .where(PayListExportArtifact.pay_list_id == pay_list.id)
                .order_by(
                    PayListExportArtifact.generated_at.asc(),
                    PayListExportArtifact.id.asc(),
                )
            )
            .scalars()
            .all()
        )
        gov_payments = (
            db.execute(
                select(GovPayment)
                .where(GovPayment.pay_list_id == pay_list.id)
                .order_by(GovPayment.id.asc())
            )
            .scalars()
            .all()
        )

        case_ids = {gov_payment.case_id for gov_payment in gov_payments if gov_payment.case_id}
        case_no_by_id: dict[str, str | None] = {}
        if case_ids:
            case_no_by_id = {
                row[0]: row[1]
                for row in db.execute(
                    select(Case.id, Case.case_no).where(Case.id.in_(case_ids))
                ).all()
            }

    result = {
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "client_id": pay_list.client_id,
            "status": pay_list.status,
            "currency": pay_list.currency,
            "planned_pay_date": pay_list.planned_pay_date,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "remark": pay_list.remark,
            "list_type": pay_list.list_type,
            "flow_dir": pay_list.flow_dir,
            "invoice_no_from": pay_list.invoice_no_from,
            "invoice_no_to": pay_list.invoice_no_to,
            "created_at": pay_list.created_at,
            "updated_at": pay_list.updated_at,
            "created_by": pay_list.created_by,
            "updated_by": pay_list.updated_by,
        },
        "gov_payments": [
            {
                "id": gov_payment.id,
                "pay_list_id": gov_payment.pay_list_id,
                "case_id": gov_payment.case_id,
                "case_no": case_no_by_id.get(gov_payment.case_id),
                "fee_item_id": gov_payment.fee_item_id,
                "status": gov_payment.status,
                "currency": gov_payment.currency,
                "paid_date": gov_payment.paid_date,
                "paid_amount": str(gov_payment.paid_amount),
                "official_receipt_no": gov_payment.official_receipt_no,
                "remark": gov_payment.remark,
                "fee_code": gov_payment.fee_code,
                "year_no": gov_payment.year_no,
                "planned_amt": (
                    str(gov_payment.planned_amt) if gov_payment.planned_amt is not None else None
                ),
                "planned_currency": gov_payment.planned_currency,
                "paid_currency": gov_payment.paid_currency,
                "voucher_no": gov_payment.voucher_no,
                "invoice_no": gov_payment.invoice_no,
                "created_at": gov_payment.created_at,
                "updated_at": gov_payment.updated_at,
                "created_by": gov_payment.created_by,
                "updated_by": gov_payment.updated_by,
            }
            for gov_payment in gov_payments
        ],
    }

    if export_artifacts:
        result["export_artifacts"] = [
            {
                "id": artifact.id,
                "pay_list_id": artifact.pay_list_id,
                "kind": artifact.kind,
                "status": artifact.status,
                "content_sha256": artifact.content_sha256,
                "managed_storage_path": artifact.managed_storage_path,
                "template_version": artifact.template_version,
                "generated_by": artifact.generated_by,
                "generated_at": artifact.generated_at,
                "idempotency_key": artifact.idempotency_key,
                "official_acceptance_evidence_ref": artifact.official_acceptance_evidence_ref,
                "official_acceptance_evidence_hash": artifact.official_acceptance_evidence_hash,
                "official_accepted_at": artifact.official_accepted_at,
                "updated_at": artifact.updated_at,
            }
            for artifact in export_artifacts
        ]

    official_workbook = {
        "official_upload_template_status": pay_list.official_upload_template_status,
        "official_upload_template_name": pay_list.official_upload_template_name,
        "official_upload_batch_limit": pay_list.official_upload_batch_limit,
        "official_pay_list_boundary_note": pay_list.official_pay_list_boundary_note,
    }
    if any(value is not None for value in official_workbook.values()):
        result["official_workbook"] = official_workbook

    return result


def _recompute_pay_list_status(pay_list: PayList, payments: list[GovPayment]) -> None:
    current_status = (pay_list.status or "").strip().upper()

    if current_status == "EXPORTED":
        pay_list.total_amount = sum((Decimal(p.paid_amount or 0) for p in payments), Decimal("0"))
        return

    if not payments:
        pay_list.status = "DRAFT"
        pay_list.paid_date = None
        pay_list.total_amount = Decimal("0")
        return

    pay_list.total_amount = sum((Decimal(p.paid_amount or 0) for p in payments), Decimal("0"))
    paid_rows = [
        p
        for p in payments
        if ((p.status or "").strip().upper() in {"PAID", "RECORDED"}) and p.paid_date is not None
    ]

    if not paid_rows:
        pay_list.status = "DRAFT"
        pay_list.paid_date = None
        return

    if len(paid_rows) < len(payments):
        pay_list.status = "PARTIAL"
        pay_list.paid_date = None
        return

    pay_list.status = "PAID"
    pay_list.paid_date = max(
        (p.paid_date for p in paid_rows if p.paid_date is not None), default=None
    )


def _gov_payment_obligation_context(
    db: Session,
    *,
    fee_item_id: str,
) -> tuple[FeeObligation, tuple[str, ...]] | None:
    rows = db.execute(
        select(FeeObligation, FeeObligationLine.id)
        .join(FeeObligationLine, FeeObligationLine.obligation_id == FeeObligation.id)
        .join(
            FeeObligationDraftItemLink,
            FeeObligationDraftItemLink.obligation_line_id == FeeObligationLine.id,
        )
        .where(FeeObligationDraftItemLink.fee_item_id == fee_item_id)
        .order_by(FeeObligationLine.id)
    ).all()
    if not rows:
        return None

    obligations = {row[0].id: row[0] for row in rows}
    if len(obligations) != 1:
        raise_business_error(
            "GOV_PAYMENT_OBLIGATION_LINK_CONFLICT",
            "Fee item is linked to multiple fee obligations",
            status_code=409,
        )
    obligation = next(iter(obligations.values()))
    return obligation, tuple(row[1] for row in rows)


def _gov_payment_projection(case: Case) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                BusinessStage(case.business_stage) if case.business_stage is not None else None
            ),
            official_procedure_stage=(
                OfficialProcedureStage(case.official_procedure_stage)
                if case.official_procedure_stage is not None
                else None
            ),
            legal_status=LegalStatus(case.legal_status) if case.legal_status is not None else None,
            lifecycle_verification_status=(
                ConfirmationStatus(case.lifecycle_verification_status)
                if case.lifecycle_verification_status is not None
                else None
            ),
        )
    except ValueError:
        raise_business_error(
            "GOV_PAYMENT_CASE_PROJECTION_INVALID",
            "Case lifecycle projection is invalid",
            status_code=409,
        )


def _record_gov_payment_activity(
    db: Session,
    *,
    payment: GovPayment,
    obligation: FeeObligation,
    obligation_line_ids: tuple[str, ...],
    actor_id: str,
) -> None:
    record_payment_evidence(
        RecordFeePaymentEvidenceCommand(
            obligation_id=obligation.id,
            obligation_line_ids=obligation_line_ids,
            gov_payment_id=payment.id,
            actor_id=actor_id,
        ),
        db,
    )
    case = db.get(Case, payment.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    projection = _gov_payment_projection(case)
    payment_at = datetime.combine(payment.paid_date or date.today(), time.min)
    append_case_activity(
        LifecycleEventCommand(
            case_id=payment.case_id,
            event_type="PAYMENT_RECORDED",
            lane=ActivityLane.FEE,
            effective_at=payment_at,
            occurred_at=payment_at,
            evidence_refs=(),
            actor_id=actor_id,
            reviewer_id=None,
            idempotency_key=f"gov-payment:{payment.id}:recorded",
            source_activity_id=obligation.source_activity_id,
            supersedes_event_id=None,
            payload={
                "gov_payment_id": payment.id,
                "obligation_id": obligation.id,
                "obligation_line_ids": list(obligation_line_ids),
                "schema": "FPMS_GOV_PAYMENT_RECORDED_V1",
            },
            confirmation_status=ConfirmationStatus.CONFIRMED,
        ),
        db,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=case.status,
        conflict_codes=(),
    )


def _record_gov_payment_official_evidence_activity(
    db: Session,
    *,
    payment: GovPayment,
    obligation: FeeObligation,
    obligation_line_ids: tuple[str, ...],
    actor_id: str,
) -> None:
    obligation.official_evidence_status = FeeOfficialEvidenceStatus.VERIFIED.value
    obligation.updated_by = actor_id
    case = db.get(Case, payment.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    projection = _gov_payment_projection(case)
    verified_at = datetime.combine(payment.paid_date or date.today(), time.min)
    append_case_activity(
        LifecycleEventCommand(
            case_id=payment.case_id,
            event_type="OFFICIAL_PAYMENT_EVIDENCE_VERIFIED",
            lane=ActivityLane.FEE,
            effective_at=verified_at,
            occurred_at=verified_at,
            evidence_refs=(),
            actor_id=actor_id,
            reviewer_id=None,
            idempotency_key=f"gov-payment:{payment.id}:official-evidence-verified",
            source_activity_id=obligation.source_activity_id,
            supersedes_event_id=None,
            payload={
                "gov_payment_id": payment.id,
                "invoice_no": payment.invoice_no,
                "obligation_id": obligation.id,
                "obligation_line_ids": list(obligation_line_ids),
                "official_receipt_no": payment.official_receipt_no,
                "schema": "FPMS_GOV_PAYMENT_OFFICIAL_EVIDENCE_VERIFIED_V1",
                "voucher_no": payment.voucher_no,
            },
            confirmation_status=ConfirmationStatus.CONFIRMED,
        ),
        db,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=case.status,
        conflict_codes=(),
    )


def register_gov_payment(
    db: Session,
    *,
    pay_list_id: int,
    fee_item_id: str,
    paid_date: date | None = None,
    paid_amount: Decimal | None = None,
    official_receipt_no: str | None = None,
    remark: str | None = None,
    paid_currency: str | None = None,
    voucher_no: str | None = None,
    invoice_no: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Register official payment with duplicate protection and pay-list status recompute."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if not pay_list:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    normalized_fee_item_id = (fee_item_id or "").strip()
    if not normalized_fee_item_id:
        raise_business_error("FEE_ITEM_REQUIRED", "fee_item_id is required", status_code=400)

    obligation_context = _gov_payment_obligation_context(
        db,
        fee_item_id=normalized_fee_item_id,
    )

    target = (
        db.execute(
            select(GovPayment)
            .where(
                GovPayment.pay_list_id == pay_list_id,
                GovPayment.fee_item_id == normalized_fee_item_id,
            )
            .order_by(GovPayment.id.desc())
        )
        .scalars()
        .first()
    )

    paid_conflict = (
        db.execute(
            select(GovPayment)
            .where(
                GovPayment.fee_item_id == normalized_fee_item_id,
                GovPayment.id != (target.id if target is not None else -1),
                (GovPayment.status.in_(["PAID", "RECORDED"]) | GovPayment.paid_date.is_not(None)),
            )
            .order_by(GovPayment.id.desc())
        )
        .scalars()
        .first()
    )
    if paid_conflict is not None:
        raise_business_error(
            "GOV_PAYMENT_DUPLICATE",
            "Official payment already registered for this fee item",
            status_code=409,
        )

    if paid_amount is not None and Decimal(paid_amount) <= Decimal("0"):
        raise_business_error(
            "GOV_PAYMENT_INVALID",
            "paid_amount must be greater than 0",
            status_code=400,
        )

    if target is None:
        fee_item_row = db.execute(
            select(FeeItem, FeeDraft)
            .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
            .where(FeeItem.id == normalized_fee_item_id)
        ).first()
        if fee_item_row is None:
            raise_business_error("FEE_ITEM_NOT_FOUND", "Fee item not found", status_code=404)

        fee_item, draft = fee_item_row
        if (fee_item.fee_type or "").strip().upper() != "GOV":
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Only GOV fee items can be registered as official payments",
                status_code=400,
            )
        if not fee_item.case_id:
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Fee item is missing case_id",
                status_code=400,
            )
        if draft.currency != pay_list.currency:
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Fee item currency does not match pay list currency",
                status_code=400,
            )
        if draft.client_id != pay_list.client_id:
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Fee item client does not match pay list client",
                status_code=400,
            )

        resolved_paid_amount = (
            Decimal(paid_amount) if paid_amount is not None else Decimal(fee_item.amount or 0)
        )
        if resolved_paid_amount <= Decimal("0"):
            raise_business_error(
                "GOV_PAYMENT_INVALID",
                "paid_amount must be greater than 0",
                status_code=400,
            )

        target = GovPayment(
            pay_list_id=pay_list.id,
            case_id=fee_item.case_id,
            fee_item_id=fee_item.id,
            status="PAID",
            currency=pay_list.currency,
            paid_date=paid_date or date.today(),
            paid_amount=resolved_paid_amount,
            official_receipt_no=official_receipt_no,
            remark=remark,
            fee_code=fee_item.fee_code,
            year_no=fee_item.year_no,
            planned_amt=Decimal(fee_item.amount or 0),
            planned_currency=pay_list.currency,
            paid_currency=_normalize_optional_text(paid_currency) or pay_list.currency,
            voucher_no=_normalize_optional_text(voucher_no),
            invoice_no=_normalize_optional_text(invoice_no),
            created_by=actor_id,
            updated_by=actor_id,
        )
        db.add(target)
    else:
        if (
            (target.status or "").strip().upper() in {"PAID", "RECORDED"}
        ) or target.paid_date is not None:
            raise_business_error(
                "GOV_PAYMENT_DUPLICATE",
                "Official payment already registered",
                status_code=409,
            )

        if paid_amount is None:
            if Decimal(target.paid_amount or 0) <= Decimal("0"):
                raise_business_error(
                    "GOV_PAYMENT_INVALID",
                    "paid_amount must be greater than 0",
                    status_code=400,
                )
        else:
            resolved_paid_amount = Decimal(paid_amount)
            if resolved_paid_amount <= Decimal("0"):
                raise_business_error(
                    "GOV_PAYMENT_INVALID",
                    "paid_amount must be greater than 0",
                    status_code=400,
                )
            target.paid_amount = resolved_paid_amount

        target.status = "PAID"
        target.paid_date = paid_date or date.today()
        if official_receipt_no is not None:
            target.official_receipt_no = official_receipt_no
        if remark is not None:
            target.remark = remark
        if paid_currency is not None:
            target.paid_currency = _normalize_optional_text(paid_currency)
        elif not target.paid_currency:
            target.paid_currency = pay_list.currency
        if voucher_no is not None:
            target.voucher_no = _normalize_optional_text(voucher_no)
        if invoice_no is not None:
            target.invoice_no = _normalize_optional_text(invoice_no)
        target.updated_by = actor_id

    db.flush()
    if obligation_context is not None:
        obligation, obligation_line_ids = obligation_context
        resolved_actor_id = (
            actor_id
            or target.updated_by
            or target.created_by
            or pay_list.updated_by
            or pay_list.created_by
        )
        if not resolved_actor_id:
            raise_business_error(
                "GOV_PAYMENT_ACTOR_REQUIRED",
                "actor_id is required for obligation-linked payment registration",
                status_code=409,
            )
        _record_gov_payment_activity(
            db,
            payment=target,
            obligation=obligation,
            obligation_line_ids=obligation_line_ids,
            actor_id=resolved_actor_id,
        )
        if any(
            (
                _normalize_optional_text(target.official_receipt_no),
                _normalize_optional_text(target.voucher_no),
                _normalize_optional_text(target.invoice_no),
            )
        ):
            _record_gov_payment_official_evidence_activity(
                db,
                payment=target,
                obligation=obligation,
                obligation_line_ids=obligation_line_ids,
                actor_id=resolved_actor_id,
            )
    payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == pay_list.id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )
    _recompute_pay_list_status(pay_list, payments)
    pay_list.updated_by = actor_id

    db.commit()
    db.refresh(target)
    db.refresh(pay_list)

    return {
        "gov_payment": {
            "id": target.id,
            "pay_list_id": target.pay_list_id,
            "case_id": target.case_id,
            "fee_item_id": target.fee_item_id,
            "status": target.status,
            "currency": target.currency,
            "paid_date": target.paid_date,
            "paid_amount": str(target.paid_amount),
            "official_receipt_no": target.official_receipt_no,
            "remark": target.remark,
            "fee_code": target.fee_code,
            "year_no": target.year_no,
            "planned_amt": str(target.planned_amt) if target.planned_amt is not None else None,
            "planned_currency": target.planned_currency,
            "paid_currency": target.paid_currency,
            "voucher_no": target.voucher_no,
            "invoice_no": target.invoice_no,
        },
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "status": pay_list.status,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "currency": pay_list.currency,
            "client_id": pay_list.client_id,
        },
    }


def add_manual_gov_payment(
    db: Session,
    *,
    pay_list_id: int,
    case_id: str,
    fee_item_id: str | None = None,
    paid_date: date,
    paid_amount: Decimal,
    official_receipt_no: str | None = None,
    remark: str | None = None,
    fee_code: str | None = None,
    year_no: int | None = None,
    paid_currency: str | None = None,
    voucher_no: str | None = None,
    invoice_no: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Add a manual/historical gov-payment row under an existing pay list."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    if (pay_list.status or "").strip().upper() != "DRAFT":
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Manual items can only be added to a DRAFT pay list",
            details={"status": pay_list.status},
            status_code=409,
        )

    existing_rows = (
        db.execute(select(GovPayment.id).where(GovPayment.pay_list_id == pay_list.id).limit(1))
        .scalars()
        .first()
    )
    if existing_rows is not None:
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Manual items can only be added to an empty historical pay list",
            details={"reason": "PAY_LIST_ALREADY_HAS_ROWS"},
            status_code=409,
        )

    normalized_case_id = (case_id or "").strip()
    if not normalized_case_id:
        raise_business_error("CASE_REQUIRED", "case_id is required", status_code=400)

    resolved_paid_amount = Decimal(paid_amount)
    if resolved_paid_amount <= Decimal("0"):
        raise_business_error(
            "GOV_PAYMENT_INVALID",
            "paid_amount must be greater than 0",
            status_code=400,
        )

    case = db.execute(select(Case).where(Case.id == normalized_case_id)).scalar_one_or_none()
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    if case.client_id != pay_list.client_id:
        raise_business_error(
            "PAY_LIST_SCOPE_INVALID",
            "Case client does not match pay list client",
            status_code=400,
        )

    normalized_fee_item_id = (fee_item_id or "").strip() or None
    if normalized_fee_item_id is not None:
        fee_item_row = db.execute(
            select(FeeItem, FeeDraft)
            .join(FeeDraft, FeeDraft.id == FeeItem.draft_id)
            .where(FeeItem.id == normalized_fee_item_id)
        ).first()
        if fee_item_row is None:
            raise_business_error("FEE_ITEM_NOT_FOUND", "Fee item not found", status_code=404)
        fee_item, draft = fee_item_row
        if draft.client_id != pay_list.client_id or draft.currency != pay_list.currency:
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Fee item does not match pay list scope",
                status_code=400,
            )
        if fee_item.case_id != normalized_case_id:
            raise_business_error(
                "PAY_LIST_SCOPE_INVALID",
                "Fee item case does not match pay list case",
                status_code=400,
            )

    target = GovPayment(
        pay_list_id=pay_list.id,
        case_id=normalized_case_id,
        fee_item_id=normalized_fee_item_id,
        status="PAID",
        currency=pay_list.currency,
        paid_date=paid_date,
        paid_amount=resolved_paid_amount,
        official_receipt_no=official_receipt_no,
        remark=remark,
        fee_code=_normalize_optional_text(fee_code),
        year_no=year_no,
        planned_amt=resolved_paid_amount,
        planned_currency=pay_list.currency,
        paid_currency=_normalize_optional_text(paid_currency) or pay_list.currency,
        voucher_no=_normalize_optional_text(voucher_no),
        invoice_no=_normalize_optional_text(invoice_no),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(target)
    db.flush()

    payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == pay_list.id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )
    _recompute_pay_list_status(pay_list, payments)
    pay_list.updated_by = actor_id

    db.commit()
    db.refresh(target)
    db.refresh(pay_list)

    return {
        "gov_payment": {
            "id": target.id,
            "pay_list_id": target.pay_list_id,
            "case_id": target.case_id,
            "fee_item_id": target.fee_item_id,
            "status": target.status,
            "currency": target.currency,
            "paid_date": target.paid_date,
            "paid_amount": str(target.paid_amount),
            "official_receipt_no": target.official_receipt_no,
            "remark": target.remark,
            "fee_code": target.fee_code,
            "year_no": target.year_no,
            "planned_amt": str(target.planned_amt) if target.planned_amt is not None else None,
            "planned_currency": target.planned_currency,
            "paid_currency": target.paid_currency,
            "voucher_no": target.voucher_no,
            "invoice_no": target.invoice_no,
        },
        "pay_list": {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "status": pay_list.status,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "currency": pay_list.currency,
            "client_id": pay_list.client_id,
        },
    }


@dataclass(frozen=True, slots=True)
class RecordAnnuityTaskInstructionCommand:
    annuity_task_id: int
    instruction: str
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecordAnnuityTaskInstructionResult:
    annuity_task_id: int
    fee_obligation_id: str
    instruction: FeeClientInstruction
    activity_id: str
    idempotency_key: str
    reused: bool


def _annuity_instruction_fail(
    code: str,
    message: str,
    *,
    status_code: int,
    details: dict[str, str] | None = None,
) -> None:
    raise_business_error(code, message, details=details, status_code=status_code)


def _annuity_instruction_command_invalid(field: str) -> None:
    _annuity_instruction_fail(
        "ANNUITY_INSTRUCTION_COMMAND_INVALID",
        "年费任务客户指示命令无效",
        status_code=400,
        details={"field": field},
    )


def _annuity_instruction_required_string(value: object, limit: int, field: str) -> None:
    if type(value) is not str or not value or value != value.strip() or len(value) > limit:
        _annuity_instruction_command_invalid(field)


def _validate_annuity_instruction_command(command: RecordAnnuityTaskInstructionCommand) -> None:
    if type(command) is not RecordAnnuityTaskInstructionCommand:
        _annuity_instruction_command_invalid("command")
    if (
        type(command.annuity_task_id) is not int
        or type(command.annuity_task_id) is bool
        or command.annuity_task_id <= 0
    ):
        _annuity_instruction_command_invalid("annuity_task_id")
    if type(command.instruction) is not str or command.instruction not in {
        "PAY",
        "HOLD",
        "ABANDON",
    }:
        _annuity_instruction_command_invalid("instruction")
    _annuity_instruction_required_string(command.actor_id, 36, "actor_id")
    _annuity_instruction_required_string(command.idempotency_key, 128, "idempotency_key")


def _annuity_instruction_not_found(message: str) -> None:
    _annuity_instruction_fail(
        "ANNUITY_INSTRUCTION_LINK_NOT_FOUND",
        message,
        status_code=404,
    )


def _annuity_instruction_conflict(message: str) -> None:
    _annuity_instruction_fail(
        "ANNUITY_INSTRUCTION_LINEAGE_CONFLICT",
        message,
        status_code=409,
    )


def _annuity_instruction_exact_string(value: object, limit: int = 36) -> bool:
    return type(value) is str and bool(value) and value == value.strip() and len(value) <= limit


def _has_future_annuity_exception_draft(
    transaction: Session,
    *,
    case_id: str,
    obligation_id: str,
) -> bool:
    matches: list[dict[str, object]] = []
    for activity in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.lane == ActivityLane.FEE.value,
            CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED",
        )
    ):
        try:
            payload = json.loads(activity.payload_json)
        except (TypeError, ValueError):
            continue
        if type(payload) is dict and payload.get("obligation_id") == obligation_id:
            matches.append(payload)
    if not matches:
        return False
    if len(matches) != 1:
        _annuity_instruction_conflict("年费任务费用义务草单活动不存在或不唯一")
    return (
        matches[0].get("schema")
        == "FPMS_FEE_DRAFT_CREATED_FROM_FUTURE_ANNUITY_EXCEPTION_V1"
    )


def _validate_annuity_instruction_lineage(
    transaction: Session,
    *,
    task: AnnuityTask,
    obligation: FeeObligation,
    case: Case,
    canonical_recognition: bool = False,
) -> None:
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine).where(FeeObligationLine.obligation_id == obligation.id)
        )
    )
    if len(lines) != 1:
        _annuity_instruction_not_found("年费任务费用义务分项不存在或不唯一")
    line = lines[0]
    expected_fee_code = _FUTURE_ANNUITY_FEE_CODE.get(case.patent_category)
    if (
        task.case_id != case.id
        or task.client_id != case.client_id
        or obligation.case_id != case.id
        or obligation.obligation_type != "FUTURE_ANNUITY"
        or obligation.source_activity_id != task.source_activity_id
        or obligation.source_document_id != task.source_document_id
        or obligation.due_date != task.due_date
        or obligation.currency != "CNY"
        or line.obligation_id != obligation.id
        or line.case_id != case.id
        or line.source_activity_id != task.source_activity_id
        or line.fee_code != expected_fee_code
        or line.fee_year_key != task.year_no
        or line.fee_year_key != task.grant_fee_year_key
        or line.source_date != task.due_date
    ):
        _annuity_instruction_conflict("年费任务费用义务谱系不一致")
    source_activity = transaction.get(CaseActivityEvent, task.source_activity_id)
    document = transaction.get(Document, task.source_document_id)
    evidence = transaction.get(DocumentEvidenceVersion, task.source_evidence_version_id)
    if source_activity is None:
        _annuity_instruction_not_found("年费任务来源活动不存在")
    if document is None:
        _annuity_instruction_not_found("年费任务来源文档不存在")
    if evidence is None:
        _annuity_instruction_not_found("年费任务来源证据不存在")
    evidence_links = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == task.source_activity_id
            )
        )
    )
    if len(evidence_links) != 1:
        _annuity_instruction_not_found("年费任务来源证据关联不存在或不唯一")
    evidence_link = evidence_links[0]
    detail = None
    if canonical_recognition:
        try:
            detail = get_fee_obligation(obligation.id, transaction)
        except BusinessError:
            _annuity_instruction_conflict("年费任务费用义务识别活动无效")
        recognitions: list[CaseActivityEvent] = []
        for candidate in transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == task.case_id,
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED",
            )
        ):
            try:
                payload = json.loads(candidate.payload_json)
            except (TypeError, ValueError):
                _annuity_instruction_conflict("年费任务费用义务识别活动无效")
            if (
                type(payload) is not dict
                or payload.get("schema") != "FPMS_FEE_OBLIGATION_RECOGNIZED_V1"
            ):
                _annuity_instruction_conflict("年费任务费用义务识别活动无效")
            if payload.get("obligation_id") == obligation.id:
                recognitions.append(candidate)
    else:
        expected_recognition_payload = json.dumps(
            {
                "obligation_id": obligation.id,
                "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        recognitions = list(
            transaction.scalars(
                select(CaseActivityEvent).where(
                    CaseActivityEvent.case_id == task.case_id,
                    CaseActivityEvent.lane == ActivityLane.FEE.value,
                    CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED",
                    CaseActivityEvent.payload_json == expected_recognition_payload,
                )
            )
        )
    if len(recognitions) != 1:
        _annuity_instruction_not_found("年费任务费用义务识别活动不存在或不唯一")
    recognition = recognitions[0]
    if (
        (
            canonical_recognition
            and (
                detail is None
                or detail.id != obligation.id
                or detail.case_id != case.id
                or detail.source.source_activity_id != task.source_activity_id
                or detail.source.source_document_id != task.source_document_id
            )
        )
        or source_activity.case_id != case.id
        or source_activity.lane != ActivityLane.LIFECYCLE.value
        or source_activity.activity_type != "GRANT_ANNOUNCEMENT_CONFIRMED"
        or source_activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or document.case_id != case.id
        or evidence.case_id != case.id
        or evidence.document_id != document.id
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or evidence.content_hash != task.source_evidence_content_hash
        or evidence.current_identity_key != f"{case.id}|{evidence.lineage_key}"
        or evidence_link.case_id != case.id
        or evidence_link.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or evidence_link.object_type != "DocumentEvidenceVersion"
        or evidence_link.object_id != evidence.id
        or evidence_link.content_hash != task.source_evidence_content_hash
        or recognition.source_activity_id != task.source_activity_id
    ):
        _annuity_instruction_conflict("年费任务费用义务谱系不一致")


def record_annuity_task_instruction(
    command: RecordAnnuityTaskInstructionCommand,
    transaction: Session,
) -> RecordAnnuityTaskInstructionResult:
    _validate_annuity_instruction_command(command)
    if transaction.new or transaction.dirty or transaction.deleted:
        _annuity_instruction_conflict("调用方事务包含未刷新的变更")
    with transaction.no_autoflush:
        task = transaction.get(AnnuityTask, command.annuity_task_id)
        if task is None:
            _annuity_instruction_fail(
                "ANNUITY_INSTRUCTION_TASK_NOT_FOUND",
                "年费任务不存在",
                status_code=404,
            )
        carrier = (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        )
        if all(value is None for value in carrier):
            _annuity_instruction_not_found("年费任务尚未关联费用义务")
        if any(value is None for value in carrier):
            _annuity_instruction_conflict("年费任务费用义务谱系不完整")
        if (
            not all(_annuity_instruction_exact_string(value) for value in carrier[:3])
            or not _annuity_instruction_exact_string(carrier[3], 71)
            or fullmatch(r"sha256:[0-9a-f]{64}", carrier[3]) is None
            or not _annuity_instruction_exact_string(carrier[4])
            or type(carrier[5]) is not int
            or type(carrier[5]) is bool
            or carrier[5] <= 0
        ):
            _annuity_instruction_conflict("年费任务费用义务谱系格式无效")
        obligation = transaction.get(FeeObligation, task.fee_obligation_id)
        case = transaction.get(Case, task.case_id)
        if obligation is None:
            _annuity_instruction_not_found("年费任务费用义务不存在")
        if case is None:
            _annuity_instruction_not_found("年费任务案件不存在")
        _validate_annuity_instruction_lineage(
            transaction,
            task=task,
            obligation=obligation,
            case=case,
            canonical_recognition=_has_future_annuity_exception_draft(
                transaction,
                case_id=case.id,
                obligation_id=obligation.id,
            ),
        )
    instruction = FeeClientInstruction(command.instruction)
    delegated = record_client_instruction(
        RecordFeeObligationInstructionCommand(
            obligation_id=obligation.id,
            instruction=instruction,
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
        ),
        transaction,
    )
    return RecordAnnuityTaskInstructionResult(
        annuity_task_id=task.id,
        fee_obligation_id=obligation.id,
        instruction=instruction,
        activity_id=delegated.activity_id,
        idempotency_key=delegated.idempotency_key,
        reused=delegated.reused,
    )


@dataclass(frozen=True, slots=True)
class FutureAnnuityAutoDraftPolicyResult:
    annuity_task_id: int
    fee_obligation_id: str
    exception_attestation: FutureAnnuityExceptionUseAttestation
    draft: PrepareFeeObligationDraftResult


def apply_future_annuity_auto_draft_policy(
    *,
    transaction: Session,
    annuity_task_id: int,
    actor_id: str,
    as_of: datetime,
) -> FutureAnnuityAutoDraftPolicyResult:
    if type(annuity_task_id) is not int or annuity_task_id <= 0:
        _future_annuity_invalid("annuity_task_id")
    if not isinstance(transaction, Session):
        _future_annuity_invalid("transaction")
    if (
        type(actor_id) is not str
        or not actor_id
        or actor_id != actor_id.strip()
        or "\x00" in actor_id
        or len(actor_id) > 36
    ):
        _future_annuity_invalid("actor_id")
    if type(as_of) is not datetime or as_of.utcoffset() is not None:
        _future_annuity_invalid("as_of")
    if transaction.new or transaction.dirty or transaction.deleted:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.TRANSACTION_DIRTY, 409)

    with transaction.no_autoflush:
        task = transaction.get(AnnuityTask, annuity_task_id)
        if task is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.TASK_NOT_FOUND, 404)
        case = transaction.get(Case, task.case_id)
        if case is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.CASE_NOT_FOUND, 404)
        carrier = (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        )
        if (
            any(value is None for value in carrier)
            or not all(_annuity_instruction_exact_string(value) for value in carrier[:3])
            or not _annuity_instruction_exact_string(carrier[3], 71)
            or fullmatch(r"sha256:[0-9a-f]{64}", carrier[3]) is None
            or not _annuity_instruction_exact_string(carrier[4])
            or type(carrier[5]) is not int
            or type(carrier[5]) is bool
            or carrier[5] <= 0
        ):
            _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
        obligation = transaction.get(FeeObligation, task.fee_obligation_id)
        if obligation is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
        try:
            _validate_annuity_instruction_lineage(
                transaction,
                task=task,
                obligation=obligation,
                case=case,
                canonical_recognition=True,
            )
        except BusinessError as exc:
            status_code = 404 if exc.status_code == 404 else 409
            _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, status_code)
        if (
            obligation.fee_domain != FeeDomain.GOV.value
            or obligation.obligation_type != "FUTURE_ANNUITY"
            or obligation.source_status != FeeSourceStatus.VERIFIED.value
            or obligation.obligation_status != "RECOGNIZED"
            or obligation.payment_status != "UNPAID"
            or obligation.official_evidence_status != FeeOfficialEvidenceStatus.PENDING.value
            or obligation.currency != "CNY"
        ):
            _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)

        existing: list[tuple[CaseActivityEvent, dict[str, object]]] = []
        for activity in transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case.id,
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED",
            )
        ):
            try:
                payload = json.loads(activity.payload_json)
            except (TypeError, ValueError):
                _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
            if type(payload) is dict and payload.get("obligation_id") == obligation.id:
                existing.append((activity, payload))

        if existing:
            if len(existing) != 1:
                _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
            activity, payload = existing[0]
            if (
                payload.get("schema")
                != "FPMS_FEE_DRAFT_CREATED_FROM_FUTURE_ANNUITY_EXCEPTION_V1"
                or payload.get("actor_id") != actor_id
                or type(payload.get("exception_publication_id")) is not str
                or activity.idempotency_key
                != (
                    f"future-annuity-exception-auto-draft:{annuity_task_id}:"
                    f"{payload['exception_publication_id']}"
                )
            ):
                _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
            try:
                attested_at = datetime.fromisoformat(
                    str(payload.get("exception_attested_at"))
                )
            except ValueError:
                _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
            if attested_at != as_of:
                _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
            command = PrepareFeeObligationDraftCommand(
                obligation_id=obligation.id,
                actor_id=actor_id,
                idempotency_key=activity.idempotency_key,
                authority=FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
                exception_gate_id=payload.get("exception_gate_id"),
                exception_gate_source_reference=payload.get("exception_gate_source_reference"),
                exception_gate_source_version=payload.get("exception_gate_source_version"),
                exception_publication_id=payload.get("exception_publication_id"),
                exception_publication_snapshot_hash=payload.get(
                    "exception_publication_snapshot_hash"
                ),
                exception_attested_at=attested_at,
            )
            draft = prepare_draft(command, transaction)
            attestation = _future_annuity_exception_attestation_or_fail(
                transaction,
                obligation,
                command,
                require_current=False,
            )
            return FutureAnnuityAutoDraftPolicyResult(
                annuity_task_id=task.id,
                fee_obligation_id=obligation.id,
                exception_attestation=attestation,
                draft=draft,
            )

        if (
            obligation.client_instruction_status != FeeClientInstructionStatus.PENDING.value
            or obligation.draft_status != "NOT_CREATED"
        ):
            _future_annuity_fail(FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT, 409)
        attestation = resolve_future_annuity_exception(
            ResolveFutureAnnuityExceptionCommand(
                client_id=case.client_id,
                case_id=case.id,
                as_of=as_of,
            ),
            transaction,
        )
        command = PrepareFeeObligationDraftCommand(
            obligation_id=obligation.id,
            actor_id=actor_id,
            idempotency_key=(
                f"future-annuity-exception-auto-draft:{annuity_task_id}:"
                f"{attestation.publication_id}"
            ),
            authority=FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
            exception_gate_id=attestation.gate_id,
            exception_gate_source_reference=attestation.gate_source_reference,
            exception_gate_source_version=attestation.gate_source_version,
            exception_publication_id=attestation.publication_id,
            exception_publication_snapshot_hash=attestation.publication_snapshot_hash,
            exception_attested_at=attestation.as_of,
        )
    draft = prepare_draft(command, transaction)
    return FutureAnnuityAutoDraftPolicyResult(
        annuity_task_id=task.id,
        fee_obligation_id=obligation.id,
        exception_attestation=attestation,
        draft=draft,
    )


class FutureAnnuityObligationErrorCode(str, Enum):
    INVALID_COMMAND = "FUTURE_ANNUITY_INVALID_COMMAND"
    TRANSACTION_DIRTY = "FUTURE_ANNUITY_TRANSACTION_DIRTY"
    TASK_NOT_FOUND = "FUTURE_ANNUITY_TASK_NOT_FOUND"
    CASE_NOT_FOUND = "FUTURE_ANNUITY_CASE_NOT_FOUND"
    SOURCE_ACTIVITY_NOT_FOUND = "FUTURE_ANNUITY_SOURCE_ACTIVITY_NOT_FOUND"
    SOURCE_DOCUMENT_NOT_FOUND = "FUTURE_ANNUITY_SOURCE_DOCUMENT_NOT_FOUND"
    SOURCE_EVIDENCE_NOT_FOUND = "FUTURE_ANNUITY_SOURCE_EVIDENCE_NOT_FOUND"
    REDUCTION_APPROVAL_NOT_FOUND = "FUTURE_ANNUITY_REDUCTION_APPROVAL_NOT_FOUND"
    TASK_CONFLICT = "FUTURE_ANNUITY_TASK_CONFLICT"
    SOURCE_ACTIVITY_CONFLICT = "FUTURE_ANNUITY_SOURCE_ACTIVITY_CONFLICT"
    SOURCE_DOCUMENT_CONFLICT = "FUTURE_ANNUITY_SOURCE_DOCUMENT_CONFLICT"
    SOURCE_EVIDENCE_CONFLICT = "FUTURE_ANNUITY_SOURCE_EVIDENCE_CONFLICT"
    PROJECTION_CONFLICT = "FUTURE_ANNUITY_PROJECTION_CONFLICT"
    LINEAGE_CONFLICT = "FUTURE_ANNUITY_LINEAGE_CONFLICT"
    RATE_MISSING = "FUTURE_ANNUITY_RATE_MISSING"
    RATE_AMBIGUOUS = "FUTURE_ANNUITY_RATE_AMBIGUOUS"
    RATE_INVALID = "FUTURE_ANNUITY_RATE_INVALID"
    REDUCTION_INVALID = "FUTURE_ANNUITY_REDUCTION_INVALID"
    REDUCTION_CONFLICT = "FUTURE_ANNUITY_REDUCTION_CONFLICT"
    IDEMPOTENCY_CONFLICT = "FUTURE_ANNUITY_IDEMPOTENCY_CONFLICT"
    OBLIGATION_CONFLICT = "FUTURE_ANNUITY_OBLIGATION_CONFLICT"


class FutureAnnuityObligationError(ValueError):
    def __init__(
        self,
        code: FutureAnnuityObligationErrorCode,
        status_code: int,
        details: dict[str, str | int | bool | None] | None = None,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self._details = {} if details is None else dict(details)
        super().__init__(code.value)

    @property
    def details(self) -> dict[str, str | int | bool | None]:
        return dict(self._details)


@dataclass(frozen=True, slots=True)
class RecognizeFutureAnnuityObligationCommand:
    annuity_task_id: int
    source_activity_id: str
    source_document_id: str
    source_evidence_version_id: str
    source_evidence_content_hash: str
    grant_fee_year_key: int
    rate_effective_on: date
    reduction_input: FeeReductionInput
    reduction_approval_id: str | None
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecognizeFutureAnnuityObligationResult:
    annuity_task_id: int
    fee_obligation_id: str
    fee_obligation_line_id: str
    source_activity_id: str
    source_document_id: str
    source_evidence_version_id: str
    source_evidence_content_hash: str
    grant_fee_year_key: int
    fee_code: str
    due_date: date
    official_full_amount: Decimal
    reduction_ratio: Decimal
    payable_amount: Decimal
    late_fee_base: Decimal
    client_instruction_status: FeeClientInstructionStatus
    activity_id: str
    idempotency_key: str
    reused: bool


_FUTURE_ANNUITY_FEE_CODE = {
    "INV": "CN_ANNUITY_FEE_INV",
    "UM": "CN_ANNUITY_FEE_UM",
    "DES": "CN_ANNUITY_FEE_DES",
}
_FUTURE_ANNUITY_FEE_CODES = frozenset(_FUTURE_ANNUITY_FEE_CODE.values())
_FUTURE_ANNUITY_CALC_PARAMS = {
    "CN_ANNUITY_FEE_INV": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"900.00","from":1,"to":3},'
        '{"amount":"1200.00","from":4,"to":6},'
        '{"amount":"2000.00","from":7,"to":9},'
        '{"amount":"4000.00","from":10,"to":12},'
        '{"amount":"6000.00","from":13,"to":15},'
        '{"amount":"8000.00","from":16,"to":20}]}'
    ),
    "CN_ANNUITY_FEE_UM": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10}]}'
    ),
    "CN_ANNUITY_FEE_DES": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10},'
        '{"amount":"3000.00","from":11,"to":15}]}'
    ),
}
_FUTURE_ANNUITY_PROJECTION = (
    "POST_GRANT_MAINTENANCE",
    "GRANT_ANNOUNCED",
    "PATENT_IN_FORCE",
    "CONFIRMED",
    "GRANTED",
)


def _future_annuity_fail(
    code: FutureAnnuityObligationErrorCode,
    status_code: int,
    details: dict[str, str | int | bool | None] | None = None,
) -> None:
    raise FutureAnnuityObligationError(code, status_code, details)


def _future_annuity_invalid(field: str) -> None:
    _future_annuity_fail(
        FutureAnnuityObligationErrorCode.INVALID_COMMAND,
        400,
        {"field": field},
    )


def _future_annuity_exact_string(value: object, limit: int) -> bool:
    return type(value) is str and bool(value) and value.strip() == value and len(value) <= limit


def _validate_future_annuity_command(
    command: RecognizeFutureAnnuityObligationCommand,
) -> None:
    if type(command) is not RecognizeFutureAnnuityObligationCommand:
        _future_annuity_invalid("command")
    for field in ("annuity_task_id", "grant_fee_year_key"):
        value = getattr(command, field)
        if type(value) is not int or value < 1:
            _future_annuity_invalid(field)
    for field in (
        "source_activity_id",
        "source_document_id",
        "source_evidence_version_id",
        "actor_id",
    ):
        if not _future_annuity_exact_string(getattr(command, field), 36):
            _future_annuity_invalid(field)
    if (
        type(command.source_evidence_content_hash) is not str
        or fullmatch(r"sha256:[0-9a-f]{64}", command.source_evidence_content_hash) is None
    ):
        _future_annuity_invalid("source_evidence_content_hash")
    if type(command.rate_effective_on) is not date:
        _future_annuity_invalid("rate_effective_on")
    if type(command.reduction_input) is not FeeReductionInput:
        _future_annuity_invalid("reduction_input")
    if command.reduction_approval_id is not None and not _future_annuity_exact_string(
        command.reduction_approval_id, 36
    ):
        _future_annuity_invalid("reduction_approval_id")
    if not _future_annuity_exact_string(command.idempotency_key, 128):
        _future_annuity_invalid("idempotency_key")


def _future_annuity_fee_code(case: Case) -> str:
    fee_code = _FUTURE_ANNUITY_FEE_CODE.get(case.patent_category)
    if fee_code is None:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.TASK_CONFLICT, 409)
    return fee_code


def _future_annuity_carrier_state(task: AnnuityTask) -> tuple[object, ...]:
    return (
        task.source_activity_id,
        task.source_document_id,
        task.source_evidence_version_id,
        task.source_evidence_content_hash,
        task.fee_obligation_id,
        task.grant_fee_year_key,
    )


def _future_annuity_line_input(
    *,
    fee_code: str,
    fee_name: str,
    year: int,
    due_date: date,
    full_amount: Decimal,
    reduction_ratio: Decimal,
    payable_amount: Decimal,
) -> FeeObligationLineInput:
    return FeeObligationLineInput(
        fee_code=fee_code,
        fee_name=fee_name,
        fee_year_key=year,
        official_full_amount=full_amount,
        reduction_ratio=reduction_ratio,
        payable_amount=payable_amount,
        source_amount=None,
        source_date=due_date,
        difference_review_state=FeeDifferenceReviewState.MATCHED,
    )


def _future_annuity_delegate_command(
    command: RecognizeFutureAnnuityObligationCommand,
    *,
    case_id: str,
    line: FeeObligationLineInput,
) -> RecognizeFeeObligationCommand:
    return RecognizeFeeObligationCommand(
        case_id=case_id,
        source_activity_id=command.source_activity_id,
        source_document_id=command.source_document_id,
        fee_domain=FeeDomain.GOV,
        obligation_type="FUTURE_ANNUITY",
        due_date=command.rate_effective_on,
        currency="CNY",
        source_status=FeeSourceStatus.VERIFIED,
        lines=(line,),
        actor_id=command.actor_id,
        idempotency_key=command.idempotency_key,
        supersedes_obligation_id=None,
        supersede_reason=None,
    )


def _future_annuity_result(
    command: RecognizeFutureAnnuityObligationCommand,
    delegated,
    *,
    reused: bool,
) -> RecognizeFutureAnnuityObligationResult:
    obligation = delegated.obligation
    if len(obligation.lines) != 1:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT, 409)
    line = obligation.lines[0]
    if obligation.due_date is None or line.official_full_amount is None:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT, 409)
    return RecognizeFutureAnnuityObligationResult(
        annuity_task_id=command.annuity_task_id,
        fee_obligation_id=obligation.id,
        fee_obligation_line_id=line.id,
        source_activity_id=command.source_activity_id,
        source_document_id=command.source_document_id,
        source_evidence_version_id=command.source_evidence_version_id,
        source_evidence_content_hash=command.source_evidence_content_hash,
        grant_fee_year_key=command.grant_fee_year_key,
        fee_code=line.fee_code,
        due_date=obligation.due_date,
        official_full_amount=line.official_full_amount,
        reduction_ratio=line.reduction_ratio,
        payable_amount=line.payable_amount,
        late_fee_base=line.official_full_amount,
        client_instruction_status=obligation.statuses.client_instruction_status,
        activity_id=delegated.activity_id,
        idempotency_key=command.idempotency_key,
        reused=reused,
    )


def _future_annuity_replay(
    command: RecognizeFutureAnnuityObligationCommand,
    transaction: Session,
    task: AnnuityTask,
    case: Case,
):
    carrier = _future_annuity_carrier_state(task)
    if any(value is None for value in carrier):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    expected_carrier = (
        command.source_activity_id,
        command.source_document_id,
        command.source_evidence_version_id,
        command.source_evidence_content_hash,
        task.fee_obligation_id,
        command.grant_fee_year_key,
    )
    if carrier != expected_carrier:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT, 409)
    if task.year_no != command.grant_fee_year_key or task.due_date != command.rate_effective_on:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT, 409)
    obligation = transaction.get(FeeObligation, task.fee_obligation_id)
    if obligation is None:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine).where(FeeObligationLine.obligation_id == obligation.id)
        )
    )
    if len(lines) != 1:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    stored = lines[0]
    lineage = transaction.get(FutureAnnuityReductionLineage, task.id)
    if (
        lineage is None
        or lineage.fee_obligation_line_id != stored.id
        or task.case_id != case.id
        or obligation.case_id != case.id
        or obligation.source_activity_id != task.source_activity_id
        or obligation.source_document_id != task.source_document_id
        or stored.obligation_id != obligation.id
        or stored.case_id != case.id
        or stored.source_activity_id != task.source_activity_id
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    stored_ratio = stored.reduction_ratio
    stored_provenance = lineage.reduction_input_provenance
    stored_approval_id = lineage.reduction_approval_id
    stored_zero = (
        type(stored_ratio) is Decimal
        and stored_ratio == Decimal("0.0000")
        and stored_ratio.as_tuple().exponent == -4
        and stored_provenance == FeeReductionInputProvenance.EXPLICIT_ENTRY.value
        and stored_approval_id is None
    )
    stored_reduced = (
        type(stored_ratio) is Decimal
        and stored_ratio in {Decimal("0.7000"), Decimal("0.8500")}
        and stored_ratio.as_tuple().exponent == -4
        and stored_provenance
        in {
            FeeReductionInputProvenance.EXPLICIT_ENTRY.value,
            FeeReductionInputProvenance.CONFIRMED_MIGRATION.value,
        }
        and stored_approval_id is not None
    )
    if not (stored_zero or stored_reduced):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    if (
        stored.fee_code not in _FUTURE_ANNUITY_FEE_CODES
        or not _future_annuity_exact_string(stored.fee_name, 256)
        or stored.fee_year_key != task.year_no
        or stored.official_full_amount is None
        or type(stored.official_full_amount) is not Decimal
        or not stored.official_full_amount.is_finite()
        or stored.official_full_amount < 0
        or type(stored.payable_amount) is not Decimal
        or not stored.payable_amount.is_finite()
        or stored.payable_amount < 0
        or stored.source_amount is not None
        or stored.source_date != task.due_date
        or stored.difference_review_state != FeeDifferenceReviewState.MATCHED.value
        or obligation.due_date != task.due_date
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    ratio = command.reduction_input.reduction_ratio
    provenance = command.reduction_input.provenance
    if (
        type(ratio) is not Decimal
        or not ratio.is_finite()
        or ratio != stored_ratio
        or type(provenance) is not FeeReductionInputProvenance
        or provenance.value != stored_provenance
        or command.reduction_approval_id != stored_approval_id
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT, 409)
    line = _future_annuity_line_input(
        fee_code=stored.fee_code,
        fee_name=stored.fee_name,
        year=stored.fee_year_key,
        due_date=stored.source_date,
        full_amount=stored.official_full_amount,
        reduction_ratio=stored.reduction_ratio,
        payable_amount=stored.payable_amount,
    )
    try:
        delegated = recognize_obligation(
            _future_annuity_delegate_command(command, case_id=case.id, line=line),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in {
            "FEE_OBLIGATION_STORED_STATE_INVALID",
            "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        }:
            _future_annuity_fail(
                FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT,
                409,
                {"cause": exc.code},
            )
        _future_annuity_fail(
            FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT,
            409,
            {"cause": exc.code},
        )
    delegated_lines = delegated.obligation.lines
    delegated_activity = transaction.get(CaseActivityEvent, delegated.activity_id)
    if (
        not delegated.reused
        or delegated.obligation.id != task.fee_obligation_id
        or delegated.obligation.id != obligation.id
        or len(delegated_lines) != 1
        or delegated_lines[0].id != stored.id
        or delegated.activity_id == task.source_activity_id
        or delegated_activity is None
        or delegated_activity.case_id != case.id
        or delegated_activity.lane != ActivityLane.FEE.value
        or delegated_activity.activity_type != "FEE_OBLIGATION_RECOGNIZED"
        or delegated_activity.idempotency_key != command.idempotency_key
        or delegated_activity.source_activity_id != task.source_activity_id
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    return delegated


def _validate_future_annuity_source(
    command: RecognizeFutureAnnuityObligationCommand,
    *,
    task: AnnuityTask,
    case: Case,
    activity: CaseActivityEvent,
    document: Document,
    evidence: DocumentEvidenceVersion,
    evidence_links: tuple[CaseActivityEventEvidence, ...],
) -> None:
    if (
        task.year_no != command.grant_fee_year_key
        or type(task.due_date) is not date
        or task.due_date != command.rate_effective_on
        or task.case_id != case.id
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.TASK_CONFLICT, 409)
    if (
        activity.case_id != case.id
        or activity.activity_type != "GRANT_ANNOUNCEMENT_CONFIRMED"
        or activity.lane != ActivityLane.LIFECYCLE.value
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or type(activity.effective_at) is not datetime
        or activity.effective_at.tzinfo is not None
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_ACTIVITY_CONFLICT, 409)
    if document.case_id != case.id:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_DOCUMENT_CONFLICT, 409)
    if len(evidence_links) != 1:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_EVIDENCE_CONFLICT, 409)
    link = evidence_links[0]
    if (
        link.case_id != case.id
        or link.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or link.object_type != "DocumentEvidenceVersion"
        or link.object_id != command.source_evidence_version_id
        or link.content_hash != command.source_evidence_content_hash
        or link.captured_at != activity.effective_at
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_EVIDENCE_CONFLICT, 409)
    if (
        evidence.case_id != case.id
        or evidence.document_id != command.source_document_id
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or type(evidence.reviewed_at) is not datetime
        or evidence.reviewed_at.tzinfo is not None
        or not _future_annuity_exact_string(evidence.reviewer_id, 36)
        or evidence.reviewer_id == evidence.creator_id
        or evidence.content_hash != command.source_evidence_content_hash
        or evidence.current_identity_key != f"{case.id}|{evidence.lineage_key}"
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_EVIDENCE_CONFLICT, 409)
    if (
        case.business_stage,
        case.official_procedure_stage,
        case.legal_status,
        case.lifecycle_verification_status,
        case.status,
    ) != _FUTURE_ANNUITY_PROJECTION:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.PROJECTION_CONFLICT, 409)


def _future_annuity_rate(
    transaction: Session,
    *,
    fee_code: str,
    fee_year_key: int,
    effective_on: date,
) -> tuple[FeeRate, Decimal]:
    books = tuple(
        transaction.scalars(
            select(OfficialRateBook).where(
                OfficialRateBook.book_code == "CNIPA_PATENT_ANNUITY_20260330",
                OfficialRateBook.approval_status == "APPROVED",
                OfficialRateBook.activation_status == "ACTIVE",
                OfficialRateBook.effective_from <= effective_on,
                or_(
                    OfficialRateBook.effective_to.is_(None),
                    OfficialRateBook.effective_to >= effective_on,
                ),
            )
        )
    )
    if not books:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_MISSING, 409)
    if len(books) != 1:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_AMBIGUOUS, 409)
    rates = tuple(
        transaction.scalars(
            select(FeeRate).where(
                FeeRate.official_rate_book_id == books[0].id,
                FeeRate.fee_code == fee_code,
                FeeRate.effective_from <= effective_on,
                or_(FeeRate.effective_to.is_(None), FeeRate.effective_to >= effective_on),
            )
        )
    )
    if not rates:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_MISSING, 409)
    if len(rates) != 1:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_AMBIGUOUS, 409)
    rate = rates[0]
    if (
        rate.enabled is not True
        or rate.fee_type != "GOV"
        or rate.currency != "CNY"
        or rate.calc_mode != "TIER"
        or rate.allow_reduction is not True
        or rate.calc_params is None
        or rate.calc_params != _FUTURE_ANNUITY_CALC_PARAMS.get(fee_code)
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_INVALID, 409)
    try:
        amount = select_cnipa_annuity_amount(fee_code, rate.calc_params, fee_year_key)
    except BusinessError:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_INVALID, 409)
    return rate, amount


def _future_annuity_approval_context(
    transaction: Session,
    approval: FeeReductionApproval,
    *,
    case_id: str,
) -> FeeReductionApprovalContext:
    try:
        scope = json.loads(approval.fee_scope_snapshot)
        canonical_scope = json.dumps(
            scope,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        scope_type = FeeReductionApprovalScopeType(approval.scope_type)
    except (TypeError, ValueError):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_CONFLICT, 409)
    if (
        type(scope) is not dict
        or set(scope) != {"fee_codes", "schema"}
        or scope.get("schema") != "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"
        or type(scope.get("fee_codes")) is not list
        or not scope["fee_codes"]
        or scope["fee_codes"] != sorted(set(scope["fee_codes"]))
        or any(not _future_annuity_exact_string(code, 64) for code in scope["fee_codes"])
        or canonical_scope != approval.fee_scope_snapshot
        or sha256(approval.fee_scope_snapshot.encode()).hexdigest() != approval.fee_scope_hash
    ):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_CONFLICT, 409)
    source = transaction.get(DocumentEvidenceVersion, approval.source_evidence_version_id)
    is_current = bool(
        source is not None
        and source.case_id == case_id
        and source.current_identity_key == f"{case_id}|{source.lineage_key}"
    )
    return FeeReductionApprovalContext(
        approval_id=approval.id,
        scope_type=scope_type,
        case_id=approval.case_id,
        applicant_set_key=approval.applicant_set_key,
        reduction_ratio=approval.reduction_ratio,
        fee_codes=frozenset(scope["fee_codes"]),
        fee_year_from=approval.fee_year_from,
        fee_year_to=approval.fee_year_to,
        effective_from=approval.effective_from,
        effective_to=approval.effective_to,
        source_evidence_version_id=approval.source_evidence_version_id,
        confirmation_status=approval.confirmation_status,
        is_current=is_current,
    )


def _future_annuity_reduction(
    command: RecognizeFutureAnnuityObligationCommand,
    transaction: Session,
    *,
    case_id: str,
    fee_code: str,
):
    ratio = command.reduction_input.reduction_ratio
    provenance = command.reduction_input.provenance
    approval_context = None
    if type(ratio) is Decimal and ratio == Decimal("0"):
        if (
            provenance is not FeeReductionInputProvenance.EXPLICIT_ENTRY
            or command.reduction_approval_id is not None
        ):
            _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_INVALID, 400)
    elif (
        type(ratio) is Decimal
        and ratio in {Decimal("0.7"), Decimal("0.85")}
        and provenance
        in {
            FeeReductionInputProvenance.EXPLICIT_ENTRY,
            FeeReductionInputProvenance.CONFIRMED_MIGRATION,
        }
    ):
        if command.reduction_approval_id is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_INVALID, 400)
        approval = transaction.get(FeeReductionApproval, command.reduction_approval_id)
        if approval is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_APPROVAL_NOT_FOUND, 404)
        approval_context = _future_annuity_approval_context(transaction, approval, case_id=case_id)
    else:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_INVALID, 400)
    context = FeeReductionEvaluationContext(
        case_id=case_id,
        applicant_set_key=None,
        fee_code=fee_code,
        fee_year_key=command.grant_fee_year_key,
        as_of_date=command.rate_effective_on,
    )
    try:
        return validate_annuity_fee_reduction(
            reduction_input=command.reduction_input,
            context=context,
            approval=approval_context,
            grant_fee_year_key=command.grant_fee_year_key,
        )
    except (AnnuityReductionScopeError, FeeReductionValidationError):
        _future_annuity_fail(FutureAnnuityObligationErrorCode.REDUCTION_CONFLICT, 409)


def recognize_future_annuity_obligation(
    command: RecognizeFutureAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFutureAnnuityObligationResult:
    _validate_future_annuity_command(command)
    if transaction.new or transaction.dirty or transaction.deleted:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.TRANSACTION_DIRTY, 409)
    with transaction.no_autoflush:
        task = transaction.get(AnnuityTask, command.annuity_task_id)
        if task is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.TASK_NOT_FOUND, 404)
        case = transaction.get(Case, task.case_id)
        if case is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.CASE_NOT_FOUND, 404)
        activity = transaction.get(CaseActivityEvent, command.source_activity_id)
        if activity is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_ACTIVITY_NOT_FOUND, 404)
        document = transaction.get(Document, command.source_document_id)
        if document is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_DOCUMENT_NOT_FOUND, 404)
        evidence = transaction.get(DocumentEvidenceVersion, command.source_evidence_version_id)
        if evidence is None:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.SOURCE_EVIDENCE_NOT_FOUND, 404)
        carrier = _future_annuity_carrier_state(task)
        if all(value is not None for value in carrier):
            delegated = _future_annuity_replay(command, transaction, task, case)
            return _future_annuity_result(command, delegated, reused=True)
        if any(value is not None for value in carrier):
            _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
        evidence_links = tuple(
            transaction.scalars(
                select(CaseActivityEventEvidence).where(
                    CaseActivityEventEvidence.activity_id == activity.id
                )
            )
        )
        _validate_future_annuity_source(
            command,
            task=task,
            case=case,
            activity=activity,
            document=document,
            evidence=evidence,
            evidence_links=evidence_links,
        )
        fee_code = _future_annuity_fee_code(case)
        rate, full_amount = _future_annuity_rate(
            transaction,
            fee_code=fee_code,
            fee_year_key=command.grant_fee_year_key,
            effective_on=command.rate_effective_on,
        )
        reduction = _future_annuity_reduction(
            command,
            transaction,
            case_id=case.id,
            fee_code=fee_code,
        )
        try:
            amount = calculate_annuity_payable_amount(
                full_annual_fee=full_amount,
                eligible_ratio=reduction.payable_ratio,
            )
        except ValueError:
            _future_annuity_fail(FutureAnnuityObligationErrorCode.RATE_INVALID, 409)
        line = _future_annuity_line_input(
            fee_code=fee_code,
            fee_name=rate.fee_name or "年费",
            year=command.grant_fee_year_key,
            due_date=command.rate_effective_on,
            full_amount=amount.full_annual_fee,
            reduction_ratio=reduction.reduction_ratio,
            payable_amount=amount.payable_amount,
        )
    try:
        with transaction.begin_nested():
            delegated = recognize_obligation(
                _future_annuity_delegate_command(command, case_id=case.id, line=line),
                transaction,
            )
            if delegated.reused:
                _future_annuity_fail(FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT, 409)
            delegated_lines = delegated.obligation.lines
            if (
                delegated.obligation.case_id != case.id
                or delegated.obligation.source.source_activity_id != command.source_activity_id
                or delegated.obligation.source.source_document_id != command.source_document_id
                or len(delegated_lines) != 1
                or delegated_lines[0].obligation_id != delegated.obligation.id
                or delegated_lines[0].case_id != case.id
                or delegated_lines[0].source_activity_id != command.source_activity_id
                or delegated_lines[0].fee_code != fee_code
                or delegated_lines[0].fee_year_key != command.grant_fee_year_key
                or delegated_lines[0].reduction_ratio != reduction.reduction_ratio
                or reduction.provenance is not command.reduction_input.provenance
                or reduction.approval_id != command.reduction_approval_id
            ):
                _future_annuity_fail(FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT, 409)
            transaction.add(
                FutureAnnuityReductionLineage(
                    annuity_task_id=task.id,
                    fee_obligation_line_id=delegated_lines[0].id,
                    reduction_input_provenance=reduction.provenance.value,
                    reduction_approval_id=reduction.approval_id,
                )
            )
            task.source_activity_id = command.source_activity_id
            task.source_document_id = command.source_document_id
            task.source_evidence_version_id = command.source_evidence_version_id
            task.source_evidence_content_hash = command.source_evidence_content_hash
            task.fee_obligation_id = delegated.obligation.id
            task.grant_fee_year_key = command.grant_fee_year_key
            transaction.flush()
    except FutureAnnuityObligationError:
        raise
    except BusinessError as exc:
        _future_annuity_fail(
            FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT,
            409,
            {"cause": exc.code},
        )
    except IntegrityError:
        _future_annuity_fail(FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT, 409)
    return _future_annuity_result(command, delegated, reused=False)


def generate_annuity_tasks_for_case(
    db: Session,
    *,
    case_id: str,
) -> dict:
    """Generate multi-year annuity tasks for a GRANTED case."""
    normalized_case_id = (case_id or "").strip()
    case = db.execute(
        select(Case).where(or_(Case.id == normalized_case_id, Case.case_no == normalized_case_id))
    ).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "案卷不存在", status_code=404)

    if case.status != "GRANTED":
        raise_business_error("CASE_NOT_GRANTED", "案卷状态不是已授权", status_code=400)

    if not case.first_annuity_year:
        raise_business_error("NO_FIRST_ANNUITY_YEAR", "未设置首年年费年度", status_code=400)

    # Calculate last year: valid_until or filing_date + 20 years (standard CN patent term)
    if case.valid_until and case.filing_date:
        last_year = case.valid_until.year - case.filing_date.year + 1
    else:
        last_year = 20

    first_year = case.first_annuity_year
    resolved_case_id = case.id
    tasks_created = 0
    tasks_skipped = 0

    for year_no in range(first_year, last_year + 1):
        # Check if task already exists for this case + year
        existing = (
            db.query(AnnuityTask)
            .filter(AnnuityTask.case_id == resolved_case_id, AnnuityTask.year_no == year_no)
            .first()
        )
        if existing:
            tasks_skipped += 1
            continue

        # Calculate due date: filing_date + year_no years
        if case.filing_date:
            try:
                due = case.filing_date.replace(year=case.filing_date.year + year_no)
            except ValueError:
                # Handle Feb 29 edge case
                due = case.filing_date.replace(year=case.filing_date.year + year_no, day=28)
        else:
            due = date.today()

        gov_amt = _rate_amount(
            db,
            fee_type="GOV",
            currency="CNY",
            year_no=year_no,
            patent_category=case.patent_category,
        )
        svc_amt = _ZERO

        task = AnnuityTask(
            case_id=resolved_case_id,
            client_id=case.client_id,
            year_no=year_no,
            due_date=due,
            status="OPEN",
            gov_fee_amt=gov_amt,
            service_fee_amt=svc_amt,
        )
        db.add(task)
        tasks_created += 1

    db.flush()
    return {
        "case_id": resolved_case_id,
        "case_no": case.case_no,
        "first_year": first_year,
        "last_year": last_year,
        "tasks_created": tasks_created,
        "tasks_skipped": tasks_skipped,
    }
