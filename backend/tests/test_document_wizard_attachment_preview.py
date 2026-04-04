from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocAttachment

BASE = "/api/v1/documents/wizard/attachment-preview"
CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"


def _unique_case_no() -> str:
    return f"WZA-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str], *, title: str) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": title,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_template(client: TestClient, auth_headers: dict, *, direction: str = "IN") -> dict:
    code = f"STEP5_{uuid4().hex[:8].upper()}"
    resp = client.post(
        DOC_TMPL_BASE,
        headers=auth_headers,
        json={
            "code": code,
            "name": f"Step 5 Template {code}",
            "direction": direction,
            "enabled": True,
            "input_fields": '[{"name": "grant_no", "type": "text"}]',
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _preview_attachment_candidates(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    template_id: str,
    rows: list[dict[str, object]],
) -> dict:
    resp = client.post(
        BASE,
        headers=auth_headers,
        json={
            "defaults": {
                "doc_template_id": template_id,
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": rows,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_document_wizard_attachment_preview_success(
    client: TestClient, auth_headers: dict, session_factory: sessionmaker
) -> None:
    case_one = _create_case(client, auth_headers, title="附件预览案件一")
    case_two = _create_case(client, auth_headers, title="附件预览案件二")
    template = _create_template(client, auth_headers, direction="IN")

    payload = _preview_attachment_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        rows=[
            {"case_id": case_one["id"], "title": "授权通知书"},
            {"case_id": case_two["id"], "title": "OA 答复"},
        ],
    )

    assert payload["total_candidates"] == 2
    assert len(payload["items"]) == 2

    first_item = payload["items"][0]
    assert first_item["row_index"] == 1
    assert first_item["case_id"] == case_one["id"]
    assert first_item["case_no"] == case_one["case_no"]
    assert first_item["source_title"] == "附件预览案件一"
    assert first_item["document_title"] == "授权通知书"
    assert first_item["template_code"] == template["code"]
    assert first_item["template_name"] == template["name"]
    assert first_item["candidate_source_kind"] == "DOC_TEMPLATE"
    assert first_item["output_name"] == "授权通知书"
    assert first_item["generate_this_candidate"] is True
    assert first_item["remark"] is None
    assert first_item["output_format"] == "DOCX"
    assert first_item["output_file_name"].endswith(".docx")

    second_item = payload["items"][1]
    assert second_item["row_index"] == 2
    assert second_item["case_id"] == case_two["id"]
    assert second_item["document_title"] == "OA 答复"

    with session_factory() as db:
        attachments = db.execute(select(DocAttachment)).scalars().all()
        assert attachments == []


def test_document_wizard_attachment_preview_returns_empty_for_inapplicable_template(
    client: TestClient,
    auth_headers: dict,
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers, title="空状态案件")
    template = _create_template(client, auth_headers, direction="OUT")

    payload = _preview_attachment_candidates(
        client,
        auth_headers,
        template_id=template["id"],
        rows=[{"case_id": case["id"], "title": "发文附件"}],
    )

    assert payload["total_candidates"] == 0
    assert payload["items"] == []

    with session_factory() as db:
        attachments = db.execute(select(DocAttachment)).scalars().all()
        assert attachments == []
