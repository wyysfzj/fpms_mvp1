from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
    OfficialWorkPackageOverride,
    OfficialWorkPackageReceipt,
)

BASE = "/api/v1/official-work-packages"


def _create_ready_package(session_factory: sessionmaker, *, package_kind: str) -> tuple[str, str]:
    with session_factory() as db:
        template = db.execute(select(DocTemplate).where(DocTemplate.code == "OA_OUT")).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"RCP-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="回执归档 API 测试案件",
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
        db.flush()
        source_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document.id,
            file_name="权利要求书.docx",
            file_path=f"attachments/{document.id}/claims.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=128,
            official_file_role="OA_MODIFIED_CLAIMS",
            content_hash="sha256:claims",
        )
        receipt_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document.id,
            file_name="电子申请回执.pdf",
            file_path=f"attachments/{document.id}/receipt.pdf",
            mime_type="application/pdf",
            file_size=256,
            official_file_role="ELECTRONIC_RECEIPT",
            content_hash="sha256:receipt",
            is_archive_evidence=True,
            is_receipt_evidence=True,
        )
        db.add_all([source_attachment, receipt_attachment])
        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind=package_kind,
            status="READY_FOR_EXTERNAL_SUBMIT",
            reply_document_id=document.id,
            external_system="CNIPA_WEB",
        )
        db.add(package)
        db.flush()
        db.add(
            OfficialWorkPackageChecklist(
                id=str(uuid4()),
                package_id=package.id,
                section_code="OA_REPLY",
                item_code="PREVIEW_CONFIRMED",
                item_label="预览确认",
                status="DONE",
                required=True,
            )
        )
        db.add(
            OfficialWorkPackageManifest(
                id=str(uuid4()),
                package_id=package.id,
                attachment_id=source_attachment.id,
                official_file_role="OA_MODIFIED_CLAIMS",
                content_hash=source_attachment.content_hash,
                required=True,
                present=True,
            )
        )
        db.commit()
        return package.id, receipt_attachment.id


def test_receipt_metadata_api_records_receipt_and_allows_archive(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, receipt_attachment_id = _create_ready_package(
        session_factory,
        package_kind="OA_REPLY",
    )

    receipt_resp = client.post(
        f"{BASE}/{package_id}/receipts",
        headers=auth_headers,
        json={
            "receipt_kind": "ELECTRONIC_APPLICATION_RECEIPT",
            "receipt_attachment_id": receipt_attachment_id,
            "receiving_case_no": "202605310001",
            "submitter": "流程人员A",
            "received_at": "2026-05-31T10:30:00",
            "received_file_list": '["意见陈述书","权利要求书"]',
            "archive_status": "ARCHIVED",
            "note": "人工下载并上传电子申请回执",
        },
    )
    assert receipt_resp.status_code == 201, receipt_resp.text
    receipt = receipt_resp.json()
    assert receipt["package_id"] == package_id
    assert receipt["receipt_attachment_id"] == receipt_attachment_id
    assert receipt["receiving_case_no"] == "202605310001"
    assert receipt["archive_status"] == "ARCHIVED"

    archive_resp = client.post(
        f"{BASE}/{package_id}/archive",
        headers=auth_headers,
        json={},
    )
    assert archive_resp.status_code == 200, archive_resp.text
    body = archive_resp.json()
    assert body["package"]["status"] == "ARCHIVED"
    assert body["evaluation"]["can_archive"] is True
    assert body["evaluation"]["receipt_hard_gate_satisfied"] is True

    with session_factory() as db:
        stored = db.execute(
            select(OfficialWorkPackageReceipt).where(
                OfficialWorkPackageReceipt.package_id == package_id
            )
        ).scalar_one()
        assert stored.receipt_attachment_id == receipt_attachment_id
        assert stored.received_file_list == '["意见陈述书","权利要求书"]'


def test_archive_api_requires_receipt_unless_override_is_complete(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, _ = _create_ready_package(session_factory, package_kind="FILING_PREP")

    blocked_resp = client.post(
        f"{BASE}/{package_id}/archive",
        headers=auth_headers,
        json={},
    )
    assert blocked_resp.status_code == 409, blocked_resp.text
    assert blocked_resp.json()["error"]["code"] == "OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED"

    override_resp = client.post(
        f"{BASE}/{package_id}/archive",
        headers=auth_headers,
        json={
            "override_reason": "官方回执暂时无法下载，负责人同意先关闭并后续补归档",
            "follow_up_owner": "formalities-user",
            "follow_up_note": "次日补传合并 PDF 或电子申请回执",
        },
    )
    assert override_resp.status_code == 200, override_resp.text
    body = override_resp.json()
    assert body["package"]["status"] == "OVERRIDE"
    assert body["evaluation"]["can_archive"] is False

    with session_factory() as db:
        override = db.execute(
            select(OfficialWorkPackageOverride).where(
                OfficialWorkPackageOverride.package_id == package_id
            )
        ).scalar_one()
        assert override.override_action == "ARCHIVE_WITHOUT_RECEIPT"
        assert override.override_reason
        assert override.override_by is not None
        assert override.follow_up_owner == "formalities-user"
        assert override.follow_up_note == "次日补传合并 PDF 或电子申请回执"
