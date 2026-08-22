from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant
from app.modules.tasks.models import Task, TaskTemplate


def _create_case(client: TestClient, auth_headers: dict[str, str], session_factory) -> str:
    client_response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"TRR-CL-{uuid4().hex[:8]}",
            "name_cn": "提醒响应客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert client_response.status_code == 201, client_response.text

    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"TRR-AP-{uuid4().hex[:8]}",
                name_cn="提醒响应申请人",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()

    case_response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"TRR-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_response.json()["id"],
            "title_cn": "提醒响应案",
            "recv_date": "2026-03-01",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "提醒响应申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert case_response.status_code == 201, case_response.text
    return case_response.json()["id"]


def _seed_task_with_reminders(session_factory, *, case_id: str) -> str:
    task_id = str(uuid4())
    with session_factory() as db:
        template = TaskTemplate(
            id=str(uuid4()),
            code=f"TRR-{uuid4().hex[:8]}",
            name="提醒响应模板",
            enabled=True,
        )
        db.add(template)
        db.flush()
        db.add(
            Task(
                id=task_id,
                case_id=case_id,
                task_template_id=template.id,
                title="提醒响应任务",
                base_date=date(2026, 3, 1),
                due_date=date(2026, 3, 31),
                internal_due_date=date(2026, 3, 24),
                remind1=date(2026, 3, 23),
                remind2=date(2026, 3, 21),
                remind3=date(2026, 3, 19),
                daily_remind_from=date(2026, 3, 19),
                daily_remind=True,
                status="OPEN",
            )
        )
        db.commit()
    return task_id


def test_task_detail_and_list_include_reminder_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    case_id = _create_case(client, auth_headers, session_factory)
    task_id = _seed_task_with_reminders(session_factory, case_id=case_id)

    detail_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["remind1"] == "2026-03-23"
    assert detail["remind2"] == "2026-03-21"
    assert detail["remind3"] == "2026-03-19"
    assert detail["daily_remind_from"] == "2026-03-19"
    assert detail["daily_remind"] is True

    list_response = client.get(
        "/api/v1/tasks",
        params={"case_id": case_id, "status": "OPEN", "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert list_response.status_code == 200, list_response.text
    items = list_response.json()["items"]
    item = next(row for row in items if row["id"] == task_id)
    assert item["remind1"] == "2026-03-23"
    assert item["remind2"] == "2026-03-21"
    assert item["remind3"] == "2026-03-19"
    assert item["daily_remind_from"] == "2026-03-19"
    assert item["daily_remind"] is True
