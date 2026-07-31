from __future__ import annotations

import inspect
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime, timezone
from decimal import ROUND_DOWN, Context, Decimal, Inexact, Rounded, localcontext
from enum import Enum
from typing import get_type_hints

import pytest

import app.modules.fees.pct_policy as pct_policy
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
)
from app.modules.fees.pct_policy import (
    ConfirmedPctEvidence,
    EvaluatePctNationalStageFeePolicyCommand,
    EvaluatePctNationalStageFeePolicyResult,
    PctFeePolicyDisposition,
    PctFeePolicyError,
    PctFeePolicyErrorCode,
    PctReductionContext,
    evaluate_pct_national_stage_fee_policy,
    validate_confirmed_pct_evidence_set,
)

APPLICATION_EXEMPT_FEE_CODES = (
    "CN_INV_APPLICATION_FEE",
    "CN_UM_APPLICATION_FEE",
    "CN_EXCESS_CLAIM_FEE",
    "CN_SPEC_PAGE_31_300_FEE",
    "CN_SPEC_PAGE_301_PLUS_FEE",
)
REEXAMINATION_FEE_CODES = (
    "CN_REEXAM_FEE_INV",
    "CN_REEXAM_FEE_UM",
    "CN_REEXAM_FEE_DES",
)
ANNUITY_FEE_CODES = (
    "CN_ANNUITY_FEE_INV",
    "CN_ANNUITY_FEE_UM",
    "CN_ANNUITY_FEE_DES",
)
EFFECTIVE_ON = date(2024, 8, 6)
HASH_A = f"sha256:{'a' * 64}"
HASH_B = f"sha256:{'b' * 64}"
HASH_C = f"sha256:{'c' * 64}"


def _evidence(document_type: str, **overrides: object) -> ConfirmedPctEvidence:
    suffix = {
        "CNIPA_RO_RECEIPT": "RO",
        "CNIPA_ISR": "ISR",
        "CNIPA_IPRP": "IPRP",
    }.get(document_type, "UNKNOWN")
    values: dict[str, object] = {
        "case_id": "CASE-PCT-001",
        "source_document_id": f"DOC-{suffix}",
        "evidence_version_id": f"VERSION-{suffix}",
        "content_hash": {
            "RO": HASH_A,
            "ISR": HASH_B,
            "IPRP": HASH_C,
            "UNKNOWN": f"sha256:{'d' * 64}",
        }[suffix],
        "lineage_key": f"LINEAGE-{suffix}",
        "current_identity_key": f"CASE-PCT-001|LINEAGE-{suffix}",
        "issuer": "CNIPA",
        "document_type": document_type,
        "issued_on": EFFECTIVE_ON,
        "role": "OFFICIAL_FINAL_PDF",
        "state": "FINAL",
        "review_state": "APPROVED",
        "creator_id": f"CREATOR-{suffix}",
        "reviewer_id": f"REVIEWER-{suffix}",
        "reviewed_at": datetime(2024, 8, 6, 12, 30),
    }
    values.update(overrides)
    return ConfirmedPctEvidence(**values)  # type: ignore[arg-type]


def _command(**overrides: object) -> EvaluatePctNationalStageFeePolicyCommand:
    values: dict[str, object] = {
        "case_id": "CASE-PCT-001",
        "fee_code": APPLICATION_EXEMPT_FEE_CODES[0],
        "full_amount": Decimal("100.00"),
        "effective_on": EFFECTIVE_ON,
        "evidence": (
            _evidence("CNIPA_RO_RECEIPT"),
            _evidence("CNIPA_ISR"),
        ),
        "reduction_context": None,
    }
    values.update(overrides)
    return EvaluatePctNationalStageFeePolicyCommand(**values)  # type: ignore[arg-type]


def _approval(
    fee_code: str,
    *,
    ratio: Decimal = Decimal("0.7000"),
) -> FeeReductionApprovalContext:
    annual = fee_code in ANNUITY_FEE_CODES
    return FeeReductionApprovalContext(
        approval_id="APPROVAL-PCT-001",
        scope_type=FeeReductionApprovalScopeType.CASE,
        case_id="CASE-PCT-001",
        applicant_set_key=None,
        reduction_ratio=ratio,
        fee_codes=frozenset({fee_code}),
        fee_year_from=1 if annual else None,
        fee_year_to=20 if annual else None,
        effective_from=EFFECTIVE_ON,
        effective_to=None,
        source_evidence_version_id="REDUCTION-EVIDENCE-001",
        confirmation_status="CONFIRMED",
        is_current=True,
    )


def _reduction_context(
    fee_code: str,
    *,
    ratio: Decimal = Decimal("0.7000"),
    fee_year_key: int = 0,
    grant_fee_year_key: int | None = None,
    approval: FeeReductionApprovalContext | None = None,
    as_of_date: date = EFFECTIVE_ON,
) -> PctReductionContext:
    return PctReductionContext(
        reduction_input=FeeReductionInput(
            reduction_ratio=ratio,
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        evaluation_context=FeeReductionEvaluationContext(
            case_id="CASE-PCT-001",
            applicant_set_key=None,
            fee_code=fee_code,
            fee_year_key=fee_year_key,
            as_of_date=as_of_date,
        ),
        approval=approval if approval is not None else _approval(fee_code, ratio=ratio),
        grant_fee_year_key=grant_fee_year_key,
    )


def _assert_error(
    command: object,
    code: PctFeePolicyErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    with pytest.raises(PctFeePolicyError) as caught:
        evaluate_pct_national_stage_fee_policy(command)  # type: ignore[arg-type]
    assert caught.value.code is code
    assert caught.value.details == details
    assert str(caught.value) == code.value


def test_public_policy_contract_is_exact_and_has_no_superseded_entry_date() -> None:
    expected_fields = {
        ConfirmedPctEvidence: (
            ("case_id", str),
            ("source_document_id", str),
            ("evidence_version_id", str),
            ("content_hash", str),
            ("lineage_key", str),
            ("current_identity_key", str),
            ("issuer", str),
            ("document_type", str),
            ("issued_on", date),
            ("role", str),
            ("state", str),
            ("review_state", str),
            ("creator_id", str),
            ("reviewer_id", str),
            ("reviewed_at", datetime),
        ),
        PctReductionContext: (
            ("reduction_input", FeeReductionInput),
            ("evaluation_context", FeeReductionEvaluationContext),
            ("approval", FeeReductionApprovalContext | None),
            ("grant_fee_year_key", int | None),
        ),
        EvaluatePctNationalStageFeePolicyCommand: (
            ("case_id", str),
            ("fee_code", str),
            ("full_amount", Decimal),
            ("effective_on", date),
            ("evidence", tuple[ConfirmedPctEvidence, ...]),
            ("reduction_context", PctReductionContext | None),
        ),
        EvaluatePctNationalStageFeePolicyResult: (
            ("rule_code", str),
            ("source_reference", str),
            ("effective_from", date),
            ("effective_to", date | None),
            ("evaluated_on", date),
            ("fee_code", str),
            ("disposition", PctFeePolicyDisposition),
            ("evidence_document_ids", tuple[str, ...]),
            ("evidence_version_ids", tuple[str, ...]),
            ("full_amount", Decimal),
            ("reduction_ratio", Decimal),
            ("payable_ratio", Decimal),
            ("payable_amount", Decimal),
        ),
    }

    for dto_type, exact_fields in expected_fields.items():
        assert is_dataclass(dto_type)
        assert dto_type.__dataclass_params__.frozen is True
        assert "__slots__" in dto_type.__dict__
        assert tuple(field.name for field in fields(dto_type)) == tuple(
            name for name, _annotation in exact_fields
        )
        assert get_type_hints(dto_type) == dict(exact_fields)
        assert all(field.default is MISSING for field in fields(dto_type))
        assert all(field.default_factory is MISSING for field in fields(dto_type))
        assert all(field.kw_only is True for field in fields(dto_type))

    assert tuple((member.name, member.value) for member in PctFeePolicyDisposition) == (
        ("EXEMPT", "EXEMPT"),
        ("DOMESTIC_REDUCTION", "DOMESTIC_REDUCTION"),
        ("FULL_AMOUNT", "FULL_AMOUNT"),
    )
    assert issubclass(PctFeePolicyDisposition, str)
    assert issubclass(PctFeePolicyDisposition, Enum)
    assert tuple((member.name, member.value) for member in PctFeePolicyErrorCode) == (
        ("COMMAND_INVALID", "PCT_POLICY_COMMAND_INVALID"),
        ("EFFECTIVE_DATE_UNSUPPORTED", "PCT_POLICY_EFFECTIVE_DATE_UNSUPPORTED"),
        ("FEE_CODE_UNSUPPORTED", "PCT_POLICY_FEE_CODE_UNSUPPORTED"),
        ("EVIDENCE_MISSING", "PCT_POLICY_EVIDENCE_MISSING"),
        ("EVIDENCE_INVALID", "PCT_POLICY_EVIDENCE_INVALID"),
        ("EVIDENCE_CONFLICT", "PCT_POLICY_EVIDENCE_CONFLICT"),
        ("REDUCTION_INVALID", "PCT_POLICY_REDUCTION_INVALID"),
    )

    assert get_type_hints(evaluate_pct_national_stage_fee_policy) == {
        "command": EvaluatePctNationalStageFeePolicyCommand,
        "return": EvaluatePctNationalStageFeePolicyResult,
    }
    assert tuple(inspect.signature(evaluate_pct_national_stage_fee_policy).parameters) == (
        "command",
    )
    assert tuple(inspect.signature(validate_confirmed_pct_evidence_set).parameters) == (
        "case_id",
        "effective_on",
        "evidence",
    )

    command = EvaluatePctNationalStageFeePolicyCommand(
        case_id="CASE-PCT-001",
        fee_code="CN_INV_APPLICATION_FEE",
        full_amount=Decimal("100.00"),
        effective_on=date(2024, 8, 6),
        evidence=(),
        reduction_context=None,
    )
    with pytest.raises(FrozenInstanceError):
        command.case_id = "CHANGED"  # type: ignore[misc]

    error = PctFeePolicyError(
        PctFeePolicyErrorCode.COMMAND_INVALID,
        {"field": "command"},
    )
    assert error.code is PctFeePolicyErrorCode.COMMAND_INVALID
    assert error.details == {"field": "command"}
    assert str(error) == "PCT_POLICY_COMMAND_INVALID"

    original = {"field": "case_id"}
    defensive = PctFeePolicyError(PctFeePolicyErrorCode.COMMAND_INVALID, original)
    original["field"] = "changed"
    exposed = defensive.details
    exposed["field"] = "also-changed"
    assert defensive.details == {"field": "case_id"}
    with pytest.raises(AttributeError):
        defensive.code = PctFeePolicyErrorCode.FEE_CODE_UNSUPPORTED  # type: ignore[misc]


def test_confirmed_evidence_is_validated_and_sorted_once() -> None:
    evidence = validate_confirmed_pct_evidence_set(
        "CASE-PCT-001",
        EFFECTIVE_ON,
        (
            _evidence("CNIPA_RO_RECEIPT"),
            _evidence("CNIPA_ISR"),
        ),
    )

    assert tuple(item.document_type for item in evidence) == (
        "CNIPA_ISR",
        "CNIPA_RO_RECEIPT",
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("case_id", "OTHER-CASE"),
        ("source_document_id", ""),
        ("evidence_version_id", " VERSION-RO"),
        ("content_hash", f"sha256:{'A' * 64}"),
        ("lineage_key", ""),
        ("current_identity_key", "CASE-PCT-001|OTHER"),
        ("issuer", "WIPO"),
        ("document_type", ""),
        ("issued_on", date(2024, 8, 7)),
        ("role", "ATTACHMENT"),
        ("state", "DRAFT"),
        ("review_state", "PENDING"),
        ("creator_id", ""),
        ("reviewer_id", "CREATOR-RO"),
        ("reviewed_at", None),
        ("reviewed_at", datetime(2024, 8, 6, tzinfo=timezone.utc)),
    ],
)
def test_evidence_fields_fail_closed(
    field: str,
    value: object,
) -> None:
    invalid = replace(_evidence("CNIPA_RO_RECEIPT"), **{field: value})
    _assert_error(
        _command(evidence=(invalid, _evidence("CNIPA_ISR"))),
        PctFeePolicyErrorCode.EVIDENCE_INVALID,
        {"field": f"evidence[0].{field}", "index": 0},
    )


@pytest.mark.parametrize(
    "duplicate_field",
    ("source_document_id", "evidence_version_id", "content_hash", "document_type"),
)
def test_duplicate_evidence_identity_or_type_conflicts(duplicate_field: str) -> None:
    first = _evidence("CNIPA_RO_RECEIPT")
    second = _evidence("CNIPA_ISR")
    second = replace(second, **{duplicate_field: getattr(first, duplicate_field)})

    _assert_error(
        _command(evidence=(first, second)),
        PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
        {"field": "evidence", "reason": "DUPLICATE"},
    )


@pytest.mark.parametrize("fee_code", APPLICATION_EXEMPT_FEE_CODES)
def test_each_application_fee_accepts_exact_ro_and_isr_exemption(fee_code: str) -> None:
    result = evaluate_pct_national_stage_fee_policy(_command(fee_code=fee_code))

    assert result == EvaluatePctNationalStageFeePolicyResult(
        rule_code="CN_PCT_NATIONAL_STAGE_POLICY_594",
        source_reference="CNIPA_ANNOUNCEMENT_594_AND_ENTRY_NOTICE_20240806",
        effective_from=EFFECTIVE_ON,
        effective_to=None,
        evaluated_on=EFFECTIVE_ON,
        fee_code=fee_code,
        disposition=PctFeePolicyDisposition.EXEMPT,
        evidence_document_ids=("DOC-ISR", "DOC-RO"),
        evidence_version_ids=("VERSION-ISR", "VERSION-RO"),
        full_amount=Decimal("100.00"),
        reduction_ratio=Decimal("1.0000"),
        payable_ratio=Decimal("0.0000"),
        payable_amount=Decimal("0.00"),
    )


@pytest.mark.parametrize("document_type", ("CNIPA_ISR", "CNIPA_IPRP"))
def test_substantive_exam_accepts_exactly_one_isr_xor_iprp(document_type: str) -> None:
    evidence = _evidence(document_type)
    result = evaluate_pct_national_stage_fee_policy(
        _command(
            fee_code="CN_SUBSTANTIVE_EXAM_FEE",
            full_amount=Decimal("2500"),
            evidence=(evidence,),
        )
    )

    assert result.disposition is PctFeePolicyDisposition.EXEMPT
    assert result.evidence_document_ids == (evidence.source_document_id,)
    assert result.full_amount == Decimal("2500.00")
    assert result.payable_amount == Decimal("0.00")


@pytest.mark.parametrize(
    ("fee_code", "evidence", "code", "details"),
    [
        (
            "CN_INV_APPLICATION_FEE",
            (),
            PctFeePolicyErrorCode.EVIDENCE_MISSING,
            {"required": "CNIPA_RO_RECEIPT+CNIPA_ISR"},
        ),
        (
            "CN_INV_APPLICATION_FEE",
            (_evidence("CNIPA_IPRP"),),
            PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
            {"field": "evidence", "reason": "COMBINATION"},
        ),
        (
            "CN_SUBSTANTIVE_EXAM_FEE",
            (),
            PctFeePolicyErrorCode.EVIDENCE_MISSING,
            {"required": "CNIPA_ISR|CNIPA_IPRP"},
        ),
        (
            "CN_SUBSTANTIVE_EXAM_FEE",
            (_evidence("CNIPA_ISR"), _evidence("CNIPA_IPRP")),
            PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
            {"field": "evidence", "reason": "EXTRA"},
        ),
    ],
)
def test_evidence_cardinality_and_combinations_fail_closed(
    fee_code: str,
    evidence: tuple[ConfirmedPctEvidence, ...],
    code: PctFeePolicyErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    _assert_error(
        _command(fee_code=fee_code, evidence=evidence),
        code,
        details,
    )


def test_unknown_and_third_evidence_do_not_expand_exemptions() -> None:
    _assert_error(
        _command(evidence=(_evidence("UNKNOWN_OFFICIAL_REPORT"),)),
        PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
        {"field": "evidence", "reason": "UNKNOWN"},
    )
    _assert_error(
        _command(
            evidence=(
                _evidence("CNIPA_RO_RECEIPT"),
                _evidence("CNIPA_ISR"),
                _evidence("CNIPA_IPRP"),
            )
        ),
        PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
        {"field": "evidence", "reason": "EXTRA"},
    )


def test_exemption_rejects_domestic_reduction_context() -> None:
    _assert_error(
        _command(reduction_context=_reduction_context("CN_REEXAM_FEE_INV")),
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {
            "field": "reduction_context",
            "cause_code": "PCT_REDUCTION_CONTEXT_NOT_ALLOWED",
        },
    )


@pytest.mark.parametrize("fee_code", REEXAMINATION_FEE_CODES)
def test_each_reexamination_fee_uses_the_accepted_reduction_validator(
    fee_code: str,
) -> None:
    result = evaluate_pct_national_stage_fee_policy(
        _command(
            fee_code=fee_code,
            full_amount=Decimal("100.05"),
            evidence=(),
            reduction_context=_reduction_context(fee_code),
        )
    )

    assert result.disposition is PctFeePolicyDisposition.DOMESTIC_REDUCTION
    assert result.evidence_document_ids == ()
    assert result.evidence_version_ids == ()
    assert result.reduction_ratio == Decimal("0.7000")
    assert result.payable_ratio == Decimal("0.3000")
    assert result.payable_amount == Decimal("30.02")


@pytest.mark.parametrize("fee_code", ANNUITY_FEE_CODES)
def test_each_annuity_fee_uses_the_accepted_first_ten_year_validator(
    fee_code: str,
) -> None:
    result = evaluate_pct_national_stage_fee_policy(
        _command(
            fee_code=fee_code,
            full_amount=Decimal("1000.00"),
            evidence=(),
            reduction_context=_reduction_context(
                fee_code,
                fee_year_key=10,
                grant_fee_year_key=1,
            ),
        )
    )

    assert result.disposition is PctFeePolicyDisposition.DOMESTIC_REDUCTION
    assert result.reduction_ratio == Decimal("0.7000")
    assert result.payable_ratio == Decimal("0.3000")
    assert result.payable_amount == Decimal("300.00")


@pytest.mark.parametrize("fee_code", (*REEXAMINATION_FEE_CODES, *ANNUITY_FEE_CODES))
def test_zero_reduction_returns_full_amount_with_four_place_ratios(
    fee_code: str,
) -> None:
    annual = fee_code in ANNUITY_FEE_CODES
    result = evaluate_pct_national_stage_fee_policy(
        _command(
            fee_code=fee_code,
            full_amount=Decimal("123.4"),
            evidence=(),
            reduction_context=_reduction_context(
                fee_code,
                ratio=Decimal("0"),
                fee_year_key=1 if annual else 0,
                grant_fee_year_key=1 if annual else None,
                approval=_approval(fee_code),
            ),
        )
    )

    assert result.disposition is PctFeePolicyDisposition.FULL_AMOUNT
    assert result.full_amount == Decimal("123.40")
    assert result.reduction_ratio == Decimal("0.0000")
    assert result.payable_ratio == Decimal("1.0000")
    assert result.payable_amount == Decimal("123.40")


@pytest.mark.parametrize("fee_code", (*REEXAMINATION_FEE_CODES, *ANNUITY_FEE_CODES))
def test_domestic_reduction_requires_empty_evidence_and_matching_context(
    fee_code: str,
) -> None:
    annual = fee_code in ANNUITY_FEE_CODES
    context = _reduction_context(
        fee_code,
        fee_year_key=1 if annual else 0,
        grant_fee_year_key=1 if annual else None,
    )
    _assert_error(
        _command(
            fee_code=fee_code,
            evidence=(_evidence("CNIPA_ISR"),),
            reduction_context=context,
        ),
        PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
        {"field": "evidence", "reason": "NOT_ALLOWED"},
    )
    _assert_error(
        _command(fee_code=fee_code, evidence=(), reduction_context=None),
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {
            "field": "reduction_context",
            "cause_code": "PCT_REDUCTION_CONTEXT_MISSING",
        },
    )


def test_reduction_context_mismatch_and_annuity_scope_fail_closed() -> None:
    mismatch = _reduction_context(
        "CN_REEXAM_FEE_INV",
        as_of_date=date(2024, 8, 7),
    )
    _assert_error(
        _command(
            fee_code="CN_REEXAM_FEE_INV",
            evidence=(),
            reduction_context=mismatch,
        ),
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {
            "field": "reduction_context",
            "cause_code": "PCT_REDUCTION_CONTEXT_MISMATCH",
        },
    )
    _assert_error(
        _command(
            fee_code="CN_ANNUITY_FEE_INV",
            evidence=(),
            reduction_context=_reduction_context(
                "CN_ANNUITY_FEE_INV",
                fee_year_key=11,
                grant_fee_year_key=1,
            ),
        ),
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {
            "field": "reduction_context",
            "cause_code": "ANNUITY_REDUCTION_YEAR_OUT_OF_SCOPE",
        },
    )


def test_accepted_reduction_error_is_mapped_without_upstream_details() -> None:
    context = _reduction_context("CN_REEXAM_FEE_INV")
    context = replace(
        context,
        reduction_input=FeeReductionInput(
            reduction_ratio=None,
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        approval=None,
    )
    _assert_error(
        _command(
            fee_code="CN_REEXAM_FEE_INV",
            evidence=(),
            reduction_context=context,
        ),
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {
            "field": "reduction_context",
            "cause_code": "FEE_REDUCTION_MISSING_VALUE",
        },
    )


def test_unexpected_validator_failure_is_not_remapped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_programming_error(**_kwargs: object) -> object:
        raise RuntimeError("injected validator programming failure")

    monkeypatch.setattr(pct_policy, "validate_fee_reduction", raise_programming_error)
    with pytest.raises(RuntimeError, match="injected validator programming failure"):
        evaluate_pct_national_stage_fee_policy(
            _command(
                fee_code="CN_REEXAM_FEE_INV",
                evidence=(),
                reduction_context=_reduction_context("CN_REEXAM_FEE_INV"),
            )
        )


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"case_id": ""}, "case_id"),
        ({"fee_code": " CN_INV_APPLICATION_FEE"}, "fee_code"),
        ({"full_amount": "100.00"}, "full_amount"),
        ({"full_amount": Decimal("0")}, "full_amount"),
        ({"full_amount": Decimal("NaN")}, "full_amount"),
        ({"full_amount": Decimal("1.001")}, "full_amount"),
        ({"effective_on": datetime(2024, 8, 6)}, "effective_on"),
        ({"evidence": []}, "evidence"),
        ({"reduction_context": object()}, "reduction_context"),
    ],
)
def test_command_fields_are_exact(
    overrides: dict[str, object],
    field: str,
) -> None:
    _assert_error(
        _command(**overrides),
        PctFeePolicyErrorCode.COMMAND_INVALID,
        {"field": field},
    )


def test_effective_start_and_unsupported_fee_codes_fail_closed() -> None:
    _assert_error(
        _command(effective_on=date(2024, 8, 5)),
        PctFeePolicyErrorCode.EFFECTIVE_DATE_UNSUPPORTED,
        {"effective_on": "2024-08-05", "effective_from": "2024-08-06"},
    )
    for fee_code in (
        "CN_PCT_INTERNATIONAL_APPLICATION_FEE",
        "WIPO_SEARCH_FEE",
        "CN_DESIGN_APPLICATION_FEE",
        "UNKNOWN",
    ):
        _assert_error(
            _command(fee_code=fee_code),
            PctFeePolicyErrorCode.FEE_CODE_UNSUPPORTED,
            {"fee_code": fee_code},
        )


def test_amount_boundaries_and_exact_command_type() -> None:
    large = Decimal("1E+100")
    result = evaluate_pct_national_stage_fee_policy(_command(full_amount=large))
    assert result.full_amount == large
    assert result.full_amount.as_tuple().exponent == -2
    assert result.payable_amount == Decimal("0.00")

    for invalid in (
        Decimal("-0.01"),
        Decimal("Infinity"),
    ):
        _assert_error(
            _command(full_amount=invalid),
            PctFeePolicyErrorCode.COMMAND_INVALID,
            {"field": "full_amount"},
        )
    _assert_error(
        object(),
        PctFeePolicyErrorCode.COMMAND_INVALID,
        {"field": "command"},
    )


def _decimal_context_state(context: Context) -> tuple[object, ...]:
    return (
        context.prec,
        context.rounding,
        dict(context.traps),
        dict(context.flags),
    )


def test_decimal_boundary_uses_half_up_without_mutating_caller_context() -> None:
    command = _command(
        fee_code="CN_REEXAM_FEE_INV",
        full_amount=Decimal("100.05"),
        evidence=(),
        reduction_context=_reduction_context("CN_REEXAM_FEE_INV"),
    )
    with localcontext() as caller_context:
        caller_context.prec = 1
        caller_context.rounding = ROUND_DOWN
        caller_context.traps[Inexact] = True
        caller_context.traps[Rounded] = True
        caller_context.flags[Inexact] = True
        before = _decimal_context_state(caller_context)

        result = evaluate_pct_national_stage_fee_policy(command)

        assert _decimal_context_state(caller_context) == before
    assert result.full_amount == Decimal("100.05")
    assert result.payable_amount == Decimal("30.02")


def test_policy_is_pure_and_does_not_cross_runtime_boundaries() -> None:
    assert inspect.iscoroutinefunction(evaluate_pct_national_stage_fee_policy) is False
    assert inspect.isgeneratorfunction(evaluate_pct_national_stage_fee_policy) is False
    source = inspect.getsource(pct_policy)
    forbidden_tokens = (
        "Session",
        "select(",
        ".commit(",
        ".flush(",
        "official_rate_book",
        "rate_activation",
        "requests.",
        "httpx.",
        "open(",
        "Path(",
        "datetime.now",
        "date.today",
        "FastAPI",
        "APIRouter",
    )
    assert all(token not in source for token in forbidden_tokens)
