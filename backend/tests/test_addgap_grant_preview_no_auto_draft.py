from __future__ import annotations

import json
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate

PREVIEW_URL = "/api/v1/documents/impact-preview"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-GRANT-PREVIEW-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "授权影响预览测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _template_ids(session_factory: sessionmaker) -> tuple[str, str, str]:
    with session_factory() as db:
        canonical_id = db.execute(
            select(DocTemplate.id).where(DocTemplate.code == "GRANT_NOTICE")
        ).scalar_one()
        suffix = uuid4().hex[:8].upper()
        alias = DocTemplate(
            id=str(uuid4()),
            code=f"GRANT_PREVIEW_ALIAS_{suffix}",
            name="可执行授权通知别名",
            direction="IN",
            status_effect="GRANT_PENDING",
            fee_draft_type="GRANT_FEE",
            need_reply=False,
            input_fields=json.dumps(
                {
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "catalog_status": "EXECUTABLE",
                    "execution_behavior": "GRANT_NOTICE",
                    "completion_event": None,
                    "archive_status_restore": None,
                    "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                    "canonical_template_code": "GRANT_NOTICE",
                },
                ensure_ascii=False,
            ),
        )
        non_grant = DocTemplate(
            id=str(uuid4()),
            code=f"CUSTOM_FEE_PREVIEW_{suffix}",
            name="普通费用文档",
            direction="IN",
            fee_draft_type="CUSTOM_FEE",
        )
        db.add_all([alias, non_grant])
        db.commit()
        return canonical_id, alias.id, non_grant.id


def _confirmed_preview_payload(case_id: str, template_id: str) -> dict:
    return {
        "case_id": case_id,
        "doc_template_id": template_id,
        "direction": "IN",
        "doc_date": "2026-07-11",
        "title": "授权通知书",
        "official_due_date": "2026-08-28",
        "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
        "official_due_date_status": "CONFIRMED",
    }


def test_canonical_and_alias_grant_preview_show_due_without_generic_fee_draft(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    canonical_id, alias_id, _ = _template_ids(session_factory)

    for template_id in (canonical_id, alias_id):
        case = _create_case(client, auth_headers)
        response = client.post(
            PREVIEW_URL,
            headers=auth_headers,
            json=_confirmed_preview_payload(case["id"], template_id),
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["official_due_date"] == "2026-08-28"
        assert body["official_due_date_source"] == "MANUAL_OFFICIAL_NOTICE"
        assert body["official_due_date_status"] == "CONFIRMED"
        assert [item["kind"] for item in body["deadline_impacts"]] == ["OFFICIAL_DUE_DATE"]
        assert body["fee_impacts"] == []
        assert "费用草稿将受模板影响" not in body["confirmation_items"]


def test_non_grant_fee_preview_remains_unchanged(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _, _, template_id = _template_ids(session_factory)
    case = _create_case(client, auth_headers)

    response = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "普通费用文档",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["fee_impacts"] == [
        {
            "kind": "FEE_DRAFT",
            "title": "费用影响",
            "effect": "CUSTOM_FEE",
            "enabled": True,
            "requires_confirmation": True,
            "document_id": None,
            "detail": "登记后将尝试生成费用草稿",
        }
    ]
    assert "费用草稿将受模板影响" in response.json()["confirmation_items"]


def test_grant_preview_without_confirmed_due_still_fails_closed(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    canonical_id, _, _ = _template_ids(session_factory)
    case = _create_case(client, auth_headers)

    response = client.post(
        PREVIEW_URL,
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": canonical_id,
            "direction": "IN",
            "doc_date": "2026-07-11",
            "title": "缺确认期限的授权通知书",
        },
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "GRANT_OFFICIAL_DUE_DATE_REQUIRED"
