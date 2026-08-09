from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import TypeVar

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
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
    OverlayDocumentEvidence,
    OverlayMilestone,
    OverlayTask,
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
from app.modules.tasks.enums import TaskStatus
from app.modules.tasks.models import Task

__all__ = ("read_lifecycle_overlay",)

_EnumT = TypeVar("_EnumT")


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
    center_activity = next(
        (item for item in reversed(frozen) if item[1] is ActivityLane.LIFECYCLE),
        None,
    )
    center_snapshot = _center_snapshot(case_id, revision, center_activity)
    if revision == current_revision:
        _validate_current_projection(case_id, case_state, center_snapshot, current_revision)

    page = tuple(item for item in frozen if item[0].sequence > after_sequence)
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
    milestones = tuple(
        _milestone(
            activity,
            lane,
            axes,
            evidence_by_activity.get(activity.id, ()),
            *document_facts.get(activity.id, ((), (), ())),
        )
        for activity, lane, axes in page
    )
    return LifecycleOverlay(
        case_id=case_id,
        lifecycle_revision=revision,
        generated_at=generated_at,
        center_snapshot=center_snapshot,
        milestones=milestones,
        decision_gates=(),
        warnings=(),
        legacy_conflicts=(),
        next_cursor=None,
        has_more=False,
    )


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


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
        fee_obligations=(),
        evidence_summary=evidence,
        warnings=(),
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
