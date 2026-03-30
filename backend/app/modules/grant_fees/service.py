from __future__ import annotations

from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.fees.models import T_GrantFeeTask

GRANT_FEE_TASK_PERMISSION_CODES = ("GrantFeeTask.Read", "GrantFeeTask.Write")
GRANT_FEE_TASK_STATES = ("OPEN", "WAITING_CLIENT", "READY_TO_DRAFT", "DRAFT_GENERATED", "DONE")
GRANT_FEE_TASK_ACTIONS = (
    "mark_waiting_client",
    "record_pay_instruction",
    "record_abandon_instruction",
    "mark_draft_generated",
    "mark_done",
)

_STATE_ALLOWED_ACTIONS = {
    "OPEN": ("mark_waiting_client",),
    "WAITING_CLIENT": ("record_pay_instruction", "record_abandon_instruction"),
    "READY_TO_DRAFT": ("mark_draft_generated",),
    "DRAFT_GENERATED": ("mark_done",),
    "DONE": (),
}

_ACTION_NEXT_STATE = {
    "mark_waiting_client": "WAITING_CLIENT",
    "record_pay_instruction": "READY_TO_DRAFT",
    "record_abandon_instruction": "DONE",
    "mark_draft_generated": "DRAFT_GENERATED",
    "mark_done": "DONE",
}


def get_grant_fee_module_contract() -> dict[str, object]:
    return {
        "module": "grant_fees",
        "permission_namespace": "GrantFeeTask",
        "permission_codes": list(GRANT_FEE_TASK_PERMISSION_CODES),
        "status": "ok",
    }


def list_grant_fee_tasks(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> dict[str, Any]:
    stmt = select(T_GrantFeeTask)
    predicates = []

    case_id = str(filters.get("case_id") or "").strip()
    if case_id:
        predicates.append(T_GrantFeeTask.case_id == case_id)

    client_instruction = str(filters.get("client_instruction") or "").strip().upper()
    if client_instruction:
        predicates.append(T_GrantFeeTask.client_instruction == client_instruction)

    if filters.get("draft_generated") is not None:
        predicates.append(T_GrantFeeTask.draft_generated.is_(bool(filters["draft_generated"])))

    if filters.get("is_overdue") is not None:
        predicates.append(T_GrantFeeTask.is_overdue.is_(bool(filters["is_overdue"])))

    date_from = filters.get("date_from")
    if date_from is not None:
        predicates.append(T_GrantFeeTask.due_date >= date_from)

    date_to = filters.get("date_to")
    if date_to is not None:
        predicates.append(T_GrantFeeTask.due_date <= date_to)

    if predicates:
        stmt = stmt.where(and_(*predicates))

    stmt = stmt.order_by(T_GrantFeeTask.due_date.asc(), T_GrantFeeTask.id.asc())

    tasks = list(db.execute(stmt).scalars().all())
    projected_items = []
    status_filter = str(filters.get("status") or "").strip().upper()

    for task in tasks:
        status = derive_grant_fee_task_state(task)
        if status_filter and status != status_filter:
            continue
        projected_items.append(_serialize_grant_fee_task_list_item(task, state=status))

    total = len(projected_items)
    safe_page = max(int(page or 1), 1)
    safe_page_size = max(int(page_size or 20), 1)
    start = (safe_page - 1) * safe_page_size
    end = start + safe_page_size
    return {
        "items": projected_items[start:end],
        "page": safe_page,
        "page_size": safe_page_size,
        "total": total,
    }


def _load_grant_fee_task(db: Session, *, task_id: str) -> T_GrantFeeTask:
    task = db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)).scalar_one_or_none()
    if task is None:
        raise_business_error("GRANT_FEE_TASK_NOT_FOUND", "Grant fee task not found", status_code=404)
    return task


def _normalize_action(action: Any) -> str:
    return str(action or "").strip()


def derive_grant_fee_task_state(task: T_GrantFeeTask) -> str:
    notify_count = int(task.notify_count or 0)
    client_instruction = (task.client_instruction or "").strip().upper() or "NONE"

    if notify_count >= 4:
        return "DONE"
    if task.draft_generated:
        return "DRAFT_GENERATED"
    if client_instruction == "PAY":
        return "READY_TO_DRAFT"
    if client_instruction == "ABANDON":
        return "DONE"
    if task.notice_sent or notify_count >= 1:
        return "WAITING_CLIENT"
    return "OPEN"


def get_grant_fee_task_state(db: Session, *, task_id: str) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    state = derive_grant_fee_task_state(task)
    return _serialize_grant_fee_task_state(task, state=state)


def apply_grant_fee_task_action(
    db: Session,
    *,
    task_id: str,
    action: str,
) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    current_state = derive_grant_fee_task_state(task)
    normalized_action = _normalize_action(action)
    allowed_actions = _STATE_ALLOWED_ACTIONS[current_state]

    if normalized_action not in allowed_actions:
        raise_business_error(
            "GRANT_FEE_STATE_TRANSITION_INVALID",
            "Invalid grant fee task state transition",
            details={
                "task_id": task_id,
                "from": current_state,
                "action": normalized_action,
                "allowed_actions": list(allowed_actions),
            },
            status_code=400,
        )

    if normalized_action == "mark_waiting_client":
        task.notice_sent = True
        task.client_instruction = "NONE"
        task.notify_count = 1
        task.draft_generated = False
    elif normalized_action == "record_pay_instruction":
        task.client_instruction = "PAY"
        task.notify_count = 2
    elif normalized_action == "record_abandon_instruction":
        task.client_instruction = "ABANDON"
        task.notify_count = 4
    elif normalized_action == "mark_draft_generated":
        task.draft_generated = True
        task.notify_count = 3
    elif normalized_action == "mark_done":
        task.notify_count = 4

    db.commit()
    db.refresh(task)
    return _serialize_grant_fee_task_state(task, state=derive_grant_fee_task_state(task))


def _serialize_grant_fee_task_state(task: T_GrantFeeTask, *, state: str) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "state": state,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "notify_count": int(task.notify_count or 0),
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "is_overdue": bool(task.is_overdue),
        "allowed_actions": list(_STATE_ALLOWED_ACTIONS[state]),
    }


def _serialize_grant_fee_task_list_item(task: T_GrantFeeTask, *, state: str) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "status": state,
        "due_date": task.due_date,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "gov_fee_amt": task.gov_fee_amt,
        "service_fee_amt": task.service_fee_amt,
        "currency": task.currency,
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "is_overdue": bool(task.is_overdue),
    }
