from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.common.doc_render.renderer import DocxRenderer
from app.db.session import get_db
from app.models.system_param import SystemParam
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.doc_render_task_sheet_context import TaskSheetContextBuilder
from app.modules.tasks.enums import TaskTodayAs
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import (
    TaskActionIn,
    TaskActionOut,
    TaskAssignIn,
    TaskCreateIn,
    TaskListItemOut,
    TaskLogOut,
    TaskOut,
    TaskTemplateCreateIn,
    TaskTemplateOut,
    TaskTemplateUpdateIn,
    TaskUpdateIn,
)
from app.modules.tasks.service import assign_task as assign_task_service
from app.modules.tasks.service import cancel_task as cancel_task_service
from app.modules.tasks.service import close_task as close_task_service
from app.modules.tasks.service import create_task as create_task_service
from app.modules.tasks.service import create_task_template as create_task_template_service
from app.modules.tasks.service import delete_task as delete_task_service
from app.modules.tasks.service import get_task as get_task_service
from app.modules.tasks.service import list_task_logs as list_task_logs_service
from app.modules.tasks.service import list_task_templates as list_task_templates_service
from app.modules.tasks.service import list_tasks, list_tasks_today
from app.modules.tasks.service import reopen_task as reopen_task_service
from app.modules.tasks.service import update_task as update_task_service
from app.modules.tasks.service import update_task_template as update_task_template_service

router = APIRouter()


def _build_task_list_items(db: Session, tasks: list[Task]) -> list[TaskListItemOut]:
    case_ids = {task.case_id for task in tasks if task.case_id}
    case_no_map: dict[str, str] = {}
    case_client_map: dict[str, str | None] = {}
    if case_ids:
        cases = db.query(Case.id, Case.case_no, Case.client_id).filter(Case.id.in_(case_ids)).all()
        case_no_map = {case.id: case.case_no for case in cases}
        case_client_map = {case.id: case.client_id for case in cases}

    client_ids = {client_id for client_id in case_client_map.values() if client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {client.id: client.name_cn for client in clients}

    return [
        TaskListItemOut(
            id=task.id,
            case_id=task.case_id,
            case_no=case_no_map.get(task.case_id) if task.case_id else None,
            client_name=client_name_map.get(case_client_map.get(task.case_id, ""))
            if task.case_id
            else None,
            document_id=task.document_id,
            task_template_id=task.task_template_id,
            title=task.title or "",
            due_date=task.due_date,
            internal_due_date=task.internal_due_date,
            worker_id=task.worker_id,
            supervisor_id=task.supervisor_id,
            remark=getattr(task, "remark", None),
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


# ---------------------------------------------------------------------------
# TaskTemplate endpoints
# ---------------------------------------------------------------------------


@router.get("/task-templates", summary="List task templates")
def get_task_templates(
    enabled_only: bool = Query(default=False),
    _perm: None = Depends(require_perm("TaskTemplate.Read")),
    db: Session = Depends(get_db),
) -> list[TaskTemplateOut]:
    templates = list_task_templates_service(db, enabled_only=enabled_only)
    return [TaskTemplateOut.model_validate(t) for t in templates]


@router.post(
    "/task-templates",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskTemplateOut,
    summary="Create a task template",
)
def create_task_template(
    payload: TaskTemplateCreateIn,
    _perm: None = Depends(require_perm("TaskTemplate.Create")),
    db: Session = Depends(get_db),
) -> TaskTemplateOut:
    tmpl = create_task_template_service(db, data=payload)
    return TaskTemplateOut.model_validate(tmpl)


@router.put(
    "/task-templates/{template_id}",
    response_model=TaskTemplateOut,
    summary="Update a task template",
)
def update_task_template(
    template_id: str,
    payload: TaskTemplateUpdateIn,
    _perm: None = Depends(require_perm("TaskTemplate.Edit")),
    db: Session = Depends(get_db),
) -> TaskTemplateOut:
    tmpl = update_task_template_service(db, template_id=template_id, data=payload)
    return TaskTemplateOut.model_validate(tmpl)


# ---------------------------------------------------------------------------
# Task endpoints
# ---------------------------------------------------------------------------


@router.get("/tasks", summary="List tasks")
def get_tasks(
    status: str | None = Query(default=None),
    as_role: TaskTodayAs | None = Query(default=None, alias="as"),
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    worker_id: str | None = Query(default=None),
    supervisor_id: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Task.Read")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List tasks with filters and pagination.

    **Auth**: Bearer JWT
    **Permission**: Task.Read
    **Request example**:
    `GET /api/v1/tasks?page=1&page_size=20&status=OPEN&case_id=CASE_ID`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/tasks?page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of tasks
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    filters = {
        "status": status,
        "case_id": case_id,
        "worker_id": worker_id,
        "supervisor_id": supervisor_id,
        "due_from": due_from,
        "due_to": due_to,
        "client_id": client_id,
    }
    tasks, total = list_tasks(
        db,
        filters=filters,
        actor_id=current_user.id,
        as_role=as_role,
        page=page,
        page_size=page_size,
    )
    items = [item.model_dump(mode="json") for item in _build_task_list_items(db, tasks)]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/tasks/today", summary="List today's tasks for the current user")
def get_tasks_today(
    as_role: TaskTodayAs = Query(default=TaskTodayAs.WORKER, alias="as"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Task.Read")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    List tasks due today for the current user.

    **Auth**: Bearer JWT
    **Permission**: Task.Read
    **Request example**:
    `GET /api/v1/tasks/today?as=worker&page=1&page_size=20`
    **Curl example**:
    ```bash
    curl -s -X GET "http://localhost:8000/api/v1/tasks/today?as=worker&page=1&page_size=20" \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: List of tasks due today
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 422: VALIDATION_ERROR
    """
    tasks, total = list_tasks_today(db, actor_id=current_user.id, as_role=as_role)
    items = [item.model_dump(mode="json") for item in _build_task_list_items(db, tasks)]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskOut,
    summary="Create a task",
)
def create_task(
    payload: TaskCreateIn,
    _perm: None = Depends(require_perm("Task.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Create a task.

    **Auth**: Bearer JWT
    **Permission**: Task.Create
    **Request example**:
    ```json
    {
      "case_id": "CASE_ID",
      "title": "CURL Task Title",
      "due_date": "2024-02-01"
    }
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/tasks \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"case_id":"CASE_ID","title":"CURL Task Title","due_date":"2024-02-01"}'
    ```
    **Responses**:
    - 201: Task created
    - 400: Task template disabled
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Related case/document/template not found
    - 422: VALIDATION_ERROR
    """
    task = create_task_service(db, data=payload, actor_id=current_user.id)
    return TaskOut.model_validate(task)


@router.post("/tasks/{task_id}/close", response_model=TaskActionOut, summary="Close a task")
def close_task(
    task_id: str,
    payload: TaskActionIn,
    _perm: None = Depends(require_perm("Task.Action")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskActionOut:
    """
    Close a task (mark as done).

    **Auth**: Bearer JWT
    **Permission**: Task.Action
    **Request example**:
    ```json
    {"remark": "Completed"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/tasks/TASK_ID/close \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"remark":"Completed"}'
    ```
    **Responses**:
    - 200: Task closed
    - 400: Invalid status transition
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 422: VALIDATION_ERROR
    """
    close_task_service(
        db,
        task_id=task_id,
        actor_id=current_user.id,
        remark=payload.remark,
    )
    return TaskActionOut()


@router.post("/tasks/{task_id}/reopen", response_model=TaskActionOut, summary="Reopen a task")
def reopen_task(
    task_id: str,
    payload: TaskActionIn,
    _perm: None = Depends(require_perm("Task.Action")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskActionOut:
    """
    Reopen a task (mark as open).

    **Auth**: Bearer JWT
    **Permission**: Task.Action
    **Request example**:
    ```json
    {"remark": "Reopened for updates"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/tasks/TASK_ID/reopen \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"remark":"Reopened for updates"}'
    ```
    **Responses**:
    - 200: Task reopened
    - 400: Invalid status transition
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 422: VALIDATION_ERROR
    """
    reopen_task_service(
        db,
        task_id=task_id,
        actor_id=current_user.id,
        remark=payload.remark,
    )
    return TaskActionOut()


@router.post("/tasks/{task_id}/cancel", response_model=TaskActionOut, summary="Cancel a task")
def cancel_task(
    task_id: str,
    payload: TaskActionIn,
    _perm: None = Depends(require_perm("Task.Action")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskActionOut:
    """
    Cancel a task.

    **Auth**: Bearer JWT
    **Permission**: Task.Action
    **Request example**:
    ```json
    {"remark": "Cancelled by request"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/tasks/TASK_ID/cancel \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"remark":"Cancelled by request"}'
    ```
    **Responses**:
    - 200: Task cancelled
    - 400: Invalid status transition
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 422: VALIDATION_ERROR
    """
    cancel_task_service(
        db,
        task_id=task_id,
        actor_id=current_user.id,
        remark=payload.remark,
    )
    return TaskActionOut()


@router.post("/tasks/{task_id}/assign", response_model=TaskActionOut, summary="Assign a task")
def assign_task(
    task_id: str,
    payload: TaskAssignIn,
    _perm: None = Depends(require_perm("Task.Action")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskActionOut:
    """
    Assign a task to a worker or supervisor.

    **Auth**: Bearer JWT
    **Permission**: Task.Action
    **Request example**:
    ```json
    {"worker_id": "WORKER_ID", "remark": "Assigned to worker"}
    ```
    **Curl example**:
    ```bash
    curl -s -X POST http://localhost:8000/api/v1/tasks/TASK_ID/assign \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"worker_id":"WORKER_ID","remark":"Assigned to worker"}'
    ```
    **Responses**:
    - 200: Task assigned
    - 400: worker_id or supervisor_id required
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task or user not found
    - 422: VALIDATION_ERROR
    """
    assign_task_service(
        db,
        task_id=task_id,
        actor_id=current_user.id,
        worker_id=payload.worker_id,
        supervisor_id=payload.supervisor_id,
        remark=payload.remark,
    )
    return TaskActionOut()


@router.put("/tasks/{task_id}", response_model=TaskOut, summary="Update a task")
def update_task(
    task_id: str,
    payload: TaskUpdateIn,
    _perm: None = Depends(require_perm("Task.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Update a task by ID.

    **Auth**: Bearer JWT
    **Permission**: Task.Edit
    **Request example**:
    ```json
    {"title": "Updated Task Title", "due_date": "2024-02-15"}
    ```
    **Curl example**:
    ```bash
    curl -s -X PUT http://localhost:8000/api/v1/tasks/TASK_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"title":"Updated Task Title","due_date":"2024-02-15"}'
    ```
    **Responses**:
    - 200: Task updated
    - 400: Task template disabled
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task or related record not found
    - 422: VALIDATION_ERROR
    """
    task = update_task_service(db, task_id=task_id, data=payload, actor_id=current_user.id)
    return TaskOut.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a task",
)
def delete_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> Response:
    """
    Delete a manually maintained task by ID.

    **Auth**: Bearer JWT
    **Permission**: Task.Edit
    **Responses**:
    - 204: Task deleted
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 422: VALIDATION_ERROR
    """
    delete_task_service(db, task_id=task_id, actor_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tasks/{task_id}/print", summary="Print a task sheet")
def print_task_sheet(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> Response:
    """
    Generate and download a task sheet document.

    **Auth**: Bearer JWT
    **Permission**: Task.Read
    **Request example**:
    `GET /api/v1/tasks/TASK_ID/print`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/tasks/TASK_ID/print \\
      -H "Authorization: Bearer $FPMS_TOKEN" \\
      -o task_sheet.docx
    ```
    **Responses**:
    - 200: Task sheet DOCX
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 409: Template not configured
    - 422: VALIDATION_ERROR
    - 500: Template file missing
    """
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


@router.get("/tasks/{task_id}/logs", summary="List task logs")
def get_task_logs(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> list[TaskLogOut]:
    logs = list_task_logs_service(db, task_id=task_id)
    return [TaskLogOut.model_validate(log) for log in logs]


@router.get("/tasks/{task_id}", response_model=TaskOut, summary="Get a task")
def get_task(
    task_id: str,
    _perm: None = Depends(require_perm("Task.Read")),
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Get a task by ID.

    **Auth**: Bearer JWT
    **Permission**: Task.Read
    **Request example**:
    `GET /api/v1/tasks/TASK_ID`
    **Curl example**:
    ```bash
    curl -s -X GET http://localhost:8000/api/v1/tasks/TASK_ID \\
      -H "Authorization: Bearer $FPMS_TOKEN"
    ```
    **Responses**:
    - 200: Task details
    - 401: AUTH_REQUIRED
    - 403: FORBIDDEN
    - 404: Task not found
    - 422: VALIDATION_ERROR
    """
    task = get_task_service(db, task_id=task_id)
    return TaskOut.model_validate(task)
