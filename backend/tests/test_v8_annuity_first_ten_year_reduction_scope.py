from __future__ import annotations

import dis
import inspect
from collections.abc import Mapping
from datetime import date, timedelta
from decimal import Decimal
from typing import get_type_hints

import pytest

import app.modules.fees.annuity_reduction as annuity_reduction
from app.modules.fees.annuity_reduction import (
    AnnuityReductionScopeError,
    validate_annuity_fee_reduction,
)
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionErrorCode,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationError,
    FeeReductionValidationResult,
    validate_fee_reduction,
)

ANNUITY_FEE_CODES = (
    "CN_ANNUITY_FEE_INV",
    "CN_ANNUITY_FEE_UM",
    "CN_ANNUITY_FEE_DES",
)


def _reduction_input(
    ratio: object = Decimal("0.7000"),
    provenance: object = FeeReductionInputProvenance.EXPLICIT_ENTRY,
) -> FeeReductionInput:
    return FeeReductionInput(  # type: ignore[arg-type]
        reduction_ratio=ratio,
        provenance=provenance,
    )


def _context(**overrides: object) -> FeeReductionEvaluationContext:
    values: dict[str, object] = {
        "case_id": "CASE-ANNUITY-001",
        "applicant_set_key": "APPLICANTS-A",
        "fee_code": ANNUITY_FEE_CODES[0],
        "fee_year_key": 5,
        "as_of_date": date(2026, 7, 14),
    }
    values.update(overrides)
    return FeeReductionEvaluationContext(**values)  # type: ignore[arg-type]


def _approval(**overrides: object) -> FeeReductionApprovalContext:
    values: dict[str, object] = {
        "approval_id": "APPROVAL-ANNUITY-001",
        "scope_type": FeeReductionApprovalScopeType.CASE,
        "case_id": "CASE-ANNUITY-001",
        "applicant_set_key": None,
        "reduction_ratio": Decimal("0.7000"),
        "fee_codes": frozenset(ANNUITY_FEE_CODES),
        "fee_year_from": 1,
        "fee_year_to": 20,
        "effective_from": date(2026, 1, 1),
        "effective_to": date(2026, 12, 31),
        "source_evidence_version_id": "EVIDENCE-ANNUITY-001",
        "confirmation_status": "CONFIRMED",
        "is_current": True,
    }
    values.update(overrides)
    return FeeReductionApprovalContext(**values)  # type: ignore[arg-type]


def _wrapper_error(
    *,
    reduction_input: FeeReductionInput | None = None,
    context: FeeReductionEvaluationContext | None = None,
    approval: FeeReductionApprovalContext | None = None,
    grant_fee_year_key: object = 5,
) -> AnnuityReductionScopeError:
    with pytest.raises(AnnuityReductionScopeError) as caught:
        validate_annuity_fee_reduction(
            reduction_input=reduction_input or _reduction_input(),
            context=context or _context(),
            approval=approval,
            grant_fee_year_key=grant_fee_year_key,  # type: ignore[arg-type]
        )
    return caught.value


def _assert_preserves_base_error(
    *,
    reduction_input: FeeReductionInput,
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext | None,
    grant_fee_year_key: int,
) -> FeeReductionValidationError:
    with pytest.raises(FeeReductionValidationError) as expected:
        validate_fee_reduction(
            reduction_input=reduction_input,
            context=context,
            approval=approval,
        )

    with pytest.raises(FeeReductionValidationError) as actual:
        validate_annuity_fee_reduction(
            reduction_input=reduction_input,
            context=context,
            approval=approval,
            grant_fee_year_key=grant_fee_year_key,
        )

    assert type(actual.value) is type(expected.value)
    assert actual.value.code is expected.value.code
    assert actual.value.details == expected.value.details
    assert str(actual.value) == str(expected.value)
    return actual.value


def test_public_contract_error_surface_and_pure_boundary_are_exact() -> None:
    assert annuity_reduction.__all__ == (
        "AnnuityReductionScopeError",
        "validate_annuity_fee_reduction",
    )
    assert issubclass(AnnuityReductionScopeError, ValueError)

    signature = inspect.signature(validate_annuity_fee_reduction)
    assert tuple(signature.parameters) == (
        "reduction_input",
        "context",
        "approval",
        "grant_fee_year_key",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(validate_annuity_fee_reduction) == {
        "reduction_input": FeeReductionInput,
        "context": FeeReductionEvaluationContext,
        "approval": FeeReductionApprovalContext | None,
        "grant_fee_year_key": int,
        "return": FeeReductionValidationResult,
    }

    error = _wrapper_error(context=_context(fee_year_key=0))
    assert error.code == "ANNUITY_REDUCTION_INVALID_CONTEXT"
    assert type(error.code) is str
    assert str(error) == error.code
    with pytest.raises(AttributeError):
        error.code = "CHANGED"  # type: ignore[misc]

    details = error.details
    assert isinstance(details, Mapping)
    assert details == {"field": "context.fee_year_key"}
    with pytest.raises(TypeError):
        details["field"] = "changed"  # type: ignore[index]
    assert error.details == {"field": "context.fee_year_key"}

    owned_functions = (
        value
        for value in vars(annuity_reduction).values()
        if inspect.isfunction(value) and value.__module__ == annuity_reduction.__name__
    )
    loaded_names = {
        instruction.argval
        for function in owned_functions
        for instruction in dis.get_instructions(function)
        if instruction.opname.startswith("LOAD_")
    }
    assert loaded_names.isdisjoint(
        {
            "Session",
            "commit",
            "flush",
            "select",
            "open",
            "Path",
            "requests",
            "httpx",
            "datetime",
            "time",
            "now",
            "utcnow",
            "logging",
            "logger",
            "round",
            "quantize",
        }
    )
    assert inspect.iscoroutinefunction(validate_annuity_fee_reduction) is False
    assert inspect.isgeneratorfunction(validate_annuity_fee_reduction) is False


@pytest.mark.parametrize("fee_year_key", [True, 1.0, "1", None, 0, -1])
def test_invalid_context_fee_year_key_wins_first(fee_year_key: object) -> None:
    error = _wrapper_error(
        reduction_input=_reduction_input(None, FeeReductionInputProvenance.UNKNOWN),
        context=_context(fee_code="UNSUPPORTED", fee_year_key=fee_year_key),
        grant_fee_year_key=0,
    )

    assert error.code == "ANNUITY_REDUCTION_INVALID_CONTEXT"
    assert error.details == {"field": "context.fee_year_key"}


@pytest.mark.parametrize("grant_fee_year_key", [True, 1.0, "1", None, 0, -1])
def test_invalid_grant_fee_year_key_wins_before_fee_and_ratio(
    grant_fee_year_key: object,
) -> None:
    error = _wrapper_error(
        reduction_input=_reduction_input(None, FeeReductionInputProvenance.UNKNOWN),
        context=_context(fee_code="UNSUPPORTED"),
        grant_fee_year_key=grant_fee_year_key,
    )

    assert error.code == "ANNUITY_REDUCTION_INVALID_CONTEXT"
    assert error.details == {"field": "grant_fee_year_key"}


@pytest.mark.parametrize("fee_code", ["APPLICATION_FEE", "CN_ANNUITY_FEE_INV ", ""])
def test_unsupported_fee_code_wins_before_ratio_window_and_approval(fee_code: str) -> None:
    context = _context(fee_code=fee_code, fee_year_key=20)
    error = _wrapper_error(
        reduction_input=_reduction_input(None, FeeReductionInputProvenance.UNKNOWN),
        context=context,
        approval=None,
        grant_fee_year_key=1,
    )

    assert error.code == "ANNUITY_REDUCTION_FEE_CODE_UNSUPPORTED"
    assert error.details == {"fee_code": fee_code}


@pytest.mark.parametrize("fee_code", ANNUITY_FEE_CODES)
def test_each_exact_annuity_fee_code_delegates_successfully(fee_code: str) -> None:
    context = _context(fee_code=fee_code)
    approval = _approval(fee_codes=frozenset({fee_code}))

    result = validate_annuity_fee_reduction(
        reduction_input=_reduction_input(),
        context=context,
        approval=approval,
        grant_fee_year_key=5,
    )

    assert result == validate_fee_reduction(
        reduction_input=_reduction_input(),
        context=context,
        approval=approval,
    )


@pytest.mark.parametrize("ratio", [Decimal("0.7"), Decimal("0.85")])
@pytest.mark.parametrize("grant_relative_year", [1, 10])
def test_both_nonzero_ratios_accept_inclusive_first_and_tenth_years(
    ratio: Decimal,
    grant_relative_year: int,
) -> None:
    grant_fee_year_key = 4
    fee_year_key = grant_fee_year_key + grant_relative_year - 1
    context = _context(fee_year_key=fee_year_key)
    reduction_input = _reduction_input(ratio)
    approval = _approval(reduction_ratio=ratio)

    result = validate_annuity_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
        grant_fee_year_key=grant_fee_year_key,
    )

    assert result == validate_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
    )


@pytest.mark.parametrize(
    ("fee_year_key", "grant_fee_year_key", "grant_relative_year"),
    [(3, 4, 0), (14, 4, 11)],
)
def test_legal_nonzero_ratio_fails_closed_outside_first_ten_years(
    fee_year_key: int,
    grant_fee_year_key: int,
    grant_relative_year: int,
) -> None:
    error = _wrapper_error(
        context=_context(fee_year_key=fee_year_key),
        approval=_approval(),
        grant_fee_year_key=grant_fee_year_key,
    )

    assert error.code == "ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE"
    assert error.details == {
        "fee_year_key": fee_year_key,
        "grant_fee_year_key": grant_fee_year_key,
        "grant_relative_year": grant_relative_year,
    }


def test_legal_zero_delegates_outside_window_and_returns_base_result_unchanged() -> None:
    reduction_input = _reduction_input(Decimal("0.000"))
    context = _context(fee_year_key=20)
    malformed_unused_approval = _approval(
        approval_id="",
        reduction_ratio=Decimal("NaN"),
    )
    snapshots = (
        repr(reduction_input),
        repr(context),
        repr(malformed_unused_approval),
    )

    result = validate_annuity_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=malformed_unused_approval,
        grant_fee_year_key=1,
    )

    assert result == validate_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=malformed_unused_approval,
    )
    assert result == FeeReductionValidationResult(
        reduction_ratio=Decimal("0.0000"),
        payable_ratio=Decimal("1.0000"),
        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        approval_id=None,
        source_evidence_version_id=None,
        scope_type=None,
    )
    assert (
        repr(reduction_input),
        repr(context),
        repr(malformed_unused_approval),
    ) == snapshots


@pytest.mark.parametrize(
    ("ratio", "provenance", "expected_code"),
    [
        (
            None,
            FeeReductionInputProvenance.EXPLICIT_ENTRY,
            FeeReductionErrorCode.MISSING_REDUCTION_VALUE,
        ),
        (
            "0.7",
            FeeReductionInputProvenance.EXPLICIT_ENTRY,
            FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
        ),
        (
            Decimal("NaN"),
            FeeReductionInputProvenance.EXPLICIT_ENTRY,
            FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
        ),
        (
            Decimal("0.6"),
            FeeReductionInputProvenance.EXPLICIT_ENTRY,
            FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
        ),
        (
            Decimal("0.7"),
            FeeReductionInputProvenance.LEGACY_UNVERIFIED,
            FeeReductionErrorCode.AMBIGUOUS_REDUCTION_PROVENANCE,
        ),
        (Decimal("0.85"), "EXPLICIT_ENTRY", FeeReductionErrorCode.AMBIGUOUS_REDUCTION_PROVENANCE),
    ],
)
def test_invalid_ratio_or_provenance_preserves_base_error_outside_window(
    ratio: object,
    provenance: object,
    expected_code: FeeReductionErrorCode,
) -> None:
    error = _assert_preserves_base_error(
        reduction_input=_reduction_input(ratio, provenance),
        context=_context(fee_year_key=20),
        approval=None,
        grant_fee_year_key=1,
    )

    assert error.code is expected_code


def test_missing_approval_inside_window_preserves_base_error() -> None:
    error = _assert_preserves_base_error(
        reduction_input=_reduction_input(),
        context=_context(),
        approval=None,
        grant_fee_year_key=5,
    )

    assert error.code is FeeReductionErrorCode.APPROVAL_REQUIRED


@pytest.mark.parametrize(
    ("approval_overrides", "expected_code"),
    [
        ({"approval_id": ""}, FeeReductionErrorCode.APPROVAL_INVALID),
        ({"confirmation_status": "PENDING"}, FeeReductionErrorCode.APPROVAL_NOT_CONFIRMED),
        ({"is_current": False}, FeeReductionErrorCode.APPROVAL_NOT_CURRENT),
        ({"source_evidence_version_id": ""}, FeeReductionErrorCode.APPROVAL_SOURCE_MISSING),
        ({"reduction_ratio": Decimal("0.85")}, FeeReductionErrorCode.APPROVAL_RATIO_MISMATCH),
        ({"case_id": "OTHER-CASE"}, FeeReductionErrorCode.APPROVAL_SCOPE_MISMATCH),
        (
            {"fee_codes": frozenset({"OTHER_FEE"})},
            FeeReductionErrorCode.APPROVAL_FEE_SCOPE_MISMATCH,
        ),
        (
            {"fee_year_from": 1, "fee_year_to": 4},
            FeeReductionErrorCode.APPROVAL_YEAR_SCOPE_MISMATCH,
        ),
        (
            {"effective_from": date(2026, 7, 15)},
            FeeReductionErrorCode.APPROVAL_EFFECTIVE_SCOPE_MISMATCH,
        ),
    ],
)
def test_inside_window_preserves_every_base_approval_and_scope_error(
    approval_overrides: dict[str, object],
    expected_code: FeeReductionErrorCode,
) -> None:
    error = _assert_preserves_base_error(
        reduction_input=_reduction_input(),
        context=_context(),
        approval=_approval(**approval_overrides),
        grant_fee_year_key=5,
    )

    assert error.code is expected_code


def test_success_returns_the_exact_base_object_and_never_mutates_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reduction_input = _reduction_input(Decimal("0.85"))
    context = _context()
    approval = _approval(reduction_ratio=Decimal("0.85"))
    expected = FeeReductionValidationResult(
        reduction_ratio=Decimal("0.8500"),
        payable_ratio=Decimal("0.1500"),
        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        approval_id="APPROVAL-ANNUITY-001",
        source_evidence_version_id="EVIDENCE-ANNUITY-001",
        scope_type=FeeReductionApprovalScopeType.CASE,
    )
    calls: list[
        tuple[FeeReductionInput, FeeReductionEvaluationContext, FeeReductionApprovalContext | None]
    ] = []
    snapshots = (repr(reduction_input), repr(context), repr(approval))

    def recording_validator(
        *,
        reduction_input: FeeReductionInput,
        context: FeeReductionEvaluationContext,
        approval: FeeReductionApprovalContext | None,
    ) -> FeeReductionValidationResult:
        calls.append((reduction_input, context, approval))
        return expected

    monkeypatch.setattr(annuity_reduction, "validate_fee_reduction", recording_validator)

    result = validate_annuity_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
        grant_fee_year_key=5,
    )

    assert result is expected
    assert calls == [(reduction_input, context, approval)]
    assert (repr(reduction_input), repr(context), repr(approval)) == snapshots


def test_effective_date_boundary_is_caller_supplied_without_clock_reads() -> None:
    context = _context(as_of_date=date(2026, 7, 14))
    approval = _approval(effective_from=date(2026, 7, 14), effective_to=date(2026, 7, 14))
    result = validate_annuity_fee_reduction(
        reduction_input=_reduction_input(),
        context=context,
        approval=approval,
        grant_fee_year_key=5,
    )
    assert result.approval_id == "APPROVAL-ANNUITY-001"

    outside_context = _context(as_of_date=context.as_of_date + timedelta(days=1))
    error = _assert_preserves_base_error(
        reduction_input=_reduction_input(),
        context=outside_context,
        approval=approval,
        grant_fee_year_key=5,
    )
    assert error.code is FeeReductionErrorCode.APPROVAL_EFFECTIVE_SCOPE_MISMATCH
