from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

BASE = "/api/v1/documents/wizard/task-preview"
CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"


def _unique_case_no() -> str:
    return f"WZT-{uuid4().hex[:8].upper()}"


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    resp = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"WZT-AP-{suffix}",
            "name_cn": f"Wizard任务预览申请人-{suffix}",
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
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Wizard Task Preview Case",
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


def _get_template(client: TestClient, auth_headers: dict, code: str) -> dict:
    resp = client.get(DOC_TMPL_BASE, headers=auth_headers, params={"q": code, "page_size": 100})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    match = [item for item in items if item["code"] == code]
    assert match, f"template {code} not found"
    return match[0]


def test_document_wizard_task_preview_success(client: TestClient, auth_headers: dict) -> None:
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
            "rows": [
                {"case_id": case_one["id"], "title": "第一次审查意见通知书"},
            ],
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total_candidates"] == 1
    item = payload["items"][0]
    assert item["row_index"] == 1
    assert item["case_id"] == case_one["id"]
    assert item["case_no"] == case_one["case_no"]
    assert item["task_template_code"] == "OA_REPLY"
    assert item["document_title"] == "第一次审查意见通知书"
    assert item["due_date"] == (date(2026, 1, 15) + timedelta(days=120)).isoformat()


def test_document_wizard_task_preview_returns_empty_for_non_deadline_template(
    client: TestClient,
    auth_headers: dict,
) -> None:
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
                {"case_id": case_one["id"], "title": "客户来函"},
            ],
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total_candidates"] == 0
    assert payload["items"] == []
