from __future__ import annotations

import inspect
from datetime import datetime, timezone
from enum import Enum
from itertools import combinations
from typing import Any, get_type_hints

import pytest

from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.evidence_policy import (
    FilingXmlDerivationErrorCode,
    FilingXmlDerivationPolicyError,
    require_filing_xml_reviewed_word_source,
)
from app.modules.documents.models import DocumentEvidenceDerivation, DocumentEvidenceVersion

CASE_ID = "00000000-0000-0000-0000-000000000001"
OTHER_CASE_ID = "00000000-0000-0000-0000-000000000009"
LINEAGE_KEY = "filing-main"
CREATOR_ID = "00000000-0000-0000-0000-000000000002"
REVIEWER_ID = "00000000-0000-0000-0000-000000000003"
REVIEWED_AT = datetime(2026, 7, 22, 9, 30)


class ExpectedErrorCode(str, Enum):
    INVALID_CONTEXT = "FILING_XML_DERIVATION_INVALID_CONTEXT"
    SOURCE_NOT_FILING_WORD = "FILING_XML_SOURCE_NOT_FILING_WORD"
    SOURCE_NOT_CURRENT = "FILING_XML_SOURCE_NOT_CURRENT"
    SOURCE_NOT_APPROVED = "FILING_XML_SOURCE_NOT_APPROVED"
    SOURCE_NOT_INDEPENDENTLY_REVIEWED = "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED"
    TARGET_NOT_XML = "FILING_XML_TARGET_NOT_XML"
    CASE_MISMATCH = "FILING_XML_DERIVATION_CASE_MISMATCH"
    LINEAGE_MISMATCH = "FILING_XML_DERIVATION_LINEAGE_MISMATCH"
    PATH_SHAPE_MISMATCH = "FILING_XML_DERIVATION_PATH_SHAPE_MISMATCH"
    EDGE_MISMATCH = "FILING_XML_DERIVATION_EDGE_MISMATCH"
    TYPE_MISMATCH = "FILING_XML_DERIVATION_TYPE_MISMATCH"


ERROR_CODES = tuple(ExpectedErrorCode)


def _version(
    evidence_version_id: str,
    role: str,
    *,
    case_id: str = CASE_ID,
    lineage_key: str = LINEAGE_KEY,
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
        creator_id=CREATOR_ID,
        review_state=EvidenceReviewState.APPROVED.value,
        reviewer_id=REVIEWER_ID,
        reviewed_at=REVIEWED_AT,
        final_submitted_at=None,
        content_hash=f"sha256:{'a' * 64}",
        current_identity_key=f"{case_id}|{lineage_key}" if current else None,
    )


def _derivation(
    derivation_id: str,
    parent: DocumentEvidenceVersion,
    child: DocumentEvidenceVersion,
    derivation_type: str,
) -> DocumentEvidenceDerivation:
    return DocumentEvidenceDerivation(
        id=derivation_id,
        case_id=CASE_ID,
        parent_evidence_version_id=parent.id,
        child_evidence_version_id=child.id,
        derivation_type=derivation_type,
        actor_id="00000000-0000-0000-0000-000000000004",
        derived_at=datetime(2026, 7, 22, 10),
        source_snapshot='{"conversion":"external"}',
    )


def _valid_path(path: str) -> dict[str, Any]:
    source = _version(
        "source-word",
        EvidenceRole.FILING_FULL_WORD.value,
        current=True,
    )
    target_role = (
        EvidenceRole.EXTERNAL_XML_PACKAGE.value
        if path == "external"
        else EvidenceRole.SUBMITTED_XML.value
    )
    target = _version("target-xml", target_role)
    parent = (
        None
        if path == "external"
        else _version("parent-xml", EvidenceRole.EXTERNAL_XML_PACKAGE.value)
    )
    source_child = target if parent is None else parent
    source_derivation = _derivation(
        "source-derivation",
        source,
        source_child,
        EvidenceDerivationType.FORMAT_CONVERSION.value,
    )
    submission_derivation = (
        None
        if parent is None
        else _derivation(
            "submission-derivation",
            parent,
            target,
            EvidenceDerivationType.EXTERNAL_SUBMISSION.value,
        )
    )
    return {
        "case_id": CASE_ID,
        "source_word": source,
        "xml_evidence": target,
        "parent_xml_evidence": parent,
        "source_derivation": source_derivation,
        "submission_derivation": submission_derivation,
    }


def _apply_defect(
    arguments: dict[str, Any],
    code: ExpectedErrorCode,
    path: str,
) -> None:
    if code is ExpectedErrorCode.INVALID_CONTEXT:
        arguments["case_id"] = ""
    elif code is ExpectedErrorCode.SOURCE_NOT_FILING_WORD:
        arguments["source_word"].role = EvidenceRole.TRACKED_REVISED_WORD.value
    elif code is ExpectedErrorCode.SOURCE_NOT_CURRENT:
        arguments["source_word"].current_identity_key = None
    elif code is ExpectedErrorCode.SOURCE_NOT_APPROVED:
        arguments["source_word"].review_state = EvidenceReviewState.PENDING.value
    elif code is ExpectedErrorCode.SOURCE_NOT_INDEPENDENTLY_REVIEWED:
        arguments["source_word"].reviewer_id = CREATOR_ID
    elif code is ExpectedErrorCode.TARGET_NOT_XML:
        arguments["xml_evidence"].role = EvidenceRole.OFFICIAL_FINAL_PDF.value
    elif code is ExpectedErrorCode.CASE_MISMATCH:
        arguments["xml_evidence"].case_id = OTHER_CASE_ID
    elif code is ExpectedErrorCode.LINEAGE_MISMATCH:
        arguments["xml_evidence"].lineage_key = "other-lineage"
    elif code is ExpectedErrorCode.PATH_SHAPE_MISMATCH:
        if path == "external":
            arguments["parent_xml_evidence"] = _version(
                "unexpected-parent",
                EvidenceRole.EXTERNAL_XML_PACKAGE.value,
            )
        else:
            arguments["parent_xml_evidence"] = None
    elif code is ExpectedErrorCode.EDGE_MISMATCH:
        derivation_name = "source_derivation" if path == "external" else "submission_derivation"
        arguments[derivation_name].child_evidence_version_id = "wrong-child"
    elif code is ExpectedErrorCode.TYPE_MISMATCH:
        derivation_name = "source_derivation" if path == "external" else "submission_derivation"
        arguments[derivation_name].derivation_type = EvidenceDerivationType.REVISION.value
    else:  # pragma: no cover - the frozen matrix enumerates every member
        raise AssertionError(f"unsupported defect: {code}")


def _assert_rejected(
    expected: ExpectedErrorCode,
    arguments: dict[str, Any],
) -> None:
    with pytest.raises(FilingXmlDerivationPolicyError) as caught:
        require_filing_xml_reviewed_word_source(**arguments)

    assert caught.value.code.name == expected.name
    assert str(caught.value) == expected.value


def test_public_policy_contract_is_exact() -> None:
    assert issubclass(FilingXmlDerivationErrorCode, str)
    assert issubclass(FilingXmlDerivationErrorCode, Enum)
    assert tuple((member.name, member.value) for member in FilingXmlDerivationErrorCode) == (
        ("INVALID_CONTEXT", "FILING_XML_DERIVATION_INVALID_CONTEXT"),
        ("SOURCE_NOT_FILING_WORD", "FILING_XML_SOURCE_NOT_FILING_WORD"),
        ("SOURCE_NOT_CURRENT", "FILING_XML_SOURCE_NOT_CURRENT"),
        ("SOURCE_NOT_APPROVED", "FILING_XML_SOURCE_NOT_APPROVED"),
        (
            "SOURCE_NOT_INDEPENDENTLY_REVIEWED",
            "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED",
        ),
        ("TARGET_NOT_XML", "FILING_XML_TARGET_NOT_XML"),
        ("CASE_MISMATCH", "FILING_XML_DERIVATION_CASE_MISMATCH"),
        ("LINEAGE_MISMATCH", "FILING_XML_DERIVATION_LINEAGE_MISMATCH"),
        ("PATH_SHAPE_MISMATCH", "FILING_XML_DERIVATION_PATH_SHAPE_MISMATCH"),
        ("EDGE_MISMATCH", "FILING_XML_DERIVATION_EDGE_MISMATCH"),
        ("TYPE_MISMATCH", "FILING_XML_DERIVATION_TYPE_MISMATCH"),
    )

    signature = inspect.signature(require_filing_xml_reviewed_word_source)
    assert tuple(signature.parameters) == (
        "case_id",
        "source_word",
        "xml_evidence",
        "parent_xml_evidence",
        "source_derivation",
        "submission_derivation",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(require_filing_xml_reviewed_word_source) == {
        "case_id": str,
        "source_word": DocumentEvidenceVersion,
        "xml_evidence": DocumentEvidenceVersion,
        "parent_xml_evidence": DocumentEvidenceVersion | None,
        "source_derivation": DocumentEvidenceDerivation,
        "submission_derivation": DocumentEvidenceDerivation | None,
        "return": type(None),
    }

    error = FilingXmlDerivationPolicyError(FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT)
    assert error.code is FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT
    assert str(error) == "FILING_XML_SOURCE_NOT_CURRENT"
    with pytest.raises(AttributeError):
        error.code = FilingXmlDerivationErrorCode.INVALID_CONTEXT


@pytest.mark.parametrize("path", ["external", "submitted"])
def test_both_exact_paths_are_read_only(path: str) -> None:
    arguments = _valid_path(path)
    objects = tuple(
        value
        for value in arguments.values()
        if type(value) in (DocumentEvidenceVersion, DocumentEvidenceDerivation)
    )
    before = tuple(dict(value.__dict__) for value in objects)

    assert require_filing_xml_reviewed_word_source(**arguments) is None

    assert tuple(dict(value.__dict__) for value in objects) == before


@pytest.mark.parametrize("path", ["external", "submitted"])
@pytest.mark.parametrize("code", ERROR_CODES)
def test_each_frozen_error_category_is_reachable(
    path: str,
    code: ExpectedErrorCode,
) -> None:
    arguments = _valid_path(path)
    _apply_defect(arguments, code, path)

    _assert_rejected(code, arguments)


PAIRWISE_PRECEDENCE = tuple(combinations(ERROR_CODES, 2))


@pytest.mark.parametrize("path", ["external", "submitted"])
@pytest.mark.parametrize(("earlier", "later"), PAIRWISE_PRECEDENCE)
def test_all_55_pairwise_overlaps_use_first_match_precedence(
    path: str,
    earlier: ExpectedErrorCode,
    later: ExpectedErrorCode,
) -> None:
    arguments = _valid_path(path)
    _apply_defect(arguments, later, path)
    _apply_defect(arguments, earlier, path)

    _assert_rejected(earlier, arguments)


@pytest.mark.parametrize(
    ("path", "defects", "expected"),
    [
        (
            "external",
            (
                ExpectedErrorCode.SOURCE_NOT_CURRENT,
                ExpectedErrorCode.CASE_MISMATCH,
                ExpectedErrorCode.PATH_SHAPE_MISMATCH,
                ExpectedErrorCode.TYPE_MISMATCH,
            ),
            ExpectedErrorCode.SOURCE_NOT_CURRENT,
        ),
        (
            "submitted",
            (
                ExpectedErrorCode.SOURCE_NOT_APPROVED,
                ExpectedErrorCode.LINEAGE_MISMATCH,
                ExpectedErrorCode.EDGE_MISMATCH,
                ExpectedErrorCode.TYPE_MISMATCH,
            ),
            ExpectedErrorCode.SOURCE_NOT_APPROVED,
        ),
    ],
)
def test_three_or_more_defects_are_transitively_ordered_on_both_paths(
    path: str,
    defects: tuple[ExpectedErrorCode, ...],
    expected: ExpectedErrorCode,
) -> None:
    arguments = _valid_path(path)
    for defect in reversed(defects):
        _apply_defect(arguments, defect, path)

    _assert_rejected(expected, arguments)


@pytest.mark.parametrize(
    ("argument_name", "invalid_value"),
    [
        ("case_id", None),
        ("source_word", object()),
        ("xml_evidence", object()),
        ("parent_xml_evidence", object()),
        ("source_derivation", object()),
        ("submission_derivation", object()),
    ],
)
def test_non_exact_required_or_present_optional_objects_are_invalid_context(
    argument_name: str,
    invalid_value: object,
) -> None:
    arguments = _valid_path("submitted")
    arguments[argument_name] = invalid_value

    _assert_rejected(ExpectedErrorCode.INVALID_CONTEXT, arguments)


@pytest.mark.parametrize(
    ("argument_name", "field_name"),
    [
        ("source_word", "id"),
        ("source_word", "case_id"),
        ("source_word", "lineage_key"),
        ("source_word", "creator_id"),
        ("xml_evidence", "id"),
        ("xml_evidence", "case_id"),
        ("xml_evidence", "lineage_key"),
        ("parent_xml_evidence", "id"),
        ("parent_xml_evidence", "case_id"),
        ("parent_xml_evidence", "lineage_key"),
        ("source_derivation", "id"),
        ("source_derivation", "case_id"),
        ("source_derivation", "parent_evidence_version_id"),
        ("source_derivation", "child_evidence_version_id"),
        ("submission_derivation", "id"),
        ("submission_derivation", "case_id"),
        ("submission_derivation", "parent_evidence_version_id"),
        ("submission_derivation", "child_evidence_version_id"),
    ],
)
def test_blank_required_object_identities_are_invalid_context(
    argument_name: str,
    field_name: str,
) -> None:
    arguments = _valid_path("submitted")
    setattr(arguments[argument_name], field_name, " ")

    _assert_rejected(ExpectedErrorCode.INVALID_CONTEXT, arguments)


@pytest.mark.parametrize("derivation_name", ["source_derivation", "submission_derivation"])
@pytest.mark.parametrize("invalid_type", ["", " ", None, 1])
def test_blank_or_non_string_derivation_type_is_invalid_context(
    derivation_name: str,
    invalid_type: object,
) -> None:
    arguments = _valid_path("submitted")
    arguments[derivation_name].derivation_type = invalid_type

    _assert_rejected(ExpectedErrorCode.INVALID_CONTEXT, arguments)


@pytest.mark.parametrize(
    ("reviewer_id", "reviewed_at"),
    [
        (None, REVIEWED_AT),
        ("", REVIEWED_AT),
        (" reviewer", REVIEWED_AT),
        (CREATOR_ID, REVIEWED_AT),
        (REVIEWER_ID, None),
        (REVIEWER_ID, datetime(2026, 7, 22, tzinfo=timezone.utc)),
    ],
)
def test_review_predicate_retains_ordinal_five(
    reviewer_id: object,
    reviewed_at: object,
) -> None:
    arguments = _valid_path("external")
    arguments["source_word"].reviewer_id = reviewer_id
    arguments["source_word"].reviewed_at = reviewed_at

    _assert_rejected(
        ExpectedErrorCode.SOURCE_NOT_INDEPENDENTLY_REVIEWED,
        arguments,
    )


@pytest.mark.parametrize(
    ("path", "argument_name"),
    [
        ("external", "parent_xml_evidence"),
        ("external", "submission_derivation"),
        ("submitted", "parent_xml_evidence"),
        ("submitted", "submission_derivation"),
    ],
)
def test_path_specific_nullability_is_path_shape_mismatch(
    path: str,
    argument_name: str,
) -> None:
    arguments = _valid_path(path)
    if path == "external":
        parent = _version("unexpected-parent", EvidenceRole.EXTERNAL_XML_PACKAGE.value)
        arguments[argument_name] = (
            parent
            if argument_name == "parent_xml_evidence"
            else _derivation(
                "unexpected-submission",
                parent,
                arguments["xml_evidence"],
                EvidenceDerivationType.EXTERNAL_SUBMISSION.value,
            )
        )
    else:
        arguments[argument_name] = None

    _assert_rejected(ExpectedErrorCode.PATH_SHAPE_MISMATCH, arguments)


def test_submitted_parent_role_is_path_shape_mismatch() -> None:
    arguments = _valid_path("submitted")
    arguments["parent_xml_evidence"].role = EvidenceRole.FILING_COMPONENT.value

    _assert_rejected(ExpectedErrorCode.PATH_SHAPE_MISMATCH, arguments)


@pytest.mark.parametrize(
    ("argument_name", "field_name"),
    [
        ("source_word", "case_id"),
        ("xml_evidence", "case_id"),
        ("parent_xml_evidence", "case_id"),
        ("source_derivation", "case_id"),
        ("submission_derivation", "case_id"),
    ],
)
def test_every_supplied_version_and_edge_case_participates_in_ordinal_seven(
    argument_name: str,
    field_name: str,
) -> None:
    arguments = _valid_path("submitted")
    setattr(arguments[argument_name], field_name, OTHER_CASE_ID)
    if argument_name == "source_word":
        arguments["source_word"].current_identity_key = f"{CASE_ID}|{LINEAGE_KEY}"

    _assert_rejected(ExpectedErrorCode.CASE_MISMATCH, arguments)


@pytest.mark.parametrize(
    "argument_name",
    ["xml_evidence", "parent_xml_evidence"],
)
def test_every_non_source_version_lineage_participates_in_ordinal_eight(
    argument_name: str,
) -> None:
    arguments = _valid_path("submitted")
    arguments[argument_name].lineage_key = "other-lineage"

    _assert_rejected(ExpectedErrorCode.LINEAGE_MISMATCH, arguments)


@pytest.mark.parametrize(
    ("path", "derivation_name", "field_name"),
    [
        ("external", "source_derivation", "parent_evidence_version_id"),
        ("external", "source_derivation", "child_evidence_version_id"),
        ("submitted", "source_derivation", "parent_evidence_version_id"),
        ("submitted", "source_derivation", "child_evidence_version_id"),
        ("submitted", "submission_derivation", "parent_evidence_version_id"),
        ("submitted", "submission_derivation", "child_evidence_version_id"),
    ],
)
def test_each_ordered_edge_identity_participates_in_ordinal_ten(
    path: str,
    derivation_name: str,
    field_name: str,
) -> None:
    arguments = _valid_path(path)
    setattr(arguments[derivation_name], field_name, "wrong-version")

    _assert_rejected(ExpectedErrorCode.EDGE_MISMATCH, arguments)


@pytest.mark.parametrize(
    ("path", "derivation_name"),
    [
        ("external", "source_derivation"),
        ("submitted", "source_derivation"),
        ("submitted", "submission_derivation"),
    ],
)
def test_exact_nonblank_wrong_derivation_type_is_ordinal_eleven(
    path: str,
    derivation_name: str,
) -> None:
    arguments = _valid_path(path)
    arguments[derivation_name].derivation_type = EvidenceDerivationType.REVISION.value

    _assert_rejected(ExpectedErrorCode.TYPE_MISMATCH, arguments)
