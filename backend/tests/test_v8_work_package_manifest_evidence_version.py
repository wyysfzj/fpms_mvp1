from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)
from app.modules.official_workflows.service import refresh_filing_preparation_package

CONTENT_HASH = f"sha256:{'a' * 64}"


def _document_attachment(
    *,
    case_id: str,
    role: str,
) -> tuple[Document, DocAttachment]:
    document = Document(
        id=str(uuid4()),
        case_id=case_id,
        direction="OUT",
        title=f"{role} test document",
    )
    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document.id,
        file_name=f"{role.lower()}.bin",
        file_path=f"attachments/{role.lower()}.bin",
        official_file_role=role,
        content_hash=CONTENT_HASH,
    )
    return document, attachment


def test_refresh_manifest_links_exact_evidence_version_and_keeps_attachment_compatibility(
    session_factory: sessionmaker,
) -> None:
    case_id = str(uuid4())
    package_id = str(uuid4())
    technical_document, technical_attachment = _document_attachment(
        case_id=case_id,
        role="TECHNICAL_DISCLOSURE",
    )
    legacy_document, legacy_attachment = _document_attachment(
        case_id=case_id,
        role="FILING_XML_ZIP",
    )
    evidence_version_id = str(uuid4())

    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"V8-MANIFEST-{uuid4().hex[:8].upper()}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="工作包证据版本关联测试案件",
                status="NOT_FILED",
            )
        )
        transaction.add_all([technical_document, legacy_document])
        transaction.flush()
        transaction.add_all([technical_attachment, legacy_attachment])
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=evidence_version_id,
                case_id=case_id,
                document_id=technical_document.id,
                attachment_id=technical_attachment.id,
                lineage_key=f"attachment:{technical_attachment.id}",
                role="RAW_ATTACHMENT",
                version_number=1,
                state="DRAFT",
                creator_id="manifest-test-creator",
                review_state="PENDING",
                content_hash=CONTENT_HASH,
                current_identity_key=(
                    f"{case_id}|attachment:{technical_attachment.id}"
                ),
            )
        )
        transaction.add(
            OfficialWorkPackage(
                id=package_id,
                case_id=case_id,
                package_kind="FILING_PREP",
                status="PREPARING",
                resolve_key=f"FILING_PREP:{case_id}",
            )
        )
        transaction.commit()

        result = refresh_filing_preparation_package(
            transaction,
            package_id=package_id,
        )

        manifests = {
            row.official_file_role: row
            for row in transaction.scalars(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == package_id
                )
            )
        }
        technical_manifest = manifests["TECHNICAL_DISCLOSURE"]
        legacy_manifest = manifests["FILING_XML_ZIP"]
        result_by_role = {
            row.official_file_role: row for row in result.filing_file_roles
        }

        assert (
            technical_manifest.attachment_id,
            technical_manifest.evidence_version_id,
            technical_manifest.content_hash,
        ) == (
            technical_attachment.id,
            evidence_version_id,
            CONTENT_HASH,
        )
        assert (
            legacy_manifest.attachment_id,
            legacy_manifest.evidence_version_id,
        ) == (
            legacy_attachment.id,
            None,
        )
        assert (
            result_by_role["TECHNICAL_DISCLOSURE"].attachment_id,
            result_by_role["TECHNICAL_DISCLOSURE"].evidence_version_id,
        ) == (
            technical_attachment.id,
            evidence_version_id,
        )
        assert (
            result_by_role["FILING_XML_ZIP"].attachment_id,
            result_by_role["FILING_XML_ZIP"].evidence_version_id,
        ) == (
            legacy_attachment.id,
            None,
        )
