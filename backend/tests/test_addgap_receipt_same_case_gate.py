from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageReceipt,
)

BASE = "/api/v1/official-work-packages"


def _create_package_and_attachments(
    session_factory: sessionmaker,
) -> tuple[str, str, str]:
    with session_factory() as db:
        package_case = Case(
            id=str(uuid4()),
            case_no=f"RCP-PKG-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="回执工作包案件",
        )
        other_case = Case(
            id=str(uuid4()),
            case_no=f"RCP-OTHER-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="其他案件",
        )
        db.add_all([package_case, other_case])
        db.flush()

        package_document = Document(
            id=str(uuid4()),
            case_id=package_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="同案电子申请回执",
        )
        other_document = Document(
            id=str(uuid4()),
            case_id=other_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="跨案电子申请回执",
        )
        db.add_all([package_document, other_document])
        db.flush()

        same_case_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=package_document.id,
            file_name="同案电子申请回执.pdf",
            file_path=f"attachments/{package_document.id}/receipt.pdf",
            mime_type="application/pdf",
            file_size=256,
            official_file_role="ELECTRONIC_RECEIPT",
            is_archive_evidence=False,
            is_receipt_evidence=False,
        )
        cross_case_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=other_document.id,
            file_name="跨案电子申请回执.pdf",
            file_path=f"attachments/{other_document.id}/receipt.pdf",
            mime_type="application/pdf",
            file_size=256,
            official_file_role="ELECTRONIC_RECEIPT",
            is_archive_evidence=False,
            is_receipt_evidence=False,
        )
        db.add_all([same_case_attachment, cross_case_attachment])

        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=package_case.id,
            package_kind="FILING_PREP",
            status="WAITING_RECEIPT",
            resolve_key=f"FILING_PREP:{package_case.id}",
            external_system="CNIPA_WEB",
        )
        db.add(package)
        db.commit()
        return package.id, same_case_attachment.id, cross_case_attachment.id


def _receipt_payload(
    attachment_id: str,
    *,
    receipt_kind: str = "ELECTRONIC_APPLICATION_RECEIPT",
) -> dict[str, str]:
    return {
        "receipt_kind": receipt_kind,
        "receipt_attachment_id": attachment_id,
        "receiving_case_no": "202607110001",
        "submitter": "流程人员A",
        "received_at": "2026-07-11T10:30:00",
        "archive_status": "ARCHIVED",
        "note": "人工下载并上传电子申请回执",
    }


def test_cross_case_receipt_attachment_is_rejected_before_any_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, same_case_attachment_id, cross_case_attachment_id = _create_package_and_attachments(
        session_factory
    )

    response = client.post(
        f"{BASE}/{package_id}/receipts",
        headers=auth_headers,
        json=_receipt_payload(cross_case_attachment_id),
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == ("OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH")

    with session_factory() as db:
        receipt_count = db.scalar(
            select(func.count(OfficialWorkPackageReceipt.id)).where(
                OfficialWorkPackageReceipt.package_id == package_id
            )
        )
        assert receipt_count == 0
        attachments = {
            attachment.id: attachment
            for attachment in db.execute(
                select(DocAttachment).where(
                    DocAttachment.id.in_([same_case_attachment_id, cross_case_attachment_id])
                )
            )
            .scalars()
            .all()
        }
        assert attachments[cross_case_attachment_id].is_archive_evidence is False
        assert attachments[cross_case_attachment_id].is_receipt_evidence is False
        assert attachments[same_case_attachment_id].is_archive_evidence is False
        assert attachments[same_case_attachment_id].is_receipt_evidence is False


@pytest.mark.parametrize(
    ("receipt_kind", "expected_receipt_evidence"),
    [
        ("ELECTRONIC_APPLICATION_RECEIPT", True),
        ("MERGED_PDF", False),
    ],
)
def test_same_case_receipt_attachment_is_recorded(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    receipt_kind: str,
    expected_receipt_evidence: bool,
) -> None:
    package_id, same_case_attachment_id, _ = _create_package_and_attachments(session_factory)

    response = client.post(
        f"{BASE}/{package_id}/receipts",
        headers=auth_headers,
        json=_receipt_payload(
            same_case_attachment_id,
            receipt_kind=receipt_kind,
        ),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["package_id"] == package_id
    assert body["receipt_kind"] == receipt_kind
    assert body["receipt_attachment_id"] == same_case_attachment_id
    assert body["archive_status"] == "ARCHIVED"

    with session_factory() as db:
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.id == same_case_attachment_id)
        ).scalar_one()
        assert attachment.is_archive_evidence is True
        assert attachment.is_receipt_evidence is expected_receipt_evidence
        receipt = db.execute(
            select(OfficialWorkPackageReceipt).where(
                OfficialWorkPackageReceipt.package_id == package_id
            )
        ).scalar_one()
        assert receipt.receipt_attachment_id == same_case_attachment_id


def test_receipt_gate_preserves_missing_package_and_attachment_404s(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    package_id, same_case_attachment_id, _ = _create_package_and_attachments(session_factory)

    missing_package_response = client.post(
        f"{BASE}/{uuid4()}/receipts",
        headers=auth_headers,
        json=_receipt_payload(same_case_attachment_id),
    )
    assert missing_package_response.status_code == 404
    assert missing_package_response.json()["error"]["code"] == ("OFFICIAL_WORK_PACKAGE_NOT_FOUND")

    missing_attachment_response = client.post(
        f"{BASE}/{package_id}/receipts",
        headers=auth_headers,
        json=_receipt_payload(str(uuid4())),
    )
    assert missing_attachment_response.status_code == 404
    assert missing_attachment_response.json()["error"]["code"] == (
        "OFFICIAL_WORK_PACKAGE_RECEIPT_ATTACHMENT_NOT_FOUND"
    )

    with session_factory() as db:
        receipt_count = db.scalar(
            select(func.count(OfficialWorkPackageReceipt.id)).where(
                OfficialWorkPackageReceipt.package_id == package_id
            )
        )
        assert receipt_count == 0
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.id == same_case_attachment_id)
        ).scalar_one()
        assert attachment.is_archive_evidence is False
        assert attachment.is_receipt_evidence is False
