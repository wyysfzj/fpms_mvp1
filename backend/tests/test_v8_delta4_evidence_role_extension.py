from app.modules.documents.evidence_contracts import EvidenceRole
from app.modules.documents.evidence_workflow_service import (
    _EXTERNAL_SUBMISSION_ELIGIBLE_ROLES,
)

EXPECTED_FIRST_TEN = [
    ("FILING_FULL_WORD", "FILING_FULL_WORD"),
    ("TRACKED_REVISED_WORD", "TRACKED_REVISED_WORD"),
    ("FILING_COMPONENT", "FILING_COMPONENT"),
    ("EXTERNAL_XML_PACKAGE", "EXTERNAL_XML_PACKAGE"),
    ("OFFICIAL_SUBMISSION_LIST", "OFFICIAL_SUBMISSION_LIST"),
    ("OFFICIAL_FINAL_PDF", "OFFICIAL_FINAL_PDF"),
    ("SUBMITTED_XML", "SUBMITTED_XML"),
    ("OFFICIAL_RECEIPT", "OFFICIAL_RECEIPT"),
    ("CLIENT_LETTER_WORD", "CLIENT_LETTER_WORD"),
    ("RAW_ATTACHMENT", "RAW_ATTACHMENT"),
]

EXPECTED_SUFFIX = [
    ("GENERATED_ATTACHMENT", "GENERATED_ATTACHMENT"),
    ("OA_STRUCTURED_ATTACHMENT", "OA_STRUCTURED_ATTACHMENT"),
]

EXPECTED_EXTERNAL_SUBMISSION_ELIGIBLE_ROLES = {
    "FILING_FULL_WORD",
    "TRACKED_REVISED_WORD",
    "FILING_COMPONENT",
    "EXTERNAL_XML_PACKAGE",
    "OFFICIAL_SUBMISSION_LIST",
    "OFFICIAL_FINAL_PDF",
    "SUBMITTED_XML",
    "OFFICIAL_RECEIPT",
    "CLIENT_LETTER_WORD",
}


def test_delta4_evidence_roles_append_exact_non_submittable_suffix() -> None:
    actual_pairs = [(member.name, member.value) for member in EvidenceRole]

    assert actual_pairs[:10] == EXPECTED_FIRST_TEN
    assert actual_pairs[10:] == EXPECTED_SUFFIX
    assert len(actual_pairs) == 12
    assert len(set(actual_pairs)) == 12
    assert len(EvidenceRole.__members__) == 12

    new_values = {value for _, value in EXPECTED_SUFFIX}
    assert _EXTERNAL_SUBMISSION_ELIGIBLE_ROLES == EXPECTED_EXTERNAL_SUBMISSION_ELIGIBLE_ROLES
    assert _EXTERNAL_SUBMISSION_ELIGIBLE_ROLES.isdisjoint(new_values)
