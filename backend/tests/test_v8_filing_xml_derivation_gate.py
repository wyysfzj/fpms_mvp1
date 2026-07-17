from __future__ import annotations

import importlib
import inspect
from datetime import datetime
from enum import Enum
from typing import get_type_hints

import pytest

from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocumentEvidenceDerivation, DocumentEvidenceVersion

CASE_ID = "00000000-0000-0000-0000-000000000001"
LINEAGE_KEY = "filing-main"
CREATOR_ID = "00000000-0000-0000-0000-000000000002"
REVIEWER_ID = "00000000-0000-0000-0000-000000000003"
REVIEWED_AT = datetime(2026, 7, 14, 9, 30)


def _policy() -> object:
    return importlib.import_module("app.modules.documents.evidence_policy")


def _version(
    *,
    evidence_version_id: str,
    role: str,
    case_id: str = CASE_ID,
    lineage_key: str = LINEAGE_KEY,
    creator_id: str = CREATOR_ID,
    review_state: str = EvidenceReviewState.APPROVED.value,
    reviewer_id: str | None = REVIEWER_ID,
    reviewed_at: datetime | None = REVIEWED_AT,
    current: bool = False,
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=evidence_version_id,
        case_id=case_id,
        document_id=f"document-{evidence_version_id}",
        attachment_id=f"attachment-{evidence_version_id}",
        lineage_key=lineage_key,
        role=role,
        version_number=1,
        state=EvidenceVersionState.FINAL.value,
        creator_id=creator_id,
        review_state=review_state,
        reviewer_id=reviewer_id,
        reviewed_at=reviewed_at,
        final_submitted_at=None,
        content_hash=f"sha256:{'a' * 64}",
        current_identity_key=f"{case_id}|{lineage_key}" if current else None,
    )


def _source(**overrides: object) -> DocumentEvidenceVersion:
    values: dict[str, object] = {
        "evidence_version_id": "source-word",
        "role": EvidenceRole.FILING_FULL_WORD.value,
        "current": True,
    }
    values.update(overrides)
    return _version(**values)  # type: ignore[arg-type]


def _target(
    role: str = EvidenceRole.EXTERNAL_XML_PACKAGE.value,
    **overrides: object,
) -> DocumentEvidenceVersion:
    values: dict[str, object] = {
        "evidence_version_id": "target-xml",
        "role": role,
    }
    values.update(overrides)
    return _version(**values)  # type: ignore[arg-type]


def _derivation(
    source: DocumentEvidenceVersion,
    target: DocumentEvidenceVersion,
    *,
    case_id: str = CASE_ID,
    parent_evidence_version_id: str | None = None,
    child_evidence_version_id: str | None = None,
) -> DocumentEvidenceDerivation:
    return DocumentEvidenceDerivation(
        id="derivation-xml",
        case_id=case_id,
        parent_evidence_version_id=parent_evidence_version_id or source.id,
        child_evidence_version_id=child_evidence_version_id or target.id,
        derivation_type=EvidenceDerivationType.FORMAT_CONVERSION.value,
        actor_id="00000000-0000-0000-0000-000000000004",
        derived_at=datetime(2026, 7, 14, 10),
        source_snapshot='{"conversion":"external"}',
    )


def _assert_rejected(
    expected_code: str,
    *,
    source: DocumentEvidenceVersion | None = None,
    target: DocumentEvidenceVersion | None = None,
    derivation: DocumentEvidenceDerivation | None = None,
    case_id: str = CASE_ID,
) -> None:
    policy = _policy()
    source = source or _source()
    target = target or _target()
    error_type = policy.FilingXmlDerivationPolicyError
    with pytest.raises(error_type) as caught:
        policy.require_filing_xml_reviewed_word_source(
            case_id=case_id,
            source_word=source,
            xml_evidence=target,
            derivation=derivation or _derivation(source, target, case_id=case_id or CASE_ID),
        )

    assert caught.value.code.value == expected_code
    assert str(caught.value) == expected_code


def test_public_policy_contract_is_exact() -> None:
    policy = _policy()

    assert issubclass(policy.FilingXmlDerivationErrorCode, str)
    assert issubclass(policy.FilingXmlDerivationErrorCode, Enum)
    assert tuple((member.name, member.value) for member in policy.FilingXmlDerivationErrorCode) == (
        ("INVALID_CONTEXT", "FILING_XML_DERIVATION_INVALID_CONTEXT"),
        ("SOURCE_NOT_FILING_WORD", "FILING_XML_SOURCE_NOT_FILING_WORD"),
        ("SOURCE_NOT_CURRENT", "FILING_XML_SOURCE_NOT_CURRENT"),
        ("SOURCE_NOT_APPROVED", "FILING_XML_SOURCE_NOT_APPROVED"),
        ("SOURCE_NOT_INDEPENDENTLY_REVIEWED", "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED"),
        ("TARGET_NOT_XML", "FILING_XML_TARGET_NOT_XML"),
        ("CASE_MISMATCH", "FILING_XML_DERIVATION_CASE_MISMATCH"),
        ("LINEAGE_MISMATCH", "FILING_XML_DERIVATION_LINEAGE_MISMATCH"),
        ("DERIVATION_MISMATCH", "FILING_XML_DERIVATION_EDGE_MISMATCH"),
    )

    signature = inspect.signature(policy.require_filing_xml_reviewed_word_source)
    assert tuple(signature.parameters) == (
        "case_id",
        "source_word",
        "xml_evidence",
        "derivation",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(policy.require_filing_xml_reviewed_word_source) == {
        "case_id": str,
        "source_word": DocumentEvidenceVersion,
        "xml_evidence": DocumentEvidenceVersion,
        "derivation": DocumentEvidenceDerivation,
        "return": type(None),
    }

    error = policy.FilingXmlDerivationPolicyError(
        policy.FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT
    )
    assert error.code is policy.FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT
    assert str(error) == "FILING_XML_SOURCE_NOT_CURRENT"
    with pytest.raises(AttributeError):
        error.code = policy.FilingXmlDerivationErrorCode.INVALID_CONTEXT


@pytest.mark.parametrize(
    "xml_role",
    [
        EvidenceRole.EXTERNAL_XML_PACKAGE.value,
        EvidenceRole.SUBMITTED_XML.value,
    ],
)
def test_xml_zip_and_final_xml_accept_only_the_current_independently_reviewed_word_lineage(
    xml_role: str,
) -> None:
    policy = _policy()
    source = _source()
    target = _target(xml_role)
    derivation = _derivation(source, target)
    before = (
        source.current_identity_key,
        source.review_state,
        source.reviewer_id,
        source.reviewed_at,
        target.case_id,
        target.lineage_key,
        target.role,
        derivation.parent_evidence_version_id,
        derivation.child_evidence_version_id,
    )

    result = policy.require_filing_xml_reviewed_word_source(
        case_id=CASE_ID,
        source_word=source,
        xml_evidence=target,
        derivation=derivation,
    )

    assert result is None
    assert (
        source.current_identity_key,
        source.review_state,
        source.reviewer_id,
        source.reviewed_at,
        target.case_id,
        target.lineage_key,
        target.role,
        derivation.parent_evidence_version_id,
        derivation.child_evidence_version_id,
    ) == before


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (
            _source(role=EvidenceRole.TRACKED_REVISED_WORD.value),
            "FILING_XML_SOURCE_NOT_FILING_WORD",
        ),
        (_source(current=False), "FILING_XML_SOURCE_NOT_CURRENT"),
        (
            _source(
                current=False,
                review_state=EvidenceReviewState.PENDING.value,
                reviewer_id=None,
                reviewed_at=None,
            ),
            "FILING_XML_SOURCE_NOT_CURRENT",
        ),
        (
            _source(
                review_state=EvidenceReviewState.PENDING.value, reviewer_id=None, reviewed_at=None
            ),
            "FILING_XML_SOURCE_NOT_APPROVED",
        ),
        (
            _source(review_state=EvidenceReviewState.REJECTED.value),
            "FILING_XML_SOURCE_NOT_APPROVED",
        ),
        (
            _source(reviewer_id=CREATOR_ID),
            "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED",
        ),
        (
            _source(reviewer_id=None),
            "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED",
        ),
        (
            _source(reviewed_at=None),
            "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED",
        ),
    ],
)
def test_source_gate_fails_closed_before_xml_can_be_treated_as_derived(
    source: DocumentEvidenceVersion,
    code: str,
) -> None:
    _assert_rejected(code, source=source)


@pytest.mark.parametrize(
    ("case_id", "source", "target", "code"),
    [
        ("", _source(), _target(), "FILING_XML_DERIVATION_INVALID_CONTEXT"),
        (
            CASE_ID,
            _source(case_id="case-other", current=True),
            _target(),
            "FILING_XML_DERIVATION_CASE_MISMATCH",
        ),
        (CASE_ID, _source(), _target(case_id="case-other"), "FILING_XML_DERIVATION_CASE_MISMATCH"),
        (
            CASE_ID,
            _source(),
            _target(lineage_key="other-lineage"),
            "FILING_XML_DERIVATION_LINEAGE_MISMATCH",
        ),
        (
            CASE_ID,
            _source(lineage_key=" filing-main", current=True),
            _target(),
            "FILING_XML_DERIVATION_INVALID_CONTEXT",
        ),
    ],
)
def test_case_and_lineage_guards_fail_closed(
    case_id: str,
    source: DocumentEvidenceVersion,
    target: DocumentEvidenceVersion,
    code: str,
) -> None:
    _assert_rejected(code, case_id=case_id, source=source, target=target)


@pytest.mark.parametrize(
    "role",
    [
        EvidenceRole.FILING_COMPONENT.value,
        EvidenceRole.OFFICIAL_FINAL_PDF.value,
        "UNKNOWN_XML_ROLE",
    ],
)
def test_non_xml_target_roles_are_rejected(role: str) -> None:
    _assert_rejected("FILING_XML_TARGET_NOT_XML", target=_target(role))


@pytest.mark.parametrize("mismatch", ["case", "parent", "child"])
def test_derivation_edge_must_connect_the_reviewed_word_to_the_xml(mismatch: str) -> None:
    source = _source()
    target = _target()
    derivation = _derivation(
        source,
        target,
        case_id="case-other" if mismatch == "case" else CASE_ID,
        parent_evidence_version_id="other-parent" if mismatch == "parent" else None,
        child_evidence_version_id="other-child" if mismatch == "child" else None,
    )

    _assert_rejected(
        "FILING_XML_DERIVATION_EDGE_MISMATCH",
        source=source,
        target=target,
        derivation=derivation,
    )
