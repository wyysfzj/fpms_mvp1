from __future__ import annotations

import inspect
import json
from dataclasses import fields, is_dataclass, replace
from datetime import datetime
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.evidence_policy import CopyableOaAttachmentEvidence
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

REVIEWED_AT = datetime(2026, 7, 18, 9)
CONTENT_HASHES = {
    "source": f"sha256:{'a' * 64}",
    "statement": f"sha256:{'b' * 64}",
    "claims": f"sha256:{'c' * 64}",
    "reply": f"sha256:{'d' * 64}",
    "other": f"sha256:{'e' * 64}",
    "additional": f"sha256:{'f' * 64}",
    "full_reply": f"sha256:{'1' * 64}",
}
PREPARATION_SCHEMA = "FPMS_OA_REPLY_PREPARATION_V1"
PREPARATION_TYPE = EvidenceDerivationType.OA_REPLY_PREPARATION.value
APPENDIX_SNAPSHOT = (
    '{"component":"OA_STATEMENT_APPENDIX","schema":"FPMS_OA_NONCOPYABLE_APPENDIX_V1"}'
)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _workflow():
    from app.modules.documents import evidence_workflow_service

    return evidence_workflow_service


def _version_result(version: DocumentEvidenceVersion) -> EvidenceVersionResult:
    return EvidenceVersionResult(
        evidence_version_id=version.id,
        case_id=version.case_id,
        document_id=version.document_id,
        attachment_id=version.attachment_id,
        lineage_key=version.lineage_key,
        role=EvidenceRole(version.role),
        version_number=version.version_number,
        state=EvidenceVersionState(version.state),
        creator_id=version.creator_id,
        review_state=EvidenceReviewState(version.review_state),
        reviewer_id=version.reviewer_id,
        reviewed_at=version.reviewed_at,
        final_submitted_at=version.final_submitted_at,
        content_hash=version.content_hash,
        is_current=version.current_identity_key is not None,
        is_final=version.state == EvidenceVersionState.FINAL.value,
    )


def _seed_attachment(
    transaction: Session,
    *,
    document_id: str,
    attachment_id: str,
    name: str,
    content_hash: str,
    mime_type: str | None = None,
    official_file_role: str | None = None,
    source_role_alias: str | None = None,
) -> DocAttachment:
    attachment = DocAttachment(
        id=attachment_id,
        document_id=document_id,
        file_name=name,
        file_path=f"/evidence/{name}",
        mime_type=mime_type,
        official_file_role=official_file_role,
        source_role_alias=source_role_alias,
        content_hash=content_hash,
    )
    transaction.add(attachment)
    transaction.flush()
    return attachment


def _seed_version(
    transaction: Session,
    *,
    version_id: str,
    case_id: str,
    document_id: str,
    attachment_id: str,
    lineage_key: str,
    role: EvidenceRole,
    content_hash: str,
    creator_id: str,
    approved: bool,
) -> DocumentEvidenceVersion:
    version = DocumentEvidenceVersion(
        id=version_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=lineage_key,
        role=role.value,
        version_number=1,
        state=EvidenceVersionState.FINAL.value,
        creator_id=creator_id,
        review_state=(
            EvidenceReviewState.APPROVED.value if approved else EvidenceReviewState.PENDING.value
        ),
        reviewer_id=_id(901) if approved else None,
        reviewed_at=REVIEWED_AT if approved else None,
        final_submitted_at=None,
        content_hash=content_hash,
        current_identity_key=f"{case_id}|{lineage_key}",
    )
    transaction.add(version)
    transaction.flush()
    return version


def _seed_typed_attachment(
    transaction: Session,
    fixture: dict[str, object],
    *,
    offset: int,
    role: str,
    content_hash: str,
    present: bool = True,
    manifest_source_role_alias: str | None = None,
    attachment_source_role_alias: str | None = None,
) -> tuple[
    CopyableOaAttachmentEvidence,
    DocumentEvidenceVersion,
    DocAttachment,
    OfficialWorkPackageManifest,
]:
    case = fixture["case"]
    package = fixture["package"]
    document = Document(
        id=_id(offset),
        case_id=case.id,
        direction="OUT",
        title=role,
    )
    transaction.add(document)
    transaction.flush()
    attachment = _seed_attachment(
        transaction,
        document_id=document.id,
        attachment_id=_id(offset + 10),
        name=f"{role.lower()}.dat",
        content_hash=content_hash,
        official_file_role=None,
        source_role_alias=attachment_source_role_alias,
    )
    version = _seed_version(
        transaction,
        version_id=_id(offset + 20),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=f"oa-structured:{attachment.id}",
        role=EvidenceRole.OA_STRUCTURED_ATTACHMENT,
        content_hash=content_hash,
        creator_id=_id(800),
        approved=True,
    )
    manifest = OfficialWorkPackageManifest(
        id=_id(offset + 30),
        package_id=package.id,
        attachment_id=attachment.id,
        evidence_version_id=version.id,
        official_file_role=role,
        source_role_alias=manifest_source_role_alias,
        content_hash=version.content_hash,
        present=present,
    )
    transaction.add(manifest)
    transaction.flush()
    selected = CopyableOaAttachmentEvidence(
        evidence_version=_version_result(version),
        manifest_id=manifest.id,
        manifest_case_id=case.id,
        manifest_package_id=package.id,
        manifest_role=role,
        manifest_evidence_version_id=version.id,
        manifest_content_hash=version.content_hash,
    )
    return selected, version, attachment, manifest


def _seed_fixture(transaction: Session) -> dict[str, object]:
    oa_in = transaction.scalar(select(DocTemplate).where(DocTemplate.code == "OA_IN"))
    oa_out = transaction.scalar(select(DocTemplate).where(DocTemplate.code == "OA_OUT"))
    assert oa_in is not None
    assert oa_out is not None

    case = Case(id=_id(1), case_no="V8-PREPARE-OA-REPLY", status="OA1")
    source = Document(
        id=_id(10),
        case_id=case.id,
        doc_template_id=oa_in.id,
        doc_type="OFFICIAL_NOTICE",
        direction="IN",
        title="审查意见通知书",
        need_reply=True,
    )
    reply = Document(
        id=_id(20),
        case_id=case.id,
        doc_template_id=oa_out.id,
        doc_type="OA_REPLY",
        direction="OUT",
        title="审查意见答复",
        reply_to_id=source.id,
    )
    transaction.add_all([case, source, reply])
    transaction.flush()

    source_attachment = _seed_attachment(
        transaction,
        document_id=source.id,
        attachment_id=_id(11),
        name="oa-notice.pdf",
        content_hash=CONTENT_HASHES["source"],
    )
    source_version = _seed_version(
        transaction,
        version_id=_id(12),
        case_id=case.id,
        document_id=source.id,
        attachment_id=source_attachment.id,
        lineage_key=f"oa-notice:{source.id}",
        role=EvidenceRole.RAW_ATTACHMENT,
        content_hash=CONTENT_HASHES["source"],
        creator_id=_id(800),
        approved=False,
    )
    reply_attachment = _seed_attachment(
        transaction,
        document_id=reply.id,
        attachment_id=_id(21),
        name="oa-reply.pdf",
        content_hash=CONTENT_HASHES["reply"],
    )

    package = OfficialWorkPackage(
        id=_id(30),
        case_id=case.id,
        package_kind="OA_REPLY",
        status="PREPARING",
        source_document_id=source.id,
        resolve_key=f"OA_REPLY:{source.id}",
    )
    transaction.add(package)
    transaction.flush()

    fixture: dict[str, object] = {
        "case": case,
        "source": source,
        "source_attachment": source_attachment,
        "source_version": source_version,
        "reply": reply,
        "reply_attachment": reply_attachment,
        "package": package,
    }
    statement = _seed_typed_attachment(
        transaction,
        fixture,
        offset=40,
        role="OA_STATEMENT_WORD",
        content_hash=CONTENT_HASHES["statement"],
    )
    claims = _seed_typed_attachment(
        transaction,
        fixture,
        offset=41,
        role="OA_MODIFIED_CLAIMS",
        content_hash=CONTENT_HASHES["claims"],
    )

    transaction.commit()
    fixture["selected"] = (statement[0], claims[0])
    fixture["typed"] = (statement, claims)
    return fixture


def _command(fixture: dict[str, object], **overrides: object):
    workflow = _workflow()
    values = {
        "case_id": fixture["case"].id,
        "source_document_id": fixture["source"].id,
        "source_evidence_version_id": fixture["source_version"].id,
        "package_id": fixture["package"].id,
        "reply_document_id": fixture["reply"].id,
        "reply_attachment_id": fixture["reply_attachment"].id,
        "reply_content_hash": CONTENT_HASHES["reply"],
        "actor_id": _id(700),
        "attachments": fixture["selected"],
    }
    values.update(overrides)
    return workflow.PrepareOaReplyCommand(**values)


def _assert_business_error(code: str, status: int, callable_: object) -> None:
    with pytest.raises(BusinessError) as caught:
        callable_()  # type: ignore[operator]
    assert (caught.value.code, caught.value.status_code) == (code, status)


def _durable_counts(transaction: Session) -> tuple[int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)) or 0,
        transaction.scalar(select(func.count()).select_from(DocumentEvidenceDerivation)) or 0,
        transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) or 0,
    )


def _preparation_derivations(transaction: Session) -> list[DocumentEvidenceDerivation]:
    return transaction.scalars(
        select(DocumentEvidenceDerivation).where(
            DocumentEvidenceDerivation.derivation_type == PREPARATION_TYPE
        )
    ).all()


def _carrier_snapshot(
    carrier: DocumentEvidenceVersion | DocumentEvidenceDerivation | OfficialWorkPackage,
) -> tuple[tuple[str, object], ...]:
    return tuple(
        (column.name, getattr(carrier, column.name)) for column in carrier.__table__.columns
    )


def _canonical_receipt(
    fixture: dict[str, object],
    *,
    reply_version: DocumentEvidenceVersion,
    prepared_at: datetime,
) -> str:
    attachments = []
    for _selected, version, attachment, manifest in fixture["typed"]:
        attachments.append(
            {
                "attachment_content_hash": attachment.content_hash,
                "attachment_document_id": attachment.document_id,
                "attachment_id": attachment.id,
                "attachment_source_role_alias": attachment.source_role_alias,
                "evidence_content_hash": version.content_hash,
                "evidence_document_id": version.document_id,
                "evidence_lineage_key": version.lineage_key,
                "evidence_role": version.role,
                "evidence_version_id": version.id,
                "evidence_version_number": version.version_number,
                "manifest_attachment_id": manifest.attachment_id,
                "manifest_content_hash": manifest.content_hash,
                "manifest_evidence_version_id": manifest.evidence_version_id,
                "manifest_id": manifest.id,
                "manifest_role": manifest.official_file_role,
                "manifest_source_role_alias": manifest.source_role_alias,
            }
        )
    role_rank = {
        role: rank
        for rank, role in enumerate(
            (
                "OA_STATEMENT_WORD",
                "OA_MODIFIED_CLAIMS",
                "OA_AMENDMENT_COMPARISON",
                "OA_OTHER_PROOF",
                "OA_ADDITIONAL_FILE",
            )
        )
    }
    attachments.sort(
        key=lambda item: (
            role_rank[item["manifest_role"]],
            item["manifest_id"],
            item["evidence_version_id"],
        )
    )
    source = fixture["source"]
    source_attachment = fixture["source_attachment"]
    source_version = fixture["source_version"]
    reply = fixture["reply"]
    reply_attachment = fixture["reply_attachment"]
    package = fixture["package"]
    payload = {
        "actor_id": _id(700),
        "attachments": attachments,
        "case_id": fixture["case"].id,
        "package_id": package.id,
        "prepared_at": prepared_at.isoformat(timespec="microseconds"),
        "reply": {
            "attachment_id": reply_attachment.id,
            "content_hash": reply_version.content_hash,
            "document_id": reply.id,
            "evidence_version_id": reply_version.id,
            "lineage_key": f"oa-reply:{source.id}",
        },
        "schema": PREPARATION_SCHEMA,
        "source": {
            "attachment_id": source_attachment.id,
            "content_hash": source_version.content_hash,
            "document_id": source.id,
            "evidence_version_id": source_version.id,
            "lineage_key": source_version.lineage_key,
        },
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_public_prepare_contract_is_frozen_typed_and_caller_transactional() -> None:
    workflow = _workflow()
    expected_command_fields = (
        ("case_id", str),
        ("source_document_id", str),
        ("source_evidence_version_id", str),
        ("package_id", str),
        ("reply_document_id", str),
        ("reply_attachment_id", str),
        ("reply_content_hash", str),
        ("actor_id", str),
        ("attachments", tuple[CopyableOaAttachmentEvidence, ...]),
    )
    expected_result_fields = (
        ("case_id", str),
        ("source_document_id", str),
        ("source_evidence_version_id", str),
        ("reply_document_id", str),
        ("reply_evidence_version_id", str),
        ("package_id", str),
        ("content_hash", str),
        ("reused", bool),
    )
    for data_type, expected_fields in (
        (workflow.PrepareOaReplyCommand, expected_command_fields),
        (workflow.OaReplyPackageResult, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )
        assert all(field.kw_only for field in fields(data_type))
        assert "__slots__" in data_type.__dict__

    signature = inspect.signature(workflow.prepare_oa_reply)
    assert tuple(signature.parameters) == ("command", "transaction")
    hints = get_type_hints(workflow.prepare_oa_reply)
    assert hints == {
        "command": workflow.PrepareOaReplyCommand,
        "transaction": Session,
        "return": workflow.OaReplyPackageResult,
    }


def test_prepare_ignores_absent_placeholder_and_creates_exact_canonical_receipt(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        _seed_typed_attachment(
            transaction,
            fixture,
            offset=90,
            role="OA_ADDITIONAL_FILE",
            content_hash=CONTENT_HASHES["additional"],
            present=False,
        )
        other_high = _seed_typed_attachment(
            transaction,
            fixture,
            offset=80,
            role="OA_OTHER_PROOF",
            content_hash=f"sha256:{'2' * 64}",
        )
        other_low = _seed_typed_attachment(
            transaction,
            fixture,
            offset=70,
            role="OA_OTHER_PROOF",
            content_hash=f"sha256:{'3' * 64}",
        )
        statement, claims = fixture["typed"]
        fixture["selected"] = (
            other_high[0],
            other_low[0],
            claims[0],
            statement[0],
        )
        fixture["typed"] = (other_high, other_low, claims, statement)
        transaction.commit()
        before = _durable_counts(transaction)
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        real_flush = transaction.flush
        flush_entries: list[
            tuple[
                tuple[object, ...] | None,
                tuple[object, ...],
                str | None,
                tuple[DocumentEvidenceDerivation, ...],
            ]
        ] = []

        def flush_spy(objects: list[object] | None = None) -> None:
            pending_derivations = tuple(
                row
                for row in transaction.new
                if isinstance(row, DocumentEvidenceDerivation)
                and row.derivation_type == PREPARATION_TYPE
            )
            flush_entries.append(
                (
                    None if objects is None else tuple(objects),
                    tuple(transaction.new),
                    fixture["package"].reply_document_id,
                    pending_derivations,
                )
            )
            real_flush(objects)

        register = Mock(side_effect=AssertionError("generic derivation registration is forbidden"))
        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)
        monkeypatch.setattr(transaction, "flush", flush_spy)
        monkeypatch.setattr(workflow, "register_evidence_derivation", register, raising=False)

        result = workflow.prepare_oa_reply(_command(fixture), transaction)

        assert result == workflow.OaReplyPackageResult(
            case_id=fixture["case"].id,
            source_document_id=fixture["source"].id,
            source_evidence_version_id=fixture["source_version"].id,
            reply_document_id=fixture["reply"].id,
            reply_evidence_version_id=result.reply_evidence_version_id,
            package_id=fixture["package"].id,
            content_hash=CONTENT_HASHES["reply"],
            reused=False,
        )
        assert commit.call_count == rollback.call_count == register.call_count == 0
        reply_version = transaction.get(
            DocumentEvidenceVersion,
            result.reply_evidence_version_id,
        )
        package = transaction.get(OfficialWorkPackage, fixture["package"].id)
        assert reply_version is not None
        assert package is not None
        assert len(flush_entries) == 2
        first_objects, first_new, first_link, first_derivations = flush_entries[0]
        assert first_objects == (reply_version,)
        assert first_new == (reply_version,)
        assert first_link is None
        assert first_derivations == ()
        second_objects, second_new, second_link, second_derivations = flush_entries[1]
        assert second_objects is None
        assert second_link == fixture["reply"].id
        assert len(second_derivations) == 1
        assert second_new == second_derivations
        assert (
            second_derivations[0].case_id,
            second_derivations[0].parent_evidence_version_id,
            second_derivations[0].child_evidence_version_id,
            second_derivations[0].derivation_type,
        ) == (
            fixture["case"].id,
            fixture["source_version"].id,
            reply_version.id,
            PREPARATION_TYPE,
        )
        assert (
            reply_version.case_id,
            reply_version.document_id,
            reply_version.attachment_id,
            reply_version.role,
            reply_version.state,
            reply_version.review_state,
            reply_version.reviewer_id,
            reply_version.reviewed_at,
            reply_version.final_submitted_at,
            reply_version.content_hash,
            package.reply_document_id,
        ) == (
            fixture["case"].id,
            fixture["reply"].id,
            fixture["reply_attachment"].id,
            EvidenceRole.GENERATED_ATTACHMENT.value,
            EvidenceVersionState.DRAFT.value,
            EvidenceReviewState.PENDING.value,
            None,
            None,
            None,
            CONTENT_HASHES["reply"],
            fixture["reply"].id,
        )
        derivations = _preparation_derivations(transaction)
        assert len(derivations) == 1
        derivation = derivations[0]
        assert (
            derivation.case_id,
            derivation.parent_evidence_version_id,
            derivation.child_evidence_version_id,
            derivation.derivation_type,
            derivation.actor_id,
            derivation.derived_at.tzinfo,
        ) == (
            fixture["case"].id,
            fixture["source_version"].id,
            reply_version.id,
            PREPARATION_TYPE,
            _id(700),
            None,
        )
        assert derivation.source_snapshot == _canonical_receipt(
            fixture,
            reply_version=reply_version,
            prepared_at=derivation.derived_at,
        )
        parsed = json.loads(derivation.source_snapshot)
        assert set(parsed) == {
            "actor_id",
            "attachments",
            "case_id",
            "package_id",
            "prepared_at",
            "reply",
            "schema",
            "source",
        }
        assert parsed["schema"] == PREPARATION_SCHEMA
        assert datetime.fromisoformat(parsed["prepared_at"]) == derivation.derived_at
        assert parsed["prepared_at"] == derivation.derived_at.isoformat(timespec="microseconds")
        assert derivation.source_snapshot == json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        after = _durable_counts(transaction)
        assert after == (before[0] + 1, before[1] + 1, before[2])


def test_supplying_a_present_false_manifest_conflicts_before_reply_writes(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        absent, *_ = _seed_typed_attachment(
            transaction,
            fixture,
            offset=90,
            role="OA_ADDITIONAL_FILE",
            content_hash=CONTENT_HASHES["additional"],
            present=False,
        )
        transaction.commit()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(
                _command(fixture, attachments=(*fixture["selected"], absent)),
                transaction,
            ),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


@pytest.mark.parametrize("duplicate_identity", ("evidence_version_id", "manifest_id"))
def test_duplicate_typed_identity_conflicts_before_reply_writes(
    session_factory: sessionmaker[Session],
    duplicate_identity: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        statement, claims = fixture["selected"]
        if duplicate_identity == "evidence_version_id":
            claims = replace(
                claims,
                evidence_version=statement.evidence_version,
                manifest_evidence_version_id=(statement.evidence_version.evidence_version_id),
            )
        else:
            claims = replace(claims, manifest_id=statement.manifest_id)
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(
                _command(fixture, attachments=(statement, claims)),
                transaction,
            ),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_ordinary_other_proof_is_copyable_and_does_not_invoke_appendix_policy(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        ordinary = _seed_typed_attachment(
            transaction,
            fixture,
            offset=90,
            role="OA_OTHER_PROOF",
            content_hash=CONTENT_HASHES["other"],
        )
        fixture["selected"] = (*fixture["selected"], ordinary[0])
        fixture["typed"] = (*fixture["typed"], ordinary)
        transaction.commit()
        forbidden = Mock(side_effect=AssertionError("ordinary proof is not an appendix"))
        monkeypatch.setattr(workflow, "require_noncopyable_oa_appendix_derivation", forbidden)

        result = workflow.prepare_oa_reply(_command(fixture), transaction)

        assert result.reused is False
        assert forbidden.call_count == 0


@pytest.mark.parametrize(
    ("manifest_alias", "attachment_alias"),
    (
        ("OA_STATEMENT_APPENDIX", None),
        (None, "OA_STATEMENT_APPENDIX"),
    ),
)
def test_one_sided_appendix_alias_conflicts_without_invoking_policy(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    manifest_alias: str | None,
    attachment_alias: str | None,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        appendix = _seed_typed_attachment(
            transaction,
            fixture,
            offset=90,
            role="OA_OTHER_PROOF",
            content_hash=CONTENT_HASHES["other"],
            manifest_source_role_alias=manifest_alias,
            attachment_source_role_alias=attachment_alias,
        )
        fixture["selected"] = (*fixture["selected"], appendix[0])
        fixture["typed"] = (*fixture["typed"], appendix)
        transaction.commit()
        forbidden = Mock(side_effect=AssertionError("one-sided alias must fail before policy"))
        monkeypatch.setattr(workflow, "require_noncopyable_oa_appendix_derivation", forbidden)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )


def test_two_sided_appendix_alias_invokes_accepted_noncopyable_policy(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    accepted_policy = workflow.require_noncopyable_oa_appendix_derivation
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        appendix = _seed_typed_attachment(
            transaction,
            fixture,
            offset=90,
            role="OA_OTHER_PROOF",
            content_hash=CONTENT_HASHES["other"],
            manifest_source_role_alias="OA_STATEMENT_APPENDIX",
            attachment_source_role_alias="OA_STATEMENT_APPENDIX",
        )
        appendix[2].official_file_role = "OA_OTHER_PROOF"
        full_document = Document(
            id=_id(100),
            case_id=fixture["case"].id,
            direction="OUT",
            title="OA_STATEMENT_PDF",
        )
        transaction.add(full_document)
        transaction.flush()
        full_attachment = _seed_attachment(
            transaction,
            document_id=full_document.id,
            attachment_id=_id(110),
            name="full-reply.pdf",
            content_hash=CONTENT_HASHES["full_reply"],
            mime_type="application/pdf",
            official_file_role="OA_STATEMENT_PDF",
        )
        full_version = _seed_version(
            transaction,
            version_id=_id(120),
            case_id=fixture["case"].id,
            document_id=full_document.id,
            attachment_id=full_attachment.id,
            lineage_key=f"oa-full-reply:{fixture['source'].id}",
            role=EvidenceRole.GENERATED_ATTACHMENT,
            content_hash=CONTENT_HASHES["full_reply"],
            creator_id=_id(800),
            approved=True,
        )
        full_version.state = EvidenceVersionState.DRAFT.value
        full_manifest = OfficialWorkPackageManifest(
            id=_id(130),
            package_id=fixture["package"].id,
            attachment_id=full_attachment.id,
            evidence_version_id=full_version.id,
            official_file_role="OA_STATEMENT_PDF",
            content_hash=full_version.content_hash,
            present=True,
        )
        extraction = DocumentEvidenceDerivation(
            id=_id(140),
            case_id=fixture["case"].id,
            parent_evidence_version_id=full_version.id,
            child_evidence_version_id=appendix[1].id,
            derivation_type=EvidenceDerivationType.COMPONENT_EXTRACTION.value,
            actor_id=_id(700),
            derived_at=REVIEWED_AT,
            source_snapshot=APPENDIX_SNAPSHOT,
        )
        transaction.add_all([full_manifest, extraction])
        fixture["selected"] = (*fixture["selected"], appendix[0])
        fixture["typed"] = (*fixture["typed"], appendix)
        transaction.commit()
        policy = Mock(wraps=accepted_policy)
        monkeypatch.setattr(workflow, "require_noncopyable_oa_appendix_derivation", policy)

        result = workflow.prepare_oa_reply(_command(fixture), transaction)

        assert result.reused is False
        assert policy.call_count == 1


@pytest.mark.parametrize(
    "mismatch",
    (
        "manifest_attachment_id",
        "dto_attachment_id",
        "attachment_document_id",
        "attachment_content_hash",
        "manifest_evidence_version_id",
        "manifest_content_hash",
    ),
)
def test_manifest_version_attachment_chain_mismatch_conflicts_before_reply_writes(
    session_factory: sessionmaker[Session],
    mismatch: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        selected, version, attachment, manifest = fixture["typed"][0]
        different_hash = f"sha256:{'9' * 64}"
        if mismatch == "manifest_attachment_id":
            manifest.attachment_id = fixture["reply_attachment"].id
        elif mismatch == "dto_attachment_id":
            changed_version = replace(
                selected.evidence_version,
                attachment_id=fixture["reply_attachment"].id,
            )
            fixture["selected"] = (
                replace(selected, evidence_version=changed_version),
                fixture["selected"][1],
            )
        elif mismatch == "attachment_document_id":
            attachment.document_id = fixture["reply"].id
        elif mismatch == "attachment_content_hash":
            attachment.content_hash = different_hash
        elif mismatch == "manifest_evidence_version_id":
            manifest.evidence_version_id = fixture["source_version"].id
        else:
            manifest.content_hash = different_hash
        transaction.flush()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


def _seed_unrelated_version(
    transaction: Session,
    fixture: dict[str, object],
    *,
    offset: int,
    lineage_key: str,
    case_id: str | None = None,
) -> DocumentEvidenceVersion:
    version_case_id = case_id or fixture["case"].id
    document = Document(
        id=_id(offset),
        case_id=version_case_id,
        direction="OUT",
        title=f"unrelated-{offset}",
    )
    transaction.add(document)
    transaction.flush()
    attachment = _seed_attachment(
        transaction,
        document_id=document.id,
        attachment_id=_id(offset + 1),
        name=f"unrelated-{offset}.bin",
        content_hash=f"sha256:{'8' * 64}",
    )
    version = _seed_version(
        transaction,
        version_id=_id(offset + 2),
        case_id=version_case_id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=lineage_key,
        role=EvidenceRole.GENERATED_ATTACHMENT,
        content_hash=attachment.content_hash,
        creator_id=_id(700),
        approved=False,
    )
    version.current_identity_key = None
    transaction.flush()
    return version


def test_fresh_requires_empty_complete_source_parent_preparation_set(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        other_child = _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key="unrelated:child",
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(160),
                case_id=fixture["case"].id,
                parent_evidence_version_id=fixture["source_version"].id,
                child_evidence_version_id=other_child.id,
                derivation_type=PREPARATION_TYPE,
                actor_id=_id(700),
                derived_at=REVIEWED_AT,
                source_snapshot="{}",
            )
        )
        transaction.commit()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


def test_fresh_rejects_cross_case_persisted_source_preparation_derivation(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        other_case = Case(
            id=_id(2),
            case_no="V8-PREPARE-OA-REPLY-OTHER",
            status="OA1",
        )
        transaction.add(other_case)
        other_child = _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key="unrelated:cross-case-child",
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(160),
                case_id=other_case.id,
                parent_evidence_version_id=fixture["source_version"].id,
                child_evidence_version_id=other_child.id,
                derivation_type=PREPARATION_TYPE,
                actor_id=_id(700),
                derived_at=REVIEWED_AT,
                source_snapshot="{}",
            )
        )
        transaction.commit()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


def test_fresh_rejects_cross_case_persisted_reply_lineage_version(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        other_case = Case(
            id=_id(2),
            case_no="V8-PREPARE-OA-REPLY-OTHER",
            status="OA1",
        )
        transaction.add(other_case)
        lineage_key = f"oa-reply:{fixture['source'].id}"
        _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key=lineage_key,
            case_id=other_case.id,
        )
        transaction.commit()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


def test_replay_rejects_same_and_cross_case_reply_lineage_versions(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        workflow.prepare_oa_reply(_command(fixture), transaction)
        other_case = Case(
            id=_id(2),
            case_no="V8-PREPARE-OA-REPLY-OTHER",
            status="OA1",
        )
        transaction.add(other_case)
        _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key=f"oa-reply:{fixture['source'].id}",
            case_id=other_case.id,
        )
        transaction.flush()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before


def test_reply_lineage_cardinality_uses_all_versions_not_document_or_role_subset(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        lineage_key = f"oa-reply:{fixture['source'].id}"
        _seed_unrelated_version(transaction, fixture, offset=150, lineage_key=lineage_key)
        _seed_unrelated_version(transaction, fixture, offset=170, lineage_key=lineage_key)
        transaction.commit()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before
        assert fixture["package"].reply_document_id is None


def test_exact_replay_reuses_same_derivation_and_extra_same_source_edge_conflicts(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        first = workflow.prepare_oa_reply(_command(fixture), transaction)
        transaction.commit()
        counts_after_first = _durable_counts(transaction)
        first_version = transaction.get(
            DocumentEvidenceVersion,
            first.reply_evidence_version_id,
        )
        first_derivation = _preparation_derivations(transaction)[0]
        package = transaction.get(OfficialWorkPackage, first.package_id)
        assert first_version is not None
        assert package is not None
        version_before = _carrier_snapshot(first_version)
        derivation_before = _carrier_snapshot(first_derivation)
        package_before = _carrier_snapshot(package)
        session_state_before = (
            tuple(transaction.new),
            tuple(transaction.dirty),
            tuple(transaction.deleted),
        )
        add = Mock(side_effect=AssertionError("replay must not add"))
        add_all = Mock(side_effect=AssertionError("replay must not add_all"))
        delete = Mock(side_effect=AssertionError("replay must not delete"))
        flush = Mock(side_effect=AssertionError("replay must not flush"))

        with monkeypatch.context() as replay_patch:
            replay_patch.setattr(transaction, "add", add)
            replay_patch.setattr(transaction, "add_all", add_all)
            replay_patch.setattr(transaction, "delete", delete)
            replay_patch.setattr(transaction, "flush", flush)
            replay = workflow.prepare_oa_reply(_command(fixture), transaction)

        assert replay == replace(first, reused=True)
        assert (
            add.call_count,
            add_all.call_count,
            delete.call_count,
            flush.call_count,
        ) == (0, 0, 0, 0)
        assert (
            tuple(transaction.new),
            tuple(transaction.dirty),
            tuple(transaction.deleted),
        ) == session_state_before
        assert _durable_counts(transaction) == counts_after_first
        assert _preparation_derivations(transaction) == [first_derivation]
        assert _carrier_snapshot(first_version) == version_before
        assert _carrier_snapshot(first_derivation) == derivation_before
        assert _carrier_snapshot(package) == package_before

        transaction.commit()
        with session_factory() as verification:
            durable_version = verification.get(
                DocumentEvidenceVersion,
                first.reply_evidence_version_id,
            )
            durable_derivation = verification.get(
                DocumentEvidenceDerivation,
                first_derivation.id,
            )
            durable_package = verification.get(OfficialWorkPackage, first.package_id)
            assert durable_version is not None
            assert durable_derivation is not None
            assert durable_package is not None
            assert _durable_counts(verification) == counts_after_first
            assert _carrier_snapshot(durable_version) == version_before
            assert _carrier_snapshot(durable_derivation) == derivation_before
            assert _carrier_snapshot(durable_package) == package_before

        other_child = _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key="unrelated:extra-child",
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(160),
                case_id=fixture["case"].id,
                parent_evidence_version_id=fixture["source_version"].id,
                child_evidence_version_id=other_child.id,
                derivation_type=PREPARATION_TYPE,
                actor_id=_id(700),
                derived_at=first_derivation.derived_at,
                source_snapshot=first_derivation.source_snapshot,
            )
        )
        transaction.flush()
        counts_with_extra = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )
        assert _durable_counts(transaction) == counts_with_extra


@pytest.mark.parametrize("carrier", ("source", "reply"))
def test_replay_rejects_cross_case_preparation_edge(
    session_factory: sessionmaker[Session],
    carrier: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        first = workflow.prepare_oa_reply(_command(fixture), transaction)
        original = _preparation_derivations(transaction)[0]
        other_case = Case(
            id=_id(2),
            case_no="V8-PREPARE-OA-REPLY-OTHER",
            status="OA1",
        )
        transaction.add(other_case)
        other_version = _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key=f"unrelated:cross-case-{carrier}",
        )
        transaction.add(
            DocumentEvidenceDerivation(
                id=_id(160),
                case_id=other_case.id,
                parent_evidence_version_id=(
                    fixture["source_version"].id if carrier == "source" else other_version.id
                ),
                child_evidence_version_id=(
                    other_version.id if carrier == "source" else first.reply_evidence_version_id
                ),
                derivation_type=PREPARATION_TYPE,
                actor_id=_id(700),
                derived_at=original.derived_at,
                source_snapshot=original.source_snapshot,
            )
        )
        transaction.flush()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before


@pytest.mark.parametrize(
    "contradiction",
    (
        "current_source",
        "source_hash",
        "typed_set",
        "typed_hash",
        "manifest_link",
        "manifest_role",
        "manifest_alias",
        "actor",
        "missing_receipt",
        "wrong_parent",
        "wrong_actor",
        "wrong_time",
        "malformed_receipt",
        "wrong_schema",
        "noncanonical_receipt",
    ),
)
def test_replay_receipt_contradictions_conflict_without_repair(
    session_factory: sessionmaker[Session],
    contradiction: str,
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        first = workflow.prepare_oa_reply(_command(fixture), transaction)
        reply_version = transaction.get(DocumentEvidenceVersion, first.reply_evidence_version_id)
        derivation = _preparation_derivations(transaction)[0]
        command_overrides: dict[str, object] = {}
        if contradiction == "current_source":
            current_source = _seed_version(
                transaction,
                version_id=_id(13),
                case_id=fixture["case"].id,
                document_id=fixture["source"].id,
                attachment_id=fixture["source_attachment"].id,
                lineage_key=f"oa-notice-current:{fixture['source'].id}",
                role=EvidenceRole.RAW_ATTACHMENT,
                content_hash=fixture["source_attachment"].content_hash,
                creator_id=_id(800),
                approved=False,
            )
            command_overrides["source_evidence_version_id"] = current_source.id
        elif contradiction == "source_hash":
            changed_hash = f"sha256:{'7' * 64}"
            fixture["source_version"].content_hash = changed_hash
            fixture["source_attachment"].content_hash = changed_hash
        elif contradiction == "typed_set":
            additional = _seed_typed_attachment(
                transaction,
                fixture,
                offset=90,
                role="OA_ADDITIONAL_FILE",
                content_hash=CONTENT_HASHES["additional"],
            )
            fixture["selected"] = (*fixture["selected"], additional[0])
            fixture["typed"] = (*fixture["typed"], additional)
        elif contradiction == "typed_hash":
            selected, version, attachment, manifest = fixture["typed"][0]
            changed_hash = f"sha256:{'7' * 64}"
            version.content_hash = changed_hash
            attachment.content_hash = changed_hash
            manifest.content_hash = changed_hash
            fixture["selected"] = (
                replace(
                    selected,
                    evidence_version=_version_result(version),
                    manifest_content_hash=changed_hash,
                ),
                fixture["selected"][1],
            )
        elif contradiction == "manifest_link":
            fixture["typed"][0][3].attachment_id = fixture["reply_attachment"].id
        elif contradiction == "manifest_role":
            selected, _, _, manifest = fixture["typed"][0]
            manifest.official_file_role = "OA_ADDITIONAL_FILE"
            fixture["selected"] = (
                replace(selected, manifest_role="OA_ADDITIONAL_FILE"),
                fixture["selected"][1],
            )
        elif contradiction == "manifest_alias":
            _, _, attachment, manifest = fixture["typed"][0]
            attachment.source_role_alias = "PRESERVED_OTHER_ALIAS"
            manifest.source_role_alias = "PRESERVED_OTHER_ALIAS"
        elif contradiction == "actor":
            command_overrides["actor_id"] = _id(701)
        elif contradiction == "missing_receipt":
            transaction.delete(derivation)
        elif contradiction == "wrong_parent":
            derivation.parent_evidence_version_id = fixture["typed"][1][1].id
        elif contradiction == "wrong_actor":
            derivation.actor_id = _id(701)
        elif contradiction == "wrong_time":
            derivation.derived_at = derivation.derived_at.replace(
                microsecond=(derivation.derived_at.microsecond + 1) % 1_000_000
            )
        elif contradiction == "malformed_receipt":
            derivation.source_snapshot = "{"
        elif contradiction == "wrong_schema":
            payload = json.loads(derivation.source_snapshot)
            payload["schema"] = "WRONG"
            derivation.source_snapshot = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        else:
            derivation.source_snapshot = f"{derivation.source_snapshot} "
        transaction.flush()
        counts_before_replay = _durable_counts(transaction)
        persisted_snapshot = (
            None if contradiction == "missing_receipt" else derivation.source_snapshot
        )

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(
                _command(fixture, **command_overrides),
                transaction,
            ),
        )

        assert _durable_counts(transaction) == counts_before_replay
        assert fixture["package"].reply_document_id == fixture["reply"].id
        assert reply_version is not None
        if contradiction == "missing_receipt":
            assert _preparation_derivations(transaction) == []
        else:
            assert derivation.source_snapshot == persisted_snapshot


def test_replay_rejects_different_source_and_reply_derivation_rows(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        first = workflow.prepare_oa_reply(_command(fixture), transaction)
        original = _preparation_derivations(transaction)[0]
        transaction.delete(original)
        other_parent = _seed_unrelated_version(
            transaction,
            fixture,
            offset=150,
            lineage_key="unrelated:parent",
        )
        other_child = _seed_unrelated_version(
            transaction,
            fixture,
            offset=170,
            lineage_key="unrelated:child",
        )
        for offset, parent_id, child_id in (
            (190, fixture["source_version"].id, other_child.id),
            (191, other_parent.id, first.reply_evidence_version_id),
        ):
            transaction.add(
                DocumentEvidenceDerivation(
                    id=_id(offset),
                    case_id=fixture["case"].id,
                    parent_evidence_version_id=parent_id,
                    child_evidence_version_id=child_id,
                    derivation_type=PREPARATION_TYPE,
                    actor_id=_id(700),
                    derived_at=original.derived_at,
                    source_snapshot=original.source_snapshot,
                )
            )
        transaction.flush()
        before = _durable_counts(transaction)

        _assert_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            409,
            lambda: workflow.prepare_oa_reply(_command(fixture), transaction),
        )

        assert _durable_counts(transaction) == before


def test_second_flush_failure_propagates_and_caller_rollback_restores_baseline(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workflow = _workflow()
    sentinel = RuntimeError("second flush sentinel")
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        before = _durable_counts(transaction)
        real_flush = transaction.flush
        flush_calls = 0
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))

        def fail_second_flush(objects: list[object] | None = None) -> None:
            nonlocal flush_calls
            flush_calls += 1
            if flush_calls == 2:
                raise sentinel
            real_flush(objects)

        with monkeypatch.context() as service_patch:
            service_patch.setattr(transaction, "commit", commit)
            service_patch.setattr(transaction, "rollback", rollback)
            service_patch.setattr(transaction, "flush", fail_second_flush)
            with pytest.raises(RuntimeError) as caught:
                workflow.prepare_oa_reply(_command(fixture), transaction)

        assert caught.value is sentinel
        assert flush_calls == 2
        assert commit.call_count == rollback.call_count == 0
        transaction.rollback()

    with session_factory() as verification:
        package = verification.get(OfficialWorkPackage, _id(30))
        assert package is not None
        assert package.reply_document_id is None
        assert _durable_counts(verification) == before


def test_caller_rollback_removes_version_reply_link_and_preparation_derivation(
    session_factory: sessionmaker[Session],
) -> None:
    workflow = _workflow()
    with session_factory() as transaction:
        fixture = _seed_fixture(transaction)
        before = _durable_counts(transaction)
        workflow.prepare_oa_reply(_command(fixture), transaction)
        transaction.rollback()

    with session_factory() as verification:
        package = verification.get(OfficialWorkPackage, _id(30))
        assert package is not None
        assert package.reply_document_id is None
        assert _durable_counts(verification) == before
