from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.billing.models import BadDebtRecovery, BadDebtVoucher, Bill


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_prefix: str) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid(name_prefix), "default_currency": "CNY"},
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
    bill_date: date,
    due_date: date | None,
    currency: str = "CNY",
    bad_debt_status: str = "NONE",
    bad_debt_amount: Decimal | None = None,
    recoveries: list[tuple[Decimal, date, str | None]] | None = None,
) -> str:
    with session_factory() as db:
        bill = Bill(
            id=str(uuid4()),
            bill_no=_uid("BILL"),
            client_id=client_id,
            currency=currency,
            direction="AR",
            status=status,
            bill_date=bill_date,
            due_date=due_date,
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
            recovered_amount = sum((item_amount for item_amount, _, _ in recoveries), Decimal("0"))
            voucher = BadDebtVoucher(
                id=str(uuid4()),
                bill_id=bill.id,
                status=bad_debt_status,
                bad_debt_amount=voucher_amount,
                recovered_amount=recovered_amount,
                bad_debt_date=bill_date + timedelta(days=2),
                remark="billing report fixture",
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


def test_get_bills_returns_billing_report_summary_and_keeps_bad_debt_compatibility(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_a = _create_client(client, auth_headers, name_prefix="BILL-RPT-CLI-A")

    current_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("300.00"),
        balance=Decimal("300.00"),
        status="UNSETTLED",
        bill_date=today - timedelta(days=5),
        due_date=today + timedelta(days=15),
    )
    overdue_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("120.00"),
        balance=Decimal("120.00"),
        status="UNSETTLED",
        bill_date=today - timedelta(days=25),
        due_date=today - timedelta(days=10),
    )
    bad_debt_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("50.00"),
        balance=Decimal("50.00"),
        status="BAD_DEBT",
        bill_date=today - timedelta(days=80),
        due_date=today - timedelta(days=75),
        bad_debt_status="OPEN",
        bad_debt_amount=Decimal("50.00"),
        recoveries=[(Decimal("20.00"), today - timedelta(days=1), "partial recovery")],
    )

    resp = client.get(
        f"/api/v1/bills?client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 3

    summary = payload["summary"]
    assert summary["receivable_bill_count"] == 2
    assert Decimal(str(summary["receivable_amount"])) == Decimal("420.00")
    assert summary["overdue_bill_count"] == 1
    assert Decimal(str(summary["overdue_amount"])) == Decimal("120.00")
    assert summary["bad_debt_bill_count"] == 1
    assert Decimal(str(summary["bad_debt_amount"])) == Decimal("50.00")
    assert Decimal(str(summary["total_recovered_amount"])) == Decimal("20.00")
    assert Decimal(str(summary["remaining_bad_debt_balance"])) == Decimal("30.00")
    assert [bucket["bucket"] for bucket in summary["aging_buckets"]] == [
        "CURRENT",
        "0-30",
        "31-60",
        "61-90",
        "90+",
    ]
    assert summary["aging_buckets"][0]["bill_count"] == 1
    assert Decimal(str(summary["aging_buckets"][0]["amount"])) == Decimal("300.00")
    assert summary["aging_buckets"][1]["bill_count"] == 1
    assert Decimal(str(summary["aging_buckets"][1]["amount"])) == Decimal("120.00")
    assert summary["aging_buckets"][2]["bill_count"] == 0
    assert Decimal(str(summary["aging_buckets"][2]["amount"])) == Decimal("0.00")

    # Keep the previous flat bad-debt fields for compatibility.
    assert payload["bad_debt_bill_count"] == summary["bad_debt_bill_count"]
    assert Decimal(str(payload["bad_debt_amount"])) == Decimal("50.00")
    assert Decimal(str(payload["total_recovered_amount"])) == Decimal("20.00")
    assert Decimal(str(payload["remaining_bad_debt_balance"])) == Decimal("30.00")

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
        "days_past_due",
        "aging_bucket",
        "is_overdue",
        "is_bad_debt",
    }
    assert all(set(item) == expected_item_keys for item in payload["items"])
    item_map = {item["id"]: item for item in payload["items"]}
    assert item_map[current_bill_id]["aging_bucket"] == "CURRENT"
    assert item_map[current_bill_id]["is_overdue"] is False
    assert item_map[overdue_bill_id]["aging_bucket"] == "0-30"
    assert item_map[overdue_bill_id]["is_overdue"] is True
    assert item_map[bad_debt_bill_id]["is_bad_debt"] is True


def test_get_bills_supports_billing_report_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_a = _create_client(client, auth_headers, name_prefix="BILL-RPT-FLT-A")

    current_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("300.00"),
        balance=Decimal("300.00"),
        status="UNSETTLED",
        bill_date=today - timedelta(days=5),
        due_date=today + timedelta(days=15),
    )
    overdue_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("120.00"),
        balance=Decimal("120.00"),
        status="UNSETTLED",
        bill_date=today - timedelta(days=25),
        due_date=today - timedelta(days=10),
    )
    usd_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("80.00"),
        balance=Decimal("80.00"),
        status="PARTIALLY_SETTLED",
        bill_date=today - timedelta(days=60),
        due_date=today - timedelta(days=40),
        currency="USD",
    )
    bad_debt_bill_id = _insert_bill(
        session_factory,
        client_id=client_a,
        amount=Decimal("50.00"),
        balance=Decimal("50.00"),
        status="BAD_DEBT",
        bill_date=today - timedelta(days=80),
        due_date=today - timedelta(days=75),
        bad_debt_status="OPEN",
        bad_debt_amount=Decimal("50.00"),
    )

    client_filtered = client.get(
        f"/api/v1/bills?client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert client_filtered.status_code == 200, client_filtered.text
    client_payload = client_filtered.json()
    assert client_payload["total"] == 4
    assert {item["id"] for item in client_payload["items"]} == {
        current_bill_id,
        overdue_bill_id,
        usd_bill_id,
        bad_debt_bill_id,
    }

    status_filtered = client.get(
        f"/api/v1/bills?status=UNSETTLED&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert status_filtered.status_code == 200, status_filtered.text
    status_payload = status_filtered.json()
    assert status_payload["total"] == 2
    assert {item["id"] for item in status_payload["items"]} == {current_bill_id, overdue_bill_id}

    currency_filtered = client.get(
        f"/api/v1/bills?currency=USD&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert currency_filtered.status_code == 200, currency_filtered.text
    currency_payload = currency_filtered.json()
    assert currency_payload["total"] == 1
    assert [item["id"] for item in currency_payload["items"]] == [usd_bill_id]

    overdue_filtered = client.get(
        f"/api/v1/bills?is_overdue=true&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert overdue_filtered.status_code == 200, overdue_filtered.text
    overdue_payload = overdue_filtered.json()
    assert overdue_payload["total"] == 2
    assert {item["id"] for item in overdue_payload["items"]} == {
        overdue_bill_id,
        usd_bill_id,
    }
    assert overdue_payload["summary"]["overdue_bill_count"] == 2
    assert Decimal(str(overdue_payload["summary"]["overdue_amount"])) == Decimal("200.00")

    aging_filtered = client.get(
        f"/api/v1/bills?aging_bucket=0-30&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert aging_filtered.status_code == 200, aging_filtered.text
    aging_payload = aging_filtered.json()
    assert aging_payload["total"] == 1
    assert [item["id"] for item in aging_payload["items"]] == [overdue_bill_id]
    assert aging_payload["items"][0]["aging_bucket"] == "0-30"

    bad_debt_filtered = client.get(
        f"/api/v1/bills?is_bad_debt=true&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert bad_debt_filtered.status_code == 200, bad_debt_filtered.text
    bad_debt_payload = bad_debt_filtered.json()
    assert bad_debt_payload["total"] == 1
    assert [item["id"] for item in bad_debt_payload["items"]] == [bad_debt_bill_id]
    assert bad_debt_payload["summary"]["bad_debt_bill_count"] == 1

    date_filtered = client.get(
        f"/api/v1/bills?bill_date_from={today - timedelta(days=30)}&bill_date_to={today - timedelta(days=1)}&client_id={client_a}&page=1&page_size=20",
        headers=auth_headers,
    )
    assert date_filtered.status_code == 200, date_filtered.text
    date_payload = date_filtered.json()
    assert date_payload["total"] == 2
    assert {item["id"] for item in date_payload["items"]} == {current_bill_id, overdue_bill_id}
