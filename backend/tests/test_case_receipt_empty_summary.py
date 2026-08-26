from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.billing.models import Bill, BillItem, CaseReceipt
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _database_snapshot(
    session_factory: sessionmaker,
    *,
    client_id: str,
    case_id: str,
) -> dict[str, object]:
    with session_factory() as db:
        return {
            "counts": {
                table.name: db.scalar(select(func.count()).select_from(table))
                for table in Base.metadata.sorted_tables
            },
            "client": dict(
                db.execute(
                    select(Client.__table__).where(Client.id == client_id)
                ).mappings().one()
            ),
            "case": dict(
                db.execute(select(Case.__table__).where(Case.id == case_id))
                .mappings()
                .one()
            ),
        }


def test_existing_case_without_billing_returns_read_only_usd_zero_summary(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        client_row = Client(name_cn=_uid("空摘要客户"), default_currency="USD")
        db.add(client_row)
        db.flush()
        case = Case(
            case_no=_uid("CASE"),
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_row.id,
            title_cn="空回款摘要测试案件",
        )
        db.add(case)
        db.commit()
        client_id = client_row.id
        case_id = case.id

    before = _database_snapshot(
        session_factory,
        client_id=client_id,
        case_id=case_id,
    )
    assert before["counts"][Bill.__tablename__] == 0
    assert before["counts"][BillItem.__tablename__] == 0
    assert before["counts"][CaseReceipt.__tablename__] == 0

    response = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)

    after = _database_snapshot(
        session_factory,
        client_id=client_id,
        case_id=case_id,
    )
    assert after == before
    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": case_id,
        "case_id": case_id,
        "fee_type": None,
        "currency": "USD",
        "receivable_amt": "0.00",
        "received_amt": "0.00",
        "last_receipt_date": None,
        "fee_code": None,
        "fee_name": None,
        "year_no": None,
        "due_date": None,
        "is_arrears": False,
        "is_prepayment": False,
        "is_commissionable": False,
        "invoice_no": None,
        "remark": None,
        "bills": [],
    }


def test_missing_case_or_missing_authoritative_currency_remains_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    missing = client.get(
        f"/api/v1/cases/{uuid4()}/receipts",
        headers=auth_headers,
    )
    assert missing.status_code == 404

    with session_factory() as db:
        client_row = Client(name_cn=_uid("无币种客户"), default_currency="")
        db.add(client_row)
        db.flush()
        case = Case(
            case_no=_uid("CASE"),
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_row.id,
            title_cn="无权威币种测试案件",
        )
        db.add(case)
        db.commit()
        case_id = case.id

    no_currency = client.get(
        f"/api/v1/cases/{case_id}/receipts",
        headers=auth_headers,
    )
    assert no_currency.status_code == 404
