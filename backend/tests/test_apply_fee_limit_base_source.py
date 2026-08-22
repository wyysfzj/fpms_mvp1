from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.masterdata.applicants.models import Applicant
from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase
from app.modules.tasks.models import Task, TaskTemplate
from tests.test_v8_batch_filing_lifecycle_adapter import (
    _seed_filing_evidence_for_case,
    _start_filing_preparation,
)


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"AFB-CL-{uuid4().hex[:8]}",
            "name_cn": "申请费基准客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"AFB-AP-{uuid4().hex[:8]}",
                name_cn=f"申请费基准申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _configure_template(session_factory, deadline_base: TaskDeadlineBase) -> None:
    with session_factory() as db:
        template = (
            db.query(TaskTemplate).filter(TaskTemplate.code == "APPLY_FEE_LIMIT").one_or_none()
        )
        if template is None:
            template = TaskTemplate(
                id=str(uuid4()),
                code="APPLY_FEE_LIMIT",
                name="申请费时限",
            )
            db.add(template)
            db.flush()
        template.enabled = True
        template.deadline_base = deadline_base
        template.add_days = 20
        template.add_months = 0
        template.inner_offset_days = 5
        template.remind_base = TaskRemindBase.DEADLINE
        template.remind_1_offset_days = 2
        template.remind_2_offset_days = 4
        template.remind_3_offset_days = 6
        template.daily_remind = True
        db.commit()


def _create_not_filed_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"AFB-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "申请费基准测试案",
            "recv_date": "2026-03-01",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "申请费基准申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _set_filing_date(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    filing_date: str,
) -> None:
    response = client.put(
        f"/api/v1/cases/{case_id}",
        json={"filing_date": filing_date},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text


def _create_filing_materials(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
) -> None:
    for title in ("发明专利请求书", "说明书", "权利要求书", "摘要"):
        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            json={
                "case_id": case_id,
                "doc_template_id": None,
                "doc_type": "CLIENT_IN",
                "direction": "IN",
                "doc_date": "2026-03-02",
                "title": title,
            },
        )
        assert response.status_code == 201, response.text


def _submit_batch(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    submitted_date: str,
) -> dict:
    response = client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": [case_id],
            "submitted_date": submitted_date,
            "apply_exam_now": False,
            "generate_list": False,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_batch_filing_apply_fee_limit_uses_filing_date_base_source(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _configure_template(session_factory, TaskDeadlineBase.FILING_DATE)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_not_filed_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    _set_filing_date(
        client,
        auth_headers,
        case_id=case_data["id"],
        filing_date="2026-03-08",
    )
    _create_filing_materials(client, auth_headers, case_id=case_data["id"])
    _start_filing_preparation(client, auth_headers, case_id=case_data["id"])
    with session_factory() as db:
        _seed_filing_evidence_for_case(db, case_id=case_data["id"], marker="filing-date")

    payload = _submit_batch(
        client,
        auth_headers,
        case_id=case_data["id"],
        submitted_date="2026-03-10",
    )

    with session_factory() as db:
        task = db.query(Task).filter(Task.id == payload["created_task_ids"][0]).one()
        expected_due = date(2026, 3, 8) + timedelta(days=20)
        assert task.base_date == date(2026, 3, 8)
        assert task.due_date == expected_due
        assert task.internal_due_date == expected_due - timedelta(days=5)
        assert task.remind1 == expected_due - timedelta(days=2)
        assert task.remind2 == expected_due - timedelta(days=4)
        assert task.remind3 == expected_due - timedelta(days=6)
        assert task.daily_remind is True
        assert task.daily_remind_from == expected_due - timedelta(days=6)


def test_batch_filing_apply_fee_limit_keeps_case_event_base_source(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _configure_template(session_factory, TaskDeadlineBase.CASE_EVENT)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_not_filed_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    _create_filing_materials(client, auth_headers, case_id=case_data["id"])
    _start_filing_preparation(client, auth_headers, case_id=case_data["id"])
    with session_factory() as db:
        _seed_filing_evidence_for_case(db, case_id=case_data["id"], marker="case-event")

    payload = _submit_batch(
        client,
        auth_headers,
        case_id=case_data["id"],
        submitted_date="2026-03-10",
    )

    with session_factory() as db:
        task = db.query(Task).filter(Task.id == payload["created_task_ids"][0]).one()
        assert task.base_date == date(2026, 3, 10)
        assert task.due_date == date(2026, 3, 30)
