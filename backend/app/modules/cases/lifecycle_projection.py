from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.modules.cases.lifecycle_contracts import (
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleProjection,
    OfficialProcedureStage,
)

__all__ = (
    "LegacyCaseStatusProjection",
    "LegacyProjectionConflictCode",
    "LegacyProjectionDisposition",
    "project_legacy_case_status",
)


class LegacyProjectionConflictCode(StrEnum):
    AXIS_CONFLICT = "LEGACY_PROJECTION_AXIS_CONFLICT"
    INCOMPLETE_AXES = "LEGACY_PROJECTION_INCOMPLETE_AXES"
    MISSING_OA_SEQUENCE = "LEGACY_PROJECTION_MISSING_OA_SEQUENCE"
    NO_MAPPING = "LEGACY_PROJECTION_NO_MAPPING"
    UNKNOWN_LEGAL_STATUS = "LEGACY_PROJECTION_UNKNOWN_LEGAL_STATUS"
    UNVERIFIED = "LEGACY_PROJECTION_UNVERIFIED"


class LegacyProjectionDisposition(StrEnum):
    UNCHANGED = "UNCHANGED"
    UPDATE_REQUIRED = "UPDATE_REQUIRED"
    RETAINED_CONFLICT = "RETAINED_CONFLICT"


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyCaseStatusProjection:
    legacy_case_status: str
    derived_case_status: str | None
    disposition: LegacyProjectionDisposition
    conflict_codes: tuple[LegacyProjectionConflictCode, ...] = ()


_ALLOWED_BUSINESS_BY_OFFICIAL = {
    OfficialProcedureStage.NOT_SUBMITTED: {
        BusinessStage.NEW_CASE,
        BusinessStage.FILING_PREPARATION,
    },
    OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT: {BusinessStage.WAITING_EXTERNAL_RECEIPT},
    OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE: {
        BusinessStage.PROSECUTION_MANAGEMENT
    },
    OfficialProcedureStage.ACCEPTED: {BusinessStage.PROSECUTION_MANAGEMENT},
    OfficialProcedureStage.PRELIMINARY_EXAMINATION: {BusinessStage.PROSECUTION_MANAGEMENT},
    OfficialProcedureStage.RECTIFICATION_RESPONSE: {BusinessStage.OA_REPLY_IN_PROGRESS},
    OfficialProcedureStage.PUBLISHED: {BusinessStage.PROSECUTION_MANAGEMENT},
    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION: {BusinessStage.PROSECUTION_MANAGEMENT},
    OfficialProcedureStage.OFFICE_ACTION_RESPONSE: {BusinessStage.OA_REPLY_IN_PROGRESS},
    OfficialProcedureStage.REEXAMINATION: {BusinessStage.PROSECUTION_MANAGEMENT},
    OfficialProcedureStage.GRANT_REGISTRATION: {BusinessStage.GRANT_REGISTRATION_IN_PROGRESS},
    OfficialProcedureStage.GRANT_ANNOUNCED: {BusinessStage.POST_GRANT_MAINTENANCE},
    OfficialProcedureStage.PROCEDURE_CLOSED: {BusinessStage.CLOSED},
}

_ALLOWED_OFFICIAL_BY_LEGAL = {
    LegalStatus.NOT_ESTABLISHED: {
        OfficialProcedureStage.NOT_SUBMITTED,
        OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    },
    LegalStatus.APPLICATION_PENDING: {
        OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
        OfficialProcedureStage.ACCEPTED,
        OfficialProcedureStage.PRELIMINARY_EXAMINATION,
        OfficialProcedureStage.RECTIFICATION_RESPONSE,
        OfficialProcedureStage.PUBLISHED,
        OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
        OfficialProcedureStage.REEXAMINATION,
        OfficialProcedureStage.GRANT_REGISTRATION,
    },
    LegalStatus.APPLICATION_REJECTED: {OfficialProcedureStage.PROCEDURE_CLOSED},
    LegalStatus.APPLICATION_WITHDRAWN: {OfficialProcedureStage.PROCEDURE_CLOSED},
    LegalStatus.APPLICATION_ABANDONED: {OfficialProcedureStage.PROCEDURE_CLOSED},
    LegalStatus.PATENT_IN_FORCE: {OfficialProcedureStage.GRANT_ANNOUNCED},
    LegalStatus.PATENT_TERMINATED: {OfficialProcedureStage.PROCEDURE_CLOSED},
    LegalStatus.PATENT_EXPIRED: {OfficialProcedureStage.PROCEDURE_CLOSED},
    LegalStatus.PATENT_INVALIDATED: {OfficialProcedureStage.PROCEDURE_CLOSED},
}


def _validate_inputs(
    *,
    existing_status: str,
    projection: LifecycleProjection,
    latest_confirmed_lifecycle_event_type: str | None,
    oa_sequence: int | None,
) -> None:
    if not isinstance(existing_status, str):
        raise TypeError("existing_status must be str")
    if not existing_status.strip():
        raise ValueError("existing_status must be non-empty")
    if not isinstance(projection, LifecycleProjection):
        raise TypeError("projection must be LifecycleProjection")
    if projection.business_stage is not None and not isinstance(
        projection.business_stage, BusinessStage
    ):
        raise TypeError("projection.business_stage must be BusinessStage or None")
    if projection.official_procedure_stage is not None and not isinstance(
        projection.official_procedure_stage, OfficialProcedureStage
    ):
        raise TypeError(
            "projection.official_procedure_stage must be OfficialProcedureStage or None"
        )
    if projection.legal_status is not None and not isinstance(projection.legal_status, LegalStatus):
        raise TypeError("projection.legal_status must be LegalStatus or None")
    if projection.lifecycle_verification_status is not None and not isinstance(
        projection.lifecycle_verification_status, ConfirmationStatus
    ):
        raise TypeError(
            "projection.lifecycle_verification_status must be ConfirmationStatus or None"
        )
    if latest_confirmed_lifecycle_event_type is not None and not isinstance(
        latest_confirmed_lifecycle_event_type, str
    ):
        raise TypeError("latest_confirmed_lifecycle_event_type must be str or None")
    if (
        latest_confirmed_lifecycle_event_type is not None
        and not latest_confirmed_lifecycle_event_type.strip()
    ):
        raise ValueError("latest_confirmed_lifecycle_event_type must be non-empty when provided")
    if oa_sequence is not None and (
        isinstance(oa_sequence, bool) or not isinstance(oa_sequence, int)
    ):
        raise TypeError("oa_sequence must be int or None")
    if oa_sequence is not None and oa_sequence < 1:
        raise ValueError("oa_sequence must be positive when provided")


def _derive_case_status(
    *,
    projection: LifecycleProjection,
    latest_confirmed_lifecycle_event_type: str | None,
    oa_sequence: int | None,
) -> str | None:
    legal = projection.legal_status
    official = projection.official_procedure_stage

    terminal_legal_statuses = {
        LegalStatus.PATENT_INVALIDATED: "INVALIDATED",
        LegalStatus.PATENT_TERMINATED: "TERMINATED",
        LegalStatus.PATENT_EXPIRED: "EXPIRED",
        LegalStatus.PATENT_IN_FORCE: "GRANTED",
        LegalStatus.APPLICATION_REJECTED: "REJECTED",
        LegalStatus.APPLICATION_WITHDRAWN: "WITHDRAWN",
        LegalStatus.APPLICATION_ABANDONED: "ABANDONED",
    }
    if legal in terminal_legal_statuses:
        return terminal_legal_statuses[legal]
    if official is OfficialProcedureStage.GRANT_REGISTRATION:
        return "GRANT_PENDING"
    if official is OfficialProcedureStage.REEXAMINATION:
        return "REEXAM"
    if official is OfficialProcedureStage.OFFICE_ACTION_RESPONSE:
        return "OA1" if oa_sequence == 1 else "OA2"
    if official is OfficialProcedureStage.RECTIFICATION_RESPONSE:
        return "AMENDMENT"
    if official is OfficialProcedureStage.SUBSTANTIVE_EXAMINATION:
        return "SUB_EXAM"
    if official is OfficialProcedureStage.PUBLISHED:
        return "PUBLISHED"
    if (
        official is OfficialProcedureStage.PRELIMINARY_EXAMINATION
        and latest_confirmed_lifecycle_event_type == "PRELIMINARY_EXAMINATION_PASSED"
    ):
        return "PRELIM_PASS"
    if official is OfficialProcedureStage.PRELIMINARY_EXAMINATION:
        return "PRELIM_EXAM"
    if official is OfficialProcedureStage.ACCEPTED:
        return "ACCEPTED"
    if official in {
        OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
        OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
    }:
        return "WAITING_RECEIPT"
    if legal is LegalStatus.APPLICATION_PENDING:
        return "PENDING"
    if official is OfficialProcedureStage.NOT_SUBMITTED:
        return "NOT_FILED"
    return None


def project_legacy_case_status(
    *,
    existing_status: str,
    projection: LifecycleProjection,
    latest_confirmed_lifecycle_event_type: str | None,
    oa_sequence: int | None,
) -> LegacyCaseStatusProjection:
    _validate_inputs(
        existing_status=existing_status,
        projection=projection,
        latest_confirmed_lifecycle_event_type=latest_confirmed_lifecycle_event_type,
        oa_sequence=oa_sequence,
    )

    conflicts: set[LegacyProjectionConflictCode] = set()
    business = projection.business_stage
    official = projection.official_procedure_stage
    legal = projection.legal_status

    if projection.lifecycle_verification_status is not ConfirmationStatus.CONFIRMED:
        conflicts.add(LegacyProjectionConflictCode.UNVERIFIED)
    if business is None or official is None or legal is None:
        conflicts.add(LegacyProjectionConflictCode.INCOMPLETE_AXES)
    if legal is LegalStatus.UNKNOWN:
        conflicts.add(LegacyProjectionConflictCode.UNKNOWN_LEGAL_STATUS)
    if (
        business is not None
        and official is not None
        and business not in _ALLOWED_BUSINESS_BY_OFFICIAL[official]
    ):
        conflicts.add(LegacyProjectionConflictCode.AXIS_CONFLICT)
    if (
        legal is not None
        and legal is not LegalStatus.UNKNOWN
        and official is not None
        and official not in _ALLOWED_OFFICIAL_BY_LEGAL[legal]
    ):
        conflicts.add(LegacyProjectionConflictCode.AXIS_CONFLICT)
    if official is OfficialProcedureStage.OFFICE_ACTION_RESPONSE and oa_sequence is None:
        conflicts.add(LegacyProjectionConflictCode.MISSING_OA_SEQUENCE)

    if conflicts:
        return LegacyCaseStatusProjection(
            legacy_case_status=existing_status,
            derived_case_status=None,
            disposition=LegacyProjectionDisposition.RETAINED_CONFLICT,
            conflict_codes=tuple(sorted(conflicts, key=lambda code: code.value)),
        )

    derived_status = _derive_case_status(
        projection=projection,
        latest_confirmed_lifecycle_event_type=latest_confirmed_lifecycle_event_type,
        oa_sequence=oa_sequence,
    )
    if derived_status is None:
        return LegacyCaseStatusProjection(
            legacy_case_status=existing_status,
            derived_case_status=None,
            disposition=LegacyProjectionDisposition.RETAINED_CONFLICT,
            conflict_codes=(LegacyProjectionConflictCode.NO_MAPPING,),
        )

    disposition = (
        LegacyProjectionDisposition.UNCHANGED
        if derived_status == existing_status
        else LegacyProjectionDisposition.UPDATE_REQUIRED
    )
    return LegacyCaseStatusProjection(
        legacy_case_status=derived_status,
        derived_case_status=derived_status,
        disposition=disposition,
    )
