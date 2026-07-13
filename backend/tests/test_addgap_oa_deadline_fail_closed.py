from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import Document
from app.modules.tasks.models import Task, TaskTemplate


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-OA-DUE-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "OA 明确期限失败关闭测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _get_oa_template(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": "OA_IN", "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == "OA_IN"]
    assert len(matches) == 1
    return matches[0]


def _create_document_template(
    client: TestClient,
    auth_headers: dict[str, str],
    **overrides,
) -> dict:
    payload = {
        "code": f"ADDGAP_OA_DUE_{uuid4().hex[:8].upper()}",
        "name": "期限任务覆盖测试模板",
        "direction": "IN",
        **overrides,
    }
    response = client.post("/api/v1/doc-templates", headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _ensure_task_template(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    code: str,
    name: str,
) -> dict:
    listed = client.get("/api/v1/task-templates", headers=auth_headers)
    assert listed.status_code == 200, listed.text
    existing = [item for item in listed.json() if item["code"] == code]
    if existing:
        assert len(existing) == 1
        return existing[0]

    created = client.post(
        "/api/v1/task-templates",
        headers=auth_headers,
        json={"code": code, "name": name},
    )
    assert created.status_code == 201, created.text
    return created.json()


def test_executable_oa_document_without_explicit_due_fails_closed(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    ref_no = f"ADDGAP-OA-DUE-MISSING-{uuid4().hex[:8].upper()}"

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "缺少官方期限的 OA 文书",
            "ref_no": ref_no,
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_OFFICIAL_DUE_DATE_REQUIRED"
    with session_factory() as db:
        document = db.execute(
            select(Document).where(Document.ref_no == ref_no)
        ).scalar_one_or_none()
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one_or_none()
        assert document is None
        assert task is None


def test_executable_oa_document_with_conflicting_due_tuple_fails_closed(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    ref_no = f"ADDGAP-OA-DUE-CONFLICT-{uuid4().hex[:8].upper()}"

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "期限元组冲突的 OA 文书",
            "ref_no": ref_no,
            "extra_data": json.dumps(
                {
                    "OfficialDueDate": "2026-10-10",
                    "OfficialDueDateStatus": "CONFIRMED",
                }
            ),
        },
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_DEADLINE_INVALID"
    with session_factory() as db:
        document = db.execute(
            select(Document).where(Document.ref_no == ref_no)
        ).scalar_one_or_none()
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one_or_none()
        assert document is None
        assert task is None


def test_executable_oa_document_with_unconfirmed_due_fails_closed(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    ref_no = f"ADDGAP-OA-DUE-UNCONFIRMED-{uuid4().hex[:8].upper()}"

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "官方期限待确认的 OA 文书",
            "ref_no": ref_no,
            "extra_data": json.dumps(
                {
                    "OfficialDueDate": "2026-10-10",
                    "OfficialDueDateSource": "IMPORTED_OFFICIAL_NOTICE",
                    "OfficialDueDateStatus": "NEEDS_CONFIRMATION",
                }
            ),
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_OFFICIAL_DUE_DATE_REQUIRED"
    with session_factory() as db:
        document = db.execute(
            select(Document).where(Document.ref_no == ref_no)
        ).scalar_one_or_none()
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one_or_none()
        assert document is None
        assert task is None


def test_executable_oa_task_uses_confirmed_explicit_due_without_template_fallback(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_oa_template(client, auth_headers)
    explicit_due = date(2026, 10, 10)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "已确认官方期限的 OA 文书",
            "extra_data": json.dumps(
                {
                    "OfficialDueDate": explicit_due.isoformat(),
                    "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                    "OfficialDueDateStatus": "CONFIRMED",
                }
            ),
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one()
        assert task.due_date == explicit_due


def test_subsequent_oa_identity_uses_confirmed_explicit_due(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    explicit_due = date(2026, 11, 20)
    _ensure_task_template(
        client,
        auth_headers,
        code="OA_REPLY_SUBSEQUENT",
        name="后续审查意见答复期限",
    )
    template = _create_document_template(
        client,
        auth_headers,
        status_effect="OA2",
        deadline_template_code="OA_REPLY_SUBSEQUENT",
        need_reply=True,
        input_fields=json.dumps(
            {
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "OA_REPLY",
                "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                "archive_status_restore": "SUB_EXAM",
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "canonical_template_code": "OA_IN",
            }
        ),
    )

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "后续 OA 已确认官方期限",
            "extra_data": json.dumps(
                {
                    "OfficialDueDate": explicit_due.isoformat(),
                    "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                    "OfficialDueDateStatus": "CONFIRMED",
                }
            ),
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one()
        task_template = db.execute(
            select(TaskTemplate).where(TaskTemplate.id == task.task_template_id)
        ).scalar_one()
        assert task_template.code == "OA_REPLY_SUBSEQUENT"
        assert task.due_date == explicit_due


def test_non_oa_task_keeps_template_deadline_fallback(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_document_template(
        client,
        auth_headers,
        deadline_template_code="GRANT_FEE",
    )

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "普通非 OA 期限任务",
        },
    )

    assert response.status_code == 201, response.text
    with session_factory() as db:
        task = db.execute(
            select(Task).where(Task.case_id == case["id"], Task.status == "OPEN")
        ).scalar_one()
        task_template = db.execute(
            select(TaskTemplate).where(TaskTemplate.id == task.task_template_id)
        ).scalar_one()
        assert task_template.code == "GRANT_FEE"
        assert task.due_date == date(2026, 9, 8)
