from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.annuity.models import GovPayment
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)

__all__ = (
    "LegacyFeeTruthMigrationRow",
    "LegacyFeeTruthLinkRowResult",
    "LegacyFeeTruthLinkResult",
    "link_legacy_fee_truth",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeTruthMigrationRow:
    case_id: str
    source_activity_id: str
    fee_code: str
    fee_year_key: int
    fee_item_id: str
    gov_payment_id: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeTruthLinkRowResult:
    fee_item_id: str
    gov_payment_id: int | None
    obligation_line_id: str | None
    classification: str
    planned_writes: int


@dataclass(frozen=True, slots=True, kw_only=True)
class LegacyFeeTruthLinkResult:
    scanned: int
    linked: int
    unchanged: int
    invalid: int
    unmatched: int
    ambiguous: int
    planned_writes: int
    input_sha256: str
    plan_sha256: str
    output_sha256: str
    rows: tuple[LegacyFeeTruthLinkRowResult, ...]


@dataclass(frozen=True, slots=True)
class _PlannedRow:
    source: LegacyFeeTruthMigrationRow
    obligation_line_id: str | None
    add_draft_link: bool
    add_payment_link: bool
    result: LegacyFeeTruthLinkRowResult


@dataclass(frozen=True, slots=True)
class _Plan:
    input_sha256: str
    plan_sha256: str
    rows: tuple[_PlannedRow, ...]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _exact_text(value: object, *, limit: int) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and "\x00" not in value
        and len(value) <= limit
    )


def _row_input(row: LegacyFeeTruthMigrationRow) -> dict[str, object]:
    return {
        "case_id": row.case_id,
        "fee_code": row.fee_code,
        "fee_item_id": row.fee_item_id,
        "fee_year_key": row.fee_year_key,
        "gov_payment_id": row.gov_payment_id,
        "source_activity_id": row.source_activity_id,
    }


def _row_order_key(row: LegacyFeeTruthMigrationRow) -> tuple[object, ...]:
    if row.gov_payment_id is None:
        payment_identity: tuple[int, object] = (0, 0)
    elif type(row.gov_payment_id) is int:
        payment_identity = (1, row.gov_payment_id)
    else:
        payment_identity = (2, repr(row.gov_payment_id))
    return (str(row.fee_item_id), payment_identity)


def _valid_row(row: object) -> bool:
    return (
        type(row) is LegacyFeeTruthMigrationRow
        and _exact_text(row.case_id, limit=36)
        and _exact_text(row.source_activity_id, limit=36)
        and _exact_text(row.fee_code, limit=64)
        and type(row.fee_year_key) is int
        and row.fee_year_key >= 0
        and _exact_text(row.fee_item_id, limit=36)
        and (
            row.gov_payment_id is None
            or (type(row.gov_payment_id) is int and row.gov_payment_id > 0)
        )
    )


def _result(
    row: LegacyFeeTruthMigrationRow,
    *,
    classification: str,
    obligation_line_id: str | None = None,
    planned_writes: int = 0,
) -> LegacyFeeTruthLinkRowResult:
    return LegacyFeeTruthLinkRowResult(
        fee_item_id=str(row.fee_item_id),
        gov_payment_id=(row.gov_payment_id if type(row.gov_payment_id) is int else None),
        obligation_line_id=obligation_line_id,
        classification=classification,
        planned_writes=planned_writes,
    )


def _history_is_exact(
    transaction: Session,
    row: LegacyFeeTruthMigrationRow,
) -> bool:
    item = transaction.get(FeeItem, row.fee_item_id)
    if item is None:
        return False
    draft = transaction.get(FeeDraft, item.draft_id)
    if (
        draft is None
        or item.case_id != row.case_id
        or draft.case_id != row.case_id
        or item.fee_code != row.fee_code
        or item.year_no != row.fee_year_key
    ):
        return False
    if row.gov_payment_id is None:
        return True
    payment = transaction.get(GovPayment, row.gov_payment_id)
    return (
        payment is not None
        and payment.case_id == row.case_id
        and payment.fee_item_id == row.fee_item_id
        and payment.fee_code == row.fee_code
        and payment.year_no == row.fee_year_key
    )


def _candidate_lines(
    transaction: Session,
    row: LegacyFeeTruthMigrationRow,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (line_id, fee_domain)
        for line_id, fee_domain in transaction.execute(
            select(FeeObligationLine.id, FeeObligation.fee_domain)
            .join(
                FeeObligation,
                FeeObligation.id == FeeObligationLine.obligation_id,
            )
            .where(
                FeeObligation.case_id == row.case_id,
                FeeObligation.source_activity_id == row.source_activity_id,
                FeeObligationLine.case_id == row.case_id,
                FeeObligationLine.source_activity_id == row.source_activity_id,
                FeeObligationLine.fee_code == row.fee_code,
                FeeObligationLine.fee_year_key == row.fee_year_key,
            )
            .order_by(FeeObligationLine.id)
        )
    )


def _existing_line_ids(
    transaction: Session,
    row: LegacyFeeTruthMigrationRow,
) -> tuple[set[str], set[str]]:
    draft_line_ids = set(
        transaction.scalars(
            select(FeeObligationDraftItemLink.obligation_line_id).where(
                FeeObligationDraftItemLink.fee_item_id == row.fee_item_id
            )
        )
    )
    payment_line_ids: set[str] = set()
    if row.gov_payment_id is not None:
        payment_line_ids.update(
            transaction.scalars(
                select(FeeObligationPaymentEvidenceLink.obligation_line_id).where(
                    FeeObligationPaymentEvidenceLink.gov_payment_id == row.gov_payment_id
                )
            )
        )
    return draft_line_ids, payment_line_ids


def _plan_row(
    transaction: Session,
    row: LegacyFeeTruthMigrationRow,
    *,
    planned_draft_links: set[tuple[str, str]],
    planned_item_lines: dict[str, str],
) -> _PlannedRow:
    if not _valid_row(row) or not _history_is_exact(transaction, row):
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="INVALID"),
        )
    candidates = _candidate_lines(transaction, row)
    if not candidates:
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="UNMATCHED"),
        )
    if len(candidates) != 1:
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="AMBIGUOUS"),
        )

    line_id, fee_domain = candidates[0]
    item = transaction.get(FeeItem, row.fee_item_id)
    if item is None or item.fee_type != fee_domain:
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="INVALID"),
        )
    draft_line_ids, payment_line_ids = _existing_line_ids(transaction, row)
    if (draft_line_ids and draft_line_ids != {line_id}) or (
        payment_line_ids and payment_line_ids != {line_id}
    ):
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="AMBIGUOUS"),
        )
    planned_line_id = planned_item_lines.get(row.fee_item_id)
    if planned_line_id is not None and planned_line_id != line_id:
        return _PlannedRow(
            row,
            None,
            False,
            False,
            _result(row, classification="AMBIGUOUS"),
        )
    planned_item_lines[row.fee_item_id] = line_id
    draft_link_identity = (line_id, row.fee_item_id)
    add_draft_link = (
        line_id not in draft_line_ids and draft_link_identity not in planned_draft_links
    )
    if add_draft_link:
        planned_draft_links.add(draft_link_identity)
    add_payment_link = row.gov_payment_id is not None and line_id not in payment_line_ids
    planned_writes = int(add_draft_link) + int(add_payment_link)
    classification = "LINKED" if planned_writes else "UNCHANGED"
    return _PlannedRow(
        row,
        line_id,
        add_draft_link,
        add_payment_link,
        _result(
            row,
            classification=classification,
            obligation_line_id=line_id,
            planned_writes=planned_writes,
        ),
    )


def _build_plan(
    transaction: Session,
    rows: tuple[LegacyFeeTruthMigrationRow, ...],
) -> _Plan:
    if type(rows) is not tuple or not rows:
        raise_business_error(
            "LEGACY_FEE_TRUTH_ROWS_INVALID",
            "Legacy fee truth rows are invalid",
            status_code=409,
        )
    if any(type(row) is not LegacyFeeTruthMigrationRow for row in rows):
        raise_business_error(
            "LEGACY_FEE_TRUTH_ROWS_INVALID",
            "Legacy fee truth rows are invalid",
            status_code=409,
        )
    ordered = tuple(sorted(rows, key=_row_order_key))
    identities = [(row.fee_item_id, row.gov_payment_id) for row in ordered]
    if len(identities) != len(set(identities)):
        raise_business_error(
            "LEGACY_FEE_TRUTH_ROWS_CONTRADICTORY",
            "Legacy fee truth rows are contradictory",
            status_code=409,
        )
    input_payload = {
        "rows": [_row_input(row) for row in ordered],
        "schema": "FPMS_LEGACY_FEE_TRUTH_INPUT_V1",
    }
    planned_draft_links: set[tuple[str, str]] = set()
    planned_item_lines: dict[str, str] = {}
    planned = tuple(
        _plan_row(
            transaction,
            row,
            planned_draft_links=planned_draft_links,
            planned_item_lines=planned_item_lines,
        )
        for row in ordered
    )
    plan_payload = {
        "input_sha256": _digest(input_payload),
        "rows": [
            {
                "add_draft_link": row.add_draft_link,
                "add_payment_link": row.add_payment_link,
                "result": {
                    "classification": row.result.classification,
                    "fee_item_id": row.result.fee_item_id,
                    "gov_payment_id": row.result.gov_payment_id,
                    "obligation_line_id": row.result.obligation_line_id,
                    "planned_writes": row.result.planned_writes,
                },
            }
            for row in planned
        ],
        "schema": "FPMS_LEGACY_FEE_TRUTH_PLAN_V1",
    }
    return _Plan(
        input_sha256=_digest(input_payload),
        plan_sha256=_digest(plan_payload),
        rows=planned,
    )


def _link_result(plan: _Plan) -> LegacyFeeTruthLinkResult:
    results = tuple(row.result for row in plan.rows)
    output_payload = {
        "input_sha256": plan.input_sha256,
        "plan_sha256": plan.plan_sha256,
        "rows": [
            {
                "classification": row.classification,
                "fee_item_id": row.fee_item_id,
                "gov_payment_id": row.gov_payment_id,
                "obligation_line_id": row.obligation_line_id,
                "planned_writes": row.planned_writes,
            }
            for row in results
        ],
        "schema": "FPMS_LEGACY_FEE_TRUTH_RESULT_V1",
    }
    return LegacyFeeTruthLinkResult(
        scanned=len(results),
        linked=sum(row.classification == "LINKED" for row in results),
        unchanged=sum(row.classification == "UNCHANGED" for row in results),
        invalid=sum(row.classification == "INVALID" for row in results),
        unmatched=sum(row.classification == "UNMATCHED" for row in results),
        ambiguous=sum(row.classification == "AMBIGUOUS" for row in results),
        planned_writes=sum(row.planned_writes for row in results),
        input_sha256=plan.input_sha256,
        plan_sha256=plan.plan_sha256,
        output_sha256=_digest(output_payload),
        rows=results,
    )


def link_legacy_fee_truth(
    *,
    transaction: Session,
    rows: tuple[LegacyFeeTruthMigrationRow, ...],
    dry_run: bool,
    expected_plan_sha256: str | None = None,
) -> LegacyFeeTruthLinkResult:
    with transaction.no_autoflush:
        plan = _build_plan(transaction, rows)
    result = _link_result(plan)
    if dry_run:
        return result
    if type(expected_plan_sha256) is not str or expected_plan_sha256 != plan.plan_sha256:
        raise_business_error(
            "LEGACY_FEE_TRUTH_PLAN_STALE",
            "Legacy fee truth plan is stale",
            status_code=409,
        )
    unresolved = tuple(
        row.result.classification
        for row in plan.rows
        if row.result.classification not in {"LINKED", "UNCHANGED"}
    )
    if unresolved:
        raise_business_error(
            "LEGACY_FEE_TRUTH_PLAN_UNRESOLVED",
            "Legacy fee truth plan contains unresolved rows",
            status_code=409,
        )

    for planned in plan.rows:
        if planned.obligation_line_id is None:
            continue
        if planned.add_draft_link:
            transaction.add(
                FeeObligationDraftItemLink(
                    id=str(uuid4()),
                    obligation_line_id=planned.obligation_line_id,
                    fee_item_id=planned.source.fee_item_id,
                )
            )
        if planned.add_payment_link:
            transaction.add(
                FeeObligationPaymentEvidenceLink(
                    id=str(uuid4()),
                    obligation_line_id=planned.obligation_line_id,
                    gov_payment_id=planned.source.gov_payment_id,
                )
            )
    transaction.flush()
    return result
