from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import Case
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import DocumentEvidenceVersion
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.models import FeeReductionApproval

__all__ = (
    "FeeReductionApprovalRecordDisposition",
    "RecordFeeReductionApprovalCommand",
    "RecordFeeReductionApprovalResult",
    "record_fee_reduction_approval",
)


class FeeReductionApprovalRecordDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordFeeReductionApprovalCommand:
    case_id: str
    scope_type: FeeReductionApprovalScopeType
    applicant_ids: tuple[str, ...]
    eligibility_attributes_version: str
    eligibility_attributes_json: str
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    expected_source_content_hash: str
    confirmed_at: datetime
    confirmed_by: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordFeeReductionApprovalResult:
    approval_id: str
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_scope_snapshot: str
    fee_scope_hash: str
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    confirmed_at: datetime
    confirmed_by: str
    eligibility_snapshot: str
    eligibility_snapshot_hash: str
    approval_identity_key: str
    disposition: FeeReductionApprovalRecordDisposition


@dataclass(frozen=True, slots=True)
class _RecordFacts:
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_scope_snapshot: str
    fee_scope_hash: str
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmed_at: datetime
    confirmed_by: str
    eligibility_snapshot: str
    eligibility_snapshot_hash: str
    approval_identity_key: str


_RATIO_70 = Decimal("0.7000")
_RATIO_85 = Decimal("0.8500")
_RATIO_QUANTUM = Decimal("0.0001")


def _invalid(field: str) -> None:
    raise_business_error(
        "FEE_REDUCTION_APPROVAL_INVALID",
        "Invalid fee reduction approval input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "FEE_REDUCTION_APPROVAL_CONFLICT",
        "Fee reduction approval conflict",
        status_code=409,
    )


def _is_canonical_string(value: object, *, limit: int | None = None) -> bool:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or (limit is not None and len(value) > limit)
    ):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _required_string(value: object, *, field: str, limit: int | None = None) -> str:
    if not _is_canonical_string(value, limit=limit):
        _invalid(field)
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _parse_strict_json(value: object) -> dict[str, object]:
    source = _required_string(value, field="eligibility_attributes_json")

    def reject_constant(_value: str) -> None:
        raise ValueError

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError
            result[key] = item
        return result

    try:
        parsed = json.loads(
            source,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        _invalid("eligibility_attributes_json")
    if type(parsed) is not dict:
        _invalid("eligibility_attributes_json")
    try:
        _canonical_json(parsed).encode("utf-8")
    except UnicodeEncodeError:
        _invalid("eligibility_attributes_json")
    return parsed


def _validate_ratio(value: object) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        _invalid("reduction_ratio")
    if value == Decimal("0"):
        raise_business_error(
            "FEE_REDUCTION_APPROVAL_NOT_REQUIRED",
            "No fee reduction approval record is required",
            details={"field": "reduction_ratio"},
            status_code=400,
        )
    if value == _RATIO_70:
        return _RATIO_70
    if value == _RATIO_85:
        return _RATIO_85
    _invalid("reduction_ratio")


def _validate_year_scope(year_from: object, year_to: object) -> tuple[int | None, int | None]:
    if year_from is None:
        if year_to is not None:
            _invalid("fee_year_from")
        return None, None
    if year_to is None:
        _invalid("fee_year_to")
    if type(year_from) is not int or year_from <= 0:
        _invalid("fee_year_from")
    if type(year_to) is not int or year_to <= 0 or year_from > year_to:
        _invalid("fee_year_to")
    return year_from, year_to


def _validate_date_scope(
    effective_from: object,
    effective_to: object,
) -> tuple[date, date | None]:
    if type(effective_from) is not date:
        _invalid("effective_from")
    if effective_to is not None and type(effective_to) is not date:
        _invalid("effective_to")
    if effective_to is not None and effective_to < effective_from:
        _invalid("effective_to")
    return effective_from, effective_to


def _build_record_facts(command: object) -> _RecordFacts:
    if type(command) is not RecordFeeReductionApprovalCommand:
        _invalid("command")

    case_id = _required_string(command.case_id, field="case_id", limit=36)
    if type(command.scope_type) is not FeeReductionApprovalScopeType:
        _invalid("scope_type")
    ratio = _validate_ratio(command.reduction_ratio)

    applicant_ids = command.applicant_ids
    if type(applicant_ids) is not tuple or not applicant_ids:
        _invalid("applicant_ids")
    validated_applicants = tuple(
        _required_string(applicant_id, field="applicant_ids", limit=36)
        for applicant_id in applicant_ids
    )
    if len(set(validated_applicants)) != len(validated_applicants):
        _invalid("applicant_ids")
    if ratio == _RATIO_85 and len(validated_applicants) != 1:
        _invalid("applicant_ids")
    if ratio == _RATIO_70 and len(validated_applicants) < 2:
        _invalid("applicant_ids")

    attributes_version = _required_string(
        command.eligibility_attributes_version,
        field="eligibility_attributes_version",
        limit=128,
    )
    attributes = _parse_strict_json(command.eligibility_attributes_json)
    if set(attributes) != set(validated_applicants) or any(
        type(attributes[applicant_id]) is not dict for applicant_id in validated_applicants
    ):
        _invalid("eligibility_attributes_json")

    fee_codes = command.fee_codes
    if type(fee_codes) is not tuple or not fee_codes:
        _invalid("fee_codes")
    validated_fee_codes = tuple(
        _required_string(fee_code, field="fee_codes", limit=64) for fee_code in fee_codes
    )
    if len(set(validated_fee_codes)) != len(validated_fee_codes):
        _invalid("fee_codes")
    sorted_fee_codes = tuple(sorted(validated_fee_codes))

    fee_year_from, fee_year_to = _validate_year_scope(
        command.fee_year_from,
        command.fee_year_to,
    )
    effective_from, effective_to = _validate_date_scope(
        command.effective_from,
        command.effective_to,
    )
    source_evidence_version_id = _required_string(
        command.source_evidence_version_id,
        field="source_evidence_version_id",
        limit=36,
    )
    _required_string(
        command.expected_source_content_hash,
        field="expected_source_content_hash",
        limit=128,
    )
    if type(command.confirmed_at) is not datetime or command.confirmed_at.tzinfo is not None:
        _invalid("confirmed_at")
    confirmed_by = _required_string(command.confirmed_by, field="confirmed_by", limit=36)

    fee_scope_snapshot = _canonical_json(
        {
            "fee_codes": sorted_fee_codes,
            "schema": "FPMS_FEE_REDUCTION_FEE_SCOPE_V1",
        }
    )
    fee_scope_hash = _digest(fee_scope_snapshot)
    eligibility_snapshot = _canonical_json(
        {
            "applicants": [
                {
                    "applicant_id": applicant_id,
                    "attributes": attributes[applicant_id],
                }
                for applicant_id in sorted(validated_applicants)
            ],
            "attributes_version": attributes_version,
            "schema": "FPMS_FEE_REDUCTION_ELIGIBILITY_V1",
        }
    )
    eligibility_snapshot_hash = _digest(eligibility_snapshot)

    if command.scope_type is FeeReductionApprovalScopeType.CASE:
        persisted_case_id = case_id
        applicant_set_key = None
        scope_id = case_id
    else:
        persisted_case_id = None
        applicant_set_key = _digest(
            _canonical_json(
                {
                    "applicant_ids": sorted(validated_applicants),
                    "eligibility_snapshot_hash": eligibility_snapshot_hash,
                    "schema": "FPMS_FEE_REDUCTION_APPLICANT_SET_V1",
                }
            )
        )
        scope_id = applicant_set_key

    approval_identity_key = _digest(
        _canonical_json(
            {
                "effective_from": effective_from.isoformat(),
                "effective_to": effective_to.isoformat() if effective_to is not None else None,
                "fee_scope_hash": fee_scope_hash,
                "fee_year_from": fee_year_from,
                "fee_year_to": fee_year_to,
                "reduction_ratio": format(ratio.quantize(_RATIO_QUANTUM), ".4f"),
                "schema": "FPMS_FEE_REDUCTION_APPROVAL_IDENTITY_V1",
                "scope_id": scope_id,
                "scope_type": command.scope_type.value,
                "source_evidence_version_id": source_evidence_version_id,
            }
        )
    )
    return _RecordFacts(
        scope_type=command.scope_type,
        case_id=persisted_case_id,
        applicant_set_key=applicant_set_key,
        reduction_ratio=ratio.quantize(_RATIO_QUANTUM),
        fee_codes=sorted_fee_codes,
        fee_scope_snapshot=fee_scope_snapshot,
        fee_scope_hash=fee_scope_hash,
        fee_year_from=fee_year_from,
        fee_year_to=fee_year_to,
        effective_from=effective_from,
        effective_to=effective_to,
        source_evidence_version_id=source_evidence_version_id,
        confirmed_at=command.confirmed_at,
        confirmed_by=confirmed_by,
        eligibility_snapshot=eligibility_snapshot,
        eligibility_snapshot_hash=eligibility_snapshot_hash,
        approval_identity_key=approval_identity_key,
    )


def _identity_rows(transaction: Session, identity_key: str) -> list[FeeReductionApproval]:
    return list(
        transaction.scalars(
            select(FeeReductionApproval).where(
                FeeReductionApproval.approval_identity_key == identity_key
            )
        )
    )


def _row_matches(row: FeeReductionApproval, facts: _RecordFacts) -> bool:
    return (
        row.scope_type == facts.scope_type.value
        and row.case_id == facts.case_id
        and row.applicant_set_key == facts.applicant_set_key
        and row.reduction_ratio == facts.reduction_ratio
        and row.fee_scope_snapshot == facts.fee_scope_snapshot
        and row.fee_scope_hash == facts.fee_scope_hash
        and row.fee_year_from == facts.fee_year_from
        and row.fee_year_to == facts.fee_year_to
        and row.effective_from == facts.effective_from
        and row.effective_to == facts.effective_to
        and row.source_evidence_version_id == facts.source_evidence_version_id
        and row.confirmation_status == "CONFIRMED"
        and row.confirmed_at == facts.confirmed_at
        and row.confirmed_by == facts.confirmed_by
        and row.eligibility_snapshot == facts.eligibility_snapshot
        and row.eligibility_snapshot_hash == facts.eligibility_snapshot_hash
        and row.approval_identity_key == facts.approval_identity_key
    )


def _require_exact_single_row(
    rows: list[FeeReductionApproval],
    facts: _RecordFacts,
) -> FeeReductionApproval | None:
    if not rows:
        return None
    if len(rows) != 1 or not _row_matches(rows[0], facts):
        _conflict()
    return rows[0]


def _validate_evidence(
    command: RecordFeeReductionApprovalCommand,
    transaction: Session,
    *,
    require_current: bool,
) -> None:
    if transaction.get(Case, command.case_id) is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    evidence = transaction.get(DocumentEvidenceVersion, command.source_evidence_version_id)
    if evidence is None:
        raise_business_error(
            "EVIDENCE_VERSION_NOT_FOUND",
            "Evidence version not found",
            status_code=404,
        )
    if (
        evidence.case_id != command.case_id
        or type(evidence.lineage_key) is not str
        or not evidence.lineage_key
        or evidence.lineage_key != evidence.lineage_key.strip()
        or "\x00" in evidence.lineage_key
        or len(evidence.lineage_key) > 128
        or evidence.state != EvidenceVersionState.FINAL.value
        or evidence.review_state != EvidenceReviewState.APPROVED.value
        or not _is_canonical_string(evidence.reviewer_id, limit=36)
        or type(evidence.reviewed_at) is not datetime
        or evidence.reviewed_at.tzinfo is not None
        or evidence.reviewer_id == evidence.creator_id
        or evidence.content_hash != command.expected_source_content_hash
    ):
        _conflict()
    if require_current:
        expected_current_identity = f"{command.case_id}|{evidence.lineage_key}"
        if evidence.current_identity_key != expected_current_identity:
            _conflict()


def _result(
    row: FeeReductionApproval,
    facts: _RecordFacts,
    disposition: FeeReductionApprovalRecordDisposition,
) -> RecordFeeReductionApprovalResult:
    return RecordFeeReductionApprovalResult(
        approval_id=row.id,
        scope_type=facts.scope_type,
        case_id=facts.case_id,
        applicant_set_key=facts.applicant_set_key,
        reduction_ratio=facts.reduction_ratio,
        fee_codes=facts.fee_codes,
        fee_scope_snapshot=facts.fee_scope_snapshot,
        fee_scope_hash=facts.fee_scope_hash,
        fee_year_from=facts.fee_year_from,
        fee_year_to=facts.fee_year_to,
        effective_from=facts.effective_from,
        effective_to=facts.effective_to,
        source_evidence_version_id=facts.source_evidence_version_id,
        confirmation_status="CONFIRMED",
        confirmed_at=facts.confirmed_at,
        confirmed_by=facts.confirmed_by,
        eligibility_snapshot=facts.eligibility_snapshot,
        eligibility_snapshot_hash=facts.eligibility_snapshot_hash,
        approval_identity_key=facts.approval_identity_key,
        disposition=disposition,
    )


def record_fee_reduction_approval(
    command: RecordFeeReductionApprovalCommand,
    transaction: Session,
) -> RecordFeeReductionApprovalResult:
    facts = _build_record_facts(command)
    existing = _require_exact_single_row(
        _identity_rows(transaction, facts.approval_identity_key),
        facts,
    )
    _validate_evidence(command, transaction, require_current=existing is None)
    if existing is not None:
        return _result(existing, facts, FeeReductionApprovalRecordDisposition.REUSED)

    row = FeeReductionApproval(
        id=str(uuid4()),
        scope_type=facts.scope_type.value,
        case_id=facts.case_id,
        applicant_set_key=facts.applicant_set_key,
        reduction_ratio=facts.reduction_ratio,
        fee_scope_snapshot=facts.fee_scope_snapshot,
        fee_scope_hash=facts.fee_scope_hash,
        fee_year_from=facts.fee_year_from,
        fee_year_to=facts.fee_year_to,
        effective_from=facts.effective_from,
        effective_to=facts.effective_to,
        source_evidence_version_id=facts.source_evidence_version_id,
        confirmation_status="CONFIRMED",
        confirmed_at=facts.confirmed_at,
        confirmed_by=facts.confirmed_by,
        eligibility_snapshot=facts.eligibility_snapshot,
        eligibility_snapshot_hash=facts.eligibility_snapshot_hash,
        approval_identity_key=facts.approval_identity_key,
        created_by=facts.confirmed_by,
        updated_by=facts.confirmed_by,
    )
    try:
        with transaction.begin_nested():
            transaction.add(row)
            transaction.flush()
    except IntegrityError:
        winner = _require_exact_single_row(
            _identity_rows(transaction, facts.approval_identity_key),
            facts,
        )
        if winner is None:
            _conflict()
        return _result(winner, facts, FeeReductionApprovalRecordDisposition.REUSED)
    return _result(row, facts, FeeReductionApprovalRecordDisposition.CREATED)
