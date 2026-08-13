from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"CASE-GATE-AP-{suffix}",
            "name_cn": f"案件文件门禁申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    applicant = _create_applicant(client, auth_headers)
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"CASE-GATE-{uuid4().hex[:8].upper()}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "案件文件门禁测试案件",
            "no_power": True,
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
    assert response.status_code == 201, response.text
    return response.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    title: str,
) -> dict:
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": None,
            "doc_type": "CLIENT_IN",
            "direction": "IN",
            "doc_date": "2026-04-03",
            "title": title,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_case_document_gate_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/cases/missing/document-gate")

    assert response.status_code == 401


def test_case_document_gate_returns_material_checks_and_file_events(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case_data = _create_case(client, auth_headers)
    request_doc = _create_document(
        client,
        auth_headers,
        case_id=case_data["id"],
        title="发明专利请求书",
    )
    spec_doc = _create_document(
        client,
        auth_headers,
        case_id=case_data["id"],
        title="说明书",
    )

    response = client.get(
        f"/api/v1/cases/{case_data['id']}/document-gate",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["case_type"] == "NORMAL"
    assert payload["patent_category"] == "INV"
    assert payload["conclusion"] == "BLOCKED"
    assert payload["material_count"] == 2
    assert [item["requirement_code"] for item in payload["missing_items"]] == [
        "CLAIMS",
        "ABSTRACT",
    ]

    check_by_code = {item["requirement_code"]: item for item in payload["checks"]}
    assert check_by_code["APPLICATION_REQUEST"]["matched_documents"][0]["id"] == request_doc["id"]
    assert check_by_code["SPECIFICATION"]["matched_documents"][0]["id"] == spec_doc["id"]

    event_by_id = {event["document_id"]: event for event in payload["file_events"]}
    assert event_by_id[request_doc["id"]]["event_status"] == "REGISTERED"
    assert event_by_id[request_doc["id"]]["title"] == "发明专利请求书"
    assert event_by_id[spec_doc["id"]]["event_status"] == "REGISTERED"


def test_case_document_gate_returns_404_for_missing_case(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        f"/api/v1/cases/{uuid4()}/document-gate",
        headers=auth_headers,
    )

    assert response.status_code == 404
