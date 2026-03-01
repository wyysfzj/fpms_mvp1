from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.models import Case
from app.modules.expenses.models import Expense

_ALLOWED_CATEGORIES = {"SEARCH_DB", "TRANSLATION", "TRANSPORT", "OTHER"}
_DEFAULT_CURRENCY = "CNY"
_DEFAULT_STATUS = "DRAFT"
_MONEY_QUANT = Decimal("0.01")


def _normalize_required_text(value: str | None, field_name: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise_business_error(
            "EXPENSE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    normalized = (value or "").strip()
    return normalized or None


def _to_decimal(value: Decimal | int | float | str | None, field_name: str) -> Decimal:
    if value is None:
        raise_business_error(
            "EXPENSE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise_business_error(
            "EXPENSE_INVALID",
            f"{field_name} must be a decimal value",
            status_code=400,
        )


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)


def _build_expense_filters(
    *,
    case_id: str | None = None,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    currency: str | None = None,
    status: str | None = None,
    q: str | None = None,
) -> list[Any]:
    if date_from and date_to and date_from > date_to:
        raise_business_error(
            "EXPENSE_INVALID",
            "date_from must be less than or equal to date_to",
            status_code=400,
        )

    filters: list[Any] = []

    normalized_case_id = _normalize_optional_text(case_id)
    if normalized_case_id:
        filters.append(Expense.case_id == normalized_case_id)

    normalized_category = _normalize_optional_text(category)
    if normalized_category:
        category_upper = normalized_category.upper()
        if category_upper not in _ALLOWED_CATEGORIES:
            raise_business_error(
                "EXPENSE_INVALID",
                "category must be one of SEARCH_DB, TRANSLATION, TRANSPORT, OTHER",
                status_code=400,
            )
        filters.append(Expense.category == category_upper)

    if date_from is not None:
        filters.extend((Expense.expense_date.is_not(None), Expense.expense_date >= date_from))
    if date_to is not None:
        filters.extend((Expense.expense_date.is_not(None), Expense.expense_date <= date_to))

    normalized_currency = _normalize_optional_text(currency)
    if normalized_currency:
        filters.append(
            func.upper(func.coalesce(Expense.currency, "")) == normalized_currency.upper()
        )

    normalized_status = _normalize_optional_text(status)
    if normalized_status:
        filters.append(func.upper(func.coalesce(Expense.status, "")) == normalized_status.upper())

    normalized_q = _normalize_optional_text(q)
    if normalized_q:
        pattern = f"%{normalized_q.lower()}%"
        filters.append(
            or_(
                func.lower(func.coalesce(Expense.expense_no, "")).like(pattern),
                func.lower(func.coalesce(Expense.vendor_name, "")).like(pattern),
                func.lower(func.coalesce(Expense.remark, "")).like(pattern),
            )
        )

    return filters


def list_expenses(
    db: Session,
    *,
    case_id: str | None = None,
    category: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    currency: str | None = None,
    status: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
    include_stats: bool = False,
) -> tuple[list[Expense], int, dict[str, Any] | None]:
    filters = _build_expense_filters(
        case_id=case_id,
        category=category,
        date_from=date_from,
        date_to=date_to,
        currency=currency,
        status=status,
        q=q,
    )

    base_stmt = select(Expense).where(*filters)
    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    offset = (page - 1) * page_size
    items = (
        db.execute(
            base_stmt.order_by(Expense.expense_date.desc(), Expense.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    if not include_stats:
        return items, total, None

    rows = db.execute(
        select(
            Expense.category,
            func.count(Expense.id),
            func.coalesce(func.sum(Expense.amount), 0),
        )
        .where(*filters)
        .group_by(Expense.category)
        .order_by(Expense.category.asc())
    ).all()

    count_by_category: dict[str, int] = {}
    sum_by_category: dict[str, Decimal] = {}
    sum_total = Decimal("0")
    for category_value, count_value, amount_sum in rows:
        category_key = str(category_value or "OTHER")
        count_by_category[category_key] = int(count_value or 0)
        normalized_amount = _quantize_money(_to_decimal(amount_sum, f"sum[{category_key}]"))
        sum_by_category[category_key] = normalized_amount
        sum_total += normalized_amount

    stats: dict[str, Any] = {
        "count_by_category": count_by_category,
        "sum_by_category": sum_by_category,
        "count_total": total,
        "sum_total": _quantize_money(sum_total),
    }
    return items, total, stats


def create_expense(
    db: Session,
    *,
    case_id: str | None,
    category: str | None,
    expense_date: date | None,
    amount: Decimal | int | float | str | None,
    client_id: str | None = None,
    expense_no: str | None = None,
    vendor_name: str | None = None,
    currency: str | None = None,
    tax_amount: Decimal | int | float | str | None = None,
    remark: str | None = None,
    actor_id: str | None = None,
) -> Expense:
    normalized_case_id = _normalize_required_text(case_id, "case_id")

    case_exists = db.execute(
        select(Case.id).where(Case.id == normalized_case_id)
    ).scalar_one_or_none()
    if not case_exists:
        raise_business_error(
            "CASE_NOT_FOUND",
            "Case not found",
            status_code=404,
        )

    normalized_category = _normalize_required_text(category, "category").upper()
    if normalized_category not in _ALLOWED_CATEGORIES:
        raise_business_error(
            "EXPENSE_INVALID",
            "category must be one of SEARCH_DB, TRANSLATION, TRANSPORT, OTHER",
            status_code=400,
        )

    if expense_date is None:
        raise_business_error(
            "EXPENSE_INVALID",
            "expense_date is required",
            status_code=400,
        )

    normalized_amount = _quantize_money(_to_decimal(amount, "amount"))
    if normalized_amount <= Decimal("0"):
        raise_business_error(
            "EXPENSE_INVALID",
            "amount must be greater than 0",
            status_code=400,
        )

    normalized_tax_amount: Decimal | None = None
    if tax_amount is not None:
        normalized_tax_amount = _quantize_money(_to_decimal(tax_amount, "tax_amount"))
        if normalized_tax_amount < Decimal("0"):
            raise_business_error(
                "EXPENSE_INVALID",
                "tax_amount must be greater than or equal to 0",
                status_code=400,
            )

    normalized_currency = (_normalize_optional_text(currency) or _DEFAULT_CURRENCY).upper()
    normalized_client_id = _normalize_optional_text(client_id)
    normalized_vendor_name = _normalize_optional_text(vendor_name)
    normalized_remark = _normalize_optional_text(remark)
    normalized_expense_no = _normalize_optional_text(expense_no)

    expense = Expense(
        case_id=normalized_case_id,
        client_id=normalized_client_id,
        expense_no=normalized_expense_no,
        category=normalized_category,
        vendor_name=normalized_vendor_name,
        expense_date=expense_date,
        currency=normalized_currency,
        amount=normalized_amount,
        tax_amount=normalized_tax_amount,
        status=_DEFAULT_STATUS,
        remark=normalized_remark,
        created_by=actor_id,
        updated_by=actor_id,
    )

    db.add(expense)
    db.flush()

    if not expense.expense_no:
        expense.expense_no = f"EXP-{expense.expense_date:%Y%m%d}-{expense.id:06d}"

    db.commit()
    db.refresh(expense)
    return expense
