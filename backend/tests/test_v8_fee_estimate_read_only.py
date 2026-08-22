from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol, get_type_hints

import pytest

import app.modules.fees.obligation_service as obligation_service
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionErrorCode,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationError,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
    PreviewFeeEstimateCommand,
)
from app.modules.fees.obligation_service import (
    FeeEstimatePreviewError,
    FeeEstimatePreviewErrorCode,
    OfficialFeeEstimateRateCandidate,
    OfficialFeeEstimateRateProvider,
    preview_estimate,
)

EFFECTIVE_ON = date(2026, 7, 13)


class StringSubclass(str):
    pass


class DateSubclass(date):
    pass


class FakeRateProvider:
    def __init__(
        self,
        candidates: object,
        *,
        error: FeeEstimatePreviewError | None = None,
    ) -> None:
        self.candidates = candidates
        self.error = error
        self.calls: list[tuple[PreviewFeeEstimateCommand, date]] = []

    def select_rate_candidates(
        self,
        *,
        command: PreviewFeeEstimateCommand,
        rate_effective_on: date,
    ) -> tuple[OfficialFeeEstimateRateCandidate, ...]:
        self.calls.append((command, rate_effective_on))
        if self.error is not None:
            raise self.error
        return self.candidates  # type: ignore[return-value]


def _command(**overrides: object) -> PreviewFeeEstimateCommand:
    values: dict[str, object] = {
        "case_id": "CASE-001",
        "trigger_context": FeeEstimateContext(
            trigger="APPLICATION_ACCEPTED",
            source_document_id="DOC-001",
        ),
        "currency": "CNY",
    }
    values.update(overrides)
    return PreviewFeeEstimateCommand(**values)  # type: ignore[arg-type]


def _source(**overrides: object) -> FeeEstimateSource:
    values: dict[str, object] = {
        "rate_id": "RATE-001",
        "source_document_id": "DOC-001",
        "source_doc": "CNIPA-RATE-GUIDE-2026",
        "source_url": "https://example.test/cnipa/rates",
        "source_policy": "CNIPA-OFFICIAL-FEE",
        "source_version": "2026-03-30",
        "status": FeeSourceStatus.VERIFIED,
    }
    values.update(overrides)
    return FeeEstimateSource(**values)  # type: ignore[arg-type]


def _reduction_context(
    *,
    fee_code: str = "APPLICATION_FEE",
    fee_year_key: int = 0,
    **overrides: object,
) -> FeeReductionEvaluationContext:
    values: dict[str, object] = {
        "case_id": "CASE-001",
        "applicant_set_key": "APPLICANT-SET-001",
        "fee_code": fee_code,
        "fee_year_key": fee_year_key,
        "as_of_date": EFFECTIVE_ON,
    }
    values.update(overrides)
    return FeeReductionEvaluationContext(**values)  # type: ignore[arg-type]


def _approval(
    *,
    fee_code: str,
    fee_year_key: int,
    ratio: str,
) -> FeeReductionApprovalContext:
    return FeeReductionApprovalContext(
        approval_id=f"APPROVAL-{fee_code}",
        scope_type=FeeReductionApprovalScopeType.CASE,
        case_id="CASE-001",
        applicant_set_key=None,
        reduction_ratio=Decimal(ratio),
        fee_codes=frozenset({fee_code}),
        fee_year_from=fee_year_key if fee_year_key else None,
        fee_year_to=fee_year_key if fee_year_key else None,
        effective_from=EFFECTIVE_ON,
        effective_to=EFFECTIVE_ON,
        source_evidence_version_id=f"EVIDENCE-{fee_code}",
        confirmation_status="CONFIRMED",
        is_current=True,
    )


def _candidate(
    *,
    fee_code: str = "APPLICATION_FEE",
    fee_name: str = "Synthetic application fee",
    fee_year_key: int = 0,
    full_amount: str = "100.00",
    ratio: str = "0.0000",
    source: FeeEstimateSource | None = None,
    reduction_input: FeeReductionInput | None = None,
    reduction_context: FeeReductionEvaluationContext | None = None,
    reduction_approval: FeeReductionApprovalContext | None = None,
) -> OfficialFeeEstimateRateCandidate:
    return OfficialFeeEstimateRateCandidate(
        fee_code=fee_code,
        fee_name=fee_name,
        fee_year_key=fee_year_key,
        official_full_amount=Decimal(full_amount),
        source=source or _source(rate_id=f"RATE-{fee_code}"),
        reduction_input=reduction_input
        or FeeReductionInput(
            reduction_ratio=Decimal(ratio),
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        reduction_context=reduction_context
        or _reduction_context(fee_code=fee_code, fee_year_key=fee_year_key),
        reduction_approval=reduction_approval,
    )


def _preview(
    candidates: object,
    *,
    command: PreviewFeeEstimateCommand | None = None,
    effective_on: object = EFFECTIVE_ON,
) -> tuple[FeeEstimate, FakeRateProvider]:
    provider = FakeRateProvider(candidates)
    result = preview_estimate(
        command=command or _command(),
        rate_effective_on=effective_on,  # type: ignore[arg-type]
        rate_provider=provider,
    )
    return result, provider


def _assert_preview_error(
    code: FeeEstimatePreviewErrorCode,
    details: dict[str, str | int | bool | None],
    *,
    candidates: object = (),
    command: PreviewFeeEstimateCommand | None = None,
    effective_on: object = EFFECTIVE_ON,
) -> FeeEstimatePreviewError:
    provider = FakeRateProvider(candidates)
    with pytest.raises(FeeEstimatePreviewError) as caught:
        preview_estimate(
            command=command or _command(),
            rate_effective_on=effective_on,  # type: ignore[arg-type]
            rate_provider=provider,
        )
    assert caught.value.code is code
    assert caught.value.details == details
    assert str(caught.value) == code.value
    return caught.value


def test_public_contract_is_exact_frozen_and_keyword_only() -> None:
    assert tuple((member.name, member.value) for member in FeeEstimatePreviewErrorCode) == (
        ("INVALID_COMMAND", "FEE_ESTIMATE_INVALID_COMMAND"),
        ("TRIGGER_UNSUPPORTED", "FEE_ESTIMATE_TRIGGER_UNSUPPORTED"),
        ("RATE_MISSING", "FEE_ESTIMATE_RATE_MISSING"),
        ("RATE_SOURCE_UNAPPROVED", "FEE_ESTIMATE_RATE_SOURCE_UNAPPROVED"),
        ("RATE_SOURCE_AMBIGUOUS", "FEE_ESTIMATE_RATE_SOURCE_AMBIGUOUS"),
        ("RATE_SOURCE_INVALID", "FEE_ESTIMATE_RATE_SOURCE_INVALID"),
        ("CANDIDATE_INVALID", "FEE_ESTIMATE_CANDIDATE_INVALID"),
    )
    assert issubclass(FeeEstimatePreviewErrorCode, str)
    assert issubclass(FeeEstimatePreviewErrorCode, Enum)

    assert is_dataclass(OfficialFeeEstimateRateCandidate)
    assert OfficialFeeEstimateRateCandidate.__dataclass_params__.frozen is True
    assert "__slots__" in OfficialFeeEstimateRateCandidate.__dict__
    assert tuple(field.name for field in fields(OfficialFeeEstimateRateCandidate)) == (
        "fee_code",
        "fee_name",
        "fee_year_key",
        "official_full_amount",
        "source",
        "reduction_input",
        "reduction_context",
        "reduction_approval",
    )
    assert get_type_hints(OfficialFeeEstimateRateCandidate) == {
        "fee_code": str,
        "fee_name": str,
        "fee_year_key": int,
        "official_full_amount": Decimal,
        "source": FeeEstimateSource,
        "reduction_input": FeeReductionInput,
        "reduction_context": FeeReductionEvaluationContext,
        "reduction_approval": FeeReductionApprovalContext | None,
    }
    candidate = _candidate()
    assert not hasattr(candidate, "__dict__")
    with pytest.raises(FrozenInstanceError):
        candidate.fee_code = "CHANGED"  # type: ignore[misc]

    assert issubclass(OfficialFeeEstimateRateProvider, Protocol)
    assert OfficialFeeEstimateRateProvider._is_protocol is True
    provider_signature = inspect.signature(OfficialFeeEstimateRateProvider.select_rate_candidates)
    assert tuple(provider_signature.parameters) == (
        "self",
        "command",
        "rate_effective_on",
    )
    assert provider_signature.parameters["self"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert all(
        provider_signature.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        for name in ("command", "rate_effective_on")
    )
    assert get_type_hints(OfficialFeeEstimateRateProvider.select_rate_candidates) == {
        "command": PreviewFeeEstimateCommand,
        "rate_effective_on": date,
        "return": tuple[OfficialFeeEstimateRateCandidate, ...],
    }

    signature = inspect.signature(preview_estimate)
    assert tuple(signature.parameters) == (
        "command",
        "rate_effective_on",
        "rate_provider",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(preview_estimate) == {
        "command": PreviewFeeEstimateCommand,
        "rate_effective_on": date,
        "rate_provider": OfficialFeeEstimateRateProvider,
        "return": FeeEstimate,
    }


def test_error_uses_exact_message_and_defensive_detail_copies() -> None:
    original = {"field": "currency"}
    error = FeeEstimatePreviewError(FeeEstimatePreviewErrorCode.INVALID_COMMAND, original)
    original["field"] = "changed"
    exposed = error.details
    exposed["field"] = "also-changed"

    assert error.code is FeeEstimatePreviewErrorCode.INVALID_COMMAND
    assert error.details == {"field": "currency"}
    assert str(error) == "FEE_ESTIMATE_INVALID_COMMAND"
    assert isinstance(error, ValueError)


@pytest.mark.parametrize(
    ("command", "effective_on", "field"),
    [
        (object(), EFFECTIVE_ON, "command"),
        (_command(case_id=""), EFFECTIVE_ON, "case_id"),
        (_command(case_id=" CASE-001"), EFFECTIVE_ON, "case_id"),
        (_command(trigger_context=object()), EFFECTIVE_ON, "trigger_context"),
        (
            _command(trigger_context=FeeEstimateContext("", "DOC-001")),
            EFFECTIVE_ON,
            "trigger",
        ),
        (
            _command(trigger_context=FeeEstimateContext(" TRIGGER", "DOC-001")),
            EFFECTIVE_ON,
            "trigger",
        ),
        (
            _command(trigger_context=FeeEstimateContext("TRIGGER", "")),
            EFFECTIVE_ON,
            "source_document_id",
        ),
        (_command(currency="cny"), EFFECTIVE_ON, "currency"),
        (_command(currency="CNY "), EFFECTIVE_ON, "currency"),
        (_command(currency="CN"), EFFECTIVE_ON, "currency"),
        (_command(currency="中NY"), EFFECTIVE_ON, "currency"),
        (_command(), datetime(2026, 7, 13), "rate_effective_on"),
        (_command(), "2026-07-13", "rate_effective_on"),
    ],
)
def test_invalid_command_fields_fail_in_frozen_order_without_provider_call(
    command: object,
    effective_on: object,
    field: str,
) -> None:
    provider = FakeRateProvider((_candidate(),))
    with pytest.raises(FeeEstimatePreviewError) as caught:
        preview_estimate(
            command=command,  # type: ignore[arg-type]
            rate_effective_on=effective_on,  # type: ignore[arg-type]
            rate_provider=provider,
        )

    assert caught.value.code is FeeEstimatePreviewErrorCode.INVALID_COMMAND
    assert caught.value.details == {"field": field}
    assert provider.calls == []


def test_provider_receives_exact_inputs_once_and_open_trigger_vocabulary_is_preserved() -> None:
    command = _command(
        trigger_context=FeeEstimateContext(
            trigger="FUTURE_APPROVED_TRIGGER",
            source_document_id="DOC-001",
        )
    )
    candidate = _candidate()
    result, provider = _preview((candidate,), command=command)

    assert provider.calls == [(command, EFFECTIVE_ON)]
    assert provider.calls[0][0] is command
    assert result.trigger_context is command.trigger_context


@pytest.mark.parametrize(
    ("code", "details"),
    [
        (
            FeeEstimatePreviewErrorCode.TRIGGER_UNSUPPORTED,
            {"trigger": "APPLICATION_ACCEPTED"},
        ),
        (
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            {
                "fee_code": "APPLICATION_FEE",
                "fee_year_key": 0,
                "rate_effective_on": "2026-07-13",
            },
        ),
        (
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            {"fee_code": "APPLICATION_FEE", "fee_year_key": 0, "rate_id": None},
        ),
        (
            FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
            {
                "fee_code": "APPLICATION_FEE",
                "fee_year_key": 0,
                "rate_effective_on": "2026-07-13",
            },
        ),
        (
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": "APPLICATION_FEE", "fee_year_key": 0, "field": "source_url"},
        ),
    ],
)
def test_provider_fail_closed_errors_propagate_unchanged(
    code: FeeEstimatePreviewErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    expected = FeeEstimatePreviewError(code, details)
    provider = FakeRateProvider((), error=expected)
    with pytest.raises(FeeEstimatePreviewError) as caught:
        preview_estimate(
            command=_command(),
            rate_effective_on=EFFECTIVE_ON,
            rate_provider=provider,
        )

    assert caught.value is expected
    assert provider.calls == [(_command(), EFFECTIVE_ON)]


def test_provider_result_must_be_exact_nonempty_tuple() -> None:
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {"fee_code": None, "fee_year_key": 0, "field": "rate_provider_result"},
        candidates=[_candidate()],
    )
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.RATE_MISSING,
        {"fee_code": None, "fee_year_key": 0, "rate_effective_on": "2026-07-13"},
    )


@pytest.mark.parametrize(
    ("candidate", "field", "fee_code", "fee_year_key"),
    [
        (object(), "candidate", None, 0),
        (replace(_candidate(), fee_code=""), "fee_code", "", 0),
        (replace(_candidate(), fee_code=" FEE"), "fee_code", " FEE", 0),
        (replace(_candidate(), fee_name=""), "fee_name", "APPLICATION_FEE", 0),
        (replace(_candidate(), fee_name=" Fee"), "fee_name", "APPLICATION_FEE", 0),
        (replace(_candidate(), fee_year_key=True), "fee_year_key", "APPLICATION_FEE", 0),
        (replace(_candidate(), fee_year_key=-1), "fee_year_key", "APPLICATION_FEE", -1),
        (
            replace(_candidate(), official_full_amount=100),
            "official_full_amount",
            "APPLICATION_FEE",
            0,
        ),
        (
            replace(_candidate(), official_full_amount=Decimal("NaN")),
            "official_full_amount",
            "APPLICATION_FEE",
            0,
        ),
        (
            replace(_candidate(), official_full_amount=Decimal("-0.01")),
            "official_full_amount",
            "APPLICATION_FEE",
            0,
        ),
        (
            replace(_candidate(), official_full_amount=Decimal("1.001")),
            "official_full_amount",
            "APPLICATION_FEE",
            0,
        ),
    ],
)
def test_candidate_identity_and_amount_fields_fail_without_coercion(
    candidate: object,
    field: str,
    fee_code: str | None,
    fee_year_key: int,
) -> None:
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {"fee_code": fee_code, "fee_year_key": fee_year_key, "field": field},
        candidates=(candidate,),
    )


def test_duplicate_identity_fails_closed_before_second_source_is_used() -> None:
    duplicate = _candidate(source=_source(rate_id="RATE-002"))
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
        {
            "fee_code": "APPLICATION_FEE",
            "fee_year_key": 0,
            "rate_effective_on": "2026-07-13",
        },
        candidates=(_candidate(), duplicate),
    )


@pytest.mark.parametrize(
    ("source", "code", "field"),
    [
        (object(), FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID, "source"),
        (
            _source(status=FeeSourceStatus.REVIEW_REQUIRED),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            None,
        ),
        (_source(rate_id=""), FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID, "rate_id"),
        (
            _source(source_doc=" source"),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            "source_doc",
        ),
        (
            _source(source_url=""),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            "source_url",
        ),
        (
            _source(source_policy=""),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            "source_policy",
        ),
        (
            _source(source_version=""),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            "source_version",
        ),
        (
            _source(source_document_id="OTHER-DOC"),
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            "source_document_id",
        ),
    ],
)
def test_source_must_be_verified_complete_and_match_command_document(
    source: object,
    code: FeeEstimatePreviewErrorCode,
    field: str | None,
) -> None:
    details: dict[str, str | int | bool | None] = {
        "fee_code": "APPLICATION_FEE",
        "fee_year_key": 0,
    }
    if code is FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED:
        details["rate_id"] = "RATE-001"
    else:
        details["field"] = field
    _assert_preview_error(
        code,
        details,
        candidates=(replace(_candidate(), source=source),),  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"reduction_input": object()}, "reduction_input"),
        ({"reduction_context": object()}, "reduction_context"),
        ({"reduction_approval": object()}, "reduction_approval"),
        (
            {
                "reduction_context": _reduction_context(case_id="OTHER-CASE"),
            },
            "reduction_context.case_id",
        ),
        (
            {
                "reduction_context": _reduction_context(case_id=StringSubclass("CASE-001")),
            },
            "reduction_context.case_id",
        ),
        (
            {
                "reduction_context": _reduction_context(fee_code="OTHER_FEE"),
            },
            "reduction_context.fee_code",
        ),
        (
            {
                "reduction_context": _reduction_context(fee_code=StringSubclass("APPLICATION_FEE")),
            },
            "reduction_context.fee_code",
        ),
        (
            {
                "reduction_context": _reduction_context(fee_year_key=2),
            },
            "reduction_context.fee_year_key",
        ),
        (
            {
                "reduction_context": _reduction_context(as_of_date=date(2026, 7, 12)),
            },
            "reduction_context.as_of_date",
        ),
        (
            {
                "reduction_context": _reduction_context(as_of_date=DateSubclass(2026, 7, 13)),
            },
            "reduction_context.as_of_date",
        ),
    ],
)
def test_reduction_dtos_and_context_identity_fail_closed(
    changes: dict[str, object],
    field: str,
) -> None:
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {"fee_code": "APPLICATION_FEE", "fee_year_key": 0, "field": field},
        candidates=(replace(_candidate(), **changes),),
    )


def test_reduction_context_boolean_year_cannot_equal_integer_candidate_year() -> None:
    candidate = _candidate(
        fee_code="ANNUITY_FEE",
        fee_year_key=1,
        reduction_context=_reduction_context(
            fee_code="ANNUITY_FEE",
            fee_year_key=True,
        ),
    )
    _assert_preview_error(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {
            "fee_code": "ANNUITY_FEE",
            "fee_year_key": 1,
            "field": "reduction_context.fee_year_key",
        },
        candidates=(candidate,),
    )


def test_zero_and_approved_reductions_round_each_line_half_up_and_preserve_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_validator = obligation_service.validate_fee_reduction
    validation_calls: list[
        tuple[
            FeeReductionInput,
            FeeReductionEvaluationContext,
            FeeReductionApprovalContext | None,
        ]
    ] = []

    def recording_validator(
        *,
        reduction_input: FeeReductionInput,
        context: FeeReductionEvaluationContext,
        approval: FeeReductionApprovalContext | None,
    ) -> object:
        validation_calls.append((reduction_input, context, approval))
        return original_validator(
            reduction_input=reduction_input,
            context=context,
            approval=approval,
        )

    monkeypatch.setattr(obligation_service, "validate_fee_reduction", recording_validator)
    annual_70 = _candidate(
        fee_code="ANNUITY_FEE",
        fee_name="Synthetic annuity fee",
        fee_year_key=3,
        full_amount="100.05",
        ratio="0.7000",
        source=_source(rate_id="RATE-ANNUITY"),
        reduction_approval=_approval(
            fee_code="ANNUITY_FEE",
            fee_year_key=3,
            ratio="0.7000",
        ),
    )
    nonannual_zero = _candidate(full_amount="10.05")
    annual_85 = _candidate(
        fee_code="ANNUITY_SURCHARGE",
        fee_name="Synthetic annual surcharge",
        fee_year_key=7,
        full_amount="100.10",
        ratio="0.8500",
        source=_source(rate_id="RATE-SURCHARGE"),
        reduction_approval=_approval(
            fee_code="ANNUITY_SURCHARGE",
            fee_year_key=7,
            ratio="0.8500",
        ),
    )
    candidates = (annual_70, nonannual_zero, annual_85)
    snapshots = tuple(repr(candidate) for candidate in candidates)

    result, provider = _preview(candidates)

    assert result == FeeEstimate(
        case_id="CASE-001",
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=_command().trigger_context,
        currency="CNY",
        candidates=(
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="ANNUITY_FEE",
                    fee_name="Synthetic annuity fee",
                    fee_year_key=3,
                    official_full_amount=Decimal("100.05"),
                    reduction_ratio=Decimal("0.7000"),
                    payable_amount=Decimal("30.02"),
                    source_amount=None,
                    source_date=EFFECTIVE_ON,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=annual_70.source,
            ),
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="APPLICATION_FEE",
                    fee_name="Synthetic application fee",
                    fee_year_key=0,
                    official_full_amount=Decimal("10.05"),
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=Decimal("10.05"),
                    source_amount=None,
                    source_date=EFFECTIVE_ON,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=nonannual_zero.source,
            ),
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="ANNUITY_SURCHARGE",
                    fee_name="Synthetic annual surcharge",
                    fee_year_key=7,
                    official_full_amount=Decimal("100.10"),
                    reduction_ratio=Decimal("0.8500"),
                    payable_amount=Decimal("15.02"),
                    source_amount=None,
                    source_date=EFFECTIVE_ON,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=annual_85.source,
            ),
        ),
        total_payable_amount=Decimal("55.09"),
    )
    assert provider.calls == [(_command(), EFFECTIVE_ON)]
    assert len(validation_calls) == 3
    assert validation_calls == [
        (
            candidate.reduction_input,
            candidate.reduction_context,
            candidate.reduction_approval,
        )
        for candidate in candidates
    ]
    assert tuple(repr(candidate) for candidate in candidates) == snapshots
    assert result.candidates[0].line.fee_year_key == 3
    assert result.candidates[1].line.fee_year_key == 0
    assert result.candidates[2].line.fee_year_key == 7


def test_fee_reduction_validation_error_propagates_unchanged() -> None:
    candidate = _candidate(
        ratio="0.7000",
        reduction_approval=None,
    )
    with pytest.raises(FeeReductionValidationError) as caught:
        _preview((candidate,))

    assert caught.value.code is FeeReductionErrorCode.APPROVAL_REQUIRED
    assert caught.value.details == {
        "reduction_ratio": "0.7000",
        "case_id": "CASE-001",
        "fee_code": "APPLICATION_FEE",
        "fee_year_key": 0,
        "as_of_date": "2026-07-13",
    }


def test_result_contains_no_business_record_identifier_or_deadline_and_is_read_only() -> None:
    result, _provider = _preview((_candidate(),))

    assert not hasattr(result, "id")
    assert not hasattr(result, "obligation_id")
    assert not hasattr(result, "draft_id")
    assert not hasattr(result, "fee_item_id")
    assert not hasattr(result, "activity_id")
    assert not hasattr(result, "due_date")
    assert not hasattr(result, "deadline_source")
    assert result.candidates[0].line.source_date == EFFECTIVE_ON
    assert result.candidates[0].line.source_amount is None
    assert result.candidates[0].source.rate_id == "RATE-APPLICATION_FEE"
    assert not hasattr(result, "__dict__")

    preview_source = inspect.getsource(preview_estimate)
    for prohibited in (
        "Session",
        "select(",
        ".add(",
        ".add_all(",
        ".delete(",
        ".flush(",
        ".commit(",
        "date.today",
        "datetime.now",
        "uuid4",
    ):
        assert prohibited not in preview_source
