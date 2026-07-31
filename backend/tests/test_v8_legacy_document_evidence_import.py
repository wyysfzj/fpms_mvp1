from __future__ import annotations

import importlib
import inspect
from types import ModuleType

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceVersion,
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _api() -> ModuleType:
    try:
        return importlib.import_module("scripts.backfill_v8_document_evidence")
    except ModuleNotFoundError:
        pytest.fail("legacy document-evidence importer public seam is missing")


def _actor_id(transaction: Session) -> str:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    return actor_id


def _seed_attachment(
    transaction: Session,
    value: int,
    *,
    content_hash: str | None = None,
) -> tuple[Case, Document, DocAttachment]:
    case = Case(id=_id(value), case_no=f"LEGACY-DOC-{value}")
    document = Document(
        id=_id(100 + value),
        case_id=case.id,
        direction="IN",
        title=f"旧附件 {value}",
    )
    attachment = DocAttachment(
        id=_id(200 + value),
        document_id=document.id,
        file_name=f"legacy-{value}.pdf",
        file_path=f"legacy/legacy-{value}.pdf",
        content_hash=content_hash,
    )
    transaction.add_all((case, document, attachment))
    transaction.flush()
    return case, document, attachment


def _add_version(
    transaction: Session,
    *,
    case: Case,
    document: Document,
    attachment: DocAttachment,
    value: int,
    role: EvidenceRole,
    lineage_attachment_id: str | None = None,
) -> DocumentEvidenceVersion:
    lineage_key = f"attachment:{lineage_attachment_id or attachment.id}"
    version = DocumentEvidenceVersion(
        id=_id(300 + value),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role=role.value,
        version_number=1,
        state=EvidenceVersionState.DRAFT.value,
        creator_id=_actor_id(transaction),
        review_state=EvidenceReviewState.PENDING.value,
        content_hash=attachment.content_hash or f"sha256:{value:064x}",
        current_identity_key=f"{case.id}|{lineage_key}",
    )
    transaction.add(version)
    transaction.flush()
    return version


def test_public_seam_is_exact_keyword_only_and_synchronous() -> None:
    api = _api()
    signature = inspect.signature(api.import_legacy_document_evidence)

    assert tuple(signature.parameters) == (
        "transaction",
        "actor_id",
        "dry_run",
        "expected_plan_sha256",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert signature.parameters["expected_plan_sha256"].default is None


def test_dry_run_classifies_deterministically_without_writes(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        eligible = _seed_attachment(
            transaction,
            1,
            content_hash=f"sha256:{'1' * 64}",
        )
        unchanged = _seed_attachment(
            transaction,
            2,
            content_hash=f"sha256:{'2' * 64}",
        )
        role_conflict = _seed_attachment(
            transaction,
            3,
            content_hash=f"sha256:{'3' * 64}",
        )
        current_conflict = _seed_attachment(
            transaction,
            4,
            content_hash=f"sha256:{'4' * 64}",
        )
        invalid = _seed_attachment(transaction, 5)
        _add_version(
            transaction,
            case=unchanged[0],
            document=unchanged[1],
            attachment=unchanged[2],
            value=2,
            role=EvidenceRole.RAW_ATTACHMENT,
        )
        _add_version(
            transaction,
            case=role_conflict[0],
            document=role_conflict[1],
            attachment=role_conflict[2],
            value=3,
            role=EvidenceRole.FILING_FULL_WORD,
        )
        conflicting_attachment = DocAttachment(
            id=_id(904),
            document_id=current_conflict[1].id,
            file_name="other.pdf",
            file_path="legacy/other.pdf",
            content_hash=None,
        )
        transaction.add(conflicting_attachment)
        transaction.flush()
        _add_version(
            transaction,
            case=current_conflict[0],
            document=current_conflict[1],
            attachment=conflicting_attachment,
            value=4,
            role=EvidenceRole.RAW_ATTACHMENT,
            lineage_attachment_id=current_conflict[2].id,
        )
        transaction.commit()

        before = list(transaction.scalars(select(DocumentEvidenceVersion)))
        first = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=_actor_id(transaction),
            dry_run=True,
        )
        second = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=_actor_id(transaction),
            dry_run=True,
        )

        assert (
            first.scanned,
            first.imported,
            first.unchanged,
            first.invalid,
            first.role_conflicts,
            first.current_conflicts,
            first.planned_writes,
        ) == (6, 1, 1, 2, 1, 1, 1)
        assert [row.classification for row in first.rows] == [
            "IMPORT",
            "UNCHANGED",
            "ROLE_CONFLICT",
            "CURRENT_CONFLICT",
            "INVALID",
            "INVALID",
        ]
        assert first == second
        assert list(transaction.scalars(select(DocumentEvidenceVersion))) == before
        assert eligible[2].id == first.rows[0].attachment_id
        assert invalid[2].id == first.rows[4].attachment_id


def test_apply_creates_one_unverified_raw_current_version_without_commit(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    with session_factory() as transaction:
        case, document, attachment = _seed_attachment(
            transaction,
            10,
            content_hash=f"sha256:{'a' * 64}",
        )
        transaction.commit()
        actor_id = _actor_id(transaction)
        plan = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=True,
        )

        rollback = transaction.rollback
        monkeypatch.setattr(transaction, "commit", lambda: pytest.fail("commit called"))
        monkeypatch.setattr(transaction, "rollback", lambda: pytest.fail("rollback called"))
        result = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )

        versions = list(transaction.scalars(select(DocumentEvidenceVersion)))
        assert (result.imported, result.planned_writes) == (1, 1)
        assert len(versions) == 1
        version = versions[0]
        assert {
            "case_id": version.case_id,
            "document_id": version.document_id,
            "attachment_id": version.attachment_id,
            "lineage_key": version.lineage_key,
            "role": version.role,
            "version_number": version.version_number,
            "state": version.state,
            "creator_id": version.creator_id,
            "review_state": version.review_state,
            "current_identity_key": version.current_identity_key,
        } == {
            "case_id": case.id,
            "document_id": document.id,
            "attachment_id": attachment.id,
            "lineage_key": f"attachment:{attachment.id}",
            "role": EvidenceRole.RAW_ATTACHMENT.value,
            "version_number": 1,
            "state": EvidenceVersionState.DRAFT.value,
            "creator_id": actor_id,
            "review_state": EvidenceReviewState.PENDING.value,
            "current_identity_key": f"{case.id}|attachment:{attachment.id}",
        }
        activity = transaction.scalar(select(CaseActivityEvent))
        assert activity is not None
        assert activity.activity_type == "DOCUMENT_EVIDENCE_VERSION_REGISTERED"

        monkeypatch.setattr(transaction, "rollback", rollback)
        transaction.rollback()

    with session_factory() as verification:
        assert verification.scalars(select(DocumentEvidenceVersion)).all() == []
        assert verification.scalars(select(CaseActivityEvent)).all() == []


def test_apply_imports_unambiguous_rows_and_leaves_conflicts_unresolved(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        eligible = _seed_attachment(
            transaction,
            20,
            content_hash=f"sha256:{'b' * 64}",
        )
        conflict = _seed_attachment(
            transaction,
            21,
            content_hash=f"sha256:{'c' * 64}",
        )
        existing = _add_version(
            transaction,
            case=conflict[0],
            document=conflict[1],
            attachment=conflict[2],
            value=21,
            role=EvidenceRole.OFFICIAL_RECEIPT,
        )
        transaction.commit()
        actor_id = _actor_id(transaction)
        plan = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=True,
        )

        result = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )

        assert (result.imported, result.role_conflicts) == (1, 1)
        versions = list(
            transaction.scalars(
                select(DocumentEvidenceVersion).order_by(DocumentEvidenceVersion.attachment_id)
            )
        )
        assert {version.id for version in versions if version.attachment_id == conflict[2].id} == {
            existing.id
        }
        assert [
            version.role for version in versions if version.attachment_id == eligible[2].id
        ] == [EvidenceRole.RAW_ATTACHMENT.value]


def test_apply_rejects_plan_drift_before_any_write(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        _seed_attachment(
            transaction,
            30,
            content_hash=f"sha256:{'d' * 64}",
        )
        transaction.commit()
        actor_id = _actor_id(transaction)
        plan = api.import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=True,
        )
        _seed_attachment(
            transaction,
            31,
            content_hash=f"sha256:{'e' * 64}",
        )

        with pytest.raises(BusinessError) as caught:
            api.import_legacy_document_evidence(
                transaction=transaction,
                actor_id=actor_id,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            )

        assert caught.value.status_code == 409
        assert caught.value.code == "LEGACY_DOCUMENT_EVIDENCE_PLAN_MISMATCH"
        assert transaction.scalars(select(DocumentEvidenceVersion)).all() == []
