from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import DocumentEvidenceVersion
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
    FeeReductionValidationError,
    validate_fee_reduction,
)
from app.modules.fees.models import (
    FeeReductionApproval,
    LegacyFeeReductionProvenance,
)

__all__ = (
    "LegacyFeeReductionApprovalMatch",
    "LegacyFeeReductionMigrationRow",
    "LegacyFeeReductionMigrationManifest",
    "LegacyFeeReductionImportRowResult",
    "LegacyFeeReductionImportResult",
    "import_legacy_fee_reductions",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeReductionApprovalMatch:
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    fee_codes: tuple[str, ...]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    source_evidence_content_hash: str


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeReductionMigrationRow:
    case_id: str
    legacy_value: object
    source_reference: str
    source_version: str
    source_snapshot_hash: str
    approval_id: str | None
    approval_match: LegacyFeeReductionApprovalMatch | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeReductionMigrationManifest:
    version: str
    manifest_hash: str
    approval_status: str
    confirmed_by: str
    confirmed_at: datetime
    rows: tuple[LegacyFeeReductionMigrationRow, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeReductionImportRowResult:
    case_id: str
    legacy_value: object
    classification: str
    approval_id: str | None
    will_update_case: bool
    will_create_provenance: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeReductionImportResult:
    rows: tuple[LegacyFeeReductionImportRowResult, ...]
    counts: Mapping[str, int]
    input_sha256: str
    plan_sha256: str
    output_sha256: str


@dataclass(frozen=True, slots=True)
class _PlannedRow:
    source: LegacyFeeReductionMigrationRow
    case: Case | None
    provenance: LegacyFeeReductionProvenance | None
    classification: str
    approval_id: str | None
    will_update_case: bool
    will_create_provenance: bool


_VALUES = {
    "0": Decimal("0.0000"),
    "0.7": Decimal("0.7000"),
    "0.85": Decimal("0.8500"),
}
_HASH_LENGTH = 64
_COUNT_KEYS = (
    "scanned",
    "explicit-zero",
    "reused-70",
    "reused-85",
    "unchanged",
    "invalid",
    "missing-approval",
    "ambiguous-approval",
    "planned-writes",
)
_FAILURE_CLASSIFICATIONS = frozenset({"invalid", "missing-approval", "ambiguous-approval"})


def _conflict(field: str | None = None) -> None:
    details = {"field": field} if field is not None else None
    raise_business_error(
        "LEGACY_FEE_REDUCTION_IMPORT_CONFLICT",
        "Legacy fee reduction import conflict",
        details=details,
        status_code=409,
    )


def _is_exact_string(value: object, *, limit: int | None = None) -> bool:
    return bool(
        type(value) is str
        and value
        and value == value.strip()
        and "\x00" not in value
        and (limit is None or len(value) <= limit)
    )


def _is_hash(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == _HASH_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _date_value(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _approval_match_payload(
    match: LegacyFeeReductionApprovalMatch | None,
) -> object:
    if match is None:
        return None
    return {
        "applicant_set_key": match.applicant_set_key,
        "case_id": match.case_id,
        "effective_from": _date_value(match.effective_from),
        "effective_to": _date_value(match.effective_to),
        "fee_codes": list(match.fee_codes),
        "fee_year_from": match.fee_year_from,
        "fee_year_to": match.fee_year_to,
        "scope_type": (
            match.scope_type.value
            if type(match.scope_type) is FeeReductionApprovalScopeType
            else str(match.scope_type)
        ),
        "source_evidence_content_hash": match.source_evidence_content_hash,
        "source_evidence_version_id": match.source_evidence_version_id,
    }


def _row_payload(row: LegacyFeeReductionMigrationRow) -> dict[str, object]:
    return {
        "approval_id": row.approval_id,
        "approval_match": _approval_match_payload(row.approval_match),
        "case_id": row.case_id,
        "legacy_value": row.legacy_value,
        "source_reference": row.source_reference,
        "source_snapshot_hash": row.source_snapshot_hash,
        "source_version": row.source_version,
    }


def _validate_manifest_authority(
    transaction: Session,
    manifest: object,
) -> LegacyFeeReductionMigrationManifest:
    if type(manifest) is not LegacyFeeReductionMigrationManifest:
        _conflict("manifest")
    if not _is_exact_string(manifest.version):
        _conflict("version")
    if not _is_hash(manifest.manifest_hash):
        _conflict("manifest_hash")
    if manifest.approval_status != "APPROVED":
        _conflict("approval_status")
    if not _is_exact_string(manifest.confirmed_by, limit=36):
        _conflict("confirmed_by")
    if type(manifest.confirmed_at) is not datetime or manifest.confirmed_at.tzinfo is not None:
        _conflict("confirmed_at")
    if type(manifest.rows) is not tuple or any(
        type(row) is not LegacyFeeReductionMigrationRow for row in manifest.rows
    ):
        _conflict("rows")
    case_ids = tuple(row.case_id for row in manifest.rows)
    if any(not _is_exact_string(case_id, limit=36) for case_id in case_ids):
        _conflict("case_id")
    if len(set(case_ids)) != len(case_ids):
        _conflict("case_id")
    with transaction.no_autoflush:
        if transaction.get(T_User, manifest.confirmed_by) is None:
            _conflict("confirmed_by")
    return manifest


def _manifest_payload(
    manifest: LegacyFeeReductionMigrationManifest,
) -> dict[str, object]:
    return {
        "approval_status": manifest.approval_status,
        "confirmed_at": manifest.confirmed_at.isoformat(),
        "confirmed_by": manifest.confirmed_by,
        "manifest_hash": manifest.manifest_hash,
        "rows": [_row_payload(row) for row in sorted(manifest.rows, key=lambda item: item.case_id)],
        "version": manifest.version,
    }


def _row_authority_is_valid(row: LegacyFeeReductionMigrationRow) -> bool:
    if (
        type(row.legacy_value) is not str
        or row.legacy_value not in _VALUES
        or not _is_exact_string(row.source_reference)
        or not _is_exact_string(row.source_version)
        or not _is_hash(row.source_snapshot_hash)
    ):
        return False
    if row.legacy_value == "0":
        return row.approval_id is None and row.approval_match is None
    return _is_exact_string(row.approval_id, limit=36) and _approval_match_is_valid(
        row,
        row.approval_match,
    )


def _approval_match_is_valid(
    row: LegacyFeeReductionMigrationRow,
    match: object,
) -> bool:
    if type(match) is not LegacyFeeReductionApprovalMatch:
        return False
    if type(match.scope_type) is not FeeReductionApprovalScopeType:
        return False
    if match.scope_type is FeeReductionApprovalScopeType.CASE:
        scope_valid = match.case_id == row.case_id and match.applicant_set_key is None
    else:
        scope_valid = match.case_id is None and _is_hash(match.applicant_set_key)
    if not scope_valid:
        return False
    if (
        type(match.fee_codes) is not tuple
        or not match.fee_codes
        or tuple(sorted(set(match.fee_codes))) != match.fee_codes
        or any(not _is_exact_string(code, limit=64) for code in match.fee_codes)
    ):
        return False
    if match.fee_year_from is None:
        year_valid = match.fee_year_to is None
    else:
        year_valid = bool(
            type(match.fee_year_from) is int
            and match.fee_year_from > 0
            and type(match.fee_year_to) is int
            and match.fee_year_to >= match.fee_year_from
        )
    return bool(
        year_valid
        and type(match.effective_from) is date
        and (match.effective_to is None or type(match.effective_to) is date)
        and (match.effective_to is None or match.effective_to >= match.effective_from)
        and _is_exact_string(match.source_evidence_version_id, limit=36)
        and _is_exact_string(match.source_evidence_content_hash, limit=128)
    )


def _parse_canonical_json(source: object) -> object | None:
    if type(source) is not str:
        return None
    try:
        parsed = json.loads(source)
        if _canonical_json(parsed) != source:
            return None
    except (TypeError, ValueError, UnicodeEncodeError, json.JSONDecodeError):
        return None
    return parsed


def _fee_codes(approval: FeeReductionApproval) -> tuple[str, ...]:
    snapshot = _parse_canonical_json(approval.fee_scope_snapshot)
    if (
        type(snapshot) is not dict
        or set(snapshot) != {"fee_codes", "schema"}
        or snapshot["schema"] != "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"
        or type(snapshot["fee_codes"]) is not list
        or not snapshot["fee_codes"]
        or snapshot["fee_codes"] != sorted(set(snapshot["fee_codes"]))
        or any(not _is_exact_string(code, limit=64) for code in snapshot["fee_codes"])
        or hashlib.sha256(approval.fee_scope_snapshot.encode("utf-8")).hexdigest()
        != approval.fee_scope_hash
    ):
        return ()
    return tuple(snapshot["fee_codes"])


def _eligibility_is_valid(approval: FeeReductionApproval) -> bool:
    snapshot = _parse_canonical_json(approval.eligibility_snapshot)
    if (
        type(snapshot) is not dict
        or set(snapshot) != {"applicants", "attributes_version", "schema"}
        or snapshot["schema"] != "FPMS_FEE_REDUCTION_ELIGIBILITY_V1"
        or not _is_exact_string(snapshot["attributes_version"])
        or type(snapshot["applicants"]) is not list
        or not snapshot["applicants"]
        or hashlib.sha256(approval.eligibility_snapshot.encode("utf-8")).hexdigest()
        != approval.eligibility_snapshot_hash
    ):
        return False
    applicant_ids: list[str] = []
    for applicant in snapshot["applicants"]:
        if (
            type(applicant) is not dict
            or set(applicant) != {"applicant_id", "attributes"}
            or not _is_exact_string(applicant["applicant_id"], limit=36)
            or type(applicant["attributes"]) is not dict
        ):
            return False
        applicant_ids.append(applicant["applicant_id"])
    if applicant_ids != sorted(set(applicant_ids)):
        return False
    if approval.scope_type == FeeReductionApprovalScopeType.CASE.value:
        return approval.applicant_set_key is None
    expected_key = _digest(
        {
            "applicant_ids": applicant_ids,
            "eligibility_snapshot_hash": approval.eligibility_snapshot_hash,
            "schema": "FPMS_FEE_REDUCTION_APPLICANT_SET_V1",
        }
    )
    return approval.applicant_set_key == expected_key


def _evidence_is_current_and_exact(
    evidence: DocumentEvidenceVersion | None,
    *,
    row: LegacyFeeReductionMigrationRow,
    match: LegacyFeeReductionApprovalMatch,
) -> bool:
    return bool(
        evidence is not None
        and evidence.case_id == row.case_id
        and evidence.id == match.source_evidence_version_id
        and evidence.content_hash == match.source_evidence_content_hash
        and _is_exact_string(evidence.lineage_key, limit=128)
        and evidence.state == EvidenceVersionState.FINAL.value
        and evidence.review_state == EvidenceReviewState.APPROVED.value
        and _is_exact_string(evidence.reviewer_id, limit=36)
        and type(evidence.reviewed_at) is datetime
        and evidence.reviewed_at.tzinfo is None
        and evidence.reviewer_id != evidence.creator_id
        and evidence.current_identity_key == f"{evidence.case_id}|{evidence.lineage_key}"
    )


def _approval_matches(
    transaction: Session,
    *,
    row: LegacyFeeReductionMigrationRow,
    approval: FeeReductionApproval,
) -> bool:
    match = row.approval_match
    if type(match) is not LegacyFeeReductionApprovalMatch:
        return False
    if (
        approval.scope_type != match.scope_type.value
        or approval.case_id != match.case_id
        or approval.applicant_set_key != match.applicant_set_key
        or approval.reduction_ratio != _VALUES[row.legacy_value]
        or _fee_codes(approval) != match.fee_codes
        or approval.fee_year_from != match.fee_year_from
        or approval.fee_year_to != match.fee_year_to
        or approval.effective_from != match.effective_from
        or approval.effective_to != match.effective_to
        or approval.source_evidence_version_id != match.source_evidence_version_id
        or approval.confirmation_status != "CONFIRMED"
        or type(approval.confirmed_at) is not datetime
        or approval.confirmed_at.tzinfo is not None
        or not _is_exact_string(approval.confirmed_by, limit=36)
        or not _eligibility_is_valid(approval)
    ):
        return False
    evidence = transaction.get(
        DocumentEvidenceVersion,
        approval.source_evidence_version_id,
    )
    if not _evidence_is_current_and_exact(evidence, row=row, match=match):
        return False
    approval_context = FeeReductionApprovalContext(
        approval_id=approval.id,
        scope_type=match.scope_type,
        case_id=approval.case_id,
        applicant_set_key=approval.applicant_set_key,
        reduction_ratio=approval.reduction_ratio,
        fee_codes=frozenset(match.fee_codes),
        fee_year_from=approval.fee_year_from,
        fee_year_to=approval.fee_year_to,
        effective_from=approval.effective_from,
        effective_to=approval.effective_to,
        source_evidence_version_id=approval.source_evidence_version_id,
        confirmation_status=approval.confirmation_status,
        is_current=True,
    )
    try:
        validate_fee_reduction(
            reduction_input=FeeReductionInput(
                reduction_ratio=_VALUES[row.legacy_value],
                provenance=FeeReductionInputProvenance.CONFIRMED_MIGRATION,
            ),
            context=FeeReductionEvaluationContext(
                case_id=row.case_id,
                applicant_set_key=match.applicant_set_key,
                fee_code=match.fee_codes[0],
                fee_year_key=match.fee_year_from or 0,
                as_of_date=match.effective_from,
            ),
            approval=approval_context,
        )
    except FeeReductionValidationError:
        return False
    return True


def _exact_provenance(
    row: LegacyFeeReductionMigrationRow,
    manifest: LegacyFeeReductionMigrationManifest,
    provenance: LegacyFeeReductionProvenance,
    approval_id: str | None,
) -> bool:
    return bool(
        provenance.case_id == row.case_id
        and provenance.legacy_value == row.legacy_value
        and provenance.source_reference == row.source_reference
        and provenance.source_version == row.source_version
        and provenance.source_snapshot_hash == row.source_snapshot_hash
        and provenance.manifest_hash == manifest.manifest_hash
        and provenance.confirmed_by == manifest.confirmed_by
        and provenance.confirmed_at == manifest.confirmed_at
        and provenance.approval_id == approval_id
    )


def _plan_row(
    transaction: Session,
    *,
    manifest: LegacyFeeReductionMigrationManifest,
    row: LegacyFeeReductionMigrationRow,
    approvals: tuple[FeeReductionApproval, ...],
) -> _PlannedRow:
    case = transaction.get(Case, row.case_id)
    if not _row_authority_is_valid(row) or case is None:
        return _PlannedRow(row, case, None, "invalid", None, False, False)

    approval_id: str | None = None
    if row.legacy_value != "0":
        matching = tuple(
            approval
            for approval in approvals
            if _approval_matches(transaction, row=row, approval=approval)
        )
        if not matching:
            return _PlannedRow(row, case, None, "missing-approval", None, False, False)
        if len(matching) != 1:
            return _PlannedRow(row, case, None, "ambiguous-approval", None, False, False)
        if matching[0].id != row.approval_id:
            return _PlannedRow(row, case, None, "missing-approval", None, False, False)
        approval_id = matching[0].id

    provenances = tuple(
        transaction.scalars(
            select(LegacyFeeReductionProvenance)
            .where(
                LegacyFeeReductionProvenance.case_id == row.case_id,
                LegacyFeeReductionProvenance.manifest_hash == manifest.manifest_hash,
            )
            .order_by(LegacyFeeReductionProvenance.id)
        )
    )
    if len(provenances) > 1:
        return _PlannedRow(row, case, None, "invalid", approval_id, False, False)
    provenance = provenances[0] if provenances else None
    if provenance is not None:
        if not _exact_provenance(row, manifest, provenance, approval_id):
            return _PlannedRow(row, case, provenance, "invalid", approval_id, False, False)
        if case.fee_reduction != row.legacy_value:
            return _PlannedRow(row, case, provenance, "invalid", approval_id, False, False)
        return _PlannedRow(row, case, provenance, "unchanged", approval_id, False, False)

    classification = {
        "0": "explicit-zero",
        "0.7": "reused-70",
        "0.85": "reused-85",
    }[row.legacy_value]
    return _PlannedRow(
        row,
        case,
        None,
        classification,
        approval_id,
        case.fee_reduction != row.legacy_value,
        True,
    )


def _result(
    *,
    manifest: LegacyFeeReductionMigrationManifest,
    planned_rows: tuple[_PlannedRow, ...],
    input_sha256: str,
) -> LegacyFeeReductionImportResult:
    rows = tuple(
        LegacyFeeReductionImportRowResult(
            case_id=planned.source.case_id,
            legacy_value=planned.source.legacy_value,
            classification=planned.classification,
            approval_id=planned.approval_id,
            will_update_case=planned.will_update_case,
            will_create_provenance=planned.will_create_provenance,
        )
        for planned in planned_rows
    )
    counts = {key: 0 for key in _COUNT_KEYS}
    counts["scanned"] = len(rows)
    for row in rows:
        counts[row.classification] += 1
        if row.will_update_case or row.will_create_provenance:
            counts["planned-writes"] += 1
    output_sha256 = _digest(
        {
            "manifest_hash": manifest.manifest_hash,
            "rows": [
                {
                    "approval_id": row.approval_id,
                    "case_id": row.case_id,
                    "legacy_value": row.legacy_value,
                }
                for row in rows
                if row.classification not in _FAILURE_CLASSIFICATIONS
            ],
        }
    )
    plan_sha256 = _digest(
        {
            "input_sha256": input_sha256,
            "output_sha256": output_sha256,
            "rows": [
                {
                    "approval_id": row.approval_id,
                    "case_id": row.case_id,
                    "classification": row.classification,
                    "legacy_value": row.legacy_value,
                    "will_create_provenance": row.will_create_provenance,
                    "will_update_case": row.will_update_case,
                }
                for row in rows
            ],
        }
    )
    return LegacyFeeReductionImportResult(
        rows=rows,
        counts=counts,
        input_sha256=input_sha256,
        plan_sha256=plan_sha256,
        output_sha256=output_sha256,
    )


def import_legacy_fee_reductions(
    *,
    transaction: Session,
    manifest: LegacyFeeReductionMigrationManifest,
    dry_run: bool,
    expected_plan_sha256: str | None = None,
) -> LegacyFeeReductionImportResult:
    if not isinstance(transaction, Session):
        _conflict("transaction")
    approved_manifest = _validate_manifest_authority(transaction, manifest)
    if type(dry_run) is not bool:
        _conflict("dry_run")
    if dry_run and expected_plan_sha256 is not None:
        _conflict("expected_plan_sha256")

    try:
        input_sha256 = _digest(_manifest_payload(approved_manifest))
    except (TypeError, ValueError, UnicodeEncodeError):
        _conflict("manifest")

    with transaction.no_autoflush:
        approvals = tuple(
            transaction.scalars(select(FeeReductionApproval).order_by(FeeReductionApproval.id))
        )
        planned_rows = tuple(
            _plan_row(
                transaction,
                manifest=approved_manifest,
                row=row,
                approvals=approvals,
            )
            for row in sorted(approved_manifest.rows, key=lambda item: item.case_id)
        )
    result = _result(
        manifest=approved_manifest,
        planned_rows=planned_rows,
        input_sha256=input_sha256,
    )
    if dry_run:
        return result
    if (
        not _is_hash(expected_plan_sha256)
        or expected_plan_sha256 != result.plan_sha256
        or any(row.classification in _FAILURE_CLASSIFICATIONS for row in result.rows)
    ):
        _conflict("expected_plan_sha256")

    for planned in planned_rows:
        if not (planned.will_update_case or planned.will_create_provenance):
            continue
        if planned.case is None:
            _conflict("case_id")
        planned.case.fee_reduction = planned.source.legacy_value
        if planned.will_create_provenance:
            transaction.add(
                LegacyFeeReductionProvenance(
                    case_id=planned.source.case_id,
                    legacy_value=planned.source.legacy_value,
                    source_reference=planned.source.source_reference,
                    source_version=planned.source.source_version,
                    source_snapshot_hash=planned.source.source_snapshot_hash,
                    manifest_hash=approved_manifest.manifest_hash,
                    confirmed_by=approved_manifest.confirmed_by,
                    confirmed_at=approved_manifest.confirmed_at,
                    approval_id=planned.approval_id,
                )
            )
    transaction.flush()
    return result
