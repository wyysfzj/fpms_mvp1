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
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)

BASE = "/api/v1/official-work-packages"


def _create_oa_receipt_fixture(session_factory: sessionmaker) -> dict[str, str]:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=f"OA-RCP-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="OA回执来源门禁测试案件",
            status="OA1",
        )
        db.add(case)
        db.flush()

        source_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            direction=DocumentDirection.IN,
            doc_date=date(2026, 5, 10),
            title="第一次审查意见通知书",
            need_reply=True,
        )
        reply_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="第一次审查意见答复",
            reply_to_id=source_document.id,
        )
        other_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="同案其他文档",
        )
        db.add_all([source_document, reply_document, other_document])
        db.flush()

        attachments = {
            "reply_attachment_id": DocAttachment(
                id=str(uuid4()),
                document_id=reply_document.id,
                file_name="答复文档电子申请回执.pdf",
                file_path=f"attachments/{reply_document.id}/receipt.pdf",
                mime_type="application/pdf",
                file_size=256,
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=False,
                is_receipt_evidence=False,
            ),
            "manifest_attachment_id": DocAttachment(
                id=str(uuid4()),
                document_id=other_document.id,
                file_name="manifest明确回执.pdf",
                file_path=f"attachments/{other_document.id}/manifest-receipt.pdf",
                mime_type="application/pdf",
                file_size=256,
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=False,
                is_receipt_evidence=False,
            ),
            "foreign_manifest_attachment_id": DocAttachment(
                id=str(uuid4()),
                document_id=other_document.id,
                file_name="其他工作包manifest回执.pdf",
                file_path=f"attachments/{other_document.id}/foreign-manifest-receipt.pdf",
                mime_type="application/pdf",
                file_size=256,
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=False,
                is_receipt_evidence=False,
            ),
            "inactive_manifest_attachment_id": DocAttachment(
                id=str(uuid4()),
                document_id=other_document.id,
                file_name="未呈现manifest回执.pdf",
                file_path=f"attachments/{other_document.id}/inactive-manifest-receipt.pdf",
                mime_type="application/pdf",
                file_size=256,
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=False,
                is_receipt_evidence=False,
            ),
        }
        db.add_all(attachments.values())

        oa_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="OA_REPLY",
            status="WAITING_RECEIPT",
            source_document_id=source_document.id,
            reply_document_id=reply_document.id,
            resolve_key=f"OA_REPLY:{source_document.id}",
            external_system="CNIPA_WEB",
        )
        filing_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="FILING_PREP",
            status="WAITING_RECEIPT",
            resolve_key=f"FILING_PREP:{case.id}",
            external_system="CNIPA_WEB",
        )
        db.add_all([oa_package, filing_package])
        db.flush()

        db.add_all(
            [
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=oa_package.id,
                    attachment_id=attachments["manifest_attachment_id"].id,
                    official_file_role="OA_ADDITIONAL_FILE",
                    present=True,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=oa_package.id,
                    attachment_id=attachments["inactive_manifest_attachment_id"].id,
                    official_file_role="OA_ADDITIONAL_FILE",
                    present=False,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=filing_package.id,
                    attachment_id=attachments["foreign_manifest_attachment_id"].id,
                    official_file_role="FILING_MERGED_PDF",
                    present=True,
                ),
            ]
        )
        db.commit()
        return {
            "oa_package_id": oa_package.id,
            "filing_package_id": filing_package.id,
            **{key: attachment.id for key, attachment in attachments.items()},
        }


def _receipt_payload(attachment_id: str) -> dict[str, str]:
    return {
        "receipt_kind": "ELECTRONIC_APPLICATION_RECEIPT",
        "receipt_attachment_id": attachment_id,
        "receiving_case_no": "202607110002",
        "submitter": "流程人员A",
        "received_at": "2026-07-11T11:00:00",
        "archive_status": "ARCHIVED",
    }


@pytest.mark.parametrize(
    "attachment_key",
    ["foreign_manifest_attachment_id", "inactive_manifest_attachment_id"],
)
def test_oa_receipt_rejects_same_case_attachment_without_active_package_source(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    attachment_key: str,
) -> None:
    ids = _create_oa_receipt_fixture(session_factory)
    attachment_id = ids[attachment_key]

    response = client.post(
        f"{BASE}/{ids['oa_package_id']}/receipts",
        headers=auth_headers,
        json=_receipt_payload(attachment_id),
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "OA_RECEIPT_ATTACHMENT_SOURCE_INVALID"

    with session_factory() as db:
        receipt_count = db.scalar(
            select(func.count(OfficialWorkPackageReceipt.id)).where(
                OfficialWorkPackageReceipt.package_id == ids["oa_package_id"]
            )
        )
        assert receipt_count == 0
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.id == attachment_id)
        ).scalar_one()
        assert attachment.is_archive_evidence is False
        assert attachment.is_receipt_evidence is False


@pytest.mark.parametrize(
    "attachment_key",
    ["reply_attachment_id", "manifest_attachment_id"],
)
def test_oa_receipt_accepts_linked_reply_or_active_package_manifest_attachment(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    attachment_key: str,
) -> None:
    ids = _create_oa_receipt_fixture(session_factory)
    attachment_id = ids[attachment_key]

    response = client.post(
        f"{BASE}/{ids['oa_package_id']}/receipts",
        headers=auth_headers,
        json=_receipt_payload(attachment_id),
    )

    assert response.status_code == 201, response.text
    assert response.json()["package_id"] == ids["oa_package_id"]
    assert response.json()["receipt_attachment_id"] == attachment_id

    with session_factory() as db:
        receipt = db.execute(
            select(OfficialWorkPackageReceipt).where(
                OfficialWorkPackageReceipt.package_id == ids["oa_package_id"]
            )
        ).scalar_one()
        assert receipt.receipt_attachment_id == attachment_id
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.id == attachment_id)
        ).scalar_one()
        assert attachment.is_archive_evidence is True
        assert attachment.is_receipt_evidence is True


def test_non_oa_package_keeps_same_case_receipt_behavior(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_oa_receipt_fixture(session_factory)
    attachment_id = ids["inactive_manifest_attachment_id"]

    response = client.post(
        f"{BASE}/{ids['filing_package_id']}/receipts",
        headers=auth_headers,
        json=_receipt_payload(attachment_id),
    )

    assert response.status_code == 201, response.text
    assert response.json()["package_id"] == ids["filing_package_id"]
    assert response.json()["receipt_attachment_id"] == attachment_id
