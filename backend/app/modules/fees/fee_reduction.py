from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

__all__ = (
    "FeeReductionInputProvenance",
    "FeeReductionApprovalScopeType",
    "FeeReductionErrorCode",
    "FeeReductionInput",
    "FeeReductionEvaluationContext",
    "FeeReductionApprovalContext",
    "FeeReductionValidationResult",
    "FeeReductionValidationError",
    "validate_fee_reduction",
)


class FeeReductionInputProvenance(str, Enum):
    EXPLICIT_ENTRY = "EXPLICIT_ENTRY"
    CONFIRMED_MIGRATION = "CONFIRMED_MIGRATION"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"
    UNKNOWN = "UNKNOWN"


class FeeReductionApprovalScopeType(str, Enum):
    CASE = "CASE"
    APPLICANT_SET = "APPLICANT_SET"


class FeeReductionErrorCode(str, Enum):
    MISSING_REDUCTION_VALUE = "FEE_REDUCTION_MISSING_VALUE"
    AMBIGUOUS_REDUCTION_PROVENANCE = "FEE_REDUCTION_AMBIGUOUS_PROVENANCE"
    ILLEGAL_REDUCTION_VALUE = "FEE_REDUCTION_ILLEGAL_VALUE"
    INVALID_EVALUATION_CONTEXT = "FEE_REDUCTION_INVALID_CONTEXT"
    APPROVAL_REQUIRED = "FEE_REDUCTION_APPROVAL_REQUIRED"
    APPROVAL_INVALID = "FEE_REDUCTION_APPROVAL_INVALID"
    APPROVAL_NOT_CONFIRMED = "FEE_REDUCTION_APPROVAL_NOT_CONFIRMED"
    APPROVAL_NOT_CURRENT = "FEE_REDUCTION_APPROVAL_NOT_CURRENT"
    APPROVAL_SOURCE_MISSING = "FEE_REDUCTION_APPROVAL_SOURCE_MISSING"
    APPROVAL_RATIO_MISMATCH = "FEE_REDUCTION_APPROVAL_RATIO_MISMATCH"
    APPROVAL_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_SCOPE_MISMATCH"
    APPROVAL_FEE_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_FEE_SCOPE_MISMATCH"
    APPROVAL_YEAR_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_YEAR_SCOPE_MISMATCH"
    APPROVAL_EFFECTIVE_SCOPE_MISMATCH = "FEE_REDUCTION_APPROVAL_EFFECTIVE_SCOPE_MISMATCH"


@dataclass(frozen=True, slots=True)
class FeeReductionInput:
    reduction_ratio: Decimal | None
    provenance: FeeReductionInputProvenance


@dataclass(frozen=True, slots=True)
class FeeReductionEvaluationContext:
    case_id: str
    applicant_set_key: str | None
    fee_code: str
    fee_year_key: int
    as_of_date: date


@dataclass(frozen=True, slots=True)
class FeeReductionApprovalContext:
    approval_id: str
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: frozenset[str]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    is_current: bool


@dataclass(frozen=True, slots=True)
class FeeReductionValidationResult:
    reduction_ratio: Decimal
    payable_ratio: Decimal
    provenance: FeeReductionInputProvenance
    approval_id: str | None
    source_evidence_version_id: str | None
    scope_type: FeeReductionApprovalScopeType | None


class FeeReductionValidationError(ValueError):
    def __init__(
        self,
        code: FeeReductionErrorCode,
        details: dict[str, str | int | bool | None],
    ) -> None:
        self.code = code
        self._details = dict(details)
        super().__init__(code.value)

    @property
    def details(self) -> dict[str, str | int | bool | None]:
        return dict(self._details)


_ZERO = Decimal("0.0000")
_SEVENTY = Decimal("0.7000")
_EIGHTY_FIVE = Decimal("0.8500")
_PAYABLE_BY_REDUCTION = {
    _ZERO: Decimal("1.0000"),
    _SEVENTY: Decimal("0.3000"),
    _EIGHTY_FIVE: Decimal("0.1500"),
}


def _raise(
    code: FeeReductionErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    raise FeeReductionValidationError(code, details)


def _is_nonblank_exact_string(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def _normalize_ratio(value: Decimal) -> Decimal | None:
    for normalized in _PAYABLE_BY_REDUCTION:
        if value == normalized:
            return normalized
    return None


def _approval_id_detail(approval: FeeReductionApprovalContext) -> str:
    return str(approval.approval_id)


def _raise_approval_invalid(
    approval: FeeReductionApprovalContext,
    field: str,
) -> None:
    _raise(
        FeeReductionErrorCode.APPROVAL_INVALID,
        {"approval_id": _approval_id_detail(approval), "field": field},
    )


def _validate_evaluation_context(context: FeeReductionEvaluationContext) -> None:
    if not _is_nonblank_exact_string(context.case_id):
        _raise(FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT, {"field": "case_id"})
    if not _is_nonblank_exact_string(context.fee_code):
        _raise(FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT, {"field": "fee_code"})
    if type(context.fee_year_key) is not int or context.fee_year_key < 0:
        _raise(FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT, {"field": "fee_year_key"})
    if type(context.as_of_date) is not date:
        _raise(FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT, {"field": "as_of_date"})


def _validate_approval_snapshot(approval: FeeReductionApprovalContext) -> Decimal:
    if not _is_nonblank_exact_string(approval.approval_id):
        _raise_approval_invalid(approval, "approval_id")

    approval_ratio = approval.reduction_ratio
    if not isinstance(approval_ratio, Decimal) or not approval_ratio.is_finite():
        _raise_approval_invalid(approval, "reduction_ratio")
    normalized_approval_ratio = _normalize_ratio(approval_ratio)
    if normalized_approval_ratio is None:
        _raise_approval_invalid(approval, "reduction_ratio")

    if (
        type(approval.fee_codes) is not frozenset
        or not approval.fee_codes
        or any(not _is_nonblank_exact_string(fee_code) for fee_code in approval.fee_codes)
    ):
        _raise_approval_invalid(approval, "fee_codes")

    if type(approval.effective_from) is not date:
        _raise_approval_invalid(approval, "effective_from")
    if approval.effective_to is not None and type(approval.effective_to) is not date:
        _raise_approval_invalid(approval, "effective_to")
    if approval.effective_to is not None and approval.effective_from > approval.effective_to:
        _raise_approval_invalid(approval, "effective_to")

    if approval.fee_year_from is None:
        if approval.fee_year_to is not None:
            _raise_approval_invalid(approval, "fee_year_from")
    elif type(approval.fee_year_from) is not int or approval.fee_year_from <= 0:
        _raise_approval_invalid(approval, "fee_year_from")

    if approval.fee_year_to is None:
        if approval.fee_year_from is not None:
            _raise_approval_invalid(approval, "fee_year_to")
    elif type(approval.fee_year_to) is not int or approval.fee_year_to <= 0:
        _raise_approval_invalid(approval, "fee_year_to")
    elif approval.fee_year_from is not None and approval.fee_year_from > approval.fee_year_to:
        _raise_approval_invalid(approval, "fee_year_to")

    if type(approval.scope_type) is not FeeReductionApprovalScopeType:
        _raise_approval_invalid(approval, "scope_type")
    if approval.scope_type is FeeReductionApprovalScopeType.CASE:
        scope_is_valid = _is_nonblank_exact_string(approval.case_id) and (
            approval.applicant_set_key is None
        )
    else:
        scope_is_valid = approval.case_id is None and _is_nonblank_exact_string(
            approval.applicant_set_key
        )
    if not scope_is_valid:
        _raise_approval_invalid(approval, "case_id/applicant_set_key")

    if type(approval.confirmation_status) is not str:
        _raise_approval_invalid(approval, "confirmation_status")
    if type(approval.is_current) is not bool:
        _raise_approval_invalid(approval, "is_current")

    return normalized_approval_ratio


def validate_fee_reduction(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
) -> FeeReductionValidationResult:
    reduction_ratio = reduction_input.reduction_ratio
    if reduction_ratio is None:
        _raise(
            FeeReductionErrorCode.MISSING_REDUCTION_VALUE,
            {"field": "reduction_ratio"},
        )
    if not isinstance(reduction_ratio, Decimal) or not reduction_ratio.is_finite():
        _raise(
            FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
            {"field": "reduction_ratio", "value": str(reduction_ratio)},
        )

    provenance = reduction_input.provenance
    if type(provenance) is not FeeReductionInputProvenance or provenance not in (
        FeeReductionInputProvenance.EXPLICIT_ENTRY,
        FeeReductionInputProvenance.CONFIRMED_MIGRATION,
    ):
        provenance_detail = (
            provenance.value if type(provenance) is FeeReductionInputProvenance else str(provenance)
        )
        _raise(
            FeeReductionErrorCode.AMBIGUOUS_REDUCTION_PROVENANCE,
            {"provenance": provenance_detail},
        )

    normalized_ratio = _normalize_ratio(reduction_ratio)
    if normalized_ratio is None:
        _raise(
            FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
            {"field": "reduction_ratio", "value": str(reduction_ratio)},
        )

    _validate_evaluation_context(context)

    if normalized_ratio == _ZERO:
        return FeeReductionValidationResult(
            reduction_ratio=_ZERO,
            payable_ratio=_PAYABLE_BY_REDUCTION[_ZERO],
            provenance=provenance,
            approval_id=None,
            source_evidence_version_id=None,
            scope_type=None,
        )

    if approval is None:
        _raise(
            FeeReductionErrorCode.APPROVAL_REQUIRED,
            {
                "reduction_ratio": str(normalized_ratio),
                "case_id": context.case_id,
                "fee_code": context.fee_code,
                "fee_year_key": context.fee_year_key,
                "as_of_date": context.as_of_date.isoformat(),
            },
        )

    normalized_approval_ratio = _validate_approval_snapshot(approval)

    approval_id = approval.approval_id
    if approval.confirmation_status != "CONFIRMED":
        _raise(
            FeeReductionErrorCode.APPROVAL_NOT_CONFIRMED,
            {
                "approval_id": approval_id,
                "confirmation_status": approval.confirmation_status,
            },
        )
    if approval.is_current is not True:
        _raise(FeeReductionErrorCode.APPROVAL_NOT_CURRENT, {"approval_id": approval_id})
    if not _is_nonblank_exact_string(approval.source_evidence_version_id):
        _raise(
            FeeReductionErrorCode.APPROVAL_SOURCE_MISSING,
            {"approval_id": approval_id, "field": "source_evidence_version_id"},
        )
    if normalized_approval_ratio != normalized_ratio:
        _raise(
            FeeReductionErrorCode.APPROVAL_RATIO_MISMATCH,
            {
                "approval_id": approval_id,
                "requested_ratio": str(normalized_ratio),
                "approval_ratio": str(normalized_approval_ratio),
            },
        )

    if approval.scope_type is FeeReductionApprovalScopeType.CASE:
        scope_matches = approval.case_id == context.case_id
    else:
        scope_matches = (
            context.applicant_set_key is not None
            and approval.applicant_set_key == context.applicant_set_key
        )
    if not scope_matches:
        _raise(
            FeeReductionErrorCode.APPROVAL_SCOPE_MISMATCH,
            {"approval_id": approval_id, "scope_type": approval.scope_type.value},
        )

    if context.fee_code not in approval.fee_codes:
        _raise(
            FeeReductionErrorCode.APPROVAL_FEE_SCOPE_MISMATCH,
            {"approval_id": approval_id, "fee_code": context.fee_code},
        )

    if context.fee_year_key == 0:
        year_matches = approval.fee_year_from is None and approval.fee_year_to is None
    else:
        year_matches = (
            approval.fee_year_from is not None
            and approval.fee_year_to is not None
            and approval.fee_year_from <= context.fee_year_key <= approval.fee_year_to
        )
    if not year_matches:
        _raise(
            FeeReductionErrorCode.APPROVAL_YEAR_SCOPE_MISMATCH,
            {"approval_id": approval_id, "fee_year_key": context.fee_year_key},
        )

    if context.as_of_date < approval.effective_from or (
        approval.effective_to is not None and context.as_of_date > approval.effective_to
    ):
        _raise(
            FeeReductionErrorCode.APPROVAL_EFFECTIVE_SCOPE_MISMATCH,
            {"approval_id": approval_id, "as_of_date": context.as_of_date.isoformat()},
        )

    return FeeReductionValidationResult(
        reduction_ratio=normalized_ratio,
        payable_ratio=_PAYABLE_BY_REDUCTION[normalized_ratio],
        provenance=provenance,
        approval_id=approval_id,
        source_evidence_version_id=approval.source_evidence_version_id,
        scope_type=approval.scope_type,
    )
