"""B3: Auto-create FeeDraft when document registered with fee-enabled template."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from re import fullmatch
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion
from app.modules.documents.schemas import DocumentWizardFeeFinalRowIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
)
from app.modules.fees.obligation_service import recognize_obligation
from app.modules.fees.official_rate_book import (
    CalculateCompensationPeriodAnnuityFeeCommand,
    GetLayoutBibliographicChangeFeeCommand,
    GetLayoutExtensionFeeCommand,
    GetLayoutNonvoluntaryLicenseFeeCommand,
    GetLayoutReexaminationFeeCommand,
    GetLayoutRegistrationFeeCommand,
    GetLayoutRemunerationAdjudicationFeeCommand,
    GetLayoutRestorationFeeCommand,
    GetPatentTermCompensationRequestFeeCommand,
    calculate_compensation_period_annuity_fee,
    get_layout_bibliographic_change_fee,
    get_layout_extension_fee,
    get_layout_nonvoluntary_license_fee,
    get_layout_reexamination_fee,
    get_layout_registration_fee,
    get_layout_remuneration_adjudication_fee,
    get_layout_restoration_fee,
    get_patent_term_compensation_request_fee,
)

logger = logging.getLogger(__name__)


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
        and semantics.execution_behavior == "GRANT_NOTICE"
        and semantics.fee_trigger == "GRANT_FEE"
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


def _exact_text(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


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
