from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
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
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.enums import DocumentDirection, DocumentDocType
from app.modules.documents.models import DocTemplate, Document, DocumentEvidenceVersion
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.fees.demo_service import _bundle
from app.modules.fees.models import FeeObligation, FeeRate, OfficialRateBook, T_GrantFeeTask
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeSourceStatus,
    PrepareFeeObligationDraftCommand,
    RecognizeFeeObligationCommand,
)
from app.modules.fees.obligation_service import (
    get_fee_obligation,
    prepare_draft,
    recognize_obligation,
)
from app.modules.grant_fees.service import (
    ConfirmGrantOfficialFeesCommand as ConfirmGrantReviewCommand,
)
from app.modules.grant_fees.service import (
    GrantOfficialFeeReviewLineInput,
    RecordGrantFeeTaskInstructionCommand,
    record_grant_fee_task_instruction,
)
from app.modules.grant_fees.service import (
    confirm_grant_official_fees as confirm_grant_official_fee_review,
)

_SOURCE_EVENT = "DEMO_GRANT_OFFICIAL_FEE_CONFIRMED"
_SOURCE_SCHEMA = "FPMS_DEMO_GRANT_OFFICIAL_FEE_CONFIRMED_V1"
_RATE_ROW_ATTESTATION_PREFIX = "FPMS_DEMO_RATE_ROW_SHA256:"


@dataclass(frozen=True, slots=True)
class GrantOfficialFeePreviewLine:
    fee_code: str
    fee_name: str
    quantity: int
    unit_price: Decimal
    calculation_mode: str
    candidate_amount: Decimal
    official_full_amount: Decimal
    payable_amount: Decimal
    currency: str
    source_reference: str
    source_version: str
    source_sha256: str


@dataclass(frozen=True, slots=True)
class GrantOfficialFeePreview:
    grant_fee_task_id: str
    case_id: str
    source_document_id: str
    reviewed_evidence_version_id: str
    reviewed_evidence_content_hash: str
    source_authority: str
    rate_book_version: str
    rate_book_sha256: str
    effective_from: date
    effective_to: date | None
    currency: str
    lines: tuple[GrantOfficialFeePreviewLine, ...]
    total_payable_amount: Decimal
    preview_digest: str
    canonical_payload: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantOfficialFeeConfirmationLine:
    fee_code: str
    quantity: int
    confirmed_payable_amount: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfirmGrantOfficialFeeCommand:
    grant_fee_task_id: str
    preview_digest: str
    reviewed_evidence_version_id: str
    expected_content_hash: str
    confirmed_at: datetime
    actor_id: str
    idempotency_key: str
    lines: tuple[GrantOfficialFeeConfirmationLine, ...]


@dataclass(frozen=True, slots=True)
class ConfirmGrantOfficialFeeResult:
    grant_fee_task_id: str
    fee_obligation_id: str
    review_activity_id: str
    draft_id: str
    obligation_line_ids: tuple[str, ...]
    fee_item_ids: tuple[str, ...]
    preview_digest: str
    idempotency_key: str
    reused: bool


def _fail(code: str, message: str, *, status_code: int) -> None:
    raise BusinessError(code, message, status_code=status_code)


def _source_conflict() -> None:
    _fail("DEMO_GOV_RATE_SOURCE_CONFLICT", "官费费率来源与运行输入不一致", status_code=409)


def _evidence_conflict() -> None:
    _fail("DEMO_GOV_EVIDENCE_CONFLICT", "授权通知证据未归档或谱系不一致", status_code=409)


def _confirmation_conflict() -> None:
    _fail("DEMO_GOV_CONFIRMATION_CONFLICT", "官费人工确认与当前预览不一致", status_code=409)


def _rate_row_attestation(row: FeeRate, book: OfficialRateBook) -> str:
    payload = {
        "schema": "FPMS_DEMO_RATE_ROW_ATTESTATION_V1",
        "book_id": book.id,
        "book_version": book.version_code,
        "book_sha256": book.source_snapshot_hash,
        "fee_code": row.fee_code,
        "fee_name": row.fee_name,
        "fee_type": row.fee_type,
        "currency": row.currency,
        "default_amount": (
            None if row.default_amount is None else format(row.default_amount, ".2f")
        ),
        "enabled": row.enabled,
        "rate_group": row.rate_group,
        "country_code": row.country_code,
        "case_type": row.case_type,
        "patent_category": row.patent_category,
        "fee_domain": row.fee_domain,
        "fee_section": row.fee_section,
        "fee_category": row.fee_category,
        "fee_subtype": row.fee_subtype,
        "reduction_scope": row.reduction_scope,
        "calc_mode": row.calc_mode,
        "calc_params": row.calc_params,
        "allow_reduction": row.allow_reduction,
        "effective_from": (
            None if row.effective_from is None else row.effective_from.isoformat()
        ),
        "effective_to": None if row.effective_to is None else row.effective_to.isoformat(),
        "source_doc": row.source_doc,
        "source_url": row.source_url,
        "source_version": row.source_version,
        "source_status": row.source_status,
        "official_rate_book_id": row.official_rate_book_id,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return _RATE_ROW_ATTESTATION_PREFIX + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def _projection(case: Case) -> LifecycleProjection:
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
            legal_status=(None if case.legal_status is None else LegalStatus(case.legal_status)),
            lifecycle_verification_status=(
                None
                if case.lifecycle_verification_status is None
                else ConfirmationStatus(case.lifecycle_verification_status)
            ),
        )
    except ValueError as exc:
        raise BusinessError(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "案件存量生命周期投影无效",
            status_code=409,
        ) from exc


def _task_evidence(
    transaction: Session, grant_fee_task_id: str
) -> tuple[T_GrantFeeTask, Case, DocumentEvidenceVersion]:
    task = transaction.get(T_GrantFeeTask, grant_fee_task_id)
    if task is None:
        _fail("DEMO_GOV_TASK_NOT_FOUND", "授权费用任务不存在", status_code=404)
    case = transaction.get(Case, task.case_id)
    if (
        case is None
        or task.type != "GRANT"
        or task.superseded_by_task_id is not None
        or task.source_document_id is None
        or task.currency != "CNY"
        or type(task.due_date) is not date
        or type(task.deadline_source) is not str
        or not task.deadline_source.strip()
        or len(task.deadline_source) > 32
        or type(task.deadline_confirmed_at) is not datetime
        or task.deadline_confirmed_at.tzinfo is not None
    ):
        _fail("DEMO_GOV_TASK_CONFLICT", "授权费用任务状态不支持官费预览", status_code=409)
    document = transaction.get(Document, task.source_document_id)
    if document is None:
        _fail("DEMO_GOV_EVIDENCE_NOT_FOUND", "授权通知证据不存在", status_code=404)
    template = transaction.get(DocTemplate, document.doc_template_id)
    try:
        semantics = resolve_document_semantics(template)
    except BusinessError:
        _fail("DEMO_GOV_TASK_CONFLICT", "授权费用任务状态不支持官费预览", status_code=409)
    if (
        document.case_id != task.case_id
        or document.direction != DocumentDirection.IN.value
        or document.doc_type != DocumentDocType.OFFICIAL_IN.value
        or semantics.execution_behavior != "GRANT_NOTICE"
        or semantics.lifecycle_event_type != "GRANT_REGISTRATION_NOTICE_RECORDED"
        or semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED"
    ):
        _fail("DEMO_GOV_TASK_CONFLICT", "授权费用任务状态不支持官费预览", status_code=409)
    all_versions = tuple(
        transaction.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.case_id == task.case_id,
                DocumentEvidenceVersion.document_id == task.source_document_id,
            )
        )
    )
    if not all_versions:
        _fail("DEMO_GOV_EVIDENCE_NOT_FOUND", "授权通知证据不存在", status_code=404)
    current = tuple(
        evidence for evidence in all_versions if evidence.current_identity_key is not None
    )
    if len(current) != 1:
        _evidence_conflict()
    evidence = current[0]
    if (
        evidence.state != "FINAL"
        or evidence.review_state != "APPROVED"
        or not evidence.reviewer_id
        or type(evidence.reviewed_at) is not datetime
        or not evidence.content_hash
        or evidence.current_identity_key != f"{task.case_id}|{evidence.lineage_key}"
    ):
        _evidence_conflict()
    return task, cast(Case, case), evidence


def _canonical_preview_payload(
    *,
    task: T_GrantFeeTask,
    evidence: DocumentEvidenceVersion,
    book: OfficialRateBook,
    lines: tuple[GrantOfficialFeePreviewLine, ...],
) -> str:
    return json.dumps(
        {
            "schema": "FPMS_DEMO_GRANT_OFFICIAL_FEE_PREVIEW_V1",
            "grant_fee_task_id": task.id,
            "case_id": task.case_id,
            "source_document_id": task.source_document_id,
            "reviewed_evidence_version_id": evidence.id,
            "reviewed_evidence_content_hash": evidence.content_hash,
            "source_authority": book.source_authority,
            "rate_book_version": book.version_code,
            "rate_book_sha256": book.source_snapshot_hash,
            "effective_from": book.effective_from.isoformat(),
            "effective_to": None if book.effective_to is None else book.effective_to.isoformat(),
            "currency": "CNY",
            "lines": [
                {
                    "fee_code": line.fee_code,
                    "fee_name": line.fee_name,
                    "quantity": line.quantity,
                    "unit_price": format(line.unit_price, ".2f"),
                    "calculation_mode": line.calculation_mode,
                    "candidate_amount": format(line.candidate_amount, ".2f"),
                    "official_full_amount": format(line.official_full_amount, ".2f"),
                    "payable_amount": format(line.payable_amount, ".2f"),
                    "currency": line.currency,
                    "source_reference": line.source_reference,
                    "source_version": line.source_version,
                    "source_sha256": line.source_sha256,
                }
                for line in lines
            ],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def preview_grant_official_fees(
    transaction: Session, *, grant_fee_task_id: str
) -> GrantOfficialFeePreview:
    if (
        type(grant_fee_task_id) is not str
        or not grant_fee_task_id
        or grant_fee_task_id != grant_fee_task_id.strip()
        or len(grant_fee_task_id) > 36
    ):
        _fail("DEMO_GOV_INPUT_INVALID", "官费预览输入无效", status_code=400)
    if transaction.new or transaction.dirty or transaction.deleted:
        _fail(
            "DEMO_GOV_PREVIEW_TRANSACTION_CONFLICT",
            "官费预览要求干净事务",
            status_code=409,
        )
    with transaction.no_autoflush:
        task, _case, evidence = _task_evidence(transaction, grant_fee_task_id)
    snapshot = _bundle()
    selector = snapshot.official_fee_selector
    if snapshot.schema_version != "fpms.demo-input-bundle/integrated-a-v2" or selector is None:
        _source_conflict()
    books = tuple(
        transaction.scalars(
            select(OfficialRateBook).where(
                OfficialRateBook.source_authority == selector.source_authority,
                OfficialRateBook.version_code == selector.rate_book_version,
                OfficialRateBook.source_snapshot_hash == selector.rate_book_sha256,
                OfficialRateBook.approval_status == "APPROVED",
                OfficialRateBook.activation_status == "ACTIVE",
                OfficialRateBook.effective_from <= task.due_date,
                (OfficialRateBook.effective_to.is_(None))
                | (OfficialRateBook.effective_to >= task.due_date),
            )
        )
    )
    if len(books) != 1:
        _source_conflict()
    book = books[0]
    if (
        book.current_identity_key != f"CNIPA|{book.book_code}"
        or hashlib.sha256(book.source_snapshot.encode("utf-8")).hexdigest()
        != book.source_snapshot_hash
        or book.approved_by is None
        or book.approved_at is None
        or book.activated_by is None
        or book.activated_at is None
    ):
        _source_conflict()
    rows = tuple(
        transaction.scalars(
            select(FeeRate).where(
                FeeRate.official_rate_book_id == book.id,
                FeeRate.fee_code.in_(selector.fee_codes),
            )
        )
    )
    by_code = {row.fee_code: row for row in rows}
    if len(rows) != len(selector.fee_codes) or set(by_code) != set(selector.fee_codes):
        _source_conflict()
    lines: list[GrantOfficialFeePreviewLine] = []
    for fee_code in selector.fee_codes:
        row = by_code[fee_code]
        amount = row.default_amount
        if (
            row.fee_type != "GOV"
            or row.currency != "CNY"
            or row.enabled is not True
            or row.calc_mode != "FIXED"
            or row.allow_reduction not in {False, None}
            or row.fee_name is None
            or amount is None
            or not amount.is_finite()
            or amount <= 0
            or amount != amount.quantize(Decimal("0.01"))
            or row.effective_from is None
            or row.effective_from > task.due_date
            or (row.effective_to is not None and row.effective_to < task.due_date)
            or row.source_doc != book.source_reference
            or row.source_version != book.source_version
            or row.source_status != "ACTIVE"
            or row.source_policy != _rate_row_attestation(row, book)
        ):
            _source_conflict()
        lines.append(
            GrantOfficialFeePreviewLine(
                fee_code=fee_code,
                fee_name=row.fee_name,
                quantity=1,
                unit_price=amount,
                calculation_mode="FIXED",
                candidate_amount=amount,
                official_full_amount=amount,
                payable_amount=amount,
                currency="CNY",
                source_reference=book.source_reference,
                source_version=book.source_version,
                source_sha256=book.source_snapshot_hash,
            )
        )
    line_tuple = tuple(lines)
    canonical = _canonical_preview_payload(
        task=task,
        evidence=evidence,
        book=book,
        lines=line_tuple,
    )
    return GrantOfficialFeePreview(
        grant_fee_task_id=task.id,
        case_id=task.case_id,
        source_document_id=cast(str, task.source_document_id),
        reviewed_evidence_version_id=evidence.id,
        reviewed_evidence_content_hash=evidence.content_hash,
        source_authority=book.source_authority,
        rate_book_version=book.version_code,
        rate_book_sha256=book.source_snapshot_hash,
        effective_from=book.effective_from,
        effective_to=book.effective_to,
        currency="CNY",
        lines=line_tuple,
        total_payable_amount=sum(
            (line.payable_amount for line in line_tuple), Decimal("0.00")
        ),
        preview_digest="sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        canonical_payload=canonical,
    )


def _validate_confirmation(command: object) -> ConfirmGrantOfficialFeeCommand:
    if type(command) is not ConfirmGrantOfficialFeeCommand:
        _fail("DEMO_GOV_INPUT_INVALID", "官费确认输入无效", status_code=400)
    for field, limit in (
        ("grant_fee_task_id", 36),
        ("reviewed_evidence_version_id", 36),
        ("actor_id", 36),
        ("idempotency_key", 128),
    ):
        value = getattr(command, field)
        if type(value) is not str or not value or value != value.strip() or len(value) > limit:
            _fail("DEMO_GOV_INPUT_INVALID", "官费确认输入无效", status_code=400)
    if (
        type(command.preview_digest) is not str
        or len(command.preview_digest) != 71
        or not command.preview_digest.startswith("sha256:")
        or type(command.expected_content_hash) is not str
        or len(command.expected_content_hash) != 71
        or not command.expected_content_hash.startswith("sha256:")
        or type(command.confirmed_at) is not datetime
        or command.confirmed_at.tzinfo is not None
        or type(command.lines) is not tuple
        or len(command.lines) < 2
    ):
        _fail("DEMO_GOV_INPUT_INVALID", "官费确认输入无效", status_code=400)
    return command


def confirm_grant_official_fees(
    command: ConfirmGrantOfficialFeeCommand, transaction: Session
) -> ConfirmGrantOfficialFeeResult:
    command = _validate_confirmation(command)
    if transaction.new or transaction.dirty or transaction.deleted:
        _confirmation_conflict()
    connection = transaction.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN IMMEDIATE")
    elif connection.dialect.name != "sqlite":
        transaction.scalar(
            select(T_GrantFeeTask.id)
            .where(T_GrantFeeTask.id == command.grant_fee_task_id)
            .with_for_update()
        )
    if (
        transaction.get(
            DocumentEvidenceVersion, command.reviewed_evidence_version_id
        )
        is None
    ):
        _fail("DEMO_GOV_EVIDENCE_NOT_FOUND", "授权通知证据不存在", status_code=404)
    preview = preview_grant_official_fees(
        transaction, grant_fee_task_id=command.grant_fee_task_id
    )
    if (
        command.preview_digest != preview.preview_digest
        or command.reviewed_evidence_version_id != preview.reviewed_evidence_version_id
        or command.expected_content_hash != preview.reviewed_evidence_content_hash
        or tuple(line.fee_code for line in command.lines)
        != tuple(line.fee_code for line in preview.lines)
        or any(
            supplied.quantity != expected.quantity
            or supplied.confirmed_payable_amount != expected.payable_amount
            for supplied, expected in zip(command.lines, preview.lines, strict=True)
        )
    ):
        _confirmation_conflict()
    task, case, evidence = _task_evidence(transaction, command.grant_fee_task_id)
    source_key = f"demo-gov-confirm-source:{command.idempotency_key}"
    recognition_key = f"demo-gov-confirm-obligation:{command.idempotency_key}"
    review_key = f"demo-gov-confirm-review:{command.idempotency_key}"
    instruction_key = f"demo-gov-confirm-instruction:{command.idempotency_key}"
    draft_key = f"demo-gov-confirm-draft:{command.idempotency_key}"
    prior_for_task: list[CaseActivityEvent] = []
    for row in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == task.case_id,
            CaseActivityEvent.activity_type == _SOURCE_EVENT,
        )
    ):
        try:
            stored_payload = json.loads(row.payload_json)
        except (TypeError, ValueError):
            _confirmation_conflict()
        if type(stored_payload) is not dict:
            _confirmation_conflict()
        if stored_payload.get("grant_fee_task_id") == task.id:
            prior_for_task.append(row)
    if prior_for_task and any(row.idempotency_key != source_key for row in prior_for_task):
        _confirmation_conflict()
    projection = _projection(case)
    payload = {
        "schema": _SOURCE_SCHEMA,
        "grant_fee_task_id": task.id,
        "case_id": task.case_id,
        "source_document_id": task.source_document_id,
        "reviewed_evidence_version_id": evidence.id,
        "reviewed_evidence_content_hash": evidence.content_hash,
        "confirmed_at": command.confirmed_at.isoformat(),
        "preview_digest": preview.preview_digest,
        "rate_book_version": preview.rate_book_version,
        "rate_book_sha256": preview.rate_book_sha256,
        "lines": [
            {
                "fee_code": line.fee_code,
                "quantity": line.quantity,
                "confirmed_payable_amount": format(line.confirmed_payable_amount, ".2f"),
            }
            for line in command.lines
        ],
    }
    with transaction.begin_nested():
        source = append_case_activity(
            LifecycleEventCommand(
                case_id=task.case_id,
                event_type=_SOURCE_EVENT,
                lane=ActivityLane.FEE,
                effective_at=command.confirmed_at,
                occurred_at=command.confirmed_at,
                evidence_refs=(
                    EvidenceReference(
                        case_id=task.case_id,
                        evidence_kind="SOURCE_DOCUMENT",
                        object_type="Document",
                        object_id=cast(str, task.source_document_id),
                        content_hash=evidence.content_hash,
                        captured_at=command.confirmed_at,
                    ),
                    EvidenceReference(
                        case_id=task.case_id,
                        evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                        object_type="DocumentEvidenceVersion",
                        object_id=evidence.id,
                        content_hash=evidence.content_hash,
                        captured_at=command.confirmed_at,
                    ),
                ),
                actor_id=command.actor_id,
                reviewer_id=command.actor_id,
                idempotency_key=source_key,
                source_activity_id=None,
                supersedes_event_id=None,
                payload=payload,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            transaction,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=case.status,
            conflict_codes=(),
        )
        if source.reused:
            stored_obligations = tuple(
                transaction.scalars(
                    select(FeeObligation).where(
                        FeeObligation.case_id == task.case_id,
                        FeeObligation.source_activity_id == source.activity_id,
                        FeeObligation.obligation_type
                        == "GRANT_REGISTRATION_OFFICIAL_FEES",
                    )
                )
            )
            if len(stored_obligations) != 1:
                _confirmation_conflict()
            obligation = get_fee_obligation(stored_obligations[0].id, transaction)
        else:
            recognition = recognize_obligation(
                RecognizeFeeObligationCommand(
                    case_id=task.case_id,
                    source_activity_id=source.activity_id,
                    source_document_id=task.source_document_id,
                    fee_domain=FeeDomain.GOV,
                    obligation_type="GRANT_REGISTRATION_OFFICIAL_FEES",
                    due_date=task.due_date,
                    currency="CNY",
                    source_status=FeeSourceStatus.VERIFIED,
                    lines=tuple(
                        FeeObligationLineInput(
                            fee_code=line.fee_code,
                            fee_name=line.fee_name,
                            fee_year_key=0,
                            official_full_amount=None,
                            reduction_ratio=Decimal("0.0000"),
                            payable_amount=line.payable_amount,
                            source_amount=line.payable_amount,
                            source_date=preview.effective_from,
                            difference_review_state=(
                                FeeDifferenceReviewState.REVIEW_REQUIRED
                            ),
                        )
                        for line in preview.lines
                    ),
                    actor_id=command.actor_id,
                    idempotency_key=recognition_key,
                    supersedes_obligation_id=None,
                    supersede_reason=None,
                ),
                transaction,
            )
            obligation = recognition.obligation
        supplied_by_code = {line.fee_code: line for line in command.lines}
        review = confirm_grant_official_fee_review(
            ConfirmGrantReviewCommand(
                grant_fee_task_id=task.id,
                source_activity_id=source.activity_id,
                obligation_id=obligation.id,
                reviewed_evidence_version_id=evidence.id,
                expected_content_hash=evidence.content_hash,
                confirmed_at=command.confirmed_at,
                actor_id=command.actor_id,
                idempotency_key=review_key,
                lines=tuple(
                    GrantOfficialFeeReviewLineInput(
                        obligation_line_id=line.id,
                        official_full_amount=supplied_by_code[
                            line.fee_code
                        ].confirmed_payable_amount,
                        confirmed_payable_amount=supplied_by_code[
                            line.fee_code
                        ].confirmed_payable_amount,
                    )
                    for line in obligation.lines
                ),
            ),
            transaction,
        )
        instruction = record_grant_fee_task_instruction(
            RecordGrantFeeTaskInstructionCommand(
                grant_fee_task_id=task.id,
                source_activity_id=source.activity_id,
                instruction="PAY",
                actor_id=command.actor_id,
                idempotency_key=instruction_key,
            ),
            transaction,
        )
        draft = prepare_draft(
            PrepareFeeObligationDraftCommand(
                obligation_id=obligation.id,
                actor_id=command.actor_id,
                idempotency_key=draft_key,
            ),
            transaction,
        )
    reused = source.reused and review.reused and instruction.reused and draft.activity_reused
    return ConfirmGrantOfficialFeeResult(
        grant_fee_task_id=task.id,
        fee_obligation_id=obligation.id,
        review_activity_id=review.review_activity_id,
        draft_id=draft.draft_id,
        obligation_line_ids=tuple(link.obligation_line_id for link in draft.links),
        fee_item_ids=tuple(link.fee_item_id for link in draft.links),
        preview_digest=preview.preview_digest,
        idempotency_key=command.idempotency_key,
        reused=reused,
    )
