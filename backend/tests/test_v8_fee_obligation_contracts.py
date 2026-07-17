from __future__ import annotations

import ast
import inspect
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import get_type_hints

import pytest

import app.modules.fees.obligation_contracts as contracts
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeDraftItemLinkResult,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationLine,
    FeeObligationLineInput,
    FeeObligationSource,
    FeeObligationStatus,
    FeeObligationStatuses,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentEvidenceLinkResult,
    FeePaymentStatus,
    FeeSourceStatus,
    PrepareFeeObligationDraftCommand,
    PrepareFeeObligationDraftResult,
    PreviewFeeEstimateCommand,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
    RecordFeeObligationInstructionCommand,
    RecordFeeObligationInstructionResult,
    RecordFeePaymentEvidenceCommand,
    RecordFeePaymentEvidenceResult,
)

EXPECTED_EXPORTS = (
    "FeeDomain",
    "FeeEstimateStatus",
    "FeeObligationStatus",
    "FeeClientInstructionStatus",
    "FeeObligationDraftStatus",
    "FeePayListStatus",
    "FeePaymentStatus",
    "FeeOfficialEvidenceStatus",
    "FeeClientInstruction",
    "FeeSourceStatus",
    "FeeDifferenceReviewState",
    "FeeEstimateContext",
    "FeeEstimateSource",
    "FeeObligationSource",
    "FeeObligationStatuses",
    "FeeObligationLineInput",
    "FeeObligationLine",
    "FeeEstimateCandidate",
    "FeeEstimate",
    "FeeObligation",
    "FeeDraftItemLinkResult",
    "FeePaymentEvidenceLinkResult",
    "PreviewFeeEstimateCommand",
    "RecognizeFeeObligationCommand",
    "RecognizeFeeObligationResult",
    "RecordFeeObligationInstructionCommand",
    "RecordFeeObligationInstructionResult",
    "PrepareFeeObligationDraftCommand",
    "PrepareFeeObligationDraftResult",
    "RecordFeePaymentEvidenceCommand",
    "RecordFeePaymentEvidenceResult",
)

EXPECTED_ENUM_VALUES = {
    FeeDomain: ("GOV", "SERVICE"),
    FeeEstimateStatus: ("ESTIMATE",),
    FeeObligationStatus: ("RECOGNIZED", "SUPERSEDED"),
    FeeClientInstructionStatus: ("PENDING", "PAY", "HOLD", "ABANDON"),
    FeeObligationDraftStatus: ("NOT_CREATED", "CREATED"),
    FeePayListStatus: ("NOT_CREATED", "CREATED"),
    FeePaymentStatus: ("UNPAID", "PAID"),
    FeeOfficialEvidenceStatus: ("PENDING", "VERIFIED", "NOT_APPLICABLE"),
    FeeClientInstruction: ("PAY", "HOLD", "ABANDON"),
    FeeSourceStatus: ("VERIFIED", "REVIEW_REQUIRED", "LEGACY_UNVERIFIED"),
    FeeDifferenceReviewState: ("MATCHED", "SOURCE_PENDING", "REVIEW_REQUIRED"),
}

EXPECTED_FIELDS = {
    FeeEstimateContext: (
        ("trigger", str),
        ("source_document_id", str | None),
    ),
    FeeEstimateSource: (
        ("rate_id", str | None),
        ("source_document_id", str | None),
        ("source_doc", str | None),
        ("source_url", str | None),
        ("source_policy", str | None),
        ("source_version", str | None),
        ("status", FeeSourceStatus),
    ),
    FeeObligationSource: (
        ("source_activity_id", str),
        ("source_document_id", str | None),
        ("status", FeeSourceStatus),
    ),
    FeeObligationStatuses: (
        ("estimate_status", FeeEstimateStatus | None),
        ("obligation_status", FeeObligationStatus),
        ("client_instruction_status", FeeClientInstructionStatus),
        ("draft_status", FeeObligationDraftStatus),
        ("pay_list_status", FeePayListStatus),
        ("payment_status", FeePaymentStatus),
        ("official_evidence_status", FeeOfficialEvidenceStatus),
    ),
    FeeObligationLineInput: (
        ("fee_code", str),
        ("fee_name", str),
        ("fee_year_key", int),
        ("official_full_amount", Decimal | None),
        ("reduction_ratio", Decimal),
        ("payable_amount", Decimal),
        ("source_amount", Decimal | None),
        ("source_date", date | None),
        ("difference_review_state", FeeDifferenceReviewState),
    ),
    FeeObligationLine: (
        ("id", str),
        ("obligation_id", str),
        ("case_id", str),
        ("source_activity_id", str),
        ("fee_code", str),
        ("fee_name", str),
        ("fee_year_key", int),
        ("official_full_amount", Decimal | None),
        ("reduction_ratio", Decimal),
        ("payable_amount", Decimal),
        ("source_amount", Decimal | None),
        ("source_date", date | None),
        ("difference_review_state", FeeDifferenceReviewState),
        ("current_identity_key", str | None),
    ),
    FeeEstimateCandidate: (
        ("line", FeeObligationLineInput),
        ("source", FeeEstimateSource),
    ),
    FeeEstimate: (
        ("case_id", str),
        ("estimate_status", FeeEstimateStatus),
        ("trigger_context", FeeEstimateContext),
        ("currency", str),
        ("candidates", tuple[FeeEstimateCandidate, ...]),
        ("total_payable_amount", Decimal),
    ),
    FeeObligation: (
        ("id", str),
        ("case_id", str),
        ("source", FeeObligationSource),
        ("fee_domain", FeeDomain),
        ("obligation_type", str),
        ("due_date", date | None),
        ("currency", str),
        ("statuses", FeeObligationStatuses),
        ("lines", tuple[FeeObligationLine, ...]),
        ("supersedes_obligation_id", str | None),
        ("supersede_reason", str | None),
    ),
    FeeDraftItemLinkResult: (
        ("id", str),
        ("obligation_line_id", str),
        ("fee_item_id", str),
        ("reused", bool),
    ),
    FeePaymentEvidenceLinkResult: (
        ("id", str),
        ("obligation_line_id", str),
        ("gov_payment_id", int),
        ("reused", bool),
    ),
    PreviewFeeEstimateCommand: (
        ("case_id", str),
        ("trigger_context", FeeEstimateContext),
        ("currency", str),
    ),
    RecognizeFeeObligationCommand: (
        ("case_id", str),
        ("source_activity_id", str),
        ("source_document_id", str | None),
        ("fee_domain", FeeDomain),
        ("obligation_type", str),
        ("due_date", date | None),
        ("currency", str),
        ("source_status", FeeSourceStatus),
        ("lines", tuple[FeeObligationLineInput, ...]),
        ("actor_id", str),
        ("idempotency_key", str),
        ("supersedes_obligation_id", str | None),
        ("supersede_reason", str | None),
    ),
    RecognizeFeeObligationResult: (
        ("obligation", FeeObligation),
        ("activity_id", str),
        ("idempotency_key", str),
        ("reused", bool),
        ("superseded_obligation_id", str | None),
    ),
    RecordFeeObligationInstructionCommand: (
        ("obligation_id", str),
        ("instruction", FeeClientInstruction),
        ("actor_id", str),
        ("idempotency_key", str),
    ),
    RecordFeeObligationInstructionResult: (
        ("obligation", FeeObligation),
        ("activity_id", str),
        ("idempotency_key", str),
        ("reused", bool),
    ),
    PrepareFeeObligationDraftCommand: (
        ("obligation_id", str),
        ("actor_id", str),
        ("idempotency_key", str),
    ),
    PrepareFeeObligationDraftResult: (
        ("obligation_id", str),
        ("draft_id", str),
        ("links", tuple[FeeDraftItemLinkResult, ...]),
        ("activity_id", str),
        ("activity_reused", bool),
        ("idempotency_key", str),
    ),
    RecordFeePaymentEvidenceCommand: (
        ("obligation_id", str),
        ("obligation_line_ids", tuple[str, ...]),
        ("gov_payment_id", int),
        ("actor_id", str),
    ),
    RecordFeePaymentEvidenceResult: (
        ("obligation", FeeObligation),
        ("links", tuple[FeePaymentEvidenceLinkResult, ...]),
    ),
}


def test_exports_and_enum_vocabularies_are_exact() -> None:
    assert contracts.__all__ == EXPECTED_EXPORTS

    for enum_type, expected_values in EXPECTED_ENUM_VALUES.items():
        assert issubclass(enum_type, str)
        assert issubclass(enum_type, Enum)
        assert tuple(member.name for member in enum_type) == expected_values
        assert tuple(member.value for member in enum_type) == expected_values


def test_value_command_and_result_shapes_are_exact_frozen_slots() -> None:
    for contract_type, expected_fields in EXPECTED_FIELDS.items():
        assert is_dataclass(contract_type)
        assert contract_type.__dataclass_params__.frozen is True
        assert tuple(field.name for field in fields(contract_type)) == tuple(
            field_name for field_name, _annotation in expected_fields
        )
        assert get_type_hints(contract_type) == dict(expected_fields)
        assert all(field.default is MISSING for field in fields(contract_type))
        assert all(field.default_factory is MISSING for field in fields(contract_type))
        assert "__slots__" in contract_type.__dict__


def test_contract_values_preserve_independent_facts_and_source_activity_identity() -> None:
    case_id = "00000000-0000-4000-8000-000000000001"
    source_activity_id = "00000000-0000-4000-8000-000000000002"
    recognition_activity_id = "00000000-0000-4000-8000-000000000003"
    obligation_id = "00000000-0000-4000-8000-000000000004"
    line_id = "00000000-0000-4000-8000-000000000005"
    document_id = "00000000-0000-4000-8000-000000000006"
    actor_id = "00000000-0000-4000-8000-000000000007"
    fee_item_id = "00000000-0000-4000-8000-000000000008"
    draft_id = "00000000-0000-4000-8000-000000000009"

    context = FeeEstimateContext(trigger="APPLICATION_FEE_NOTICE", source_document_id=document_id)
    estimate_source = FeeEstimateSource(
        rate_id="00000000-0000-4000-8000-000000000010",
        source_document_id=document_id,
        source_doc="CNIPA fee schedule",
        source_url=None,
        source_policy="CURRENT_OFFICIAL",
        source_version="2026-03-30",
        status=FeeSourceStatus.VERIFIED,
    )
    line_input = FeeObligationLineInput(
        fee_code="APPLICATION_FEE",
        fee_name="Application fee",
        fee_year_key=0,
        official_full_amount=Decimal("100.00"),
        reduction_ratio=Decimal("0"),
        payable_amount=Decimal("100.00"),
        source_amount=Decimal("100.00"),
        source_date=date(2026, 7, 13),
        difference_review_state=FeeDifferenceReviewState.MATCHED,
    )
    candidate = FeeEstimateCandidate(line=line_input, source=estimate_source)
    preview_command = PreviewFeeEstimateCommand(
        case_id=case_id,
        trigger_context=context,
        currency="CNY",
    )
    estimate = FeeEstimate(
        case_id=case_id,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=context,
        currency="CNY",
        candidates=(candidate,),
        total_payable_amount=Decimal("100.00"),
    )
    statuses = FeeObligationStatuses(
        estimate_status=None,
        obligation_status=FeeObligationStatus.RECOGNIZED,
        client_instruction_status=FeeClientInstructionStatus.PENDING,
        draft_status=FeeObligationDraftStatus.NOT_CREATED,
        pay_list_status=FeePayListStatus.NOT_CREATED,
        payment_status=FeePaymentStatus.UNPAID,
        official_evidence_status=FeeOfficialEvidenceStatus.PENDING,
    )
    obligation_source = FeeObligationSource(
        source_activity_id=source_activity_id,
        source_document_id=document_id,
        status=FeeSourceStatus.VERIFIED,
    )
    line = FeeObligationLine(
        id=line_id,
        obligation_id=obligation_id,
        case_id=case_id,
        source_activity_id=source_activity_id,
        fee_code=line_input.fee_code,
        fee_name=line_input.fee_name,
        fee_year_key=line_input.fee_year_key,
        official_full_amount=line_input.official_full_amount,
        reduction_ratio=line_input.reduction_ratio,
        payable_amount=line_input.payable_amount,
        source_amount=line_input.source_amount,
        source_date=line_input.source_date,
        difference_review_state=line_input.difference_review_state,
        current_identity_key="a" * 64,
    )
    obligation = FeeObligation(
        id=obligation_id,
        case_id=case_id,
        source=obligation_source,
        fee_domain=FeeDomain.GOV,
        obligation_type="APPLICATION",
        due_date=date(2026, 8, 13),
        currency="CNY",
        statuses=statuses,
        lines=(line,),
        supersedes_obligation_id=None,
        supersede_reason=None,
    )
    recognize_command = RecognizeFeeObligationCommand(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_document_id=document_id,
        fee_domain=FeeDomain.GOV,
        obligation_type="APPLICATION",
        due_date=date(2026, 8, 13),
        currency="CNY",
        source_status=FeeSourceStatus.VERIFIED,
        lines=(line_input,),
        actor_id=actor_id,
        idempotency_key="recognize-application-fee",
        supersedes_obligation_id=None,
        supersede_reason=None,
    )
    recognize_result = RecognizeFeeObligationResult(
        obligation=obligation,
        activity_id=recognition_activity_id,
        idempotency_key=recognize_command.idempotency_key,
        reused=False,
        superseded_obligation_id=None,
    )
    instruction_command = RecordFeeObligationInstructionCommand(
        obligation_id=obligation_id,
        instruction=FeeClientInstruction.PAY,
        actor_id=actor_id,
        idempotency_key="instruction-pay",
    )
    instruction_result = RecordFeeObligationInstructionResult(
        obligation=obligation,
        activity_id="00000000-0000-4000-8000-000000000011",
        idempotency_key=instruction_command.idempotency_key,
        reused=False,
    )
    draft_link = FeeDraftItemLinkResult(
        id="00000000-0000-4000-8000-000000000012",
        obligation_line_id=line_id,
        fee_item_id=fee_item_id,
        reused=False,
    )
    draft_command = PrepareFeeObligationDraftCommand(
        obligation_id=obligation_id,
        actor_id=actor_id,
        idempotency_key="prepare-draft",
    )
    draft_result = PrepareFeeObligationDraftResult(
        obligation_id=obligation_id,
        draft_id=draft_id,
        links=(draft_link,),
        activity_id="00000000-0000-4000-8000-000000000013",
        activity_reused=False,
        idempotency_key=draft_command.idempotency_key,
    )
    payment_link = FeePaymentEvidenceLinkResult(
        id="00000000-0000-4000-8000-000000000014",
        obligation_line_id=line_id,
        gov_payment_id=7,
        reused=False,
    )
    payment_command = RecordFeePaymentEvidenceCommand(
        obligation_id=obligation_id,
        obligation_line_ids=(line_id,),
        gov_payment_id=7,
        actor_id=actor_id,
    )
    payment_result = RecordFeePaymentEvidenceResult(
        obligation=obligation,
        links=(payment_link,),
    )

    assert preview_command.trigger_context is estimate.trigger_context
    assert not hasattr(estimate, "obligation_id")
    assert recognize_command.source_activity_id == obligation.source.source_activity_id
    assert recognize_command.source_activity_id == obligation.lines[0].source_activity_id
    assert recognize_result.activity_id != recognize_command.source_activity_id
    assert recognize_result.activity_id == recognition_activity_id
    assert (
        instruction_result.obligation.statuses.draft_status is FeeObligationDraftStatus.NOT_CREATED
    )
    assert draft_result.links == (draft_link,)
    assert payment_command.obligation_line_ids == (line_id,)
    assert payment_result.links == (payment_link,)
    assert (
        payment_result.obligation.statuses.official_evidence_status
        is FeeOfficialEvidenceStatus.PENDING
    )
    assert all(
        not hasattr(value, "__dict__")
        for value in (
            context,
            estimate_source,
            line_input,
            candidate,
            estimate,
            statuses,
            obligation_source,
            line,
            obligation,
            preview_command,
            recognize_command,
            recognize_result,
            instruction_command,
            instruction_result,
            draft_link,
            draft_command,
            draft_result,
            payment_link,
            payment_command,
            payment_result,
        )
    )

    with pytest.raises(FrozenInstanceError):
        context.trigger = "CHANGED"  # type: ignore[misc]


def test_module_is_a_standard_library_only_value_contract() -> None:
    tree = ast.parse(inspect.getsource(contracts))
    allowed_import_roots = {"__future__", "dataclasses", "datetime", "decimal", "enum"}
    imported_roots = {
        alias.name.split(".", maxsplit=1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        (node.module or "").split(".", maxsplit=1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )

    assert imported_roots <= allowed_import_roots
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree)
    )
