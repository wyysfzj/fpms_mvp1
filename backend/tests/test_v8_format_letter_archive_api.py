from __future__ import annotations

import inspect
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import get_type_hints
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.documents.letter_render_service import RenderedFormatLetter
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
    LetterHandoff,
)
from app.modules.masterdata.clients.models import Client, ClientContact
from app.modules.official_workflows import api as workflow_api
from app.modules.official_workflows import schemas as workflow_schemas
from app.modules.official_workflows import service as workflow_service
from app.modules.templates.models import FormatLetterMapping, Template

SOURCE_DOCUMENT_ID = UUID("00000000-0000-0000-0000-000000000101")
OPERATION_ID = UUID("00000000-0000-0000-0000-000000000102")
ACTOR_ID = "00000000-0000-0000-0000-000000000103"
CONTENT_HASH = f"sha256:{'a' * 64}"
CASE_ID = "00000000-0000-0000-0000-000000000110"
SOURCE_EVIDENCE_ID = "00000000-0000-0000-0000-000000000111"
SOURCE_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000112"
DOC_TEMPLATE_ID = "00000000-0000-0000-0000-000000000113"
MAPPING_ID = "00000000-0000-0000-0000-000000000114"
TEMPLATE_ID = "00000000-0000-0000-0000-000000000115"
CLIENT_ID = "00000000-0000-0000-0000-000000000117"
CONTACT_ID = "00000000-0000-0000-0000-000000000118"
RENDERED_CONTENT = b"format-letter-archive-api-content"
RENDERED_HASH = __import__("hashlib").sha256(RENDERED_CONTENT).hexdigest()


def test_format_letter_archive_api_route_contract_is_exposed() -> None:
    route = next(
        (
            item
            for item in workflow_api.router.routes
            if item.path == "/official-documents/{source_document_id}/format-letter-archive"
        ),
        None,
    )

    assert route is not None
    assert route.methods == {"POST"}
    assert route.status_code == 201
    assert route.response_model is workflow_schemas.FormatLetterArchiveOut
    signature = inspect.signature(route.endpoint)
    assert get_type_hints(route.endpoint)["source_document_id"] is UUID
    assert signature.parameters["current_user"].default is workflow_api.current_user_dep


def test_format_letter_archive_payload_keeps_explicit_uuid_and_normalizes_remark() -> None:
    payload = workflow_schemas.FormatLetterArchiveIn(
        operation_id=OPERATION_ID,
        selected_contact_id=None,
        remark="  本次归档  ",
    )

    assert payload.operation_id == OPERATION_ID
    assert payload.selected_contact_id is None
    assert payload.remark == "本次归档"

    with pytest.raises(ValueError):
        workflow_schemas.FormatLetterArchiveIn(
            operation_id=OPERATION_ID,
            remark="x" * 2001,
        )


def test_format_letter_archive_endpoint_injects_actor_and_commits_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = SimpleNamespace(marker="prepared", reused=False)
    calls: list[workflow_service.FormatLetterArchiveCommand] = []

    def prepare(command, transaction):
        calls.append(command)
        assert transaction is db
        return result

    monkeypatch.setattr(workflow_api, "prepare_format_letter_archive", prepare)
    monkeypatch.setattr(
        workflow_api,
        "format_letter_archive_out",
        lambda transaction, pending, *, reused: {
            "transaction": transaction,
            "pending": pending,
            "reused": reused,
        },
    )
    db = _FakeSession()
    payload = workflow_schemas.FormatLetterArchiveIn(
        operation_id=OPERATION_ID,
        selected_contact_id=None,
        remark="本次归档",
    )

    response = workflow_api.archive_format_letter_endpoint(
        source_document_id=SOURCE_DOCUMENT_ID,
        payload=payload,
        current_user=SimpleNamespace(id=ACTOR_ID),
        _perm=None,
        db=db,
    )

    assert calls == [
        workflow_service.FormatLetterArchiveCommand(
            source_document_id=str(SOURCE_DOCUMENT_ID),
            operation_id=str(OPERATION_ID),
            selected_contact_id=None,
            remark="本次归档",
            actor_id=ACTOR_ID,
        )
    ]
    assert db.commits == 1
    assert db.rollbacks == 0
    assert response == {"transaction": db, "pending": result, "reused": False}


def test_format_letter_archive_endpoint_rolls_back_and_compensates_commit_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pending = SimpleNamespace(
        reused=False,
        managed_file_path="/managed/letter.docx",
        managed_file_identity=(1, 2),
    )
    db = _FakeSession(commit_error=RuntimeError("commit failed"))
    monkeypatch.setattr(
        workflow_api,
        "prepare_format_letter_archive",
        lambda command, transaction: pending,
    )
    cleanup_calls: list[tuple[object, tuple[int, int], Exception]] = []

    def cleanup(path, *, expected_identity, original_error):
        cleanup_calls.append((path, expected_identity, original_error))

    monkeypatch.setattr(workflow_api, "_remove_format_letter_archive_file", cleanup)

    with pytest.raises(Exception) as caught:
        workflow_api.archive_format_letter_endpoint(
            source_document_id=SOURCE_DOCUMENT_ID,
            payload=workflow_schemas.FormatLetterArchiveIn(operation_id=OPERATION_ID),
            current_user=SimpleNamespace(id=ACTOR_ID),
            _perm=None,
            db=db,
        )

    assert getattr(caught.value, "code", None) == "FORMAT_LETTER_ARCHIVE_PERSIST_FAILED"
    assert db.commits == 1
    assert db.rollbacks == 1
    assert cleanup_calls[0][:2] == ("/managed/letter.docx", (1, 2))


def test_format_letter_archive_api_creates_exact_lineage_and_replays_without_new_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _seed_ready_source(session_factory)
    rendered = RenderedFormatLetter(
        file_name="CASE-LETTER-API-给申请人甲的邮件.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        content=RENDERED_CONTENT,
        content_hash=f"sha256:{RENDERED_HASH}",
    )
    monkeypatch.setattr(workflow_service, "render_format_letter", lambda context: rendered)
    monkeypatch.setattr(workflow_service, "_format_letter_storage_root", lambda: tmp_path)
    payload = {
        "operation_id": str(OPERATION_ID),
        "selected_contact_id": None,
        "remark": "  本次归档  ",
    }

    created_response = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        headers=auth_headers,
        json=payload,
    )

    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created == {
        "handoff": created["handoff"],
        "evidence_version_id": created["evidence_version_id"],
        "version_number": 1,
        "content_hash": f"sha256:{RENDERED_HASH}",
        "generated_document_id": created["generated_document_id"],
        "attachment_id": created["attachment_id"],
        "file_name": rendered.file_name,
        "role": "CLIENT_LETTER_WORD",
        "state": "DRAFT",
        "review_state": "PENDING",
        "is_current": True,
        "reused": False,
    }
    assert created["handoff"]["id"] == str(OPERATION_ID)
    assert created["handoff"]["source_document_id"] == str(SOURCE_DOCUMENT_ID)
    assert created["handoff"]["remark"] == "本次归档"
    assert created["handoff"]["client_contact_id"] == CONTACT_ID
    assert created["handoff"]["contact_selection_source"] == "PRIMARY"
    assert created["handoff"]["salutation_source"] == "SELECTED_CONTACT"
    assert len(created["handoff"]["attachments"]) == 1
    assert created["handoff"]["attachments"][0]["attachment_id"] == created["attachment_id"]
    managed_path = tmp_path / f"letters/CASE-LETTER-API/{rendered.file_name}"
    assert managed_path.read_bytes() == RENDERED_CONTENT

    with session_factory() as db:
        actor_id = db.scalar(select(T_User.id).where(T_User.username == "admin"))
        version_count = db.scalar(select(func.count(DocumentEvidenceVersion.id)))
        document_count = db.scalar(select(func.count(Document.id)))
        attachment_count = db.scalar(select(func.count(DocAttachment.id)))
        stored = db.get(LetterHandoff, str(OPERATION_ID))
        assert stored is not None
        version = db.get(DocumentEvidenceVersion, created["evidence_version_id"])
        assert version is not None
        assert version.creator_id == actor_id

    replay_response = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        headers=auth_headers,
        json=payload,
    )

    assert replay_response.status_code == 201, replay_response.text
    assert replay_response.json() == {**created, "reused": True}
    assert managed_path.read_bytes() == RENDERED_CONTENT
    with session_factory() as db:
        assert db.scalar(select(func.count(DocumentEvidenceVersion.id))) == version_count
        assert db.scalar(select(func.count(Document.id))) == document_count
        assert db.scalar(select(func.count(DocAttachment.id))) == attachment_count

    drift_response = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        headers=auth_headers,
        json={**payload, "remark": "另一条备注"},
    )
    assert drift_response.status_code == 409, drift_response.text
    assert drift_response.json()["error"]["code"] == "FORMAT_LETTER_ARCHIVE_CONFLICT"


def test_format_letter_archive_api_keeps_auth_and_uuid_validation_boundaries(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    unauthenticated = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        json={"operation_id": str(OPERATION_ID)},
    )
    invalid_operation = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        headers=auth_headers,
        json={"operation_id": "not-a-uuid"},
    )
    invalid_source = client.post(
        "/api/v1/official-documents/not-a-uuid/format-letter-archive",
        headers=auth_headers,
        json={"operation_id": str(OPERATION_ID)},
    )

    assert unauthenticated.status_code == 401
    assert invalid_operation.status_code == 422
    assert invalid_source.status_code == 422


@pytest.mark.parametrize(
    ("drift", "expected_status", "expected_code"),
    (
        ("OUT", 400, "FORMAT_LETTER_SOURCE_DIRECTION_INVALID"),
        ("STALE", 409, "FORMAT_LETTER_ARCHIVE_CONFLICT"),
        ("UNREVIEWED", 409, "FORMAT_LETTER_SOURCE_UNREVIEWED"),
        ("PARTIAL", 409, "FORMAT_LETTER_ARCHIVE_CONFLICT"),
    ),
)
def test_format_letter_archive_api_rejects_ineligible_or_partial_source_state(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    drift: str,
    expected_status: int,
    expected_code: str,
) -> None:
    _seed_ready_source(session_factory)
    with session_factory() as db:
        source = db.get(Document, str(SOURCE_DOCUMENT_ID))
        assert source is not None
        if drift == "OUT":
            source.direction = "OUT"
        elif drift == "STALE":
            db.add(
                Document(
                    id="00000000-0000-0000-0000-000000000119",
                    case_id=CASE_ID,
                    direction="IN",
                    doc_date=date(2026, 8, 10),
                    title="更新官文",
                    created_at=datetime(2026, 8, 10, 8, 0),
                    updated_at=datetime(2026, 8, 10, 8, 0),
                )
            )
        elif drift == "UNREVIEWED":
            evidence = db.get(DocumentEvidenceVersion, SOURCE_EVIDENCE_ID)
            assert evidence is not None
            evidence.review_state = "PENDING"
            evidence.reviewer_id = None
            evidence.reviewed_at = None
        else:
            db.add(
                LetterHandoff(
                    id=str(OPERATION_ID),
                    source_document_id=str(SOURCE_DOCUMENT_ID),
                    remark=None,
                )
            )
        db.commit()

    response = client.post(
        f"/api/v1/official-documents/{SOURCE_DOCUMENT_ID}/format-letter-archive",
        headers=auth_headers,
        json={"operation_id": str(OPERATION_ID)},
    )

    assert response.status_code == expected_status, response.text
    assert response.json()["error"]["code"] == expected_code


def _seed_ready_source(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as db:
        client = Client(
            id=CLIENT_ID,
            client_code="CLIENT-LETTER-API",
            name_cn="格式函客户",
            client_type="CLIENT",
            default_currency="CNY",
            is_active=True,
        )
        db.add(client)
        db.flush()
        contact = ClientContact(
            id=CONTACT_ID,
            client_id=client.id,
            contact_name="张三",
            title="老师",
            is_primary=True,
        )
        db.add(contact)
        db.flush()
        case = Case(
            id=CASE_ID,
            case_no="CASE-LETTER-API",
            status="OPEN",
            client_id=client.id,
            title_cn="格式函归档案件",
            app_no="CN202610000001.0",
            filing_date=date(2025, 1, 2),
        )
        doc_template = DocTemplate(
            id=DOC_TEMPLATE_ID,
            code="FORMAT-LETTER-API-IN",
            name="格式函归档官文",
            direction="IN",
            enabled=True,
        )
        template = Template(
            id=TEMPLATE_ID,
            name="FORMAT_LETTER_002",
            group="FORMAT_LETTER",
            language="zh-CN",
            file_path="templates/format_letters/FORMAT_LETTER_002.docx",
            enabled=True,
        )
        db.add_all([case, doc_template, template])
        db.flush()
        source = Document(
            id=str(SOURCE_DOCUMENT_ID),
            case_id=CASE_ID,
            doc_template_id=DOC_TEMPLATE_ID,
            direction="IN",
            doc_date=date(2026, 8, 9),
            title="初步审查合格",
            created_at=datetime(2026, 8, 9, 8, 0),
            updated_at=datetime(2026, 8, 9, 8, 0),
        )
        mapping = FormatLetterMapping(
            id=MAPPING_ID,
            official_doc_template_id=DOC_TEMPLATE_ID,
            official_doc_template_code=doc_template.code,
            official_doc_name_pattern=source.title,
            format_letter_template_id=TEMPLATE_ID,
            format_letter_template_code=template.name,
            enabled=True,
        )
        applicant = T_CaseApplicant(
            id="00000000-0000-0000-0000-000000000116",
            case_id=CASE_ID,
            seq=1,
            is_first=True,
            name_cn="申请人甲",
        )
        db.add_all([source, mapping, applicant])
        db.flush()
        attachment = DocAttachment(
            id=SOURCE_ATTACHMENT_ID,
            document_id=source.id,
            file_name="official.pdf",
            file_path="evidence/official.pdf",
            content_hash=f"sha256:{'b' * 64}",
        )
        db.add(attachment)
        db.flush()
        db.add(
            DocumentEvidenceVersion(
                id=SOURCE_EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=source.id,
                attachment_id=attachment.id,
                lineage_key="official:source",
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id="source-creator",
                review_state="APPROVED",
                reviewer_id="source-reviewer",
                reviewed_at=datetime(2026, 8, 9, 8, 5),
                content_hash=attachment.content_hash,
                current_identity_key=f"{CASE_ID}|official:source",
            )
        )
        db.commit()


class _FakeSession:
    def __init__(self, *, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollbacks += 1
