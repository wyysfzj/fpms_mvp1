from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.documents.service import (
    persist_generated_attachment,
    summarize_attachment_manifest,
)


def _create_document(session_factory: sessionmaker) -> str:
    with session_factory() as db:
        template = db.execute(select(DocTemplate).where(DocTemplate.code == "OA_OUT")).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"ATT-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="附件 manifest 测试案件",
        )
        db.add(case)
        db.flush()
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 5, 31),
            title="OA 答复",
        )
        db.add(document)
        db.commit()
        return document.id


def test_generated_attachment_persists_manifest_metadata_and_hash(
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    document_id = _create_document(session_factory)
    content = b"pdf statement bytes"

    with session_factory() as db:
        attachment = persist_generated_attachment(
            db,
            document_id=document_id,
            file_name="意见陈述书.pdf",
            content_bytes=content,
            storage_dir=str(tmp_path),
            mime_type="application/pdf",
            official_file_role="OA_STATEMENT_PDF",
            source_role_alias="PDF 意见陈述",
        )

        assert attachment.official_file_role == "OA_STATEMENT_PDF"
        assert attachment.source_role_alias == "PDF 意见陈述"
        assert attachment.external_upload_position == "OA_REPLY_OTHER_PROOF_FILES"
        assert attachment.package_usage_hint == "OA_REPLY"
        assert attachment.content_hash == f"sha256:{sha256(content).hexdigest()}"
        assert attachment.is_archive_evidence is False
        assert attachment.is_receipt_evidence is False


def test_attachment_manifest_summary_separates_roles_and_missing_intake_gates() -> None:
    attachments = [
        DocAttachment(
            id="att-td",
            document_id="doc-1",
            file_name="技术交底书.docx",
            file_path="attachments/doc-1/td.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=10,
            official_file_role="TECHNICAL_DISCLOSURE",
        ),
        DocAttachment(
            id="att-xml",
            document_id="doc-1",
            file_name="请求类表格.zip",
            file_path="attachments/doc-1/request.zip",
            mime_type="application/zip",
            file_size=20,
            official_file_role="FILING_XML_ZIP",
        ),
        DocAttachment(
            id="att-claims",
            document_id="doc-1",
            file_name="权利要求书.docx",
            file_path="attachments/doc-1/claims.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=30,
            official_file_role="OA_MODIFIED_CLAIMS",
        ),
        DocAttachment(
            id="att-receipt",
            document_id="doc-1",
            file_name="电子申请回执.pdf",
            file_path="attachments/doc-1/receipt.pdf",
            mime_type="application/pdf",
            file_size=40,
            official_file_role="ELECTRONIC_RECEIPT",
        ),
        DocAttachment(
            id="att-legacy",
            document_id="doc-1",
            file_name="旧系统归档.docx",
            file_path="attachments/doc-1/legacy.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=50,
            source_role_alias="PCT 公开文本",
        ),
    ]

    summary = summarize_attachment_manifest(
        attachments,
        require_commission_instruction=True,
    )

    assert [item.official_file_role for item in summary.intake_gate_roles] == [
        "TECHNICAL_DISCLOSURE"
    ]
    assert [item.official_file_role for item in summary.filing_roles] == ["FILING_XML_ZIP"]
    assert [item.official_file_role for item in summary.oa_roles] == ["OA_MODIFIED_CLAIMS"]
    assert [item.official_file_role for item in summary.archive_roles] == ["ELECTRONIC_RECEIPT"]
    assert [item.source_role_alias for item in summary.historical_alias_roles] == ["PCT 公开文本"]
    assert summary.missing_intake_gate_roles == ["COMMISSION_INSTRUCTION"]
    assert "TECHNICAL_DISCLOSURE" not in [item.official_file_role for item in summary.filing_roles]


def test_attachment_manifest_summary_does_not_require_optional_commission_instruction() -> None:
    summary = summarize_attachment_manifest(
        [
            DocAttachment(
                id="att-td",
                document_id="doc-1",
                file_name="技术交底书.docx",
                file_path="attachments/doc-1/td.docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_size=10,
                official_file_role="TECHNICAL_DISCLOSURE",
            )
        ],
        require_commission_instruction=False,
    )

    assert summary.missing_intake_gate_roles == []
