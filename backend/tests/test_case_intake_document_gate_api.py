from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _create_applicant(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"INTAKE-GATE-AP-{suffix}",
            "name_cn": f"收案门禁申请人-{suffix}",
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
            "case_no": f"INTAKE-GATE-{uuid4().hex[:8].upper()}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "收案门禁测试案件",
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
            "doc_date": "2026-04-01",
            "title": title,
            "ref_no": None,
            "extra_data": None,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_intake_document_gate_requires_auth(client: TestClient) -> None:
    response = client.get(
        "/api/v1/cases/document-gate/intake-preview",
        params={
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
        },
    )

    assert response.status_code == 401


def test_intake_document_gate_returns_missing_materials_without_sources(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/api/v1/cases/document-gate/intake-preview",
        headers=auth_headers,
        params={
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "no_power": True,
            "has_priority": False,
            "has_exam_request": False,
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["conclusion"] == "BLOCKED"
    assert payload["hard_block"] is True
    assert payload["material_count"] == 0
    assert {
        item["requirement_code"] for item in payload["missing_items"] if item["blocks_submission"]
    } == {"APPLICATION_REQUEST", "SPECIFICATION", "CLAIMS", "ABSTRACT"}
    assert payload["suggested_actions"] == ["补齐硬性递交材料后再递交"]


def test_intake_document_gate_matches_existing_source_documents(
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
        "/api/v1/cases/document-gate/intake-preview",
        headers=auth_headers,
        params=[
            ("case_type", "NORMAL"),
            ("patent_category", "INV"),
            ("flow_dir", "CN_DOMESTIC"),
            ("no_power", "true"),
            ("has_priority", "false"),
            ("has_exam_request", "false"),
            ("source_document_ids", request_doc["id"]),
            ("source_document_ids", spec_doc["id"]),
        ],
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["conclusion"] == "BLOCKED"
    assert payload["material_count"] == 2

    check_by_code = {item["requirement_code"]: item for item in payload["checks"]}
    assert check_by_code["APPLICATION_REQUEST"]["status"] == "MATCHED"
    assert check_by_code["APPLICATION_REQUEST"]["matched_documents"][0]["id"] == request_doc["id"]
    assert check_by_code["SPECIFICATION"]["status"] == "MATCHED"
    assert check_by_code["SPECIFICATION"]["matched_documents"][0]["id"] == spec_doc["id"]
    assert [item["requirement_code"] for item in payload["missing_items"]] == [
        "CLAIMS",
        "ABSTRACT",
    ]
