from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from types import MappingProxyType

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.letter_context import (
    FormatLetterContextResult,
    FormatLetterNoticeVariant,
)
from app.modules.documents.letter_render_service import RenderedFormatLetter
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
    LetterHandoff,
    LetterHandoffAttachment,
)
from app.modules.official_workflows import service as workflow_service
from app.modules.templates.models import FormatLetterMapping, Template

CASE_ID = "00000000-0000-0000-0000-000000000001"
SOURCE_DOCUMENT_ID = "00000000-0000-0000-0000-000000000002"
SOURCE_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000003"
SOURCE_EVIDENCE_VERSION_ID = "00000000-0000-0000-0000-000000000004"
HANDOFF_ID = "00000000-0000-0000-0000-000000000005"
HANDOFF_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000006"
ACTOR_ID = "00000000-0000-0000-0000-000000000007"
FILE_NAME = "CASE-001-给申请人甲的邮件.docx"
RENDERED_CONTENT = b"rendered-format-letter"
CONTENT_HASH = f"sha256:{hashlib.sha256(RENDERED_CONTENT).hexdigest()}"


def _context_result() -> FormatLetterContextResult:
    return FormatLetterContextResult(
        case_id=CASE_ID,
        source_document_id=SOURCE_DOCUMENT_ID,
        source_evidence_version_id=SOURCE_EVIDENCE_VERSION_ID,
        mapping_id="00000000-0000-0000-0000-000000000008",
        template_id="00000000-0000-0000-0000-000000000009",
        template_family_code="FORMAT_LETTER",
        template_variant_code="FORMAT_LETTER_002",
        template_file_path="templates/format_letters/format_letter_002.docx",
        notice_variant=FormatLetterNoticeVariant.PRELIMINARY_PASS,
        selected_contact_id=None,
        contact_selection_source="UNCONFIRMED",
        salutation_source="DEFAULT",
        context=MappingProxyType({"salutation_text": "尊敬的客户："}),
    )


def _rendered_letter() -> RenderedFormatLetter:
    return RenderedFormatLetter(
        file_name=FILE_NAME,
        media_type=("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        content=RENDERED_CONTENT,
        content_hash=CONTENT_HASH,
    )


def _seed(transaction: Session) -> None:
    transaction.add(Case(id=CASE_ID, case_no="CASE-001"))
    transaction.flush()
    transaction.add(
        Template(
            id="00000000-0000-0000-0000-000000000009",
            name="格式函模板",
            group="FORMAT_LETTER",
            language="zh-CN",
            file_path="templates/format_letters/format_letter_002.docx",
            enabled=True,
        )
    )
    transaction.flush()
    transaction.add(
        FormatLetterMapping(
            id="00000000-0000-0000-0000-000000000008",
            format_letter_template_id="00000000-0000-0000-0000-000000000009",
            format_letter_template_code="FORMAT_LETTER_002",
            enabled=True,
        )
    )
    transaction.flush()
    transaction.add(
        Document(
            id=SOURCE_DOCUMENT_ID,
            case_id=CASE_ID,
            direction="IN",
            doc_date=date(2026, 7, 27),
            title="初步审查合格",
        )
    )
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=SOURCE_ATTACHMENT_ID,
            document_id=SOURCE_DOCUMENT_ID,
            file_name="official.pdf",
            file_path="evidence/official.pdf",
            mime_type="application/pdf",
            content_hash=f"sha256:{'a' * 64}",
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=SOURCE_EVIDENCE_VERSION_ID,
            case_id=CASE_ID,
            document_id=SOURCE_DOCUMENT_ID,
            attachment_id=SOURCE_ATTACHMENT_ID,
            lineage_key="official:source",
            role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=ACTOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=ACTOR_ID,
            reviewed_at=datetime(2026, 7, 27, 9, 0),
            content_hash=f"sha256:{'a' * 64}",
            current_identity_key=f"{CASE_ID}|official:source",
        )
    )
    transaction.add(
        LetterHandoff(
            id=HANDOFF_ID,
            source_document_id=SOURCE_DOCUMENT_ID,
            format_letter_mapping_id="00000000-0000-0000-0000-000000000008",
            format_letter_template_id="00000000-0000-0000-0000-000000000009",
            client_contact_id=None,
            contact_selection_source="UNCONFIRMED",
            salutation_source="DEFAULT",
            salutation_text="尊敬的客户：",
            generated_word_path=f"letters/CASE-001/{FILE_NAME}",
            longxia_handoff_status="READY",
        )
    )
    transaction.flush()
    transaction.add(
        LetterHandoffAttachment(
            id=HANDOFF_ATTACHMENT_ID,
            handoff_id=HANDOFF_ID,
            attachment_id=None,
            file_name=FILE_NAME,
            file_path=f"letters/CASE-001/{FILE_NAME}",
            attachment_role="FORMAT_LETTER_WORD",
            required=True,
            included=True,
            sort_order=1,
        )
    )
    transaction.commit()


def test_returns_pending_archive_for_caller_rollback_cleanup_and_exact_retry(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)

        monkeypatch.setattr(
            transaction,
            "commit",
            lambda: pytest.fail("format-letter archive must not commit"),
        )
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
            raising=False,
        )

        pending = workflow_service.archive_format_letter(
            transaction,
            handoff_id=HANDOFF_ID,
            context_result=_context_result(),
            rendered=_rendered_letter(),
            actor_id=ACTOR_ID,
        )

        assert isinstance(pending, workflow_service.PendingFormatLetterArchive)
        result = pending.evidence_version
        assert isinstance(result, EvidenceVersionResult)
        assert (
            result.case_id,
            result.role,
            result.state,
            result.creator_id,
            result.review_state,
            result.content_hash,
            result.is_current,
        ) == (
            CASE_ID,
            EvidenceRole.CLIENT_LETTER_WORD,
            EvidenceVersionState.DRAFT,
            ACTOR_ID,
            EvidenceReviewState.PENDING,
            CONTENT_HASH,
            True,
        )

        handoff = transaction.get(LetterHandoff, HANDOFF_ID)
        assert handoff is not None
        assert handoff.generated_document_id == result.document_id

        generated_document = transaction.get(Document, result.document_id)
        generated_attachment = transaction.get(DocAttachment, result.attachment_id)
        assert generated_document is not None
        assert generated_attachment is not None
        assert (
            generated_document.case_id,
            generated_document.direction,
            generated_document.reply_to_id,
            generated_document.title,
        ) == (CASE_ID, "OUT", SOURCE_DOCUMENT_ID, FILE_NAME)
        assert (
            generated_attachment.document_id,
            generated_attachment.file_name,
            generated_attachment.mime_type,
            generated_attachment.file_size,
            generated_attachment.content_hash,
            generated_attachment.is_archive_evidence,
        ) == (
            generated_document.id,
            FILE_NAME,
            _rendered_letter().media_type,
            len(RENDERED_CONTENT),
            CONTENT_HASH,
            True,
        )
        assert pending.managed_file_path == tmp_path / generated_attachment.file_path
        assert pending.managed_file_path.read_bytes() == RENDERED_CONTENT

        handoff_attachment = transaction.get(
            LetterHandoffAttachment,
            HANDOFF_ATTACHMENT_ID,
        )
        assert handoff_attachment is not None
        assert handoff_attachment.attachment_id == generated_attachment.id

        derivation = transaction.scalar(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.child_evidence_version_id == result.evidence_version_id
            )
        )
        assert derivation is not None
        assert (
            derivation.case_id,
            derivation.parent_evidence_version_id,
            derivation.derivation_type,
            derivation.actor_id,
        ) == (
            CASE_ID,
            SOURCE_EVIDENCE_VERSION_ID,
            EvidenceDerivationType.CUSTOMER_LETTER_RENDER.value,
            ACTOR_ID,
        )
        source_snapshot = json.loads(derivation.source_snapshot)
        assert source_snapshot["handoff_id"] == HANDOFF_ID
        assert source_snapshot["source_document_id"] == SOURCE_DOCUMENT_ID
        assert source_snapshot["source_evidence_version_id"] == SOURCE_EVIDENCE_VERSION_ID
        assert source_snapshot["rendered_content_hash"] == CONTENT_HASH
        assert source_snapshot["format_letter_mapping_id"] == _context_result().mapping_id
        assert source_snapshot["format_letter_template_id"] == _context_result().template_id
        assert source_snapshot["client_contact_id"] is None
        assert (
            source_snapshot["contact_selection_source"]
            == _context_result().contact_selection_source
        )
        assert source_snapshot["salutation_source"] == _context_result().salutation_source
        assert source_snapshot["salutation_text"] == "尊敬的客户："

        transaction.rollback()
        workflow_service._remove_format_letter_archive_file(
            pending.managed_file_path,
            expected_identity=pending.managed_file_identity,
            original_error=RuntimeError("caller rollback"),
        )
        assert not pending.managed_file_path.exists()

    with session_factory() as retry_transaction:
        monkeypatch.setattr(
            retry_transaction,
            "commit",
            lambda: pytest.fail("format-letter archive retry must not commit"),
        )
        retried = workflow_service.archive_format_letter(
            retry_transaction,
            handoff_id=HANDOFF_ID,
            context_result=_context_result(),
            rendered=_rendered_letter(),
            actor_id=ACTOR_ID,
        )

        assert retried.managed_file_path.read_bytes() == RENDERED_CONTENT
        retry_transaction.rollback()
        workflow_service._remove_format_letter_archive_file(
            retried.managed_file_path,
            expected_identity=retried.managed_file_identity,
            original_error=RuntimeError("retry rollback"),
        )


def test_rejects_old_in_source_when_the_true_latest_in_document_has_no_qualifying_evidence(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        transaction.add(
            Document(
                id="00000000-0000-0000-0000-000000000020",
                case_id=CASE_ID,
                direction="IN",
                doc_date=date(2026, 7, 28),
                title="更新的官方来文",
            )
        )
        transaction.commit()
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409
        assert not (tmp_path / f"letters/CASE-001/{FILE_NAME}").exists()


def test_requires_exactly_one_qualifying_evidence_on_the_latest_in_document(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        second_attachment_id = "00000000-0000-0000-0000-000000000021"
        transaction.add(
            DocAttachment(
                id=second_attachment_id,
                document_id=SOURCE_DOCUMENT_ID,
                file_name="official-second.pdf",
                file_path="evidence/official-second.pdf",
                mime_type="application/pdf",
                content_hash=f"sha256:{'b' * 64}",
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id="00000000-0000-0000-0000-000000000022",
                case_id=CASE_ID,
                document_id=SOURCE_DOCUMENT_ID,
                attachment_id=second_attachment_id,
                lineage_key="official:source:second",
                role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id=ACTOR_ID,
                review_state=EvidenceReviewState.APPROVED.value,
                reviewer_id=ACTOR_ID,
                reviewed_at=datetime(2026, 7, 27, 9, 1),
                content_hash=f"sha256:{'b' * 64}",
                current_identity_key=f"{CASE_ID}|official:source:second",
            )
        )
        transaction.commit()
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409


def test_rejects_duplicate_format_letter_word_handoff_rows(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        transaction.add(
            LetterHandoffAttachment(
                id="00000000-0000-0000-0000-000000000023",
                handoff_id=HANDOFF_ID,
                attachment_id=None,
                file_name=FILE_NAME,
                file_path=f"letters/CASE-001/{FILE_NAME}",
                attachment_role="FORMAT_LETTER_WORD",
                required=True,
                included=True,
                sort_order=2,
            )
        )
        transaction.commit()
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("file_name", "different.docx"),
        ("file_path", "letters/CASE-001/different.docx"),
        ("required", False),
        ("included", False),
    ),
)
def test_rejects_inconsistent_format_letter_word_handoff_row(
    field: str,
    value: object,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        row = transaction.get(LetterHandoffAttachment, HANDOFF_ATTACHMENT_ID)
        assert row is not None
        setattr(row, field, value)
        transaction.commit()
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409


def test_actor_id_must_be_byte_exact_trimmed_before_any_file_write(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=" actor-1 ",
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409
        assert not (tmp_path / f"letters/CASE-001/{FILE_NAME}").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("mapping_id", "00000000-0000-0000-0000-000000000030"),
        ("template_id", "00000000-0000-0000-0000-000000000031"),
        ("selected_contact_id", "00000000-0000-0000-0000-000000000032"),
        ("contact_selection_source", "PRIMARY"),
        ("salutation_source", "MAPPING"),
    ),
)
def test_rejects_context_provenance_that_differs_from_the_persisted_handoff(
    field: str,
    value: str,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        mismatched_context = replace(_context_result(), **{field: value})
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=mismatched_context,
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409
        assert not (tmp_path / f"letters/CASE-001/{FILE_NAME}").exists()


def test_rejects_salutation_text_that_differs_from_the_persisted_handoff(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        mismatched_context = replace(
            _context_result(),
            context=MappingProxyType({"salutation_text": "尊敬的另一位客户："}),
        )
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=mismatched_context,
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409
        assert not (tmp_path / f"letters/CASE-001/{FILE_NAME}").exists()


def test_partial_storage_write_is_cleaned_before_the_error_escapes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )
        original_open = Path.open

        class PartialWriter:
            def __init__(self, path: Path) -> None:
                self.stream = original_open(path, "xb")

            def __enter__(self) -> "PartialWriter":
                return self

            def __exit__(self, *_args: object) -> None:
                self.stream.close()

            def fileno(self) -> int:
                return self.stream.fileno()

            def write(self, _content: bytes) -> int:
                self.stream.write(b"partial")
                self.stream.flush()
                raise OSError("write interrupted")

            def flush(self) -> None:
                self.stream.flush()

        def partial_open(path: Path, mode: str = "r", *args: object, **kwargs: object):
            if path == managed_path and mode == "xb":
                return PartialWriter(path)
            return original_open(path, mode, *args, **kwargs)

        managed_path = tmp_path / f"letters/CASE-001/{FILE_NAME}"
        monkeypatch.setattr(Path, "open", partial_open)

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_STORAGE_ERROR"
        assert caught.value.status_code == 500
        assert not managed_path.exists()
        transaction.rollback()


def test_existing_archive_path_is_a_409_and_is_never_overwritten(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    managed_path = tmp_path / f"letters/CASE-001/{FILE_NAME}"
    managed_path.parent.mkdir(parents=True)
    managed_path.write_bytes(b"other-success")
    with session_factory() as transaction:
        _seed(transaction)
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_CONFLICT"
        assert caught.value.status_code == 409
        assert managed_path.read_bytes() == b"other-success"


def test_operational_storage_failure_is_a_500(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    managed_parent = tmp_path / "letters/CASE-001"
    original_mkdir = Path.mkdir

    def failed_mkdir(path: Path, *args: object, **kwargs: object) -> None:
        if path == managed_parent:
            raise OSError("storage unavailable")
        original_mkdir(path, *args, **kwargs)

    with session_factory() as transaction:
        _seed(transaction)
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )
        monkeypatch.setattr(Path, "mkdir", failed_mkdir)

        with pytest.raises(BusinessError) as caught:
            workflow_service.archive_format_letter(
                transaction,
                handoff_id=HANDOFF_ID,
                context_result=_context_result(),
                rendered=_rendered_letter(),
                actor_id=ACTOR_ID,
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_STORAGE_ERROR"
        assert caught.value.status_code == 500


def test_compensation_refuses_to_unlink_a_replaced_file(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        monkeypatch.setattr(
            workflow_service,
            "_format_letter_storage_root",
            lambda: tmp_path,
        )
        pending = workflow_service.archive_format_letter(
            transaction,
            handoff_id=HANDOFF_ID,
            context_result=_context_result(),
            rendered=_rendered_letter(),
            actor_id=ACTOR_ID,
        )
        pending.managed_file_path.unlink()
        pending.managed_file_path.write_bytes(b"other-success")

        with pytest.raises(BusinessError) as caught:
            workflow_service._remove_format_letter_archive_file(
                pending.managed_file_path,
                expected_identity=pending.managed_file_identity,
                original_error=RuntimeError("caller rollback"),
            )

        assert caught.value.code == "FORMAT_LETTER_ARCHIVE_COMPENSATION_FAILED"
        assert caught.value.status_code == 500
        assert pending.managed_file_path.read_bytes() == b"other-success"


def test_path_lock_serializes_compensation_with_a_successful_retry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    managed_path = tmp_path / "letters/CASE-001/format-letter.docx"
    first_identity = workflow_service._create_format_letter_archive_file(
        managed_path,
        b"first",
    )
    stat_entered = threading.Event()
    creator_attempted = threading.Event()
    creator_errors: list[Exception] = []
    original_stat = Path.stat
    delayed_once = False

    def delayed_stat(path: Path, *args: object, **kwargs: object):
        nonlocal delayed_once
        result = original_stat(path, *args, **kwargs)
        if path == managed_path and not delayed_once:
            delayed_once = True
            stat_entered.set()
            assert creator_attempted.wait(timeout=2)
        return result

    monkeypatch.setattr(Path, "stat", delayed_stat)

    def create_retry() -> None:
        assert stat_entered.wait(timeout=2)
        creator_attempted.set()
        try:
            workflow_service._create_format_letter_archive_file(
                managed_path,
                b"second",
            )
        except Exception as exc:  # pragma: no cover - asserted below
            creator_errors.append(exc)

    creator = threading.Thread(target=create_retry)
    creator.start()
    workflow_service._remove_format_letter_archive_file(
        managed_path,
        expected_identity=first_identity,
        original_error=RuntimeError("caller rollback"),
    )
    creator.join(timeout=2)

    assert not creator.is_alive()
    assert creator_errors == []
    assert managed_path.read_bytes() == b"second"
