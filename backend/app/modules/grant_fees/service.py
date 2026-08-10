from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

from sqlalchemy import String, and_, cast, or_, select, update
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.billing.models import Bill, BillItem
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_service import apply_lifecycle_event
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.extra_data import DocumentExtraDataError, parse_document_extra_data
from app.modules.documents.grant_fee_lines import (
    GrantNoticeFeeLineSnapshot,
    extract_grant_notice_fee_line_snapshot,
)
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion
from app.modules.documents.schemas import DocumentCreateIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.documents.service import (
    _backend_storage_dir,
    _merge_document_create_extra_data,
    build_document_template_render_context,
    create_document,
    persist_generated_attachment,
    resolve_document_template_render_source,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationLine,
    FeeRate,
    T_GrantFeeTask,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeObligationStatus,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
    RecordFeeObligationInstructionCommand,
)
from app.modules.fees.obligation_service import (
    get_fee_obligation,
    recognize_obligation,
    record_client_instruction,
)
from app.modules.fees.service import (
    fee_rate_effective_on_conditions,
    fee_rate_source_enabled_condition,
    recalc_fee_draft_totals,
)
from app.modules.templates.render import TemplateRenderer

GRANT_FEE_TASK_PERMISSION_CODES = ("GrantFeeTask.Read", "GrantFeeTask.Write")
GRANT_FEE_TASK_STATES = ("OPEN", "WAITING_CLIENT", "READY_TO_DRAFT", "DRAFT_GENERATED", "DONE")
GRANT_FEE_TASK_ACTIONS = (
    "mark_waiting_client",
    "record_pay_instruction",
    "record_abandon_instruction",
    "mark_draft_generated",
    "mark_done",
)

GRANT_FEE_DRAFT_TYPE = "GRANT_FEE"
GRANT_FEE_DRAFT_MARKER_PREFIX = "GRANT_FEE_TASK:"
GRANT_FEE_GOV_FEE_CODE = "GRANT_FEE_GOV"
GRANT_FEE_SERVICE_FEE_CODE = "GRANT_FEE_SERVICE"
GRANT_FEE_NOTICE_TEMPLATE_CODE = "GRANT_FEE_NOTICE"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_ZERO = Decimal("0")
_MONEY_QUANT = Decimal("0.01")
_SQLITE_LOCK_RETRY_ATTEMPTS = 10
_SQLITE_LOCK_RETRY_DELAY_SECONDS = 0.05
_GRANT_NOTICE_EVENT_TYPE = "GRANT_REGISTRATION_NOTICE_RECORDED"
_GRANT_NOTICE_EVENT_SCHEMA = "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1"
_GRANT_NOTICE_FEE_LINES_SCHEMA = "FPMS_GRANT_NOTICE_FEE_LINES_V1"
_GRANT_NOTICE_IDEMPOTENCY_PREFIX = "grant-registration-notice:"
_GRANT_NOTICE_PAYLOAD_KEYS = {
    "schema",
    "case_id",
    "grant_fee_task_id",
    "source_document_id",
    "reviewed_evidence_version_id",
    "reviewed_evidence_content_hash",
    "reviewed_at",
    "grant_fee_lines_schema",
    "grant_fee_lines_snapshot",
    "grant_fee_lines_snapshot_hash",
    "due_date",
    "deadline_source",
    "deadline_confirmed_at",
    "predecessor_grant_fee_task_id",
    "supersedes_activity_id",
}
_GRANT_NOTICE_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_GRANT_NOTICE_SNAPSHOT_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_GRANT_NOTICE_CANONICAL_AMOUNT_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.[0-9]{2}")
_GRANT_FEE_TASK_DONE_EVENT_TYPE = "GRANT_FEE_TASK_DONE"
_GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE = "GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED"
_GRANT_OFFICIAL_FEE_REVIEW_SCHEMA = "FPMS_GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED_V1"
_GRANT_OFFICIAL_FEE_REVIEW_BASIS = "AUTHORIZED_OPERATOR_MANUAL_ENTRY"
_GRANT_OFFICIAL_FEE_REVIEW_PAYLOAD_KEYS = {
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
_GRANT_OFFICIAL_FEE_REVIEW_LINE_KEYS = {
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

_STATE_ALLOWED_ACTIONS = {
    "OPEN": ("mark_waiting_client",),
    "WAITING_CLIENT": ("record_pay_instruction", "record_abandon_instruction"),
    "READY_TO_DRAFT": ("mark_draft_generated",),
    "DRAFT_GENERATED": ("mark_done",),
    "DONE": (),
}

_ACTION_NEXT_STATE = {
    "mark_waiting_client": "WAITING_CLIENT",
    "record_pay_instruction": "READY_TO_DRAFT",
    "record_abandon_instruction": "DONE",
    "mark_draft_generated": "DRAFT_GENERATED",
    "mark_done": "DONE",
}

_BATCH_ALLOWED_ACTIONS = ("record_pay_instruction", "record_abandon_instruction")
_NOTICE_ALLOWED_STATES = ("OPEN", "WAITING_CLIENT")
_GRANT_FEE_DEADLINE_PREVIEW_FIELDS = {
    "trigger_rule": "收到办理登记手续通知书/授权通知书",
    "deadline_rule": "以办理登记手续通知书/授权通知书载明期限为准；当前按授权费任务到期日展示",
    "fee_basis": "授权阶段官费按授权费任务金额展示；如无授权费率则回退授权当年年费规则",
    "fee_node_explanation": "授权费用节点：客户确认缴费后生成官费草单，缴费登记后进入授权后年费监视。",
}


@dataclass(frozen=True, slots=True)
class GrantFeeTaskReplacementResult:
    document: Document
    replacement_task: T_GrantFeeTask
    superseded_task_id: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class RecognizeGrantYearAnnuityObligationCommand:
    grant_fee_task_id: str
    source_activity_id: str
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordGrantFeeTaskInstructionCommand:
    grant_fee_task_id: str
    source_activity_id: str
    instruction: str
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecordGrantFeeTaskInstructionResult:
    grant_fee_task_id: str
    fee_obligation_id: str
    instruction: FeeClientInstruction
    activity_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantOfficialFeeReviewLineInput:
    obligation_line_id: str
    official_full_amount: Decimal
    confirmed_payable_amount: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfirmGrantOfficialFeesCommand:
    grant_fee_task_id: str
    source_activity_id: str
    obligation_id: str
    reviewed_evidence_version_id: str
    expected_content_hash: str
    confirmed_at: datetime
    actor_id: str
    idempotency_key: str
    lines: tuple[GrantOfficialFeeReviewLineInput, ...]


@dataclass(frozen=True, slots=True)
class ConfirmGrantOfficialFeesResult:
    grant_fee_task_id: str
    fee_obligation_id: str
    source_activity_id: str
    review_activity_id: str
    reviewed_line_ids: tuple[str, ...]
    confirmed_at: datetime
    idempotency_key: str
    reused: bool


def _grant_instruction_command_invalid(field: str) -> None:
    raise_business_error(
        "GRANT_INSTRUCTION_COMMAND_INVALID",
        "授权费用任务客户指示命令无效",
        details={"field": field},
        status_code=400,
    )


def _grant_instruction_link_not_found() -> None:
    raise_business_error(
        "GRANT_INSTRUCTION_LINK_NOT_FOUND",
        "授权费用任务客户指示关联不存在",
        status_code=404,
    )


def _grant_instruction_lineage_conflict() -> None:
    raise_business_error(
        "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
        "授权费用任务客户指示谱系不一致",
        status_code=409,
    )


def _validate_grant_instruction_command(command: object) -> None:
    if type(command) is not RecordGrantFeeTaskInstructionCommand:
        _grant_instruction_command_invalid("command")
    for field, limit in (
        ("grant_fee_task_id", 36),
        ("source_activity_id", 36),
        ("actor_id", 36),
        ("idempotency_key", 128),
    ):
        value = getattr(command, field)
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or "\x00" in value
            or len(value) > limit
        ):
            _grant_instruction_command_invalid(field)
    if type(command.instruction) is not str or command.instruction not in {
        "PAY",
        "HOLD",
        "ABANDON",
    }:
        _grant_instruction_command_invalid("instruction")


def _grant_instruction_expected_source(
    transaction: Session,
    *,
    task: T_GrantFeeTask,
    activity: CaseActivityEvent,
) -> tuple[Case, tuple[FeeObligationLineInput, ...], dict[str, object]]:
    if (
        task.type != "GRANT"
        or type(task.case_id) is not str
        or not task.case_id
        or task.source_document_id is None
        or type(task.due_date) is not date
        or not _exact_grant_notice_text(task.deadline_source, max_length=32)
        or type(task.deadline_confirmed_at) is not datetime
        or task.deadline_confirmed_at.tzinfo is not None
        or activity.case_id != task.case_id
        or activity.activity_type != _GRANT_NOTICE_EVENT_TYPE
        or activity.lane != ActivityLane.LIFECYCLE.value
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
    ):
        _grant_instruction_lineage_conflict()
    try:
        payload, _ = _validated_stored_grant_notice(
            transaction,
            activity=activity,
            task=task,
        )
    except BusinessError:
        _grant_instruction_lineage_conflict()
    document = transaction.get(Document, task.source_document_id)
    evidence = transaction.get(
        DocumentEvidenceVersion,
        payload["reviewed_evidence_version_id"],
    )
    case = transaction.get(Case, task.case_id)
    if document is None or evidence is None or case is None:
        _grant_instruction_link_not_found()
    if (
        document.id != payload["source_document_id"]
        or document.case_id != task.case_id
        or evidence.case_id != task.case_id
        or evidence.document_id != document.id
        or evidence.id != payload["reviewed_evidence_version_id"]
        or evidence.content_hash != payload["reviewed_evidence_content_hash"]
        or payload["case_id"] != task.case_id
        or payload["grant_fee_task_id"] != task.id
        or payload["due_date"] != task.due_date.isoformat()
        or payload["deadline_source"] != task.deadline_source
        or payload["deadline_confirmed_at"] != task.deadline_confirmed_at.isoformat()
    ):
        _grant_instruction_lineage_conflict()
    fee_code = {
        "INV": "CN_ANNUITY_FEE_INV",
        "UM": "CN_ANNUITY_FEE_UM",
        "DES": "CN_ANNUITY_FEE_DES",
    }.get(case.patent_category)
    if fee_code is None:
        _grant_instruction_lineage_conflict()
    try:
        lines = _grant_year_annuity_lines(payload, fee_code=fee_code)
    except BusinessError:
        _grant_instruction_lineage_conflict()
    return case, lines, payload


def _grant_instruction_recognition_count(
    transaction: Session,
    *,
    case_id: str,
    obligation_id: str,
) -> int:
    matches = 0
    for activity in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.lane == ActivityLane.FEE.value,
            CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED",
        )
    ):
        try:
            payload = json.loads(activity.payload_json)
        except (TypeError, ValueError):
            continue
        if type(payload) is dict and payload.get("obligation_id") == obligation_id:
            matches += 1
    return matches


def _validate_grant_instruction_obligation(
    transaction: Session,
    *,
    task: T_GrantFeeTask,
    activity: CaseActivityEvent,
    expected_lines: tuple[FeeObligationLineInput, ...],
    obligation_id: str,
) -> None:
    recognition_count = _grant_instruction_recognition_count(
        transaction,
        case_id=task.case_id,
        obligation_id=obligation_id,
    )
    if recognition_count == 0:
        _grant_instruction_link_not_found()
    if recognition_count != 1:
        _grant_instruction_lineage_conflict()
    try:
        obligation = get_fee_obligation(obligation_id, transaction)
    except BusinessError as exc:
        if exc.code == "FEE_OBLIGATION_NOT_FOUND":
            _grant_instruction_link_not_found()
        _grant_instruction_lineage_conflict()
    expected_by_year = {line.fee_year_key: line for line in expected_lines}
    actual_by_year = {line.fee_year_key: line for line in obligation.lines}
    if (
        obligation.case_id != task.case_id
        or obligation.source.source_activity_id != activity.id
        or obligation.source.source_document_id != task.source_document_id
        or obligation.source.status is not FeeSourceStatus.VERIFIED
        or obligation.fee_domain is not FeeDomain.GOV
        or obligation.obligation_type != "GRANT_YEAR_ANNUITY"
        or obligation.due_date != task.due_date
        or obligation.currency != "CNY"
        or len(actual_by_year) != len(obligation.lines)
        or set(actual_by_year) != set(expected_by_year)
    ):
        _grant_instruction_lineage_conflict()
    for year, expected in expected_by_year.items():
        actual = actual_by_year[year]
        expected_identity = hashlib.sha256(
            (f"{task.case_id}|{activity.id}|{expected.fee_code}|{expected.fee_year_key}").encode(
                "utf-8"
            )
        ).hexdigest()
        expected_current_identity = (
            expected_identity
            if obligation.statuses.obligation_status is FeeObligationStatus.RECOGNIZED
            else None
        )
        if (
            actual.case_id != task.case_id
            or actual.source_activity_id != activity.id
            or actual.fee_code != expected.fee_code
            or actual.fee_name != expected.fee_name
            or actual.official_full_amount != expected.official_full_amount
            or actual.reduction_ratio != expected.reduction_ratio
            or actual.payable_amount != expected.payable_amount
            or actual.source_amount != expected.source_amount
            or actual.source_date != expected.source_date
            or actual.difference_review_state is not expected.difference_review_state
            or actual.current_identity_key != expected_current_identity
        ):
            _grant_instruction_lineage_conflict()

    try:
        predecessor_id, _ = _grant_year_annuity_predecessor(
            transaction,
            task=task,
            activity=activity,
            payload=_grant_notice_payload(activity.payload_json),
            fee_code=next(iter(expected_by_year.values())).fee_code,
        )
    except BusinessError:
        _grant_instruction_lineage_conflict()
    if predecessor_id is not None:
        if obligation.supersedes_obligation_id != predecessor_id:
            _grant_instruction_lineage_conflict()
        return
    if obligation.supersedes_obligation_id is not None:
        _grant_instruction_lineage_conflict()
    if obligation.statuses.obligation_status is FeeObligationStatus.RECOGNIZED:
        return

    children = tuple(
        transaction.scalars(
            select(FeeObligation).where(FeeObligation.supersedes_obligation_id == obligation.id)
        )
    )
    if len(children) != 1:
        _grant_instruction_lineage_conflict()
    child_activity = transaction.get(CaseActivityEvent, children[0].source_activity_id)
    if child_activity is None:
        _grant_instruction_link_not_found()
    try:
        child_payload = _grant_notice_payload(child_activity.payload_json)
    except BusinessError:
        _grant_instruction_lineage_conflict()
    child_task_id = child_payload["grant_fee_task_id"]
    child_task = transaction.get(T_GrantFeeTask, child_task_id)
    if child_task is None:
        _grant_instruction_link_not_found()
    try:
        _validated_stored_grant_notice(
            transaction,
            activity=child_activity,
            task=child_task,
        )
        child_predecessor_id, _ = _grant_year_annuity_predecessor(
            transaction,
            task=child_task,
            activity=child_activity,
            payload=child_payload,
            fee_code=next(iter(expected_by_year.values())).fee_code,
        )
    except BusinessError:
        _grant_instruction_lineage_conflict()
    if child_predecessor_id != obligation.id:
        _grant_instruction_lineage_conflict()


def record_grant_fee_task_instruction(
    command: RecordGrantFeeTaskInstructionCommand,
    transaction: Session,
) -> RecordGrantFeeTaskInstructionResult:
    _validate_grant_instruction_command(command)
    if transaction.new or transaction.dirty or transaction.deleted:
        _grant_instruction_lineage_conflict()
    with transaction.no_autoflush:
        task = transaction.get(T_GrantFeeTask, command.grant_fee_task_id)
        if task is None:
            raise_business_error(
                "GRANT_INSTRUCTION_TASK_NOT_FOUND",
                "授权费用任务不存在",
                status_code=404,
            )
        activity = transaction.get(CaseActivityEvent, command.source_activity_id)
        if activity is None:
            _grant_instruction_link_not_found()
        _case, expected_lines, _payload = _grant_instruction_expected_source(
            transaction,
            task=task,
            activity=activity,
        )
        obligations = tuple(
            transaction.scalars(
                select(FeeObligation).where(
                    FeeObligation.case_id == task.case_id,
                    FeeObligation.source_activity_id == activity.id,
                    FeeObligation.obligation_type == "GRANT_YEAR_ANNUITY",
                )
            )
        )
        if not obligations:
            _grant_instruction_link_not_found()
        if len(obligations) != 1:
            _grant_instruction_lineage_conflict()
        obligation_id = obligations[0].id
        _validate_grant_instruction_obligation(
            transaction,
            task=task,
            activity=activity,
            expected_lines=expected_lines,
            obligation_id=obligation_id,
        )
    instruction = FeeClientInstruction(command.instruction)
    delegated = record_client_instruction(
        RecordFeeObligationInstructionCommand(
            obligation_id=obligation_id,
            instruction=instruction,
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
        ),
        transaction,
    )
    return RecordGrantFeeTaskInstructionResult(
        grant_fee_task_id=task.id,
        fee_obligation_id=obligation_id,
        instruction=instruction,
        activity_id=delegated.activity_id,
        idempotency_key=delegated.idempotency_key,
        reused=delegated.reused,
    )


def _grant_review_error(code: str, message: str, *, status_code: int) -> None:
    raise_business_error(code, message, status_code=status_code)


def _grant_review_command_invalid(field: str) -> None:
    raise_business_error(
        "GRANT_OFFICIAL_FEE_REVIEW_COMMAND_INVALID",
        "授权当年官费人工复核命令无效",
        details={"field": field},
        status_code=400,
    )


def _grant_review_link_not_found() -> None:
    _grant_review_error(
        "GRANT_OFFICIAL_FEE_REVIEW_LINK_NOT_FOUND",
        "授权当年官费人工复核关联不存在",
        status_code=404,
    )


def _grant_review_lineage_conflict() -> None:
    _grant_review_error(
        "GRANT_OFFICIAL_FEE_REVIEW_LINEAGE_CONFLICT",
        "授权当年官费人工复核谱系不一致",
        status_code=409,
    )


def _grant_review_state_conflict() -> None:
    _grant_review_error(
        "GRANT_OFFICIAL_FEE_REVIEW_STATE_CONFLICT",
        "授权当年官费人工复核状态冲突",
        status_code=409,
    )


def _grant_review_idempotency_conflict() -> None:
    _grant_review_error(
        "GRANT_OFFICIAL_FEE_REVIEW_IDEMPOTENCY_CONFLICT",
        "授权当年官费人工复核幂等冲突",
        status_code=409,
    )


def _valid_review_text(value: object, *, limit: int) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _valid_review_money(value: object) -> bool:
    return (
        type(value) is Decimal
        and value.is_finite()
        and value > 0
        and value <= Decimal("9999999999999999.99")
        and value == value.quantize(_MONEY_QUANT)
    )


def _validate_grant_review_command(command: object) -> None:
    if type(command) is not ConfirmGrantOfficialFeesCommand:
        _grant_review_command_invalid("command")
    for field, limit in (
        ("grant_fee_task_id", 36),
        ("source_activity_id", 36),
        ("obligation_id", 36),
        ("reviewed_evidence_version_id", 36),
        ("actor_id", 36),
        ("idempotency_key", 128),
    ):
        if not _valid_review_text(getattr(command, field), limit=limit):
            _grant_review_command_invalid(field)
    if (
        type(command.expected_content_hash) is not str
        or _GRANT_NOTICE_HASH_PATTERN.fullmatch(command.expected_content_hash) is None
    ):
        _grant_review_command_invalid("expected_content_hash")
    if type(command.confirmed_at) is not datetime or command.confirmed_at.tzinfo is not None:
        _grant_review_command_invalid("confirmed_at")
    if type(command.lines) is not tuple or not command.lines:
        _grant_review_command_invalid("lines")
    seen: set[str] = set()
    for line in command.lines:
        if type(line) is not GrantOfficialFeeReviewLineInput:
            _grant_review_command_invalid("lines")
        if not _valid_review_text(line.obligation_line_id, limit=36):
            _grant_review_command_invalid("lines.obligation_line_id")
        if line.obligation_line_id in seen:
            _grant_review_command_invalid("lines")
        seen.add(line.obligation_line_id)
        if not _valid_review_money(line.official_full_amount):
            _grant_review_command_invalid("lines.official_full_amount")
        if not _valid_review_money(line.confirmed_payable_amount):
            _grant_review_command_invalid("lines.confirmed_payable_amount")


def _grant_review_current_evidence(
    transaction: Session,
    *,
    task: T_GrantFeeTask,
    payload: dict[str, object],
) -> DocumentEvidenceVersion:
    evidence = transaction.get(
        DocumentEvidenceVersion,
        payload["reviewed_evidence_version_id"],
    )
    if evidence is None:
        _grant_review_link_not_found()
    current_identity = f"{task.case_id}|{evidence.lineage_key}"
    current_versions = tuple(
        transaction.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.current_identity_key == current_identity
            )
        )
    )
    if (
        evidence.case_id != task.case_id
        or evidence.document_id != task.source_document_id
        or evidence.current_identity_key != current_identity
        or len(current_versions) != 1
        or current_versions[0].id != evidence.id
        or evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or not _valid_review_text(evidence.reviewer_id, limit=36)
        or type(evidence.reviewed_at) is not datetime
        or evidence.reviewed_at.tzinfo is not None
        or evidence.content_hash != payload["reviewed_evidence_content_hash"]
    ):
        _grant_review_lineage_conflict()
    return evidence


def _grant_review_context(
    command: ConfirmGrantOfficialFeesCommand,
    transaction: Session,
) -> tuple[
    T_GrantFeeTask,
    CaseActivityEvent,
    Case,
    FeeObligation,
    tuple[FeeObligationLine, ...],
    dict[str, object],
    tuple[EvidenceReference, EvidenceReference],
]:
    task = transaction.get(T_GrantFeeTask, command.grant_fee_task_id)
    if task is None:
        _grant_review_error(
            "GRANT_OFFICIAL_FEE_REVIEW_TASK_NOT_FOUND",
            "授权费用任务不存在",
            status_code=404,
        )
    activity = transaction.get(CaseActivityEvent, command.source_activity_id)
    if activity is None:
        _grant_review_link_not_found()
    named_evidence = transaction.get(
        DocumentEvidenceVersion,
        command.reviewed_evidence_version_id,
    )
    named_obligation = transaction.get(FeeObligation, command.obligation_id)
    named_line_ids = {
        line_id
        for line_id in transaction.scalars(
            select(FeeObligationLine.id).where(
                FeeObligationLine.id.in_(
                    tuple(line.obligation_line_id for line in command.lines)
                )
            )
        )
    }
    if (
        named_evidence is None
        or named_obligation is None
        or len(named_line_ids) != len(command.lines)
    ):
        _grant_review_link_not_found()
    try:
        case, expected_lines, payload = _grant_instruction_expected_source(
            transaction,
            task=task,
            activity=activity,
        )
        payload, evidence_refs = _validated_stored_grant_notice(
            transaction,
            activity=activity,
            task=task,
        )
    except BusinessError as exc:
        if exc.code == "GRANT_INSTRUCTION_LINK_NOT_FOUND":
            _grant_review_link_not_found()
        _grant_review_lineage_conflict()
    if (
        payload["reviewed_evidence_version_id"] != command.reviewed_evidence_version_id
        or payload["reviewed_evidence_content_hash"] != command.expected_content_hash
        or named_evidence.id != payload["reviewed_evidence_version_id"]
    ):
        _grant_review_lineage_conflict()
    _grant_review_current_evidence(transaction, task=task, payload=payload)
    obligations = tuple(
        transaction.scalars(
            select(FeeObligation).where(
                FeeObligation.case_id == task.case_id,
                FeeObligation.source_activity_id == activity.id,
                FeeObligation.obligation_type == "GRANT_YEAR_ANNUITY",
            )
        )
    )
    if not obligations:
        _grant_review_link_not_found()
    if len(obligations) != 1 or obligations[0].id != command.obligation_id:
        _grant_review_lineage_conflict()
    obligation = obligations[0]
    recognition_count = _grant_instruction_recognition_count(
        transaction,
        case_id=task.case_id,
        obligation_id=obligation.id,
    )
    if recognition_count == 0:
        _grant_review_link_not_found()
    if recognition_count != 1:
        _grant_review_lineage_conflict()
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine)
            .where(FeeObligationLine.obligation_id == obligation.id)
            .order_by(
                FeeObligationLine.fee_year_key.asc(),
                FeeObligationLine.fee_code.asc(),
                FeeObligationLine.id.asc(),
            )
        )
    )
    expected_by_year = {line.fee_year_key: line for line in expected_lines}
    if (
        obligation.case_id != task.case_id
        or obligation.source_activity_id != activity.id
        or obligation.source_document_id != task.source_document_id
        or obligation.fee_domain != FeeDomain.GOV.value
        or obligation.obligation_type != "GRANT_YEAR_ANNUITY"
        or obligation.source_status != FeeSourceStatus.VERIFIED.value
        or obligation.currency != "CNY"
        or obligation.due_date != task.due_date
        or len(lines) != len(expected_by_year)
    ):
        _grant_review_lineage_conflict()
    for line in lines:
        expected = expected_by_year.get(line.fee_year_key)
        if expected is None:
            _grant_review_lineage_conflict()
        expected_identity = hashlib.sha256(
            f"{task.case_id}|{activity.id}|{expected.fee_code}|{expected.fee_year_key}".encode()
        ).hexdigest()
        if (
            line.case_id != task.case_id
            or line.source_activity_id != activity.id
            or line.fee_code != expected.fee_code
            or line.fee_name != expected.fee_name
            or line.reduction_ratio != expected.reduction_ratio
            or line.payable_amount != expected.payable_amount
            or line.source_amount != expected.source_amount
            or line.source_date != expected.source_date
            or line.current_identity_key != expected_identity
        ):
            _grant_review_lineage_conflict()
    try:
        detail = get_fee_obligation(obligation.id, transaction)
    except BusinessError as exc:
        if exc.code in {"FEE_OBLIGATION_NOT_FOUND"}:
            _grant_review_link_not_found()
        _grant_review_lineage_conflict()
    if detail.id != obligation.id or tuple(line.id for line in detail.lines) != tuple(
        line.id for line in lines
    ):
        _grant_review_lineage_conflict()
    return task, activity, case, obligation, lines, payload, evidence_refs


def _grant_review_line_snapshot(
    line: FeeObligationLine,
    *,
    official_full_amount: Decimal | None,
    difference_review_state: str,
) -> dict[str, object]:
    return {
        "obligation_line_id": line.id,
        "fee_code": line.fee_code,
        "fee_name": line.fee_name,
        "fee_year_key": line.fee_year_key,
        "official_full_amount": (
            None if official_full_amount is None else format(official_full_amount, ".2f")
        ),
        "reduction_ratio": format(line.reduction_ratio, ".4f"),
        "payable_amount": format(line.payable_amount, ".2f"),
        "source_amount": format(line.source_amount, ".2f"),
        "source_date": line.source_date.isoformat() if line.source_date is not None else None,
        "difference_review_state": difference_review_state,
        "current_identity_key": line.current_identity_key,
    }


def _grant_review_payload(
    command: ConfirmGrantOfficialFeesCommand,
    *,
    task: T_GrantFeeTask,
    obligation: FeeObligation,
    lines: tuple[FeeObligationLine, ...],
) -> dict[str, object]:
    by_id = {line.obligation_line_id: line for line in command.lines}
    return {
        "schema": _GRANT_OFFICIAL_FEE_REVIEW_SCHEMA,
        "case_id": task.case_id,
        "grant_fee_task_id": task.id,
        "obligation_id": obligation.id,
        "source_activity_id": command.source_activity_id,
        "source_document_id": task.source_document_id,
        "reviewed_evidence_version_id": command.reviewed_evidence_version_id,
        "reviewed_evidence_content_hash": command.expected_content_hash,
        "confirmed_at": command.confirmed_at.isoformat(),
        "review_basis": _GRANT_OFFICIAL_FEE_REVIEW_BASIS,
        "before_lines": [
            _grant_review_line_snapshot(
                line,
                official_full_amount=None,
                difference_review_state=FeeDifferenceReviewState.REVIEW_REQUIRED.value,
            )
            for line in lines
        ],
        "after_lines": [
            _grant_review_line_snapshot(
                line,
                official_full_amount=by_id[line.id].official_full_amount,
                difference_review_state=FeeDifferenceReviewState.MATCHED.value,
            )
            for line in lines
        ],
    }


def _validate_grant_review_command_lines(
    command: ConfirmGrantOfficialFeesCommand,
    lines: tuple[FeeObligationLine, ...],
    *,
    pre_review: bool,
) -> None:
    if tuple(line.obligation_line_id for line in command.lines) != tuple(line.id for line in lines):
        _grant_review_lineage_conflict()
    for supplied, stored in zip(command.lines, lines, strict=True):
        if (
            supplied.confirmed_payable_amount != stored.payable_amount
            or supplied.confirmed_payable_amount != stored.source_amount
        ):
            _grant_review_lineage_conflict()
        if pre_review and (
            stored.official_full_amount is not None
            or stored.difference_review_state != FeeDifferenceReviewState.REVIEW_REQUIRED.value
        ):
            _grant_review_state_conflict()


def _canonical_review_payload(payload: object) -> str:
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _grant_review_idempotency_conflict()


def _precheck_existing_grant_review(
    command: ConfirmGrantOfficialFeesCommand,
    existing: CaseActivityEvent,
) -> None:
    try:
        payload = json.loads(existing.payload_json)
    except (TypeError, ValueError):
        _grant_review_idempotency_conflict()
    if type(payload) is not dict:
        _grant_review_idempotency_conflict()
    after_lines = payload.get("after_lines")
    if (
        set(payload) != _GRANT_OFFICIAL_FEE_REVIEW_PAYLOAD_KEYS
        or payload.get("schema") != _GRANT_OFFICIAL_FEE_REVIEW_SCHEMA
        or payload.get("grant_fee_task_id") != command.grant_fee_task_id
        or payload.get("obligation_id") != command.obligation_id
        or payload.get("source_activity_id") != command.source_activity_id
        or payload.get("reviewed_evidence_version_id")
        != command.reviewed_evidence_version_id
        or payload.get("reviewed_evidence_content_hash") != command.expected_content_hash
        or payload.get("confirmed_at") != command.confirmed_at.isoformat()
        or existing.activity_type != _GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE
        or existing.lane != ActivityLane.FEE.value
        or existing.source_activity_id != command.source_activity_id
        or existing.actor_id != command.actor_id
        or existing.reviewer_id != command.actor_id
        or existing.occurred_at != command.confirmed_at
        or existing.effective_at != command.confirmed_at
        or existing.old_business_stage != existing.new_business_stage
        or existing.old_official_procedure_stage != existing.new_official_procedure_stage
        or existing.old_legal_status != existing.new_legal_status
        or _canonical_review_payload(payload) != existing.payload_json
        or type(after_lines) is not list
        or len(after_lines) != len(command.lines)
    ):
        _grant_review_idempotency_conflict()
    for stored, supplied in zip(after_lines, command.lines, strict=True):
        if (
            type(stored) is not dict
            or set(stored) != _GRANT_OFFICIAL_FEE_REVIEW_LINE_KEYS
            or stored["obligation_line_id"] != supplied.obligation_line_id
            or stored["official_full_amount"] != format(supplied.official_full_amount, ".2f")
            or stored["payable_amount"] != format(supplied.confirmed_payable_amount, ".2f")
        ):
            _grant_review_idempotency_conflict()


def _matching_grant_review_activities(
    transaction: Session,
    *,
    case_id: str,
    grant_fee_task_id: str,
    obligation_id: str,
) -> tuple[CaseActivityEvent, ...]:
    matches: list[CaseActivityEvent] = []
    for candidate in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.activity_type == _GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE,
        )
    ):
        try:
            payload = json.loads(candidate.payload_json)
        except (TypeError, ValueError):
            _grant_review_lineage_conflict()
        if type(payload) is not dict:
            _grant_review_lineage_conflict()
        if (
            payload.get("grant_fee_task_id") == grant_fee_task_id
            or payload.get("obligation_id") == obligation_id
        ):
            if (
                payload.get("grant_fee_task_id") != grant_fee_task_id
                or payload.get("obligation_id") != obligation_id
            ):
                _grant_review_lineage_conflict()
            matches.append(candidate)
    return tuple(matches)


def _replay_grant_official_fee_review(
    command: ConfirmGrantOfficialFeesCommand,
    transaction: Session,
    *,
    existing: CaseActivityEvent,
    task: T_GrantFeeTask,
    case: Case,
    obligation: FeeObligation,
    lines: tuple[FeeObligationLine, ...],
    evidence_refs: tuple[EvidenceReference, EvidenceReference],
) -> ConfirmGrantOfficialFeesResult:
    _validate_grant_review_command_lines(command, lines, pre_review=False)
    if any(
        line.official_full_amount != supplied.official_full_amount
        or line.difference_review_state != FeeDifferenceReviewState.MATCHED.value
        for line, supplied in zip(lines, command.lines, strict=True)
    ):
        _grant_review_idempotency_conflict()
    expected_payload = _grant_review_payload(
        command,
        task=task,
        obligation=obligation,
        lines=lines,
    )
    try:
        stored_payload = json.loads(existing.payload_json)
    except (TypeError, ValueError):
        _grant_review_idempotency_conflict()
    if (
        type(stored_payload) is not dict
        or set(stored_payload) != _GRANT_OFFICIAL_FEE_REVIEW_PAYLOAD_KEYS
        or existing.activity_type != _GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE
        or existing.lane != ActivityLane.FEE.value
        or existing.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or existing.source_activity_id != command.source_activity_id
        or existing.actor_id != command.actor_id
        or existing.reviewer_id != command.actor_id
        or existing.occurred_at != command.confirmed_at
        or existing.effective_at != command.confirmed_at
        or _canonical_review_payload(stored_payload) != existing.payload_json
        or stored_payload != expected_payload
    ):
        _grant_review_idempotency_conflict()
    try:
        previous_projection = LifecycleProjection(
            business_stage=(
                None
                if existing.old_business_stage is None
                else BusinessStage(existing.old_business_stage)
            ),
            official_procedure_stage=(
                None
                if existing.old_official_procedure_stage is None
                else OfficialProcedureStage(existing.old_official_procedure_stage)
            ),
            legal_status=(
                None if existing.old_legal_status is None else LegalStatus(existing.old_legal_status)
            ),
            lifecycle_verification_status=None,
        )
        current_projection = LifecycleProjection(
            business_stage=(
                None
                if existing.new_business_stage is None
                else BusinessStage(existing.new_business_stage)
            ),
            official_procedure_stage=(
                None
                if existing.new_official_procedure_stage is None
                else OfficialProcedureStage(existing.new_official_procedure_stage)
            ),
            legal_status=(
                None if existing.new_legal_status is None else LegalStatus(existing.new_legal_status)
            ),
            lifecycle_verification_status=None,
        )
    except ValueError:
        _grant_review_idempotency_conflict()
    try:
        replay = append_case_activity(
            LifecycleEventCommand(
                case_id=case.id,
                event_type=_GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE,
                lane=ActivityLane.FEE,
                effective_at=command.confirmed_at,
                occurred_at=command.confirmed_at,
                evidence_refs=evidence_refs,
                actor_id=command.actor_id,
                reviewer_id=command.actor_id,
                idempotency_key=command.idempotency_key,
                source_activity_id=command.source_activity_id,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload=expected_payload,
            ),
            transaction,
            previous_projection=previous_projection,
            current_projection=current_projection,
            legacy_case_status=case.status,
        )
    except BusinessError:
        _grant_review_idempotency_conflict()
    if not replay.reused or replay.activity_id != existing.id:
        _grant_review_idempotency_conflict()
    return ConfirmGrantOfficialFeesResult(
        grant_fee_task_id=task.id,
        fee_obligation_id=obligation.id,
        source_activity_id=command.source_activity_id,
        review_activity_id=existing.id,
        reviewed_line_ids=tuple(line.id for line in lines),
        confirmed_at=command.confirmed_at,
        idempotency_key=command.idempotency_key,
        reused=True,
    )


def confirm_grant_official_fees(
    command: ConfirmGrantOfficialFeesCommand,
    transaction: Session,
) -> ConfirmGrantOfficialFeesResult:
    _validate_grant_review_command(command)
    if not isinstance(transaction, Session):
        _grant_review_command_invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _grant_review_error(
            "GRANT_OFFICIAL_FEE_REVIEW_TRANSACTION_CONFLICT",
            "授权当年官费人工复核要求干净事务",
            status_code=409,
        )
    with transaction.no_autoflush:
        preloaded_task = transaction.get(T_GrantFeeTask, command.grant_fee_task_id)
        if preloaded_task is None:
            _grant_review_error(
                "GRANT_OFFICIAL_FEE_REVIEW_TASK_NOT_FOUND",
                "授权费用任务不存在",
                status_code=404,
            )
        existing = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == preloaded_task.case_id,
                CaseActivityEvent.idempotency_key == command.idempotency_key,
            )
        )
        if existing is not None:
            _precheck_existing_grant_review(command, existing)
        task, activity, case, obligation, lines, _payload, evidence_refs = _grant_review_context(
            command,
            transaction,
        )
        if existing is not None:
            return _replay_grant_official_fee_review(
                command,
                transaction,
                existing=existing,
                task=task,
                case=case,
                obligation=obligation,
                lines=lines,
                evidence_refs=evidence_refs,
            )
        prior_reviews = _matching_grant_review_activities(
            transaction,
            case_id=task.case_id,
            grant_fee_task_id=task.id,
            obligation_id=obligation.id,
        )
        if prior_reviews:
            _grant_review_state_conflict()
        _validate_grant_instruction_obligation(
            transaction,
            task=task,
            activity=activity,
            expected_lines=_grant_instruction_expected_source(
                transaction,
                task=task,
                activity=activity,
            )[1],
            obligation_id=obligation.id,
        )
        _validate_grant_review_command_lines(command, lines, pre_review=True)
        review_payload = _grant_review_payload(
            command,
            task=task,
            obligation=obligation,
            lines=lines,
        )
        projection = _grant_fee_task_done_projection(case)
        appended = append_case_activity(
            LifecycleEventCommand(
                case_id=case.id,
                event_type=_GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE,
                lane=ActivityLane.FEE,
                effective_at=command.confirmed_at,
                occurred_at=command.confirmed_at,
                evidence_refs=evidence_refs,
                actor_id=command.actor_id,
                reviewer_id=command.actor_id,
                idempotency_key=command.idempotency_key,
                source_activity_id=activity.id,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload=review_payload,
            ),
            transaction,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=case.status,
        )
        by_id = {line.obligation_line_id: line for line in command.lines}
        for line in lines:
            predicates = (
                FeeObligationLine.id == line.id,
                FeeObligationLine.obligation_id == line.obligation_id,
                FeeObligationLine.case_id == line.case_id,
                FeeObligationLine.source_activity_id == line.source_activity_id,
                FeeObligationLine.fee_code == line.fee_code,
                FeeObligationLine.fee_name == line.fee_name,
                FeeObligationLine.fee_year_key == line.fee_year_key,
                FeeObligationLine.current_identity_key == line.current_identity_key,
                FeeObligationLine.reduction_ratio == line.reduction_ratio,
                FeeObligationLine.payable_amount == line.payable_amount,
                FeeObligationLine.source_amount == line.source_amount,
                FeeObligationLine.source_date.is_(None)
                if line.source_date is None
                else FeeObligationLine.source_date == line.source_date,
                cast(FeeObligationLine.updated_at, String)
                == line.updated_at.isoformat(sep=" "),
                FeeObligationLine.official_full_amount.is_(None),
                FeeObligationLine.difference_review_state
                == FeeDifferenceReviewState.REVIEW_REQUIRED.value,
            )
            changed = transaction.execute(
                update(FeeObligationLine)
                .where(*predicates)
                .values(
                    official_full_amount=by_id[line.id].official_full_amount,
                    difference_review_state=FeeDifferenceReviewState.MATCHED.value,
                    updated_by=command.actor_id,
                    updated_at=command.confirmed_at,
                )
                .execution_options(synchronize_session=False)
            )
            if changed.rowcount != 1:
                _grant_review_error(
                    "GRANT_OFFICIAL_FEE_REVIEW_CONCURRENCY_CONFLICT",
                    "授权当年官费人工复核发生并发冲突",
                    status_code=409,
                )
        transaction.flush()
        for line in lines:
            transaction.expire(line)
    return ConfirmGrantOfficialFeesResult(
        grant_fee_task_id=task.id,
        fee_obligation_id=obligation.id,
        source_activity_id=activity.id,
        review_activity_id=appended.activity_id,
        reviewed_line_ids=tuple(line.id for line in lines),
        confirmed_at=command.confirmed_at,
        idempotency_key=command.idempotency_key,
        reused=False,
    )


def validated_grant_year_official_fee_review_for_draft(
    transaction: Session,
    *,
    grant_fee_task_id: str,
) -> tuple[FeeObligation, CaseActivityEvent]:
    if not _valid_review_text(grant_fee_task_id, limit=36):
        _grant_review_command_invalid("grant_fee_task_id")
    task = transaction.get(T_GrantFeeTask, grant_fee_task_id)
    if task is None:
        _grant_review_error(
            "GRANT_OFFICIAL_FEE_REVIEW_TASK_NOT_FOUND",
            "授权费用任务不存在",
            status_code=404,
        )
    task_reviews = tuple(
        candidate
        for candidate in transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == task.case_id,
                CaseActivityEvent.activity_type == _GRANT_OFFICIAL_FEE_REVIEW_EVENT_TYPE,
            )
        )
        if _stored_review_targets_task(candidate, task.id)
    )
    if len(task_reviews) != 1:
        _grant_review_state_conflict()
    review = task_reviews[0]
    try:
        payload = json.loads(review.payload_json)
    except (TypeError, ValueError):
        _grant_review_lineage_conflict()
    if (
        type(payload) is not dict
        or set(payload) != _GRANT_OFFICIAL_FEE_REVIEW_PAYLOAD_KEYS
        or payload.get("schema") != _GRANT_OFFICIAL_FEE_REVIEW_SCHEMA
        or payload.get("grant_fee_task_id") != task.id
        or _canonical_review_payload(payload) != review.payload_json
    ):
        _grant_review_lineage_conflict()
    matching_reviews = _matching_grant_review_activities(
        transaction,
        case_id=task.case_id,
        grant_fee_task_id=task.id,
        obligation_id=payload["obligation_id"],
    )
    if len(matching_reviews) != 1 or matching_reviews[0].id != review.id:
        _grant_review_lineage_conflict()
    after_lines = payload.get("after_lines")
    if type(after_lines) is not list or not after_lines:
        _grant_review_lineage_conflict()
    try:
        command_lines = tuple(
            GrantOfficialFeeReviewLineInput(
                obligation_line_id=item["obligation_line_id"],
                official_full_amount=Decimal(item["official_full_amount"]),
                confirmed_payable_amount=Decimal(item["payable_amount"]),
            )
            for item in after_lines
            if type(item) is dict and set(item) == _GRANT_OFFICIAL_FEE_REVIEW_LINE_KEYS
        )
        command = ConfirmGrantOfficialFeesCommand(
            grant_fee_task_id=task.id,
            source_activity_id=payload["source_activity_id"],
            obligation_id=payload["obligation_id"],
            reviewed_evidence_version_id=payload["reviewed_evidence_version_id"],
            expected_content_hash=payload["reviewed_evidence_content_hash"],
            confirmed_at=datetime.fromisoformat(payload["confirmed_at"]),
            actor_id=review.actor_id,
            idempotency_key=review.idempotency_key,
            lines=command_lines,
        )
    except (InvalidOperation, TypeError, ValueError, KeyError):
        _grant_review_lineage_conflict()
    if len(command_lines) != len(after_lines):
        _grant_review_lineage_conflict()
    _validate_grant_review_command(command)
    (
        context_task,
        _source,
        case,
        obligation,
        lines,
        _source_payload,
        evidence_refs,
    ) = _grant_review_context(command, transaction)
    if context_task.id != task.id:
        _grant_review_lineage_conflict()
    _replay_grant_official_fee_review(
        command,
        transaction,
        existing=review,
        task=task,
        case=case,
        obligation=obligation,
        lines=lines,
        evidence_refs=evidence_refs,
    )
    return obligation, review


def _stored_review_targets_task(activity: CaseActivityEvent, task_id: str) -> bool:
    try:
        payload = json.loads(activity.payload_json)
    except (TypeError, ValueError):
        _grant_review_lineage_conflict()
    if type(payload) is not dict:
        _grant_review_lineage_conflict()
    return payload.get("grant_fee_task_id") == task_id


def recognize_grant_year_annuity_obligation(
    command: RecognizeGrantYearAnnuityObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    _validate_grant_year_annuity_command(command, transaction)

    with transaction.no_autoflush:
        task = transaction.get(T_GrantFeeTask, command.grant_fee_task_id)
        if task is None:
            raise_business_error(
                "GRANT_FEE_TASK_NOT_FOUND",
                "未找到授权费用任务",
                status_code=404,
            )
        activity = transaction.get(CaseActivityEvent, command.source_activity_id)
        if activity is None:
            _grant_year_annuity_source_conflict("activity_missing")
        if (
            task.type != "GRANT"
            or type(task.case_id) is not str
            or not task.case_id
            or task.source_document_id is None
            or type(task.due_date) is not date
            or not _exact_grant_notice_text(task.deadline_source, max_length=32)
            or type(task.deadline_confirmed_at) is not datetime
            or task.deadline_confirmed_at.tzinfo is not None
            or activity.case_id != task.case_id
            or activity.activity_type != _GRANT_NOTICE_EVENT_TYPE
            or activity.lane != ActivityLane.LIFECYCLE.value
            or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        ):
            _grant_year_annuity_source_conflict("task_activity_mismatch")

        try:
            preliminary_payload = _grant_notice_payload(activity.payload_json)
            _reject_empty_grant_year_annuity_snapshot(preliminary_payload)
        except BusinessError as exc:
            if exc.code == "GRANT_YEAR_ANNUITY_FEE_LINE_CONFLICT":
                raise
            _grant_year_annuity_source_conflict("stored_notice_invalid")
        try:
            payload, _ = _validated_stored_grant_notice(
                transaction,
                activity=activity,
                task=task,
            )
        except BusinessError:
            _grant_year_annuity_source_conflict("stored_notice_invalid")

        document = transaction.get(Document, task.source_document_id)
        evidence_id = payload["reviewed_evidence_version_id"]
        evidence = transaction.get(DocumentEvidenceVersion, evidence_id)
        if (
            document is None
            or evidence is None
            or document.id != payload["source_document_id"]
            or document.case_id != task.case_id
            or evidence.case_id != task.case_id
            or evidence.document_id != document.id
            or evidence.id != evidence_id
            or evidence.content_hash != payload["reviewed_evidence_content_hash"]
            or payload["case_id"] != task.case_id
            or payload["grant_fee_task_id"] != task.id
            or payload["due_date"] != task.due_date.isoformat()
            or payload["deadline_source"] != task.deadline_source
            or payload["deadline_confirmed_at"] != task.deadline_confirmed_at.isoformat()
        ):
            _grant_year_annuity_source_conflict("bound_source_mismatch")

        case = transaction.get(Case, task.case_id)
        if case is None:
            _grant_year_annuity_source_conflict("case_missing")
        fee_code = {
            "INV": "CN_ANNUITY_FEE_INV",
            "UM": "CN_ANNUITY_FEE_UM",
            "DES": "CN_ANNUITY_FEE_DES",
        }.get(case.patent_category)
        if fee_code is None:
            raise_business_error(
                "GRANT_YEAR_ANNUITY_PATENT_CATEGORY_UNSUPPORTED",
                "案件专利类型不支持授权当年年费识别",
                status_code=409,
            )

        lines = _grant_year_annuity_lines(payload, fee_code=fee_code)
        supersedes_obligation_id, supersede_reason = _grant_year_annuity_predecessor(
            transaction,
            task=task,
            activity=activity,
            payload=payload,
            fee_code=fee_code,
        )

    return recognize_obligation(
        RecognizeFeeObligationCommand(
            case_id=task.case_id,
            source_activity_id=activity.id,
            source_document_id=document.id,
            fee_domain=FeeDomain.GOV,
            obligation_type="GRANT_YEAR_ANNUITY",
            due_date=task.due_date,
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED,
            lines=lines,
            actor_id=command.actor_id,
            idempotency_key=command.idempotency_key,
            supersedes_obligation_id=supersedes_obligation_id,
            supersede_reason=supersede_reason,
        ),
        transaction,
    )


def _grant_year_annuity_command_invalid(field: str) -> None:
    raise_business_error(
        "GRANT_YEAR_ANNUITY_COMMAND_INVALID",
        "授权当年年费识别命令无效",
        details={"field": field},
        status_code=400,
    )


def _grant_year_annuity_source_conflict(reason: str) -> None:
    raise_business_error(
        "GRANT_YEAR_ANNUITY_SOURCE_LINEAGE_CONFLICT",
        "授权当年年费来源谱系不一致",
        details={"reason": reason},
        status_code=409,
    )


def _grant_year_annuity_line_conflict(reason: str) -> None:
    raise_business_error(
        "GRANT_YEAR_ANNUITY_FEE_LINE_CONFLICT",
        "授权当年年费明细不一致",
        details={"reason": reason},
        status_code=409,
    )


def _grant_year_annuity_predecessor_conflict(reason: str) -> None:
    raise_business_error(
        "GRANT_YEAR_ANNUITY_PREDECESSOR_CONFLICT",
        "授权当年年费更正谱系不一致",
        details={"reason": reason},
        status_code=409,
    )


def _validate_grant_year_annuity_command(
    command: object,
    transaction: object,
) -> None:
    if type(command) is not RecognizeGrantYearAnnuityObligationCommand:
        _grant_year_annuity_command_invalid("command")
    for field, limit in (
        ("grant_fee_task_id", 36),
        ("source_activity_id", 36),
        ("actor_id", 36),
        ("idempotency_key", 128),
    ):
        value = getattr(command, field)
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or "\x00" in value
            or len(value) > limit
        ):
            _grant_year_annuity_command_invalid(field)
    if not isinstance(transaction, Session):
        _grant_year_annuity_command_invalid("transaction")


def _grant_year_annuity_lines(
    payload: dict[str, object],
    *,
    fee_code: str,
) -> tuple[FeeObligationLineInput, ...]:
    snapshot = payload["grant_fee_lines_snapshot"]
    snapshot_hash = payload["grant_fee_lines_snapshot_hash"]
    if (
        type(snapshot) is not str
        or type(snapshot_hash) is not str
        or _GRANT_NOTICE_SNAPSHOT_HASH_PATTERN.fullmatch(snapshot_hash) is None
        or hashlib.sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        _grant_year_annuity_source_conflict("snapshot_hash_mismatch")
    try:
        parsed = json.loads(snapshot)
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _grant_year_annuity_source_conflict("snapshot_invalid")
    if (
        canonical != snapshot
        or type(parsed) is not dict
        or set(parsed)
        != {
            "schema",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "lines",
        }
        or parsed["schema"] != _GRANT_NOTICE_FEE_LINES_SCHEMA
        or parsed["schema"] != payload["grant_fee_lines_schema"]
        or parsed["source_document_id"] != payload["source_document_id"]
        or parsed["reviewed_evidence_version_id"] != payload["reviewed_evidence_version_id"]
        or parsed["reviewed_evidence_content_hash"] != payload["reviewed_evidence_content_hash"]
        or type(parsed["lines"]) is not list
        or not parsed["lines"]
    ):
        _grant_year_annuity_source_conflict("snapshot_binding_mismatch")

    projected: list[FeeObligationLineInput] = []
    seen_years: set[int] = set()
    for index, raw in enumerate(parsed["lines"]):
        if type(raw) is not dict or set(raw) != {
            "fee_name",
            "year",
            "amount",
            "reduction_ratio",
        }:
            _grant_year_annuity_line_conflict(f"lines[{index}].shape")
        name = raw["fee_name"]
        year = raw["year"]
        amount_text = raw["amount"]
        ratio_text = raw["reduction_ratio"]
        if (
            type(name) is not str
            or not name
            or name != name.strip()
            or "\x00" in name
            or len(name) > 256
        ):
            _grant_year_annuity_line_conflict(f"lines[{index}].fee_name")
        if type(year) is not int or year <= 0 or year > 2147483647 or year in seen_years:
            _grant_year_annuity_line_conflict(f"lines[{index}].year")
        seen_years.add(year)
        if (
            type(amount_text) is not str
            or _GRANT_NOTICE_CANONICAL_AMOUNT_PATTERN.fullmatch(amount_text) is None
        ):
            _grant_year_annuity_line_conflict(f"lines[{index}].amount")
        try:
            amount = Decimal(amount_text)
        except (InvalidOperation, ValueError):
            _grant_year_annuity_line_conflict(f"lines[{index}].amount")
        if (
            not amount.is_finite()
            or amount <= 0
            or amount > Decimal("9999999999999999.99")
            or max(-amount.as_tuple().exponent, 0) > 2
        ):
            _grant_year_annuity_line_conflict(f"lines[{index}].amount")
        ratios = {
            "0": Decimal("0"),
            "0.7": Decimal("0.7"),
            "0.85": Decimal("0.85"),
        }
        if type(ratio_text) is not str or ratio_text not in ratios:
            _grant_year_annuity_line_conflict(f"lines[{index}].reduction_ratio")
        projected.append(
            FeeObligationLineInput(
                fee_code=fee_code,
                fee_name=name,
                fee_year_key=year,
                official_full_amount=None,
                reduction_ratio=ratios[ratio_text],
                payable_amount=amount,
                source_amount=amount,
                source_date=None,
                difference_review_state=FeeDifferenceReviewState.REVIEW_REQUIRED,
            )
        )
    return tuple(projected)


def _reject_empty_grant_year_annuity_snapshot(payload: dict[str, object]) -> None:
    snapshot = payload["grant_fee_lines_snapshot"]
    snapshot_hash = payload["grant_fee_lines_snapshot_hash"]
    if (
        type(snapshot) is not str
        or type(snapshot_hash) is not str
        or _GRANT_NOTICE_SNAPSHOT_HASH_PATTERN.fullmatch(snapshot_hash) is None
        or hashlib.sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        _grant_year_annuity_source_conflict("snapshot_hash_mismatch")
    try:
        parsed = json.loads(snapshot)
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _grant_year_annuity_source_conflict("snapshot_invalid")
    if (
        canonical != snapshot
        or type(parsed) is not dict
        or set(parsed)
        != {
            "schema",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "lines",
        }
        or parsed["schema"] != _GRANT_NOTICE_FEE_LINES_SCHEMA
        or parsed["schema"] != payload["grant_fee_lines_schema"]
        or parsed["source_document_id"] != payload["source_document_id"]
        or parsed["reviewed_evidence_version_id"] != payload["reviewed_evidence_version_id"]
        or parsed["reviewed_evidence_content_hash"] != payload["reviewed_evidence_content_hash"]
        or type(parsed["lines"]) is not list
    ):
        _grant_year_annuity_source_conflict("snapshot_binding_mismatch")
    if not parsed["lines"]:
        _grant_year_annuity_line_conflict("lines")


def _grant_year_annuity_predecessor(
    transaction: Session,
    *,
    task: T_GrantFeeTask,
    activity: CaseActivityEvent,
    payload: dict[str, object],
    fee_code: str,
) -> tuple[str | None, str | None]:
    predecessors = tuple(
        transaction.scalars(
            select(T_GrantFeeTask)
            .where(T_GrantFeeTask.superseded_by_task_id == task.id)
            .order_by(T_GrantFeeTask.id)
        ).all()
    )
    payload_task_id = payload["predecessor_grant_fee_task_id"]
    payload_activity_id = payload["supersedes_activity_id"]
    if payload_task_id is None:
        if (
            predecessors
            or payload_activity_id is not None
            or activity.supersedes_event_id is not None
        ):
            _grant_year_annuity_predecessor_conflict("partial_original_lineage")
        return None, None
    if (
        len(predecessors) != 1
        or predecessors[0].id != payload_task_id
        or type(payload_activity_id) is not str
        or activity.supersedes_event_id != payload_activity_id
    ):
        _grant_year_annuity_predecessor_conflict("direct_predecessor_mismatch")
    predecessor_task = predecessors[0]
    predecessor_activity = transaction.get(CaseActivityEvent, payload_activity_id)
    if (
        predecessor_task.case_id != task.case_id
        or predecessor_activity is None
        or predecessor_activity.case_id != task.case_id
        or predecessor_activity.id != activity.supersedes_event_id
    ):
        _grant_year_annuity_predecessor_conflict("cross_case_predecessor")
    try:
        predecessor_payload, _ = _validated_stored_grant_notice(
            transaction,
            activity=predecessor_activity,
            task=predecessor_task,
        )
    except BusinessError:
        _grant_year_annuity_predecessor_conflict("predecessor_source_invalid")
    if (
        predecessor_payload["grant_fee_task_id"] != predecessor_task.id
        or predecessor_payload["case_id"] != task.case_id
    ):
        _grant_year_annuity_predecessor_conflict("predecessor_source_mismatch")
    predecessor_document = transaction.get(
        Document,
        predecessor_task.source_document_id,
    )
    predecessor_evidence = transaction.get(
        DocumentEvidenceVersion,
        predecessor_payload["reviewed_evidence_version_id"],
    )
    if (
        predecessor_task.type != "GRANT"
        or predecessor_task.superseded_by_task_id != task.id
        or predecessor_document is None
        or predecessor_evidence is None
        or predecessor_document.id != predecessor_payload["source_document_id"]
        or predecessor_document.case_id != task.case_id
        or predecessor_evidence.case_id != task.case_id
        or predecessor_evidence.document_id != predecessor_document.id
        or predecessor_evidence.id != predecessor_payload["reviewed_evidence_version_id"]
        or predecessor_evidence.content_hash
        != predecessor_payload["reviewed_evidence_content_hash"]
    ):
        _grant_year_annuity_predecessor_conflict("predecessor_bound_source_mismatch")

    obligations = tuple(
        transaction.scalars(
            select(FeeObligation)
            .where(
                FeeObligation.case_id == task.case_id,
                FeeObligation.source_activity_id == predecessor_activity.id,
                FeeObligation.obligation_type == "GRANT_YEAR_ANNUITY",
            )
            .order_by(FeeObligation.id)
        ).all()
    )
    if len(obligations) != 1:
        _grant_year_annuity_predecessor_conflict("predecessor_obligation_multiplicity")
    prior = obligations[0]
    expected_lines = _grant_year_annuity_lines(predecessor_payload, fee_code=fee_code)
    stored_lines = tuple(
        transaction.scalars(
            select(FeeObligationLine)
            .where(FeeObligationLine.obligation_id == prior.id)
            .order_by(FeeObligationLine.fee_year_key, FeeObligationLine.id)
        ).all()
    )
    children = tuple(
        transaction.scalars(
            select(FeeObligation)
            .where(FeeObligation.supersedes_obligation_id == prior.id)
            .order_by(FeeObligation.id)
        ).all()
    )
    if len(children) > 1 or (children and children[0].source_activity_id != activity.id):
        _grant_year_annuity_predecessor_conflict("predecessor_already_diverged")
    expected_status = (
        FeeObligationStatus.SUPERSEDED.value if children else FeeObligationStatus.RECOGNIZED.value
    )
    expected_by_year = {line.fee_year_key: line for line in expected_lines}
    if (
        prior.source_document_id != predecessor_task.source_document_id
        or prior.fee_domain != FeeDomain.GOV.value
        or prior.obligation_status != expected_status
        or prior.due_date != predecessor_task.due_date
        or prior.currency != "CNY"
        or prior.source_status != FeeSourceStatus.VERIFIED.value
        or len(stored_lines) != len(expected_lines)
        or set(line.fee_year_key for line in stored_lines) != set(expected_by_year)
    ):
        _grant_year_annuity_predecessor_conflict("predecessor_obligation_source_mismatch")
    for stored in stored_lines:
        expected = expected_by_year[stored.fee_year_key]
        if (
            stored.case_id != task.case_id
            or stored.source_activity_id != predecessor_activity.id
            or stored.fee_code != expected.fee_code
            or stored.fee_name != expected.fee_name
            or stored.official_full_amount is not None
            or stored.reduction_ratio != expected.reduction_ratio
            or stored.payable_amount != expected.payable_amount
            or stored.source_amount != expected.source_amount
            or stored.source_date is not None
            or stored.difference_review_state != expected.difference_review_state.value
            or (children and stored.current_identity_key is not None)
            or (
                not children
                and stored.current_identity_key
                != hashlib.sha256(
                    (
                        f"{stored.case_id}|{stored.source_activity_id}|"
                        f"{stored.fee_code}|{stored.fee_year_key}"
                    ).encode("utf-8")
                ).hexdigest()
            )
        ):
            _grant_year_annuity_predecessor_conflict("predecessor_obligation_line_mismatch")
    return prior.id, "GRANT_REGISTRATION_NOTICE_CORRECTION"


def _grant_notice_invalid() -> None:
    raise_business_error(
        "GRANT_NOTICE_LIFECYCLE_INVALID",
        "办理登记手续通知书生命周期输入无效",
        status_code=400,
    )


def _grant_notice_source_conflict() -> None:
    raise_business_error(
        "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT",
        "办理登记手续通知书生命周期来源不一致",
        status_code=409,
    )


def _grant_notice_hash_conflict() -> None:
    raise_business_error(
        "GRANT_NOTICE_EVIDENCE_HASH_CONFLICT",
        "办理登记手续通知书证据哈希不匹配",
        status_code=409,
    )


def _grant_notice_fee_lines_conflict() -> None:
    raise_business_error(
        "GRANT_NOTICE_FEE_LINES_CONFLICT",
        "办理登记手续通知书费用明细不一致",
        status_code=409,
    )


def _grant_notice_replacement_conflict() -> None:
    raise_business_error(
        "GRANT_NOTICE_REPLACEMENT_LINEAGE_CONFLICT",
        "办理登记手续通知书替换谱系不一致",
        status_code=409,
    )


def _grant_notice_idempotency_conflict() -> None:
    raise_business_error(
        "LIFECYCLE_IDEMPOTENCY_CONFLICT",
        "生命周期幂等键与已存活动冲突",
        status_code=409,
    )


def _exact_grant_notice_text(value: object, *, max_length: int) -> bool:
    return (
        type(value) is str and bool(value) and value == value.strip() and len(value) <= max_length
    )


def _validate_grant_notice_dispatch_input(
    *,
    grant_fee_task_id: object,
    source_document_id: object,
    reviewed_evidence_version_id: object,
    expected_content_hash: object,
    actor_id: object,
    recorded_at: object,
    idempotency_key: object,
) -> None:
    if (
        not _exact_grant_notice_text(grant_fee_task_id, max_length=36)
        or not _exact_grant_notice_text(source_document_id, max_length=36)
        or not _exact_grant_notice_text(reviewed_evidence_version_id, max_length=36)
        or not _exact_grant_notice_text(actor_id, max_length=36)
        or not _exact_grant_notice_text(
            idempotency_key,
            max_length=128 - len(_GRANT_NOTICE_IDEMPOTENCY_PREFIX),
        )
        or type(expected_content_hash) is not str
        or _GRANT_NOTICE_HASH_PATTERN.fullmatch(expected_content_hash) is None
        or type(recorded_at) is not datetime
        or recorded_at.tzinfo is not None
    ):
        _grant_notice_invalid()


def _grant_notice_payload(value: str) -> dict[str, object]:
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        _grant_notice_idempotency_conflict()
    if type(parsed) is not dict or set(parsed) != _GRANT_NOTICE_PAYLOAD_KEYS:
        _grant_notice_idempotency_conflict()
    return parsed


def _grant_notice_stored_date(value: object) -> date:
    if type(value) is not str:
        _grant_notice_idempotency_conflict()
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _grant_notice_idempotency_conflict()
    if parsed.isoformat() != value:
        _grant_notice_idempotency_conflict()
    return parsed


def _grant_notice_stored_datetime(value: object) -> datetime:
    if type(value) is not str:
        _grant_notice_idempotency_conflict()
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        _grant_notice_idempotency_conflict()
    if parsed.tzinfo is not None or parsed.isoformat() != value:
        _grant_notice_idempotency_conflict()
    return parsed


def _validate_grant_notice_stored_snapshot(payload: dict[str, object]) -> None:
    snapshot = payload["grant_fee_lines_snapshot"]
    snapshot_hash = payload["grant_fee_lines_snapshot_hash"]
    if (
        type(snapshot) is not str
        or not snapshot
        or type(snapshot_hash) is not str
        or _GRANT_NOTICE_SNAPSHOT_HASH_PATTERN.fullmatch(snapshot_hash) is None
        or hashlib.sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        _grant_notice_idempotency_conflict()
    try:
        parsed = json.loads(snapshot)
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _grant_notice_idempotency_conflict()
    if (
        type(parsed) is not dict
        or canonical != snapshot
        or set(parsed)
        != {
            "schema",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "lines",
        }
        or parsed["schema"] != payload["grant_fee_lines_schema"]
        or parsed["source_document_id"] != payload["source_document_id"]
        or parsed["reviewed_evidence_version_id"] != payload["reviewed_evidence_version_id"]
        or parsed["reviewed_evidence_content_hash"] != payload["reviewed_evidence_content_hash"]
        or type(parsed["lines"]) is not list
        or not parsed["lines"]
    ):
        _grant_notice_idempotency_conflict()


def _validated_stored_grant_notice(
    transaction: Session,
    *,
    activity: CaseActivityEvent,
    task: T_GrantFeeTask,
) -> tuple[dict[str, object], tuple[EvidenceReference, EvidenceReference]]:
    payload = _grant_notice_payload(activity.payload_json)
    reviewed_at = _grant_notice_stored_datetime(payload["reviewed_at"])
    deadline_confirmed_at = _grant_notice_stored_datetime(payload["deadline_confirmed_at"])
    due_date = _grant_notice_stored_date(payload["due_date"])
    predecessor_task_id = payload["predecessor_grant_fee_task_id"]
    supersedes_activity_id = payload["supersedes_activity_id"]
    if (
        activity.activity_type != _GRANT_NOTICE_EVENT_TYPE
        or activity.lane != ActivityLane.LIFECYCLE.value
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.source_activity_id is not None
        or type(activity.occurred_at) is not datetime
        or activity.occurred_at.tzinfo is not None
        or activity.effective_at != activity.occurred_at
        or not _exact_grant_notice_text(activity.actor_id, max_length=36)
        or not _exact_grant_notice_text(activity.reviewer_id, max_length=36)
        or payload["schema"] != _GRANT_NOTICE_EVENT_SCHEMA
        or payload["case_id"] != activity.case_id
        or payload["grant_fee_task_id"] != task.id
        or payload["source_document_id"] != task.source_document_id
        or not _exact_grant_notice_text(
            payload["reviewed_evidence_version_id"],
            max_length=36,
        )
        or type(payload["reviewed_evidence_content_hash"]) is not str
        or _GRANT_NOTICE_HASH_PATTERN.fullmatch(payload["reviewed_evidence_content_hash"]) is None
        or payload["grant_fee_lines_schema"] != _GRANT_NOTICE_FEE_LINES_SCHEMA
        or due_date != task.due_date
        or payload["deadline_source"] != task.deadline_source
        or not _exact_grant_notice_text(payload["deadline_source"], max_length=32)
        or deadline_confirmed_at != task.deadline_confirmed_at
        or (
            predecessor_task_id is None
            and (supersedes_activity_id is not None or activity.supersedes_event_id is not None)
        )
        or (
            predecessor_task_id is not None
            and (
                not _exact_grant_notice_text(predecessor_task_id, max_length=36)
                or not _exact_grant_notice_text(supersedes_activity_id, max_length=36)
                or activity.supersedes_event_id != supersedes_activity_id
            )
        )
    ):
        _grant_notice_idempotency_conflict()
    _validate_grant_notice_stored_snapshot(payload)
    evidence_refs = _grant_notice_evidence_references(
        transaction,
        activity=activity,
        payload=payload,
    )
    if any(reference.case_id != activity.case_id for reference in evidence_refs):
        _grant_notice_idempotency_conflict()
    if reviewed_at != evidence_refs[0].captured_at:
        _grant_notice_idempotency_conflict()
    return payload, evidence_refs


def _grant_notice_evidence_references(
    transaction: Session,
    *,
    activity: CaseActivityEvent,
    payload: dict[str, object],
) -> tuple[EvidenceReference, EvidenceReference]:
    rows = list(
        transaction.scalars(
            select(CaseActivityEventEvidence)
            .where(
                CaseActivityEventEvidence.case_id == activity.case_id,
                CaseActivityEventEvidence.activity_id == activity.id,
            )
            .order_by(
                CaseActivityEventEvidence.evidence_kind.asc(),
                CaseActivityEventEvidence.id.asc(),
            )
        ).all()
    )
    if len(rows) != 2:
        _grant_notice_idempotency_conflict()
    by_kind = {row.evidence_kind: row for row in rows}
    if set(by_kind) != {"SOURCE_DOCUMENT", "DOCUMENT_EVIDENCE_VERSION"}:
        _grant_notice_idempotency_conflict()
    source = by_kind["SOURCE_DOCUMENT"]
    evidence = by_kind["DOCUMENT_EVIDENCE_VERSION"]
    expected_reviewed_at = _grant_notice_stored_datetime(payload["reviewed_at"])
    if (
        source.object_type != "Document"
        or source.object_id != payload["source_document_id"]
        or evidence.object_type != "DocumentEvidenceVersion"
        or evidence.object_id != payload["reviewed_evidence_version_id"]
        or source.content_hash != payload["reviewed_evidence_content_hash"]
        or evidence.content_hash != payload["reviewed_evidence_content_hash"]
        or source.captured_at != expected_reviewed_at
        or evidence.captured_at != expected_reviewed_at
    ):
        _grant_notice_idempotency_conflict()
    return (
        EvidenceReference(
            case_id=source.case_id,
            evidence_kind=source.evidence_kind,
            object_type=source.object_type,
            object_id=source.object_id,
            content_hash=source.content_hash,
            captured_at=source.captured_at,
        ),
        EvidenceReference(
            case_id=evidence.case_id,
            evidence_kind=evidence.evidence_kind,
            object_type=evidence.object_type,
            object_id=evidence.object_id,
            content_hash=evidence.content_hash,
            captured_at=evidence.captured_at,
        ),
    )


def _replay_grant_registration_notice(
    *,
    activity: CaseActivityEvent,
    task: T_GrantFeeTask,
    grant_fee_task_id: str,
    source_document_id: str,
    reviewed_evidence_version_id: str,
    expected_content_hash: str,
    actor_id: str,
    recorded_at: datetime,
    transaction: Session,
) -> LifecycleTransitionResult:
    payload, evidence_refs = _validated_stored_grant_notice(
        transaction,
        activity=activity,
        task=task,
    )
    if (
        activity.occurred_at != recorded_at
        or activity.effective_at != recorded_at
        or activity.actor_id != actor_id
        or payload["grant_fee_task_id"] != grant_fee_task_id
        or payload["source_document_id"] != source_document_id
        or payload["reviewed_evidence_version_id"] != reviewed_evidence_version_id
        or payload["reviewed_evidence_content_hash"] != expected_content_hash
    ):
        _grant_notice_idempotency_conflict()
    return apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=activity.case_id,
            event_type=_GRANT_NOTICE_EVENT_TYPE,
            lane=ActivityLane.LIFECYCLE,
            effective_at=activity.effective_at,
            occurred_at=activity.occurred_at,
            evidence_refs=evidence_refs,
            actor_id=activity.actor_id,
            reviewer_id=activity.reviewer_id,
            idempotency_key=activity.idempotency_key,
            source_activity_id=activity.source_activity_id,
            supersedes_event_id=activity.supersedes_event_id,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=payload,
        ),
        transaction,
    )


def _grant_notice_predecessor(
    transaction: Session,
    *,
    task: T_GrantFeeTask,
) -> tuple[T_GrantFeeTask | None, CaseActivityEvent | None]:
    if task.superseded_by_task_id is not None:
        _grant_notice_replacement_conflict()
    predecessors = list(
        transaction.scalars(
            select(T_GrantFeeTask)
            .where(T_GrantFeeTask.superseded_by_task_id == task.id)
            .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
        ).all()
    )
    if not predecessors:
        return None, None
    if len(predecessors) != 1:
        _grant_notice_replacement_conflict()
    predecessor = predecessors[0]
    if predecessor.id == task.id or predecessor.case_id != task.case_id:
        _grant_notice_replacement_conflict()

    candidate_activities = list(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(
                CaseActivityEvent.case_id == task.case_id,
                CaseActivityEvent.activity_type == _GRANT_NOTICE_EVENT_TYPE,
            )
            .order_by(CaseActivityEvent.sequence.asc(), CaseActivityEvent.id.asc())
        ).all()
    )
    matching: list[CaseActivityEvent] = []
    for activity in candidate_activities:
        try:
            payload = json.loads(activity.payload_json)
        except (TypeError, ValueError):
            continue
        if type(payload) is dict and payload.get("grant_fee_task_id") == predecessor.id:
            matching.append(activity)
    if len(matching) != 1:
        _grant_notice_replacement_conflict()
    predecessor_activity = matching[0]
    try:
        predecessor_payload, _ = _validated_stored_grant_notice(
            transaction,
            activity=predecessor_activity,
            task=predecessor,
        )
    except BusinessError:
        _grant_notice_replacement_conflict()
    if (
        predecessor_payload["grant_fee_task_id"] != predecessor.id
        or predecessor_payload["case_id"] != task.case_id
    ):
        _grant_notice_replacement_conflict()
    return predecessor, predecessor_activity


def dispatch_grant_registration_notice(
    *,
    grant_fee_task_id: str,
    source_document_id: str,
    reviewed_evidence_version_id: str,
    expected_content_hash: str,
    actor_id: str,
    recorded_at: datetime,
    idempotency_key: str,
    transaction: Session,
) -> LifecycleTransitionResult:
    _validate_grant_notice_dispatch_input(
        grant_fee_task_id=grant_fee_task_id,
        source_document_id=source_document_id,
        reviewed_evidence_version_id=reviewed_evidence_version_id,
        expected_content_hash=expected_content_hash,
        actor_id=actor_id,
        recorded_at=recorded_at,
        idempotency_key=idempotency_key,
    )
    if not isinstance(transaction, Session):
        _grant_notice_invalid()
    prefixed_idempotency_key = f"{_GRANT_NOTICE_IDEMPOTENCY_PREFIX}{idempotency_key}"

    with transaction.no_autoflush:
        task = transaction.get(T_GrantFeeTask, grant_fee_task_id)
        if task is None:
            raise_business_error(
                "GRANT_FEE_TASK_NOT_FOUND",
                "未找到授权费用任务",
                status_code=404,
            )
        existing = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == task.case_id,
                CaseActivityEvent.idempotency_key == prefixed_idempotency_key,
            )
        )
        if existing is not None:
            return _replay_grant_registration_notice(
                activity=existing,
                task=task,
                grant_fee_task_id=grant_fee_task_id,
                source_document_id=source_document_id,
                reviewed_evidence_version_id=reviewed_evidence_version_id,
                expected_content_hash=expected_content_hash,
                actor_id=actor_id,
                recorded_at=recorded_at,
                transaction=transaction,
            )

        document = transaction.get(Document, source_document_id)
        if document is None:
            raise_business_error(
                "DOCUMENT_NOT_FOUND",
                "未找到文书",
                status_code=404,
            )
        evidence = transaction.get(
            DocumentEvidenceVersion,
            reviewed_evidence_version_id,
        )
        if evidence is None:
            raise_business_error(
                "EVIDENCE_VERSION_NOT_FOUND",
                "未找到证据版本",
                status_code=404,
            )
        case = transaction.get(Case, task.case_id)
        if case is None:
            raise_business_error("CASE_NOT_FOUND", "未找到案件", status_code=404)

        template = (
            transaction.get(DocTemplate, document.doc_template_id)
            if document.doc_template_id
            else None
        )
        try:
            semantics = resolve_document_semantics(template)
        except BusinessError:
            _grant_notice_source_conflict()
        if (
            task.type != "GRANT"
            or task.case_id != document.case_id
            or task.source_document_id != document.id
            or type(task.due_date) is not date
            or not _exact_grant_notice_text(task.deadline_source, max_length=32)
            or type(task.deadline_confirmed_at) is not datetime
            or task.deadline_confirmed_at.tzinfo is not None
            or document.direction != DocumentDirection.IN.value
            or semantics.catalog_status != "EXECUTABLE"
            or semantics.execution_behavior != "GRANT_NOTICE"
            or semantics.lifecycle_event_type != _GRANT_NOTICE_EVENT_TYPE
        ):
            _grant_notice_source_conflict()

        current_identity = f"{task.case_id}|{evidence.lineage_key}"
        current_versions = list(
            transaction.scalars(
                select(DocumentEvidenceVersion).where(
                    DocumentEvidenceVersion.current_identity_key == current_identity
                )
            ).all()
        )
        if (
            evidence.case_id != task.case_id
            or evidence.document_id != document.id
            or evidence.current_identity_key != current_identity
            or len(current_versions) != 1
            or current_versions[0].id != evidence.id
            or evidence.state != "FINAL"
            or evidence.review_state != "APPROVED"
            or not _exact_grant_notice_text(evidence.reviewer_id, max_length=36)
            or type(evidence.reviewed_at) is not datetime
            or evidence.reviewed_at.tzinfo is not None
        ):
            _grant_notice_source_conflict()
        if evidence.content_hash != expected_content_hash:
            _grant_notice_hash_conflict()

        predecessor, predecessor_activity = _grant_notice_predecessor(
            transaction,
            task=task,
        )
        try:
            snapshot = extract_grant_notice_fee_line_snapshot(
                document=document,
                reviewed_evidence_version_id=reviewed_evidence_version_id,
                expected_evidence_content_hash=expected_content_hash,
            )
        except DocumentExtraDataError:
            _grant_notice_fee_lines_conflict()
        if (
            type(snapshot) is not GrantNoticeFeeLineSnapshot
            or snapshot.schema != _GRANT_NOTICE_FEE_LINES_SCHEMA
            or snapshot.source_document_id != document.id
            or snapshot.reviewed_evidence_version_id != evidence.id
            or snapshot.reviewed_evidence_content_hash != evidence.content_hash
            or type(snapshot.lines) is not tuple
            or type(snapshot.canonical_json) is not str
            or not snapshot.canonical_json
            or type(snapshot.snapshot_hash) is not str
            or _GRANT_NOTICE_SNAPSHOT_HASH_PATTERN.fullmatch(snapshot.snapshot_hash) is None
        ):
            _grant_notice_fee_lines_conflict()

    payload = {
        "schema": _GRANT_NOTICE_EVENT_SCHEMA,
        "case_id": task.case_id,
        "grant_fee_task_id": task.id,
        "source_document_id": document.id,
        "reviewed_evidence_version_id": evidence.id,
        "reviewed_evidence_content_hash": evidence.content_hash,
        "reviewed_at": evidence.reviewed_at.isoformat(),
        "grant_fee_lines_schema": snapshot.schema,
        "grant_fee_lines_snapshot": snapshot.canonical_json,
        "grant_fee_lines_snapshot_hash": snapshot.snapshot_hash,
        "due_date": task.due_date.isoformat(),
        "deadline_source": task.deadline_source,
        "deadline_confirmed_at": task.deadline_confirmed_at.isoformat(),
        "predecessor_grant_fee_task_id": predecessor.id if predecessor else None,
        "supersedes_activity_id": predecessor_activity.id if predecessor_activity else None,
    }
    return apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=task.case_id,
            event_type=_GRANT_NOTICE_EVENT_TYPE,
            lane=ActivityLane.LIFECYCLE,
            effective_at=recorded_at,
            occurred_at=recorded_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=task.case_id,
                    evidence_kind="SOURCE_DOCUMENT",
                    object_type="Document",
                    object_id=document.id,
                    content_hash=evidence.content_hash,
                    captured_at=evidence.reviewed_at,
                ),
                EvidenceReference(
                    case_id=task.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=evidence.id,
                    content_hash=evidence.content_hash,
                    captured_at=evidence.reviewed_at,
                ),
            ),
            actor_id=actor_id,
            reviewer_id=evidence.reviewer_id,
            idempotency_key=prefixed_idempotency_key,
            source_activity_id=None,
            supersedes_event_id=(predecessor_activity.id if predecessor_activity else None),
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=payload,
        ),
        transaction,
    )


def get_grant_fee_module_contract() -> dict[str, object]:
    return {
        "module": "grant_fees",
        "permission_namespace": "GrantFeeTask",
        "permission_codes": list(GRANT_FEE_TASK_PERMISSION_CODES),
        "status": "ok",
    }


def list_grant_fee_tasks(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> dict[str, Any]:
    stmt = select(T_GrantFeeTask)
    predicates = []

    case_id = str(filters.get("case_id") or "").strip()
    if case_id:
        predicates.append(T_GrantFeeTask.case_id == case_id)

    case_no = str(filters.get("case_no") or "").strip()
    if case_no:
        stmt = stmt.join(Case, Case.id == T_GrantFeeTask.case_id)
        predicates.append(Case.case_no == case_no)

    client_instruction = str(filters.get("client_instruction") or "").strip().upper()
    if client_instruction:
        predicates.append(T_GrantFeeTask.client_instruction == client_instruction)

    if filters.get("draft_generated") is not None:
        predicates.append(T_GrantFeeTask.draft_generated.is_(bool(filters["draft_generated"])))

    if filters.get("is_overdue") is not None:
        predicates.append(T_GrantFeeTask.is_overdue.is_(bool(filters["is_overdue"])))

    date_from = filters.get("date_from")
    if date_from is not None:
        predicates.append(T_GrantFeeTask.due_date >= date_from)

    date_to = filters.get("date_to")
    if date_to is not None:
        predicates.append(T_GrantFeeTask.due_date <= date_to)

    if predicates:
        stmt = stmt.where(and_(*predicates))

    stmt = stmt.order_by(T_GrantFeeTask.due_date.asc(), T_GrantFeeTask.id.asc())

    tasks = list(db.execute(stmt).scalars().all())
    case_no_map = _build_grant_fee_task_case_no_map(db, tasks=tasks)
    bill_visibility_map = _build_grant_fee_bill_visibility_map(db, tasks=tasks)
    projected_items = []
    status_filter = str(filters.get("status") or "").strip().upper()

    for task in tasks:
        status = derive_grant_fee_task_state(task)
        if status_filter and status != status_filter:
            continue
        projected_items.append(
            _serialize_grant_fee_task_list_item(
                task,
                state=status,
                case_no=case_no_map.get(task.case_id),
                bill_visibility=bill_visibility_map.get(
                    task.id,
                    {"billed": False, "linked_bill_id": None, "linked_bill_no": None},
                ),
            )
        )

    total = len(projected_items)
    safe_page = max(int(page or 1), 1)
    safe_page_size = max(int(page_size or 20), 1)
    start = (safe_page - 1) * safe_page_size
    end = start + safe_page_size
    return {
        "items": projected_items[start:end],
        "page": safe_page,
        "page_size": safe_page_size,
        "total": total,
    }


def _load_grant_fee_task(db: Session, *, task_id: str) -> T_GrantFeeTask:
    task = db.execute(
        select(T_GrantFeeTask).where(T_GrantFeeTask.id == task_id)
    ).scalar_one_or_none()
    if task is None:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND", "Grant fee task not found", status_code=404
        )
    return task


def _normalize_action(action: Any) -> str:
    return str(action or "").strip()


def _apply_grant_fee_task_mutation(task: T_GrantFeeTask, *, normalized_action: str) -> None:
    if normalized_action == "mark_waiting_client":
        task.notice_sent = True
        task.client_instruction = "NONE"
        task.notify_count = 1
        task.draft_generated = False
    elif normalized_action == "record_pay_instruction":
        task.client_instruction = "PAY"
        task.notify_count = 2
    elif normalized_action == "record_abandon_instruction":
        task.client_instruction = "ABANDON"
        task.notify_count = 4
    elif normalized_action == "mark_draft_generated":
        task.draft_generated = True
        task.notify_count = 3
    elif normalized_action == "mark_done":
        task.notify_count = 4


def _draft_marker(task_id: str) -> str:
    return f"{GRANT_FEE_DRAFT_MARKER_PREFIX}{task_id}"


def _find_existing_grant_fee_draft(db: Session, *, marker: str) -> FeeDraft | None:
    stmt = (
        select(FeeDraft)
        .where(
            FeeDraft.draft_type == GRANT_FEE_DRAFT_TYPE,
            FeeDraft.id.in_(select(FeeItem.draft_id).where(FeeItem.remark == marker)),
        )
        .order_by(FeeDraft.created_at.asc(), FeeDraft.id.asc())
    )
    return db.execute(stmt).scalars().first()


def _count_fee_items_for_draft(db: Session, *, draft_id: str) -> int:
    return len(db.execute(select(FeeItem).where(FeeItem.draft_id == draft_id)).scalars().all())


def _money_amount(value: Any) -> Decimal:
    if value is None or value == "":
        return _ZERO
    try:
        return Decimal(str(value)).quantize(_MONEY_QUANT)
    except (InvalidOperation, ValueError):
        return _ZERO


def _tiered_rate_amount(rate: FeeRate, year_no: int | None) -> Decimal:
    default_amount = _money_amount(rate.default_amount)
    if year_no is None or (rate.calc_mode or "").strip().upper() != "TIER":
        return default_amount

    try:
        parsed_params = json.loads(rate.calc_params or "{}")
    except (TypeError, ValueError):
        return default_amount

    if not isinstance(parsed_params, dict):
        return default_amount

    tiers = parsed_params.get("tiers")
    if not isinstance(tiers, list):
        return default_amount

    for tier in tiers:
        if not isinstance(tier, dict):
            continue
        try:
            start_year = int(tier.get("from"))
            end_year = int(tier.get("to", start_year))
        except (TypeError, ValueError):
            continue
        if start_year <= year_no <= end_year:
            return _money_amount(tier.get("amount", default_amount))

    return default_amount


def _select_matching_gov_rate(
    db: Session,
    *,
    rate_group: str,
    currency: str,
    patent_category: str | None,
) -> FeeRate | None:
    normalized_patent_category = (patent_category or "").strip() or None
    conditions = [
        FeeRate.enabled.is_(True),
        FeeRate.fee_type == "GOV",
        FeeRate.currency == currency,
        FeeRate.rate_group == rate_group,
        fee_rate_source_enabled_condition(),
        *fee_rate_effective_on_conditions(date.today()),
    ]
    if normalized_patent_category:
        conditions.append(
            or_(
                FeeRate.patent_category == normalized_patent_category,
                FeeRate.patent_category.is_(None),
                FeeRate.patent_category == "",
            )
        )

    rates = (
        db.execute(select(FeeRate).where(*conditions).order_by(FeeRate.updated_at.desc()))
        .scalars()
        .all()
    )
    if not rates:
        return None

    if normalized_patent_category:
        for rate in rates:
            if rate.patent_category == normalized_patent_category:
                return rate
        for rate in rates:
            if not rate.patent_category:
                return rate
        return None

    return rates[0]


def _resolve_grant_task_gov_amount(db: Session, *, case: Case | None, currency: str) -> Decimal:
    if case is None:
        return _ZERO

    grant_rate = _select_matching_gov_rate(
        db,
        rate_group="GRANT",
        currency=currency,
        patent_category=case.patent_category,
    )
    if grant_rate is not None:
        return _tiered_rate_amount(grant_rate, None)

    annuity_rate = _select_matching_gov_rate(
        db,
        rate_group="ANNUITY",
        currency=currency,
        patent_category=case.patent_category,
    )
    return _tiered_rate_amount(annuity_rate, case.first_annuity_year) if annuity_rate else _ZERO


def derive_grant_fee_task_state(task: T_GrantFeeTask) -> str:
    notify_count = int(task.notify_count or 0)
    client_instruction = (task.client_instruction or "").strip().upper() or "NONE"

    if notify_count >= 4:
        return "DONE"
    if task.draft_generated:
        return "DRAFT_GENERATED"
    if client_instruction == "PAY":
        return "READY_TO_DRAFT"
    if client_instruction == "ABANDON":
        return "DONE"
    if task.notice_sent or notify_count >= 1:
        return "WAITING_CLIENT"
    return "OPEN"


def _derive_grant_fee_task_lineage_status(task: T_GrantFeeTask) -> str:
    if task.superseded_by_task_id:
        return "SUPERSEDED"
    if task.source_document_id and task.deadline_source and task.deadline_confirmed_at:
        return "CONFIRMED"
    return "LEGACY_UNVERIFIED"


def _require_grant_fee_task_actionable(task: T_GrantFeeTask) -> str:
    lineage_status = _derive_grant_fee_task_lineage_status(task)
    if lineage_status != "CONFIRMED":
        raise_business_error(
            "GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE",
            "Grant fee task lineage is not actionable",
            details={"task_id": task.id, "lineage_status": lineage_status},
            status_code=409,
        )
    return lineage_status


def _grant_fee_task_done_projection(case: Case) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                BusinessStage(case.business_stage) if case.business_stage is not None else None
            ),
            official_procedure_stage=(
                OfficialProcedureStage(case.official_procedure_stage)
                if case.official_procedure_stage is not None
                else None
            ),
            legal_status=LegalStatus(case.legal_status) if case.legal_status is not None else None,
            lifecycle_verification_status=(
                ConfirmationStatus(case.lifecycle_verification_status)
                if case.lifecycle_verification_status is not None
                else None
            ),
        )
    except ValueError:
        raise_business_error(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "案件生命周期投影无效",
            status_code=409,
        )


def _append_grant_fee_task_done_activity(db: Session, *, task: T_GrantFeeTask) -> None:
    case = db.get(Case, task.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "案件不存在", status_code=404)
    actor_id = task.updated_by or task.created_by
    if (
        type(actor_id) is not str
        or not actor_id
        or actor_id != actor_id.strip()
        or len(actor_id) > 36
    ):
        raise_business_error(
            "GRANT_FEE_TASK_DONE_ACTOR_REQUIRED",
            "授权费任务完成活动缺少可追溯操作者",
            status_code=409,
        )
    projection = _grant_fee_task_done_projection(case)
    occurred_at = datetime.now()
    append_case_activity(
        LifecycleEventCommand(
            case_id=case.id,
            event_type=_GRANT_FEE_TASK_DONE_EVENT_TYPE,
            lane=ActivityLane.FEE,
            effective_at=occurred_at,
            occurred_at=occurred_at,
            evidence_refs=(),
            actor_id=actor_id,
            idempotency_key=f"grant-fee-task:{task.id}:done",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={"center_changes": {}},
        ),
        db,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=case.status,
        conflict_codes=(),
    )


def get_grant_fee_task_state(db: Session, *, task_id: str) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    state = derive_grant_fee_task_state(task)
    return _serialize_grant_fee_task_state(task, state=state)


def apply_grant_fee_task_action(
    db: Session,
    *,
    task_id: str,
    action: str,
) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    normalized_action = _normalize_action(action)
    _require_grant_fee_task_actionable(task)

    current_state = derive_grant_fee_task_state(task)
    allowed_actions = _STATE_ALLOWED_ACTIONS[current_state]

    if normalized_action not in allowed_actions:
        raise_business_error(
            "GRANT_FEE_STATE_TRANSITION_INVALID",
            "Invalid grant fee task state transition",
            details={
                "task_id": task_id,
                "from": current_state,
                "action": normalized_action,
                "allowed_actions": list(allowed_actions),
            },
            status_code=400,
        )

    _apply_grant_fee_task_mutation(task, normalized_action=normalized_action)
    if normalized_action == "mark_done":
        try:
            _append_grant_fee_task_done_activity(db, task=task)
            db.commit()
        except Exception:
            db.rollback()
            raise
    else:
        db.commit()
    db.refresh(task)
    return _serialize_grant_fee_task_state(task, state=derive_grant_fee_task_state(task))


def _raise_active_grant_source_conflict(
    active_task: T_GrantFeeTask,
    *,
    requested_source_document_id: str,
) -> None:
    raise_business_error(
        "GRANT_FEE_TASK_ACTIVE_SOURCE_CONFLICT",
        "A different active grant notice source requires explicit replacement",
        details={
            "task_id": active_task.id,
            "active_source_document_id": active_task.source_document_id,
            "requested_source_document_id": requested_source_document_id,
        },
        status_code=409,
    )


def _ensure_sqlite_grant_write_transaction(db: Session) -> None:
    connection = db.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if driver_connection.in_transaction:
        return

    for attempt in range(_SQLITE_LOCK_RETRY_ATTEMPTS + 1):
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            return
        except OperationalError as exc:
            message = str(exc).lower()
            if "database is locked" not in message and "database is busy" not in message:
                raise
            if attempt == _SQLITE_LOCK_RETRY_ATTEMPTS:
                if not driver_connection.in_transaction:
                    connection.exec_driver_sql("BEGIN")
                raise_business_error(
                    "GRANT_FEE_TASK_CONCURRENCY_CONFLICT",
                    "Grant fee task creation is busy; retry the request",
                    status_code=409,
                )
            time.sleep(_SQLITE_LOCK_RETRY_DELAY_SECONDS)


def ensure_grant_fee_task_for_notice_document(
    db: Session,
    *,
    document: Document,
    template: DocTemplate,
    superseding_task_id: str | None = None,
) -> T_GrantFeeTask | None:
    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "GRANT_NOTICE"
        or semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        or semantics.fee_trigger != GRANT_FEE_DRAFT_TYPE
    ):
        return None

    source_document_id = str(document.id or "").strip()
    case_id = str(document.case_id or "").strip()
    if not source_document_id or not case_id:
        raise_business_error(
            "GRANT_FEE_TASK_SOURCE_REQUIRED",
            "Grant fee task requires a persisted source document and case",
            details={
                "source_document_id": source_document_id or None,
                "case_id": case_id or None,
            },
            status_code=409,
        )

    try:
        deadline = parse_document_extra_data(document.extra_data)
    except DocumentExtraDataError as exc:
        raise_business_error(
            "GRANT_OFFICIAL_DUE_DATE_CONFLICT",
            "Executable grant notice requires a consistent official due date tuple",
            details={"field": exc.field, "reason": exc.reason},
            status_code=409,
        )
    if (
        deadline.official_due_date_status != "CONFIRMED"
        or deadline.official_due_date is None
        or deadline.official_due_date_source is None
    ):
        raise_business_error(
            "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
            "Executable grant notice requires a confirmed explicit official due date",
            details={"status": deadline.official_due_date_status},
            status_code=409,
        )

    _ensure_sqlite_grant_write_transaction(db)

    same_source_task = (
        db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.source_document_id == source_document_id)
        )
        .scalars()
        .one_or_none()
    )
    if same_source_task is not None:
        if same_source_task.case_id != case_id:
            raise_business_error(
                "GRANT_FEE_TASK_SOURCE_IDENTITY_CONFLICT",
                "Grant fee task source belongs to a different case",
                details={
                    "task_id": same_source_task.id,
                    "source_document_id": source_document_id,
                    "task_case_id": same_source_task.case_id,
                    "source_case_id": case_id,
                },
                status_code=409,
            )
        return same_source_task

    active_tasks = list(
        db.execute(
            select(T_GrantFeeTask)
            .where(
                T_GrantFeeTask.case_id == case_id,
                T_GrantFeeTask.superseded_by_task_id.is_(None),
            )
            .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
        )
        .scalars()
        .all()
    )
    conflicting_active_tasks = [task for task in active_tasks if task.id != superseding_task_id]
    if conflicting_active_tasks:
        _raise_active_grant_source_conflict(
            conflicting_active_tasks[0],
            requested_source_document_id=source_document_id,
        )

    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    currency = "CNY"
    task = T_GrantFeeTask(
        case_id=case_id,
        source_document_id=source_document_id,
        due_date=deadline.official_due_date,
        deadline_source=deadline.official_due_date_source,
        deadline_confirmed_at=datetime.now(),
        gov_fee_amt=_resolve_grant_task_gov_amount(db, case=case, currency=currency),
        service_fee_amt=0,
        currency=currency,
        client_instruction="NONE",
        notify_count=0,
        draft_generated=False,
        notice_sent=False,
        is_overdue=False,
    )
    try:
        with db.begin_nested():
            db.add(task)
            db.flush()
            competing_tasks = list(
                db.execute(
                    select(T_GrantFeeTask)
                    .where(
                        T_GrantFeeTask.case_id == case_id,
                        T_GrantFeeTask.superseded_by_task_id.is_(None),
                        T_GrantFeeTask.id != task.id,
                        T_GrantFeeTask.id != superseding_task_id,
                    )
                    .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
                )
                .scalars()
                .all()
            )
            if competing_tasks:
                _raise_active_grant_source_conflict(
                    competing_tasks[0],
                    requested_source_document_id=source_document_id,
                )
    except IntegrityError:
        winner = (
            db.execute(
                select(T_GrantFeeTask).where(
                    T_GrantFeeTask.source_document_id == source_document_id
                )
            )
            .scalars()
            .one_or_none()
        )
        if winner is not None and winner.case_id == case_id:
            return winner
        competing_task = (
            db.execute(
                select(T_GrantFeeTask)
                .where(
                    T_GrantFeeTask.case_id == case_id,
                    T_GrantFeeTask.superseded_by_task_id.is_(None),
                )
                .order_by(T_GrantFeeTask.created_at.asc(), T_GrantFeeTask.id.asc())
            )
            .scalars()
            .first()
        )
        if competing_task is not None:
            _raise_active_grant_source_conflict(
                competing_task,
                requested_source_document_id=source_document_id,
            )
        raise_business_error(
            "GRANT_FEE_TASK_SOURCE_IDENTITY_CONFLICT",
            "Grant fee task source identity conflicted during creation",
            details={"source_document_id": source_document_id, "case_id": case_id},
            status_code=409,
        )
    return task


def _normalize_replacement_text(
    value: str | None,
    *,
    field: str,
    max_length: int | None = None,
) -> str:
    normalized = str(value or "").strip()
    if not normalized or (max_length is not None and len(normalized) > max_length):
        raise_business_error(
            "GRANT_REPLACEMENT_INVALID",
            f"{field} is required and must use the supported length",
            details={"field": field, "max_length": max_length},
            status_code=400,
        )
    return normalized


def _validate_replacement_template(template: DocTemplate | None) -> DocTemplate:
    if template is None:
        raise_business_error(
            "GRANT_REPLACEMENT_TEMPLATE_INVALID",
            "Replacement notice requires an executable grant template",
            status_code=409,
        )
    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "GRANT_NOTICE"
        or semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        or semantics.fee_trigger != GRANT_FEE_DRAFT_TYPE
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_TEMPLATE_INVALID",
            "Replacement notice requires executable grant semantics",
            details={"template_id": template.id, "template_code": template.code},
            status_code=409,
        )
    return template


def _validate_replacement_document_shape(
    *,
    old_task: T_GrantFeeTask,
    replacement_document: DocumentCreateIn,
) -> None:
    direction = getattr(replacement_document.direction, "value", replacement_document.direction)
    if (
        replacement_document.case_id != old_task.case_id
        or direction != DocumentDirection.IN.value
        or replacement_document.reply_to_id is not None
        or not str(replacement_document.title or "").strip()
        or not str(replacement_document.ref_no or "").strip()
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_DOCUMENT_INVALID",
            "Replacement notice must be an incoming document for the old task case",
            details={
                "task_case_id": old_task.case_id,
                "document_case_id": replacement_document.case_id,
                "direction": direction,
                "reply_to_id": replacement_document.reply_to_id,
                "title": replacement_document.title,
                "ref_no": replacement_document.ref_no,
            },
            status_code=400,
        )


def _replacement_document_matches(
    document: Document,
    *,
    replacement_document: DocumentCreateIn,
    expected_extra_data: str | None,
) -> bool:
    direction = getattr(replacement_document.direction, "value", replacement_document.direction)
    doc_type = getattr(replacement_document.doc_type, "value", replacement_document.doc_type)
    return (
        document.case_id == replacement_document.case_id
        and document.doc_template_id == replacement_document.doc_template_id
        and document.doc_type == doc_type
        and document.direction == direction
        and document.doc_date == replacement_document.doc_date
        and document.title == replacement_document.title
        and document.ref_no == replacement_document.ref_no
        and document.extra_data == expected_extra_data
        and document.reply_to_id == replacement_document.reply_to_id
    )


def _existing_replacement_result(
    db: Session,
    *,
    old_task: T_GrantFeeTask,
    request_key: str,
    reason: str,
    replacement_document: DocumentCreateIn,
    expected_extra_data: str | None,
) -> GrantFeeTaskReplacementResult | None:
    request_owner = db.execute(
        select(T_GrantFeeTask).where(T_GrantFeeTask.supersede_request_key == request_key)
    ).scalar_one_or_none()
    if request_owner is None:
        return None
    if request_owner.id != old_task.id or request_owner.superseded_by_task_id is None:
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request key is already bound to a different operation",
            details={"request_key": request_key},
            status_code=409,
        )
    replacement_task = db.get(T_GrantFeeTask, request_owner.superseded_by_task_id)
    replacement_source = (
        db.get(Document, replacement_task.source_document_id)
        if replacement_task is not None and replacement_task.source_document_id
        else None
    )
    if (
        request_owner.supersede_reason != reason
        or replacement_task is None
        or replacement_task.case_id != old_task.case_id
        or replacement_source is None
        or not _replacement_document_matches(
            replacement_source,
            replacement_document=replacement_document,
            expected_extra_data=expected_extra_data,
        )
    ):
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request key conflicts with the existing payload",
            details={"request_key": request_key, "task_id": old_task.id},
            status_code=409,
        )
    return GrantFeeTaskReplacementResult(
        document=replacement_source,
        replacement_task=replacement_task,
        superseded_task_id=old_task.id,
        reused=True,
    )


def replace_grant_fee_task_with_notice(
    db: Session,
    *,
    task_id: str,
    request_key: str,
    reason: str,
    replacement_document: DocumentCreateIn,
    actor_id: str,
) -> GrantFeeTaskReplacementResult:
    normalized_request_key = _normalize_replacement_text(
        request_key,
        field="request_key",
        max_length=64,
    )
    normalized_reason = _normalize_replacement_text(reason, field="reason")
    normalized_actor_id = _normalize_replacement_text(
        actor_id,
        field="actor_id",
        max_length=36,
    )

    _ensure_sqlite_grant_write_transaction(db)
    try:
        old_task = _load_grant_fee_task(db, task_id=task_id)
        _validate_replacement_document_shape(
            old_task=old_task,
            replacement_document=replacement_document,
        )
        if (
            not old_task.source_document_id
            or not old_task.deadline_source
            or old_task.deadline_confirmed_at is None
        ):
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Only an active grant task with confirmed source lineage can be replaced",
                details={"task_id": old_task.id},
                status_code=409,
            )
        source_document = db.get(Document, old_task.source_document_id)
        if source_document is None or source_document.case_id != old_task.case_id:
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Old grant task source lineage is missing or inconsistent",
                details={"task_id": old_task.id},
                status_code=409,
            )

        expected_extra_data = _merge_document_create_extra_data(replacement_document)
        expected_deadline = parse_document_extra_data(expected_extra_data)
        if (
            expected_deadline.official_due_date_status != "CONFIRMED"
            or expected_deadline.official_due_date is None
            or expected_deadline.official_due_date_source is None
        ):
            raise_business_error(
                "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
                "Replacement grant notice requires a confirmed official due date",
                status_code=409,
            )

        existing = _existing_replacement_result(
            db,
            old_task=old_task,
            request_key=normalized_request_key,
            reason=normalized_reason,
            replacement_document=replacement_document,
            expected_extra_data=expected_extra_data,
        )
        if existing is not None:
            db.commit()
            return existing
        if old_task.superseded_by_task_id is not None or old_task.supersede_request_key is not None:
            raise_business_error(
                "GRANT_REPLACEMENT_LINEAGE_CONFLICT",
                "Grant fee task has already been superseded",
                details={"task_id": old_task.id},
                status_code=409,
            )

        template = _validate_replacement_template(
            db.get(DocTemplate, replacement_document.doc_template_id)
            if replacement_document.doc_template_id
            else None
        )

        replacement_source = create_document(db, replacement_document)
        replacement_task = ensure_grant_fee_task_for_notice_document(
            db,
            document=replacement_source,
            template=template,
            superseding_task_id=old_task.id,
        )
        if replacement_task is None:
            raise_business_error(
                "GRANT_REPLACEMENT_TEMPLATE_INVALID",
                "Replacement notice did not create a grant fee task",
                status_code=409,
            )

        old_task.superseded_by_task_id = replacement_task.id
        old_task.supersede_reason = normalized_reason
        old_task.superseded_at = datetime.now()
        old_task.superseded_by = normalized_actor_id
        old_task.supersede_request_key = normalized_request_key
        db.flush()
        db.commit()
        db.refresh(replacement_source)
        db.refresh(replacement_task)
        return GrantFeeTaskReplacementResult(
            document=replacement_source,
            replacement_task=replacement_task,
            superseded_task_id=old_task.id,
            reused=False,
        )
    except IntegrityError:
        db.rollback()
        old_task = db.get(T_GrantFeeTask, task_id)
        if old_task is not None:
            existing = _existing_replacement_result(
                db,
                old_task=old_task,
                request_key=normalized_request_key,
                reason=normalized_reason,
                replacement_document=replacement_document,
                expected_extra_data=_merge_document_create_extra_data(replacement_document),
            )
            if existing is not None:
                return existing
        raise_business_error(
            "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            "Replacement request conflicted during atomic creation",
            details={"request_key": normalized_request_key},
            status_code=409,
        )
    except Exception:
        db.rollback()
        raise


def apply_grant_fee_batch_instruction(
    db: Session,
    *,
    task_ids: list[str],
    action: str,
) -> dict[str, Any]:
    normalized_action = _normalize_action(action)
    if normalized_action not in _BATCH_ALLOWED_ACTIONS:
        raise_business_error(
            "GRANT_FEE_BATCH_ACTION_INVALID",
            "Invalid grant fee batch action",
            details={"action": normalized_action, "allowed_actions": list(_BATCH_ALLOWED_ACTIONS)},
            status_code=400,
        )

    unique_task_ids = list(
        dict.fromkeys(
            str(task_id or "").strip() for task_id in task_ids if str(task_id or "").strip()
        )
    )
    if not unique_task_ids:
        raise_business_error(
            "GRANT_FEE_BATCH_SELECTION_REQUIRED",
            "task_ids must not be empty",
            status_code=400,
        )

    tasks = list(
        db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id.in_(unique_task_ids)))
        .scalars()
        .all()
    )
    task_by_id = {task.id: task for task in tasks}
    missing_task_ids = [task_id for task_id in unique_task_ids if task_id not in task_by_id]
    if missing_task_ids:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND",
            "One or more grant fee tasks do not exist",
            details={"task_ids": missing_task_ids},
            status_code=404,
        )

    for task_id in unique_task_ids:
        _require_grant_fee_task_actionable(task_by_id[task_id])

    invalid_tasks: list[dict[str, str]] = []
    for task_id in unique_task_ids:
        task = task_by_id[task_id]
        state = derive_grant_fee_task_state(task)
        if state != "WAITING_CLIENT":
            invalid_tasks.append({"task_id": task_id, "state": state})

    if invalid_tasks:
        raise_business_error(
            "GRANT_FEE_BATCH_STATE_INVALID",
            "One or more selected grant fee tasks are not waiting for client instruction",
            details={"invalid_tasks": invalid_tasks, "required_state": "WAITING_CLIENT"},
            status_code=400,
        )

    for task_id in unique_task_ids:
        _apply_grant_fee_task_mutation(task_by_id[task_id], normalized_action=normalized_action)

    db.commit()
    return {
        "success_count": len(unique_task_ids),
        "failure_count": 0,
        "updated_task_ids": unique_task_ids,
    }


def generate_grant_fee_notice_documents(
    db: Session,
    *,
    task_ids: list[str],
) -> dict[str, Any]:
    unique_task_ids = list(
        dict.fromkeys(
            str(task_id or "").strip() for task_id in task_ids if str(task_id or "").strip()
        )
    )
    if not unique_task_ids:
        raise_business_error(
            "GRANT_FEE_NOTICE_SELECTION_REQUIRED",
            "task_ids must not be empty",
            status_code=400,
        )

    tasks = list(
        db.execute(select(T_GrantFeeTask).where(T_GrantFeeTask.id.in_(unique_task_ids)))
        .scalars()
        .all()
    )
    task_by_id = {task.id: task for task in tasks}
    missing_task_ids = [task_id for task_id in unique_task_ids if task_id not in task_by_id]
    if missing_task_ids:
        raise_business_error(
            "GRANT_FEE_TASK_NOT_FOUND",
            "One or more grant fee tasks do not exist",
            details={"task_ids": missing_task_ids},
            status_code=404,
        )

    for task_id in unique_task_ids:
        _require_grant_fee_task_actionable(task_by_id[task_id])

    doc_template = db.execute(
        select(DocTemplate).where(
            DocTemplate.code == GRANT_FEE_NOTICE_TEMPLATE_CODE,
            DocTemplate.enabled.is_(True),
        )
    ).scalar_one_or_none()
    if doc_template is None:
        raise_business_error(
            "GRANT_FEE_NOTICE_TEMPLATE_NOT_FOUND",
            "Grant fee notice template is not configured",
            details={"template_code": GRANT_FEE_NOTICE_TEMPLATE_CODE},
            status_code=409,
        )

    try:
        _, template_path = resolve_document_template_render_source(db, doc_template=doc_template)
        renderer = TemplateRenderer()
        created_items: list[dict[str, Any]] = []

        for task_id in unique_task_ids:
            task = task_by_id[task_id]
            state = derive_grant_fee_task_state(task)
            _validate_grant_fee_notice_task(task, state=state)
            created_items.append(
                _generate_grant_fee_notice_document(
                    db,
                    task=task,
                    doc_template=doc_template,
                    template_path=template_path,
                    renderer=renderer,
                )
            )

        db.commit()
    except BusinessError:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise_business_error(
            "GRANT_FEE_NOTICE_GENERATION_FAILED",
            "Grant fee notice generation failed",
            details={"error": str(exc)},
            status_code=409,
        )

    return {
        "success_count": len(created_items),
        "failure_count": 0,
        "generated_document_ids": [item["document_id"] for item in created_items],
        "items": created_items,
    }


def generate_grant_fee_draft(
    db: Session,
    *,
    task_id: str,
    actor_id: str | None,
) -> dict[str, Any]:
    task = _load_grant_fee_task(db, task_id=task_id)
    _require_grant_fee_task_actionable(task)
    state = derive_grant_fee_task_state(task)
    marker = _draft_marker(task_id)
    existing_draft = _find_existing_grant_fee_draft(db, marker=marker)

    if existing_draft is not None:
        if not task.draft_generated:
            task.draft_generated = True
            db.commit()
            db.refresh(task)
            state = derive_grant_fee_task_state(task)
        return _serialize_grant_fee_draft_generation_result(
            task,
            draft=existing_draft,
            state=state,
            reused=True,
            item_count=_count_fee_items_for_draft(db, draft_id=existing_draft.id),
        )

    normalized_currency = str(task.currency or "").strip().upper()
    if state != "READY_TO_DRAFT" or task.draft_generated or not str(task.case_id or "").strip():
        raise_business_error(
            "GRANT_FEE_DRAFT_PRECONDITION_FAILED",
            "Grant fee task is not ready to generate draft",
            details={
                "task_id": task_id,
                "state": state,
                "draft_generated": bool(task.draft_generated),
                "case_id": task.case_id,
                "currency": task.currency,
            },
            status_code=400,
        )
    if not normalized_currency:
        raise_business_error(
            "GRANT_FEE_DRAFT_PRECONDITION_FAILED",
            "Grant fee task currency is required",
            details={"task_id": task_id, "currency": task.currency},
            status_code=400,
        )

    case = db.execute(select(Case).where(Case.id == task.case_id)).scalar_one_or_none()
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    gov_amount = _money_amount(task.gov_fee_amt)
    service_amount = _ZERO
    total_amount = gov_amount + service_amount

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=case.id,
        client_id=case.client_id,
        draft_type=GRANT_FEE_DRAFT_TYPE,
        currency=normalized_currency,
        status="OPEN",
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(draft)
    db.flush()

    fee_items = [
        {
            "fee_code": GRANT_FEE_GOV_FEE_CODE,
            "fee_name": "授权官费",
            "fee_type": "GOV",
            "amount": gov_amount,
        }
    ]
    for line in fee_items:
        db.add(
            FeeItem(
                id=str(uuid4()),
                draft_id=draft.id,
                case_id=case.id,
                fee_code=line["fee_code"],
                fee_name=line["fee_name"],
                fee_type=line["fee_type"],
                quantity=Decimal("1"),
                unit_price=line["amount"],
                amount=line["amount"],
                remark=marker,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )

    db.flush()
    recalc_fee_draft_totals(db, draft_id=draft.id)
    draft = db.get(FeeDraft, draft.id)
    if draft is None:
        raise_business_error(
            "GRANT_FEE_DRAFT_GENERATION_FAILED", "Draft generation failed", status_code=500
        )

    task.draft_generated = True
    db.commit()
    db.refresh(task)
    db.refresh(draft)
    return _serialize_grant_fee_draft_generation_result(
        task,
        draft=draft,
        state=derive_grant_fee_task_state(task),
        reused=False,
        item_count=len(fee_items),
        amount=total_amount,
    )


def _serialize_grant_fee_task_state(task: T_GrantFeeTask, *, state: str) -> dict[str, Any]:
    lineage_status = _derive_grant_fee_task_lineage_status(task)
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "state": state,
        "lineage_status": lineage_status,
        "source_document_id": task.source_document_id,
        "deadline_source": task.deadline_source,
        "deadline_confirmed_at": task.deadline_confirmed_at,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "notify_count": int(task.notify_count or 0),
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "is_overdue": bool(task.is_overdue),
        "allowed_actions": list(_STATE_ALLOWED_ACTIONS[state])
        if lineage_status == "CONFIRMED"
        else [],
        **_GRANT_FEE_DEADLINE_PREVIEW_FIELDS,
    }


def _build_grant_fee_bill_visibility_map(
    db: Session,
    *,
    tasks: list[T_GrantFeeTask],
) -> dict[str, dict[str, Any]]:
    task_ids = [str(task.id) for task in tasks if str(task.id or "").strip()]
    if not task_ids:
        return {}

    markers = {_draft_marker(task_id): task_id for task_id in task_ids}
    fee_item_rows = list(
        db.execute(
            select(FeeItem.remark, FeeItem.draft_id)
            .where(FeeItem.remark.in_(list(markers)), FeeItem.draft_id.is_not(None))
            .order_by(FeeItem.draft_id.asc())
        ).all()
    )

    task_to_draft_ids: dict[str, list[str]] = {}
    for remark, draft_id in fee_item_rows:
        if not remark or not draft_id:
            continue
        task_id = markers.get(str(remark))
        if not task_id:
            continue
        draft_ids = task_to_draft_ids.setdefault(task_id, [])
        if draft_id not in draft_ids:
            draft_ids.append(draft_id)

    all_draft_ids = sorted(
        {draft_id for draft_ids in task_to_draft_ids.values() for draft_id in draft_ids}
    )
    if not all_draft_ids:
        return {}

    bill_rows = list(
        db.execute(
            select(BillItem.draft_id, Bill.id, Bill.bill_no)
            .join(Bill, Bill.id == BillItem.bill_id)
            .where(BillItem.draft_id.in_(all_draft_ids))
            .order_by(Bill.created_at.asc(), Bill.id.asc(), BillItem.id.asc())
        ).all()
    )

    draft_to_bill: dict[str, dict[str, Any]] = {}
    for draft_id, bill_id, bill_no in bill_rows:
        if draft_id and draft_id not in draft_to_bill:
            draft_to_bill[draft_id] = {
                "billed": True,
                "linked_bill_id": bill_id,
                "linked_bill_no": bill_no or bill_id,
            }

    visibility_map: dict[str, dict[str, Any]] = {}
    for task_id, draft_ids in task_to_draft_ids.items():
        for draft_id in draft_ids:
            bill_visibility = draft_to_bill.get(draft_id)
            if bill_visibility:
                visibility_map[task_id] = bill_visibility
                break
    return visibility_map


def _build_grant_fee_task_case_no_map(
    db: Session,
    *,
    tasks: list[T_GrantFeeTask],
) -> dict[str, str]:
    case_ids = sorted({str(task.case_id) for task in tasks if str(task.case_id or "").strip()})
    if not case_ids:
        return {}
    rows = db.execute(select(Case.id, Case.case_no).where(Case.id.in_(case_ids))).all()
    return {case_id: case_no for case_id, case_no in rows if case_no}


def _serialize_grant_fee_task_list_item(
    task: T_GrantFeeTask,
    *,
    state: str,
    case_no: str | None,
    bill_visibility: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "case_no": case_no,
        "status": state,
        "lineage_status": _derive_grant_fee_task_lineage_status(task),
        "source_document_id": task.source_document_id,
        "deadline_source": task.deadline_source,
        "deadline_confirmed_at": task.deadline_confirmed_at,
        "due_date": task.due_date,
        "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
        "gov_fee_amt": task.gov_fee_amt,
        "service_fee_amt": task.service_fee_amt,
        "currency": task.currency,
        "draft_generated": bool(task.draft_generated),
        "notice_sent": bool(task.notice_sent),
        "notify_count": int(task.notify_count or 0),
        "is_overdue": bool(task.is_overdue),
        "billed": bool(bill_visibility.get("billed")),
        "linked_bill_id": bill_visibility.get("linked_bill_id"),
        "linked_bill_no": bill_visibility.get("linked_bill_no"),
        **_GRANT_FEE_DEADLINE_PREVIEW_FIELDS,
    }


def _serialize_grant_fee_draft_generation_result(
    task: T_GrantFeeTask,
    *,
    draft: FeeDraft,
    state: str,
    reused: bool,
    item_count: int | None = None,
    amount: Decimal | None = None,
) -> dict[str, Any]:
    draft_amount = amount if amount is not None else _money_amount(draft.amount)
    if item_count is None:
        item_count = 0

    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "draft_id": draft.id,
        "draft_type": draft.draft_type,
        "state": state,
        "draft_generated": bool(task.draft_generated),
        "currency": draft.currency,
        "amount": draft_amount,
        "item_count": item_count,
        "reused": reused,
    }


def _validate_grant_fee_notice_task(task: T_GrantFeeTask, *, state: str) -> None:
    if state not in _NOTICE_ALLOWED_STATES or task.draft_generated:
        raise_business_error(
            "GRANT_FEE_NOTICE_STATE_INVALID",
            "Grant fee task is not eligible for notice generation",
            details={
                "task_id": task.id,
                "state": state,
                "required_states": list(_NOTICE_ALLOWED_STATES),
                "draft_generated": bool(task.draft_generated),
            },
            status_code=400,
        )

    instruction = (task.client_instruction or "NONE").strip().upper() or "NONE"
    if instruction != "NONE":
        raise_business_error(
            "GRANT_FEE_NOTICE_STATE_INVALID",
            "Grant fee task already has client instruction",
            details={
                "task_id": task.id,
                "client_instruction": instruction,
                "required_instruction": "NONE",
            },
            status_code=400,
        )


def _generate_grant_fee_notice_document(
    db: Session,
    *,
    task: T_GrantFeeTask,
    doc_template: DocTemplate,
    template_path: str,
    renderer: TemplateRenderer,
) -> dict[str, Any]:
    next_notify_count = int(task.notify_count or 0) + 1
    document = Document(
        id=str(uuid4()),
        case_id=task.case_id,
        doc_template_id=doc_template.id,
        direction="OUT",
        doc_date=date.today(),
        title="授权费通知函",
        extra_data=json.dumps({"grant_fee_task_id": task.id}, ensure_ascii=False),
    )
    db.add(document)
    db.flush()

    render_context = {
        **build_document_template_render_context(db, document=document),
        "grant_fee_task": {
            "id": task.id,
            "case_id": task.case_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "gov_fee_amt": str(Decimal(task.gov_fee_amt or 0)),
            "service_fee_amt": str(Decimal(task.service_fee_amt or 0)),
            "currency": task.currency,
            "client_instruction": (task.client_instruction or "NONE").strip().upper() or "NONE",
            "notify_count": next_notify_count,
            "notice_sent": True,
            "is_overdue": bool(task.is_overdue),
        },
    }
    try:
        rendered_bytes = renderer.render_template_docx_bytes(
            template_path=template_path,
            context=render_context,
        )
    except Exception as exc:
        raise_business_error(
            "GRANT_FEE_NOTICE_RENDER_FAILED",
            "Grant fee notice render failed",
            details={"task_id": task.id, "error": str(exc)},
            status_code=409,
        )

    attachment = persist_generated_attachment(
        db,
        document_id=document.id,
        file_name=_grant_fee_notice_file_name(task),
        content_bytes=rendered_bytes,
        storage_dir=str(_backend_storage_dir()),
        mime_type=DOCX_MIME_TYPE,
        commit=False,
    )

    task.notice_sent = True
    task.notify_count = next_notify_count
    db.flush()
    return {
        "task_id": task.id,
        "case_id": task.case_id,
        "document_id": document.id,
        "attachment_id": attachment.id,
        "file_name": attachment.file_name,
        "notify_count": int(task.notify_count or 0),
    }


def _grant_fee_notice_file_name(task: T_GrantFeeTask) -> str:
    suffix = (str(task.case_id or "").strip() or str(task.id or "").strip() or "task")[:24]
    return f"授权费通知函-{suffix}.docx"
