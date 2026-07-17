from __future__ import annotations

from datetime import datetime
from enum import Enum

from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
)
from app.modules.documents.models import DocumentEvidenceDerivation, DocumentEvidenceVersion

__all__ = (
    "CopyableOaAttachmentErrorCode",
    "CopyableOaAttachmentPolicyError",
    "FilingXmlDerivationErrorCode",
    "FilingXmlDerivationPolicyError",
    "require_copyable_oa_attachment_combination",
    "require_filing_xml_reviewed_word_source",
)


_COPYABLE_OA_ATTACHMENT_ROLES = frozenset(
    {
        "OA_STATEMENT_WORD",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    }
)


class CopyableOaAttachmentErrorCode(str, Enum):
    INVALID_CONTEXT = "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT"
    CASE_MISMATCH = "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH"
    DUPLICATE_EVIDENCE = "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE"
    ROLE_NOT_PERMITTED = "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED"
    STATEMENT_WORD_REQUIRED = "OA_COPYABLE_STATEMENT_WORD_REQUIRED"
    MULTIPLE_STATEMENT_WORDS = "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS"
    MODIFIED_CLAIMS_REQUIRED = "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED"
    MULTIPLE_COMPARISON_PAGES = "OA_COPYABLE_MULTIPLE_COMPARISON_PAGES"


class CopyableOaAttachmentPolicyError(ValueError):
    def __init__(self, code: CopyableOaAttachmentErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> CopyableOaAttachmentErrorCode:
        return self._code


class FilingXmlDerivationErrorCode(str, Enum):
    INVALID_CONTEXT = "FILING_XML_DERIVATION_INVALID_CONTEXT"
    SOURCE_NOT_FILING_WORD = "FILING_XML_SOURCE_NOT_FILING_WORD"
    SOURCE_NOT_CURRENT = "FILING_XML_SOURCE_NOT_CURRENT"
    SOURCE_NOT_APPROVED = "FILING_XML_SOURCE_NOT_APPROVED"
    SOURCE_NOT_INDEPENDENTLY_REVIEWED = "FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED"
    TARGET_NOT_XML = "FILING_XML_TARGET_NOT_XML"
    CASE_MISMATCH = "FILING_XML_DERIVATION_CASE_MISMATCH"
    LINEAGE_MISMATCH = "FILING_XML_DERIVATION_LINEAGE_MISMATCH"
    DERIVATION_MISMATCH = "FILING_XML_DERIVATION_EDGE_MISMATCH"


class FilingXmlDerivationPolicyError(ValueError):
    def __init__(self, code: FilingXmlDerivationErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> FilingXmlDerivationErrorCode:
        return self._code


def _raise(code: FilingXmlDerivationErrorCode) -> None:
    raise FilingXmlDerivationPolicyError(code)


def _is_exact_text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def require_copyable_oa_attachment_combination(
    *,
    case_id: str,
    attachments: tuple[DocumentEvidenceVersion, ...],
) -> None:
    if not _is_exact_text(case_id) or type(attachments) is not tuple:
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(
        type(attachment) is not DocumentEvidenceVersion
        or not _is_exact_text(attachment.id)
        or not _is_exact_text(attachment.case_id)
        or not _is_exact_text(attachment.role)
        for attachment in attachments
    ):
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(attachment.case_id != case_id for attachment in attachments):
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.CASE_MISMATCH)

    evidence_ids = [attachment.id for attachment in attachments]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.DUPLICATE_EVIDENCE)
    if any(attachment.role not in _COPYABLE_OA_ATTACHMENT_ROLES for attachment in attachments):
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.ROLE_NOT_PERMITTED)

    roles = [attachment.role for attachment in attachments]
    statement_word_count = roles.count("OA_STATEMENT_WORD")
    if statement_word_count == 0:
        raise CopyableOaAttachmentPolicyError(CopyableOaAttachmentErrorCode.STATEMENT_WORD_REQUIRED)
    if statement_word_count > 1:
        raise CopyableOaAttachmentPolicyError(
            CopyableOaAttachmentErrorCode.MULTIPLE_STATEMENT_WORDS
        )
    if "OA_MODIFIED_CLAIMS" not in roles:
        raise CopyableOaAttachmentPolicyError(
            CopyableOaAttachmentErrorCode.MODIFIED_CLAIMS_REQUIRED
        )
    if roles.count("OA_AMENDMENT_COMPARISON") > 1:
        raise CopyableOaAttachmentPolicyError(
            CopyableOaAttachmentErrorCode.MULTIPLE_COMPARISON_PAGES
        )


def require_filing_xml_reviewed_word_source(
    *,
    case_id: str,
    source_word: DocumentEvidenceVersion,
    xml_evidence: DocumentEvidenceVersion,
    derivation: DocumentEvidenceDerivation,
) -> None:
    if (
        not _is_exact_text(case_id)
        or type(source_word) is not DocumentEvidenceVersion
        or type(xml_evidence) is not DocumentEvidenceVersion
        or type(derivation) is not DocumentEvidenceDerivation
        or not _is_exact_text(source_word.id)
        or not _is_exact_text(source_word.case_id)
        or not _is_exact_text(source_word.lineage_key)
        or not _is_exact_text(source_word.creator_id)
        or not _is_exact_text(xml_evidence.id)
        or not _is_exact_text(xml_evidence.case_id)
        or not _is_exact_text(xml_evidence.lineage_key)
        or not _is_exact_text(derivation.case_id)
        or not _is_exact_text(derivation.parent_evidence_version_id)
        or not _is_exact_text(derivation.child_evidence_version_id)
        or not _is_exact_text(derivation.derivation_type)
    ):
        _raise(FilingXmlDerivationErrorCode.INVALID_CONTEXT)
    try:
        EvidenceDerivationType(derivation.derivation_type)
    except ValueError:
        _raise(FilingXmlDerivationErrorCode.INVALID_CONTEXT)

    if source_word.case_id != case_id or xml_evidence.case_id != case_id:
        _raise(FilingXmlDerivationErrorCode.CASE_MISMATCH)
    if source_word.role != EvidenceRole.FILING_FULL_WORD.value:
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_FILING_WORD)

    current_identity = f"{case_id}|{source_word.lineage_key}"
    if source_word.current_identity_key != current_identity:
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_CURRENT)
    if source_word.review_state != EvidenceReviewState.APPROVED.value:
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_APPROVED)
    if (
        not _is_exact_text(source_word.reviewer_id)
        or source_word.reviewer_id == source_word.creator_id
        or type(source_word.reviewed_at) is not datetime
        or source_word.reviewed_at.tzinfo is not None
    ):
        _raise(FilingXmlDerivationErrorCode.SOURCE_NOT_INDEPENDENTLY_REVIEWED)

    if xml_evidence.role not in (
        EvidenceRole.EXTERNAL_XML_PACKAGE.value,
        EvidenceRole.SUBMITTED_XML.value,
    ):
        _raise(FilingXmlDerivationErrorCode.TARGET_NOT_XML)
    if xml_evidence.lineage_key != source_word.lineage_key:
        _raise(FilingXmlDerivationErrorCode.LINEAGE_MISMATCH)
    if (
        derivation.case_id != case_id
        or derivation.parent_evidence_version_id != source_word.id
        or derivation.child_evidence_version_id != xml_evidence.id
    ):
        _raise(FilingXmlDerivationErrorCode.DERIVATION_MISMATCH)
