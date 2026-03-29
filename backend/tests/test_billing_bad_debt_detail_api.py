from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.billing.models import BadDebtRecovery, BadDebtVoucher, Bill


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("BD-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _insert_bill(
    session_factory: sessionmaker,
    *,
    client_id: str,
    amount: Decimal,
    balance: Decimal,
    status: str = "UNSETTLED",
    bad_debt_status: str = "NONE",
    bad_debt_substatus: str | None = None,
) -> str:
    with session_factory() as db:
        bill = Bill(
            id=str(uuid4()),
            bill_no=_uid("BILL"),
            client_id=client_id,
            currency="CNY",
            direction="AR",
            status=status,
            bill_date=date(2026, 4, 1),
            due_date=date(2026, 4, 30),
            total_gov=Decimal("0"),
            total_service=amount,
            total_misc=Decimal("0"),
            amount=amount,
            balance=balance,
            bad_debt_status=bad_debt_status,
            bad_debt_substatus=bad_debt_substatus,
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill.id


def test_bill_detail_includes_bad_debt_chain(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("500.00"),
        balance=Decimal("150.00"),
        status="PARTIALLY_SETTLED",
        bad_debt_status="OPEN",
        bad_debt_substatus="PARTIAL_TRANSFER",
    )

    with session_factory() as db:
        voucher = BadDebtVoucher(
            id=str(uuid4()),
            bill_id=bill_id,
            status="OPEN",
            bad_debt_amount=Decimal("150.00"),
            recovered_amount=Decimal("40.00"),
            bad_debt_date=date(2026, 5, 1),
            remark="write-off the remaining balance",
        )
        db.add(voucher)
        db.flush()
        db.add_all(
            [
                BadDebtRecovery(
                    id=str(uuid4()),
                    voucher_id=voucher.id,
                    recovery_amount=Decimal("10.00"),
                    recovery_date=date(2026, 5, 10),
                    remark="first recovery",
                ),
                BadDebtRecovery(
                    id=str(uuid4()),
                    voucher_id=voucher.id,
                    recovery_amount=Decimal("30.00"),
                    recovery_date=date(2026, 5, 20),
                    remark="second recovery",
                ),
            ]
        )
        db.commit()

    resp = client.get(f"/api/v1/bills/{bill_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["id"] == bill_id
    assert payload["bad_debt_status"] == "OPEN"
    assert payload["bad_debt_substatus"] == "PARTIAL_TRANSFER"
    assert payload["bad_debt_voucher"]["bill_id"] == bill_id
    assert payload["bad_debt_voucher"]["status"] == "OPEN"
    assert Decimal(str(payload["bad_debt_voucher"]["bad_debt_amount"])) == Decimal("150.00")
    assert Decimal(str(payload["bad_debt_voucher"]["recovered_amount"])) == Decimal("40.00")
    assert Decimal(str(payload["bad_debt_total_recovered"])) == Decimal("40.00")
    assert Decimal(str(payload["bad_debt_remaining_amount"])) == Decimal("110.00")
    assert len(payload["bad_debt_recoveries"]) == 2
    assert payload["bad_debt_recoveries"][0]["remark"] == "first recovery"
    assert payload["bad_debt_recoveries"][1]["remark"] == "second recovery"


def test_bill_detail_without_bad_debt_chain_returns_empty_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("200.00"),
        balance=Decimal("200.00"),
    )

    resp = client.get(f"/api/v1/bills/{bill_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["bad_debt_status"] == "NONE"
    assert payload["bad_debt_substatus"] is None
    assert payload["bad_debt_voucher"] is None
    assert payload["bad_debt_recoveries"] == []
    assert Decimal(str(payload["bad_debt_total_recovered"])) == Decimal("0")
    assert Decimal(str(payload["bad_debt_remaining_amount"])) == Decimal("0")
