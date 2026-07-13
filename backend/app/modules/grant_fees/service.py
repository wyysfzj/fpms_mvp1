from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.billing.models import Bill, BillItem
from app.modules.cases.models import Case
from app.modules.cases.service import has_required_granted_status_fields
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.extra_data import DocumentExtraDataError, parse_document_extra_data
from app.modules.documents.models import DocTemplate, Document
from app.modules.documents.schemas import DocumentCreateIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.documents.service import (
    _backend_storage_dir,
    _merge_document_create_extra_data,
    build_document_template_render_context,
    create_document,
    persist_generated_attachment,
    resolve_document_template_render_source,
)
from app.modules.fees.models import FeeDraft, FeeItem, FeeRate, T_GrantFeeTask
from app.modules.fees.service import (
    fee_rate_effective_on_conditions,
    fee_rate_source_enabled_condition,
    recalc_fee_draft_totals,
)
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
_ZERO = Decimal("0")
_MONEY_QUANT = Decimal("0.01")
_SQLITE_LOCK_RETRY_ATTEMPTS = 10
_SQLITE_LOCK_RETRY_DELAY_SECONDS = 0.05

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
_GRANT_FEE_DEADLINE_PREVIEW_FIELDS = {
    "trigger_rule": "收到办理登记手续通知书/授权通知书",
    "deadline_rule": "以办理登记手续通知书/授权通知书载明期限为准；当前按授权费任务到期日展示",
    "fee_basis": "授权阶段官费按授权费任务金额展示；如无授权费率则回退授权当年年费规则",
    "fee_node_explanation": "授权费用节点：客户确认缴费后生成官费草单，缴费登记后进入授权后年费监视。",
}


@dataclass(frozen=True, slots=True)
class GrantFeeTaskReplacementResult:
    document: Document
    replacement_task: T_GrantFeeTask
    superseded_task_id: str
    reused: bool


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


def _money_amount(value: Any) -> Decimal:
    if value is None or value == "":
        return _ZERO
    try:
        return Decimal(str(value)).quantize(_MONEY_QUANT)
    except (InvalidOperation, ValueError):
        return _ZERO


def _tiered_rate_amount(rate: FeeRate, year_no: int | None) -> Decimal:
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


def _select_matching_gov_rate(
    db: Session,
    *,
    rate_group: str,
    currency: str,
    patent_category: str | None,
) -> FeeRate | None:
    normalized_patent_category = (patent_category or "").strip() or None
    conditions = [
        FeeRate.enabled.is_(True),
        FeeRate.fee_type == "GOV",
        FeeRate.currency == currency,
        FeeRate.rate_group == rate_group,
        fee_rate_source_enabled_condition(),
        *fee_rate_effective_on_conditions(date.today()),
    ]
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
        return None

    if normalized_patent_category:
        for rate in rates:
            if rate.patent_category == normalized_patent_category:
                return rate
        for rate in rates:
            if not rate.patent_category:
                return rate
        return None

    return rates[0]


def _resolve_grant_task_gov_amount(db: Session, *, case: Case | None, currency: str) -> Decimal:
    if case is None:
        return _ZERO

    grant_rate = _select_matching_gov_rate(
        db,
        rate_group="GRANT",
        currency=currency,
        patent_category=case.patent_category,
    )
    if grant_rate is not None:
        return _tiered_rate_amount(grant_rate, None)

    annuity_rate = _select_matching_gov_rate(
        db,
        rate_group="ANNUITY",
        currency=currency,
        patent_category=case.patent_category,
    )
    return _tiered_rate_amount(annuity_rate, case.first_annuity_year) if annuity_rate else _ZERO


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


def _derive_grant_fee_task_lineage_status(task: T_GrantFeeTask) -> str:
    if task.superseded_by_task_id:
        return "SUPERSEDED"
    if task.source_document_id and task.deadline_source and task.deadline_confirmed_at:
        return "CONFIRMED"
    return "LEGACY_UNVERIFIED"


def _require_grant_fee_task_actionable(task: T_GrantFeeTask) -> str:
    lineage_status = _derive_grant_fee_task_lineage_status(task)
    if lineage_status != "CONFIRMED":
        raise_business_error(
            "GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE",
            "Grant fee task lineage is not actionable",
            details={"task_id": task.id, "lineage_status": lineage_status},
            status_code=409,
        )
    return lineage_status


def _case_has_required_grant_fields(case: Case) -> bool:
    return has_required_granted_status_fields(case)


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
    normalized_action = _normalize_action(action)
    _require_grant_fee_task_actionable(task)

    current_state = derive_grant_fee_task_state(task)
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


def _raise_active_grant_source_conflict(
    active_task: T_GrantFeeTask,
    *,
    requested_source_document_id: str,
) -> None:
    raise_business_error(
        "GRANT_FEE_TASK_ACTIVE_SOURCE_CONFLICT",
        "A different active grant notice source requires explicit replacement",
        details={
            "task_id": active_task.id,
            "active_source_document_id": active_task.source_document_id,
            "requested_source_document_id": requested_source_document_id,
        },
        status_code=409,
    )


def _ensure_sqlite_grant_write_transaction(db: Session) -> None:
    connection = db.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if driver_connection.in_transaction:
        return

    for attempt in range(_SQLITE_LOCK_RETRY_ATTEMPTS + 1):
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            return
        except OperationalError as exc:
            message = str(exc).lower()
            if "database is locked" not in message and "database is busy" not in message:
                raise
            if attempt == _SQLITE_LOCK_RETRY_ATTEMPTS:
                if not driver_connection.in_transaction:
                    connection.exec_driver_sql("BEGIN")
                raise_business_error(
                    "GRANT_FEE_TASK_CONCURRENCY_CONFLICT",
                    "Grant fee task creation is busy; retry the request",
                    status_code=409,
                )
            time.sleep(_SQLITE_LOCK_RETRY_DELAY_SECONDS)


def ensure_grant_fee_task_for_notice_document(
    db: Session,
    *,
    document: Document,
    template: DocTemplate,
    superseding_task_id: str | None = None,
) -> T_GrantFeeTask | None:
    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "GRANT_NOTICE"
        or semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        or semantics.fee_trigger != GRANT_FEE_DRAFT_TYPE
    ):
        return None

    source_document_id = str(document.id or "").strip()
    case_id = str(document.case_id or "").strip()
    if not source_document_id or not case_id:
        raise_business_error(
            "GRANT_FEE_TASK_SOURCE_REQUIRED",
            "Grant fee task requires a persisted source document and case",
            details={
                "source_document_id": source_document_id or None,
                "case_id": case_id or None,
            },
            status_code=409,
        )

    try:
        deadline = parse_document_extra_data(document.extra_data)
    except DocumentExtraDataError as exc:
        raise_business_error(
            "GRANT_OFFICIAL_DUE_DATE_CONFLICT",
            "Executable grant notice requires a consistent official due date tuple",
            details={"field": exc.field, "reason": exc.reason},
            status_code=409,
        )
    if (
        deadline.official_due_date_status != "CONFIRMED"
        or deadline.official_due_date is None
        or deadline.official_due_date_source is None
    ):
        raise_business_error(
            "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
            "Executable grant notice requires a confirmed explicit official due date",
            details={"status": deadline.official_due_date_status},
            status_code=409,
        )

    _ensure_sqlite_grant_write_transaction(db)

    same_source_task = (
        db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.source_document_id == source_document_id)
        )
        .scalars()
        .one_or_none()
    )
    if same_source_task is not None:
        if same_source_task.case_id != case_id:
            raise_business_error(
                "GRANT_FEE_TASK_SOURCE_IDENTITY_CONFLICT",
                "Grant fee task source belongs to a different case",
                details={
                    "task_id": same_source_task.id,
                    "source_document_id": source_document_id,
                    "task_case_id": same_source_task.case_id,
                    "source_case_id": case_id,
                },
                status_code=409,
            )
        return same_source_task

    active_tasks = list(
        db.execute(
            select(T_GrantFeeTask)
            .where(
                T_GrantFeeTask.case_id == case_id,
                T_GrantFeeTask.superseded_by_task_id.is_(None),
            )
            .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
        )
        .scalars()
        .all()
    )
    conflicting_active_tasks = [task for task in active_tasks if task.id != superseding_task_id]
    if conflicting_active_tasks:
        _raise_active_grant_source_conflict(
            conflicting_active_tasks[0],
            requested_source_document_id=source_document_id,
        )

    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    currency = "CNY"
    task = T_GrantFeeTask(
        case_id=case_id,
        source_document_id=source_document_id,
        due_date=deadline.official_due_date,
        deadline_source=deadline.official_due_date_source,
        deadline_confirmed_at=datetime.now(),
        gov_fee_amt=_resolve_grant_task_gov_amount(db, case=case, currency=currency),
        service_fee_amt=0,
        currency=currency,
        client_instruction="NONE",
        notify_count=0,
        draft_generated=False,
        notice_sent=False,
        is_overdue=False,
    )
    try:
        with db.begin_nested():
            db.add(task)
            db.flush()
            competing_tasks = list(
                db.execute(
                    select(T_GrantFeeTask)
                    .where(
                        T_GrantFeeTask.case_id == case_id,
                        T_GrantFeeTask.superseded_by_task_id.is_(None),
                        T_GrantFeeTask.id != task.id,
                        T_GrantFeeTask.id != superseding_task_id,
                    )
                    .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
                )
                .scalars()
                .all()
            )
            if competing_tasks:
                _raise_active_grant_source_conflict(
                    competing_tasks[0],
                    requested_source_document_id=source_document_id,
                )
    except IntegrityError:
        winner = (
            db.execute(
                select(T_GrantFeeTask).where(
                    T_GrantFeeTask.source_document_id == source_document_id
                )
            )
            .scalars()
            .one_or_none()
        )
        if winner is not None and winner.case_id == case_id:
            return winner
        competing_task = (
            db.execute(
                select(T_GrantFeeTask)
                .where(
                    T_GrantFeeTask.case_id == case_id,
                    T_GrantFeeTask.superseded_by_task_id.is_(None),
                )
                .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
            )
            .scalars()
            .first()
        )
        if competing_task is not None:
            _raise_active_grant_source_conflict(
                competing_task,
                requested_source_document_id=source_document_id,
            )
        raise_business_error(
            "GRANT_FEE_TASK_SOURCE_IDENTITY_CONFLICT",
            "Grant fee task source identity conflicted during creation",
            details={"source_document_id": source_document_id, "case_id": case_id},
            status_code=409,
        )
    return task


def _normalize_replacement_text(
    value: str | None,
    *,
    field: str,
    max_length: int | None = None,
) -> str:
    normalized = str(value or "").strip()
    if not normalized or (max_length is not None and len(normalized) > max_length):
        raise_business_error(
            "GRANT_REPLACEMENT_INVALID",
            f"{field} is required and must use the supported length",
            details={"field": field, "max_length": max_length},
            status_code=400,
        )
    return normalized


def _validate_replacement_template(template: DocTemplate | None) -> DocTemplate:
    if template is None:
        raise_business_error(
            "GRANT_REPLACEMENT_TEMPLATE_INVALID",
            "Replacement notice requires an executable grant template",
            status_code=409,
        )
    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "GRANT_NOTICE"
        or semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        or semantics.fee_trigger != GRANT_FEE_DRAFT_TYPE
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_TEMPLATE_INVALID",
            "Replacement notice requires executable grant semantics",
            details={"template_id": template.id, "template_code": template.code},
            status_code=409,
        )
    return template


def _validate_replacement_document_shape(
    *,
    old_task: T_GrantFeeTask,
    replacement_document: DocumentCreateIn,
) -> None:
    direction = getattr(replacement_document.direction, "value", replacement_document.direction)
    if (
        replacement_document.case_id != old_task.case_id
        or direction != DocumentDirection.IN.value
        or replacement_document.reply_to_id is not None
        or not str(replacement_document.title or "").strip()
        or not str(replacement_document.ref_no or "").strip()
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_DOCUMENT_INVALID",
            "Replacement notice must be an incoming document for the old task case",
            details={
                "task_case_id": old_task.case_id,
                "document_case_id": replacement_document.case_id,
                "direction": direction,
                "reply_to_id": replacement_document.reply_to_id,
                "title": replacement_document.title,
                "ref_no": replacement_document.ref_no,
            },
            status_code=400,
        )


def _replacement_document_matches(
    document: Document,
    *,
    replacement_document: DocumentCreateIn,
    expected_extra_data: str | None,
) -> bool:
    direction = getattr(replacement_document.direction, "value", replacement_document.direction)
    doc_type = getattr(replacement_document.doc_type, "value", replacement_document.doc_type)
    return (
        document.case_id == replacement_document.case_id
        and document.doc_template_id == replacement_document.doc_template_id
        and document.doc_type == doc_type
        and document.direction == direction
        and document.doc_date == replacement_document.doc_date
        and document.title == replacement_document.title
        and document.ref_no == replacement_document.ref_no
        and document.extra_data == expected_extra_data
        and document.reply_to_id == replacement_document.reply_to_id
    )


def _existing_replacement_result(
    db: Session,
    *,
    old_task: T_GrantFeeTask,
    request_key: str,
    reason: str,
    replacement_document: DocumentCreateIn,
    expected_extra_data: str | None,
) -> GrantFeeTaskReplacementResult | None:
    request_owner = db.execute(
        select(T_GrantFeeTask).where(T_GrantFeeTask.supersede_request_key == request_key)
    ).scalar_one_or_none()
    if request_owner is None:
        return None
    if request_owner.id != old_task.id or request_owner.superseded_by_task_id is None:
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request key is already bound to a different operation",
            details={"request_key": request_key},
            status_code=409,
        )
    replacement_task = db.get(T_GrantFeeTask, request_owner.superseded_by_task_id)
    replacement_source = (
        db.get(Document, replacement_task.source_document_id)
        if replacement_task is not None and replacement_task.source_document_id
        else None
    )
    if (
        request_owner.supersede_reason != reason
        or replacement_task is None
        or replacement_task.case_id != old_task.case_id
        or replacement_source is None
        or not _replacement_document_matches(
            replacement_source,
            replacement_document=replacement_document,
            expected_extra_data=expected_extra_data,
        )
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request key conflicts with the existing payload",
            details={"request_key": request_key, "task_id": old_task.id},
            status_code=409,
        )
    return GrantFeeTaskReplacementResult(
        document=replacement_source,
        replacement_task=replacement_task,
        superseded_task_id=old_task.id,
        reused=True,
    )


def replace_grant_fee_task_with_notice(
    db: Session,
    *,
    task_id: str,
    request_key: str,
    reason: str,
    replacement_document: DocumentCreateIn,
    actor_id: str,
) -> GrantFeeTaskReplacementResult:
    normalized_request_key = _normalize_replacement_text(
        request_key,
        field="request_key",
        max_length=64,
    )
    normalized_reason = _normalize_replacement_text(reason, field="reason")
    normalized_actor_id = _normalize_replacement_text(
        actor_id,
        field="actor_id",
        max_length=36,
    )

    _ensure_sqlite_grant_write_transaction(db)
    try:
        old_task = _load_grant_fee_task(db, task_id=task_id)
        _validate_replacement_document_shape(
            old_task=old_task,
            replacement_document=replacement_document,
        )
        if (
            not old_task.source_document_id
            or not old_task.deadline_source
            or old_task.deadline_confirmed_at is None
        ):
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Only an active grant task with confirmed source lineage can be replaced",
                details={"task_id": old_task.id},
                status_code=409,
            )
        source_document = db.get(Document, old_task.source_document_id)
        if source_document is None or source_document.case_id != old_task.case_id:
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Old grant task source lineage is missing or inconsistent",
                details={"task_id": old_task.id},
                status_code=409,
            )

        expected_extra_data = _merge_document_create_extra_data(replacement_document)
        expected_deadline = parse_document_extra_data(expected_extra_data)
        if (
            expected_deadline.official_due_date_status != "CONFIRMED"
            or expected_deadline.official_due_date is None
            or expected_deadline.official_due_date_source is None
        ):
            raise_business_error(
                "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
                "Replacement grant notice requires a confirmed official due date",
                status_code=409,
            )

        existing = _existing_replacement_result(
            db,
            old_task=old_task,
            request_key=normalized_request_key,
            reason=normalized_reason,
            replacement_document=replacement_document,
            expected_extra_data=expected_extra_data,
        )
        if existing is not None:
            db.commit()
            return existing
        if old_task.superseded_by_task_id is not None or old_task.supersede_request_key is not None:
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Grant fee task has already been superseded",
                details={"task_id": old_task.id},
                status_code=409,
            )

        template = _validate_replacement_template(
            db.get(DocTemplate, replacement_document.doc_template_id)
            if replacement_document.doc_template_id
            else None
        )

        replacement_source = create_document(db, replacement_document)
        replacement_task = ensure_grant_fee_task_for_notice_document(
            db,
            document=replacement_source,
            template=template,
            superseding_task_id=old_task.id,
        )
        if replacement_task is None:
            raise_business_error(
                "GRANT_REPLACEMENT_TEMPLATE_INVALID",
                "Replacement notice did not create a grant fee task",
                status_code=409,
            )

        old_task.superseded_by_task_id = replacement_task.id
        old_task.supersede_reason = normalized_reason
        old_task.superseded_at = datetime.now()
        old_task.superseded_by = normalized_actor_id
        old_task.supersede_request_key = normalized_request_key
        db.flush()
        db.commit()
        db.refresh(replacement_source)
        db.refresh(replacement_task)
        return GrantFeeTaskReplacementResult(
            document=replacement_source,
            replacement_task=replacement_task,
            superseded_task_id=old_task.id,
            reused=False,
        )
    except IntegrityError:
        db.rollback()
        old_task = db.get(T_GrantFeeTask, task_id)
        if old_task is not None:
            existing = _existing_replacement_result(
                db,
                old_task=old_task,
                request_key=normalized_request_key,
                reason=normalized_reason,
                replacement_document=replacement_document,
                expected_extra_data=_merge_document_create_extra_data(replacement_document),
            )
            if existing is not None:
                return existing
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request conflicted during atomic creation",
            details={"request_key": normalized_request_key},
            status_code=409,
        )
    except Exception:
        db.rollback()
        raise


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

    for task_id in unique_task_ids:
        _require_grant_fee_task_actionable(task_by_id[task_id])

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

    for task_id in unique_task_ids:
        _require_grant_fee_task_actionable(task_by_id[task_id])

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
    _require_grant_fee_task_actionable(task)
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

    gov_amount = _money_amount(task.gov_fee_amt)
    service_amount = _ZERO
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
            "fee_name": "授权官费",
            "fee_type": "GOV",
            "amount": gov_amount,
        }
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
    lineage_status = _derive_grant_fee_task_lineage_status(task)
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "state": state,
        "lineage_status": lineage_status,
        "source_document_id": task.source_document_id,
        "deadline_source": task.deadline_source,
        "deadline_confirmed_at": task.deadline_confirmed_at,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "notify_count": int(task.notify_count or 0),
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "is_overdue": bool(task.is_overdue),
        "allowed_actions": list(_STATE_ALLOWED_ACTIONS[state])
        if lineage_status == "CONFIRMED"
        else [],
        **_GRANT_FEE_DEADLINE_PREVIEW_FIELDS,
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
        "lineage_status": _derive_grant_fee_task_lineage_status(task),
        "source_document_id": task.source_document_id,
        "deadline_source": task.deadline_source,
        "deadline_confirmed_at": task.deadline_confirmed_at,
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
        **_GRANT_FEE_DEADLINE_PREVIEW_FIELDS,
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
    draft_amount = amount if amount is not None else _money_amount(draft.amount)
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
