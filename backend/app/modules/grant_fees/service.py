from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.billing.models import Bill, BillItem
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.service import (
    _backend_storage_dir,
    build_document_template_render_context,
    persist_generated_attachment,
    resolve_document_template_render_source,
)
from app.modules.fees.models import FeeDraft, FeeItem, T_GrantFeeTask
from app.modules.fees.service import recalc_fee_draft_totals
from app.modules.templates.render import TemplateRenderer

GRANT_FEE_TASK_PERMISSION_CODES = ("GrantFeeTask.Read", "GrantFeeTask.Write")
GRANT_FEE_TASK_STATES = ("OPEN", "WAITING_CLIENT", "READY_TO_DRAFT", "DRAFT_GENERATED", "DONE")
GRANT_FEE_TASK_ACTIONS = (
    "mark_waiting_client",
    "record_pay_instruction",
    "record_abandon_instruction",
    "mark_draft_generated",
    "mark_done",
)

GRANT_FEE_DRAFT_TYPE = "GRANT_FEE"
GRANT_FEE_DRAFT_MARKER_PREFIX = "GRANT_FEE_TASK:"
GRANT_FEE_GOV_FEE_CODE = "GRANT_FEE_GOV"
GRANT_FEE_SERVICE_FEE_CODE = "GRANT_FEE_SERVICE"
GRANT_FEE_NOTICE_TEMPLATE_CODE = "GRANT_FEE_NOTICE"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
GRANT_FEE_NOTICE_DUE_DAYS = 60

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

_BATCH_ALLOWED_ACTIONS = ("record_pay_instruction", "record_abandon_instruction")
_NOTICE_ALLOWED_STATES = ("OPEN", "WAITING_CLIENT")


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

    case_no = str(filters.get("case_no") or "").strip()
    if case_no:
        stmt = stmt.join(Case, Case.id == T_GrantFeeTask.case_id)
        predicates.append(Case.case_no == case_no)

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
    case_no_map = _build_grant_fee_task_case_no_map(db, tasks=tasks)
    bill_visibility_map = _build_grant_fee_bill_visibility_map(db, tasks=tasks)
    projected_items = []
    status_filter = str(filters.get("status") or "").strip().upper()

    for task in tasks:
        status = derive_grant_fee_task_state(task)
        if status_filter and status != status_filter:
            continue
        projected_items.append(
            _serialize_grant_fee_task_list_item(
                task,
                state=status,
                case_no=case_no_map.get(task.case_id),
                bill_visibility=bill_visibility_map.get(
                    task.id,
                    {"billed": False, "linked_bill_id": None, "linked_bill_no": None},
                ),
            )
        )

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
    task = db.execute(
        select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)
    ).scalar_one_or_none()
    if task is None:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND", "Grant fee task not found", status_code=404
        )
    return task


def _normalize_action(action: Any) -> str:
    return str(action or "").strip()


def _apply_grant_fee_task_mutation(task: T_GrantFeeTask, *, normalized_action: str) -> None:
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


def _draft_marker(task_id: str) -> str:
    return f"{GRANT_FEE_DRAFT_MARKER_PREFIX}{task_id}"


def _find_existing_grant_fee_draft(db: Session, *, marker: str) -> FeeDraft | None:
    stmt = (
        select(FeeDraft)
        .where(
            FeeDraft.draft_type == GRANT_FEE_DRAFT_TYPE,
            FeeDraft.id.in_(select(FeeItem.draft_id).where(FeeItem.remark == marker)),
        )
        .order_by(FeeDraft.created_at.asc(), FeeDraft.id.asc())
    )
    return db.execute(stmt).scalars().first()


def _count_fee_items_for_draft(db: Session, *, draft_id: str) -> int:
    return len(db.execute(select(FeeItem).where(FeeItem.draft_id == draft_id)).scalars().all())


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


def _case_has_required_grant_fields(case: Case) -> bool:
    return all(
        (
            case.app_no,
            case.filing_date,
            case.pub_no,
            case.pub_date,
            case.grant_no,
            case.grant_date,
            case.first_annuity_year is not None,
            case.valid_until,
        )
    )


def _advance_case_to_granted_if_ready(db: Session, *, task: T_GrantFeeTask) -> None:
    case = db.execute(select(Case).where(Case.id == task.case_id)).scalar_one_or_none()
    if case is None or case.status == "GRANTED":
        return
    if _case_has_required_grant_fields(case):
        case.status = "GRANTED"


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

    _apply_grant_fee_task_mutation(task, normalized_action=normalized_action)
    if normalized_action == "mark_done":
        _advance_case_to_granted_if_ready(db, task=task)

    db.commit()
    db.refresh(task)
    return _serialize_grant_fee_task_state(task, state=derive_grant_fee_task_state(task))


def ensure_grant_fee_task_for_notice_document(
    db: Session,
    *,
    document: Document,
    template: DocTemplate,
) -> T_GrantFeeTask | None:
    if (
        (template.code or "").strip().upper() != "GRANT_NOTICE"
        or (template.fee_draft_type or "").strip().upper() != GRANT_FEE_DRAFT_TYPE
        or not str(document.case_id or "").strip()
    ):
        return None

    existing_task = (
        db.execute(
            select(T_GrantFeeTask)
            .where(T_GrantFeeTask.case_id == document.case_id)
            .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
        )
        .scalars()
        .first()
    )
    if existing_task is not None:
        return existing_task

    base_date = document.doc_date or date.today()
    task = T_GrantFeeTask(
        case_id=document.case_id,
        due_date=base_date + timedelta(days=GRANT_FEE_NOTICE_DUE_DAYS),
        gov_fee_amt=0,
        service_fee_amt=0,
        currency="CNY",
        client_instruction="NONE",
        notify_count=0,
        draft_generated=False,
        notice_sent=False,
        is_overdue=False,
    )
    db.add(task)
    db.flush()
    return task


def apply_grant_fee_batch_instruction(
    db: Session,
    *,
    task_ids: list[str],
    action: str,
) -> dict[str, Any]:
    normalized_action = _normalize_action(action)
    if normalized_action not in _BATCH_ALLOWED_ACTIONS:
        raise_business_error(
            "GRANT_FEE_BATCH_ACTION_INVALID",
            "Invalid grant fee batch action",
            details={"action": normalized_action, "allowed_actions": list(_BATCH_ALLOWED_ACTIONS)},
            status_code=400,
        )

    unique_task_ids = list(
        dict.fromkeys(
            str(task_id or "").strip() for task_id in task_ids if str(task_id or "").strip()
        )
    )
    if not unique_task_ids:
        raise_business_error(
            "GRANT_FEE_BATCH_SELECTION_REQUIRED",
            "task_ids must not be empty",
            status_code=400,
        )

    tasks = list(
        db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id.in_(unique_task_ids)))
        .scalars()
        .all()
    )
    task_by_id = {task.id: task for task in tasks}
    missing_task_ids = [task_id for task_id in unique_task_ids if task_id not in task_by_id]
    if missing_task_ids:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND",
            "One or more grant fee tasks do not exist",
            details={"task_ids": missing_task_ids},
            status_code=404,
        )

    invalid_tasks: list[dict[str, str]] = []
    for task_id in unique_task_ids:
        task = task_by_id[task_id]
        state = derive_grant_fee_task_state(task)
        if state != "WAITING_CLIENT":
            invalid_tasks.append({"task_id": task_id, "state": state})

    if invalid_tasks:
        raise_business_error(
            "GRANT_FEE_BATCH_STATE_INVALID",
            "One or more selected grant fee tasks are not waiting for client instruction",
            details={"invalid_tasks": invalid_tasks, "required_state": "WAITING_CLIENT"},
            status_code=400,
        )

    for task_id in unique_task_ids:
        _apply_grant_fee_task_mutation(task_by_id[task_id], normalized_action=normalized_action)

    db.commit()
    return {
        "success_count": len(unique_task_ids),
        "failure_count": 0,
        "updated_task_ids": unique_task_ids,
    }


def generate_grant_fee_notice_documents(
    db: Session,
    *,
    task_ids: list[str],
) -> dict[str, Any]:
    unique_task_ids = list(
        dict.fromkeys(
            str(task_id or "").strip() for task_id in task_ids if str(task_id or "").strip()
        )
    )
    if not unique_task_ids:
        raise_business_error(
            "GRANT_FEE_NOTICE_SELECTION_REQUIRED",
            "task_ids must not be empty",
            status_code=400,
        )

    tasks = list(
        db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id.in_(unique_task_ids)))
        .scalars()
        .all()
    )
    task_by_id = {task.id: task for task in tasks}
    missing_task_ids = [task_id for task_id in unique_task_ids if task_id not in task_by_id]
    if missing_task_ids:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND",
            "One or more grant fee tasks do not exist",
            details={"task_ids": missing_task_ids},
            status_code=404,
        )

    doc_template = db.execute(
        select(DocTemplate).where(
            DocTemplate.code == GRANT_FEE_NOTICE_TEMPLATE_CODE,
            DocTemplate.enabled.is_(True),
        )
    ).scalar_one_or_none()
    if doc_template is None:
        raise_business_error(
            "GRANT_FEE_NOTICE_TEMPLATE_NOT_FOUND",
            "Grant fee notice template is not configured",
            details={"template_code": GRANT_FEE_NOTICE_TEMPLATE_CODE},
            status_code=409,
        )

    try:
        _, template_path = resolve_document_template_render_source(db, doc_template=doc_template)
        renderer = TemplateRenderer()
        created_items: list[dict[str, Any]] = []

        for task_id in unique_task_ids:
            task = task_by_id[task_id]
            state = derive_grant_fee_task_state(task)
            _validate_grant_fee_notice_task(task, state=state)
            created_items.append(
                _generate_grant_fee_notice_document(
                    db,
                    task=task,
                    doc_template=doc_template,
                    template_path=template_path,
                    renderer=renderer,
                )
            )

        db.commit()
    except BusinessError:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise_business_error(
            "GRANT_FEE_NOTICE_GENERATION_FAILED",
            "Grant fee notice generation failed",
            details={"error": str(exc)},
            status_code=409,
        )

    return {
        "success_count": len(created_items),
        "failure_count": 0,
        "generated_document_ids": [item["document_id"] for item in created_items],
        "items": created_items,
    }


def generate_grant_fee_draft(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    state = derive_grant_fee_task_state(task)
    marker = _draft_marker(task_id)
    existing_draft = _find_existing_grant_fee_draft(db, marker=marker)

    if existing_draft is not None:
        if not task.draft_generated:
            task.draft_generated = True
            db.commit()
            db.refresh(task)
            state = derive_grant_fee_task_state(task)
        return _serialize_grant_fee_draft_generation_result(
            task,
            draft=existing_draft,
            state=state,
            reused=True,
            item_count=_count_fee_items_for_draft(db, draft_id=existing_draft.id),
        )

    normalized_currency = str(task.currency or "").strip().upper()
    if state != "READY_TO_DRAFT" or task.draft_generated or not str(task.case_id or "").strip():
        raise_business_error(
            "GRANT_FEE_DRAFT_PRECONDITION_FAILED",
            "Grant fee task is not ready to generate draft",
            details={
                "task_id": task_id,
                "state": state,
                "draft_generated": bool(task.draft_generated),
                "case_id": task.case_id,
                "currency": task.currency,
            },
            status_code=400,
        )
    if not normalized_currency:
        raise_business_error(
            "GRANT_FEE_DRAFT_PRECONDITION_FAILED",
            "Grant fee task currency is required",
            details={"task_id": task_id, "currency": task.currency},
            status_code=400,
        )

    case = db.execute(select(Case).where(Case.id == task.case_id)).scalar_one_or_none()
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    gov_amount = Decimal(task.gov_fee_amt or 0)
    service_amount = Decimal(task.service_fee_amt or 0)
    total_amount = gov_amount + service_amount

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=case.id,
        client_id=case.client_id,
        draft_type=GRANT_FEE_DRAFT_TYPE,
        currency=normalized_currency,
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(draft)
    db.flush()

    fee_items = [
        {
            "fee_code": GRANT_FEE_GOV_FEE_CODE,
            "fee_name": "Grant fee government fee",
            "fee_type": "GOV",
            "amount": gov_amount,
        },
        {
            "fee_code": GRANT_FEE_SERVICE_FEE_CODE,
            "fee_name": "Grant fee service fee",
            "fee_type": "SERVICE",
            "amount": service_amount,
        },
    ]
    for line in fee_items:
        db.add(
            FeeItem(
                id=str(uuid4()),
                draft_id=draft.id,
                case_id=case.id,
                fee_code=line["fee_code"],
                fee_name=line["fee_name"],
                fee_type=line["fee_type"],
                quantity=Decimal("1"),
                unit_price=line["amount"],
                amount=line["amount"],
                remark=marker,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )

    db.flush()
    recalc_fee_draft_totals(db, draft_id=draft.id)
    draft = db.get(FeeDraft, draft.id)
    if draft is None:
        raise_business_error(
            "GRANT_FEE_DRAFT_GENERATION_FAILED", "Draft generation failed", status_code=500
        )

    task.draft_generated = True
    db.commit()
    db.refresh(task)
    db.refresh(draft)
    return _serialize_grant_fee_draft_generation_result(
        task,
        draft=draft,
        state=derive_grant_fee_task_state(task),
        reused=False,
        item_count=len(fee_items),
        amount=total_amount,
    )


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


def _build_grant_fee_bill_visibility_map(
    db: Session,
    *,
    tasks: list[T_GrantFeeTask],
) -> dict[str, dict[str, Any]]:
    task_ids = [str(task.id) for task in tasks if str(task.id or "").strip()]
    if not task_ids:
        return {}

    markers = {_draft_marker(task_id): task_id for task_id in task_ids}
    fee_item_rows = list(
        db.execute(
            select(FeeItem.remark, FeeItem.draft_id)
            .where(FeeItem.remark.in_(list(markers)), FeeItem.draft_id.is_not(None))
            .order_by(FeeItem.draft_id.asc())
        ).all()
    )

    task_to_draft_ids: dict[str, list[str]] = {}
    for remark, draft_id in fee_item_rows:
        if not remark or not draft_id:
            continue
        task_id = markers.get(str(remark))
        if not task_id:
            continue
        draft_ids = task_to_draft_ids.setdefault(task_id, [])
        if draft_id not in draft_ids:
            draft_ids.append(draft_id)

    all_draft_ids = sorted(
        {draft_id for draft_ids in task_to_draft_ids.values() for draft_id in draft_ids}
    )
    if not all_draft_ids:
        return {}

    bill_rows = list(
        db.execute(
            select(BillItem.draft_id, Bill.id, Bill.bill_no)
            .join(Bill, Bill.id == BillItem.bill_id)
            .where(BillItem.draft_id.in_(all_draft_ids))
            .order_by(Bill.created_at.asc(), Bill.id.asc(), BillItem.id.asc())
        ).all()
    )

    draft_to_bill: dict[str, dict[str, Any]] = {}
    for draft_id, bill_id, bill_no in bill_rows:
        if draft_id and draft_id not in draft_to_bill:
            draft_to_bill[draft_id] = {
                "billed": True,
                "linked_bill_id": bill_id,
                "linked_bill_no": bill_no or bill_id,
            }

    visibility_map: dict[str, dict[str, Any]] = {}
    for task_id, draft_ids in task_to_draft_ids.items():
        for draft_id in draft_ids:
            bill_visibility = draft_to_bill.get(draft_id)
            if bill_visibility:
                visibility_map[task_id] = bill_visibility
                break
    return visibility_map


def _build_grant_fee_task_case_no_map(
    db: Session,
    *,
    tasks: list[T_GrantFeeTask],
) -> dict[str, str]:
    case_ids = sorted({str(task.case_id) for task in tasks if str(task.case_id or "").strip()})
    if not case_ids:
        return {}
    rows = db.execute(select(Case.id, Case.case_no).where(Case.id.in_(case_ids))).all()
    return {case_id: case_no for case_id, case_no in rows if case_no}


def _serialize_grant_fee_task_list_item(
    task: T_GrantFeeTask,
    *,
    state: str,
    case_no: str | None,
    bill_visibility: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "case_no": case_no,
        "status": state,
        "due_date": task.due_date,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "gov_fee_amt": task.gov_fee_amt,
        "service_fee_amt": task.service_fee_amt,
        "currency": task.currency,
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "notify_count": int(task.notify_count or 0),
        "is_overdue": bool(task.is_overdue),
        "billed": bool(bill_visibility.get("billed")),
        "linked_bill_id": bill_visibility.get("linked_bill_id"),
        "linked_bill_no": bill_visibility.get("linked_bill_no"),
    }


def _serialize_grant_fee_draft_generation_result(
    task: T_GrantFeeTask,
    *,
    draft: FeeDraft,
    state: str,
    reused: bool,
    item_count: int | None = None,
    amount: Decimal | None = None,
) -> dict[str, Any]:
    draft_amount = amount if amount is not None else Decimal(draft.amount or 0)
    if item_count is None:
        item_count = 0

    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "draft_id": draft.id,
        "draft_type": draft.draft_type,
        "state": state,
        "draft_generated": bool(task.draft_generated),
        "currency": draft.currency,
        "amount": draft_amount,
        "item_count": item_count,
        "reused": reused,
    }


def _validate_grant_fee_notice_task(task: T_GrantFeeTask, *, state: str) -> None:
    if state not in _NOTICE_ALLOWED_STATES or task.draft_generated:
        raise_business_error(
            "GRANT_FEE_NOTICE_STATE_INVALID",
            "Grant fee task is not eligible for notice generation",
            details={
                "task_id": task.id,
                "state": state,
                "required_states": list(_NOTICE_ALLOWED_STATES),
                "draft_generated": bool(task.draft_generated),
            },
            status_code=400,
        )

    instruction = (task.client_instruction or "NONE").strip().upper() or "NONE"
    if instruction != "NONE":
        raise_business_error(
            "GRANT_FEE_NOTICE_STATE_INVALID",
            "Grant fee task already has client instruction",
            details={
                "task_id": task.id,
                "client_instruction": instruction,
                "required_instruction": "NONE",
            },
            status_code=400,
        )


def _generate_grant_fee_notice_document(
    db: Session,
    *,
    task: T_GrantFeeTask,
    doc_template: DocTemplate,
    template_path: str,
    renderer: TemplateRenderer,
) -> dict[str, Any]:
    next_notify_count = int(task.notify_count or 0) + 1
    document = Document(
        id=str(uuid4()),
        case_id=task.case_id,
        doc_template_id=doc_template.id,
        direction="OUT",
        doc_date=date.today(),
        title="授权费通知函",
        extra_data=json.dumps({"grant_fee_task_id": task.id}, ensure_ascii=False),
    )
    db.add(document)
    db.flush()

    render_context = {
        **build_document_template_render_context(db, document=document),
        "grant_fee_task": {
            "id": task.id,
            "case_id": task.case_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "gov_fee_amt": str(Decimal(task.gov_fee_amt or 0)),
            "service_fee_amt": str(Decimal(task.service_fee_amt or 0)),
            "currency": task.currency,
            "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
            "notify_count": next_notify_count,
            "notice_sent": True,
            "is_overdue": bool(task.is_overdue),
        },
    }
    try:
        rendered_bytes = renderer.render_template_docx_bytes(
            template_path=template_path,
            context=render_context,
        )
    except Exception as exc:
        raise_business_error(
            "GRANT_FEE_NOTICE_RENDER_FAILED",
            "Grant fee notice render failed",
            details={"task_id": task.id, "error": str(exc)},
            status_code=409,
        )

    attachment = persist_generated_attachment(
        db,
        document_id=document.id,
        file_name=_grant_fee_notice_file_name(task),
        content_bytes=rendered_bytes,
        storage_dir=str(_backend_storage_dir()),
        mime_type=DOCX_MIME_TYPE,
        commit=False,
    )

    task.notice_sent = True
    task.notify_count = next_notify_count
    db.flush()
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "document_id": document.id,
        "attachment_id": attachment.id,
        "file_name": attachment.file_name,
        "notify_count": int(task.notify_count or 0),
    }


def _grant_fee_notice_file_name(task: T_GrantFeeTask) -> str:
    suffix = (str(task.case_id or "").strip() or str(task.id or "").strip() or "task")[:24]
    return f"授权费通知函-{suffix}.docx"
