from __future__ import annotations

import io
import zipfile
from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.models import Task, TaskTemplate

SPECIAL_EXPORT_BASE = "/api/v1/tasks/special/search/export"
SPECIAL_PRINT_BASE = "/api/v1/tasks/special/search/print"


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
            db.query(TaskTemplate).filter(TaskTemplate.code == "EXAM_REQUEST_LIMIT").one_or_none()
            is None
        ):
            db.add(TaskTemplate(id=str(uuid4()), code="EXAM_REQUEST_LIMIT", name="实审请求时限"))
        db.commit()

        apply_template = db.query(TaskTemplate).filter(TaskTemplate.code == "APPLY_FEE_LIMIT").one()
        exam_template = (
            db.query(TaskTemplate).filter(TaskTemplate.code == "EXAM_REQUEST_LIMIT").one()
        )

        apply_task_id = f"10000000-0000-0000-0000-{uuid4().hex[:12]}"
        apply_task = Task(
            id=apply_task_id,
            case_id=case_a_id,
            task_template_id=apply_template.id,
            title="申请费时限",
            due_date=date(2026, 3, 1),
            status="OPEN",
            worker_id=worker_id,
            created_at=datetime(2026, 1, 10, 9, 0, 0),
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
        db.add_all([apply_task, exam_task])
        db.commit()

    return case_a_id, case_b_id, apply_task_id, exam_task_id, code_suffix


def test_task_special_search_export_returns_excel_with_filtered_rows(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_special_task_data(session_factory)

    response = client.get(
        SPECIAL_EXPORT_BASE,
        headers=auth_headers,
        params={
            "task_code": "APPLY_FEE_LIMIT",
            "case_no": "CASE-A-",
            "client_name": "甲方客户",
            "is_overdue": True,
        },
    )

    assert response.status_code == 200, response.text
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment;" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "专项期限检索清单" in sheet_xml
    assert "APPLY_FEE_LIMIT" in sheet_xml
    assert "甲方客户" in sheet_xml
    assert "实审请求时限" not in sheet_xml


def test_task_special_search_print_returns_html_with_filtered_rows(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_special_task_data(session_factory)

    response = client.get(
        SPECIAL_PRINT_BASE,
        headers=auth_headers,
        params={
            "task_code": "EXAM_REQUEST_LIMIT",
            "case_no": "CASE-B-",
            "client_name": "乙方客户",
            "is_overdue": False,
        },
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/html")
    assert "专项期限检索清单" in response.text
    assert "EXAM_REQUEST_LIMIT" in response.text
    assert "乙方客户" in response.text
    assert "APPLY_FEE_LIMIT" not in response.text


def test_task_special_search_export_requires_task_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get(SPECIAL_EXPORT_BASE, headers=auth_headers)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "Task.Read"


def test_task_special_search_print_requires_authentication(client: TestClient) -> None:
    response = client.get(SPECIAL_PRINT_BASE)

    assert response.status_code == 401, response.text
