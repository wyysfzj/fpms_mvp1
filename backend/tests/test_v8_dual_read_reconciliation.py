from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime
from types import ModuleType
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from scripts.backfill_v8_document_evidence import (
    LegacyDocumentEvidenceImportResult,
    LegacyDocumentEvidenceImportRowResult,
)
from scripts.backfill_v8_fee_reduction import (
    LegacyFeeReductionImportResult,
    LegacyFeeReductionImportRowResult,
    LegacyFeeReductionMigrationManifest,
    LegacyFeeReductionMigrationRow,
)
from scripts.backfill_v8_fee_truth import (
    LegacyFeeTruthLinkResult,
    LegacyFeeTruthLinkRowResult,
    LegacyFeeTruthMigrationRow,
)
from scripts.backfill_v8_lifecycle import (
    LegacyLifecycleImportResult,
    LegacyLifecycleImportRowResult,
)

RECORDED_AT = datetime(2026, 8, 9, 18, 0)
HASHES = ("1" * 64, "2" * 64, "3" * 64)


def _api() -> ModuleType:
    try:
        return importlib.import_module("scripts.audit_v8_dual_read")
    except ModuleNotFoundError:
        pytest.fail("dual-read reconciliation public seam is missing")


def _manifest() -> LegacyFeeReductionMigrationManifest:
    return LegacyFeeReductionMigrationManifest(
        version="v1",
        manifest_hash="a" * 64,
        approval_status="APPROVED",
        confirmed_by="actor-1",
        confirmed_at=RECORDED_AT,
        rows=(
            LegacyFeeReductionMigrationRow(
                case_id="case-reduction-source",
                legacy_value="0",
                source_reference="source",
                source_version="v1",
                source_snapshot_hash="b" * 64,
                approval_id=None,
            ),
        ),
    )


def _fee_truth_rows() -> tuple[LegacyFeeTruthMigrationRow, ...]:
    return (
        LegacyFeeTruthMigrationRow(
            case_id="case-fee-source",
            source_activity_id="activity-fee-source",
            fee_code="APPLICATION_FEE",
            fee_year_key=0,
            fee_item_id="item-fee-source",
            gov_payment_id=None,
        ),
    )


def _lifecycle_result(
    classifications: tuple[str, ...],
) -> LegacyLifecycleImportResult:
    rows = tuple(
        LegacyLifecycleImportRowResult(
            case_id=f"case-lifecycle-{index}",
            legacy_status="GRANTED",
            classification=classification,
            planned_write=classification == "IMPORT",
            activity_id=(f"activity-lifecycle-{index}" if classification == "UNCHANGED" else None),
        )
        for index, classification in enumerate(classifications)
    )
    return LegacyLifecycleImportResult(
        scanned=len(rows),
        imported=classifications.count("IMPORT"),
        unchanged=classifications.count("UNCHANGED"),
        conflicts=classifications.count("CONFLICT"),
        invalid=classifications.count("INVALID"),
        planned_writes=classifications.count("IMPORT"),
        input_sha256=HASHES[0],
        plan_sha256=HASHES[1],
        output_sha256=HASHES[2],
        rows=rows,
    )


def _document_result(
    classifications: tuple[str, ...],
) -> LegacyDocumentEvidenceImportResult:
    rows = tuple(
        LegacyDocumentEvidenceImportRowResult(
            attachment_id=f"attachment-{index}",
            classification=classification,
            planned_write=classification == "IMPORT",
        )
        for index, classification in enumerate(classifications)
    )
    return LegacyDocumentEvidenceImportResult(
        scanned=len(rows),
        imported=classifications.count("IMPORT"),
        unchanged=classifications.count("UNCHANGED"),
        invalid=classifications.count("INVALID"),
        role_conflicts=classifications.count("ROLE_CONFLICT"),
        current_conflicts=classifications.count("CURRENT_CONFLICT"),
        planned_writes=classifications.count("IMPORT"),
        input_sha256=HASHES[0],
        plan_sha256=HASHES[1],
        output_sha256=HASHES[2],
        rows=rows,
    )


def _reduction_result(
    classifications: tuple[str, ...],
) -> LegacyFeeReductionImportResult:
    required = {"explicit-zero", "reused-70", "reused-85"}
    rows = tuple(
        LegacyFeeReductionImportRowResult(
            case_id=f"case-reduction-{index}",
            legacy_value="0",
            classification=classification,
            approval_id=None,
            will_update_case=classification in required,
            will_create_provenance=classification in required,
        )
        for index, classification in enumerate(classifications)
    )
    return LegacyFeeReductionImportResult(
        rows=rows,
        counts={"scanned": len(rows)},
        input_sha256=HASHES[0],
        plan_sha256=HASHES[1],
        output_sha256=HASHES[2],
    )


def _fee_truth_result(
    classifications: tuple[str, ...],
) -> LegacyFeeTruthLinkResult:
    rows = tuple(
        LegacyFeeTruthLinkRowResult(
            fee_item_id=f"fee-item-{index}",
            gov_payment_id=index + 1,
            obligation_line_id=f"line-{index}",
            classification=classification,
            planned_writes=int(classification == "LINKED"),
        )
        for index, classification in enumerate(classifications)
    )
    return LegacyFeeTruthLinkResult(
        scanned=len(rows),
        linked=classifications.count("LINKED"),
        unchanged=classifications.count("UNCHANGED"),
        invalid=classifications.count("INVALID"),
        unmatched=classifications.count("UNMATCHED"),
        ambiguous=classifications.count("AMBIGUOUS"),
        planned_writes=classifications.count("LINKED"),
        input_sha256=HASHES[0],
        plan_sha256=HASHES[1],
        output_sha256=HASHES[2],
        rows=rows,
    )


def _install_results(
    monkeypatch: pytest.MonkeyPatch,
    api: ModuleType,
    *,
    lifecycle: LegacyLifecycleImportResult,
    document: LegacyDocumentEvidenceImportResult,
    reduction: LegacyFeeReductionImportResult,
    fee_truth: LegacyFeeTruthLinkResult,
) -> tuple[Mock, Mock, Mock, Mock]:
    calls = tuple(
        Mock(return_value=result) for result in (lifecycle, document, reduction, fee_truth)
    )
    for name, call in zip(
        (
            "import_legacy_lifecycle",
            "import_legacy_document_evidence",
            "import_legacy_fee_reductions",
            "link_legacy_fee_truth",
        ),
        calls,
        strict=True,
    ):
        monkeypatch.setattr(api, name, call)
    return calls


def _run(api: ModuleType, transaction: Session):
    return api.audit_v8_dual_read(
        transaction=transaction,
        actor_id="actor-1",
        lifecycle_recorded_at=RECORDED_AT,
        fee_reduction_manifest=_manifest(),
        fee_truth_rows=_fee_truth_rows(),
    )


def test_public_contract_is_frozen_keyword_only_and_synchronous() -> None:
    api = _api()
    signature = inspect.signature(api.audit_v8_dual_read)
    assert tuple(signature.parameters) == (
        "transaction",
        "actor_id",
        "lifecycle_recorded_at",
        "fee_reduction_manifest",
        "fee_truth_rows",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert not inspect.iscoroutinefunction(api.audit_v8_dual_read)
    assert api.__all__ == (
        "DualReadChildHashes",
        "DualReadReconciliationRow",
        "DualReadReconciliationReport",
        "audit_v8_dual_read",
    )
    expected = {
        api.DualReadChildHashes: (
            "lane",
            "input_sha256",
            "plan_sha256",
            "output_sha256",
        ),
        api.DualReadReconciliationRow: (
            "lane",
            "identity",
            "source_classification",
            "disposition",
        ),
        api.DualReadReconciliationReport: (
            "scanned",
            "reconciled",
            "classified_conflicts",
            "requires_import",
            "accepted",
            "child_hashes",
            "report_sha256",
            "rows",
        ),
    }
    for result_type, names in expected.items():
        assert is_dataclass(result_type)
        assert tuple(field.name for field in fields(result_type)) == names
        assert result_type.__slots__ == names
        assert all(field.kw_only for field in fields(result_type))
    row = api.DualReadReconciliationRow(
        lane="LIFECYCLE",
        identity="case-1",
        source_classification="UNCHANGED",
        disposition="RECONCILED",
    )
    with pytest.raises(FrozenInstanceError):
        row.disposition = "CLASSIFIED_CONFLICT"


def test_report_maps_every_frozen_classification_and_delegates_dry_runs(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    calls = _install_results(
        monkeypatch,
        api,
        lifecycle=_lifecycle_result(("UNCHANGED", "CONFLICT", "INVALID", "IMPORT")),
        document=_document_result(
            ("UNCHANGED", "INVALID", "ROLE_CONFLICT", "CURRENT_CONFLICT", "IMPORT")
        ),
        reduction=_reduction_result(
            (
                "unchanged",
                "invalid",
                "missing-approval",
                "ambiguous-approval",
                "explicit-zero",
                "reused-70",
                "reused-85",
            )
        ),
        fee_truth=_fee_truth_result(("UNCHANGED", "INVALID", "UNMATCHED", "AMBIGUOUS", "LINKED")),
    )
    with session_factory() as transaction:
        before = (tuple(transaction.new), tuple(transaction.dirty), tuple(transaction.deleted))
        first = _run(api, transaction)
        second = _run(api, transaction)
        after = (tuple(transaction.new), tuple(transaction.dirty), tuple(transaction.deleted))

    assert first == second
    assert (first.scanned, first.reconciled, first.classified_conflicts, first.requires_import) == (
        21,
        4,
        11,
        6,
    )
    assert first.accepted is False
    assert len(first.child_hashes) == 4
    assert len(first.report_sha256) == 64
    assert before == after == ((), (), ())
    for call in calls:
        assert call.call_count == 2
        assert all(invocation.kwargs["dry_run"] is True for invocation in call.call_args_list)
        assert all(
            invocation.kwargs.get("expected_plan_sha256") is None
            for invocation in call.call_args_list
        )


def test_only_reconciled_and_classified_conflicts_are_accepted(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    _install_results(
        monkeypatch,
        api,
        lifecycle=_lifecycle_result(("UNCHANGED", "CONFLICT")),
        document=_document_result(("UNCHANGED", "ROLE_CONFLICT")),
        reduction=_reduction_result(("unchanged", "missing-approval")),
        fee_truth=_fee_truth_result(("UNCHANGED", "UNMATCHED")),
    )
    with session_factory() as transaction:
        report = _run(api, transaction)

    assert report.accepted is True
    assert (report.reconciled, report.classified_conflicts, report.requires_import) == (4, 4, 0)
    assert [row.disposition for row in report.rows] == [
        "RECONCILED",
        "CLASSIFIED_CONFLICT",
        "RECONCILED",
        "CLASSIFIED_CONFLICT",
        "RECONCILED",
        "CLASSIFIED_CONFLICT",
        "RECONCILED",
        "CLASSIFIED_CONFLICT",
    ]


def test_unknown_child_classification_fails_closed(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    _install_results(
        monkeypatch,
        api,
        lifecycle=_lifecycle_result(("SURPRISE",)),
        document=_document_result(("UNCHANGED",)),
        reduction=_reduction_result(("unchanged",)),
        fee_truth=_fee_truth_result(("UNCHANGED",)),
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as captured:
        _run(api, transaction)

    assert captured.value.code == "V8_DUAL_READ_UNCLASSIFIED_RESULT"
    assert captured.value.status_code == 409


def test_invalid_public_input_fails_before_delegation(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api = _api()
    calls = _install_results(
        monkeypatch,
        api,
        lifecycle=_lifecycle_result(()),
        document=_document_result(()),
        reduction=_reduction_result(()),
        fee_truth=_fee_truth_result(()),
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as captured:
        api.audit_v8_dual_read(
            transaction=transaction,
            actor_id=" actor-1",
            lifecycle_recorded_at=RECORDED_AT,
            fee_reduction_manifest=_manifest(),
            fee_truth_rows=_fee_truth_rows(),
        )

    assert captured.value.code == "V8_DUAL_READ_INPUT_INVALID"
    assert captured.value.status_code == 409
    assert all(call.call_count == 0 for call in calls)
