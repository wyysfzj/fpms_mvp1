from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.models import Task, TaskTemplate

SPECIAL_SEARCH_BASE = "/api/v1/tasks/special/search"


def _seed_special_task_data(session_factory: sessionmaker) -> tuple[str, str, str, str, str]:
    code_suffix = uuid4().hex[:8].upper()
    client_a_id = str(uuid4())
    client_b_id = str(uuid4())
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    worker_id = str(uuid4())

    with session_factory() as db:
        db.add_all(
            [
                Client(
                    id=client_a_id,
                    client_code=f"CL-A-{code_suffix}",
                    name_cn="甲方客户",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                Client(
                    id=client_b_id,
                    client_code=f"CL-B-{code_suffix}",
                    name_cn="乙方客户",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                T_User(
                    id=worker_id,
                    username=f"worker-{uuid4().hex[:8]}",
                    display_name="工作人",
                    password_hash="x",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        db.add_all(
            [
                Case(
                    id=case_a_id,
                    case_no=f"CASE-A-{code_suffix}",
                    client_id=client_a_id,
                    title_cn="申请费时限案",
                ),
                Case(
                    id=case_b_id,
                    case_no=f"CASE-B-{code_suffix}",
                    client_id=client_b_id,
                    title_cn="实审请求时限案",
                ),
            ]
        )
        if (
            db.query(TaskTemplate).filter(TaskTemplate.code == "APPLY_FEE_LIMIT").one_or_none()
            is None
        ):
            db.add(TaskTemplate(id=str(uuid4()), code="APPLY_FEE_LIMIT", name="申请费时限"))
        if (
            db.query(TaskTemplate)
            .filter(TaskTemplate.code == "EXAM_REQUEST_LIMIT")
            .one_or_none()
            is None
        ):
            db.add(TaskTemplate(id=str(uuid4()), code="EXAM_REQUEST_LIMIT", name="实审请求时限"))
        db.commit()

        apply_template = db.query(TaskTemplate).filter(TaskTemplate.code == "APPLY_FEE_LIMIT").one()
        exam_template = (
            db.query(TaskTemplate).filter(TaskTemplate.code == "EXAM_REQUEST_LIMIT").one()
        )

        apply_task_id = f"10000000-0000-0000-0000-{uuid4().hex[:12]}"
        shared_created_at = datetime(2026, 1, 10, 9, 0, 0)

        apply_task = Task(
            id=apply_task_id,
            case_id=case_a_id,
            task_template_id=apply_template.id,
            title="申请费时限",
            due_date=date(2026, 3, 1),
            status="OPEN",
            worker_id=worker_id,
            created_at=shared_created_at,
        )
        apply_task_2_id = f"f0000000-0000-0000-0000-{uuid4().hex[:12]}"
        apply_task_2 = Task(
            id=apply_task_2_id,
            case_id=case_a_id,
            task_template_id=apply_template.id,
            title="申请费时限-二",
            due_date=date(2026, 3, 1),
            status="OPEN",
            worker_id=worker_id,
            created_at=shared_created_at,
        )
        exam_task_id = f"90000000-0000-0000-0000-{uuid4().hex[:12]}"
        exam_task = Task(
            id=exam_task_id,
            case_id=case_b_id,
            task_template_id=exam_template.id,
            title="实审请求时限",
            due_date=date(2026, 4, 1),
            status="DONE",
            worker_id=worker_id,
        )
        other_task = Task(
            id=str(uuid4()),
            case_id=case_b_id,
            title="普通任务",
            due_date=date(2026, 2, 1),
            status="OPEN",
            worker_id=worker_id,
        )
        db.add_all([apply_task, apply_task_2, exam_task, other_task])
        db.commit()

    return case_a_id, case_b_id, apply_task_id, apply_task_2_id, exam_task_id


def test_task_special_search_requires_task_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get(SPECIAL_SEARCH_BASE, headers=auth_headers)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "Task.Read"


def test_task_special_search_lists_special_tasks_with_projection_and_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _, _, apply_task_id, apply_task_2_id, exam_task_id = _seed_special_task_data(session_factory)

    response = client.get(
        SPECIAL_SEARCH_BASE,
        headers=auth_headers,
        params={
            "task_code": "APPLY_FEE_LIMIT",
            "status": "OPEN",
            "case_no": "CASE-A-",
            "client_name": "甲方客户",
            "due_date_from": "2026-02-01",
            "due_date_to": "2026-03-31",
            "is_overdue": True,
            "page": 1,
            "page_size": 1,
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert set(payload) == {"items", "page", "page_size", "total"}
    assert payload["page"] == 1
    assert payload["page_size"] == 1
    assert payload["total"] == 2
    assert len(payload["items"]) == 1

    item = payload["items"][0]
    assert set(item) == {
        "task_code",
        "task_id",
        "case_id",
        "case_no",
        "client_name",
        "title",
        "status",
        "due_date",
        "is_overdue",
        "remark",
    }
    assert item["task_code"] == "APPLY_FEE_LIMIT"
    assert item["task_id"] == apply_task_id
    assert item["case_no"].startswith("CASE-A-")
    assert item["client_name"] == "甲方客户"
    assert item["status"] == "OPEN"
    assert item["due_date"] == "2026-03-01"
    assert item["is_overdue"] is True
    assert item["remark"] is None
    assert item["task_id"] == apply_task_id
    assert item["task_id"] != apply_task_2_id
    assert item["task_id"] != exam_task_id

    next_page_resp = client.get(
        SPECIAL_SEARCH_BASE,
        headers=auth_headers,
        params={
            "task_code": "APPLY_FEE_LIMIT",
            "status": "OPEN",
            "case_no": "CASE-A-",
            "client_name": "甲方客户",
            "due_date_from": "2026-02-01",
            "due_date_to": "2026-03-31",
            "is_overdue": True,
            "page": 2,
            "page_size": 1,
        },
    )

    assert next_page_resp.status_code == 200, next_page_resp.text
    next_payload = next_page_resp.json()
    assert next_payload["total"] == 2
    assert len(next_payload["items"]) == 1
    assert next_payload["items"][0]["task_id"] == apply_task_2_id


def test_task_special_search_overdue_semantics_include_non_done_statuses(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _, _, _, _, exam_task_id = _seed_special_task_data(session_factory)

    with session_factory() as db:
        exam_task = db.query(Task).filter(Task.id == exam_task_id).one()
        exam_task.status = "CANCELLED"
        exam_task.due_date = date(2026, 3, 1)
        db.commit()

    overdue_resp = client.get(
        SPECIAL_SEARCH_BASE,
        headers=auth_headers,
        params={
            "task_code": "EXAM_REQUEST_LIMIT",
            "case_no": "CASE-B-",
            "client_name": "乙方客户",
            "is_overdue": True,
            "page": 1,
            "page_size": 20,
        },
    )

    assert overdue_resp.status_code == 200, overdue_resp.text
    overdue_payload = overdue_resp.json()
    assert overdue_payload["total"] == 1
    assert overdue_payload["items"][0]["task_id"] == exam_task_id
    assert overdue_payload["items"][0]["status"] == "CANCELLED"
    assert overdue_payload["items"][0]["is_overdue"] is True

    not_overdue_resp = client.get(
        SPECIAL_SEARCH_BASE,
        headers=auth_headers,
        params={
            "task_code": "EXAM_REQUEST_LIMIT",
            "case_no": "CASE-B-",
            "is_overdue": False,
            "page": 1,
            "page_size": 20,
        },
    )

    assert not_overdue_resp.status_code == 200, not_overdue_resp.text
    not_overdue_payload = not_overdue_resp.json()
    assert exam_task_id not in {item["task_id"] for item in not_overdue_payload["items"]}
