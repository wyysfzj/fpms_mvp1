from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

PREVIEW_URL = "/api/v1/documents/impact-preview"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-DUE-PREVIEW-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "期限影响预览测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _get_template(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": code, "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == code]
    assert len(matches) == 1
    return matches[0]


def _preview_payload(case_id: str, template_id: str) -> dict:
    return {
        "case_id": case_id,
        "doc_template_id": template_id,
        "direction": "IN",
        "doc_date": "2026-07-11",
        "title": "第一次审查意见通知书",
    }


def test_impact_preview_reports_confirmed_explicit_due_lineage(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")
    payload = {
        **_preview_payload(case["id"], template["id"]),
        "official_due_date": "2026-10-11",
        "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
        "official_due_date_status": "CONFIRMED",
        "description": "已根据官文核对",
    }

    response = client.post(PREVIEW_URL, headers=auth_headers, json=payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["official_due_date"] == "2026-10-11"
    assert body["official_due_date_source"] == "MANUAL_OFFICIAL_NOTICE"
    assert body["official_due_date_status"] == "CONFIRMED"
    assert body["description"] == "已根据官文核对"
    due_impacts = [item for item in body["deadline_impacts"] if item["kind"] == "OFFICIAL_DUE_DATE"]
    assert len(due_impacts) == 1
    assert due_impacts[0]["effect"] == "2026-10-11"
    assert "MANUAL_OFFICIAL_NOTICE" in due_impacts[0]["detail"]
    assert "CONFIRMED" in due_impacts[0]["detail"]


@pytest.mark.parametrize(
    "deadline_fields, expected_status",
    [
        ({}, None),
        (
            {
                "official_due_date": "2026-10-11",
                "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
                "official_due_date_status": "NEEDS_CONFIRMATION",
            },
            "NEEDS_CONFIRMATION",
        ),
    ],
)
def test_impact_preview_blocks_executable_oa_without_confirmed_due(
    client: TestClient,
    auth_headers: dict[str, str],
    deadline_fields: dict,
    expected_status: str | None,
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")

    response = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json={
            **_preview_payload(case["id"], template["id"]),
            **deadline_fields,
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"] == {
        "code": "OA_OFFICIAL_DUE_DATE_REQUIRED",
        "message": "Executable notice preview requires a confirmed explicit official due date",
        "details": {"status": expected_status},
    }


def test_impact_preview_preserves_deadline_validation_status_codes(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "OA_IN")
    base_payload = _preview_payload(case["id"], template["id"])

    incomplete = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json={**base_payload, "official_due_date": "2026-10-11"},
    )
    malformed = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json={
            **base_payload,
            "official_due_date": "2026-10-11",
            "official_due_date_source": "UNKNOWN_SOURCE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert incomplete.status_code == 400, incomplete.text
    assert incomplete.json()["error"]["code"] == "DOCUMENT_DEADLINE_INVALID"
    assert malformed.status_code == 422, malformed.text


def test_impact_preview_uses_grant_deadline_blocker_without_guessing(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _get_template(client, auth_headers, "GRANT_NOTICE")

    response = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json=_preview_payload(case["id"], template["id"]),
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "GRANT_OFFICIAL_DUE_DATE_REQUIRED"
