from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from dataclasses import fields, is_dataclass, replace
from datetime import datetime, timezone
from typing import get_type_hints

import pytest

from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)

CASE_ID = "00000000-0000-0000-0000-000000000001"
OTHER_CASE_ID = "00000000-0000-0000-0000-000000000002"
PACKAGE_ID = "00000000-0000-0000-0000-000000000003"
OTHER_PACKAGE_ID = "00000000-0000-0000-0000-000000000004"
CREATOR_ID = "00000000-0000-0000-0000-000000000005"
REVIEWER_ID = "00000000-0000-0000-0000-000000000006"
REVIEWED_AT = datetime(2026, 7, 18, 12, 0)
CONTENT_HASH = f"sha256:{'a' * 64}"


def _policy() -> object:
    return importlib.import_module("app.modules.documents.evidence_policy")


def _evidence(
    evidence_version_id: str,
    *,
    case_id: str = CASE_ID,
    role: EvidenceRole = EvidenceRole.OA_STRUCTURED_ATTACHMENT,
    state: EvidenceVersionState = EvidenceVersionState.FINAL,
    review_state: EvidenceReviewState = EvidenceReviewState.APPROVED,
    creator_id: str = CREATOR_ID,
    reviewer_id: str | None = REVIEWER_ID,
    reviewed_at: datetime | None = REVIEWED_AT,
    content_hash: str = CONTENT_HASH,
    is_current: bool = True,
    is_final: bool = True,
) -> EvidenceVersionResult:
    return EvidenceVersionResult(
        evidence_version_id=evidence_version_id,
        case_id=case_id,
        document_id=f"document-{evidence_version_id}",
        attachment_id=f"attachment-{evidence_version_id}",
        lineage_key=f"oa-structured:{evidence_version_id}",
        role=role,
        version_number=2,
        state=state,
        creator_id=creator_id,
        review_state=review_state,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
        final_submitted_at=None,
        content_hash=content_hash,
        is_current=is_current,
        is_final=is_final,
    )


def _attachment(
    evidence_version_id: str,
    manifest_role: str,
    *,
    manifest_id: str | None = None,
    case_id: str = CASE_ID,
    package_id: str = PACKAGE_ID,
    manifest_evidence_version_id: str | None = None,
    manifest_content_hash: str = CONTENT_HASH,
    evidence: EvidenceVersionResult | None = None,
) -> object:
    policy = _policy()
    return policy.CopyableOaAttachmentEvidence(
        evidence_version=evidence or _evidence(evidence_version_id, case_id=case_id),
        manifest_id=manifest_id or f"manifest-{evidence_version_id}",
        manifest_case_id=case_id,
        manifest_package_id=package_id,
        manifest_role=manifest_role,
        manifest_evidence_version_id=(manifest_evidence_version_id or evidence_version_id),
        manifest_content_hash=manifest_content_hash,
    )


def _required_combination() -> tuple[object, ...]:
    return (
        _attachment("statement-word", "OA_STATEMENT_WORD"),
        _attachment("modified-claims", "OA_MODIFIED_CLAIMS"),
    )


def _assert_rejected(
    expected_code: str,
    *,
    case_id: str = CASE_ID,
    package_id: str = PACKAGE_ID,
    attachments: object,
) -> None:
    policy = _policy()
    with pytest.raises(policy.CopyableOaAttachmentPolicyError) as caught:
        policy.require_copyable_oa_attachment_combination(
            case_id=case_id,
            package_id=package_id,
            attachments=attachments,
        )

    assert caught.value.code.value == expected_code
    assert str(caught.value) == expected_code


def test_public_policy_contract_uses_only_typed_version_and_manifest_authority() -> None:
    policy = _policy()

    assert is_dataclass(policy.CopyableOaAttachmentEvidence)
    assert policy.CopyableOaAttachmentEvidence.__dataclass_params__.frozen is True
    assert policy.CopyableOaAttachmentEvidence.__slots__ == (
        "evidence_version",
        "manifest_id",
        "manifest_case_id",
        "manifest_package_id",
        "manifest_role",
        "manifest_evidence_version_id",
        "manifest_content_hash",
    )
    assert tuple(field.name for field in fields(policy.CopyableOaAttachmentEvidence)) == (
        "evidence_version",
        "manifest_id",
        "manifest_case_id",
        "manifest_package_id",
        "manifest_role",
        "manifest_evidence_version_id",
        "manifest_content_hash",
    )
    assert get_type_hints(policy.CopyableOaAttachmentEvidence) == {
        "evidence_version": EvidenceVersionResult,
        "manifest_id": str,
        "manifest_case_id": str,
        "manifest_package_id": str,
        "manifest_role": str,
        "manifest_evidence_version_id": str,
        "manifest_content_hash": str,
    }

    signature = inspect.signature(policy.require_copyable_oa_attachment_combination)
    assert tuple(signature.parameters) == ("case_id", "package_id", "attachments")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(policy.require_copyable_oa_attachment_combination) == {
        "case_id": str,
        "package_id": str,
        "attachments": tuple[policy.CopyableOaAttachmentEvidence, ...],
        "return": type(None),
    }
    assert "DocAttachment" not in inspect.getsource(
        policy.require_copyable_oa_attachment_combination
    )
    assert "file_name" not in inspect.getsource(policy.require_copyable_oa_attachment_combination)


def test_copyable_oa_accepts_exact_structured_singletons_and_repeatable_files() -> None:
    attachments = _required_combination() + (
        _attachment("comparison", "OA_AMENDMENT_COMPARISON"),
        _attachment("proof-1", "OA_OTHER_PROOF"),
        _attachment("proof-2", "OA_OTHER_PROOF"),
        _attachment("additional-1", "OA_ADDITIONAL_FILE"),
        _attachment("additional-2", "OA_ADDITIONAL_FILE"),
    )

    result = _policy().require_copyable_oa_attachment_combination(
        case_id=CASE_ID,
        package_id=PACKAGE_ID,
        attachments=attachments,
    )

    assert result is None


@pytest.mark.parametrize(
    ("state", "is_final"),
    (
        (EvidenceVersionState.DRAFT, False),
        (EvidenceVersionState.FINAL, True),
    ),
)
def test_copyable_oa_accepts_each_exact_promoted_state(
    state: EvidenceVersionState,
    is_final: bool,
) -> None:
    attachments = tuple(
        replace(
            attachment,
            evidence_version=replace(
                attachment.evidence_version,
                state=state,
                is_final=is_final,
            ),
        )
        for attachment in _required_combination()
    )

    result = _policy().require_copyable_oa_attachment_combination(
        case_id=CASE_ID,
        package_id=PACKAGE_ID,
        attachments=attachments,
    )

    assert result is None


@pytest.mark.parametrize(
    ("build_attachments", "code"),
    [
        (lambda: (), "OA_COPYABLE_STATEMENT_WORD_REQUIRED"),
        (
            lambda: (_attachment("claims", "OA_MODIFIED_CLAIMS"),),
            "OA_COPYABLE_STATEMENT_WORD_REQUIRED",
        ),
        (
            lambda: (_attachment("statement", "OA_STATEMENT_WORD"),),
            "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED",
        ),
        (
            lambda: (
                _attachment("statement-1", "OA_STATEMENT_WORD"),
                _attachment("statement-2", "OA_STATEMENT_WORD"),
                _attachment("claims", "OA_MODIFIED_CLAIMS"),
            ),
            "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS",
        ),
        (
            lambda: (
                _attachment("statement", "OA_STATEMENT_WORD"),
                _attachment("claims-1", "OA_MODIFIED_CLAIMS"),
                _attachment("claims-2", "OA_MODIFIED_CLAIMS"),
            ),
            "OA_COPYABLE_MULTIPLE_MODIFIED_CLAIMS",
        ),
        (
            lambda: _required_combination()
            + (
                _attachment("comparison-1", "OA_AMENDMENT_COMPARISON"),
                _attachment("comparison-2", "OA_AMENDMENT_COMPARISON"),
            ),
            "OA_COPYABLE_MULTIPLE_COMPARISON_PAGES",
        ),
        (
            lambda: _required_combination()
            + (_attachment("statement-pdf", "OA_STATEMENT_PDF"),),
            "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED",
        ),
    ],
)
def test_copyable_oa_rejects_missing_excess_or_unknown_manifest_roles(
    build_attachments: Callable[[], tuple[object, ...]],
    code: str,
) -> None:
    _assert_rejected(code, attachments=build_attachments())


@pytest.mark.parametrize(
    ("build_attachments", "code"),
    [
        (
            lambda: _required_combination()
            + (
                _attachment(
                    "statement-word",
                    "OA_OTHER_PROOF",
                    manifest_id="manifest-proof",
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE",
        ),
        (
            lambda: _required_combination()
            + (
                _attachment(
                    "proof",
                    "OA_OTHER_PROOF",
                    manifest_id="manifest-statement-word",
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_DUPLICATE_MANIFEST",
        ),
    ],
)
def test_copyable_oa_rejects_duplicate_version_or_manifest_identity(
    build_attachments: Callable[[], tuple[object, ...]],
    code: str,
) -> None:
    _assert_rejected(code, attachments=build_attachments())


@pytest.mark.parametrize(
    ("build_attachment", "code"),
    [
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                case_id=OTHER_CASE_ID,
            ),
            "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                package_id=OTHER_PACKAGE_ID,
            ),
            "OA_COPYABLE_ATTACHMENT_PACKAGE_MISMATCH",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence(
                    "proof",
                    role=EvidenceRole.RAW_ATTACHMENT,
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_NOT_STRUCTURED",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence("proof", is_current=False),
            ),
            "OA_COPYABLE_ATTACHMENT_NOT_CURRENT",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence(
                    "proof",
                    review_state=EvidenceReviewState.PENDING,
                    reviewer_id=None,
                    reviewed_at=None,
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_NOT_APPROVED",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence("proof", reviewer_id=CREATOR_ID),
            ),
            "OA_COPYABLE_ATTACHMENT_NOT_INDEPENDENTLY_REVIEWED",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence(
                    "proof",
                    reviewed_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_NOT_INDEPENDENTLY_REVIEWED",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                evidence=_evidence(
                    "proof",
                    state=EvidenceVersionState.DRAFT,
                    is_final=True,
                ),
            ),
            "OA_COPYABLE_ATTACHMENT_STATE_MISMATCH",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                manifest_evidence_version_id="other-version",
            ),
            "OA_COPYABLE_ATTACHMENT_LINK_MISMATCH",
        ),
        (
            lambda: _attachment(
                "proof",
                "OA_OTHER_PROOF",
                manifest_content_hash=f"sha256:{'b' * 64}",
            ),
            "OA_COPYABLE_ATTACHMENT_HASH_MISMATCH",
        ),
    ],
)
def test_copyable_oa_rejects_untrusted_version_or_manifest_authority(
    build_attachment: Callable[[], object],
    code: str,
) -> None:
    _assert_rejected(
        code,
        attachments=_required_combination() + (build_attachment(),),
    )


@pytest.mark.parametrize(
    ("case_id", "package_id", "as_list"),
    [
        ("", PACKAGE_ID, False),
        (" case ", PACKAGE_ID, False),
        (CASE_ID, "", False),
        (CASE_ID, " package ", False),
        (CASE_ID, PACKAGE_ID, True),
    ],
)
def test_copyable_oa_rejects_malformed_context(
    case_id: str,
    package_id: str,
    as_list: bool,
) -> None:
    attachments: object = _required_combination()
    if as_list:
        attachments = list(attachments)
    _assert_rejected(
        "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT",
        case_id=case_id,
        package_id=package_id,
        attachments=attachments,
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "manifest_id",
        "manifest_case_id",
        "manifest_package_id",
        "manifest_role",
        "manifest_evidence_version_id",
        "manifest_content_hash",
    ),
)
def test_copyable_oa_rejects_malformed_manifest_dto(field_name: str) -> None:
    attachment = replace(
        _attachment("proof", "OA_OTHER_PROOF"),
        **{field_name: ""},
    )

    _assert_rejected(
        "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT",
        attachments=_required_combination() + (attachment,),
    )
