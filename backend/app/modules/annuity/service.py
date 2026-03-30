from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.annuity.export_excel import build_pay_list_export_xlsx
from app.modules.annuity.models import AnnuityTask, GovPayment, PayList
from app.modules.cases.models import Case
from app.modules.fees.models import FeeDraft, FeeItem, FeeRate
from app.modules.masterdata.clients.models import Client

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

    case_id = filters.get("case_id")
    client_id = filters.get("client_id")
    notice_status_values = _normalize_statuses(filters.get("notice_status"))

    if case_id:
        stmt = stmt.where(AnnuityTask.case_id == case_id)
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
        "status_counts": [
            {"key": key, "count": status_counts[key]} for key in sorted(status_counts.keys())
        ],
        "year_counts": [
            {"key": key, "count": year_counts[key]} for key in sorted(year_counts.keys(), key=int)
        ],
    }


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
    pending_mode = _normalize_pending_mode(
        filters.get("pending_mode", filters.get("pending_filter", filters.get("pending")))
    )

    case_id = filters.get("case_id")
    client_id = filters.get("client_id")
    notice_status_values = _normalize_statuses(filters.get("notice_status"))

    if case_id:
        stmt = stmt.where(AnnuityTask.case_id == case_id)
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
    total = len(all_items)
    offset = (page - 1) * page_size
    items = all_items[offset : offset + page_size]
    return items, total, summarize_annuity_tasks(all_items)


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


def _rate_amount(
    db: Session,
    *,
    fee_type: str,
    currency: str,
    year_no: int | None = None,
) -> Decimal:
    conditions = [
        FeeRate.enabled.is_(True),
        FeeRate.rate_group == "ANNUITY",
        FeeRate.fee_type == fee_type,
        FeeRate.currency == currency,
    ]
    rate = (
        db.execute(select(FeeRate).where(*conditions).order_by(FeeRate.updated_at.desc()))
        .scalars()
        .first()
    )
    if not rate or rate.default_amount is None:
        return Decimal("0")
    return Decimal(rate.default_amount)


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

            instruction = (task.client_instruction or "").strip().upper()
            if instruction == "ABANDON":
                raise_business_error(
                    "ANNUITY_STATE_CONFLICT",
                    "Cannot generate draft for ABANDON instruction",
                    status_code=409,
                )

            if _draft_exists_for_target(db, task_id=task_id, year_no=year_no):
                raise_business_error(
                    "ANNUITY_DRAFT_ALREADY_GENERATED",
                    "Draft already generated for task/year",
                    status_code=409,
                )

            gov_amount = _rate_amount(db, fee_type="GOV", currency=normalized_currency)
            service_amount = _rate_amount(db, fee_type="SERVICE", currency=normalized_currency)
            total_amount = gov_amount + service_amount
            marker = _annuity_marker(task_id, year_no)

            draft = FeeDraft(
                id=str(uuid4()),
                case_id=task.case_id,
                client_id=task.client_id,
                draft_type=_ANNUITY_DRAFT_TYPE,
                currency=normalized_currency,
                status="OPEN",
                total_gov=gov_amount,
                total_service=service_amount,
                total_misc=Decimal("0"),
                amount=total_amount,
                created_by=actor_id,
                updated_by=actor_id,
            )
            db.add(draft)

            db.add(
                FeeItem(
                    id=str(uuid4()),
                    draft_id=draft.id,
                    case_id=task.case_id,
                    fee_code="ANNUITY_GOV",
                    fee_name="Annuity Government Fee",
                    fee_type="GOV",
                    year_no=year_no,
                    quantity=Decimal("1"),
                    unit_price=gov_amount,
                    amount=gov_amount,
                    remark=marker,
                    created_by=actor_id,
                    updated_by=actor_id,
                )
            )
            db.add(
                FeeItem(
                    id=str(uuid4()),
                    draft_id=draft.id,
                    case_id=task.case_id,
                    fee_code="ANNUITY_SERVICE",
                    fee_name="Annuity Service Fee",
                    fee_type="SERVICE",
                    year_no=year_no,
                    quantity=Decimal("1"),
                    unit_price=service_amount,
                    amount=service_amount,
                    remark=marker,
                    created_by=actor_id,
                    updated_by=actor_id,
                )
            )

            task.draft_generated = True
            db.commit()
            success.append(
                {
                    "source_task_id": target["source_task_id"],
                    "task_id": task_id,
                    "year_no": year_no,
                    "draft_id": draft.id,
                    "currency": normalized_currency,
                    "amount": str(total_amount),
                    "pay_next_year": target["pay_next_year"],
                }
            )
        except BusinessError as exc:
            db.rollback()
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

    db.commit()
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
        "created_at": pay_list.created_at,
        "updated_at": pay_list.updated_at,
        "created_by": pay_list.created_by,
        "updated_by": pay_list.updated_by,
    }


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
    """Record header paid date and advance an exported pay list to PAID."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    if (pay_list.status or "").strip().upper() != "EXPORTED":
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Pay list can only be marked paid from EXPORTED status",
            details={"status": pay_list.status},
            status_code=409,
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
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    gov_payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.pay_list_id == pay_list.id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )

    return {
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
                "fee_item_id": gov_payment.fee_item_id,
                "status": gov_payment.status,
                "currency": gov_payment.currency,
                "paid_date": gov_payment.paid_date,
                "paid_amount": str(gov_payment.paid_amount),
                "official_receipt_no": gov_payment.official_receipt_no,
                "remark": gov_payment.remark,
                "created_at": gov_payment.created_at,
                "updated_at": gov_payment.updated_at,
                "created_by": gov_payment.created_by,
                "updated_by": gov_payment.updated_by,
            }
            for gov_payment in gov_payments
        ],
    }


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


def register_gov_payment(
    db: Session,
    *,
    pay_list_id: int,
    fee_item_id: str,
    paid_date: date | None = None,
    paid_amount: Decimal | None = None,
    official_receipt_no: str | None = None,
    remark: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Register official payment with duplicate protection and pay-list status recompute."""
    pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one_or_none()
    if not pay_list:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)

    normalized_fee_item_id = (fee_item_id or "").strip()
    if not normalized_fee_item_id:
        raise_business_error("FEE_ITEM_REQUIRED", "fee_item_id is required", status_code=400)

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
        target.updated_by = actor_id

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


def generate_annuity_tasks_for_case(
    db: Session,
    *,
    case_id: str,
) -> dict:
    """Generate multi-year annuity tasks for a GRANTED case."""
    from app.modules.cases.models import Case

    case = db.query(Case).filter(Case.id == case_id).first()
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
    tasks_created = 0
    tasks_skipped = 0

    for year_no in range(first_year, last_year + 1):
        # Check if task already exists for this case + year
        existing = (
            db.query(AnnuityTask)
            .filter(AnnuityTask.case_id == case_id, AnnuityTask.year_no == year_no)
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

        # Look up fee rates (with year_no for year-specific rates)
        gov_amt = _rate_amount(db, fee_type="GOV", currency="CNY", year_no=year_no)
        svc_amt = _rate_amount(db, fee_type="SERVICE", currency="CNY", year_no=year_no)

        task = AnnuityTask(
            case_id=case_id,
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
        "case_id": case_id,
        "case_no": case.case_no,
        "first_year": first_year,
        "last_year": last_year,
        "tasks_created": tasks_created,
        "tasks_skipped": tasks_skipped,
    }
