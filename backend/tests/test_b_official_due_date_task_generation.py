from __future__ import annotations

import json
from uuid import uuid4

from fastapi.testclient import TestClient

CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"
WIZARD_TASK_PREVIEW_BASE = "/api/v1/documents/wizard/task-preview"
WIZARD_BATCH_CREATE_BASE = "/api/v1/documents/wizard/batch-create"


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    resp = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"BOD-AP-{suffix}",
            "name_cn": f"B官方绝限申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    applicant = _create_applicant(client, auth_headers)
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": f"BOD-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": "B官方绝限测试案",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant["id"],
                    "name_cn": applicant["name_cn"],
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    resp = client.get(DOC_TMPL_BASE, headers=auth_headers, params={"q": code, "page_size": 100})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    match = [item for item in items if item["code"] == code]
    assert match, f"template {code} not found"
    return match[0]


def _confirmed_due_extra_data(due_date: str) -> str:
    return json.dumps(
        {
            "OfficialDueDate": due_date,
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
        }
    )


def test_official_due_date_overrides_preview_due_date(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    resp = client.post(
        WIZARD_TASK_PREVIEW_BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
                "extra_data": _confirmed_due_extra_data("2026-03-20"),
            },
            "rows": [{"case_id": case["id"], "title": "官方绝限 OA"}],
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total_candidates"] == 1
    item = payload["items"][0]
    assert item["base_date"] == "2026-01-15"
    assert item["due_date"] == "2026-03-20"
    assert item["internal_due_date"] == "2026-03-06"


def test_official_due_date_overrides_created_task_due_date(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    resp = client.post(
        WIZARD_BATCH_CREATE_BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
                "extra_data": _confirmed_due_extra_data("2026-03-20"),
            },
            "rows": [{"case_id": case["id"], "title": "官方绝限 OA"}],
        },
    )

    assert resp.status_code == 201, resp.text
    tasks_resp = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"case_id": case["id"], "page_size": 100},
    )
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks = tasks_resp.json()["items"]
    assert len(tasks) == 1
    task_detail_resp = client.get(f"/api/v1/tasks/{tasks[0]['id']}", headers=auth_headers)
    assert task_detail_resp.status_code == 200, task_detail_resp.text
    task = task_detail_resp.json()
    assert task["base_date"] == "2026-01-15"
    assert task["due_date"] == "2026-03-20"
    assert task["internal_due_date"] == "2026-03-06"


def test_invalid_official_due_date_returns_stable_error(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    resp = client.post(
        WIZARD_TASK_PREVIEW_BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
                "extra_data": _confirmed_due_extra_data("2026-99-99"),
            },
            "rows": [{"case_id": case["id"], "title": "无效官方绝限 OA"}],
        },
    )

    assert resp.status_code == 422, resp.text
    assert resp.json()["error"]["code"] == "DOCUMENT_EXTRA_DATA_INVALID"
