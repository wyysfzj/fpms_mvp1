from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

BASE = "/api/v1/documents/dispatch/mailing/batch-register"
CASE_BASE = "/api/v1/cases"
DOC_BASE = "/api/v1/documents"


def _unique_case_no() -> str:
    return f"MAIL-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Mail Test Case",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    direction: str,
    title: str,
) -> dict:
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": None,
            "direction": direction,
            "doc_date": "2026-01-15",
            "title": title,
            "ref_no": None,
            "extra_data": None,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_batch_mailing_registration_updates_selected_documents(
    client: TestClient, auth_headers: dict
) -> None:
    case = _create_case(client, auth_headers)
    doc_one = _create_document(
        client,
        auth_headers,
        case_id=case["id"],
        direction="OUT",
        title="第一份去文",
    )
    doc_two = _create_document(
        client,
        auth_headers,
        case_id=case["id"],
        direction="OUT",
        title="第二份去文",
    )

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "selected_document_ids": [doc_one["id"], doc_two["id"]],
            "outgoing_reg_no": "SG123456789CN",
            "forward_date": "2026-01-16",
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["success_count"] == 2
    assert payload["failure_count"] == 0
    assert len(payload["items"]) == 2

    returned = {item["document_id"]: item for item in payload["items"]}
    assert returned[doc_one["id"]]["outgoing_reg_no"] == "SG123456789CN"
    assert returned[doc_two["id"]]["outgoing_reg_no"] == "SG123456789CN"
    assert returned[doc_one["id"]]["forward_date"] == "2026-01-16"
    assert returned[doc_two["id"]]["forward_date"] == "2026-01-16"


def test_batch_mailing_registration_rejects_incoming_documents(
    client: TestClient, auth_headers: dict
) -> None:
    case = _create_case(client, auth_headers)
    incoming_doc = _create_document(
        client,
        auth_headers,
        case_id=case["id"],
        direction="IN",
        title="来文",
    )

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "selected_document_ids": [incoming_doc["id"]],
            "outgoing_reg_no": "SG123456789CN",
            "forward_date": "2026-01-16",
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_MAILING_DIRECTION_INVALID"
