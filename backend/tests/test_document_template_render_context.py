from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.documents.models import Document
from app.modules.documents.service import build_document_template_render_context
from app.modules.masterdata.clients.models import Client

CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"
DOC_BASE = "/api/v1/documents"


def _unique_case_no() -> str:
    return f"WZC-{uuid4().hex[:8].upper()}"


def _create_client_record(db) -> Client:
    client = Client(
        id=str(uuid4()),
        client_code=f"CL-{uuid4().hex[:6].upper()}",
        name_cn="测试客户",
        name_en="Test Client",
        is_active=True,
    )
    db.add(client)
    db.flush()
    return client


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    title: str,
    client_id: str,
) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": title,
            "client_id": client_id,
            "app_no": f"APP-{uuid4().hex[:8].upper()}",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_template(client: TestClient, auth_headers: dict[str, str]) -> dict:
    code = f"CTX_{uuid4().hex[:8].upper()}"
    resp = client.post(
        DOC_TMPL_BASE,
        headers=auth_headers,
        json={
            "code": code,
            "name": f"Context Template {code}",
            "direction": "IN",
            "enabled": True,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    doc_template_id: str,
    title: str,
) -> dict:
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": doc_template_id,
            "direction": "IN",
            "doc_date": "2026-04-04",
            "title": title,
            "ref_no": "DOC-CTX-001",
            "extra_data": "上下文补充说明",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_build_document_template_render_context_success(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        client_record = _create_client_record(db)
        db.commit()
        client_id = client_record.id

    case = _create_case(client, auth_headers, title="渲染上下文案件", client_id=client_id)
    template = _create_template(client, auth_headers)
    document_payload = _create_document(
        client,
        auth_headers,
        case_id=case["id"],
        doc_template_id=template["id"],
        title="渲染上下文文书",
    )

    with session_factory() as db:
        document = db.execute(
            select(Document).where(Document.id == document_payload["id"])
        ).scalar_one()
        context = build_document_template_render_context(db, document=document)

    assert context["document_id"] == document_payload["id"]
    assert context["document_title"] == "渲染上下文文书"
    assert context["document_direction"] == "IN"
    assert context["document_date"] == "2026-04-04"
    assert context["document_ref_no"] == "DOC-CTX-001"
    assert context["document_extra_data"] == "上下文补充说明"
    assert context["template_code"] == template["code"]

    case_context = context["case"]
    assert case_context["id"] == case["id"]
    assert case_context["case_no"] == case["case_no"]
    assert case_context["title"] == "渲染上下文案件"
    assert case_context["app_no"] is not None

    client_context = context["client"]
    assert client_context["id"] == client_id
    assert client_context["name"] == "测试客户"
    assert client_context["name_en"] == "Test Client"

    document_context = context["document"]
    assert document_context["title"] == "渲染上下文文书"
    assert document_context["template_code"] == template["code"]


def test_build_document_template_render_context_case_not_found(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        document = Document(
            id=str(uuid4()),
            case_id=str(uuid4()),
            doc_template_id=None,
            direction="IN",
            title="孤立文书",
        )

        with pytest.raises(BusinessError) as exc_info:
            build_document_template_render_context(db, document=document)

        assert exc_info.value.code == "CASE_NOT_FOUND"
        assert exc_info.value.status_code == 404
