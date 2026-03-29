from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

PAYMENTS_URL = "/api/v1/payments"


def _uid(prefix: str = "PREPAY") -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client, auth_headers, *, name_cn: str) -> dict:
    resp = client.post(
        "/api/v1/clients",
        json={
            "name_cn": name_cn,
            "name_en": f"{name_cn}-EN",
            "client_type": "CORPORATE",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client, auth_headers, *, client_id: str) -> dict:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "预收款报表测试案件",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_rate(client, auth_headers, *, default_amount: str) -> dict:
    resp = client.post(
        "/api/v1/fees/rates",
        json={
            "fee_code": _uid("RATE"),
            "fee_name": "预收款报表测试费用",
            "fee_type": "SERVICE",
            "currency": "CNY",
            "default_amount": default_amount,
            "enabled": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_draft(client, auth_headers, *, case_id: str, client_id: str) -> dict:
    resp = client.post(
        "/api/v1/fees/drafts",
        json={"case_id": case_id, "client_id": client_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_fee_item(client, auth_headers, *, draft_id: str, rate_id: str, unit_price: str) -> None:
    resp = client.post(
        f"/api/v1/fees/drafts/{draft_id}/items",
        json={"rate_id": rate_id, "quantity": 1, "unit_price": unit_price},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text


def _create_bill_from_drafts(client, auth_headers, *, draft_ids: list[str]) -> dict:
    resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": draft_ids, "bill_no": _uid("BILL")},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_payment(
    client,
    auth_headers,
    *,
    client_id: str,
    amount: str,
    pay_date: str,
) -> dict:
    resp = client.post(
        PAYMENTS_URL,
        json={
            "client_id": client_id,
            "amount": amount,
            "pay_no": _uid("PAY"),
            "pay_date": pay_date,
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_payment_line_id(client, auth_headers, *, payment_id: str) -> str:
    resp = client.get(f"{PAYMENTS_URL}/{payment_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    lines = resp.json()["payment_lines"]
    assert lines, "expected payment lines"
    return lines[0]["id"]


def _create_offset(
    client,
    auth_headers,
    *,
    payment_line_id: str,
    bill_id: str,
    amount: str,
) -> dict:
    resp = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line_id,
            "bill_id": bill_id,
            "offset_amt": amount,
            "offset_date": "2026-03-15",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _setup_payment_chain(
    client,
    auth_headers,
    *,
    client_name: str | None = None,
    client_data: dict | None = None,
    payment_amount: str,
    pay_date: str,
    offset_amount: str | None = None,
) -> dict:
    cl = client_data or _create_client(client, auth_headers, name_cn=client_name or _uid("CLI"))
    case = _create_case(client, auth_headers, client_id=cl["id"])
    rate = _create_fee_rate(client, auth_headers, default_amount=payment_amount)
    draft = _create_fee_draft(client, auth_headers, case_id=case["id"], client_id=cl["id"])
    _add_fee_item(
        client, auth_headers, draft_id=draft["id"], rate_id=rate["id"], unit_price=payment_amount
    )
    bill = _create_bill_from_drafts(client, auth_headers, draft_ids=[draft["id"]])
    payment = _create_payment(
        client,
        auth_headers,
        client_id=cl["id"],
        amount=payment_amount,
        pay_date=pay_date,
    )
    payment_line_id = _get_payment_line_id(client, auth_headers, payment_id=payment["id"])
    if offset_amount is not None:
        _create_offset(
            client,
            auth_headers,
            payment_line_id=payment_line_id,
            bill_id=bill["id"],
            amount=offset_amount,
        )
    return {"client": cl, "payment": payment}


def test_payments_report_filters_and_summary(client, auth_headers):
    shared_client = _create_client(client, auth_headers, name_cn="预收客户A")
    unallocated = _setup_payment_chain(
        client,
        auth_headers,
        client_data=shared_client,
        payment_amount="100.00",
        pay_date="2026-03-01",
    )
    partial = _setup_payment_chain(
        client,
        auth_headers,
        client_data=shared_client,
        payment_amount="200.00",
        pay_date="2026-03-05",
        offset_amount="50.00",
    )
    fully_allocated = _setup_payment_chain(
        client,
        auth_headers,
        client_name="预收客户B",
        payment_amount="300.00",
        pay_date="2026-03-10",
        offset_amount="300.00",
    )

    resp = client.get(PAYMENTS_URL, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total"] >= 3
    assert data["prepayment_count"] >= 3
    assert Decimal(str(data["prepayment_total_amount"])) >= Decimal("600.00")
    assert Decimal(str(data["allocated_total_amount"])) >= Decimal("350.00")
    assert Decimal(str(data["remaining_prepayment_balance"])) >= Decimal("150.00")

    our_items = {
        item["id"]: item
        for item in data["items"]
        if item["id"]
        in {
            unallocated["payment"]["id"],
            partial["payment"]["id"],
            fully_allocated["payment"]["id"],
        }
    }
    assert our_items[unallocated["payment"]["id"]]["client_name"] == "预收客户A"
    assert our_items[unallocated["payment"]["id"]]["prepayment_status"] == "UNALLOCATED"
    assert our_items[partial["payment"]["id"]]["prepayment_status"] == "PARTIALLY_ALLOCATED"
    assert our_items[fully_allocated["payment"]["id"]]["prepayment_status"] == "FULLY_ALLOCATED"

    resp = client.get(
        PAYMENTS_URL, params={"client_id": unallocated["client"]["id"]}, headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 2
    assert data["prepayment_count"] == 2
    assert Decimal(str(data["prepayment_total_amount"])) == Decimal("300.00")
    assert Decimal(str(data["allocated_total_amount"])) == Decimal("50.00")
    assert Decimal(str(data["remaining_prepayment_balance"])) == Decimal("250.00")
    assert {item["id"] for item in data["items"]} == {
        unallocated["payment"]["id"],
        partial["payment"]["id"],
    }

    resp = client.get(
        PAYMENTS_URL,
        params={"prepayment_status": "PARTIALLY_ALLOCATED"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == partial["payment"]["id"]
    assert data["items"][0]["prepayment_status"] == "PARTIALLY_ALLOCATED"

    resp = client.get(
        PAYMENTS_URL,
        params={"pay_date_from": "2026-03-02", "pay_date_to": "2026-03-08"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == partial["payment"]["id"]

    resp = client.get(PAYMENTS_URL, params={"has_unapplied_only": True}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert {item["id"] for item in data["items"]} == {
        unallocated["payment"]["id"],
        partial["payment"]["id"],
    }
    assert fully_allocated["payment"]["id"] not in {item["id"] for item in data["items"]}
