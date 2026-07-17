from __future__ import annotations

import importlib
import inspect
from enum import Enum
from typing import get_type_hints

import pytest

from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceVersionState,
)
from app.modules.documents.models import DocumentEvidenceVersion

CASE_ID = "00000000-0000-0000-0000-000000000001"
OTHER_CASE_ID = "00000000-0000-0000-0000-000000000002"
CREATOR_ID = "00000000-0000-0000-0000-000000000003"


def _policy() -> object:
    return importlib.import_module("app.modules.documents.evidence_policy")


def _version(
    evidence_version_id: str,
    role: str,
    *,
    case_id: str = CASE_ID,
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=evidence_version_id,
        case_id=case_id,
        document_id=f"document-{evidence_version_id}",
        attachment_id=f"attachment-{evidence_version_id}",
        lineage_key=f"oa-reply-{evidence_version_id}",
        role=role,
        version_number=1,
        state=EvidenceVersionState.FINAL.value,
        creator_id=CREATOR_ID,
        review_state=EvidenceReviewState.PENDING.value,
        reviewer_id=None,
        reviewed_at=None,
        final_submitted_at=None,
        content_hash=f"sha256:{'a' * 64}",
        current_identity_key=None,
    )


def _required_combination() -> tuple[DocumentEvidenceVersion, ...]:
    return (
        _version("statement-word", "OA_STATEMENT_WORD"),
        _version("modified-claims", "OA_MODIFIED_CLAIMS"),
    )


def _assert_rejected(
    expected_code: str,
    *,
    case_id: str = CASE_ID,
    attachments: object,
) -> None:
    policy = _policy()
    with pytest.raises(policy.CopyableOaAttachmentPolicyError) as caught:
        policy.require_copyable_oa_attachment_combination(
            case_id=case_id,
            attachments=attachments,
        )

    assert caught.value.code.value == expected_code
    assert str(caught.value) == expected_code


def test_public_policy_contract_is_exact() -> None:
    policy = _policy()

    assert issubclass(policy.CopyableOaAttachmentErrorCode, str)
    assert issubclass(policy.CopyableOaAttachmentErrorCode, Enum)
    assert tuple(
        (member.name, member.value) for member in policy.CopyableOaAttachmentErrorCode
    ) == (
        ("INVALID_CONTEXT", "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT"),
        ("CASE_MISMATCH", "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH"),
        ("DUPLICATE_EVIDENCE", "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE"),
        ("ROLE_NOT_PERMITTED", "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED"),
        ("STATEMENT_WORD_REQUIRED", "OA_COPYABLE_STATEMENT_WORD_REQUIRED"),
        ("MULTIPLE_STATEMENT_WORDS", "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS"),
        ("MODIFIED_CLAIMS_REQUIRED", "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED"),
        ("MULTIPLE_COMPARISON_PAGES", "OA_COPYABLE_MULTIPLE_COMPARISON_PAGES"),
    )

    signature = inspect.signature(policy.require_copyable_oa_attachment_combination)
    assert tuple(signature.parameters) == ("case_id", "attachments")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(policy.require_copyable_oa_attachment_combination) == {
        "case_id": str,
        "attachments": tuple[DocumentEvidenceVersion, ...],
        "return": type(None),
    }

    error = policy.CopyableOaAttachmentPolicyError(
        policy.CopyableOaAttachmentErrorCode.ROLE_NOT_PERMITTED
    )
    assert error.code is policy.CopyableOaAttachmentErrorCode.ROLE_NOT_PERMITTED
    assert str(error) == "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED"
    with pytest.raises(AttributeError):
        error.code = policy.CopyableOaAttachmentErrorCode.INVALID_CONTEXT


def test_copyable_oa_accepts_only_the_frozen_structured_attachment_combination() -> None:
    policy = _policy()
    attachments = (
        _version("statement-word", "OA_STATEMENT_WORD"),
        _version("modified-claims-1", "OA_MODIFIED_CLAIMS"),
        _version("modified-claims-2", "OA_MODIFIED_CLAIMS"),
        _version("comparison", "OA_AMENDMENT_COMPARISON"),
        _version("proof-1", "OA_OTHER_PROOF"),
        _version("proof-2", "OA_OTHER_PROOF"),
        _version("additional-1", "OA_ADDITIONAL_FILE"),
        _version("additional-2", "OA_ADDITIONAL_FILE"),
    )
    before = tuple((item.id, item.case_id, item.role) for item in attachments)

    result = policy.require_copyable_oa_attachment_combination(
        case_id=CASE_ID,
        attachments=attachments,
    )

    assert result is None
    assert tuple((item.id, item.case_id, item.role) for item in attachments) == before


@pytest.mark.parametrize(
    ("attachments", "code"),
    [
        ((), "OA_COPYABLE_STATEMENT_WORD_REQUIRED"),
        (
            (_version("claims", "OA_MODIFIED_CLAIMS"),),
            "OA_COPYABLE_STATEMENT_WORD_REQUIRED",
        ),
        (
            (_version("statement", "OA_STATEMENT_WORD"),),
            "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED",
        ),
        (
            (
                _version("statement-1", "OA_STATEMENT_WORD"),
                _version("statement-2", "OA_STATEMENT_WORD"),
                _version("claims", "OA_MODIFIED_CLAIMS"),
            ),
            "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS",
        ),
        (
            _required_combination()
            + (
                _version("comparison-1", "OA_AMENDMENT_COMPARISON"),
                _version("comparison-2", "OA_AMENDMENT_COMPARISON"),
            ),
            "OA_COPYABLE_MULTIPLE_COMPARISON_PAGES",
        ),
        (
            _required_combination() + (_version("statement-pdf", "OA_STATEMENT_PDF"),),
            "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED",
        ),
        (
            _required_combination() + (_version("raw", "RAW_ATTACHMENT"),),
            "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED",
        ),
    ],
)
def test_copyable_oa_rejects_missing_repeated_or_non_structured_roles(
    attachments: tuple[DocumentEvidenceVersion, ...],
    code: str,
) -> None:
    _assert_rejected(code, attachments=attachments)


def test_copyable_oa_rejects_duplicate_evidence_identity() -> None:
    statement, claims = _required_combination()
    duplicate = _version(statement.id, "OA_OTHER_PROOF")

    _assert_rejected(
        "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE",
        attachments=(statement, claims, duplicate),
    )


def test_copyable_oa_rejects_cross_case_attachment() -> None:
    _assert_rejected(
        "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH",
        attachments=_required_combination()
        + (_version("proof", "OA_OTHER_PROOF", case_id=OTHER_CASE_ID),),
    )


@pytest.mark.parametrize(
    ("case_id", "attachments"),
    [
        ("", _required_combination()),
        (" case ", _required_combination()),
        (CASE_ID, list(_required_combination())),
        (CASE_ID, (_version("", "OA_OTHER_PROOF"),)),
        (CASE_ID, (_version("statement", " OA_STATEMENT_WORD"),)),
    ],
)
def test_copyable_oa_rejects_malformed_context(
    case_id: str,
    attachments: object,
) -> None:
    _assert_rejected(
        "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT",
        case_id=case_id,
        attachments=attachments,
    )
