from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.applicants.models import Applicant
from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase
from app.modules.tasks.models import Task, TaskLog, TaskTemplate
from tests.test_v8_batch_filing_lifecycle_adapter import (
    _seed_filing_evidence_for_case,
    _start_filing_preparation,
)


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"AFL-CL-{uuid4().hex[:8]}",
            "name_cn": "申请费时限客户",
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
                code=f"AFL-AP-{uuid4().hex[:8]}",
                name_cn=f"申请费时限申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _configure_apply_fee_limit_template(session_factory) -> str:
    with session_factory() as db:
        admin = db.query(T_User).filter(T_User.username == "admin").one()
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
        template.deadline_base = TaskDeadlineBase.CASE_EVENT
        template.add_days = 30
        template.add_months = 0
        template.inner_offset_days = 7
        template.remind_base = TaskRemindBase.INNER
        template.remind_1_offset_days = 1
        template.remind_2_offset_days = 3
        template.remind_3_offset_days = 5
        template.daily_remind = True
        template.default_worker_role = "Admin"
        template.default_supervisor_id = admin.id
        db.commit()
        return admin.id


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"AFL-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "申请费时限测试案",
            "recv_date": "2026-03-01",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "申请费时限申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


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


def test_batch_filing_apply_fee_limit_task_uses_template_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    assignee_id = _configure_apply_fee_limit_template(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    _create_filing_materials(client, auth_headers, case_id=case_data["id"])
    _start_filing_preparation(client, auth_headers, case_id=case_data["id"])
    with session_factory() as db:
        _seed_filing_evidence_for_case(db, case_id=case_data["id"], marker="task-fields")

    response = client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": [case_data["id"]],
            "submitted_date": "2026-03-10",
            "apply_exam_now": False,
            "generate_list": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload["created_task_ids"]) == 1

    with session_factory() as db:
        refreshed_case = db.query(Case).filter(Case.id == case_data["id"]).one()
        assert refreshed_case.status == "WAITING_RECEIPT"

        task = db.query(Task).filter(Task.id == payload["created_task_ids"][0]).one()
        expected_due = date(2026, 3, 10) + timedelta(days=30)
        expected_internal_due = expected_due - timedelta(days=7)
        assert task.base_date == date(2026, 3, 10)
        assert task.due_date == expected_due
        assert task.internal_due_date == expected_internal_due
        assert task.remind1 == expected_internal_due - timedelta(days=1)
        assert task.remind2 == expected_internal_due - timedelta(days=3)
        assert task.remind3 == expected_internal_due - timedelta(days=5)
        assert task.daily_remind is True
        assert task.daily_remind_from == expected_internal_due - timedelta(days=5)
        assert task.worker_id == assignee_id
        assert task.supervisor_id == assignee_id
        assert task.status == "OPEN"

        log = db.query(TaskLog).filter(TaskLog.task_id == task.id).one()
        assert log.action == "AUTO_CREATE"
        assert log.from_status is None
        assert log.to_status == "OPEN"
