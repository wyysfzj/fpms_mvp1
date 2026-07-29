from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.models import DocumentEvidenceDerivation, DocumentEvidenceVersion

__all__ = (
    "CopyableOaAttachmentEvidence",
    "CopyableOaAttachmentErrorCode",
    "CopyableOaAttachmentPolicyError",
    "FilingXmlDerivationErrorCode",
    "FilingXmlDerivationPolicyError",
    "require_copyable_oa_attachment_combination",
    "require_filing_xml_reviewed_word_source",
)


_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_COPYABLE_OA_ATTACHMENT_ROLES = frozenset(
    {
        "OA_STATEMENT_WORD",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CopyableOaAttachmentEvidence:
    evidence_version: EvidenceVersionResult
    manifest_id: str
    manifest_case_id: str
    manifest_package_id: str
    manifest_role: str
    manifest_evidence_version_id: str
    manifest_content_hash: str


class CopyableOaAttachmentErrorCode(str, Enum):
    INVALID_CONTEXT = "OA_COPYABLE_ATTACHMENT_INVALID_CONTEXT"
    CASE_MISMATCH = "OA_COPYABLE_ATTACHMENT_CASE_MISMATCH"
    PACKAGE_MISMATCH = "OA_COPYABLE_ATTACHMENT_PACKAGE_MISMATCH"
    DUPLICATE_EVIDENCE = "OA_COPYABLE_ATTACHMENT_DUPLICATE_EVIDENCE"
    DUPLICATE_MANIFEST = "OA_COPYABLE_ATTACHMENT_DUPLICATE_MANIFEST"
    ROLE_NOT_PERMITTED = "OA_COPYABLE_ATTACHMENT_ROLE_NOT_PERMITTED"
    NOT_STRUCTURED = "OA_COPYABLE_ATTACHMENT_NOT_STRUCTURED"
    NOT_CURRENT = "OA_COPYABLE_ATTACHMENT_NOT_CURRENT"
    NOT_APPROVED = "OA_COPYABLE_ATTACHMENT_NOT_APPROVED"
    NOT_INDEPENDENTLY_REVIEWED = "OA_COPYABLE_ATTACHMENT_NOT_INDEPENDENTLY_REVIEWED"
    STATE_MISMATCH = "OA_COPYABLE_ATTACHMENT_STATE_MISMATCH"
    LINK_MISMATCH = "OA_COPYABLE_ATTACHMENT_LINK_MISMATCH"
    HASH_MISMATCH = "OA_COPYABLE_ATTACHMENT_HASH_MISMATCH"
    STATEMENT_WORD_REQUIRED = "OA_COPYABLE_STATEMENT_WORD_REQUIRED"
    MULTIPLE_STATEMENT_WORDS = "OA_COPYABLE_MULTIPLE_STATEMENT_WORDS"
    MODIFIED_CLAIMS_REQUIRED = "OA_COPYABLE_MODIFIED_CLAIMS_REQUIRED"
    MULTIPLE_MODIFIED_CLAIMS = "OA_COPYABLE_MULTIPLE_MODIFIED_CLAIMS"
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


def _raise_copyable(code: CopyableOaAttachmentErrorCode) -> None:
    raise CopyableOaAttachmentPolicyError(code)


def _has_valid_copyable_evidence_shape(evidence: object) -> bool:
    return (
        type(evidence) is EvidenceVersionResult
        and _is_exact_text(evidence.evidence_version_id)
        and _is_exact_text(evidence.case_id)
        and _is_exact_text(evidence.document_id)
        and _is_exact_text(evidence.attachment_id)
        and _is_exact_text(evidence.lineage_key)
        and type(evidence.role) is EvidenceRole
        and type(evidence.version_number) is int
        and evidence.version_number > 0
        and type(evidence.state) is EvidenceVersionState
        and _is_exact_text(evidence.creator_id)
        and type(evidence.review_state) is EvidenceReviewState
        and (
            evidence.reviewer_id is None
            or _is_exact_text(evidence.reviewer_id)
        )
        and (
            evidence.reviewed_at is None
            or type(evidence.reviewed_at) is datetime
        )
        and (
            evidence.final_submitted_at is None
            or type(evidence.final_submitted_at) is datetime
        )
        and _is_exact_text(evidence.content_hash)
        and _CONTENT_HASH_PATTERN.fullmatch(evidence.content_hash) is not None
        and type(evidence.is_current) is bool
        and type(evidence.is_final) is bool
    )


def require_copyable_oa_attachment_combination(
    *,
    case_id: str,
    package_id: str,
    attachments: tuple[CopyableOaAttachmentEvidence, ...],
) -> None:
    if (
        not _is_exact_text(case_id)
        or not _is_exact_text(package_id)
        or type(attachments) is not tuple
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(
        type(attachment) is not CopyableOaAttachmentEvidence
        or not _has_valid_copyable_evidence_shape(attachment.evidence_version)
        or not _is_exact_text(attachment.manifest_id)
        or not _is_exact_text(attachment.manifest_case_id)
        or not _is_exact_text(attachment.manifest_package_id)
        or not _is_exact_text(attachment.manifest_role)
        or not _is_exact_text(attachment.manifest_evidence_version_id)
        or not _is_exact_text(attachment.manifest_content_hash)
        or _CONTENT_HASH_PATTERN.fullmatch(attachment.manifest_content_hash) is None
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.INVALID_CONTEXT)
    if any(
        attachment.evidence_version.case_id != case_id
        or attachment.manifest_case_id != case_id
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.CASE_MISMATCH)
    if any(attachment.manifest_package_id != package_id for attachment in attachments):
        _raise_copyable(CopyableOaAttachmentErrorCode.PACKAGE_MISMATCH)

    evidence_ids = [
        attachment.evidence_version.evidence_version_id for attachment in attachments
    ]
    if len(evidence_ids) != len(set(evidence_ids)):
        _raise_copyable(CopyableOaAttachmentErrorCode.DUPLICATE_EVIDENCE)
    manifest_ids = [attachment.manifest_id for attachment in attachments]
    if len(manifest_ids) != len(set(manifest_ids)):
        _raise_copyable(CopyableOaAttachmentErrorCode.DUPLICATE_MANIFEST)
    if any(
        attachment.manifest_role not in _COPYABLE_OA_ATTACHMENT_ROLES
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.ROLE_NOT_PERMITTED)
    if any(
        attachment.evidence_version.role is not EvidenceRole.OA_STRUCTURED_ATTACHMENT
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_STRUCTURED)
    if any(not attachment.evidence_version.is_current for attachment in attachments):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_CURRENT)
    if any(
        attachment.evidence_version.review_state is not EvidenceReviewState.APPROVED
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_APPROVED)
    if any(
        not _is_exact_text(attachment.evidence_version.reviewer_id)
        or attachment.evidence_version.reviewer_id
        == attachment.evidence_version.creator_id
        or type(attachment.evidence_version.reviewed_at) is not datetime
        or attachment.evidence_version.reviewed_at.tzinfo is not None
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.NOT_INDEPENDENTLY_REVIEWED)
    if any(
        attachment.evidence_version.is_final
        is not (attachment.evidence_version.state is EvidenceVersionState.FINAL)
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.STATE_MISMATCH)
    if any(
        attachment.manifest_evidence_version_id
        != attachment.evidence_version.evidence_version_id
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.LINK_MISMATCH)
    if any(
        attachment.manifest_content_hash != attachment.evidence_version.content_hash
        for attachment in attachments
    ):
        _raise_copyable(CopyableOaAttachmentErrorCode.HASH_MISMATCH)

    roles = [attachment.manifest_role for attachment in attachments]
    statement_word_count = roles.count("OA_STATEMENT_WORD")
    if statement_word_count == 0:
        _raise_copyable(CopyableOaAttachmentErrorCode.STATEMENT_WORD_REQUIRED)
    if statement_word_count > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_STATEMENT_WORDS)
    modified_claims_count = roles.count("OA_MODIFIED_CLAIMS")
    if modified_claims_count == 0:
        _raise_copyable(CopyableOaAttachmentErrorCode.MODIFIED_CLAIMS_REQUIRED)
    if modified_claims_count > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_MODIFIED_CLAIMS)
    if roles.count("OA_AMENDMENT_COMPARISON") > 1:
        _raise_copyable(CopyableOaAttachmentErrorCode.MULTIPLE_COMPARISON_PAGES)


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
