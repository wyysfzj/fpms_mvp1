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
    status: str,
    bad_debt_status: str = "NONE",
    bad_debt_amount: Decimal | None = None,
    recoveries: list[tuple[Decimal, date, str | None]] | None = None,
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
            bad_debt_substatus="MANUAL_MARK" if bad_debt_status != "NONE" else None,
        )
        db.add(bill)
        db.flush()

        if bad_debt_status != "NONE":
            voucher_amount = bad_debt_amount if bad_debt_amount is not None else balance
            recoveries = recoveries or []
            recovered_amount = sum((amount for amount, _, _ in recoveries), Decimal("0"))
            voucher = BadDebtVoucher(
                id=str(uuid4()),
                bill_id=bill.id,
                status=bad_debt_status,
                bad_debt_amount=voucher_amount,
                recovered_amount=recovered_amount,
                bad_debt_date=date(2026, 5, 1),
                remark="bad debt report fixture",
            )
            db.add(voucher)
            db.flush()
            for recovery_amount, recovery_date, remark in recoveries:
                db.add(
                    BadDebtRecovery(
                        id=str(uuid4()),
                        voucher_id=voucher.id,
                        recovery_amount=recovery_amount,
                        recovery_date=recovery_date,
                        remark=remark,
                    )
                )

        db.commit()
        return bill.id


def test_get_bills_supports_bad_debt_status_filter_and_summary(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    normal_bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("100.00"),
        balance=Decimal("100.00"),
        status="UNSETTLED",
    )
    open_bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("200.00"),
        balance=Decimal("50.00"),
        status="BAD_DEBT",
        bad_debt_status="OPEN",
        bad_debt_amount=Decimal("50.00"),
        recoveries=[(Decimal("10.00"), date(2026, 5, 10), "first recovery")],
    )
    closed_bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("300.00"),
        balance=Decimal("0.00"),
        status="BAD_DEBT",
        bad_debt_status="CLOSED",
        bad_debt_amount=Decimal("80.00"),
        recoveries=[
            (Decimal("30.00"), date(2026, 5, 11), "partial recovery"),
            (Decimal("50.00"), date(2026, 5, 12), "final recovery"),
        ],
    )

    resp = client.get("/api/v1/bills", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 3
    assert payload["bad_debt_bill_count"] == 2
    assert Decimal(str(payload["bad_debt_amount"])) == Decimal("130.00")
    assert Decimal(str(payload["total_recovered_amount"])) == Decimal("90.00")
    assert Decimal(str(payload["remaining_bad_debt_balance"])) == Decimal("40.00")

    expected_item_keys = {
        "id",
        "bill_no",
        "client_id",
        "client_name",
        "currency",
        "status",
        "amount",
        "balance",
        "bill_date",
        "due_date",
    }
    assert all(expected_item_keys <= set(item) for item in payload["items"])

    filtered_resp = client.get(
        "/api/v1/bills?bad_debt_status=OPEN&page=1&page_size=20",
        headers=auth_headers,
    )
    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_payload = filtered_resp.json()

    assert filtered_payload["total"] == 1
    assert filtered_payload["bad_debt_bill_count"] == 1
    assert Decimal(str(filtered_payload["bad_debt_amount"])) == Decimal("50.00")
    assert Decimal(str(filtered_payload["total_recovered_amount"])) == Decimal("10.00")
    assert Decimal(str(filtered_payload["remaining_bad_debt_balance"])) == Decimal("40.00")
    assert [item["id"] for item in filtered_payload["items"]] == [open_bill_id]

    closed_resp = client.get(
        "/api/v1/bills?bad_debt_status=CLOSED&page=1&page_size=20",
        headers=auth_headers,
    )
    assert closed_resp.status_code == 200, closed_resp.text
    closed_payload = closed_resp.json()

    assert closed_payload["total"] == 1
    assert closed_payload["bad_debt_bill_count"] == 1
    assert Decimal(str(closed_payload["bad_debt_amount"])) == Decimal("80.00")
    assert Decimal(str(closed_payload["total_recovered_amount"])) == Decimal("80.00")
    assert Decimal(str(closed_payload["remaining_bad_debt_balance"])) == Decimal("0.00")
    assert [item["id"] for item in closed_payload["items"]] == [closed_bill_id]
    assert normal_bill_id not in {item["id"] for item in closed_payload["items"]}
