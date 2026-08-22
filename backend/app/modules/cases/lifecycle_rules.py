from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from datetime import date, datetime
from hashlib import sha256
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
from app.modules.cases.lifecycle_service import (
    LifecycleRuleDecision,
    PatentRegisterStatusRuleContext,
)

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
        and all(
            type(reference.object_id) is str and bool(reference.object_id.strip())
            for reference in evidence_refs
        )
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


def _acceptance_notice_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_acceptance_notice_recorded_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=previous_projection.business_stage,
            official_procedure_stage=OfficialProcedureStage.ACCEPTED,
            legal_status=previous_projection.legal_status,
            lifecycle_verification_status=(previous_projection.lifecycle_verification_status),
        ),
        oa_sequence=None,
    )


def _valid_acceptance_notice_recorded_command(command: object) -> bool:
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
        command.event_type == "ACCEPTANCE_NOTICE_RECORDED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_acceptance_notice_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_acceptance_notice_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.evidence_kind == "ACCEPTANCE_NOTICE"
        and reference.object_type == "DocumentEvidenceVersion"
        and reference.case_id == case_id
        and type(reference.object_id) is str
        and bool(reference.object_id.strip())
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _preliminary_examination_started(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_preliminary_examination_started_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage is not OfficialProcedureStage.ACCEPTED
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=previous_projection.business_stage,
            official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            legal_status=previous_projection.legal_status,
            lifecycle_verification_status=previous_projection.lifecycle_verification_status,
        ),
        oa_sequence=None,
    )


def _valid_preliminary_examination_started_command(command: object) -> bool:
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
        command.event_type == "PRELIMINARY_EXAMINATION_STARTED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_preliminary_examination_source_refs(
            command.case_id,
            command.evidence_refs,
        )
        and isinstance(command.payload, Mapping)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_preliminary_examination_source_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.evidence_kind == "PRELIMINARY_EXAMINATION_SOURCE"
        and reference.object_type == "DocumentEvidenceVersion"
        and reference.case_id == case_id
        and type(reference.object_id) is str
        and bool(reference.object_id.strip())
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _preliminary_examination_passed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_preliminary_examination_passed_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.PRELIMINARY_EXAMINATION
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=previous_projection,
        oa_sequence=None,
    )


def _valid_preliminary_examination_passed_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "PRELIMINARY_EXAMINATION_PASSED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_preliminary_examination_pass_notice_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_preliminary_examination_pass_notice_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.evidence_kind == "PRELIMINARY_EXAMINATION_PASS_NOTICE"
        and reference.object_type == "DocumentEvidenceVersion"
        and reference.case_id == case_id
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _rectification_notice_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_rectification_notice_recorded_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.PRELIMINARY_EXAMINATION
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.RECTIFICATION_RESPONSE,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_rectification_notice_recorded_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "RECTIFICATION_NOTICE_RECORDED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_rectification_notice_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and _valid_rectification_deadline_payload(command.payload)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_rectification_notice_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and type(reference.case_id) is str
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == "RECTIFICATION_NOTICE"
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _valid_rectification_deadline_payload(payload: object) -> bool:
    if (
        type(payload) is not dict
        or not all(type(key) is str for key in payload)
        or set(payload)
        != {
            "official_due_date",
            "official_due_date_source",
            "official_due_date_status",
        }
    ):
        return False
    due_date = payload["official_due_date"]
    source = payload["official_due_date_source"]
    status = payload["official_due_date_status"]
    if (
        type(due_date) is not str
        or type(source) is not str
        or source not in {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
        or type(status) is not str
        or status != "CONFIRMED"
    ):
        return False
    try:
        return date.fromisoformat(due_date).isoformat() == due_date
    except ValueError:
        return False


def _publication_notice_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_publication_notice_recorded_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.PRELIMINARY_EXAMINATION
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.PUBLISHED,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_publication_notice_recorded_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "PUBLICATION_NOTICE_RECORDED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_publication_notice_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_publication_notice_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and type(reference.case_id) is str
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == "PUBLICATION_NOTICE"
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _substantive_examination_started(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_substantive_examination_started_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage is not OfficialProcedureStage.PUBLISHED
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_substantive_examination_started_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "SUBSTANTIVE_EXAMINATION_STARTED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_substantive_examination_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_substantive_examination_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and type(reference.case_id) is str
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == "SUBSTANTIVE_EXAMINATION_SOURCE"
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _oa_notice_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_oa_notice_recorded_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.PROSECUTION_MANAGEMENT
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.SUBSTANTIVE_EXAMINATION
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=command.payload["oa_sequence"],
    )


def _valid_oa_notice_recorded_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "OA_NOTICE_RECORDED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_oa_notice_evidence_refs(command.case_id, command.evidence_refs)
        and _valid_oa_notice_payload(command.payload)
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_oa_notice_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and type(reference.case_id) is str
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == "OA_NOTICE"
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _valid_oa_notice_payload(payload: object) -> bool:
    if (
        type(payload) is not dict
        or not all(type(key) is str for key in payload)
        or set(payload)
        != {
            "official_due_date",
            "official_due_date_source",
            "official_due_date_status",
            "oa_sequence",
            "source_template_code",
        }
    ):
        return False
    due_date = payload["official_due_date"]
    source = payload["official_due_date_source"]
    status = payload["official_due_date_status"]
    oa_sequence = payload["oa_sequence"]
    source_template_code = payload["source_template_code"]
    if (
        type(due_date) is not str
        or type(source) is not str
        or source not in {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
        or type(status) is not str
        or status != "CONFIRMED"
        or type(oa_sequence) is not int
        or oa_sequence < 1
        or type(source_template_code) is not str
        or not source_template_code
        or source_template_code.strip() != source_template_code
        or len(source_template_code) > 64
    ):
        return False
    try:
        return date.fromisoformat(due_date).isoformat() == due_date
    except ValueError:
        return False



def _oa_receipt_archived(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_oa_receipt_archived_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.OA_REPLY_IN_PROGRESS
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.OFFICE_ACTION_RESPONSE
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_oa_receipt_archived_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "OA_RECEIPT_ARCHIVED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_oa_receipt_evidence_refs(command.case_id, command.evidence_refs)
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_oa_receipt_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and type(reference.case_id) is str
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == "OA_RECEIPT"
        and type(reference.object_type) is str
        and reference.object_type == "OfficialWorkPackageReceipt"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _reexamination_started(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_reexamination_started_command(command)
        or not _valid_reexamination_prior_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.REEXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_reexamination_started_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "REEXAMINATION_STARTED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_reexamination_evidence_refs(command.case_id, command.evidence_refs)
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_reexamination_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and reference.evidence_kind == "REEXAMINATION_SOURCE"
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _valid_reexamination_prior_projection(previous_projection: object) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return False
    return (
        previous_projection.business_stage is BusinessStage.PROSECUTION_MANAGEMENT
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.SUBSTANTIVE_EXAMINATION
        and previous_projection.legal_status is LegalStatus.APPLICATION_PENDING
    ) or (
        previous_projection.business_stage is BusinessStage.CLOSED
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.PROCEDURE_CLOSED
        and previous_projection.legal_status is LegalStatus.APPLICATION_REJECTED
    )


def _grant_registration_notice_recorded(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_grant_registration_notice_command(command)
        or not _valid_grant_registration_prior_projection(
            command,
            previous_projection,
        )
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_grant_registration_notice_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.reviewer_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "GRANT_REGISTRATION_NOTICE_RECORDED"
        and command.idempotency_key.startswith("grant-registration-notice:")
        and len(command.idempotency_key) > len("grant-registration-notice:")
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_grant_registration_evidence_refs(
            command.case_id,
            command.evidence_refs,
            command.payload,
        )
        and _valid_grant_registration_payload(
            command.case_id,
            command.payload,
            command.supersedes_event_id,
        )
        and _naive_datetime(command.effective_at)
        and _naive_datetime(command.occurred_at)
        and command.effective_at == command.occurred_at
        and command.source_activity_id is None
    )


def _valid_grant_registration_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
    payload: object,
) -> bool:
    if (
        len(evidence_refs) != 2
        or type(payload) is not dict
        or any(type(reference) is not EvidenceReference for reference in evidence_refs)
    ):
        return False
    source_document, evidence_version = evidence_refs
    content_hash = payload.get("reviewed_evidence_content_hash")
    reviewed_at = payload.get("reviewed_at")
    return (
        source_document.case_id == case_id
        and source_document.evidence_kind == "SOURCE_DOCUMENT"
        and source_document.object_type == "Document"
        and source_document.object_id == payload.get("source_document_id")
        and evidence_version.case_id == case_id
        and evidence_version.evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
        and evidence_version.object_type == "DocumentEvidenceVersion"
        and evidence_version.object_id == payload.get("reviewed_evidence_version_id")
        and all(
            type(reference.object_id) is str
            and bool(reference.object_id)
            and reference.object_id.strip() == reference.object_id
            and len(reference.object_id) <= 36
            and type(reference.content_hash) is str
            and reference.content_hash == content_hash
            and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
            and _naive_datetime(reference.captured_at)
            and reference.captured_at.isoformat() == reviewed_at
            for reference in evidence_refs
        )
    )


def _valid_grant_registration_payload(
    case_id: str,
    payload: object,
    supersedes_event_id: object,
) -> bool:
    expected_keys = {
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
    if (
        type(payload) is not dict
        or not all(type(key) is str for key in payload)
        or set(payload) != expected_keys
    ):
        return False
    identifiers = (
        payload["grant_fee_task_id"],
        payload["source_document_id"],
        payload["reviewed_evidence_version_id"],
    )
    predecessor_id = payload["predecessor_grant_fee_task_id"]
    supersedes_activity_id = payload["supersedes_activity_id"]
    initial_notice = (
        predecessor_id is None
        and supersedes_activity_id is None
        and supersedes_event_id is None
    )
    replacement_notice = (
        _canonical_identifier(predecessor_id)
        and predecessor_id != payload["grant_fee_task_id"]
        and _canonical_identifier(supersedes_activity_id)
        and supersedes_event_id == supersedes_activity_id
    )
    return (
        payload["schema"] == "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1"
        and type(payload["case_id"]) is str
        and payload["case_id"] == case_id
        and all(_canonical_identifier(value) for value in identifiers)
        and type(payload["reviewed_evidence_content_hash"]) is str
        and fullmatch(
            r"sha256:[0-9a-f]{64}",
            payload["reviewed_evidence_content_hash"],
        )
        is not None
        and _canonical_naive_datetime(payload["reviewed_at"])
        and payload["grant_fee_lines_schema"] == "FPMS_GRANT_NOTICE_FEE_LINES_V1"
        and _valid_grant_fee_lines_snapshot(payload)
        and _canonical_date(payload["due_date"])
        and type(payload["deadline_source"]) is str
        and bool(payload["deadline_source"])
        and payload["deadline_source"].strip() == payload["deadline_source"]
        and _canonical_naive_datetime(payload["deadline_confirmed_at"])
        and (initial_notice or replacement_notice)
    )


def _valid_grant_registration_prior_projection(
    command: LifecycleEventCommand,
    previous_projection: object,
) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
    ):
        return False
    if command.supersedes_event_id is not None:
        return (
            previous_projection.business_stage
            is BusinessStage.GRANT_REGISTRATION_IN_PROGRESS
            and previous_projection.official_procedure_stage
            is OfficialProcedureStage.GRANT_REGISTRATION
        )
    return (
        previous_projection.business_stage is BusinessStage.PROSECUTION_MANAGEMENT
        and (
            previous_projection.official_procedure_stage
            is OfficialProcedureStage.PRELIMINARY_EXAMINATION
            or previous_projection.official_procedure_stage
            is OfficialProcedureStage.SUBSTANTIVE_EXAMINATION
            or previous_projection.official_procedure_stage
            is OfficialProcedureStage.REEXAMINATION
        )
    )


def _valid_grant_fee_lines_snapshot(payload: dict[str, object]) -> bool:
    snapshot = payload["grant_fee_lines_snapshot"]
    snapshot_hash = payload["grant_fee_lines_snapshot_hash"]
    if (
        type(snapshot) is not str
        or not snapshot
        or type(snapshot_hash) is not str
        or fullmatch(r"[0-9a-f]{64}", snapshot_hash) is None
        or sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        return False
    try:
        parsed = json.loads(
            snapshot,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return False
    return (
        canonical == snapshot
        and type(parsed) is dict
        and set(parsed)
        == {
            "schema",
            "source_document_id",
            "reviewed_evidence_version_id",
            "reviewed_evidence_content_hash",
            "lines",
        }
        and parsed["schema"] == "FPMS_GRANT_NOTICE_FEE_LINES_V1"
        and parsed["source_document_id"] == payload["source_document_id"]
        and parsed["reviewed_evidence_version_id"]
        == payload["reviewed_evidence_version_id"]
        and parsed["reviewed_evidence_content_hash"]
        == payload["reviewed_evidence_content_hash"]
        and _valid_grant_fee_snapshot_lines(parsed["lines"])
    )


def _valid_grant_fee_snapshot_lines(lines: object) -> bool:
    if type(lines) is not list:
        return False
    if not lines:
        return (
            os.environ.get("FPMS_ENV") == "demo"
            and os.environ.get("FPMS_DEMO_SCOPE") == "LOCAL_ABC_E2E"
        )
    seen_years: set[int] = set()
    for line in lines:
        if (
            type(line) is not dict
            or set(line) != {"fee_name", "year", "amount", "reduction_ratio"}
        ):
            return False
        fee_name = line["fee_name"]
        year = line["year"]
        amount = line["amount"]
        reduction_ratio = line["reduction_ratio"]
        if (
            type(fee_name) is not str
            or not fee_name
            or fee_name.strip() != fee_name
            or "\x00" in fee_name
            or type(year) is not int
            or year <= 0
            or year in seen_years
            or type(amount) is not str
            or fullmatch(r"(?:0|[1-9][0-9]*)\.[0-9]{2}", amount) is None
            or not any(character not in {"0", "."} for character in amount)
            or type(reduction_ratio) is not str
            or reduction_ratio not in {"0", "0.7", "0.85"}
        ):
            return False
        seen_years.add(year)
    return True


def _grant_announcement_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_grant_announcement_command(command)
        or not _valid_grant_announcement_prior_projection(
            command,
            previous_projection,
        )
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
            official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
            legal_status=LegalStatus.PATENT_IN_FORCE,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_grant_announcement_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.reviewer_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "GRANT_ANNOUNCEMENT_CONFIRMED"
        and command.idempotency_key.startswith("grant-announcement:")
        and len(command.idempotency_key) > len("grant-announcement:")
        and command.reviewer_id != command.actor_id
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_grant_announcement_evidence_refs(
            command.case_id,
            command.effective_at,
            command.evidence_refs,
            command.payload,
        )
        and _valid_grant_announcement_payload(
            command.case_id,
            command.effective_at,
            command.payload,
            command.supersedes_event_id,
        )
        and _naive_datetime(command.effective_at)
        and _naive_datetime(command.occurred_at)
        and command.source_activity_id is None
    )


def _valid_grant_announcement_evidence_refs(
    case_id: str,
    effective_at: object,
    evidence_refs: tuple[EvidenceReference, ...],
    payload: object,
) -> bool:
    if (
        len(evidence_refs) != 1
        or type(payload) is not dict
        or type(evidence_refs[0]) is not EvidenceReference
    ):
        return False
    reference = evidence_refs[0]
    return (
        reference.case_id == case_id
        and reference.evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
        and reference.object_type == "DocumentEvidenceVersion"
        and reference.object_id == payload.get("source_evidence_version_id")
        and type(reference.object_id) is str
        and _canonical_identifier(reference.object_id)
        and reference.content_hash == payload.get("source_evidence_content_hash")
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
        and reference.captured_at == effective_at
    )


def _valid_grant_announcement_payload(
    case_id: str,
    effective_at: object,
    payload: object,
    supersedes_event_id: object,
) -> bool:
    expected_keys = {
        "schema",
        "case_id",
        "announcement_date",
        "source_document_id",
        "source_evidence_version_id",
        "source_evidence_content_hash",
        "source_provenance_id",
        "source_snapshot_schema",
        "source_snapshot",
        "source_snapshot_hash",
        "predecessor_source_snapshot_hash",
        "supersedes_activity_id",
    }
    if (
        type(payload) is not dict
        or not all(type(key) is str for key in payload)
        or set(payload) != expected_keys
        or not _naive_datetime(effective_at)
    ):
        return False
    identifiers = (
        payload["source_document_id"],
        payload["source_evidence_version_id"],
        payload["source_provenance_id"],
    )
    predecessor_hash = payload["predecessor_source_snapshot_hash"]
    supersedes_activity_id = payload["supersedes_activity_id"]
    initial_announcement = (
        predecessor_hash is None
        and supersedes_activity_id is None
        and supersedes_event_id is None
    )
    replacement_announcement = (
        type(predecessor_hash) is str
        and fullmatch(r"[0-9a-f]{64}", predecessor_hash) is not None
        and predecessor_hash != payload["source_snapshot_hash"]
        and _canonical_identifier(supersedes_activity_id)
        and supersedes_event_id == supersedes_activity_id
    )
    return (
        payload["schema"] == "FPMS_GRANT_ANNOUNCEMENT_CONFIRMED_V1"
        and type(payload["case_id"]) is str
        and payload["case_id"] == case_id
        and all(_canonical_identifier(value) for value in identifiers)
        and _canonical_date(payload["announcement_date"])
        and payload["announcement_date"] == effective_at.date().isoformat()
        and type(payload["source_evidence_content_hash"]) is str
        and fullmatch(
            r"sha256:[0-9a-f]{64}",
            payload["source_evidence_content_hash"],
        )
        is not None
        and payload["source_snapshot_schema"]
        == "FPMS_GRANT_ANNOUNCEMENT_SOURCE_V1"
        and _valid_grant_announcement_source_snapshot(payload)
        and (initial_announcement or replacement_announcement)
    )


def _valid_grant_announcement_prior_projection(
    command: LifecycleEventCommand,
    previous_projection: object,
) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return False
    if command.supersedes_event_id is not None:
        return (
            previous_projection.business_stage
            is BusinessStage.POST_GRANT_MAINTENANCE
            and previous_projection.official_procedure_stage
            is OfficialProcedureStage.GRANT_ANNOUNCED
            and previous_projection.legal_status is LegalStatus.PATENT_IN_FORCE
        )
    return (
        previous_projection.business_stage
        is BusinessStage.GRANT_REGISTRATION_IN_PROGRESS
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.GRANT_REGISTRATION
        and previous_projection.legal_status is LegalStatus.APPLICATION_PENDING
    )


def _valid_grant_announcement_source_snapshot(payload: dict[str, object]) -> bool:
    snapshot = payload["source_snapshot"]
    snapshot_hash = payload["source_snapshot_hash"]
    if (
        type(snapshot) is not str
        or not snapshot
        or type(snapshot_hash) is not str
        or fullmatch(r"[0-9a-f]{64}", snapshot_hash) is None
        or sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        return False
    try:
        parsed = json.loads(
            snapshot,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return False
    return (
        canonical == snapshot
        and type(parsed) is dict
        and set(parsed)
        == {
            "schema",
            "announcement_date",
            "source_document_id",
            "source_evidence_version_id",
            "source_evidence_content_hash",
            "source_provenance_id",
        }
        and parsed["schema"] == payload["source_snapshot_schema"]
        and parsed["announcement_date"] == payload["announcement_date"]
        and parsed["source_document_id"] == payload["source_document_id"]
        and parsed["source_evidence_version_id"]
        == payload["source_evidence_version_id"]
        and parsed["source_evidence_content_hash"]
        == payload["source_evidence_content_hash"]
        and parsed["source_provenance_id"] == payload["source_provenance_id"]
    )


def _patent_register_status_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    context: PatentRegisterStatusRuleContext,
) -> LifecycleRuleDecision | None:
    if (
        not _valid_patent_register_status_command(command, context)
        or not _valid_patent_register_status_prior_projection(previous_projection)
    ):
        return None
    register_status = command.payload["register_status"]
    conflict_codes: tuple[str, ...] = ()
    if previous_projection.legal_status is LegalStatus.PATENT_IN_FORCE:
        if register_status in {
            LegalStatus.PATENT_TERMINATED.value,
            LegalStatus.PATENT_EXPIRED.value,
            LegalStatus.PATENT_INVALIDATED.value,
        }:
            conflict_codes = ("PATENT_REGISTER_STATUS_REQUIRES_SPECIFIC_EVENT",)
        elif register_status != LegalStatus.PATENT_IN_FORCE.value:
            return None
    elif register_status == LegalStatus.PATENT_IN_FORCE.value:
        conflict_codes = ("PATENT_REGISTER_STATUS_REQUIRES_SPECIFIC_EVENT",)
    else:
        return None
    return LifecycleRuleDecision(
        current_projection=previous_projection,
        oa_sequence=None,
        conflict_codes=conflict_codes,
    )


def _valid_patent_register_status_command(
    command: object,
    context: object,
) -> bool:
    if (
        type(command) is not LifecycleEventCommand
        or type(context) is not PatentRegisterStatusRuleContext
    ):
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.reviewer_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "PATENT_REGISTER_STATUS_CONFIRMED"
        and command.idempotency_key.startswith("patent-register-status:")
        and len(command.idempotency_key) > len("patent-register-status:")
        and command.reviewer_id != command.actor_id
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_patent_register_status_evidence_refs(
            command.case_id,
            command.effective_at,
            command.evidence_refs,
            command.payload,
        )
        and _valid_patent_register_status_payload(
            command.case_id,
            command.payload,
            command.supersedes_event_id,
            context,
        )
        and _naive_datetime(command.effective_at)
        and _naive_datetime(command.occurred_at)
        and command.source_activity_id is None
    )


def _valid_patent_register_status_evidence_refs(
    case_id: str,
    effective_at: object,
    evidence_refs: tuple[EvidenceReference, ...],
    payload: object,
) -> bool:
    if (
        len(evidence_refs) != 1
        or type(payload) is not dict
        or type(evidence_refs[0]) is not EvidenceReference
    ):
        return False
    reference = evidence_refs[0]
    return (
        reference.case_id == case_id
        and reference.evidence_kind == "DOCUMENT_EVIDENCE_VERSION"
        and reference.object_type == "DocumentEvidenceVersion"
        and reference.object_id == payload.get("source_evidence_version_id")
        and type(reference.object_id) is str
        and _canonical_identifier(reference.object_id)
        and reference.content_hash == payload.get("source_evidence_content_hash")
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
        and reference.captured_at == effective_at
    )


def _valid_patent_register_status_payload(
    case_id: str,
    payload: object,
    supersedes_event_id: object,
    context: PatentRegisterStatusRuleContext,
) -> bool:
    expected_keys = {
        "schema",
        "case_id",
        "register_status",
        "source_document_id",
        "source_evidence_version_id",
        "source_evidence_content_hash",
        "source_provenance_id",
        "status_snapshot_schema",
        "status_snapshot",
        "status_snapshot_hash",
        "predecessor_status_snapshot_hash",
        "supersedes_activity_id",
    }
    if (
        type(payload) is not dict
        or not all(type(key) is str for key in payload)
        or set(payload) != expected_keys
    ):
        return False
    identifiers = (
        payload["source_document_id"],
        payload["source_evidence_version_id"],
        payload["source_provenance_id"],
    )
    predecessor_hash = payload["predecessor_status_snapshot_hash"]
    supersedes_activity_id = payload["supersedes_activity_id"]
    initial_confirmation = (
        predecessor_hash is None
        and supersedes_activity_id is None
        and supersedes_event_id is None
        and context.predecessor_event_type is None
        and context.predecessor_status_snapshot_hash is None
    )
    replacement_confirmation = (
        type(predecessor_hash) is str
        and fullmatch(r"[0-9a-f]{64}", predecessor_hash) is not None
        and _canonical_identifier(supersedes_activity_id)
        and supersedes_event_id == supersedes_activity_id
        and type(context.predecessor_event_type) is str
        and context.predecessor_event_type == "PATENT_REGISTER_STATUS_CONFIRMED"
        and type(context.predecessor_status_snapshot_hash) is str
        and predecessor_hash == context.predecessor_status_snapshot_hash
        and predecessor_hash != payload["status_snapshot_hash"]
    )
    return (
        payload["schema"] == "FPMS_PATENT_REGISTER_STATUS_CONFIRMED_V1"
        and type(payload["case_id"]) is str
        and payload["case_id"] == case_id
        and type(payload["register_status"]) is str
        and payload["register_status"]
        in {
            LegalStatus.PATENT_IN_FORCE.value,
            LegalStatus.PATENT_TERMINATED.value,
            LegalStatus.PATENT_EXPIRED.value,
            LegalStatus.PATENT_INVALIDATED.value,
        }
        and all(_canonical_identifier(value) for value in identifiers)
        and type(payload["source_evidence_content_hash"]) is str
        and fullmatch(
            r"sha256:[0-9a-f]{64}",
            payload["source_evidence_content_hash"],
        )
        is not None
        and payload["status_snapshot_schema"]
        == "FPMS_PATENT_REGISTER_STATUS_SOURCE_V1"
        and _valid_patent_register_status_snapshot(payload)
        and (initial_confirmation or replacement_confirmation)
    )


def _valid_patent_register_status_prior_projection(
    previous_projection: object,
) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return False
    return (
        previous_projection.business_stage is BusinessStage.POST_GRANT_MAINTENANCE
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.GRANT_ANNOUNCED
        and previous_projection.legal_status is LegalStatus.PATENT_IN_FORCE
    ) or (
        previous_projection.business_stage is BusinessStage.CLOSED
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.PROCEDURE_CLOSED
        and previous_projection.legal_status is LegalStatus.PATENT_TERMINATED
    )


def _valid_patent_register_status_snapshot(payload: dict[str, object]) -> bool:
    snapshot = payload["status_snapshot"]
    snapshot_hash = payload["status_snapshot_hash"]
    if (
        type(snapshot) is not str
        or not snapshot
        or type(snapshot_hash) is not str
        or fullmatch(r"[0-9a-f]{64}", snapshot_hash) is None
        or sha256(snapshot.encode("utf-8")).hexdigest() != snapshot_hash
    ):
        return False
    try:
        parsed = json.loads(
            snapshot,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return False
    return (
        canonical == snapshot
        and type(parsed) is dict
        and set(parsed)
        == {
            "schema",
            "register_status",
            "source_document_id",
            "source_evidence_version_id",
            "source_evidence_content_hash",
            "source_provenance_id",
        }
        and parsed["schema"] == payload["status_snapshot_schema"]
        and parsed["register_status"] == payload["register_status"]
        and parsed["source_document_id"] == payload["source_document_id"]
        and parsed["source_evidence_version_id"]
        == payload["source_evidence_version_id"]
        and parsed["source_evidence_content_hash"]
        == payload["source_evidence_content_hash"]
        and parsed["source_provenance_id"] == payload["source_provenance_id"]
    )


def _application_rejection_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if not _valid_application_rejection_command(
        command
    ) or not _valid_application_rejection_prior_projection(
        command,
        previous_projection,
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_REJECTED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_application_rejection_prior_projection(
    command: LifecycleEventCommand,
    previous_projection: object,
) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED
    ):
        return False
    predecessor = (
        previous_projection.business_stage,
        previous_projection.official_procedure_stage,
    )
    coherent_pending_application_predecessors = {
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.ACCEPTED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.PUBLISHED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.REEXAMINATION),
        (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            OfficialProcedureStage.GRANT_REGISTRATION,
        ),
    }
    if predecessor not in coherent_pending_application_predecessors:
        return False
    return command.evidence_refs[
        0
    ].evidence_kind != "REEXAMINATION_FINAL_REJECTION_DECISION" or predecessor == (
        BusinessStage.PROSECUTION_MANAGEMENT,
        OfficialProcedureStage.REEXAMINATION,
    )


def _valid_application_rejection_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str or not value or value.strip() != value or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "APPLICATION_REJECTION_CONFIRMED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_application_rejection_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
    )


def _valid_application_rejection_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind
        in {"REJECTION_DECISION", "REEXAMINATION_FINAL_REJECTION_DECISION"}
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and type(reference.object_id) is str
        and bool(reference.object_id)
        and reference.object_id.strip() == reference.object_id
        and len(reference.object_id) <= 36
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _application_withdrawal_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_application_withdrawal_command(command)
        or not _valid_ungranted_application_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_WITHDRAWN,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_application_withdrawal_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "APPLICATION_WITHDRAWAL_CONFIRMED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_application_withdrawal_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
        and command.source_activity_id is None
        and command.supersedes_event_id is None
    )


def _valid_application_withdrawal_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 2:
        return False
    expected_kinds = (
        "APPLICATION_WITHDRAWAL_REQUEST",
        "APPLICATION_WITHDRAWAL_OFFICIAL_CONFIRMATION",
    )
    return all(
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == expected_kind
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and _canonical_identifier(reference.object_id)
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
        for reference, expected_kind in zip(
            evidence_refs,
            expected_kinds,
            strict=True,
        )
    ) and evidence_refs[0].object_id != evidence_refs[1].object_id


def _valid_ungranted_application_projection(previous_projection: object) -> bool:
    if (
        type(previous_projection) is not LifecycleProjection
        or previous_projection.legal_status is not LegalStatus.APPLICATION_PENDING
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return False
    return (
        previous_projection.business_stage,
        previous_projection.official_procedure_stage,
    ) in {
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.ACCEPTED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.PUBLISHED),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        ),
        (BusinessStage.PROSECUTION_MANAGEMENT, OfficialProcedureStage.REEXAMINATION),
        (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            OfficialProcedureStage.GRANT_REGISTRATION,
        ),
    }


def _application_abandonment_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_application_abandonment_command(command)
        or not _valid_ungranted_application_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_ABANDONED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_application_abandonment_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "APPLICATION_ABANDONMENT_CONFIRMED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_application_abandonment_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
        and command.source_activity_id is None
        and command.supersedes_event_id is None
    )


def _valid_application_abandonment_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind
        in {"DEEMED_ABANDONMENT_NOTICE", "RIGHT_ABANDONMENT_CONFIRMATION"}
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and _canonical_identifier(reference.object_id)
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _patent_termination_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_patent_termination_command(command)
        or not _valid_in_force_patent_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.PATENT_TERMINATED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_patent_termination_command(command: object) -> bool:
    return _valid_confirmed_lifecycle_command(
        command,
        event_type="PATENT_TERMINATION_CONFIRMED",
        evidence_kinds={"PATENT_TERMINATION_NOTICE", "PATENT_REGISTER_STATUS_EVIDENCE"},
    )


def _valid_confirmed_lifecycle_command(
    command: object,
    *,
    event_type: str,
    evidence_kinds: set[str],
) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == event_type
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_single_document_evidence_ref(
            command.case_id,
            command.evidence_refs,
            evidence_kinds,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
        and command.source_activity_id is None
        and command.supersedes_event_id is None
    )


def _valid_single_document_evidence_ref(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
    evidence_kinds: set[str],
) -> bool:
    if len(evidence_refs) != 1:
        return False
    reference = evidence_refs[0]
    return (
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind in evidence_kinds
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and _canonical_identifier(reference.object_id)
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
    )


def _valid_in_force_patent_projection(previous_projection: object) -> bool:
    return (
        type(previous_projection) is LifecycleProjection
        and previous_projection.business_stage is BusinessStage.POST_GRANT_MAINTENANCE
        and previous_projection.official_procedure_stage
        is OfficialProcedureStage.GRANT_ANNOUNCED
        and previous_projection.legal_status is LegalStatus.PATENT_IN_FORCE
        and previous_projection.lifecycle_verification_status
        is ConfirmationStatus.CONFIRMED
    )


def _patent_expiry_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_confirmed_lifecycle_command(
            command,
            event_type="PATENT_EXPIRY_CONFIRMED",
            evidence_kinds={
                "PATENT_EXPIRY_CONFIRMATION",
                "PATENT_REGISTER_STATUS_EVIDENCE",
            },
        )
        or not _valid_in_force_patent_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.PATENT_EXPIRED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _patent_invalidation_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_patent_invalidation_command(command)
        or not _valid_in_force_patent_projection(previous_projection)
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.PATENT_INVALIDATED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_patent_invalidation_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "PATENT_INVALIDATION_CONFIRMED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_patent_invalidation_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
        and command.source_activity_id is None
        and command.supersedes_event_id is None
    )


def _valid_patent_invalidation_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 2:
        return False
    expected_kinds = (
        "EFFECTIVE_PATENT_INVALIDATION_DECISION",
        "PATENT_REGISTER_STATUS_EVIDENCE",
    )
    return all(
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == expected_kind
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and _canonical_identifier(reference.object_id)
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
        for reference, expected_kind in zip(
            evidence_refs,
            expected_kinds,
            strict=True,
        )
    ) and evidence_refs[0].object_id != evidence_refs[1].object_id


def _application_right_restoration_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    restored_stage = _valid_application_restoration_command(command)
    if (
        restored_stage is None
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.CLOSED
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.PROCEDURE_CLOSED
        or previous_projection.legal_status is not LegalStatus.APPLICATION_ABANDONED
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return None
    business_stage, official_stage = restored_stage
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=business_stage,
            official_procedure_stage=official_stage,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_application_restoration_command(
    command: object,
) -> tuple[BusinessStage, OfficialProcedureStage] | None:
    if type(command) is not LifecycleEventCommand:
        return None
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return None
    if (
        command.event_type != "APPLICATION_RIGHT_RESTORATION_CONFIRMED"
        or type(command.lane) is not ActivityLane
        or command.lane is not ActivityLane.LIFECYCLE
        or type(command.confirmation_status) is not ConfirmationStatus
        or command.confirmation_status is not ConfirmationStatus.CONFIRMED
        or type(command.evidence_refs) is not tuple
        or not _valid_single_document_evidence_ref(
            command.case_id,
            command.evidence_refs,
            {"APPLICATION_RIGHT_RESTORATION_DECISION"},
        )
        or type(command.payload) is not dict
        or set(command.payload) != {"restored_official_procedure_stage"}
        or not _naive_datetime(command.effective_at)
        or (command.occurred_at is not None and not _naive_datetime(command.occurred_at))
        or command.source_activity_id is not None
        or command.supersedes_event_id is not None
    ):
        return None
    restored_value = command.payload["restored_official_procedure_stage"]
    if type(restored_value) is not str:
        return None
    restored_stages = {
        OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
        ),
        OfficialProcedureStage.ACCEPTED.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.ACCEPTED,
        ),
        OfficialProcedureStage.PRELIMINARY_EXAMINATION.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        ),
        OfficialProcedureStage.RECTIFICATION_RESPONSE.value: (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
        ),
        OfficialProcedureStage.PUBLISHED.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PUBLISHED,
        ),
        OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        ),
        OfficialProcedureStage.OFFICE_ACTION_RESPONSE.value: (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        ),
        OfficialProcedureStage.REEXAMINATION.value: (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.REEXAMINATION,
        ),
        OfficialProcedureStage.GRANT_REGISTRATION.value: (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            OfficialProcedureStage.GRANT_REGISTRATION,
        ),
    }
    return restored_stages.get(restored_value)


def _patent_right_restoration_confirmed(
    command: LifecycleEventCommand,
    previous_projection: LifecycleProjection,
    transaction: Session,
) -> LifecycleRuleDecision | None:
    del transaction
    if (
        not _valid_patent_restoration_command(command)
        or type(previous_projection) is not LifecycleProjection
        or previous_projection.business_stage is not BusinessStage.CLOSED
        or previous_projection.official_procedure_stage
        is not OfficialProcedureStage.PROCEDURE_CLOSED
        or previous_projection.legal_status is not LegalStatus.PATENT_TERMINATED
        or previous_projection.lifecycle_verification_status
        is not ConfirmationStatus.CONFIRMED
    ):
        return None
    return LifecycleRuleDecision(
        current_projection=LifecycleProjection(
            business_stage=BusinessStage.POST_GRANT_MAINTENANCE,
            official_procedure_stage=OfficialProcedureStage.GRANT_ANNOUNCED,
            legal_status=LegalStatus.PATENT_IN_FORCE,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        ),
        oa_sequence=None,
    )


def _valid_patent_restoration_command(command: object) -> bool:
    if type(command) is not LifecycleEventCommand:
        return False
    required_strings = (
        (command.case_id, 36),
        (command.event_type, 64),
        (command.actor_id, 36),
        (command.idempotency_key, 128),
    )
    if any(
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > limit
        for value, limit in required_strings
    ):
        return False
    return (
        command.event_type == "PATENT_RIGHT_RESTORATION_CONFIRMED"
        and type(command.lane) is ActivityLane
        and command.lane is ActivityLane.LIFECYCLE
        and type(command.confirmation_status) is ConfirmationStatus
        and command.confirmation_status is ConfirmationStatus.CONFIRMED
        and type(command.evidence_refs) is tuple
        and _valid_patent_restoration_evidence_refs(
            command.case_id,
            command.evidence_refs,
        )
        and type(command.payload) is dict
        and not command.payload
        and _naive_datetime(command.effective_at)
        and (command.occurred_at is None or _naive_datetime(command.occurred_at))
        and command.source_activity_id is None
        and command.supersedes_event_id is None
    )


def _valid_patent_restoration_evidence_refs(
    case_id: str,
    evidence_refs: tuple[EvidenceReference, ...],
) -> bool:
    if len(evidence_refs) != 2:
        return False
    expected_kinds = (
        "PATENT_RIGHT_RESTORATION_DECISION",
        "PATENT_REGISTER_STATUS_EVIDENCE",
    )
    return all(
        type(reference) is EvidenceReference
        and reference.case_id == case_id
        and type(reference.evidence_kind) is str
        and reference.evidence_kind == expected_kind
        and type(reference.object_type) is str
        and reference.object_type == "DocumentEvidenceVersion"
        and _canonical_identifier(reference.object_id)
        and type(reference.content_hash) is str
        and fullmatch(r"sha256:[0-9a-f]{64}", reference.content_hash) is not None
        and _naive_datetime(reference.captured_at)
        for reference, expected_kind in zip(
            evidence_refs,
            expected_kinds,
            strict=True,
        )
    ) and evidence_refs[0].object_id != evidence_refs[1].object_id


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON constant: {value}")


def _canonical_identifier(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and len(value) <= 36
    )


def _canonical_date(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _canonical_naive_datetime(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is None and parsed.isoformat() == value



def _naive_datetime(value: object) -> bool:
    return type(value) is datetime and value.tzinfo is None


_RULES: dict[str, _LifecycleRule] = {
    "CASE_OPENED": _case_opened,
    "FILING_PREPARATION_STARTED": _filing_preparation_started,
    "FILING_EXTERNAL_SUBMISSION_RECORDED": _filing_external_submission_recorded,
    "FILING_RECEIPT_ARCHIVED": _filing_receipt_archived,
    "ACCEPTANCE_NOTICE_RECORDED": _acceptance_notice_recorded,
    "PRELIMINARY_EXAMINATION_STARTED": _preliminary_examination_started,
    "PRELIMINARY_EXAMINATION_PASSED": _preliminary_examination_passed,
    "RECTIFICATION_NOTICE_RECORDED": _rectification_notice_recorded,
    "PUBLICATION_NOTICE_RECORDED": _publication_notice_recorded,
    "SUBSTANTIVE_EXAMINATION_STARTED": _substantive_examination_started,
    "OA_NOTICE_RECORDED": _oa_notice_recorded,
    "OA_RECEIPT_ARCHIVED": _oa_receipt_archived,
    "REEXAMINATION_STARTED": _reexamination_started,
    "GRANT_REGISTRATION_NOTICE_RECORDED": _grant_registration_notice_recorded,
    "GRANT_ANNOUNCEMENT_CONFIRMED": _grant_announcement_confirmed,
    "PATENT_REGISTER_STATUS_CONFIRMED": _patent_register_status_confirmed,
    "APPLICATION_REJECTION_CONFIRMED": _application_rejection_confirmed,
    "APPLICATION_WITHDRAWAL_CONFIRMED": _application_withdrawal_confirmed,
    "APPLICATION_ABANDONMENT_CONFIRMED": _application_abandonment_confirmed,
    "PATENT_TERMINATION_CONFIRMED": _patent_termination_confirmed,
    "PATENT_EXPIRY_CONFIRMED": _patent_expiry_confirmed,
    "PATENT_INVALIDATION_CONFIRMED": _patent_invalidation_confirmed,
    "APPLICATION_RIGHT_RESTORATION_CONFIRMED": (
        _application_right_restoration_confirmed
    ),
    "PATENT_RIGHT_RESTORATION_CONFIRMED": _patent_right_restoration_confirmed,
}
