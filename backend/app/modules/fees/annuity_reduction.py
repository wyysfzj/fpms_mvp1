from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationResult,
    validate_fee_reduction,
)

__all__ = (
    "AnnuityReductionScopeError",
    "validate_annuity_fee_reduction",
)


class AnnuityReductionScopeError(ValueError):
    def __init__(self, code: str, details: Mapping[str, str | int]) -> None:
        self._code = code
        self._details = MappingProxyType(dict(details))
        super().__init__(code)

    @property
    def code(self) -> str:
        return self._code

    @property
    def details(self) -> Mapping[str, str | int]:
        return MappingProxyType(dict(self._details))


_ANNUITY_FEE_CODES = (
    "CN_ANNUITY_FEE_INV",
    "CN_ANNUITY_FEE_UM",
    "CN_ANNUITY_FEE_DES",
)
_ZERO = Decimal("0")
_LEGAL_RATIOS = (_ZERO, Decimal("0.7"), Decimal("0.85"))
_USABLE_PROVENANCE = (
    FeeReductionInputProvenance.EXPLICIT_ENTRY,
    FeeReductionInputProvenance.CONFIRMED_MIGRATION,
)


def _raise(code: str, details: Mapping[str, str | int]) -> None:
    raise AnnuityReductionScopeError(code, details)


def _delegate(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
) -> FeeReductionValidationResult:
    return validate_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
    )


def validate_annuity_fee_reduction(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
    grant_fee_year_key: int,
) -> FeeReductionValidationResult:
    if type(context.fee_year_key) is not int or context.fee_year_key < 1:
        _raise(
            "ANNUITY_REDUCTION_INVALID_CONTEXT",
            {"field": "context.fee_year_key"},
        )
    if type(grant_fee_year_key) is not int or grant_fee_year_key < 1:
        _raise(
            "ANNUITY_REDUCTION_INVALID_CONTEXT",
            {"field": "grant_fee_year_key"},
        )
    if context.fee_code not in _ANNUITY_FEE_CODES:
        _raise(
            "ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED",
            {"fee_code": context.fee_code},
        )

    ratio = reduction_input.reduction_ratio
    provenance = reduction_input.provenance
    if (
        ratio is None
        or not isinstance(ratio, Decimal)
        or not ratio.is_finite()
        or ratio not in _LEGAL_RATIOS
        or type(provenance) is not FeeReductionInputProvenance
        or provenance not in _USABLE_PROVENANCE
        or ratio == _ZERO
    ):
        return _delegate(
            reduction_input=reduction_input,
            context=context,
            approval=approval,
        )

    grant_relative_year = context.fee_year_key - grant_fee_year_key + 1
    if not 1 <= grant_relative_year <= 10:
        _raise(
            "ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE",
            {
                "fee_year_key": context.fee_year_key,
                "grant_fee_year_key": grant_fee_year_key,
                "grant_relative_year": grant_relative_year,
            },
        )

    return _delegate(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
    )
