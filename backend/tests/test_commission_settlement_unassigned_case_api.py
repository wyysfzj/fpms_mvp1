from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.commission.models import Commission, CommissionSettleLine, CommissionSettlement

UNASSIGNED_AGENT = "UNASSIGNED"


def _create_case(session_factory: sessionmaker, *, case_no: str) -> str:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=case_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="未分配提成结算测试",
        )
        db.add(case)
        db.commit()
        return case.id


def _create_unassigned_commission(
    session_factory: sessionmaker,
    *,
    case_id: str,
    amount: str = "80.00",
) -> int:
    with session_factory() as db:
        commission = Commission(
            case_id=case_id,
            agent_id=None,
            fee_type="SERVICE",
            base_fee=Decimal("800.00"),
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


def _create_settlement(session_factory: sessionmaker) -> int:
    with session_factory() as db:
        settlement = CommissionSettlement(
            settlement_no=f"CS-{uuid4().hex[:8].upper()}",
            agent_id=UNASSIGNED_AGENT,
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


def test_generate_lines_for_unassigned_commission_by_visible_case_no(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    target_case_no = f"RUI{uuid4().hex[:12].upper()}"
    other_case_no = f"RUI{uuid4().hex[:12].upper()}"
    target_case_id = _create_case(session_factory, case_no=target_case_no)
    other_case_id = _create_case(session_factory, case_no=other_case_no)
    target_commission_id = _create_unassigned_commission(
        session_factory,
        case_id=target_case_id,
        amount="80.00",
    )
    other_commission_id = _create_unassigned_commission(
        session_factory,
        case_id=other_case_id,
        amount="25.00",
    )
    settlement_id = _create_settlement(session_factory)

    response = client.post(
        f"/api/v1/commission/settlements/{settlement_id}/generate-lines",
        headers=auth_headers,
        params={"case_id": target_case_no},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["settlement_id"] == settlement_id
    assert payload["line_count"] == 1
    assert payload["created_count"] == 1
    assert payload["status"] == "GENERATED"

    with session_factory() as db:
        generated_commission_ids = set(
            db.execute(
                select(CommissionSettleLine.commission_id).where(
                    CommissionSettleLine.settlement_id == settlement_id
                )
            ).scalars()
        )
        target_commission = db.get(Commission, target_commission_id)

    assert generated_commission_ids == {target_commission_id}
    assert other_commission_id not in generated_commission_ids
    assert target_commission is not None
    assert target_commission.status == "SETTLED"

    report_response = client.get(
        "/api/v1/commission/reports/settlement",
        headers=auth_headers,
        params={"case_id": target_case_no},
    )

    assert report_response.status_code == 200, report_response.text
    report = report_response.json()
    assert report["filters"]["case_id"] == target_case_id
    assert report["summary"]["line_count"] == 1
    assert report["details"][0]["commission_id"] == target_commission_id
    assert report["details"][0]["agent_id"] == UNASSIGNED_AGENT
