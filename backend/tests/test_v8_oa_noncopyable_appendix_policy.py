from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone
from enum import Enum
from typing import Any, get_type_hints

import pytest

from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

CASE_ID = "00000000-0000-0000-0000-000000000001"
PACKAGE_ID = "00000000-0000-0000-0000-000000000010"
PARENT_HASH = f"sha256:{'a' * 64}"
CHILD_HASH = f"sha256:{'b' * 64}"
CANONICAL_SNAPSHOT = (
    '{"component":"OA_STATEMENT_APPENDIX","schema":"FPMS_OA_NONCOPYABLE_APPENDIX_V1"}'
)


def _policy() -> object:
    return importlib.import_module("app.modules.documents.evidence_policy")


def _version(
    evidence_version_id: str,
    *,
    document_id: str,
    attachment_id: str,
    role: EvidenceRole,
    content_hash: str,
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=evidence_version_id,
        case_id=CASE_ID,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=f"oa-noncopyable:{evidence_version_id}",
        role=role.value,
        version_number=1,
        state=EvidenceVersionState.FINAL.value,
        creator_id="00000000-0000-0000-0000-000000000002",
        review_state=EvidenceReviewState.APPROVED.value,
        reviewer_id="00000000-0000-0000-0000-000000000003",
        reviewed_at=datetime(2026, 7, 18, 13, 0),
        final_submitted_at=None,
        content_hash=content_hash,
        current_identity_key=None,
    )


def _attachment(
    attachment_id: str,
    *,
    document_id: str,
    mime_type: str,
    official_file_role: str,
    source_role_alias: str | None,
    content_hash: str,
) -> DocAttachment:
    return DocAttachment(
        id=attachment_id,
        document_id=document_id,
        file_name=f"{attachment_id}.pdf",
        file_path=f"/evidence/{attachment_id}.pdf",
        mime_type=mime_type,
        official_file_role=official_file_role,
        source_role_alias=source_role_alias,
        content_hash=content_hash,
    )


def _manifest(
    manifest_id: str,
    *,
    attachment_id: str,
    evidence_version_id: str,
    official_file_role: str,
    source_role_alias: str | None,
    content_hash: str,
) -> OfficialWorkPackageManifest:
    return OfficialWorkPackageManifest(
        id=manifest_id,
        package_id=PACKAGE_ID,
        attachment_id=attachment_id,
        evidence_version_id=evidence_version_id,
        official_file_role=official_file_role,
        source_role_alias=source_role_alias,
        content_hash=content_hash,
        required=True,
        present=True,
    )


def _valid_call() -> dict[str, Any]:
    full_reply_pdf = _version(
        "full-reply-pdf",
        document_id="full-reply-document",
        attachment_id="full-reply-attachment",
        role=EvidenceRole.GENERATED_ATTACHMENT,
        content_hash=PARENT_HASH,
    )
    full_reply_attachment = _attachment(
        "full-reply-attachment",
        document_id="full-reply-document",
        mime_type="application/pdf",
        official_file_role="OA_STATEMENT_PDF",
        source_role_alias=None,
        content_hash=PARENT_HASH,
    )
    full_reply_manifest = _manifest(
        "full-reply-manifest",
        attachment_id=full_reply_attachment.id,
        evidence_version_id=full_reply_pdf.id,
        official_file_role="OA_STATEMENT_PDF",
        source_role_alias=None,
        content_hash=PARENT_HASH,
    )
    extracted_appendix = _version(
        "extracted-appendix",
        document_id="appendix-document",
        attachment_id="appendix-attachment",
        role=EvidenceRole.OA_STRUCTURED_ATTACHMENT,
        content_hash=CHILD_HASH,
    )
    appendix_attachment = _attachment(
        "appendix-attachment",
        document_id="appendix-document",
        mime_type="application/pdf",
        official_file_role="OA_OTHER_PROOF",
        source_role_alias="OA_STATEMENT_APPENDIX",
        content_hash=CHILD_HASH,
    )
    appendix_manifest = _manifest(
        "appendix-manifest",
        attachment_id=appendix_attachment.id,
        evidence_version_id=extracted_appendix.id,
        official_file_role="OA_OTHER_PROOF",
        source_role_alias="OA_STATEMENT_APPENDIX",
        content_hash=CHILD_HASH,
    )
    derivation = DocumentEvidenceDerivation(
        id="appendix-derivation",
        case_id=CASE_ID,
        parent_evidence_version_id=full_reply_pdf.id,
        child_evidence_version_id=extracted_appendix.id,
        derivation_type=EvidenceDerivationType.COMPONENT_EXTRACTION.value,
        actor_id="00000000-0000-0000-0000-000000000004",
        derived_at=datetime(2026, 7, 18, 13, 30),
        source_snapshot=CANONICAL_SNAPSHOT,
    )
    return {
        "case_id": CASE_ID,
        "package": OfficialWorkPackage(
            id=PACKAGE_ID,
            case_id=CASE_ID,
            package_kind="OA_REPLY",
            status="PREPARING",
        ),
        "full_reply_pdf": full_reply_pdf,
        "full_reply_attachment": full_reply_attachment,
        "full_reply_manifest": full_reply_manifest,
        "extracted_appendix": extracted_appendix,
        "appendix_attachment": appendix_attachment,
        "appendix_manifest": appendix_manifest,
        "derivation": derivation,
        "other_proof_evidence_version_id": extracted_appendix.id,
    }


def _set(values: dict[str, Any], path: str, value: Any) -> None:
    owner, separator, attribute = path.partition(".")
    if separator:
        setattr(values[owner], attribute, value)
    else:
        values[owner] = value


def _snapshot(values: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (
            {name: value for name, value in vars(item).items() if not name.startswith("_")}
            if hasattr(item, "__dict__")
            else item
        )
        for key, item in values.items()
    }


def _assert_error(values: dict[str, Any], expected_code: str) -> None:
    policy = _policy()
    before = _snapshot(values)
    with pytest.raises(policy.NoncopyableOaAppendixPolicyError) as caught:
        policy.require_noncopyable_oa_appendix_derivation(**values)

    assert caught.value.code.value == expected_code
    assert str(caught.value) == expected_code
    assert _snapshot(values) == before


def test_public_seam_has_exact_keyword_only_contract_and_never_uses_filename() -> None:
    policy = _policy()
    parameters = inspect.signature(
        policy.require_noncopyable_oa_appendix_derivation
    ).parameters

    assert tuple(parameters) == (
        "case_id",
        "package",
        "full_reply_pdf",
        "full_reply_attachment",
        "full_reply_manifest",
        "extracted_appendix",
        "appendix_attachment",
        "appendix_manifest",
        "derivation",
        "other_proof_evidence_version_id",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in parameters.values()
    )
    assert get_type_hints(policy.require_noncopyable_oa_appendix_derivation) == {
        "case_id": str,
        "package": OfficialWorkPackage,
        "full_reply_pdf": DocumentEvidenceVersion,
        "full_reply_attachment": DocAttachment,
        "full_reply_manifest": OfficialWorkPackageManifest,
        "extracted_appendix": DocumentEvidenceVersion,
        "appendix_attachment": DocAttachment,
        "appendix_manifest": OfficialWorkPackageManifest,
        "derivation": DocumentEvidenceDerivation,
        "other_proof_evidence_version_id": str,
        "return": type(None),
    }
    assert "file_name" not in inspect.getsource(
        policy.require_noncopyable_oa_appendix_derivation
    )

    assert issubclass(policy.NoncopyableOaAppendixErrorCode, str)
    assert issubclass(policy.NoncopyableOaAppendixErrorCode, Enum)
    assert tuple(
        (member.name, member.value)
        for member in policy.NoncopyableOaAppendixErrorCode
    ) == (
        ("INVALID_CONTEXT", "OA_NONCOPYABLE_APPENDIX_INVALID_CONTEXT"),
        ("FULL_REPLY_PDF_REQUIRED", "OA_NONCOPYABLE_FULL_REPLY_PDF_REQUIRED"),
        ("EXTRACTED_APPENDIX_REQUIRED", "OA_NONCOPYABLE_EXTRACTED_APPENDIX_REQUIRED"),
        ("CASE_MISMATCH", "OA_NONCOPYABLE_APPENDIX_CASE_MISMATCH"),
        ("DERIVATION_MISMATCH", "OA_NONCOPYABLE_APPENDIX_DERIVATION_MISMATCH"),
        ("OTHER_PROOF_NOT_APPENDIX", "OA_NONCOPYABLE_OTHER_PROOF_NOT_APPENDIX"),
    )


def test_exact_full_reply_to_appendix_derivation_is_accepted_without_mutation() -> None:
    values = _valid_call()
    before = _snapshot(values)

    assert _policy().require_noncopyable_oa_appendix_derivation(**values) is None
    assert _snapshot(values) == before


@pytest.mark.parametrize(
    ("parameter", "invalid_value"),
    (
        ("case_id", 1),
        ("case_id", f" {CASE_ID}"),
        ("package", object()),
        ("full_reply_pdf", object()),
        ("full_reply_attachment", object()),
        ("full_reply_manifest", object()),
        ("extracted_appendix", object()),
        ("appendix_attachment", object()),
        ("appendix_manifest", object()),
        ("derivation", object()),
        ("other_proof_evidence_version_id", ""),
        ("other_proof_evidence_version_id", " extracted-appendix"),
        ("package.id", ""),
        ("package.id", f" {PACKAGE_ID}"),
        ("package.case_id", ""),
        ("package.package_kind", ""),
        ("full_reply_pdf.id", ""),
        ("full_reply_pdf.case_id", ""),
        ("full_reply_pdf.document_id", ""),
        ("full_reply_pdf.attachment_id", ""),
        ("full_reply_pdf.role", ""),
        ("full_reply_pdf.content_hash", "sha256:not-a-hash"),
        ("full_reply_attachment.id", ""),
        ("full_reply_attachment.document_id", ""),
        ("full_reply_attachment.mime_type", ""),
        ("full_reply_attachment.official_file_role", ""),
        ("full_reply_attachment.content_hash", "sha256:not-a-hash"),
        ("full_reply_manifest.id", ""),
        ("full_reply_manifest.package_id", ""),
        ("full_reply_manifest.attachment_id", ""),
        ("full_reply_manifest.evidence_version_id", ""),
        ("full_reply_manifest.official_file_role", ""),
        ("full_reply_manifest.content_hash", "sha256:not-a-hash"),
        ("full_reply_manifest.present", 1),
        ("extracted_appendix.id", ""),
        ("extracted_appendix.case_id", ""),
        ("extracted_appendix.document_id", ""),
        ("extracted_appendix.attachment_id", ""),
        ("extracted_appendix.role", ""),
        ("extracted_appendix.content_hash", "sha256:not-a-hash"),
        ("appendix_attachment.id", ""),
        ("appendix_attachment.document_id", ""),
        ("appendix_attachment.official_file_role", ""),
        ("appendix_attachment.source_role_alias", ""),
        ("appendix_attachment.content_hash", "sha256:not-a-hash"),
        ("appendix_manifest.id", ""),
        ("appendix_manifest.package_id", ""),
        ("appendix_manifest.attachment_id", ""),
        ("appendix_manifest.evidence_version_id", ""),
        ("appendix_manifest.official_file_role", ""),
        ("appendix_manifest.source_role_alias", ""),
        ("appendix_manifest.content_hash", "sha256:not-a-hash"),
        ("appendix_manifest.present", 1),
        ("derivation.id", ""),
        ("derivation.case_id", ""),
        ("derivation.parent_evidence_version_id", ""),
        ("derivation.child_evidence_version_id", ""),
        ("derivation.derivation_type", ""),
        ("derivation.actor_id", ""),
        ("derivation.derived_at", "2026-07-18T13:30:00"),
        ("derivation.derived_at", datetime(2026, 7, 18, tzinfo=timezone.utc)),
        ("derivation.source_snapshot", ""),
        ("derivation.source_snapshot", 1),
    ),
)
def test_invalid_context_fails_closed(parameter: str, invalid_value: Any) -> None:
    values = _valid_call()
    _set(values, parameter, invalid_value)

    _assert_error(values, "OA_NONCOPYABLE_APPENDIX_INVALID_CONTEXT")


@pytest.mark.parametrize(
    "parameter",
    (
        "package.case_id",
        "full_reply_pdf.case_id",
        "extracted_appendix.case_id",
        "derivation.case_id",
    ),
)
def test_every_same_case_carrier_is_required(parameter: str) -> None:
    values = _valid_call()
    _set(values, parameter, "00000000-0000-0000-0000-000000000099")

    _assert_error(values, "OA_NONCOPYABLE_APPENDIX_CASE_MISMATCH")


@pytest.mark.parametrize(
    ("parameter", "invalid_value"),
    (
        ("full_reply_pdf.role", EvidenceRole.OA_STRUCTURED_ATTACHMENT.value),
        ("full_reply_attachment.mime_type", "application/octet-stream"),
        ("full_reply_attachment.official_file_role", "OA_OTHER_PROOF"),
        ("full_reply_manifest.official_file_role", "OA_OTHER_PROOF"),
    ),
)
def test_parent_must_have_exact_full_reply_pdf_identity(
    parameter: str,
    invalid_value: Any,
) -> None:
    values = _valid_call()
    _set(values, parameter, invalid_value)

    _assert_error(values, "OA_NONCOPYABLE_FULL_REPLY_PDF_REQUIRED")


@pytest.mark.parametrize(
    ("parameter", "invalid_value"),
    (
        ("extracted_appendix.role", EvidenceRole.GENERATED_ATTACHMENT.value),
        ("appendix_attachment.official_file_role", "OA_ADDITIONAL_FILE"),
        ("appendix_manifest.official_file_role", "OA_ADDITIONAL_FILE"),
        ("appendix_attachment.source_role_alias", "OA_STATEMENT_WORD"),
        ("appendix_manifest.source_role_alias", "OA_STATEMENT_WORD"),
    ),
)
def test_child_must_have_exact_appendix_other_proof_identity(
    parameter: str,
    invalid_value: Any,
) -> None:
    values = _valid_call()
    _set(values, parameter, invalid_value)

    _assert_error(values, "OA_NONCOPYABLE_EXTRACTED_APPENDIX_REQUIRED")


@pytest.mark.parametrize(
    ("parameter", "invalid_value"),
    (
        ("package.package_kind", "FILING"),
        ("full_reply_manifest.package_id", "other-package"),
        ("appendix_manifest.package_id", "other-package"),
        ("full_reply_attachment.id", "other-parent-attachment"),
        ("full_reply_attachment.document_id", "other-parent-document"),
        ("full_reply_manifest.attachment_id", "other-parent-attachment"),
        ("full_reply_manifest.evidence_version_id", "other-parent-evidence"),
        ("full_reply_manifest.present", False),
        ("appendix_attachment.id", "other-child-attachment"),
        ("appendix_attachment.document_id", "other-child-document"),
        ("appendix_manifest.attachment_id", "other-child-attachment"),
        ("appendix_manifest.evidence_version_id", "other-child-evidence"),
        ("appendix_manifest.present", False),
        ("full_reply_attachment.content_hash", CHILD_HASH),
        ("full_reply_manifest.content_hash", CHILD_HASH),
        ("appendix_attachment.content_hash", PARENT_HASH),
        ("appendix_manifest.content_hash", PARENT_HASH),
        ("derivation.parent_evidence_version_id", "unrelated-parent"),
        ("derivation.child_evidence_version_id", "unrelated-child"),
        ("derivation.derivation_type", "RENDERING"),
        (
            "derivation.source_snapshot",
            '{"schema":"FPMS_OA_NONCOPYABLE_APPENDIX_V1",'
            '"component":"OA_STATEMENT_APPENDIX"}',
        ),
    ),
)
def test_package_link_hash_identity_and_derivation_mismatches_fail_closed(
    parameter: str,
    invalid_value: Any,
) -> None:
    values = _valid_call()
    _set(values, parameter, invalid_value)

    _assert_error(values, "OA_NONCOPYABLE_APPENDIX_DERIVATION_MISMATCH")


@pytest.mark.parametrize("identity", ("evidence", "attachment", "document"))
def test_parent_and_child_identities_must_be_distinct(identity: str) -> None:
    values = _valid_call()
    if identity == "evidence":
        values["extracted_appendix"].id = values["full_reply_pdf"].id
        values["appendix_manifest"].evidence_version_id = values["full_reply_pdf"].id
        values["derivation"].child_evidence_version_id = values["full_reply_pdf"].id
        values["other_proof_evidence_version_id"] = values["full_reply_pdf"].id
    elif identity == "attachment":
        values["extracted_appendix"].attachment_id = values[
            "full_reply_attachment"
        ].id
        values["appendix_attachment"].id = values["full_reply_attachment"].id
        values["appendix_manifest"].attachment_id = values[
            "full_reply_attachment"
        ].id
    else:
        values["extracted_appendix"].document_id = values["full_reply_pdf"].document_id
        values["appendix_attachment"].document_id = values[
            "full_reply_pdf"
        ].document_id

    _assert_error(values, "OA_NONCOPYABLE_APPENDIX_DERIVATION_MISMATCH")


@pytest.mark.parametrize(
    "selected_id",
    (
        "full-reply-pdf",
        "unrelated-evidence",
    ),
)
def test_selected_other_proof_must_be_the_child_only(selected_id: str) -> None:
    values = _valid_call()
    values["other_proof_evidence_version_id"] = selected_id

    _assert_error(values, "OA_NONCOPYABLE_OTHER_PROOF_NOT_APPENDIX")


def test_error_priority_is_fixed_and_failures_do_not_mutate_inputs() -> None:
    stages = (
        ("case_id", "", "OA_NONCOPYABLE_APPENDIX_INVALID_CONTEXT"),
        (
            "package.case_id",
            "other-case",
            "OA_NONCOPYABLE_APPENDIX_CASE_MISMATCH",
        ),
        (
            "full_reply_attachment.mime_type",
            "text/plain",
            "OA_NONCOPYABLE_FULL_REPLY_PDF_REQUIRED",
        ),
        (
            "appendix_attachment.source_role_alias",
            "OA_STATEMENT_WORD",
            "OA_NONCOPYABLE_EXTRACTED_APPENDIX_REQUIRED",
        ),
        (
            "package.package_kind",
            "FILING",
            "OA_NONCOPYABLE_APPENDIX_DERIVATION_MISMATCH",
        ),
        (
            "other_proof_evidence_version_id",
            "full-reply-pdf",
            "OA_NONCOPYABLE_OTHER_PROOF_NOT_APPENDIX",
        ),
    )
    values = _valid_call()
    for parameter, invalid_value, _expected_code in stages:
        _set(values, parameter, invalid_value)
    before = _snapshot(values)

    for parameter, valid_value, expected_code in (
        ("case_id", CASE_ID, stages[0][2]),
        ("package.case_id", CASE_ID, stages[1][2]),
        ("full_reply_attachment.mime_type", "application/pdf", stages[2][2]),
        (
            "appendix_attachment.source_role_alias",
            "OA_STATEMENT_APPENDIX",
            stages[3][2],
        ),
        ("package.package_kind", "OA_REPLY", stages[4][2]),
        (
            "other_proof_evidence_version_id",
            "extracted-appendix",
            stages[5][2],
        ),
    ):
        _assert_error(values, expected_code)
        _set(values, parameter, valid_value)

    assert _snapshot(values) != before
    assert _policy().require_noncopyable_oa_appendix_derivation(**values) is None
