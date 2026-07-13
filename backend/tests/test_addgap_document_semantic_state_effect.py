from __future__ import annotations

import json
from uuid import uuid4

from fastapi.testclient import TestClient


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-SEM-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "文档语义状态副作用测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_template(
    client: TestClient,
    auth_headers: dict[str, str],
    **overrides,
) -> dict:
    payload = {
        "code": f"CUSTOM_RAW_{uuid4().hex[:8].upper()}",
        "name": "第一次审查意见通知书",
        "direction": "IN",
        "status_effect": "OA1",
        "need_reply": True,
        **overrides,
    }
    response = client.post("/api/v1/doc-templates", headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _get_case(client: TestClient, auth_headers: dict[str, str], case_id: str) -> dict:
    response = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert response.status_code == 200, response.text
    return response.json()


def _oa_metadata() -> str:
    return json.dumps(
        {
            "catalog_kind": "OFFICIAL_NOTICE",
            "catalog_status": "EXECUTABLE",
            "execution_behavior": "OA_REPLY",
            "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
            "archive_status_restore": "SUB_EXAM",
            "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
            "canonical_template_code": "OA_IN",
        }
    )


def test_unknown_template_raw_fields_do_not_drive_document_or_case_state(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_template(client, auth_headers)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "显示名称和原始字段不得推断执行语义",
        },
    )

    assert response.status_code == 201, response.text
    assert response.json()["need_reply"] is False
    assert _get_case(client, auth_headers, case["id"])["status"] == "NOT_FILED"


def test_impact_preview_ignores_unknown_template_raw_state_fields(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_template(client, auth_headers)

    response = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "原始状态字段不得进入影响预览",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["status_impacts"] == []
    assert response.json()["file_status_impacts"] == []


def test_declared_oa_alias_drives_preview_document_and_case_state(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_template(
        client,
        auth_headers,
        code=f"OFFICIAL_NOTICE_ALIAS_{uuid4().hex[:8].upper()}",
        status_effect="OA1",
        deadline_template_code="OA_REPLY",
        need_reply=True,
        input_fields=_oa_metadata(),
    )

    preview = client.post(
        "/api/v1/documents/impact-preview",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "声明式 OA 影响预览",
            "official_due_date": "2026-10-10",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["status_impacts"][0]["effect"] == "OA1"
    assert preview.json()["file_status_impacts"][0]["kind"] == "NEED_REPLY"

    created = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "声明式 OA 文书",
            "official_due_date": "2026-10-10",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["need_reply"] is True
    assert _get_case(client, auth_headers, case["id"])["status"] == "OA1"


def test_document_update_uses_resolver_for_template_defaults(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_template(client, auth_headers)
    created = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "待更新模板文书",
        },
    )
    assert created.status_code == 201, created.text

    updated = client.put(
        f"/api/v1/documents/{created.json()['id']}",
        headers=auth_headers,
        json={"doc_template_id": template["id"]},
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["need_reply"] is False
    assert _get_case(client, auth_headers, case["id"])["status"] == "NOT_FILED"


def test_conflicting_semantics_fail_closed_through_document_api(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    template = _create_template(
        client,
        auth_headers,
        code=f"OFFICIAL_NOTICE_CONFLICT_{uuid4().hex[:8].upper()}",
        status_effect="GRANT_PENDING",
        deadline_template_code="OA_REPLY",
        need_reply=True,
        input_fields=_oa_metadata(),
    )

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template["id"],
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "冲突语义不得落库",
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "DOCUMENT_SEMANTICS_CONFLICT"
    assert _get_case(client, auth_headers, case["id"])["status"] == "NOT_FILED"
