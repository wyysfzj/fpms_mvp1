from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from scripts.backfill_v8_document_evidence import (
    LegacyDocumentEvidenceImportResult,
    import_legacy_document_evidence,
)
from scripts.backfill_v8_fee_reduction import (
    LegacyFeeReductionImportResult,
    LegacyFeeReductionMigrationManifest,
    import_legacy_fee_reductions,
)
from scripts.backfill_v8_fee_truth import (
    LegacyFeeTruthLinkResult,
    LegacyFeeTruthMigrationRow,
    link_legacy_fee_truth,
)
from scripts.backfill_v8_lifecycle import (
    LegacyLifecycleImportResult,
    import_legacy_lifecycle,
)

__all__ = (
    "DualReadChildHashes",
    "DualReadReconciliationRow",
    "DualReadReconciliationReport",
    "audit_v8_dual_read",
)

_RECONCILED = "RECONCILED"
_CLASSIFIED_CONFLICT = "CLASSIFIED_CONFLICT"
_REQUIRES_IMPORT = "REQUIRES_IMPORT"
_DISPOSITIONS = {
    "LIFECYCLE": {
        "UNCHANGED": _RECONCILED,
        "CONFLICT": _CLASSIFIED_CONFLICT,
        "INVALID": _CLASSIFIED_CONFLICT,
        "IMPORT": _REQUIRES_IMPORT,
    },
    "DOCUMENT_EVIDENCE": {
        "UNCHANGED": _RECONCILED,
        "INVALID": _CLASSIFIED_CONFLICT,
        "ROLE_CONFLICT": _CLASSIFIED_CONFLICT,
        "CURRENT_CONFLICT": _CLASSIFIED_CONFLICT,
        "IMPORT": _REQUIRES_IMPORT,
    },
    "FEE_REDUCTION": {
        "unchanged": _RECONCILED,
        "invalid": _CLASSIFIED_CONFLICT,
        "missing-approval": _CLASSIFIED_CONFLICT,
        "ambiguous-approval": _CLASSIFIED_CONFLICT,
        "explicit-zero": _REQUIRES_IMPORT,
        "reused-70": _REQUIRES_IMPORT,
        "reused-85": _REQUIRES_IMPORT,
    },
    "FEE_TRUTH": {
        "UNCHANGED": _RECONCILED,
        "INVALID": _CLASSIFIED_CONFLICT,
        "UNMATCHED": _CLASSIFIED_CONFLICT,
        "AMBIGUOUS": _CLASSIFIED_CONFLICT,
        "LINKED": _REQUIRES_IMPORT,
    },
}


@dataclass(frozen=True, slots=True, kw_only=True)
class DualReadChildHashes:
    lane: str
    input_sha256: str
    plan_sha256: str
    output_sha256: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DualReadReconciliationRow:
    lane: str
    identity: str
    source_classification: str
    disposition: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DualReadReconciliationReport:
    scanned: int
    reconciled: int
    classified_conflicts: int
    requires_import: int
    accepted: bool
    child_hashes: tuple[DualReadChildHashes, ...]
    report_sha256: str
    rows: tuple[DualReadReconciliationRow, ...]


def _conflict(code: str, *, field: str | None = None) -> None:
    raise_business_error(
        code,
        "V8 双读对账结果无效",
        details=None if field is None else {"field": field},
        status_code=409,
    )


def _exact_text(value: object, *, limit: int) -> bool:
    return bool(
        type(value) is str
        and value
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _is_hash(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_input(
    *,
    transaction: Session,
    actor_id: str,
    lifecycle_recorded_at: datetime,
    fee_reduction_manifest: LegacyFeeReductionMigrationManifest,
    fee_truth_rows: tuple[LegacyFeeTruthMigrationRow, ...],
) -> None:
    valid = bool(
        isinstance(transaction, Session)
        and _exact_text(actor_id, limit=36)
        and type(lifecycle_recorded_at) is datetime
        and lifecycle_recorded_at.tzinfo is None
        and type(fee_reduction_manifest) is LegacyFeeReductionMigrationManifest
        and type(fee_truth_rows) is tuple
        and fee_truth_rows
        and all(type(row) is LegacyFeeTruthMigrationRow for row in fee_truth_rows)
    )
    if not valid:
        _conflict("V8_DUAL_READ_INPUT_INVALID")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict("V8_DUAL_READ_INPUT_INVALID", field="transaction")


def _child_hashes(
    lane: str,
    result: object,
    expected_type: type,
) -> DualReadChildHashes:
    if type(result) is not expected_type:
        _conflict("V8_DUAL_READ_UNCLASSIFIED_RESULT", field=lane)
    hashes = (
        result.input_sha256,
        result.plan_sha256,
        result.output_sha256,
    )
    if any(not _is_hash(value) for value in hashes):
        _conflict("V8_DUAL_READ_UNCLASSIFIED_RESULT", field=lane)
    return DualReadChildHashes(
        lane=lane,
        input_sha256=hashes[0],
        plan_sha256=hashes[1],
        output_sha256=hashes[2],
    )


def _row(
    *,
    lane: str,
    identity: object,
    classification: object,
) -> DualReadReconciliationRow:
    if not _exact_text(identity, limit=128) or not _exact_text(classification, limit=64):
        _conflict("V8_DUAL_READ_UNCLASSIFIED_RESULT", field=lane)
    disposition = _DISPOSITIONS[lane].get(classification)
    if disposition is None:
        _conflict("V8_DUAL_READ_UNCLASSIFIED_RESULT", field=lane)
    return DualReadReconciliationRow(
        lane=lane,
        identity=identity,
        source_classification=classification,
        disposition=disposition,
    )


def _rows(
    lifecycle: LegacyLifecycleImportResult,
    document: LegacyDocumentEvidenceImportResult,
    reduction: LegacyFeeReductionImportResult,
    fee_truth: LegacyFeeTruthLinkResult,
) -> tuple[DualReadReconciliationRow, ...]:
    lifecycle_rows = tuple(
        _row(
            lane="LIFECYCLE",
            identity=row.case_id,
            classification=row.classification,
        )
        for row in lifecycle.rows
    )
    document_rows = tuple(
        _row(
            lane="DOCUMENT_EVIDENCE",
            identity=row.attachment_id,
            classification=row.classification,
        )
        for row in document.rows
    )
    reduction_rows = tuple(
        _row(
            lane="FEE_REDUCTION",
            identity=row.case_id,
            classification=row.classification,
        )
        for row in reduction.rows
    )
    fee_truth_rows = tuple(
        _row(
            lane="FEE_TRUTH",
            identity=f"{row.fee_item_id}|payment:{row.gov_payment_id or 'NONE'}",
            classification=row.classification,
        )
        for row in fee_truth.rows
    )
    return lifecycle_rows + document_rows + reduction_rows + fee_truth_rows


def _report_hash(
    *,
    scanned: int,
    reconciled: int,
    classified_conflicts: int,
    requires_import: int,
    accepted: bool,
    child_hashes: tuple[DualReadChildHashes, ...],
    rows: tuple[DualReadReconciliationRow, ...],
) -> str:
    canonical = json.dumps(
        {
            "accepted": accepted,
            "child_hashes": [asdict(item) for item in child_hashes],
            "classified_conflicts": classified_conflicts,
            "reconciled": reconciled,
            "requires_import": requires_import,
            "rows": [asdict(row) for row in rows],
            "scanned": scanned,
            "schema": "FPMS_V8_DUAL_READ_RECONCILIATION_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audit_v8_dual_read(
    *,
    transaction: Session,
    actor_id: str,
    lifecycle_recorded_at: datetime,
    fee_reduction_manifest: LegacyFeeReductionMigrationManifest,
    fee_truth_rows: tuple[LegacyFeeTruthMigrationRow, ...],
) -> DualReadReconciliationReport:
    _validate_input(
        transaction=transaction,
        actor_id=actor_id,
        lifecycle_recorded_at=lifecycle_recorded_at,
        fee_reduction_manifest=fee_reduction_manifest,
        fee_truth_rows=fee_truth_rows,
    )
    with transaction.no_autoflush:
        lifecycle = import_legacy_lifecycle(
            transaction=transaction,
            actor_id=actor_id,
            recorded_at=lifecycle_recorded_at,
            dry_run=True,
            expected_plan_sha256=None,
        )
        document = import_legacy_document_evidence(
            transaction=transaction,
            actor_id=actor_id,
            dry_run=True,
            expected_plan_sha256=None,
        )
        reduction = import_legacy_fee_reductions(
            transaction=transaction,
            manifest=fee_reduction_manifest,
            dry_run=True,
            expected_plan_sha256=None,
        )
        fee_truth = link_legacy_fee_truth(
            transaction=transaction,
            rows=fee_truth_rows,
            dry_run=True,
            expected_plan_sha256=None,
        )
    child_hashes = (
        _child_hashes("LIFECYCLE", lifecycle, LegacyLifecycleImportResult),
        _child_hashes(
            "DOCUMENT_EVIDENCE",
            document,
            LegacyDocumentEvidenceImportResult,
        ),
        _child_hashes("FEE_REDUCTION", reduction, LegacyFeeReductionImportResult),
        _child_hashes("FEE_TRUTH", fee_truth, LegacyFeeTruthLinkResult),
    )
    rows = _rows(lifecycle, document, reduction, fee_truth)
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict("V8_DUAL_READ_WRITE_DETECTED")
    reconciled = sum(row.disposition == _RECONCILED for row in rows)
    classified_conflicts = sum(row.disposition == _CLASSIFIED_CONFLICT for row in rows)
    requires_import = sum(row.disposition == _REQUIRES_IMPORT for row in rows)
    accepted = requires_import == 0
    report_sha256 = _report_hash(
        scanned=len(rows),
        reconciled=reconciled,
        classified_conflicts=classified_conflicts,
        requires_import=requires_import,
        accepted=accepted,
        child_hashes=child_hashes,
        rows=rows,
    )
    return DualReadReconciliationReport(
        scanned=len(rows),
        reconciled=reconciled,
        classified_conflicts=classified_conflicts,
        requires_import=requires_import,
        accepted=accepted,
        child_hashes=child_hashes,
        report_sha256=report_sha256,
        rows=rows,
    )
