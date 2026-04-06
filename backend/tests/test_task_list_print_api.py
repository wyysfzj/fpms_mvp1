from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.tasks.models import Task

PRINT_BASE = "/api/v1/tasks/print"


def _seed_task_list_print_data(session_factory: sessionmaker) -> tuple[str, str]:
    suffix = uuid4().hex[:8].upper()
    client_id = str(uuid4())
    case_id = str(uuid4())
    other_case_id = str(uuid4())
    other_client_id = str(uuid4())

    with session_factory() as db:
        admin_user = db.query(T_User).filter(T_User.username == "admin").one()
        other_user_id = str(uuid4())
        db.add_all(
            [
                Client(
                    id=client_id,
                    client_code=f"TP-A-{suffix}",
                    name_cn="打印客户甲",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                Client(
                    id=other_client_id,
                    client_code=f"TP-B-{suffix}",
                    name_cn="打印客户乙",
                    client_type="CLIENT",
                    default_currency="CNY",
                    is_active=True,
                ),
                T_User(
                    id=other_user_id,
                    username=f"task-print-{uuid4().hex[:8]}",
                    display_name="打印用户",
                    password_hash="x",
                    is_active=True,
                ),
            ]
        )
        db.commit()
        db.add_all(
            [
                Case(
                    id=case_id,
                    case_no=f"TASK-PRINT-A-{suffix}",
                    client_id=client_id,
                    title_cn="打印案件甲",
                ),
                Case(
                    id=other_case_id,
                    case_no=f"TASK-PRINT-B-{suffix}",
                    client_id=other_client_id,
                    title_cn="打印案件乙",
                ),
            ]
        )
        db.commit()
        db.add_all(
            [
                Task(
                    id=str(uuid4()),
                    case_id=case_id,
                    title=f"监督打印任务-{suffix}",
                    due_date=date(2026, 6, 1),
                    status="OPEN",
                    worker_id=other_user_id,
                    supervisor_id=admin_user.id,
                    created_at=datetime(2026, 1, 11, 9, 0, 0),
                ),
                Task(
                    id=str(uuid4()),
                    case_id=other_case_id,
                    title=f"过滤掉的打印任务-{suffix}",
                    due_date=date(2026, 6, 2),
                    status="DONE",
                    worker_id=other_user_id,
                    supervisor_id=other_user_id,
                    created_at=datetime(2026, 1, 11, 10, 0, 0),
                ),
            ]
        )
        db.commit()
    return suffix, client_id


def test_task_list_print_returns_html_for_supervisor_view(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix, _ = _seed_task_list_print_data(session_factory)

    response = client.get(
        PRINT_BASE,
        headers=auth_headers,
        params={"as": "supervisor", "status": "OPEN"},
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/html")
    assert "监督时限任务清单" in response.text
    assert f"监督打印任务-{suffix}" in response.text
    assert f"TASK-PRINT-A-{suffix}" in response.text
    assert "过滤掉的打印任务" not in response.text


def test_task_list_print_can_filter_by_client(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    suffix, client_id = _seed_task_list_print_data(session_factory)

    response = client.get(
        PRINT_BASE,
        headers=auth_headers,
        params={"client_id": client_id},
    )

    assert response.status_code == 200, response.text
    assert "时限任务清单" in response.text
    assert f"监督打印任务-{suffix}" in response.text
    assert "过滤掉的打印任务" not in response.text


def test_task_list_print_requires_task_read_permission(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
) -> None:
    import app.api.deps as deps

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get(PRINT_BASE, headers=auth_headers)

    assert response.status_code == 403, response.text
    assert response.json()["error"]["details"]["required_perm"] == "Task.Read"


def test_task_list_print_requires_authentication(client: TestClient) -> None:
    response = client.get(PRINT_BASE)

    assert response.status_code == 401, response.text
