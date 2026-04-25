from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.commission.models import Commission
from app.modules.masterdata.clients.models import Client


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _insert_case_commission(
    session_factory: sessionmaker,
    *,
    case_no: str,
) -> tuple[str, int]:
    with session_factory() as db:
        client = Client(name_cn=_uid("客户"), default_currency="CNY")
        db.add(client)
        db.flush()

        case = Case(
            case_no=case_no,
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client.id,
            title_cn="提成查询案件",
        )
        db.add(case)
        db.flush()

        commission = Commission(
            case_id=case.id,
            agent_id=_uid("AGT"),
            fee_type="SERVICE",
            base_fee=Decimal("1000.00"),
            s1_rate=Decimal("0.10"),
            s1_amount=Decimal("100.00"),
            s1_done=False,
            s2_rate=Decimal("0.05"),
            s2_amount=Decimal("50.00"),
            s2_done=False,
            wait_pay=False,
            force_settle=False,
            status="OPEN",
            is_settleable=True,
            settleable_date=date(2026, 4, 20),
        )
        db.add(commission)
        db.commit()
        db.refresh(commission)
        return case.id, commission.id


def test_commission_list_filters_by_case_no_and_returns_case_no(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    matched_case_no = _uid("COM-Q-A")
    unmatched_case_no = _uid("COM-Q-B")
    matched_case_id, matched_commission_id = _insert_case_commission(
        session_factory,
        case_no=matched_case_no,
    )
    _insert_case_commission(session_factory, case_no=unmatched_case_no)

    response = client.get(
        "/api/v1/commission",
        headers=auth_headers,
        params={"case_no": matched_case_no, "page": 1, "page_size": 20},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["id"] == matched_commission_id
    assert item["case_id"] == matched_case_id
    assert item["case_no"] == matched_case_no
