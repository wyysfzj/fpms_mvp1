"""Tests for Batch A1: TaskTemplate CRUD, TaskLog API, and auto-generation."""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import get_password_hash
from app.modules.auth.models import T_User
from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase
from app.modules.tasks.schemas import TaskTemplateCreateIn, TaskTemplateOut, TaskTemplateUpdateIn

# ---------- helpers ----------


def _create_case(client: TestClient, headers: dict) -> str:
    """Create a minimal case and return its id."""
    cl = client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "client_code": f"TST-{uuid4().hex[:6]}",
            "name_cn": "测试客户",
        },
    )
    assert cl.status_code == 201, cl.text
    client_id = cl.json()["id"]

    resp = client.post(
        "/api/v1/cases",
        headers=headers,
        json={
            "case_no": f"A1-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "client_id": client_id,
            "title_cn": "测试案件",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_user(session_factory: sessionmaker, username_prefix: str) -> str:
    with session_factory() as db:
        user = T_User(
            id=str(uuid4()),
            username=f"{username_prefix}_{uuid4().hex[:6]}",
            display_name="测试用户",
            password_hash=get_password_hash("secret123"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        return user.id


# ---------- TaskTemplate CRUD ----------


def test_task_template_schemas_include_reminder_fields() -> None:
    create_payload = TaskTemplateCreateIn(
        code="TPL-SCHEMA",
        name="模板 schema 测试",
        deadline_base=TaskDeadlineBase.RECEIVE_DATE,
        remind_base=TaskRemindBase.DEADLINE,
        remind_1_offset_days=1,
        remind_2_offset_days=2,
        remind_3_offset_days=3,
        daily_remind=True,
        default_supervisor_id="supervisor-id",
        add_days=90,
        inner_offset_days=10,
    )
    assert create_payload.deadline_base == TaskDeadlineBase.RECEIVE_DATE
    assert create_payload.remind_base == TaskRemindBase.DEADLINE
    assert create_payload.remind_1_offset_days == 1
    assert create_payload.remind_2_offset_days == 2
    assert create_payload.remind_3_offset_days == 3
    assert create_payload.daily_remind is True
    assert create_payload.default_supervisor_id == "supervisor-id"

    update_payload = TaskTemplateUpdateIn(
        deadline_base=TaskDeadlineBase.FILING_DATE,
        remind_base=TaskRemindBase.INNER,
        remind_1_offset_days=4,
        remind_2_offset_days=5,
        remind_3_offset_days=6,
        daily_remind=False,
        default_supervisor_id=None,
    )
    assert update_payload.deadline_base == TaskDeadlineBase.FILING_DATE
    assert update_payload.remind_base == TaskRemindBase.INNER
    assert update_payload.remind_1_offset_days == 4
    assert update_payload.remind_2_offset_days == 5
    assert update_payload.remind_3_offset_days == 6
    assert update_payload.daily_remind is False
    assert update_payload.default_supervisor_id is None

    out = TaskTemplateOut.model_validate(
        SimpleNamespace(
            id=str(uuid4()),
            code="TPL-OUT",
            name="模板 out 测试",
            add_days=30,
            add_months=0,
            inner_offset_days=7,
            deadline_base=TaskDeadlineBase.RECEIVE_DATE,
            remind_base=TaskRemindBase.DEADLINE,
            remind_1_offset_days=1,
            remind_2_offset_days=2,
            remind_3_offset_days=3,
            daily_remind=True,
            default_supervisor_id="supervisor-id",
            default_worker_role="worker",
            enabled=True,
            description="desc",
            created_at=date(2025, 1, 1),
            updated_at=date(2025, 1, 2),
        )
    )
    assert out.deadline_base == TaskDeadlineBase.RECEIVE_DATE
    assert out.remind_base == TaskRemindBase.DEADLINE
    assert out.remind_1_offset_days == 1
    assert out.remind_2_offset_days == 2
    assert out.remind_3_offset_days == 3
    assert out.daily_remind is True
    assert out.default_supervisor_id == "supervisor-id"


def test_list_task_templates_returns_seeded(client: TestClient, auth_headers: dict) -> None:
    """Verify seeded OA_REPLY and GRANT_FEE appear in listing."""
    resp = client.get("/api/v1/task-templates", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    codes = {t["code"] for t in data}
    assert "OA_REPLY" in codes
    assert "GRANT_FEE" in codes

    oa = next(t for t in data if t["code"] == "OA_REPLY")
    assert oa["add_days"] == 120
    assert oa["inner_offset_days"] == 14

    gf = next(t for t in data if t["code"] == "GRANT_FEE")
    assert gf["add_days"] == 60
    assert gf["inner_offset_days"] == 7


def test_create_task_template(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    code = f"T-{uuid4().hex[:6]}"
    supervisor_id = _create_user(session_factory, "task_template_supervisor")
    resp = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={
            "code": code,
            "name": "Test Template",
            "add_days": 90,
            "inner_offset_days": 10,
            "deadline_base": "RECEIVE_DATE",
            "remind_base": "DEADLINE",
            "remind_1_offset_days": 1,
            "remind_2_offset_days": 2,
            "remind_3_offset_days": 3,
            "daily_remind": True,
            "default_supervisor_id": supervisor_id,
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["code"] == code
    assert body["add_days"] == 90
    assert body["inner_offset_days"] == 10
    assert body["deadline_base"] == "RECEIVE_DATE"
    assert body["remind_base"] == "DEADLINE"
    assert body["remind_1_offset_days"] == 1
    assert body["remind_2_offset_days"] == 2
    assert body["remind_3_offset_days"] == 3
    assert body["daily_remind"] is True
    assert body["default_supervisor_id"]
    assert body["enabled"] is True


def test_create_task_template_commits_once(
    client: TestClient, auth_headers: dict, monkeypatch, session_factory: sessionmaker
) -> None:
    commit_count = 0
    original_commit = Session.commit

    def wrapped_commit(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal commit_count
        commit_count += 1
        return original_commit(self, *args, **kwargs)

    monkeypatch.setattr(Session, "commit", wrapped_commit)

    code = f"C-{uuid4().hex[:6]}"
    resp = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": code, "name": "Atomic Template", "add_days": 15},
    )
    assert resp.status_code == 201, resp.text
    assert commit_count == 1


def test_create_task_template_rejects_missing_default_supervisor(
    client: TestClient, auth_headers: dict
) -> None:
    resp = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={
            "code": f"S-{uuid4().hex[:6]}",
            "name": "Supervisor Guard Template",
            "default_supervisor_id": str(uuid4()),
        },
    )
    assert resp.status_code == 404, resp.text


def test_create_task_template_rejects_null_daily_remind(
    client: TestClient, auth_headers: dict
) -> None:
    resp = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={
            "code": f"N-{uuid4().hex[:6]}",
            "name": "Null Daily Remind",
            "daily_remind": None,
        },
    )
    assert resp.status_code == 422, resp.text


def test_update_task_template(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    code = f"U-{uuid4().hex[:6]}"
    supervisor_id = _create_user(session_factory, "task_template_supervisor")
    create = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": code, "name": "Before", "add_days": 30},
    )
    assert create.status_code == 201, create.text
    tid = create.json()["id"]

    update = client.put(
        f"/api/v1/task-templates/{tid}",
        headers=auth_headers,
        json={
            "name": "After",
            "add_days": 60,
            "deadline_base": "FILING_DATE",
            "remind_base": "INNER",
            "remind_1_offset_days": 4,
            "remind_2_offset_days": 5,
            "remind_3_offset_days": 6,
            "daily_remind": True,
            "default_supervisor_id": supervisor_id,
        },
    )
    assert update.status_code == 200, update.text
    body = update.json()
    assert body["name"] == "After"
    assert body["add_days"] == 60
    assert body["deadline_base"] == "FILING_DATE"
    assert body["remind_base"] == "INNER"
    assert body["remind_1_offset_days"] == 4
    assert body["remind_2_offset_days"] == 5
    assert body["remind_3_offset_days"] == 6
    assert body["daily_remind"] is True
    assert body["default_supervisor_id"]


def test_update_task_template_rejects_missing_default_supervisor(
    client: TestClient, auth_headers: dict
) -> None:
    create = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": f"U-{uuid4().hex[:6]}", "name": "Before"},
    )
    assert create.status_code == 201, create.text
    tid = create.json()["id"]

    update = client.put(
        f"/api/v1/task-templates/{tid}",
        headers=auth_headers,
        json={"default_supervisor_id": str(uuid4())},
    )
    assert update.status_code == 404, update.text


def test_update_task_template_rejects_null_daily_remind(
    client: TestClient, auth_headers: dict
) -> None:
    create = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": f"N-{uuid4().hex[:6]}", "name": "Before"},
    )
    assert create.status_code == 201, create.text
    tid = create.json()["id"]

    update = client.put(
        f"/api/v1/task-templates/{tid}",
        headers=auth_headers,
        json={"daily_remind": None},
    )
    assert update.status_code == 422, update.text


def test_duplicate_code_rejected(client: TestClient, auth_headers: dict) -> None:
    code = f"D-{uuid4().hex[:6]}"
    r1 = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": code, "name": "First"},
    )
    assert r1.status_code == 201, r1.text

    r2 = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": code, "name": "Duplicate"},
    )
    assert r2.status_code == 409


# ---------- TaskLog API ----------


def test_list_task_logs_includes_create(client: TestClient, auth_headers: dict) -> None:
    """Manual task creation now writes a CREATE log entry."""
    case_id = _create_case(client, auth_headers)

    task_resp = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "Log Test Task",
            "due_date": str(date.today() + timedelta(days=30)),
        },
    )
    assert task_resp.status_code == 201, task_resp.text
    task_id = task_resp.json()["id"]

    # Fetch logs — should have CREATE entry from manual creation
    logs_resp = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    assert logs_resp.status_code == 200, logs_resp.text
    logs = logs_resp.json()
    assert len(logs) >= 1
    create_log = next((entry for entry in logs if entry["action"] == "CREATE"), None)
    assert create_log is not None
    assert create_log["to_status"] == "OPEN"

    # Close it and verify CLOSE log also appears
    close_resp = client.post(
        f"/api/v1/tasks/{task_id}/close",
        headers=auth_headers,
        json={"remark": "done"},
    )
    assert close_resp.status_code == 200, close_resp.text

    logs_resp2 = client.get(f"/api/v1/tasks/{task_id}/logs", headers=auth_headers)
    logs2 = logs_resp2.json()
    actions = [entry["action"] for entry in logs2]
    assert "CREATE" in actions
    assert "CLOSE" in actions


def test_delete_manual_task_removes_it(client: TestClient, auth_headers: dict) -> None:
    """Manual task maintenance includes delete within Batch 2 scope."""
    case_id = _create_case(client, auth_headers)

    task_resp = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "Delete Test Task",
            "due_date": str(date.today() + timedelta(days=7)),
        },
    )
    assert task_resp.status_code == 201, task_resp.text
    task_id = task_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_resp.status_code == 204, delete_resp.text
    assert delete_resp.text == ""

    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404, get_resp.text


def test_tasks_today_returns_enriched_fields_and_role_filtered(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    """Today's reminder endpoint should enrich task rows and respect as=worker/supervisor."""
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200, me_resp.text
    current_user_id = me_resp.json()["user"]["id"]
    other_user_id = _create_user(session_factory, "task_other")
    case_id = _create_case(client, auth_headers)

    task_worker = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "今日我的任务",
            "due_date": str(date.today()),
            "worker_id": current_user_id,
            "supervisor_id": other_user_id,
        },
    )
    assert task_worker.status_code == 201, task_worker.text

    task_supervisor = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "今日团队任务",
            "due_date": str(date.today()),
            "worker_id": other_user_id,
            "supervisor_id": current_user_id,
        },
    )
    assert task_supervisor.status_code == 201, task_supervisor.text

    worker_today = client.get("/api/v1/tasks/today?as=worker", headers=auth_headers)
    assert worker_today.status_code == 200, worker_today.text
    worker_items = worker_today.json()["items"]
    assert [item["title"] for item in worker_items] == ["今日我的任务"]
    assert worker_items[0]["case_no"].startswith("A1-")
    assert worker_items[0]["client_name"] == "测试客户"
    assert worker_items[0]["created_at"]
    assert worker_items[0]["updated_at"]

    supervisor_today = client.get("/api/v1/tasks/today?as=supervisor", headers=auth_headers)
    assert supervisor_today.status_code == 200, supervisor_today.text
    supervisor_items = supervisor_today.json()["items"]
    assert [item["title"] for item in supervisor_items] == ["今日团队任务"]


def test_list_tasks_supports_current_user_role_view(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    """Task list should support current-user scoped worker/supervisor views."""
    me_resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200, me_resp.text
    current_user_id = me_resp.json()["user"]["id"]
    other_user_id = _create_user(session_factory, "task_other")
    case_id = _create_case(client, auth_headers)

    task_worker = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "列表我的任务",
            "due_date": str(date.today() + timedelta(days=1)),
            "worker_id": current_user_id,
            "supervisor_id": other_user_id,
        },
    )
    assert task_worker.status_code == 201, task_worker.text

    task_supervisor = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "title": "列表团队任务",
            "due_date": str(date.today() + timedelta(days=1)),
            "worker_id": other_user_id,
            "supervisor_id": current_user_id,
        },
    )
    assert task_supervisor.status_code == 201, task_supervisor.text

    worker_list = client.get("/api/v1/tasks?as=worker&page=1&page_size=20", headers=auth_headers)
    assert worker_list.status_code == 200, worker_list.text
    worker_titles = {item["title"] for item in worker_list.json()["items"]}
    assert "列表我的任务" in worker_titles
    assert "列表团队任务" not in worker_titles

    supervisor_list = client.get(
        "/api/v1/tasks?as=supervisor&page=1&page_size=20",
        headers=auth_headers,
    )
    assert supervisor_list.status_code == 200, supervisor_list.text
    supervisor_titles = {item["title"] for item in supervisor_list.json()["items"]}
    assert "列表团队任务" in supervisor_titles
    assert "列表我的任务" not in supervisor_titles


# ---------- Auto-generation via TaskGenerationService ----------


def test_task_generation_creates_task_with_due_date() -> None:
    """Unit test: generate_from_document sets due_date and internal_due_date."""
    from unittest.mock import MagicMock

    from app.modules.tasks.task_generation_service import TaskGenerationService

    svc = TaskGenerationService()

    template = MagicMock()
    template.code = "GENERIC_DEADLINE"
    template.name = "通用期限"
    template.enabled = True
    template.add_days = 120
    template.add_months = 0
    template.inner_offset_days = 14
    template.id = str(uuid4())

    doc = MagicMock()
    doc.id = str(uuid4())
    doc.case_id = str(uuid4())
    doc.doc_date = date(2025, 1, 10)
    doc.direction = "IN"
    doc.doc_type = "GENERIC_DEADLINE"
    doc.title = "通用期限文件"

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [template]
    db.query.return_value.filter.return_value.first.return_value = None

    tasks = svc.generate_from_document(db, doc)
    assert len(tasks) == 1

    task = tasks[0]
    expected_due = date(2025, 1, 10) + timedelta(days=120)
    expected_internal = expected_due - timedelta(days=14)
    assert task.due_date == expected_due
    assert task.internal_due_date == expected_internal
    assert task.base_date == date(2025, 1, 10)


def test_task_generation_grant_fee_triggers() -> None:
    """GRANT_FEE template now triggers auto-generation (no OA filter)."""
    from unittest.mock import MagicMock

    from app.modules.tasks.task_generation_service import TaskGenerationService

    svc = TaskGenerationService()

    template = MagicMock()
    template.code = "GRANT_FEE"
    template.name = "授权登记费"
    template.enabled = True
    template.add_days = 60
    template.add_months = 0
    template.inner_offset_days = 7
    template.id = str(uuid4())

    doc = MagicMock()
    doc.id = str(uuid4())
    doc.case_id = str(uuid4())
    doc.doc_date = date(2025, 3, 1)
    doc.direction = "IN"
    doc.doc_type = "GRANT_FEE"
    doc.title = "授权通知书"

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [template]
    db.query.return_value.filter.return_value.first.return_value = None

    tasks = svc.generate_from_document(db, doc)
    assert len(tasks) == 1
    assert tasks[0].due_date == date(2025, 3, 1) + timedelta(days=60)
    assert tasks[0].internal_due_date == tasks[0].due_date - timedelta(days=7)


def test_task_generation_add_months() -> None:
    """Templates with add_months compute due_date correctly."""
    from unittest.mock import MagicMock

    from app.modules.tasks.task_generation_service import TaskGenerationService

    svc = TaskGenerationService()

    template = MagicMock()
    template.code = "ANNUAL_FEE"
    template.name = "年费"
    template.enabled = True
    template.add_days = 0
    template.add_months = 3
    template.inner_offset_days = None
    template.id = str(uuid4())

    doc = MagicMock()
    doc.id = str(uuid4())
    doc.case_id = str(uuid4())
    doc.doc_date = date(2025, 1, 31)
    doc.direction = "IN"
    doc.doc_type = "ANNUAL_FEE"
    doc.title = "年费通知"

    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [template]
    db.query.return_value.filter.return_value.first.return_value = None

    tasks = svc.generate_from_document(db, doc)
    assert len(tasks) == 1
    # Jan 31 + 3 months → Apr 30 (clamped)
    assert tasks[0].due_date == date(2025, 4, 30)
    assert tasks[0].internal_due_date is None
