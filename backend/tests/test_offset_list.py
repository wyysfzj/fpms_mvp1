"""Tests for GET /api/v1/offsets list endpoint (P0-4)."""

from __future__ import annotations

from uuid import uuid4

OFFSETS_URL = "/api/v1/offsets"
BILLS_URL = "/api/v1/bills"


# ── Helpers (reused from test_b5_billing_polish.py pattern) ──────────────


def _create_client(client, auth_headers) -> dict:
    payload = {
        "name_cn": f"测试客户-{uuid4().hex[:6]}",
        "short_code": f"TC{uuid4().hex[:4].upper()}",
        "client_type": "COMPANY",
    }
    resp = client.post("/api/v1/clients", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client, auth_headers, client_id: str) -> dict:
    payload = {
        "case_no": f"CASE-OFF-{uuid4().hex[:6]}",
        "fee_reduction": "0",
        "client_id": client_id,
        "case_type": "NORMAL",
    }
    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_rate(client, auth_headers, default_amount: str = "1000.00") -> dict:
    payload = {
        "fee_code": f"OFF-{uuid4().hex[:6]}",
        "fee_name": "冲销测试费",
        "fee_type": "SERVICE",
        "currency": "CNY",
        "default_amount": default_amount,
    }
    resp = client.post("/api/v1/fees/rates", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_fee_draft(client, auth_headers, case_id: str, client_id: str) -> dict:
    payload = {"case_id": case_id, "client_id": client_id, "currency": "CNY"}
    resp = client.post("/api/v1/fees/drafts", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_fee_item(client, auth_headers, draft_id: str, rate_id: str, unit_price: str) -> dict:
    payload = {
        "rate_id": rate_id,
        "quantity": 1,
        "unit_price": unit_price,
    }
    resp = client.post(f"/api/v1/fees/drafts/{draft_id}/items", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_bill_from_drafts(client, auth_headers, draft_ids: list[str]) -> dict:
    resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": draft_ids, "bill_no": f"BILL-OFF-{uuid4().hex[:6]}"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_payment(client, auth_headers, client_id: str, amount: str) -> dict:
    payload = {
        "client_id": client_id,
        "amount": amount,
        "pay_date": "2026-03-20",
        "pay_no": f"PAY-OFF-{uuid4().hex[:6]}",
        "currency": "CNY",
    }
    resp = client.post("/api/v1/payments", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_payment_line_id(client, auth_headers, payment_id: str) -> str:
    resp = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert resp.status_code == 200
    lines = resp.json()["payment_lines"]
    assert len(lines) > 0, "No payment lines found"
    return lines[0]["id"]


def _create_offset(client, auth_headers, payment_line_id: str, bill_id: str, amount: str) -> dict:
    payload = {
        "payment_line_id": payment_line_id,
        "bill_id": bill_id,
        "offset_amt": amount,
        "offset_date": "2026-03-20",
    }
    resp = client.post(OFFSETS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Offset creation failed: {resp.text}"
    return resp.json()


def _setup_billing_chain(client, auth_headers, fee_amount: str = "1000.00") -> dict:
    """Create client -> case -> rate -> draft -> item -> bill -> payment -> offset."""
    cl = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=cl["id"])
    rate = _create_fee_rate(client, auth_headers, default_amount=fee_amount)
    draft = _create_fee_draft(client, auth_headers, case["id"], cl["id"])
    _add_fee_item(client, auth_headers, draft["id"], rate["id"], unit_price=fee_amount)
    bill = _create_bill_from_drafts(client, auth_headers, [draft["id"]])
    payment = _create_payment(client, auth_headers, cl["id"], fee_amount)
    payment_line_id = _get_payment_line_id(client, auth_headers, payment["id"])
    offset = _create_offset(client, auth_headers, payment_line_id, bill["id"], fee_amount)
    return {"client": cl, "case": case, "bill": bill, "offset": offset}


# ── Tests ────────────────────────────────────────────────────────────────


def test_list_offsets_empty(client, auth_headers):
    """GET /offsets returns paginated result (may include offsets from other tests)."""
    resp = client.get(OFFSETS_URL, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


def test_list_offsets_with_data(client, auth_headers):
    """GET /offsets returns offset with enriched bill_no."""
    chain = _setup_billing_chain(client, auth_headers)
    offset_id = chain["offset"]["id"]
    bill_id = chain["bill"]["id"]

    resp = client.get(OFFSETS_URL, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    our_offset = next((o for o in data["items"] if o["id"] == offset_id), None)
    assert our_offset is not None, f"Offset {offset_id} not found in list"

    assert our_offset["bill_id"] == bill_id
    assert our_offset["bill_no"] is not None
    assert "offset_amt" in our_offset
    assert "is_reversed" in our_offset
    assert our_offset["is_reversed"] is False
    assert "created_at" in our_offset


def test_list_offsets_filter_by_bill_id(client, auth_headers):
    """GET /offsets?bill_id=X returns only offsets for that bill."""
    chain = _setup_billing_chain(client, auth_headers)
    bill_id = chain["bill"]["id"]
    offset_id = chain["offset"]["id"]

    resp = client.get(OFFSETS_URL, params={"bill_id": bill_id}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total"] >= 1
    assert all(o["bill_id"] == bill_id for o in data["items"])
    assert any(o["id"] == offset_id for o in data["items"])


def test_list_offsets_filter_by_is_reversed(client, auth_headers):
    """GET /offsets?is_reversed=false returns only non-reversed offsets."""
    chain = _setup_billing_chain(client, auth_headers)

    resp = client.get(OFFSETS_URL, params={"is_reversed": False}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(o["is_reversed"] is False for o in data["items"])

    client.post(f"{OFFSETS_URL}/{chain['offset']['id']}/reverse", headers=auth_headers)

    resp = client.get(OFFSETS_URL, params={"is_reversed": True}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    reversed_ids = [o["id"] for o in data["items"]]
    assert chain["offset"]["id"] in reversed_ids


def test_list_offsets_pagination(client, auth_headers):
    """GET /offsets?page=1&page_size=1 returns paginated results."""
    _setup_billing_chain(client, auth_headers)

    resp = client.get(OFFSETS_URL, params={"page": 1, "page_size": 1}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert len(data["items"]) <= 1


def test_list_offsets_unauthorized(client):
    """GET /offsets without auth returns 401."""
    resp = client.get(OFFSETS_URL)
    assert resp.status_code == 401
