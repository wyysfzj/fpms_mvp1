from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents import service as documents_service
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.documents.schemas import DocumentWizardBatchCreateIn
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)
from app.modules.tasks.models import Task
from app.modules.templates.models import Template
from app.modules.templates.render import TemplateRenderer

ACTOR_ID = "oa-out-actor"
REVIEWER_ID = "oa-out-reviewer"
RENDERED_CONTENT = b"real-oa-out-package-atomic-link"


@dataclass(frozen=True)
class _Fixture:
    case_id: str
    source_document_id: str
    package_ids: tuple[str, ...]
    task_id: str
    oa_out_template_id: str
    storage_dir: Path


def _hash(seed: str) -> str:
    return f"sha256:{sha256(seed.encode()).hexdigest()}"


def _attachment(
    *,
    document_id: str,
    name: str,
    content_hash: str,
) -> DocAttachment:
    return DocAttachment(
        id=str(uuid4()),
        document_id=document_id,
        file_name=name,
        file_path=f"seed/{uuid4().hex}/{name}",
        mime_type="application/octet-stream",
        file_size=10,
        content_hash=content_hash,
    )


def _version(
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    lineage_key: str,
    role: EvidenceRole,
    content_hash: str,
    approved: bool,
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=lineage_key,
        role=role.value,
        version_number=1,
        state=EvidenceVersionState.FINAL.value,
        creator_id="seed-creator",
        review_state=(
            EvidenceReviewState.APPROVED.value
            if approved
            else EvidenceReviewState.PENDING.value
        ),
        reviewer_id=REVIEWER_ID if approved else None,
        reviewed_at=datetime(2026, 7, 20, 9, 0) if approved else None,
        content_hash=content_hash,
        current_identity_key=f"{case_id}|{lineage_key}",
    )


def _seed_typed_manifest(
    db: Session,
    *,
    case_id: str,
    package_id: str,
    role: str,
    ordinal: int,
) -> None:
    document = Document(
        id=str(uuid4()),
        case_id=case_id,
        direction="OUT",
        title=f"{role}-{ordinal}",
    )
    db.add(document)
    db.flush()
    content_hash = _hash(f"{role}-{ordinal}")
    attachment = _attachment(
        document_id=document.id,
        name=f"{role.lower()}-{ordinal}.dat",
        content_hash=content_hash,
    )
    db.add(attachment)
    db.flush()
    version = _version(
        case_id=case_id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=f"oa-structured:{attachment.id}",
        role=EvidenceRole.OA_STRUCTURED_ATTACHMENT,
        content_hash=content_hash,
        approved=True,
    )
    db.add(version)
    db.flush()
    db.add(
        OfficialWorkPackageManifest(
            id=str(uuid4()),
            package_id=package_id,
            attachment_id=attachment.id,
            evidence_version_id=version.id,
            official_file_role=role,
            content_hash=content_hash,
            present=True,
        )
    )


def _seed_fixture(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    package_count: int = 1,
    source_version_count: int = 1,
    typed_mode: str = "valid",
) -> _Fixture:
    storage_dir = tmp_path / "storage"
    source_template_path = tmp_path / "templates" / "oa-out.docx"
    source_template_path.parent.mkdir(parents=True)
    source_template_path.write_bytes(b"oa-out-template")
    monkeypatch.setattr(documents_service, "_backend_storage_dir", lambda: storage_dir)
    monkeypatch.setattr(
        TemplateRenderer,
        "render_template_docx_bytes",
        lambda self, *, template_path, context: RENDERED_CONTENT,
    )

    with session_factory() as db:
        oa_in = db.scalar(select(DocTemplate).where(DocTemplate.code == "OA_IN"))
        oa_out = db.scalar(select(DocTemplate).where(DocTemplate.code == "OA_OUT"))
        assert oa_in is not None
        assert oa_out is not None
        db.add(
            Template(
                id=str(uuid4()),
                name="OA_OUT",
                group="DOC_TEMPLATE",
                language="zh-CN",
                file_path=str(source_template_path),
                enabled=True,
            )
        )
        case = Case(
            id=str(uuid4()),
            case_no=f"OA-ATOMIC-{uuid4().hex}",
            status="OA1",
            fee_reduction="0",
        )
        source = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=oa_in.id,
            doc_type="OFFICIAL_NOTICE",
            direction="IN",
            doc_date=date(2026, 1, 15),
            title="审查意见通知书",
            need_reply=True,
        )
        db.add_all([case, source])
        db.flush()
        source_attachment = _attachment(
            document_id=source.id,
            name="oa-notice.pdf",
            content_hash=_hash("source"),
        )
        db.add(source_attachment)
        db.flush()
        for ordinal in range(source_version_count):
            db.add(
                _version(
                    case_id=case.id,
                    document_id=source.id,
                    attachment_id=source_attachment.id,
                    lineage_key=f"oa-notice:{source.id}:{ordinal}",
                    role=EvidenceRole.RAW_ATTACHMENT,
                    content_hash=source_attachment.content_hash,
                    approved=True,
                )
            )
        packages = [
            OfficialWorkPackage(
                id=str(uuid4()),
                case_id=case.id,
                package_kind="OA_REPLY",
                status="PREPARING",
                source_document_id=source.id,
                resolve_key=(
                    f"OA_REPLY:{source.id}"
                    if ordinal == 0
                    else f"OA_REPLY:{source.id}:conflict:{ordinal}"
                ),
            )
            for ordinal in range(package_count)
        ]
        db.add_all(packages)
        db.flush()
        if packages and typed_mode != "zero":
            _seed_typed_manifest(
                db,
                case_id=case.id,
                package_id=packages[0].id,
                role="OA_STATEMENT_WORD",
                ordinal=1,
            )
            _seed_typed_manifest(
                db,
                case_id=case.id,
                package_id=packages[0].id,
                role="OA_MODIFIED_CLAIMS",
                ordinal=1,
            )
            if typed_mode == "multiple":
                _seed_typed_manifest(
                    db,
                    case_id=case.id,
                    package_id=packages[0].id,
                    role="OA_STATEMENT_WORD",
                    ordinal=2,
                )
        task = Task(
            id=str(uuid4()),
            case_id=case.id,
            document_id=source.id,
            title="OA答复",
            status="OPEN",
        )
        db.add(task)
        db.commit()
        return _Fixture(
            case_id=case.id,
            source_document_id=source.id,
            package_ids=tuple(package.id for package in packages),
            task_id=task.id,
            oa_out_template_id=oa_out.id,
            storage_dir=storage_dir,
        )


def _payload(
    fixture: _Fixture,
    *,
    reply_attachment_count: int = 1,
) -> DocumentWizardBatchCreateIn:
    return DocumentWizardBatchCreateIn.model_validate(
        {
            "defaults": {
                "doc_template_id": fixture.oa_out_template_id,
                "direction": "OUT",
                "doc_date": "2026-03-01",
                "reply_to_id": fixture.source_document_id,
            },
            "rows": [{"case_id": fixture.case_id, "title": "审查意见答复"}],
            "attachment_rows": [
                {
                    "row_index": 1,
                    "case_id": fixture.case_id,
                    "template_code": "OA_OUT",
                    "output_name": f"答复文件-{ordinal}",
                    "output_file_name": f"答复文件-{ordinal}.docx",
                    "output_format": "DOCX",
                    "candidate_source_kind": "DOC_TEMPLATE",
                }
                for ordinal in range(reply_attachment_count)
            ],
        }
    )


def _assert_failed_unit_is_absent(
    session_factory: sessionmaker[Session],
    fixture: _Fixture,
) -> None:
    with session_factory() as db:
        replies = db.scalars(
            select(Document).where(
                Document.case_id == fixture.case_id,
                Document.reply_to_id == fixture.source_document_id,
            )
        ).all()
        assert replies == []
        for package_id in fixture.package_ids:
            assert db.get(OfficialWorkPackage, package_id).reply_document_id is None
        assert (
            db.scalar(
                select(func.count())
                .select_from(DocumentEvidenceDerivation)
                .where(
                    DocumentEvidenceDerivation.derivation_type
                    == EvidenceDerivationType.OA_REPLY_PREPARATION.value
                )
            )
            == 0
        )
        task = db.get(Task, fixture.task_id)
        assert task is not None
        assert (task.status, task.done_at) == ("OPEN", None)
    assert not fixture.storage_dir.exists() or not any(
        path.is_file() for path in fixture.storage_dir.rglob("*")
    )


def test_real_oa_out_entrypoint_prepares_unique_package_and_keeps_task_open(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)

    with session_factory() as db:
        created = documents_service.create_document_wizard_batch(
            db,
            _payload(fixture),
            actor_id=ACTOR_ID,
        )
        reply_id = created[0][1].id

    with session_factory() as db:
        package = db.get(OfficialWorkPackage, fixture.package_ids[0])
        task = db.get(Task, fixture.task_id)
        reply = db.get(Document, reply_id)
        reply_attachments = db.scalars(
            select(DocAttachment).where(DocAttachment.document_id == reply_id)
        ).all()
        reply_versions = db.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.case_id == fixture.case_id,
                DocumentEvidenceVersion.lineage_key
                == f"oa-reply:{fixture.source_document_id}",
            )
        ).all()
        derivations = db.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.derivation_type
                == EvidenceDerivationType.OA_REPLY_PREPARATION.value
            )
        ).all()
        assert package is not None
        assert task is not None
        assert reply is not None
        assert package.reply_document_id == reply.id
        assert reply.reply_to_id == fixture.source_document_id
        assert len(reply_attachments) == 1
        assert len(reply_versions) == 1
        assert len(derivations) == 1
        assert (
            reply_versions[0].document_id,
            reply_versions[0].attachment_id,
            reply_versions[0].state,
            reply_versions[0].review_state,
            reply_versions[0].creator_id,
        ) == (
            reply.id,
            reply_attachments[0].id,
            EvidenceVersionState.DRAFT.value,
            EvidenceReviewState.PENDING.value,
            ACTOR_ID,
        )
        assert (task.status, task.done_at) == ("OPEN", None)
        stored_path = fixture.storage_dir / reply_attachments[0].file_path
        assert stored_path.read_bytes() == RENDERED_CONTENT


@pytest.mark.parametrize(
    ("seed_overrides", "reply_attachment_count"),
    [
        ({"package_count": 0}, 1),
        ({"package_count": 2}, 1),
        ({"source_version_count": 0}, 1),
        ({"source_version_count": 2}, 1),
        ({}, 0),
        ({}, 2),
        ({"typed_mode": "zero"}, 1),
        ({"typed_mode": "multiple"}, 1),
    ],
    ids=[
        "zero-package",
        "multiple-package",
        "zero-source-evidence",
        "multiple-source-evidence",
        "zero-reply-attachment",
        "multiple-reply-attachment",
        "zero-typed-manifest",
        "multiple-typed-manifest",
    ],
)
def test_real_entrypoint_fails_closed_for_non_unique_atomic_identity(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    seed_overrides: dict[str, object],
    reply_attachment_count: int,
) -> None:
    fixture = _seed_fixture(
        session_factory,
        monkeypatch,
        tmp_path,
        **seed_overrides,
    )

    with session_factory() as db:
        with pytest.raises(BusinessError) as raised:
            documents_service.create_document_wizard_batch(
                db,
                _payload(fixture, reply_attachment_count=reply_attachment_count),
                actor_id=ACTOR_ID,
            )

    assert (raised.value.code, raised.value.status_code) == (
        "OA_REPLY_IDENTITY_CONFLICT",
        409,
    )
    _assert_failed_unit_is_absent(session_factory, fixture)


def test_outer_commit_failure_rolls_back_real_seam_and_compensates_generated_file(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fixture = _seed_fixture(session_factory, monkeypatch, tmp_path)

    with session_factory() as db:
        real_rollback = db.rollback
        rollback = Mock(side_effect=real_rollback)
        monkeypatch.setattr(db, "rollback", rollback)
        monkeypatch.setattr(
            db,
            "commit",
            Mock(side_effect=RuntimeError("outer commit failed")),
        )
        with pytest.raises(RuntimeError, match="outer commit failed"):
            documents_service.create_document_wizard_batch(
                db,
                _payload(fixture),
                actor_id=ACTOR_ID,
            )
        assert rollback.call_count == 1

    _assert_failed_unit_is_absent(session_factory, fixture)
