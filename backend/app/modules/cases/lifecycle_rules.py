from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from re import fullmatch

from sqlalchemy.orm import Session

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
from app.modules.cases.lifecycle_service import LifecycleRuleDecision

__all__ = ("get_lifecycle_rule",)

_LifecycleRule = Callable[
    [LifecycleEventCommand, LifecycleProjection, Session],
    LifecycleRuleDecision | None,
]


def get_lifecycle_rule(event_type: object) -> _LifecycleRule | None:
    if type(event_type) is not str:
        return None
    return _RULES.get(event_type)


def _case_opened(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_case_opened_command(command)
        or type(previous_projection) is not LifecycleProjection
        or any(
            value is not None
            for value in (
                previous_projection.business_stage,
                previous_projection.official_procedure_stage,
                previous_projection.legal_status,
                previous_projection.lifecycle_verification_status,
            )
        )
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.NEW_CASE,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED,
            legal_status=LegalStatus.NOT_ESTABLISHED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_case_opened_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "CASE_OPENED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_case_opened_evidence_refs(command.case_id, command.evidence_refs)
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_case_opened_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.evidence_kind == "CASE_RECORD"
        and reference.object_type == "Case"
        and reference.case_id == case_id
        and type(reference.object_id) is str
        and bool(reference.object_id.strip())
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _filing_preparation_started(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_filing_preparation_started_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.NEW_CASE
        or previous_projection.official_procedure_stage is not OfficialProcedureStage.NOT_SUBMITTED
        or previous_projection.legal_status is not LegalStatus.NOT_ESTABLISHED
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.FILING_PREPARATION,
            official_procedure_stage=previous_projection.official_procedure_stage,
            legal_status=previous_projection.legal_status,
            lifecycle_verification_status=(previous_projection.lifecycle_verification_status),
        ),
        oa_sequence=None,
    )


def _valid_filing_preparation_started_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "FILING_PREPARATION_STARTED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_filing_preparation_evidence_refs(command.case_id, command.evidence_refs)
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_filing_preparation_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.evidence_kind == "FILING_WORK_PACKAGE"
        and reference.object_type == "OfficialWorkPackage"
        and reference.case_id == case_id
        and type(reference.object_id) is str
        and bool(reference.object_id.strip())
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _filing_external_submission_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_filing_external_submission_recorded_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.FILING_PREPARATION
        or previous_projection.official_procedure_stage is not OfficialProcedureStage.NOT_SUBMITTED
        or previous_projection.legal_status is not LegalStatus.NOT_ESTABLISHED
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.WAITING_EXTERNAL_RECEIPT,
            official_procedure_stage=OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
            legal_status=previous_projection.legal_status,
            lifecycle_verification_status=(previous_projection.lifecycle_verification_status),
        ),
        oa_sequence=None,
    )


def _valid_filing_external_submission_recorded_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "FILING_EXTERNAL_SUBMISSION_RECORDED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_filing_external_submission_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_filing_external_submission_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 2 or any(
        type(reference) is not EvidenceReference for reference in evidence_refs
    ):
        return False
    expected_reference_types = {
        ("FINAL_SUBMISSION_VERSION", "DocumentEvidenceVersion"),
        ("MANUAL_EXTERNAL_SUBMISSION_RECORD", "CaseActivityEvent"),
    }
    return (
        {(reference.evidence_kind, reference.object_type) for reference in evidence_refs}
        == expected_reference_types
        and all(reference.case_id == case_id for reference in evidence_refs)
        and all(type(reference.object_id) is str for reference in evidence_refs)
        and evidence_refs[0].object_id != evidence_refs[1].object_id
        and all(
            type(reference.content_hash) is str
            and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
            for reference in evidence_refs
        )
        and all(_naive_datetime(reference.captured_at) for reference in evidence_refs)
    )


def _filing_receipt_archived(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_filing_receipt_archived_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.WAITING_EXTERNAL_RECEIPT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT
        or previous_projection.legal_status is not LegalStatus.NOT_ESTABLISHED
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=(
                OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE
            ),
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=(previous_projection.lifecycle_verification_status),
        ),
        oa_sequence=None,
    )


def _valid_filing_receipt_archived_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "FILING_RECEIPT_ARCHIVED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_filing_receipt_evidence_refs(command.case_id, command.evidence_refs)
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_filing_receipt_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 2 or any(
        type(reference) is not EvidenceReference for reference in evidence_refs
    ):
        return False
    expected_reference_types = {
        ("FINAL_SUBMISSION_VERSION", "DocumentEvidenceVersion"),
        ("VALID_FILING_RECEIPT", "OfficialWorkPackageReceipt"),
    }
    return (
        {(reference.evidence_kind, reference.object_type) for reference in evidence_refs}
        == expected_reference_types
        and all(reference.case_id == case_id for reference in evidence_refs)
        and all(
            type(reference.object_id) is str and bool(reference.object_id.strip())
            for reference in evidence_refs
        )
        and len({reference.object_id for reference in evidence_refs}) == 2
        and all(
            type(reference.content_hash) is str
            and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
            for reference in evidence_refs
        )
        and all(_naive_datetime(reference.captured_at) for reference in evidence_refs)
    )


def _naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.tzinfo is None


_RULES: dict[str, _LifecycleRule] = {
    "CASE_OPENED": _case_opened,
    "FILING_PREPARATION_STARTED": _filing_preparation_started,
    "FILING_EXTERNAL_SUBMISSION_RECORDED": _filing_external_submission_recorded,
    "FILING_RECEIPT_ARCHIVED": _filing_receipt_archived,
}
