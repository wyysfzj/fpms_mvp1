from __future__ import annotations

import ast
import inspect
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import get_type_hints

import pytest

import app.modules.fees.fee_reduction as fee_reduction
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

EXPECTED_EXPORTS = (
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

EXPECTED_ENUM_VALUES = {
    FeeReductionInputProvenance: (
        ("EXPLICIT_ENTRY", "EXPLICIT_ENTRY"),
        ("CONFIRMED_MIGRATION", "CONFIRMED_MIGRATION"),
        ("LEGACY_UNVERIFIED", "LEGACY_UNVERIFIED"),
        ("UNKNOWN", "UNKNOWN"),
    ),
    FeeReductionApprovalScopeType: (
        ("CASE", "CASE"),
        ("APPLICANT_SET", "APPLICANT_SET"),
    ),
    FeeReductionErrorCode: (
        ("MISSING_REDUCTION_VALUE", "FEE_REDUCTION_MISSING_VALUE"),
        ("AMBIGUOUS_REDUCTION_PROVENANCE", "FEE_REDUCTION_AMBIGUOUS_PROVENANCE"),
        ("ILLEGAL_REDUCTION_VALUE", "FEE_REDUCTION_ILLEGAL_VALUE"),
        ("INVALID_EVALUATION_CONTEXT", "FEE_REDUCTION_INVALID_CONTEXT"),
        ("APPROVAL_REQUIRED", "FEE_REDUCTION_APPROVAL_REQUIRED"),
        ("APPROVAL_INVALID", "FEE_REDUCTION_APPROVAL_INVALID"),
        ("APPROVAL_NOT_CONFIRMED", "FEE_REDUCTION_APPROVAL_NOT_CONFIRMED"),
        ("APPROVAL_NOT_CURRENT", "FEE_REDUCTION_APPROVAL_NOT_CURRENT"),
        ("APPROVAL_SOURCE_MISSING", "FEE_REDUCTION_APPROVAL_SOURCE_MISSING"),
        ("APPROVAL_RATIO_MISMATCH", "FEE_REDUCTION_APPROVAL_RATIO_MISMATCH"),
        ("APPROVAL_SCOPE_MISMATCH", "FEE_REDUCTION_APPROVAL_SCOPE_MISMATCH"),
        ("APPROVAL_FEE_SCOPE_MISMATCH", "FEE_REDUCTION_APPROVAL_FEE_SCOPE_MISMATCH"),
        ("APPROVAL_YEAR_SCOPE_MISMATCH", "FEE_REDUCTION_APPROVAL_YEAR_SCOPE_MISMATCH"),
        (
            "APPROVAL_EFFECTIVE_SCOPE_MISMATCH",
            "FEE_REDUCTION_APPROVAL_EFFECTIVE_SCOPE_MISMATCH",
        ),
    ),
}

EXPECTED_FIELDS = {
    FeeReductionInput: (
        ("reduction_ratio", Decimal | None),
        ("provenance", FeeReductionInputProvenance),
    ),
    FeeReductionEvaluationContext: (
        ("case_id", str),
        ("applicant_set_key", str | None),
        ("fee_code", str),
        ("fee_year_key", int),
        ("as_of_date", date),
    ),
    FeeReductionApprovalContext: (
        ("approval_id", str),
        ("scope_type", FeeReductionApprovalScopeType),
        ("case_id", str | None),
        ("applicant_set_key", str | None),
        ("reduction_ratio", Decimal),
        ("fee_codes", frozenset[str]),
        ("fee_year_from", int | None),
        ("fee_year_to", int | None),
        ("effective_from", date),
        ("effective_to", date | None),
        ("source_evidence_version_id", str),
        ("confirmation_status", str),
        ("is_current", bool),
    ),
    FeeReductionValidationResult: (
        ("reduction_ratio", Decimal),
        ("payable_ratio", Decimal),
        ("provenance", FeeReductionInputProvenance),
        ("approval_id", str | None),
        ("source_evidence_version_id", str | None),
        ("scope_type", FeeReductionApprovalScopeType | None),
    ),
}


def _context(**overrides: object) -> FeeReductionEvaluationContext:
    values: dict[str, object] = {
        "case_id": "CASE-001",
        "applicant_set_key": "APPLICANTS-A",
        "fee_code": "APPLICATION_FEE",
        "fee_year_key": 0,
        "as_of_date": date(2026, 7, 13),
    }
    values.update(overrides)
    return FeeReductionEvaluationContext(**values)  # type: ignore[arg-type]


def _approval(**overrides: object) -> FeeReductionApprovalContext:
    values: dict[str, object] = {
        "approval_id": "APPROVAL-001",
        "scope_type": FeeReductionApprovalScopeType.CASE,
        "case_id": "CASE-001",
        "applicant_set_key": None,
        "reduction_ratio": Decimal("0.7000"),
        "fee_codes": frozenset({"APPLICATION_FEE"}),
        "fee_year_from": None,
        "fee_year_to": None,
        "effective_from": date(2026, 1, 1),
        "effective_to": date(2026, 12, 31),
        "source_evidence_version_id": "EVIDENCE-001",
        "confirmation_status": "CONFIRMED",
        "is_current": True,
    }
    values.update(overrides)
    return FeeReductionApprovalContext(**values)  # type: ignore[arg-type]


def _evaluate(
    ratio: object,
    *,
    provenance: object = FeeReductionInputProvenance.EXPLICIT_ENTRY,
    context: FeeReductionEvaluationContext | None = None,
    approval: FeeReductionApprovalContext | None = None,
) -> FeeReductionValidationResult:
    return validate_fee_reduction(
        reduction_input=FeeReductionInput(  # type: ignore[arg-type]
            reduction_ratio=ratio,
            provenance=provenance,
        ),
        context=context or _context(),
        approval=approval,
    )


def _assert_error(
    code: FeeReductionErrorCode,
    details: dict[str, str | int | bool | None],
    ratio: object = Decimal("0.7000"),
    *,
    provenance: object = FeeReductionInputProvenance.EXPLICIT_ENTRY,
    context: FeeReductionEvaluationContext | None = None,
    approval: FeeReductionApprovalContext | None = None,
) -> FeeReductionValidationError:
    with pytest.raises(FeeReductionValidationError) as caught:
        _evaluate(
            ratio,
            provenance=provenance,
            context=context,
            approval=approval,
        )

    assert caught.value.code is code
    assert caught.value.details == details
    assert str(caught.value) == code.value
    return caught.value


def test_public_contract_is_exact() -> None:
    assert fee_reduction.__all__ == EXPECTED_EXPORTS

    for enum_type, expected_members in EXPECTED_ENUM_VALUES.items():
        assert issubclass(enum_type, str)
        assert issubclass(enum_type, Enum)
        assert tuple((member.name, member.value) for member in enum_type) == expected_members

    for dto_type, expected_fields in EXPECTED_FIELDS.items():
        assert is_dataclass(dto_type)
        assert dto_type.__dataclass_params__.frozen is True
        assert tuple(field.name for field in fields(dto_type)) == tuple(
            field_name for field_name, _annotation in expected_fields
        )
        assert get_type_hints(dto_type) == dict(expected_fields)
        assert all(field.default is MISSING for field in fields(dto_type))
        assert all(field.default_factory is MISSING for field in fields(dto_type))
        assert "__slots__" in dto_type.__dict__

    signature = inspect.signature(validate_fee_reduction)
    assert tuple(signature.parameters) == ("reduction_input", "context", "approval")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(validate_fee_reduction) == {
        "reduction_input": FeeReductionInput,
        "context": FeeReductionEvaluationContext,
        "approval": FeeReductionApprovalContext | None,
        "return": FeeReductionValidationResult,
    }


def test_validation_error_exposes_defensive_detail_copies() -> None:
    original = {"field": "reduction_ratio"}
    error = FeeReductionValidationError(FeeReductionErrorCode.MISSING_REDUCTION_VALUE, original)

    original["field"] = "changed"
    exposed = error.details
    exposed["field"] = "also_changed"

    assert error.code is FeeReductionErrorCode.MISSING_REDUCTION_VALUE
    assert error.details == {"field": "reduction_ratio"}
    assert str(error) == FeeReductionErrorCode.MISSING_REDUCTION_VALUE.value


@pytest.mark.parametrize(
    "provenance",
    [
        FeeReductionInputProvenance.EXPLICIT_ENTRY,
        FeeReductionInputProvenance.CONFIRMED_MIGRATION,
    ],
)
def test_explicit_or_confirmed_zero_returns_unreduced_result_without_inspecting_approval(
    provenance: FeeReductionInputProvenance,
) -> None:
    malformed_unused_approval = _approval(approval_id="", reduction_ratio=Decimal("NaN"))

    result = _evaluate(
        Decimal("0.00"),
        provenance=provenance,
        approval=malformed_unused_approval,
    )

    assert result == FeeReductionValidationResult(
        reduction_ratio=Decimal("0.0000"),
        payable_ratio=Decimal("1.0000"),
        provenance=provenance,
        approval_id=None,
        source_evidence_version_id=None,
        scope_type=None,
    )


def test_missing_value_wins_before_provenance_validation() -> None:
    _assert_error(
        FeeReductionErrorCode.MISSING_REDUCTION_VALUE,
        {"field": "reduction_ratio"},
        None,
        provenance=FeeReductionInputProvenance.LEGACY_UNVERIFIED,
    )


@pytest.mark.parametrize(
    ("provenance", "detail"),
    [
        (FeeReductionInputProvenance.LEGACY_UNVERIFIED, "LEGACY_UNVERIFIED"),
        (FeeReductionInputProvenance.UNKNOWN, "UNKNOWN"),
        ("UNRECOGNIZED", "UNRECOGNIZED"),
    ],
)
def test_zero_with_ambiguous_or_unknown_provenance_fails_closed(
    provenance: object,
    detail: str,
) -> None:
    _assert_error(
        FeeReductionErrorCode.AMBIGUOUS_REDUCTION_PROVENANCE,
        {"provenance": detail},
        Decimal("0"),
        provenance=provenance,
    )


@pytest.mark.parametrize(
    ("value", "detail"),
    [
        ("0.7", "0.7"),
        (0.7, "0.7"),
        (True, "True"),
        (0, "0"),
        (Decimal("NaN"), "NaN"),
        (Decimal("Infinity"), "Infinity"),
        (Decimal("-Infinity"), "-Infinity"),
        (Decimal("0.15"), "0.15"),
        (Decimal("0.30"), "0.30"),
        (Decimal("1"), "1"),
        (Decimal("-0.1"), "-0.1"),
        (Decimal("1.1"), "1.1"),
        (Decimal("0.70001"), "0.70001"),
    ],
)
def test_illegal_values_are_rejected_without_coercion_or_rounding(
    value: object,
    detail: str,
) -> None:
    _assert_error(
        FeeReductionErrorCode.ILLEGAL_REDUCTION_VALUE,
        {"field": "reduction_ratio", "value": detail},
        value,
    )


@pytest.mark.parametrize(
    ("ratio", "normalized", "payable"),
    [
        (Decimal("0.70"), Decimal("0.7000"), Decimal("0.3000")),
        (Decimal("0.850"), Decimal("0.8500"), Decimal("0.1500")),
    ],
)
def test_equivalent_decimal_scales_normalize_to_four_places(
    ratio: Decimal,
    normalized: Decimal,
    payable: Decimal,
) -> None:
    approval = _approval(reduction_ratio=normalized)

    result = _evaluate(ratio, approval=approval)

    assert result.reduction_ratio == normalized
    assert result.payable_ratio == payable


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_id", ""),
        ("case_id", " CASE-001"),
        ("case_id", None),
        ("fee_code", ""),
        ("fee_code", "APPLICATION_FEE "),
        ("fee_code", 1),
        ("fee_year_key", True),
        ("fee_year_key", -1),
        ("fee_year_key", 1.0),
        ("as_of_date", datetime(2026, 7, 13)),
        ("as_of_date", "2026-07-13"),
    ],
)
def test_invalid_evaluation_context_fields_fail_in_the_frozen_surface(
    field: str,
    value: object,
) -> None:
    _assert_error(
        FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT,
        {"field": field},
        context=_context(**{field: value}),
    )


def test_evaluation_context_stops_at_the_first_invalid_field() -> None:
    _assert_error(
        FeeReductionErrorCode.INVALID_EVALUATION_CONTEXT,
        {"field": "case_id"},
        context=_context(case_id="", fee_code="", fee_year_key=-1, as_of_date="invalid"),
    )


def test_nonzero_reduction_requires_an_approval_snapshot() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_REQUIRED,
        {
            "reduction_ratio": "0.7000",
            "case_id": "CASE-001",
            "fee_code": "APPLICATION_FEE",
            "fee_year_key": 0,
            "as_of_date": "2026-07-13",
        },
    )


@pytest.mark.parametrize(
    ("field", "overrides"),
    [
        ("approval_id", {"approval_id": ""}),
        ("reduction_ratio", {"reduction_ratio": "0.7"}),
        ("reduction_ratio", {"reduction_ratio": Decimal("NaN")}),
        ("reduction_ratio", {"reduction_ratio": Decimal("0.15")}),
        ("fee_codes", {"fee_codes": set()}),
        ("fee_codes", {"fee_codes": frozenset()}),
        ("fee_codes", {"fee_codes": frozenset({" APPLICATION_FEE"})}),
        ("effective_from", {"effective_from": datetime(2026, 1, 1)}),
        ("effective_to", {"effective_to": datetime(2026, 12, 31)}),
        ("effective_to", {"effective_to": date(2025, 12, 31)}),
        ("fee_year_from", {"fee_year_from": True, "fee_year_to": 2}),
        ("fee_year_to", {"fee_year_from": 1, "fee_year_to": 0}),
        ("fee_year_to", {"fee_year_from": 2, "fee_year_to": 1}),
        ("scope_type", {"scope_type": "CASE"}),
        ("case_id/applicant_set_key", {"applicant_set_key": "APPLICANTS-A"}),
        ("confirmation_status", {"confirmation_status": None}),
        ("is_current", {"is_current": 1}),
    ],
)
def test_malformed_approval_snapshot_fails_with_the_exact_field(
    field: str,
    overrides: dict[str, object],
) -> None:
    approval = _approval(**overrides)

    _assert_error(
        FeeReductionErrorCode.APPROVAL_INVALID,
        {"approval_id": approval.approval_id, "field": field},
        approval=approval,
    )


def test_malformed_approval_stops_at_the_first_invalid_field() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_INVALID,
        {"approval_id": "", "field": "approval_id"},
        approval=_approval(
            approval_id="",
            reduction_ratio=Decimal("NaN"),
            fee_codes=frozenset(),
        ),
    )


def test_unconfirmed_approval_fails_with_exact_details() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_NOT_CONFIRMED,
        {"approval_id": "APPROVAL-001", "confirmation_status": "PENDING"},
        approval=_approval(confirmation_status="PENDING"),
    )


def test_noncurrent_approval_fails_with_exact_details() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_NOT_CURRENT,
        {"approval_id": "APPROVAL-001"},
        approval=_approval(is_current=False),
    )


@pytest.mark.parametrize("source", ["", " EVIDENCE-001", None])
def test_missing_or_malformed_source_evidence_fails_closed(source: object) -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_SOURCE_MISSING,
        {"approval_id": "APPROVAL-001", "field": "source_evidence_version_id"},
        approval=_approval(source_evidence_version_id=source),
    )


def test_approval_ratio_must_match_the_requested_ratio() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_RATIO_MISMATCH,
        {
            "approval_id": "APPROVAL-001",
            "requested_ratio": "0.7000",
            "approval_ratio": "0.8500",
        },
        approval=_approval(reduction_ratio=Decimal("0.850")),
    )


@pytest.mark.parametrize(
    ("context", "approval", "scope_type"),
    [
        (_context(case_id="CASE-002"), _approval(), "CASE"),
        (
            _context(applicant_set_key=None),
            _approval(
                scope_type=FeeReductionApprovalScopeType.APPLICANT_SET,
                case_id=None,
                applicant_set_key="APPLICANTS-A",
            ),
            "APPLICANT_SET",
        ),
        (
            _context(applicant_set_key="APPLICANTS-B"),
            _approval(
                scope_type=FeeReductionApprovalScopeType.APPLICANT_SET,
                case_id=None,
                applicant_set_key="APPLICANTS-A",
            ),
            "APPLICANT_SET",
        ),
    ],
)
def test_approval_identity_scope_must_match_exactly(
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext,
    scope_type: str,
) -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_SCOPE_MISMATCH,
        {"approval_id": "APPROVAL-001", "scope_type": scope_type},
        context=context,
        approval=approval,
    )


def test_fee_code_must_be_an_exact_approval_member() -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_FEE_SCOPE_MISMATCH,
        {"approval_id": "APPROVAL-001", "fee_code": "APPLICATION_FEE"},
        approval=_approval(fee_codes=frozenset({"ANNUITY_FEE"})),
    )


@pytest.mark.parametrize(
    ("context", "approval"),
    [
        (_context(fee_year_key=0), _approval(fee_year_from=1, fee_year_to=3)),
        (_context(fee_year_key=2), _approval()),
        (_context(fee_year_key=1), _approval(fee_year_from=2, fee_year_to=3)),
        (_context(fee_year_key=4), _approval(fee_year_from=2, fee_year_to=3)),
    ],
)
def test_year_scope_mismatch_fails_closed(
    context: FeeReductionEvaluationContext,
    approval: FeeReductionApprovalContext,
) -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_YEAR_SCOPE_MISMATCH,
        {"approval_id": "APPROVAL-001", "fee_year_key": context.fee_year_key},
        context=context,
        approval=approval,
    )


@pytest.mark.parametrize("fee_year_key", [2, 3])
def test_annual_year_scope_is_inclusive_at_both_boundaries(fee_year_key: int) -> None:
    result = _evaluate(
        Decimal("0.7000"),
        context=_context(fee_year_key=fee_year_key),
        approval=_approval(fee_year_from=2, fee_year_to=3),
    )

    assert result.payable_ratio == Decimal("0.3000")


@pytest.mark.parametrize("as_of_date", [date(2025, 12, 31), date(2027, 1, 1)])
def test_effective_date_outside_approval_interval_fails(as_of_date: date) -> None:
    _assert_error(
        FeeReductionErrorCode.APPROVAL_EFFECTIVE_SCOPE_MISMATCH,
        {"approval_id": "APPROVAL-001", "as_of_date": as_of_date.isoformat()},
        context=_context(as_of_date=as_of_date),
        approval=_approval(),
    )


@pytest.mark.parametrize("as_of_date", [date(2026, 1, 1), date(2026, 12, 31)])
def test_effective_date_interval_is_inclusive_at_both_boundaries(as_of_date: date) -> None:
    result = _evaluate(
        Decimal("0.7000"),
        context=_context(as_of_date=as_of_date),
        approval=_approval(),
    )

    assert result.payable_ratio == Decimal("0.3000")


def test_open_ended_effective_interval_accepts_later_dates() -> None:
    result = _evaluate(
        Decimal("0.7000"),
        context=_context(as_of_date=date(2030, 1, 1)),
        approval=_approval(effective_to=None),
    )

    assert result.payable_ratio == Decimal("0.3000")


@pytest.mark.parametrize(
    ("ratio", "payable"),
    [
        (Decimal("0.7000"), Decimal("0.3000")),
        (Decimal("0.8500"), Decimal("0.1500")),
    ],
)
def test_matching_case_approval_returns_source_backed_result(
    ratio: Decimal,
    payable: Decimal,
) -> None:
    result = _evaluate(ratio, approval=_approval(reduction_ratio=ratio))

    assert result == FeeReductionValidationResult(
        reduction_ratio=ratio,
        payable_ratio=payable,
        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        approval_id="APPROVAL-001",
        source_evidence_version_id="EVIDENCE-001",
        scope_type=FeeReductionApprovalScopeType.CASE,
    )


def test_matching_applicant_set_approval_returns_scoped_result() -> None:
    result = _evaluate(
        Decimal("0.8500"),
        approval=_approval(
            scope_type=FeeReductionApprovalScopeType.APPLICANT_SET,
            case_id=None,
            applicant_set_key="APPLICANTS-A",
            reduction_ratio=Decimal("0.8500"),
        ),
    )

    assert result.scope_type is FeeReductionApprovalScopeType.APPLICANT_SET
    assert result.payable_ratio == Decimal("0.1500")


def test_validation_does_not_mutate_any_input_dto() -> None:
    reduction_input = FeeReductionInput(
        reduction_ratio=Decimal("0.7000"),
        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
    )
    context = _context()
    approval = _approval()
    snapshots = (repr(reduction_input), repr(context), repr(approval))

    result = validate_fee_reduction(
        reduction_input=reduction_input,
        context=context,
        approval=approval,
    )

    assert result.payable_ratio == Decimal("0.3000")
    assert (repr(reduction_input), repr(context), repr(approval)) == snapshots
    with pytest.raises(FrozenInstanceError):
        reduction_input.reduction_ratio = Decimal("0")  # type: ignore[misc]


def test_pure_module_imports_only_standard_library_dependencies() -> None:
    module_path = inspect.getsourcefile(fee_reduction)
    assert module_path is not None
    tree = ast.parse(open(module_path, encoding="utf-8").read())
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert imported_roots <= {"__future__", "dataclasses", "datetime", "decimal", "enum"}


def test_adjacent_days_demonstrate_effective_boundary_without_clock_reads() -> None:
    approval = _approval(effective_from=date(2026, 7, 13), effective_to=date(2026, 7, 13))
    result = _evaluate(Decimal("0.7000"), approval=approval)
    assert result.payable_ratio == Decimal("0.3000")

    for as_of_date in (
        approval.effective_from - timedelta(days=1),
        approval.effective_to + timedelta(days=1),
    ):
        _assert_error(
            FeeReductionErrorCode.APPROVAL_EFFECTIVE_SCOPE_MISMATCH,
            {"approval_id": "APPROVAL-001", "as_of_date": as_of_date.isoformat()},
            context=_context(as_of_date=as_of_date),
            approval=approval,
        )
