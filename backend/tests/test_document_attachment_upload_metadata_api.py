from __future__ import annotations

from datetime import date
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocTemplate, Document

DOC_BASE = "/api/v1/documents"


def _create_document(session_factory: sessionmaker) -> str:
    with session_factory() as db:
        template = db.execute(select(DocTemplate).where(DocTemplate.code == "OA_OUT")).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"ATT-UPLOAD-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="附件上传角色测试案件",
        )
        db.add(case)
        db.flush()
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 5),
            title="OA 答复文件",
        )
        db.add(document)
        db.commit()
        return document.id


def test_upload_attachment_accepts_official_file_role_and_source_alias(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    document_id = _create_document(session_factory)

    resp = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
        data={
            "official_file_role": "OA_STATEMENT_PDF",
            "source_role_alias": "OA意见陈述 PDF",
        },
        files={
            "file": (
                "意见陈述书.pdf",
                BytesIO(b"%PDF-1.4 statement pdf"),
                "application/pdf",
            )
        },
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["official_file_role"] == "OA_STATEMENT_PDF"
    assert body["source_role_alias"] == "OA意见陈述 PDF"
    assert body["external_upload_position"] == "OA_REPLY_OTHER_PROOF_FILES"
    assert body["package_usage_hint"] == "OA_REPLY"
    assert body["content_hash"].startswith("sha256:")

    detail_resp = client.get(f"{DOC_BASE}/{document_id}", headers=auth_headers)
    assert detail_resp.status_code == 200, detail_resp.text
    attachment = detail_resp.json()["attachments"][0]
    assert attachment["official_file_role"] == "OA_STATEMENT_PDF"
    assert attachment["source_role_alias"] == "OA意见陈述 PDF"


def test_upload_attachment_rejects_official_notice_catalog_code_as_role(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    document_id = _create_document(session_factory)

    resp = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
        data={"official_file_role": "OFFICIAL_NOTICE_001"},
        files={"file": ("受理通知.pdf", BytesIO(b"%PDF-1.4 notice"), "application/pdf")},
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["error"]["code"] == "ATTACHMENT_OFFICIAL_ROLE_INVALID"
