from __future__ import annotations

import ast
import importlib
import inspect
from collections.abc import Mapping
from dataclasses import MISSING, FrozenInstanceError, fields
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import get_type_hints

import pytest

MODULE_NAME = "app.modules.cases.lifecycle_contracts"

EXPORTS = (
    "ActivityLane",
    "BusinessStage",
    "ConfirmationStatus",
    "EvidenceReference",
    "LegalStatus",
    "LifecycleEventCommand",
    "LifecycleProjection",
    "LifecycleTransitionResult",
    "OfficialProcedureStage",
)

ENUM_VALUES = {
    "BusinessStage": (
        "NEW_CASE",
        "FILING_PREPARATION",
        "WAITING_EXTERNAL_RECEIPT",
        "PROSECUTION_MANAGEMENT",
        "OA_REPLY_IN_PROGRESS",
        "GRANT_REGISTRATION_IN_PROGRESS",
        "POST_GRANT_MAINTENANCE",
        "CLOSED",
    ),
    "OfficialProcedureStage": (
        "NOT_SUBMITTED",
        "SUBMITTED_WAITING_RECEIPT",
        "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE",
        "ACCEPTED",
        "PRELIMINARY_EXAMINATION",
        "RECTIFICATION_RESPONSE",
        "PUBLISHED",
        "SUBSTANTIVE_EXAMINATION",
        "OFFICE_ACTION_RESPONSE",
        "REEXAMINATION",
        "GRANT_REGISTRATION",
        "GRANT_ANNOUNCED",
        "PROCEDURE_CLOSED",
    ),
    "LegalStatus": (
        "NOT_ESTABLISHED",
        "APPLICATION_PENDING",
        "APPLICATION_REJECTED",
        "APPLICATION_WITHDRAWN",
        "APPLICATION_ABANDONED",
        "PATENT_IN_FORCE",
        "PATENT_TERMINATED",
        "PATENT_EXPIRED",
        "PATENT_INVALIDATED",
        "UNKNOWN",
    ),
    "ActivityLane": (
        "LIFECYCLE",
        "DOCUMENT",
        "FEE",
    ),
    "ConfirmationStatus": (
        "NEEDS_REVIEW",
        "CONFIRMED",
        "LEGACY_UNVERIFIED",
    ),
}


def _module():
    return importlib.import_module(MODULE_NAME)


def test_module_exports_only_the_frozen_contract() -> None:
    module = _module()

    assert module.__all__ == EXPORTS
    for name in EXPORTS:
        assert hasattr(module, name)
    assert not hasattr(module, "Protocol")

    source_path = Path(module.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert imported_roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "datetime",
        "enum",
    }


@pytest.mark.parametrize(("enum_name", "expected_values"), ENUM_VALUES.items())
def test_enums_have_exact_stable_string_values(
    enum_name: str,
    expected_values: tuple[str, ...],
) -> None:
    enum_type = getattr(_module(), enum_name)

    assert issubclass(enum_type, StrEnum)
    assert tuple(enum_type.__members__) == expected_values
    assert tuple(member.value for member in enum_type) == expected_values
    assert all(member.name == member.value for member in enum_type)
    with pytest.raises(ValueError):
        enum_type(expected_values[0].lower())


def test_dataclass_shapes_match_the_frozen_interface() -> None:
    module = _module()
    projection = module.LifecycleProjection
    evidence = module.EvidenceReference
    command = module.LifecycleEventCommand
    result = module.LifecycleTransitionResult
    required = MISSING

    expected = {
        projection: (
            ("business_stage", module.BusinessStage | None, required),
            (
                "official_procedure_stage",
                module.OfficialProcedureStage | None,
                required,
            ),
            ("legal_status", module.LegalStatus | None, required),
            (
                "lifecycle_verification_status",
                module.ConfirmationStatus | None,
                required,
            ),
        ),
        evidence: (
            ("case_id", str, required),
            ("evidence_kind", str, required),
            ("object_type", str, required),
            ("object_id", str, required),
            ("content_hash", str, required),
            ("captured_at", datetime, required),
        ),
        command: (
            ("case_id", str, required),
            ("event_type", str, required),
            ("lane", module.ActivityLane, required),
            ("effective_at", datetime, required),
            ("evidence_refs", tuple[evidence, ...], required),
            ("actor_id", str, required),
            ("idempotency_key", str, required),
            ("confirmation_status", module.ConfirmationStatus, required),
            ("payload", Mapping[str, object], required),
            ("occurred_at", datetime | None, None),
            ("reviewer_id", str | None, None),
            ("source_activity_id", str | None, None),
            ("supersedes_event_id", str | None, None),
        ),
        result: (
            ("case_id", str, required),
            ("activity_id", str, required),
            ("sequence", int, required),
            ("lifecycle_revision", int, required),
            ("lane", module.ActivityLane, required),
            ("event_type", str, required),
            ("confirmation_status", module.ConfirmationStatus, required),
            ("previous_projection", projection, required),
            ("current_projection", projection, required),
            ("legacy_case_status", str, required),
            ("idempotency_key", str, required),
            ("reused", bool, required),
            ("conflict_codes", tuple[str, ...], ()),
        ),
    }

    for data_type, expected_fields in expected.items():
        actual_fields = fields(data_type)
        hints = get_type_hints(data_type)
        assert tuple(data_type.__slots__) == tuple(item[0] for item in expected_fields)
        assert tuple(field.name for field in actual_fields) == tuple(
            item[0] for item in expected_fields
        )
        assert tuple(hints[field.name] for field in actual_fields) == tuple(
            item[1] for item in expected_fields
        )
        assert tuple(field.default for field in actual_fields) == tuple(
            item[2] for item in expected_fields
        )
        assert all(field.default_factory is MISSING for field in actual_fields)
        assert all(field.kw_only for field in actual_fields)
        assert data_type.__dataclass_params__.frozen is True
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in inspect.signature(data_type).parameters.values()
        )
        assert "__post_init__" not in data_type.__dict__
        with pytest.raises(TypeError):
            data_type(None)


def test_value_objects_are_immutable_and_preserve_explicit_nulls_and_defaults() -> None:
    module = _module()
    projection = module.LifecycleProjection(
        business_stage=None,
        official_procedure_stage=None,
        legal_status=None,
        lifecycle_verification_status=None,
    )
    evidence = module.EvidenceReference(
        case_id="case-1",
        evidence_kind="OFFICIAL_NOTICE",
        object_type="DOCUMENT_EVIDENCE_VERSION",
        object_id="evidence-1",
        content_hash="sha256:abc",
        captured_at=datetime(2026, 7, 13, 14, 0, 0),
    )
    command = module.LifecycleEventCommand(
        case_id="case-1",
        event_type="FUTURE_RULE_OWNED_EVENT",
        lane=module.ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 7, 13, 14, 0, 0),
        evidence_refs=(evidence,),
        actor_id="actor-1",
        idempotency_key="case-1:event-1",
        confirmation_status=module.ConfirmationStatus.NEEDS_REVIEW,
        payload={"source": "review"},
    )
    result = module.LifecycleTransitionResult(
        case_id="case-1",
        activity_id="activity-1",
        sequence=1,
        lifecycle_revision=1,
        lane=module.ActivityLane.LIFECYCLE,
        event_type=command.event_type,
        confirmation_status=command.confirmation_status,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status="NOT_FILED",
        idempotency_key=command.idempotency_key,
        reused=False,
    )

    assert command.occurred_at is None
    assert command.reviewer_id is None
    assert command.source_activity_id is None
    assert command.supersedes_event_id is None
    assert result.conflict_codes == ()
    assert result.previous_projection is result.current_projection
    with pytest.raises(FrozenInstanceError):
        command.case_id = "case-2"
    with pytest.raises(FrozenInstanceError):
        result.reused = True
