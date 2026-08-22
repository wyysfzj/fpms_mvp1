from __future__ import annotations

import ast
import dataclasses
import inspect
from dataclasses import FrozenInstanceError

import pytest

from app.modules.cases.lifecycle_contracts import (
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_projection import (
    LegacyCaseStatusProjection,
    LegacyProjectionConflictCode,
    LegacyProjectionDisposition,
    project_legacy_case_status,
)


def make_projection(
    *,
    business: BusinessStage | None = BusinessStage.PROSECUTION_MANAGEMENT,
    official: OfficialProcedureStage | None = OfficialProcedureStage.ACCEPTED,
    legal: LegalStatus | None = LegalStatus.APPLICATION_PENDING,
    verification: ConfirmationStatus | None = ConfirmationStatus.CONFIRMED,
) -> LifecycleProjection:
    return LifecycleProjection(
        business_stage=business,
        official_procedure_stage=official,
        legal_status=legal,
        lifecycle_verification_status=verification,
    )


def project(
    projection: LifecycleProjection,
    *,
    existing_status: str = "LEGACY",
    event_type: str | None = None,
    oa_sequence: int | None = None,
) -> LegacyCaseStatusProjection:
    return project_legacy_case_status(
        existing_status=existing_status,
        projection=projection,
        latest_confirmed_lifecycle_event_type=event_type,
        oa_sequence=oa_sequence,
    )


def test_public_contract_is_exact_and_result_is_frozen_slotted_keyword_only() -> None:
    import app.modules.cases.lifecycle_projection as module

    assert module.__all__ == (
        "LegacyCaseStatusProjection",
        "LegacyProjectionConflictCode",
        "LegacyProjectionDisposition",
        "project_legacy_case_status",
    )
    assert [(member.name, member.value) for member in LegacyProjectionConflictCode] == [
        ("AXIS_CONFLICT", "LEGACY_PROJECTION_AXIS_CONFLICT"),
        ("INCOMPLETE_AXES", "LEGACY_PROJECTION_INCOMPLETE_AXES"),
        ("MISSING_OA_SEQUENCE", "LEGACY_PROJECTION_MISSING_OA_SEQUENCE"),
        ("NO_MAPPING", "LEGACY_PROJECTION_NO_MAPPING"),
        ("UNKNOWN_LEGAL_STATUS", "LEGACY_PROJECTION_UNKNOWN_LEGAL_STATUS"),
        ("UNVERIFIED", "LEGACY_PROJECTION_UNVERIFIED"),
    ]
    assert [(member.name, member.value) for member in LegacyProjectionDisposition] == [
        ("UNCHANGED", "UNCHANGED"),
        ("UPDATE_REQUIRED", "UPDATE_REQUIRED"),
        ("RETAINED_CONFLICT", "RETAINED_CONFLICT"),
    ]

    result_fields = dataclasses.fields(LegacyCaseStatusProjection)
    assert [field.name for field in result_fields] == [
        "legacy_case_status",
        "derived_case_status",
        "disposition",
        "conflict_codes",
    ]
    assert result_fields[-1].default == ()
    assert (
        inspect.signature(LegacyCaseStatusProjection).parameters["legacy_case_status"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )

    result = LegacyCaseStatusProjection(
        legacy_case_status="PENDING",
        derived_case_status="PENDING",
        disposition=LegacyProjectionDisposition.UNCHANGED,
    )
    assert not hasattr(result, "__dict__")
    with pytest.raises(FrozenInstanceError):
        result.legacy_case_status = "OTHER"  # type: ignore[misc]
    with pytest.raises(TypeError):
        LegacyCaseStatusProjection(  # type: ignore[misc]
            "PENDING",
            "PENDING",
            LegacyProjectionDisposition.UNCHANGED,
        )


@pytest.mark.parametrize(
    (
        "business",
        "official",
        "legal",
        "event_type",
        "oa_sequence",
        "expected",
    ),
    [
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.PATENT_INVALIDATED,
            None,
            None,
            "INVALIDATED",
        ),
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.PATENT_TERMINATED,
            None,
            None,
            "TERMINATED",
        ),
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.PATENT_EXPIRED,
            None,
            None,
            "EXPIRED",
        ),
        (
            BusinessStage.POST_GRANT_MAINTENANCE,
            OfficialProcedureStage.GRANT_ANNOUNCED,
            LegalStatus.PATENT_IN_FORCE,
            None,
            None,
            "GRANTED",
        ),
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.APPLICATION_REJECTED,
            None,
            None,
            "REJECTED",
        ),
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.APPLICATION_WITHDRAWN,
            None,
            None,
            "WITHDRAWN",
        ),
        (
            BusinessStage.CLOSED,
            OfficialProcedureStage.PROCEDURE_CLOSED,
            LegalStatus.APPLICATION_ABANDONED,
            None,
            None,
            "ABANDONED",
        ),
        (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
            OfficialProcedureStage.GRANT_REGISTRATION,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "GRANT_PENDING",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.REEXAMINATION,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "REEXAM",
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            LegalStatus.APPLICATION_PENDING,
            None,
            1,
            "OA1",
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            LegalStatus.APPLICATION_PENDING,
            None,
            2,
            "OA2",
        ),
        (
            BusinessStage.OA_REPLY_IN_PROGRESS,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "AMENDMENT",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "SUB_EXAM",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PUBLISHED,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "PUBLISHED",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            LegalStatus.APPLICATION_PENDING,
            "PRELIMINARY_EXAMINATION_PASSED",
            None,
            "PRELIM_PASS",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            LegalStatus.APPLICATION_PENDING,
            "SOME_OPEN_EVENT",
            None,
            "PRELIM_EXAM",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.ACCEPTED,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "ACCEPTED",
        ),
        (
            BusinessStage.WAITING_EXTERNAL_RECEIPT,
            OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
            LegalStatus.NOT_ESTABLISHED,
            None,
            None,
            "WAITING_RECEIPT",
        ),
        (
            BusinessStage.PROSECUTION_MANAGEMENT,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
            LegalStatus.APPLICATION_PENDING,
            None,
            None,
            "WAITING_RECEIPT",
        ),
        (
            BusinessStage.NEW_CASE,
            OfficialProcedureStage.NOT_SUBMITTED,
            LegalStatus.NOT_ESTABLISHED,
            None,
            None,
            "NOT_FILED",
        ),
    ],
)
def test_every_currently_reachable_precedence_row(
    business: BusinessStage,
    official: OfficialProcedureStage,
    legal: LegalStatus,
    event_type: str | None,
    oa_sequence: int | None,
    expected: str,
) -> None:
    result = project(
        make_projection(business=business, official=official, legal=legal),
        event_type=event_type,
        oa_sequence=oa_sequence,
    )

    assert result == LegacyCaseStatusProjection(
        legacy_case_status=expected,
        derived_case_status=expected,
        disposition=LegacyProjectionDisposition.UPDATE_REQUIRED,
    )


@pytest.mark.parametrize(
    "verification",
    [None, ConfirmationStatus.NEEDS_REVIEW, ConfirmationStatus.LEGACY_UNVERIFIED],
)
def test_non_confirmed_projection_is_retained_as_unverified(
    verification: ConfirmationStatus | None,
) -> None:
    result = project(make_projection(verification=verification))

    assert result.conflict_codes == (LegacyProjectionConflictCode.UNVERIFIED,)


@pytest.mark.parametrize("missing_axis", ["business", "official", "legal"])
def test_each_nullable_axis_adds_one_incomplete_axes_conflict(
    missing_axis: str,
) -> None:
    values = {
        "business": BusinessStage.PROSECUTION_MANAGEMENT,
        "official": OfficialProcedureStage.ACCEPTED,
        "legal": LegalStatus.APPLICATION_PENDING,
    }
    values[missing_axis] = None

    result = project(make_projection(**values))  # type: ignore[arg-type]

    assert LegacyProjectionConflictCode.INCOMPLETE_AXES in result.conflict_codes
    assert result.conflict_codes.count(LegacyProjectionConflictCode.INCOMPLETE_AXES) == 1


def test_unknown_legal_status_is_retained() -> None:
    result = project(make_projection(legal=LegalStatus.UNKNOWN))

    assert result.conflict_codes == (LegacyProjectionConflictCode.UNKNOWN_LEGAL_STATUS,)


def test_conflicts_accumulate_sorted_and_duplicate_free() -> None:
    result = project(
        make_projection(
            business=None,
            official=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal=LegalStatus.UNKNOWN,
            verification=ConfirmationStatus.NEEDS_REVIEW,
        )
    )

    assert result.conflict_codes == (
        LegacyProjectionConflictCode.INCOMPLETE_AXES,
        LegacyProjectionConflictCode.UNKNOWN_LEGAL_STATUS,
        LegacyProjectionConflictCode.UNVERIFIED,
    )

    duplicate_axis_result = project(
        make_projection(
            business=BusinessStage.NEW_CASE,
            official=OfficialProcedureStage.GRANT_ANNOUNCED,
            legal=LegalStatus.APPLICATION_REJECTED,
            verification=ConfirmationStatus.NEEDS_REVIEW,
        )
    )
    assert duplicate_axis_result.conflict_codes == (
        LegacyProjectionConflictCode.AXIS_CONFLICT,
        LegacyProjectionConflictCode.UNVERIFIED,
    )


BUSINESS_OFFICIAL_ALLOWED = [
    (BusinessStage.NEW_CASE, OfficialProcedureStage.NOT_SUBMITTED),
    (BusinessStage.FILING_PREPARATION, OfficialProcedureStage.NOT_SUBMITTED),
    (
        BusinessStage.WAITING_EXTERNAL_RECEIPT,
        OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    ),
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
    (
        BusinessStage.POST_GRANT_MAINTENANCE,
        OfficialProcedureStage.GRANT_ANNOUNCED,
    ),
    (BusinessStage.CLOSED, OfficialProcedureStage.PROCEDURE_CLOSED),
]


@pytest.mark.parametrize(("business", "official"), BUSINESS_OFFICIAL_ALLOWED)
def test_every_allowed_business_official_pair_has_no_axis_conflict(
    business: BusinessStage,
    official: OfficialProcedureStage,
) -> None:
    result = project(make_projection(business=business, official=official, legal=None))

    assert LegacyProjectionConflictCode.AXIS_CONFLICT not in result.conflict_codes


@pytest.mark.parametrize("official", list(OfficialProcedureStage))
def test_every_official_stage_rejects_a_representative_disallowed_business(
    official: OfficialProcedureStage,
) -> None:
    allowed = {
        business
        for business, allowed_official in BUSINESS_OFFICIAL_ALLOWED
        if allowed_official is official
    }
    disallowed = next(business for business in BusinessStage if business not in allowed)

    result = project(make_projection(business=disallowed, official=official, legal=None))

    assert LegacyProjectionConflictCode.AXIS_CONFLICT in result.conflict_codes


LEGAL_OFFICIAL_ALLOWED = [
    (LegalStatus.NOT_ESTABLISHED, OfficialProcedureStage.NOT_SUBMITTED),
    (
        LegalStatus.NOT_ESTABLISHED,
        OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT,
    ),
    *[
        (LegalStatus.APPLICATION_PENDING, official)
        for official in (
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
            OfficialProcedureStage.ACCEPTED,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION,
            OfficialProcedureStage.RECTIFICATION_RESPONSE,
            OfficialProcedureStage.PUBLISHED,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
            OfficialProcedureStage.REEXAMINATION,
            OfficialProcedureStage.GRANT_REGISTRATION,
        )
    ],
    (LegalStatus.APPLICATION_REJECTED, OfficialProcedureStage.PROCEDURE_CLOSED),
    (LegalStatus.APPLICATION_WITHDRAWN, OfficialProcedureStage.PROCEDURE_CLOSED),
    (LegalStatus.APPLICATION_ABANDONED, OfficialProcedureStage.PROCEDURE_CLOSED),
    (LegalStatus.PATENT_IN_FORCE, OfficialProcedureStage.GRANT_ANNOUNCED),
    (LegalStatus.PATENT_TERMINATED, OfficialProcedureStage.PROCEDURE_CLOSED),
    (LegalStatus.PATENT_EXPIRED, OfficialProcedureStage.PROCEDURE_CLOSED),
    (LegalStatus.PATENT_INVALIDATED, OfficialProcedureStage.PROCEDURE_CLOSED),
]


@pytest.mark.parametrize(("legal", "official"), LEGAL_OFFICIAL_ALLOWED)
def test_every_allowed_legal_official_pair_has_no_axis_conflict(
    legal: LegalStatus,
    official: OfficialProcedureStage,
) -> None:
    result = project(make_projection(business=None, official=official, legal=legal))

    assert LegacyProjectionConflictCode.AXIS_CONFLICT not in result.conflict_codes


@pytest.mark.parametrize(
    "legal", [legal for legal in LegalStatus if legal is not LegalStatus.UNKNOWN]
)
def test_every_known_legal_status_rejects_a_disallowed_official(
    legal: LegalStatus,
) -> None:
    allowed = {
        official for allowed_legal, official in LEGAL_OFFICIAL_ALLOWED if allowed_legal is legal
    }
    disallowed = next(official for official in OfficialProcedureStage if official not in allowed)

    result = project(make_projection(business=None, official=disallowed, legal=legal))

    assert LegacyProjectionConflictCode.AXIS_CONFLICT in result.conflict_codes


def test_oa_sequence_boundaries_and_non_oa_sequence_ignoring() -> None:
    oa_projection = make_projection(
        business=BusinessStage.OA_REPLY_IN_PROGRESS,
        official=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
    )
    missing = project(oa_projection, oa_sequence=None)
    assert missing.conflict_codes == (LegacyProjectionConflictCode.MISSING_OA_SEQUENCE,)
    assert project(oa_projection, oa_sequence=1).derived_case_status == "OA1"
    assert project(oa_projection, oa_sequence=2).derived_case_status == "OA2"
    assert project(oa_projection, oa_sequence=8).derived_case_status == "OA2"

    accepted = make_projection(official=OfficialProcedureStage.ACCEPTED)
    assert project(accepted, oa_sequence=27).derived_case_status == "ACCEPTED"


@pytest.mark.parametrize(
    ("oa_sequence", "error_type", "message"),
    [
        (True, TypeError, "oa_sequence must be int or None"),
        (1.5, TypeError, "oa_sequence must be int or None"),
        (0, ValueError, "oa_sequence must be positive when provided"),
        (-1, ValueError, "oa_sequence must be positive when provided"),
    ],
)
def test_invalid_oa_sequence_errors_are_exact(
    oa_sequence: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=f"^{message}$"):
        project_legacy_case_status(
            existing_status="LEGACY",
            projection=make_projection(),
            latest_confirmed_lifecycle_event_type=None,
            oa_sequence=oa_sequence,  # type: ignore[arg-type]
        )


def test_dispositions_and_exact_legacy_retention() -> None:
    accepted = make_projection()
    assert project(accepted, existing_status="ACCEPTED") == LegacyCaseStatusProjection(
        legacy_case_status="ACCEPTED",
        derived_case_status="ACCEPTED",
        disposition=LegacyProjectionDisposition.UNCHANGED,
    )
    assert project(accepted, existing_status="PENDING") == LegacyCaseStatusProjection(
        legacy_case_status="ACCEPTED",
        derived_case_status="ACCEPTED",
        disposition=LegacyProjectionDisposition.UPDATE_REQUIRED,
    )

    unverified = make_projection(verification=ConfirmationStatus.LEGACY_UNVERIFIED)
    assert project(unverified, existing_status="ACCEPTED") == LegacyCaseStatusProjection(
        legacy_case_status="ACCEPTED",
        derived_case_status=None,
        disposition=LegacyProjectionDisposition.RETAINED_CONFLICT,
        conflict_codes=(LegacyProjectionConflictCode.UNVERIFIED,),
    )
    assert project(unverified, existing_status="CUSTOM_STATUS") == LegacyCaseStatusProjection(
        legacy_case_status="CUSTOM_STATUS",
        derived_case_status=None,
        disposition=LegacyProjectionDisposition.RETAINED_CONFLICT,
        conflict_codes=(LegacyProjectionConflictCode.UNVERIFIED,),
    )


@pytest.mark.parametrize(
    ("kwargs", "error_type", "message"),
    [
        ({"existing_status": None}, TypeError, "existing_status must be str"),
        ({"existing_status": "  "}, ValueError, "existing_status must be non-empty"),
        (
            {"projection": object()},
            TypeError,
            "projection must be LifecycleProjection",
        ),
        (
            {"projection": make_projection(business="NEW_CASE")},
            TypeError,
            "projection.business_stage must be BusinessStage or None",
        ),
        (
            {"projection": make_projection(official="ACCEPTED")},
            TypeError,
            "projection.official_procedure_stage must be OfficialProcedureStage or None",
        ),
        (
            {"projection": make_projection(legal="APPLICATION_PENDING")},
            TypeError,
            "projection.legal_status must be LegalStatus or None",
        ),
        (
            {"projection": make_projection(verification="CONFIRMED")},
            TypeError,
            "projection.lifecycle_verification_status must be ConfirmationStatus or None",
        ),
        (
            {"latest_confirmed_lifecycle_event_type": 42},
            TypeError,
            "latest_confirmed_lifecycle_event_type must be str or None",
        ),
        (
            {"latest_confirmed_lifecycle_event_type": " \t"},
            ValueError,
            "latest_confirmed_lifecycle_event_type must be non-empty when provided",
        ),
    ],
)
def test_validation_errors_are_exact(
    kwargs: dict[str, object],
    error_type: type[Exception],
    message: str,
) -> None:
    valid: dict[str, object] = {
        "existing_status": "LEGACY",
        "projection": make_projection(),
        "latest_confirmed_lifecycle_event_type": None,
        "oa_sequence": None,
    }
    valid.update(kwargs)

    with pytest.raises(error_type, match=f"^{message}$"):
        project_legacy_case_status(**valid)  # type: ignore[arg-type]


def test_projection_is_pure_deterministic_and_has_no_persistence_imports_or_calls() -> None:
    import app.modules.cases.lifecycle_projection as module

    projection = make_projection(
        business=BusinessStage.PROSECUTION_MANAGEMENT,
        official=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    )
    before = dataclasses.asdict(projection)
    first = project(
        projection,
        existing_status="CUSTOM",
        event_type="PRELIMINARY_EXAMINATION_PASSED",
        oa_sequence=3,
    )
    second = project(
        projection,
        existing_status="CUSTOM",
        event_type="PRELIMINARY_EXAMINATION_PASSED",
        oa_sequence=3,
    )
    assert dataclasses.asdict(projection) == before
    assert first == second

    tree = ast.parse(inspect.getsource(module))
    imported_modules = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not any(
        prohibited in imported.lower()
        for imported in imported_modules
        for prohibited in ("sqlalchemy", "fastapi", "model", "session")
    )
    prohibited_calls = {"commit", "delete", "execute", "flush", "query", "rollback"}
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert prohibited_calls.isdisjoint(called_attributes)
