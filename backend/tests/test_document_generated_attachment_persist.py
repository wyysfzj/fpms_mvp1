from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.documents.models import DocAttachment
from app.modules.documents.service import persist_generated_attachment

CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"
DOC_BASE = "/api/v1/documents"


def _unique_case_no() -> str:
    return f"WZP-{uuid4().hex[:8].upper()}"


def _create_case(client: TestClient, auth_headers: dict[str, str], *, title: str) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": _unique_case_no(),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": title,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_template(client: TestClient, auth_headers: dict[str, str]) -> dict:
    code = f"PERSIST_{uuid4().hex[:8].upper()}"
    resp = client.post(
        DOC_TMPL_BASE,
        headers=auth_headers,
        json={
            "code": code,
            "name": f"Persist Template {code}",
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
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_persist_generated_attachment_success(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    case = _create_case(client, auth_headers, title="附件持久化案件")
    template = _create_template(client, auth_headers)
    document = _create_document(
        client,
        auth_headers,
        case_id=case["id"],
        doc_template_id=template["id"],
        title="授权通知书",
    )

    content = b"generated-docx-bytes"

    with session_factory() as db:
        attachment = persist_generated_attachment(
            db,
            document_id=document["id"],
            file_name="grant_notice.docx",
            content_bytes=content,
            storage_dir=str(tmp_path),
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        assert attachment.document_id == document["id"]
        assert attachment.file_name == "grant_notice.docx"
        assert attachment.file_size == len(content)
        assert attachment.mime_type == (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert attachment.file_path.startswith(f"attachments/{document['id']}/")

        stored_path = tmp_path / attachment.file_path
        assert stored_path.exists()
        assert stored_path.read_bytes() == content

        stored = db.execute(
            select(DocAttachment).where(DocAttachment.id == attachment.id)
        ).scalar_one()
        assert stored.file_name == "grant_notice.docx"


def test_persist_generated_attachment_document_not_found(
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    with session_factory() as db:
        with pytest.raises(BusinessError) as exc_info:
            persist_generated_attachment(
                db,
                document_id=str(uuid4()),
                file_name="missing.docx",
                content_bytes=b"abc",
                storage_dir=str(tmp_path),
            )

        assert exc_info.value.code == "DOCUMENT_NOT_FOUND"
        assert exc_info.value.status_code == 404
