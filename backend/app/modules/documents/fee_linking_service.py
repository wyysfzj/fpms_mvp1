"""B3: Auto-create FeeDraft when document registered with fee-enabled template."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from hashlib import sha256
from re import fullmatch
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.annuity.models import AnnuityTask, FutureAnnuityReductionLineage
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.application_fee_notice_contracts import (
    ApplicationFeeNotice,
    ApplicationFeeNoticeEvidence,
    ApplicationFeeNoticeItem,
    ApplicationFeeNoticePct,
    ApplicationFeeNoticeSource,
    ApplicationFeeNoticeSourceError,
)
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion
from app.modules.documents.schemas import DocumentWizardFeeFinalRowIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.fees.annuity_reduction import (
    AnnuityReductionScopeError,
    validate_annuity_fee_reduction,
)
from app.modules.fees.cnipa_annuity_rate_candidate import (
    CNIPA_ANNUITY_SOURCE_SNAPSHOT,
    select_cnipa_annuity_amount,
)
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationError,
)
from app.modules.fees.fee_reduction_approval_service import (
    RecordFeeReductionApprovalCommand,
    RecordFeeReductionApprovalResult,
    record_fee_reduction_approval,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationLine,
    FeeRate,
    FeeReductionApproval,
    OfficialRateBook,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
)
from app.modules.fees.obligation_service import recognize_obligation
from app.modules.fees.official_rate_book import (
    CalculateCompensationPeriodAnnuityFeeCommand,
    CalculateOpenLicenseAnnuityReductionCommand,
    GetLayoutBibliographicChangeFeeCommand,
    GetLayoutExtensionFeeCommand,
    GetLayoutNonvoluntaryLicenseFeeCommand,
    GetLayoutReexaminationFeeCommand,
    GetLayoutRegistrationFeeCommand,
    GetLayoutRemunerationAdjudicationFeeCommand,
    GetLayoutRestorationFeeCommand,
    GetPatentTermCompensationRequestFeeCommand,
    calculate_compensation_period_annuity_fee,
    calculate_open_license_annuity_reduction,
    get_layout_bibliographic_change_fee,
    get_layout_extension_fee,
    get_layout_nonvoluntary_license_fee,
    get_layout_reexamination_fee,
    get_layout_registration_fee,
    get_layout_remuneration_adjudication_fee,
    get_layout_restoration_fee,
    get_patent_term_compensation_request_fee,
)
from app.modules.fees.pct_policy import (
    ConfirmedPctEvidence,
    EvaluatePctNationalStageFeePolicyCommand,
    PctFeePolicyError,
    evaluate_pct_national_stage_fee_policy,
    validate_confirmed_pct_evidence_set,
)

logger = logging.getLogger(__name__)

_APPLICATION_FEE_NOTICE_SCHEMA = "FPMS_APPLICATION_FEE_NOTICE_V1"
_APPLICATION_FEE_NOTICE_FIELD = "ApplicationFeeNotice"
_APPLICATION_FEE_NOTICE_ERROR = "APPLICATION_FEE_NOTICE_SOURCE_INVALID"
_APPLICATION_FEE_CODES = frozenset(
    {
        "CN_INV_APPLICATION_FEE",
        "CN_UM_APPLICATION_FEE",
        "CN_DES_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_SPEC_PAGE_31_300_FEE",
        "CN_SPEC_PAGE_301_PLUS_FEE",
        "CN_PUBLICATION_PRINT_FEE",
        "CN_PRIORITY_CLAIM_FEE",
    }
)
_PCT_APPLICATION_FEE_CODES = frozenset(
    {
        "CN_INV_APPLICATION_FEE",
        "CN_UM_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_SPEC_PAGE_31_300_FEE",
        "CN_SPEC_PAGE_301_PLUS_FEE",
    }
)
_PCT_APPLICATION_EVIDENCE = frozenset({"CNIPA_RO_RECEIPT", "CNIPA_ISR"})
_PCT_EVIDENCE_TYPES = _PCT_APPLICATION_EVIDENCE | {"CNIPA_IPRP"}
_APPLICATION_FEE_DUE_DATE_SOURCES = frozenset(
    {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
)


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (TypeError, ValueError, ArithmeticError):
        return None


def parse_fee_item_list_candidates(
    raw_json: str | None, template_code: str
) -> list[dict[str, object]]:
    """Parse fee_item_list JSON into preview-safe candidate dicts."""
    if not raw_json:
        return []

    try:
        items = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("B3: Malformed fee_item_list JSON in template %s: %s", template_code, exc)
        return []

    if not isinstance(items, list):
        logger.warning("B3: fee_item_list in template %s is not a list", template_code)
        return []

    candidates: list[dict[str, object]] = []
    for item_data in items:
        if not isinstance(item_data, dict):
            continue
        amount = _to_decimal(item_data.get("amount"))
        if amount is None:
            amount = Decimal("0")
        candidates.append(
            {
                "fee_code": item_data.get("code") or item_data.get("fee_code"),
                "fee_name": item_data.get("name") or item_data.get("fee_name"),
                "fee_type": item_data.get("fee_type", "SERVICE"),
                "quantity": _to_decimal(item_data.get("quantity")),
                "unit_price": _to_decimal(item_data.get("unit_price")),
                "amount": amount,
                "remark": item_data.get("remark")
                or item_data.get("description")
                or item_data.get("label"),
            }
        )
    return candidates


def maybe_create_fee_draft(
    db: Session,
    document: Document,
    template: DocTemplate,
) -> FeeDraft | None:
    """Auto-create a FeeDraft if template has fee_draft_type configured.

    Returns created FeeDraft, or None if no draft was needed.
    Does NOT commit — caller is responsible for db.commit().
    """
    fee_draft_type = getattr(template, "fee_draft_type", None)
    if not fee_draft_type:
        return None
    semantics = resolve_document_semantics(template)
    if str(getattr(template, "code", "")).strip().upper() == "GRANT_NOTICE" or (
        semantics.catalog_status == "EXECUTABLE"
        and (
            (
                semantics.execution_behavior == "GRANT_NOTICE"
                and semantics.fee_trigger == "GRANT_FEE"
            )
            or (
                semantics.execution_behavior == "APPLICATION_FEE_NOTICE"
                and semantics.fee_trigger == "APPLICATION_FEE"
            )
        )
    ):
        return None

    # Load case to get client_id
    case = db.get(Case, document.case_id)
    if not case:
        logger.warning(
            "B3: Case %s not found for document %s, skipping fee draft",
            document.case_id,
            document.id,
        )
        return None

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=document.case_id,
        client_id=case.client_id,
        draft_type=fee_draft_type,
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)

    fee_item_list_raw = getattr(template, "fee_item_list", None)
    if fee_item_list_raw:
        _create_fee_items_from_candidates(
            db,
            draft,
            document,
            parse_fee_item_list_candidates(fee_item_list_raw, template.code),
        )

    return draft


def create_fee_draft_from_wizard_row(
    db: Session,
    document: Document,
    fee_row: DocumentWizardFeeFinalRowIn,
) -> FeeDraft | None:
    """Create a FeeDraft from explicit wizard fee row values."""
    if fee_row.skip_this_candidate:
        return None

    case = db.get(Case, document.case_id)
    if not case:
        logger.warning(
            "B3: Case %s not found for document %s, skipping explicit fee draft",
            document.case_id,
            document.id,
        )
        return None

    draft_type = str(fee_row.fee_draft_type).strip()
    if not draft_type:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid fee rows",
            details={
                "row_errors": [
                    {
                        "row_index": fee_row.row_index,
                        "field": "fee_draft_type",
                        "code": "FEE_DRAFT_TYPE_REQUIRED",
                        "message": "fee_draft_type is required",
                    }
                ]
            },
            status_code=400,
        )

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=document.case_id,
        client_id=case.client_id,
        draft_type=draft_type,
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)
    _create_fee_items_from_wizard_row(db, draft, document, fee_row)
    return draft


def _create_fee_items_from_candidates(
    db: Session,
    draft: FeeDraft,
    document: Document,
    candidates: list[dict[str, object]],
) -> None:
    """Create FeeItem rows from parsed candidates."""
    total_gov = Decimal("0")
    total_service = Decimal("0")
    total_misc = Decimal("0")
    total_amount = Decimal("0")

    for item_data in candidates:
        fee_type = str(item_data.get("fee_type") or "SERVICE").upper()
        amount = item_data.get("amount", Decimal("0"))
        if not isinstance(amount, Decimal):
            amount = _to_decimal(amount) or Decimal("0")
        total_amount += amount
        if fee_type == "GOV":
            total_gov += amount
        elif fee_type == "SERVICE":
            total_service += amount
        else:
            total_misc += amount

        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.get("fee_code"),
            fee_name=item_data.get("fee_name"),
            fee_type=fee_type,
            quantity=item_data.get("quantity"),
            unit_price=item_data.get("unit_price"),
            amount=amount,
        )
        db.add(fee_item)

    draft.total_gov = total_gov
    draft.total_service = total_service
    draft.total_misc = total_misc
    draft.amount = total_amount


def _create_fee_items_from_wizard_row(
    db: Session,
    draft: FeeDraft,
    document: Document,
    fee_row: DocumentWizardFeeFinalRowIn,
) -> None:
    total_gov = Decimal("0")
    total_service = Decimal("0")
    total_misc = Decimal("0")
    total_amount = Decimal("0")

    for item_data in fee_row.fee_items:
        fee_type = (item_data.fee_type or "SERVICE").upper()
        amount = item_data.amount or Decimal("0")
        total_amount += amount
        if fee_type == "GOV":
            total_gov += amount
        elif fee_type == "SERVICE":
            total_service += amount
        else:
            total_misc += amount

        fee_item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=document.case_id,
            fee_code=item_data.fee_code,
            fee_name=item_data.fee_name,
            fee_type=item_data.fee_type or "SERVICE",
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            amount=amount,
            remark=item_data.remark,
        )
        db.add(fee_item)

    draft.total_gov = total_gov
    draft.total_service = total_service
    draft.total_misc = total_misc
    draft.amount = total_amount


_CANONICAL_HASH_PATTERN = r"sha256:[0-9a-f]{64}"

_IC_LAYOUT_SOURCE_ACTIVITY_TYPE = "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED"

_IC_LAYOUT_SOURCE_ERROR = "IC_LAYOUT_REGISTRATION_FILED_SOURCE_CONFLICT"

_IC_LAYOUT_REEXAM_LINEAGE = "ic-layout-reexamination-request-submission"

_IC_LAYOUT_RESTORE_RIGHT_LINEAGE = "ic-layout-right-restoration-request-submission"

_IC_LAYOUT_BIBLIO_CHANGE_LINEAGE = "ic-layout-bibliographic-change-submission"

_IC_LAYOUT_EXTENSION_REQUEST_LINEAGE = "ic-layout-extension-request-submission"

_IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_LINEAGE = (
    "ic-layout-nonvoluntary-license-request-submission"
)

_IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_LINEAGE = (
    "ic-layout-remuneration-adjudication-request-submission"
)

_PATENT_TERM_COMPENSATION_REQUEST_LINEAGE = "patent-term-compensation-request-submission"

_TERM_COMPENSATION_GRANTED_LINEAGE = "term-compensation-grant-decision"

_TERM_COMPENSATION_GRANTED_SCHEMA = "FPMS_TERM_COMPENSATION_GRANTED_V1"

_TERM_COMPENSATION_GRANTED_FIELD = "TermCompensationGrant"

_OPEN_LICENSE_PERIOD_LINEAGE = "open-license-implementation-period"

_OPEN_LICENSE_PERIOD_SCHEMA = "FPMS_OPEN_LICENSE_IMPLEMENTATION_PERIOD_V1"

_OPEN_LICENSE_PERIOD_FIELD = "OpenLicenseImplementationPeriod"

_ORDINARY_ANNUITY_FEE_CODES = frozenset(
    {
        "CN_ANNUITY_FEE_INV",
        "CN_ANNUITY_FEE_UM",
        "CN_ANNUITY_FEE_DES",
    }
)

_OPEN_LICENSE_ANNUITY_FEE_CODE_BY_PATENT_CATEGORY = {
    "DES": "CN_ANNUITY_FEE_DES",
    "INV": "CN_ANNUITY_FEE_INV",
    "UM": "CN_ANNUITY_FEE_UM",
}

_OPEN_LICENSE_ANNUITY_CALC_PARAMS = {
    "CN_ANNUITY_FEE_DES": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10},'
        '{"amount":"3000.00","from":11,"to":15}]}'
    ),
    "CN_ANNUITY_FEE_INV": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"900.00","from":1,"to":3},'
        '{"amount":"1200.00","from":4,"to":6},'
        '{"amount":"2000.00","from":7,"to":9},'
        '{"amount":"4000.00","from":10,"to":12},'
        '{"amount":"6000.00","from":13,"to":15},'
        '{"amount":"8000.00","from":16,"to":20}]}'
    ),
    "CN_ANNUITY_FEE_UM": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10}]}'
    ),
}

_IC_LAYOUT_REEXAM_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_IC_LAYOUT_RESTORE_RIGHT_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_IC_LAYOUT_BIBLIO_CHANGE_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_IC_LAYOUT_EXTENSION_REQUEST_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)

_PATENT_TERM_COMPENSATION_REQUEST_SOURCE_ERRORS = frozenset(
    {
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "FEE_OBLIGATION_STORED_STATE_INVALID",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutRegistrationFiledObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutReexaminationRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutRightRestorationRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutBibliographicChangeSubmissionObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutExtensionRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutNonvoluntaryLicenseRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeIcLayoutRemunerationAdjudicationRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizePatentTermCompensationRequestObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeCompensationPeriodAnnuityObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeOpenLicenseAnnuityObligationCommand:
    case_id: str
    source_activity_id: str
    source_evidence_version_id: str
    existing_obligation_id: str


def _exact_text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def _application_fee_notice_invalid() -> None:
    raise ApplicationFeeNoticeSourceError(
        status_code=400,
        code=_APPLICATION_FEE_NOTICE_ERROR,
        details={"field": _APPLICATION_FEE_NOTICE_FIELD},
    )


def _application_fee_notice_conflict(field: str) -> None:
    raise_business_error(
        "APPLICATION_FEE_NOTICE_SOURCE_CONFLICT",
        "Application-fee notice review authority conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _notice_amount(value: object) -> bool:
    if type(value) is not Decimal or not value.is_finite() or value < 0:
        return False
    return value.as_tuple().exponent == -2


def _canonical_notice_bytes(notice: ApplicationFeeNotice) -> bytes:
    payload: dict[str, object] = {
        "schema": notice.schema,
        "currency": notice.currency,
        "total_amount": format(notice.total_amount, ".2f"),
        "items": [
            {
                "fee_code": item.fee_code,
                "fee_name": item.fee_name,
                "source_amount": format(item.source_amount, ".2f"),
            }
            for item in notice.items
        ],
    }
    if notice.pct is not None:
        payload["pct"] = {
            "national_stage_entry_date": notice.pct.national_stage_entry_date.isoformat(),
            "evidence": [
                {
                    "evidence_version_id": item.evidence_version_id,
                    "source_document_id": item.source_document_id,
                    "content_hash": item.content_hash,
                    "lineage_key": item.lineage_key,
                    "issuer": item.issuer,
                    "document_type": item.document_type,
                    "issued_on": item.issued_on.isoformat(),
                    "role": item.role,
                }
                for item in notice.pct.evidence
            ],
        }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _validated_application_fee_source(
    source: object,
) -> ApplicationFeeNoticeSource:
    if type(source) is not ApplicationFeeNoticeSource:
        _application_fee_notice_invalid()
    assert isinstance(source, ApplicationFeeNoticeSource)
    if (
        not _exact_text(source.document_id)
        or not _exact_text(source.case_id)
        or type(source.source_date) is not date
        or type(source.due_date) is not date
        or source.due_date_source not in _APPLICATION_FEE_DUE_DATE_SOURCES
        or source.due_date_status != "CONFIRMED"
        or type(source.notice) is not ApplicationFeeNotice
        or type(source.canonical_bytes) is not bytes
        or type(source.canonical_sha256) is not str
    ):
        _application_fee_notice_invalid()

    notice = source.notice
    if (
        notice.schema != _APPLICATION_FEE_NOTICE_SCHEMA
        or notice.currency != "CNY"
        or not _notice_amount(notice.total_amount)
        or type(notice.items) is not tuple
        or not notice.items
    ):
        _application_fee_notice_invalid()

    seen_codes: set[str] = set()
    total = Decimal("0.00")
    for item in notice.items:
        if (
            type(item) is not ApplicationFeeNoticeItem
            or item.fee_code not in _APPLICATION_FEE_CODES
            or item.fee_code in seen_codes
            or not _exact_text(item.fee_name)
            or not _notice_amount(item.source_amount)
        ):
            _application_fee_notice_invalid()
        seen_codes.add(item.fee_code)
        total += item.source_amount
    if total != notice.total_amount:
        _application_fee_notice_invalid()

    if notice.pct is not None and (
        type(notice.pct) is not ApplicationFeeNoticePct
        or type(notice.pct.national_stage_entry_date) is not date
        or type(notice.pct.evidence) is not tuple
        or not notice.pct.evidence
    ):
        _application_fee_notice_invalid()
    try:
        canonical_bytes = _canonical_notice_bytes(notice)
    except (AttributeError, TypeError, ValueError):
        _application_fee_notice_invalid()
    if (
        source.canonical_bytes != canonical_bytes
        or source.canonical_sha256 != sha256(canonical_bytes).hexdigest()
    ):
        _application_fee_notice_invalid()
    return source


def _validated_preview_by_code(
    source: ApplicationFeeNoticeSource,
    preview: object,
) -> dict[str, FeeObligationLineInput]:
    if (
        type(preview) is not FeeEstimate
        or preview.case_id != source.case_id
        or preview.estimate_status is not FeeEstimateStatus.ESTIMATE
        or preview.currency != "CNY"
        or preview.trigger_context.trigger != "APPLICATION_FEE_NOTICE"
        or preview.trigger_context.source_document_id != source.document_id
        or type(preview.candidates) is not tuple
    ):
        _application_fee_notice_invalid()

    by_code: dict[str, FeeObligationLineInput] = {}
    for candidate in preview.candidates:
        if (
            type(candidate) is not FeeEstimateCandidate
            or candidate.source.status is not FeeSourceStatus.VERIFIED
            or type(candidate.line) is not FeeObligationLineInput
            or candidate.line.fee_code in by_code
            or candidate.line.fee_year_key != 0
            or type(candidate.line.official_full_amount) is not Decimal
            or not candidate.line.official_full_amount.is_finite()
            or candidate.line.official_full_amount <= 0
            or type(candidate.line.reduction_ratio) is not Decimal
            or not candidate.line.reduction_ratio.is_finite()
            or not Decimal("0") <= candidate.line.reduction_ratio <= Decimal("1")
            or type(candidate.line.payable_amount) is not Decimal
            or not candidate.line.payable_amount.is_finite()
            or candidate.line.payable_amount < 0
        ):
            _application_fee_notice_invalid()
        by_code[candidate.line.fee_code] = candidate.line

    if set(by_code) != {item.fee_code for item in source.notice.items}:
        _application_fee_notice_invalid()
    return by_code


def _validated_pct_evidence(
    source: ApplicationFeeNoticeSource,
    confirmed: object,
) -> tuple[ConfirmedPctEvidence, ...]:
    if type(confirmed) is not tuple or any(
        type(item) is not ConfirmedPctEvidence for item in confirmed
    ):
        _application_fee_notice_invalid()
    assert isinstance(confirmed, tuple)

    pct = source.notice.pct
    if pct is None:
        if confirmed:
            _application_fee_notice_invalid()
        return ()

    references: dict[str, ApplicationFeeNoticeEvidence] = {}
    for reference in pct.evidence:
        if (
            type(reference) is not ApplicationFeeNoticeEvidence
            or not _exact_text(reference.evidence_version_id)
            or not _exact_text(reference.source_document_id)
            or type(reference.content_hash) is not str
            or fullmatch(_CANONICAL_HASH_PATTERN, reference.content_hash) is None
            or not _exact_text(reference.lineage_key)
            or reference.issuer != "CNIPA"
            or reference.document_type not in _PCT_EVIDENCE_TYPES
            or type(reference.issued_on) is not date
            or reference.issued_on > pct.national_stage_entry_date
            or reference.role != "OFFICIAL_FINAL_PDF"
            or reference.evidence_version_id in references
        ):
            _application_fee_notice_invalid()
        references[reference.evidence_version_id] = reference

    try:
        validate_confirmed_pct_evidence_set(
            source.case_id,
            pct.national_stage_entry_date,
            confirmed,
        )
    except PctFeePolicyError:
        _application_fee_notice_invalid()

    confirmed_by_id: dict[str, ConfirmedPctEvidence] = {}
    for item in confirmed:
        if item.evidence_version_id in confirmed_by_id or item.case_id != source.case_id:
            _application_fee_notice_invalid()
        confirmed_by_id[item.evidence_version_id] = item
    if set(confirmed_by_id) != set(references):
        _application_fee_notice_invalid()

    for evidence_version_id, reference in references.items():
        item = confirmed_by_id[evidence_version_id]
        if (
            item.source_document_id != reference.source_document_id
            or item.content_hash != reference.content_hash
            or item.lineage_key != reference.lineage_key
            or item.issuer != reference.issuer
            or item.document_type != reference.document_type
            or item.issued_on != reference.issued_on
            or item.role != reference.role
        ):
            _application_fee_notice_invalid()
    return confirmed


def _pct_application_exemption_applies(source: ApplicationFeeNoticeSource) -> bool:
    pct = source.notice.pct
    if pct is None or len(pct.evidence) != 2:
        return False
    return {item.document_type for item in pct.evidence} == _PCT_APPLICATION_EVIDENCE


def _validated_application_fee_review(
    *,
    transaction: Session,
    source: ApplicationFeeNoticeSource,
    review_activity_id: str,
    reviewed_evidence_version_id: str,
    reviewer_id: str,
) -> None:
    if not isinstance(transaction, Session):
        _application_fee_notice_conflict("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _application_fee_notice_conflict("transaction")

    with transaction.no_autoflush:
        activity = transaction.get(CaseActivityEvent, review_activity_id)
        evidence = transaction.get(
            DocumentEvidenceVersion,
            reviewed_evidence_version_id,
        )
        if activity is None or evidence is None:
            _application_fee_notice_conflict("review_authority")
        assert isinstance(activity, CaseActivityEvent)
        assert isinstance(evidence, DocumentEvidenceVersion)
        document = transaction.get(Document, evidence.document_id)
        if document is None:
            _application_fee_notice_conflict("source_document")
        assert isinstance(document, Document)

        if (
            evidence.case_id != source.case_id
            or evidence.document_id != source.document_id
            or document.id != source.document_id
            or document.case_id != source.case_id
            or document.direction != "IN"
            or evidence.role != "OFFICIAL_FINAL_PDF"
            or evidence.state != "FINAL"
            or evidence.review_state != "APPROVED"
            or evidence.current_identity_key != f"{source.case_id}|{evidence.lineage_key}"
            or not _exact_text(evidence.lineage_key)
            or not _exact_text(evidence.creator_id)
            or not _exact_text(evidence.reviewer_id)
            or evidence.creator_id == evidence.reviewer_id
            or evidence.reviewer_id != reviewer_id
            or type(evidence.reviewed_at) is not datetime
            or evidence.reviewed_at.tzinfo is not None
            or type(evidence.content_hash) is not str
            or fullmatch(_CANONICAL_HASH_PATTERN, evidence.content_hash) is None
        ):
            _application_fee_notice_conflict("reviewed_evidence")

        if (
            activity.case_id != source.case_id
            or activity.activity_type != "DOCUMENT_EVIDENCE_REVIEW_DECIDED"
            or activity.lane != "DOCUMENT"
            or activity.confirmation_status != "CONFIRMED"
            or activity.source_activity_id is not None
            or activity.supersedes_event_id is not None
            or activity.old_business_stage != activity.new_business_stage
            or activity.old_official_procedure_stage != activity.new_official_procedure_stage
            or activity.old_legal_status != activity.new_legal_status
            or type(activity.effective_at) is not datetime
            or activity.effective_at.tzinfo is not None
            or activity.occurred_at != activity.effective_at
            or activity.actor_id != reviewer_id
            or activity.reviewer_id != reviewer_id
            or evidence.reviewed_at != activity.effective_at
        ):
            _application_fee_notice_conflict("review_activity")

        expected_payload = {
            "creator_id": evidence.creator_id,
            "decision": "APPROVE",
            "evidence_version_id": evidence.id,
            "previous_review_state": "PENDING",
            "review_state": "APPROVED",
            "reviewer_id": reviewer_id,
        }
        try:
            payload = json.loads(activity.payload_json)
        except (RecursionError, TypeError, ValueError):
            _application_fee_notice_conflict("review_activity_payload")
        if payload != expected_payload or activity.payload_json != _canonical_json(payload):
            _application_fee_notice_conflict("review_activity_payload")

        references = tuple(
            transaction.scalars(
                select(CaseActivityEventEvidence).where(
                    CaseActivityEventEvidence.activity_id == activity.id
                )
            )
        )
        if len(references) != 1:
            _application_fee_notice_conflict("review_activity_reference")
        reference = references[0]
        if (
            reference.case_id != source.case_id
            or reference.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
            or reference.object_type != "DocumentEvidenceVersion"
            or reference.object_id != evidence.id
            or reference.content_hash != evidence.content_hash
            or reference.captured_at != activity.effective_at
        ):
            _application_fee_notice_conflict("review_activity_reference")


def recognize_application_fee_notice_obligation(
    *,
    transaction: Session,
    source: ApplicationFeeNoticeSource,
    review_activity_id: str,
    reviewed_evidence_version_id: str,
    reviewer_id: str,
    official_preview: FeeEstimate,
    confirmed_pct_evidence: tuple[ConfirmedPctEvidence, ...] = (),
) -> RecognizeFeeObligationResult:
    source = _validated_application_fee_source(source)
    if (
        not _exact_text(review_activity_id)
        or not _exact_text(reviewed_evidence_version_id)
        or not _exact_text(reviewer_id)
    ):
        _application_fee_notice_invalid()
    _validated_application_fee_review(
        transaction=transaction,
        source=source,
        review_activity_id=review_activity_id,
        reviewed_evidence_version_id=reviewed_evidence_version_id,
        reviewer_id=reviewer_id,
    )
    preview_by_code = _validated_preview_by_code(source, official_preview)
    pct_evidence = _validated_pct_evidence(source, confirmed_pct_evidence)
    apply_pct = _pct_application_exemption_applies(source)

    lines: list[FeeObligationLineInput] = []
    for item in source.notice.items:
        preview_line = preview_by_code[item.fee_code]
        official_full_amount = preview_line.official_full_amount
        reduction_ratio = preview_line.reduction_ratio
        official_payable_amount = preview_line.payable_amount
        if apply_pct and item.fee_code in _PCT_APPLICATION_FEE_CODES:
            assert source.notice.pct is not None
            assert official_full_amount is not None
            policy = evaluate_pct_national_stage_fee_policy(
                EvaluatePctNationalStageFeePolicyCommand(
                    case_id=source.case_id,
                    fee_code=item.fee_code,
                    full_amount=official_full_amount,
                    effective_on=source.notice.pct.national_stage_entry_date,
                    evidence=pct_evidence,
                    reduction_context=None,
                )
            )
            official_full_amount = policy.full_amount
            reduction_ratio = policy.reduction_ratio
            official_payable_amount = policy.payable_amount

        lines.append(
            FeeObligationLineInput(
                fee_code=item.fee_code,
                fee_name=item.fee_name,
                fee_year_key=0,
                official_full_amount=official_full_amount,
                reduction_ratio=reduction_ratio,
                payable_amount=item.source_amount,
                source_amount=item.source_amount,
                source_date=source.source_date,
                difference_review_state=(
                    FeeDifferenceReviewState.MATCHED
                    if official_payable_amount == item.source_amount
                    else FeeDifferenceReviewState.REVIEW_REQUIRED
                ),
            )
        )

    return recognize_obligation(
        RecognizeFeeObligationCommand(
            case_id=source.case_id,
            source_activity_id=review_activity_id,
            source_document_id=source.document_id,
            fee_domain=FeeDomain.GOV,
            obligation_type="APPLICATION_FEE",
            due_date=source.due_date,
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED,
            lines=tuple(lines),
            actor_id=reviewer_id,
            idempotency_key=(
                f"application-fee-notice:{reviewed_evidence_version_id}:{source.due_date_source}"
            ),
            supersedes_obligation_id=None,
            supersede_reason=None,
        ),
        transaction,
    )


def maybe_record_fee_reduction_approval_notice(
    *,
    transaction: Session,
    template: DocTemplate | None,
    command: RecordFeeReductionApprovalCommand,
) -> RecordFeeReductionApprovalResult | None:
    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "FEE_REDUCTION_APPROVAL_NOTICE"
    ):
        return None
    return record_fee_reduction_approval(command, transaction)


def _ic_layout_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_REGISTRATION_FILED_INVALID",
        "Invalid IC-layout registration-filed obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_conflict(field: str) -> None:
    raise_business_error(
        _IC_LAYOUT_SOURCE_ERROR,
        "IC-layout registration-filed source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _ic_layout_reexam_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_REEXAM_REQUEST_INVALID",
        "Invalid IC-layout reexamination-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_reexam_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_REEXAM_REQUEST_SOURCE_CONFLICT",
        "IC-layout reexamination-request source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _ic_layout_restore_right_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_RESTORE_RIGHT_INVALID",
        "Invalid IC-layout right-restoration-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_restore_right_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_RESTORE_RIGHT_SOURCE_CONFLICT",
        "IC-layout right-restoration-request source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _ic_layout_biblio_change_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_BIBLIO_CHANGE_INVALID",
        "Invalid IC-layout bibliographic-change obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_biblio_change_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_BIBLIO_CHANGE_SOURCE_CONFLICT",
        "IC-layout bibliographic-change source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _ic_layout_extension_request_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_EXTENSION_REQUEST_INVALID",
        "Invalid IC-layout extension-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_extension_request_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_EXTENSION_REQUEST_SOURCE_CONFLICT",
        "IC-layout extension-request source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _ic_layout_nonvoluntary_license_request_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_INVALID",
        "Invalid IC-layout nonvoluntary-license-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_nonvoluntary_license_request_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_SOURCE_CONFLICT",
        (
            "IC-layout nonvoluntary-license-request source carrier conflicts "
            "with the frozen contract"
        ),
        details={"field": field},
        status_code=409,
    )


def _ic_layout_remuneration_adjudication_request_invalid(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_INVALID",
        "Invalid IC-layout remuneration-adjudication-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _ic_layout_remuneration_adjudication_request_conflict(field: str) -> None:
    raise_business_error(
        "IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_SOURCE_CONFLICT",
        (
            "IC-layout remuneration-adjudication-request source carrier conflicts "
            "with the frozen contract"
        ),
        details={"field": field},
        status_code=409,
    )


def _patent_term_compensation_request_invalid(field: str) -> None:
    raise_business_error(
        "PATENT_TERM_COMPENSATION_REQUEST_INVALID",
        "Invalid patent-term compensation-request obligation input",
        details={"field": field},
        status_code=400,
    )


def _patent_term_compensation_request_conflict(field: str) -> None:
    raise_business_error(
        "PATENT_TERM_COMPENSATION_REQUEST_SOURCE_CONFLICT",
        "Patent-term compensation-request source carrier conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _compensation_period_annuity_invalid(field: str) -> None:
    raise_business_error(
        "COMPENSATION_PERIOD_ANNUITY_INVALID",
        "Invalid compensation-period annuity obligation input",
        details={"field": field},
        status_code=400,
    )


def _compensation_period_annuity_conflict(field: str) -> None:
    raise_business_error(
        "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT",
        "Compensation-period annuity source conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _open_license_annuity_invalid(field: str) -> None:
    raise_business_error(
        "OPEN_LICENSE_ANNUITY_INVALID",
        "Invalid open-license annuity obligation input",
        details={"field": field},
        status_code=400,
    )


def _open_license_annuity_conflict(field: str) -> None:
    raise_business_error(
        "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT",
        "Open-license annuity source conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _compensation_strict_object(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_compensation_json_constant(_value: str) -> object:
    raise ValueError("non-finite JSON constant")


def _compensation_period_review_snapshot(
    evidence: DocumentEvidenceVersion,
    document: Document,
) -> tuple[dict[str, object], str]:
    if (
        type(evidence) is not DocumentEvidenceVersion
        or type(document) is not Document
        or evidence.document_id != document.id
        or evidence.case_id != document.case_id
        or document.direction != "IN"
        or evidence.lineage_key != _TERM_COMPENSATION_GRANTED_LINEAGE
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.current_identity_key
        != f"{evidence.case_id}|{_TERM_COMPENSATION_GRANTED_LINEAGE}"
        or type(evidence.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, evidence.content_hash) is None
        or type(document.doc_date) is not date
    ):
        _compensation_period_annuity_conflict("source_evidence")
    try:
        fields = json.loads(
            document.extra_data,
            object_pairs_hook=_compensation_strict_object,
            parse_constant=_reject_compensation_json_constant,
        )
    except (RecursionError, TypeError, ValueError):
        _compensation_period_annuity_conflict("period")
    if type(fields) is not dict:
        _compensation_period_annuity_conflict("period")

    period = fields.get(_TERM_COMPENSATION_GRANTED_FIELD)
    if type(period) is not dict or period.get("schema") != _TERM_COMPENSATION_GRANTED_SCHEMA:
        _compensation_period_annuity_conflict("period")
    if "complete_years" not in period:
        _compensation_period_annuity_conflict("complete_years")
    if set(period) != {
        "schema",
        "period_start",
        "period_end",
        "complete_years",
    }:
        _compensation_period_annuity_conflict("period")
    complete_years = period.get("complete_years")
    if type(complete_years) is not int or complete_years < 0:
        _compensation_period_annuity_conflict("complete_years")
    try:
        period_start = date.fromisoformat(period["period_start"])
        period_end = date.fromisoformat(period["period_end"])
    except (TypeError, ValueError):
        _compensation_period_annuity_conflict("period")
    if (
        period_start.isoformat() != period["period_start"]
        or period_end.isoformat() != period["period_end"]
        or period_start > period_end
    ):
        _compensation_period_annuity_conflict("period")

    due_date_value = fields.get("OfficialDueDate")
    due_date_source = fields.get("OfficialDueDateSource")
    if (
        type(due_date_value) is not str
        or due_date_source not in {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
        or fields.get("OfficialDueDateStatus") != "CONFIRMED"
    ):
        _compensation_period_annuity_conflict("deadline")
    try:
        due_date = date.fromisoformat(due_date_value)
    except ValueError:
        _compensation_period_annuity_conflict("deadline")
    if due_date.isoformat() != due_date_value:
        _compensation_period_annuity_conflict("deadline")
    if document.extra_data != _canonical_json(fields):
        _compensation_period_annuity_conflict("source_snapshot")

    snapshot: dict[str, object] = {
        "case_id": evidence.case_id,
        "complete_years": complete_years,
        "decision_date": document.doc_date.isoformat(),
        "due_date": due_date.isoformat(),
        "due_date_source": due_date_source,
        "due_date_status": "CONFIRMED",
        "evidence_content_hash": evidence.content_hash,
        "evidence_version_id": evidence.id,
        "period_end": period_end.isoformat(),
        "period_start": period_start.isoformat(),
        "schema": _TERM_COMPENSATION_GRANTED_SCHEMA,
        "source_document_id": document.id,
    }
    snapshot_hash = f"sha256:{sha256(_canonical_json(snapshot).encode()).hexdigest()}"
    return snapshot, snapshot_hash


def _open_license_review_snapshot(
    evidence: DocumentEvidenceVersion,
    document: Document,
) -> tuple[dict[str, object], str]:
    if (
        type(evidence) is not DocumentEvidenceVersion
        or type(document) is not Document
        or evidence.document_id != document.id
        or evidence.case_id != document.case_id
        or document.direction != "IN"
        or evidence.lineage_key != _OPEN_LICENSE_PERIOD_LINEAGE
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.current_identity_key != f"{evidence.case_id}|{_OPEN_LICENSE_PERIOD_LINEAGE}"
        or type(evidence.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, evidence.content_hash) is None
    ):
        _open_license_annuity_conflict("source_evidence")
    try:
        fields = json.loads(
            document.extra_data,
            object_pairs_hook=_compensation_strict_object,
            parse_constant=_reject_compensation_json_constant,
        )
    except (RecursionError, TypeError, ValueError):
        _open_license_annuity_conflict("period")
    if (
        type(fields) is not dict
        or set(fields) != {_OPEN_LICENSE_PERIOD_FIELD}
        or document.extra_data != _canonical_json(fields)
    ):
        _open_license_annuity_conflict("period")
    period = fields.get(_OPEN_LICENSE_PERIOD_FIELD)
    if (
        type(period) is not dict
        or set(period) != {"schema", "period_start", "period_end"}
        or period.get("schema") != _OPEN_LICENSE_PERIOD_SCHEMA
    ):
        _open_license_annuity_conflict("period")
    try:
        period_start = date.fromisoformat(period["period_start"])
        period_end = date.fromisoformat(period["period_end"])
    except (TypeError, ValueError):
        _open_license_annuity_conflict("period")
    if (
        period_start.isoformat() != period["period_start"]
        or period_end.isoformat() != period["period_end"]
        or period_start > period_end
    ):
        _open_license_annuity_conflict("period")
    snapshot: dict[str, object] = {
        "case_id": evidence.case_id,
        "evidence_content_hash": evidence.content_hash,
        "evidence_version_id": evidence.id,
        "period_end": period_end.isoformat(),
        "period_start": period_start.isoformat(),
        "schema": _OPEN_LICENSE_PERIOD_SCHEMA,
        "source_document_id": document.id,
    }
    snapshot_hash = f"sha256:{sha256(_canonical_json(snapshot).encode()).hexdigest()}"
    return snapshot, snapshot_hash


def _validate_ic_layout_command(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    *,
    invalid: Callable[[str], None] = _ic_layout_invalid,
) -> None:
    if type(command) is not RecognizeIcLayoutRegistrationFiledObligationCommand:
        invalid("command")
    for field in ("case_id", "source_activity_id", "source_evidence_version_id"):
        value = getattr(command, field)
        if not _exact_text(value) or len(value) > 36:
            invalid(field)


def _validate_ic_layout_transaction(
    transaction: Session,
    *,
    invalid: Callable[[str], None] = _ic_layout_invalid,
    conflict: Callable[[str], None] = _ic_layout_conflict,
) -> None:
    if not isinstance(transaction, Session):
        invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        conflict("transaction")


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _ic_layout_source_activity(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    transaction: Session,
    *,
    conflict: Callable[[str], None] = _ic_layout_conflict,
) -> CaseActivityEvent:
    activity = transaction.get(CaseActivityEvent, command.source_activity_id)
    if activity is None:
        conflict("source_activity_id")
    assert isinstance(activity, CaseActivityEvent)
    if (
        activity.case_id != command.case_id
        or activity.activity_type != _IC_LAYOUT_SOURCE_ACTIVITY_TYPE
        or activity.lane != "DOCUMENT"
        or activity.confirmation_status != "CONFIRMED"
        or activity.source_activity_id is not None
        or activity.supersedes_event_id is not None
    ):
        conflict("source_activity")
    if (
        activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
    ):
        conflict("source_activity_projection")
    if (
        type(activity.effective_at) is not datetime
        or activity.effective_at.tzinfo is not None
        or type(activity.occurred_at) is not datetime
        or activity.occurred_at.tzinfo is not None
        or activity.occurred_at != activity.effective_at
        or not _exact_text(activity.actor_id)
        or len(activity.actor_id) > 36
    ):
        conflict("source_activity_time")
    return activity


def _ic_layout_source_evidence(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    transaction: Session,
    activity: CaseActivityEvent,
    *,
    conflict: Callable[[str], None] = _ic_layout_conflict,
    expected_lineage_key: str | None = None,
    expected_direction: str | None = None,
) -> tuple[DocumentEvidenceVersion, Document]:
    evidence = transaction.get(
        DocumentEvidenceVersion,
        command.source_evidence_version_id,
    )
    if evidence is None:
        conflict("source_evidence_version_id")
    assert isinstance(evidence, DocumentEvidenceVersion)
    document = transaction.get(Document, evidence.document_id)
    if document is None:
        conflict("source_document_id")
    assert isinstance(document, Document)

    if (
        evidence.case_id != command.case_id
        or document.case_id != command.case_id
        or (expected_lineage_key is not None and evidence.lineage_key != expected_lineage_key)
        or (expected_direction is not None and document.direction != expected_direction)
        or evidence.role != "SUBMITTED_XML"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or evidence.current_identity_key != f"{command.case_id}|{evidence.lineage_key}"
        or not _exact_text(evidence.lineage_key)
        or len(evidence.lineage_key) > 128
        or not _exact_text(evidence.creator_id)
        or len(evidence.creator_id) > 36
        or not _exact_text(evidence.reviewer_id)
        or len(evidence.reviewer_id) > 36
        or evidence.creator_id == evidence.reviewer_id
        or type(evidence.reviewed_at) is not datetime
        or evidence.reviewed_at.tzinfo is not None
        or evidence.reviewer_id != activity.reviewer_id
        or type(evidence.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, evidence.content_hash) is None
        or evidence.final_submitted_at != activity.effective_at
    ):
        conflict("source_evidence")
    return evidence, document


def _validate_ic_layout_payload(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    activity: CaseActivityEvent,
    evidence: DocumentEvidenceVersion,
    *,
    conflict: Callable[[str], None] = _ic_layout_conflict,
) -> None:
    expected = {
        "evidence_version_id": command.source_evidence_version_id,
        "lineage_key": evidence.lineage_key,
        "role": "SUBMITTED_XML",
        "submitted_at": activity.effective_at.isoformat(),
    }
    try:
        payload = json.loads(activity.payload_json)
        canonical = _canonical_json(payload)
    except (RecursionError, TypeError, ValueError):
        conflict("source_activity_payload")
    if type(payload) is not dict or payload != expected or activity.payload_json != canonical:
        conflict("source_activity_payload")


def _validate_ic_layout_reference(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    transaction: Session,
    activity: CaseActivityEvent,
    evidence: DocumentEvidenceVersion,
    *,
    conflict: Callable[[str], None] = _ic_layout_conflict,
) -> None:
    references = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        )
    )
    if len(references) != 1:
        conflict("source_activity_evidence")
    reference = references[0]
    if (
        reference.case_id != command.case_id
        or reference.activity_id != activity.id
        or reference.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or reference.object_type != "DocumentEvidenceVersion"
        or reference.object_id != command.source_evidence_version_id
        or reference.content_hash != evidence.content_hash
        or reference.captured_at != activity.effective_at
    ):
        conflict("source_activity_evidence")


def recognize_ic_layout_registration_filed_obligation(
    command: RecognizeIcLayoutRegistrationFiledObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    _validate_ic_layout_command(command)
    _validate_ic_layout_transaction(transaction)

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(command, transaction)
        evidence, document = _ic_layout_source_evidence(command, transaction, activity)
        _validate_ic_layout_payload(command, activity, evidence)
        _validate_ic_layout_reference(command, transaction, activity, evidence)
        rate = get_layout_registration_fee(
            GetLayoutRegistrationFeeCommand(
                effective_date=activity.effective_at.date(),
            ),
            transaction,
        )

    return recognize_obligation(
        RecognizeFeeObligationCommand(
            case_id=command.case_id,
            source_activity_id=activity.id,
            source_document_id=document.id,
            fee_domain=FeeDomain.GOV,
            obligation_type="IC_LAYOUT_REGISTRATION_FILED",
            due_date=None,
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED,
            lines=(
                FeeObligationLineInput(
                    fee_code=rate.fee_code,
                    fee_name="布图设计登记费",
                    fee_year_key=0,
                    official_full_amount=rate.amount,
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=rate.amount,
                    source_amount=None,
                    source_date=activity.effective_at.date(),
                    difference_review_state=FeeDifferenceReviewState.MATCHED,
                ),
            ),
            actor_id=activity.actor_id,
            idempotency_key="ic-layout-registration-filed",
            supersedes_obligation_id=None,
            supersede_reason=None,
        ),
        transaction,
    )


def recognize_ic_layout_reexamination_request_obligation(
    command: RecognizeIcLayoutReexaminationRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutReexaminationRequestObligationCommand:
        _ic_layout_reexam_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(source_command, invalid=_ic_layout_reexam_invalid)
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_reexam_invalid,
        conflict=_ic_layout_reexam_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_reexam_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_reexam_conflict,
            expected_lineage_key=_IC_LAYOUT_REEXAM_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_reexam_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_reexam_conflict,
        )
        rate = get_layout_reexamination_fee(
            GetLayoutReexaminationFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_REEXAM_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="布图设计登记复审请求费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key="ic-layout-reexamination-request",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_REEXAM_SOURCE_ERRORS:
            _ic_layout_reexam_conflict("obligation_source")
        raise


def recognize_ic_layout_right_restoration_request_obligation(
    command: RecognizeIcLayoutRightRestorationRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutRightRestorationRequestObligationCommand:
        _ic_layout_restore_right_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(source_command, invalid=_ic_layout_restore_right_invalid)
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_restore_right_invalid,
        conflict=_ic_layout_restore_right_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_restore_right_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_restore_right_conflict,
            expected_lineage_key=_IC_LAYOUT_RESTORE_RIGHT_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_restore_right_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_restore_right_conflict,
        )
        rate = get_layout_restoration_fee(
            GetLayoutRestorationFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_RESTORE_RIGHT_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="恢复布图设计登记权利请求费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key="ic-layout-right-restoration-request",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_RESTORE_RIGHT_SOURCE_ERRORS:
            _ic_layout_restore_right_conflict("obligation_source")
        raise


def recognize_ic_layout_bibliographic_change_submission_obligation(
    command: RecognizeIcLayoutBibliographicChangeSubmissionObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutBibliographicChangeSubmissionObligationCommand:
        _ic_layout_biblio_change_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(source_command, invalid=_ic_layout_biblio_change_invalid)
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_biblio_change_invalid,
        conflict=_ic_layout_biblio_change_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_biblio_change_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_biblio_change_conflict,
            expected_lineage_key=_IC_LAYOUT_BIBLIO_CHANGE_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_biblio_change_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_biblio_change_conflict,
        )
        rate = get_layout_bibliographic_change_fee(
            GetLayoutBibliographicChangeFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_BIBLIO_CHANGE_SUBMITTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="布图设计著录事项变更手续费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key=f"ic-layout-bibliographic-change:{activity.id}",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_BIBLIO_CHANGE_SOURCE_ERRORS:
            _ic_layout_biblio_change_conflict("obligation_source")
        raise


def recognize_ic_layout_extension_request_obligation(
    command: RecognizeIcLayoutExtensionRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutExtensionRequestObligationCommand:
        _ic_layout_extension_request_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(
        source_command,
        invalid=_ic_layout_extension_request_invalid,
    )
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_extension_request_invalid,
        conflict=_ic_layout_extension_request_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_extension_request_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_extension_request_conflict,
            expected_lineage_key=_IC_LAYOUT_EXTENSION_REQUEST_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_extension_request_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_extension_request_conflict,
        )
        rate = get_layout_extension_fee(
            GetLayoutExtensionFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_EXTENSION_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="布图设计延长期限请求费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key=f"ic-layout-extension-request:{activity.id}",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_EXTENSION_REQUEST_SOURCE_ERRORS:
            _ic_layout_extension_request_conflict("obligation_source")
        raise


def recognize_ic_layout_nonvoluntary_license_request_obligation(
    command: RecognizeIcLayoutNonvoluntaryLicenseRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutNonvoluntaryLicenseRequestObligationCommand:
        _ic_layout_nonvoluntary_license_request_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(
        source_command,
        invalid=_ic_layout_nonvoluntary_license_request_invalid,
    )
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_nonvoluntary_license_request_invalid,
        conflict=_ic_layout_nonvoluntary_license_request_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_nonvoluntary_license_request_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_nonvoluntary_license_request_conflict,
            expected_lineage_key=_IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_nonvoluntary_license_request_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_nonvoluntary_license_request_conflict,
        )
        rate = get_layout_nonvoluntary_license_fee(
            GetLayoutNonvoluntaryLicenseFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="非自愿许可使用布图设计请求费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key=(f"ic-layout-nonvoluntary-license-request:{activity.id}"),
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_SOURCE_ERRORS:
            _ic_layout_nonvoluntary_license_request_conflict("obligation_source")
        raise


def recognize_ic_layout_remuneration_adjudication_request_obligation(
    command: RecognizeIcLayoutRemunerationAdjudicationRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeIcLayoutRemunerationAdjudicationRequestObligationCommand:
        _ic_layout_remuneration_adjudication_request_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(
        source_command,
        invalid=_ic_layout_remuneration_adjudication_request_invalid,
    )
    _validate_ic_layout_transaction(
        transaction,
        invalid=_ic_layout_remuneration_adjudication_request_invalid,
        conflict=_ic_layout_remuneration_adjudication_request_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_ic_layout_remuneration_adjudication_request_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_ic_layout_remuneration_adjudication_request_conflict,
            expected_lineage_key=_IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_ic_layout_remuneration_adjudication_request_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_ic_layout_remuneration_adjudication_request_conflict,
        )
        rate = get_layout_remuneration_adjudication_fee(
            GetLayoutRemunerationAdjudicationFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="非自愿许可使用支付报酬裁决费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key=f"ic-layout-remuneration-adjudication-request:{activity.id}",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _IC_LAYOUT_REMUNERATION_ADJUDICATION_REQUEST_SOURCE_ERRORS:
            _ic_layout_remuneration_adjudication_request_conflict("obligation_source")
        raise


def recognize_patent_term_compensation_request_obligation(
    command: RecognizePatentTermCompensationRequestObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizePatentTermCompensationRequestObligationCommand:
        _patent_term_compensation_request_invalid("command")
    source_command = RecognizeIcLayoutRegistrationFiledObligationCommand(
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_evidence_version_id=command.source_evidence_version_id,
    )
    _validate_ic_layout_command(
        source_command,
        invalid=_patent_term_compensation_request_invalid,
    )
    _validate_ic_layout_transaction(
        transaction,
        invalid=_patent_term_compensation_request_invalid,
        conflict=_patent_term_compensation_request_conflict,
    )

    with transaction.no_autoflush:
        activity = _ic_layout_source_activity(
            source_command,
            transaction,
            conflict=_patent_term_compensation_request_conflict,
        )
        evidence, document = _ic_layout_source_evidence(
            source_command,
            transaction,
            activity,
            conflict=_patent_term_compensation_request_conflict,
            expected_lineage_key=_PATENT_TERM_COMPENSATION_REQUEST_LINEAGE,
            expected_direction="OUT",
        )
        _validate_ic_layout_payload(
            source_command,
            activity,
            evidence,
            conflict=_patent_term_compensation_request_conflict,
        )
        _validate_ic_layout_reference(
            source_command,
            transaction,
            activity,
            evidence,
            conflict=_patent_term_compensation_request_conflict,
        )
        rate = get_patent_term_compensation_request_fee(
            GetPatentTermCompensationRequestFeeCommand(
                effective_date=activity.effective_at.date(),
            )
        )

    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="TERM_COMPENSATION_REQUESTED",
                due_date=None,
                currency="CNY",
                source_status=FeeSourceStatus.REVIEW_REQUIRED,
                lines=(
                    FeeObligationLineInput(
                        fee_code=rate.fee_code,
                        fee_name="专利权期限补偿请求费",
                        fee_year_key=0,
                        official_full_amount=rate.amount,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=rate.amount,
                        source_amount=None,
                        source_date=activity.effective_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    ),
                ),
                actor_id=activity.actor_id,
                idempotency_key=f"patent-term-compensation-request:{activity.id}",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _PATENT_TERM_COMPENSATION_REQUEST_SOURCE_ERRORS:
            _patent_term_compensation_request_conflict("obligation_source")
        raise


def _compensation_period_source(
    command: RecognizeCompensationPeriodAnnuityObligationCommand,
    transaction: Session,
) -> tuple[
    CaseActivityEvent,
    DocumentEvidenceVersion,
    Document,
    dict[str, object],
]:
    activity = transaction.get(CaseActivityEvent, command.source_activity_id)
    evidence = transaction.get(
        DocumentEvidenceVersion,
        command.source_evidence_version_id,
    )
    if activity is None or evidence is None:
        _compensation_period_annuity_conflict("source")
    assert isinstance(activity, CaseActivityEvent)
    assert isinstance(evidence, DocumentEvidenceVersion)
    document = transaction.get(Document, evidence.document_id)
    if document is None:
        _compensation_period_annuity_conflict("source_document")
    assert isinstance(document, Document)

    if (
        activity.case_id != command.case_id
        or activity.activity_type != "DOCUMENT_EVIDENCE_REVIEW_DECIDED"
        or activity.lane != "DOCUMENT"
        or activity.confirmation_status != "CONFIRMED"
        or activity.source_activity_id is not None
        or activity.supersedes_event_id is not None
        or activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
        or type(activity.effective_at) is not datetime
        or activity.effective_at.tzinfo is not None
        or activity.occurred_at != activity.effective_at
        or not _exact_text(activity.actor_id)
        or activity.actor_id != activity.reviewer_id
    ):
        _compensation_period_annuity_conflict("source_activity")
    if (
        evidence.case_id != command.case_id
        or document.case_id != command.case_id
        or document.direction != "IN"
        or evidence.lineage_key != _TERM_COMPENSATION_GRANTED_LINEAGE
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or evidence.current_identity_key
        != f"{command.case_id}|{_TERM_COMPENSATION_GRANTED_LINEAGE}"
        or not _exact_text(evidence.creator_id)
        or not _exact_text(evidence.reviewer_id)
        or evidence.creator_id == evidence.reviewer_id
        or evidence.reviewer_id != activity.reviewer_id
        or evidence.reviewed_at != activity.effective_at
        or type(evidence.content_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, evidence.content_hash) is None
        or type(document.doc_date) is not date
    ):
        _compensation_period_annuity_conflict("source_evidence")

    expected_review_payload = {
        "creator_id": evidence.creator_id,
        "decision": "APPROVE",
        "evidence_version_id": evidence.id,
        "previous_review_state": "PENDING",
        "review_state": "APPROVED",
        "reviewer_id": evidence.reviewer_id,
    }
    try:
        payload = json.loads(activity.payload_json)
    except (RecursionError, TypeError, ValueError):
        _compensation_period_annuity_conflict("source_activity_payload")
    if type(payload) is not dict:
        _compensation_period_annuity_conflict("source_activity_payload")
    source_snapshot = payload.get("source_snapshot")
    source_snapshot_hash = payload.get("source_snapshot_hash")
    if (
        type(source_snapshot) is not dict
        or type(source_snapshot_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, source_snapshot_hash) is None
        or source_snapshot_hash
        != f"sha256:{sha256(_canonical_json(source_snapshot).encode()).hexdigest()}"
        or payload
        != {
            **expected_review_payload,
            "source_snapshot": source_snapshot,
            "source_snapshot_hash": source_snapshot_hash,
        }
        or activity.payload_json != _canonical_json(payload)
    ):
        _compensation_period_annuity_conflict("source_activity_payload")

    references = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        )
    )
    if len(references) != 1:
        _compensation_period_annuity_conflict("source_activity_evidence")
    reference = references[0]
    if (
        reference.case_id != command.case_id
        or reference.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or reference.object_type != "DocumentEvidenceVersion"
        or reference.object_id != evidence.id
        or reference.content_hash != source_snapshot_hash
        or reference.captured_at != activity.effective_at
    ):
        _compensation_period_annuity_conflict("source_activity_evidence")

    current_snapshot, current_snapshot_hash = _compensation_period_review_snapshot(
        evidence,
        document,
    )
    if current_snapshot != source_snapshot or current_snapshot_hash != source_snapshot_hash:
        _compensation_period_annuity_conflict("source_snapshot")
    return activity, evidence, document, source_snapshot


def recognize_compensation_period_annuity_obligation(
    command: RecognizeCompensationPeriodAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult | None:
    if type(command) is not RecognizeCompensationPeriodAnnuityObligationCommand:
        _compensation_period_annuity_invalid("command")
    for field in ("case_id", "source_activity_id", "source_evidence_version_id"):
        value = getattr(command, field)
        if not _exact_text(value) or len(value) > 36:
            _compensation_period_annuity_invalid(field)
    if not isinstance(transaction, Session):
        _compensation_period_annuity_invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _compensation_period_annuity_conflict("transaction")

    with transaction.no_autoflush:
        activity, evidence, document, source_snapshot = _compensation_period_source(
            command,
            transaction,
        )
        complete_years = source_snapshot["complete_years"]
        decision_date = date.fromisoformat(source_snapshot["decision_date"])
        due_date = date.fromisoformat(source_snapshot["due_date"])
        try:
            rate = calculate_compensation_period_annuity_fee(
                CalculateCompensationPeriodAnnuityFeeCommand(
                    effective_date=decision_date,
                    complete_years=complete_years,
                )
            )
        except BusinessError:
            _compensation_period_annuity_conflict("decision_date")
    if rate.complete_years == 0:
        return None

    lines = tuple(
        FeeObligationLineInput(
            fee_code=rate.fee_code,
            fee_name="专利权补偿期年费",
            fee_year_key=year,
            official_full_amount=rate.unit_amount,
            reduction_ratio=Decimal("0.0000"),
            payable_amount=rate.unit_amount,
            source_amount=None,
            source_date=decision_date,
            difference_review_state=FeeDifferenceReviewState.MATCHED,
        )
        for year in range(1, rate.complete_years + 1)
    )
    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type="TERM_COMPENSATION_GRANTED",
                due_date=due_date,
                currency=rate.currency,
                source_status=FeeSourceStatus.VERIFIED,
                lines=lines,
                actor_id=evidence.reviewer_id,
                idempotency_key=f"compensation-period-annuity:{activity.id}",
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
    except BusinessError as exc:
        if exc.code in _PATENT_TERM_COMPENSATION_REQUEST_SOURCE_ERRORS:
            _compensation_period_annuity_conflict("obligation_source")
        raise


def _open_license_source(
    command: RecognizeOpenLicenseAnnuityObligationCommand,
    transaction: Session,
) -> tuple[
    CaseActivityEvent,
    DocumentEvidenceVersion,
    Document,
    dict[str, object],
]:
    activity = transaction.get(CaseActivityEvent, command.source_activity_id)
    evidence = transaction.get(
        DocumentEvidenceVersion,
        command.source_evidence_version_id,
    )
    if activity is None or evidence is None:
        _open_license_annuity_conflict("source")
    assert isinstance(activity, CaseActivityEvent)
    assert isinstance(evidence, DocumentEvidenceVersion)
    document = transaction.get(Document, evidence.document_id)
    if document is None:
        _open_license_annuity_conflict("source")
    assert isinstance(document, Document)
    if (
        activity.case_id != command.case_id
        or activity.activity_type != "DOCUMENT_EVIDENCE_REVIEW_DECIDED"
        or activity.lane != "DOCUMENT"
        or activity.confirmation_status != "CONFIRMED"
        or activity.source_activity_id is not None
        or activity.supersedes_event_id is not None
        or activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
        or type(activity.effective_at) is not datetime
        or activity.effective_at.tzinfo is not None
        or activity.occurred_at != activity.effective_at
        or not _exact_text(activity.actor_id)
        or activity.actor_id != activity.reviewer_id
    ):
        _open_license_annuity_conflict("source")
    if (
        evidence.case_id != command.case_id
        or document.case_id != command.case_id
        or document.direction != "IN"
        or evidence.lineage_key != _OPEN_LICENSE_PERIOD_LINEAGE
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or evidence.current_identity_key != f"{command.case_id}|{_OPEN_LICENSE_PERIOD_LINEAGE}"
        or not _exact_text(evidence.creator_id)
        or not _exact_text(evidence.reviewer_id)
        or evidence.creator_id == evidence.reviewer_id
        or evidence.reviewer_id != activity.reviewer_id
        or evidence.reviewed_at != activity.effective_at
    ):
        _open_license_annuity_conflict("source_evidence")
    try:
        payload = json.loads(activity.payload_json)
    except (RecursionError, TypeError, ValueError):
        _open_license_annuity_conflict("source")
    expected_review_payload = {
        "creator_id": evidence.creator_id,
        "decision": "APPROVE",
        "evidence_version_id": evidence.id,
        "previous_review_state": "PENDING",
        "review_state": "APPROVED",
        "reviewer_id": evidence.reviewer_id,
    }
    source_snapshot = payload.get("source_snapshot") if type(payload) is dict else None
    source_snapshot_hash = payload.get("source_snapshot_hash") if type(payload) is dict else None
    if (
        type(source_snapshot) is not dict
        or type(source_snapshot_hash) is not str
        or fullmatch(_CANONICAL_HASH_PATTERN, source_snapshot_hash) is None
        or source_snapshot_hash
        != f"sha256:{sha256(_canonical_json(source_snapshot).encode()).hexdigest()}"
        or payload
        != {
            **expected_review_payload,
            "source_snapshot": source_snapshot,
            "source_snapshot_hash": source_snapshot_hash,
        }
        or activity.payload_json != _canonical_json(payload)
    ):
        _open_license_annuity_conflict("source")
    references = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        )
    )
    if len(references) != 1:
        _open_license_annuity_conflict("source")
    reference = references[0]
    if (
        reference.case_id != command.case_id
        or reference.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or reference.object_type != "DocumentEvidenceVersion"
        or reference.object_id != evidence.id
        or reference.content_hash != source_snapshot_hash
        or reference.captured_at != activity.effective_at
    ):
        _open_license_annuity_conflict("source")
    current_snapshot, current_hash = _open_license_review_snapshot(evidence, document)
    if current_snapshot != source_snapshot or current_hash != source_snapshot_hash:
        _open_license_annuity_conflict("source_snapshot")
    return activity, evidence, document, source_snapshot


def _existing_open_license_annuity(
    command: RecognizeOpenLicenseAnnuityObligationCommand,
    transaction: Session,
    *,
    period_start: date,
    period_end: date,
) -> tuple[FeeObligation, FeeObligationLine]:
    obligation = transaction.get(FeeObligation, command.existing_obligation_id)
    if obligation is None:
        _open_license_annuity_conflict("existing_obligation")
    assert isinstance(obligation, FeeObligation)
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine).where(FeeObligationLine.obligation_id == obligation.id)
        )
    )
    tasks = tuple(
        transaction.scalars(
            select(AnnuityTask).where(AnnuityTask.fee_obligation_id == obligation.id)
        )
    )
    if (
        obligation.case_id != command.case_id
        or obligation.fee_domain != "GOV"
        or obligation.obligation_type != "FUTURE_ANNUITY"
        or obligation.obligation_status not in {"RECOGNIZED", "SUPERSEDED"}
        or obligation.currency != "CNY"
        or obligation.source_status != "VERIFIED"
        or type(obligation.due_date) is not date
        or len(lines) != 1
        or len(tasks) != 1
    ):
        _open_license_annuity_conflict("existing_obligation")
    if not period_start <= obligation.due_date <= period_end:
        _open_license_annuity_conflict("period")
    line = lines[0]
    task = tasks[0]
    case = transaction.get(Case, command.case_id)
    source_activity = transaction.get(CaseActivityEvent, task.source_activity_id)
    source_document = transaction.get(Document, task.source_document_id)
    source_evidence = transaction.get(
        DocumentEvidenceVersion,
        task.source_evidence_version_id,
    )
    reduction_lineages = tuple(
        transaction.scalars(
            select(FutureAnnuityReductionLineage).where(
                FutureAnnuityReductionLineage.annuity_task_id == task.id
            )
        )
    )
    if (
        line.case_id != command.case_id
        or line.source_activity_id != obligation.source_activity_id
        or line.fee_code not in _ORDINARY_ANNUITY_FEE_CODES
        or line.fee_year_key < 1
        or type(line.official_full_amount) is not Decimal
        or not line.official_full_amount.is_finite()
        or line.official_full_amount < 0
        or type(line.reduction_ratio) is not Decimal
        or line.reduction_ratio not in {Decimal("0.0000"), Decimal("0.7000"), Decimal("0.8500")}
        or type(line.payable_amount) is not Decimal
        or not line.payable_amount.is_finite()
        or line.payable_amount < 0
        or line.source_date != obligation.due_date
        or line.difference_review_state != "MATCHED"
        or case is None
        or line.fee_code
        != _OPEN_LICENSE_ANNUITY_FEE_CODE_BY_PATENT_CATEGORY.get(case.patent_category)
        or task.case_id != command.case_id
        or task.client_id != case.client_id
        or task.year_no != line.fee_year_key
        or task.due_date != obligation.due_date
        or task.source_activity_id != obligation.source_activity_id
        or task.source_document_id != obligation.source_document_id
        or task.fee_obligation_id != obligation.id
        or task.grant_fee_year_key != line.fee_year_key
        or len(reduction_lineages) != 1
    ):
        _open_license_annuity_conflict("existing_obligation")
    reduction_lineage = reduction_lineages[0]
    stored_ratio = line.reduction_ratio
    stored_provenance = reduction_lineage.reduction_input_provenance
    stored_approval_id = reduction_lineage.reduction_approval_id
    stored_zero = (
        type(stored_ratio) is Decimal
        and stored_ratio == Decimal("0.0000")
        and stored_ratio.as_tuple().exponent == -4
        and stored_provenance == "EXPLICIT_ENTRY"
        and stored_approval_id is None
    )
    stored_reduced = (
        type(stored_ratio) is Decimal
        and stored_ratio in {Decimal("0.7000"), Decimal("0.8500")}
        and stored_ratio.as_tuple().exponent == -4
        and stored_provenance in {"EXPLICIT_ENTRY", "CONFIRMED_MIGRATION"}
        and stored_approval_id is not None
    )
    if (
        reduction_lineage.fee_obligation_line_id != line.id
        or not (stored_zero or stored_reduced)
        or source_activity is None
        or source_document is None
        or source_evidence is None
        or source_activity.case_id != command.case_id
        or source_activity.activity_type != "GRANT_ANNOUNCEMENT_CONFIRMED"
        or source_activity.lane != "LIFECYCLE"
        or source_activity.confirmation_status != "CONFIRMED"
        or type(source_activity.effective_at) is not datetime
        or source_activity.effective_at.tzinfo is not None
        or source_document.case_id != command.case_id
        or source_document.direction != "IN"
        or source_evidence.case_id != command.case_id
        or source_evidence.document_id != source_document.id
        or source_evidence.role != "OFFICIAL_FINAL_PDF"
        or source_evidence.state != "FINAL"
        or source_evidence.review_state != "APPROVED"
        or type(source_evidence.reviewed_at) is not datetime
        or source_evidence.reviewed_at.tzinfo is not None
        or not _exact_text(source_evidence.creator_id)
        or not _exact_text(source_evidence.reviewer_id)
        or source_evidence.creator_id == source_evidence.reviewer_id
        or source_evidence.id != task.source_evidence_version_id
        or source_evidence.content_hash != task.source_evidence_content_hash
        or source_evidence.current_identity_key
        != f"{command.case_id}|{source_evidence.lineage_key}"
    ):
        _open_license_annuity_conflict("existing_obligation")
    source_references = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == source_activity.id
            )
        )
    )
    if len(source_references) != 1:
        _open_license_annuity_conflict("existing_obligation")
    source_reference = source_references[0]
    if (
        source_reference.case_id != command.case_id
        or source_reference.evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or source_reference.object_type != "DocumentEvidenceVersion"
        or source_reference.object_id != source_evidence.id
        or source_reference.content_hash != source_evidence.content_hash
        or source_reference.captured_at != source_activity.effective_at
    ):
        _open_license_annuity_conflict("existing_obligation")
    if stored_reduced:
        approval = transaction.get(FeeReductionApproval, stored_approval_id)
        if approval is None:
            _open_license_annuity_conflict("existing_obligation")
        try:
            fee_scope = json.loads(approval.fee_scope_snapshot)
            canonical_fee_scope = json.dumps(
                fee_scope,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            approval_scope_type = FeeReductionApprovalScopeType(approval.scope_type)
            stored_provenance_value = FeeReductionInputProvenance(stored_provenance)
        except (TypeError, ValueError):
            _open_license_annuity_conflict("existing_obligation")
        if (
            type(fee_scope) is not dict
            or set(fee_scope) != {"fee_codes", "schema"}
            or fee_scope.get("schema") != "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"
            or type(fee_scope.get("fee_codes")) is not list
            or not fee_scope["fee_codes"]
            or fee_scope["fee_codes"] != sorted(set(fee_scope["fee_codes"]))
            or any(not _exact_text(code) or len(code) > 64 for code in fee_scope["fee_codes"])
            or canonical_fee_scope != approval.fee_scope_snapshot
            or sha256(approval.fee_scope_snapshot.encode()).hexdigest() != approval.fee_scope_hash
        ):
            _open_license_annuity_conflict("existing_obligation")
        approval_source = transaction.get(
            DocumentEvidenceVersion,
            approval.source_evidence_version_id,
        )
        approval_context = FeeReductionApprovalContext(
            approval_id=approval.id,
            scope_type=approval_scope_type,
            case_id=approval.case_id,
            applicant_set_key=approval.applicant_set_key,
            reduction_ratio=approval.reduction_ratio,
            fee_codes=frozenset(fee_scope["fee_codes"]),
            fee_year_from=approval.fee_year_from,
            fee_year_to=approval.fee_year_to,
            effective_from=approval.effective_from,
            effective_to=approval.effective_to,
            source_evidence_version_id=approval.source_evidence_version_id,
            confirmation_status=approval.confirmation_status,
            is_current=bool(
                approval_source is not None
                and approval_source.case_id == command.case_id
                and approval_source.current_identity_key
                == f"{command.case_id}|{approval_source.lineage_key}"
            ),
        )
        try:
            validated_reduction = validate_annuity_fee_reduction(
                reduction_input=FeeReductionInput(
                    reduction_ratio=stored_ratio,
                    provenance=stored_provenance_value,
                ),
                context=FeeReductionEvaluationContext(
                    case_id=command.case_id,
                    applicant_set_key=None,
                    fee_code=line.fee_code,
                    fee_year_key=line.fee_year_key,
                    as_of_date=obligation.due_date,
                ),
                approval=approval_context,
                grant_fee_year_key=line.fee_year_key,
            )
        except (AnnuityReductionScopeError, FeeReductionValidationError):
            _open_license_annuity_conflict("existing_obligation")
        if (
            validated_reduction.reduction_ratio != stored_ratio
            or validated_reduction.provenance.value != stored_provenance
            or validated_reduction.approval_id != stored_approval_id
        ):
            _open_license_annuity_conflict("existing_obligation")
    rate_books = tuple(
        transaction.scalars(
            select(OfficialRateBook).where(
                OfficialRateBook.book_code == "CNIPA_PATENT_ANNUITY_20260330",
                OfficialRateBook.activation_status == "ACTIVE",
            )
        )
    )
    if len(rate_books) != 1:
        _open_license_annuity_conflict("existing_obligation")
    rate_book = rate_books[0]
    if (
        rate_book.source_authority != "CNIPA"
        or rate_book.approval_status != "APPROVED"
        or rate_book.source_snapshot != CNIPA_ANNUITY_SOURCE_SNAPSHOT
        or rate_book.source_snapshot_hash
        != sha256(CNIPA_ANNUITY_SOURCE_SNAPSHOT.encode()).hexdigest()
        or rate_book.current_identity_key != "CNIPA|CNIPA_PATENT_ANNUITY_20260330"
        or rate_book.effective_from > obligation.due_date
        or (rate_book.effective_to is not None and rate_book.effective_to < obligation.due_date)
    ):
        _open_license_annuity_conflict("existing_obligation")
    rates = tuple(
        transaction.scalars(
            select(FeeRate).where(
                FeeRate.official_rate_book_id == rate_book.id,
                FeeRate.fee_code == line.fee_code,
            )
        )
    )
    if len(rates) != 1:
        _open_license_annuity_conflict("existing_obligation")
    rate = rates[0]
    if (
        rate.enabled is not True
        or rate.fee_type != "GOV"
        or rate.currency != "CNY"
        or rate.calc_mode != "TIER"
        or rate.allow_reduction is not True
        or rate.calc_params is None
        or rate.calc_params != _OPEN_LICENSE_ANNUITY_CALC_PARAMS.get(line.fee_code)
        or rate.effective_from is None
        or rate.effective_from > obligation.due_date
        or (rate.effective_to is not None and rate.effective_to < obligation.due_date)
    ):
        _open_license_annuity_conflict("existing_obligation")
    try:
        official_amount = select_cnipa_annuity_amount(
            line.fee_code,
            rate.calc_params,
            line.fee_year_key,
        )
    except BusinessError:
        _open_license_annuity_conflict("existing_obligation")
    if official_amount != line.official_full_amount:
        _open_license_annuity_conflict("existing_obligation")
    return obligation, line


def recognize_open_license_annuity_obligation(
    command: RecognizeOpenLicenseAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if type(command) is not RecognizeOpenLicenseAnnuityObligationCommand:
        _open_license_annuity_invalid("command")
    for field in (
        "case_id",
        "source_activity_id",
        "source_evidence_version_id",
        "existing_obligation_id",
    ):
        value = getattr(command, field)
        if not _exact_text(value) or len(value) > 36:
            _open_license_annuity_invalid(field)
    if not isinstance(transaction, Session):
        _open_license_annuity_invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _open_license_annuity_conflict("transaction")

    with transaction.no_autoflush:
        activity, evidence, document, snapshot = _open_license_source(
            command,
            transaction,
        )
        period_start = date.fromisoformat(snapshot["period_start"])
        period_end = date.fromisoformat(snapshot["period_end"])
        obligation, line = _existing_open_license_annuity(
            command,
            transaction,
            period_start=period_start,
            period_end=period_end,
        )
        try:
            reduction = calculate_open_license_annuity_reduction(
                CalculateOpenLicenseAnnuityReductionCommand(
                    existing_reduction_ratio=line.reduction_ratio,
                )
            )
        except BusinessError:
            _open_license_annuity_conflict("existing_obligation")
        payable_amount = (line.official_full_amount * reduction.payable_ratio).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        replacement_line = FeeObligationLineInput(
            fee_code=line.fee_code,
            fee_name=line.fee_name,
            fee_year_key=line.fee_year_key,
            official_full_amount=line.official_full_amount,
            reduction_ratio=reduction.applied_reduction_ratio,
            payable_amount=payable_amount,
            source_amount=line.source_amount,
            source_date=line.source_date,
            difference_review_state=FeeDifferenceReviewState(line.difference_review_state),
        )
    try:
        return recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=command.case_id,
                source_activity_id=activity.id,
                source_document_id=document.id,
                fee_domain=FeeDomain.GOV,
                obligation_type=obligation.obligation_type,
                due_date=obligation.due_date,
                currency=obligation.currency,
                source_status=FeeSourceStatus.VERIFIED,
                lines=(replacement_line,),
                actor_id=evidence.reviewer_id,
                idempotency_key=(f"open-license-annuity:{activity.id}:{obligation.id}"),
                supersedes_obligation_id=obligation.id,
                supersede_reason="开放许可实施期间年费减缴",
            ),
            transaction,
        )
    except BusinessError:
        _open_license_annuity_conflict("existing_obligation")
