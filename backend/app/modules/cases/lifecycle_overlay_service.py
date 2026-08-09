from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import TypeVar, cast

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.cases.lifecycle_activity_service import read_activity_conflict_codes
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_schemas import (
    LifecycleOverlay,
    OverlayCenterAxis,
    OverlayCenterAxisChange,
    OverlayCenterSnapshot,
    OverlayDecisionGate,
    OverlayDocumentEvidence,
    OverlayFeeLine,
    OverlayFeeObligation,
    OverlayFeeRelatedFact,
    OverlayFeeRelatedFactKind,
    OverlayGateResolutionStatus,
    OverlayLegacyConflict,
    OverlayMilestone,
    OverlayTask,
    OverlayWarning,
    OverlayWarningKind,
    OverlayWorkPackage,
    OverlayWorkPackageReceipt,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)
from app.modules.fees.models import (
    FeeObligation as FeeObligationModel,
)
from app.modules.fees.obligation_service import get_fee_obligation
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)
from app.modules.official_workflows.schemas import (
    OFFICIAL_WORK_PACKAGE_KINDS,
    OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS,
    OFFICIAL_WORK_PACKAGE_STATUSES,
)
from app.modules.official_workflows.service import evaluate_official_work_package
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)
from app.modules.tasks.enums import TaskStatus
from app.modules.tasks.models import Task

__all__ = ("read_lifecycle_overlay",)

_EnumT = TypeVar("_EnumT")
_DECISION_GATE_UNRESOLVED_CODES = frozenset(
    {
        "DECISION_GATE_NOT_FOUND",
        "DECISION_GATE_REVOKED",
        "DECISION_GATE_NOT_EFFECTIVE",
        "DECISION_GATE_CANDIDATE_MULTIPLICITY",
        "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        "DECISION_GATE_CURRENT_ROW_CORRUPT",
        "DECISION_GATE_LEGACY_MAP_CORRUPT",
    }
)
_DECISION_GATE_CASE_CODES = (
    DecisionGateCode.FEE_APPLICATION_DRAFT,
    DecisionGateCode.FEE_GRANT_YEAR_DRAFT,
    DecisionGateCode.FEE_FUTURE_ANNUITY,
    DecisionGateCode.GRANT_EVIDENCE_SOURCE,
    DecisionGateCode.GRANT_MANUAL_REVIEW,
    DecisionGateCode.PAYMENT_WORKBOOK,
    DecisionGateCode.SERVICE_RATE_VERSION,
)
_LEGACY_IMPORT_STATUSES = frozenset(
    {
        "NOT_FILED",
        "PENDING",
        "GRANTED",
        "REJECTED",
        "WITHDRAWN",
        "ABANDONED",
        "EXPIRED",
        "WAITING_RECEIPT",
        "PRELIM_EXAM",
        "PRELIM_PASS",
        "AMENDMENT",
        "PUBLISHED",
        "SUB_EXAM",
        "OA1",
        "OA2",
        "REEXAM",
        "ACCEPTED",
        "GRANT_PENDING",
        "TERMINATED",
        "INVALIDATED",
    }
)


def read_lifecycle_overlay(
    *,
    case_id: str,
    after_sequence: int,
    limit: int,
    as_of_revision: int | None,
    transaction: Session,
) -> LifecycleOverlay:
    generated_at = _utc_now()
    case_state = transaction.execute(
        select(
            Case.business_stage,
            Case.official_procedure_stage,
            Case.legal_status,
            Case.lifecycle_verification_status,
            Case.lifecycle_revision,
        ).where(Case.id == case_id)
    ).one_or_none()
    if case_state is None:
        _fail("CASE_NOT_FOUND", "案件不存在", status_code=404)

    current_revision = _current_revision(case_state)
    revision = current_revision if as_of_revision is None else as_of_revision
    if (
        not isinstance(after_sequence, int)
        or isinstance(after_sequence, bool)
        or not isinstance(limit, int)
        or isinstance(limit, bool)
        or not isinstance(revision, int)
        or isinstance(revision, bool)
        or after_sequence < 0
        or limit <= 0
        or revision < 0
        or revision > current_revision
        or after_sequence > revision
    ):
        _fail(
            "LIFECYCLE_OVERLAY_QUERY_INVALID",
            "生命周期视图查询参数无效",
            details={
                "case_id": case_id,
                "after_sequence": after_sequence,
                "limit": limit,
                "as_of_revision": as_of_revision,
                "current_revision": current_revision,
            },
            status_code=400,
        )

    activity_query = select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
    if as_of_revision is not None:
        activity_query = activity_query.where(CaseActivityEvent.sequence <= revision)
    activities = (
        transaction.execute(
            activity_query.order_by(CaseActivityEvent.sequence, CaseActivityEvent.id)
        )
        .scalars()
        .all()
    )
    if [activity.sequence for activity in activities] != list(range(1, revision + 1)):
        _state_conflict(case_id, "ACTIVITY_SEQUENCE_INVALID")

    parsed = _validate_and_parse_activities(case_id, activities)
    frozen = parsed
    first_lifecycle_activity_id = next(
        (item[0].id for item in frozen if item[1] is ActivityLane.LIFECYCLE),
        None,
    )
    center_activity = next(
        (item for item in reversed(frozen) if item[1] is ActivityLane.LIFECYCLE),
        None,
    )
    center_snapshot = _center_snapshot(case_id, revision, center_activity)
    if revision == current_revision:
        _validate_current_projection(case_id, case_state, center_snapshot, current_revision)

    page = tuple(item for item in frozen if after_sequence < item[0].sequence <= revision)[
        : limit + 1
    ]
    has_more = len(page) > limit
    if has_more:
        page = page[:limit]
    evidence_by_activity = _read_evidence(
        transaction,
        case_id=case_id,
        activity_ids=tuple(item[0].id for item in page),
    )
    document_facts = _read_document_facts(
        transaction,
        case_id=case_id,
        evidence_by_activity=evidence_by_activity,
    )
    fee_facts = _read_fee_facts(
        transaction,
        case_id=case_id,
        activities=tuple(item[0] for item in page),
    )
    conflict_codes_by_activity = read_activity_conflict_codes(
        transaction,
        tuple(item[0] for item in page),
    )
    milestones = tuple(
        _milestone(
            activity,
            lane,
            axes,
            evidence_by_activity.get(activity.id, ()),
            *document_facts.get(activity.id, ((), (), ())),
            fee_facts.get(activity.id, ()),
            conflict_codes_by_activity[activity.id],
        )
        for activity, lane, axes in page
    )
    decision_gates = _read_decision_gates(
        case_id=case_id,
        generated_at=generated_at,
        transaction=transaction,
    )
    gate_warnings = _decision_gate_warnings(decision_gates)
    warnings = tuple(
        warning for milestone in milestones for warning in milestone.warnings
    ) + gate_warnings
    legacy_conflicts = tuple(
        OverlayLegacyConflict(
            code=code,
            activity_id=activity.id,
            message="历史生命周期活动存在待核对冲突",
        )
        for activity, _lane, _axes in page
        if _is_exact_legacy_import(
            activity,
            evidence_by_activity.get(activity.id, ()),
        )
        and activity.id == first_lifecycle_activity_id
        for code in conflict_codes_by_activity[activity.id]
    )
    return LifecycleOverlay(
        case_id=case_id,
        lifecycle_revision=revision,
        generated_at=generated_at,
        center_snapshot=center_snapshot,
        milestones=milestones,
        decision_gates=decision_gates,
        warnings=warnings,
        legacy_conflicts=legacy_conflicts,
        next_cursor=page[-1][0].sequence if has_more else None,
        has_more=has_more,
    )


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _read_decision_gates(
    *,
    case_id: str,
    generated_at: datetime,
    transaction: Session,
) -> tuple[OverlayDecisionGate, ...]:
    commands = tuple(
        ResolveDecisionGateCommand(
            gate_code=gate_code,
            scope_key=scope_key,
            as_of=generated_at,
        )
        for gate_code, scope_key in (
            *((gate_code, f"case:{case_id}") for gate_code in _DECISION_GATE_CASE_CODES),
            *(
                (DecisionGateCode.LEGACY_FORM_CLASS, f"form-{number:03d}")
                for number in range(1, 23)
            ),
        )
    )
    result = []
    for command in commands:
        try:
            resolved = resolve_decision_gate(command, transaction)
        except BusinessError as error:
            if error.status_code == 409 and error.code in _DECISION_GATE_UNRESOLVED_CODES:
                result.append(
                    OverlayDecisionGate(
                        gate_code=command.gate_code,
                        requested_scope_key=command.scope_key,
                        resolution_status=OverlayGateResolutionStatus.UNRESOLVED,
                        gate_id=None,
                        resolved_scope_key=None,
                        decision_value=None,
                        source_reference=None,
                        source_version=None,
                        confirmed_by=None,
                        effective_at=None,
                        unresolved_reason=error.code,
                    )
                )
                continue
            if error.status_code == 400 and error.code == "DECISION_GATE_INVALID":
                _fail(
                    "LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID",
                    "生命周期决策门禁连接契约无效",
                    status_code=409,
                )
            raise
        result.append(
            OverlayDecisionGate(
                gate_code=resolved.gate_code,
                requested_scope_key=resolved.requested_scope_key,
                resolution_status=OverlayGateResolutionStatus.RESOLVED,
                gate_id=resolved.gate_id,
                resolved_scope_key=resolved.resolved_scope_key,
                decision_value=resolved.decision_value,
                source_reference=resolved.source_reference,
                source_version=resolved.source_version,
                confirmed_by=resolved.confirmed_by,
                effective_at=resolved.effective_at,
                unresolved_reason=None,
            )
        )
    return tuple(result)


def _current_revision(case_state: object) -> int:
    revision = case_state.lifecycle_revision
    carriers = (
        case_state.business_stage,
        case_state.official_procedure_stage,
        case_state.legal_status,
        case_state.lifecycle_verification_status,
    )
    if revision is None:
        if any(value is not None for value in carriers):
            _state_conflict(None, "REVISION_MISSING")
        return 0
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        _state_conflict(None, "REVISION_INVALID")
    if revision == 0 and any(value is not None for value in carriers):
        _state_conflict(None, "ZERO_REVISION_HAS_PROJECTION")
    return revision


def _validate_and_parse_activities(
    case_id: str,
    activities: list[CaseActivityEvent],
) -> tuple[
    tuple[
        CaseActivityEvent,
        ActivityLane,
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ],
    ],
    ...,
]:
    result = []
    projection: (
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ]
        | None
    ) = None
    for activity in activities:
        try:
            lane = ActivityLane(activity.lane)
            ConfirmationStatus(activity.confirmation_status)
            old_axes = (
                _parse_optional(activity.old_business_stage, BusinessStage),
                _parse_optional(
                    activity.old_official_procedure_stage,
                    OfficialProcedureStage,
                ),
                _parse_optional(activity.old_legal_status, LegalStatus),
            )
            new_axes = (
                _parse_optional(activity.new_business_stage, BusinessStage),
                _parse_optional(
                    activity.new_official_procedure_stage,
                    OfficialProcedureStage,
                ),
                _parse_optional(activity.new_legal_status, LegalStatus),
            )
        except (TypeError, ValueError):
            _state_conflict(case_id, "ACTIVITY_ENUM_INVALID")
        if projection is not None and old_axes != projection:
            _state_conflict(case_id, "ACTIVITY_PROJECTION_GAP")
        if lane is not ActivityLane.LIFECYCLE and old_axes != new_axes:
            _state_conflict(case_id, "NON_LIFECYCLE_CENTER_CHANGE")
        projection = new_axes
        result.append((activity, lane, (*old_axes, *new_axes)))
    return tuple(result)


def _parse_optional(value: str | None, enum_type: type[_EnumT]) -> _EnumT | None:
    return None if value is None else enum_type(value)


def _center_snapshot(
    case_id: str,
    revision: int,
    center_activity: tuple[
        CaseActivityEvent,
        ActivityLane,
        tuple[
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
            BusinessStage | None,
            OfficialProcedureStage | None,
            LegalStatus | None,
        ],
    ]
    | None,
) -> OverlayCenterSnapshot:
    if center_activity is None:
        if revision != 0:
            _state_conflict(case_id, "LIFECYCLE_ACTIVITY_MISSING")
        return OverlayCenterSnapshot(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=None,
            effective_at=None,
            verification_status=None,
            source_event_id=None,
        )
    activity, _, axes = center_activity
    return OverlayCenterSnapshot(
        business_stage=axes[3],
        official_procedure_stage=axes[4],
        legal_status=axes[5],
        effective_at=activity.effective_at,
        verification_status=_parse_optional(
            activity.confirmation_status,
            ConfirmationStatus,
        ),
        source_event_id=activity.id,
    )


def _validate_current_projection(
    case_id: str,
    case_state: object,
    snapshot: OverlayCenterSnapshot,
    revision: int,
) -> None:
    try:
        stored = (
            _parse_optional(case_state.business_stage, BusinessStage),
            _parse_optional(
                case_state.official_procedure_stage,
                OfficialProcedureStage,
            ),
            _parse_optional(case_state.legal_status, LegalStatus),
            _parse_optional(
                case_state.lifecycle_verification_status,
                ConfirmationStatus,
            ),
        )
    except (TypeError, ValueError):
        _state_conflict(case_id, "CASE_PROJECTION_ENUM_INVALID")
    reconstructed = (
        snapshot.business_stage,
        snapshot.official_procedure_stage,
        snapshot.legal_status,
        snapshot.verification_status,
    )
    if revision == 0:
        if stored != (None, None, None, None):
            _state_conflict(case_id, "ZERO_REVISION_HAS_PROJECTION")
    elif stored != reconstructed:
        _state_conflict(case_id, "CASE_PROJECTION_MISMATCH")


def _read_evidence(
    transaction: Session,
    *,
    case_id: str,
    activity_ids: tuple[str, ...],
) -> dict[str, tuple[EvidenceReference, ...]]:
    if not activity_ids:
        return {}
    rows = transaction.execute(
        select(CaseActivityEventEvidence)
        .where(
            CaseActivityEventEvidence.case_id == case_id,
            CaseActivityEventEvidence.activity_id.in_(activity_ids),
        )
        .order_by(
            CaseActivityEventEvidence.activity_id,
            CaseActivityEventEvidence.evidence_kind,
            CaseActivityEventEvidence.object_type,
            CaseActivityEventEvidence.object_id,
        )
    ).scalars()
    grouped: defaultdict[str, list[EvidenceReference]] = defaultdict(list)
    for row in rows:
        grouped[row.activity_id].append(
            EvidenceReference(
                case_id=row.case_id,
                evidence_kind=row.evidence_kind,
                object_type=row.object_type,
                object_id=row.object_id,
                content_hash=row.content_hash,
                captured_at=row.captured_at,
            )
        )
    return {key: tuple(values) for key, values in grouped.items()}


def _read_document_facts(
    transaction: Session,
    *,
    case_id: str,
    evidence_by_activity: dict[str, tuple[EvidenceReference, ...]],
) -> dict[
    str,
    tuple[
        tuple[OverlayDocumentEvidence, ...],
        tuple[OverlayWorkPackage, ...],
        tuple[OverlayTask, ...],
    ],
]:
    version_activities: defaultdict[str, set[str]] = defaultdict(set)
    package_activities: defaultdict[str, set[str]] = defaultdict(set)
    receipt_activities: defaultdict[str, set[str]] = defaultdict(set)
    for activity_id, evidence in evidence_by_activity.items():
        for reference in evidence:
            if reference.object_type == "DocumentEvidenceVersion":
                version_activities[reference.object_id].add(activity_id)
            elif reference.object_type == "OfficialWorkPackage":
                package_activities[reference.object_id].add(activity_id)
            elif reference.object_type == "OfficialWorkPackageReceipt":
                receipt_activities[reference.object_id].add(activity_id)
    if not (version_activities or package_activities or receipt_activities):
        return {}

    versions = _selected_versions(
        transaction,
        case_id=case_id,
        version_ids=tuple(version_activities),
    )
    packages = _selected_packages(
        transaction,
        case_id=case_id,
        package_ids=tuple(package_activities),
    )
    receipts = _selected_receipts(
        transaction,
        receipt_ids=tuple(receipt_activities),
    )
    for receipt_id, receipt in receipts.items():
        package = _selected_packages(
            transaction,
            case_id=case_id,
            package_ids=(receipt.package_id,),
        )[receipt.package_id]
        packages[package.id] = package
        package_activities[package.id].update(receipt_activities[receipt_id])

    manifests_for_versions = (
        transaction.execute(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.evidence_version_id.in_(tuple(versions))
            )
        )
        .scalars()
        .all()
        if versions
        else []
    )
    for manifest in manifests_for_versions:
        package = _selected_packages(
            transaction,
            case_id=case_id,
            package_ids=(manifest.package_id,),
        )[manifest.package_id]
        packages[package.id] = package
        package_activities[package.id].update(version_activities[manifest.evidence_version_id])

    manifests_by_package = _manifests_for_packages(
        transaction,
        case_id=case_id,
        package_ids=tuple(packages),
    )
    receipts_by_package = _receipts_for_packages(
        transaction,
        package_ids=tuple(packages),
    )
    derivations_by_version = _derivations_for_versions(
        transaction,
        case_id=case_id,
        version_ids=tuple(versions),
    )
    package_documents = {
        document_id
        for package in packages.values()
        for document_id in (package.source_document_id, package.reply_document_id)
        if document_id is not None
    }
    _require_same_case_documents(
        transaction,
        case_id=case_id,
        document_ids=tuple(package_documents),
    )

    documents_by_activity: defaultdict[str, set[str]] = defaultdict(set)
    for version_id, activity_ids in version_activities.items():
        for activity_id in activity_ids:
            documents_by_activity[activity_id].add(versions[version_id].document_id)
    for package_id, activity_ids in package_activities.items():
        package = packages[package_id]
        for activity_id in activity_ids:
            documents_by_activity[activity_id].update(
                document_id
                for document_id in (package.source_document_id, package.reply_document_id)
                if document_id is not None
            )
    tasks_by_document = _tasks_by_document(
        transaction,
        case_id=case_id,
        document_ids=tuple({item for values in documents_by_activity.values() for item in values}),
    )
    projected_packages = {
        package_id: _work_package(
            transaction,
            package=package,
            manifests=manifests_by_package.get(package_id, ()),
            receipts=receipts_by_package.get(package_id, ()),
        )
        for package_id, package in packages.items()
    }

    result = {}
    for activity_id in evidence_by_activity:
        document_evidence = tuple(
            OverlayDocumentEvidence(
                version=_evidence_result(versions[version_id]),
                derivations=derivations_by_version.get(version_id, ()),
            )
            for version_id in sorted(version_activities)
            if activity_id in version_activities[version_id]
        )
        work_packages = tuple(
            projected_packages[package_id]
            for package_id in sorted(package_activities)
            if activity_id in package_activities[package_id]
        )
        tasks = tuple(
            task
            for document_id in documents_by_activity.get(activity_id, ())
            for task in tasks_by_document.get(document_id, ())
        )
        result[activity_id] = (
            document_evidence,
            work_packages,
            tuple(
                sorted(tasks, key=lambda item: (item.due_date is None, item.due_date, item.task_id))
            ),
        )
    return result


def _selected_versions(
    transaction: Session,
    *,
    case_id: str,
    version_ids: tuple[str, ...],
) -> dict[str, DocumentEvidenceVersion]:
    if not version_ids:
        return {}
    rows = (
        transaction.execute(
            select(DocumentEvidenceVersion).where(DocumentEvidenceVersion.id.in_(version_ids))
        )
        .scalars()
        .all()
    )
    versions = {row.id: row for row in rows}
    if set(versions) != set(version_ids):
        _document_conflict(case_id, "EVIDENCE_VERSION_MISSING")
    _require_same_case_documents(
        transaction,
        case_id=case_id,
        document_ids=tuple(row.document_id for row in rows),
    )
    attachments = {
        row.id: row
        for row in transaction.execute(
            select(DocAttachment).where(
                DocAttachment.id.in_(tuple(version.attachment_id for version in rows))
            )
        ).scalars()
    }
    for version in rows:
        attachment = attachments.get(version.attachment_id)
        if (
            version.case_id != case_id
            or attachment is None
            or attachment.document_id != version.document_id
        ):
            _document_conflict(case_id, "EVIDENCE_VERSION_CASE_MISMATCH")
        _evidence_result(version)
    return versions


def _selected_packages(
    transaction: Session,
    *,
    case_id: str,
    package_ids: tuple[str, ...],
) -> dict[str, OfficialWorkPackage]:
    if not package_ids:
        return {}
    rows = (
        transaction.execute(
            select(OfficialWorkPackage).where(OfficialWorkPackage.id.in_(package_ids))
        )
        .scalars()
        .all()
    )
    packages = {row.id: row for row in rows}
    if set(packages) != set(package_ids):
        _document_conflict(case_id, "WORK_PACKAGE_MISSING")
    for package in rows:
        if (
            package.case_id != case_id
            or package.package_kind not in OFFICIAL_WORK_PACKAGE_KINDS
            or package.status not in OFFICIAL_WORK_PACKAGE_STATUSES
        ):
            _document_conflict(case_id, "WORK_PACKAGE_INVALID")
    return packages


def _selected_receipts(
    transaction: Session,
    *,
    receipt_ids: tuple[str, ...],
) -> dict[str, OfficialWorkPackageReceipt]:
    if not receipt_ids:
        return {}
    rows = (
        transaction.execute(
            select(OfficialWorkPackageReceipt).where(OfficialWorkPackageReceipt.id.in_(receipt_ids))
        )
        .scalars()
        .all()
    )
    receipts = {row.id: row for row in rows}
    if set(receipts) != set(receipt_ids):
        _document_conflict(None, "WORK_PACKAGE_RECEIPT_MISSING")
    if any(row.receipt_kind not in OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS for row in rows):
        _document_conflict(None, "WORK_PACKAGE_RECEIPT_INVALID")
    return receipts


def _manifests_for_packages(
    transaction: Session,
    *,
    case_id: str,
    package_ids: tuple[str, ...],
) -> dict[str, tuple[OfficialWorkPackageManifest, ...]]:
    if not package_ids:
        return {}
    rows = (
        transaction.execute(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id.in_(package_ids)
            )
        )
        .scalars()
        .all()
    )
    evidence_ids = tuple(
        row.evidence_version_id for row in rows if row.evidence_version_id is not None
    )
    if evidence_ids:
        _selected_versions(
            transaction,
            case_id=case_id,
            version_ids=evidence_ids,
        )
    grouped: defaultdict[str, list[OfficialWorkPackageManifest]] = defaultdict(list)
    for row in rows:
        grouped[row.package_id].append(row)
    return {
        package_id: tuple(
            sorted(
                manifests,
                key=lambda item: (item.sort_order is None, item.sort_order, item.id),
            )
        )
        for package_id, manifests in grouped.items()
    }


def _receipts_for_packages(
    transaction: Session,
    *,
    package_ids: tuple[str, ...],
) -> dict[str, tuple[OfficialWorkPackageReceipt, ...]]:
    if not package_ids:
        return {}
    rows = (
        transaction.execute(
            select(OfficialWorkPackageReceipt).where(
                OfficialWorkPackageReceipt.package_id.in_(package_ids)
            )
        )
        .scalars()
        .all()
    )
    if any(row.receipt_kind not in OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS for row in rows):
        _document_conflict(None, "WORK_PACKAGE_RECEIPT_INVALID")
    grouped: defaultdict[str, list[OfficialWorkPackageReceipt]] = defaultdict(list)
    for row in rows:
        grouped[row.package_id].append(row)
    return {
        package_id: tuple(
            sorted(
                receipts,
                key=lambda item: (item.received_at is None, item.received_at, item.id),
            )
        )
        for package_id, receipts in grouped.items()
    }


def _derivations_for_versions(
    transaction: Session,
    *,
    case_id: str,
    version_ids: tuple[str, ...],
) -> dict[str, tuple[EvidenceDerivationResult, ...]]:
    if not version_ids:
        return {}
    rows = (
        transaction.execute(
            select(DocumentEvidenceDerivation).where(
                or_(
                    DocumentEvidenceDerivation.parent_evidence_version_id.in_(version_ids),
                    DocumentEvidenceDerivation.child_evidence_version_id.in_(version_ids),
                )
            )
        )
        .scalars()
        .all()
    )
    endpoint_ids = {
        endpoint_id
        for row in rows
        for endpoint_id in (row.parent_evidence_version_id, row.child_evidence_version_id)
    }
    endpoints = (
        transaction.execute(
            select(DocumentEvidenceVersion).where(DocumentEvidenceVersion.id.in_(endpoint_ids))
        )
        .scalars()
        .all()
    )
    if len(endpoints) != len(endpoint_ids) or any(row.case_id != case_id for row in endpoints):
        _document_conflict(case_id, "EVIDENCE_DERIVATION_CASE_MISMATCH")
    grouped: defaultdict[str, list[EvidenceDerivationResult]] = defaultdict(list)
    for row in rows:
        try:
            derivation_type = EvidenceDerivationType(row.derivation_type)
        except (TypeError, ValueError):
            _document_conflict(case_id, "EVIDENCE_DERIVATION_ENUM_INVALID")
        if row.case_id != case_id:
            _document_conflict(case_id, "EVIDENCE_DERIVATION_CASE_MISMATCH")
        result = EvidenceDerivationResult(
            evidence_derivation_id=row.id,
            case_id=row.case_id,
            parent_evidence_version_id=row.parent_evidence_version_id,
            child_evidence_version_id=row.child_evidence_version_id,
            derivation_type=derivation_type,
            actor_id=row.actor_id,
            derived_at=row.derived_at,
            source_snapshot=row.source_snapshot,
        )
        for version_id in (row.parent_evidence_version_id, row.child_evidence_version_id):
            if version_id in version_ids:
                grouped[version_id].append(result)
    return {
        version_id: tuple(
            sorted(
                results,
                key=lambda item: (item.derived_at, item.evidence_derivation_id),
            )
        )
        for version_id, results in grouped.items()
    }


def _require_same_case_documents(
    transaction: Session,
    *,
    case_id: str,
    document_ids: tuple[str, ...],
) -> None:
    if not document_ids:
        return
    rows = (
        transaction.execute(select(Document).where(Document.id.in_(document_ids))).scalars().all()
    )
    if len(rows) != len(set(document_ids)) or any(row.case_id != case_id for row in rows):
        _document_conflict(case_id, "DOCUMENT_CASE_MISMATCH")


def _tasks_by_document(
    transaction: Session,
    *,
    case_id: str,
    document_ids: tuple[str, ...],
) -> dict[str, tuple[OverlayTask, ...]]:
    if not document_ids:
        return {}
    rows = (
        transaction.execute(
            select(Task).where(Task.case_id == case_id, Task.document_id.in_(document_ids))
        )
        .scalars()
        .all()
    )
    grouped: defaultdict[str, list[OverlayTask]] = defaultdict(list)
    for row in rows:
        try:
            TaskStatus(row.status)
        except (TypeError, ValueError):
            _document_conflict(case_id, "TASK_STATUS_INVALID")
        if row.document_id is None:
            _document_conflict(case_id, "TASK_DOCUMENT_MISSING")
        grouped[row.document_id].append(
            OverlayTask(
                task_id=row.id,
                document_id=row.document_id,
                task_template_id=row.task_template_id,
                title=row.title,
                due_date=row.due_date,
                internal_due_date=row.internal_due_date,
                status=row.status,
                done_at=row.done_at,
            )
        )
    return {key: tuple(value) for key, value in grouped.items()}


def _evidence_result(version: DocumentEvidenceVersion) -> EvidenceVersionResult:
    try:
        role = EvidenceRole(version.role)
        state = EvidenceVersionState(version.state)
        review_state = EvidenceReviewState(version.review_state)
    except (TypeError, ValueError):
        _document_conflict(version.case_id, "EVIDENCE_VERSION_ENUM_INVALID")
    identity_key = f"{version.case_id}|{version.lineage_key}"
    if version.current_identity_key not in (None, identity_key):
        _document_conflict(version.case_id, "EVIDENCE_VERSION_IDENTITY_INVALID")
    return EvidenceVersionResult(
        evidence_version_id=version.id,
        case_id=version.case_id,
        document_id=version.document_id,
        attachment_id=version.attachment_id,
        lineage_key=version.lineage_key,
        role=role,
        version_number=version.version_number,
        state=state,
        creator_id=version.creator_id,
        review_state=review_state,
        reviewer_id=version.reviewer_id,
        reviewed_at=version.reviewed_at,
        final_submitted_at=version.final_submitted_at,
        content_hash=version.content_hash,
        is_current=version.current_identity_key == identity_key,
        is_final=state is EvidenceVersionState.FINAL,
    )


def _work_package(
    transaction: Session,
    *,
    package: OfficialWorkPackage,
    manifests: tuple[OfficialWorkPackageManifest, ...],
    receipts: tuple[OfficialWorkPackageReceipt, ...],
) -> OverlayWorkPackage:
    evaluation = evaluate_official_work_package(transaction, package_id=package.id)
    return OverlayWorkPackage(
        package_id=package.id,
        package_kind=package.package_kind,
        status=package.status,
        source_document_id=package.source_document_id,
        reply_document_id=package.reply_document_id,
        manifest_evidence_version_ids=tuple(
            manifest.evidence_version_id
            for manifest in manifests
            if manifest.evidence_version_id is not None
        ),
        receipts=tuple(
            OverlayWorkPackageReceipt(
                receipt_id=receipt.id,
                receipt_kind=receipt.receipt_kind,
                receipt_attachment_id=receipt.receipt_attachment_id,
                receiving_case_no=receipt.receiving_case_no,
                submitter=receipt.submitter,
                received_at=receipt.received_at,
                archive_status=receipt.archive_status,
            )
            for receipt in receipts
        ),
        missing_gate_codes=tuple(blocker.blocker_type for blocker in evaluation.blockers),
    )


def _milestone(
    activity: CaseActivityEvent,
    lane: ActivityLane,
    axes: tuple[
        BusinessStage | None,
        OfficialProcedureStage | None,
        LegalStatus | None,
        BusinessStage | None,
        OfficialProcedureStage | None,
        LegalStatus | None,
    ],
    evidence: tuple[EvidenceReference, ...],
    document_evidence: tuple[OverlayDocumentEvidence, ...],
    work_packages: tuple[OverlayWorkPackage, ...],
    tasks: tuple[OverlayTask, ...],
    fee_obligations: tuple[OverlayFeeObligation, ...],
    conflict_codes: tuple[str, ...],
) -> OverlayMilestone:
    changes: dict[OverlayCenterAxis, OverlayCenterAxisChange] = {}
    if lane is ActivityLane.LIFECYCLE:
        for axis, old, new in (
            (OverlayCenterAxis.BUSINESS_STAGE, axes[0], axes[3]),
            (OverlayCenterAxis.OFFICIAL_PROCEDURE_STAGE, axes[1], axes[4]),
            (OverlayCenterAxis.LEGAL_STATUS, axes[2], axes[5]),
        ):
            if old != new:
                changes[axis] = OverlayCenterAxisChange(
                    previous_value=old,
                    current_value=new,
                )
    warnings: list[OverlayWarning] = []
    if activity.confirmation_status == ConfirmationStatus.NEEDS_REVIEW.value:
        warnings.append(
            _activity_warning(
                activity,
                kind=OverlayWarningKind.UNVERIFIED,
                code="LIFECYCLE_ACTIVITY_NEEDS_REVIEW",
                message="该生命周期活动尚待复核",
            )
        )
    elif activity.confirmation_status == ConfirmationStatus.LEGACY_UNVERIFIED.value:
        warnings.append(
            _activity_warning(
                activity,
                kind=OverlayWarningKind.UNVERIFIED,
                code="LEGACY_ACTIVITY_UNVERIFIED",
                message="该历史生命周期活动尚未核验",
            )
        )
    warnings.extend(
        _activity_warning(
            activity,
            kind=OverlayWarningKind.CONFLICT,
            code=code,
            message="生命周期活动存在待核对冲突",
        )
        for code in conflict_codes
    )
    return OverlayMilestone(
        sequence=activity.sequence,
        activity_id=activity.id,
        lane=lane,
        activity_type=activity.activity_type,
        source_activity_id=activity.source_activity_id,
        effective_at=activity.effective_at,
        confirmation_status=ConfirmationStatus(activity.confirmation_status),
        center_changes=changes,
        document_evidence=document_evidence,
        work_packages=work_packages,
        tasks=tasks,
        fee_obligations=fee_obligations,
        evidence_summary=evidence,
        warnings=tuple(warnings),
    )


def _activity_warning(
    activity: CaseActivityEvent,
    *,
    kind: OverlayWarningKind,
    code: str,
    message: str,
) -> OverlayWarning:
    return OverlayWarning(
        kind=kind,
        code=code,
        message=message,
        activity_id=activity.id,
        source_object_type="CASE_ACTIVITY_EVENT",
        source_object_id=activity.id,
    )


def _is_exact_legacy_import(
    activity: CaseActivityEvent,
    evidence: tuple[EvidenceReference, ...],
) -> bool:
    if (
        activity.lane != ActivityLane.LIFECYCLE.value
        or activity.activity_type != "LEGACY_IMPORT"
        or activity.confirmation_status != ConfirmationStatus.LEGACY_UNVERIFIED.value
        or activity.source_activity_id is not None
        or activity.supersedes_event_id is not None
        or activity.reviewer_id is not None
        or activity.old_business_stage is not None
        or activity.new_business_stage is not None
        or activity.old_official_procedure_stage is not None
        or activity.new_official_procedure_stage is not None
        or activity.old_legal_status is not None
        or activity.new_legal_status != LegalStatus.UNKNOWN.value
        or activity.occurred_at != activity.effective_at
        or activity.idempotency_key != f"v8-legacy-lifecycle-import:{activity.case_id}"
        or evidence
    ):
        return False
    try:
        payload = json.loads(activity.payload_json)
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return False
    return bool(
        type(payload) is dict
        and set(payload) == {"case_id", "legacy_status", "reverse_mapping", "schema"}
        and payload["case_id"] == activity.case_id
        and type(payload["legacy_status"]) is str
        and payload["legacy_status"] in _LEGACY_IMPORT_STATUSES
        and payload["reverse_mapping"] == "NONE"
        and payload["schema"] == "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1"
        and canonical == activity.payload_json
    )


def _decision_gate_warnings(
    decision_gates: tuple[OverlayDecisionGate, ...],
) -> tuple[OverlayWarning, ...]:
    result: list[OverlayWarning] = []
    for gate in decision_gates:
        if gate.resolution_status is OverlayGateResolutionStatus.UNRESOLVED:
            if gate.unresolved_reason is None:
                _state_conflict(None, "DECISION_GATE_WARNING_INVALID")
            result.append(
                OverlayWarning(
                    kind=OverlayWarningKind.CUSTOMER_DECISION_GATE,
                    code=gate.unresolved_reason,
                    message="客户决策门禁尚未解析",
                    activity_id=None,
                    source_object_type="CUSTOMER_DECISION_GATE",
                    source_object_id=f"{gate.gate_code.value}:{gate.requested_scope_key}",
                )
            )
        elif gate.decision_value in {"HISTORICAL", "INTERNAL_ONLY"}:
            if gate.gate_id is None:
                _state_conflict(None, "DECISION_GATE_WARNING_INVALID")
            result.append(
                OverlayWarning(
                    kind=OverlayWarningKind.REFERENCE_ONLY,
                    code="DECISION_GATE_REFERENCE_ONLY",
                    message="该客户决策分类仅供参考，不得激活",
                    activity_id=None,
                    source_object_type="CUSTOMER_DECISION_GATE",
                    source_object_id=(
                        f"{gate.gate_code.value}:{gate.requested_scope_key}:{gate.gate_id}"
                    ),
                )
            )
    return tuple(result)


_FEE_ACTIVITY_SCHEMAS: dict[str, tuple[str | None, str, frozenset[str]]] = {
    "FEE_OBLIGATION_RECOGNIZED": (
        "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
        "obligation_id",
        frozenset({"schema", "obligation_id"}),
    ),
    "FEE_CLIENT_INSTRUCTION_RECORDED": (
        "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1",
        "obligation_id",
        frozenset(
            {
                "actor_id",
                "instruction",
                "obligation_id",
                "previous_instruction_status",
                "schema",
            }
        ),
    ),
    "FEE_DRAFT_CREATED": (
        "FPMS_FEE_DRAFT_CREATED_V1",
        "obligation_id",
        frozenset({"actor_id", "center_changes", "draft_id", "links", "obligation_id", "schema"}),
    ),
    "PAY_LIST_CREATED": (
        "FPMS_PAY_LIST_CREATED_V1",
        "obligation_ids",
        frozenset(
            {
                "actor_id",
                "center_changes",
                "fee_item_ids",
                "obligation_ids",
                "obligation_line_ids",
                "pay_list_id",
                "schema",
            }
        ),
    ),
    "PAY_LIST_INTERNAL_EXPORTED": (
        None,
        "pay_list_id",
        frozenset({"artifact_id", "pay_list_id", "content_sha256", "managed_storage_path"}),
    ),
    "PAYMENT_RECORDED": (
        "FPMS_GOV_PAYMENT_RECORDED_V1",
        "obligation_id",
        frozenset({"gov_payment_id", "obligation_id", "obligation_line_ids", "schema"}),
    ),
    "OFFICIAL_PAYMENT_EVIDENCE_VERIFIED": (
        "FPMS_GOV_PAYMENT_OFFICIAL_EVIDENCE_VERIFIED_V1",
        "obligation_id",
        frozenset(
            {
                "gov_payment_id",
                "invoice_no",
                "obligation_id",
                "obligation_line_ids",
                "official_receipt_no",
                "schema",
                "voucher_no",
            }
        ),
    ),
}


def _read_fee_facts(
    transaction: Session,
    *,
    case_id: str,
    activities: tuple[CaseActivityEvent, ...],
) -> dict[str, tuple[OverlayFeeObligation, ...]]:
    projected: dict[str, tuple[OverlayFeeObligation, ...]] = {}
    obligation_cache: dict[str, object] = {}
    for activity in activities:
        if activity.lane != ActivityLane.FEE.value:
            continue
        spec = _FEE_ACTIVITY_SCHEMAS.get(activity.activity_type)
        if spec is None:
            projected[activity.id] = ()
            continue
        payload = _fee_payload(
            case_id,
            activity,
            expected_schema=spec[0],
            expected_keys=spec[2],
        )
        obligation_ids, related = _fee_activity_roots(
            transaction,
            case_id=case_id,
            activity=activity,
            payload=payload,
            identity_field=spec[1],
        )
        obligations: list[OverlayFeeObligation] = []
        for obligation_id in sorted(obligation_ids):
            try:
                obligation = obligation_cache.get(obligation_id)
                if obligation is None:
                    obligation = get_fee_obligation(obligation_id, transaction)
                    obligation_cache[obligation_id] = obligation
            except BusinessError:
                _fee_conflict(case_id, "OBLIGATION_DETAIL_INVALID")
            if obligation.case_id != case_id:
                _fee_conflict(case_id, "OBLIGATION_CASE_MISMATCH")
            _validate_fee_activity_lineage(
                transaction,
                case_id=case_id,
                activity=activity,
                obligation_id=obligation_id,
                source_activity_id=obligation.source.source_activity_id,
            )
            obligations.append(
                OverlayFeeObligation(
                    obligation_id=obligation.id,
                    source_activity_id=obligation.source.source_activity_id,
                    source_document_id=obligation.source.source_document_id,
                    source_status=obligation.source.status,
                    fee_domain=obligation.fee_domain,
                    obligation_type=obligation.obligation_type,
                    due_date=obligation.due_date,
                    currency=obligation.currency,
                    statuses=obligation.statuses,
                    lines=tuple(
                        OverlayFeeLine(
                            line_id=line.id,
                            fee_code=line.fee_code,
                            fee_name=line.fee_name,
                            fee_year_key=line.fee_year_key,
                            official_full_amount=_money(line.official_full_amount),
                            reduction_ratio=format(line.reduction_ratio, ".4f"),
                            payable_amount=cast(str, _money(line.payable_amount)),
                            source_amount=_money(line.source_amount),
                            source_date=line.source_date,
                            difference_review_state=line.difference_review_state,
                        )
                        for line in obligation.lines
                    ),
                    related_facts=tuple(
                        fact for owner_id, fact in related if owner_id == obligation.id
                    ),
                    supersedes_obligation_id=obligation.supersedes_obligation_id,
                    supersede_reason=obligation.supersede_reason,
                )
            )
        projected[activity.id] = tuple(obligations)
    return projected


def _fee_payload(
    case_id: str,
    activity: CaseActivityEvent,
    *,
    expected_schema: str | None,
    expected_keys: frozenset[str] | None = None,
) -> dict[str, object]:
    try:
        pairs = json.loads(
            activity.payload_json,
            object_pairs_hook=lambda values: _unique_json_object(case_id, values),
            parse_constant=lambda _value: _fee_conflict(case_id, "PAYLOAD_CONSTANT_INVALID"),
        )
        canonical = json.dumps(
            pairs,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        _fee_conflict(case_id, "PAYLOAD_INVALID")
    if type(pairs) is not dict or canonical != activity.payload_json:
        _fee_conflict(case_id, "PAYLOAD_NOT_CANONICAL")
    payload = cast(dict[str, object], pairs)
    if expected_schema is not None and payload.get("schema") != expected_schema:
        _fee_conflict(case_id, "PAYLOAD_SCHEMA_INVALID")
    allowed_keys = expected_keys
    if activity.activity_type == "FEE_OBLIGATION_RECOGNIZED" and "obligation" in payload:
        allowed_keys = frozenset({"schema", "obligation_id", "obligation"})
    if allowed_keys is not None and frozenset(payload) != allowed_keys:
        _fee_conflict(case_id, "PAYLOAD_SHAPE_INVALID")
    return payload


def _unique_json_object(
    case_id: str,
    values: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in values:
        if key in result:
            _fee_conflict(case_id, "PAYLOAD_DUPLICATE_KEY")
        result[key] = value
    return result


def _fee_activity_roots(
    transaction: Session,
    *,
    case_id: str,
    activity: CaseActivityEvent,
    payload: dict[str, object],
    identity_field: str,
) -> tuple[tuple[str, ...], tuple[tuple[str, OverlayFeeRelatedFact], ...]]:
    if identity_field == "obligation_id":
        value = payload.get(identity_field)
        if type(value) is not str or not value or value.strip() != value:
            _fee_conflict(case_id, "OBLIGATION_ID_INVALID")
        obligation_ids = (value,)
    elif identity_field == "obligation_ids":
        values = payload.get(identity_field)
        if (
            type(values) is not list
            or not values
            or any(
                type(value) is not str or not value or value.strip() != value for value in values
            )
            or len(set(values)) != len(values)
        ):
            _fee_conflict(case_id, "OBLIGATION_IDS_INVALID")
        obligation_ids = tuple(cast(list[str], values))
    else:
        pay_list_id = payload.get("pay_list_id")
        if type(pay_list_id) is not int or isinstance(pay_list_id, bool) or pay_list_id <= 0:
            _fee_conflict(case_id, "PAY_LIST_ID_INVALID")
        obligation_ids = _pay_list_obligation_ids(transaction, case_id, pay_list_id)

    related: list[tuple[str, OverlayFeeRelatedFact]] = []
    if activity.activity_type == "FEE_DRAFT_CREATED":
        related.extend(
            _draft_related_facts(transaction, case_id, payload.get("draft_id"), obligation_ids)
        )
    elif activity.activity_type in {"PAY_LIST_CREATED", "PAY_LIST_INTERNAL_EXPORTED"}:
        related.extend(
            _pay_list_related_facts(
                transaction,
                case_id,
                payload.get("pay_list_id"),
                obligation_ids,
            )
        )
    elif activity.activity_type in {
        "PAYMENT_RECORDED",
        "OFFICIAL_PAYMENT_EVIDENCE_VERIFIED",
    }:
        related.extend(
            _payment_related_facts(
                transaction,
                case_id,
                payload.get("gov_payment_id"),
                obligation_ids,
                official=activity.activity_type == "OFFICIAL_PAYMENT_EVIDENCE_VERIFIED",
            )
        )
    _validate_fee_payload_relations(
        transaction,
        case_id=case_id,
        activity_type=activity.activity_type,
        payload=payload,
        obligation_ids=obligation_ids,
    )
    return tuple(sorted(obligation_ids)), tuple(
        sorted(related, key=lambda item: (item[0], item[1].kind.value, item[1].object_id))
    )


def _validate_fee_payload_relations(
    transaction: Session,
    *,
    case_id: str,
    activity_type: str,
    payload: dict[str, object],
    obligation_ids: tuple[str, ...],
) -> None:
    if activity_type == "FEE_DRAFT_CREATED":
        draft_id = cast(str, payload["draft_id"])
        declared = payload.get("links")
        if type(declared) is not list:
            _fee_conflict(case_id, "DRAFT_LINKS_INVALID")
        normalized: list[tuple[str, str]] = []
        for item in cast(list[object], declared):
            if (
                type(item) is not dict
                or set(item) != {"fee_item_id", "obligation_line_id"}
                or type(item.get("fee_item_id")) is not str
                or type(item.get("obligation_line_id")) is not str
            ):
                _fee_conflict(case_id, "DRAFT_LINKS_INVALID")
            normalized.append(
                (cast(str, item["fee_item_id"]), cast(str, item["obligation_line_id"]))
            )
        rows = transaction.execute(
            select(FeeItem.id, FeeObligationDraftItemLink.obligation_line_id)
            .join(
                FeeObligationDraftItemLink,
                FeeObligationDraftItemLink.fee_item_id == FeeItem.id,
            )
            .where(FeeItem.draft_id == draft_id)
        ).all()
        if sorted(normalized) != sorted((row.id, row.obligation_line_id) for row in rows):
            _fee_conflict(case_id, "DRAFT_PAYLOAD_LINK_MISMATCH")
    elif activity_type == "PAY_LIST_CREATED":
        pay_list_id = cast(int, payload["pay_list_id"])
        rows = _pay_list_relation_rows(transaction, pay_list_id)
        declared_items = _string_list(case_id, payload.get("fee_item_ids"), "FEE_ITEM_IDS")
        declared_lines = _string_list(
            case_id,
            payload.get("obligation_line_ids"),
            "OBLIGATION_LINE_IDS",
        )
        if (
            tuple(sorted(declared_items)) != tuple(sorted({row.fee_item_id for row in rows}))
            or tuple(sorted(declared_lines))
            != tuple(sorted({row.obligation_line_id for row in rows}))
            or tuple(sorted(obligation_ids)) != tuple(sorted({row.obligation_id for row in rows}))
        ):
            _fee_conflict(case_id, "PAY_LIST_PAYLOAD_LINK_MISMATCH")
    elif activity_type in {"PAYMENT_RECORDED", "OFFICIAL_PAYMENT_EVIDENCE_VERIFIED"}:
        payment_id = cast(int, payload["gov_payment_id"])
        declared_lines = _string_list(
            case_id,
            payload.get("obligation_line_ids"),
            "OBLIGATION_LINE_IDS",
        )
        rows = transaction.execute(
            select(
                FeeObligationPaymentEvidenceLink.obligation_line_id,
                FeeObligationLine.obligation_id,
            )
            .join(
                FeeObligationLine,
                FeeObligationLine.id == FeeObligationPaymentEvidenceLink.obligation_line_id,
            )
            .where(FeeObligationPaymentEvidenceLink.gov_payment_id == payment_id)
        ).all()
        if tuple(sorted(declared_lines)) != tuple(
            sorted(row.obligation_line_id for row in rows)
        ) or tuple(sorted(obligation_ids)) != tuple(sorted({row.obligation_id for row in rows})):
            _fee_conflict(case_id, "PAYMENT_PAYLOAD_LINK_MISMATCH")
    elif activity_type == "PAY_LIST_INTERNAL_EXPORTED":
        artifact_id = payload.get("artifact_id")
        if type(artifact_id) is not str or not artifact_id:
            _fee_conflict(case_id, "PAY_LIST_ARTIFACT_ID_INVALID")
        artifact = transaction.get(PayListExportArtifact, artifact_id)
        if (
            artifact is None
            or artifact.pay_list_id != payload.get("pay_list_id")
            or artifact.content_sha256 != payload.get("content_sha256")
            or artifact.managed_storage_path != payload.get("managed_storage_path")
        ):
            _fee_conflict(case_id, "PAY_LIST_ARTIFACT_MISMATCH")


def _string_list(case_id: str, value: object, field: str) -> tuple[str, ...]:
    if (
        type(value) is not list
        or not value
        or any(type(item) is not str or not item or item.strip() != item for item in value)
        or len(set(value)) != len(value)
    ):
        _fee_conflict(case_id, f"{field}_INVALID")
    return tuple(cast(list[str], value))


def _pay_list_relation_rows(transaction: Session, pay_list_id: int) -> tuple[object, ...]:
    return tuple(
        transaction.execute(
            select(
                FeeItem.id.label("fee_item_id"),
                FeeObligationDraftItemLink.obligation_line_id.label("obligation_line_id"),
                FeeObligationLine.obligation_id.label("obligation_id"),
                GovPayment.case_id.label("case_id"),
            )
            .select_from(GovPayment)
            .join(FeeItem, FeeItem.id == GovPayment.fee_item_id)
            .join(
                FeeObligationDraftItemLink,
                FeeObligationDraftItemLink.fee_item_id == FeeItem.id,
            )
            .join(
                FeeObligationLine,
                FeeObligationLine.id == FeeObligationDraftItemLink.obligation_line_id,
            )
            .where(GovPayment.pay_list_id == pay_list_id)
        ).all()
    )


def _draft_related_facts(
    transaction: Session,
    case_id: str,
    draft_id: object,
    obligation_ids: tuple[str, ...],
) -> tuple[tuple[str, OverlayFeeRelatedFact], ...]:
    if type(draft_id) is not str or not draft_id:
        _fee_conflict(case_id, "DRAFT_ID_INVALID")
    draft = transaction.get(FeeDraft, draft_id)
    if draft is None or draft.case_id != case_id:
        _fee_conflict(case_id, "DRAFT_CASE_MISMATCH")
    owners = _draft_obligation_ids(transaction, draft_id)
    if owners != set(obligation_ids):
        _fee_conflict(case_id, "DRAFT_OBLIGATION_MISMATCH")
    return tuple(
        (
            owner,
            OverlayFeeRelatedFact(
                kind=OverlayFeeRelatedFactKind.DRAFT,
                object_id=draft.id,
                status=draft.status,
            ),
        )
        for owner in sorted(owners)
    )


def _pay_list_related_facts(
    transaction: Session,
    case_id: str,
    pay_list_id: object,
    obligation_ids: tuple[str, ...],
) -> tuple[tuple[str, OverlayFeeRelatedFact], ...]:
    if type(pay_list_id) is not int or isinstance(pay_list_id, bool) or pay_list_id <= 0:
        _fee_conflict(case_id, "PAY_LIST_ID_INVALID")
    pay_list = transaction.get(PayList, pay_list_id)
    if pay_list is None:
        _fee_conflict(case_id, "PAY_LIST_MISSING")
    owners = set(_pay_list_obligation_ids(transaction, case_id, pay_list_id))
    if owners != set(obligation_ids):
        _fee_conflict(case_id, "PAY_LIST_OBLIGATION_MISMATCH")
    return tuple(
        (
            owner,
            OverlayFeeRelatedFact(
                kind=OverlayFeeRelatedFactKind.PAY_LIST,
                object_id=str(pay_list.id),
                status=pay_list.status,
            ),
        )
        for owner in sorted(owners)
    )


def _payment_related_facts(
    transaction: Session,
    case_id: str,
    payment_id: object,
    obligation_ids: tuple[str, ...],
    *,
    official: bool,
) -> tuple[tuple[str, OverlayFeeRelatedFact], ...]:
    if type(payment_id) is not int or isinstance(payment_id, bool) or payment_id <= 0:
        _fee_conflict(case_id, "PAYMENT_ID_INVALID")
    payment = transaction.get(GovPayment, payment_id)
    if payment is None or payment.case_id != case_id:
        _fee_conflict(case_id, "PAYMENT_CASE_MISMATCH")
    owners = _payment_obligation_ids(transaction, payment_id)
    if owners != set(obligation_ids):
        _fee_conflict(case_id, "PAYMENT_OBLIGATION_MISMATCH")
    kind = (
        OverlayFeeRelatedFactKind.OFFICIAL_EVIDENCE
        if official
        else OverlayFeeRelatedFactKind.PAYMENT
    )
    return tuple(
        (
            owner,
            OverlayFeeRelatedFact(
                kind=kind,
                object_id=str(payment.id),
                status=(
                    _obligation_official_status(transaction, owner) if official else payment.status
                ),
            ),
        )
        for owner in sorted(owners)
    )


def _draft_obligation_ids(transaction: Session, draft_id: str) -> set[str]:
    rows = transaction.execute(
        select(FeeObligationLine.obligation_id)
        .join(
            FeeObligationDraftItemLink,
            FeeObligationDraftItemLink.obligation_line_id == FeeObligationLine.id,
        )
        .join(FeeItem, FeeItem.id == FeeObligationDraftItemLink.fee_item_id)
        .where(FeeItem.draft_id == draft_id)
    ).all()
    return {row[0] for row in rows}


def _pay_list_obligation_ids(
    transaction: Session,
    case_id: str,
    pay_list_id: int,
) -> tuple[str, ...]:
    rows = _pay_list_relation_rows(transaction, pay_list_id)
    if (
        not rows
        or any(row.case_id != case_id for row in rows)
        or len(rows) != len({row.fee_item_id for row in rows})
        or len(rows) != len({row.obligation_line_id for row in rows})
    ):
        _fee_conflict(case_id, "PAY_LIST_CASE_MISMATCH")
    return tuple(sorted({row.obligation_id for row in rows}))


def _payment_obligation_ids(transaction: Session, payment_id: int) -> set[str]:
    rows = transaction.execute(
        select(FeeObligationLine.obligation_id)
        .join(
            FeeObligationPaymentEvidenceLink,
            FeeObligationPaymentEvidenceLink.obligation_line_id == FeeObligationLine.id,
        )
        .where(FeeObligationPaymentEvidenceLink.gov_payment_id == payment_id)
    ).all()
    return {row[0] for row in rows}


def _obligation_official_status(transaction: Session, obligation_id: str) -> str:
    status = transaction.scalar(
        select(FeeObligationModel.official_evidence_status).where(
            FeeObligationModel.id == obligation_id
        )
    )
    if type(status) is not str or not status:
        _fee_conflict(None, "OBLIGATION_DETAIL_INVALID")
    return status


def _validate_fee_activity_lineage(
    transaction: Session,
    *,
    case_id: str,
    activity: CaseActivityEvent,
    obligation_id: str,
    source_activity_id: str,
) -> None:
    if activity.activity_type == "FEE_OBLIGATION_RECOGNIZED":
        if activity.source_activity_id != source_activity_id:
            _fee_conflict(case_id, "RECOGNITION_SOURCE_MISMATCH")
        return
    if activity.activity_type in {"FEE_CLIENT_INSTRUCTION_RECORDED", "FEE_DRAFT_CREATED"}:
        predecessor = transaction.get(CaseActivityEvent, activity.source_activity_id)
        if predecessor is None or predecessor.case_id != case_id:
            _fee_conflict(case_id, "FEE_ACTIVITY_PREDECESSOR_MISSING")
        if activity.activity_type == "FEE_DRAFT_CREATED":
            instruction_payload = _fee_payload(
                case_id,
                predecessor,
                expected_schema="FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1",
                expected_keys=_FEE_ACTIVITY_SCHEMAS["FEE_CLIENT_INSTRUCTION_RECORDED"][2],
            )
            if (
                predecessor.activity_type != "FEE_CLIENT_INSTRUCTION_RECORDED"
                or instruction_payload.get("obligation_id") != obligation_id
            ):
                _fee_conflict(case_id, "INSTRUCTION_LINEAGE_MISMATCH")
            recognition = transaction.get(CaseActivityEvent, predecessor.source_activity_id)
        else:
            recognition = predecessor
        if recognition is None or recognition.case_id != case_id:
            _fee_conflict(case_id, "RECOGNITION_ACTIVITY_MISSING")
        payload = _fee_payload(
            case_id,
            recognition,
            expected_schema="FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            expected_keys=frozenset({"schema", "obligation_id"}),
        )
        if (
            recognition.activity_type != "FEE_OBLIGATION_RECOGNIZED"
            or payload.get("obligation_id") != obligation_id
            or recognition.source_activity_id != source_activity_id
        ):
            _fee_conflict(case_id, "RECOGNITION_LINEAGE_MISMATCH")


def _money(value: Decimal | None) -> str | None:
    return None if value is None else format(value, ".2f")


def _fee_conflict(case_id: str | None, reason: str) -> None:
    _fail(
        "LIFECYCLE_OVERLAY_FEE_CONFLICT",
        "生命周期费用视图数据不一致",
        details={"case_id": case_id, "reason": reason},
        status_code=409,
    )


def _state_conflict(case_id: str | None, reason: str) -> None:
    _fail(
        "LIFECYCLE_OVERLAY_STATE_CONFLICT",
        "生命周期视图数据不一致",
        details={"case_id": case_id, "reason": reason},
        status_code=409,
    )


def _document_conflict(case_id: str | None, reason: str) -> None:
    _fail(
        "LIFECYCLE_OVERLAY_DOCUMENT_CONFLICT",
        "生命周期文档视图数据不一致",
        details={"case_id": case_id, "reason": reason},
        status_code=409,
    )


def _fail(
    code: str,
    message: str,
    *,
    details: dict[str, object] | None = None,
    status_code: int,
) -> None:
    raise BusinessError(code, message, details=details, status_code=status_code)
