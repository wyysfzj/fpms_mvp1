from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.cases.models import Case  # noqa: E402, F401
from app.modules.documents.models import DocAttachment, Document  # noqa: E402
from app.modules.official_workflows.models import (  # noqa: E402
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)


def scan_receipt_ownership(db: Session) -> dict[str, object]:
    """Report invalid historical receipt links without changing persisted data."""
    with db.no_autoflush:
        rows = db.execute(
            select(
                OfficialWorkPackageReceipt,
                OfficialWorkPackage,
                DocAttachment,
                Document,
            )
            .select_from(OfficialWorkPackageReceipt)
            .join(
                OfficialWorkPackage,
                OfficialWorkPackageReceipt.package_id == OfficialWorkPackage.id,
            )
            .join(
                DocAttachment,
                OfficialWorkPackageReceipt.receipt_attachment_id == DocAttachment.id,
            )
            .join(Document, DocAttachment.document_id == Document.id)
            .order_by(
                OfficialWorkPackageReceipt.created_at.asc(),
                OfficialWorkPackageReceipt.id.asc(),
            )
        ).all()
        active_manifest_links = set(
            db.execute(
                select(
                    OfficialWorkPackageManifest.package_id,
                    OfficialWorkPackageManifest.attachment_id,
                ).where(
                    OfficialWorkPackageManifest.attachment_id.is_not(None),
                    OfficialWorkPackageManifest.present.is_(True),
                )
            ).all()
        )

    findings: list[dict[str, object]] = []
    for receipt, package, attachment, attachment_document in rows:
        finding = {
            "package_id": package.id,
            "receipt_id": receipt.id,
            "attachment_id": attachment.id,
            "package_case_id": package.case_id,
            "attachment_case_id": attachment_document.case_id,
            "package_kind": package.package_kind,
            "reply_document_id": package.reply_document_id,
        }
        if attachment_document.case_id != package.case_id:
            findings.append(
                {
                    "finding_code": "OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH",
                    **finding,
                }
            )
            continue

        package_kind = (package.package_kind or "").strip().upper()
        if (
            package_kind == "OA_REPLY"
            and attachment.document_id != package.reply_document_id
            and (package.id, attachment.id) not in active_manifest_links
        ):
            findings.append(
                {
                    "finding_code": "OA_RECEIPT_ATTACHMENT_SOURCE_INVALID",
                    **finding,
                }
            )

    return {
        "status": "COMPLETED",
        "scanned_link_count": len(rows),
        "finding_count": len(findings),
        "findings": findings,
    }


def main() -> int:
    with SessionLocal() as db:
        result = scan_receipt_ownership(db)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
