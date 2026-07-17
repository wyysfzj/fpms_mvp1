from __future__ import annotations

import inspect
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import date, datetime
from typing import get_type_hints

import pytest

from app.modules.cases import lifecycle_overlay_schemas as overlay
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceVersionResult,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationStatuses,
    FeeSourceStatus,
)
from app.modules.system.decision_gate_service import DecisionGateCode


def _assert_value_contract(cls: type, expected: dict[str, object]) -> None:
    assert is_dataclass(cls)
    assert cls.__dataclass_params__.frozen is True
    assert "__dict__" not in cls.__dict__
    assert tuple(field.name for field in fields(cls)) == tuple(expected)
    assert get_type_hints(cls) == expected
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(cls).parameters.values()
    )


def test_overlay_exports_exact_reused_types_enums_and_dto_contracts() -> None:
    assert tuple(overlay.OverlayCenterAxis) == (
        overlay.OverlayCenterAxis.BUSINESS_STAGE,
        overlay.OverlayCenterAxis.OFFICIAL_PROCEDURE_STAGE,
        overlay.OverlayCenterAxis.LEGAL_STATUS,
    )
    assert tuple(overlay.OverlayWarningKind) == (
        overlay.OverlayWarningKind.UNVERIFIED,
        overlay.OverlayWarningKind.CUSTOMER_DECISION_GATE,
        overlay.OverlayWarningKind.CONFLICT,
        overlay.OverlayWarningKind.REFERENCE_ONLY,
    )
    assert tuple(overlay.OverlayFeeRelatedFactKind) == (
        overlay.OverlayFeeRelatedFactKind.DRAFT,
        overlay.OverlayFeeRelatedFactKind.PAY_LIST,
        overlay.OverlayFeeRelatedFactKind.PAYMENT,
        overlay.OverlayFeeRelatedFactKind.OFFICIAL_EVIDENCE,
    )
    assert tuple(overlay.OverlayGateResolutionStatus) == (
        overlay.OverlayGateResolutionStatus.RESOLVED,
        overlay.OverlayGateResolutionStatus.UNRESOLVED,
    )
    for enum_cls in (
        overlay.OverlayCenterAxis,
        overlay.OverlayWarningKind,
        overlay.OverlayFeeRelatedFactKind,
        overlay.OverlayGateResolutionStatus,
    ):
        assert all(member.name == member.value for member in enum_cls)

    assert overlay.BusinessStage is BusinessStage
    assert overlay.OfficialProcedureStage is OfficialProcedureStage
    assert overlay.LegalStatus is LegalStatus
    assert overlay.ConfirmationStatus is ConfirmationStatus
    assert overlay.ActivityLane is ActivityLane
    assert overlay.EvidenceReference is EvidenceReference
    assert overlay.EvidenceVersionResult is EvidenceVersionResult
    assert overlay.EvidenceDerivationResult is EvidenceDerivationResult
    assert overlay.FeeDifferenceReviewState is FeeDifferenceReviewState
    assert overlay.FeeSourceStatus is FeeSourceStatus
    assert overlay.FeeDomain is FeeDomain
    assert overlay.FeeObligationStatuses is FeeObligationStatuses
    assert overlay.DecisionGateCode is DecisionGateCode

    contracts = {
        overlay.LifecycleOverlayQuery: {
            "after_sequence": int,
            "limit": int,
            "as_of_revision": int | None,
        },
        overlay.OverlayCenterSnapshot: {
            "business_stage": BusinessStage | None,
            "official_procedure_stage": OfficialProcedureStage | None,
            "legal_status": LegalStatus | None,
            "effective_at": datetime | None,
            "verification_status": ConfirmationStatus | None,
            "source_event_id": str | None,
        },
        overlay.OverlayCenterAxisChange: {
            "previous_value": BusinessStage | OfficialProcedureStage | LegalStatus | None,
            "current_value": BusinessStage | OfficialProcedureStage | LegalStatus | None,
        },
        overlay.OverlayDocumentEvidence: {
            "version": EvidenceVersionResult,
            "derivations": tuple[EvidenceDerivationResult, ...],
        },
        overlay.OverlayWorkPackageReceipt: {
            "receipt_id": str,
            "receipt_kind": str,
            "receipt_attachment_id": str | None,
            "receiving_case_no": str | None,
            "submitter": str | None,
            "received_at": datetime | None,
            "archive_status": str,
        },
        overlay.OverlayWorkPackage: {
            "package_id": str,
            "package_kind": str,
            "status": str,
            "source_document_id": str | None,
            "reply_document_id": str | None,
            "manifest_evidence_version_ids": tuple[str, ...],
            "receipts": tuple[overlay.OverlayWorkPackageReceipt, ...],
            "missing_gate_codes": tuple[str, ...],
        },
        overlay.OverlayTask: {
            "task_id": str,
            "document_id": str | None,
            "task_template_id": str | None,
            "title": str | None,
            "due_date": date | None,
            "internal_due_date": date | None,
            "status": str,
            "done_at": datetime | None,
        },
        overlay.OverlayFeeLine: {
            "line_id": str,
            "fee_code": str,
            "fee_name": str,
            "fee_year_key": int,
            "official_full_amount": str | None,
            "reduction_ratio": str,
            "payable_amount": str,
            "source_amount": str | None,
            "source_date": date | None,
            "difference_review_state": FeeDifferenceReviewState,
        },
        overlay.OverlayFeeRelatedFact: {
            "kind": overlay.OverlayFeeRelatedFactKind,
            "object_id": str,
            "status": str,
        },
        overlay.OverlayFeeObligation: {
            "obligation_id": str,
            "source_activity_id": str,
            "source_document_id": str | None,
            "source_status": FeeSourceStatus,
            "fee_domain": FeeDomain,
            "obligation_type": str,
            "due_date": date | None,
            "currency": str,
            "statuses": FeeObligationStatuses,
            "lines": tuple[overlay.OverlayFeeLine, ...],
            "related_facts": tuple[overlay.OverlayFeeRelatedFact, ...],
            "supersedes_obligation_id": str | None,
            "supersede_reason": str | None,
        },
        overlay.OverlayWarning: {
            "kind": overlay.OverlayWarningKind,
            "code": str,
            "message": str,
            "activity_id": str | None,
            "source_object_type": str | None,
            "source_object_id": str | None,
        },
        overlay.OverlayDecisionGate: {
            "gate_code": DecisionGateCode,
            "requested_scope_key": str,
            "resolution_status": overlay.OverlayGateResolutionStatus,
            "gate_id": str | None,
            "resolved_scope_key": str | None,
            "decision_value": str | None,
            "source_reference": str | None,
            "source_version": str | None,
            "confirmed_by": str | None,
            "effective_at": datetime | None,
            "unresolved_reason": str | None,
        },
        overlay.OverlayLegacyConflict: {
            "code": str,
            "activity_id": str | None,
            "message": str | None,
        },
        overlay.OverlayMilestone: {
            "sequence": int,
            "activity_id": str,
            "lane": ActivityLane,
            "activity_type": str,
            "source_activity_id": str | None,
            "effective_at": datetime,
            "confirmation_status": ConfirmationStatus,
            "center_changes": Mapping[overlay.OverlayCenterAxis, overlay.OverlayCenterAxisChange],
            "document_evidence": tuple[overlay.OverlayDocumentEvidence, ...],
            "work_packages": tuple[overlay.OverlayWorkPackage, ...],
            "tasks": tuple[overlay.OverlayTask, ...],
            "fee_obligations": tuple[overlay.OverlayFeeObligation, ...],
            "evidence_summary": tuple[EvidenceReference, ...],
            "warnings": tuple[overlay.OverlayWarning, ...],
        },
        overlay.LifecycleOverlay: {
            "case_id": str,
            "lifecycle_revision": int,
            "generated_at": datetime,
            "center_snapshot": overlay.OverlayCenterSnapshot,
            "milestones": tuple[overlay.OverlayMilestone, ...],
            "decision_gates": tuple[overlay.OverlayDecisionGate, ...],
            "warnings": tuple[overlay.OverlayWarning, ...],
            "legacy_conflicts": tuple[overlay.OverlayLegacyConflict, ...],
            "next_cursor": int | None,
            "has_more": bool,
        },
    }
    for cls, expected in contracts.items():
        _assert_value_contract(cls, expected)

    query = overlay.LifecycleOverlayQuery(after_sequence=0, limit=25, as_of_revision=None)
    with pytest.raises(FrozenInstanceError):
        query.limit = 50  # type: ignore[misc]


def _gate(
    gate_code: DecisionGateCode,
    requested_scope_key: str,
    *,
    resolved_scope_key: str | None = None,
    unresolved_reason: str | None = None,
) -> overlay.OverlayDecisionGate:
    resolved = unresolved_reason is None
    return overlay.OverlayDecisionGate(
        gate_code=gate_code,
        requested_scope_key=requested_scope_key,
        resolution_status=(
            overlay.OverlayGateResolutionStatus.RESOLVED
            if resolved
            else overlay.OverlayGateResolutionStatus.UNRESOLVED
        ),
        gate_id="gate-1" if resolved else None,
        resolved_scope_key=(resolved_scope_key or requested_scope_key) if resolved else None,
        decision_value="CONFIRMED" if resolved else None,
        source_reference="source" if resolved else None,
        source_version="v1" if resolved else None,
        confirmed_by="user-1" if resolved else None,
        effective_at=datetime(2026, 7, 15, 9, 0) if resolved else None,
        unresolved_reason=unresolved_reason,
    )


def test_overlay_preserves_money_gate_page_and_cursor_wire_invariants() -> None:
    fee_line = overlay.OverlayFeeLine(
        line_id="line-1",
        fee_code="FEE-1",
        fee_name="申请费",
        fee_year_key=0,
        official_full_amount="900.00",
        reduction_ratio="0.8500",
        payable_amount="135.00",
        source_amount="900.00",
        source_date=date(2026, 7, 15),
        difference_review_state=FeeDifferenceReviewState.MATCHED,
    )
    assert fee_line.official_full_amount == "900.00"
    assert fee_line.reduction_ratio == "0.8500"
    assert fee_line.payable_amount == "135.00"

    case_id = "case-1"
    non_legacy = tuple(DecisionGateCode)[:-1]
    gates = tuple(_gate(code, f"case:{case_id}") for code in non_legacy) + tuple(
        _gate(
            DecisionGateCode.LEGACY_FORM_CLASS,
            f"form-{number:03d}",
            resolved_scope_key="ALL-22" if number == 1 else None,
        )
        for number in range(1, 23)
    )
    assert len(gates) == 29
    assert len({gate.gate_code for gate in gates}) == 8
    assert len({(gate.gate_code, gate.requested_scope_key) for gate in gates}) == 29
    assert len({gate.gate_code: gate for gate in gates}) == 8
    assert gates[7].requested_scope_key == "form-001"
    assert gates[7].resolved_scope_key == "ALL-22"
    assert all(gate.requested_scope_key != "ALL-22" for gate in gates)

    reasons = (
        "DECISION_GATE_NOT_FOUND",
        "DECISION_GATE_REVOKED",
        "DECISION_GATE_NOT_EFFECTIVE",
        "DECISION_GATE_CANDIDATE_MULTIPLICITY",
        "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        "DECISION_GATE_CURRENT_ROW_CORRUPT",
        "DECISION_GATE_LEGACY_MAP_CORRUPT",
    )
    for reason in reasons:
        unresolved = _gate(
            DecisionGateCode.LEGACY_FORM_CLASS,
            "form-022",
            unresolved_reason=reason,
        )
        assert unresolved.unresolved_reason == reason
        assert (
            unresolved.gate_id,
            unresolved.resolved_scope_key,
            unresolved.decision_value,
            unresolved.source_reference,
            unresolved.source_version,
            unresolved.confirmed_by,
            unresolved.effective_at,
        ) == (None, None, None, None, None, None, None)

    generated_at = datetime(2026, 7, 15, 10, 0)
    result = overlay.LifecycleOverlay(
        case_id=case_id,
        lifecycle_revision=40,
        generated_at=generated_at,
        center_snapshot=overlay.OverlayCenterSnapshot(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=None,
            effective_at=None,
            verification_status=None,
            source_event_id=None,
        ),
        milestones=(),
        decision_gates=gates,
        warnings=(),
        legacy_conflicts=(),
        next_cursor=25,
        has_more=True,
    )
    assert result.generated_at is generated_at
    assert result.next_cursor == 25
    assert result.has_more is True
    assert "as_of" not in {field.name for field in fields(overlay.LifecycleOverlay)}
    assert (
        overlay.LifecycleOverlayQuery(after_sequence=25, limit=25, as_of_revision=40).as_of_revision
        == 40
    )
