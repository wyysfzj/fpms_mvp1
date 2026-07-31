from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Context, Decimal, Inexact, Rounded, localcontext
from enum import Enum

from app.modules.fees.annuity_reduction import (
    AnnuityReductionScopeError,
    validate_annuity_fee_reduction,
)
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionValidationError,
    FeeReductionValidationResult,
    validate_fee_reduction,
)

__all__ = (
    "ConfirmedPctEvidence",
    "PctReductionContext",
    "EvaluatePctNationalStageFeePolicyCommand",
    "PctFeePolicyDisposition",
    "EvaluatePctNationalStageFeePolicyResult",
    "PctFeePolicyErrorCode",
    "PctFeePolicyError",
    "validate_confirmed_pct_evidence_set",
    "evaluate_pct_national_stage_fee_policy",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfirmedPctEvidence:
    case_id: str
    source_document_id: str
    evidence_version_id: str
    content_hash: str
    lineage_key: str
    current_identity_key: str
    issuer: str
    document_type: str
    issued_on: date
    role: str
    state: str
    review_state: str
    creator_id: str
    reviewer_id: str
    reviewed_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PctReductionContext:
    reduction_input: FeeReductionInput
    evaluation_context: FeeReductionEvaluationContext
    approval: FeeReductionApprovalContext | None
    grant_fee_year_key: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluatePctNationalStageFeePolicyCommand:
    case_id: str
    fee_code: str
    full_amount: Decimal
    effective_on: date
    evidence: tuple[ConfirmedPctEvidence, ...]
    reduction_context: PctReductionContext | None


class PctFeePolicyDisposition(str, Enum):
    EXEMPT = "EXEMPT"
    DOMESTIC_REDUCTION = "DOMESTIC_REDUCTION"
    FULL_AMOUNT = "FULL_AMOUNT"


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluatePctNationalStageFeePolicyResult:
    rule_code: str
    source_reference: str
    effective_from: date
    effective_to: date | None
    evaluated_on: date
    fee_code: str
    disposition: PctFeePolicyDisposition
    evidence_document_ids: tuple[str, ...]
    evidence_version_ids: tuple[str, ...]
    full_amount: Decimal
    reduction_ratio: Decimal
    payable_ratio: Decimal
    payable_amount: Decimal


class PctFeePolicyErrorCode(str, Enum):
    COMMAND_INVALID = "PCT_POLICY_COMMAND_INVALID"
    EFFECTIVE_DATE_UNSUPPORTED = "PCT_POLICY_EFFECTIVE_DATE_UNSUPPORTED"
    FEE_CODE_UNSUPPORTED = "PCT_POLICY_FEE_CODE_UNSUPPORTED"
    EVIDENCE_MISSING = "PCT_POLICY_EVIDENCE_MISSING"
    EVIDENCE_INVALID = "PCT_POLICY_EVIDENCE_INVALID"
    EVIDENCE_CONFLICT = "PCT_POLICY_EVIDENCE_CONFLICT"
    REDUCTION_INVALID = "PCT_POLICY_REDUCTION_INVALID"


class PctFeePolicyError(ValueError):
    def __init__(
        self,
        code: PctFeePolicyErrorCode,
        details: dict[str, str | int | bool | None],
    ) -> None:
        self._code = code
        self._details = dict(details)
        super().__init__(code.value)

    @property
    def code(self) -> PctFeePolicyErrorCode:
        return self._code

    @property
    def details(self) -> dict[str, str | int | bool | None]:
        return dict(self._details)


_RULE_CODE = "CN_PCT_NATIONAL_STAGE_POLICY_594"
_SOURCE_REFERENCE = "CNIPA_ANNOUNCEMENT_594_AND_ENTRY_NOTICE_20240806"
_EFFECTIVE_FROM = date(2024, 8, 6)
_AMOUNT_QUANTUM = Decimal("0.01")
_RATIO_ONE = Decimal("1.0000")
_RATIO_ZERO = Decimal("0.0000")
_DECIMAL_CONTEXT = Context(prec=24, rounding=ROUND_HALF_UP)
_DECIMAL_CONTEXT.traps[Inexact] = False
_DECIMAL_CONTEXT.traps[Rounded] = False
_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_DOCUMENT_TYPES = frozenset({"CNIPA_RO_RECEIPT", "CNIPA_ISR", "CNIPA_IPRP"})
_APPLICATION_EXEMPT_FEE_CODES = frozenset(
    {
        "CN_INV_APPLICATION_FEE",
        "CN_UM_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_SPEC_PAGE_31_300_FEE",
        "CN_SPEC_PAGE_301_PLUS_FEE",
    }
)
_SUBSTANTIVE_EXAM_FEE_CODE = "CN_SUBSTANTIVE_EXAM_FEE"
_REEXAMINATION_FEE_CODES = frozenset(
    {
        "CN_REEXAM_FEE_INV",
        "CN_REEXAM_FEE_UM",
        "CN_REEXAM_FEE_DES",
    }
)
_ANNUITY_FEE_CODES = frozenset(
    {
        "CN_ANNUITY_FEE_INV",
        "CN_ANNUITY_FEE_UM",
        "CN_ANNUITY_FEE_DES",
    }
)
_SUPPORTED_FEE_CODES = (
    _APPLICATION_EXEMPT_FEE_CODES
    | {_SUBSTANTIVE_EXAM_FEE_CODE}
    | _REEXAMINATION_FEE_CODES
    | _ANNUITY_FEE_CODES
)


def _raise(
    code: PctFeePolicyErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    raise PctFeePolicyError(code, details)


def _command_invalid(field: str) -> None:
    _raise(PctFeePolicyErrorCode.COMMAND_INVALID, {"field": field})


def _evidence_invalid(index: int, field: str) -> None:
    _raise(
        PctFeePolicyErrorCode.EVIDENCE_INVALID,
        {"field": f"evidence[{index}].{field}", "index": index},
    )


def _evidence_conflict(reason: str) -> None:
    _raise(
        PctFeePolicyErrorCode.EVIDENCE_CONFLICT,
        {"field": "evidence", "reason": reason},
    )


def _is_nonblank_exact_string(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def _valid_full_amount(value: object) -> bool:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        return False
    exponent = value.as_tuple().exponent
    return type(exponent) is int and exponent >= -2


def _quantize_amount(value: Decimal) -> Decimal:
    exponent = value.as_tuple().exponent
    assert type(exponent) is int
    required_precision = len(value.as_tuple().digits) + max(exponent, 0) + 8
    with localcontext(_DECIMAL_CONTEXT) as context:
        context.prec = max(context.prec, required_precision)
        return value.quantize(_AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)


def _multiply_and_quantize_amount(left: Decimal, right: Decimal) -> Decimal:
    left_exponent = left.as_tuple().exponent
    assert type(left_exponent) is int
    required_precision = len(left.as_tuple().digits) + max(left_exponent, 0) + 8
    with localcontext(_DECIMAL_CONTEXT) as context:
        context.prec = max(context.prec, required_precision)
        return (left * right).quantize(_AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)


def _validate_command(command: object) -> EvaluatePctNationalStageFeePolicyCommand:
    if type(command) is not EvaluatePctNationalStageFeePolicyCommand:
        _command_invalid("command")
    assert isinstance(command, EvaluatePctNationalStageFeePolicyCommand)
    if not _is_nonblank_exact_string(command.case_id):
        _command_invalid("case_id")
    if not _is_nonblank_exact_string(command.fee_code):
        _command_invalid("fee_code")
    if not _valid_full_amount(command.full_amount):
        _command_invalid("full_amount")
    if type(command.effective_on) is not date:
        _command_invalid("effective_on")
    if type(command.evidence) is not tuple:
        _command_invalid("evidence")
    if command.reduction_context is not None and (
        type(command.reduction_context) is not PctReductionContext
    ):
        _command_invalid("reduction_context")
    return command


def _validate_nonblank_evidence_field(
    item: ConfirmedPctEvidence,
    index: int,
    field: str,
) -> None:
    if not _is_nonblank_exact_string(getattr(item, field)):
        _evidence_invalid(index, field)


def validate_confirmed_pct_evidence_set(
    case_id: str,
    effective_on: date,
    evidence: tuple[ConfirmedPctEvidence, ...],
) -> tuple[ConfirmedPctEvidence, ...]:
    validated: list[ConfirmedPctEvidence] = []
    for index, item in enumerate(evidence):
        if type(item) is not ConfirmedPctEvidence:
            _evidence_invalid(index, "evidence")
        if not _is_nonblank_exact_string(item.case_id) or item.case_id != case_id:
            _evidence_invalid(index, "case_id")
        for field in ("source_document_id", "evidence_version_id"):
            _validate_nonblank_evidence_field(item, index, field)
        if type(item.content_hash) is not str or _HASH_PATTERN.fullmatch(item.content_hash) is None:
            _evidence_invalid(index, "content_hash")
        _validate_nonblank_evidence_field(item, index, "lineage_key")
        if (
            type(item.current_identity_key) is not str
            or item.current_identity_key != f"{case_id}|{item.lineage_key}"
        ):
            _evidence_invalid(index, "current_identity_key")
        if item.issuer != "CNIPA":
            _evidence_invalid(index, "issuer")
        if not _is_nonblank_exact_string(item.document_type):
            _evidence_invalid(index, "document_type")
        if type(item.issued_on) is not date or item.issued_on > effective_on:
            _evidence_invalid(index, "issued_on")
        if item.role != "OFFICIAL_FINAL_PDF":
            _evidence_invalid(index, "role")
        if item.state != "FINAL":
            _evidence_invalid(index, "state")
        if item.review_state != "APPROVED":
            _evidence_invalid(index, "review_state")
        _validate_nonblank_evidence_field(item, index, "creator_id")
        if not _is_nonblank_exact_string(item.reviewer_id) or item.reviewer_id == item.creator_id:
            _evidence_invalid(index, "reviewer_id")
        if type(item.reviewed_at) is not datetime or item.reviewed_at.tzinfo is not None:
            _evidence_invalid(index, "reviewed_at")
        validated.append(item)

    for field in (
        "source_document_id",
        "evidence_version_id",
        "content_hash",
        "document_type",
    ):
        values = [getattr(item, field) for item in validated]
        if len(values) != len(set(values)):
            _evidence_conflict("DUPLICATE")
    if any(item.document_type not in _DOCUMENT_TYPES for item in validated):
        _evidence_conflict("UNKNOWN")

    return tuple(
        sorted(
            validated,
            key=lambda item: (
                item.document_type,
                item.source_document_id,
                item.evidence_version_id,
            ),
        )
    )


def _validate_fee_evidence_combination(
    fee_code: str,
    evidence: tuple[ConfirmedPctEvidence, ...],
) -> None:
    document_types = tuple(item.document_type for item in evidence)
    if fee_code in _REEXAMINATION_FEE_CODES or fee_code in _ANNUITY_FEE_CODES:
        if evidence:
            _evidence_conflict("NOT_ALLOWED")
        return

    if fee_code in _APPLICATION_EXEMPT_FEE_CODES:
        if len(evidence) > 2:
            _evidence_conflict("EXTRA")
        if len(evidence) == 2:
            if set(document_types) != {"CNIPA_RO_RECEIPT", "CNIPA_ISR"}:
                _evidence_conflict("COMBINATION")
            return
        if len(evidence) == 1 and document_types[0] == "CNIPA_IPRP":
            _evidence_conflict("COMBINATION")
        _raise(
            PctFeePolicyErrorCode.EVIDENCE_MISSING,
            {"required": "CNIPA_RO_RECEIPT+CNIPA_ISR"},
        )

    if len(evidence) > 1:
        _evidence_conflict("EXTRA")
    if len(evidence) == 1:
        if document_types[0] not in {"CNIPA_ISR", "CNIPA_IPRP"}:
            _evidence_conflict("COMBINATION")
        return
    _raise(
        PctFeePolicyErrorCode.EVIDENCE_MISSING,
        {"required": "CNIPA_ISR|CNIPA_IPRP"},
    )


def _result(
    command: EvaluatePctNationalStageFeePolicyCommand,
    *,
    disposition: PctFeePolicyDisposition,
    evidence: tuple[ConfirmedPctEvidence, ...],
    full_amount: Decimal,
    reduction_ratio: Decimal,
    payable_ratio: Decimal,
    payable_amount: Decimal,
) -> EvaluatePctNationalStageFeePolicyResult:
    return EvaluatePctNationalStageFeePolicyResult(
        rule_code=_RULE_CODE,
        source_reference=_SOURCE_REFERENCE,
        effective_from=_EFFECTIVE_FROM,
        effective_to=None,
        evaluated_on=command.effective_on,
        fee_code=command.fee_code,
        disposition=disposition,
        evidence_document_ids=tuple(item.source_document_id for item in evidence),
        evidence_version_ids=tuple(item.evidence_version_id for item in evidence),
        full_amount=full_amount,
        reduction_ratio=reduction_ratio,
        payable_ratio=payable_ratio,
        payable_amount=payable_amount,
    )


def _reduction_invalid(cause_code: str) -> None:
    _raise(
        PctFeePolicyErrorCode.REDUCTION_INVALID,
        {"field": "reduction_context", "cause_code": cause_code},
    )


def _validate_reduction_context(
    command: EvaluatePctNationalStageFeePolicyCommand,
) -> PctReductionContext:
    context = command.reduction_context
    if context is None:
        _reduction_invalid("PCT_REDUCTION_CONTEXT_MISSING")
    assert context is not None
    if (
        type(context.reduction_input) is not FeeReductionInput
        or type(context.evaluation_context) is not FeeReductionEvaluationContext
        or (
            context.approval is not None
            and type(context.approval) is not FeeReductionApprovalContext
        )
    ):
        _reduction_invalid("PCT_REDUCTION_CONTEXT_INVALID")
    evaluation = context.evaluation_context
    if (
        evaluation.case_id != command.case_id
        or evaluation.fee_code != command.fee_code
        or evaluation.as_of_date != command.effective_on
    ):
        _reduction_invalid("PCT_REDUCTION_CONTEXT_MISMATCH")
    return context


def _map_reduction_error(
    error: FeeReductionValidationError | AnnuityReductionScopeError,
) -> None:
    cause_code = error.code
    if isinstance(cause_code, Enum):
        _reduction_invalid(cause_code.value)
    _reduction_invalid(cause_code)


def _evaluate_domestic_reduction(
    command: EvaluatePctNationalStageFeePolicyCommand,
) -> FeeReductionValidationResult:
    context = _validate_reduction_context(command)
    evaluation = context.evaluation_context
    try:
        if command.fee_code in _REEXAMINATION_FEE_CODES:
            if evaluation.fee_year_key != 0 or context.grant_fee_year_key is not None:
                _reduction_invalid("PCT_REDUCTION_CONTEXT_INVALID")
            return validate_fee_reduction(
                reduction_input=context.reduction_input,
                context=evaluation,
                approval=context.approval,
            )

        if (
            type(evaluation.fee_year_key) is not int
            or evaluation.fee_year_key < 1
            or type(context.grant_fee_year_key) is not int
            or context.grant_fee_year_key < 1
        ):
            _reduction_invalid("ANNUITY_REDUCTION_INVALID_CONTEXT")
        return validate_annuity_fee_reduction(
            reduction_input=context.reduction_input,
            context=evaluation,
            approval=context.approval,
            grant_fee_year_key=context.grant_fee_year_key,
        )
    except (FeeReductionValidationError, AnnuityReductionScopeError) as error:
        _map_reduction_error(error)


def evaluate_pct_national_stage_fee_policy(
    command: EvaluatePctNationalStageFeePolicyCommand,
) -> EvaluatePctNationalStageFeePolicyResult:
    command = _validate_command(command)
    if command.effective_on < _EFFECTIVE_FROM:
        _raise(
            PctFeePolicyErrorCode.EFFECTIVE_DATE_UNSUPPORTED,
            {
                "effective_on": command.effective_on.isoformat(),
                "effective_from": _EFFECTIVE_FROM.isoformat(),
            },
        )
    if command.fee_code not in _SUPPORTED_FEE_CODES:
        _raise(
            PctFeePolicyErrorCode.FEE_CODE_UNSUPPORTED,
            {"fee_code": command.fee_code},
        )
    evidence = validate_confirmed_pct_evidence_set(
        command.case_id,
        command.effective_on,
        command.evidence,
    )
    _validate_fee_evidence_combination(command.fee_code, evidence)
    full_amount = _quantize_amount(command.full_amount)
    if (
        command.fee_code in _APPLICATION_EXEMPT_FEE_CODES
        or command.fee_code == _SUBSTANTIVE_EXAM_FEE_CODE
    ):
        if command.reduction_context is not None:
            _raise(
                PctFeePolicyErrorCode.REDUCTION_INVALID,
                {
                    "field": "reduction_context",
                    "cause_code": "PCT_REDUCTION_CONTEXT_NOT_ALLOWED",
                },
            )
        return _result(
            command,
            disposition=PctFeePolicyDisposition.EXEMPT,
            evidence=evidence,
            full_amount=full_amount,
            reduction_ratio=_RATIO_ONE,
            payable_ratio=_RATIO_ZERO,
            payable_amount=Decimal("0.00"),
        )

    reduction = _evaluate_domestic_reduction(command)
    disposition = (
        PctFeePolicyDisposition.FULL_AMOUNT
        if reduction.reduction_ratio == _RATIO_ZERO
        else PctFeePolicyDisposition.DOMESTIC_REDUCTION
    )
    return _result(
        command,
        disposition=disposition,
        evidence=evidence,
        full_amount=full_amount,
        reduction_ratio=reduction.reduction_ratio,
        payable_ratio=reduction.payable_ratio,
        payable_amount=_multiply_and_quantize_amount(
            full_amount,
            reduction.payable_ratio,
        ),
    )
