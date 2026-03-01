from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cases.models import Case
from app.modules.cases.service import create_consulting_or_search_case
from app.modules.fees.service import generate_consulting_fee_draft_strategy

_CONSULTING_CASE_TYPES = {"CONSULTING", "SEARCH"}


def create_consulting_case(
    db: Session,
    *,
    case_no: str | None,
    case_type: str | None,
    client_id: str | None,
    title_cn: str | None,
    primary_agent_id: str | None,
    recv_date: date | None,
    actor_id: str | None = None,
) -> Case:
    return create_consulting_or_search_case(
        db,
        case_no=case_no,
        case_type=case_type,
        client_id=client_id,
        title_cn=title_cn,
        primary_agent_id=primary_agent_id,
        recv_date=recv_date,
        actor_id=actor_id,
    )


def generate_consulting_fee_draft(
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
    return generate_consulting_fee_draft_strategy(
        db,
        case_id=case_id,
        mode=mode,
        currency=currency,
        fixed_fee=fixed_fee,
        hourly_lines=hourly_lines,
        misc_lines=misc_lines,
        actor_id=actor_id,
    )


def filter_consulting_search_case_ids(db: Session, case_ids: list[str]) -> list[str]:
    normalized_case_ids = sorted(
        {str(case_id).strip() for case_id in case_ids if str(case_id).strip()}
    )
    if not normalized_case_ids:
        return []

    rows = db.execute(select(Case.id, Case.case_type).where(Case.id.in_(normalized_case_ids))).all()
    matched = [
        case_id
        for case_id, case_type in rows
        if (case_type or "").strip().upper() in _CONSULTING_CASE_TYPES
    ]
    return sorted(matched)
