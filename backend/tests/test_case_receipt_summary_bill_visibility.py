from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.billing.models import Bill, BillItem, CaseReceipt
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def test_case_receipt_summary_includes_bills_without_manual_receipt(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        client_row = Client(name_cn=_uid("账单客户"), default_currency="CNY")
        db.add(client_row)
        db.flush()

        case = Case(
            case_no=_uid("CASE"),
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_row.id,
            title_cn="账单可见性测试案件",
        )
        db.add(case)
        db.flush()

        bill = Bill(
            bill_no=_uid("BILL"),
            client_id=client_row.id,
            currency="CNY",
            direction="AR",
            status="UNSETTLED",
            bill_date=date(2026, 5, 1),
            total_service=Decimal("880.00"),
            amount=Decimal("880.00"),
            balance=Decimal("880.00"),
        )
        db.add(bill)
        db.flush()

        db.add(
            BillItem(
                bill_id=bill.id,
                case_id=case.id,
                fee_code="LOCKED-DRAFT-SVC",
                fee_name="锁定草稿服务费",
                fee_type="SERVICE",
                amount=Decimal("880.00"),
            )
        )
        db.commit()

        receipt_count = db.query(CaseReceipt).filter(CaseReceipt.case_id == case.id).count()
        assert receipt_count == 0
        case_id = case.id
        bill_id = bill.id
        bill_no = bill.bill_no

    response = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["case_id"] == case_id
    assert payload["receivable_amt"] == "880.00"
    assert payload["received_amt"] == "0.00"
    assert payload["currency"] == "CNY"
    assert payload["is_arrears"] is True
    assert len(payload["bills"]) == 1
    assert payload["bills"][0] == {
        "id": bill_id,
        "bill_no": bill_no,
        "status": "UNSETTLED",
        "amount": "880.00",
        "balance": "880.00",
        "issue_date": "2026-05-01",
    }
