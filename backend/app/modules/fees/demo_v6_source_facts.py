from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.demo_service import (
    _service_source_rows,
    _validated_service_adjustment_activity,
)
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
)
from app.modules.fees.obligation_service import get_fee_obligation
from app.modules.grant_fees.demo_official_fee import preview_grant_official_fees


@dataclass(frozen=True, slots=True)
class DemoV6DraftSourceFactLine:
    current_item_id: str
    obligation_line_id: str
    fee_code: str
    fee_name: str
    quantity: int
    unit_price: Decimal
    amount: Decimal
    source_authority: str
    source_ref: str
    source_version: str
    effective_date: date | None
    source_sha256: str
    activation_status: str
    adjustable: bool
    adjustment_activity_id: str | None
    adjustment_reason: str | None
    adjustment_before_digest: str | None
    adjustment_after_digest: str | None


@dataclass(frozen=True, slots=True)
class DemoV6DraftSourceFacts:
    draft_id: str
    draft_status: str
    fee_domain: str
    lines: tuple[DemoV6DraftSourceFactLine, ...]


def _invalid() -> None:
    raise BusinessError(
        code="DEMO_V6_DRAFT_SOURCE_FACTS_INVALID",
        message="费用草单来源事实无效",
        status_code=409,
    )


def _payload(activity: CaseActivityEvent) -> dict[str, object]:
    try:
        payload = json.loads(activity.payload_json)
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (RecursionError, TypeError, ValueError):
        _invalid()
    if type(payload) is not dict or canonical != activity.payload_json:
        _invalid()
    return payload


def _draft_rows(
    draft: FeeDraft,
    transaction: Session,
) -> tuple[
    tuple[FeeItem, FeeObligationDraftItemLink, FeeObligationLine], ...
]:
    items = tuple(
        transaction.scalars(
            select(FeeItem)
            .where(FeeItem.draft_id == draft.id)
            .order_by(FeeItem.fee_code, FeeItem.id)
        )
    )
    links = tuple(
        transaction.scalars(
            select(FeeObligationDraftItemLink).where(
                FeeObligationDraftItemLink.fee_item_id.in_(tuple(item.id for item in items))
            )
        )
    )
    link_by_item = {link.fee_item_id: link for link in links}
    lines = tuple(
        transaction.scalars(
            select(FeeObligationLine).where(
                FeeObligationLine.id.in_(tuple(link.obligation_line_id for link in links))
            )
        )
    )
    line_by_id = {line.id: line for line in lines}
    if not items or len(items) != len(links) or len(links) != len(lines):
        _invalid()
    try:
        return tuple(
            (item, link_by_item[item.id], line_by_id[link_by_item[item.id].obligation_line_id])
            for item in items
        )
    except KeyError:
        _invalid()


def _service_facts(
    draft: FeeDraft,
    header: FeeObligation,
    rows: tuple[tuple[FeeItem, FeeObligationDraftItemLink, FeeObligationLine], ...],
    transaction: Session,
) -> DemoV6DraftSourceFacts:
    current_source = transaction.get(CaseActivityEvent, header.source_activity_id)
    if current_source is None:
        _invalid()
    adjustment = None
    adjustment_payload = None
    if current_source.activity_type == "DEMO_SERVICE_DRAFT_ADJUSTED":
        adjustment = current_source
        try:
            adjustment_payload, validated_adjustment = (
                _validated_service_adjustment_activity(transaction, adjustment)
            )
        except BusinessError:
            _invalid()
        if (
            validated_adjustment.draft_id != draft.id
            or validated_adjustment.superseding_obligation_id != header.id
        ):
            _invalid()
        source_id = adjustment_payload.get("source_activity_id")
        if type(source_id) is not str:
            _invalid()
        current_source = transaction.get(CaseActivityEvent, source_id)
    if current_source is None:
        _invalid()
    try:
        current_source, validated_rows = _service_source_rows(
            transaction,
            current_source.id,
            case_id=header.case_id,
        )
    except BusinessError:
        _invalid()
    source_rows = list(validated_rows)
    validated_payload = _payload(current_source)
    source_authority = validated_payload.get("authority_classification")
    if type(source_authority) is not str:
        _invalid()
    source_by_code = {
        row.get("item_code"): row for row in source_rows if type(row) is dict
    }
    if len(source_by_code) != len(source_rows) or set(source_by_code) != {
        line.fee_code for _item, _link, line in rows
    }:
        _invalid()
    adjusted_by_code = {}
    if adjustment_payload is not None:
        after_rows = adjustment_payload.get("after_lines")
        if type(after_rows) is not list:
            _invalid()
        adjusted_by_code = {
            row.get("fee_code"): row for row in after_rows if type(row) is dict
        }
        if len(adjusted_by_code) != len(after_rows) or set(adjusted_by_code) != set(
            source_by_code
        ):
            _invalid()
    facts: list[DemoV6DraftSourceFactLine] = []
    for item, link, line in rows:
        source = source_by_code.get(line.fee_code)
        if type(source) is not dict:
            _invalid()
        adjusted = adjusted_by_code.get(line.fee_code)
        quantity = source.get("quantity") if adjusted is None else adjusted.get("quantity")
        if type(quantity) is not int or quantity <= 0:
            _invalid()
        try:
            unit_price = Decimal(str(source["unit_price"]))
            expected = unit_price * quantity
        except (InvalidOperation, KeyError, TypeError, ValueError):
            _invalid()
        if (
            item.fee_type != "SERVICE"
            or item.fee_code != line.fee_code
            or line.fee_name != source.get("name_zh_cn")
            or item.fee_name != source.get("name_zh_cn")
            or item.amount != expected
            or (item.quantity is None) != (item.unit_price is None)
            or (
                item.quantity is not None
                and (
                    item.quantity != Decimal(quantity)
                    or item.unit_price != unit_price
                )
            )
            or line.payable_amount != expected
            or type(source.get("source_ref")) is not str
            or type(source.get("source_version")) is not str
            or type(source.get("source_sha256")) is not str
            or len(str(source.get("source_sha256"))) != 64
        ):
            _invalid()
        facts.append(
            DemoV6DraftSourceFactLine(
                current_item_id=item.id,
                obligation_line_id=link.obligation_line_id,
                fee_code=line.fee_code,
                fee_name=line.fee_name,
                quantity=quantity,
                unit_price=unit_price,
                amount=expected,
                source_authority=source_authority,
                source_ref=str(source.get("source_ref")),
                source_version=str(source.get("source_version")),
                effective_date=None,
                source_sha256=str(source.get("source_sha256")),
                activation_status="DIGEST_BOUND",
                adjustable=source.get("adjustable") is True,
                adjustment_activity_id=(None if adjustment is None else adjustment.id),
                adjustment_reason=(
                    None
                    if adjustment_payload is None
                    else str(adjustment_payload.get("reason"))
                ),
                adjustment_before_digest=(
                    None
                    if adjustment_payload is None
                    else str(adjustment_payload.get("before_digest"))
                ),
                adjustment_after_digest=(
                    None
                    if adjustment_payload is None
                    else str(adjustment_payload.get("after_digest"))
                ),
            )
        )
    return DemoV6DraftSourceFacts(draft.id, draft.status, "SERVICE", tuple(facts))


def _gov_facts(
    draft: FeeDraft,
    header: FeeObligation,
    rows: tuple[tuple[FeeItem, FeeObligationDraftItemLink, FeeObligationLine], ...],
    transaction: Session,
) -> DemoV6DraftSourceFacts:
    source = transaction.get(CaseActivityEvent, header.source_activity_id)
    if source is None or source.activity_type != "DEMO_GRANT_OFFICIAL_FEE_CONFIRMED":
        _invalid()
    payload = _payload(source)
    source_lines = payload.get("lines")
    if payload.get("schema") != "FPMS_DEMO_GRANT_OFFICIAL_FEE_CONFIRMED_V1" or type(
        source_lines
    ) is not list:
        _invalid()
    by_code = {row.get("fee_code"): row for row in source_lines if type(row) is dict}
    task_id = payload.get("grant_fee_task_id")
    if type(task_id) is not str:
        _invalid()
    try:
        preview = preview_grant_official_fees(
            transaction,
            grant_fee_task_id=task_id,
        )
    except BusinessError:
        _invalid()
    preview_by_code = {line.fee_code: line for line in preview.lines}
    if (
        payload.get("preview_digest") != preview.preview_digest
        or payload.get("rate_book_version") != preview.rate_book_version
        or payload.get("rate_book_sha256") != preview.rate_book_sha256
        or set(preview_by_code) != set(by_code)
        or set(by_code) != {line.fee_code for _item, _link, line in rows}
    ):
        _invalid()
    facts: list[DemoV6DraftSourceFactLine] = []
    for item, link, line in rows:
        source_line = by_code.get(line.fee_code)
        preview_line = preview_by_code.get(line.fee_code)
        if type(source_line) is not dict or preview_line is None:
            _invalid()
        quantity = source_line.get("quantity")
        if type(quantity) is not int or quantity <= 0:
            _invalid()
        try:
            amount = Decimal(str(source_line["confirmed_payable_amount"]))
            unit_price = amount / quantity
        except (InvalidOperation, KeyError, TypeError, ValueError, ZeroDivisionError):
            _invalid()
        if (
            item.fee_type != "GOV"
            or item.fee_code != line.fee_code
            or item.amount != amount
            or line.payable_amount != amount
            or preview_line.quantity != quantity
            or preview_line.payable_amount != amount
            or preview_line.unit_price != unit_price
        ):
            _invalid()
        facts.append(
            DemoV6DraftSourceFactLine(
                current_item_id=item.id,
                obligation_line_id=link.obligation_line_id,
                fee_code=line.fee_code,
                fee_name=line.fee_name,
                quantity=quantity,
                unit_price=unit_price,
                amount=amount,
                source_authority=preview.source_authority,
                source_ref=preview_line.source_reference,
                source_version=preview_line.source_version,
                effective_date=preview_line.effective_from,
                source_sha256=preview_line.rate_row_sha256,
                activation_status="APPROVED_ACTIVE",
                adjustable=False,
                adjustment_activity_id=None,
                adjustment_reason=None,
                adjustment_before_digest=None,
                adjustment_after_digest=None,
            )
        )
    return DemoV6DraftSourceFacts(draft.id, draft.status, "GOV", tuple(facts))


def get_demo_v6_draft_source_facts(
    draft_id: str,
    transaction: Session,
) -> DemoV6DraftSourceFacts:
    draft = transaction.get(FeeDraft, draft_id)
    if draft is None:
        raise BusinessError(
            code="FEE_DRAFT_NOT_FOUND",
            message="费用草单不存在",
            status_code=404,
        )
    rows = _draft_rows(draft, transaction)
    obligation_ids = {line.obligation_id for _item, _link, line in rows}
    if len(obligation_ids) != 1:
        _invalid()
    header = transaction.get(FeeObligation, obligation_ids.pop())
    if header is None:
        _invalid()
    get_fee_obligation(header.id, transaction)
    if header.fee_domain == "SERVICE":
        return _service_facts(draft, header, rows, transaction)
    if header.fee_domain == "GOV":
        return _gov_facts(draft, header, rows, transaction)
    _invalid()
