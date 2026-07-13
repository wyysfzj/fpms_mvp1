from __future__ import annotations

import json
import logging
from datetime import date as date_type
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any, Literal
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.billing.models import Bill, BillItem
from app.modules.cases.models import Case, T_CaseAgentSplit
from app.modules.fees.enums import FeeDraftStatus, FeeType
from app.modules.fees.models import FeeDraft, FeeItem, FeeRate
from app.modules.fees.schemas import (
    ApplyFeeDraftGenerateIn,
    FeeDraftCreateIn,
    FeeDraftUpdateIn,
    FeeItemCreateIn,
    FeeItemUpdateIn,
    FeeRateCreateIn,
    FeeRateUpdateIn,
    OfficialFeePreviewIn,
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
_APPLY_FEE_DRAFT_TYPE = "APPLY_FEE"
_APPLY_FEE_BASE_GOV_CODES_BY_PATENT_CATEGORY = {
    "INV": "CN_INV_APPLICATION_FEE",
    "UM": "CN_UM_APPLICATION_FEE",
    "DES": "CN_DES_APPLICATION_FEE",
}
_APPLY_FEE_EXCESS_CLAIM_CODE = "CN_EXCESS_CLAIM_FEE"
_APPLY_FEE_PUBLICATION_PRINT_CODE = "CN_PUBLICATION_PRINT_FEE"
_APPLY_FEE_SUBSTANTIVE_EXAM_CODE = "CN_SUBSTANTIVE_EXAM_FEE"
_FILING_ACCEPTED_TRIGGER_RULE = "提交申请/收到受理通知"
_FILING_ACCEPTED_DEADLINE_RULE = "申请日/受理通知起 2 个月"
_REEXAM_FEE_DRAFT_TYPE = "REEXAM_FEE"
_REEXAM_FEE_CODES_BY_PATENT_CATEGORY = {
    "INV": "CN_REEXAM_FEE_INV",
    "UM": "CN_REEXAM_FEE_UM",
    "DES": "CN_REEXAM_FEE_DES",
}
_REEXAM_REQUESTED_TRIGGER_RULE = "收到驳回决定且决定复审"
_REEXAM_REQUESTED_DEADLINE_RULE = "驳回决定起 3 个月"


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


def _normalize_report_text_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


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


def _draft_report_date_bounds(
    date_from: date_type | None,
    date_to: date_type | None,
) -> tuple[datetime | None, datetime | None]:
    lower_bound = (
        datetime.combine(date_from, datetime.min.time()) if date_from is not None else None
    )
    upper_bound = (
        datetime.combine(date_to + timedelta(days=1), datetime.min.time())
        if date_to is not None
        else None
    )
    return lower_bound, upper_bound


def _client_report_label(client: Client | None, client_id: str | None) -> tuple[str, str]:
    if client is not None:
        display_name = (client.name_cn or client.name_en or "").strip()
        if display_name:
            return client.id, display_name
    if client_id:
        return client_id, client_id
    return "UNASSIGNED", "未分配客户"


def _case_type_report_label(case: Case | None) -> tuple[str, str]:
    case_type = (case.case_type or "").strip() if case is not None else ""
    if case_type:
        return case_type, case_type
    return "UNSPECIFIED", "未填写"


def _country_report_label(case: Case | None) -> tuple[str, str]:
    if case is not None:
        country = (case.to_country or case.from_country or "").strip()
        if country:
            return country, country
    return "未填写", "未填写"


def _grouped_amount_payload(
    grouped_amounts: dict[str, dict[str, Decimal | int | str]],
) -> list[dict[str, Decimal | int | str]]:
    rows = []
    for values in grouped_amounts.values():
        rows.append(
            {
                "key": str(values["key"]),
                "label": str(values["label"]),
                "draft_count": int(values["draft_count"]),
                "service_fee_amount": _quantize_money(Decimal(values["service_fee_amount"])),
                "government_fee_amount": _quantize_money(Decimal(values["government_fee_amount"])),
                "income_amount": _quantize_money(Decimal(values["income_amount"])),
            }
        )
    return sorted(rows, key=lambda row: (-int(row["draft_count"]), str(row["label"])))


def _agent_service_amount_payload(
    grouped_amounts: dict[str, dict[str, Decimal | int | str]],
) -> list[dict[str, Decimal | int | str]]:
    rows = []
    for values in grouped_amounts.values():
        rows.append(
            {
                "key": str(values["key"]),
                "label": str(values["label"]),
                "draft_count": int(values["draft_count"]),
                "service_fee_amount": _quantize_money(Decimal(values["service_fee_amount"])),
            }
        )
    return sorted(rows, key=lambda row: (-int(row["draft_count"]), str(row["label"])))


def _trend_amount_payload(
    grouped_amounts: dict[str, dict[str, Any]],
    *,
    sort_key,
) -> list[dict[str, Any]]:
    rows = []
    for values in grouped_amounts.values():
        rows.append(
            {
                "key": str(values["key"]),
                "label": str(values["label"]),
                "draft_count": int(values["draft_count"]),
                "service_fee_amount": _quantize_money(Decimal(values["service_fee_amount"])),
                "government_fee_amount": _quantize_money(Decimal(values["government_fee_amount"])),
                "income_amount": _quantize_money(Decimal(values["income_amount"])),
                "draft_type_amounts": _grouped_amount_payload(values["draft_type_amounts"]),
            }
        )
    return sorted(rows, key=sort_key)


def _draft_report_bill_balance_summary(
    db: Session,
    *,
    draft_ids: list[str],
) -> dict[str, Decimal | int]:
    if not draft_ids:
        return {
            "billed_amount": Decimal("0"),
            "received_amount": Decimal("0"),
            "unpaid_balance_amount": Decimal("0"),
            "partially_received_bill_count": 0,
        }

    rows = db.execute(
        select(Bill.id, Bill.amount, Bill.balance)
        .join(BillItem, BillItem.bill_id == Bill.id)
        .where(Bill.direction == "AR")
        .where(BillItem.draft_id.is_not(None))
        .where(BillItem.draft_id.in_(draft_ids))
        .group_by(Bill.id, Bill.amount, Bill.balance)
    ).all()

    billed_amount = Decimal("0")
    received_amount = Decimal("0")
    unpaid_balance_amount = Decimal("0")
    partially_received_bill_count = 0

    for _bill_id, amount, balance in rows:
        bill_amount = _to_decimal(amount, field_name="bill.amount")
        bill_balance = _to_decimal(balance, field_name="bill.balance")
        billed_amount += bill_amount
        received_amount += bill_amount - bill_balance
        unpaid_balance_amount += bill_balance
        if Decimal("0") < bill_balance < bill_amount:
            partially_received_bill_count += 1

    return {
        "billed_amount": _quantize_money(billed_amount),
        "received_amount": _quantize_money(received_amount),
        "unpaid_balance_amount": _quantize_money(unpaid_balance_amount),
        "partially_received_bill_count": partially_received_bill_count,
    }


def _accumulate_grouped_amount(
    grouped_amounts: dict[str, dict[str, Decimal | int | str]],
    *,
    key: str,
    label: str,
    draft: FeeDraft,
) -> None:
    row = grouped_amounts.setdefault(
        key,
        {
            "key": key,
            "label": label,
            "draft_count": 0,
            "service_fee_amount": Decimal("0"),
            "government_fee_amount": Decimal("0"),
            "income_amount": Decimal("0"),
        },
    )
    row["draft_count"] = int(row["draft_count"]) + 1
    row["service_fee_amount"] = Decimal(row["service_fee_amount"]) + Decimal(
        draft.total_service or 0
    )
    row["government_fee_amount"] = Decimal(row["government_fee_amount"]) + Decimal(
        draft.total_gov or 0
    )
    row["income_amount"] = Decimal(row["income_amount"]) + Decimal(draft.amount or 0)


def _accumulate_agent_service_amount(
    grouped_amounts: dict[str, dict[str, Decimal | int | str]],
    *,
    key: str,
    label: str,
    service_amount: Decimal,
) -> None:
    row = grouped_amounts.setdefault(
        key,
        {
            "key": key,
            "label": label,
            "draft_count": 0,
            "service_fee_amount": Decimal("0"),
        },
    )
    row["draft_count"] = int(row["draft_count"]) + 1
    row["service_fee_amount"] = Decimal(row["service_fee_amount"]) + service_amount


def _load_case_agent_split_map(
    db: Session, *, case_ids: set[str]
) -> dict[str, list[tuple[str, Decimal]]]:
    if not case_ids:
        return {}
    rows = db.execute(
        select(T_CaseAgentSplit.case_id, T_CaseAgentSplit.agent_id, T_CaseAgentSplit.share_ratio)
        .where(T_CaseAgentSplit.case_id.in_(case_ids))
        .order_by(T_CaseAgentSplit.created_at.asc(), T_CaseAgentSplit.id.asc())
    ).all()
    mapping: dict[str, list[tuple[str, Decimal]]] = {}
    for case_id, agent_id, share_ratio in rows:
        mapping.setdefault(case_id, []).append(
            (agent_id, _to_decimal(share_ratio, field_name="case_agent_split.share_ratio"))
        )
    return mapping


def _split_money_by_ratios(base_amount: Decimal, ratios: list[Decimal]) -> list[Decimal]:
    if not ratios:
        return []
    allocations: list[Decimal] = []
    allocated_total = Decimal("0")
    for ratio in ratios[:-1]:
        share = _quantize_money((base_amount * ratio) / Decimal("100"))
        allocations.append(share)
        allocated_total += share
    allocations.append(_quantize_money(base_amount - allocated_total))
    return allocations


def _draft_report_amount_summary(
    db: Session,
    drafts: list[FeeDraft],
) -> dict[str, Decimal | int | list[dict[str, Decimal | int | str]]]:
    draft_ids = [draft.id for draft in drafts]
    case_ids = {draft.case_id for draft in drafts if draft.case_id}
    cases = db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all()
    case_map = {case.id: case for case in cases}

    client_ids = {draft.client_id for draft in drafts if draft.client_id}
    clients = db.execute(select(Client).where(Client.id.in_(client_ids))).scalars().all()
    client_map = {client.id: client for client in clients}
    case_agent_split_map = _load_case_agent_split_map(db, case_ids=case_ids)
    bill_balance_summary = _draft_report_bill_balance_summary(db, draft_ids=draft_ids)

    client_amounts: dict[str, dict[str, Decimal | int | str]] = {}
    case_type_amounts: dict[str, dict[str, Decimal | int | str]] = {}
    country_amounts: dict[str, dict[str, Decimal | int | str]] = {}
    agent_service_amounts: dict[str, dict[str, Decimal | int | str]] = {}
    year_amounts: dict[str, dict[str, Any]] = {}
    month_amounts: dict[str, dict[str, Any]] = {}

    for draft in drafts:
        case = case_map.get(draft.case_id)
        client = client_map.get(draft.client_id) if draft.client_id else None

        client_key, client_label = _client_report_label(client, draft.client_id)
        _accumulate_grouped_amount(
            client_amounts,
            key=client_key,
            label=client_label,
            draft=draft,
        )

        case_type_key, case_type_label = _case_type_report_label(case)
        _accumulate_grouped_amount(
            case_type_amounts,
            key=case_type_key,
            label=case_type_label,
            draft=draft,
        )

        country_key, country_label = _country_report_label(case)
        _accumulate_grouped_amount(
            country_amounts,
            key=country_key,
            label=country_label,
            draft=draft,
        )

        service_amount = Decimal(draft.total_service or 0)
        split_rows = case_agent_split_map.get(draft.case_id, [])
        if split_rows:
            split_amounts = _split_money_by_ratios(service_amount, [row[1] for row in split_rows])
            for (agent_id, _share_ratio), split_amount in zip(
                split_rows, split_amounts, strict=True
            ):
                _accumulate_agent_service_amount(
                    agent_service_amounts,
                    key=agent_id,
                    label=agent_id,
                    service_amount=split_amount,
                )
        elif case is not None and case.primary_agent_id:
            _accumulate_agent_service_amount(
                agent_service_amounts,
                key=case.primary_agent_id,
                label=case.primary_agent_id,
                service_amount=service_amount,
            )
        else:
            _accumulate_agent_service_amount(
                agent_service_amounts,
                key="UNASSIGNED",
                label="未分配代理人",
                service_amount=service_amount,
            )

        created_at = draft.created_at
        year_key = str(created_at.year)
        month_key = created_at.strftime("%Y-%m")
        for bucket_key, bucket_label, bucket_map in (
            (year_key, f"{created_at.year} 年", year_amounts),
            (month_key, month_key, month_amounts),
        ):
            bucket = bucket_map.setdefault(
                bucket_key,
                {
                    "key": bucket_key,
                    "label": bucket_label,
                    "draft_count": 0,
                    "service_fee_amount": Decimal("0"),
                    "government_fee_amount": Decimal("0"),
                    "income_amount": Decimal("0"),
                    "draft_type_amounts": {},
                },
            )
            bucket["draft_count"] += 1
            bucket["service_fee_amount"] += Decimal(draft.total_service or 0)
            bucket["government_fee_amount"] += Decimal(draft.total_gov or 0)
            bucket["income_amount"] += Decimal(draft.amount or 0)
            _accumulate_grouped_amount(
                bucket["draft_type_amounts"],
                key=draft.draft_type,
                label=draft.draft_type,
                draft=draft,
            )

    return {
        "total_draft_count": len(drafts),
        "service_fee_amount": _quantize_money(
            sum((Decimal(draft.total_service or 0) for draft in drafts), Decimal("0"))
        ),
        "government_fee_amount": _quantize_money(
            sum((Decimal(draft.total_gov or 0) for draft in drafts), Decimal("0"))
        ),
        "income_amount": _quantize_money(
            sum((Decimal(draft.amount or 0) for draft in drafts), Decimal("0"))
        ),
        "billed_amount": bill_balance_summary["billed_amount"],
        "received_amount": bill_balance_summary["received_amount"],
        "unpaid_balance_amount": bill_balance_summary["unpaid_balance_amount"],
        "partially_received_bill_count": bill_balance_summary["partially_received_bill_count"],
        "client_amounts": _grouped_amount_payload(client_amounts),
        "case_type_amounts": _grouped_amount_payload(case_type_amounts),
        "country_amounts": _grouped_amount_payload(country_amounts),
        "agent_service_amounts": _agent_service_amount_payload(agent_service_amounts),
        "year_amounts": _trend_amount_payload(year_amounts, sort_key=lambda row: row["key"]),
        "month_amounts": _trend_amount_payload(month_amounts, sort_key=lambda row: row["key"]),
    }


def _draft_report_matching_ids_by_fee_type(
    db: Session,
    *,
    draft_ids: list[str],
    fee_type: str,
) -> set[str]:
    if not draft_ids:
        return set()
    rows = (
        db.execute(
            select(FeeItem.draft_id)
            .where(FeeItem.draft_id.in_(draft_ids))
            .where(func.upper(FeeItem.fee_type) == fee_type)
            .distinct()
        )
        .scalars()
        .all()
    )
    return set(rows)


def _draft_report_matching_ids_by_bill_status(
    db: Session,
    *,
    draft_ids: list[str],
    bill_status: str,
) -> set[str]:
    if not draft_ids:
        return set()
    rows = (
        db.execute(
            select(BillItem.draft_id)
            .join(Bill, Bill.id == BillItem.bill_id)
            .where(BillItem.draft_id.isnot(None))
            .where(BillItem.draft_id.in_(draft_ids))
            .where(func.upper(Bill.status) == bill_status)
            .distinct()
        )
        .scalars()
        .all()
    )
    return set(rows)


def list_fee_drafts(
    db: Session,
    *,
    filters: dict[str, Any],
    page: int,
    page_size: int,
) -> tuple[list[FeeDraft], int, dict[str, Decimal | int]]:
    stmt = select(FeeDraft)

    case_id = filters.get("case_id")
    case_no = _normalize_optional_text(filters.get("case_no"))
    client_id = filters.get("client_id")
    currency = _normalize_report_text_filter(filters.get("currency"))
    fee_type = _normalize_report_text_filter(filters.get("fee_type"))
    bill_status = _normalize_report_text_filter(filters.get("bill_status"))
    draft_status = _normalize_report_text_filter(filters.get("draft_status"))
    if draft_status is None:
        draft_status = _normalize_report_text_filter(filters.get("status"))
    date_from = filters.get("date_from")
    date_to = filters.get("date_to")

    if case_id:
        stmt = stmt.where(FeeDraft.case_id == case_id)
    if case_no:
        stmt = stmt.join(Case, Case.id == FeeDraft.case_id).where(Case.case_no == case_no)
    if client_id:
        stmt = stmt.where(FeeDraft.client_id == client_id)
    if currency:
        stmt = stmt.where(func.upper(FeeDraft.currency) == currency)
    if draft_status:
        stmt = stmt.where(func.upper(FeeDraft.status) == draft_status)

    if isinstance(date_from, date_type):
        lower_bound, _ = _draft_report_date_bounds(date_from, None)
        if lower_bound is not None:
            stmt = stmt.where(FeeDraft.created_at >= lower_bound)
    if isinstance(date_to, date_type):
        _, upper_bound = _draft_report_date_bounds(None, date_to)
        if upper_bound is not None:
            stmt = stmt.where(FeeDraft.created_at < upper_bound)

    stmt = stmt.order_by(FeeDraft.updated_at.desc(), FeeDraft.id.desc())
    drafts = db.execute(stmt).scalars().all()

    if fee_type:
        matching_ids = _draft_report_matching_ids_by_fee_type(
            db,
            draft_ids=[draft.id for draft in drafts],
            fee_type=fee_type,
        )
        drafts = [draft for draft in drafts if draft.id in matching_ids]

    if bill_status:
        matching_ids = _draft_report_matching_ids_by_bill_status(
            db,
            draft_ids=[draft.id for draft in drafts],
            bill_status=bill_status,
        )
        drafts = [draft for draft in drafts if draft.id in matching_ids]

    total = len(drafts)
    offset = (page - 1) * page_size
    items = drafts[offset : offset + page_size]
    summary = _draft_report_amount_summary(db, drafts)
    return items, total, summary


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


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)


def _normalize_ratio(value: Decimal | str | None, *, default: Decimal) -> Decimal:
    if value is None:
        return default
    try:
        ratio = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return default
    if ratio < Decimal("0"):
        return Decimal("0")
    if ratio > Decimal("1"):
        return Decimal("1")
    return ratio


def _official_payable_ratio_from_customer_reduction(
    value: Decimal | str | None,
) -> Decimal:
    reduction_ratio = _normalize_ratio(value, default=Decimal("0"))
    if reduction_ratio == Decimal("0"):
        return Decimal("1")
    return Decimal("1") - reduction_ratio


def fee_rate_effective_on_conditions(as_of_date: date_type):
    return (
        or_(FeeRate.effective_from.is_(None), FeeRate.effective_from <= as_of_date),
        or_(FeeRate.effective_to.is_(None), FeeRate.effective_to >= as_of_date),
    )


# 待确认/停用来源的费率不得参与自动生成草单或预览（GAP-AUDIT-006 启用门禁）。
_BLOCKED_SOURCE_STATUSES = ("PENDING_CONFIRMATION", "PENDING", "DISABLED")


def fee_rate_source_enabled_condition():
    return or_(
        FeeRate.source_status.is_(None),
        FeeRate.source_status.not_in(_BLOCKED_SOURCE_STATUSES),
    )


def _enabled_fee_rates_by_code(
    db: Session,
    *,
    fee_codes: tuple[str, ...],
    currency: str,
    as_of_date: date_type | None = None,
) -> dict[str, FeeRate]:
    effective_on = as_of_date or date_type.today()
    rates = (
        db.execute(
            select(FeeRate).where(
                FeeRate.fee_code.in_(fee_codes),
                FeeRate.fee_type == FeeType.GOV.value,
                FeeRate.currency == currency,
                FeeRate.enabled.is_(True),
                fee_rate_source_enabled_condition(),
                *fee_rate_effective_on_conditions(effective_on),
            )
        )
        .scalars()
        .all()
    )
    return {rate.fee_code: rate for rate in rates}


def _assert_apply_fee_supported_case(case: Case) -> None:
    if (
        case.case_type != "NORMAL"
        or case.flow_dir != "CN_DOMESTIC"
        or case.patent_category not in _APPLY_FEE_BASE_GOV_CODES_BY_PATENT_CATEGORY
    ):
        raise_business_error(
            "APPLY_FEE_UNSUPPORTED_CASE",
            "Apply fee draft generation only supports domestic application cases",
            details={
                "case_id": case.id,
                "case_type": case.case_type,
                "flow_dir": case.flow_dir,
                "patent_category": case.patent_category,
            },
            status_code=400,
        )


def _existing_open_apply_fee_draft(db: Session, *, case_id: str, currency: str) -> FeeDraft | None:
    return (
        db.execute(
            select(FeeDraft)
            .where(
                FeeDraft.case_id == case_id,
                FeeDraft.draft_type == _APPLY_FEE_DRAFT_TYPE,
                FeeDraft.currency == currency,
                FeeDraft.status == FeeDraftStatus.OPEN.value,
            )
            .order_by(FeeDraft.created_at.asc(), FeeDraft.id.asc())
        )
        .scalars()
        .first()
    )


def _assert_reexam_fee_supported_case(case: Case) -> None:
    if (
        case.case_type != "NORMAL"
        or case.flow_dir != "CN_DOMESTIC"
        or case.patent_category not in _REEXAM_FEE_CODES_BY_PATENT_CATEGORY
    ):
        raise_business_error(
            "REEXAM_FEE_UNSUPPORTED_CASE",
            "Reexamination fee preview supports domestic normal patent cases only",
            details={
                "case_type": case.case_type,
                "flow_dir": case.flow_dir,
                "patent_category": case.patent_category,
            },
            status_code=400,
        )


def _apply_fee_required_rate_codes(case: Case) -> tuple[str, ...]:
    rate_codes = [
        _APPLY_FEE_BASE_GOV_CODES_BY_PATENT_CATEGORY[str(case.patent_category)],
    ]

    claim_count = Decimal(case.claim_count or 0)
    if claim_count > Decimal("10"):
        rate_codes.append(_APPLY_FEE_EXCESS_CLAIM_CODE)

    if case.patent_category == "INV":
        rate_codes.append(_APPLY_FEE_PUBLICATION_PRINT_CODE)
        if case.has_exam_request:
            rate_codes.append(_APPLY_FEE_SUBSTANTIVE_EXAM_CODE)

    return tuple(rate_codes)


def _official_amount(rate: FeeRate, *, quantity: Decimal, payable_ratio: Decimal) -> Decimal:
    unit_price = Decimal(rate.default_amount or 0)
    amount = unit_price * quantity
    if rate.allow_reduction:
        amount *= payable_ratio
    return _money(amount)


def _build_apply_fee_item_specs(
    case: Case, *, rates_by_code: dict[str, FeeRate]
) -> list[tuple[FeeRate, Decimal, Decimal, str]]:
    fee_reduction_ratio = _official_payable_ratio_from_customer_reduction(case.fee_reduction)
    claim_count = Decimal(case.claim_count or 0)
    excess_claim_count = max(claim_count - Decimal("10"), Decimal("0"))

    item_specs: list[tuple[FeeRate, Decimal, Decimal, str]] = []
    base_rate = rates_by_code[
        _APPLY_FEE_BASE_GOV_CODES_BY_PATENT_CATEGORY[str(case.patent_category)]
    ]
    item_specs.append(
        (
            base_rate,
            Decimal("1"),
            _official_amount(base_rate, quantity=Decimal("1"), payable_ratio=fee_reduction_ratio),
            "application official fee",
        )
    )

    if excess_claim_count > 0:
        excess_rate = rates_by_code[_APPLY_FEE_EXCESS_CLAIM_CODE]
        item_specs.append(
            (
                excess_rate,
                excess_claim_count,
                _official_amount(
                    excess_rate,
                    quantity=excess_claim_count,
                    payable_ratio=fee_reduction_ratio,
                ),
                "excess claim official fee",
            )
        )

    if case.patent_category == "INV":
        publication_rate = rates_by_code[_APPLY_FEE_PUBLICATION_PRINT_CODE]
        item_specs.append(
            (
                publication_rate,
                Decimal("1"),
                _official_amount(
                    publication_rate,
                    quantity=Decimal("1"),
                    payable_ratio=fee_reduction_ratio,
                ),
                "publication printing official fee",
            )
        )
        if case.has_exam_request:
            exam_rate = rates_by_code[_APPLY_FEE_SUBSTANTIVE_EXAM_CODE]
            item_specs.append(
                (
                    exam_rate,
                    Decimal("1"),
                    _official_amount(
                        exam_rate,
                        quantity=Decimal("1"),
                        payable_ratio=fee_reduction_ratio,
                    ),
                    "substantive exam official fee",
                )
            )

    return item_specs


def _add_apply_fee_item(
    db: Session,
    *,
    draft: FeeDraft,
    rate: FeeRate,
    quantity: Decimal,
    unit_price: Decimal,
    amount: Decimal,
    remark: str,
    actor_id: str | None,
) -> None:
    db.add(
        FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=draft.case_id,
            rate_id=rate.id,
            fee_code=rate.fee_code,
            fee_name=rate.fee_name,
            fee_type=rate.fee_type,
            quantity=quantity.quantize(_QTY_QUANT),
            unit_price=_money(unit_price),
            amount=_money(amount),
            remark=remark,
            created_by=actor_id,
            updated_by=actor_id,
        )
    )


def generate_apply_fee_draft(
    db: Session, *, data: ApplyFeeDraftGenerateIn, actor_id: str | None
) -> tuple[FeeDraft, bool]:
    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    _assert_apply_fee_supported_case(case)

    currency = (data.currency or "CNY").strip().upper()
    existing = _existing_open_apply_fee_draft(db, case_id=case.id, currency=currency)
    if existing:
        return existing, False

    required_fee_codes = _apply_fee_required_rate_codes(case)
    rates_by_code = _enabled_fee_rates_by_code(
        db,
        fee_codes=required_fee_codes,
        currency=currency,
    )
    missing_fee_codes = [
        fee_code for fee_code in required_fee_codes if fee_code not in rates_by_code
    ]
    if missing_fee_codes:
        raise_business_error(
            "APPLY_FEE_RATE_MISSING",
            "Required apply fee rates are missing",
            details={"missing_fee_codes": missing_fee_codes, "currency": currency},
            status_code=409,
        )

    item_specs = _build_apply_fee_item_specs(case, rates_by_code=rates_by_code)
    total_gov = sum((amount for _rate, _quantity, amount, _remark in item_specs), Decimal("0"))

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=case.id,
        client_id=case.client_id,
        draft_type=_APPLY_FEE_DRAFT_TYPE,
        currency=currency,
        status=FeeDraftStatus.OPEN.value,
        total_gov=total_gov,
        total_service=Decimal("0"),
        total_misc=Decimal("0"),
        amount=total_gov,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(draft)
    db.flush()

    for rate, quantity, amount, remark in item_specs:
        unit_price = Decimal(rate.default_amount or 0)
        _add_apply_fee_item(
            db,
            draft=draft,
            rate=rate,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount,
            remark=remark,
            actor_id=actor_id,
        )

    db.commit()
    db.refresh(draft)
    return draft, True


def preview_official_fee_candidates(db: Session, *, data: OfficialFeePreviewIn) -> dict[str, Any]:
    trigger_event = (data.trigger_event or "").strip().upper()
    supported_triggers = {"FILING_ACCEPTED", "REEXAM_REQUESTED"}
    if trigger_event not in supported_triggers:
        raise_business_error(
            "OFFICIAL_FEE_PREVIEW_TRIGGER_UNSUPPORTED",
            "Official fee preview trigger is not supported",
            details={"trigger_event": data.trigger_event},
            status_code=400,
        )

    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    currency = (data.currency or "CNY").strip().upper()
    if trigger_event == "FILING_ACCEPTED":
        _assert_apply_fee_supported_case(case)
        required_fee_codes = _apply_fee_required_rate_codes(case)
        draft_type = _APPLY_FEE_DRAFT_TYPE
    else:
        _assert_reexam_fee_supported_case(case)
        required_fee_codes = (_REEXAM_FEE_CODES_BY_PATENT_CATEGORY[str(case.patent_category)],)
        draft_type = _REEXAM_FEE_DRAFT_TYPE

    rates_by_code = _enabled_fee_rates_by_code(
        db,
        fee_codes=required_fee_codes,
        currency=currency,
    )
    missing_fee_codes = [
        fee_code for fee_code in required_fee_codes if fee_code not in rates_by_code
    ]
    if missing_fee_codes:
        raise_business_error(
            "OFFICIAL_FEE_PREVIEW_RATE_MISSING",
            "Required official fee preview rates are missing",
            details={"missing_fee_codes": missing_fee_codes, "currency": currency},
            status_code=409,
        )

    reduction_ratio = _normalize_ratio(case.fee_reduction, default=Decimal("0"))
    payable_ratio = _official_payable_ratio_from_customer_reduction(case.fee_reduction)
    if trigger_event == "FILING_ACCEPTED":
        item_specs = _build_apply_fee_item_specs(case, rates_by_code=rates_by_code)
        trigger_rule = _FILING_ACCEPTED_TRIGGER_RULE
        deadline_rule = _FILING_ACCEPTED_DEADLINE_RULE
    else:
        reexam_rate = rates_by_code[required_fee_codes[0]]
        item_specs = [
            (
                reexam_rate,
                Decimal("1"),
                _official_amount(
                    reexam_rate,
                    quantity=Decimal("1"),
                    payable_ratio=payable_ratio,
                ),
                "reexamination official fee",
            )
        ]
        trigger_rule = _REEXAM_REQUESTED_TRIGGER_RULE
        deadline_rule = _REEXAM_REQUESTED_DEADLINE_RULE

    candidates = [
        {
            "rate_id": rate.id,
            "fee_code": rate.fee_code,
            "fee_name": rate.fee_name,
            "fee_type": rate.fee_type,
            "quantity": quantity.quantize(_QTY_QUANT),
            "unit_price": _money(Decimal(rate.default_amount or 0)),
            "amount": _money(amount),
            "calculation_note": remark,
            "source_doc": rate.source_doc,
            "source_status": rate.source_status,
            "fee_category": rate.fee_category,
            "fee_subtype": rate.fee_subtype,
            "trigger_rule": trigger_rule,
            "deadline_rule": deadline_rule,
            "reduction_scope": rate.reduction_scope,
            "source_document_id": data.source_document_id,
            "amount_before_reduction": _money(Decimal(rate.default_amount or 0) * quantity),
            "reduction_ratio": reduction_ratio if rate.allow_reduction else Decimal("0"),
            "payable_ratio": payable_ratio if rate.allow_reduction else Decimal("1"),
        }
        for rate, quantity, amount, remark in item_specs
    ]
    total_gov = sum((amount for _rate, _quantity, amount, _remark in item_specs), Decimal("0"))
    source_key = data.source_document_id or "NO_SOURCE"

    return {
        "case_id": case.id,
        "draft_type": draft_type,
        "trigger_event": trigger_event,
        "source_document_id": data.source_document_id,
        "idempotency_key": f"{case.id}:{trigger_event}:{source_key}",
        "currency": currency,
        "preview_only": True,
        "total_gov": _money(total_gov),
        "candidates": candidates,
    }


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
    if Decimal(quantity) < Decimal("0") or Decimal(unit_price) < Decimal("0"):
        raise_business_error(
            "FEE_ITEM_AMOUNT_INVALID",
            "Fee item quantity and unit price must be non-negative",
            status_code=400,
            details={"quantity": str(quantity), "unit_price": str(unit_price)},
        )
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


def list_fee_items(db: Session, *, draft_id: str) -> list[FeeItem]:
    get_fee_draft(db, draft_id=draft_id)
    stmt = select(FeeItem).where(FeeItem.draft_id == draft_id).order_by(FeeItem.created_at.asc())
    return list(db.execute(stmt).scalars().all())


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
    if Decimal(quantity) < Decimal("0") or Decimal(unit_price) < Decimal("0"):
        raise_business_error(
            "FEE_ITEM_AMOUNT_INVALID",
            "Fee item quantity and unit price must be non-negative",
            status_code=400,
            details={"quantity": str(quantity), "unit_price": str(unit_price)},
        )
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
    fee_domain = filters.get("fee_domain")
    fee_section = filters.get("fee_section")
    fee_category = filters.get("fee_category")
    fee_subtype = filters.get("fee_subtype")
    calc_mode = filters.get("calc_mode")

    if rate_group:
        stmt = stmt.where(FeeRate.rate_group == rate_group)
    if country_code:
        stmt = stmt.where(FeeRate.country_code == country_code)
    if case_type:
        stmt = stmt.where(FeeRate.case_type == case_type)
    if patent_category:
        stmt = stmt.where(FeeRate.patent_category == patent_category)
    if fee_domain:
        stmt = stmt.where(FeeRate.fee_domain == fee_domain)
    if fee_section:
        stmt = stmt.where(FeeRate.fee_section == fee_section)
    if fee_category:
        stmt = stmt.where(FeeRate.fee_category == fee_category)
    if fee_subtype:
        stmt = stmt.where(FeeRate.fee_subtype == fee_subtype)
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
        fee_domain=data.fee_domain,
        fee_section=data.fee_section,
        fee_category=data.fee_category,
        fee_subtype=data.fee_subtype,
        reduction_scope=data.reduction_scope,
        calc_mode=data.calc_mode.value if data.calc_mode else None,
        calc_params=data.calc_params,
        allow_reduction=data.allow_reduction,
        effective_from=data.effective_from,
        effective_to=data.effective_to,
        source_doc=data.source_doc,
        source_url=data.source_url,
        source_policy=data.source_policy,
        source_version=data.source_version,
        source_status=data.source_status,
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

    Batch 3 slice:
    - FIXED keeps default amount behavior
    - PER_CLAIM supports calc_params + optional reduction/discount percentages
    - PER_PAGE bills the pages falling inside [from_page, to_page] at unit_amount
      (page basis: spec_pages + draw_pages, i.e. 说明书含附图页数)
    - Other modes still fall back to default amount
    """
    amount = rate.default_amount if rate.default_amount is not None else Decimal("0")
    calc_mode = (getattr(rate, "calc_mode", None) or "FIXED").upper()

    if calc_mode == "FIXED":
        return amount

    if calc_mode == "PER_CLAIM":
        calc_params_raw = getattr(rate, "calc_params", None)
        calc_params: dict[str, Any] = {}
        if calc_params_raw:
            try:
                parsed = json.loads(calc_params_raw)
                if isinstance(parsed, dict):
                    calc_params = parsed
            except (TypeError, ValueError):
                logger.warning(
                    "calculate_fee_amount: invalid calc_params for rate=%s, raw=%r",
                    rate.fee_code,
                    calc_params_raw,
                )

        per_claim_amount_raw = calc_params.get("per_claim_amount", amount)
        try:
            per_claim_amount = Decimal(per_claim_amount_raw)
        except (InvalidOperation, TypeError, ValueError):
            per_claim_amount = amount

        if case is not None and case.claim_count is not None:
            claim_count = Decimal(case.claim_count)
        else:
            claim_count_raw = calc_params.get("claim_count", 1)
            try:
                claim_count = Decimal(claim_count_raw)
            except (InvalidOperation, TypeError, ValueError):
                claim_count = Decimal("1")

        computed = per_claim_amount * claim_count

        if getattr(rate, "allow_reduction", False):
            reduction_raw = calc_params.get("reduction_pct", 0)
            try:
                reduction_pct = Decimal(reduction_raw)
            except (InvalidOperation, TypeError, ValueError):
                reduction_pct = Decimal("0")
            reduction_pct = max(Decimal("0"), min(Decimal("100"), reduction_pct))
            if reduction_pct > 0:
                computed = computed * (Decimal("100") - reduction_pct) / Decimal("100")

        discount_raw = calc_params.get("discount_pct", 0)
        try:
            discount_pct = Decimal(discount_raw)
        except (InvalidOperation, TypeError, ValueError):
            discount_pct = Decimal("0")
        discount_pct = max(Decimal("0"), min(Decimal("100"), discount_pct))
        if discount_pct > 0:
            computed = computed * (Decimal("100") - discount_pct) / Decimal("100")

        return _quantize_money(computed)

    if calc_mode == "PER_PAGE":
        calc_params_raw = getattr(rate, "calc_params", None)
        calc_params = {}
        if calc_params_raw:
            try:
                parsed = json.loads(calc_params_raw)
                if isinstance(parsed, dict):
                    calc_params = parsed
            except (TypeError, ValueError):
                logger.warning(
                    "calculate_fee_amount: invalid calc_params for rate=%s, raw=%r",
                    rate.fee_code,
                    calc_params_raw,
                )

        try:
            unit_amount = Decimal(calc_params.get("unit_amount", amount))
        except (InvalidOperation, TypeError, ValueError):
            unit_amount = amount

        # 页数口径：说明书含附图页数（spec_pages + draw_pages）。
        total_pages = 0
        if case is not None:
            total_pages = int(case.spec_pages or 0) + int(case.draw_pages or 0)
        if total_pages <= 0:
            try:
                total_pages = int(calc_params.get("total_pages", 0))
            except (TypeError, ValueError):
                total_pages = 0

        try:
            from_page = int(calc_params.get("from_page", 1))
        except (TypeError, ValueError):
            from_page = 1
        to_page_raw = calc_params.get("to_page")
        try:
            to_page = int(to_page_raw) if to_page_raw is not None else None
        except (TypeError, ValueError):
            to_page = None

        upper = min(total_pages, to_page) if to_page is not None else total_pages
        billable_pages = max(0, upper - from_page + 1) if total_pages >= from_page else 0
        return _quantize_money(unit_amount * Decimal(billable_pages))

    logger.warning(
        "calculate_fee_amount: calc_mode=%s not yet implemented for rate=%s, "
        "returning default_amount=%s",
        calc_mode,
        rate.fee_code,
        amount,
    )
    return amount
