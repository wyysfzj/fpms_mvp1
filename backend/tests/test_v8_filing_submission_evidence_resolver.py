from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime, timezone
from typing import get_type_hints

import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_contracts import EvidenceRole
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.filing_evidence_resolver import (
    FilingFinalEvidenceResolution,
    resolve_filing_final_evidence,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

CASE_ID = "00000000-0000-0000-0000-000000000001"
VERSION_ID = "00000000-0000-0000-0000-000000000002"
PACKAGE_ID = "00000000-0000-0000-0000-000000000003"
MANIFEST_ID = "00000000-0000-0000-0000-000000000004"
ACTIVITY_ID = "00000000-0000-0000-0000-000000000005"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000100"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000101"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
ACTOR_ID = "00000000-0000-0000-0000-000000000700"
LINEAGE_KEY = "filing-main"
CONTENT_HASH = f"sha256:{'a' * 64}"
REVIEWED_AT = datetime(2026, 7, 15, 9)
SUBMITTED_AT = datetime(2026, 7, 15, 10, 30)
ELIGIBLE_ROLES = (
    "FILING_FULL_WORD",
    "TRACKED_REVISED_WORD",
    "FILING_COMPONENT",
    "EXTERNAL_XML_PACKAGE",
    "OFFICIAL_SUBMISSION_LIST",
    "OFFICIAL_FINAL_PDF",
    "SUBMITTED_XML",
    "OFFICIAL_RECEIPT",
    "CLIENT_LETTER_WORD",
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _assert_error(
    code: str,
    status: int,
    callable_: object,
) -> BusinessError:
    with pytest.raises(BusinessError) as exc_info:
        callable_()  # type: ignore[operator]
    assert (exc_info.value.code, exc_info.value.status_code) == (code, status)
    return exc_info.value


def _seed_base(
    transaction: Session,
    *,
    final_submitted_at: datetime | None = None,
    role: str = EvidenceRole.SUBMITTED_XML.value,
) -> None:
    transaction.add(Case(id=CASE_ID, case_no="CASE-FILING-RESOLVER", status="ACCEPTED"))
    transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=ATTACHMENT_ID,
            document_id=DOCUMENT_ID,
            file_name="filing-final.xml",
            file_path="/evidence/filing-final.xml",
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=VERSION_ID,
            case_id=CASE_ID,
            document_id=DOCUMENT_ID,
            attachment_id=ATTACHMENT_ID,
            lineage_key=LINEAGE_KEY,
            role=role,
            version_number=1,
            state="FINAL",
            creator_id=CREATOR_ID,
            review_state="APPROVED",
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            final_submitted_at=final_submitted_at,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|{LINEAGE_KEY}",
        )
    )
    transaction.add(
        OfficialWorkPackage(
            id=PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="FILING_PREP",
        )
    )
    transaction.flush()
    transaction.add(
        OfficialWorkPackageManifest(
            id=MANIFEST_ID,
            package_id=PACKAGE_ID,
            attachment_id=ATTACHMENT_ID,
            evidence_version_id=VERSION_ID,
            content_hash=CONTENT_HASH,
            present=True,
        )
    )
    transaction.commit()


def _activity_payload() -> dict[str, str]:
    return {
        "evidence_version_id": VERSION_ID,
        "lineage_key": LINEAGE_KEY,
        "role": EvidenceRole.SUBMITTED_XML.value,
        "submitted_at": SUBMITTED_AT.isoformat(),
    }


def _seed_activity(
    transaction: Session,
    *,
    activity_id: str = ACTIVITY_ID,
    sequence: int = 1,
    idempotency_key: str = "document-external-submission:submission-1",
    with_link: bool = True,
) -> None:
    transaction.add(
        CaseActivityEvent(
            id=activity_id,
            case_id=CASE_ID,
            sequence=sequence,
            lane="DOCUMENT",
            activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            occurred_at=SUBMITTED_AT,
            effective_at=SUBMITTED_AT,
            confirmation_status="CONFIRMED",
            actor_id=ACTOR_ID,
            reviewer_id=REVIEWER_ID,
            idempotency_key=idempotency_key,
            payload_json=json.dumps(_activity_payload(), separators=(",", ":")),
        )
    )
    transaction.flush()
    if with_link:
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(1000 + sequence),
                case_id=CASE_ID,
                activity_id=activity_id,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=VERSION_ID,
                content_hash=CONTENT_HASH,
                captured_at=SUBMITTED_AT,
            )
        )
    transaction.commit()


def _expected_activity_hash() -> str:
    snapshot = {
        "activity_id": ACTIVITY_ID,
        "activity_type": "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
        "actor_id": ACTOR_ID,
        "case_id": CASE_ID,
        "confirmation_status": "CONFIRMED",
        "effective_at": SUBMITTED_AT.isoformat(),
        "evidence": [
            {
                "captured_at": SUBMITTED_AT.isoformat(),
                "content_hash": CONTENT_HASH,
                "evidence_kind": "DOCUMENT_EVIDENCE_VERSION",
                "object_id": VERSION_ID,
                "object_type": "DocumentEvidenceVersion",
            }
        ],
        "idempotency_key": "document-external-submission:submission-1",
        "lane": "DOCUMENT",
        "occurred_at": SUBMITTED_AT.isoformat(),
        "payload": _activity_payload(),
        "reviewer_id": REVIEWER_ID,
    }
    exact_bytes = json.dumps(
        snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()
    return f"sha256:{hashlib.sha256(exact_bytes).hexdigest()}"


def test_public_contract_is_exact_frozen_slotted_and_keyword_only() -> None:
    assert is_dataclass(FilingFinalEvidenceResolution)
    assert FilingFinalEvidenceResolution.__dataclass_params__.frozen is True
    assert "__slots__" in FilingFinalEvidenceResolution.__dict__
    hints = get_type_hints(FilingFinalEvidenceResolution)
    assert tuple(
        (field.name, hints[field.name]) for field in fields(FilingFinalEvidenceResolution)
    ) == (
        ("package_id", str),
        ("case_id", str),
        ("evidence_version_id", str),
        ("content_hash", str),
        ("reviewer_id", str),
        ("reviewed_at", datetime),
        ("final_submitted_at", datetime | None),
        ("submission_activity_id", str | None),
        ("submission_activity_hash", str | None),
    )
    assert all(field.kw_only for field in fields(FilingFinalEvidenceResolution))
    signature = inspect.signature(resolve_filing_final_evidence)
    assert tuple(signature.parameters) == ("package_id", "transaction")
    assert get_type_hints(resolve_filing_final_evidence)["return"] is (
        FilingFinalEvidenceResolution
    )


def test_resolves_exact_unfinalized_evidence_without_any_write(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        before_identity_keys = tuple(transaction.identity_map.keys())
        statements: list[str] = []
        bind = transaction.get_bind()

        def capture_statement(
            _conn: object,
            _cursor: object,
            statement: str,
            _parameters: object,
            _context: object,
            _executemany: object,
        ) -> None:
            statements.append(statement)

        event.listen(bind, "before_cursor_execute", capture_statement)
        try:
            result = resolve_filing_final_evidence(PACKAGE_ID, transaction)
        finally:
            event.remove(bind, "before_cursor_execute", capture_statement)

        assert result == FilingFinalEvidenceResolution(
            package_id=PACKAGE_ID,
            case_id=CASE_ID,
            evidence_version_id=VERSION_ID,
            content_hash=CONTENT_HASH,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            final_submitted_at=None,
            submission_activity_id=None,
            submission_activity_hash=None,
        )
        with pytest.raises(FrozenInstanceError):
            result.case_id = _id(99)  # type: ignore[misc]
        assert statements and all(
            statement.lstrip().upper().startswith("SELECT") for statement in statements
        )
        assert tuple(transaction.identity_map.keys()) == before_identity_keys
        assert not transaction.new and not transaction.dirty and not transaction.deleted


def test_resolves_finalized_evidence_and_exact_canonical_snapshot_hash(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, final_submitted_at=SUBMITTED_AT)
        _seed_activity(transaction)

        result = resolve_filing_final_evidence(PACKAGE_ID, transaction)

        assert result == FilingFinalEvidenceResolution(
            package_id=PACKAGE_ID,
            case_id=CASE_ID,
            evidence_version_id=VERSION_ID,
            content_hash=CONTENT_HASH,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            final_submitted_at=SUBMITTED_AT,
            submission_activity_id=ACTIVITY_ID,
            submission_activity_hash=_expected_activity_hash(),
        )
        assert not transaction.new and not transaction.dirty and not transaction.deleted


@pytest.mark.parametrize("role", ELIGIBLE_ROLES)
def test_accepts_each_exact_delta3_external_submission_role(
    session_factory: sessionmaker[Session], role: str
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, role=role)
        result = resolve_filing_final_evidence(PACKAGE_ID, transaction)
        assert result.evidence_version_id == VERSION_ID


@pytest.mark.parametrize("package_id", (None, 1, "", "   ", "x" * 37))
def test_invalid_package_id_is_exact_400(
    session_factory: sessionmaker[Session], package_id: object
) -> None:
    with session_factory() as transaction:
        _assert_error(
            "FILING_FINAL_EVIDENCE_INVALID",
            400,
            lambda: resolve_filing_final_evidence(package_id, transaction),  # type: ignore[arg-type]
        )


def test_invalid_transaction_boundary_is_exact_400() -> None:
    _assert_error(
        "FILING_FINAL_EVIDENCE_INVALID",
        400,
        lambda: resolve_filing_final_evidence(PACKAGE_ID, object()),  # type: ignore[arg-type]
    )


def test_missing_package_is_exact_404(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as transaction:
        _assert_error(
            "OFFICIAL_WORK_PACKAGE_NOT_FOUND",
            404,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


@pytest.mark.parametrize("condition", ("wrong_kind", "zero_candidate", "multiple_candidates"))
def test_package_and_manifest_selection_ambiguity_is_exact_409(
    session_factory: sessionmaker[Session], condition: str
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        package = transaction.get(OfficialWorkPackage, PACKAGE_ID)
        manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
        assert package is not None and manifest is not None
        if condition == "wrong_kind":
            package.package_kind = "OA_REPLY"
        elif condition == "zero_candidate":
            manifest.present = False
        else:
            transaction.add(
                OfficialWorkPackageManifest(
                    id=_id(6),
                    package_id=PACKAGE_ID,
                    attachment_id=ATTACHMENT_ID,
                    evidence_version_id=VERSION_ID,
                    content_hash=CONTENT_HASH,
                    present=True,
                )
            )
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_dangling_manifest_version_is_exact_404(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        transaction.add(Case(id=CASE_ID, case_no="CASE-DANGLING", status="ACCEPTED"))
        transaction.add(
            OfficialWorkPackage(
                id=PACKAGE_ID,
                case_id=CASE_ID,
                package_kind="FILING_PREP",
            )
        )
        transaction.commit()
        transaction.execute(text("PRAGMA defer_foreign_keys=ON"))
        transaction.add(
            OfficialWorkPackageManifest(
                id=MANIFEST_ID,
                package_id=PACKAGE_ID,
                evidence_version_id=VERSION_ID,
                content_hash=CONTENT_HASH,
                present=True,
            )
        )
        transaction.flush()

        _assert_error(
            "EVIDENCE_VERSION_NOT_FOUND",
            404,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )
        transaction.rollback()


@pytest.mark.parametrize(
    "mismatch",
    ("package_case", "document_case", "attachment_document", "manifest_attachment"),
)
def test_cross_case_and_persisted_link_mismatches_fail_closed(
    session_factory: sessionmaker[Session], mismatch: str
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        if mismatch in {"package_case", "document_case"}:
            transaction.add(Case(id=_id(20), case_no="CASE-OTHER", status="ACCEPTED"))
            transaction.flush()
        if mismatch == "package_case":
            package = transaction.get(OfficialWorkPackage, PACKAGE_ID)
            assert package is not None
            package.case_id = _id(20)
        elif mismatch == "document_case":
            document = transaction.get(Document, DOCUMENT_ID)
            assert document is not None
            document.case_id = _id(20)
        elif mismatch == "attachment_document":
            transaction.add(Document(id=_id(21), case_id=CASE_ID))
            transaction.flush()
            attachment = transaction.get(DocAttachment, ATTACHMENT_ID)
            assert attachment is not None
            attachment.document_id = _id(21)
        else:
            transaction.add(
                DocAttachment(
                    id=_id(22),
                    document_id=DOCUMENT_ID,
                    file_name="other.xml",
                    file_path="/evidence/other.xml",
                )
            )
            transaction.flush()
            manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
            assert manifest is not None
            manifest.attachment_id = _id(22)
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


@pytest.mark.parametrize(
    ("target", "field", "value"),
    (
        ("manifest", "content_hash", f"sha256:{'b' * 64}"),
        ("manifest", "content_hash", None),
        ("version", "content_hash", "sha256:not-a-digest"),
        ("version", "current_identity_key", None),
        ("version", "current_identity_key", f"{CASE_ID}|different-lineage"),
        ("version", "state", "DRAFT"),
        ("version", "review_state", "PENDING"),
        ("version", "creator_id", ""),
        ("version", "reviewer_id", ""),
        ("version", "reviewer_id", CREATOR_ID),
        ("version", "reviewed_at", None),
        ("version", "lineage_key", ""),
        ("version", "role", EvidenceRole.RAW_ATTACHMENT.value),
        ("version", "role", "NOT_A_ROLE"),
    ),
)
def test_hash_current_final_review_and_role_contradictions_fail_closed(
    session_factory: sessionmaker[Session], target: str, field: str, value: object
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        stored = transaction.get(
            OfficialWorkPackageManifest if target == "manifest" else DocumentEvidenceVersion,
            MANIFEST_ID if target == "manifest" else VERSION_ID,
        )
        assert stored is not None
        setattr(stored, field, value)
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_full_length_uppercase_hash_fails_when_manifest_hash_matches(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        uppercase_hash = f"sha256:{'A' * 64}"
        version = transaction.get(DocumentEvidenceVersion, VERSION_ID)
        manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
        assert version is not None and manifest is not None
        version.content_hash = uppercase_hash
        manifest.content_hash = uppercase_hash
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


@pytest.mark.parametrize("field", ("reviewed_at", "final_submitted_at"))
def test_timezone_aware_stored_evidence_times_fail_closed(
    session_factory: sessionmaker[Session], field: str
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        aware_value = SUBMITTED_AT.replace(tzinfo=timezone.utc).isoformat(sep=" ")
        if field == "reviewed_at":
            statement = text(
                "UPDATE t_document_evidence_version SET reviewed_at = :value WHERE id = :version_id"
            )
        else:
            statement = text(
                "UPDATE t_document_evidence_version "
                "SET final_submitted_at = :value WHERE id = :version_id"
            )
        transaction.execute(statement, {"value": aware_value, "version_id": VERSION_ID})
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_unfinalized_carrier_rejects_matching_activity(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        _seed_activity(transaction)
        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_finalized_carrier_rejects_absent_or_multiple_activity(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, final_submitted_at=SUBMITTED_AT)
        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )

        _seed_activity(transaction)
        _seed_activity(
            transaction,
            activity_id=_id(7),
            sequence=2,
            idempotency_key="document-external-submission:submission-2",
        )
        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


@pytest.mark.parametrize(
    ("target", "field", "value"),
    (
        ("activity", "lane", "CASE"),
        ("activity", "confirmation_status", "UNCONFIRMED"),
        ("activity", "actor_id", ""),
        ("activity", "reviewer_id", CREATOR_ID),
        ("activity", "effective_at", REVIEWED_AT),
        ("activity", "occurred_at", REVIEWED_AT),
        ("activity", "idempotency_key", "wrong-namespace"),
        ("activity", "payload_json", "not-json"),
        (
            "activity",
            "payload_json",
            json.dumps({**_activity_payload(), "extra": "forbidden"}),
        ),
        (
            "activity",
            "payload_json",
            json.dumps(
                {
                    **_activity_payload(),
                    "role": EvidenceRole.OFFICIAL_RECEIPT.value,
                }
            ),
        ),
        ("link", "evidence_kind", "DOCUMENT"),
        ("link", "object_type", "Document"),
        ("link", "object_id", _id(88)),
        ("link", "content_hash", f"sha256:{'b' * 64}"),
        ("link", "captured_at", REVIEWED_AT),
    ),
)
def test_finalized_activity_and_evidence_link_mismatch_fail_closed(
    session_factory: sessionmaker[Session], target: str, field: str, value: object
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, final_submitted_at=SUBMITTED_AT)
        _seed_activity(transaction)
        stored = transaction.get(
            CaseActivityEvent if target == "activity" else CaseActivityEventEvidence,
            ACTIVITY_ID if target == "activity" else _id(1001),
        )
        assert stored is not None
        setattr(stored, field, value)
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_finalized_activity_requires_exactly_one_evidence_link(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, final_submitted_at=SUBMITTED_AT)
        _seed_activity(transaction, with_link=False)
        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )

        transaction.add(
            CaseActivityEventEvidence(
                id=_id(50),
                case_id=CASE_ID,
                activity_id=ACTIVITY_ID,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=VERSION_ID,
                content_hash=CONTENT_HASH,
                captured_at=SUBMITTED_AT,
            )
        )
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(51),
                case_id=CASE_ID,
                activity_id=ACTIVITY_ID,
                evidence_kind="DOCUMENT",
                object_type="Document",
                object_id=DOCUMENT_ID,
                content_hash=CONTENT_HASH,
                captured_at=SUBMITTED_AT,
            )
        )
        transaction.commit()
        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


def test_finalized_activity_rejects_cross_case_candidate(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction, final_submitted_at=SUBMITTED_AT)
        transaction.add(Case(id=_id(60), case_no="CASE-OTHER-ACTIVITY", status="ACCEPTED"))
        transaction.flush()
        transaction.add(
            CaseActivityEvent(
                id=ACTIVITY_ID,
                case_id=_id(60),
                sequence=1,
                lane="DOCUMENT",
                activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
                occurred_at=SUBMITTED_AT,
                effective_at=SUBMITTED_AT,
                confirmation_status="CONFIRMED",
                actor_id=ACTOR_ID,
                reviewer_id=REVIEWER_ID,
                idempotency_key="document-external-submission:submission-1",
                payload_json=json.dumps(_activity_payload()),
            )
        )
        transaction.flush()
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(61),
                case_id=_id(60),
                activity_id=ACTIVITY_ID,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=VERSION_ID,
                content_hash=CONTENT_HASH,
                captured_at=SUBMITTED_AT,
            )
        )
        transaction.commit()

        _assert_error(
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
            lambda: resolve_filing_final_evidence(PACKAGE_ID, transaction),
        )


@pytest.mark.parametrize(
    ("activity_id", "activity_hash"),
    (
        (ACTIVITY_ID, None),
        (None, f"sha256:{'b' * 64}"),
    ),
)
def test_resolution_dto_rejects_each_mixed_activity_pair(
    activity_id: str | None,
    activity_hash: str | None,
) -> None:
    _assert_error(
        "FILING_FINAL_EVIDENCE_CONFLICT",
        409,
        lambda: FilingFinalEvidenceResolution(
            package_id=PACKAGE_ID,
            case_id=CASE_ID,
            evidence_version_id=VERSION_ID,
            content_hash=CONTENT_HASH,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            final_submitted_at=SUBMITTED_AT,
            submission_activity_id=activity_id,
            submission_activity_hash=activity_hash,
        ),
    )


def test_activity_result_fields_are_never_mixed(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as transaction:
        _seed_base(transaction)
        unfinalized = resolve_filing_final_evidence(PACKAGE_ID, transaction)
        assert (unfinalized.submission_activity_id, unfinalized.submission_activity_hash) == (
            None,
            None,
        )

        version = transaction.get(DocumentEvidenceVersion, VERSION_ID)
        assert version is not None
        version.final_submitted_at = SUBMITTED_AT
        transaction.commit()
        _seed_activity(transaction)
        finalized = resolve_filing_final_evidence(PACKAGE_ID, transaction)
        assert finalized.submission_activity_id is not None
        assert finalized.submission_activity_hash is not None
        assert not transaction.new and not transaction.dirty and not transaction.deleted
