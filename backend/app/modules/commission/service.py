from __future__ import annotations

from datetime import date, datetime, time
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.billing.models import Bill, BillItem, CaseReceipt
from app.modules.cases.models import Case, T_CaseAgentSplit
from app.modules.commission.models import (
    Commission,
    CommissionRule,
    CommissionSettleLine,
    CommissionSettlement,
)

_MONEY_QUANT = Decimal("0.01")
_SERVICE_FEE_TYPE = "SERVICE"
_TERMINAL_COMMISSION_STATUSES = {"SETTLED", "CANCELLED", "VOID", "CLOSED"}
_ACTIVE_SETTLEMENT_STATUSES = {"DRAFT", "CREATED"}
_SETTLEMENT_GENERATE_ALLOWED_STATUSES = {"DRAFT", "GENERATED"}
_SETTLEMENT_REPORT_TIME_FIELDS = {"line_created_at", "settleable_date", "settlement_period"}
_UNKNOWN_TIME_BUCKET = "UNKNOWN"
_UNASSIGNED_AGENT_SENTINELS = {"UNASSIGNED"}


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _validate_rule_name(value: str | None) -> str:
    if value is None:
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "rule_name is required",
            status_code=400,
        )
    normalized = str(value).strip()
    if not normalized:
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "rule_name is required",
            status_code=400,
        )
    return normalized


def _validate_rate(value: Decimal | None, field_name: str) -> Decimal:
    if value is None:
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    try:
        normalized = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} must be a decimal value",
            status_code=400,
        )

    if normalized < Decimal("0") or normalized > Decimal("1"):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} must be within [0, 1]",
            status_code=400,
        )
    return normalized


def _validate_non_negative(value: Decimal | None, field_name: str) -> Decimal:
    if value is None:
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    try:
        normalized = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} must be a decimal value",
            status_code=400,
        )

    if normalized < Decimal("0"):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            f"{field_name} must be >= 0",
            status_code=400,
        )
    return normalized


def _validate_effective_range(effective_from: date | None, effective_to: date | None) -> None:
    if effective_from and effective_to and effective_from > effective_to:
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "effective_from must be less than or equal to effective_to",
            status_code=400,
        )


def _raise_conflict(conflict_rule_id: int) -> None:
    raise_business_error(
        "COMMISSION_RULE_CONFLICT",
        "Commission rule conflicts with an existing effective rule",
        details={"conflict_rule_id": conflict_rule_id},
        status_code=409,
    )


def _find_conflict_rule_id(
    db: Session,
    *,
    case_type: str | None,
    fee_type: str | None,
    flow_dir: str | None,
    patent_category: str | None,
    wait_pay: bool,
    force_settle: bool,
    effective_from: date | None,
    effective_to: date | None,
    exclude_rule_id: int | None = None,
) -> int | None:
    stmt = select(CommissionRule.id).where(
        CommissionRule.case_type == case_type,
        CommissionRule.fee_type == fee_type,
        CommissionRule.flow_dir == flow_dir,
        CommissionRule.patent_category == patent_category,
        CommissionRule.wait_pay == wait_pay,
        CommissionRule.force_settle == force_settle,
    )

    if exclude_rule_id is not None:
        stmt = stmt.where(CommissionRule.id != exclude_rule_id)

    if effective_from is not None:
        stmt = stmt.where(
            or_(
                CommissionRule.effective_to.is_(None),
                CommissionRule.effective_to >= effective_from,
            )
        )

    if effective_to is not None:
        stmt = stmt.where(
            or_(
                CommissionRule.effective_from.is_(None),
                CommissionRule.effective_from <= effective_to,
            )
        )

    return db.execute(stmt.order_by(CommissionRule.id.asc()).limit(1)).scalar_one_or_none()


def create_commission_rule(
    db: Session,
    *,
    rule_name: str,
    case_type: str | None,
    fee_type: str | None,
    flow_dir: str | None,
    patent_category: str | None,
    s1_rate: Decimal,
    s2_rate: Decimal,
    s1_fixed_amount: Decimal,
    s2_fixed_amount: Decimal,
    wait_pay: bool,
    force_settle: bool,
    enabled: bool,
    effective_from: date | None,
    effective_to: date | None,
    remark: str | None,
    actor_id: str | None = None,
) -> CommissionRule:
    normalized_rule_name = _validate_rule_name(rule_name)
    normalized_case_type = _normalize_optional_text(case_type)
    normalized_fee_type = _normalize_optional_text(fee_type)
    normalized_flow_dir = _normalize_optional_text(flow_dir)
    normalized_patent_category = _normalize_optional_text(patent_category)
    normalized_remark = _normalize_optional_text(remark)

    validated_s1_rate = _validate_rate(s1_rate, "s1_rate")
    validated_s2_rate = _validate_rate(s2_rate, "s2_rate")
    validated_s1_fixed_amount = _validate_non_negative(s1_fixed_amount, "s1_fixed_amount")
    validated_s2_fixed_amount = _validate_non_negative(s2_fixed_amount, "s2_fixed_amount")

    _validate_effective_range(effective_from, effective_to)

    conflict_rule_id = _find_conflict_rule_id(
        db,
        case_type=normalized_case_type,
        fee_type=normalized_fee_type,
        flow_dir=normalized_flow_dir,
        patent_category=normalized_patent_category,
        wait_pay=wait_pay,
        force_settle=force_settle,
        effective_from=effective_from,
        effective_to=effective_to,
    )
    if conflict_rule_id is not None:
        _raise_conflict(conflict_rule_id)

    rule = CommissionRule(
        rule_name=normalized_rule_name,
        case_type=normalized_case_type,
        fee_type=normalized_fee_type,
        flow_dir=normalized_flow_dir,
        patent_category=normalized_patent_category,
        s1_rate=validated_s1_rate,
        s2_rate=validated_s2_rate,
        s1_fixed_amount=validated_s1_fixed_amount,
        s2_fixed_amount=validated_s2_fixed_amount,
        wait_pay=wait_pay,
        force_settle=force_settle,
        enabled=enabled,
        effective_from=effective_from,
        effective_to=effective_to,
        remark=normalized_remark,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_commission_rule(
    db: Session,
    *,
    rule_id: int,
    patch: dict[str, Any],
    actor_id: str | None = None,
) -> CommissionRule:
    rule = db.execute(
        select(CommissionRule).where(CommissionRule.id == rule_id)
    ).scalar_one_or_none()
    if not rule:
        raise_business_error(
            "COMMISSION_RULE_NOT_FOUND",
            "Commission rule not found",
            status_code=404,
        )

    def _pick(field: str, current_value):
        if field not in patch:
            return current_value
        return patch[field]

    final_rule_name = _validate_rule_name(_pick("rule_name", rule.rule_name))
    final_case_type = _normalize_optional_text(_pick("case_type", rule.case_type))
    final_fee_type = _normalize_optional_text(_pick("fee_type", rule.fee_type))
    final_flow_dir = _normalize_optional_text(_pick("flow_dir", rule.flow_dir))
    final_patent_category = _normalize_optional_text(_pick("patent_category", rule.patent_category))
    final_remark = _normalize_optional_text(_pick("remark", rule.remark))

    final_s1_rate = _validate_rate(_pick("s1_rate", rule.s1_rate), "s1_rate")
    final_s2_rate = _validate_rate(_pick("s2_rate", rule.s2_rate), "s2_rate")
    final_s1_fixed_amount = _validate_non_negative(
        _pick("s1_fixed_amount", rule.s1_fixed_amount), "s1_fixed_amount"
    )
    final_s2_fixed_amount = _validate_non_negative(
        _pick("s2_fixed_amount", rule.s2_fixed_amount), "s2_fixed_amount"
    )

    final_wait_pay = _pick("wait_pay", rule.wait_pay)
    final_force_settle = _pick("force_settle", rule.force_settle)
    final_enabled = _pick("enabled", rule.enabled)
    final_effective_from = _pick("effective_from", rule.effective_from)
    final_effective_to = _pick("effective_to", rule.effective_to)

    if not isinstance(final_wait_pay, bool):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "wait_pay must be boolean",
            status_code=400,
        )
    if not isinstance(final_force_settle, bool):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "force_settle must be boolean",
            status_code=400,
        )
    if not isinstance(final_enabled, bool):
        raise_business_error(
            "COMMISSION_RULE_INVALID",
            "enabled must be boolean",
            status_code=400,
        )

    _validate_effective_range(final_effective_from, final_effective_to)

    conflict_rule_id = _find_conflict_rule_id(
        db,
        case_type=final_case_type,
        fee_type=final_fee_type,
        flow_dir=final_flow_dir,
        patent_category=final_patent_category,
        wait_pay=final_wait_pay,
        force_settle=final_force_settle,
        effective_from=final_effective_from,
        effective_to=final_effective_to,
        exclude_rule_id=rule.id,
    )
    if conflict_rule_id is not None:
        _raise_conflict(conflict_rule_id)

    rule.rule_name = final_rule_name
    rule.case_type = final_case_type
    rule.fee_type = final_fee_type
    rule.flow_dir = final_flow_dir
    rule.patent_category = final_patent_category
    rule.s1_rate = final_s1_rate
    rule.s2_rate = final_s2_rate
    rule.s1_fixed_amount = final_s1_fixed_amount
    rule.s2_fixed_amount = final_s2_fixed_amount
    rule.wait_pay = final_wait_pay
    rule.force_settle = final_force_settle
    rule.enabled = final_enabled
    rule.effective_from = final_effective_from
    rule.effective_to = final_effective_to
    rule.remark = final_remark
    rule.updated_by = actor_id

    db.commit()
    db.refresh(rule)
    return rule


def _to_decimal(value: Decimal | int | float | str | None, *, field_name: str) -> Decimal:
    if value is None:
        raise_business_error(
            "COMMISSION_CONTEXT_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise_business_error(
            "COMMISSION_CONTEXT_INVALID",
            f"{field_name} must be a decimal value",
            status_code=400,
        )


def _quantize_money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY_QUANT, rounding=ROUND_HALF_UP)


def _load_case_map(db: Session, *, case_ids: list[str]) -> dict[str, Case]:
    case_rows = db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all()
    case_map = {row.id: row for row in case_rows}
    missing_case_ids = sorted(set(case_ids) - set(case_map))
    if missing_case_ids:
        raise_business_error(
            "CASE_NOT_FOUND",
            "One or more cases referenced by bill items were not found",
            details={"missing_case_ids": missing_case_ids},
            status_code=404,
        )
    return case_map


def _collect_bill_service_case_totals(db: Session, *, bill_id: str) -> dict[str, Decimal]:
    bill_items = (
        db.execute(
            select(BillItem).where(
                BillItem.bill_id == bill_id,
                BillItem.case_id.is_not(None),
            )
        )
        .scalars()
        .all()
    )

    case_totals: dict[str, Decimal] = {}
    for item in bill_items:
        fee_type = (item.fee_type or "").strip().upper()
        if fee_type != _SERVICE_FEE_TYPE:
            continue
        amount = _to_decimal(item.amount, field_name="bill_item.amount")
        if amount < Decimal("0"):
            raise_business_error(
                "COMMISSION_CONTEXT_INVALID",
                "Bill item amount cannot be negative",
                details={"bill_item_id": item.id},
                status_code=400,
            )
        case_totals[item.case_id] = case_totals.get(item.case_id, Decimal("0")) + amount

    return case_totals


def _select_best_commission_rule(
    db: Session,
    *,
    ref_date: date,
    fee_type: str,
    case_type: str | None,
    flow_dir: str | None,
    patent_category: str | None,
) -> CommissionRule | None:
    normalized_fee_type = _normalize_optional_text(fee_type)
    normalized_case_type = _normalize_optional_text(case_type)
    normalized_flow_dir = _normalize_optional_text(flow_dir)
    normalized_patent_category = _normalize_optional_text(patent_category)

    stmt = select(CommissionRule).where(
        CommissionRule.enabled.is_(True),
        or_(CommissionRule.effective_from.is_(None), CommissionRule.effective_from <= ref_date),
        or_(CommissionRule.effective_to.is_(None), CommissionRule.effective_to >= ref_date),
        or_(CommissionRule.fee_type.is_(None), CommissionRule.fee_type == normalized_fee_type),
        or_(CommissionRule.case_type.is_(None), CommissionRule.case_type == normalized_case_type),
        or_(CommissionRule.flow_dir.is_(None), CommissionRule.flow_dir == normalized_flow_dir),
        or_(
            CommissionRule.patent_category.is_(None),
            CommissionRule.patent_category == normalized_patent_category,
        ),
    )

    candidates = db.execute(stmt).scalars().all()
    if not candidates:
        return None

    def _specificity(rule: CommissionRule) -> int:
        return sum(
            1
            for value in (
                rule.fee_type,
                rule.case_type,
                rule.flow_dir,
                rule.patent_category,
            )
            if value is not None
        )

    return max(
        candidates,
        key=lambda rule: (
            _specificity(rule),
            1 if rule.effective_from is not None else 0,
            rule.effective_from or date.min,
            rule.id,
        ),
    )


def _find_existing_commission(
    db: Session,
    *,
    case_id: str,
    agent_id: str | None,
    fee_type: str,
    rule_id: int,
) -> Commission | None:
    stmt = select(Commission).where(
        Commission.case_id == case_id,
        Commission.fee_type == fee_type,
        Commission.rule_id == rule_id,
    )
    if agent_id is None:
        stmt = stmt.where(Commission.agent_id.is_(None))
    else:
        stmt = stmt.where(Commission.agent_id == agent_id)

    rows = db.execute(stmt.order_by(Commission.id.asc())).scalars().all()
    if len(rows) > 1:
        raise_business_error(
            "COMMISSION_UPSERT_CONFLICT",
            "Multiple commission rows matched the deterministic upsert key",
            details={
                "case_id": case_id,
                "agent_id": agent_id,
                "fee_type": fee_type,
                "rule_id": rule_id,
            },
            status_code=409,
        )
    return rows[0] if rows else None


def _calculate_stage_amounts(
    *,
    base_fee: Decimal,
    s1_rate: Decimal,
    s2_rate: Decimal,
    s1_fixed_amount: Decimal,
    s2_fixed_amount: Decimal,
) -> tuple[Decimal, Decimal]:
    s1_amount = _quantize_money((base_fee * s1_rate) + s1_fixed_amount)
    s2_amount = _quantize_money((base_fee * s2_rate) + s2_fixed_amount)
    return s1_amount, s2_amount


def _load_case_agent_splits(db: Session, *, case_id: str) -> list[tuple[str, Decimal]]:
    rows = db.execute(
        select(T_CaseAgentSplit.agent_id, T_CaseAgentSplit.share_ratio)
        .where(T_CaseAgentSplit.case_id == case_id)
        .order_by(T_CaseAgentSplit.created_at.asc(), T_CaseAgentSplit.id.asc())
    ).all()
    return [
        (agent_id, _to_decimal(share_ratio, field_name="case_agent_split.share_ratio"))
        for agent_id, share_ratio in rows
    ]


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


def _commission_is_rewritable(db: Session, commission: Commission) -> bool:
    if _normalized_status(commission.status) in _TERMINAL_COMMISSION_STATUSES:
        return False
    line_exists = db.execute(
        select(CommissionSettleLine.id)
        .where(CommissionSettleLine.commission_id == commission.id)
        .limit(1)
    ).scalar_one_or_none()
    return line_exists is None


def apply_commission_for_bill(
    db: Session,
    bill_id: str,
    actor_id: str | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "bill_id": bill_id,
        "processed_cases": 0,
        "created_count": 0,
        "updated_count": 0,
        "deleted_count": 0,
        "skipped_count": 0,
        "items": [],
        "status": "NOOP",
    }

    try:
        bill = db.execute(select(Bill).where(Bill.id == bill_id)).scalar_one_or_none()
        if not bill:
            raise_business_error("BILL_NOT_FOUND", "Bill not found", status_code=404)

        ref_date = bill.bill_date or date.today()
        case_totals = _collect_bill_service_case_totals(db, bill_id=bill_id)
        summary["processed_cases"] = len(case_totals)

        if not case_totals:
            return summary

        case_map = _load_case_map(db, case_ids=sorted(case_totals))

        for case_id in sorted(case_totals):
            base_fee = _quantize_money(
                _to_decimal(case_totals[case_id], field_name="commission.base_fee")
            )
            case = case_map[case_id]
            fee_type = _SERVICE_FEE_TYPE
            case_splits = _load_case_agent_splits(db, case_id=case_id)
            if case_splits:
                target_allocations = [
                    {
                        "agent_id": agent_id,
                        "share_ratio": share_ratio,
                    }
                    for agent_id, share_ratio in case_splits
                ]
                split_amounts = _split_money_by_ratios(
                    base_fee, [row["share_ratio"] for row in target_allocations]
                )
            else:
                target_allocations = [
                    {
                        "agent_id": case.primary_agent_id,
                        "share_ratio": Decimal("100"),
                    }
                ]
                split_amounts = [base_fee]
            target_agent_ids = {allocation["agent_id"] for allocation in target_allocations}

            rule = _select_best_commission_rule(
                db,
                ref_date=ref_date,
                fee_type=fee_type,
                case_type=case.case_type,
                flow_dir=case.flow_dir,
                patent_category=case.patent_category,
            )
            if not rule:
                summary["skipped_count"] += 1
                summary["items"].append(
                    {
                        "case_id": case_id,
                        "action": "SKIPPED",
                        "reason": "RULE_NOT_FOUND",
                    }
                )
                continue

            s1_rate = _validate_rate(rule.s1_rate, "s1_rate")
            s2_rate = _validate_rate(rule.s2_rate, "s2_rate")
            s1_fixed_amount = _validate_non_negative(rule.s1_fixed_amount, "s1_fixed_amount")
            s2_fixed_amount = _validate_non_negative(rule.s2_fixed_amount, "s2_fixed_amount")
            initial_settleable = bool(rule.force_settle) or not bool(rule.wait_pay)
            initial_settleable_date = ref_date if initial_settleable else None
            for allocation, split_base_fee in zip(target_allocations, split_amounts, strict=True):
                agent_id = allocation["agent_id"]
                s1_amount, s2_amount = _calculate_stage_amounts(
                    base_fee=split_base_fee,
                    s1_rate=s1_rate,
                    s2_rate=s2_rate,
                    s1_fixed_amount=s1_fixed_amount,
                    s2_fixed_amount=s2_fixed_amount,
                )

                existing = _find_existing_commission(
                    db,
                    case_id=case_id,
                    agent_id=agent_id,
                    fee_type=fee_type,
                    rule_id=rule.id,
                )
                if existing is None:
                    commission = Commission(
                        case_id=case_id,
                        agent_id=agent_id,
                        rule_id=rule.id,
                        fee_type=fee_type,
                        base_fee=split_base_fee,
                        s1_rate=s1_rate,
                        s1_amount=s1_amount,
                        s2_rate=s2_rate,
                        s2_amount=s2_amount,
                        wait_pay=rule.wait_pay,
                        force_settle=rule.force_settle,
                        status="OPEN",
                        is_settleable=initial_settleable,
                        settleable_date=initial_settleable_date,
                        created_by=actor_id,
                        updated_by=actor_id,
                    )
                    db.add(commission)
                    summary["created_count"] += 1
                    summary["items"].append(
                        {
                            "case_id": case_id,
                            "agent_id": agent_id,
                            "action": "CREATED",
                            "rule_id": rule.id,
                        }
                    )
                    continue

                if not _commission_is_rewritable(db, existing):
                    summary["skipped_count"] += 1
                    summary["items"].append(
                        {
                            "case_id": case_id,
                            "agent_id": agent_id,
                            "action": "SKIPPED",
                            "reason": "COMMISSION_LOCKED",
                            "rule_id": rule.id,
                            "commission_id": existing.id,
                        }
                    )
                    continue

                existing.agent_id = agent_id
                existing.rule_id = rule.id
                existing.fee_type = fee_type
                existing.base_fee = split_base_fee
                existing.s1_rate = s1_rate
                existing.s1_amount = s1_amount
                existing.s2_rate = s2_rate
                existing.s2_amount = s2_amount
                existing.wait_pay = rule.wait_pay
                existing.force_settle = rule.force_settle
                existing.is_settleable = initial_settleable
                existing.settleable_date = initial_settleable_date
                if not existing.status:
                    existing.status = "OPEN"
                existing.updated_by = actor_id

                summary["updated_count"] += 1
                summary["items"].append(
                    {
                        "case_id": case_id,
                        "agent_id": agent_id,
                        "action": "UPDATED",
                        "rule_id": rule.id,
                        "commission_id": existing.id,
                    }
                )

            current_commissions = (
                db.execute(
                    select(Commission).where(
                        Commission.case_id == case_id,
                        Commission.rule_id == rule.id,
                        Commission.fee_type == fee_type,
                    )
                )
                .scalars()
                .all()
            )
            for existing in current_commissions:
                if existing.agent_id in target_agent_ids:
                    continue
                if not _commission_is_rewritable(db, existing):
                    summary["skipped_count"] += 1
                    summary["items"].append(
                        {
                            "case_id": case_id,
                            "agent_id": existing.agent_id,
                            "action": "SKIPPED",
                            "reason": "COMMISSION_LOCKED",
                            "rule_id": rule.id,
                            "commission_id": existing.id,
                        }
                    )
                    continue
                db.delete(existing)
                summary["deleted_count"] += 1
                summary["items"].append(
                    {
                        "case_id": case_id,
                        "agent_id": existing.agent_id,
                        "action": "DELETED",
                        "rule_id": rule.id,
                        "commission_id": existing.id,
                    }
                )

        summary["status"] = (
            "APPLIED"
            if (summary["created_count"] + summary["updated_count"] + summary["deleted_count"]) > 0
            else "NOOP"
        )
        db.commit()
        return summary

    except BusinessError as exc:
        db.rollback()
        if strict:
            raise
        summary["status"] = "FAILED_NON_BLOCKING"
        summary["error"] = {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        }
        return summary
    except Exception as exc:  # pragma: no cover - defensive path for strict/non-strict mode
        db.rollback()
        if strict:
            raise_business_error(
                "COMMISSION_APPLY_FAILED",
                "Failed to apply commission for bill",
                details={"bill_id": bill_id, "reason": str(exc)},
                status_code=400,
            )
        summary["status"] = "FAILED_NON_BLOCKING"
        summary["error"] = {
            "code": "COMMISSION_APPLY_FAILED",
            "message": "Failed to apply commission for bill",
            "details": {"bill_id": bill_id, "reason": str(exc)},
            "status_code": 400,
        }
        return summary


def _normalize_case_ids(case_ids: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in case_ids:
        value = str(raw).strip()
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _safe_paid_ratio(*, received_amt: Decimal, receivable_amt: Decimal) -> Decimal:
    if receivable_amt <= Decimal("0"):
        return Decimal("0")
    ratio = received_amt / receivable_amt
    if ratio < Decimal("0"):
        return Decimal("0")
    if ratio > Decimal("1"):
        return Decimal("1")
    return ratio


def recompute_commission_settleable(
    db: Session,
    *,
    case_ids: list[str],
    as_of_date: date | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "processed_count": 0,
        "updated_count": 0,
        "unchanged_count": 0,
        "status": "NOOP",
        "items": [],
    }

    try:
        normalized_case_ids = _normalize_case_ids(case_ids)
        if not normalized_case_ids:
            raise_business_error(
                "COMMISSION_CONTEXT_INVALID",
                "case_ids must contain at least one valid case id",
                status_code=400,
            )

        effective_date = as_of_date or date.today()
        commissions = (
            db.execute(select(Commission).where(Commission.case_id.in_(normalized_case_ids)))
            .scalars()
            .all()
        )
        active_commissions = [
            row
            for row in commissions
            if (row.status or "").strip().upper() not in _TERMINAL_COMMISSION_STATUSES
        ]
        summary["processed_count"] = len(active_commissions)

        if not active_commissions:
            return summary

        receipt_rows = db.execute(
            select(
                CaseReceipt.case_id,
                func.coalesce(func.sum(CaseReceipt.receivable_amt), 0),
                func.coalesce(func.sum(CaseReceipt.received_amt), 0),
            )
            .where(
                CaseReceipt.case_id.in_(normalized_case_ids),
                func.upper(func.coalesce(CaseReceipt.fee_type, "")) == _SERVICE_FEE_TYPE,
            )
            .group_by(CaseReceipt.case_id)
        ).all()
        receipt_totals: dict[str, tuple[Decimal, Decimal]] = {
            case_id: (
                _to_decimal(receivable_amt, field_name="case_receipt.receivable_amt"),
                _to_decimal(received_amt, field_name="case_receipt.received_amt"),
            )
            for case_id, receivable_amt, received_amt in receipt_rows
        }

        for row in active_commissions:
            receivable_amt, received_amt = receipt_totals.get(
                row.case_id, (Decimal("0"), Decimal("0"))
            )
            paid_ratio = _safe_paid_ratio(
                received_amt=received_amt,
                receivable_amt=receivable_amt,
            )

            if row.force_settle:
                next_settleable = True
                reason = "FORCE_SETTLE"
            elif row.wait_pay:
                next_settleable = paid_ratio >= Decimal("1")
                reason = "WAIT_PAY_FULL_RECEIPT"
            else:
                next_settleable = True
                reason = "DEFAULT_SETTLEABLE"

            current_settleable = bool(row.is_settleable)
            if next_settleable and not current_settleable:
                next_settleable_date = effective_date
            elif next_settleable and current_settleable:
                next_settleable_date = row.settleable_date
            elif not next_settleable and current_settleable:
                next_settleable_date = None
            else:
                next_settleable_date = row.settleable_date

            changed = (
                current_settleable != next_settleable or row.settleable_date != next_settleable_date
            )
            if changed:
                row.is_settleable = next_settleable
                row.settleable_date = next_settleable_date
                summary["updated_count"] += 1
            else:
                summary["unchanged_count"] += 1

            summary["items"].append(
                {
                    "commission_id": row.id,
                    "case_id": row.case_id,
                    "is_settleable": next_settleable,
                    "settleable_date": next_settleable_date,
                    "paid_ratio": str(paid_ratio),
                    "reason": reason,
                    "action": "UPDATED" if changed else "UNCHANGED",
                }
            )

        summary["status"] = "APPLIED" if summary["updated_count"] > 0 else "NOOP"
        db.commit()
        return summary
    except BusinessError as exc:
        db.rollback()
        if strict:
            raise
        summary["status"] = "FAILED_NON_BLOCKING"
        summary["error"] = {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        }
        return summary
    except Exception as exc:  # pragma: no cover - defensive path
        db.rollback()
        if strict:
            raise_business_error(
                "COMMISSION_RECOMPUTE_FAILED",
                "Failed to recompute commission settleable state",
                details={"reason": str(exc)},
                status_code=400,
            )
        summary["status"] = "FAILED_NON_BLOCKING"
        summary["error"] = {
            "code": "COMMISSION_RECOMPUTE_FAILED",
            "message": "Failed to recompute commission settleable state",
            "details": {"reason": str(exc)},
            "status_code": 400,
        }
        return summary


def _normalize_required_text(value: str | None, *, field_name: str) -> str:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        raise_business_error(
            "COMMISSION_SETTLEMENT_INVALID",
            f"{field_name} is required",
            status_code=400,
        )
    return normalized


def _find_active_settlement_conflict(
    db: Session,
    *,
    agent_id: str,
    currency: str,
    period_from: date | None,
    period_to: date | None,
) -> int | None:
    stmt = select(CommissionSettlement.id).where(
        CommissionSettlement.agent_id == agent_id,
        CommissionSettlement.currency == currency,
        func.upper(CommissionSettlement.status).in_(sorted(_ACTIVE_SETTLEMENT_STATUSES)),
    )
    if period_from is None:
        stmt = stmt.where(CommissionSettlement.period_from.is_(None))
    else:
        stmt = stmt.where(CommissionSettlement.period_from == period_from)

    if period_to is None:
        stmt = stmt.where(CommissionSettlement.period_to.is_(None))
    else:
        stmt = stmt.where(CommissionSettlement.period_to == period_to)

    return db.execute(stmt.order_by(CommissionSettlement.id.asc()).limit(1)).scalar_one_or_none()


def create_commission_settlement(
    db: Session,
    *,
    agent_id: str,
    period_from: date | None,
    period_to: date | None,
    currency: str,
    remark: str | None,
    actor_id: str | None = None,
) -> CommissionSettlement:
    normalized_agent_id = _normalize_required_text(agent_id, field_name="agent_id")
    normalized_currency = _normalize_required_text(currency, field_name="currency").upper()
    normalized_remark = _normalize_optional_text(remark)

    if period_from and period_to and period_from > period_to:
        raise_business_error(
            "COMMISSION_SETTLEMENT_INVALID",
            "period_from must be less than or equal to period_to",
            status_code=400,
        )

    conflict_id = _find_active_settlement_conflict(
        db,
        agent_id=normalized_agent_id,
        currency=normalized_currency,
        period_from=period_from,
        period_to=period_to,
    )
    if conflict_id is not None:
        raise_business_error(
            "COMMISSION_SETTLEMENT_CONFLICT",
            "Settlement batch already exists for same active scope",
            details={"conflict_settlement_id": conflict_id},
            status_code=409,
        )

    settlement = CommissionSettlement(
        settlement_no=None,
        agent_id=normalized_agent_id,
        status="DRAFT",
        currency=normalized_currency,
        period_from=period_from,
        period_to=period_to,
        line_count=0,
        total_amount=Decimal("0"),
        remark=normalized_remark,
        created_by=actor_id,
        updated_by=actor_id,
    )
    db.add(settlement)
    db.flush()
    settlement.settlement_no = f"CS-{date.today():%Y%m%d}-{settlement.id:06d}"
    db.commit()
    db.refresh(settlement)
    return settlement


def _normalized_status(value: str | None) -> str:
    return (value or "").strip().upper()


def _line_amount_for_commission(commission: Commission) -> Decimal:
    s1_amount = (
        Decimal("0")
        if commission.s1_done
        else _to_decimal(commission.s1_amount, field_name="commission.s1_amount")
    )
    s2_amount = (
        Decimal("0")
        if commission.s2_done
        else _to_decimal(commission.s2_amount, field_name="commission.s2_amount")
    )
    return _quantize_money(s1_amount + s2_amount)


def _apply_settlement_completion(commission: Commission, *, actor_id: str | None) -> None:
    _to_decimal(commission.s1_amount, field_name="commission.s1_amount")
    _to_decimal(commission.s2_amount, field_name="commission.s2_amount")

    commission.s1_done = True
    commission.s2_done = True
    if commission.s1_done and commission.s2_done:
        commission.status = "SETTLED"
    elif not _normalize_optional_text(commission.status):
        commission.status = "OPEN"
    commission.updated_by = actor_id


def _normalize_report_time_field(value: str | None) -> str:
    normalized = _normalize_optional_text(value)
    effective = normalized or "line_created_at"
    if effective not in _SETTLEMENT_REPORT_TIME_FIELDS:
        raise_business_error(
            "COMMISSION_REPORT_INVALID",
            "time_field must be one of line_created_at, settleable_date, settlement_period",
            status_code=400,
        )
    return effective


def _to_date_only(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _to_month_bucket(value: date | datetime | None) -> str:
    normalized = _to_date_only(value)
    if normalized is None:
        return _UNKNOWN_TIME_BUCKET
    return normalized.strftime("%Y-%m")


def _resolve_case_filter_id(db: Session, value: str | None) -> str | None:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        return None

    resolved = db.execute(
        select(Case.id)
        .where(or_(Case.id == normalized, Case.case_no == normalized))
        .order_by(Case.id.asc())
        .limit(1)
    ).scalar_one_or_none()
    return resolved or normalized


def get_commission_settlement_report(
    db: Session,
    *,
    agent_id: str | None = None,
    case_id: str | None = None,
    currency: str | None = None,
    settlement_status: str | None = None,
    line_status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    time_field: str = "line_created_at",
) -> dict[str, Any]:
    if date_from and date_to and date_from > date_to:
        raise_business_error(
            "COMMISSION_REPORT_INVALID",
            "date_from must be less than or equal to date_to",
            status_code=400,
        )

    effective_time_field = _normalize_report_time_field(time_field)
    normalized_agent_id = _normalize_optional_text(agent_id)
    normalized_case_id = _resolve_case_filter_id(db, case_id)
    normalized_currency = _normalize_optional_text(currency)
    normalized_settlement_status = _normalize_optional_text(settlement_status)
    normalized_line_status = _normalize_optional_text(line_status)

    stmt = (
        select(CommissionSettleLine, CommissionSettlement, Commission)
        .join(
            CommissionSettlement,
            CommissionSettlement.id == CommissionSettleLine.settlement_id,
        )
        .join(
            Commission,
            Commission.id == CommissionSettleLine.commission_id,
        )
    )

    if normalized_agent_id:
        stmt = stmt.where(
            func.coalesce(Commission.agent_id, CommissionSettlement.agent_id) == normalized_agent_id
        )
    if normalized_case_id:
        stmt = stmt.where(Commission.case_id == normalized_case_id)
    if normalized_currency:
        stmt = stmt.where(
            func.upper(func.coalesce(CommissionSettlement.currency, ""))
            == normalized_currency.upper()
        )
    if normalized_settlement_status:
        stmt = stmt.where(
            func.upper(func.coalesce(CommissionSettlement.status, ""))
            == normalized_settlement_status.upper()
        )
    if normalized_line_status:
        stmt = stmt.where(
            func.upper(func.coalesce(CommissionSettleLine.status, ""))
            == normalized_line_status.upper()
        )

    if effective_time_field == "line_created_at":
        if date_from is not None:
            stmt = stmt.where(
                CommissionSettleLine.created_at >= datetime.combine(date_from, time.min)
            )
        if date_to is not None:
            stmt = stmt.where(
                CommissionSettleLine.created_at <= datetime.combine(date_to, time.max)
            )
    elif effective_time_field == "settleable_date":
        if date_from is not None:
            stmt = stmt.where(
                Commission.settleable_date.is_not(None),
                Commission.settleable_date >= date_from,
            )
        if date_to is not None:
            stmt = stmt.where(
                Commission.settleable_date.is_not(None),
                Commission.settleable_date <= date_to,
            )
    else:
        period_ref = func.coalesce(CommissionSettlement.period_to, CommissionSettlement.period_from)
        if date_from is not None:
            stmt = stmt.where(period_ref.is_not(None), period_ref >= date_from)
        if date_to is not None:
            stmt = stmt.where(period_ref.is_not(None), period_ref <= date_to)

    rows = db.execute(
        stmt.order_by(CommissionSettleLine.created_at.asc(), CommissionSettleLine.id.asc())
    ).all()

    details: list[dict[str, Any]] = []
    by_agent_map: dict[str | None, dict[str, Any]] = {}
    by_case_map: dict[str | None, dict[str, Any]] = {}
    by_time_map: dict[str, dict[str, Any]] = {}
    settlement_ids: set[int] = set()
    total_amount = Decimal("0")

    for line, settlement, commission in rows:
        line_amount = _quantize_money(_to_decimal(line.amount, field_name="settlement_line.amount"))
        agent_value = _normalize_optional_text(commission.agent_id) or _normalize_optional_text(
            settlement.agent_id
        )

        if effective_time_field == "line_created_at":
            bucket_source = line.created_at
        elif effective_time_field == "settleable_date":
            bucket_source = commission.settleable_date
        else:
            bucket_source = settlement.period_to or settlement.period_from
        time_bucket = _to_month_bucket(bucket_source)

        detail = {
            "settlement_id": settlement.id,
            "settlement_no": settlement.settlement_no,
            "commission_id": commission.id,
            "agent_id": agent_value,
            "case_id": commission.case_id,
            "amount": line_amount,
            "currency": settlement.currency,
            "line_status": line.status,
            "settlement_status": settlement.status,
            "s1_done": commission.s1_done,
            "s2_done": commission.s2_done,
            "is_settleable": commission.is_settleable,
            "settleable_date": commission.settleable_date,
            "period_from": settlement.period_from,
            "period_to": settlement.period_to,
            "created_at": line.created_at,
        }
        details.append(detail)
        total_amount += line_amount
        settlement_ids.add(settlement.id)

        if agent_value not in by_agent_map:
            by_agent_map[agent_value] = {
                "agent_id": agent_value,
                "line_count": 0,
                "total_amount": Decimal("0"),
            }
        by_agent_map[agent_value]["line_count"] += 1
        by_agent_map[agent_value]["total_amount"] += line_amount

        case_value = commission.case_id
        if case_value not in by_case_map:
            by_case_map[case_value] = {
                "case_id": case_value,
                "line_count": 0,
                "total_amount": Decimal("0"),
            }
        by_case_map[case_value]["line_count"] += 1
        by_case_map[case_value]["total_amount"] += line_amount

        if time_bucket not in by_time_map:
            by_time_map[time_bucket] = {
                "time_bucket": time_bucket,
                "line_count": 0,
                "total_amount": Decimal("0"),
            }
        by_time_map[time_bucket]["line_count"] += 1
        by_time_map[time_bucket]["total_amount"] += line_amount

    by_agent = sorted(by_agent_map.values(), key=lambda item: item["agent_id"] or "")
    by_case = sorted(by_case_map.values(), key=lambda item: item["case_id"] or "")
    by_time = sorted(
        by_time_map.values(),
        key=lambda item: (item["time_bucket"] == _UNKNOWN_TIME_BUCKET, item["time_bucket"]),
    )
    for entry in by_agent:
        entry["total_amount"] = _quantize_money(entry["total_amount"])
    for entry in by_case:
        entry["total_amount"] = _quantize_money(entry["total_amount"])
    for entry in by_time:
        entry["total_amount"] = _quantize_money(entry["total_amount"])

    summary = {
        "line_count": len(details),
        "settlement_count": len(settlement_ids),
        "agent_count": len(by_agent),
        "case_count": len(by_case),
        "total_amount": _quantize_money(total_amount),
    }

    return {
        "filters": {
            "agent_id": normalized_agent_id,
            "case_id": normalized_case_id,
            "currency": normalized_currency.upper() if normalized_currency else None,
            "settlement_status": (
                normalized_settlement_status.upper() if normalized_settlement_status else None
            ),
            "line_status": normalized_line_status.upper() if normalized_line_status else None,
            "date_from": date_from,
            "date_to": date_to,
            "time_field": effective_time_field,
        },
        "summary": summary,
        "totals": {
            "line_count": summary["line_count"],
            "total_amount": summary["total_amount"],
        },
        "by_agent": by_agent,
        "by_case": by_case,
        "by_time": by_time,
        "details": details,
    }


def generate_commission_settlement_lines(
    db: Session,
    *,
    settlement_id: int,
    case_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    settlement = db.execute(
        select(CommissionSettlement).where(CommissionSettlement.id == settlement_id)
    ).scalar_one_or_none()
    if not settlement:
        raise_business_error(
            "COMMISSION_SETTLEMENT_NOT_FOUND",
            "Settlement batch not found",
            status_code=404,
        )

    if (
        settlement.period_from
        and settlement.period_to
        and settlement.period_from > settlement.period_to
    ):
        raise_business_error(
            "COMMISSION_SETTLEMENT_INVALID",
            "Settlement period range is invalid",
            status_code=400,
        )

    normalized_agent_id = _normalize_optional_text(settlement.agent_id)
    normalized_case_id = _resolve_case_filter_id(db, case_id)
    if not normalized_agent_id:
        raise_business_error(
            "COMMISSION_SETTLEMENT_INVALID",
            "Settlement agent_id is required",
            status_code=400,
        )

    current_status = _normalized_status(settlement.status)
    if current_status not in _SETTLEMENT_GENERATE_ALLOWED_STATUSES:
        raise_business_error(
            "COMMISSION_SETTLEMENT_CONFLICT",
            "Settlement state does not allow line generation",
            details={"status": settlement.status},
            status_code=409,
        )

    commission_stmt = select(Commission).where(
        Commission.is_settleable.is_(True),
        ~func.upper(func.coalesce(Commission.status, "")).in_(
            sorted(_TERMINAL_COMMISSION_STATUSES)
        ),
    )
    if normalized_agent_id.upper() in _UNASSIGNED_AGENT_SENTINELS:
        commission_stmt = commission_stmt.where(Commission.agent_id.is_(None))
    else:
        commission_stmt = commission_stmt.where(Commission.agent_id == normalized_agent_id)
    if normalized_case_id:
        commission_stmt = commission_stmt.where(Commission.case_id == normalized_case_id)
    if settlement.period_from is not None:
        commission_stmt = commission_stmt.where(
            Commission.settleable_date.is_not(None),
            Commission.settleable_date >= settlement.period_from,
        )
    if settlement.period_to is not None:
        commission_stmt = commission_stmt.where(
            Commission.settleable_date.is_not(None),
            Commission.settleable_date <= settlement.period_to,
        )

    candidate_commissions = (
        db.execute(commission_stmt.order_by(Commission.created_at.asc(), Commission.id.asc()))
        .scalars()
        .all()
    )

    eligible_entries: list[tuple[Commission, Decimal]] = []
    for commission in candidate_commissions:
        line_amount = _line_amount_for_commission(commission)
        if line_amount > Decimal("0"):
            eligible_entries.append((commission, line_amount))

    existing_lines = (
        db.execute(
            select(CommissionSettleLine)
            .where(CommissionSettleLine.settlement_id == settlement.id)
            .order_by(CommissionSettleLine.line_no.asc(), CommissionSettleLine.id.asc())
        )
        .scalars()
        .all()
    )

    line_map: dict[int, CommissionSettleLine] = {}
    max_line_no = 0
    for line in existing_lines:
        max_line_no = max(max_line_no, int(line.line_no or 0))
        if line.commission_id in line_map:
            raise_business_error(
                "COMMISSION_SETTLEMENT_CONFLICT",
                "Duplicate settlement lines detected for same commission",
                details={
                    "settlement_id": settlement.id,
                    "commission_id": line.commission_id,
                },
                status_code=409,
            )
        line_map[line.commission_id] = line

    created_count = 0
    updated_count = 0
    for commission, line_amount in sorted(eligible_entries, key=lambda item: item[0].id):
        existing = line_map.get(commission.id)
        if existing is None:
            max_line_no += 1
            line = CommissionSettleLine(
                settlement_id=settlement.id,
                commission_id=commission.id,
                line_no=max_line_no,
                amount=line_amount,
                status="PENDING",
                created_by=actor_id,
                updated_by=actor_id,
            )
            db.add(line)
            _apply_settlement_completion(commission, actor_id=actor_id)
            created_count += 1
            continue

        changed = False
        if _to_decimal(existing.amount, field_name="settlement_line.amount") != line_amount:
            existing.amount = line_amount
            changed = True
        if not _normalize_optional_text(existing.status):
            existing.status = "PENDING"
            changed = True
        if changed:
            existing.updated_by = actor_id
            updated_count += 1
        _apply_settlement_completion(commission, actor_id=actor_id)

    db.flush()
    aggregate = db.execute(
        select(
            func.coalesce(func.count(CommissionSettleLine.id), 0),
            func.coalesce(func.sum(CommissionSettleLine.amount), 0),
        ).where(CommissionSettleLine.settlement_id == settlement.id)
    ).one()

    line_count = int(aggregate[0])
    total_amount = _to_decimal(aggregate[1], field_name="settlement.total_amount")
    settlement.line_count = line_count
    settlement.total_amount = _quantize_money(total_amount)

    if line_count > 0:
        settlement.status = "GENERATED"
    elif current_status == "DRAFT":
        settlement.status = "DRAFT"

    settlement.updated_by = actor_id
    db.commit()
    db.refresh(settlement)

    return {
        "settlement_id": settlement.id,
        "line_count": settlement.line_count,
        "total_amount": settlement.total_amount,
        "created_count": created_count,
        "updated_count": updated_count,
        "status": settlement.status,
    }
