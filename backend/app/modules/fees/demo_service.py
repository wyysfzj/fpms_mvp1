from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.demo_bundle import DemoBundleError, DemoBundleSnapshot, load_demo_bundle
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
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
)
from app.modules.fees.obligation_service import recognize_obligation

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SOURCE_SCHEMA = "FPMS_DEMO_SERVICE_PRICE_ITEM_SELECTED_V1"


@dataclass(frozen=True, slots=True)
class DemoServiceItem:
    classification: str
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    template_code: str
    template_sha256: str
    template_required_variables: tuple[str, ...]
    item_code: str
    name_zh_cn: str
    currency: str
    amount: Decimal
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str


@dataclass(frozen=True, slots=True)
class DemoServiceObligationResult:
    classification: str
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    template_code: str
    template_sha256: str
    template_required_variables: tuple[str, ...]
    item_code: str
    name_zh_cn: str
    currency: str
    amount: Decimal
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str
    obligation: object
    source_activity_id: str
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
    root: str, manifest_digest: str, authority_digest: str
) -> DemoBundleSnapshot:
    try:
        return load_demo_bundle(
            Path(root),
            expected_manifest_sha256=manifest_digest,
            expected_authority_sha256=authority_digest,
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
    if not root or not digest or not authority_digest:
        raise _config_required("本地演示输入未配置")
    return _load_bundle_snapshot(root, digest, authority_digest)


def get_demo_service_item() -> DemoServiceItem:
    snapshot = _bundle()
    rate = snapshot.service_rate
    try:
        amount = Decimal(rate.amount)
    except InvalidOperation as exc:
        raise _config_required("本地演示服务费金额无效") from exc
    return DemoServiceItem(
        classification="DEMO_ONLY",
        bundle_id=snapshot.bundle_id,
        bundle_version=snapshot.bundle_version,
        manifest_sha256=snapshot.manifest_sha256,
        template_code=snapshot.template.template_code,
        template_sha256=snapshot.template.sha256,
        template_required_variables=snapshot.template.required_variables,
        item_code=rate.item_code,
        name_zh_cn=rate.name_zh_cn,
        currency=rate.currency,
        amount=amount,
        source_ref=rate.source_ref,
        source_version=rate.source_version,
        source_sha256=rate.source_sha256,
        disclaimer_zh_cn=rate.disclaimer_zh_cn,
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
    item_code: str,
    actor_id: str,
    idempotency_key: str,
    recognized_at: datetime,
) -> DemoServiceObligationResult:
    item = get_demo_service_item()
    if item_code != item.item_code:
        raise _config_required("本地演示服务费项目不存在")
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
    bundle_object_id = str(UUID(item.manifest_sha256[:32]))

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
                        content_hash=item.manifest_sha256,
                        captured_at=recognized_at,
                    ),
                ),
                actor_id=actor_id,
                reviewer_id=None,
                idempotency_key=source_key,
                source_activity_id=None,
                supersedes_event_id=None,
                payload={
                    "schema": _SOURCE_SCHEMA,
                    "bundle_id": item.bundle_id,
                    "bundle_version": item.bundle_version,
                    "manifest_sha256": item.manifest_sha256,
                    "item_code": item.item_code,
                    "name_zh_cn": item.name_zh_cn,
                    "currency": item.currency,
                    "amount": format(item.amount, ".2f"),
                    "source_ref": item.source_ref,
                    "source_version": item.source_version,
                    "source_sha256": item.source_sha256,
                    "disclaimer_zh_cn": item.disclaimer_zh_cn,
                },
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
                currency=item.currency,
                source_status=FeeSourceStatus.VERIFIED,
                lines=(
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
                    ),
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
        classification=item.classification,
        bundle_id=item.bundle_id,
        bundle_version=item.bundle_version,
        manifest_sha256=item.manifest_sha256,
        template_code=item.template_code,
        template_sha256=item.template_sha256,
        template_required_variables=item.template_required_variables,
        item_code=item.item_code,
        name_zh_cn=item.name_zh_cn,
        currency=item.currency,
        amount=item.amount,
        source_ref=item.source_ref,
        source_version=item.source_version,
        source_sha256=item.source_sha256,
        disclaimer_zh_cn=item.disclaimer_zh_cn,
        obligation=recognition.obligation,
        source_activity_id=source.activity_id,
        idempotency_key=idempotency_key,
        reused=recognition.reused,
    )
