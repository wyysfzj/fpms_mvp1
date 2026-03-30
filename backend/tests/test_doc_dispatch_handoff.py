from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

BASE = "/api/v1/documents/dispatches"
CASE_BASE = "/api/v1/cases"
CLIENT_BASE = "/api/v1/clients"
DOC_BASE = "/api/v1/documents"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_suffix: str) -> dict:
    resp = client.post(
        CLIENT_BASE,
        headers=auth_headers,
        json={
            "client_code": _unique("CLI"),
            "name_cn": f"交接单客户-{name_suffix}",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client: TestClient, auth_headers: dict[str, str], *, client_id: str, case_no_prefix: str
) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique(case_no_prefix),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "交接单测试案件",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    title: str,
    direction: str = "OUT",
) -> dict:
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": None,
            "direction": direction,
            "doc_date": "2026-01-16",
            "title": title,
            "ref_no": None,
            "extra_data": None,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_document_dispatch_success(client: TestClient, auth_headers: dict[str, str]) -> None:
    client_a = _create_client(client, auth_headers, name_suffix="A")
    case_a = _create_case(client, auth_headers, client_id=client_a["id"], case_no_prefix="DSP")
    doc_one = _create_document(client, auth_headers, case_id=case_a["id"], title="第一份去文")
    doc_two = _create_document(client, auth_headers, case_id=case_a["id"], title="第二份去文")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "client_id": client_a["id"],
            "dispatch_date": "2026-01-18",
            "remark": "批量交接",
            "selected_document_ids": [doc_one["id"], doc_two["id"]],
        },
    )

    assert resp.status_code == 201, resp.text
    payload = resp.json()
    assert payload["client_id"] == client_a["id"]
    assert payload["dispatch_date"] == "2026-01-18"
    assert payload["remark"] == "批量交接"
    assert len(payload["lines"]) == 2

    line_doc_ids = {line["document_id"] for line in payload["lines"]}
    assert line_doc_ids == {doc_one["id"], doc_two["id"]}
    assert {line["case_id"] for line in payload["lines"]} == {case_a["id"]}
    assert {line["case_no"] for line in payload["lines"]} == {case_a["case_no"]}
    assert {line["doc_name"] for line in payload["lines"]} == {"第一份去文", "第二份去文"}

    detail = client.get(f"{BASE}/{payload['id']}", headers=auth_headers)
    assert detail.status_code == 200, detail.text
    detail_payload = detail.json()
    assert detail_payload["id"] == payload["id"]
    assert len(detail_payload["lines"]) == 2


def test_create_document_dispatch_rejects_mixed_clients(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_a = _create_client(client, auth_headers, name_suffix="A")
    client_b = _create_client(client, auth_headers, name_suffix="B")
    case_a = _create_case(client, auth_headers, client_id=client_a["id"], case_no_prefix="DSPA")
    case_b = _create_case(client, auth_headers, client_id=client_b["id"], case_no_prefix="DSPB")
    doc_one = _create_document(client, auth_headers, case_id=case_a["id"], title="A 去文")
    doc_two = _create_document(client, auth_headers, case_id=case_b["id"], title="B 去文")

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "client_id": client_a["id"],
            "dispatch_date": "2026-01-18",
            "selected_document_ids": [doc_one["id"], doc_two["id"]],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_DISPATCH_CLIENT_MISMATCH"


def test_create_document_dispatch_rejects_incoming_documents(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_a = _create_client(client, auth_headers, name_suffix="A")
    case_a = _create_case(client, auth_headers, client_id=client_a["id"], case_no_prefix="DSPI")
    incoming_doc = _create_document(
        client,
        auth_headers,
        case_id=case_a["id"],
        title="来文",
        direction="IN",
    )

    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "client_id": client_a["id"],
            "dispatch_date": "2026-01-18",
            "selected_document_ids": [incoming_doc["id"]],
        },
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "DOCUMENT_DISPATCH_DIRECTION_INVALID"
