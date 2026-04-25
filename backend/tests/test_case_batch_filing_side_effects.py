from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.masterdata.applicants.models import Applicant
from app.modules.tasks.models import Task, TaskLog, TaskTemplate


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_cn: str) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"BFS2-CL-{uuid4().hex[:8]}",
            "name_cn": name_cn,
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory, *, name_cn: str = "批量递交申请人") -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"BFS2-AP-{uuid4().hex[:8]}",
                name_cn=f"{name_cn}-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    case_no_prefix: str,
    recv_date: str,
    has_exam_request: bool | None = None,
) -> dict:
    payload = {
        "case_no": f"{case_no_prefix}-{uuid4().hex[:8]}",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": f"{case_no_prefix} 标题",
        "status": "NOT_FILED",
        "recv_date": recv_date,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": "批量递交申请人",
            }
        ],
    }
    if has_exam_request is not None:
        payload["has_exam_request"] = has_exam_request

    response = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def _submit_batch_filing(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_ids: list[str],
    submitted_date: str = "2026-03-10",
    generate_list: bool,
    apply_exam_now: bool = True,
):
    return client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": case_ids,
            "submitted_date": submitted_date,
            "apply_exam_now": apply_exam_now,
            "generate_list": generate_list,
        },
        headers=auth_headers,
    )


def _apply_fee_limit_tasks(db, case_ids: list[str]) -> list[Task]:
    return (
        db.query(Task)
        .join(TaskTemplate, Task.task_template_id == TaskTemplate.id)
        .filter(Task.case_id.in_(case_ids), TaskTemplate.code == "APPLY_FEE_LIMIT")
        .order_by(Task.case_id.asc(), Task.created_at.asc())
        .all()
    )


def test_batch_filing_generate_list_creates_documents_and_apply_fee_tasks(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批量递交副作用客户")
    applicant_id = _seed_applicant(session_factory)
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="BFS2A",
        recv_date="2026-03-01",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="BFS2B",
        recv_date="2026-03-02",
        has_exam_request=False,
    )

    response = _submit_batch_filing(
        client,
        auth_headers,
        case_ids=[case_a["id"], case_b["id"]],
        generate_list=True,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success_count"] == 2
    assert payload["failure_count"] == 0
    assert set(payload["updated_case_ids"]) == {case_a["id"], case_b["id"]}
    assert len(payload["document_ids"]) == 2
    assert len(payload["created_task_ids"]) == 2

    with session_factory() as db:
        refreshed_cases = db.query(Case).filter(Case.id.in_([case_a["id"], case_b["id"]])).all()
        assert {case.status for case in refreshed_cases} == {"WAITING_RECEIPT"}
        assert {case.submitted_date for case in refreshed_cases} == {date(2026, 3, 10)}
        assert {case.has_exam_request for case in refreshed_cases} == {True}

        documents = (
            db.query(Document)
            .filter(Document.id.in_(payload["document_ids"]))
            .order_by(Document.case_id.asc())
            .all()
        )
        assert len(documents) == 2
        assert {document.case_id for document in documents} == {case_a["id"], case_b["id"]}
        for document in documents:
            assert document.direction == "OUT"
            assert document.doc_type == "OFFICIAL_OUT"
            assert document.doc_date == date(2026, 3, 10)
            assert "批量递交清单" in document.title
            assert document.ref_no.startswith("BATCH-FILING-2026-03-10-")
            extra_data = json.loads(document.extra_data)
            assert extra_data["source"] == "batch_filing"
            assert set(extra_data["selected_case_ids"]) == {case_a["id"], case_b["id"]}

        tasks = _apply_fee_limit_tasks(db, [case_a["id"], case_b["id"]])
        assert len(tasks) == 2
        assert {task.id for task in tasks} == set(payload["created_task_ids"])
        for task in tasks:
            assert task.status == "OPEN"
            assert task.title == "申请费时限"
            assert task.base_date == date(2026, 3, 10)
            assert task.due_date is not None
            assert task.internal_due_date is not None
            log = db.query(TaskLog).filter(TaskLog.task_id == task.id).one()
            assert log.action == "AUTO_CREATE"
            assert log.to_status == "OPEN"


def test_batch_filing_generate_list_false_skips_documents_but_creates_tasks(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批量递交不生成清单客户")
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="BFS2N",
        recv_date="2026-03-01",
    )

    response = _submit_batch_filing(
        client,
        auth_headers,
        case_ids=[case_data["id"]],
        generate_list=False,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["document_ids"] == []
    assert len(payload["created_task_ids"]) == 1

    with session_factory() as db:
        documents = (
            db.query(Document)
            .filter(Document.case_id == case_data["id"], Document.title.like("%批量递交清单%"))
            .all()
        )
        assert documents == []
        assert len(_apply_fee_limit_tasks(db, [case_data["id"]])) == 1


def test_batch_filing_reuses_existing_apply_fee_limit_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批量递交幂等任务客户")
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="BFS2I",
        recv_date="2026-03-01",
    )
    with session_factory() as db:
        template = (
            db.query(TaskTemplate).filter(TaskTemplate.code == "APPLY_FEE_LIMIT").one_or_none()
        )
        if template is None:
            template = TaskTemplate(
                id=str(uuid4()),
                code="APPLY_FEE_LIMIT",
                name="申请费时限",
                add_days=30,
                inner_offset_days=7,
            )
            db.add(template)
            db.flush()
        existing_task = Task(
            id=str(uuid4()),
            case_id=case_data["id"],
            task_template_id=template.id,
            title=template.name,
            base_date=date(2026, 3, 1),
            due_date=date(2026, 3, 31),
            internal_due_date=date(2026, 3, 24),
            status="OPEN",
        )
        db.add(existing_task)
        existing_task_id = existing_task.id
        db.commit()

    response = _submit_batch_filing(
        client,
        auth_headers,
        case_ids=[case_data["id"]],
        generate_list=True,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["created_task_ids"] == []

    with session_factory() as db:
        tasks = _apply_fee_limit_tasks(db, [case_data["id"]])
        assert len(tasks) == 1
        assert tasks[0].id == existing_task_id


def test_batch_filing_validation_failure_creates_no_side_effects(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批量递交失败无副作用客户")
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="BFS2F",
        recv_date="2026-03-20",
    )

    response = _submit_batch_filing(
        client,
        auth_headers,
        case_ids=[case_data["id"]],
        submitted_date="2026-03-10",
        generate_list=True,
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "CASE_BATCH_FILING_SUBMITTED_DATE_INVALID"

    with session_factory() as db:
        documents = (
            db.query(Document)
            .filter(Document.case_id == case_data["id"], Document.title.like("%批量递交清单%"))
            .all()
        )
        assert documents == []
        assert _apply_fee_limit_tasks(db, [case_data["id"]]) == []
        refreshed_case = db.query(Case).filter(Case.id == case_data["id"]).one()
        assert refreshed_case.status == "NOT_FILED"
