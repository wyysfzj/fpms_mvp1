from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any, Literal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import Case
from app.modules.fees.enums import FeeDraftStatus, FeeType
from app.modules.fees.models import FeeDraft, FeeItem, FeeRate
from app.modules.fees.schemas import (
    FeeDraftCreateIn,
    FeeDraftUpdateIn,
    FeeItemCreateIn,
    FeeItemUpdateIn,
    FeeRateCreateIn,
    FeeRateUpdateIn,
)
from app.modules.masterdata.clients.models import Client

logger = logging.getLogger(__name__)

_CONSULTING_CASE_TYPES = {"CONSULTING", "SEARCH"}
_CONSULTING_DRAFT_TYPE_MAP = {
    "CONSULTING": "CONSULT_FEE",
    "SEARCH": "SEARCH_FEE",
}
_CONSULTING_MODES = {"FIXED", "HOURLY", "HYBRID"}
_MONEY_QUANT = Decimal("0.01")
_QTY_QUANT = Decimal("0.0001")


def _normalize_optional_text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None


def _normalize_required_text(value: str | None, field_name: str) -> str:
    normalized = _normalize_optional_text(value)
    if not normalized:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    return normalized


def _to_decimal(
    value: Decimal | int | float | str | None,
    *,
    field_name: str,
    required: bool = True,
) -> Decimal:
    if value is None:
        if required:
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                f"{field_name} is required",
                status_code=400,
            )
        return Decimal("0")
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            f"{field_name} must be a decimal value",
            status_code=400,
        )


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)


def _quantize_quantity(value: Decimal) -> Decimal:
    return value.quantize(_QTY_QUANT, rounding=ROUND_HALF_UP)


def list_fee_drafts(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> tuple[list[FeeDraft], int]:
    stmt = select(FeeDraft)

    case_id = filters.get("case_id")
    client_id = filters.get("client_id")
    status = filters.get("status")

    if case_id:
        stmt = stmt.where(FeeDraft.case_id == case_id)
    if client_id:
        stmt = stmt.where(FeeDraft.client_id == client_id)
    if status:
        stmt = stmt.where(FeeDraft.status == status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(FeeDraft.updated_at.desc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_fee_draft(db: Session, *, draft_id: str) -> FeeDraft:
    draft = db.execute(select(FeeDraft).where(FeeDraft.id == draft_id)).scalar_one_or_none()
    if not draft:
        raise_business_error("FEE_DRAFT_NOT_FOUND", "Fee draft not found", status_code=404)
    return draft


def create_fee_draft(db: Session, *, data: FeeDraftCreateIn, actor_id: str | None) -> FeeDraft:
    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if data.client_id:
        client = db.execute(select(Client).where(Client.id == data.client_id)).scalar_one_or_none()
        if not client:
            raise_business_error("CLIENT_NOT_FOUND", "Client not found", status_code=404)

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=data.case_id,
        client_id=data.client_id,
        draft_type=data.draft_type or "GENERIC",
        currency=data.currency,
        status=FeeDraftStatus.OPEN.value,
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def update_fee_draft(
    db: Session,
    *,
    draft_id: str,
    data: FeeDraftUpdateIn,
    actor_id: str | None,
) -> FeeDraft:
    draft = get_fee_draft(db, draft_id=draft_id)
    updates = data.model_dump(exclude_unset=True)
    updates.pop("status", None)

    for field, value in updates.items():
        setattr(draft, field, value)

    db.commit()
    db.refresh(draft)
    return draft


def recalc_fee_draft_totals(db: Session, *, draft_id: str) -> None:
    draft = get_fee_draft(db, draft_id=draft_id)

    rows = db.execute(
        select(FeeItem.fee_type, func.coalesce(func.sum(FeeItem.amount), 0))
        .where(FeeItem.draft_id == draft_id)
        .group_by(FeeItem.fee_type)
    ).all()

    totals: dict[str, Decimal] = {
        FeeType.GOV.value: Decimal("0"),
        FeeType.SERVICE.value: Decimal("0"),
        FeeType.MISC.value: Decimal("0"),
    }
    for fee_type, total in rows:
        if fee_type in totals:
            totals[fee_type] = Decimal(total)

    draft.total_gov = totals[FeeType.GOV.value]
    draft.total_service = totals[FeeType.SERVICE.value]
    draft.total_misc = totals[FeeType.MISC.value]
    draft.amount = draft.total_gov + draft.total_service + draft.total_misc

    db.commit()


def assert_draft_unlocked(draft: FeeDraft) -> None:
    if draft.status == FeeDraftStatus.LOCKED.value:
        raise_business_error("FEE_DRAFT_LOCKED", "Fee draft is locked", status_code=409)


def lock_fee_draft(
    db: Session,
    *,
    draft_id: str,
    actor_id: str | None,
    remark: str | None = None,
) -> None:
    draft = get_fee_draft(db, draft_id=draft_id)
    if draft.status == FeeDraftStatus.LOCKED.value:
        raise_business_error(
            "FEE_DRAFT_ALREADY_LOCKED",
            "Fee draft already locked",
            status_code=409,
        )
    draft.status = FeeDraftStatus.LOCKED.value
    db.commit()


def unlock_fee_draft(
    db: Session,
    *,
    draft_id: str,
    actor_id: str | None,
    remark: str | None = None,
) -> None:
    draft = get_fee_draft(db, draft_id=draft_id)
    if draft.status != FeeDraftStatus.LOCKED.value:
        raise_business_error(
            "FEE_DRAFT_NOT_LOCKED",
            "Fee draft not locked",
            status_code=409,
        )
    draft.status = FeeDraftStatus.OPEN.value
    db.commit()


def add_fee_item(
    db: Session,
    *,
    draft_id: str,
    data: FeeItemCreateIn,
    actor_id: str | None,
) -> FeeItem:
    draft = get_fee_draft(db, draft_id=draft_id)
    assert_draft_unlocked(draft)

    rate = db.execute(select(FeeRate).where(FeeRate.id == data.rate_id)).scalar_one_or_none()
    if not rate:
        raise_business_error("FEE_RATE_NOT_FOUND", "Fee rate not found", status_code=404)
    if getattr(rate, "enabled", True) is False:
        raise_business_error("FEE_RATE_DISABLED", "Fee rate disabled", status_code=400)
    if draft.currency != rate.currency:
        raise_business_error(
            "FEE_CURRENCY_MISMATCH",
            "Fee draft currency does not match rate currency",
            status_code=400,
        )

    quantity = data.quantity if data.quantity is not None else Decimal("1")
    unit_price = data.unit_price if data.unit_price is not None else rate.default_amount
    if unit_price is None:
        unit_price = Decimal("0")
    amount = Decimal(quantity) * Decimal(unit_price)

    item = FeeItem(
        id=str(uuid4()),
        draft_id=draft_id,
        case_id=draft.case_id,
        rate_id=rate.id,
        fee_code=rate.fee_code,
        fee_name=rate.fee_name,
        fee_type=rate.fee_type,
        year_no=data.year_no,
        quantity=quantity,
        unit_price=unit_price,
        amount=amount,
        remark=data.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    recalc_fee_draft_totals(db, draft_id=draft_id)
    return item


def update_fee_item(
    db: Session,
    *,
    draft_id: str,
    item_id: str,
    data: FeeItemUpdateIn,
    actor_id: str | None,
) -> FeeItem:
    draft = get_fee_draft(db, draft_id=draft_id)
    assert_draft_unlocked(draft)

    item = db.execute(select(FeeItem).where(FeeItem.id == item_id)).scalar_one_or_none()
    if not item or item.draft_id != draft_id:
        raise_business_error("FEE_ITEM_NOT_FOUND", "Fee item not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    quantity = item.quantity if item.quantity is not None else Decimal("1")
    unit_price = item.unit_price if item.unit_price is not None else Decimal("0")
    if "quantity" in updates or "unit_price" in updates:
        item.amount = Decimal(quantity) * Decimal(unit_price)

    db.commit()
    db.refresh(item)
    recalc_fee_draft_totals(db, draft_id=draft_id)
    return item


def list_fee_rates(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> tuple[list[FeeRate], int]:
    stmt = select(FeeRate)

    fee_code = filters.get("fee_code")
    fee_type = filters.get("fee_type")
    currency = filters.get("currency")
    enabled = filters.get("enabled")

    if fee_code:
        stmt = stmt.where(FeeRate.fee_code == fee_code)
    if fee_type:
        stmt = stmt.where(FeeRate.fee_type == fee_type)
    if currency:
        stmt = stmt.where(FeeRate.currency == currency)
    if enabled is not None:
        stmt = stmt.where(FeeRate.enabled == enabled)

    rate_group = filters.get("rate_group")
    country_code = filters.get("country_code")
    case_type = filters.get("case_type")
    patent_category = filters.get("patent_category")
    calc_mode = filters.get("calc_mode")

    if rate_group:
        stmt = stmt.where(FeeRate.rate_group == rate_group)
    if country_code:
        stmt = stmt.where(FeeRate.country_code == country_code)
    if case_type:
        stmt = stmt.where(FeeRate.case_type == case_type)
    if patent_category:
        stmt = stmt.where(FeeRate.patent_category == patent_category)
    if calc_mode:
        stmt = stmt.where(FeeRate.calc_mode == calc_mode)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(FeeRate.fee_code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def create_fee_rate(db: Session, *, data: FeeRateCreateIn, actor_id: str | None) -> FeeRate:
    rate = FeeRate(
        id=str(uuid4()),
        fee_code=data.fee_code,
        fee_name=data.fee_name,
        fee_type=data.fee_type,
        currency=data.currency,
        default_amount=data.default_amount,
        enabled=data.enabled if data.enabled is not None else True,
        rate_group=data.rate_group,
        country_code=data.country_code,
        case_type=data.case_type,
        patent_category=data.patent_category,
        calc_mode=data.calc_mode.value if data.calc_mode else None,
        calc_params=data.calc_params,
        allow_reduction=data.allow_reduction,
        effective_from=data.effective_from,
        effective_to=data.effective_to,
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


def update_fee_rate(
    db: Session,
    *,
    rate_id: str,
    data: FeeRateUpdateIn,
    actor_id: str | None,
) -> FeeRate:
    rate = db.execute(select(FeeRate).where(FeeRate.id == rate_id)).scalar_one_or_none()
    if not rate:
        raise_business_error("FEE_RATE_NOT_FOUND", "Fee rate not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(rate, field, value)

    db.commit()
    db.refresh(rate)
    return rate


def _normalize_hourly_lines(
    hourly_lines: list[dict[str, Any]] | None,
    *,
    mode: str,
    case_type: str,
) -> list[dict[str, Any]]:
    if mode == "FIXED":
        if hourly_lines:
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "hourly_lines are not allowed for FIXED mode",
                status_code=400,
            )
        return []

    if not hourly_lines:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            "hourly_lines are required for HOURLY/HYBRID modes",
            status_code=400,
        )

    normalized_lines: list[dict[str, Any]] = []
    for index, line in enumerate(hourly_lines, start=1):
        if not isinstance(line, dict):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "hourly_lines must contain objects",
                status_code=400,
            )

        fee_code = _normalize_required_text(line.get("fee_code"), f"hourly_lines[{index}].fee_code")
        fee_name = _normalize_required_text(line.get("fee_name"), f"hourly_lines[{index}].fee_name")
        hours = _to_decimal(line.get("hours"), field_name=f"hourly_lines[{index}].hours")
        hourly_rate = _to_decimal(
            line.get("hourly_rate"), field_name=f"hourly_lines[{index}].hourly_rate"
        )
        if hours <= Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                f"hourly_lines[{index}].hours must be greater than 0",
                status_code=400,
            )
        if hourly_rate < Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                f"hourly_lines[{index}].hourly_rate must be greater than or equal to 0",
                status_code=400,
            )

        qty = _quantize_quantity(hours)
        price = _quantize_money(hourly_rate)
        amount = _quantize_money(qty * price)
        trace_key = _normalize_optional_text(line.get("trace_key")) or f"{case_type}:hourly:{index}"
        input_remark = _normalize_optional_text(line.get("remark"))
        trace_remark = f"mode={mode};trace_key={trace_key};source=HOURLY"
        remark = f"{input_remark} | {trace_remark}" if input_remark else trace_remark

        normalized_lines.append(
            {
                "fee_code": fee_code,
                "fee_name": fee_name,
                "fee_type": FeeType.SERVICE.value,
                "quantity": qty,
                "unit_price": price,
                "amount": amount,
                "trace_key": trace_key,
                "remark": remark,
            }
        )

    return normalized_lines


def _normalize_misc_lines(
    misc_lines: list[dict[str, Any]] | None,
    *,
    mode: str,
) -> list[dict[str, Any]]:
    if not misc_lines:
        return []

    normalized_lines: list[dict[str, Any]] = []
    for index, line in enumerate(misc_lines, start=1):
        if not isinstance(line, dict):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "misc_lines must contain objects",
                status_code=400,
            )

        fee_code = _normalize_required_text(line.get("fee_code"), f"misc_lines[{index}].fee_code")
        fee_name = _normalize_required_text(line.get("fee_name"), f"misc_lines[{index}].fee_name")
        amount = _quantize_money(
            _to_decimal(line.get("amount"), field_name=f"misc_lines[{index}].amount")
        )
        if amount < Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                f"misc_lines[{index}].amount must be greater than or equal to 0",
                status_code=400,
            )

        quantity = _quantize_quantity(Decimal("1"))
        unit_price = amount
        trace_key = _normalize_optional_text(line.get("trace_key")) or f"misc:{index}"
        input_remark = _normalize_optional_text(line.get("remark"))
        trace_remark = f"mode={mode};trace_key={trace_key};source=MISC"
        remark = f"{input_remark} | {trace_remark}" if input_remark else trace_remark

        normalized_lines.append(
            {
                "fee_code": fee_code,
                "fee_name": fee_name,
                "fee_type": FeeType.MISC.value,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount,
                "trace_key": trace_key,
                "remark": remark,
            }
        )

    return normalized_lines


def generate_consulting_fee_draft_strategy(
    db: Session,
    *,
    case_id: str,
    mode: Literal["FIXED", "HOURLY", "HYBRID"] | str,
    currency: str | None = None,
    fixed_fee: Decimal | int | float | str | None = None,
    hourly_lines: list[dict[str, Any]] | None = None,
    misc_lines: list[dict[str, Any]] | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    normalized_case_id = _normalize_required_text(case_id, "case_id")
    normalized_mode = _normalize_required_text(mode, "mode").upper()
    if normalized_mode not in _CONSULTING_MODES:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            "mode must be one of FIXED, HOURLY, HYBRID",
            status_code=400,
        )

    case = db.execute(select(Case).where(Case.id == normalized_case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    case_type = _normalize_required_text(case.case_type, "case.case_type").upper()
    if case_type not in _CONSULTING_CASE_TYPES:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            "case_type must be CONSULTING or SEARCH",
            status_code=400,
        )

    normalized_currency = (_normalize_optional_text(currency) or "CNY").upper()
    if not normalized_currency:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            "currency is required",
            status_code=400,
        )

    draft_type = _CONSULTING_DRAFT_TYPE_MAP[case_type]

    conflict_draft = db.execute(
        select(FeeDraft.id)
        .where(
            FeeDraft.case_id == case.id,
            FeeDraft.draft_type == draft_type,
            func.upper(FeeDraft.currency) == normalized_currency,
            FeeDraft.status == FeeDraftStatus.OPEN.value,
        )
        .order_by(FeeDraft.created_at.desc(), FeeDraft.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if conflict_draft:
        raise_business_error(
            "FEE_DRAFT_CONFLICT",
            "Open fee draft already exists for same case/type/currency",
            details={"draft_id": conflict_draft},
            status_code=409,
        )

    lines: list[dict[str, Any]] = []
    case_prefix = "CONSULT" if case_type == "CONSULTING" else "SEARCH"
    fixed_fee_dec = _to_decimal(fixed_fee, field_name="fixed_fee", required=False)

    if normalized_mode == "FIXED":
        if fixed_fee_dec <= Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "fixed_fee must be greater than 0 for FIXED mode",
                status_code=400,
            )
        trace_key = f"{case_prefix.lower()}:fixed"
        lines.append(
            {
                "fee_code": f"{case_prefix}_FIXED",
                "fee_name": f"{case_prefix.title()} fixed service",
                "fee_type": FeeType.SERVICE.value,
                "quantity": _quantize_quantity(Decimal("1")),
                "unit_price": _quantize_money(fixed_fee_dec),
                "amount": _quantize_money(fixed_fee_dec),
                "trace_key": trace_key,
                "remark": f"mode={normalized_mode};trace_key={trace_key};source=FIXED",
            }
        )

    hourly_service_lines = _normalize_hourly_lines(
        hourly_lines,
        mode=normalized_mode,
        case_type=case_prefix.lower(),
    )
    if normalized_mode == "HYBRID":
        if fixed_fee_dec < Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "fixed_fee must be greater than or equal to 0 for HYBRID mode",
                status_code=400,
            )
        if fixed_fee_dec > Decimal("0"):
            trace_key = f"{case_prefix.lower()}:hybrid_fixed"
            lines.append(
                {
                    "fee_code": f"{case_prefix}_FIXED",
                    "fee_name": f"{case_prefix.title()} fixed service",
                    "fee_type": FeeType.SERVICE.value,
                    "quantity": _quantize_quantity(Decimal("1")),
                    "unit_price": _quantize_money(fixed_fee_dec),
                    "amount": _quantize_money(fixed_fee_dec),
                    "trace_key": trace_key,
                    "remark": f"mode={normalized_mode};trace_key={trace_key};source=FIXED",
                }
            )

    lines.extend(hourly_service_lines)
    lines.extend(_normalize_misc_lines(misc_lines, mode=normalized_mode))

    if normalized_mode == "HYBRID":
        hybrid_total = _quantize_money(sum((line["amount"] for line in lines), start=Decimal("0")))
        if hybrid_total <= Decimal("0"):
            raise_business_error(
                "CONSULTING_FEE_INVALID",
                "HYBRID mode total amount must be greater than 0",
                status_code=400,
            )

    if not lines:
        raise_business_error(
            "CONSULTING_FEE_INVALID",
            "No fee lines were generated",
            status_code=400,
        )

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=case.id,
        client_id=case.client_id,
        draft_type=draft_type,
        currency=normalized_currency,
        status=FeeDraftStatus.OPEN.value,
        total_gov=Decimal("0"),
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=Decimal("0"),
    )
    db.add(draft)
    db.flush()

    created_items: list[FeeItem] = []
    for line in lines:
        item = FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=case.id,
            rate_id=None,
            fee_code=line["fee_code"],
            fee_name=line["fee_name"],
            fee_type=line["fee_type"],
            quantity=line["quantity"],
            unit_price=line["unit_price"],
            amount=line["amount"],
            remark=line["remark"],
            created_by=actor_id,
            updated_by=actor_id,
        )
        db.add(item)
        created_items.append(item)

    db.flush()
    recalc_fee_draft_totals(db, draft_id=draft.id)
    draft = get_fee_draft(db, draft_id=draft.id)

    output_items: list[dict[str, Any]] = []
    for item, line in zip(created_items, lines, strict=True):
        output_items.append(
            {
                "item_id": item.id,
                "fee_code": item.fee_code,
                "fee_name": item.fee_name,
                "fee_type": item.fee_type,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "amount": item.amount,
                "trace_key": line["trace_key"],
                "remark": item.remark,
            }
        )

    return {
        "draft_id": draft.id,
        "draft_type": draft.draft_type,
        "mode": normalized_mode,
        "currency": draft.currency,
        "totals": {
            "total_gov": draft.total_gov,
            "total_service": draft.total_service,
            "total_misc": draft.total_misc,
            "amount": draft.amount,
        },
        "items": output_items,
        "created_line_count": len(output_items),
    }


def calculate_fee_amount(rate: FeeRate, case: Case | None = None) -> Decimal:
    """Calculate fee amount based on rate's calc_mode.

    Currently only FIXED mode is implemented.
    Other modes (PER_CLAIM, PER_PAGE, TIER) return default_amount with a TODO log.
    """
    amount = rate.default_amount if rate.default_amount is not None else Decimal("0")
    calc_mode = getattr(rate, "calc_mode", None) or "FIXED"

    if calc_mode == "FIXED":
        return amount

    logger.warning(
        "calculate_fee_amount: calc_mode=%s not yet implemented for rate=%s, "
        "returning default_amount=%s",
        calc_mode,
        rate.fee_code,
        amount,
    )
    return amount
