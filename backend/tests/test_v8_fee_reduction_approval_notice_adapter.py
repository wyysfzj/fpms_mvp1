from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.documents import fee_linking_service
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.fee_reduction_approval_service import (
    RecordFeeReductionApprovalCommand,
)


def _template(*, catalog_status: str = "EXECUTABLE") -> SimpleNamespace:
    metadata: dict[str, object] = {
        "catalog_kind": "OFFICIAL_NOTICE",
        "catalog_status": catalog_status,
    }
    if catalog_status == "EXECUTABLE":
        metadata.update(
            {
                "execution_behavior": "FEE_REDUCTION_APPROVAL_NOTICE",
                "canonical_template_code": "FEE_REDUCTION_APPROVAL_NOTICE",
            }
        )
    return SimpleNamespace(
        code="OFFICIAL_NOTICE_031",
        input_fields=json.dumps(metadata),
        direction="IN",
        status_effect=None,
        deadline_template_code=None,
        fee_draft_type=None,
        status_restore=None,
        reply_to_template_code=None,
        need_reply=False,
    )


def _command() -> RecordFeeReductionApprovalCommand:
    return RecordFeeReductionApprovalCommand(
        case_id="case-fee-reduction-notice",
        scope_type=FeeReductionApprovalScopeType.CASE,
        applicant_ids=("applicant-fee-reduction",),
        eligibility_attributes_version="reviewed-notice-v1",
        eligibility_attributes_json=json.dumps(
            {"applicant-fee-reduction": {"kind": "个人"}},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        reduction_ratio=Decimal("0.85"),
        fee_codes=("CN_INV_APPLICATION_FEE", "CN_ANNUITY_FEE_INV"),
        fee_year_from=1,
        fee_year_to=10,
        effective_from=date(2026, 7, 1),
        effective_to=date(2036, 6, 30),
        source_evidence_version_id="evidence-fee-reduction-notice-v1",
        expected_source_content_hash="sha256:" + "a" * 64,
        confirmed_at=datetime(2026, 7, 12, 9, 30),
        confirmed_by="reviewer-fee-reduction-notice",
    )


def _adapter():
    adapter = getattr(
        fee_linking_service,
        "maybe_record_fee_reduction_approval_notice",
        None,
    )
    assert callable(adapter), (
        "missing frozen behavior: fee_linking_service.py must expose "
        "maybe_record_fee_reduction_approval_notice()"
    )
    return adapter


def test_executable_notice_delegates_exact_reviewed_approval_without_other_side_effects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    semantics = resolve_document_semantics(_template())
    assert semantics.catalog_status == "EXECUTABLE"
    assert semantics.execution_behavior == "FEE_REDUCTION_APPROVAL_NOTICE"
    assert semantics.case_status_effect is None
    assert semantics.task_template_code is None
    assert semantics.requires_reply is False
    assert semantics.completion_event is None
    assert semantics.archive_status_restore is None
    assert semantics.deadline_source_policy is None
    assert semantics.fee_trigger is None

    command = _command()
    transaction = object()
    created = object()
    reused = object()
    calls: list[tuple[RecordFeeReductionApprovalCommand, object]] = []

    def record_spy(
        received_command: RecordFeeReductionApprovalCommand,
        received_transaction: object,
    ) -> object:
        calls.append((received_command, received_transaction))
        return created if len(calls) == 1 else reused

    def forbidden_side_effect(*_args: object, **_kwargs: object) -> None:
        raise AssertionError(
            "fee-reduction approval notice must not create an obligation, draft, "
            "task, reply, activity, or lifecycle change"
        )

    monkeypatch.setattr(
        fee_linking_service,
        "record_fee_reduction_approval",
        record_spy,
        raising=False,
    )
    for side_effect_name in (
        "recognize_obligation",
        "maybe_create_fee_draft",
        "append_case_activity",
        "create_task",
        "create_reply",
        "update_document_status",
        "apply_lifecycle_event",
    ):
        monkeypatch.setattr(
            fee_linking_service,
            side_effect_name,
            forbidden_side_effect,
            raising=False,
        )

    result = _adapter()(
        transaction=transaction,
        template=_template(),
        command=command,
    )
    replay = _adapter()(
        transaction=transaction,
        template=_template(),
        command=command,
    )

    assert result is created
    assert replay is reused
    assert calls == [(command, transaction), (command, transaction)]


@pytest.mark.parametrize(
    "template",
    (
        _template(catalog_status="REFERENCE_ONLY"),
        SimpleNamespace(code="UNKNOWN_NOTICE", input_fields=None),
        None,
    ),
    ids=("reference-only", "unknown", "missing"),
)
def test_reference_only_unknown_and_missing_notices_do_nothing(
    monkeypatch: pytest.MonkeyPatch,
    template: object | None,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(
        fee_linking_service,
        "record_fee_reduction_approval",
        lambda *_args, **_kwargs: calls.append(object()),
        raising=False,
    )

    result = _adapter()(
        transaction=object(),
        template=template,
        command=_command(),
    )

    assert result is None
    assert calls == []
