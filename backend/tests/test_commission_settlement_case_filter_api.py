from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.commission.models import Commission, CommissionSettleLine, CommissionSettlement

TARGET_CASE_NO = "RUI202605100035"


def _create_case(session_factory: sessionmaker, *, case_no: str) -> str:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=case_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="提成结算案件筛选测试",
        )
        db.add(case)
        db.commit()
        return case.id


def _create_commission(
    session_factory: sessionmaker,
    *,
    case_id: str,
    agent_id: str,
    amount: str = "100.00",
) -> int:
    with session_factory() as db:
        commission = Commission(
            case_id=case_id,
            agent_id=agent_id,
            fee_type="SERVICE",
            base_fee=Decimal("1000.00"),
            s1_rate=Decimal("0.10"),
            s1_amount=Decimal(amount),
            s1_done=False,
            s2_rate=Decimal("0"),
            s2_amount=Decimal("0"),
            s2_done=False,
            wait_pay=False,
            force_settle=False,
            status="OPEN",
            is_settleable=True,
            settleable_date=date(2026, 5, 10),
        )
        db.add(commission)
        db.commit()
        db.refresh(commission)
        return commission.id


def _create_settlement(session_factory: sessionmaker, *, agent_id: str) -> int:
    with session_factory() as db:
        settlement = CommissionSettlement(
            settlement_no=f"CS-{uuid4().hex[:8].upper()}",
            agent_id=agent_id,
            status="DRAFT",
            currency="CNY",
            period_from=date(2026, 5, 1),
            period_to=date(2026, 5, 31),
            line_count=0,
            total_amount=Decimal("0"),
        )
        db.add(settlement)
        db.commit()
        db.refresh(settlement)
        return settlement.id


def _create_settlement_line(
    session_factory: sessionmaker,
    *,
    settlement_id: int,
    commission_id: int,
    amount: str,
    line_no: int,
) -> None:
    with session_factory() as db:
        line = CommissionSettleLine(
            settlement_id=settlement_id,
            commission_id=commission_id,
            line_no=line_no,
            amount=Decimal(amount),
            status="PENDING",
        )
        db.add(line)
        settlement = db.execute(
            select(CommissionSettlement).where(CommissionSettlement.id == settlement_id)
        ).scalar_one()
        settlement.line_count = 1
        settlement.total_amount += Decimal(amount)
        db.commit()


def test_settlement_report_resolves_case_number_in_case_id_filter(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    agent_id = f"AGT-{uuid4().hex[:8].upper()}"
    target_case_id = _create_case(session_factory, case_no=TARGET_CASE_NO)
    other_case_id = _create_case(session_factory, case_no="RUI202605100099")
    target_commission_id = _create_commission(
        session_factory,
        case_id=target_case_id,
        agent_id=agent_id,
        amount="100.00",
    )
    other_commission_id = _create_commission(
        session_factory,
        case_id=other_case_id,
        agent_id=agent_id,
        amount="25.00",
    )
    settlement_id = _create_settlement(session_factory, agent_id=agent_id)
    _create_settlement_line(
        session_factory,
        settlement_id=settlement_id,
        commission_id=target_commission_id,
        amount="100.00",
        line_no=1,
    )
    _create_settlement_line(
        session_factory,
        settlement_id=settlement_id,
        commission_id=other_commission_id,
        amount="25.00",
        line_no=2,
    )

    response = client.get(
        "/api/v1/commission/reports/settlement",
        headers=auth_headers,
        params={"case_id": TARGET_CASE_NO},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["filters"]["case_id"] == target_case_id
    assert payload["totals"] == {"line_count": 1, "total_amount": "100.00"}
    assert [detail["case_id"] for detail in payload["details"]] == [target_case_id]


def test_generate_lines_resolves_case_number_in_case_id_filter(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    agent_id = f"AGT-{uuid4().hex[:8].upper()}"
    target_case_id = _create_case(session_factory, case_no=TARGET_CASE_NO)
    other_case_id = _create_case(session_factory, case_no="RUI202605100100")
    target_commission_id = _create_commission(
        session_factory,
        case_id=target_case_id,
        agent_id=agent_id,
        amount="100.00",
    )
    other_commission_id = _create_commission(
        session_factory,
        case_id=other_case_id,
        agent_id=agent_id,
        amount="25.00",
    )
    settlement_id = _create_settlement(session_factory, agent_id=agent_id)

    response = client.post(
        f"/api/v1/commission/settlements/{settlement_id}/generate-lines",
        headers=auth_headers,
        params={"case_id": TARGET_CASE_NO},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["settlement_id"] == settlement_id
    assert payload["line_count"] == 1
    assert payload["created_count"] == 1

    with session_factory() as db:
        generated_commission_ids = set(
            db.execute(
                select(CommissionSettleLine.commission_id).where(
                    CommissionSettleLine.settlement_id == settlement_id
                )
            ).scalars()
        )

    assert generated_commission_ids == {target_commission_id}
    assert other_commission_id not in generated_commission_ids
