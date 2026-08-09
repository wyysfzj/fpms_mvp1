from __future__ import annotations

import json
from datetime import date
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents import service
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.fees.models import T_GrantFeeTask


def test_grant_notice_attachment_is_lifecycle_neutral_and_creates_fee_task(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    case_id = str(uuid4())
    document_id = str(uuid4())

    with session_factory() as db:
        template = db.scalar(select(DocTemplate).where(DocTemplate.code == "GRANT_NOTICE"))
        actor_id = db.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert template is not None
        assert actor_id is not None
        db.add_all(
            [
                Case(
                    id=case_id,
                    case_no=f"V8-GRANT-ATTACH-{uuid4().hex[:8].upper()}",
                    case_type="NORMAL",
                    patent_category="INV",
                    flow_dir="CN_DOMESTIC",
                    title_cn="授权通知书附件无授权法律效果测试",
                    status="GRANT_PENDING",
                    app_no="CN202610000075",
                    filing_date=date(2026, 3, 20),
                    issue_date=date(2026, 7, 20),
                    pub_no="CN202610000075A",
                    pub_date=date(2026, 4, 1),
                    grant_no="CN202610000075B",
                    grant_date=date(2026, 8, 1),
                    first_annuity_year=3,
                    valid_until=date(2046, 3, 20),
                ),
                Document(
                    id=document_id,
                    case_id=case_id,
                    doc_template_id=template.id,
                    doc_type="OFFICIAL_IN",
                    direction="IN",
                    doc_date=date(2026, 7, 20),
                    title="授权通知书",
                    extra_data=json.dumps(
                        {
                            "OfficialDueDate": "2026-09-20",
                            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                            "OfficialDueDateStatus": "CONFIRMED",
                        }
                    ),
                ),
            ]
        )
        db.commit()

    upload = SimpleNamespace(
        filename="授权通知书.pdf",
        content_type="application/pdf",
        file=BytesIO(b"%PDF-1.4 reviewed grant notice"),
    )
    with session_factory() as db:
        pending = service.add_attachment(
            db,
            document_id,
            upload,
            str(tmp_path),
            actor_id=actor_id,
        )
        db.commit()
        attachment_id = pending.attachment.id
        evidence_version_id = pending.evidence_version.evidence_version_id

    with session_factory() as db:
        case = db.get(Case, case_id)
        assert case is not None
        assert case.status == "GRANT_PENDING"

        task = db.scalar(select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case_id))
        assert task is not None
        assert task.source_document_id == document_id
        assert task.due_date == date(2026, 9, 20)

        attachment = db.get(DocAttachment, attachment_id)
        evidence_version = db.get(DocumentEvidenceVersion, evidence_version_id)
        assert attachment is not None
        assert attachment.document_id == document_id
        assert evidence_version is not None
        assert evidence_version.attachment_id == attachment_id
