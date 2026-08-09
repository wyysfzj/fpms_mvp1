from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timezone
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)
from app.modules.tasks.models import Task

CONTENT_HASH = f"sha256:{'a' * 64}"
SUBMITTED_AT = datetime(2026, 7, 24, 1, 30)
STORED_SUBMITTED_AT = datetime(2026, 7, 24, 1, 30)
REVIEWED_AT = datetime(2026, 7, 24, 1)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _workflow():
    from app.modules.official_workflows import service

    return service


def _seed_case(transaction: Session, *, case_id: str) -> Case:
    case = Case(
        id=case_id,
        case_no=f"OA-EXTERNAL-{case_id[-12:]}",
        status="OA1",
        business_stage="PROSECUTION_MANAGEMENT",
        official_procedure_stage="OFFICE_ACTION_RESPONSE",
        legal_status="APPLICATION_PENDING",
        lifecycle_verification_status="CONFIRMED",
        lifecycle_revision=0,
    )
    transaction.add(case)
    transaction.flush()
    return case


def _seed_fixture(transaction: Session, *, ordinal: int = 1) -> dict[str, object]:
    base = ordinal * 100
    case_id = _id(base + 1)
    source_id = _id(base + 2)
    reply_id = _id(base + 3)
    attachment_id = _id(base + 4)
    version_id = _id(base + 5)
    package_id = _id(base + 6)
    creator_id = _id(base + 7)
    reviewer_id = _id(base + 8)

    case = _seed_case(transaction, case_id=case_id)
    source = Document(id=source_id, case_id=case_id, direction="IN")
    reply = Document(
        id=reply_id,
        case_id=case_id,
        direction="OUT",
        reply_to_id=source_id,
    )
    transaction.add_all((source, reply))
    transaction.flush()
    attachment = DocAttachment(
        id=attachment_id,
        document_id=reply_id,
        file_name="oa-official-submission-list.pdf",
        file_path="/evidence/oa-official-submission-list.pdf",
        official_file_role="OFFICIAL_SUBMISSION_LIST",
        content_hash=CONTENT_HASH,
    )
    transaction.add(attachment)
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=version_id,
        case_id=case_id,
        document_id=reply_id,
        attachment_id=attachment_id,
        lineage_key=f"oa-external-{ordinal}",
        role="OFFICIAL_SUBMISSION_LIST",
        version_number=1,
        state="FINAL",
        creator_id=creator_id,
        review_state="APPROVED",
        reviewer_id=reviewer_id,
        reviewed_at=REVIEWED_AT,
        content_hash=CONTENT_HASH,
        current_identity_key=f"{case_id}|oa-external-{ordinal}",
    )
    package = OfficialWorkPackage(
        id=package_id,
        case_id=case_id,
        package_kind="OA_REPLY",
        status="READY_FOR_EXTERNAL_SUBMIT",
        source_document_id=source_id,
        reply_document_id=reply_id,
        resolve_key=f"OA_REPLY:{source_id}",
    )
    transaction.add_all((version, package))
    transaction.flush()
    manifest = OfficialWorkPackageManifest(
        id=_id(base + 9),
        package_id=package_id,
        attachment_id=attachment_id,
        evidence_version_id=version_id,
        official_file_role="OFFICIAL_SUBMISSION_LIST",
        content_hash=CONTENT_HASH,
        required=True,
        present=True,
    )
    transaction.add(manifest)
    transaction.flush()
    return {
        "case": case,
        "source": source,
        "reply": reply,
        "attachment": attachment,
        "version": version,
        "package": package,
        "manifest": manifest,
        "case_id": case_id,
        "source_id": source_id,
        "reply_id": reply_id,
        "attachment_id": attachment_id,
        "version_id": version_id,
        "package_id": package_id,
        "creator_id": creator_id,
        "reviewer_id": reviewer_id,
    }


def _command(seeded: dict[str, object], **overrides: object):
    command_type = _workflow().FinalizeOaExternalSubmissionCommand
    values = {
        "package_id": seeded["package_id"],
        "evidence_version_id": seeded["version_id"],
        "actor_id": _id(90),
        "submitted_at": SUBMITTED_AT,
        "idempotency_key": "oa-submit-1",
    }
    values.update(overrides)
    return command_type(**values)


def _assert_error(code: str, status: int, callable_: object) -> BusinessError:
    with pytest.raises(BusinessError) as exc_info:
        callable_()  # type: ignore[operator]
    assert (exc_info.value.code, exc_info.value.status_code) == (code, status)
    return exc_info.value


def _counts(
    transaction: Session,
    *,
    case_id: str,
    package_id: str,
) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        )
        or 0,
        transaction.scalar(
            select(func.count())
            .select_from(OfficialWorkPackageChecklist)
            .where(OfficialWorkPackageChecklist.package_id == package_id)
        )
        or 0,
        transaction.scalar(
            select(func.count())
            .select_from(OfficialWorkPackageReceipt)
            .where(OfficialWorkPackageReceipt.package_id == package_id)
        )
        or 0,
        transaction.scalar(
            select(func.count()).select_from(Task).where(Task.case_id == case_id)
        )
        or 0,
    )


def test_public_contract_is_exact_frozen_slotted_and_keyword_only() -> None:
    workflow = _workflow()
    assert hasattr(workflow, "FinalizeOaExternalSubmissionCommand")
    assert hasattr(workflow, "FinalizeOaExternalSubmissionResult")
    assert hasattr(workflow, "finalize_oa_external_submission")

    expected_command_fields = (
        ("package_id", str),
        ("evidence_version_id", str),
        ("actor_id", str),
        ("submitted_at", datetime),
        ("idempotency_key", str),
    )
    expected_result_fields = (
        ("package_id", str),
        ("evidence_version_id", str),
        ("checklist_item", workflow.OfficialWorkPackageChecklistOut),
        ("activity_id", str),
        ("activity_sequence", int),
        ("lifecycle_revision", int),
        ("submitted_at", datetime),
        ("idempotency_key", str),
        ("reused", bool),
    )
    for data_type, expected_fields in (
        (workflow.FinalizeOaExternalSubmissionCommand, expected_command_fields),
        (workflow.FinalizeOaExternalSubmissionResult, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__

    signature = inspect.signature(workflow.finalize_oa_external_submission)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert get_type_hints(workflow.finalize_oa_external_submission)["return"] is (
        workflow.FinalizeOaExternalSubmissionResult
    )


def test_finalizes_exact_oa_evidence_once_and_replays_without_extra_writes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        seeded = _seed_fixture(transaction)
        command = _command(seeded)
        case = seeded["case"]
        package = seeded["package"]
        source = seeded["source"]
        reply = seeded["reply"]
        assert isinstance(case, Case)
        assert isinstance(package, OfficialWorkPackage)
        assert isinstance(source, Document)
        assert isinstance(reply, Document)
        case_projection_before = (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
        )
        package_before = (
            package.case_id,
            package.package_kind,
            package.status,
            package.source_document_id,
            package.reply_document_id,
            package.resolve_key,
            package.external_system,
            package.remark,
        )
        document_before = (
            source.case_id,
            source.reply_date,
            reply.case_id,
            reply.reply_to_id,
            reply.reply_date,
        )

        deep_calls: list[object] = []
        original_finalizer = workflow.finalize_external_submission

        def tracked_finalizer(deep_command: object, deep_transaction: Session):
            deep_calls.append(deep_command)
            return original_finalizer(deep_command, deep_transaction)

        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(wraps=transaction.close)
        monkeypatch.setattr(workflow, "finalize_external_submission", tracked_finalizer)
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)
        monkeypatch.setattr(transaction, "close", close)

        result = workflow.finalize_oa_external_submission(command, transaction)
        transaction.flush()
        first_counts = _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        )

        assert len(deep_calls) == 1
        deep_command = deep_calls[0]
        assert deep_command == workflow.FinalizeExternalSubmissionCommand(
            case_id=seeded["case_id"],
            evidence_version_id=seeded["version_id"],
            actor_id=_id(90),
            submitted_at=STORED_SUBMITTED_AT,
            idempotency_key=f"oa-external:{seeded['package_id']}:oa-submit-1",
        )
        assert result == workflow.FinalizeOaExternalSubmissionResult(
            package_id=seeded["package_id"],
            evidence_version_id=seeded["version_id"],
            checklist_item=result.checklist_item,
            activity_id=result.activity_id,
            activity_sequence=1,
            lifecycle_revision=1,
            submitted_at=SUBMITTED_AT,
            idempotency_key="oa-submit-1",
            reused=False,
        )
        with pytest.raises(FrozenInstanceError):
            result.reused = True  # type: ignore[misc]
        assert (
            result.checklist_item.package_id,
            result.checklist_item.section_code,
            result.checklist_item.item_code,
            result.checklist_item.item_label,
            result.checklist_item.status,
            result.checklist_item.required,
            result.checklist_item.evidence_note,
        ) == (
            seeded["package_id"],
            "OA_REPLY",
            "SUBMISSION_CONFIRMED",
            "SUBMISSION_CONFIRMED",
            "DONE",
            True,
            (
                f"evidence_version_id={seeded['version_id']}; "
                f"activity_id={result.activity_id}"
            ),
        )
        assert first_counts == (1, 1, 0, 0)
        activity = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == seeded["case_id"]
            )
        )
        assert activity is not None
        assert (
            activity.lane,
            activity.activity_type,
            activity.idempotency_key,
            activity.actor_id,
            activity.effective_at,
        ) == (
            "DOCUMENT",
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            (
                "document-external-submission:"
                f"oa-external:{seeded['package_id']}:oa-submit-1"
            ),
            _id(90),
            STORED_SUBMITTED_AT,
        )
        version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
        assert version is not None
        assert version.final_submitted_at == STORED_SUBMITTED_AT
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
        ) == case_projection_before
        assert (
            package.case_id,
            package.package_kind,
            package.status,
            package.source_document_id,
            package.reply_document_id,
            package.resolve_key,
            package.external_system,
            package.remark,
        ) == package_before
        assert (
            source.case_id,
            source.reply_date,
            reply.case_id,
            reply.reply_to_id,
            reply.reply_date,
        ) == document_before
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(
                    CaseActivityEvent.case_id == seeded["case_id"],
                    CaseActivityEvent.lane == "LIFECYCLE",
                )
            )
            == 0
        )

        replay = workflow.finalize_oa_external_submission(command, transaction)
        transaction.flush()

        assert len(deep_calls) == 2
        assert replay == replace(result, reused=True)
        assert _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        ) == first_counts
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
        assert commit.call_count == rollback.call_count == close.call_count == 0
        monkeypatch.undo()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("package_id", ""),
        ("package_id", " "),
        ("package_id", " package"),
        ("package_id", "package "),
        ("package_id", "x" * 37),
        ("evidence_version_id", ""),
        ("evidence_version_id", " evidence"),
        ("evidence_version_id", "evidence "),
        ("evidence_version_id", "x" * 37),
        ("actor_id", ""),
        ("actor_id", " actor"),
        ("actor_id", "actor "),
        ("actor_id", "x" * 37),
        ("idempotency_key", ""),
        ("idempotency_key", " key"),
        ("idempotency_key", "key "),
        ("idempotency_key", "x" * 51),
        ("submitted_at", datetime(2026, 7, 24, 1, 30, tzinfo=timezone.utc)),
    ),
)
def test_invalid_command_is_rejected_before_any_write(
    session_factory: sessionmaker[Session],
    field: str,
    value: object,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        seeded = _seed_fixture(transaction)
        command = replace(_command(seeded), **{field: value})
        before = _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        )

        error = _assert_error(
            "OA_EXTERNAL_SUBMISSION_INVALID",
            400,
            lambda: workflow.finalize_oa_external_submission(command, transaction),
        )

        assert error.details == {"field": field}
        assert _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        ) == before


@pytest.mark.parametrize(
    "mutation",
    (
        "package_kind",
        "resolve_key",
        "source_case",
        "reply_case",
        "reply_relation",
        "manifest_missing",
        "manifest_duplicate",
        "manifest_evidence",
        "manifest_hash",
        "evidence_case",
        "evidence_document",
        "evidence_role",
        "evidence_state",
        "evidence_review",
        "evidence_self_review",
        "evidence_not_current",
        "attachment_document",
        "attachment_hash",
        "evidence_hash",
    ),
)
def test_inexact_package_manifest_or_evidence_fails_closed_before_finalizer(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        seeded = _seed_fixture(transaction)
        other_case = _seed_case(transaction, case_id=_id(999))
        package = seeded["package"]
        source = seeded["source"]
        reply = seeded["reply"]
        manifest = seeded["manifest"]
        version = seeded["version"]
        attachment = seeded["attachment"]
        assert isinstance(package, OfficialWorkPackage)
        assert isinstance(source, Document)
        assert isinstance(reply, Document)
        assert isinstance(manifest, OfficialWorkPackageManifest)
        assert isinstance(version, DocumentEvidenceVersion)
        assert isinstance(attachment, DocAttachment)

        if mutation == "package_kind":
            package.package_kind = "FILING_PREP"
        elif mutation == "resolve_key":
            package.resolve_key = f"OA_REPLY:{_id(777)}"
        elif mutation == "source_case":
            source.case_id = other_case.id
        elif mutation == "reply_case":
            reply.case_id = other_case.id
        elif mutation == "reply_relation":
            reply.reply_to_id = None
        elif mutation == "manifest_missing":
            manifest.present = False
        elif mutation == "manifest_duplicate":
            transaction.add(
                OfficialWorkPackageManifest(
                    id=_id(998),
                    package_id=package.id,
                    attachment_id=attachment.id,
                    evidence_version_id=version.id,
                    official_file_role="OFFICIAL_SUBMISSION_LIST",
                    content_hash=CONTENT_HASH,
                    present=True,
                )
            )
        elif mutation == "manifest_evidence":
            manifest.evidence_version_id = None
        elif mutation == "manifest_hash":
            manifest.content_hash = f"sha256:{'b' * 64}"
        elif mutation == "evidence_case":
            version.case_id = other_case.id
        elif mutation == "evidence_document":
            version.document_id = source.id
        elif mutation == "evidence_role":
            version.role = "OFFICIAL_FINAL_PDF"
        elif mutation == "evidence_state":
            version.state = "DRAFT"
        elif mutation == "evidence_review":
            version.review_state = "PENDING"
        elif mutation == "evidence_self_review":
            version.reviewer_id = version.creator_id
        elif mutation == "evidence_not_current":
            version.current_identity_key = None
        elif mutation == "attachment_document":
            attachment.document_id = source.id
        elif mutation == "attachment_hash":
            attachment.content_hash = f"sha256:{'b' * 64}"
        elif mutation == "evidence_hash":
            version.content_hash = f"sha256:{'A' * 64}"
            manifest.content_hash = version.content_hash
            attachment.content_hash = version.content_hash
        transaction.flush()

        deep = Mock(side_effect=AssertionError("inexact carrier reached deep finalizer"))
        monkeypatch.setattr(workflow, "finalize_external_submission", deep)
        before = _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        )

        _assert_error(
            "OA_EXTERNAL_SUBMISSION_CONFLICT",
            409,
            lambda: workflow.finalize_oa_external_submission(
                _command(seeded),
                transaction,
            ),
        )

        assert deep.call_count == 0
        assert _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        ) == before


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("actor_id", _id(91)),
        (
            "submitted_at",
            datetime(2026, 7, 24, 1, 31),
        ),
    ),
)
def test_same_upstream_key_payload_drift_is_typed_conflict_with_zero_writes(
    session_factory: sessionmaker[Session],
    field: str,
    value: object,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        seeded = _seed_fixture(transaction)
        command = _command(seeded)
        workflow.finalize_oa_external_submission(command, transaction)
        transaction.flush()
        before = _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        )
        case_revision = seeded["case"].lifecycle_revision

        _assert_error(
            "OA_EXTERNAL_SUBMISSION_CONFLICT",
            409,
            lambda: workflow.finalize_oa_external_submission(
                replace(command, **{field: value}),
                transaction,
            ),
        )

        transaction.flush()
        assert _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        ) == before
        assert seeded["case"].lifecycle_revision == case_revision


def test_same_upstream_key_cannot_be_reused_for_another_package(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        first = _seed_fixture(transaction, ordinal=1)
        second = _seed_fixture(transaction, ordinal=2)
        workflow.finalize_oa_external_submission(_command(first), transaction)
        transaction.flush()
        before_first = _counts(
            transaction,
            case_id=str(first["case_id"]),
            package_id=str(first["package_id"]),
        )
        before_second = _counts(
            transaction,
            case_id=str(second["case_id"]),
            package_id=str(second["package_id"]),
        )

        _assert_error(
            "OA_EXTERNAL_SUBMISSION_CONFLICT",
            409,
            lambda: workflow.finalize_oa_external_submission(
                _command(second),
                transaction,
            ),
        )

        transaction.flush()
        assert _counts(
            transaction,
            case_id=str(first["case_id"]),
            package_id=str(first["package_id"]),
        ) == before_first
        assert _counts(
            transaction,
            case_id=str(second["case_id"]),
            package_id=str(second["package_id"]),
        ) == before_second
        second_version = transaction.get(DocumentEvidenceVersion, second["version_id"])
        assert second_version is not None
        assert second_version.final_submitted_at is None
        assert second["case"].lifecycle_revision == 0


def test_colon_containing_idempotency_keys_are_compared_as_exact_values(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        first = _seed_fixture(transaction, ordinal=1)
        second = _seed_fixture(transaction, ordinal=2)
        first_result = workflow.finalize_oa_external_submission(
            _command(first, idempotency_key="scope:shared"),
            transaction,
        )

        second_result = workflow.finalize_oa_external_submission(
            _command(second, idempotency_key="shared"),
            transaction,
        )
        transaction.flush()

        assert first_result.idempotency_key == "scope:shared"
        assert second_result.idempotency_key == "shared"
        assert first_result.activity_id != second_result.activity_id
        assert _counts(
            transaction,
            case_id=str(first["case_id"]),
            package_id=str(first["package_id"]),
        ) == (1, 1, 0, 0)
        assert _counts(
            transaction,
            case_id=str(second["case_id"]),
            package_id=str(second["package_id"]),
        ) == (1, 1, 0, 0)


def test_replay_hash_drift_is_typed_conflict_with_zero_additional_writes(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        seeded = _seed_fixture(transaction)
        command = _command(seeded)
        workflow.finalize_oa_external_submission(command, transaction)
        transaction.flush()
        manifest = seeded["manifest"]
        assert isinstance(manifest, OfficialWorkPackageManifest)
        manifest.content_hash = f"sha256:{'b' * 64}"
        transaction.flush()
        before = _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        )
        case_revision = seeded["case"].lifecycle_revision

        _assert_error(
            "OA_EXTERNAL_SUBMISSION_CONFLICT",
            409,
            lambda: workflow.finalize_oa_external_submission(command, transaction),
        )

        transaction.flush()
        assert _counts(
            transaction,
            case_id=str(seeded["case_id"]),
            package_id=str(seeded["package_id"]),
        ) == before
        assert seeded["case"].lifecycle_revision == case_revision
