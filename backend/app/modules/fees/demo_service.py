from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, fields
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.demo_bundle import DemoBundleError, DemoBundleSnapshot, load_demo_bundle
from app.core.errors import BusinessError
from app.modules.billing.models import Bill, BillDraftSource, Offset, Payment
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
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationDraftStatus,
    FeeObligationLineInput,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
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
from app.modules.fees.service import get_fee_draft, list_fee_items
from app.modules.masterdata.clients.models import Client, ClientContact
from app.modules.official_workflows.models import OfficialWorkPackage
from app.modules.tasks.models import Task

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SOURCE_SCHEMA = "FPMS_DEMO_SERVICE_PRICE_ITEMS_SELECTED_V2"
_INTEGRATED_SCHEMA = "fpms.demo-input-bundle/integrated-a-v2"


@dataclass(frozen=True, slots=True)
class DemoServiceItem:
    item_code: str
    name_zh_cn: str
    currency: str
    unit_price: Decimal
    quantity: int
    final_quantity: int
    adjustable: bool
    amount: Decimal
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str


@dataclass(frozen=True, slots=True)
class DemoServiceItems:
    classification: str
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    template_code: str
    template_sha256: str
    template_required_variables: tuple[str, ...]
    items: tuple[DemoServiceItem, ...]
    total_amount: Decimal


@dataclass(frozen=True, slots=True)
class DemoPreflightResult(DemoServiceItems):
    authority_classification: str
    customer_activation_eligible: bool
    readiness: str
    business_counts: dict[str, int]


@dataclass(frozen=True, slots=True)
class DemoServiceObligationResult(DemoServiceItems):
    obligation: object
    source_activity_id: str
    idempotency_key: str
    reused: bool


@dataclass(frozen=True, slots=True)
class DemoServiceAdjustmentCommand:
    draft_id: str
    item_id: str
    expected_quantity: int
    new_quantity: int
    reason: str
    actor_id: str
    idempotency_key: str
    adjusted_at: datetime


@dataclass(frozen=True, slots=True)
class DemoServiceAdjustmentResult:
    draft_id: str
    original_obligation_id: str
    superseding_obligation_id: str
    adjustment_activity_id: str
    instruction_activity_id: str
    fee_item_ids: tuple[str, ...]
    before_total: Decimal
    after_total: Decimal
    idempotency_key: str
    reused: bool


def _config_required(message: str) -> BusinessError:
    return BusinessError(
        code="DEMO_INPUT_CONFIG_REQUIRED",
        message=message,
        status_code=409,
    )


@lru_cache(maxsize=8)
def _load_bundle_snapshot(
    root: str,
    manifest_digest: str,
    authority_digest: str,
    authority_classification: str,
) -> DemoBundleSnapshot:
    try:
        return load_demo_bundle(
            Path(root),
            expected_manifest_sha256=manifest_digest,
            expected_authority_sha256=authority_digest,
            expected_authority_classification=authority_classification,
            repo_root=_REPO_ROOT,
        )
    except DemoBundleError as exc:
        raise _config_required("本地演示输入无效或已变化") from exc


def _bundle() -> DemoBundleSnapshot:
    if os.environ.get("FPMS_ENV") != "demo" or os.environ.get("FPMS_DEMO_SCOPE") != "LOCAL_ABC_E2E":
        raise _config_required("本地演示输入仅在 LOCAL_ABC_E2E 模式可用")
    root = os.environ.get("FPMS_DEMO_BUNDLE_PATH", "")
    digest = os.environ.get("FPMS_DEMO_EXPECTED_MANIFEST_SHA256", "")
    authority_digest = os.environ.get("FPMS_DEMO_EXPECTED_AUTHORITY_SHA256", "")
    authority_classification = os.environ.get(
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION", ""
    )
    if not root or not digest or not authority_digest or not authority_classification:
        raise _config_required("本地演示输入未配置")
    required_profile = (
        "TECHNICAL_REHEARSAL"
        if authority_classification == "SYNTHETIC_TEST_ONLY"
        else "CUSTOMER_DEMO"
    )
    if os.environ.get("FPMS_DEMO_RUN_PROFILE") != required_profile:
        raise _config_required("本地演示输入来源分类与运行模式不匹配")
    return _load_bundle_snapshot(root, digest, authority_digest, authority_classification)


def _demo_service_items(snapshot: DemoBundleSnapshot) -> DemoServiceItems:
    items: list[DemoServiceItem] = []
    try:
        for rate in snapshot.service_rates:
            unit_price = Decimal(rate.unit_price)
            items.append(
                DemoServiceItem(
                    item_code=rate.item_code,
                    name_zh_cn=rate.name_zh_cn,
                    currency=rate.currency,
                    unit_price=unit_price,
                    quantity=rate.initial_quantity,
                    final_quantity=rate.final_quantity,
                    adjustable=rate.adjustable,
                    amount=unit_price * rate.initial_quantity,
                    source_ref=rate.source_ref,
                    source_version=rate.source_version,
                    source_sha256=rate.source_sha256,
                    disclaimer_zh_cn=rate.disclaimer_zh_cn,
                )
            )
    except InvalidOperation as exc:
        raise _config_required("本地演示服务费金额无效") from exc
    return DemoServiceItems(
        classification="DEMO_ONLY",
        bundle_id=snapshot.bundle_id,
        bundle_version=snapshot.bundle_version,
        manifest_sha256=snapshot.manifest_sha256,
        template_code=snapshot.template.template_code,
        template_sha256=snapshot.template.sha256,
        template_required_variables=snapshot.template.required_variables,
        items=tuple(items),
        total_amount=sum((item.amount for item in items), Decimal("0.00")),
    )


def _service_source_payload(
    snapshot: DemoBundleSnapshot,
    selection: DemoServiceItems,
) -> dict[str, object]:
    return {
        "schema": _SOURCE_SCHEMA,
        "bundle_id": selection.bundle_id,
        "bundle_version": selection.bundle_version,
        "manifest_sha256": selection.manifest_sha256,
        "authority_sha256": snapshot.authority_sha256,
        "authority_classification": snapshot.authority_classification,
        "approved_by": snapshot.approved_by,
        "approved_at": snapshot.approved_at,
        "items": [
            {
                "item_code": item.item_code,
                "name_zh_cn": item.name_zh_cn,
                "currency": item.currency,
                "unit_price": format(item.unit_price, ".2f"),
                "quantity": item.quantity,
                "final_quantity": item.final_quantity,
                "adjustable": item.adjustable,
                "amount": format(item.amount, ".2f"),
                "source_ref": item.source_ref,
                "source_version": item.source_version,
                "source_sha256": item.source_sha256,
                "disclaimer_zh_cn": item.disclaimer_zh_cn,
            }
            for item in selection.items
        ],
    }


def get_demo_service_item() -> DemoServiceItems:
    return _demo_service_items(_bundle())


def get_demo_preflight(transaction: Session) -> DemoPreflightResult:
    snapshot = _bundle()
    if snapshot.schema_version != _INTEGRATED_SCHEMA:
        raise _config_required("当前输入不是集成演示方案 A 的运行包")
    item = _demo_service_items(snapshot)
    models = (
        ("client", Client),
        ("contact", ClientContact),
        ("case", Case),
        ("package", OfficialWorkPackage),
        ("task", Task),
        ("obligation", FeeObligation),
        ("draft", FeeDraft),
        ("bill", Bill),
        ("payment", Payment),
        ("offset", Offset),
    )
    counts = {
        name: int(transaction.scalar(select(func.count()).select_from(model)) or 0)
        for name, model in models
    }
    if any(counts.values()):
        raise BusinessError(
            code="DEMO_RUN_NOT_FRESH",
            message="本地集成演示必须从全新业务数据库开始",
            status_code=409,
        )
    values = {field.name: getattr(item, field.name) for field in fields(DemoServiceItems)}
    return DemoPreflightResult(
        **values,
        authority_classification=snapshot.authority_classification,
        customer_activation_eligible=snapshot.customer_activation_eligible,
        readiness="READY",
        business_counts=counts,
    )


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
            legal_status=None if case.legal_status is None else LegalStatus(case.legal_status),
            lifecycle_verification_status=(
                None
                if case.lifecycle_verification_status is None
                else ConfirmationStatus(case.lifecycle_verification_status)
            ),
        )
    except ValueError as exc:
        raise BusinessError(
            code="LIFECYCLE_PROJECTION_CONFLICT",
            message="案件存量生命周期投影无效",
            status_code=409,
        ) from exc


def create_demo_service_obligation(
    transaction: Session,
    *,
    case_id: str,
    actor_id: str,
    idempotency_key: str,
    recognized_at: datetime,
) -> DemoServiceObligationResult:
    snapshot = _bundle()
    if snapshot.schema_version != _INTEGRATED_SCHEMA:
        raise _config_required("当前输入不是集成演示方案 A 的运行包")
    selection = _demo_service_items(snapshot)
    values = (
        (case_id, 36, "case_id"),
        (actor_id, 36, "actor_id"),
        (idempotency_key, 96, "idempotency_key"),
    )
    if any(
        not value or value != value.strip() or "\x00" in value or len(value) > limit
        for value, limit, _field in values
    ) or recognized_at.tzinfo is not None:
        raise BusinessError(
            code="DEMO_SERVICE_INPUT_INVALID",
            message="本地演示服务费输入无效",
            status_code=400,
        )
    if transaction.new or transaction.dirty or transaction.deleted:
        raise BusinessError(
            code="DEMO_SERVICE_TRANSACTION_CONFLICT",
            message="本地演示服务费事务状态冲突",
            status_code=409,
        )

    connection = transaction.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN IMMEDIATE")
    case = transaction.scalar(select(Case).where(Case.id == case_id))
    if case is None:
        raise BusinessError(code="CASE_NOT_FOUND", message="案件不存在", status_code=404)
    projection = _projection(case)
    source_key = f"demo-service-source:{idempotency_key}"
    recognition_key = f"demo-service-obligation:{idempotency_key}"
    existing_source_time = transaction.scalar(
        select(CaseActivityEvent.occurred_at).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.idempotency_key == source_key,
        )
    )
    if existing_source_time is not None:
        recognized_at = existing_source_time
    bundle_object_id = str(UUID(selection.manifest_sha256[:32]))

    with transaction.begin_nested():
        source = append_case_activity(
            LifecycleEventCommand(
                case_id=case_id,
                event_type="DEMO_SERVICE_PRICE_ITEM_SELECTED",
                lane=ActivityLane.FEE,
                effective_at=recognized_at,
                occurred_at=recognized_at,
                evidence_refs=(
                    EvidenceReference(
                        case_id=case_id,
                        evidence_kind="DEMO_SERVICE_BUNDLE",
                        object_type="DemoBundle",
                        object_id=bundle_object_id,
                        content_hash=selection.manifest_sha256,
                        captured_at=recognized_at,
                    ),
                ),
                actor_id=actor_id,
                reviewer_id=None,
                idempotency_key=source_key,
                source_activity_id=None,
                supersedes_event_id=None,
                payload=_service_source_payload(snapshot, selection),
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            transaction,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=case.status,
            conflict_codes=(),
        )
        recognition: RecognizeFeeObligationResult = recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=case_id,
                source_activity_id=source.activity_id,
                source_document_id=None,
                fee_domain=FeeDomain.SERVICE,
                obligation_type="SERVICE_FEE",
                due_date=None,
                currency=selection.items[0].currency,
                source_status=FeeSourceStatus.VERIFIED,
                lines=tuple(
                    FeeObligationLineInput(
                        fee_code=item.item_code,
                        fee_name=item.name_zh_cn,
                        fee_year_key=0,
                        official_full_amount=None,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=item.amount,
                        source_amount=item.amount,
                        source_date=recognized_at.date(),
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    )
                    for item in selection.items
                ),
                actor_id=actor_id,
                idempotency_key=recognition_key,
                supersedes_obligation_id=None,
                supersede_reason=None,
            ),
            transaction,
        )
        if source.reused != recognition.reused:
            raise BusinessError(
                code="DEMO_SERVICE_IDEMPOTENCY_CONFLICT",
                message="本地演示服务费幂等状态冲突",
                status_code=409,
            )

    return DemoServiceObligationResult(
        classification=selection.classification,
        bundle_id=selection.bundle_id,
        bundle_version=selection.bundle_version,
        manifest_sha256=selection.manifest_sha256,
        template_code=selection.template_code,
        template_sha256=selection.template_sha256,
        template_required_variables=selection.template_required_variables,
        items=selection.items,
        total_amount=selection.total_amount,
        obligation=recognition.obligation,
        source_activity_id=source.activity_id,
        idempotency_key=idempotency_key,
        reused=recognition.reused,
    )


def _adjustment_conflict(message: str = "服务费草单调整状态冲突") -> None:
    raise BusinessError(
        code="DEMO_SERVICE_ADJUSTMENT_CONFLICT",
        message=message,
        status_code=409,
    )


def _stored_adjustment_payload(activity: CaseActivityEvent) -> dict[str, object]:
    try:
        payload = json.loads(activity.payload_json)
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _adjustment_conflict("服务费草单调整记录无效")
    if type(payload) is not dict or canonical != activity.payload_json:
        _adjustment_conflict("服务费草单调整记录无效")
    return payload


def _snapshot_digest(rows: list[dict[str, object]]) -> str:
    raw = json.dumps(
        rows,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _service_source_rows(
    transaction: Session,
    source_activity_id: str,
    *,
    case_id: str,
) -> tuple[CaseActivityEvent, tuple[dict[str, object], ...]]:
    source = transaction.get(CaseActivityEvent, source_activity_id)
    if (
        source is None
        or source.case_id != case_id
        or source.activity_type != "DEMO_SERVICE_PRICE_ITEM_SELECTED"
        or source.lane != ActivityLane.FEE.value
        or source.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or source.source_activity_id is not None
        or source.supersedes_event_id is not None
    ):
        _adjustment_conflict("服务费来源记录不存在")
    payload = _stored_adjustment_payload(source)
    rows = payload.get("items")
    snapshot = _bundle()
    if snapshot.schema_version != _INTEGRATED_SCHEMA:
        _adjustment_conflict("服务费运行输入无效")
    selection = _demo_service_items(snapshot)
    evidence = tuple(
        transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == source.id
            )
        )
    )
    expected_object_id = str(UUID(snapshot.manifest_sha256[:32]))
    if (
        payload != _service_source_payload(snapshot, selection)
        or type(rows) is not list
        or len(rows) < 2
        or any(type(row) is not dict for row in rows)
        or any(
            type(row.get("item_code")) is not str
            or type(row.get("source_ref")) is not str
            or type(row.get("source_version")) is not str
            or type(row.get("source_sha256")) is not str
            or len(str(row.get("source_sha256"))) != 64
            for row in rows
        )
        or len({row.get("item_code") for row in rows}) != len(rows)
        or len(evidence) != 1
        or evidence[0].case_id != case_id
        or evidence[0].evidence_kind != "DEMO_SERVICE_BUNDLE"
        or evidence[0].object_type != "DemoBundle"
        or evidence[0].object_id != expected_object_id
        or evidence[0].content_hash != snapshot.manifest_sha256
    ):
        _adjustment_conflict("服务费来源记录无效")
    return source, tuple(rows)


def _service_adjustment_replay(
    command: DemoServiceAdjustmentCommand,
    transaction: Session,
    activity: CaseActivityEvent,
) -> DemoServiceAdjustmentResult:
    payload = _stored_adjustment_payload(activity)
    if (
        set(payload)
        != {
            "schema",
            "draft_id",
            "item_id",
            "expected_quantity",
            "new_quantity",
            "reason",
            "actor_id",
            "original_obligation_id",
            "original_instruction_activity_id",
            "source_activity_id",
            "before_lines",
            "after_lines",
            "before_digest",
            "after_digest",
            "before_total",
            "after_total",
        }
        or payload.get("schema") != "FPMS_DEMO_SERVICE_DRAFT_ADJUSTED_V1"
        or payload.get("draft_id") != command.draft_id
        or payload.get("item_id") != command.item_id
        or payload.get("expected_quantity") != command.expected_quantity
        or payload.get("new_quantity") != command.new_quantity
        or payload.get("reason") != command.reason
        or payload.get("actor_id") != command.actor_id
        or activity.activity_type != "DEMO_SERVICE_DRAFT_ADJUSTED"
        or activity.lane != ActivityLane.FEE.value
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.actor_id != command.actor_id
        or activity.reviewer_id is not None
        or activity.supersedes_event_id is not None
        or activity.idempotency_key
        != f"demo-service-adjustment:{command.idempotency_key}"
    ):
        _adjustment_conflict("服务费草单调整幂等输入冲突")
    original_id = payload.get("original_obligation_id")
    if type(original_id) is not str:
        _adjustment_conflict("服务费草单调整记录无效")
    children = tuple(
        transaction.scalars(
            select(FeeObligation).where(
                FeeObligation.supersedes_obligation_id == original_id,
                FeeObligation.source_activity_id == activity.id,
            )
        )
    )
    instruction = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == activity.case_id,
            CaseActivityEvent.idempotency_key
            == f"demo-service-adjustment-pay:{command.idempotency_key}",
        )
    )
    draft = transaction.get(FeeDraft, command.draft_id)
    if len(children) != 1 or instruction is None or draft is None:
        _adjustment_conflict("服务费草单调整结果不完整")
    child = children[0]
    items = tuple(
        transaction.scalars(
            select(FeeItem)
            .where(FeeItem.draft_id == draft.id)
            .order_by(FeeItem.fee_code, FeeItem.id)
        )
    )
    links = tuple(
        transaction.scalars(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.fee_item_id.in_(
                    tuple(item.id for item in items)
                )
            )
        )
    )
    original = transaction.get(FeeObligation, original_id)
    original_lines = tuple(
        transaction.scalars(
            select(FeeObligationLine)
            .where(FeeObligationLine.obligation_id == original_id)
            .order_by(FeeObligationLine.fee_code, FeeObligationLine.id)
        )
    )
    replacement_lines = tuple(
        transaction.scalars(
            select(FeeObligationLine)
            .where(FeeObligationLine.obligation_id == child.id)
            .order_by(FeeObligationLine.fee_code, FeeObligationLine.id)
        )
    )
    before_rows = payload.get("before_lines")
    after_rows = payload.get("after_lines")
    if (
        type(before_rows) is not list
        or type(after_rows) is not list
        or len(before_rows) != len(after_rows)
        or any(type(row) is not dict for row in before_rows + after_rows)
        or any(
            set(row)
            != {
                "fee_code",
                "fee_name",
                "fee_item_id",
                "quantity",
                "unit_price",
                "amount",
                "source_sha256",
            }
            for row in before_rows + after_rows
        )
    ):
        _adjustment_conflict("服务费草单调整记录无效")
    try:
        before_total = Decimal(str(payload["before_total"]))
        after_total = Decimal(str(payload["after_total"]))
        recomputed_before_total = sum(
            (Decimal(str(row["amount"])) for row in before_rows), Decimal("0.00")
        )
        recomputed_after_total = sum(
            (Decimal(str(row["amount"])) for row in after_rows), Decimal("0.00")
        )
    except (InvalidOperation, KeyError, TypeError, ValueError):
        _adjustment_conflict("服务费草单调整记录无效")
    if (
        payload.get("before_digest") != _snapshot_digest(before_rows)
        or payload.get("after_digest") != _snapshot_digest(after_rows)
        or before_total != recomputed_before_total
        or after_total != recomputed_after_total
    ):
        _adjustment_conflict("服务费草单调整记录无效")
    source_id = payload.get("source_activity_id")
    original_instruction_id = payload.get("original_instruction_activity_id")
    if type(source_id) is not str or type(original_instruction_id) is not str:
        _adjustment_conflict("服务费草单调整记录无效")
    _source, source_rows = _service_source_rows(
        transaction,
        source_id,
        case_id=activity.case_id,
    )
    original_instruction = transaction.get(
        CaseActivityEvent,
        original_instruction_id,
    )
    if original_instruction is None:
        _adjustment_conflict("服务费草单调整记录无效")
    original_instruction_payload = _stored_adjustment_payload(original_instruction)
    instruction_payload = _stored_adjustment_payload(instruction)
    original_recognition = transaction.get(
        CaseActivityEvent,
        original_instruction.source_activity_id,
    )
    replacement_recognition = transaction.get(
        CaseActivityEvent,
        instruction.source_activity_id,
    )
    if original_recognition is None or replacement_recognition is None:
        _adjustment_conflict("服务费草单调整谱系无效")
    original_recognition_payload = _stored_adjustment_payload(original_recognition)
    replacement_recognition_payload = _stored_adjustment_payload(
        replacement_recognition
    )
    if (
        activity.source_activity_id != original_instruction_id
        or activity.case_id != draft.case_id
        or original_instruction.activity_type != "FEE_CLIENT_INSTRUCTION_RECORDED"
        or original_instruction.case_id != activity.case_id
        or original_instruction_payload.get("obligation_id") != original_id
        or original_instruction_payload.get("instruction") != "PAY"
        or original_recognition.activity_type != "FEE_OBLIGATION_RECOGNIZED"
        or original_recognition.case_id != activity.case_id
        or original_recognition.source_activity_id != source_id
        or original_recognition_payload.get("obligation_id") != original_id
        or instruction.activity_type != "FEE_CLIENT_INSTRUCTION_RECORDED"
        or instruction.case_id != activity.case_id
        or instruction.supersedes_event_id is not None
        or instruction_payload.get("obligation_id") != child.id
        or instruction_payload.get("instruction") != "PAY"
        or instruction_payload.get("actor_id") != command.actor_id
        or replacement_recognition.activity_type != "FEE_OBLIGATION_RECOGNIZED"
        or replacement_recognition.case_id != activity.case_id
        or replacement_recognition.source_activity_id != activity.id
        or replacement_recognition_payload.get("obligation_id") != child.id
    ):
        _adjustment_conflict("服务费草单调整谱系无效")
    item_by_id = {item.id: item for item in items}
    item_by_code = {item.fee_code: item for item in items}
    source_by_code = {row.get("item_code"): row for row in source_rows}
    original_by_code = {line.fee_code: line for line in original_lines}
    replacement_by_code = {line.fee_code: line for line in replacement_lines}
    if (
        not items
        or len(item_by_id) != len(items)
        or len(item_by_code) != len(items)
        or len(source_by_code) != len(source_rows)
        or len(original_by_code) != len(original_lines)
        or len(replacement_by_code) != len(replacement_lines)
        or set(item_by_code) != set(source_by_code)
        or set(item_by_code) != set(original_by_code)
        or set(item_by_code) != set(replacement_by_code)
        or command.item_id not in item_by_id
    ):
        _adjustment_conflict("服务费草单调整结果漂移")
    expected_before: list[dict[str, object]] = []
    expected_after: list[dict[str, object]] = []
    for code in sorted(source_by_code):
        source_row = source_by_code[code]
        item = item_by_code[code]
        original_line = original_by_code[code]
        replacement_line = replacement_by_code[code]
        try:
            source_quantity = source_row["quantity"]
            source_unit_price = Decimal(str(source_row["unit_price"]))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            _adjustment_conflict("服务费草单调整记录无效")
        if type(source_quantity) is not int or source_quantity <= 0:
            _adjustment_conflict("服务费草单调整记录无效")
        after_quantity = (
            command.new_quantity if item.id == command.item_id else source_quantity
        )
        before_amount = source_unit_price * source_quantity
        after_amount = source_unit_price * after_quantity
        if (
            original_line.case_id != activity.case_id
            or original_line.obligation_id != original_id
            or original_line.source_activity_id != source_id
            or original_line.payable_amount != before_amount
            or original_line.source_amount != before_amount
            or replacement_line.case_id != activity.case_id
            or replacement_line.obligation_id != child.id
            or replacement_line.source_activity_id != activity.id
            or replacement_line.fee_name != original_line.fee_name
            or replacement_line.payable_amount != after_amount
            or replacement_line.source_amount != after_amount
            or replacement_line.source_date != original_line.source_date
            or item.fee_type != FeeDomain.SERVICE.value
            or item.fee_name != original_line.fee_name
            or item.amount != after_amount
            or (item.quantity is None) != (item.unit_price is None)
            or (
                item.quantity is not None
                and (
                    item.quantity != Decimal(after_quantity)
                    or item.unit_price != source_unit_price
                )
            )
            or (item.id == command.item_id and item.quantity is None)
        ):
            _adjustment_conflict("服务费草单调整结果漂移")
        before = {
            "fee_code": code,
            "fee_name": original_line.fee_name,
            "fee_item_id": item.id,
            "quantity": source_quantity,
            "unit_price": format(source_unit_price, ".2f"),
            "amount": format(before_amount, ".2f"),
            "source_sha256": source_row.get("source_sha256"),
        }
        expected_before.append(before)
        expected_after.append(
            {
                **before,
                "quantity": after_quantity,
                "amount": format(after_amount, ".2f"),
            }
        )
    target = item_by_id[command.item_id]
    target_source = source_by_code[target.fee_code]
    if (
        before_rows != expected_before
        or after_rows != expected_after
        or target_source.get("adjustable") is not True
        or target_source.get("final_quantity") != command.new_quantity
    ):
        _adjustment_conflict("服务费草单调整结果漂移")
    link_by_item = {link.fee_item_id: link for link in links}
    if (
        len(links) != len(items)
        or len(link_by_item) != len(items)
        or {link.obligation_line_id for link in links}
        != {line.id for line in replacement_lines}
        or any(
            link_by_item[item.id].obligation_line_id
            != replacement_by_code[item.fee_code].id
            for item in items
        )
    ):
        _adjustment_conflict("服务费草单调整关联漂移")
    if (
        draft.status not in {"OPEN", "LOCKED"}
        or original is None
        or original.obligation_status != FeeObligationStatus.SUPERSEDED.value
        or original.client_instruction_status != FeeClientInstructionStatus.PAY.value
        or original.draft_status != FeeObligationDraftStatus.NOT_CREATED.value
        or child.obligation_status != FeeObligationStatus.RECOGNIZED.value
        or child.client_instruction_status != FeeClientInstructionStatus.PAY.value
        or child.draft_status != FeeObligationDraftStatus.CREATED.value
        or child.supersedes_obligation_id != original_id
        or child.source_activity_id != activity.id
        or draft.total_gov != Decimal("0.00")
        or draft.total_misc != Decimal("0.00")
        or after_total != draft.total_service
        or after_total != draft.amount
    ):
        _adjustment_conflict("服务费草单调整结果漂移")
    get_fee_obligation(original_id, transaction)
    get_fee_obligation(child.id, transaction)
    return DemoServiceAdjustmentResult(
        draft_id=draft.id,
        original_obligation_id=original_id,
        superseding_obligation_id=child.id,
        adjustment_activity_id=activity.id,
        instruction_activity_id=instruction.id,
        fee_item_ids=tuple(item.id for item in items),
        before_total=before_total,
        after_total=after_total,
        idempotency_key=command.idempotency_key,
        reused=True,
    )


def _validated_service_adjustment_activity(
    transaction: Session,
    activity: CaseActivityEvent,
) -> tuple[dict[str, object], DemoServiceAdjustmentResult]:
    payload = _stored_adjustment_payload(activity)
    prefix = "demo-service-adjustment:"
    values = (
        payload.get("draft_id"),
        payload.get("item_id"),
        payload.get("reason"),
        payload.get("actor_id"),
    )
    if (
        any(type(value) is not str or not value for value in values)
        or type(payload.get("expected_quantity")) is not int
        or type(payload.get("new_quantity")) is not int
        or not activity.idempotency_key.startswith(prefix)
        or not activity.idempotency_key[len(prefix) :]
    ):
        _adjustment_conflict("服务费草单调整记录无效")
    command = DemoServiceAdjustmentCommand(
        draft_id=str(payload["draft_id"]),
        item_id=str(payload["item_id"]),
        expected_quantity=int(payload["expected_quantity"]),
        new_quantity=int(payload["new_quantity"]),
        reason=str(payload["reason"]),
        actor_id=str(payload["actor_id"]),
        idempotency_key=activity.idempotency_key[len(prefix) :],
        adjusted_at=activity.effective_at,
    )
    return payload, _service_adjustment_replay(command, transaction, activity)


def adjust_demo_service_draft(
    command: DemoServiceAdjustmentCommand,
    transaction: Session,
) -> DemoServiceAdjustmentResult:
    if (
        type(command) is not DemoServiceAdjustmentCommand
        or type(command.expected_quantity) is not int
        or type(command.new_quantity) is not int
        or command.expected_quantity <= 0
        or command.new_quantity <= 0
        or type(command.adjusted_at) is not datetime
        or command.adjusted_at.tzinfo is not None
        or any(
            type(value) is not str
            or not value
            or value != value.strip()
            or "\x00" in value
            or len(value) > limit
            for value, limit in (
                (command.draft_id, 36),
                (command.item_id, 36),
                (command.reason, 256),
                (command.actor_id, 36),
                (command.idempotency_key, 96),
            )
        )
        or not any("\u4e00" <= char <= "\u9fff" for char in command.reason)
    ):
        raise BusinessError(
            code="DEMO_SERVICE_ADJUSTMENT_INPUT_INVALID",
            message="服务费草单调整输入无效",
            status_code=400,
        )
    if transaction.new or transaction.dirty or transaction.deleted:
        _adjustment_conflict("服务费草单调整事务状态冲突")
    connection = transaction.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        try:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        except OperationalError as exc:
            raise BusinessError(
                code="DEMO_SERVICE_ADJUSTMENT_CONFLICT",
                message="服务费草单正在被其他操作修改",
                status_code=409,
            ) from exc

    draft = transaction.scalar(
        select(FeeDraft)
        .where(FeeDraft.id == command.draft_id)
        .with_for_update()
    )
    if draft is None:
        raise BusinessError(
            code="FEE_DRAFT_NOT_FOUND",
            message="费用草单不存在",
            status_code=404,
        )
    existing = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == draft.case_id,
            CaseActivityEvent.idempotency_key
            == f"demo-service-adjustment:{command.idempotency_key}"
        )
    )
    if existing is not None:
        if existing.activity_type != "DEMO_SERVICE_DRAFT_ADJUSTED":
            _adjustment_conflict("服务费草单调整幂等键冲突")
        return _service_adjustment_replay(command, transaction, existing)

    if draft.status != "OPEN" or draft.total_gov != Decimal("0.00"):
        _adjustment_conflict("只有未锁定的服务费草单可以调整")
    if transaction.scalar(
        select(BillDraftSource.id).where(BillDraftSource.draft_id == draft.id)
    ) is not None:
        _adjustment_conflict("已生成账单的服务费草单不能调整")
    items = tuple(
        transaction.scalars(
            select(FeeItem)
            .where(FeeItem.draft_id == draft.id)
            .order_by(FeeItem.fee_code, FeeItem.id)
            .with_for_update()
        )
    )
    if len(items) < 2 or any(item.fee_type != FeeDomain.SERVICE.value for item in items):
        _adjustment_conflict("服务费草单明细无效")
    links = tuple(
        transaction.scalars(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.fee_item_id.in_(tuple(item.id for item in items))
            ).with_for_update()
        )
    )
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine).where(
                FeeObligationLine.id.in_(tuple(link.obligation_line_id for link in links))
            ).with_for_update()
        )
    )
    obligation_ids = {line.obligation_id for line in lines}
    if len(links) != len(items) or len(lines) != len(items) or len(obligation_ids) != 1:
        _adjustment_conflict("服务费草单关联不完整")
    original = transaction.scalar(
        select(FeeObligation)
        .where(FeeObligation.id == obligation_ids.pop())
        .with_for_update()
    )
    if original is None:
        _adjustment_conflict("服务费义务不存在")
    get_fee_obligation(original.id, transaction)
    if (
        original.fee_domain != FeeDomain.SERVICE.value
        or original.obligation_status != FeeObligationStatus.RECOGNIZED.value
        or original.client_instruction_status != FeeClientInstructionStatus.PAY.value
        or original.draft_status != FeeObligationDraftStatus.CREATED.value
        or original.payment_status != FeePaymentStatus.UNPAID.value
        or original.official_evidence_status
        != FeeOfficialEvidenceStatus.NOT_APPLICABLE.value
    ):
        _adjustment_conflict("服务费义务状态不允许调整")
    if transaction.scalar(
        select(FeeObligation.id).where(
            FeeObligation.supersedes_obligation_id == original.id
        )
    ) is not None:
        _adjustment_conflict("服务费草单只允许调整一次")

    source, source_rows = _service_source_rows(
        transaction,
        original.source_activity_id,
        case_id=original.case_id,
    )
    source_by_code = {str(row.get("item_code")): row for row in source_rows}
    item_by_code = {str(item.fee_code): item for item in items}
    line_by_code = {line.fee_code: line for line in lines}
    if set(source_by_code) != set(item_by_code) or set(item_by_code) != set(line_by_code):
        _adjustment_conflict("服务费来源与草单明细不一致")
    selected = next((item for item in items if item.id == command.item_id), None)
    if selected is None:
        raise BusinessError(
            code="FEE_ITEM_NOT_FOUND",
            message="费用明细不存在",
            status_code=404,
        )
    selected_source = None if selected is None else source_by_code.get(str(selected.fee_code))
    if (
        selected_source is None
        or selected_source.get("adjustable") is not True
        or selected_source.get("final_quantity") != command.new_quantity
    ):
        _adjustment_conflict("服务费项目或目标数量不符合已授权配置")

    prior_instruction = None
    for candidate in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == original.case_id,
            CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED",
        )
    ):
        candidate_payload = _stored_adjustment_payload(candidate)
        if (
            candidate_payload.get("obligation_id") == original.id
            and candidate_payload.get("instruction") == "PAY"
        ):
            if prior_instruction is not None:
                _adjustment_conflict("服务费收费指示记录不唯一")
            prior_instruction = candidate
    if prior_instruction is None:
        _adjustment_conflict("服务费收费指示记录不存在")
    for candidate in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == original.case_id,
            CaseActivityEvent.activity_type == "DEMO_SERVICE_DRAFT_ADJUSTED",
        )
    ):
        if _stored_adjustment_payload(candidate).get("draft_id") == draft.id:
            _adjustment_conflict("服务费草单只允许调整一次")

    before_rows: list[dict[str, object]] = []
    after_rows: list[dict[str, object]] = []
    for code in sorted(source_by_code):
        row = source_by_code[code]
        item = item_by_code[code]
        line = line_by_code[code]
        try:
            unit_price = Decimal(str(row["unit_price"]))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            _adjustment_conflict("服务费来源金额无效")
        quantity = row.get("quantity")
        if type(quantity) is not int or quantity <= 0:
            _adjustment_conflict("服务费来源数量无效")
        amount = unit_price * quantity
        if (
            item.amount != amount
            or line.payable_amount != amount
            or (item.quantity is not None and item.quantity != Decimal(quantity))
            or (item.unit_price is not None and item.unit_price != unit_price)
            or (item.quantity is None) != (item.unit_price is None)
        ):
            _adjustment_conflict("服务费来源金额与草单不一致")
        if item.id == command.item_id and quantity != command.expected_quantity:
            _adjustment_conflict("服务费项目当前数量已变化")
        before = {
            "fee_code": code,
            "fee_name": line.fee_name,
            "fee_item_id": item.id,
            "quantity": quantity,
            "unit_price": format(unit_price, ".2f"),
            "amount": format(amount, ".2f"),
            "source_sha256": row.get("source_sha256"),
        }
        after_quantity = command.new_quantity if item.id == command.item_id else quantity
        after = {**before, "quantity": after_quantity}
        after["amount"] = format(unit_price * after_quantity, ".2f")
        before_rows.append(before)
        after_rows.append(after)
    before_total = sum(
        (Decimal(str(row["amount"])) for row in before_rows), Decimal("0.00")
    )
    after_total = sum(
        (Decimal(str(row["amount"])) for row in after_rows), Decimal("0.00")
    )
    if draft.total_service != before_total or draft.amount != before_total:
        _adjustment_conflict("服务费草单合计已变化")
    payload = {
        "schema": "FPMS_DEMO_SERVICE_DRAFT_ADJUSTED_V1",
        "draft_id": draft.id,
        "item_id": command.item_id,
        "expected_quantity": command.expected_quantity,
        "new_quantity": command.new_quantity,
        "reason": command.reason,
        "actor_id": command.actor_id,
        "original_obligation_id": original.id,
        "original_instruction_activity_id": prior_instruction.id,
        "source_activity_id": source.id,
        "before_lines": before_rows,
        "after_lines": after_rows,
        "before_digest": _snapshot_digest(before_rows),
        "after_digest": _snapshot_digest(after_rows),
        "before_total": format(before_total, ".2f"),
        "after_total": format(after_total, ".2f"),
    }
    projection = _projection(transaction.get(Case, original.case_id))
    with transaction.begin_nested():
        adjustment = append_case_activity(
            LifecycleEventCommand(
                case_id=original.case_id,
                event_type="DEMO_SERVICE_DRAFT_ADJUSTED",
                lane=ActivityLane.FEE,
                effective_at=command.adjusted_at,
                occurred_at=command.adjusted_at,
                evidence_refs=(),
                actor_id=command.actor_id,
                reviewer_id=None,
                idempotency_key=f"demo-service-adjustment:{command.idempotency_key}",
                source_activity_id=prior_instruction.id,
                supersedes_event_id=None,
                payload=payload,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            ),
            transaction,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status=transaction.get(Case, original.case_id).status,
            conflict_codes=(),
        )
        replacement = recognize_obligation(
            RecognizeFeeObligationCommand(
                case_id=original.case_id,
                source_activity_id=adjustment.activity_id,
                source_document_id=None,
                fee_domain=FeeDomain.SERVICE,
                obligation_type=original.obligation_type,
                due_date=original.due_date,
                currency=original.currency,
                source_status=FeeSourceStatus.VERIFIED,
                lines=tuple(
                    FeeObligationLineInput(
                        fee_code=str(row["fee_code"]),
                        fee_name=str(row["fee_name"]),
                        fee_year_key=0,
                        official_full_amount=None,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=Decimal(str(row["amount"])),
                        source_amount=Decimal(str(row["amount"])),
                        source_date=line_by_code[str(row["fee_code"])].source_date,
                        difference_review_state=FeeDifferenceReviewState.MATCHED,
                    )
                    for row in after_rows
                ),
                actor_id=command.actor_id,
                idempotency_key=(
                    f"demo-service-adjustment-obligation:{command.idempotency_key}"
                ),
                supersedes_obligation_id=original.id,
                supersede_reason=command.reason,
            ),
            transaction,
        )
        instruction = record_client_instruction(
            RecordFeeObligationInstructionCommand(
                obligation_id=replacement.obligation.id,
                instruction=FeeClientInstruction.PAY,
                actor_id=command.actor_id,
                idempotency_key=f"demo-service-adjustment-pay:{command.idempotency_key}",
            ),
            transaction,
        )
        replacement_lines = {
            line.fee_code: line
            for line in transaction.scalars(
                select(FeeObligationLine).where(
                    FeeObligationLine.obligation_id == replacement.obligation.id
                )
            )
        }
        link_by_item = {link.fee_item_id: link for link in links}
        target_source = source_by_code[str(selected.fee_code)]
        target_unit_price = Decimal(str(target_source["unit_price"]))
        target_changed = transaction.execute(
            update(FeeItem)
            .where(
                FeeItem.id == selected.id,
                FeeItem.draft_id == draft.id,
                FeeItem.amount == selected.amount,
                (
                    FeeItem.quantity.is_(None)
                    if selected.quantity is None
                    else FeeItem.quantity == selected.quantity
                ),
                (
                    FeeItem.unit_price.is_(None)
                    if selected.unit_price is None
                    else FeeItem.unit_price == selected.unit_price
                ),
            )
            .values(
                quantity=Decimal(command.new_quantity),
                unit_price=target_unit_price,
                amount=target_unit_price * command.new_quantity,
                updated_by=command.actor_id,
            )
            .execution_options(synchronize_session=False)
        )
        if target_changed.rowcount != 1:
            _adjustment_conflict("服务费草单明细并发变化")
        for item in items:
            link = link_by_item[item.id]
            relinked = transaction.execute(
                update(FeeObligationDraftItemLink)
                .where(
                    FeeObligationDraftItemLink.id == link.id,
                    FeeObligationDraftItemLink.fee_item_id == item.id,
                    FeeObligationDraftItemLink.obligation_line_id
                    == link.obligation_line_id,
                )
                .values(
                    obligation_line_id=replacement_lines[str(item.fee_code)].id,
                    updated_by=command.actor_id,
                )
                .execution_options(synchronize_session=False)
            )
            if relinked.rowcount != 1:
                _adjustment_conflict("服务费草单关联并发变化")
        draft_cas = transaction.execute(
            update(FeeDraft)
            .where(
                FeeDraft.id == draft.id,
                FeeDraft.status == "OPEN",
                FeeDraft.total_gov == Decimal("0.00"),
                FeeDraft.total_service == before_total,
                FeeDraft.amount == before_total,
            )
            .values(
                total_service=after_total,
                amount=after_total,
                updated_by=command.actor_id,
            )
            .execution_options(synchronize_session=False)
        )
        original_cas = transaction.execute(
            update(FeeObligation)
            .where(
                FeeObligation.id == original.id,
                FeeObligation.obligation_status == FeeObligationStatus.SUPERSEDED.value,
                FeeObligation.client_instruction_status
                == FeeClientInstructionStatus.PAY.value,
                FeeObligation.draft_status == FeeObligationDraftStatus.CREATED.value,
                FeeObligation.payment_status == FeePaymentStatus.UNPAID.value,
                FeeObligation.official_evidence_status
                == FeeOfficialEvidenceStatus.NOT_APPLICABLE.value,
            )
            .values(draft_status=FeeObligationDraftStatus.NOT_CREATED.value)
            .execution_options(synchronize_session=False)
        )
        replacement_cas = transaction.execute(
            update(FeeObligation)
            .where(
                FeeObligation.id == replacement.obligation.id,
                FeeObligation.obligation_status == FeeObligationStatus.RECOGNIZED.value,
                FeeObligation.client_instruction_status
                == FeeClientInstructionStatus.PAY.value,
                FeeObligation.draft_status == FeeObligationDraftStatus.NOT_CREATED.value,
                FeeObligation.payment_status == FeePaymentStatus.UNPAID.value,
                FeeObligation.official_evidence_status
                == FeeOfficialEvidenceStatus.NOT_APPLICABLE.value,
            )
            .values(draft_status=FeeObligationDraftStatus.CREATED.value)
            .execution_options(synchronize_session=False)
        )
        if (
            draft_cas.rowcount != 1
            or original_cas.rowcount != 1
            or replacement_cas.rowcount != 1
        ):
            _adjustment_conflict("服务费草单调整状态并发变化")
        transaction.flush()
        transaction.expire_all()
        get_fee_obligation(original.id, transaction)
        get_fee_obligation(replacement.obligation.id, transaction)
        validated_draft = get_fee_draft(transaction, draft_id=draft.id)
        validated_items = list_fee_items(transaction, draft_id=draft.id)
        if (
            validated_draft.status != "OPEN"
            or validated_draft.total_service != after_total
            or validated_draft.amount != after_total
            or {item.id for item in validated_items} != {item.id for item in items}
            or sum((item.amount for item in validated_items), Decimal("0.00"))
            != after_total
        ):
            _adjustment_conflict("服务费草单调整结果无效")
    return DemoServiceAdjustmentResult(
        draft_id=draft.id,
        original_obligation_id=original.id,
        superseding_obligation_id=replacement.obligation.id,
        adjustment_activity_id=adjustment.activity_id,
        instruction_activity_id=instruction.activity_id,
        fee_item_ids=tuple(item.id for item in items),
        before_total=before_total,
        after_total=after_total,
        idempotency_key=command.idempotency_key,
        reused=False,
    )
