from __future__ import annotations

import importlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _load_scan():
    module_name = "scripts.audit_receipt_ownership"
    assert importlib.util.find_spec(module_name) is not None, (
        "receipt ownership audit script must exist"
    )
    return importlib.import_module(module_name).scan_receipt_ownership


def _create_history(session_factory: sessionmaker) -> dict[str, str]:
    with session_factory() as db:
        package_case = Case(
            id=str(uuid4()),
            case_no=f"SCAN-PKG-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="历史回执扫描工作包案件",
        )
        other_case = Case(
            id=str(uuid4()),
            case_no=f"SCAN-OTHER-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="历史回执扫描其他案件",
        )
        db.add_all([package_case, other_case])
        db.flush()

        source_document = Document(
            id=str(uuid4()),
            case_id=package_case.id,
            direction=DocumentDirection.IN,
            doc_date=date(2026, 5, 10),
            title="第一次审查意见通知书",
            need_reply=True,
        )
        reply_document = Document(
            id=str(uuid4()),
            case_id=package_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="第一次审查意见答复",
            reply_to_id=source_document.id,
        )
        same_case_document = Document(
            id=str(uuid4()),
            case_id=package_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="同案其他文档",
        )
        other_case_document = Document(
            id=str(uuid4()),
            case_id=other_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="跨案文档",
        )
        db.add_all(
            [
                source_document,
                reply_document,
                same_case_document,
                other_case_document,
            ]
        )
        db.flush()

        attachments = {
            "cross_case": DocAttachment(
                id=str(uuid4()),
                document_id=other_case_document.id,
                file_name="跨案历史回执.pdf",
                file_path=f"attachments/{other_case_document.id}/cross-case.pdf",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "oa_invalid": DocAttachment(
                id=str(uuid4()),
                document_id=same_case_document.id,
                file_name="OA无效来源历史回执.pdf",
                file_path=f"attachments/{same_case_document.id}/oa-invalid.pdf",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "oa_reply": DocAttachment(
                id=str(uuid4()),
                document_id=reply_document.id,
                file_name="OA答复文档历史回执.pdf",
                file_path=f"attachments/{reply_document.id}/oa-reply.pdf",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "oa_manifest": DocAttachment(
                id=str(uuid4()),
                document_id=same_case_document.id,
                file_name="OA清单历史回执.pdf",
                file_path=f"attachments/{same_case_document.id}/oa-manifest.pdf",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "filing_valid": DocAttachment(
                id=str(uuid4()),
                document_id=same_case_document.id,
                file_name="申请同案历史回执.pdf",
                file_path=f"attachments/{same_case_document.id}/filing-valid.pdf",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
        }
        db.add_all(attachments.values())

        filing_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=package_case.id,
            package_kind="FILING_PREP",
            status="WAITING_RECEIPT",
            resolve_key=f"FILING_PREP:{package_case.id}",
        )
        oa_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=package_case.id,
            package_kind="oa_reply",
            status="WAITING_RECEIPT",
            source_document_id=source_document.id,
            reply_document_id=reply_document.id,
            resolve_key=f"OA_REPLY:{source_document.id}",
        )
        foreign_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=package_case.id,
            package_kind="FILING_PREP",
            status="WAITING_RECEIPT",
            resolve_key=f"FILING_PREP:FOREIGN:{package_case.id}",
        )
        db.add_all([filing_package, oa_package, foreign_package])
        db.flush()

        db.add_all(
            [
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=oa_package.id,
                    attachment_id=attachments["oa_manifest"].id,
                    official_file_role="OA_ADDITIONAL_FILE",
                    present=True,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=oa_package.id,
                    attachment_id=attachments["oa_invalid"].id,
                    official_file_role="OA_ADDITIONAL_FILE",
                    present=False,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=foreign_package.id,
                    attachment_id=attachments["oa_invalid"].id,
                    official_file_role="FILING_MERGED_PDF",
                    present=True,
                ),
            ]
        )

        receipt_specs = [
            ("cross_receipt", filing_package.id, "cross_case", 0),
            ("oa_invalid_receipt", oa_package.id, "oa_invalid", 1),
            ("oa_reply_receipt", oa_package.id, "oa_reply", 2),
            ("oa_manifest_receipt", oa_package.id, "oa_manifest", 3),
            ("filing_valid_receipt", filing_package.id, "filing_valid", 4),
        ]
        receipt_ids: dict[str, str] = {}
        for key, package_id, attachment_key, minute in receipt_specs:
            receipt = OfficialWorkPackageReceipt(
                id=str(uuid4()),
                package_id=package_id,
                receipt_kind="ELECTRONIC_APPLICATION_RECEIPT",
                receipt_attachment_id=attachments[attachment_key].id,
                receiving_case_no=f"2026071100{minute}",
                archive_status="ARCHIVED",
                created_at=datetime(2026, 7, 11, 10, minute, tzinfo=timezone.utc),
            )
            db.add(receipt)
            receipt_ids[key] = receipt.id

        db.commit()
        return {
            "package_case_id": package_case.id,
            "other_case_id": other_case.id,
            "filing_package_id": filing_package.id,
            "oa_package_id": oa_package.id,
            "reply_document_id": reply_document.id,
            "cross_attachment_id": attachments["cross_case"].id,
            "oa_invalid_attachment_id": attachments["oa_invalid"].id,
            **receipt_ids,
        }


def _database_snapshot(db: Session) -> dict[str, list[tuple[object, ...]]]:
    return {
        "receipts": list(
            db.execute(
                select(
                    OfficialWorkPackageReceipt.id,
                    OfficialWorkPackageReceipt.package_id,
                    OfficialWorkPackageReceipt.receipt_attachment_id,
                    OfficialWorkPackageReceipt.archive_status,
                ).order_by(OfficialWorkPackageReceipt.id)
            ).all()
        ),
        "attachments": list(
            db.execute(
                select(
                    DocAttachment.id,
                    DocAttachment.is_archive_evidence,
                    DocAttachment.is_receipt_evidence,
                    DocAttachment.updated_at,
                ).order_by(DocAttachment.id)
            ).all()
        ),
        "manifests": list(
            db.execute(
                select(
                    OfficialWorkPackageManifest.id,
                    OfficialWorkPackageManifest.package_id,
                    OfficialWorkPackageManifest.attachment_id,
                    OfficialWorkPackageManifest.present,
                ).order_by(OfficialWorkPackageManifest.id)
            ).all()
        ),
    }


def test_scan_reports_cross_case_and_oa_source_findings_without_writes(
    session_factory: sessionmaker,
) -> None:
    ids = _create_history(session_factory)
    scan_receipt_ownership = _load_scan()

    with session_factory() as db:
        before = _database_snapshot(db)
        result = scan_receipt_ownership(db)
        after = _database_snapshot(db)

        assert before == after
        assert not db.new
        assert not db.dirty
        assert not db.deleted

    assert result["status"] == "COMPLETED"
    assert result["scanned_link_count"] == 5
    assert result["finding_count"] == 2
    assert [finding["receipt_id"] for finding in result["findings"]] == [
        ids["cross_receipt"],
        ids["oa_invalid_receipt"],
    ]

    cross_case, oa_invalid = result["findings"]
    assert cross_case == {
        "finding_code": "OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH",
        "package_id": ids["filing_package_id"],
        "receipt_id": ids["cross_receipt"],
        "attachment_id": ids["cross_attachment_id"],
        "package_case_id": ids["package_case_id"],
        "attachment_case_id": ids["other_case_id"],
        "package_kind": "FILING_PREP",
        "reply_document_id": None,
    }
    assert oa_invalid == {
        "finding_code": "OA_RECEIPT_ATTACHMENT_SOURCE_INVALID",
        "package_id": ids["oa_package_id"],
        "receipt_id": ids["oa_invalid_receipt"],
        "attachment_id": ids["oa_invalid_attachment_id"],
        "package_case_id": ids["package_case_id"],
        "attachment_case_id": ids["package_case_id"],
        "package_kind": "oa_reply",
        "reply_document_id": ids["reply_document_id"],
    }


def test_cli_emits_json_and_exits_zero_when_findings_exist(
    session_factory: sessionmaker,
) -> None:
    _create_history(session_factory)

    completed = subprocess.run(
        [sys.executable, "scripts/audit_receipt_ownership.py"],
        cwd=BACKEND_DIR,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    result = json.loads(completed.stdout)
    assert result["status"] == "COMPLETED"
    assert result["scanned_link_count"] == 5
    assert result["finding_count"] == 2
