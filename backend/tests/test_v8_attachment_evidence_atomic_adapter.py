from __future__ import annotations

import json
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.core.security import get_password_hash
from app.modules.annuity.models import GovPayment
from app.modules.auth.models import T_User
from app.modules.billing.models import Payment
from app.modules.cases.lifecycle_contracts import ActivityLane
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import api as documents_api
from app.modules.documents import service as documents_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.fees.models import FeeDraft, FeeObligation, T_GrantFeeTask
from app.modules.grant_fees import service as grant_fee_service

DOC_BASE = "/api/v1/documents"
WORD_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

OTHER_EXPLICIT_ROLES = tuple(
    role
    for role in documents_service._ATTACHMENT_ROLE_DEFINITIONS
    if role != EvidenceRole.FILING_FULL_WORD.value
)


def _create_document(
    session_factory: sessionmaker[Session],
    *,
    legal_status: str | None = None,
) -> tuple[str, str]:
    with session_factory() as db:
        template = db.scalar(select(DocTemplate).where(DocTemplate.code == "OA_OUT"))
        assert template is not None
        case = Case(
            id=str(uuid4()),
            case_no=f"ATT-EVIDENCE-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="附件证据原子适配测试案件",
            legal_status=legal_status,
        )
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            direction="OUT",
            doc_date=date(2026, 7, 14),
            title="附件证据原子适配文书",
        )
        db.add_all([case, document])
        db.commit()
        return case.id, document.id


def _create_executable_grant_document(
    session_factory: sessionmaker[Session],
) -> tuple[str, str]:
    with session_factory() as db:
        template = db.scalar(select(DocTemplate).where(DocTemplate.code == "GRANT_NOTICE"))
        assert template is not None
        case = Case(
            id=str(uuid4()),
            case_no=f"ATT-GRANT-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="附件授权载体事务测试案件",
            status="GRANT_PENDING",
        )
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            direction="IN",
            doc_date=date(2026, 7, 15),
            title="授权通知书",
            extra_data=json.dumps(
                {
                    "OfficialDueDate": "2026-09-15",
                    "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                    "OfficialDueDateStatus": "CONFIRMED",
                }
            ),
        )
        db.add_all([case, document])
        db.commit()
        return case.id, document.id


def _upload_spec(role: str) -> tuple[str, str]:
    normalized_role = role.strip().upper()
    if normalized_role in {"FILING_FULL_WORD", "OA_STATEMENT_WORD", "OA_MODIFIED_CLAIMS"}:
        return f"{role}.docx", WORD_MIME
    if normalized_role == "FILING_XML_ZIP":
        return f"{role}.zip", "application/zip"
    if normalized_role in {"FILING_MERGED_PDF", "ELECTRONIC_RECEIPT", "OA_STATEMENT_PDF"}:
        return f"{role}.pdf", "application/pdf"
    if normalized_role in {"OA_AMENDMENT_COMPARISON", "OA_OTHER_PROOF", "OA_ADDITIONAL_FILE"}:
        return f"{role}.pdf", "application/pdf"
    return f"{role}.bin", "application/octet-stream"


def _post_attachment(
    client: TestClient,
    auth_headers: dict[str, str],
    document_id: str,
    *,
    role: str | None = None,
    alias: str | None = None,
    content: bytes = b"task-owned-evidence-content",
) -> object:
    upload_role = role or ("FILING_FULL_WORD" if alias == "完整递交文件" else "RAW")
    file_name, mime_type = _upload_spec(upload_role)
    data: dict[str, str] = {}
    if role is not None:
        data["official_file_role"] = role
    if alias is not None:
        data["source_role_alias"] = alias
    return client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
        data=data,
        files={"file": (file_name, BytesIO(content), mime_type)},
    )


def _set_api_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        documents_api,
        "get_settings",
        lambda: SimpleNamespace(storage_dir=str(tmp_path)),
    )


def test_exact_filing_word_post_records_creator_draft_version_and_document_activity(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    case_id, document_id = _create_document(session_factory)

    response = _post_attachment(
        client,
        auth_headers,
        document_id,
        role="FILING_FULL_WORD",
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {
        "id",
        "document_id",
        "file_name",
        "mime_type",
        "file_size",
        "uploaded_at",
        "official_file_role",
        "source_role_alias",
        "external_upload_position",
        "content_hash",
        "package_usage_hint",
        "is_archive_evidence",
        "is_receipt_evidence",
    }

    with session_factory() as db:
        admin = db.scalar(select(T_User).where(T_User.username == "admin"))
        version = db.scalar(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id == body["id"]
            )
        )
        activity = db.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case_id,
                CaseActivityEvent.activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED",
            )
        )
        assert admin is not None
        assert version is not None
        assert activity is not None
        assert (
            version.role,
            version.state,
            version.review_state,
            version.lineage_key,
            version.version_number,
            version.creator_id,
        ) == (
            EvidenceRole.FILING_FULL_WORD.value,
            EvidenceVersionState.DRAFT.value,
            EvidenceReviewState.PENDING.value,
            f"attachment:{body['id']}",
            1,
            admin.id,
        )
        assert activity.lane == ActivityLane.DOCUMENT.value
        assert activity.actor_id == admin.id
        links = db.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert len(links) == 1
        assert links[0].object_id == version.id


@pytest.mark.parametrize("role", OTHER_EXPLICIT_ROLES)
def test_every_other_explicit_role_records_raw_evidence_and_preserves_display_metadata(
    role: str,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    _case_id, document_id = _create_document(session_factory)

    response = _post_attachment(client, auth_headers, document_id, role=role)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["official_file_role"] == role
    with session_factory() as db:
        version = db.scalar(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id == body["id"]
            )
        )
        assert version is not None
        assert version.role == EvidenceRole.RAW_ATTACHMENT.value
        assert version.state == EvidenceVersionState.DRAFT.value


@pytest.mark.parametrize(
    ("role", "alias", "expected_display_role"),
    (
        (None, None, None),
        ("", None, None),
        (None, "完整递交文件", "FILING_FULL_WORD"),
        (" filing_full_word ", None, "FILING_FULL_WORD"),
    ),
)
def test_missing_blank_alias_only_and_nonexact_roles_never_gain_formal_evidence_authority(
    role: str | None,
    alias: str | None,
    expected_display_role: str | None,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    _case_id, document_id = _create_document(session_factory)

    response = _post_attachment(
        client,
        auth_headers,
        document_id,
        role=role,
        alias=alias,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["official_file_role"] == expected_display_role
    with session_factory() as db:
        version = db.scalar(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id == body["id"]
            )
        )
        assert version is not None
        assert version.role == EvidenceRole.RAW_ATTACHMENT.value


def test_repeated_same_hash_posts_create_distinct_version_one_lineages(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    _case_id, document_id = _create_document(session_factory)

    responses = [
        _post_attachment(client, auth_headers, document_id, content=b"same bytes") for _ in range(2)
    ]

    assert [response.status_code for response in responses] == [201, 201]
    attachment_ids = [response.json()["id"] for response in responses]
    assert len(set(attachment_ids)) == 2
    with session_factory() as db:
        versions = db.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id.in_(attachment_ids)
            )
        ).all()
        assert {(item.lineage_key, item.version_number) for item in versions} == {
            (f"attachment:{attachment_id}", 1) for attachment_id in attachment_ids
        }


class _Upload:
    def __init__(self, content: bytes = b"service upload") -> None:
        self.filename = "service-upload.bin"
        self.content_type = "application/octet-stream"
        self.file = BytesIO(content)


def test_service_returns_pending_uncommitted_result_without_commit_rollback_or_refresh(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_id, document_id = _create_document(session_factory)
    with session_factory() as db:
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not rollback"))
        refresh = Mock(side_effect=AssertionError("adapter must not refresh"))
        monkeypatch.setattr(db, "commit", commit)
        monkeypatch.setattr(db, "rollback", rollback)
        monkeypatch.setattr(db, "refresh", refresh)

        pending = documents_service.add_attachment(
            db,
            document_id,
            upload_file=_Upload(),
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

        assert isinstance(pending, documents_service.PendingAttachmentEvidenceUpload)
        assert isinstance(pending.evidence_version, EvidenceVersionResult)
        assert pending.evidence_version.case_id == case_id
        assert pending.evidence_version.attachment_id == pending.attachment.id
        assert pending.managed_file_path.is_file()
        assert commit.call_count == rollback.call_count == refresh.call_count == 0


def test_executable_grant_carrier_and_evidence_share_outer_transaction_without_fee_writes(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    case_id, document_id = _create_executable_grant_document(session_factory)

    with session_factory() as db:
        pending = documents_service.add_attachment(
            db,
            document_id,
            upload_file=_Upload(),
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

        carrier = db.scalar(
            select(T_GrantFeeTask).where(T_GrantFeeTask.source_document_id == document_id)
        )
        assert carrier is not None
        assert carrier.case_id == case_id
        assert carrier.due_date == date(2026, 9, 15)
        assert db.get(DocAttachment, pending.attachment.id) is pending.attachment
        assert db.get(DocumentEvidenceVersion, pending.evidence_version.evidence_version_id)
        assert db.scalars(select(FeeObligation)).all() == []
        assert db.scalars(select(FeeDraft)).all() == []
        assert db.scalars(select(Payment)).all() == []
        assert db.scalars(select(GovPayment)).all() == []
        db.rollback()

    with session_factory() as verification:
        assert verification.get(DocAttachment, pending.attachment.id) is None
        assert (
            verification.get(
                DocumentEvidenceVersion,
                pending.evidence_version.evidence_version_id,
            )
            is None
        )
        assert (
            verification.scalar(
                select(T_GrantFeeTask).where(T_GrantFeeTask.source_document_id == document_id)
            )
            is None
        )


@pytest.mark.parametrize(
    "boundary",
    (
        "attachment_flush",
        "evidence_version",
        "activity",
        "evidence_link",
        "carrier",
        "final_flush",
    ),
)
def test_each_post_write_failure_boundary_rolls_back_and_cleans_exactly_once(
    boundary: str,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    if boundary == "carrier":
        _case_id, document_id = _create_executable_grant_document(session_factory)
        monkeypatch.setattr(
            grant_fee_service,
            "ensure_grant_fee_task_for_notice_document",
            Mock(side_effect=RuntimeError("carrier failure")),
        )
    else:
        _case_id, document_id = _create_document(session_factory)

    original_flush = Session.flush
    flush_calls = 0

    def injected_flush(self: Session, *args: object, **kwargs: object) -> None:
        nonlocal flush_calls
        flush_calls += 1
        if (boundary == "attachment_flush" and flush_calls == 1) or (
            boundary == "final_flush" and flush_calls == 4
        ):
            raise RuntimeError(f"{boundary} failure")
        original_flush(self, *args, **kwargs)

    original_add = Session.add

    def injected_add(self: Session, instance: object, *args: object, **kwargs: object) -> None:
        if boundary == "evidence_version" and isinstance(instance, DocumentEvidenceVersion):
            raise RuntimeError("evidence version failure")
        if boundary == "activity" and isinstance(instance, CaseActivityEvent):
            raise RuntimeError("activity failure")
        original_add(self, instance, *args, **kwargs)

    original_add_all = Session.add_all

    def injected_add_all(
        self: Session,
        instances: object,
        *args: object,
        **kwargs: object,
    ) -> None:
        materialized = tuple(instances)  # type: ignore[arg-type]
        if boundary == "evidence_link" and any(
            isinstance(instance, CaseActivityEventEvidence) for instance in materialized
        ):
            raise RuntimeError("evidence link failure")
        original_add_all(self, materialized, *args, **kwargs)

    rollback_calls: list[Session] = []
    original_rollback = Session.rollback

    def tracked_rollback(self: Session) -> None:
        rollback_calls.append(self)
        original_rollback(self)

    monkeypatch.setattr(Session, "flush", injected_flush)
    monkeypatch.setattr(Session, "add", injected_add)
    monkeypatch.setattr(Session, "add_all", injected_add_all)
    monkeypatch.setattr(Session, "rollback", tracked_rollback)

    original_cleanup = documents_service._remove_managed_attachment_file
    service_cleanup = Mock(wraps=original_cleanup)
    api_cleanup = Mock(side_effect=AssertionError("API must not double-delete pre-return files"))
    monkeypatch.setattr(documents_service, "_remove_managed_attachment_file", service_cleanup)
    monkeypatch.setattr(documents_api, "_remove_managed_attachment_file", api_cleanup)

    response = _post_attachment(client, auth_headers, document_id)

    assert response.status_code == 500, response.text
    assert response.json()["error"]["code"] == "ATTACHMENT_PERSIST_FAILED"
    assert len(rollback_calls) == 1
    assert service_cleanup.call_count == 1
    assert api_cleanup.call_count == 0
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


@pytest.mark.parametrize("ordinary", (False, True))
def test_post_write_failure_is_service_compensated_and_preserves_or_maps_error(
    ordinary: bool,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _case_id, document_id = _create_document(session_factory)
    original = (
        RuntimeError("persist exploded")
        if ordinary
        else BusinessError("LIFECYCLE_PROJECTION_CONFLICT", "projection conflict", status_code=409)
    )
    monkeypatch.setattr(
        documents_service,
        "register_evidence_version",
        Mock(side_effect=original),
    )

    with session_factory() as db, pytest.raises(BusinessError) as exc_info:
        documents_service.add_attachment(
            db,
            document_id,
            upload_file=_Upload(),
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

    assert not any(path.is_file() for path in tmp_path.rglob("*"))
    if ordinary:
        assert exc_info.value.code == "ATTACHMENT_PERSIST_FAILED"
        assert exc_info.value.status_code == 500
    else:
        assert exc_info.value is original


def test_write_failure_cleans_partial_file_and_maps_storage_error(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    _case_id, document_id = _create_document(session_factory)
    upload = _Upload()
    upload.file = Mock()
    upload.file.read.side_effect = [b"partial", RuntimeError("read exploded")]

    with session_factory() as db, pytest.raises(BusinessError) as exc_info:
        documents_service.add_attachment(
            db,
            document_id,
            upload_file=upload,
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

    assert exc_info.value.code == "ATTACHMENT_STORAGE_WRITE_FAILED"
    assert exc_info.value.status_code == 500
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


def test_size_limit_business_error_is_preserved_after_partial_file_cleanup(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    _case_id, document_id = _create_document(session_factory)
    upload = _Upload(b"x" * (25 * 1024 * 1024 + 1))

    with session_factory() as db, pytest.raises(BusinessError) as exc_info:
        documents_service.add_attachment(
            db,
            document_id,
            upload_file=upload,
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

    assert exc_info.value.code == "ATTACHMENT_TOO_LARGE"
    assert exc_info.value.status_code == 400
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


def test_prefile_validation_never_creates_or_cleans_a_managed_file(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cleanup = Mock(side_effect=AssertionError("prefile failure must not clean"))
    monkeypatch.setattr(documents_service, "_remove_managed_attachment_file", cleanup)

    with session_factory() as db, pytest.raises(BusinessError) as exc_info:
        documents_service.add_attachment(
            db,
            "missing-document",
            upload_file=_Upload(),
            storage_dir=str(tmp_path),
            actor_id="actor-1",
        )

    assert exc_info.value.code == "DOCUMENT_NOT_FOUND"
    assert exc_info.value.status_code == 404
    assert cleanup.call_count == 0
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


def test_missing_actor_rejects_before_managed_file_creation_or_cleanup(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _case_id, document_id = _create_document(session_factory)
    cleanup = Mock(side_effect=AssertionError("prefile failure must not clean"))
    monkeypatch.setattr(documents_service, "_remove_managed_attachment_file", cleanup)

    with session_factory() as db, pytest.raises(BusinessError) as exc_info:
        documents_service.add_attachment(
            db,
            document_id,
            upload_file=_Upload(),
            storage_dir=str(tmp_path),
            actor_id=" ",
        )

    assert exc_info.value.code == "ATTACHMENT_ACTOR_REQUIRED"
    assert exc_info.value.status_code == 400
    assert cleanup.call_count == 0
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


def _pending(path: Path) -> object:
    attachment = SimpleNamespace(
        id="attachment-1",
        document_id="document-1",
        file_name="secret-original-name.bin",
        mime_type="application/octet-stream",
        file_size=4,
        created_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
        official_file_role=None,
        source_role_alias=None,
        external_upload_position=None,
        content_hash=f"sha256:{'a' * 64}",
        package_usage_hint=None,
        is_archive_evidence=False,
        is_receipt_evidence=False,
    )
    result = SimpleNamespace(attachment=attachment, managed_file_path=path)
    return result


def test_api_commit_failure_rolls_back_and_compensates_only_returned_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "managed.bin"
    path.write_bytes(b"data")
    pending = _pending(path)
    monkeypatch.setattr(documents_api, "add_attachment_service", Mock(return_value=pending))
    db = Mock()
    db.commit.side_effect = RuntimeError("commit exploded")

    with pytest.raises(BusinessError) as exc_info:
        documents_api.add_attachment(
            "document-1",
            file=Mock(),
            official_file_role=None,
            source_role_alias=None,
            _perm=None,
            current_user=SimpleNamespace(id="actor-1"),
            db=db,
        )

    assert exc_info.value.code == "ATTACHMENT_PERSIST_FAILED"
    assert exc_info.value.status_code == 500
    assert "managed.bin" not in str(exc_info.value)
    assert "secret-original-name.bin" not in str(exc_info.value)
    assert db.rollback.call_count == 1
    assert not path.exists()


def test_api_success_commits_once_and_never_compensates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "managed.bin"
    path.write_bytes(b"data")
    pending = _pending(path)
    monkeypatch.setattr(documents_api, "add_attachment_service", Mock(return_value=pending))
    cleanup = Mock(side_effect=AssertionError("successful commit must not compensate"))
    monkeypatch.setattr(documents_api, "_remove_managed_attachment_file", cleanup)
    db = Mock()

    result = documents_api.add_attachment(
        "document-1",
        file=Mock(),
        official_file_role=None,
        source_role_alias=None,
        _perm=None,
        current_user=SimpleNamespace(id="actor-1"),
        db=db,
    )

    assert result.id == "attachment-1"
    assert db.commit.call_count == 1
    assert db.rollback.call_count == 0
    assert cleanup.call_count == 0
    assert path.exists()


@pytest.mark.parametrize("origin", ("write", "persist", "commit"))
def test_missing_file_during_cleanup_preserves_each_originating_error(
    origin: str,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(Path, "unlink", Mock(side_effect=FileNotFoundError))

    if origin == "commit":
        pending = _pending(tmp_path / "already-absent.bin")
        monkeypatch.setattr(
            documents_api,
            "add_attachment_service",
            Mock(return_value=pending),
        )
        db = Mock()
        db.commit.side_effect = RuntimeError("commit exploded")

        def call() -> object:
            return documents_api.add_attachment(
                "document-1",
                file=Mock(),
                official_file_role=None,
                source_role_alias=None,
                _perm=None,
                current_user=SimpleNamespace(id="actor-1"),
                db=db,
            )

        expected_code = "ATTACHMENT_PERSIST_FAILED"
    else:
        _case_id, document_id = _create_document(session_factory)
        upload = _Upload()
        if origin == "write":
            upload.file = Mock()
            upload.file.read.side_effect = RuntimeError("write exploded")
            expected_code = "ATTACHMENT_STORAGE_WRITE_FAILED"
        else:
            monkeypatch.setattr(
                documents_service,
                "register_evidence_version",
                Mock(side_effect=RuntimeError("persist exploded")),
            )
            expected_code = "ATTACHMENT_PERSIST_FAILED"

        def call() -> object:
            with session_factory() as db:
                return documents_service.add_attachment(
                    db,
                    document_id,
                    upload_file=upload,
                    storage_dir=str(tmp_path),
                    actor_id="actor-1",
                )

    with pytest.raises(BusinessError) as exc_info:
        call()

    assert exc_info.value.code == expected_code
    assert exc_info.value.status_code == 500


@pytest.mark.parametrize("origin", ("write", "persist", "commit"))
def test_cleanup_failure_takes_precedence_without_leaking_paths_or_original_filename(
    origin: str,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    residual_path = tmp_path / "residual-secret.bin"
    cleanup_error = PermissionError("cannot delete")
    unlink = Mock(side_effect=cleanup_error)
    logged_error = Mock()
    monkeypatch.setattr(Path, "unlink", unlink)
    monkeypatch.setattr(documents_service.logger, "error", logged_error)

    if origin == "commit":
        original_error = RuntimeError("commit exploded")
        residual_path.write_bytes(b"data")
        monkeypatch.setattr(
            documents_api,
            "add_attachment_service",
            Mock(return_value=_pending(residual_path)),
        )
        db = Mock()
        db.commit.side_effect = original_error
        call = lambda: documents_api.add_attachment(  # noqa: E731
            "document-1",
            file=Mock(),
            official_file_role=None,
            source_role_alias=None,
            _perm=None,
            current_user=SimpleNamespace(id="actor-1"),
            db=db,
        )
    else:
        _case_id, document_id = _create_document(session_factory)
        if origin == "persist":
            original_error = RuntimeError("persist exploded")
            monkeypatch.setattr(
                documents_service,
                "register_evidence_version",
                Mock(side_effect=original_error),
            )
            upload = _Upload()
        else:
            original_error = RuntimeError("write exploded")
            upload = _Upload()
            upload.file = Mock()
            upload.file.read.side_effect = [b"partial", original_error]

        def call() -> object:
            with session_factory() as db:
                return documents_service.add_attachment(
                    db,
                    document_id,
                    upload_file=upload,
                    storage_dir=str(tmp_path),
                    actor_id="actor-1",
                )

    with pytest.raises(BusinessError) as exc_info:
        call()

    assert exc_info.value.code == "ATTACHMENT_STORAGE_COMPENSATION_FAILED"
    assert exc_info.value.status_code == 500
    assert str(tmp_path) not in str(exc_info.value)
    assert "service-upload.bin" not in str(exc_info.value)
    assert "secret-original-name.bin" not in str(exc_info.value)
    assert unlink.call_count == 1
    assert logged_error.call_count == 1
    log_args = logged_error.call_args.args
    assert log_args[0] == ("Attachment compensation failed; residual_path=%s; original_error=%r")
    assert isinstance(log_args[1], Path)
    assert log_args[2] is original_error
    assert logged_error.call_args.kwargs["exc_info"][1] is original_error


def test_http_error_semantics_remain_401_404_422_and_409(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_api_storage(monkeypatch, tmp_path)
    _case_id, document_id = _create_document(session_factory, legal_status="INVALID")
    with session_factory() as db:
        unprivileged = T_User(
            id=str(uuid4()),
            username=f"no-doc-attach-{uuid4().hex[:8]}",
            password_hash=get_password_hash("no-permission-password"),
            is_active=True,
        )
        db.add(unprivileged)
        db.commit()
        unprivileged_username = unprivileged.username
    login = client.post(
        "/api/v1/auth/login",
        json={"username": unprivileged_username, "password": "no-permission-password"},
    )
    assert login.status_code == 200
    forbidden_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    unauthenticated = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        files={"file": ("a.bin", BytesIO(b"a"), "application/octet-stream")},
    )
    forbidden = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=forbidden_headers,
        files={"file": ("a.bin", BytesIO(b"a"), "application/octet-stream")},
    )
    missing_document = _post_attachment(client, auth_headers, "missing-document")
    missing_file = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
    )
    lifecycle_conflict = _post_attachment(client, auth_headers, document_id)

    assert unauthenticated.status_code == 401
    assert forbidden.status_code == 403
    assert missing_document.status_code == 404
    assert missing_document.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"
    assert missing_file.status_code == 422
    assert lifecycle_conflict.status_code == 409
    assert lifecycle_conflict.json()["error"]["code"] == "LIFECYCLE_PROJECTION_CONFLICT"
    assert not any(path.is_file() for path in tmp_path.rglob("*"))
