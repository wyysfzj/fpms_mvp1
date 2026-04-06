from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, literal, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.enums import TaskAction, TaskStatus, TaskTodayAs
from app.modules.tasks.models import Task, TaskLog, TaskTemplate
from app.modules.tasks.schemas import (
    TaskCreateIn,
    TaskTemplateCreateIn,
    TaskTemplateUpdateIn,
    TaskUpdateIn,
)

SPECIAL_SEARCH_TASK_CODES = {"APPLY_FEE_LIMIT", "EXAM_REQUEST_LIMIT"}


def _validate_transition(from_status: str, to_status: str) -> None:
    allowed = {
        TaskStatus.OPEN: {TaskStatus.DONE, TaskStatus.CANCELLED},
        TaskStatus.DONE: {TaskStatus.OPEN},
        TaskStatus.CANCELLED: set(),
    }
    try:
        from_key = TaskStatus(from_status)
        to_key = TaskStatus(to_status)
    except ValueError:
        raise_business_error(
            "TASK_INVALID_TRANSITION",
            "Invalid task status transition",
            status_code=400,
        )
    if to_key not in allowed.get(from_key, set()):
        raise_business_error(
            "TASK_INVALID_TRANSITION",
            "Invalid task status transition",
            status_code=400,
        )


def _create_task_log(
    db: Session,
    *,
    task_id: str,
    action: TaskAction,
    from_status: str | None,
    to_status: str | None,
    remark: str | None,
) -> None:
    db.add(
        TaskLog(
            id=str(uuid4()),
            task_id=task_id,
            action=action.value,
            from_status=from_status,
            to_status=to_status,
            remark=remark,
        )
    )


def list_tasks(
    db: Session,
    *,
    filters: dict[str, Any],
    actor_id: str | None,
    as_role: TaskTodayAs | None,
    page: int,
    page_size: int,
) -> tuple[list[Task], int]:
    stmt = select(Task)

    status = filters.get("status")
    case_id = filters.get("case_id")
    worker_id = filters.get("worker_id")
    supervisor_id = filters.get("supervisor_id")
    due_from: date | None = filters.get("due_from")
    due_to: date | None = filters.get("due_to")
    client_id = filters.get("client_id")

    if as_role == TaskTodayAs.WORKER and actor_id:
        stmt = stmt.where(Task.worker_id == actor_id)
    elif as_role == TaskTodayAs.SUPERVISOR and actor_id:
        stmt = stmt.where(Task.supervisor_id == actor_id)

    if status:
        stmt = stmt.where(Task.status == status)
    if case_id:
        stmt = stmt.where(Task.case_id == case_id)
    if worker_id:
        stmt = stmt.where(Task.worker_id == worker_id)
    if supervisor_id:
        stmt = stmt.where(Task.supervisor_id == supervisor_id)
    if due_from:
        stmt = stmt.where(Task.due_date >= due_from)
    if due_to:
        stmt = stmt.where(Task.due_date <= due_to)
    if client_id:
        stmt = stmt.join(Case, Task.case_id == Case.id).where(Case.client_id == client_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        stmt.order_by(Task.due_date.asc(), Task.created_at.desc()).offset(offset).limit(page_size)
    )
    items = db.execute(stmt).scalars().all()
    return items, total


def list_tasks_for_export(
    db: Session,
    *,
    filters: dict[str, Any],
    actor_id: str | None,
    as_role: TaskTodayAs | None,
) -> list[Task]:
    stmt = select(Task)

    status = filters.get("status")
    case_id = filters.get("case_id")
    worker_id = filters.get("worker_id")
    supervisor_id = filters.get("supervisor_id")
    due_from: date | None = filters.get("due_from")
    due_to: date | None = filters.get("due_to")
    client_id = filters.get("client_id")

    if as_role == TaskTodayAs.WORKER and actor_id:
        stmt = stmt.where(Task.worker_id == actor_id)
    elif as_role == TaskTodayAs.SUPERVISOR and actor_id:
        stmt = stmt.where(Task.supervisor_id == actor_id)

    if status:
        stmt = stmt.where(Task.status == status)
    if case_id:
        stmt = stmt.where(Task.case_id == case_id)
    if worker_id:
        stmt = stmt.where(Task.worker_id == worker_id)
    if supervisor_id:
        stmt = stmt.where(Task.supervisor_id == supervisor_id)
    if due_from:
        stmt = stmt.where(Task.due_date >= due_from)
    if due_to:
        stmt = stmt.where(Task.due_date <= due_to)
    if client_id:
        stmt = stmt.join(Case, Task.case_id == Case.id).where(Case.client_id == client_id)

    return list(
        db.execute(stmt.order_by(Task.due_date.asc(), Task.created_at.desc())).scalars().all()
    )


def get_task(db: Session, *, task_id: str) -> Task:
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        raise_business_error("TASK_NOT_FOUND", "Task not found", status_code=404)
    return task


def create_task(db: Session, *, data: TaskCreateIn, actor_id: str | None) -> Task:
    if data.case_id:
        case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
        if not case:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if data.document_id:
        document = db.execute(
            select(Document).where(Document.id == data.document_id)
        ).scalar_one_or_none()
        if not document:
            raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    if data.task_template_id:
        template = db.execute(
            select(TaskTemplate).where(TaskTemplate.id == data.task_template_id)
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "TASK_TEMPLATE_NOT_FOUND",
                "Task template not found",
                status_code=404,
            )
        if getattr(template, "enabled", True) is False:
            raise_business_error(
                "TASK_TEMPLATE_DISABLED",
                "Task template disabled",
                status_code=400,
            )

    task = Task(
        id=str(uuid4()),
        case_id=data.case_id,
        document_id=data.document_id,
        task_template_id=data.task_template_id,
        title=data.title,
        base_date=data.base_date,
        due_date=data.due_date,
        internal_due_date=data.internal_due_date,
        worker_id=data.worker_id,
        supervisor_id=data.supervisor_id,
        status=TaskStatus.OPEN,
    )
    db.add(task)
    _create_task_log(
        db,
        task_id=task.id,
        action=TaskAction.CREATE,
        from_status=None,
        to_status=TaskStatus.OPEN.value,
        remark=getattr(data, "remark", None),
    )
    db.commit()
    db.refresh(task)
    return task


def update_task(
    db: Session,
    *,
    task_id: str,
    data: TaskUpdateIn,
    actor_id: str | None,
) -> Task:
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        raise_business_error("TASK_NOT_FOUND", "Task not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)

    if "case_id" in updates and updates["case_id"]:
        case = db.execute(select(Case).where(Case.id == updates["case_id"])).scalar_one_or_none()
        if not case:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if "document_id" in updates and updates["document_id"]:
        document = db.execute(
            select(Document).where(Document.id == updates["document_id"])
        ).scalar_one_or_none()
        if not document:
            raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    if "task_template_id" in updates and updates["task_template_id"]:
        template = db.execute(
            select(TaskTemplate).where(TaskTemplate.id == updates["task_template_id"])
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "TASK_TEMPLATE_NOT_FOUND",
                "Task template not found",
                status_code=404,
            )
        if getattr(template, "enabled", True) is False:
            raise_business_error(
                "TASK_TEMPLATE_DISABLED",
                "Task template disabled",
                status_code=400,
            )

    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
) -> None:
    task = get_task(db, task_id=task_id)
    db.delete(task)
    db.commit()


def close_task(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
    remark: str | None = None,
) -> None:
    task = get_task(db, task_id=task_id)
    from_status = task.status
    _validate_transition(task.status, TaskStatus.DONE.value)
    task.status = TaskStatus.DONE.value
    task.done_at = datetime.utcnow()
    _create_task_log(
        db,
        task_id=task.id,
        action=TaskAction.CLOSE,
        from_status=from_status,
        to_status=TaskStatus.DONE.value,
        remark=remark,
    )
    db.commit()


def reopen_task(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
    remark: str | None = None,
) -> None:
    task = get_task(db, task_id=task_id)
    from_status = task.status
    _validate_transition(task.status, TaskStatus.OPEN.value)
    task.status = TaskStatus.OPEN.value
    task.done_at = None
    _create_task_log(
        db,
        task_id=task.id,
        action=TaskAction.REOPEN,
        from_status=from_status,
        to_status=TaskStatus.OPEN.value,
        remark=remark,
    )
    db.commit()


def cancel_task(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
    remark: str | None = None,
) -> None:
    task = get_task(db, task_id=task_id)
    from_status = task.status
    _validate_transition(task.status, TaskStatus.CANCELLED.value)
    task.status = TaskStatus.CANCELLED.value
    task.done_at = None
    _create_task_log(
        db,
        task_id=task.id,
        action=TaskAction.CANCEL,
        from_status=from_status,
        to_status=TaskStatus.CANCELLED.value,
        remark=remark,
    )
    db.commit()


def assign_task(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
    worker_id: str | None,
    supervisor_id: str | None,
    remark: str | None = None,
) -> None:
    if not worker_id and not supervisor_id:
        raise_business_error(
            "TASK_ASSIGNEE_REQUIRED",
            "worker_id or supervisor_id must be provided",
            status_code=400,
        )

    task = get_task(db, task_id=task_id)

    if worker_id:
        worker = db.execute(select(T_User).where(T_User.id == worker_id)).scalar_one_or_none()
        if not worker:
            raise_business_error("USER_NOT_FOUND", "User not found", status_code=404)
        task.worker_id = worker_id
    if supervisor_id:
        supervisor = db.execute(
            select(T_User).where(T_User.id == supervisor_id)
        ).scalar_one_or_none()
        if not supervisor:
            raise_business_error("USER_NOT_FOUND", "User not found", status_code=404)
        task.supervisor_id = supervisor_id

    _create_task_log(
        db,
        task_id=task.id,
        action=TaskAction.ASSIGN,
        from_status=task.status,
        to_status=task.status,
        remark=remark,
    )
    db.commit()


def list_tasks_today(
    db: Session,
    *,
    actor_id: str,
    as_role: TaskTodayAs,
) -> tuple[list[Task], int]:
    today = date.today()
    stmt = select(Task)

    if as_role == TaskTodayAs.WORKER:
        stmt = stmt.where(Task.worker_id == actor_id)
    else:
        stmt = stmt.where(Task.supervisor_id == actor_id)

    stmt = stmt.where(
        or_(
            Task.due_date == today,
            Task.internal_due_date == today,
        )
    )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.order_by(Task.due_date.asc(), Task.created_at.desc())).scalars().all()
    return items, total


def list_special_search_tasks(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int]:
    today = date.today()
    stmt = (
        select(
            TaskTemplate.code.label("task_code"),
            Task.id.label("task_id"),
            Task.case_id.label("case_id"),
            Case.case_no.label("case_no"),
            Client.name_cn.label("client_name"),
            Task.title.label("title"),
            Task.status.label("status"),
            Task.due_date.label("due_date"),
            # Task currently has no mapped persisted remark column; keep the
            # frozen projection field present and nullable.
            literal(None).label("remark"),
        )
        .join(TaskTemplate, Task.task_template_id == TaskTemplate.id)
        .join(Case, Task.case_id == Case.id)
        .outerjoin(Client, Case.client_id == Client.id)
        .where(TaskTemplate.code.in_(SPECIAL_SEARCH_TASK_CODES))
    )

    task_code = filters.get("task_code")
    status = filters.get("status")
    case_no = filters.get("case_no")
    client_name = filters.get("client_name")
    due_date_from: date | None = filters.get("due_date_from")
    due_date_to: date | None = filters.get("due_date_to")
    is_overdue = filters.get("is_overdue")

    if task_code:
        stmt = stmt.where(TaskTemplate.code == task_code)
    if status:
        stmt = stmt.where(Task.status == status)
    if case_no:
        stmt = stmt.where(func.lower(Case.case_no).like(f"%{case_no.strip().lower()}%"))
    if client_name:
        stmt = stmt.where(
            func.lower(func.coalesce(Client.name_cn, "")).like(f"%{client_name.strip().lower()}%")
        )
    if due_date_from:
        stmt = stmt.where(Task.due_date >= due_date_from)
    if due_date_to:
        stmt = stmt.where(Task.due_date <= due_date_to)
    if is_overdue is True:
        stmt = stmt.where(Task.due_date < today, Task.status != TaskStatus.DONE.value)
    elif is_overdue is False:
        stmt = stmt.where(
            or_(
                Task.due_date.is_(None),
                Task.due_date >= today,
                Task.status == TaskStatus.DONE.value,
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    rows = db.execute(
        stmt.order_by(Task.due_date.asc(), Task.created_at.desc(), Task.id.asc())
        .offset(offset)
        .limit(page_size)
    ).all()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row._mapping)
        due_date = item.get("due_date")
        status_value = item.get("status")
        item["title"] = item.get("title") or ""
        item["is_overdue"] = bool(
            due_date is not None and due_date < today and status_value != TaskStatus.DONE.value
        )
        items.append(item)
    return items, total


def list_special_search_tasks_for_output(
    db: Session,
    *,
    filters: dict[str, Any],
) -> list[dict[str, Any]]:
    today = date.today()
    stmt = (
        select(
            TaskTemplate.code.label("task_code"),
            Task.id.label("task_id"),
            Task.case_id.label("case_id"),
            Case.case_no.label("case_no"),
            Client.name_cn.label("client_name"),
            Task.title.label("title"),
            Task.status.label("status"),
            Task.due_date.label("due_date"),
            literal(None).label("remark"),
        )
        .join(TaskTemplate, Task.task_template_id == TaskTemplate.id)
        .join(Case, Task.case_id == Case.id)
        .outerjoin(Client, Case.client_id == Client.id)
        .where(TaskTemplate.code.in_(SPECIAL_SEARCH_TASK_CODES))
    )

    task_code = filters.get("task_code")
    status = filters.get("status")
    case_no = filters.get("case_no")
    client_name = filters.get("client_name")
    due_date_from: date | None = filters.get("due_date_from")
    due_date_to: date | None = filters.get("due_date_to")
    is_overdue = filters.get("is_overdue")

    if task_code:
        stmt = stmt.where(TaskTemplate.code == task_code)
    if status:
        stmt = stmt.where(Task.status == status)
    if case_no:
        stmt = stmt.where(func.lower(Case.case_no).like(f"%{case_no.strip().lower()}%"))
    if client_name:
        stmt = stmt.where(
            func.lower(func.coalesce(Client.name_cn, "")).like(f"%{client_name.strip().lower()}%")
        )
    if due_date_from:
        stmt = stmt.where(Task.due_date >= due_date_from)
    if due_date_to:
        stmt = stmt.where(Task.due_date <= due_date_to)
    if is_overdue is True:
        stmt = stmt.where(Task.due_date < today, Task.status != TaskStatus.DONE.value)
    elif is_overdue is False:
        stmt = stmt.where(
            or_(
                Task.due_date.is_(None),
                Task.due_date >= today,
                Task.status == TaskStatus.DONE.value,
            )
        )

    rows = db.execute(
        stmt.order_by(Task.due_date.asc(), Task.created_at.desc(), Task.id.asc())
    ).all()
    items: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row._mapping)
        due_date = item.get("due_date")
        status_value = item.get("status")
        item["title"] = item.get("title") or ""
        item["is_overdue"] = bool(
            due_date is not None and due_date < today and status_value != TaskStatus.DONE.value
        )
        items.append(item)
    return items


# ---------------------------------------------------------------------------
# TaskTemplate CRUD
# ---------------------------------------------------------------------------


def list_task_templates(db: Session, *, enabled_only: bool = False) -> list[TaskTemplate]:
    stmt = select(TaskTemplate)
    if enabled_only:
        stmt = stmt.where(TaskTemplate.enabled.is_(True))
    stmt = stmt.order_by(TaskTemplate.code.asc())
    return list(db.execute(stmt).scalars().all())


def _validate_default_supervisor(db: Session, supervisor_id: str | None) -> None:
    if supervisor_id is None:
        return
    supervisor = db.execute(select(T_User).where(T_User.id == supervisor_id)).scalar_one_or_none()
    if not supervisor:
        raise_business_error("USER_NOT_FOUND", "User not found", status_code=404)


def get_task_template(db: Session, *, template_id: str) -> TaskTemplate:
    tmpl = db.execute(
        select(TaskTemplate).where(TaskTemplate.id == template_id)
    ).scalar_one_or_none()
    if not tmpl:
        raise_business_error("TASK_TEMPLATE_NOT_FOUND", "Task template not found", status_code=404)
    return tmpl


def create_task_template(db: Session, *, data: TaskTemplateCreateIn) -> TaskTemplate:
    existing = db.execute(
        select(TaskTemplate).where(TaskTemplate.code == data.code)
    ).scalar_one_or_none()
    if existing:
        raise_business_error(
            "TASK_TEMPLATE_DUPLICATE_CODE",
            f"Task template with code '{data.code}' already exists",
            status_code=409,
        )
    updates = data.model_dump(exclude_unset=True)
    _validate_default_supervisor(db, updates.get("default_supervisor_id"))
    tmpl = TaskTemplate(
        id=str(uuid4()),
        code=data.code,
        name=data.name,
    )
    for field, value in updates.items():
        if field in {"code", "name"}:
            continue
        setattr(tmpl, field, value)
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


def update_task_template(
    db: Session, *, template_id: str, data: TaskTemplateUpdateIn
) -> TaskTemplate:
    tmpl = get_task_template(db, template_id=template_id)
    updates = data.model_dump(exclude_unset=True)
    _validate_default_supervisor(db, updates.get("default_supervisor_id"))
    for field, value in updates.items():
        setattr(tmpl, field, value)
    db.commit()
    db.refresh(tmpl)
    return tmpl


# ---------------------------------------------------------------------------
# TaskLog read
# ---------------------------------------------------------------------------


def list_task_logs(db: Session, *, task_id: str) -> list[TaskLog]:
    # Verify task exists
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        raise_business_error("TASK_NOT_FOUND", "Task not found", status_code=404)
    stmt = select(TaskLog).where(TaskLog.task_id == task_id).order_by(TaskLog.created_at.desc())
    return list(db.execute(stmt).scalars().all())
