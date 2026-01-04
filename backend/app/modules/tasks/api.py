from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.common.doc_render.renderer import DocxRenderer
from app.db.session import get_db
from app.models.system_param import SystemParam
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.doc_render_task_sheet_context import TaskSheetContextBuilder
from app.modules.tasks.models import Task

router = APIRouter()


@router.get("/tasks")
def get_tasks(
    status: str | None = Query(default=None),
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    worker_id: str | None = Query(default=None),
    supervisor_id: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if due_from:
        query = query.filter(Task.due_date >= due_from)
    if due_to:
        query = query.filter(Task.due_date <= due_to)
    if worker_id:
        query = query.filter(Task.worker_id == worker_id)
    if supervisor_id:
        query = query.filter(Task.supervisor_id == supervisor_id)
    if case_id:
        query = query.filter(Task.case_id == case_id)

    total = query.count()
    tasks = (
        query.order_by(Task.due_date.asc()).offset((page - 1) * page_size).limit(page_size).all()
    )

    items = [
        {
            "id": task.id,
            "case_id": task.case_id,
            "document_id": task.document_id,
            "task_template_id": task.task_template_id,
        }
        for task in tasks
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/tasks/today")
def get_tasks_today(
    as_role: str = Query(alias="as"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if as_role not in {"worker", "supervisor"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid role")

    query = db.query(Task).filter(Task.due_date == date.today())
    if as_role == "worker":
        query = query.filter(Task.worker_id.isnot(None))
    else:
        query = query.filter(Task.supervisor_id.isnot(None))

    total = query.count()
    tasks = (
        query.order_by(Task.due_date.asc()).offset((page - 1) * page_size).limit(page_size).all()
    )

    items = [
        {
            "id": task.id,
            "case_id": task.case_id,
            "document_id": task.document_id,
            "task_template_id": task.task_template_id,
        }
        for task in tasks
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Task.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case_id = payload.get("case_id")
    if not case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="case_id is required")

    task = Task(
        id=str(uuid4()),
        case_id=case_id,
        document_id=payload.get("document_id"),
        task_template_id=payload.get("task_template_id"),
        title=payload.get("title"),
        base_date=payload.get("base_date"),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "case_id": task.case_id,
        "document_id": task.document_id,
        "task_template_id": task.task_template_id,
        "title": task.title,
        "base_date": str(task.base_date) if task.base_date else None,
    }


@router.post("/tasks/{task_id}/close")
def close_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = "DONE"
    task.done_at = datetime.utcnow()
    db.commit()

    return {"status": "ok"}


@router.post("/tasks/{task_id}/reopen")
def reopen_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = "OPEN"
    task.done_at = None
    db.commit()

    return {"status": "ok"}


@router.post("/tasks/{task_id}/cancel")
def cancel_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = "CANCELLED"
    task.done_at = None
    db.commit()

    return {"status": "ok"}


@router.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Task.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if "case_id" in payload:
        task.case_id = payload.get("case_id")
    if "document_id" in payload:
        task.document_id = payload.get("document_id")
    if "task_template_id" in payload:
        task.task_template_id = payload.get("task_template_id")
    if "title" in payload:
        task.title = payload.get("title")
    if "base_date" in payload:
        task.base_date = payload.get("base_date")

    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "case_id": task.case_id,
        "document_id": task.document_id,
        "task_template_id": task.task_template_id,
        "title": task.title,
        "base_date": str(task.base_date) if task.base_date else None,
    }


@router.get("/tasks/{task_id}/print")
def print_task_sheet(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> Response:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    case = None
    client = None
    if task.case_id:
        case = db.query(Case).filter(Case.id == task.case_id).first()
        if case and case.client_id:
            client = db.query(Client).filter(Client.id == case.client_id).first()

    param = (
        db.query(SystemParam).filter(SystemParam.param_key == "task_sheet_template_path").first()
    )
    template_path = param.param_value if param else None
    if not template_path:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task sheet template not configured",
        )

    context = TaskSheetContextBuilder().build(task, case, client)
    renderer = DocxRenderer()
    try:
        docx_bytes = renderer.render_docx_bytes(template_path, context)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template file missing",
        ) from exc

    headers = {
        "Content-Disposition": f'attachment; filename="task_{task.id}.docx"',
    }
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.get("/tasks/{task_id}")
def get_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {
        "id": task.id,
        "case_id": task.case_id,
        "document_id": task.document_id,
        "task_template_id": task.task_template_id,
        "title": task.title,
        "base_date": str(task.base_date) if task.base_date else None,
    }
