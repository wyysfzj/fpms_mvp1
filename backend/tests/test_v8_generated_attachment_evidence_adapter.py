from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import ActivityLane
from app.modules.cases.models import CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import service as documents_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.documents.schemas import DocumentWizardBatchCreateIn
from app.modules.templates.models import Template
from app.modules.templates.render import TemplateRenderer

BASE = "/api/v1/documents/wizard/batch-create"
CASE_BASE = "/api/v1/cases"
DOC_TMPL_BASE = "/api/v1/doc-templates"
CONTENT = b"generated-attachment-evidence"


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
) -> dict[str, object]:
    suffix = uuid4().hex[:8].upper()
    applicant_response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"GEN-EVIDENCE-APPLICANT-{suffix}",
            "name_cn": f"生成附件证据申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert applicant_response.status_code == 201, applicant_response.text
    applicant = applicant_response.json()

    case_response = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": f"GEN-EVIDENCE-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "生成附件证据适配案件",
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant["id"],
                    "name_cn": applicant["name_cn"],
                }
            ],
        },
    )
    assert case_response.status_code == 201, case_response.text
    return case_response.json()


def _get_doc_template(
    client: TestClient,
    auth_headers: dict[str, str],
) -> dict[str, object]:
    response = client.get(
        DOC_TMPL_BASE,
        headers=auth_headers,
        params={"q": "CLIENT_IN", "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == "CLIENT_IN"]
    assert len(matches) == 1
    return matches[0]


def _install_source_template(
    session_factory: sessionmaker[Session],
    *,
    template_code: str,
    template_path: Path,
) -> str:
    source_template_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Template(
                id=source_template_id,
                name=template_code,
                group="DOC_TEMPLATE",
                language="zh-CN",
                file_path=str(template_path),
                enabled=True,
            )
        )
        db.commit()
    return source_template_id


def _payload(
    *,
    case_id: str,
    doc_template_id: str,
    template_code: str,
) -> dict[str, object]:
    return {
        "defaults": {
            "doc_template_id": doc_template_id,
            "direction": "IN",
            "doc_date": "2026-07-17",
        },
        "rows": [{"case_id": case_id, "title": "生成附件证据文书"}],
        "attachment_rows": [
            {
                "row_index": 1,
                "case_id": case_id,
                "template_code": template_code,
                "output_name": "生成证据附件",
                "output_file_name": "生成证据附件.docx",
                "output_format": "DOCX",
                "candidate_source_kind": "DOC_TEMPLATE",
                "remark": "Task 50",
            }
        ],
    }


def _prepare_wizard(
    *,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[dict[str, object], dict[str, object], str, Path]:
    case = _create_case(client, auth_headers)
    doc_template = _get_doc_template(client, auth_headers)
    template_path = tmp_path / "source" / "client-in.docx"
    template_path.parent.mkdir(parents=True)
    template_path.write_bytes(b"source-template")
    source_template_id = _install_source_template(
        session_factory,
        template_code=str(doc_template["code"]),
        template_path=template_path,
    )
    storage_dir = tmp_path / "storage"
    monkeypatch.setattr(documents_service, "_backend_storage_dir", lambda: storage_dir)
    monkeypatch.setattr(
        TemplateRenderer,
        "render_template_docx_bytes",
        lambda self, *, template_path, context: CONTENT,
    )
    return case, doc_template, source_template_id, storage_dir


def test_public_wizard_registers_generated_attachment_with_server_actor_and_exact_lineage(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case, doc_template, source_template_id, storage_dir = _prepare_wizard(
        client=client,
        auth_headers=auth_headers,
        session_factory=session_factory,
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )

    response = client.post(
        BASE,
        headers=auth_headers,
        json=_payload(
            case_id=str(case["id"]),
            doc_template_id=str(doc_template["id"]),
            template_code=str(doc_template["code"]),
        ),
    )

    assert response.status_code == 201, response.text
    document_id = response.json()["items"][0]["document"]["id"]
    expected_content_hash = f"sha256:{sha256(CONTENT).hexdigest()}"
    template_code_hash = sha256(str(doc_template["code"]).encode()).hexdigest()[:16]

    with session_factory() as db:
        actor = db.scalar(select(T_User).where(T_User.username == "admin"))
        document = db.get(Document, document_id)
        attachment = db.scalar(
            select(DocAttachment).where(DocAttachment.document_id == document_id)
        )
        assert actor is not None
        assert document is not None
        assert attachment is not None
        version = db.scalar(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id == attachment.id
            )
        )
        assert version is not None
        assert document.doc_template_id == doc_template["id"]
        assert (
            version.case_id,
            version.document_id,
            version.attachment_id,
            version.lineage_key,
            version.role,
            version.state,
            version.review_state,
            version.creator_id,
            version.content_hash,
            version.final_submitted_at,
        ) == (
            case["id"],
            document_id,
            attachment.id,
            (f"generated:{source_template_id}:{template_code_hash}:{attachment.id}"),
            EvidenceRole.GENERATED_ATTACHMENT.value,
            EvidenceVersionState.DRAFT.value,
            EvidenceReviewState.PENDING.value,
            actor.id,
            expected_content_hash,
            None,
        )
        assert attachment.content_hash == expected_content_hash
        assert attachment.external_upload_position is None
        assert db.scalars(select(DocumentEvidenceDerivation)).all() == []

        activity = db.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case["id"],
                CaseActivityEvent.activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED",
            )
        )
        assert activity is not None
        assert (activity.lane, activity.actor_id) == (
            ActivityLane.DOCUMENT.value,
            actor.id,
        )
        links = db.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert len(links) == 1
        assert links[0].object_id == version.id

    stored_path = storage_dir / attachment.file_path
    assert stored_path.read_bytes() == CONTENT


def test_registration_failure_rolls_back_document_unit_and_removes_managed_file(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case, doc_template, _source_template_id, storage_dir = _prepare_wizard(
        client=client,
        auth_headers=auth_headers,
        session_factory=session_factory,
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )
    monkeypatch.setattr(
        documents_service,
        "register_evidence_version",
        Mock(side_effect=RuntimeError("registration failed")),
    )

    response = client.post(
        BASE,
        headers=auth_headers,
        json=_payload(
            case_id=str(case["id"]),
            doc_template_id=str(doc_template["id"]),
            template_code=str(doc_template["code"]),
        ),
    )

    assert response.status_code == 500, response.text
    with session_factory() as db:
        documents = db.scalars(select(Document).where(Document.case_id == case["id"])).all()
        assert documents == []
        assert db.scalars(select(DocAttachment)).all() == []
        assert db.scalars(select(DocumentEvidenceVersion)).all() == []
        assert db.scalars(select(DocumentEvidenceDerivation)).all() == []
    assert not storage_dir.exists() or not any(path.is_file() for path in storage_dir.rglob("*"))


def test_outer_commit_failure_rolls_back_database_and_compensates_generated_file(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case, doc_template, _source_template_id, storage_dir = _prepare_wizard(
        client=client,
        auth_headers=auth_headers,
        session_factory=session_factory,
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
    )
    payload = DocumentWizardBatchCreateIn.model_validate(
        _payload(
            case_id=str(case["id"]),
            doc_template_id=str(doc_template["id"]),
            template_code=str(doc_template["code"]),
        )
    )

    with session_factory() as db:
        rollback = Mock(wraps=db.rollback)
        monkeypatch.setattr(db, "rollback", rollback)
        monkeypatch.setattr(
            db,
            "commit",
            Mock(side_effect=RuntimeError("outer commit failed")),
        )
        with pytest.raises(RuntimeError, match="outer commit failed"):
            documents_service.create_document_wizard_batch(
                db,
                payload,
                actor_id="actor-1",
            )
        assert rollback.call_count == 1

    with session_factory() as db:
        assert db.scalars(select(Document).where(Document.case_id == case["id"])).all() == []
        assert db.scalars(select(DocAttachment)).all() == []
        assert db.scalars(select(DocumentEvidenceVersion)).all() == []
    assert not storage_dir.exists() or not any(path.is_file() for path in storage_dir.rglob("*"))
