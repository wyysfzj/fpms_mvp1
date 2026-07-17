from __future__ import annotations

import hashlib
import json
from dataclasses import fields, replace
from datetime import datetime, timezone
from inspect import signature

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session, sessionmaker

import app.modules.documents.oa_attachment_promotion_service as promotion_service
from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_contracts import EvidenceVersionState
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.documents.oa_attachment_promotion_service import (
    PromoteOaStructuredAttachmentCommand,
    PromoteOaStructuredAttachmentResult,
    promote_oa_structured_attachment,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

CASE_ID = "00000000-0000-0000-0000-000000000001"
PACKAGE_ID = "00000000-0000-0000-0000-000000000002"
MANIFEST_ID = "00000000-0000-0000-0000-000000000003"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000004"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000005"
RAW_VERSION_ID = "00000000-0000-0000-0000-000000000006"
ACTOR_ID = "00000000-0000-0000-0000-000000000007"
CREATOR_ID = "00000000-0000-0000-0000-000000000008"
CONTENT_HASH = f"sha256:{'a' * 64}"
PROMOTED_AT = datetime(2026, 7, 16, 9, 30)
MANIFEST_ROLE = "OA_STATEMENT_WORD"
IDEMPOTENCY_KEY = "oa-promotion-1"
PREEXISTING_CHILD_ID = "00000000-0000-0000-0000-000000000009"
PREEXISTING_DERIVATION_ID = "00000000-0000-0000-0000-000000000010"


def _canonical_json(value: dict[str, str]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _seed_eligible_raw_manifest(
    transaction: Session,
    *,
    manifest_role: str = MANIFEST_ROLE,
) -> None:
    transaction.add(Case(id=CASE_ID, case_no="CASE-OA-PROMOTION", status="OA1"))
    transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=ATTACHMENT_ID,
            document_id=DOCUMENT_ID,
            file_name="filename-must-not-classify.bin",
            file_path="/evidence/raw-oa.bin",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=RAW_VERSION_ID,
            case_id=CASE_ID,
            document_id=DOCUMENT_ID,
            attachment_id=ATTACHMENT_ID,
            lineage_key="oa-raw",
            role="RAW_ATTACHMENT",
            version_number=1,
            state="DRAFT",
            creator_id=CREATOR_ID,
            review_state="PENDING",
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|oa-raw",
        )
    )
    transaction.add(
        OfficialWorkPackage(
            id=PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="OA_REPLY",
        )
    )
    transaction.flush()
    transaction.add(
        OfficialWorkPackageManifest(
            id=MANIFEST_ID,
            package_id=PACKAGE_ID,
            attachment_id=ATTACHMENT_ID,
            evidence_version_id=RAW_VERSION_ID,
            official_file_role=manifest_role,
            source_role_alias="customer-reviewed-role",
            external_upload_position="OA_UPLOAD_1",
            content_hash=CONTENT_HASH,
            required=True,
            present=True,
            sort_order=1,
            note="preserve",
        )
    )
    transaction.commit()


def _command(
    *,
    target_state: EvidenceVersionState = EvidenceVersionState.FINAL,
) -> PromoteOaStructuredAttachmentCommand:
    return PromoteOaStructuredAttachmentCommand(
        case_id=CASE_ID,
        package_id=PACKAGE_ID,
        manifest_id=MANIFEST_ID,
        raw_evidence_version_id=RAW_VERSION_ID,
        target_state=target_state,
        actor_id=ACTOR_ID,
        promoted_at=PROMOTED_AT,
        idempotency_key=IDEMPOTENCY_KEY,
    )


def _promotion_row_counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
        transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)),
        transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
        transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
    )


def test_public_contract_has_exact_command_and_service_shape() -> None:
    assert [field.name for field in fields(PromoteOaStructuredAttachmentCommand)] == [
        "case_id",
        "package_id",
        "manifest_id",
        "raw_evidence_version_id",
        "target_state",
        "actor_id",
        "promoted_at",
        "idempotency_key",
    ]
    assert PromoteOaStructuredAttachmentCommand.__annotations__ == {
        "case_id": "str",
        "package_id": "str",
        "manifest_id": "str",
        "raw_evidence_version_id": "str",
        "target_state": "EvidenceVersionState",
        "actor_id": "str",
        "promoted_at": "datetime",
        "idempotency_key": "str",
    }
    service_signature = signature(promote_oa_structured_attachment)
    assert list(service_signature.parameters) == ["command", "transaction"]
    assert service_signature.parameters["command"].annotation == (
        "PromoteOaStructuredAttachmentCommand"
    )
    assert service_signature.parameters["transaction"].annotation == "Session"
    assert service_signature.return_annotation == ("PromoteOaStructuredAttachmentResult")
    assert PromoteOaStructuredAttachmentResult is not None


def test_promotes_one_eligible_raw_manifest_into_exact_typed_carriers(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        manifest_before = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
        preserved_manifest_fields = (
            manifest_before.official_file_role,
            manifest_before.source_role_alias,
            manifest_before.external_upload_position,
            manifest_before.required,
            manifest_before.present,
            manifest_before.sort_order,
            manifest_before.note,
        )

        result = promote_oa_structured_attachment(_command(), transaction)

        child = transaction.get(
            DocumentEvidenceVersion,
            result.typed_evidence_version_id,
        )
        assert child is not None
        assert (
            child.case_id,
            child.document_id,
            child.attachment_id,
            child.lineage_key,
            child.role,
            child.state,
            child.creator_id,
            child.review_state,
            child.reviewer_id,
            child.reviewed_at,
            child.final_submitted_at,
            child.content_hash,
        ) == (
            CASE_ID,
            DOCUMENT_ID,
            ATTACHMENT_ID,
            f"oa-raw|OA|{MANIFEST_ROLE}",
            "OA_STRUCTURED_ATTACHMENT",
            "FINAL",
            ACTOR_ID,
            "PENDING",
            None,
            None,
            None,
            CONTENT_HASH,
        )

        identity_source = {
            "actor_id": ACTOR_ID,
            "case_id": CASE_ID,
            "command_idempotency_key": IDEMPOTENCY_KEY,
            "manifest_id": MANIFEST_ID,
            "manifest_role": MANIFEST_ROLE,
            "package_id": PACKAGE_ID,
            "promoted_at": PROMOTED_AT.isoformat(),
            "raw_content_hash": CONTENT_HASH,
            "raw_evidence_version_id": RAW_VERSION_ID,
            "target_state": "FINAL",
        }
        expected_identity = (
            "sha256:" + hashlib.sha256(_canonical_json(identity_source).encode("utf-8")).hexdigest()
        )
        expected_carrier = {
            **identity_source,
            "promotion_identity_key": expected_identity,
            "schema": "FPMS_OA_STRUCTURED_ATTACHMENT_PROMOTION_V1",
            "typed_content_hash": CONTENT_HASH,
            "typed_evidence_version_id": child.id,
        }
        expected_carrier_json = _canonical_json(expected_carrier)
        assert result.promotion_identity_key == expected_identity
        assert result.reused is False

        derivations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.case_id == CASE_ID,
                DocumentEvidenceDerivation.parent_evidence_version_id == RAW_VERSION_ID,
                DocumentEvidenceDerivation.child_evidence_version_id == child.id,
                DocumentEvidenceDerivation.derivation_type == "OFFICIAL_RECOGNITION",
            )
        ).all()
        assert len(derivations) == 1
        assert derivations[0].id == result.evidence_derivation_id
        assert derivations[0].source_snapshot == expected_carrier_json

        activity = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.id == result.activity_id,
                CaseActivityEvent.case_id == CASE_ID,
                CaseActivityEvent.idempotency_key == f"oa-structured-promotion:{IDEMPOTENCY_KEY}",
            )
        )
        assert activity is not None
        assert (
            activity.lane,
            activity.activity_type,
            activity.confirmation_status,
            activity.actor_id,
            activity.reviewer_id,
            activity.effective_at,
            activity.occurred_at,
            activity.payload_json,
        ) == (
            "DOCUMENT",
            "OA_STRUCTURED_ATTACHMENT_PROMOTED",
            "CONFIRMED",
            ACTOR_ID,
            None,
            PROMOTED_AT,
            PROMOTED_AT,
            expected_carrier_json,
        )
        references = transaction.scalars(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == activity.id)
            .order_by(CaseActivityEventEvidence.evidence_kind)
        ).all()
        assert [
            (
                reference.evidence_kind,
                reference.object_type,
                reference.object_id,
                reference.content_hash,
                reference.captured_at,
            )
            for reference in references
        ] == [
            (
                "OA_STRUCTURED_ATTACHMENT_VERSION",
                "DocumentEvidenceVersion",
                child.id,
                CONTENT_HASH,
                PROMOTED_AT,
            ),
            (
                "RAW_ATTACHMENT_VERSION",
                "DocumentEvidenceVersion",
                RAW_VERSION_ID,
                CONTENT_HASH,
                PROMOTED_AT,
            ),
        ]

        manifest_after = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
        assert (manifest_after.evidence_version_id, manifest_after.content_hash) == (
            child.id,
            CONTENT_HASH,
        )
        assert (
            manifest_after.official_file_role,
            manifest_after.source_role_alias,
            manifest_after.external_upload_position,
            manifest_after.required,
            manifest_after.present,
            manifest_after.sort_order,
            manifest_after.note,
        ) == preserved_manifest_fields


def test_exact_replay_reuses_complete_carrier_without_row_growth(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        first = promote_oa_structured_attachment(_command(), transaction)
        transaction.flush()
        counts_before = (
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
        )

        replay = promote_oa_structured_attachment(_command(), transaction)

        assert replay == PromoteOaStructuredAttachmentResult(
            typed_evidence_version_id=first.typed_evidence_version_id,
            evidence_derivation_id=first.evidence_derivation_id,
            activity_id=first.activity_id,
            promotion_identity_key=first.promotion_identity_key,
            reused=True,
        )
        assert (
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
        ) == counts_before


@pytest.mark.parametrize(
    "conflict",
    (
        "command_actor",
        "activity_payload",
        "child_creator",
        "derivation_snapshot",
        "manifest_pointer",
        "reference_hash",
    ),
)
def test_replay_conflicts_return_409_without_promotion_row_growth(
    session_factory: sessionmaker,
    conflict: str,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        first = promote_oa_structured_attachment(_command(), transaction)
        transaction.flush()
        replay_command = _command()
        if conflict == "command_actor":
            replay_command = replace(replay_command, actor_id=CREATOR_ID)
        elif conflict == "activity_payload":
            activity = transaction.get(CaseActivityEvent, first.activity_id)
            activity.payload_json = "{}"
        elif conflict == "child_creator":
            child = transaction.get(
                DocumentEvidenceVersion,
                first.typed_evidence_version_id,
            )
            child.creator_id = CREATOR_ID
        elif conflict == "derivation_snapshot":
            derivation = transaction.get(
                DocumentEvidenceDerivation,
                first.evidence_derivation_id,
            )
            derivation.source_snapshot = "{}"
        elif conflict == "manifest_pointer":
            manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
            manifest.evidence_version_id = RAW_VERSION_ID
        elif conflict == "reference_hash":
            reference = transaction.scalar(
                select(CaseActivityEventEvidence).where(
                    CaseActivityEventEvidence.activity_id == first.activity_id,
                    CaseActivityEventEvidence.evidence_kind == "RAW_ATTACHMENT_VERSION",
                )
            )
            reference.content_hash = f"sha256:{'b' * 64}"
        transaction.flush()
        counts_before = (
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
        )

        with pytest.raises(BusinessError) as exc_info:
            promote_oa_structured_attachment(replay_command, transaction)

        assert exc_info.value.status_code == 409
        assert (
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
            transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
        ) == counts_before


@pytest.mark.parametrize(
    ("conflict", "expected_status"),
    (
        ("invalid_target", 400),
        ("wrong_package_kind", 409),
        ("absent_manifest", 409),
        ("wrong_manifest_role", 409),
        ("wrong_parent_role", 409),
        ("wrong_parent_state", 409),
        ("noncurrent_parent", 409),
        ("manifest_hash", 409),
        ("attachment_hash", 409),
        ("malformed_stored_hash", 409),
        ("empty_parent_lineage", 409),
    ),
)
def test_fresh_conflicts_fail_closed_before_any_promotion_write(
    session_factory: sessionmaker,
    conflict: str,
    expected_status: int,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        command = _command()
        package = transaction.get(OfficialWorkPackage, PACKAGE_ID)
        manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)
        parent = transaction.get(DocumentEvidenceVersion, RAW_VERSION_ID)
        attachment = transaction.get(DocAttachment, ATTACHMENT_ID)
        if conflict == "invalid_target":
            command = replace(command, target_state="FINAL")  # type: ignore[arg-type]
        elif conflict == "wrong_package_kind":
            package.package_kind = "FILING_PREP"
        elif conflict == "absent_manifest":
            manifest.present = False
        elif conflict == "wrong_manifest_role":
            manifest.official_file_role = "OA_STATEMENT_WORD.pdf"
        elif conflict == "wrong_parent_role":
            parent.role = "GENERATED_ATTACHMENT"
        elif conflict == "wrong_parent_state":
            parent.state = "FINAL"
        elif conflict == "noncurrent_parent":
            parent.current_identity_key = None
        elif conflict == "manifest_hash":
            manifest.content_hash = f"sha256:{'b' * 64}"
        elif conflict == "attachment_hash":
            attachment.content_hash = f"sha256:{'b' * 64}"
        elif conflict == "malformed_stored_hash":
            parent.content_hash = "not-a-hash"
            manifest.content_hash = "not-a-hash"
            attachment.content_hash = "not-a-hash"
        elif conflict == "empty_parent_lineage":
            parent.lineage_key = ""
            parent.current_identity_key = f"{CASE_ID}|"
        transaction.flush()
        counts_before = _promotion_row_counts(transaction)
        manifest_before = (manifest.evidence_version_id, manifest.content_hash)

        with pytest.raises(BusinessError) as exc_info:
            promote_oa_structured_attachment(command, transaction)

        assert exc_info.value.status_code == expected_status
        assert _promotion_row_counts(transaction) == counts_before
        assert (manifest.evidence_version_id, manifest.content_hash) == manifest_before


def test_fresh_path_rejects_preexisting_derivation_before_any_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        transaction.add(
            DocumentEvidenceVersion(
                id=PREEXISTING_CHILD_ID,
                case_id=CASE_ID,
                document_id=DOCUMENT_ID,
                attachment_id=ATTACHMENT_ID,
                lineage_key=f"oa-raw|OA|{MANIFEST_ROLE}",
                role="OA_STRUCTURED_ATTACHMENT",
                version_number=1,
                state="FINAL",
                creator_id=ACTOR_ID,
                review_state="PENDING",
                reviewer_id=None,
                reviewed_at=None,
                final_submitted_at=None,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|oa-raw|OA|{MANIFEST_ROLE}",
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceDerivation(
                id=PREEXISTING_DERIVATION_ID,
                case_id=CASE_ID,
                parent_evidence_version_id=RAW_VERSION_ID,
                child_evidence_version_id=PREEXISTING_CHILD_ID,
                derivation_type="OFFICIAL_RECOGNITION",
                actor_id=ACTOR_ID,
                derived_at=PROMOTED_AT,
                source_snapshot="{}",
            )
        )
        transaction.commit()
        counts_before = _promotion_row_counts(transaction)
        manifest = transaction.get(OfficialWorkPackageManifest, MANIFEST_ID)

        with pytest.raises(BusinessError) as exc_info:
            promote_oa_structured_attachment(_command(), transaction)

        assert exc_info.value.status_code == 409
        assert _promotion_row_counts(transaction) == counts_before
        assert (manifest.evidence_version_id, manifest.content_hash) == (
            RAW_VERSION_ID,
            CONTENT_HASH,
        )


@pytest.mark.parametrize("difference", ("actor", "target_state", "promoted_at"))
def test_replay_lookup_precedes_fresh_validation_and_returns_409_for_identity_difference(
    session_factory: sessionmaker,
    difference: str,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        promote_oa_structured_attachment(_command(), transaction)
        transaction.flush()
        replay_command = _command()
        if difference == "actor":
            replay_command = replace(replay_command, actor_id="")
        elif difference == "target_state":
            replay_command = replace(  # type: ignore[arg-type]
                replay_command,
                target_state="FINAL",
            )
        else:
            replay_command = replace(
                replay_command,
                promoted_at=PROMOTED_AT.replace(tzinfo=timezone.utc),
            )
        counts_before = _promotion_row_counts(transaction)

        with pytest.raises(BusinessError) as exc_info:
            promote_oa_structured_attachment(replay_command, transaction)

        assert exc_info.value.status_code == 409
        assert _promotion_row_counts(transaction) == counts_before


@pytest.mark.parametrize(
    "manifest_role",
    (
        "OA_STATEMENT_WORD",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    ),
)
@pytest.mark.parametrize(
    "target_state",
    (EvidenceVersionState.DRAFT, EvidenceVersionState.FINAL),
)
def test_each_exact_manifest_role_promotes_to_each_permitted_target_state(
    session_factory: sessionmaker,
    manifest_role: str,
    target_state: EvidenceVersionState,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction, manifest_role=manifest_role)

        result = promote_oa_structured_attachment(
            _command(target_state=target_state),
            transaction,
        )

        child = transaction.get(
            DocumentEvidenceVersion,
            result.typed_evidence_version_id,
        )
        assert (
            child.lineage_key,
            child.role,
            child.state,
            child.review_state,
            child.content_hash,
        ) == (
            f"oa-raw|OA|{manifest_role}",
            "OA_STRUCTURED_ATTACHMENT",
            target_state.value,
            "PENDING",
            CONTENT_HASH,
        )


@pytest.mark.parametrize(
    "failure_boundary",
    ("version", "derivation", "activity", "manifest"),
)
def test_caller_rollback_removes_every_partial_write_after_injected_failure(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    failure_boundary: str,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        if failure_boundary == "version":
            original = promotion_service.register_evidence_version

            def fail_after_version(*args: object, **kwargs: object) -> object:
                original(*args, **kwargs)
                raise RuntimeError("injected version boundary failure")

            monkeypatch.setattr(
                promotion_service,
                "register_evidence_version",
                fail_after_version,
            )
        elif failure_boundary == "derivation":
            original = promotion_service.register_evidence_derivation

            def fail_after_derivation(*args: object, **kwargs: object) -> object:
                original(*args, **kwargs)
                raise RuntimeError("injected derivation boundary failure")

            monkeypatch.setattr(
                promotion_service,
                "register_evidence_derivation",
                fail_after_derivation,
            )
        elif failure_boundary == "activity":
            original = promotion_service.append_case_activity

            def fail_after_activity(*args: object, **kwargs: object) -> object:
                original(*args, **kwargs)
                raise RuntimeError("injected activity boundary failure")

            monkeypatch.setattr(
                promotion_service,
                "append_case_activity",
                fail_after_activity,
            )
        else:

            def fail_manifest_flush(
                session: Session,
                _flush_context: object,
                _instances: object,
            ) -> None:
                if any(
                    isinstance(instance, OfficialWorkPackageManifest)
                    and instance.id == MANIFEST_ID
                    and instance.evidence_version_id != RAW_VERSION_ID
                    for instance in session.dirty
                ):
                    raise RuntimeError("injected manifest boundary failure")

            event.listen(transaction, "before_flush", fail_manifest_flush)

        with pytest.raises(RuntimeError, match="injected"):
            promote_oa_structured_attachment(_command(), transaction)
        transaction.rollback()

    with session_factory() as verification:
        manifest = verification.get(OfficialWorkPackageManifest, MANIFEST_ID)
        assert _promotion_row_counts(verification) == (1, 0, 0, 0)
        assert (manifest.evidence_version_id, manifest.content_hash) == (
            RAW_VERSION_ID,
            CONTENT_HASH,
        )


def test_fresh_path_reuses_one_exact_same_content_typed_child(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_eligible_raw_manifest(transaction)
        transaction.add(
            DocumentEvidenceVersion(
                id=PREEXISTING_CHILD_ID,
                case_id=CASE_ID,
                document_id=DOCUMENT_ID,
                attachment_id=ATTACHMENT_ID,
                lineage_key=f"oa-raw|OA|{MANIFEST_ROLE}",
                role="OA_STRUCTURED_ATTACHMENT",
                version_number=1,
                state="FINAL",
                creator_id=ACTOR_ID,
                review_state="PENDING",
                reviewer_id=None,
                reviewed_at=None,
                final_submitted_at=None,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|oa-raw|OA|{MANIFEST_ROLE}",
            )
        )
        transaction.commit()

        result = promote_oa_structured_attachment(_command(), transaction)

        assert result.typed_evidence_version_id == PREEXISTING_CHILD_ID
        assert transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)) == 2
        derivations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.parent_evidence_version_id == RAW_VERSION_ID,
                DocumentEvidenceDerivation.child_evidence_version_id == PREEXISTING_CHILD_ID,
                DocumentEvidenceDerivation.derivation_type == "OFFICIAL_RECOGNITION",
            )
        ).all()
        assert len(derivations) == 1
