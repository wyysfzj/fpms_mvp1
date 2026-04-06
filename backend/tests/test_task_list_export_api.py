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
from app.modules.tasks.models import Task

EXPORT_BASE = "/api/v1/tasks/export"


def _seed_task_list_export_data(session_factory: sessionmaker) -> tuple[str, str, str]:
    suffix = uuid4().hex[:8].upper()
    client_a_id = str(uuid4())
    client_b_id = str(uuid4())
    case_a_id = str(uuid4())
    case_b_id = str(uuid4())
    other_user_id = str(uuid4())

    with session_factory() as db:
        admin_user = db.query(T_User).filter(T_User.username == "admin").one()
        db.add_all(
            [
                Client(
                    id=client_a_id,
                    client_code=f"TK-A-{suffix}",
                    name_cn="任务导出客户甲",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                Client(
                    id=client_b_id,
                    client_code=f"TK-B-{suffix}",
                    name_cn="任务导出客户乙",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                T_User(
                    id=other_user_id,
                    username=f"task-export-{uuid4().hex[:8]}",
                    display_name="外部用户",
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
                    case_no=f"TASK-EXPORT-A-{suffix}",
                    client_id=client_a_id,
                    title_cn="任务导出案件甲",
                ),
                Case(
                    id=case_b_id,
                    case_no=f"TASK-EXPORT-B-{suffix}",
                    client_id=client_b_id,
                    title_cn="任务导出案件乙",
                ),
            ]
        )
        db.commit()
        db.add_all(
            [
                Task(
                    id=str(uuid4()),
                    case_id=case_a_id,
                    title=f"我的导出任务-{suffix}",
                    due_date=date(2026, 5, 1),
                    status="OPEN",
                    worker_id=admin_user.id,
                    supervisor_id=other_user_id,
                    created_at=datetime(2026, 1, 10, 9, 0, 0),
                ),
                Task(
                    id=str(uuid4()),
                    case_id=case_b_id,
                    title=f"团队导出任务-{suffix}",
                    due_date=date(2026, 5, 2),
                    status="DONE",
                    worker_id=other_user_id,
                    supervisor_id=admin_user.id,
                    created_at=datetime(2026, 1, 10, 10, 0, 0),
                ),
            ]
        )
        db.commit()
    return suffix, client_a_id, client_b_id


def test_task_list_export_returns_excel_for_my_task_view(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix, _, _ = _seed_task_list_export_data(session_factory)

    response = client.get(
        EXPORT_BASE,
        headers=auth_headers,
        params={"as": "worker", "status": "OPEN"},
    )

    assert response.status_code == 200, response.text
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment;" in response.headers["content-disposition"]
    assert "my-task-list.xlsx" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "我的时限任务清单" in sheet_xml
    assert f"我的导出任务-{suffix}" in sheet_xml
    assert f"TASK-EXPORT-A-{suffix}" in sheet_xml
    assert "团队导出任务" not in sheet_xml


def test_task_list_export_can_filter_by_client_for_all_view(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix, client_a_id, _ = _seed_task_list_export_data(session_factory)

    response = client.get(
        EXPORT_BASE,
        headers=auth_headers,
        params={"client_id": client_a_id},
    )

    assert response.status_code == 200, response.text
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "时限任务清单" in sheet_xml
    assert f"我的导出任务-{suffix}" in sheet_xml
    assert "团队导出任务" not in sheet_xml


def test_task_list_export_requires_task_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get(EXPORT_BASE, headers=auth_headers)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "Task.Read"


def test_task_list_export_requires_authentication(client: TestClient) -> None:
    response = client.get(EXPORT_BASE)

    assert response.status_code == 401, response.text
