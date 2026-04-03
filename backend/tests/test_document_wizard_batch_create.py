from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.tasks.models import Task

BASE = "/api/v1/documents/wizard/batch-create"
CASE_BASE = "/api/v1/cases"
DOC_BASE = "/api/v1/documents"
DOC_TMPL_BASE = "/api/v1/doc-templates"


def _unique_case_no() -> str:
    return f"WZ-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Wizard Test Case",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template(client: TestClient, auth_headers: dict, code: str) -> dict:
    resp = client.get(DOC_TMPL_BASE, headers=auth_headers, params={"q": code, "page_size": 100})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    match = [item for item in items if item["code"] == code]
    assert match, f"template {code} not found"
    return match[0]


def _preview_task_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    case_id: str,
    title: str,
) -> dict:
    resp = client.post(
        "/api/v1/documents/wizard/task-preview",
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_id, "title": title}],
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_batch_create_documents_success(client: TestClient, auth_headers: dict) -> None:
    case_one = _create_case(client, auth_headers)
    case_two = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [
                {"case_id": case_one["id"], "title": "第一份批量文件"},
                {"case_id": case_two["id"], "title": "第二份批量文件"},
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 2
    assert len(payload["items"]) == 2

    documents = [row["document"] for row in payload["items"]]
    assert {doc["case_id"] for doc in documents} == {case_one["id"], case_two["id"]}
    assert all(doc["doc_template_id"] == template["id"] for doc in documents)

    single_resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_one["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "单条文件",
        },
    )
    assert single_resp.status_code == 201, single_resp.text


def test_batch_create_documents_uses_step3_task_rows(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    preview = _preview_task_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        case_id=case_one["id"],
        title="OA 收文任务",
    )
    assert preview["total_candidates"] == 1
    preview_item = preview["items"][0]
    expected_due_date = preview_item["due_date"][:10]
    expected_internal_due_date = "2026-05-01"

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "OA 收文文书"}],
            "task_rows": [
                {
                    "row_index": preview_item["row_index"],
                    "case_id": case_one["id"],
                    "task_template_code": preview_item["task_template_code"],
                    "title": "手动任务标题",
                    "internal_due_date": expected_internal_due_date,
                    "remind1": "2026-04-30",
                    "remind2": "2026-04-28",
                    "remind3": "2026-04-26",
                }
            ],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["created"] == 1

    tasks_resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": case_one["id"], "page_size": 100},
    )
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks_payload = tasks_resp.json()
    assert tasks_payload["total"] == 1
    task = tasks_payload["items"][0]
    assert task["title"] == "手动任务标题"
    assert task["due_date"] == expected_due_date
    assert task["internal_due_date"] == expected_internal_due_date
    assert task["case_id"] == case_one["id"]

    with session_factory() as db:
        created_task = db.query(Task).filter(Task.id == task["id"]).one()
        assert created_task.remind1.isoformat() == "2026-04-30"
        assert created_task.remind2.isoformat() == "2026-04-28"
        assert created_task.remind3.isoformat() == "2026-04-26"
        assert created_task.daily_remind is False


def test_batch_create_documents_rejects_invalid_row(client: TestClient, auth_headers: dict) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "CLIENT_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [
                {"case_id": case_one["id"], "title": "有效行"},
                {"case_id": str(uuid4()), "title": "无效行"},
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]


def test_batch_create_documents_rejects_invalid_step3_task_row(
    client: TestClient, auth_headers: dict
) -> None:
    case_one = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [{"case_id": case_one["id"], "title": "OA 收文文书"}],
            "task_rows": [
                {
                    "row_index": 2,
                    "case_id": case_one["id"],
                    "task_template_code": "OA_REPLY",
                    "title": "无效任务行",
                }
            ],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_WIZARD_BATCH_INVALID"
    assert payload["error"]["details"]["row_errors"]
