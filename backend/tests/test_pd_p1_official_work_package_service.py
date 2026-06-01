from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
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
from app.modules.official_workflows.service import (
    archive_official_work_package,
    classify_work_package_missing_item,
    evaluate_official_work_package,
)


def _create_case_document_and_package(
    session_factory: sessionmaker,
    *,
    package_kind: str = "OA_REPLY",
) -> tuple[str, str, str]:
    with session_factory() as db:
        template = db.execute(select(DocTemplate).where(DocTemplate.code == "OA_OUT")).scalar_one()
        case = Case(
            id=str(uuid4()),
            case_no=f"OWP-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="官方工作包服务测试案件",
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
        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind=package_kind,
            status="READY_FOR_EXTERNAL_SUBMIT",
            reply_document_id=document.id,
            external_system="CNIPA_WEB",
        )
        db.add(package)
        db.commit()
        return case.id, document.id, package.id


def _add_complete_checklist_and_manifest(
    session_factory: sessionmaker,
    *,
    package_id: str,
    document_id: str,
) -> str:
    with session_factory() as db:
        attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document_id,
            file_name="权利要求书.docx",
            file_path=f"attachments/{document_id}/claims.docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=128,
            official_file_role="OA_MODIFIED_CLAIMS",
            content_hash="sha256:claims",
        )
        db.add(attachment)
        db.add(
            OfficialWorkPackageChecklist(
                id=str(uuid4()),
                package_id=package_id,
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
                package_id=package_id,
                attachment_id=attachment.id,
                official_file_role="OA_MODIFIED_CLAIMS",
                content_hash=attachment.content_hash,
                required=True,
                present=True,
            )
        )
        db.commit()
        return attachment.id


def _add_archived_receipt(
    session_factory: sessionmaker,
    *,
    package_id: str,
    document_id: str,
) -> str:
    with session_factory() as db:
        receipt_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document_id,
            file_name="电子申请回执.pdf",
            file_path=f"attachments/{document_id}/receipt.pdf",
            mime_type="application/pdf",
            file_size=256,
            official_file_role="ELECTRONIC_RECEIPT",
            content_hash="sha256:receipt",
            is_archive_evidence=True,
            is_receipt_evidence=True,
        )
        db.add(receipt_attachment)
        db.add(
            OfficialWorkPackageReceipt(
                id=str(uuid4()),
                package_id=package_id,
                receipt_kind="ELECTRONIC_APPLICATION_RECEIPT",
                receipt_attachment_id=receipt_attachment.id,
                receiving_case_no="202605310001",
                submitter="流程人员A",
                archive_status="ARCHIVED",
                received_file_list='["意见陈述书","权利要求书"]',
            )
        )
        db.commit()
        return receipt_attachment.id


def test_classifies_stable_missing_items_as_maintenance_and_pending_items_as_confirmation() -> None:
    assert classify_work_package_missing_item("SYSTEM_FIELD") == "NEEDS_MAINTENANCE"
    assert classify_work_package_missing_item("SYSTEM_FILE") == "NEEDS_MAINTENANCE"
    assert classify_work_package_missing_item("REQUIRED_MANIFEST") == "NEEDS_MAINTENANCE"
    assert classify_work_package_missing_item("OFFICIAL_TRANSIENT") == "NEEDS_CONFIRMATION"
    assert classify_work_package_missing_item("UNCONFIRMED_OWNERSHIP") == "NEEDS_CONFIRMATION"
    assert classify_work_package_missing_item("INTEGRATION_ONLY") == "NEEDS_CONFIRMATION"


def test_evaluate_package_blocks_on_incomplete_checklist_and_manifest(
    session_factory: sessionmaker,
) -> None:
    _, _, package_id = _create_case_document_and_package(session_factory)
    with session_factory() as db:
        db.add(
            OfficialWorkPackageChecklist(
                id=str(uuid4()),
                package_id=package_id,
                section_code="FIELDS",
                item_code="APPLICANT_CERTIFICATE_NO",
                item_label="申请人证件号",
                status="NEEDS_MAINTENANCE",
                required=True,
            )
        )
        db.add(
            OfficialWorkPackageManifest(
                id=str(uuid4()),
                package_id=package_id,
                official_file_role="OA_STATEMENT_PDF",
                required=True,
                present=False,
            )
        )
        db.commit()

        result = evaluate_official_work_package(db, package_id=package_id)

        assert result.status == "NEEDS_MAINTENANCE"
        assert result.can_archive is False
        assert {blocker.blocker_type for blocker in result.blockers} == {
            "CHECKLIST_INCOMPLETE",
            "MANIFEST_MISSING",
            "RECEIPT_MISSING",
        }


def test_archive_package_requires_receipt_unless_complete_override_is_recorded(
    session_factory: sessionmaker,
) -> None:
    _, document_id, package_id = _create_case_document_and_package(session_factory)
    _add_complete_checklist_and_manifest(
        session_factory,
        package_id=package_id,
        document_id=document_id,
    )

    with session_factory() as db:
        with pytest.raises(BusinessError) as exc_info:
            archive_official_work_package(
                db,
                package_id=package_id,
                actor_id="user-1",
            )

        assert exc_info.value.code == "OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED"
        assert exc_info.value.status_code == 409

    with session_factory() as db:
        package = archive_official_work_package(
            db,
            package_id=package_id,
            actor_id="user-1",
            override_reason="官方回执暂时无法下载，先由负责人批准关闭并后续补归档",
            follow_up_owner="user-2",
            follow_up_note="流程人员明日补传电子申请回执 PDF",
        )

        assert package.status == "OVERRIDE"
        override = db.execute(
            select(OfficialWorkPackageOverride).where(
                OfficialWorkPackageOverride.package_id == package_id
            )
        ).scalar_one()
        assert override.override_action == "ARCHIVE_WITHOUT_RECEIPT"
        assert override.override_by == "user-1"
        assert override.override_reason
        assert override.override_at is not None
        assert override.follow_up_owner == "user-2"
        assert override.follow_up_note == "流程人员明日补传电子申请回执 PDF"


def test_archive_package_with_receipt_sets_archived(
    session_factory: sessionmaker,
) -> None:
    _, document_id, package_id = _create_case_document_and_package(session_factory)
    _add_complete_checklist_and_manifest(
        session_factory,
        package_id=package_id,
        document_id=document_id,
    )
    _add_archived_receipt(
        session_factory,
        package_id=package_id,
        document_id=document_id,
    )

    with session_factory() as db:
        package = archive_official_work_package(
            db,
            package_id=package_id,
            actor_id="user-1",
        )

        assert package.status == "ARCHIVED"
        assert (
            db.execute(
                select(OfficialWorkPackageOverride).where(
                    OfficialWorkPackageOverride.package_id == package_id
                )
            ).scalar_one_or_none()
            is None
        )
