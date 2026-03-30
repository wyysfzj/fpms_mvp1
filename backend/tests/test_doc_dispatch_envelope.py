from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

API = "/api/v1"
DOC_BASE = f"{API}/documents"
CASE_BASE = f"{API}/cases"
CLIENT_BASE = f"{API}/clients"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str], *, suffix: str) -> dict:
    resp = client.post(
        CLIENT_BASE,
        headers=auth_headers,
        json={
            "client_code": _unique("CLI"),
            "name_cn": f"信封客户-{suffix}",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_client_address(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    address_line1: str,
    is_default: bool = False,
) -> dict:
    resp = client.post(
        f"{CLIENT_BASE}/{client_id}/addresses",
        headers=auth_headers,
        json={
            "address_type": "MAILING",
            "address_line1": address_line1,
            "city": "Shanghai",
            "province": "Shanghai",
            "postal_code": "200000",
            "country_code": "CN",
            "is_default": is_default,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_no_prefix: str,
    doc_address_id: str | None = None,
    applicant_address: str | None = None,
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
            "doc_address_id": doc_address_id,
            "title_cn": "信封测试案件",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "name_cn": "第一申请人",
                    "address_cn": applicant_address,
                }
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
) -> dict:
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": None,
            "direction": "OUT",
            "doc_date": "2026-01-18",
            "title": "信封预览去文",
            "ref_no": "DOC-ENV-001",
            "extra_data": None,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _preview(client: TestClient, auth_headers: dict[str, str], *, document_id: str) -> dict:
    resp = client.get(f"{DOC_BASE}/{document_id}/envelope-preview", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_envelope_preview_prefers_case_doc_address(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_row = _create_client(client, auth_headers, suffix="DOC")
    doc_address = _create_client_address(
        client,
        auth_headers,
        client_id=client_row["id"],
        address_line1="Case Doc Address Road",
    )
    _create_client_address(
        client,
        auth_headers,
        client_id=client_row["id"],
        address_line1="Client Default Lane",
        is_default=True,
    )
    case = _create_case(
        client,
        auth_headers,
        client_id=client_row["id"],
        case_no_prefix="ENV-DOC",
        doc_address_id=doc_address["id"],
        applicant_address="Applicant Lane",
    )
    document = _create_document(client, auth_headers, case_id=case["id"])

    payload = _preview(client, auth_headers, document_id=document["id"])

    assert payload["document_id"] == document["id"]
    assert payload["case_id"] == case["id"]
    assert payload["case_no"] == case["case_no"]
    assert payload["address_source"] == "CASE_DOC_ADDRESS"
    assert payload["recipient_name"] == client_row["name_cn"]
    assert "Case Doc Address Road" in payload["recipient_address"]


def test_envelope_preview_falls_back_to_default_client_address(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_row = _create_client(client, auth_headers, suffix="DEFAULT")
    _create_client_address(
        client,
        auth_headers,
        client_id=client_row["id"],
        address_line1="Default Mailing Road",
        is_default=True,
    )
    case = _create_case(
        client,
        auth_headers,
        client_id=client_row["id"],
        case_no_prefix="ENV-DEF",
        applicant_address="Applicant Lane",
    )
    document = _create_document(client, auth_headers, case_id=case["id"])

    payload = _preview(client, auth_headers, document_id=document["id"])

    assert payload["address_source"] == "CLIENT_DEFAULT_ADDRESS"
    assert payload["recipient_name"] == client_row["name_cn"]
    assert "Default Mailing Road" in payload["recipient_address"]


def test_envelope_preview_falls_back_to_first_applicant_address(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_row = _create_client(client, auth_headers, suffix="APPLICANT")
    case = _create_case(
        client,
        auth_headers,
        client_id=client_row["id"],
        case_no_prefix="ENV-APP",
        applicant_address="Applicant Address Road",
    )
    document = _create_document(client, auth_headers, case_id=case["id"])

    payload = _preview(client, auth_headers, document_id=document["id"])

    assert payload["address_source"] == "FIRST_APPLICANT_ADDRESS"
    assert payload["recipient_name"] == "第一申请人"
    assert "Applicant Address Road" in payload["recipient_address"]


def test_envelope_preview_requires_manual_address_when_no_sources(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_row = _create_client(client, auth_headers, suffix="MANUAL")
    case = _create_case(
        client,
        auth_headers,
        client_id=client_row["id"],
        case_no_prefix="ENV-MAN",
        applicant_address=None,
    )
    document = _create_document(client, auth_headers, case_id=case["id"])

    payload = _preview(client, auth_headers, document_id=document["id"])

    assert payload["address_source"] == "MANUAL_REQUIRED"
    assert payload["recipient_name"] is None
    assert payload["recipient_address"] is None
