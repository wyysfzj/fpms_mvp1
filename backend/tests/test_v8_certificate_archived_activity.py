from __future__ import annotations

import json
from datetime import date
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import service
from app.modules.documents.models import (
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)


class _CertificateUpload:
    filename = "专利证书.pdf"
    content_type = "application/pdf"
    file = BytesIO(b"reviewed patent certificate")


def test_certificate_attachment_appends_document_evidence_without_changing_grant_date(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    case_id = str(uuid4())
    document_id = str(uuid4())
    actor_id = str(uuid4())
    grant_date = date(2026, 6, 30)

    with session_factory() as db:
        template = DocTemplate(
            id=str(uuid4()),
            code="OFFICIAL_NOTICE_010",
            name="专利证书",
            direction="IN",
            enabled=True,
            input_fields=json.dumps(
                {
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "catalog_status": "REFERENCE_ONLY",
                    "official_notice_name": "专利证书",
                    "official_doc_codes": ["400001", "400002", "400003"],
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
        )
        db.add_all(
            [
                template,
                Case(
                    id=case_id,
                    case_no=f"CERTIFICATE-{uuid4().hex[:8].upper()}",
                    status="GRANTED",
                    business_stage=BusinessStage.POST_GRANT_MAINTENANCE.value,
                    official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED.value,
                    legal_status=LegalStatus.PATENT_IN_FORCE.value,
                    lifecycle_revision=0,
                    lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
                    grant_date=grant_date,
                ),
                Document(
                    id=document_id,
                    case_id=case_id,
                    doc_template_id=template.id,
                    direction="IN",
                    doc_date=date(2026, 7, 25),
                    title="专利证书",
                ),
            ]
        )
        db.commit()

    with session_factory() as db:
        pending = service.add_attachment(
            db,
            document_id,
            _CertificateUpload(),
            str(tmp_path),
            actor_id=actor_id,
        )
        db.commit()
        evidence_version_id = pending.evidence_version.evidence_version_id
        attachment_id = pending.attachment.id

    with session_factory() as db:
        stored_case = db.get(Case, case_id)
        assert stored_case is not None
        assert stored_case.grant_date == grant_date
        assert stored_case.status == "GRANTED"
        assert stored_case.business_stage == BusinessStage.POST_GRANT_MAINTENANCE.value
        assert stored_case.official_procedure_stage == OfficialProcedureStage.GRANT_ANNOUNCED.value
        assert stored_case.legal_status == LegalStatus.PATENT_IN_FORCE.value
        assert stored_case.lifecycle_revision == 2

        version = db.get(DocumentEvidenceVersion, evidence_version_id)
        assert version is not None
        activities = db.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
            .order_by(CaseActivityEvent.sequence)
        ).all()
        assert [activity.activity_type for activity in activities] == [
            "DOCUMENT_EVIDENCE_VERSION_REGISTERED",
            "CERTIFICATE_ARCHIVED",
        ]

        archived = activities[1]
        assert archived.lane == ActivityLane.DOCUMENT.value
        assert archived.actor_id == actor_id
        assert archived.effective_at == version.created_at
        assert archived.occurred_at == version.created_at
        assert archived.idempotency_key == f"certificate-archived:{evidence_version_id}"
        assert json.loads(archived.payload_json) == {
            "attachment_id": attachment_id,
            "document_id": document_id,
            "evidence_version_id": evidence_version_id,
        }
        assert (
            archived.old_business_stage,
            archived.new_business_stage,
            archived.old_official_procedure_stage,
            archived.new_official_procedure_stage,
            archived.old_legal_status,
            archived.new_legal_status,
        ) == (
            BusinessStage.POST_GRANT_MAINTENANCE.value,
            BusinessStage.POST_GRANT_MAINTENANCE.value,
            OfficialProcedureStage.GRANT_ANNOUNCED.value,
            OfficialProcedureStage.GRANT_ANNOUNCED.value,
            LegalStatus.PATENT_IN_FORCE.value,
            LegalStatus.PATENT_IN_FORCE.value,
        )

        evidence_links = db.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == archived.id
            )
        ).all()
        assert len(evidence_links) == 1
        assert evidence_links[0].case_id == case_id
        assert evidence_links[0].evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
        assert evidence_links[0].object_type == "DocumentEvidenceVersion"
        assert evidence_links[0].object_id == evidence_version_id
        assert evidence_links[0].content_hash == version.content_hash
        assert evidence_links[0].captured_at == version.created_at
