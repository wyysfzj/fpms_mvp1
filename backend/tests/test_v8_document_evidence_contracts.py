from __future__ import annotations

import ast
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import get_type_hints

import pytest

from app.modules.documents import evidence_contracts
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
    RegisterEvidenceDerivationCommand,
    RegisterEvidenceVersionCommand,
)

EXPECTED_EXPORTS = [
    "EvidenceRole",
    "EvidenceVersionState",
    "EvidenceReviewState",
    "EvidenceDerivationType",
    "RegisterEvidenceVersionCommand",
    "EvidenceVersionResult",
    "RegisterEvidenceDerivationCommand",
    "EvidenceDerivationResult",
]

ENUM_MEMBERS = {
    EvidenceRole: [
        ("FILING_FULL_WORD", "FILING_FULL_WORD"),
        ("TRACKED_REVISED_WORD", "TRACKED_REVISED_WORD"),
        ("FILING_COMPONENT", "FILING_COMPONENT"),
        ("EXTERNAL_XML_PACKAGE", "EXTERNAL_XML_PACKAGE"),
        ("OFFICIAL_SUBMISSION_LIST", "OFFICIAL_SUBMISSION_LIST"),
        ("OFFICIAL_FINAL_PDF", "OFFICIAL_FINAL_PDF"),
        ("SUBMITTED_XML", "SUBMITTED_XML"),
        ("OFFICIAL_RECEIPT", "OFFICIAL_RECEIPT"),
        ("CLIENT_LETTER_WORD", "CLIENT_LETTER_WORD"),
        ("RAW_ATTACHMENT", "RAW_ATTACHMENT"),
        ("GENERATED_ATTACHMENT", "GENERATED_ATTACHMENT"),
        ("OA_STRUCTURED_ATTACHMENT", "OA_STRUCTURED_ATTACHMENT"),
    ],
    EvidenceVersionState: [("DRAFT", "DRAFT"), ("FINAL", "FINAL")],
    EvidenceReviewState: [
        ("PENDING", "PENDING"),
        ("APPROVED", "APPROVED"),
        ("REJECTED", "REJECTED"),
    ],
    EvidenceDerivationType: [
        ("REVISION", "REVISION"),
        ("COMPONENT_EXTRACTION", "COMPONENT_EXTRACTION"),
        ("FORMAT_CONVERSION", "FORMAT_CONVERSION"),
        ("OFFICIAL_RECOGNITION", "OFFICIAL_RECOGNITION"),
        ("EXTERNAL_SUBMISSION", "EXTERNAL_SUBMISSION"),
        ("RECEIPT_LINK", "RECEIPT_LINK"),
        ("CUSTOMER_LETTER_RENDER", "CUSTOMER_LETTER_RENDER"),
        ("OA_REPLY_PREPARATION", "OA_REPLY_PREPARATION"),
    ],
}

DATACLASS_FIELDS = {
    RegisterEvidenceVersionCommand: [
        ("case_id", str),
        ("document_id", str),
        ("attachment_id", str),
        ("lineage_key", str),
        ("role", EvidenceRole),
        ("state", EvidenceVersionState),
        ("creator_id", str),
        ("content_hash", str),
    ],
    EvidenceVersionResult: [
        ("evidence_version_id", str),
        ("case_id", str),
        ("document_id", str),
        ("attachment_id", str),
        ("lineage_key", str),
        ("role", EvidenceRole),
        ("version_number", int),
        ("state", EvidenceVersionState),
        ("creator_id", str),
        ("review_state", EvidenceReviewState),
        ("reviewer_id", str | None),
        ("reviewed_at", datetime | None),
        ("final_submitted_at", datetime | None),
        ("content_hash", str),
        ("is_current", bool),
        ("is_final", bool),
    ],
    RegisterEvidenceDerivationCommand: [
        ("case_id", str),
        ("parent_evidence_version_id", str),
        ("child_evidence_version_id", str),
        ("derivation_type", EvidenceDerivationType),
        ("actor_id", str),
        ("derived_at", datetime),
        ("source_snapshot", str),
    ],
    EvidenceDerivationResult: [
        ("evidence_derivation_id", str),
        ("case_id", str),
        ("parent_evidence_version_id", str),
        ("child_evidence_version_id", str),
        ("derivation_type", EvidenceDerivationType),
        ("actor_id", str),
        ("derived_at", datetime),
        ("source_snapshot", str),
    ],
}


def test_public_exports_and_enum_values_are_exact() -> None:
    assert evidence_contracts.__all__ == EXPECTED_EXPORTS

    for enum_type, expected_members in ENUM_MEMBERS.items():
        assert issubclass(enum_type, str)
        assert issubclass(enum_type, Enum)
        assert [(member.name, member.value) for member in enum_type] == expected_members


def test_frozen_slotted_dataclass_shapes_are_exact() -> None:
    for dataclass_type, expected_fields in DATACLASS_FIELDS.items():
        assert is_dataclass(dataclass_type)
        assert dataclass_type.__dataclass_params__.frozen is True
        assert "__slots__" in dataclass_type.__dict__
        assert list(get_type_hints(dataclass_type).items()) == expected_fields

        actual_fields = fields(dataclass_type)
        assert [item.name for item in actual_fields] == [name for name, _ in expected_fields]
        assert all(item.default is MISSING for item in actual_fields)
        assert all(item.default_factory is MISSING for item in actual_fields)


def test_contract_instances_are_value_objects_and_reject_mutation() -> None:
    version_command = RegisterEvidenceVersionCommand(
        case_id="case-1",
        document_id="document-1",
        attachment_id="attachment-1",
        lineage_key="filing-main",
        role=EvidenceRole.FILING_FULL_WORD,
        state=EvidenceVersionState.DRAFT,
        creator_id="user-1",
        content_hash=f"sha256:{'a' * 64}",
    )
    assert version_command == RegisterEvidenceVersionCommand(
        case_id="case-1",
        document_id="document-1",
        attachment_id="attachment-1",
        lineage_key="filing-main",
        role=EvidenceRole.FILING_FULL_WORD,
        state=EvidenceVersionState.DRAFT,
        creator_id="user-1",
        content_hash=f"sha256:{'a' * 64}",
    )
    assert not hasattr(version_command, "__dict__")
    with pytest.raises(FrozenInstanceError):
        version_command.case_id = "case-2"  # type: ignore[misc]

    version_result = EvidenceVersionResult(
        evidence_version_id="version-1",
        case_id="case-1",
        document_id="document-1",
        attachment_id="attachment-1",
        lineage_key="filing-main",
        role=EvidenceRole.FILING_FULL_WORD,
        version_number=1,
        state=EvidenceVersionState.FINAL,
        creator_id="user-1",
        review_state=EvidenceReviewState.APPROVED,
        reviewer_id="user-2",
        reviewed_at=datetime(2026, 7, 13, 14, 0),
        final_submitted_at=None,
        content_hash=f"sha256:{'a' * 64}",
        is_current=True,
        is_final=True,
    )
    assert version_result.reviewer_id == "user-2"
    assert version_result.final_submitted_at is None

    derived_at = datetime(2026, 7, 13, 14, 30)
    source_snapshot = '{"source_evidence_version_id":"version-1"}'
    derivation_command = RegisterEvidenceDerivationCommand(
        case_id="case-1",
        parent_evidence_version_id="version-1",
        child_evidence_version_id="version-2",
        derivation_type=EvidenceDerivationType.FORMAT_CONVERSION,
        actor_id="user-1",
        derived_at=derived_at,
        source_snapshot=source_snapshot,
    )
    derivation_result = EvidenceDerivationResult(
        evidence_derivation_id="derivation-1",
        case_id=derivation_command.case_id,
        parent_evidence_version_id=derivation_command.parent_evidence_version_id,
        child_evidence_version_id=derivation_command.child_evidence_version_id,
        derivation_type=derivation_command.derivation_type,
        actor_id=derivation_command.actor_id,
        derived_at=derivation_command.derived_at,
        source_snapshot=derivation_command.source_snapshot,
    )
    assert derivation_result.source_snapshot == source_snapshot


def test_contract_module_is_stdlib_only_and_declares_no_service_functions() -> None:
    module_path = Path(evidence_contracts.__file__ or "")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    allowed_roots = {"__future__", "dataclasses", "datetime", "enum"}

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_roots.add(node.module.split(".", maxsplit=1)[0])

    assert imported_roots <= allowed_roots
    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in tree.body)
