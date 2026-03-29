from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

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
