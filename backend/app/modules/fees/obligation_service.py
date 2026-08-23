from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext
from enum import Enum
from typing import Protocol, cast
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, aliased

from app.core.errors import BusinessError
from app.modules.annuity.models import AnnuityTask, GovPayment, PayList
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import Document, DocumentEvidenceVersion
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    validate_fee_reduction,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligationDraftItemLink,
    FeeObligationPaymentEvidenceLink,
    ServicePriceBook,
    T_GrantFeeTask,
)
from app.modules.fees.models import (
    FeeObligation as FeeObligationModel,
)
from app.modules.fees.models import (
    FeeObligationLine as FeeObligationLineModel,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeDraftAuthority,
    FeeDraftItemLinkResult,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationLine,
    FeeObligationLineInput,
    FeeObligationSource,
    FeeObligationStatus,
    FeeObligationStatuses,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentEvidenceLinkResult,
    FeePaymentStatus,
    FeeSourceStatus,
    PrepareFeeObligationDraftCommand,
    PrepareFeeObligationDraftResult,
    PreviewFeeEstimateCommand,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
    RecordFeeObligationInstructionCommand,
    RecordFeeObligationInstructionResult,
    RecordFeePaymentEvidenceCommand,
    RecordFeePaymentEvidenceResult,
)
from app.modules.fees.service_price_book import _activation_snapshot
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)
from app.modules.system.future_annuity_exception_authority_service import (
    FutureAnnuityExceptionScope,
    FutureAnnuityExceptionUseAttestation,
    ResolveFutureAnnuityExceptionCommand,
    resolve_future_annuity_exception,
)
from app.modules.system.models import CustomerDecisionGate, FutureAnnuityDraftExceptionRecord

__all__ = (
    "AnnuityPayableAmountResult",
    "FeeEstimatePreviewErrorCode",
    "FeeEstimatePreviewError",
    "OfficialFeeEstimateRateCandidate",
    "OfficialFeeEstimateRateProvider",
    "calculate_annuity_payable_amount",
    "get_fee_obligation",
    "preview_estimate",
    "prepare_draft",
    "recognize_obligation",
    "record_client_instruction",
    "record_payment_evidence",
    "create_service_receivable_obligation",
)

_ACTIVITY_TYPE = "FEE_OBLIGATION_RECOGNIZED"
_PAYLOAD_SCHEMA = "FPMS_FEE_OBLIGATION_RECOGNIZED_V1"
_SERVICE_SOURCE_SCHEMA = "FPMS_SERVICE_PRICE_ITEM_SELECTED_V1"


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateServiceReceivableObligationCommand:
    price_book_version_id: str
    item_code: str
    case_id: str
    actor_id: str
    idempotency_key: str
    recognized_at: datetime


@dataclass(frozen=True, slots=True)
class CreateServiceReceivableObligationResult:
    recognition: RecognizeFeeObligationResult
    price_book_version_id: str
    item_code: str
    unit_price: Decimal
    source_activity_id: str
    reused: bool


_INSTRUCTION_ACTIVITY_TYPE = "FEE_CLIENT_INSTRUCTION_RECORDED"
_GRANT_REVIEW_ACTIVITY_TYPE = "GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED"
_GRANT_REVIEW_PAYLOAD_SCHEMA = "FPMS_GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"
_GRANT_REGISTRATION_REVIEW_ACTIVITY_TYPE = (
    "GRANT_REGISTRATION_OFFICIAL_FEE_REVIEW_CONFIRMED"
)
_GRANT_REGISTRATION_REVIEW_PAYLOAD_SCHEMA = (
    "FPMS_GRANT_REGISTRATION_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"
)
_GRANT_REVIEW_BASIS = "AUTHORIZED_OPERATOR_MANUAL_ENTRY"
_GRANT_REVIEW_PAYLOAD_KEYS = {
    "schema",
    "case_id",
    "grant_fee_task_id",
    "obligation_id",
    "source_activity_id",
    "source_document_id",
    "reviewed_evidence_version_id",
    "reviewed_evidence_content_hash",
    "confirmed_at",
    "review_basis",
    "before_lines",
    "after_lines",
}
_GRANT_REVIEW_LINE_KEYS = {
    "obligation_line_id",
    "fee_code",
    "fee_name",
    "fee_year_key",
    "official_full_amount",
    "reduction_ratio",
    "payable_amount",
    "source_amount",
    "source_date",
    "difference_review_state",
    "current_identity_key",
}
_INSTRUCTION_PAYLOAD_SCHEMA = "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1"
_DRAFT_ACTIVITY_TYPE = "FEE_DRAFT_CREATED"
_DRAFT_PAYLOAD_SCHEMA = "FPMS_FEE_DRAFT_CREATED_V1"
_REVIEWED_NOTICE_DRAFT_PAYLOAD_SCHEMA = "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1"
_REVIEWED_GRANT_DRAFT_PAYLOAD_SCHEMA = "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_GRANT_YEAR_NOTICE_V1"
_FUTURE_ANNUITY_EXCEPTION_DRAFT_PAYLOAD_SCHEMA = (
    "FPMS_FEE_DRAFT_CREATED_FROM_FUTURE_ANNUITY_EXCEPTION_V1"
)
_FUTURE_ANNUITY_GATE_SOURCE_REFERENCE = (
    "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
)
_FUTURE_ANNUITY_GATE_SOURCE_VERSION = (
    "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
)
_FUTURE_ANNUITY_FEE_CODE = {
    "INV": "CN_ANNUITY_FEE_INV",
    "UM": "CN_ANNUITY_FEE_UM",
    "DES": "CN_ANNUITY_FEE_DES",
}
_MAX_AMOUNT = Decimal("9999999999999999.99")
_TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class AnnuityPayableAmountResult:
    full_annual_fee: Decimal
    eligible_ratio: Decimal
    payable_amount: Decimal
    late_fee_base: Decimal


def calculate_annuity_payable_amount(
    *,
    full_annual_fee: Decimal,
    eligible_ratio: Decimal,
) -> AnnuityPayableAmountResult:
    if (
        type(full_annual_fee) is not Decimal
        or not full_annual_fee.is_finite()
        or full_annual_fee <= 0
        or full_annual_fee > _MAX_AMOUNT
    ):
        raise ValueError("ANNUITY_FULL_ANNUAL_FEE_INVALID")
    if (
        type(eligible_ratio) is not Decimal
        or not eligible_ratio.is_finite()
        or not Decimal("0") < eligible_ratio <= Decimal("1")
    ):
        raise ValueError("ANNUITY_ELIGIBLE_RATIO_INVALID")

    with localcontext() as context:
        context.prec = max(
            len(full_annual_fee.as_tuple().digits) + len(eligible_ratio.as_tuple().digits),
            full_annual_fee.adjusted() + 3,
            1,
        )
        payable_amount = (full_annual_fee * eligible_ratio).quantize(
            _TWO_PLACES,
            rounding=ROUND_HALF_UP,
        )
    return AnnuityPayableAmountResult(
        full_annual_fee=full_annual_fee,
        eligible_ratio=eligible_ratio,
        payable_amount=payable_amount,
        late_fee_base=full_annual_fee,
    )


class FeeEstimatePreviewErrorCode(str, Enum):
    INVALID_COMMAND = "FEE_ESTIMATE_INVALID_COMMAND"
    TRIGGER_UNSUPPORTED = "FEE_ESTIMATE_TRIGGER_UNSUPPORTED"
    RATE_MISSING = "FEE_ESTIMATE_RATE_MISSING"
    RATE_SOURCE_UNAPPROVED = "FEE_ESTIMATE_RATE_SOURCE_UNAPPROVED"
    RATE_SOURCE_AMBIGUOUS = "FEE_ESTIMATE_RATE_SOURCE_AMBIGUOUS"
    RATE_SOURCE_INVALID = "FEE_ESTIMATE_RATE_SOURCE_INVALID"
    CANDIDATE_INVALID = "FEE_ESTIMATE_CANDIDATE_INVALID"


class FeeEstimatePreviewError(ValueError):
    def __init__(
        self,
        code: FeeEstimatePreviewErrorCode,
        details: dict[str, str | int | bool | None],
    ) -> None:
        self.code = code
        self._details = dict(details)
        super().__init__(code.value)

    @property
    def details(self) -> dict[str, str | int | bool | None]:
        return dict(self._details)


@dataclass(frozen=True, slots=True)
class OfficialFeeEstimateRateCandidate:
    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: Decimal
    source: FeeEstimateSource
    reduction_input: FeeReductionInput
    reduction_context: FeeReductionEvaluationContext
    reduction_approval: FeeReductionApprovalContext | None


class OfficialFeeEstimateRateProvider(Protocol):
    def select_rate_candidates(
        self,
        *,
        command: PreviewFeeEstimateCommand,
        rate_effective_on: date,
    ) -> tuple[OfficialFeeEstimateRateCandidate, ...]: ...


def preview_estimate(
    *,
    command: PreviewFeeEstimateCommand,
    rate_effective_on: date,
    rate_provider: OfficialFeeEstimateRateProvider,
) -> FeeEstimate:
    _validate_preview_command(command, rate_effective_on)
    selections = rate_provider.select_rate_candidates(
        command=command,
        rate_effective_on=rate_effective_on,
    )
    if type(selections) is not tuple:
        _candidate_invalid(None, 0, "rate_provider_result")
    if not selections:
        raise FeeEstimatePreviewError(
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            {
                "fee_code": None,
                "fee_year_key": 0,
                "rate_effective_on": rate_effective_on.isoformat(),
            },
        )

    identities: set[tuple[str, int]] = set()
    candidates: list[FeeEstimateCandidate] = []
    total = Decimal("0.00")
    for selection in selections:
        fee_code, fee_year_key = _candidate_identity_details(selection)
        if type(selection) is not OfficialFeeEstimateRateCandidate:
            _candidate_invalid(fee_code, fee_year_key, "candidate")
        if not _preview_string(selection.fee_code):
            _candidate_invalid(fee_code, fee_year_key, "fee_code")
        if not _preview_string(selection.fee_name):
            _candidate_invalid(fee_code, fee_year_key, "fee_name")
        if type(selection.fee_year_key) is not int or selection.fee_year_key < 0:
            _candidate_invalid(fee_code, fee_year_key, "fee_year_key")
        if not _valid_preview_amount(selection.official_full_amount):
            _candidate_invalid(fee_code, fee_year_key, "official_full_amount")

        identity = (selection.fee_code, selection.fee_year_key)
        if identity in identities:
            raise FeeEstimatePreviewError(
                FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
                {
                    "fee_code": selection.fee_code,
                    "fee_year_key": selection.fee_year_key,
                    "rate_effective_on": rate_effective_on.isoformat(),
                },
            )
        identities |= {identity}

        _validate_preview_source(selection, command)
        _validate_preview_reduction(selection, command, rate_effective_on)
        reduction = validate_fee_reduction(
            reduction_input=selection.reduction_input,
            context=selection.reduction_context,
            approval=selection.reduction_approval,
        )
        payable_amount = (selection.official_full_amount * reduction.payable_ratio).quantize(
            _TWO_PLACES, rounding=ROUND_HALF_UP
        )
        candidates.append(
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code=selection.fee_code,
                    fee_name=selection.fee_name,
                    fee_year_key=selection.fee_year_key,
                    official_full_amount=selection.official_full_amount,
                    reduction_ratio=reduction.reduction_ratio,
                    payable_amount=payable_amount,
                    source_amount=None,
                    source_date=rate_effective_on,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=selection.source,
            )
        )
        total += payable_amount

    return FeeEstimate(
        case_id=command.case_id,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=command.trigger_context,
        currency=command.currency,
        candidates=tuple(candidates),
        total_payable_amount=total.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP),
    )


def _validate_preview_command(
    command: PreviewFeeEstimateCommand,
    rate_effective_on: date,
) -> None:
    if type(command) is not PreviewFeeEstimateCommand:
        _invalid_preview_command("command")
    if not _preview_string(command.case_id):
        _invalid_preview_command("case_id")
    if type(command.trigger_context) is not FeeEstimateContext:
        _invalid_preview_command("trigger_context")
    if not _preview_string(command.trigger_context.trigger):
        _invalid_preview_command("trigger")
    source_document_id = command.trigger_context.source_document_id
    if source_document_id is not None and not _preview_string(source_document_id):
        _invalid_preview_command("source_document_id")
    if (
        type(command.currency) is not str
        or re.fullmatch(r"[A-Z]{3}", command.currency, flags=re.ASCII) is None
    ):
        _invalid_preview_command("currency")
    if type(rate_effective_on) is not date:
        _invalid_preview_command("rate_effective_on")


def _validate_preview_source(
    selection: OfficialFeeEstimateRateCandidate,
    command: PreviewFeeEstimateCommand,
) -> None:
    source = selection.source
    if type(source) is not FeeEstimateSource:
        _rate_source_invalid(selection, "source")
    if source.status is not FeeSourceStatus.VERIFIED:
        rate_id = source.rate_id if type(source.rate_id) is str else None
        raise FeeEstimatePreviewError(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            {
                "fee_code": selection.fee_code,
                "fee_year_key": selection.fee_year_key,
                "rate_id": rate_id,
            },
        )
    for field in (
        "rate_id",
        "source_doc",
        "source_url",
        "source_policy",
        "source_version",
    ):
        if not _preview_string(getattr(source, field)):
            _rate_source_invalid(selection, field)
    if source.source_document_id != command.trigger_context.source_document_id:
        _rate_source_invalid(selection, "source_document_id")


def _validate_preview_reduction(
    selection: OfficialFeeEstimateRateCandidate,
    command: PreviewFeeEstimateCommand,
    rate_effective_on: date,
) -> None:
    if type(selection.reduction_input) is not FeeReductionInput:
        _candidate_invalid(selection.fee_code, selection.fee_year_key, "reduction_input")
    if type(selection.reduction_context) is not FeeReductionEvaluationContext:
        _candidate_invalid(selection.fee_code, selection.fee_year_key, "reduction_context")
    if selection.reduction_approval is not None and (
        type(selection.reduction_approval) is not FeeReductionApprovalContext
    ):
        _candidate_invalid(selection.fee_code, selection.fee_year_key, "reduction_approval")

    context = selection.reduction_context
    expected = (
        ("case_id", command.case_id, str),
        ("fee_code", selection.fee_code, str),
        ("fee_year_key", selection.fee_year_key, int),
        ("as_of_date", rate_effective_on, date),
    )
    for field, expected_value, expected_type in expected:
        value = getattr(context, field)
        if type(value) is not expected_type or value != expected_value:
            _candidate_invalid(
                selection.fee_code,
                selection.fee_year_key,
                f"reduction_context.{field}",
            )


def _preview_string(value: object) -> bool:
    return type(value) is str and bool(value) and value == value.strip()


def _valid_preview_amount(value: object) -> bool:
    if type(value) is not Decimal or not value.is_finite() or value < 0:
        return False
    try:
        return value == value.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return False


def _candidate_identity_details(selection: object) -> tuple[str | None, int]:
    if type(selection) is not OfficialFeeEstimateRateCandidate:
        return None, 0
    fee_code = selection.fee_code if type(selection.fee_code) is str else None
    fee_year_key = (
        selection.fee_year_key
        if type(selection.fee_year_key) is int and type(selection.fee_year_key) is not bool
        else 0
    )
    return fee_code, fee_year_key


def _invalid_preview_command(field: str) -> None:
    raise FeeEstimatePreviewError(
        FeeEstimatePreviewErrorCode.INVALID_COMMAND,
        {"field": field},
    )


def _candidate_invalid(fee_code: str | None, fee_year_key: int, field: str) -> None:
    raise FeeEstimatePreviewError(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {"fee_code": fee_code, "fee_year_key": fee_year_key, "field": field},
    )


def _rate_source_invalid(
    selection: OfficialFeeEstimateRateCandidate,
    field: str,
) -> None:
    raise FeeEstimatePreviewError(
        FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
        {
            "fee_code": selection.fee_code,
            "fee_year_key": selection.fee_year_key,
            "field": field,
        },
    )


def recognize_obligation(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            "调用方事务包含未刷新的变更",
            status_code=409,
        )
    lines = _validate_command(command)

    with transaction.no_autoflush:
        case = _case_or_fail(transaction, command.case_id)
        existing_activity = _activity_by_key(
            transaction,
            case_id=command.case_id,
            idempotency_key=command.idempotency_key,
        )
        if existing_activity is not None:
            return _replay_existing(command, transaction, case, existing_activity, lines)

        source_activity = _source_activity_or_fail(command, transaction)
        _validate_source_confirmation(command, source_activity)
        _validate_document(command, transaction)
        prior = _validate_supersede(command, transaction, lines)
        _validate_current_identities(command, transaction, lines, prior=prior)

    obligation_id = str(uuid4())
    payload = _payload(command, lines, obligation_id)
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            if prior is not None:
                _release_prior(prior, lines=prior.lines, actor_id=command.actor_id)
                transaction.flush()

            activity_result = append_case_activity(
                _activity_command(
                    command,
                    transaction,
                    source_activity=source_activity,
                    payload=payload,
                    supersedes_event_id=None if prior is None else prior.activity_id,
                ),
                transaction,
                previous_projection=_case_projection(case),
                current_projection=_case_projection(case),
                legacy_case_status=case.status,
                conflict_codes=(),
            )
            header = _new_header(command, obligation_id)
            transaction.add(header)
            transaction.add_all(_new_line(command, line, obligation_id) for line in lines)
            transaction.flush()
    except BusinessError as exc:
        if exc.code != "LIFECYCLE_IDEMPOTENCY_CONFLICT":
            raise
        return _recover_recognized_race(command, transaction, lines)
    except IntegrityError as exc:
        if not _recognized_unique_failure(exc):
            raise
        return _recover_recognized_race(command, transaction, lines)

    return _result(
        transaction,
        header,
        activity_id=activity_result.activity_id,
        idempotency_key=command.idempotency_key,
        reused=False,
        superseded_obligation_id=(None if prior is None else prior.header.id),
    )


def create_service_receivable_obligation(
    command: CreateServiceReceivableObligationCommand,
    transaction: Session,
) -> CreateServiceReceivableObligationResult:
    if type(command) is not CreateServiceReceivableObligationCommand:
        _fail("SERVICE_RECEIVABLE_INVALID", "服务费应收输入无效", status_code=400)
    for field, value, limit in (
        ("price_book_version_id", command.price_book_version_id, 36),
        ("item_code", command.item_code, 128),
        ("case_id", command.case_id, 36),
        ("actor_id", command.actor_id, 36),
        ("idempotency_key", command.idempotency_key, 96),
    ):
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or "\x00" in value
            or len(value) > limit
        ):
            _fail(
                "SERVICE_RECEIVABLE_INVALID",
                "服务费应收输入无效",
                details={"field": field},
                status_code=400,
            )
    if type(command.recognized_at) is not datetime or command.recognized_at.utcoffset() is not None:
        _fail(
            "SERVICE_RECEIVABLE_INVALID",
            "服务费应收输入无效",
            details={"field": "recognized_at"},
            status_code=400,
        )
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail("SERVICE_RECEIVABLE_CONFLICT", "服务费应收事务状态冲突", status_code=409)

    try:
        _ensure_service_receivable_write_transaction(transaction)
        with transaction.no_autoflush:
            book = transaction.scalar(
                _service_receivable_book_for_update(command.price_book_version_id)
            )
            case = transaction.scalar(select(Case).where(Case.id == command.case_id))
    except OperationalError as exc:
        raise BusinessError(
            "SERVICE_RECEIVABLE_CONFLICT",
            "服务费应收并发锁定冲突",
            status_code=409,
        ) from exc
    if case is None:
        _fail("CASE_NOT_FOUND", "案件不存在", status_code=404)
    if (
        book is None
        or book.source_classification != "PRODUCTION"
        or book.status != "ACTIVE"
        or book.scope_key != "GLOBAL"
        or book.current_identity_key != "GLOBAL"
        or book.effective_from > command.recognized_at
        or (book.effective_to is not None and command.recognized_at >= book.effective_to)
    ):
        _fail("SERVICE_RECEIVABLE_CONFLICT", "服务价格版本不可用", status_code=409)
    try:
        decision_value = _activation_snapshot(book)
        gate = resolve_decision_gate(
            ResolveDecisionGateCommand(
                gate_code=DecisionGateCode.SERVICE_RATE_VERSION,
                scope_key="GLOBAL",
                as_of=command.recognized_at,
            ),
            transaction,
        )
        snapshot = json.loads(book.item_snapshot)
    except (BusinessError, TypeError, ValueError) as exc:
        raise BusinessError(
            "SERVICE_RECEIVABLE_CONFLICT",
            "服务价格版本或决策门不可用",
            status_code=409,
        ) from exc
    if (
        gate.resolved_scope_key != "GLOBAL"
        or gate.source_reference != book.source_reference
        or gate.source_version != book.book_version
        or gate.decision_value != decision_value
        or type(snapshot) is not dict
        or type(snapshot.get("items")) is not list
    ):
        _fail("SERVICE_RECEIVABLE_CONFLICT", "服务价格版本或决策门不匹配", status_code=409)
    matches = [item for item in snapshot["items"] if item.get("item_code") == command.item_code]
    if len(matches) != 1:
        _fail("SERVICE_RECEIVABLE_CONFLICT", "服务价格项目不存在或不唯一", status_code=409)
    try:
        unit_price = Decimal(matches[0]["unit_price"])
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise BusinessError(
            "SERVICE_RECEIVABLE_CONFLICT",
            "服务价格项目金额无效",
            status_code=409,
        ) from exc
    if not _valid_amount(unit_price, optional=False):
        _fail("SERVICE_RECEIVABLE_CONFLICT", "服务价格项目金额无效", status_code=409)

    source_key = f"service-receivable-source:{command.idempotency_key}"
    recognition_key = f"service-receivable:{command.idempotency_key}"
    with transaction.no_autoflush:
        source_owners = tuple(
            transaction.scalars(
                select(CaseActivityEvent).where(CaseActivityEvent.idempotency_key == source_key)
            )
        )
        recognition_owners = tuple(
            transaction.scalars(
                select(CaseActivityEvent).where(
                    CaseActivityEvent.idempotency_key == recognition_key
                )
            )
        )
    if (
        len(source_owners) > 1
        or len(recognition_owners) > 1
        or bool(source_owners) != bool(recognition_owners)
        or any(owner.case_id != command.case_id for owner in (*source_owners, *recognition_owners))
    ):
        _fail(
            "SERVICE_RECEIVABLE_CONFLICT",
            "服务费应收幂等键已由其他案件或不完整事实占用",
            status_code=409,
        )
    existing_source = source_owners[0] if source_owners else None
    if existing_source is not None:
        existing_recognition = recognition_owners[0]
        if (
            existing_source.activity_type != "SERVICE_PRICE_ITEM_SELECTED"
            or existing_source.lane != ActivityLane.FEE.value
            or existing_recognition.activity_type != _ACTIVITY_TYPE
            or existing_recognition.lane != ActivityLane.FEE.value
            or existing_recognition.source_activity_id != existing_source.id
        ):
            _fail(
                "SERVICE_RECEIVABLE_CONFLICT",
                "服务费应收幂等事实不匹配",
                status_code=409,
            )
    source_time = command.recognized_at if existing_source is None else existing_source.effective_at
    projection = _case_projection(case)
    try:
        with transaction.begin_nested():
            source_result = append_case_activity(
                LifecycleEventCommand(
                    case_id=command.case_id,
                    event_type="SERVICE_PRICE_ITEM_SELECTED",
                    lane=ActivityLane.FEE,
                    effective_at=source_time,
                    occurred_at=source_time,
                    evidence_refs=(
                        EvidenceReference(
                            case_id=command.case_id,
                            evidence_kind="SERVICE_PRICE_BOOK_ITEM",
                            object_type="ServicePriceBook",
                            object_id=book.id,
                            content_hash=book.item_snapshot_hash,
                            captured_at=source_time,
                        ),
                    ),
                    actor_id=command.actor_id,
                    reviewer_id=None,
                    idempotency_key=source_key,
                    source_activity_id=None,
                    supersedes_event_id=None,
                    payload={
                        "schema": _SERVICE_SOURCE_SCHEMA,
                        "price_book_version_id": book.id,
                        "book_version": book.book_version,
                        "source_content_hash": book.source_content_hash,
                        "item_snapshot_hash": book.item_snapshot_hash,
                        "item_code": command.item_code,
                        "unit_price": format(unit_price, "f"),
                        "currency": book.currency,
                        "tax_policy": book.tax_policy,
                        "discount_policy": book.discount_policy,
                    },
                    confirmation_status=ConfirmationStatus.CONFIRMED,
                ),
                transaction,
                previous_projection=projection,
                current_projection=projection,
                legacy_case_status=case.status,
                conflict_codes=(),
            )
            recognition = recognize_obligation(
                RecognizeFeeObligationCommand(
                    case_id=command.case_id,
                    source_activity_id=source_result.activity_id,
                    source_document_id=None,
                    fee_domain=FeeDomain.SERVICE,
                    obligation_type="SERVICE_FEE",
                    due_date=None,
                    currency=book.currency,
                    source_status=FeeSourceStatus.VERIFIED,
                    lines=(
                        FeeObligationLineInput(
                            fee_code=_service_receivable_fee_code(command.item_code),
                            fee_name=command.item_code,
                            fee_year_key=0,
                            official_full_amount=None,
                            reduction_ratio=Decimal("0.0000"),
                            payable_amount=unit_price,
                            source_amount=unit_price,
                            source_date=source_time.date(),
                            difference_review_state=FeeDifferenceReviewState.MATCHED,
                        ),
                    ),
                    actor_id=command.actor_id,
                    idempotency_key=recognition_key,
                    supersedes_obligation_id=None,
                    supersede_reason=None,
                ),
                transaction,
            )
            if source_result.reused != recognition.reused:
                _fail("SERVICE_RECEIVABLE_CONFLICT", "服务费应收重放状态冲突", status_code=409)
    except (BusinessError, IntegrityError, OperationalError) as exc:
        if isinstance(exc, BusinessError) and exc.code == "SERVICE_RECEIVABLE_CONFLICT":
            raise
        raise BusinessError(
            "SERVICE_RECEIVABLE_CONFLICT",
            "服务费应收持久化冲突",
            status_code=409,
        ) from exc
    return CreateServiceReceivableObligationResult(
        recognition=recognition,
        price_book_version_id=book.id,
        item_code=command.item_code,
        unit_price=unit_price,
        source_activity_id=source_result.activity_id,
        reused=recognition.reused,
    )


def _service_receivable_fee_code(item_code: str) -> str:
    if len(item_code) <= 64:
        return item_code
    return hashlib.sha256(item_code.encode("utf-8")).hexdigest()


def _service_receivable_book_for_update(price_book_version_id: str):
    return (
        select(ServicePriceBook)
        .where(ServicePriceBook.id == price_book_version_id)
        .with_for_update()
    )


def get_fee_obligation(
    obligation_id: str,
    transaction: Session,
) -> FeeObligation:
    if (
        type(obligation_id) is not str
        or not obligation_id
        or obligation_id.strip() != obligation_id
        or "\x00" in obligation_id
        or len(obligation_id) > 36
    ):
        _fail(
            "FEE_OBLIGATION_DETAIL_INVALID",
            "费用义务标识无效",
            details={"field": "obligation_id"},
            status_code=400,
        )

    current_child = aliased(FeeObligationModel)
    prior_header = aliased(FeeObligationModel)
    with transaction.no_autoflush:
        header_rows = tuple(
            transaction.execute(
                select(
                    FeeObligationModel.id.label("id"),
                    FeeObligationModel.case_id.label("case_id"),
                    FeeObligationModel.source_activity_id.label("source_activity_id"),
                    FeeObligationModel.source_document_id.label("source_document_id"),
                    FeeObligationModel.fee_domain.label("fee_domain"),
                    FeeObligationModel.obligation_type.label("obligation_type"),
                    FeeObligationModel.obligation_status.label("obligation_status"),
                    FeeObligationModel.due_date.label("due_date"),
                    FeeObligationModel.currency.label("currency"),
                    FeeObligationModel.source_status.label("source_status"),
                    FeeObligationModel.client_instruction_status.label("client_instruction_status"),
                    FeeObligationModel.draft_status.label("draft_status"),
                    FeeObligationModel.payment_status.label("payment_status"),
                    FeeObligationModel.official_evidence_status.label("official_evidence_status"),
                    FeeObligationModel.supersedes_obligation_id.label("supersedes_obligation_id"),
                    FeeObligationModel.supersede_reason.label("supersede_reason"),
                    Document.case_id.label("document_case_id"),
                    current_child.id.label("current_child_id"),
                    current_child.case_id.label("current_child_case_id"),
                    current_child.source_activity_id.label("current_child_source_activity_id"),
                    current_child.fee_domain.label("current_child_fee_domain"),
                    current_child.obligation_type.label("current_child_obligation_type"),
                    current_child.obligation_status.label("current_child_obligation_status"),
                    current_child.currency.label("current_child_currency"),
                    current_child.source_status.label("current_child_source_status"),
                    current_child.supersedes_obligation_id.label(
                        "current_child_supersedes_obligation_id"
                    ),
                    current_child.supersede_reason.label("current_child_supersede_reason"),
                    prior_header.id.label("prior_id"),
                    prior_header.case_id.label("prior_case_id"),
                    prior_header.source_activity_id.label("prior_source_activity_id"),
                    prior_header.fee_domain.label("prior_fee_domain"),
                    prior_header.obligation_type.label("prior_obligation_type"),
                    prior_header.obligation_status.label("prior_obligation_status"),
                    prior_header.currency.label("prior_currency"),
                )
                .select_from(FeeObligationModel)
                .outerjoin(
                    Document,
                    Document.id == FeeObligationModel.source_document_id,
                )
                .outerjoin(
                    current_child,
                    current_child.supersedes_obligation_id == FeeObligationModel.id,
                )
                .outerjoin(
                    prior_header,
                    prior_header.id == FeeObligationModel.supersedes_obligation_id,
                )
                .where(FeeObligationModel.id == obligation_id)
            )
            .mappings()
            .all()
        )
        if not header_rows:
            _fail("FEE_OBLIGATION_NOT_FOUND", "费用义务不存在", status_code=404)
        if len(header_rows) != 1:
            _stored_state_invalid()
        header = header_rows[0]
        _validate_detail_header(header)

        line_rows = tuple(
            transaction.execute(
                select(
                    FeeObligationLineModel.id.label("id"),
                    FeeObligationLineModel.obligation_id.label("obligation_id"),
                    FeeObligationLineModel.case_id.label("case_id"),
                    FeeObligationLineModel.source_activity_id.label("source_activity_id"),
                    FeeObligationLineModel.fee_code.label("fee_code"),
                    FeeObligationLineModel.fee_name.label("fee_name"),
                    FeeObligationLineModel.fee_year_key.label("fee_year_key"),
                    FeeObligationLineModel.official_full_amount.label("official_full_amount"),
                    FeeObligationLineModel.reduction_ratio.label("reduction_ratio"),
                    FeeObligationLineModel.payable_amount.label("payable_amount"),
                    FeeObligationLineModel.source_amount.label("source_amount"),
                    FeeObligationLineModel.source_date.label("source_date"),
                    FeeObligationLineModel.difference_review_state.label("difference_review_state"),
                    FeeObligationLineModel.current_identity_key.label("current_identity_key"),
                )
                .where(FeeObligationLineModel.obligation_id == obligation_id)
                .order_by(
                    FeeObligationLineModel.fee_code,
                    FeeObligationLineModel.fee_year_key,
                    FeeObligationLineModel.id,
                )
            )
            .mappings()
            .all()
        )
        lines = _detail_lines(header, line_rows)

        activity_rows = tuple(
            transaction.execute(
                select(
                    CaseActivityEvent.id.label("id"),
                    CaseActivityEvent.case_id.label("case_id"),
                    CaseActivityEvent.sequence.label("sequence"),
                    CaseActivityEvent.lane.label("lane"),
                    CaseActivityEvent.activity_type.label("activity_type"),
                    CaseActivityEvent.source_activity_id.label("source_activity_id"),
                    CaseActivityEvent.occurred_at.label("occurred_at"),
                    CaseActivityEvent.effective_at.label("effective_at"),
                    CaseActivityEvent.confirmation_status.label("confirmation_status"),
                    CaseActivityEvent.old_business_stage.label("old_business_stage"),
                    CaseActivityEvent.new_business_stage.label("new_business_stage"),
                    CaseActivityEvent.old_official_procedure_stage.label(
                        "old_official_procedure_stage"
                    ),
                    CaseActivityEvent.new_official_procedure_stage.label(
                        "new_official_procedure_stage"
                    ),
                    CaseActivityEvent.old_legal_status.label("old_legal_status"),
                    CaseActivityEvent.new_legal_status.label("new_legal_status"),
                    CaseActivityEvent.actor_id.label("actor_id"),
                    CaseActivityEvent.reviewer_id.label("reviewer_id"),
                    CaseActivityEvent.idempotency_key.label("idempotency_key"),
                    CaseActivityEvent.supersedes_event_id.label("supersedes_event_id"),
                    CaseActivityEvent.payload_json.label("payload_json"),
                ).where(
                    CaseActivityEvent.case_id == header["case_id"],
                    (CaseActivityEvent.id == header["source_activity_id"])
                    | (CaseActivityEvent.id == header["current_child_source_activity_id"])
                    | (
                        (CaseActivityEvent.lane == ActivityLane.FEE.value)
                        & (
                            CaseActivityEvent.activity_type.in_(
                                (
                                    _ACTIVITY_TYPE,
                                    _GRANT_REVIEW_ACTIVITY_TYPE,
                                    _GRANT_REGISTRATION_REVIEW_ACTIVITY_TYPE,
                                )
                            )
                        )
                    ),
                )
            )
            .mappings()
            .all()
        )
        _validate_detail_activities(transaction, header, line_rows, activity_rows)

        relation_rows = tuple(
            transaction.execute(
                select(
                    FeeObligationDraftItemLink.id.label("link_id"),
                    FeeObligationDraftItemLink.obligation_line_id.label("obligation_line_id"),
                    FeeItem.id.label("item_id"),
                    FeeItem.draft_id.label("item_draft_id"),
                    FeeItem.case_id.label("item_case_id"),
                    FeeItem.fee_code.label("item_fee_code"),
                    FeeItem.fee_type.label("item_fee_type"),
                    FeeItem.year_no.label("item_year_no"),
                    FeeDraft.id.label("draft_id"),
                    FeeDraft.case_id.label("draft_case_id"),
                    FeeDraft.currency.label("draft_currency"),
                    GovPayment.id.label("payment_id"),
                    GovPayment.pay_list_id.label("payment_pay_list_id"),
                    GovPayment.case_id.label("payment_case_id"),
                    GovPayment.fee_item_id.label("payment_fee_item_id"),
                    GovPayment.currency.label("payment_currency"),
                    PayList.id.label("pay_list_id"),
                    PayList.currency.label("pay_list_currency"),
                )
                .select_from(FeeObligationDraftItemLink)
                .outerjoin(
                    FeeItem,
                    FeeItem.id == FeeObligationDraftItemLink.fee_item_id,
                )
                .outerjoin(FeeDraft, FeeDraft.id == FeeItem.draft_id)
                .outerjoin(GovPayment, GovPayment.fee_item_id == FeeItem.id)
                .outerjoin(PayList, PayList.id == GovPayment.pay_list_id)
                .where(
                    FeeObligationDraftItemLink.obligation_line_id.in_(
                        tuple(line.id for line in lines)
                    )
                )
            )
            .mappings()
            .all()
        )
        pay_list_status = _detail_pay_list_status(header, line_rows, relation_rows)

    return FeeObligation(
        id=header["id"],
        case_id=header["case_id"],
        source=FeeObligationSource(
            source_activity_id=header["source_activity_id"],
            source_document_id=header["source_document_id"],
            status=_stored_enum(FeeSourceStatus, header["source_status"]),
        ),
        fee_domain=_stored_enum(FeeDomain, header["fee_domain"]),
        obligation_type=header["obligation_type"],
        due_date=header["due_date"],
        currency=header["currency"],
        statuses=FeeObligationStatuses(
            estimate_status=None,
            obligation_status=_stored_enum(
                FeeObligationStatus,
                header["obligation_status"],
            ),
            client_instruction_status=_stored_enum(
                FeeClientInstructionStatus,
                header["client_instruction_status"],
            ),
            draft_status=_stored_enum(
                FeeObligationDraftStatus,
                header["draft_status"],
            ),
            pay_list_status=pay_list_status,
            payment_status=_stored_enum(
                FeePaymentStatus,
                header["payment_status"],
            ),
            official_evidence_status=_stored_enum(
                FeeOfficialEvidenceStatus,
                header["official_evidence_status"],
            ),
        ),
        lines=lines,
        supersedes_obligation_id=header["supersedes_obligation_id"],
        supersede_reason=header["supersede_reason"],
    )


def _validate_detail_header(header: Mapping[str, object]) -> None:
    for field, limit in (
        ("id", 36),
        ("case_id", 36),
        ("source_activity_id", 36),
        ("obligation_type", 64),
    ):
        value = header[field]
        if type(value) is not str or not value.strip() or len(value) > limit:
            _stored_state_invalid()
    if header["source_document_id"] is not None and (
        type(header["source_document_id"]) is not str
        or not cast(str, header["source_document_id"]).strip()
        or len(cast(str, header["source_document_id"])) > 36
        or header["document_case_id"] != header["case_id"]
    ):
        _stored_state_invalid()
    fee_domain = _stored_enum(FeeDomain, cast(str, header["fee_domain"]))
    _stored_enum(FeeSourceStatus, cast(str, header["source_status"]))
    obligation_status = _stored_enum(
        FeeObligationStatus,
        cast(str, header["obligation_status"]),
    )
    _stored_enum(
        FeeClientInstructionStatus,
        cast(str, header["client_instruction_status"]),
    )
    _stored_enum(FeeObligationDraftStatus, cast(str, header["draft_status"]))
    _stored_enum(FeePaymentStatus, cast(str, header["payment_status"]))
    _stored_enum(
        FeeOfficialEvidenceStatus,
        cast(str, header["official_evidence_status"]),
    )
    if (
        not _valid_date(header["due_date"], optional=True)
        or type(header["currency"]) is not str
        or re.fullmatch(r"[A-Z]{3}", cast(str, header["currency"]), flags=re.ASCII) is None
        or (fee_domain is FeeDomain.GOV and header["source_document_id"] is None)
    ):
        _stored_state_invalid()
    has_prior = header["supersedes_obligation_id"] is not None
    has_reason = header["supersede_reason"] is not None
    if has_prior != has_reason:
        _stored_state_invalid()
    if has_prior and (
        type(header["supersedes_obligation_id"]) is not str
        or not cast(str, header["supersedes_obligation_id"]).strip()
        or len(cast(str, header["supersedes_obligation_id"])) > 36
        or type(header["supersede_reason"]) is not str
        or not cast(str, header["supersede_reason"]).strip()
    ):
        _stored_state_invalid()
    if has_prior:
        if (
            header["prior_id"] != header["supersedes_obligation_id"]
            or header["prior_case_id"] != header["case_id"]
            or header["prior_source_activity_id"] == header["source_activity_id"]
            or header["prior_fee_domain"] != header["fee_domain"]
            or header["prior_obligation_type"] != header["obligation_type"]
            or header["prior_obligation_status"] != FeeObligationStatus.SUPERSEDED.value
            or header["prior_currency"] != header["currency"]
        ):
            _stored_state_invalid()
    elif header["prior_id"] is not None:
        _stored_state_invalid()
    child_id = header["current_child_id"]
    if obligation_status is FeeObligationStatus.RECOGNIZED:
        if child_id is not None:
            _stored_state_invalid()
        return
    if (
        type(child_id) is not str
        or not child_id.strip()
        or len(child_id) > 36
        or header["current_child_case_id"] != header["case_id"]
        or header["current_child_source_activity_id"] == header["source_activity_id"]
        or header["current_child_fee_domain"] != header["fee_domain"]
        or header["current_child_obligation_type"] != header["obligation_type"]
        or header["current_child_obligation_status"] != FeeObligationStatus.RECOGNIZED.value
        or header["current_child_currency"] != header["currency"]
        or header["current_child_supersedes_obligation_id"] != header["id"]
        or type(header["current_child_supersede_reason"]) is not str
        or not cast(str, header["current_child_supersede_reason"]).strip()
    ):
        _stored_state_invalid()
    _stored_enum(
        FeeSourceStatus,
        cast(str, header["current_child_source_status"]),
    )


def _detail_lines(
    header: Mapping[str, object],
    rows: tuple[Mapping[str, object], ...],
) -> tuple[FeeObligationLine, ...]:
    if not rows:
        _stored_state_invalid()
    status = _stored_enum(
        FeeObligationStatus,
        cast(str, header["obligation_status"]),
    )
    identities: set[tuple[str, int]] = set()
    values: list[FeeObligationLine] = []
    for row in rows:
        for field, limit in (("id", 36), ("fee_code", 64), ("fee_name", 256)):
            value = row[field]
            if type(value) is not str or not value.strip() or len(value) > limit:
                _stored_state_invalid()
        if (
            row["obligation_id"] != header["id"]
            or row["case_id"] != header["case_id"]
            or row["source_activity_id"] != header["source_activity_id"]
            or type(row["fee_year_key"]) is not int
            or not 0 <= cast(int, row["fee_year_key"]) <= 2147483647
            or not _valid_amount(row["official_full_amount"], optional=True)
            or not _valid_ratio(row["reduction_ratio"])
            or not _valid_amount(row["payable_amount"], optional=False)
            or not _valid_amount(row["source_amount"], optional=True)
            or not _valid_date(row["source_date"], optional=True)
        ):
            _stored_state_invalid()
        identity = (
            cast(str, row["fee_code"]),
            cast(int, row["fee_year_key"]),
        )
        if identity in identities:
            _stored_state_invalid()
        identities.add(identity)
        expected_key = _identity_key(
            cast(str, row["case_id"]),
            cast(str, row["source_activity_id"]),
            identity[0],
            identity[1],
        )
        if (
            status is FeeObligationStatus.RECOGNIZED and row["current_identity_key"] != expected_key
        ) or (status is FeeObligationStatus.SUPERSEDED and row["current_identity_key"] is not None):
            _stored_state_invalid()
        values.append(
            FeeObligationLine(
                id=cast(str, row["id"]),
                obligation_id=cast(str, row["obligation_id"]),
                case_id=cast(str, row["case_id"]),
                source_activity_id=cast(str, row["source_activity_id"]),
                fee_code=identity[0],
                fee_name=cast(str, row["fee_name"]),
                fee_year_key=identity[1],
                official_full_amount=cast(Decimal | None, row["official_full_amount"]),
                reduction_ratio=cast(Decimal, row["reduction_ratio"]),
                payable_amount=cast(Decimal, row["payable_amount"]),
                source_amount=cast(Decimal | None, row["source_amount"]),
                source_date=cast(date | None, row["source_date"]),
                difference_review_state=_stored_enum(
                    FeeDifferenceReviewState,
                    cast(str, row["difference_review_state"]),
                ),
                current_identity_key=cast(str | None, row["current_identity_key"]),
            )
        )
    return tuple(values)


def _detail_line_payload(line: Mapping[str, object]) -> dict[str, object]:
    return {
        "difference_review_state": line["difference_review_state"],
        "fee_code": line["fee_code"],
        "fee_name": line["fee_name"],
        "fee_year_key": line["fee_year_key"],
        "official_full_amount": _amount_text(cast(Decimal | None, line["official_full_amount"])),
        "payable_amount": _amount_text(cast(Decimal, line["payable_amount"])),
        "reduction_ratio": format(cast(Decimal, line["reduction_ratio"]), ".4f"),
        "source_amount": _amount_text(cast(Decimal | None, line["source_amount"])),
        "source_date": (
            None if line["source_date"] is None else cast(date, line["source_date"]).isoformat()
        ),
    }


def _detail_grant_review_snapshot(
    line: Mapping[str, object],
    *,
    official_full_amount: object,
    difference_review_state: object,
) -> dict[str, object]:
    return {
        "obligation_line_id": line["id"],
        "fee_code": line["fee_code"],
        "fee_name": line["fee_name"],
        "fee_year_key": line["fee_year_key"],
        "official_full_amount": official_full_amount,
        "reduction_ratio": format(cast(Decimal, line["reduction_ratio"]), ".4f"),
        "payable_amount": _amount_text(cast(Decimal, line["payable_amount"])),
        "source_amount": _amount_text(cast(Decimal | None, line["source_amount"])),
        "source_date": (
            None if line["source_date"] is None else cast(date, line["source_date"]).isoformat()
        ),
        "difference_review_state": difference_review_state,
        "current_identity_key": line["current_identity_key"],
    }


def _detail_recognition_lines(
    transaction: Session,
    header: Mapping[str, object],
    lines: tuple[Mapping[str, object], ...],
    rows: tuple[Mapping[str, object], ...],
    *,
    recognition: Mapping[str, object],
    payload: dict[str, object],
) -> tuple[Mapping[str, object], ...]:
    obligation_payload = payload.get("obligation")
    if type(obligation_payload) is not dict:
        _stored_state_invalid()
    recognized_lines = obligation_payload.get("lines")
    if type(recognized_lines) is not list or len(recognized_lines) != len(lines):
        _stored_state_invalid()
    if header["obligation_type"] == "GRANT_YEAR_ANNUITY":
        review_activity_type = _GRANT_REVIEW_ACTIVITY_TYPE
        review_schema = _GRANT_REVIEW_PAYLOAD_SCHEMA
    elif header["obligation_type"] == "GRANT_REGISTRATION_OFFICIAL_FEES":
        review_activity_type = _GRANT_REGISTRATION_REVIEW_ACTIVITY_TYPE
        review_schema = _GRANT_REGISTRATION_REVIEW_PAYLOAD_SCHEMA
    else:
        review_activity_type = None
        review_schema = None
    reviews: list[tuple[Mapping[str, object], dict[str, object]]] = []
    for row in rows:
        if (
            row["lane"] != ActivityLane.FEE.value
            or row["activity_type"] != review_activity_type
        ):
            continue
        try:
            review_payload = _strict_json_loads(cast(str, row["payload_json"]))
        except (TypeError, ValueError):
            _stored_state_invalid()
        if type(review_payload) is not dict:
            _stored_state_invalid()
        if review_payload.get("obligation_id") == header["id"]:
            reviews.append((row, review_payload))
    if recognized_lines == [_detail_line_payload(line) for line in lines]:
        if reviews:
            _stored_state_invalid()
        return lines
    if (
        header["obligation_type"]
        not in {"GRANT_YEAR_ANNUITY", "GRANT_REGISTRATION_OFFICIAL_FEES"}
        or header["obligation_status"] != FeeObligationStatus.RECOGNIZED.value
    ):
        _stored_state_invalid()
    if len(reviews) != 1:
        _stored_state_invalid()
    review, review_payload = reviews[0]
    canonical_review = json.dumps(
        review_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    try:
        confirmed_at = datetime.fromisoformat(cast(str, review_payload.get("confirmed_at")))
    except (TypeError, ValueError):
        _stored_state_invalid()
    if (
        set(review_payload) != _GRANT_REVIEW_PAYLOAD_KEYS
        or review_payload["schema"] != review_schema
        or review_payload["review_basis"] != _GRANT_REVIEW_BASIS
        or review_payload["case_id"] != header["case_id"]
        or review_payload["obligation_id"] != header["id"]
        or review_payload["source_activity_id"] != header["source_activity_id"]
        or review_payload["source_document_id"] != header["source_document_id"]
        or type(review_payload["grant_fee_task_id"]) is not str
        or not cast(str, review_payload["grant_fee_task_id"]).strip()
        or "\x00" in cast(str, review_payload["grant_fee_task_id"])
        or len(cast(str, review_payload["grant_fee_task_id"])) > 36
        or type(review_payload["reviewed_evidence_version_id"]) is not str
        or not cast(str, review_payload["reviewed_evidence_version_id"]).strip()
        or "\x00" in cast(str, review_payload["reviewed_evidence_version_id"])
        or len(cast(str, review_payload["reviewed_evidence_version_id"])) > 36
        or type(review_payload["reviewed_evidence_content_hash"]) is not str
        or re.fullmatch(
            r"sha256:[0-9a-f]{64}",
            cast(str, review_payload["reviewed_evidence_content_hash"]),
        )
        is None
        or review["payload_json"] != canonical_review
        or review["source_activity_id"] != header["source_activity_id"]
        or review["confirmation_status"] != ConfirmationStatus.CONFIRMED.value
        or review["old_business_stage"] != review["new_business_stage"]
        or review["old_official_procedure_stage"] != review["new_official_procedure_stage"]
        or review["old_legal_status"] != review["new_legal_status"]
        or review["actor_id"] != review["reviewer_id"]
        or type(review["actor_id"]) is not str
        or not cast(str, review["actor_id"]).strip()
        or "\x00" in cast(str, review["actor_id"])
        or type(review["idempotency_key"]) is not str
        or not cast(str, review["idempotency_key"]).strip()
        or "\x00" in cast(str, review["idempotency_key"])
        or review["supersedes_event_id"] is not None
        or review["occurred_at"] != review["effective_at"]
        or review["id"] == recognition["id"]
        or type(review["sequence"]) is not int
        or type(recognition["sequence"]) is not int
        or cast(int, review["sequence"]) <= cast(int, recognition["sequence"])
        or confirmed_at.tzinfo is not None
        or confirmed_at != review["occurred_at"]
        or review_payload["confirmed_at"] != cast(datetime, review["occurred_at"]).isoformat()
    ):
        _stored_state_invalid()
    before_lines = review_payload["before_lines"]
    after_lines = review_payload["after_lines"]
    if (
        type(before_lines) is not list
        or type(after_lines) is not list
        or len(before_lines) != len(lines)
        or len(after_lines) != len(lines)
        or any(
            type(item) is not dict or set(item) != _GRANT_REVIEW_LINE_KEYS for item in before_lines
        )
        or any(
            type(item) is not dict or set(item) != _GRANT_REVIEW_LINE_KEYS for item in after_lines
        )
    ):
        _stored_state_invalid()

    recognized_by_identity: dict[tuple[object, object], Mapping[str, object]] = {}
    for recognized in recognized_lines:
        if type(recognized) is not dict:
            _stored_state_invalid()
        identity = (recognized.get("fee_code"), recognized.get("fee_year_key"))
        if identity in recognized_by_identity:
            _stored_state_invalid()
        recognized_by_identity[identity] = recognized
    ordered_lines = tuple(
        sorted(lines, key=lambda line: (line["fee_year_key"], line["fee_code"], line["id"]))
    )
    expected_before: list[dict[str, object]] = []
    synthetic_recognition: list[Mapping[str, object]] = []
    for line in ordered_lines:
        recognized = recognized_by_identity.get((line["fee_code"], line["fee_year_key"]))
        if recognized is None:
            _stored_state_invalid()
        if (
            recognized.get("official_full_amount") is not None
            or recognized.get("difference_review_state")
            != FeeDifferenceReviewState.REVIEW_REQUIRED.value
        ):
            _stored_state_invalid()
        synthetic = dict(line)
        synthetic["official_full_amount"] = None
        synthetic["difference_review_state"] = FeeDifferenceReviewState.REVIEW_REQUIRED.value
        if recognized != _detail_line_payload(synthetic):
            _stored_state_invalid()
        synthetic_recognition.append(synthetic)
        expected_before.append(
            _detail_grant_review_snapshot(
                line,
                official_full_amount=None,
                difference_review_state=FeeDifferenceReviewState.REVIEW_REQUIRED.value,
            )
        )
    expected_after = [
        _detail_grant_review_snapshot(
            line,
            official_full_amount=_amount_text(cast(Decimal, line["official_full_amount"])),
            difference_review_state=FeeDifferenceReviewState.MATCHED.value,
        )
        for line in ordered_lines
    ]
    if (
        before_lines != expected_before
        or after_lines != expected_after
        or any(
            line["official_full_amount"] is None
            or line["difference_review_state"] != FeeDifferenceReviewState.MATCHED.value
            for line in ordered_lines
        )
    ):
        _stored_state_invalid()

    evidence_rows = tuple(
        transaction.execute(
            select(
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
                CaseActivityEventEvidence.content_hash,
                CaseActivityEventEvidence.captured_at,
            ).where(CaseActivityEventEvidence.activity_id == review["id"])
        ).mappings()
    )
    source_evidence_rows = tuple(
        transaction.execute(
            select(
                CaseActivityEventEvidence.case_id,
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
                CaseActivityEventEvidence.content_hash,
                CaseActivityEventEvidence.captured_at,
            ).where(CaseActivityEventEvidence.activity_id == header["source_activity_id"])
        ).mappings()
    )
    evidence_by_kind = {row["evidence_kind"]: row for row in evidence_rows}
    evidence_identity = {tuple(row[field] for field in row.keys()) for row in evidence_rows}
    source_evidence_identity = {
        tuple(row[field] for field in row.keys()) for row in source_evidence_rows
    }
    if (
        len(evidence_rows) != 2
        or len(source_evidence_rows) != 2
        or evidence_identity != source_evidence_identity
        or set(evidence_by_kind) != {"SOURCE_DOCUMENT", "DOCUMENT_EVIDENCE_VERSION"}
        or evidence_by_kind["SOURCE_DOCUMENT"]["case_id"] != header["case_id"]
        or evidence_by_kind["SOURCE_DOCUMENT"]["object_type"] != "Document"
        or evidence_by_kind["SOURCE_DOCUMENT"]["object_id"] != header["source_document_id"]
        or evidence_by_kind["DOCUMENT_EVIDENCE_VERSION"]["case_id"] != header["case_id"]
        or evidence_by_kind["DOCUMENT_EVIDENCE_VERSION"]["object_type"] != "DocumentEvidenceVersion"
        or evidence_by_kind["DOCUMENT_EVIDENCE_VERSION"]["object_id"]
        != review_payload["reviewed_evidence_version_id"]
        or any(
            row["content_hash"] != review_payload["reviewed_evidence_content_hash"]
            for row in evidence_rows
        )
        or evidence_rows[0]["captured_at"] != evidence_rows[1]["captured_at"]
    ):
        _stored_state_invalid()
    return tuple(synthetic_recognition)


def _validate_detail_activities(
    transaction: Session,
    header: Mapping[str, object],
    lines: tuple[Mapping[str, object], ...],
    rows: tuple[Mapping[str, object], ...],
) -> None:
    source_rows = tuple(row for row in rows if row["id"] == header["source_activity_id"])
    if len(source_rows) != 1:
        _stored_state_invalid()
    source = source_rows[0]
    source_status = _stored_enum(
        FeeSourceStatus,
        cast(str, header["source_status"]),
    )
    expected_confirmation = (
        ConfirmationStatus.LEGACY_UNVERIFIED.value
        if source_status is FeeSourceStatus.LEGACY_UNVERIFIED
        else ConfirmationStatus.CONFIRMED.value
    )
    if (
        source["case_id"] != header["case_id"]
        or source["confirmation_status"] != expected_confirmation
        or (source["lane"] == ActivityLane.FEE.value and source["activity_type"] == _ACTIVITY_TYPE)
    ):
        _stored_state_invalid()

    decoded: list[tuple[Mapping[str, object], dict[str, object]]] = []
    for row in rows:
        if row["lane"] != ActivityLane.FEE.value or row["activity_type"] != _ACTIVITY_TYPE:
            continue
        try:
            payload = _strict_json_loads(cast(str, row["payload_json"]))
        except (TypeError, ValueError):
            if row["source_activity_id"] == header["source_activity_id"]:
                _stored_state_invalid()
            continue
        if type(payload) is not dict or payload.get("schema") != _PAYLOAD_SCHEMA:
            if row["source_activity_id"] == header["source_activity_id"]:
                _stored_state_invalid()
            continue
        decoded.append((row, payload))

    matches = tuple(
        (row, payload) for row, payload in decoded if payload.get("obligation_id") == header["id"]
    )
    if len(matches) != 1:
        _stored_state_invalid()
    recognition, payload = matches[0]
    recognition_lines = _detail_recognition_lines(
        transaction,
        header,
        lines,
        rows,
        recognition=recognition,
        payload=payload,
    )
    expected_payload = {
        "schema": _PAYLOAD_SCHEMA,
        "obligation_id": header["id"],
        "obligation": {
            "actor_id": recognition["actor_id"],
            "case_id": header["case_id"],
            "currency": header["currency"],
            "due_date": (
                None if header["due_date"] is None else cast(date, header["due_date"]).isoformat()
            ),
            "fee_domain": header["fee_domain"],
            "lines": [
                {
                    "difference_review_state": line["difference_review_state"],
                    "fee_code": line["fee_code"],
                    "fee_name": line["fee_name"],
                    "fee_year_key": line["fee_year_key"],
                    "official_full_amount": _amount_text(
                        cast(Decimal | None, line["official_full_amount"])
                    ),
                    "payable_amount": _amount_text(cast(Decimal, line["payable_amount"])),
                    "reduction_ratio": format(
                        cast(Decimal, line["reduction_ratio"]),
                        ".4f",
                    ),
                    "source_amount": _amount_text(cast(Decimal | None, line["source_amount"])),
                    "source_date": (
                        None
                        if line["source_date"] is None
                        else cast(date, line["source_date"]).isoformat()
                    ),
                }
                for line in recognition_lines
            ],
            "obligation_type": header["obligation_type"],
            "source_activity_id": header["source_activity_id"],
            "source_document_id": header["source_document_id"],
            "source_status": header["source_status"],
            "supersede_reason": header["supersede_reason"],
            "supersedes_obligation_id": header["supersedes_obligation_id"],
        },
    }
    canonical = json.dumps(
        expected_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    if (
        payload != expected_payload
        or recognition["payload_json"] != canonical
        or recognition["case_id"] != header["case_id"]
        or recognition["id"] == source["id"]
        or recognition["source_activity_id"] != header["source_activity_id"]
        or type(source["sequence"]) is not int
        or type(recognition["sequence"]) is not int
        or cast(int, source["sequence"]) >= cast(int, recognition["sequence"])
        or recognition["confirmation_status"] != expected_confirmation
        or recognition["occurred_at"] != source["occurred_at"]
        or recognition["effective_at"] != source["effective_at"]
        or recognition["reviewer_id"] != source["reviewer_id"]
        or type(recognition["actor_id"]) is not str
        or not cast(str, recognition["actor_id"]).strip()
        or type(recognition["idempotency_key"]) is not str
        or not cast(str, recognition["idempotency_key"]).strip()
    ):
        _stored_state_invalid()

    prior_id = header["supersedes_obligation_id"]
    if prior_id is None:
        if recognition["supersedes_event_id"] is not None:
            _stored_state_invalid()
    else:
        prior_matches = tuple(
            (row, other_payload)
            for row, other_payload in decoded
            if other_payload.get("obligation_id") == prior_id
        )
        if len(prior_matches) != 1:
            _stored_state_invalid()
        prior_recognition, prior_payload = prior_matches[0]
        prior_obligation = prior_payload.get("obligation")
        if (
            prior_recognition["id"] != recognition["supersedes_event_id"]
            or prior_recognition["case_id"] != header["prior_case_id"]
            or prior_recognition["source_activity_id"] != header["prior_source_activity_id"]
            or type(prior_obligation) is not dict
            or cast(dict[str, object], prior_obligation).get("case_id") != header["prior_case_id"]
            or cast(dict[str, object], prior_obligation).get("source_activity_id")
            != header["prior_source_activity_id"]
            or cast(dict[str, object], prior_obligation).get("fee_domain")
            != header["prior_fee_domain"]
            or cast(dict[str, object], prior_obligation).get("obligation_type")
            != header["prior_obligation_type"]
            or cast(dict[str, object], prior_obligation).get("currency") != header["prior_currency"]
        ):
            _stored_state_invalid()

    if header["obligation_status"] == FeeObligationStatus.SUPERSEDED.value:
        children = tuple(
            (row, child_payload)
            for row, child_payload in decoded
            if child_payload.get("obligation_id") == header["current_child_id"]
        )
        if len(children) != 1:
            _stored_state_invalid()
        child_recognition, child_payload = children[0]
        child_obligation = child_payload.get("obligation")
        child_source_rows = tuple(
            row for row in rows if row["id"] == header["current_child_source_activity_id"]
        )
        child_source_status = _stored_enum(
            FeeSourceStatus,
            cast(str, header["current_child_source_status"]),
        )
        child_confirmation = (
            ConfirmationStatus.LEGACY_UNVERIFIED.value
            if child_source_status is FeeSourceStatus.LEGACY_UNVERIFIED
            else ConfirmationStatus.CONFIRMED.value
        )
        if (
            len(child_source_rows) != 1
            or type(child_obligation) is not dict
            or child_recognition["id"] == child_source_rows[0]["id"]
            or (
                child_source_rows[0]["lane"] == ActivityLane.FEE.value
                and child_source_rows[0]["activity_type"] == _ACTIVITY_TYPE
            )
            or child_recognition["source_activity_id"] != header["current_child_source_activity_id"]
            or child_recognition["supersedes_event_id"] != recognition["id"]
            or child_source_rows[0]["confirmation_status"] != child_confirmation
            or child_recognition["confirmation_status"] != child_confirmation
            or child_recognition["occurred_at"] != child_source_rows[0]["occurred_at"]
            or child_recognition["effective_at"] != child_source_rows[0]["effective_at"]
            or child_recognition["reviewer_id"] != child_source_rows[0]["reviewer_id"]
            or type(child_source_rows[0]["sequence"]) is not int
            or type(child_recognition["sequence"]) is not int
            or cast(int, child_source_rows[0]["sequence"])
            >= cast(int, child_recognition["sequence"])
            or cast(dict[str, object], child_obligation).get("case_id") != header["case_id"]
            or cast(dict[str, object], child_obligation).get("source_activity_id")
            != header["current_child_source_activity_id"]
            or cast(dict[str, object], child_obligation).get("fee_domain") != header["fee_domain"]
            or cast(dict[str, object], child_obligation).get("obligation_type")
            != header["obligation_type"]
            or cast(dict[str, object], child_obligation).get("currency") != header["currency"]
            or cast(dict[str, object], child_obligation).get("supersedes_obligation_id")
            != header["id"]
            or cast(dict[str, object], child_obligation).get("supersede_reason")
            != header["current_child_supersede_reason"]
        ):
            _stored_state_invalid()


def _detail_pay_list_status(
    header: Mapping[str, object],
    lines: tuple[Mapping[str, object], ...],
    rows: tuple[Mapping[str, object], ...],
) -> FeePayListStatus:
    if not rows:
        return FeePayListStatus.NOT_CREATED
    fee_domain = _stored_enum(FeeDomain, cast(str, header["fee_domain"]))
    line_by_id = {line["id"]: line for line in lines}
    payment_states: set[bool] = set()
    for row in rows:
        line = line_by_id.get(row["obligation_line_id"])
        if (
            line is None
            or row["item_id"] is None
            or row["draft_id"] is None
            or row["item_draft_id"] != row["draft_id"]
            or row["draft_case_id"] != header["case_id"]
            or row["draft_currency"] != header["currency"]
            or row["item_case_id"] != header["case_id"]
            or row["item_fee_type"] != fee_domain.value
            or row["item_fee_code"] != line["fee_code"]
            or row["item_year_no"] != line["fee_year_key"]
        ):
            _stored_state_invalid()
        payment_values = (
            row["payment_id"],
            row["pay_list_id"],
            row["payment_fee_item_id"],
            row["payment_pay_list_id"],
            row["payment_case_id"],
            row["payment_currency"],
            row["pay_list_currency"],
        )
        if fee_domain is FeeDomain.SERVICE:
            if any(value is not None for value in payment_values):
                _stored_state_invalid()
            continue
        if any(value is None for value in payment_values) and not all(
            value is None for value in payment_values
        ):
            _stored_state_invalid()
        has_payment = all(value is not None for value in payment_values)
        payment_states.add(has_payment)
        if has_payment and (
            row["payment_fee_item_id"] != row["item_id"]
            or row["payment_pay_list_id"] != row["pay_list_id"]
            or row["payment_case_id"] != header["case_id"]
            or row["payment_currency"] != header["currency"]
            or row["pay_list_currency"] != header["currency"]
        ):
            _stored_state_invalid()
    if fee_domain is FeeDomain.SERVICE:
        if (
            header["draft_status"] != FeeObligationDraftStatus.CREATED.value
            or header["payment_status"] != FeePaymentStatus.UNPAID.value
            or header["official_evidence_status"]
            != FeeOfficialEvidenceStatus.NOT_APPLICABLE.value
            or header["client_instruction_status"] != FeeClientInstructionStatus.PAY.value
        ):
            _stored_state_invalid()
        return FeePayListStatus.NOT_CREATED
    if len(payment_states) != 1:
        _stored_state_invalid()
    if False in payment_states:
        if (
            header["draft_status"] != FeeObligationDraftStatus.CREATED.value
            or header["payment_status"] != FeePaymentStatus.UNPAID.value
            or header["official_evidence_status"]
            != FeeOfficialEvidenceStatus.PENDING.value
            or header["client_instruction_status"]
            not in {
                FeeClientInstructionStatus.PENDING.value,
                FeeClientInstructionStatus.PAY.value,
            }
        ):
            _stored_state_invalid()
        return FeePayListStatus.NOT_CREATED
    return FeePayListStatus.CREATED


def record_client_instruction(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
) -> RecordFeeObligationInstructionResult:
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            "调用方事务包含未刷新的变更",
            status_code=409,
        )
    if type(command) is not RecordFeeObligationInstructionCommand:
        _instruction_command_invalid("command")
    _required_string(
        command.obligation_id,
        36,
        "obligation_id",
        _instruction_command_invalid,
    )
    if type(command.instruction) is not FeeClientInstruction:
        _instruction_command_invalid("instruction")
    _required_string(command.actor_id, 36, "actor_id", _instruction_command_invalid)
    _required_string(
        command.idempotency_key,
        128,
        "idempotency_key",
        _instruction_command_invalid,
    )

    with transaction.no_autoflush:
        header = transaction.get(FeeObligationModel, command.obligation_id)
        if header is None:
            _fail("FEE_OBLIGATION_NOT_FOUND", "费用义务不存在", status_code=404)
        case = _case_or_fail(transaction, header.case_id)
        existing = _activity_by_key(
            transaction,
            case_id=header.case_id,
            idempotency_key=command.idempotency_key,
        )
        if existing is not None:
            return _instruction_replay_existing(
                command,
                transaction,
                case,
                header,
                existing,
            )
        recognition = _instruction_recognition(transaction, header)
        previous, current_activity = _instruction_stored_chain(
            transaction,
            header,
            recognition,
        )
        reviewed_notice_draft = (
            command.instruction is FeeClientInstruction.PAY
            and header.draft_status == FeeObligationDraftStatus.CREATED.value
            and _has_reviewed_notice_draft_candidate(transaction, header)
        )
        if reviewed_notice_draft:
            _reviewed_notice_draft_for_instruction(transaction, header)
        else:
            _instruction_eligible(header)
        if previous.value == command.instruction.value:
            _instruction_same_state()

    occurred_at = datetime.now(UTC).replace(tzinfo=None)
    projection = _case_projection(case)
    activity_command = LifecycleEventCommand(
        case_id=header.case_id,
        event_type=_INSTRUCTION_ACTIVITY_TYPE,
        lane=ActivityLane.FEE,
        effective_at=occurred_at,
        occurred_at=occurred_at,
        evidence_refs=(),
        actor_id=command.actor_id,
        reviewer_id=None,
        idempotency_key=command.idempotency_key,
        source_activity_id=recognition.id,
        supersedes_event_id=(None if current_activity is None else current_activity.id),
        payload={
            "actor_id": command.actor_id,
            "instruction": command.instruction.value,
            "obligation_id": command.obligation_id,
            "previous_instruction_status": previous.value,
            "schema": _INSTRUCTION_PAYLOAD_SCHEMA,
        },
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            activity = append_case_activity(
                activity_command,
                transaction,
                previous_projection=projection,
                current_projection=projection,
                legacy_case_status=case.status,
                conflict_codes=(),
            )
            changed = transaction.execute(
                update(FeeObligationModel)
                .where(
                    FeeObligationModel.id == header.id,
                    FeeObligationModel.client_instruction_status == previous.value,
                    FeeObligationModel.obligation_status == FeeObligationStatus.RECOGNIZED.value,
                    FeeObligationModel.draft_status
                    == (
                        FeeObligationDraftStatus.CREATED.value
                        if reviewed_notice_draft
                        else FeeObligationDraftStatus.NOT_CREATED.value
                    ),
                    FeeObligationModel.payment_status == FeePaymentStatus.UNPAID.value,
                    FeeObligationModel.official_evidence_status
                    != FeeOfficialEvidenceStatus.VERIFIED.value,
                )
                .values(
                    client_instruction_status=command.instruction.value,
                    updated_by=command.actor_id,
                    updated_at=occurred_at,
                )
                .execution_options(synchronize_session=False)
            )
            if changed.rowcount != 1:
                raise _InstructionCasMiss
            transaction.flush()
    except _InstructionCasMiss:
        return _instruction_recover_cas(command, transaction)
    except BusinessError as exc:
        if exc.code != "LIFECYCLE_IDEMPOTENCY_CONFLICT":
            raise
        return _instruction_recover_activity_race(command, transaction)
    except IntegrityError as exc:
        if not _instruction_activity_unique_failure(exc):
            raise
        return _instruction_recover_activity_race(command, transaction)
    transaction.expire(header)
    return _instruction_result(
        transaction,
        header,
        activity_id=activity.activity_id,
        idempotency_key=command.idempotency_key,
        reused=False,
    )


def prepare_draft(
    command: PrepareFeeObligationDraftCommand,
    transaction: Session,
) -> PrepareFeeObligationDraftResult:
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            "调用方事务包含未刷新的变更",
            status_code=409,
        )
    _validate_prepare_draft_command(command)
    if command.authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION:
        _serialize_future_annuity_exception_draft(transaction)
    reviewed_notice = command.authority in {
        FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE,
        FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE,
        FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
    }

    with transaction.no_autoflush:
        header = transaction.get(FeeObligationModel, command.obligation_id)
        if header is None:
            _fail("FEE_OBLIGATION_NOT_FOUND", "费用义务不存在", status_code=404)
        case = _case_or_fail(transaction, header.case_id)
        existing = _activity_by_key(
            transaction,
            case_id=header.case_id,
            idempotency_key=command.idempotency_key,
        )
        if existing is not None:
            return _draft_replay_existing(command, transaction, header, existing)
        recognition = _instruction_recognition(transaction, header)
        instruction, instruction_activity = _instruction_stored_chain(
            transaction,
            header,
            recognition,
        )
        lines = _draft_lines_or_fail(
            transaction,
            header,
            allowed_review_states=(
                frozenset(
                    {
                        FeeDifferenceReviewState.MATCHED.value,
                        FeeDifferenceReviewState.REVIEW_REQUIRED.value,
                    }
                )
                if reviewed_notice
                and command.authority is not FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION
                else frozenset({FeeDifferenceReviewState.MATCHED.value})
            ),
        )
        if reviewed_notice:
            _reviewed_notice_draft_eligible(
                transaction,
                header,
                authority=command.authority,
                expected_actor_id=command.actor_id,
                expected_draft_idempotency_key=command.idempotency_key,
                recognition=recognition,
                instruction=instruction,
                instruction_activity=instruction_activity,
                lines=lines,
                command=command,
            )
        else:
            _draft_eligible(
                transaction,
                header,
                instruction=instruction,
                instruction_activity=instruction_activity,
                lines=lines,
            )

    occurred_at = datetime.now(UTC).replace(tzinfo=None)
    draft_id = str(uuid4())
    total = sum((cast(Decimal, line.payable_amount) for line in lines), Decimal("0.00"))
    is_gov = header.fee_domain == FeeDomain.GOV.value
    draft = FeeDraft(
        id=draft_id,
        case_id=header.case_id,
        client_id=case.client_id,
        draft_type="GENERIC",
        currency=header.currency,
        status="OPEN",
        total_gov=total if is_gov else Decimal("0.00"),
        total_service=Decimal("0.00") if is_gov else total,
        total_misc=Decimal("0.00"),
        amount=total,
        created_by=command.actor_id,
        updated_by=command.actor_id,
    )
    created: list[tuple[FeeObligationLineModel, FeeItem, FeeObligationDraftItemLink]] = []
    for line in lines:
        item = FeeItem(
            id=str(uuid4()),
            draft_id=draft_id,
            case_id=header.case_id,
            rate_id=None,
            fee_code=line.fee_code,
            fee_name=line.fee_name,
            fee_type=header.fee_domain,
            year_no=line.fee_year_key,
            amount=line.payable_amount,
            created_by=command.actor_id,
            updated_by=command.actor_id,
        )
        link = FeeObligationDraftItemLink(
            id=str(uuid4()),
            obligation_line_id=line.id,
            fee_item_id=item.id,
            created_by=command.actor_id,
            updated_by=command.actor_id,
        )
        created.append((line, item, link))

    payload = {
        "actor_id": command.actor_id,
        "center_changes": {},
        "draft_id": draft_id,
        "links": [
            {
                "fee_item_id": item.id,
                "obligation_line_id": line.id,
            }
            for line, item, _link in created
        ],
        "obligation_id": command.obligation_id,
        "schema": (
            _reviewed_notice_draft_schema(command.authority)
            if reviewed_notice
            else _DRAFT_PAYLOAD_SCHEMA
        ),
    }
    if reviewed_notice:
        payload["authority"] = command.authority.value
    if command.authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION:
        payload.update(
            {
                "exception_attested_at": cast(datetime, command.exception_attested_at).isoformat(
                    timespec="microseconds"
                ),
                "exception_gate_id": command.exception_gate_id,
                "exception_gate_source_reference": command.exception_gate_source_reference,
                "exception_gate_source_version": command.exception_gate_source_version,
                "exception_publication_id": command.exception_publication_id,
                "exception_publication_snapshot_hash": (
                    command.exception_publication_snapshot_hash
                ),
            }
        )
    projection = _case_projection(case)
    activity_command = LifecycleEventCommand(
        case_id=header.case_id,
        event_type=_DRAFT_ACTIVITY_TYPE,
        lane=ActivityLane.FEE,
        effective_at=occurred_at,
        occurred_at=occurred_at,
        evidence_refs=(),
        actor_id=command.actor_id,
        reviewer_id=None,
        idempotency_key=command.idempotency_key,
        source_activity_id=(
            recognition.id if reviewed_notice else cast(CaseActivityEvent, instruction_activity).id
        ),
        supersedes_event_id=None,
        payload=payload,
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            transaction.add(draft)
            transaction.add_all(
                [item for _line, item, _link in created] + [link for _line, _item, link in created]
            )
            transaction.flush()
            activity = append_case_activity(
                activity_command,
                transaction,
                previous_projection=projection,
                current_projection=projection,
                legacy_case_status=case.status,
                conflict_codes=(),
            )
            changed = transaction.execute(
                update(FeeObligationModel)
                .where(
                    FeeObligationModel.id == header.id,
                    FeeObligationModel.obligation_status == FeeObligationStatus.RECOGNIZED.value,
                    FeeObligationModel.source_status == FeeSourceStatus.VERIFIED.value,
                    FeeObligationModel.client_instruction_status
                    == (
                        FeeClientInstructionStatus.PENDING.value
                        if reviewed_notice
                        else FeeClientInstructionStatus.PAY.value
                    ),
                    FeeObligationModel.draft_status == FeeObligationDraftStatus.NOT_CREATED.value,
                    FeeObligationModel.payment_status == FeePaymentStatus.UNPAID.value,
                    FeeObligationModel.official_evidence_status
                    != FeeOfficialEvidenceStatus.VERIFIED.value,
                )
                .values(
                    draft_status=FeeObligationDraftStatus.CREATED.value,
                    updated_by=command.actor_id,
                    updated_at=occurred_at,
                )
                .execution_options(synchronize_session=False)
            )
            if changed.rowcount != 1:
                raise _DraftCasMiss
            transaction.flush()
    except _DraftCasMiss:
        return _draft_recover_race(command, transaction)
    except BusinessError as exc:
        if exc.code != "LIFECYCLE_IDEMPOTENCY_CONFLICT":
            raise
        return _draft_recover_race(command, transaction)
    except IntegrityError as exc:
        if not _draft_unique_failure(exc):
            raise
        return _draft_recover_race(command, transaction)

    transaction.expire(header)
    return PrepareFeeObligationDraftResult(
        obligation_id=header.id,
        draft_id=draft.id,
        links=tuple(
            FeeDraftItemLinkResult(
                id=link.id,
                obligation_line_id=line.id,
                fee_item_id=item.id,
                reused=False,
            )
            for line, item, link in created
        ),
        activity_id=activity.activity_id,
        activity_reused=False,
        idempotency_key=command.idempotency_key,
    )


def record_payment_evidence(
    command: RecordFeePaymentEvidenceCommand,
    transaction: Session,
) -> RecordFeePaymentEvidenceResult:
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            "调用方事务包含未刷新的变更",
            status_code=409,
        )
    _validate_payment_evidence_command(command)

    with transaction.no_autoflush:
        header = transaction.get(FeeObligationModel, command.obligation_id)
        if header is None:
            _fail("FEE_OBLIGATION_NOT_FOUND", "费用义务不存在", status_code=404)
        payment = transaction.get(GovPayment, command.gov_payment_id)
        if payment is None:
            _fail("FEE_PAYMENT_EVIDENCE_NOT_FOUND", "支付证据不存在", status_code=404)
        lines_by_id = {
            line.id: line
            for line in transaction.scalars(
                select(FeeObligationLineModel).where(
                    FeeObligationLineModel.id.in_(command.obligation_line_ids)
                )
            )
        }
        lines = tuple(lines_by_id.get(line_id) for line_id in command.obligation_line_ids)
        if any(line is None for line in lines):
            _fail("FEE_OBLIGATION_LINE_NOT_FOUND", "费用义务分项不存在", status_code=404)
        if any(line.obligation_id != header.id for line in lines if line is not None):
            _fail(
                "FEE_PAYMENT_EVIDENCE_OBLIGATION_MISMATCH",
                "支付证据分项不属于指定费用义务",
                status_code=409,
            )
        if payment.case_id != header.case_id or any(
            line.case_id != header.case_id for line in lines if line is not None
        ):
            _fail(
                "FEE_PAYMENT_EVIDENCE_CASE_MISMATCH",
                "支付证据与费用义务不属于同一案件",
                status_code=409,
            )
        existing_by_line_id = {
            link.obligation_line_id: link
            for link in transaction.scalars(
                select(FeeObligationPaymentEvidenceLink).where(
                    FeeObligationPaymentEvidenceLink.obligation_line_id.in_(
                        command.obligation_line_ids
                    ),
                    FeeObligationPaymentEvidenceLink.gov_payment_id == command.gov_payment_id,
                )
            )
        }

    occurred_at = datetime.now(UTC).replace(tzinfo=None)
    links: list[tuple[FeeObligationPaymentEvidenceLink, bool]] = []
    for line_id in command.obligation_line_ids:
        link = existing_by_line_id.get(line_id)
        reused = link is not None
        if link is None:
            link = FeeObligationPaymentEvidenceLink(
                obligation_line_id=line_id,
                gov_payment_id=command.gov_payment_id,
                created_by=command.actor_id,
                updated_by=command.actor_id,
            )
            transaction.add(link)
        links.append((link, reused))
    header.payment_status = FeePaymentStatus.PAID.value
    header.updated_by = command.actor_id
    header.updated_at = occurred_at
    transaction.flush()

    obligation = _result(
        transaction,
        header,
        activity_id="",
        idempotency_key="",
        reused=False,
        superseded_obligation_id=header.supersedes_obligation_id,
    ).obligation
    return RecordFeePaymentEvidenceResult(
        obligation=obligation,
        links=tuple(
            FeePaymentEvidenceLinkResult(
                id=link.id,
                obligation_line_id=link.obligation_line_id,
                gov_payment_id=link.gov_payment_id,
                reused=reused,
            )
            for link, reused in links
        ),
    )


def _validate_prepare_draft_command(command: PrepareFeeObligationDraftCommand) -> None:
    if type(command) is not PrepareFeeObligationDraftCommand:
        _draft_command_invalid("command")
    _required_string(
        command.obligation_id,
        36,
        "obligation_id",
        _draft_command_invalid,
    )
    _required_string(command.actor_id, 36, "actor_id", _draft_command_invalid)
    _required_string(
        command.idempotency_key,
        128,
        "idempotency_key",
        _draft_command_invalid,
    )
    if type(command.authority) is not FeeDraftAuthority:
        _draft_command_invalid("authority")
    exception_fields = (
        ("exception_gate_id", command.exception_gate_id),
        ("exception_gate_source_reference", command.exception_gate_source_reference),
        ("exception_gate_source_version", command.exception_gate_source_version),
        ("exception_publication_id", command.exception_publication_id),
        ("exception_publication_snapshot_hash", command.exception_publication_snapshot_hash),
        ("exception_attested_at", command.exception_attested_at),
    )
    if command.authority is not FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION:
        if any(value is not None for _field, value in exception_fields):
            _draft_command_invalid("authority")
        return
    for field in ("exception_gate_id", "exception_publication_id"):
        value = getattr(command, field)
        if type(value) is not str:
            _draft_command_invalid(field)
        try:
            parsed = UUID(value)
        except (TypeError, ValueError, AttributeError):
            _draft_command_invalid(field)
        if str(parsed) != value:
            _draft_command_invalid(field)
    _required_string(
        command.exception_gate_source_reference,
        512,
        "exception_gate_source_reference",
        _draft_command_invalid,
    )
    _required_string(
        command.exception_gate_source_version,
        128,
        "exception_gate_source_version",
        _draft_command_invalid,
    )
    if (
        type(command.exception_publication_snapshot_hash) is not str
        or re.fullmatch(r"[0-9a-f]{64}", command.exception_publication_snapshot_hash) is None
    ):
        _draft_command_invalid("exception_publication_snapshot_hash")
    if (
        type(command.exception_attested_at) is not datetime
        or command.exception_attested_at.utcoffset() is not None
    ):
        _draft_command_invalid("exception_attested_at")


def _reviewed_notice_draft_schema(authority: FeeDraftAuthority) -> str:
    if authority is FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE:
        return _REVIEWED_NOTICE_DRAFT_PAYLOAD_SCHEMA
    if authority is FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE:
        return _REVIEWED_GRANT_DRAFT_PAYLOAD_SCHEMA
    if authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION:
        return _FUTURE_ANNUITY_EXCEPTION_DRAFT_PAYLOAD_SCHEMA
    _draft_command_invalid("authority")


def _future_annuity_exception_record_or_fail(
    row: FutureAnnuityDraftExceptionRecord,
) -> None:
    def exact_text(value: object, limit: int) -> bool:
        return (
            type(value) is str
            and bool(value)
            and value == value.strip()
            and "\x00" not in value
            and len(value) <= limit
        )

    def canonical_uuid(value: object) -> bool:
        if type(value) is not str:
            return False
        try:
            return str(UUID(value)) == value
        except (TypeError, ValueError, AttributeError):
            return False

    if (
        not canonical_uuid(row.id)
        or not canonical_uuid(row.confirmed_by)
        or not exact_text(row.record_version, 128)
        or not exact_text(row.source_reference, 512)
        or not exact_text(row.source_version, 128)
        or not exact_text(row.reason, 4096)
        or not exact_text(row.idempotency_key, 128)
        or type(row.published_at) is not datetime
        or row.published_at.utcoffset() is not None
        or type(row.effective_at) is not datetime
        or row.effective_at.utcoffset() is not None
    ):
        _draft_stored_state_invalid()
    if row.record_type == "PUBLISHED":
        scope_id = row.client_id if row.scope_type == "CLIENT" else row.case_id
        if (
            row.scope_type not in {"CLIENT", "CASE"}
            or not canonical_uuid(scope_id)
            or (row.scope_type == "CLIENT" and row.case_id is not None)
            or (row.scope_type == "CASE" and row.client_id is not None)
            or row.target_publication_id is not None
            or type(row.effective_from) is not datetime
            or row.effective_from.utcoffset() is not None
            or type(row.effective_to) is not datetime
            or row.effective_to.utcoffset() is not None
            or row.effective_to <= row.effective_from
            or max(row.effective_from, row.published_at, row.effective_at) >= row.effective_to
        ):
            _draft_stored_state_invalid()
        payload = {
            "schema": "FPMS_FUTURE_ANNUITY_DRAFT_EXCEPTION_V1",
            "record_type": row.record_type,
            "scope_type": row.scope_type,
            "scope_id": scope_id,
            "effective_from": row.effective_from.isoformat(timespec="microseconds"),
            "effective_to": row.effective_to.isoformat(timespec="microseconds"),
            "effective_at": row.effective_at.isoformat(timespec="microseconds"),
            "record_version": row.record_version,
            "source_reference": row.source_reference,
            "source_version": row.source_version,
            "reason": row.reason,
            "confirmed_by": row.confirmed_by,
            "published_at": row.published_at.isoformat(timespec="microseconds"),
        }
    elif row.record_type == "REVOKED":
        if (
            not canonical_uuid(row.target_publication_id)
            or row.scope_type is not None
            or row.client_id is not None
            or row.case_id is not None
            or row.effective_from is not None
            or row.effective_to is not None
        ):
            _draft_stored_state_invalid()
        payload = {
            "schema": "FPMS_FUTURE_ANNUITY_DRAFT_EXCEPTION_V1",
            "record_type": row.record_type,
            "target_publication_id": row.target_publication_id,
            "effective_at": row.effective_at.isoformat(timespec="microseconds"),
            "record_version": row.record_version,
            "source_reference": row.source_reference,
            "source_version": row.source_version,
            "reason": row.reason,
            "confirmed_by": row.confirmed_by,
            "published_at": row.published_at.isoformat(timespec="microseconds"),
        }
    else:
        _draft_stored_state_invalid()
    snapshot = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    if (
        row.record_snapshot != snapshot
        or row.record_snapshot_hash != hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
    ):
        _draft_stored_state_invalid()


def _future_annuity_exception_attestation_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    command: PrepareFeeObligationDraftCommand,
    *,
    require_current: bool,
) -> FutureAnnuityExceptionUseAttestation:
    case = transaction.get(Case, header.case_id)
    publication = transaction.get(
        FutureAnnuityDraftExceptionRecord,
        command.exception_publication_id,
    )
    gate = transaction.get(CustomerDecisionGate, command.exception_gate_id)
    if case is None or publication is None or gate is None or case.client_id is None:
        _draft_stored_state_invalid()
    _future_annuity_exception_record_or_fail(publication)
    attested_at = cast(datetime, command.exception_attested_at)
    scope_id = publication.client_id if publication.scope_type == "CLIENT" else publication.case_id
    if (
        publication.record_type != "PUBLISHED"
        or publication.record_snapshot_hash != command.exception_publication_snapshot_hash
        or publication.effective_from is None
        or publication.effective_to is None
        or not publication.effective_from <= attested_at < publication.effective_to
        or publication.published_at > attested_at
        or publication.effective_at > attested_at
        or publication.scope_type not in {"CLIENT", "CASE"}
        or scope_id is None
        or (
            publication.scope_type == "CLIENT"
            and (publication.client_id != case.client_id or publication.case_id is not None)
        )
        or (
            publication.scope_type == "CASE"
            and (publication.case_id != case.id or publication.client_id is not None)
        )
    ):
        _draft_stored_state_invalid()
    revocations = tuple(
        transaction.scalars(
            select(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.target_publication_id == publication.id
            )
        )
    )
    if len(revocations) > 1:
        _draft_stored_state_invalid()
    for revocation in revocations:
        _future_annuity_exception_record_or_fail(revocation)
        if (
            revocation.source_reference != publication.source_reference
            or revocation.source_version != publication.source_version
        ):
            _draft_stored_state_invalid()
        if (
            require_current
            and revocation.published_at <= attested_at
            and revocation.effective_at <= attested_at
        ):
            _draft_stored_state_invalid()
    try:
        gate_snapshot = json.loads(gate.decision_snapshot)
        canonical_gate_snapshot = json.dumps(
            gate_snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _draft_stored_state_invalid()
    if (
        type(gate_snapshot) is not dict
        or set(gate_snapshot)
        != {
            "confirmed_by",
            "decision_status",
            "decision_value",
            "effective_at",
            "expected_current_gate_id",
            "gate_code",
            "scope_key",
            "source_reference",
            "source_version",
        }
        or canonical_gate_snapshot != gate.decision_snapshot
        or gate_snapshot.get("confirmed_by") != gate.confirmed_by
        or gate_snapshot.get("decision_status") != gate.decision_status
        or gate_snapshot.get("decision_value") != gate.decision_value
        or gate_snapshot.get("effective_at")
        != gate.effective_at.isoformat(timespec="microseconds")
        or gate_snapshot.get("gate_code") != gate.gate_code
        or gate_snapshot.get("scope_key") != gate.scope_key
        or gate_snapshot.get("source_reference") != gate.source_reference
        or gate_snapshot.get("source_version") != gate.source_version
        or gate.gate_code != "DG-FEE-FUTURE-ANNUITY"
        or gate.scope_key != "GLOBAL"
        or gate.decision_status != "CONFIRMED"
        or gate.decision_value != "APPROVED_POLICY"
        or gate.source_reference != command.exception_gate_source_reference
        or gate.source_version != command.exception_gate_source_version
        or gate.source_reference != _FUTURE_ANNUITY_GATE_SOURCE_REFERENCE
        or gate.source_version != _FUTURE_ANNUITY_GATE_SOURCE_VERSION
        or gate.effective_at > attested_at
    ):
        _draft_stored_state_invalid()
    attestation = FutureAnnuityExceptionUseAttestation(
        gate_id=gate.id,
        gate_source_reference=gate.source_reference,
        gate_source_version=gate.source_version,
        publication_id=publication.id,
        publication_snapshot_hash=publication.record_snapshot_hash,
        scope_type=FutureAnnuityExceptionScope(publication.scope_type),
        scope_id=scope_id,
        client_id=case.client_id,
        case_id=case.id,
        effective_from=publication.effective_from,
        effective_to=publication.effective_to,
        record_version=publication.record_version,
        source_reference=publication.source_reference,
        source_version=publication.source_version,
        confirmed_by=publication.confirmed_by,
        published_at=publication.published_at,
        effective_at=publication.effective_at,
        as_of=attested_at,
    )
    if require_current:
        current = resolve_future_annuity_exception(
            ResolveFutureAnnuityExceptionCommand(
                client_id=case.client_id,
                case_id=case.id,
                as_of=attested_at,
            ),
            transaction,
        )
        if current != attestation:
            _draft_stored_state_invalid()
    return attestation


def _future_annuity_exception_source_graph_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    *,
    command: PrepareFeeObligationDraftCommand,
    recognition: CaseActivityEvent,
    lines: tuple[FeeObligationLineModel, ...],
    allow_later_state: bool,
) -> None:
    instruction_states = {FeeClientInstructionStatus.PENDING.value}
    draft_states = {FeeObligationDraftStatus.NOT_CREATED.value}
    if allow_later_state:
        instruction_states.add(FeeClientInstructionStatus.PAY.value)
        draft_states.add(FeeObligationDraftStatus.CREATED.value)
    try:
        detail = get_fee_obligation(header.id, transaction)
    except BusinessError:
        _draft_stored_state_invalid()
    key_parts = command.idempotency_key.split(":")
    try:
        task_id = int(key_parts[1])
    except (IndexError, TypeError, ValueError):
        _draft_stored_state_invalid()
    case = transaction.get(Case, header.case_id)
    task = transaction.get(AnnuityTask, task_id)
    source_activity = transaction.get(CaseActivityEvent, header.source_activity_id)
    source_document = transaction.get(Document, header.source_document_id)
    source_evidence = (
        transaction.get(DocumentEvidenceVersion, task.source_evidence_version_id)
        if task is not None and task.source_evidence_version_id is not None
        else None
    )
    evidence_links = (
        tuple(
            transaction.scalars(
                select(CaseActivityEventEvidence).where(
                    CaseActivityEventEvidence.activity_id == header.source_activity_id
                )
            )
        )
        if source_activity is not None
        else ()
    )
    if (
        len(key_parts) != 3
        or key_parts[0] != "future-annuity-exception-auto-draft"
        or task_id <= 0
        or str(task_id) != key_parts[1]
        or key_parts[2] != command.exception_publication_id
        or case is None
        or case.client_id is None
        or task is None
        or task.id != task_id
        or task.case_id != header.case_id
        or task.client_id != case.client_id
        or task.fee_obligation_id != header.id
        or task.source_activity_id != header.source_activity_id
        or task.source_document_id != header.source_document_id
        or task.source_evidence_version_id is None
        or task.source_evidence_content_hash is None
        or re.fullmatch(r"sha256:[0-9a-f]{64}", task.source_evidence_content_hash)
        is None
        or task.grant_fee_year_key is None
        or task.grant_fee_year_key != task.year_no
        or task.due_date != header.due_date
        or source_activity is None
        or source_activity.case_id != header.case_id
        or source_activity.lane != ActivityLane.LIFECYCLE.value
        or source_activity.activity_type != "GRANT_ANNOUNCEMENT_CONFIRMED"
        or source_activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or source_document is None
        or source_document.case_id != header.case_id
        or source_evidence is None
        or source_evidence.case_id != header.case_id
        or source_evidence.document_id != header.source_document_id
        or source_evidence.role != "OFFICIAL_FINAL_PDF"
        or source_evidence.state != "FINAL"
        or source_evidence.review_state != "APPROVED"
        or source_evidence.content_hash != task.source_evidence_content_hash
        or source_evidence.current_identity_key
        != f"{header.case_id}|{source_evidence.lineage_key}"
        or len(evidence_links) != 1
        or evidence_links[0].case_id != header.case_id
        or evidence_links[0].evidence_kind != "DOCUMENT_EVIDENCE_VERSION"
        or evidence_links[0].object_type != "DocumentEvidenceVersion"
        or evidence_links[0].object_id != source_evidence.id
        or evidence_links[0].content_hash != task.source_evidence_content_hash
        or header.fee_domain != FeeDomain.GOV.value
        or header.obligation_type != "FUTURE_ANNUITY"
        or header.source_status != FeeSourceStatus.VERIFIED.value
        or header.obligation_status != FeeObligationStatus.RECOGNIZED.value
        or header.client_instruction_status not in instruction_states
        or header.draft_status not in draft_states
        or header.payment_status != FeePaymentStatus.UNPAID.value
        or header.official_evidence_status != FeeOfficialEvidenceStatus.PENDING.value
        or header.currency != "CNY"
        or len(lines) != 1
        or lines[0].difference_review_state != FeeDifferenceReviewState.MATCHED.value
        or lines[0].fee_year_key != task.grant_fee_year_key
        or lines[0].source_date != task.due_date
        or lines[0].fee_code != _FUTURE_ANNUITY_FEE_CODE.get(case.patent_category)
        or detail.id != header.id
        or detail.case_id != header.case_id
        or detail.source.source_activity_id != header.source_activity_id
        or detail.source.source_document_id != header.source_document_id
        or tuple(line.id for line in detail.lines) != tuple(line.id for line in lines)
        or recognition.case_id != header.case_id
        or recognition.lane != ActivityLane.FEE.value
        or recognition.activity_type != _ACTIVITY_TYPE
        or recognition.source_activity_id != header.source_activity_id
        or recognition.confirmation_status != ConfirmationStatus.CONFIRMED.value
    ):
        _draft_stored_state_invalid()
    _future_annuity_exception_attestation_or_fail(
        transaction,
        header,
        command,
        require_current=not allow_later_state,
    )


def _draft_lines_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    *,
    require_current: bool = True,
    allowed_review_states: frozenset[str] = frozenset({FeeDifferenceReviewState.MATCHED.value}),
) -> tuple[FeeObligationLineModel, ...]:
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLineModel)
            .where(FeeObligationLineModel.obligation_id == header.id)
            .order_by(
                FeeObligationLineModel.fee_code,
                FeeObligationLineModel.fee_year_key,
                FeeObligationLineModel.id,
            )
        )
    )
    identities: set[tuple[str, int]] = set()
    if not lines:
        _draft_stored_state_invalid()
    for line in lines:
        identity = (line.fee_code, line.fee_year_key)
        if (
            line.case_id != header.case_id
            or line.source_activity_id != header.source_activity_id
            or type(line.fee_code) is not str
            or not line.fee_code
            or line.fee_code.strip() != line.fee_code
            or type(line.fee_name) is not str
            or not line.fee_name
            or line.fee_name.strip() != line.fee_name
            or type(line.fee_year_key) is not int
            or line.fee_year_key < 0
            or not _valid_amount(line.payable_amount, optional=False)
            or line.difference_review_state not in allowed_review_states
            or identity in identities
            or (
                require_current
                and line.current_identity_key
                != _identity_key(
                    line.case_id,
                    line.source_activity_id,
                    line.fee_code,
                    line.fee_year_key,
                )
            )
        ):
            _draft_stored_state_invalid()
        identities.add(identity)
    return lines


def _draft_eligible(
    transaction: Session,
    header: FeeObligationModel,
    *,
    instruction: FeeClientInstructionStatus,
    instruction_activity: CaseActivityEvent | None,
    lines: tuple[FeeObligationLineModel, ...],
) -> None:
    try:
        fee_domain = FeeDomain(header.fee_domain)
        source_status = FeeSourceStatus(header.source_status)
        obligation_status = FeeObligationStatus(header.obligation_status)
        instruction_status = FeeClientInstructionStatus(header.client_instruction_status)
        draft_status = FeeObligationDraftStatus(header.draft_status)
        payment_status = FeePaymentStatus(header.payment_status)
        official_status = FeeOfficialEvidenceStatus(header.official_evidence_status)
    except ValueError:
        _draft_stored_state_invalid()
    if (
        type(header.currency) is not str
        or re.fullmatch(r"[A-Z]{3}", header.currency, flags=re.ASCII) is None
        or instruction_status is not instruction
        or (
            fee_domain is FeeDomain.GOV and official_status is not FeeOfficialEvidenceStatus.PENDING
        )
        or (
            fee_domain is FeeDomain.SERVICE
            and official_status is not FeeOfficialEvidenceStatus.NOT_APPLICABLE
        )
    ):
        _draft_stored_state_invalid()
    if (
        source_status is not FeeSourceStatus.VERIFIED
        or obligation_status is not FeeObligationStatus.RECOGNIZED
        or instruction is not FeeClientInstructionStatus.PAY
        or instruction_activity is None
        or draft_status is not FeeObligationDraftStatus.NOT_CREATED
        or payment_status is not FeePaymentStatus.UNPAID
        or official_status is FeeOfficialEvidenceStatus.VERIFIED
    ):
        _draft_not_actionable(header)
    child_count = transaction.scalar(
        select(func.count())
        .select_from(FeeObligationModel)
        .where(FeeObligationModel.supersedes_obligation_id == header.id)
    )
    relation_count = transaction.scalar(
        select(func.count())
        .select_from(FeeObligationDraftItemLink)
        .where(FeeObligationDraftItemLink.obligation_line_id.in_(tuple(line.id for line in lines)))
    )
    activity_count = transaction.scalar(
        select(func.count())
        .select_from(CaseActivityEvent)
        .where(
            CaseActivityEvent.case_id == header.case_id,
            CaseActivityEvent.activity_type == _DRAFT_ACTIVITY_TYPE,
            CaseActivityEvent.source_activity_id == instruction_activity.id,
        )
    )
    if child_count or relation_count or activity_count:
        _draft_stored_state_invalid()


def _reviewed_notice_draft_eligible(
    transaction: Session,
    header: FeeObligationModel,
    *,
    authority: FeeDraftAuthority,
    expected_actor_id: str,
    expected_draft_idempotency_key: str,
    recognition: CaseActivityEvent,
    instruction: FeeClientInstructionStatus,
    instruction_activity: CaseActivityEvent | None,
    lines: tuple[FeeObligationLineModel, ...],
    command: PrepareFeeObligationDraftCommand | None = None,
) -> None:
    _reviewed_notice_source_graph_or_fail(
        transaction,
        header,
        authority=authority,
        expected_actor_id=expected_actor_id,
        expected_draft_idempotency_key=expected_draft_idempotency_key,
        recognition=recognition,
        lines=lines,
        allow_later_state=False,
        command=command,
    )
    if instruction is not FeeClientInstructionStatus.PENDING or instruction_activity is not None:
        _draft_not_actionable(header)
    child_count = transaction.scalar(
        select(func.count())
        .select_from(FeeObligationModel)
        .where(FeeObligationModel.supersedes_obligation_id == header.id)
    )
    relation_count = transaction.scalar(
        select(func.count())
        .select_from(FeeObligationDraftItemLink)
        .where(FeeObligationDraftItemLink.obligation_line_id.in_(tuple(line.id for line in lines)))
    )
    if child_count or relation_count or _reviewed_notice_draft_activities(transaction, header):
        _draft_stored_state_invalid()


def _reviewed_notice_source_graph_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    *,
    authority: FeeDraftAuthority,
    expected_actor_id: str,
    expected_draft_idempotency_key: str,
    recognition: CaseActivityEvent,
    lines: tuple[FeeObligationLineModel, ...],
    allow_later_state: bool,
    command: PrepareFeeObligationDraftCommand | None = None,
) -> None:
    if authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION:
        if command is None:
            _draft_command_invalid("authority")
        _future_annuity_exception_source_graph_or_fail(
            transaction,
            header,
            command=command,
            recognition=recognition,
            lines=lines,
            allow_later_state=allow_later_state,
        )
        return
    if authority is FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE:
        _reviewed_grant_year_source_graph_or_fail(
            transaction,
            header,
            expected_actor_id=expected_actor_id,
            expected_draft_idempotency_key=expected_draft_idempotency_key,
            recognition=recognition,
            lines=lines,
            allow_later_state=allow_later_state,
        )
        return
    if authority is not FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE:
        _draft_command_invalid("authority")
    try:
        obligation_status = FeeObligationStatus(header.obligation_status)
        instruction_status = FeeClientInstructionStatus(header.client_instruction_status)
        draft_status = FeeObligationDraftStatus(header.draft_status)
        payment_status = FeePaymentStatus(header.payment_status)
        official_status = FeeOfficialEvidenceStatus(header.official_evidence_status)
    except ValueError:
        _draft_stored_state_invalid()
    if (
        not _reviewed_notice_exact_text(expected_actor_id, 36)
        or not _reviewed_notice_exact_text(header.id, 36)
        or not _reviewed_notice_exact_text(header.case_id, 36)
        or not _reviewed_notice_exact_text(header.source_activity_id, 36)
        or not _reviewed_notice_exact_text(header.source_document_id, 36)
        or header.fee_domain != FeeDomain.GOV.value
        or header.obligation_type != "APPLICATION_FEE"
        or header.source_status != FeeSourceStatus.VERIFIED.value
        or obligation_status is not FeeObligationStatus.RECOGNIZED
        or type(header.currency) is not str
        or re.fullmatch(r"[A-Z]{3}", header.currency, flags=re.ASCII) is None
        or any(
            line.difference_review_state
            not in {
                FeeDifferenceReviewState.MATCHED.value,
                FeeDifferenceReviewState.REVIEW_REQUIRED.value,
            }
            for line in lines
        )
        or any(
            not _reviewed_notice_exact_text(line.id, 36)
            or line.obligation_id != header.id
            or not _valid_amount(line.official_full_amount, optional=False)
            or not _valid_ratio(line.reduction_ratio)
            or not _valid_amount(line.source_amount, optional=False)
            or line.source_amount != line.payable_amount
            or type(line.source_date) is not date
            for line in lines
        )
    ):
        _draft_stored_state_invalid()
    if not allow_later_state and (
        instruction_status is not FeeClientInstructionStatus.PENDING
        or draft_status is not FeeObligationDraftStatus.NOT_CREATED
        or payment_status is not FeePaymentStatus.UNPAID
        or official_status is not FeeOfficialEvidenceStatus.PENDING
    ):
        _draft_not_actionable(header)
    if allow_later_state and draft_status is not FeeObligationDraftStatus.CREATED:
        _draft_stored_state_invalid()

    try:
        recognition_payload = _strict_json_loads(recognition.payload_json)
    except (TypeError, ValueError):
        _draft_stored_state_invalid()
    obligation_payload = (
        recognition_payload.get("obligation") if type(recognition_payload) is dict else None
    )
    expected_payload_lines = [
        {
            "difference_review_state": line.difference_review_state,
            "fee_code": line.fee_code,
            "fee_name": line.fee_name,
            "fee_year_key": line.fee_year_key,
            "official_full_amount": _amount_text(line.official_full_amount),
            "payable_amount": _amount_text(line.payable_amount),
            "reduction_ratio": format(line.reduction_ratio, ".4f"),
            "source_amount": _amount_text(line.source_amount),
            "source_date": None if line.source_date is None else line.source_date.isoformat(),
        }
        for line in lines
    ]
    if (
        type(recognition_payload) is not dict
        or set(recognition_payload) != {"obligation", "obligation_id", "schema"}
        or recognition_payload.get("schema") != _PAYLOAD_SCHEMA
        or recognition_payload.get("obligation_id") != header.id
        or type(obligation_payload) is not dict
        or set(obligation_payload)
        != {
            "actor_id",
            "case_id",
            "currency",
            "due_date",
            "fee_domain",
            "lines",
            "obligation_type",
            "source_activity_id",
            "source_document_id",
            "source_status",
            "supersede_reason",
            "supersedes_obligation_id",
        }
        or obligation_payload.get("case_id") != header.case_id
        or obligation_payload.get("actor_id") != expected_actor_id
        or obligation_payload.get("currency") != header.currency
        or obligation_payload.get("due_date")
        != (None if header.due_date is None else header.due_date.isoformat())
        or obligation_payload.get("source_activity_id") != header.source_activity_id
        or obligation_payload.get("source_document_id") != header.source_document_id
        or obligation_payload.get("fee_domain") != FeeDomain.GOV.value
        or obligation_payload.get("obligation_type") != "APPLICATION_FEE"
        or obligation_payload.get("source_status") != FeeSourceStatus.VERIFIED.value
        or obligation_payload.get("supersede_reason") is not None
        or obligation_payload.get("supersedes_obligation_id") is not None
        or obligation_payload.get("lines") != expected_payload_lines
        or recognition.case_id != header.case_id
        or not _reviewed_notice_exact_text(recognition.id, 36)
        or not _reviewed_notice_exact_text(recognition.actor_id, 36)
        or not _reviewed_notice_exact_text(recognition.reviewer_id, 36)
        or not _reviewed_notice_exact_text(recognition.idempotency_key, 128)
        or recognition.actor_id != expected_actor_id
        or recognition.lane != ActivityLane.FEE.value
        or recognition.activity_type != _ACTIVITY_TYPE
        or recognition.source_activity_id != header.source_activity_id
        or recognition.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or recognition.supersedes_event_id is not None
        or not _reviewed_notice_naive_datetime(recognition.occurred_at)
        or not _reviewed_notice_naive_datetime(recognition.effective_at)
        or recognition.occurred_at != recognition.effective_at
        or recognition.old_business_stage != recognition.new_business_stage
        or recognition.old_official_procedure_stage != recognition.new_official_procedure_stage
        or recognition.old_legal_status != recognition.new_legal_status
        or recognition.payload_json
        != json.dumps(
            recognition_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    ):
        _draft_stored_state_invalid()

    review = transaction.get(CaseActivityEvent, header.source_activity_id)
    document = transaction.get(Document, header.source_document_id)
    if review is None or document is None:
        _draft_stored_state_invalid()
    try:
        review_payload = _strict_json_loads(review.payload_json)
    except (TypeError, ValueError):
        _draft_stored_state_invalid()
    if (
        type(review_payload) is not dict
        or set(review_payload)
        != {
            "creator_id",
            "decision",
            "evidence_version_id",
            "previous_review_state",
            "review_state",
            "reviewer_id",
        }
        or review_payload.get("decision") != "APPROVE"
        or review_payload.get("previous_review_state") != "PENDING"
        or review_payload.get("review_state") != "APPROVED"
        or not _reviewed_notice_exact_text(review_payload.get("creator_id"), 36)
        or not _reviewed_notice_exact_text(review_payload.get("evidence_version_id"), 36)
        or not _reviewed_notice_exact_text(review_payload.get("reviewer_id"), 36)
        or review_payload.get("reviewer_id") != review.reviewer_id
        or review_payload.get("reviewer_id") != expected_actor_id
        or not _reviewed_notice_exact_text(review.id, 36)
        or not _reviewed_notice_exact_text(review.actor_id, 36)
        or not _reviewed_notice_exact_text(review.reviewer_id, 36)
        or not _reviewed_notice_exact_text(review.idempotency_key, 128)
        or review.id != header.source_activity_id
        or review.case_id != header.case_id
        or review.lane != ActivityLane.DOCUMENT.value
        or review.activity_type != "DOCUMENT_EVIDENCE_REVIEW_DECIDED"
        or review.source_activity_id is not None
        or review.supersedes_event_id is not None
        or review.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or review.actor_id != review.reviewer_id
        or review.actor_id != expected_actor_id
        or recognition.reviewer_id != review.reviewer_id
        or recognition.occurred_at != review.occurred_at
        or recognition.effective_at != review.effective_at
        or not _reviewed_notice_naive_datetime(review.occurred_at)
        or not _reviewed_notice_naive_datetime(review.effective_at)
        or review.occurred_at != review.effective_at
        or review.old_business_stage != review.new_business_stage
        or review.old_official_procedure_stage != review.new_official_procedure_stage
        or review.old_legal_status != review.new_legal_status
        or type(review.sequence) is not int
        or type(recognition.sequence) is not int
        or recognition.sequence <= review.sequence
        or review.payload_json
        != json.dumps(
            review_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        or not _reviewed_notice_exact_text(document.id, 36)
        or document.case_id != header.case_id
        or document.direction != "IN"
    ):
        _draft_stored_state_invalid()

    evidence_id = review_payload.get("evidence_version_id")
    evidence = (
        transaction.get(DocumentEvidenceVersion, evidence_id) if type(evidence_id) is str else None
    )
    if (
        evidence is None
        or not _reviewed_notice_exact_text(evidence.id, 36)
        or not _reviewed_notice_exact_text(evidence.case_id, 36)
        or not _reviewed_notice_exact_text(evidence.document_id, 36)
        or not _reviewed_notice_exact_text(evidence.attachment_id, 36)
        or not _reviewed_notice_exact_text(evidence.lineage_key, 128)
        or not _reviewed_notice_exact_text(evidence.creator_id, 36)
        or not _reviewed_notice_exact_text(evidence.reviewer_id, 36)
        or type(evidence.version_number) is not int
        or evidence.version_number <= 0
        or evidence.case_id != header.case_id
        or evidence.document_id != header.source_document_id
        or evidence.role != "OFFICIAL_FINAL_PDF"
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or review_payload.get("evidence_version_id") != evidence.id
        or review_payload.get("creator_id") != evidence.creator_id
        or evidence.reviewer_id != review.reviewer_id
        or evidence.creator_id != review_payload.get("creator_id")
        or evidence.creator_id == evidence.reviewer_id
        or evidence.reviewer_id != expected_actor_id
        or not _reviewed_notice_naive_datetime(evidence.reviewed_at)
        or evidence.reviewed_at != review.effective_at
        or evidence.current_identity_key != f"{header.case_id}|{evidence.lineage_key}"
        or type(evidence.content_hash) is not str
        or re.fullmatch(r"sha256:[0-9a-f]{64}", evidence.content_hash) is None
        or not expected_draft_idempotency_key.startswith(
            f"application-fee-auto-draft:{evidence.id}:"
        )
        or not _reviewed_notice_exact_text(
            expected_draft_idempotency_key.removeprefix(
                f"application-fee-auto-draft:{evidence.id}:"
            ),
            64,
        )
        or recognition.idempotency_key
        != expected_draft_idempotency_key.replace(
            "application-fee-auto-draft:",
            "application-fee-notice:",
            1,
        )
    ):
        _draft_stored_state_invalid()

    review_refs = _activity_evidence_signatures(transaction, review.id)
    recognition_refs = _activity_evidence_signatures(transaction, recognition.id)
    expected_ref = (
        header.case_id,
        "DOCUMENT_EVIDENCE_VERSION",
        "DocumentEvidenceVersion",
        evidence.id,
        evidence.content_hash,
        review.effective_at,
    )
    if review_refs != (expected_ref,) or recognition_refs != (expected_ref,):
        _draft_stored_state_invalid()


def _reviewed_grant_year_source_graph_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    *,
    expected_actor_id: str,
    expected_draft_idempotency_key: str,
    recognition: CaseActivityEvent,
    lines: tuple[FeeObligationLineModel, ...],
    allow_later_state: bool,
) -> None:
    try:
        obligation_status = FeeObligationStatus(header.obligation_status)
        instruction_status = FeeClientInstructionStatus(header.client_instruction_status)
        draft_status = FeeObligationDraftStatus(header.draft_status)
        payment_status = FeePaymentStatus(header.payment_status)
        official_status = FeeOfficialEvidenceStatus(header.official_evidence_status)
        detail = get_fee_obligation(header.id, transaction)
    except (BusinessError, ValueError):
        _draft_stored_state_invalid()
    if (
        not _reviewed_notice_exact_text(expected_actor_id, 36)
        or header.fee_domain != FeeDomain.GOV.value
        or header.obligation_type != "GRANT_YEAR_ANNUITY"
        or header.source_status != FeeSourceStatus.VERIFIED.value
        or obligation_status is not FeeObligationStatus.RECOGNIZED
        or payment_status is not FeePaymentStatus.UNPAID
        or official_status is not FeeOfficialEvidenceStatus.PENDING
        or detail.id != header.id
        or detail.case_id != header.case_id
        or detail.source.source_activity_id != header.source_activity_id
        or detail.source.source_document_id != header.source_document_id
        or detail.statuses.obligation_status is not FeeObligationStatus.RECOGNIZED
        or tuple(line.id for line in detail.lines) != tuple(line.id for line in lines)
        or any(
            line.difference_review_state != FeeDifferenceReviewState.MATCHED.value
            or not _valid_amount(line.official_full_amount, optional=False)
            for line in lines
        )
        or recognition.case_id != header.case_id
        or recognition.activity_type != _ACTIVITY_TYPE
        or recognition.lane != ActivityLane.FEE.value
        or recognition.source_activity_id != header.source_activity_id
        or recognition.confirmation_status != ConfirmationStatus.CONFIRMED.value
    ):
        _draft_stored_state_invalid()
    if not allow_later_state and (
        instruction_status is not FeeClientInstructionStatus.PENDING
        or draft_status is not FeeObligationDraftStatus.NOT_CREATED
    ):
        _draft_not_actionable(header)
    if allow_later_state and (
        draft_status is not FeeObligationDraftStatus.CREATED
        or instruction_status
        not in {FeeClientInstructionStatus.PENDING, FeeClientInstructionStatus.PAY}
    ):
        _draft_stored_state_invalid()

    reviews: list[tuple[CaseActivityEvent, dict[str, object]]] = []
    for activity in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == header.case_id,
            CaseActivityEvent.activity_type == _GRANT_REVIEW_ACTIVITY_TYPE,
        )
    ):
        try:
            payload = _strict_json_loads(activity.payload_json)
        except (TypeError, ValueError):
            _draft_stored_state_invalid()
        if type(payload) is not dict:
            _draft_stored_state_invalid()
        if payload.get("obligation_id") == header.id:
            reviews.append((activity, payload))
    if len(reviews) != 1:
        _draft_stored_state_invalid()
    review, review_payload = reviews[0]
    grant_fee_task_id = review_payload.get("grant_fee_task_id")
    task = (
        transaction.get(T_GrantFeeTask, grant_fee_task_id)
        if type(grant_fee_task_id) is str
        else None
    )
    if (
        not _reviewed_notice_exact_text(grant_fee_task_id, 36)
        or task is None
        or task.type != "GRANT"
        or task.case_id != header.case_id
        or task.source_document_id != header.source_document_id
        or task.due_date != header.due_date
        or review_payload.get("schema") != _GRANT_REVIEW_PAYLOAD_SCHEMA
        or review_payload.get("source_activity_id") != header.source_activity_id
        or review_payload.get("source_document_id") != header.source_document_id
        or review.source_activity_id != header.source_activity_id
        or review.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or review.actor_id != review.reviewer_id
        or expected_draft_idempotency_key
        != f"grant-year-auto-draft:{grant_fee_task_id}:{header.source_activity_id}"
    ):
        _draft_stored_state_invalid()


def _reviewed_notice_exact_text(value: object, limit: int) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _reviewed_notice_naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.tzinfo is None


def _activity_evidence_signatures(
    transaction: Session,
    activity_id: str,
) -> tuple[tuple[object, ...], ...]:
    rows = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity_id
            )
        )
    )
    return tuple(
        (
            row.case_id,
            row.evidence_kind,
            row.object_type,
            row.object_id,
            row.content_hash,
            row.captured_at,
        )
        for row in rows
    )


def _reviewed_notice_draft_activities(
    transaction: Session,
    header: FeeObligationModel,
) -> tuple[CaseActivityEvent, ...]:
    matches: list[CaseActivityEvent] = []
    for activity in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == header.case_id,
            CaseActivityEvent.lane == ActivityLane.FEE.value,
            CaseActivityEvent.activity_type == _DRAFT_ACTIVITY_TYPE,
        )
    ):
        try:
            payload = _strict_json_loads(activity.payload_json)
        except (TypeError, ValueError):
            _draft_stored_state_invalid()
        if type(payload) is not dict:
            _draft_stored_state_invalid()
        if payload.get("obligation_id") == header.id:
            matches.append(activity)
    return tuple(matches)


def _has_reviewed_notice_draft_candidate(
    transaction: Session,
    header: FeeObligationModel,
) -> bool:
    for activity in _reviewed_notice_draft_activities(transaction, header):
        try:
            payload = _strict_json_loads(activity.payload_json)
        except (TypeError, ValueError):
            continue
        if type(payload) is dict and payload.get("schema") in {
            _REVIEWED_NOTICE_DRAFT_PAYLOAD_SCHEMA,
            _REVIEWED_GRANT_DRAFT_PAYLOAD_SCHEMA,
            _FUTURE_ANNUITY_EXCEPTION_DRAFT_PAYLOAD_SCHEMA,
        }:
            return True
    return False


def _draft_replay_existing(
    command: PrepareFeeObligationDraftCommand,
    transaction: Session,
    header: FeeObligationModel,
    activity: CaseActivityEvent,
) -> PrepareFeeObligationDraftResult:
    reviewed_notice = command.authority in {
        FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE,
        FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE,
        FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
    }
    recognition = _instruction_recognition(transaction, header)
    instruction, instruction_activity = _instruction_stored_chain(
        transaction,
        header,
        recognition,
    )
    lines = _draft_lines_or_fail(
        transaction,
        header,
        require_current=reviewed_notice,
        allowed_review_states=(
            frozenset(
                {
                    FeeDifferenceReviewState.MATCHED.value,
                    FeeDifferenceReviewState.REVIEW_REQUIRED.value,
                }
            )
            if reviewed_notice
            and command.authority is not FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION
            else frozenset({FeeDifferenceReviewState.MATCHED.value})
        ),
    )
    if reviewed_notice:
        _reviewed_notice_source_graph_or_fail(
            transaction,
            header,
            authority=command.authority,
            expected_actor_id=command.actor_id,
            expected_draft_idempotency_key=command.idempotency_key,
            recognition=recognition,
            lines=lines,
            allow_later_state=True,
            command=command,
        )
    try:
        payload = _strict_json_loads(activity.payload_json)
    except (TypeError, ValueError):
        _draft_idempotency_conflict()
    if (
        type(payload) is not dict
        or set(payload)
        != (
            {
                "actor_id",
                "authority",
                "center_changes",
                "draft_id",
                "exception_attested_at",
                "exception_gate_id",
                "exception_gate_source_reference",
                "exception_gate_source_version",
                "exception_publication_id",
                "exception_publication_snapshot_hash",
                "links",
                "obligation_id",
                "schema",
            }
            if command.authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION
            else
            {
                "actor_id",
                "authority",
                "center_changes",
                "draft_id",
                "links",
                "obligation_id",
                "schema",
            }
            if reviewed_notice
            else {
                "actor_id",
                "center_changes",
                "draft_id",
                "links",
                "obligation_id",
                "schema",
            }
        )
        or payload.get("schema")
        != (
            _reviewed_notice_draft_schema(command.authority)
            if reviewed_notice
            else _DRAFT_PAYLOAD_SCHEMA
        )
        or (reviewed_notice and payload.get("authority") != command.authority.value)
        or (
            command.authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION
            and (
                payload.get("exception_gate_id") != command.exception_gate_id
                or payload.get("exception_gate_source_reference")
                != command.exception_gate_source_reference
                or payload.get("exception_gate_source_version")
                != command.exception_gate_source_version
                or payload.get("exception_publication_id") != command.exception_publication_id
                or payload.get("exception_publication_snapshot_hash")
                != command.exception_publication_snapshot_hash
                or payload.get("exception_attested_at")
                != cast(datetime, command.exception_attested_at).isoformat(
                    timespec="microseconds"
                )
            )
        )
        or payload.get("obligation_id") != command.obligation_id
        or payload.get("actor_id") != command.actor_id
        or payload.get("center_changes") != {}
        or type(payload.get("draft_id")) is not str
        or type(payload.get("links")) is not list
        or activity.payload_json
        != json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    ):
        _draft_idempotency_conflict()
    if (
        (not reviewed_notice and instruction is not FeeClientInstructionStatus.PAY)
        or (not reviewed_notice and instruction_activity is None)
        or activity.case_id != header.case_id
        or activity.lane != ActivityLane.FEE.value
        or activity.activity_type != _DRAFT_ACTIVITY_TYPE
        or activity.source_activity_id
        != (recognition.id if reviewed_notice else cast(CaseActivityEvent, instruction_activity).id)
        or activity.occurred_at != activity.effective_at
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.actor_id != command.actor_id
        or activity.reviewer_id is not None
        or activity.supersedes_event_id is not None
        or activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
        or transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == activity.id)
        )
        != 0
    ):
        _draft_idempotency_conflict()
    links, draft = _draft_relations_or_fail(
        transaction,
        header,
        lines=lines,
        draft_id=cast(str, payload["draft_id"]),
    )
    expected_links = [
        {
            "fee_item_id": item.id,
            "obligation_line_id": line.id,
        }
        for line, item, _link in links
    ]
    if payload["links"] != expected_links:
        _draft_idempotency_conflict()
    return PrepareFeeObligationDraftResult(
        obligation_id=header.id,
        draft_id=draft.id,
        links=tuple(
            FeeDraftItemLinkResult(
                id=link.id,
                obligation_line_id=line.id,
                fee_item_id=item.id,
                reused=True,
            )
            for line, item, link in links
        ),
        activity_id=activity.id,
        activity_reused=True,
        idempotency_key=command.idempotency_key,
    )


def _reviewed_notice_draft_for_instruction(
    transaction: Session,
    header: FeeObligationModel,
) -> PrepareFeeObligationDraftResult:
    activities = _reviewed_notice_draft_activities(transaction, header)
    if len(activities) != 1:
        _instruction_stored_state_invalid()
    activity = activities[0]
    try:
        payload = _strict_json_loads(activity.payload_json)
        authority = FeeDraftAuthority(payload.get("authority")) if type(payload) is dict else None
    except (TypeError, ValueError):
        _instruction_stored_state_invalid()
    if authority not in {
        FeeDraftAuthority.REVIEWED_APPLICATION_FEE_NOTICE,
        FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE,
        FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
    }:
        _instruction_stored_state_invalid()
    try:
        return _draft_replay_existing(
            PrepareFeeObligationDraftCommand(
                obligation_id=header.id,
                actor_id=activity.actor_id,
                idempotency_key=activity.idempotency_key,
                authority=authority,
                exception_gate_id=payload.get("exception_gate_id"),
                exception_gate_source_reference=payload.get(
                    "exception_gate_source_reference"
                ),
                exception_gate_source_version=payload.get("exception_gate_source_version"),
                exception_publication_id=payload.get("exception_publication_id"),
                exception_publication_snapshot_hash=payload.get(
                    "exception_publication_snapshot_hash"
                ),
                exception_attested_at=(
                    datetime.fromisoformat(payload["exception_attested_at"])
                    if authority is FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION
                    and type(payload.get("exception_attested_at")) is str
                    else None
                ),
            ),
            transaction,
            header,
            activity,
        )
    except (BusinessError, ValueError):
        _instruction_stored_state_invalid()


def _draft_relations_or_fail(
    transaction: Session,
    header: FeeObligationModel,
    *,
    lines: tuple[FeeObligationLineModel, ...],
    draft_id: str,
) -> tuple[
    tuple[tuple[FeeObligationLineModel, FeeItem, FeeObligationDraftItemLink], ...],
    FeeDraft,
]:
    draft = transaction.get(FeeDraft, draft_id)
    total = sum((cast(Decimal, line.payable_amount) for line in lines), Decimal("0.00"))
    is_gov = header.fee_domain == FeeDomain.GOV.value
    if (
        draft is None
        or header.draft_status != FeeObligationDraftStatus.CREATED.value
        or draft.case_id != header.case_id
        or draft.currency != header.currency
        or draft.status != "OPEN"
        or draft.total_gov != (total if is_gov else Decimal("0.00"))
        or draft.total_service != (Decimal("0.00") if is_gov else total)
        or draft.total_misc != Decimal("0.00")
        or draft.amount != total
    ):
        _draft_stored_state_invalid()
    stored_links = tuple(
        transaction.scalars(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.obligation_line_id.in_(tuple(line.id for line in lines))
            )
        )
    )
    by_line: dict[str, FeeObligationDraftItemLink] = {}
    for link in stored_links:
        if link.obligation_line_id in by_line:
            _draft_stored_state_invalid()
        by_line[link.obligation_line_id] = link
    if set(by_line) != {line.id for line in lines}:
        _draft_stored_state_invalid()
    resolved: list[tuple[FeeObligationLineModel, FeeItem, FeeObligationDraftItemLink]] = []
    for line in lines:
        link = by_line[line.id]
        item = transaction.get(FeeItem, link.fee_item_id)
        if (
            item is None
            or item.draft_id != draft.id
            or item.case_id != header.case_id
            or item.fee_code != line.fee_code
            or item.fee_name != line.fee_name
            or item.fee_type != header.fee_domain
            or item.year_no != line.fee_year_key
            or item.amount != line.payable_amount
        ):
            _draft_stored_state_invalid()
        resolved.append((line, item, link))
    return tuple(resolved), draft


def _draft_recover_race(
    command: PrepareFeeObligationDraftCommand,
    transaction: Session,
) -> PrepareFeeObligationDraftResult:
    transaction.expire_all()
    header = transaction.get(FeeObligationModel, command.obligation_id)
    if header is None:
        _draft_concurrency_conflict()
    activity = _activity_by_key(
        transaction,
        case_id=header.case_id,
        idempotency_key=command.idempotency_key,
    )
    if activity is not None:
        return _draft_replay_existing(command, transaction, header, activity)
    _draft_concurrency_conflict()


def _draft_unique_failure(exc: IntegrityError) -> bool:
    message = str(exc.orig).lower()
    return (
        "t_case_activity_event.case_id, t_case_activity_event.idempotency_key" in message
        or "uq_t_case_activity_event_case_idempotency_key" in message
        or (
            "t_fee_obligation_draft_item_link.obligation_line_id" in message
            and "t_fee_obligation_draft_item_link.fee_item_id" in message
        )
        or "uq_t_fee_obligation_draft_item_link_pair" in message
    )


def _draft_command_invalid(field: str) -> None:
    _fail(
        "FEE_OBLIGATION_DRAFT_COMMAND_INVALID",
        "费用义务请款草稿命令无效",
        details={"field": field},
        status_code=400,
    )


def _draft_not_actionable(header: FeeObligationModel) -> None:
    _fail(
        "FEE_OBLIGATION_DRAFT_NOT_ACTIONABLE",
        "当前费用义务不可生成请款草稿",
        details={
            "obligation_id": header.id,
            "source_status": header.source_status,
            "obligation_status": header.obligation_status,
            "client_instruction_status": header.client_instruction_status,
            "draft_status": header.draft_status,
            "payment_status": header.payment_status,
            "official_evidence_status": header.official_evidence_status,
        },
        status_code=409,
    )


def _draft_stored_state_invalid() -> None:
    _fail(
        "FEE_OBLIGATION_DRAFT_STORED_STATE_INVALID",
        "费用义务请款草稿存量状态无效",
        status_code=409,
    )


def _draft_idempotency_conflict() -> None:
    _fail(
        "FEE_OBLIGATION_DRAFT_IDEMPOTENCY_CONFLICT",
        "幂等键已用于不同的费用义务请款草稿事实",
        status_code=409,
    )


class _DraftCasMiss(Exception):
    pass


def _draft_concurrency_conflict() -> None:
    _fail(
        "FEE_OBLIGATION_DRAFT_CONCURRENCY_CONFLICT",
        "并发费用义务请款草稿尚不可见，请重试完整事务",
        status_code=409,
    )


def _validate_payment_evidence_command(command: RecordFeePaymentEvidenceCommand) -> None:
    if type(command) is not RecordFeePaymentEvidenceCommand:
        _payment_evidence_command_invalid("command")
    _required_string(
        command.obligation_id,
        36,
        "obligation_id",
        _payment_evidence_command_invalid,
    )
    if (
        type(command.obligation_line_ids) is not tuple
        or not command.obligation_line_ids
        or len(set(command.obligation_line_ids)) != len(command.obligation_line_ids)
    ):
        _payment_evidence_command_invalid("obligation_line_ids")
    for index, line_id in enumerate(command.obligation_line_ids):
        _required_string(
            line_id,
            36,
            f"obligation_line_ids[{index}]",
            _payment_evidence_command_invalid,
        )
    if (
        type(command.gov_payment_id) is not int
        or type(command.gov_payment_id) is bool
        or command.gov_payment_id <= 0
    ):
        _payment_evidence_command_invalid("gov_payment_id")
    _required_string(command.actor_id, 36, "actor_id", _payment_evidence_command_invalid)


def _payment_evidence_command_invalid(field: str) -> None:
    _fail(
        "FEE_PAYMENT_EVIDENCE_COMMAND_INVALID",
        "支付证据命令无效",
        details={"field": field},
        status_code=400,
    )


def _instruction_recognition(
    transaction: Session,
    header: FeeObligationModel,
) -> CaseActivityEvent:
    rows = tuple(
        transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == header.case_id,
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == _ACTIVITY_TYPE,
            )
        )
    )
    matches: list[CaseActivityEvent] = []
    for activity in rows:
        try:
            payload = _strict_json_loads(activity.payload_json)
        except (TypeError, ValueError):
            _instruction_recognition_invalid()
        if type(payload) is not dict or payload.get("schema") != _PAYLOAD_SCHEMA:
            _instruction_recognition_invalid()
        if payload.get("obligation_id") == header.id:
            matches.append(activity)
    if len(matches) != 1:
        _instruction_recognition_invalid()
    return matches[0]


def _instruction_stored_chain(
    transaction: Session,
    header: FeeObligationModel,
    recognition: CaseActivityEvent,
) -> tuple[FeeClientInstructionStatus, CaseActivityEvent | None]:
    try:
        current = FeeClientInstructionStatus(header.client_instruction_status)
    except ValueError:
        _instruction_stored_state_invalid()
    rows = tuple(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(
                CaseActivityEvent.case_id == header.case_id,
                CaseActivityEvent.lane == ActivityLane.FEE.value,
                CaseActivityEvent.activity_type == _INSTRUCTION_ACTIVITY_TYPE,
            )
            .order_by(CaseActivityEvent.sequence)
        )
    )
    chain: list[tuple[CaseActivityEvent, dict[str, object]]] = []
    for activity in rows:
        payload = _instruction_payload_or_fail(activity)
        if payload["obligation_id"] == header.id:
            _instruction_activity_shape_or_fail(
                transaction,
                activity,
                payload,
                recognition_id=recognition.id,
            )
            chain.append((activity, payload))
    previous_activity: CaseActivityEvent | None = None
    previous_instruction = FeeClientInstructionStatus.PENDING
    for activity, payload in chain:
        if (
            payload["previous_instruction_status"] != previous_instruction.value
            or activity.supersedes_event_id
            != (None if previous_activity is None else previous_activity.id)
            or payload["instruction"] == previous_instruction.value
        ):
            _instruction_stored_state_invalid()
        previous_activity = activity
        previous_instruction = FeeClientInstructionStatus(cast(str, payload["instruction"]))
    if current is FeeClientInstructionStatus.PENDING:
        if chain:
            _instruction_stored_state_invalid()
        return current, None
    if not chain or previous_instruction is not current:
        _instruction_stored_state_invalid()
    return current, previous_activity


def _instruction_payload_or_fail(activity: CaseActivityEvent) -> dict[str, object]:
    try:
        payload = _strict_json_loads(activity.payload_json)
    except (TypeError, ValueError):
        _instruction_stored_state_invalid()
    if (
        type(payload) is not dict
        or set(payload)
        != {
            "actor_id",
            "instruction",
            "obligation_id",
            "previous_instruction_status",
            "schema",
        }
        or payload.get("schema") != _INSTRUCTION_PAYLOAD_SCHEMA
        or payload.get("instruction") not in {item.value for item in FeeClientInstruction}
        or payload.get("previous_instruction_status")
        not in {item.value for item in FeeClientInstructionStatus}
        or type(payload.get("actor_id")) is not str
        or type(payload.get("obligation_id")) is not str
        or activity.payload_json
        != json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    ):
        _instruction_stored_state_invalid()
    return payload


def _instruction_activity_shape_or_fail(
    transaction: Session,
    activity: CaseActivityEvent,
    payload: dict[str, object],
    *,
    recognition_id: str,
) -> None:
    evidence_count = transaction.scalar(
        select(func.count())
        .select_from(CaseActivityEventEvidence)
        .where(CaseActivityEventEvidence.activity_id == activity.id)
    )
    if (
        activity.source_activity_id != recognition_id
        or activity.actor_id != payload["actor_id"]
        or activity.reviewer_id is not None
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or evidence_count != 0
    ):
        _instruction_stored_state_invalid()


def _instruction_replay_existing(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
    case: Case,
    header: FeeObligationModel,
    activity: CaseActivityEvent,
) -> RecordFeeObligationInstructionResult:
    recognition = _instruction_replay_recognition_source(transaction, header)
    payload = _instruction_payload_or_idempotency_conflict(activity)
    if (
        payload.get("obligation_id") != command.obligation_id
        or payload.get("instruction") != command.instruction.value
        or payload.get("actor_id") != command.actor_id
    ):
        _instruction_idempotency_conflict()
    _instruction_replay_activity_shape(
        transaction,
        activity,
        header,
        payload,
        recognition_id=recognition.id,
    )
    previous = cast(str, payload["previous_instruction_status"])
    if previous == FeeClientInstructionStatus.PENDING.value:
        if (
            activity.supersedes_event_id is not None
            or _instruction_latest_prior_fact(
                transaction,
                activity,
                obligation_id=command.obligation_id,
            )
            is not None
        ):
            _instruction_idempotency_conflict()
    else:
        _instruction_replay_prior_fact(
            transaction,
            activity,
            header,
            expected_instruction=previous,
            recognition_id=recognition.id,
        )
    try:
        projection = _activity_projection(activity)
    except BusinessError:
        _instruction_idempotency_conflict()
    replay_command = LifecycleEventCommand(
        case_id=header.case_id,
        event_type=_INSTRUCTION_ACTIVITY_TYPE,
        lane=ActivityLane.FEE,
        effective_at=activity.effective_at,
        occurred_at=activity.occurred_at,
        evidence_refs=(),
        actor_id=command.actor_id,
        reviewer_id=None,
        idempotency_key=command.idempotency_key,
        source_activity_id=activity.source_activity_id,
        supersedes_event_id=activity.supersedes_event_id,
        payload=payload,
        confirmation_status=ConfirmationStatus.CONFIRMED,
    )
    try:
        replay = append_case_activity(
            replay_command,
            transaction,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=case.status,
            conflict_codes=(),
        )
    except BusinessError as exc:
        if exc.code == "LIFECYCLE_IDEMPOTENCY_CONFLICT":
            _instruction_idempotency_conflict()
        raise
    if not replay.reused or replay.activity_id != activity.id:
        _instruction_stored_state_invalid()
    return _instruction_result(
        transaction,
        header,
        activity_id=activity.id,
        idempotency_key=command.idempotency_key,
        reused=True,
    )


def _instruction_replay_activity_shape(
    transaction: Session,
    activity: CaseActivityEvent,
    header: FeeObligationModel,
    payload: dict[str, object],
    *,
    recognition_id: str,
) -> None:
    evidence_count = transaction.scalar(
        select(func.count())
        .select_from(CaseActivityEventEvidence)
        .where(CaseActivityEventEvidence.activity_id == activity.id)
    )
    if (
        activity.case_id != header.case_id
        or activity.activity_type != _INSTRUCTION_ACTIVITY_TYPE
        or activity.lane != ActivityLane.FEE.value
        or activity.source_activity_id != recognition_id
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.actor_id != payload.get("actor_id")
        or activity.reviewer_id is not None
        or activity.occurred_at is None
        or activity.effective_at != activity.occurred_at
        or activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
        or evidence_count != 0
    ):
        _instruction_idempotency_conflict()


def _instruction_replay_prior_fact(
    transaction: Session,
    activity: CaseActivityEvent,
    header: FeeObligationModel,
    *,
    expected_instruction: str,
    recognition_id: str,
) -> None:
    prior = transaction.get(CaseActivityEvent, activity.supersedes_event_id)
    if prior is None:
        _instruction_idempotency_conflict()
    prior_payload = _instruction_payload_or_idempotency_conflict(prior)
    if (
        prior_payload.get("obligation_id") != header.id
        or prior_payload.get("instruction") != expected_instruction
        or prior.sequence >= activity.sequence
    ):
        _instruction_idempotency_conflict()
    latest = _instruction_latest_prior_fact(
        transaction,
        activity,
        obligation_id=header.id,
    )
    if latest is None or latest.id != prior.id:
        _instruction_idempotency_conflict()
    _instruction_replay_activity_shape(
        transaction,
        prior,
        header,
        prior_payload,
        recognition_id=recognition_id,
    )
    prior_previous = cast(str, prior_payload["previous_instruction_status"])
    if prior_previous == FeeClientInstructionStatus.PENDING.value:
        if (
            prior.supersedes_event_id is not None
            or _instruction_latest_prior_fact(
                transaction,
                prior,
                obligation_id=header.id,
            )
            is not None
        ):
            _instruction_idempotency_conflict()
        return
    _instruction_replay_prior_fact(
        transaction,
        prior,
        header,
        expected_instruction=prior_previous,
        recognition_id=recognition_id,
    )


def _instruction_latest_prior_fact(
    transaction: Session,
    activity: CaseActivityEvent,
    *,
    obligation_id: str,
) -> CaseActivityEvent | None:
    candidates = transaction.scalars(
        select(CaseActivityEvent)
        .where(
            CaseActivityEvent.case_id == activity.case_id,
            CaseActivityEvent.sequence < activity.sequence,
        )
        .order_by(CaseActivityEvent.sequence.desc())
    )
    for candidate in candidates:
        try:
            payload = _strict_json_loads(candidate.payload_json)
        except (TypeError, ValueError):
            if candidate.activity_type == _INSTRUCTION_ACTIVITY_TYPE:
                _instruction_idempotency_conflict()
            continue
        if (
            type(payload) is dict
            and payload.get("schema") == _INSTRUCTION_PAYLOAD_SCHEMA
            and payload.get("obligation_id") == obligation_id
        ):
            return candidate
    return None


def _instruction_replay_recognition_source(
    transaction: Session,
    header: FeeObligationModel,
) -> CaseActivityEvent:
    try:
        return _instruction_recognition(transaction, header)
    except BusinessError as exc:
        if exc.code == "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID":
            _instruction_idempotency_conflict()
        raise


def _instruction_payload_or_idempotency_conflict(
    activity: CaseActivityEvent,
) -> dict[str, object]:
    try:
        payload = _strict_json_loads(activity.payload_json)
    except (TypeError, ValueError):
        _instruction_idempotency_conflict()
    if (
        type(payload) is not dict
        or set(payload)
        != {
            "actor_id",
            "instruction",
            "obligation_id",
            "previous_instruction_status",
            "schema",
        }
        or payload.get("schema") != _INSTRUCTION_PAYLOAD_SCHEMA
        or payload.get("instruction") not in {item.value for item in FeeClientInstruction}
        or payload.get("previous_instruction_status")
        not in {item.value for item in FeeClientInstructionStatus}
        or activity.payload_json
        != json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    ):
        _instruction_idempotency_conflict()
    return payload


def _instruction_eligible(header: FeeObligationModel) -> None:
    values = (
        header.obligation_status,
        header.draft_status,
        header.payment_status,
        header.official_evidence_status,
    )
    try:
        obligation_status = FeeObligationStatus(values[0])
        draft_status = FeeObligationDraftStatus(values[1])
        payment_status = FeePaymentStatus(values[2])
        official_status = FeeOfficialEvidenceStatus(values[3])
    except ValueError:
        _instruction_stored_state_invalid()
    if (
        obligation_status is not FeeObligationStatus.RECOGNIZED
        or draft_status is not FeeObligationDraftStatus.NOT_CREATED
        or payment_status is not FeePaymentStatus.UNPAID
        or official_status is FeeOfficialEvidenceStatus.VERIFIED
    ):
        _fail(
            "FEE_CLIENT_INSTRUCTION_LOCKED",
            "当前费用义务已锁定，不能修改客户指示",
            details={
                "obligation_id": header.id,
                "obligation_status": header.obligation_status,
                "draft_status": header.draft_status,
                "payment_status": header.payment_status,
                "official_evidence_status": header.official_evidence_status,
            },
            status_code=409,
        )


def _instruction_result(
    transaction: Session,
    header: FeeObligationModel,
    *,
    activity_id: str,
    idempotency_key: str,
    reused: bool,
) -> RecordFeeObligationInstructionResult:
    try:
        obligation = _result(
            transaction,
            header,
            activity_id=activity_id,
            idempotency_key=idempotency_key,
            reused=reused,
            superseded_obligation_id=header.supersedes_obligation_id,
        ).obligation
    except BusinessError as exc:
        if exc.code == "FEE_OBLIGATION_STORED_STATE_INVALID":
            _instruction_stored_state_invalid()
        raise
    return RecordFeeObligationInstructionResult(
        obligation=obligation,
        activity_id=activity_id,
        idempotency_key=idempotency_key,
        reused=reused,
    )


def _instruction_command_invalid(field: str) -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_COMMAND_INVALID",
        "客户费用指示命令无效",
        details={"field": field},
        status_code=400,
    )


def _instruction_recognition_invalid() -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID",
        "费用义务识别活动无效",
        status_code=409,
    )


def _instruction_stored_state_invalid() -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_STORED_STATE_INVALID",
        "客户费用指示存量状态无效",
        status_code=409,
    )


def _instruction_same_state() -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_SAME_STATE",
        "客户费用指示已处于目标状态",
        status_code=409,
    )


def _instruction_idempotency_conflict() -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
        "幂等键已用于不同的客户费用指示事实",
        status_code=409,
    )


class _InstructionCasMiss(Exception):
    pass


def _instruction_activity_unique_failure(exc: IntegrityError) -> bool:
    message = str(exc.orig).lower()
    return (
        "t_case_activity_event.case_id, t_case_activity_event.idempotency_key" in message
        or "uq_t_case_activity_event_case_idempotency_key" in message
    )


def _instruction_recover_activity_race(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
) -> RecordFeeObligationInstructionResult:
    with transaction.no_autoflush:
        header = transaction.get(FeeObligationModel, command.obligation_id)
        if header is None:
            _fail("FEE_OBLIGATION_NOT_FOUND", "费用义务不存在", status_code=404)
        case = _case_or_fail(transaction, header.case_id)
        activity = _activity_by_key(
            transaction,
            case_id=header.case_id,
            idempotency_key=command.idempotency_key,
        )
        if activity is not None:
            return _instruction_replay_existing(
                command,
                transaction,
                case,
                header,
                activity,
            )
    _instruction_concurrency_conflict()


def _instruction_recover_cas(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
) -> RecordFeeObligationInstructionResult:
    transaction.expire_all()
    header = transaction.get(FeeObligationModel, command.obligation_id)
    if header is None:
        _instruction_concurrency_conflict()
    if (
        command.instruction is FeeClientInstruction.PAY
        and header.draft_status == FeeObligationDraftStatus.CREATED.value
        and _has_reviewed_notice_draft_candidate(transaction, header)
    ):
        _reviewed_notice_draft_for_instruction(transaction, header)
    else:
        _instruction_eligible(header)
    try:
        current = FeeClientInstructionStatus(header.client_instruction_status)
    except ValueError:
        _instruction_stored_state_invalid()
    if current.value == command.instruction.value:
        _instruction_same_state()
    _instruction_concurrency_conflict()


def _instruction_concurrency_conflict() -> None:
    _fail(
        "FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT",
        "并发客户费用指示尚不可见，请重试完整事务",
        status_code=409,
    )


class _Prior:
    def __init__(
        self,
        header: FeeObligationModel,
        lines: tuple[FeeObligationLineModel, ...],
        activity_id: str,
    ) -> None:
        self.header = header
        self.lines = lines
        self.activity_id = activity_id


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if not driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def _ensure_service_receivable_write_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if not driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN IMMEDIATE")


def _serialize_future_annuity_exception_draft(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    try:
        if not driver_connection.in_transaction:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        else:
            connection.exec_driver_sql(
                "UPDATE t_future_annuity_draft_exception_record SET id = id WHERE 0"
            )
    except OperationalError:
        _draft_stored_state_invalid()


def _validate_command(
    command: RecognizeFeeObligationCommand,
) -> tuple[FeeObligationLineInput, ...]:
    if type(command) is not RecognizeFeeObligationCommand:
        _invalid_command("command")
    _required_string(command.case_id, 36, "case_id", _invalid_command)
    _required_string(
        command.source_activity_id,
        36,
        "source_activity_id",
        _invalid_command,
    )
    _optional_string(
        command.source_document_id,
        36,
        "source_document_id",
        _invalid_command,
    )
    _required_string(command.actor_id, 36, "actor_id", _invalid_command)
    _required_string(
        command.obligation_type,
        64,
        "obligation_type",
        _invalid_command,
    )
    _required_string(
        command.idempotency_key,
        128,
        "idempotency_key",
        _invalid_command,
    )
    if type(command.fee_domain) is not FeeDomain:
        _invalid_command("fee_domain")
    if type(command.source_status) is not FeeSourceStatus:
        _invalid_command("source_status")
    if not _valid_date(command.due_date, optional=True):
        _invalid_line_field("due_date")
    if (
        type(command.currency) is not str
        or re.fullmatch(r"[A-Z]{3}", command.currency, flags=re.ASCII) is None
    ):
        _fail(
            "FEE_OBLIGATION_CURRENCY_INVALID",
            "币种代码无效",
            details={"field": "currency"},
            status_code=400,
        )
    if type(command.lines) is not tuple or not command.lines:
        _invalid_command("lines")

    validated: list[FeeObligationLineInput] = []
    identities: set[tuple[str, int]] = set()
    for index, line in enumerate(command.lines):
        if type(line) is not FeeObligationLineInput:
            _invalid_line(index, "line")
        _required_string(
            line.fee_code,
            64,
            f"lines[{index}].fee_code",
            _invalid_line_field,
        )
        _required_string(
            line.fee_name,
            256,
            f"lines[{index}].fee_name",
            _invalid_line_field,
        )
        if type(line.fee_year_key) is not int or not 0 <= line.fee_year_key <= 2147483647:
            _invalid_line(index, "fee_year_key")
        if not _valid_amount(line.official_full_amount, optional=True):
            _invalid_line(index, "official_full_amount")
        if not _valid_ratio(line.reduction_ratio):
            _invalid_line(index, "reduction_ratio")
        if not _valid_amount(line.payable_amount, optional=False):
            _invalid_line(index, "payable_amount")
        if not _valid_amount(line.source_amount, optional=True):
            _invalid_line(index, "source_amount")
        if not _valid_date(line.source_date, optional=True):
            _invalid_line(index, "source_date")
        if type(line.difference_review_state) is not FeeDifferenceReviewState:
            _invalid_line(index, "difference_review_state")
        identity = (line.fee_code, line.fee_year_key)
        if identity in identities:
            _fail(
                "FEE_OBLIGATION_LINE_DUPLICATE",
                "费用明细身份重复",
                details={"field": f"lines[{index}]"},
                status_code=400,
            )
        identities.add(identity)
        validated.append(line)

    has_supersedes = command.supersedes_obligation_id is not None
    has_reason = command.supersede_reason is not None
    if has_supersedes != has_reason:
        _supersede_pair_invalid()
    if has_supersedes:
        if (
            type(command.supersedes_obligation_id) is not str
            or not command.supersedes_obligation_id.strip()
            or len(command.supersedes_obligation_id) > 36
            or type(command.supersede_reason) is not str
            or not command.supersede_reason.strip()
        ):
            _supersede_pair_invalid()
    if command.fee_domain is FeeDomain.GOV and command.source_document_id is None:
        _fail(
            "FEE_OBLIGATION_GOV_SOURCE_DOCUMENT_REQUIRED",
            "官费义务必须引用来源文件",
            status_code=409,
        )
    return tuple(sorted(validated, key=lambda item: (item.fee_code, item.fee_year_key)))


def _valid_amount(value: object, *, optional: bool) -> bool:
    if value is None:
        return optional
    return (
        type(value) is Decimal
        and value.is_finite()
        and Decimal(0) <= value <= _MAX_AMOUNT
        and _fractional_digits(value) <= 2
    )


def _valid_ratio(value: object) -> bool:
    return (
        type(value) is Decimal
        and value.is_finite()
        and Decimal(0) <= value <= Decimal(1)
        and _fractional_digits(value) <= 4
    )


def _fractional_digits(value: Decimal) -> int:
    return max(-value.as_tuple().exponent, 0)


def _valid_date(value: object, *, optional: bool) -> bool:
    return (value is None and optional) or (type(value) is date)


def _case_or_fail(transaction: Session, case_id: str) -> Case:
    case = transaction.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    if case is None:
        _fail("CASE_NOT_FOUND", "案件不存在", status_code=404)
    return case


def _activity_by_key(
    transaction: Session,
    *,
    case_id: str,
    idempotency_key: str,
) -> CaseActivityEvent | None:
    return transaction.execute(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.idempotency_key == idempotency_key,
        )
    ).scalar_one_or_none()


def _source_activity_or_fail(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
) -> CaseActivityEvent:
    source = transaction.execute(
        select(CaseActivityEvent).where(CaseActivityEvent.id == command.source_activity_id)
    ).scalar_one_or_none()
    if source is None:
        _fail(
            "FEE_OBLIGATION_SOURCE_ACTIVITY_NOT_FOUND",
            "费用义务来源活动不存在",
            status_code=409,
        )
    if source.case_id != command.case_id:
        _fail(
            "FEE_OBLIGATION_SOURCE_ACTIVITY_CASE_MISMATCH",
            "费用义务来源活动不属于当前案件",
            status_code=409,
        )
    return source


def _validate_source_confirmation(
    command: RecognizeFeeObligationCommand,
    source: CaseActivityEvent,
) -> None:
    expected = (
        ConfirmationStatus.LEGACY_UNVERIFIED.value
        if command.source_status is FeeSourceStatus.LEGACY_UNVERIFIED
        else ConfirmationStatus.CONFIRMED.value
    )
    if source.confirmation_status != expected:
        _fail(
            "FEE_OBLIGATION_SOURCE_NOT_CONFIRMED",
            "费用义务来源活动未达到所需确认状态",
            status_code=409,
        )


def _validate_document(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
) -> None:
    if command.source_document_id is None:
        return
    document = transaction.execute(
        select(Document).where(Document.id == command.source_document_id)
    ).scalar_one_or_none()
    if document is None:
        _fail(
            "FEE_OBLIGATION_SOURCE_DOCUMENT_NOT_FOUND",
            "费用义务来源文件不存在",
            status_code=409,
        )
    if document.case_id != command.case_id:
        _fail(
            "FEE_OBLIGATION_SOURCE_DOCUMENT_CASE_MISMATCH",
            "费用义务来源文件不属于当前案件",
            status_code=409,
        )


def _validate_supersede(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    lines: tuple[FeeObligationLineInput, ...],
) -> _Prior | None:
    del lines
    prior_id = command.supersedes_obligation_id
    if prior_id is None:
        return None
    header = transaction.execute(
        select(FeeObligationModel).where(FeeObligationModel.id == prior_id)
    ).scalar_one_or_none()
    if header is None:
        _fail(
            "FEE_OBLIGATION_SUPERSEDED_NOT_FOUND",
            "被替代费用义务不存在",
            status_code=409,
        )
    if header.case_id != command.case_id:
        _fail(
            "FEE_OBLIGATION_SUPERSEDED_CASE_MISMATCH",
            "被替代费用义务不属于当前案件",
            status_code=409,
        )
    prior_lines = tuple(
        transaction.execute(
            select(FeeObligationLineModel)
            .where(FeeObligationLineModel.obligation_id == header.id)
            .order_by(FeeObligationLineModel.fee_code, FeeObligationLineModel.fee_year_key)
        ).scalars()
    )
    child = (
        transaction.execute(
            select(FeeObligationModel.id).where(
                FeeObligationModel.supersedes_obligation_id == header.id
            )
        )
        .scalars()
        .first()
    )
    if (
        header.obligation_status != FeeObligationStatus.RECOGNIZED.value
        or not prior_lines
        or child is not None
        or any(
            line.current_identity_key
            != _identity_key(
                line.case_id,
                line.source_activity_id,
                line.fee_code,
                line.fee_year_key,
            )
            for line in prior_lines
        )
    ):
        _fail(
            "FEE_OBLIGATION_SUPERSEDED_NOT_CURRENT",
            "被替代费用义务不是当前有效义务",
            status_code=409,
        )
    if (
        header.fee_domain != command.fee_domain.value
        or header.obligation_type != command.obligation_type
        or header.currency != command.currency
        or header.source_activity_id == command.source_activity_id
    ):
        _fail(
            "FEE_OBLIGATION_SUPERSEDE_SCOPE_MISMATCH",
            "费用义务更正范围不匹配",
            status_code=409,
        )
    activities = _activities_naming_header(transaction, command.case_id, header.id)
    if len(activities) != 1:
        _fail(
            "FEE_OBLIGATION_PRIOR_ACTIVITY_INVALID",
            "被替代费用义务的识别活动无效",
            status_code=409,
        )
    return _Prior(header, prior_lines, activities[0].id)


def _activities_naming_header(
    transaction: Session,
    case_id: str,
    obligation_id: str,
) -> tuple[CaseActivityEvent, ...]:
    activities = transaction.execute(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.lane == ActivityLane.FEE.value,
            CaseActivityEvent.activity_type == _ACTIVITY_TYPE,
        )
    ).scalars()
    matches: list[CaseActivityEvent] = []
    for activity in activities:
        try:
            payload = _strict_json_loads(activity.payload_json)
        except (TypeError, ValueError):
            _stored_state_invalid()
        if (
            type(payload) is dict
            and payload.get("schema") == _PAYLOAD_SCHEMA
            and payload.get("obligation_id") == obligation_id
        ):
            matches.append(activity)
    return tuple(matches)


def _validate_current_identities(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    lines: tuple[FeeObligationLineInput, ...],
    *,
    prior: _Prior | None,
) -> None:
    owners = _identity_owners(command, transaction, lines)
    if not owners:
        return
    if prior is not None:
        if any(owner != prior.header.id for owner in owners.values()):
            _identity_conflict()
        return
    if len(owners) == len(lines) and len(set(owners.values())) == 1:
        _identity_conflict()
    _mixed_identity_conflict()


def _identity_owners(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    lines: tuple[FeeObligationLineInput, ...],
) -> dict[str, str]:
    keys = tuple(
        _identity_key(
            command.case_id,
            command.source_activity_id,
            line.fee_code,
            line.fee_year_key,
        )
        for line in lines
    )
    return dict(
        transaction.execute(
            select(
                FeeObligationLineModel.current_identity_key,
                FeeObligationLineModel.obligation_id,
            ).where(FeeObligationLineModel.current_identity_key.in_(keys))
        ).all()
    )


def _release_prior(
    prior: _Prior,
    *,
    lines: tuple[FeeObligationLineModel, ...],
    actor_id: str,
) -> None:
    now = datetime.now()
    prior.header.obligation_status = FeeObligationStatus.SUPERSEDED.value
    prior.header.updated_by = actor_id
    prior.header.updated_at = now
    for line in lines:
        line.current_identity_key = None
        line.updated_by = actor_id
        line.updated_at = now


def _activity_command(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    *,
    source_activity: CaseActivityEvent,
    payload: dict[str, object],
    supersedes_event_id: str | None,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=command.case_id,
        event_type=_ACTIVITY_TYPE,
        lane=ActivityLane.FEE,
        effective_at=source_activity.effective_at,
        occurred_at=source_activity.occurred_at,
        evidence_refs=_source_evidence(transaction, source_activity.id),
        actor_id=command.actor_id,
        reviewer_id=source_activity.reviewer_id,
        idempotency_key=command.idempotency_key,
        source_activity_id=command.source_activity_id,
        supersedes_event_id=supersedes_event_id,
        payload=payload,
        confirmation_status=_fee_confirmation(command.source_status),
    )


def _source_evidence(
    transaction: Session,
    source_activity_id: str,
) -> tuple[EvidenceReference, ...]:
    rows = transaction.execute(
        select(CaseActivityEventEvidence)
        .where(CaseActivityEventEvidence.activity_id == source_activity_id)
        .order_by(
            CaseActivityEventEvidence.case_id,
            CaseActivityEventEvidence.evidence_kind,
            CaseActivityEventEvidence.object_type,
            CaseActivityEventEvidence.object_id,
            CaseActivityEventEvidence.content_hash,
            CaseActivityEventEvidence.captured_at,
        )
    ).scalars()
    return tuple(
        EvidenceReference(
            case_id=row.case_id,
            evidence_kind=row.evidence_kind,
            object_type=row.object_type,
            object_id=row.object_id,
            content_hash=row.content_hash,
            captured_at=row.captured_at,
        )
        for row in rows
    )


def _fee_confirmation(source_status: FeeSourceStatus) -> ConfirmationStatus:
    if source_status is FeeSourceStatus.VERIFIED:
        return ConfirmationStatus.CONFIRMED
    if source_status is FeeSourceStatus.REVIEW_REQUIRED:
        return ConfirmationStatus.NEEDS_REVIEW
    return ConfirmationStatus.LEGACY_UNVERIFIED


def _new_header(
    command: RecognizeFeeObligationCommand,
    obligation_id: str,
) -> FeeObligationModel:
    return FeeObligationModel(
        id=obligation_id,
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        source_document_id=command.source_document_id,
        fee_domain=command.fee_domain.value,
        obligation_type=command.obligation_type,
        obligation_status=FeeObligationStatus.RECOGNIZED.value,
        due_date=command.due_date,
        currency=command.currency,
        source_status=command.source_status.value,
        client_instruction_status=FeeClientInstructionStatus.PENDING.value,
        draft_status=FeeObligationDraftStatus.NOT_CREATED.value,
        payment_status=FeePaymentStatus.UNPAID.value,
        official_evidence_status=(
            FeeOfficialEvidenceStatus.PENDING.value
            if command.fee_domain is FeeDomain.GOV
            else FeeOfficialEvidenceStatus.NOT_APPLICABLE.value
        ),
        supersedes_obligation_id=command.supersedes_obligation_id,
        supersede_reason=command.supersede_reason,
        created_by=command.actor_id,
        updated_by=command.actor_id,
    )


def _new_line(
    command: RecognizeFeeObligationCommand,
    line: FeeObligationLineInput,
    obligation_id: str,
) -> FeeObligationLineModel:
    return FeeObligationLineModel(
        id=str(uuid4()),
        obligation_id=obligation_id,
        case_id=command.case_id,
        source_activity_id=command.source_activity_id,
        fee_code=line.fee_code,
        fee_name=line.fee_name,
        fee_year_key=line.fee_year_key,
        official_full_amount=line.official_full_amount,
        reduction_ratio=line.reduction_ratio,
        payable_amount=line.payable_amount,
        source_amount=line.source_amount,
        source_date=line.source_date,
        difference_review_state=line.difference_review_state.value,
        current_identity_key=_identity_key(
            command.case_id,
            command.source_activity_id,
            line.fee_code,
            line.fee_year_key,
        ),
        created_by=command.actor_id,
        updated_by=command.actor_id,
    )


def _payload(
    command: RecognizeFeeObligationCommand,
    lines: tuple[FeeObligationLineInput, ...],
    obligation_id: str,
) -> dict[str, object]:
    return {
        "schema": _PAYLOAD_SCHEMA,
        "obligation_id": obligation_id,
        "obligation": {
            "actor_id": command.actor_id,
            "case_id": command.case_id,
            "currency": command.currency,
            "due_date": None if command.due_date is None else command.due_date.isoformat(),
            "fee_domain": command.fee_domain.value,
            "lines": [
                {
                    "difference_review_state": line.difference_review_state.value,
                    "fee_code": line.fee_code,
                    "fee_name": line.fee_name,
                    "fee_year_key": line.fee_year_key,
                    "official_full_amount": _amount_text(line.official_full_amount),
                    "payable_amount": _amount_text(line.payable_amount),
                    "reduction_ratio": format(line.reduction_ratio, ".4f"),
                    "source_amount": _amount_text(line.source_amount),
                    "source_date": (
                        None if line.source_date is None else line.source_date.isoformat()
                    ),
                }
                for line in lines
            ],
            "obligation_type": command.obligation_type,
            "source_activity_id": command.source_activity_id,
            "source_document_id": command.source_document_id,
            "source_status": command.source_status.value,
            "supersede_reason": command.supersede_reason,
            "supersedes_obligation_id": command.supersedes_obligation_id,
        },
    }


def _amount_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, ".2f")


def _identity_key(
    case_id: str,
    source_activity_id: str,
    fee_code: str,
    fee_year_key: int,
) -> str:
    raw = f"{case_id}|{source_activity_id}|{fee_code}|{fee_year_key}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _replay_existing(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    case: Case,
    activity: CaseActivityEvent,
    lines: tuple[FeeObligationLineInput, ...],
) -> RecognizeFeeObligationResult:
    if activity.activity_type != _ACTIVITY_TYPE or activity.lane != ActivityLane.FEE.value:
        _idempotency_conflict()
    try:
        stored_payload = _strict_json_loads(activity.payload_json)
    except (TypeError, ValueError):
        _stored_state_invalid()
    if type(stored_payload) is not dict or stored_payload.get("schema") != _PAYLOAD_SCHEMA:
        _stored_state_invalid()
    if activity.payload_json != json.dumps(
        stored_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ):
        _stored_state_invalid()
    obligation_id = stored_payload.get("obligation_id")
    if not _valid_uuid(obligation_id):
        _stored_state_invalid()
    if stored_payload != _payload(command, lines, cast(str, obligation_id)):
        _idempotency_conflict()

    header = transaction.execute(
        select(FeeObligationModel).where(FeeObligationModel.id == obligation_id)
    ).scalar_one_or_none()
    if header is None:
        _stored_state_invalid()
    if header.case_id != command.case_id:
        _idempotency_conflict()
    _validate_replay_header(command, transaction, header, lines)

    source_activity = transaction.execute(
        select(CaseActivityEvent).where(CaseActivityEvent.id == command.source_activity_id)
    ).scalar_one_or_none()
    if source_activity is None or source_activity.case_id != command.case_id:
        _stored_state_invalid()
    supersedes_event_id = _replay_supersedes_event_id(
        command,
        transaction,
        activity,
    )
    stored_projection = _activity_projection(activity)
    try:
        transition = append_case_activity(
            _activity_command(
                command,
                transaction,
                source_activity=source_activity,
                payload=cast(dict[str, object], stored_payload),
                supersedes_event_id=supersedes_event_id,
            ),
            transaction,
            previous_projection=stored_projection,
            current_projection=stored_projection,
            legacy_case_status=case.status,
            conflict_codes=(),
        )
    except BusinessError as exc:
        if exc.code == "LIFECYCLE_IDEMPOTENCY_CONFLICT":
            _idempotency_conflict()
        raise
    if not transition.reused or transition.activity_id != activity.id:
        _stored_state_invalid()
    return _result(
        transaction,
        header,
        activity_id=activity.id,
        idempotency_key=command.idempotency_key,
        reused=True,
        superseded_obligation_id=command.supersedes_obligation_id,
    )


def _validate_replay_header(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    header: FeeObligationModel,
    command_lines: tuple[FeeObligationLineInput, ...],
) -> None:
    immutable = (
        (header.source_activity_id, command.source_activity_id),
        (header.source_document_id, command.source_document_id),
        (header.fee_domain, command.fee_domain.value),
        (header.obligation_type, command.obligation_type),
        (header.due_date, command.due_date),
        (header.currency, command.currency),
        (header.source_status, command.source_status.value),
        (header.supersedes_obligation_id, command.supersedes_obligation_id),
        (header.supersede_reason, command.supersede_reason),
    )
    if any(stored != expected for stored, expected in immutable):
        _idempotency_conflict()
    if header.obligation_status not in {
        FeeObligationStatus.RECOGNIZED.value,
        FeeObligationStatus.SUPERSEDED.value,
    }:
        _stored_state_invalid()
    stored_lines = tuple(
        transaction.execute(
            select(FeeObligationLineModel)
            .where(FeeObligationLineModel.obligation_id == header.id)
            .order_by(FeeObligationLineModel.fee_code, FeeObligationLineModel.fee_year_key)
        ).scalars()
    )
    if len(stored_lines) != len(command_lines):
        _idempotency_conflict()
    for stored, expected in zip(stored_lines, command_lines, strict=True):
        snapshots = (
            (stored.obligation_id, header.id),
            (stored.case_id, command.case_id),
            (stored.source_activity_id, command.source_activity_id),
            (stored.fee_code, expected.fee_code),
            (stored.fee_name, expected.fee_name),
            (stored.fee_year_key, expected.fee_year_key),
            (stored.official_full_amount, expected.official_full_amount),
            (stored.reduction_ratio, expected.reduction_ratio),
            (stored.payable_amount, expected.payable_amount),
            (stored.source_amount, expected.source_amount),
            (stored.source_date, expected.source_date),
            (stored.difference_review_state, expected.difference_review_state.value),
        )
        if any(value != supplied for value, supplied in snapshots):
            _idempotency_conflict()
        expected_key = _identity_key(
            stored.case_id,
            stored.source_activity_id,
            stored.fee_code,
            stored.fee_year_key,
        )
        if header.obligation_status == FeeObligationStatus.RECOGNIZED.value:
            if stored.current_identity_key != expected_key:
                _idempotency_conflict()
        elif stored.current_identity_key is not None:
            _stored_state_invalid()


def _replay_supersedes_event_id(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    activity: CaseActivityEvent,
) -> str | None:
    if command.supersedes_obligation_id is None:
        if activity.supersedes_event_id is not None:
            _idempotency_conflict()
        return None
    prior_activity = transaction.execute(
        select(CaseActivityEvent).where(CaseActivityEvent.id == activity.supersedes_event_id)
    ).scalar_one_or_none()
    if prior_activity is None:
        _stored_state_invalid()
    try:
        payload = _strict_json_loads(prior_activity.payload_json)
    except (TypeError, ValueError):
        _stored_state_invalid()
    if (
        type(payload) is not dict
        or payload.get("schema") != _PAYLOAD_SCHEMA
        or payload.get("obligation_id") != command.supersedes_obligation_id
    ):
        _stored_state_invalid()
    return prior_activity.id


def _result(
    transaction: Session,
    header: FeeObligationModel,
    *,
    activity_id: str,
    idempotency_key: str,
    reused: bool,
    superseded_obligation_id: str | None,
) -> RecognizeFeeObligationResult:
    lines = tuple(
        transaction.execute(
            select(FeeObligationLineModel)
            .where(FeeObligationLineModel.obligation_id == header.id)
            .order_by(FeeObligationLineModel.fee_code, FeeObligationLineModel.fee_year_key)
        ).scalars()
    )
    return RecognizeFeeObligationResult(
        obligation=FeeObligation(
            id=header.id,
            case_id=header.case_id,
            source=FeeObligationSource(
                source_activity_id=header.source_activity_id,
                source_document_id=header.source_document_id,
                status=_stored_enum(FeeSourceStatus, header.source_status),
            ),
            fee_domain=_stored_enum(FeeDomain, header.fee_domain),
            obligation_type=header.obligation_type,
            due_date=header.due_date,
            currency=header.currency,
            statuses=FeeObligationStatuses(
                estimate_status=None,
                obligation_status=_stored_enum(
                    FeeObligationStatus,
                    header.obligation_status,
                ),
                client_instruction_status=_stored_enum(
                    FeeClientInstructionStatus,
                    header.client_instruction_status,
                ),
                draft_status=_stored_enum(
                    FeeObligationDraftStatus,
                    header.draft_status,
                ),
                pay_list_status=FeePayListStatus.NOT_CREATED,
                payment_status=_stored_enum(FeePaymentStatus, header.payment_status),
                official_evidence_status=_stored_enum(
                    FeeOfficialEvidenceStatus,
                    header.official_evidence_status,
                ),
            ),
            lines=tuple(_line_value(line) for line in lines),
            supersedes_obligation_id=header.supersedes_obligation_id,
            supersede_reason=header.supersede_reason,
        ),
        activity_id=activity_id,
        idempotency_key=idempotency_key,
        reused=reused,
        superseded_obligation_id=superseded_obligation_id,
    )


def _line_value(line: FeeObligationLineModel) -> FeeObligationLine:
    return FeeObligationLine(
        id=line.id,
        obligation_id=line.obligation_id,
        case_id=line.case_id,
        source_activity_id=line.source_activity_id,
        fee_code=line.fee_code,
        fee_name=line.fee_name,
        fee_year_key=line.fee_year_key,
        official_full_amount=line.official_full_amount,
        reduction_ratio=line.reduction_ratio,
        payable_amount=line.payable_amount,
        source_amount=line.source_amount,
        source_date=line.source_date,
        difference_review_state=_stored_enum(
            FeeDifferenceReviewState,
            line.difference_review_state,
        ),
        current_identity_key=line.current_identity_key,
    )


def _stored_enum(enum_type, value: str):
    try:
        return enum_type(value)
    except ValueError:
        _stored_state_invalid()


def _case_projection(case: Case) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                None if case.business_stage is None else BusinessStage(case.business_stage)
            ),
            official_procedure_stage=(
                None
                if case.official_procedure_stage is None
                else OfficialProcedureStage(case.official_procedure_stage)
            ),
            legal_status=None if case.legal_status is None else LegalStatus(case.legal_status),
            lifecycle_verification_status=(
                None
                if case.lifecycle_verification_status is None
                else ConfirmationStatus(case.lifecycle_verification_status)
            ),
        )
    except ValueError:
        _fail(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "案件存量生命周期投影无效",
            status_code=409,
        )


def _activity_projection(activity: CaseActivityEvent) -> LifecycleProjection:
    try:
        if (
            activity.old_business_stage != activity.new_business_stage
            or activity.old_official_procedure_stage != activity.new_official_procedure_stage
            or activity.old_legal_status != activity.new_legal_status
        ):
            _stored_state_invalid()
        return LifecycleProjection(
            business_stage=(
                None
                if activity.old_business_stage is None
                else BusinessStage(activity.old_business_stage)
            ),
            official_procedure_stage=(
                None
                if activity.old_official_procedure_stage is None
                else OfficialProcedureStage(activity.old_official_procedure_stage)
            ),
            legal_status=(
                None
                if activity.old_legal_status is None
                else LegalStatus(activity.old_legal_status)
            ),
            lifecycle_verification_status=None,
        )
    except ValueError:
        _stored_state_invalid()


def _recognized_unique_failure(exc: IntegrityError) -> bool:
    message = str(exc.orig).lower()
    return (
        "t_case_activity_event.case_id, t_case_activity_event.idempotency_key" in message
        or "uq_t_case_activity_event_case_idempotency_key" in message
        or "t_fee_obligation_line.current_identity_key" in message
        or "uq_t_fee_obligation_line_current_identity_key" in message
    )


def _recover_recognized_race(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
    lines: tuple[FeeObligationLineInput, ...],
) -> RecognizeFeeObligationResult:
    with transaction.no_autoflush:
        case = _case_or_fail(transaction, command.case_id)
        activity = _activity_by_key(
            transaction,
            case_id=command.case_id,
            idempotency_key=command.idempotency_key,
        )
        owners = _identity_owners(command, transaction, lines)
        if activity is not None:
            return _replay_existing(command, transaction, case, activity, lines)
        if owners:
            if len(owners) == len(lines) and len(set(owners.values())) == 1:
                _identity_conflict()
            _mixed_identity_conflict()
    _fail(
        "FEE_OBLIGATION_CONCURRENCY_CONFLICT",
        "并发费用义务尚不可见，请重试完整事务",
        status_code=409,
    )


def _valid_uuid(value: object) -> bool:
    if type(value) is not str or len(value) != 36:
        return False
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False


def _strict_json_loads(value: str) -> object:
    return json.loads(value, parse_constant=_reject_non_finite_json_constant)


def _reject_non_finite_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _required_string(
    value: object,
    limit: int,
    field: str,
    invalid: Callable[[str], None],
) -> None:
    if type(value) is not str or not value.strip() or len(value) > limit:
        invalid(field)


def _optional_string(
    value: object,
    limit: int,
    field: str,
    invalid: Callable[[str], None],
) -> None:
    if value is not None:
        _required_string(value, limit, field, invalid)


def _invalid_command(field: str) -> None:
    _fail(
        "FEE_OBLIGATION_COMMAND_INVALID",
        "费用义务识别命令无效",
        details={"field": field},
        status_code=400,
    )


def _invalid_line(index: int, field: str) -> None:
    _invalid_line_field(f"lines[{index}].{field}")


def _invalid_line_field(field: str) -> None:
    _fail(
        "FEE_OBLIGATION_LINE_INVALID",
        "费用义务明细无效",
        details={"field": field},
        status_code=400,
    )


def _supersede_pair_invalid() -> None:
    _fail(
        "FEE_OBLIGATION_SUPERSEDE_PAIR_INVALID",
        "被替代义务与更正原因必须同时提供",
        status_code=409,
    )


def _identity_conflict() -> None:
    _fail(
        "FEE_OBLIGATION_IDENTITY_CONFLICT",
        "费用义务当前身份已被其他识别占用",
        status_code=409,
    )


def _mixed_identity_conflict() -> None:
    _fail(
        "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        "费用义务当前身份集合不完整或跨越多个义务",
        status_code=409,
    )


def _idempotency_conflict() -> None:
    _fail(
        "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        "幂等键已用于不同的费用义务事实",
        status_code=409,
    )


def _stored_state_invalid() -> None:
    _fail(
        "FEE_OBLIGATION_STORED_STATE_INVALID",
        "费用义务存量识别状态无效",
        status_code=409,
    )


def _fail(
    code: str,
    message: str,
    *,
    details: dict | None = None,
    status_code: int,
) -> None:
    raise BusinessError(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
    )
