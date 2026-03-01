"""B5 — CaseReceipt Enrichment + Billing Polish — Tests.

Covers:
  T2a: CaseReceipt new fields (fee_code, year_no, is_arrears, invoice_no, is_commissionable)
  T2b: CaseReceipt backward compat — null values for new fields
  T3:  Offset reversal happy path — full flow with bill balance/status restored
  T4:  Offset reversal partial — two offsets, reverse one, bill partially settled
  T5:  Double reversal blocked — 400 error
  T6:  Offset not found — 404 error
  T7:  Payment line balance restored after reversal
  T8:  CaseReceipt received_amt reversed after offset reversal
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.billing.models import CaseReceipt, PaymentLine

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CLIENTS_URL = "/api/v1/clients"
CASES_URL = "/api/v1/cases"
FEE_RATES_URL = "/api/v1/fees/rates"
FEE_DRAFTS_URL = "/api/v1/fees/drafts"
BILLS_FROM_DRAFTS_URL = "/api/v1/bills/from-drafts"
PAYMENTS_URL = "/api/v1/payments"
OFFSETS_URL = "/api/v1/offsets"


def _uid(prefix: str = "B5") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# Helper: full billing setup chain
# ---------------------------------------------------------------------------
def _create_client(client, auth_headers, **overrides) -> dict:
    payload = {
        "name_cn": f"测试客户-{_uid('CLI')}",
        "name_en": "Test Client",
        "client_type": "CORPORATE",
        "default_currency": "CNY",
        "is_active": True,
        **overrides,
    }
    resp = client.post(CLIENTS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Client creation failed: {resp.text}"
    return resp.json()


def _create_case(client, auth_headers, client_id: str, **overrides) -> dict:
    payload = {
        "case_no": _uid("CASE"),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "测试案件",
        **overrides,
    }
    resp = client.post(CASES_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Case creation failed: {resp.text}"
    return resp.json()


def _create_fee_rate(client, auth_headers, **overrides) -> dict:
    payload = {
        "fee_code": _uid("RATE"),
        "fee_name": "Test Filing Fee",
        "fee_type": "GOV",
        "currency": "CNY",
        "default_amount": "500.00",
        "enabled": True,
        **overrides,
    }
    resp = client.post(FEE_RATES_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Rate creation failed: {resp.text}"
    return resp.json()


def _create_fee_draft(client, auth_headers, case_id: str, client_id: str) -> dict:
    payload = {"case_id": case_id, "client_id": client_id, "currency": "CNY"}
    resp = client.post(FEE_DRAFTS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Draft creation failed: {resp.text}"
    return resp.json()


def _add_fee_item(client, auth_headers, draft_id: str, rate_id: str, **overrides) -> dict:
    payload = {"rate_id": rate_id, "quantity": 1, "unit_price": "500.00", **overrides}
    resp = client.post(f"{FEE_DRAFTS_URL}/{draft_id}/items", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Fee item creation failed: {resp.text}"
    return resp.json()


def _create_bill_from_drafts(client, auth_headers, draft_ids: list[str]) -> dict:
    payload = {"draft_ids": draft_ids, "bill_no": _uid("BILL")}
    resp = client.post(BILLS_FROM_DRAFTS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Bill creation failed: {resp.text}"
    return resp.json()


def _create_payment(client, auth_headers, client_id: str, amount: str) -> dict:
    payload = {
        "client_id": client_id,
        "amount": amount,
        "pay_no": _uid("PAY"),
        "currency": "CNY",
    }
    resp = client.post(PAYMENTS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Payment creation failed: {resp.text}"
    return resp.json()


def _get_payment_line_id(client, auth_headers, payment_id: str) -> str:
    """Get the first payment line ID for a payment."""
    resp = client.get(f"{PAYMENTS_URL}/{payment_id}", headers=auth_headers)
    assert resp.status_code == 200
    lines = resp.json()["payment_lines"]
    assert len(lines) > 0, "No payment lines found"
    return lines[0]["id"]


def _create_offset(client, auth_headers, payment_line_id: str, bill_id: str, amount: str) -> dict:
    payload = {
        "payment_line_id": payment_line_id,
        "bill_id": bill_id,
        "offset_amt": amount,
        "offset_date": "2026-02-26",
    }
    resp = client.post(OFFSETS_URL, json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Offset creation failed: {resp.text}"
    return resp.json()


def _reverse_offset(client, auth_headers, offset_id: str) -> dict:
    resp = client.post(f"{OFFSETS_URL}/{offset_id}/reverse", headers=auth_headers)
    return resp.json() if resp.status_code != 204 else {}, resp.status_code


def _get_bill(client, auth_headers, bill_id: str) -> dict:
    resp = client.get(f"/api/v1/bills/{bill_id}", headers=auth_headers)
    assert resp.status_code == 200
    return resp.json()


def _setup_full_billing_chain(client, auth_headers, fee_amount: str = "500.00"):
    """Set up: client -> case -> fee rate -> fee draft -> fee item -> bill -> payment.

    Returns dict with all created entity IDs and data.
    """
    cl = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=cl["id"])
    rate = _create_fee_rate(client, auth_headers, default_amount=fee_amount)
    draft = _create_fee_draft(client, auth_headers, case["id"], cl["id"])
    _add_fee_item(client, auth_headers, draft["id"], rate["id"], unit_price=fee_amount)
    bill = _create_bill_from_drafts(client, auth_headers, [draft["id"]])
    payment = _create_payment(client, auth_headers, cl["id"], fee_amount)
    payment_line_id = _get_payment_line_id(client, auth_headers, payment["id"])

    return {
        "client": cl,
        "case": case,
        "rate": rate,
        "draft": draft,
        "bill": bill,
        "payment": payment,
        "payment_line_id": payment_line_id,
    }


# ---------------------------------------------------------------------------
# T2a — CaseReceipt new fields
# ---------------------------------------------------------------------------
def test_case_receipt_new_fields(client, auth_headers, session_factory):
    """Create receipt with new fields via DB, verify via GET endpoint."""
    # Set up a case
    cl = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=cl["id"])

    # Insert a CaseReceipt directly in DB with new fields populated
    db: Session = session_factory()
    try:
        receipt = CaseReceipt(
            id=str(uuid.uuid4()),
            case_id=case["id"],
            fee_type="GOV",
            currency="CNY",
            receivable_amt=Decimal("1000.00"),
            received_amt=Decimal("0"),
            fee_code="FEE-T2A-001",
            year_no=2026,
            is_arrears=True,
            invoice_no="INV-T2A-001",
            is_commissionable=True,
        )
        db.add(receipt)
        db.commit()
    finally:
        db.close()

    # Verify via API
    resp = client.get(f"/api/v1/cases/{case['id']}/receipts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["fee_code"] == "FEE-T2A-001"
    assert data["year_no"] == 2026
    assert data["is_arrears"] is True
    assert data["invoice_no"] == "INV-T2A-001"
    assert data["is_commissionable"] is True
    assert data["fee_type"] == "GOV"
    assert data["currency"] == "CNY"


# ---------------------------------------------------------------------------
# T2b — CaseReceipt backward compat (no new fields)
# ---------------------------------------------------------------------------
def test_case_receipt_backward_compat(client, auth_headers, session_factory):
    """Receipt without new fields → null values in response."""
    cl = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=cl["id"])

    db: Session = session_factory()
    try:
        receipt = CaseReceipt(
            id=str(uuid.uuid4()),
            case_id=case["id"],
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("500.00"),
            received_amt=Decimal("0"),
        )
        db.add(receipt)
        db.commit()
    finally:
        db.close()

    resp = client.get(f"/api/v1/cases/{case['id']}/receipts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Original fields present
    assert data["fee_type"] == "SERVICE"
    assert data["currency"] == "CNY"

    # New fields should be null (not set)
    assert data["fee_code"] is None
    assert data["year_no"] is None
    assert data["is_arrears"] is None or data["is_arrears"] is False
    assert data["invoice_no"] is None
    assert data["is_commissionable"] is None or data["is_commissionable"] is False


# ---------------------------------------------------------------------------
# T3 — Offset reversal happy path
# ---------------------------------------------------------------------------
def test_offset_reversal_happy_path(client, auth_headers):
    """Full flow: bill → offset → reverse → verify balances and status."""
    setup = _setup_full_billing_chain(client, auth_headers, fee_amount="500.00")
    bill_id = setup["bill"]["id"]
    payment_line_id = setup["payment_line_id"]

    # Create offset for full bill amount
    offset = _create_offset(client, auth_headers, payment_line_id, bill_id, "500.00")
    assert offset["is_reversed"] is False

    # Verify bill is settled after offset via list endpoint (includes balance)
    bills_resp = client.get("/api/v1/bills", headers=auth_headers)
    assert bills_resp.status_code == 200
    bill_in_list = next((b for b in bills_resp.json()["items"] if b["id"] == bill_id), None)
    assert bill_in_list is not None
    assert bill_in_list["status"] == "SETTLED"
    assert Decimal(str(bill_in_list["balance"])) == Decimal("0")

    # Reverse the offset
    resp = client.post(f"{OFFSETS_URL}/{offset['id']}/reverse", headers=auth_headers)
    assert resp.status_code == 200
    reversed_data = resp.json()
    assert reversed_data["is_reversed"] is True
    assert reversed_data["offset_amt"] == offset["offset_amt"]
    assert reversed_data["offset_date"] == "2026-02-26"

    # Verify bill balance restored and status back to UNSETTLED
    bills_resp2 = client.get("/api/v1/bills", headers=auth_headers)
    bill_after = next((b for b in bills_resp2.json()["items"] if b["id"] == bill_id), None)
    assert bill_after is not None
    assert bill_after["status"] == "UNSETTLED"
    assert Decimal(str(bill_after["balance"])) == Decimal("500.00")


# ---------------------------------------------------------------------------
# T4 — Offset reversal partial
# ---------------------------------------------------------------------------
def test_offset_reversal_partial(client, auth_headers):
    """Two partial offsets → reverse one → bill partially settled."""
    setup = _setup_full_billing_chain(client, auth_headers, fee_amount="1000.00")
    bill_id = setup["bill"]["id"]
    payment_line_id = setup["payment_line_id"]

    # Create two partial offsets: 400 + 300 = 700 out of 1000
    offset1 = _create_offset(client, auth_headers, payment_line_id, bill_id, "400.00")
    _create_offset(client, auth_headers, payment_line_id, bill_id, "300.00")

    # Bill balance should be 300 (1000 - 700)
    bills_resp = client.get("/api/v1/bills", headers=auth_headers)
    bill_data = next((b for b in bills_resp.json()["items"] if b["id"] == bill_id), None)
    assert Decimal(str(bill_data["balance"])) == Decimal("300.00")
    assert bill_data["status"] == "PARTIALLY_SETTLED"

    # Reverse offset1 (400.00) → bill balance should become 300 + 400 = 700
    resp = client.post(f"{OFFSETS_URL}/{offset1['id']}/reverse", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_reversed"] is True

    # Bill should be PARTIALLY_SETTLED with balance = 700
    bills_resp2 = client.get("/api/v1/bills", headers=auth_headers)
    bill_after = next((b for b in bills_resp2.json()["items"] if b["id"] == bill_id), None)
    assert bill_after is not None
    assert Decimal(str(bill_after["balance"])) == Decimal("700.00")
    assert bill_after["status"] == "PARTIALLY_SETTLED"


# ---------------------------------------------------------------------------
# T5 — Double reversal blocked
# ---------------------------------------------------------------------------
def test_double_reversal_blocked(client, auth_headers):
    """Reverse → re-reverse same offset → 400 OFFSET_ALREADY_REVERSED."""
    setup = _setup_full_billing_chain(client, auth_headers, fee_amount="500.00")
    bill_id = setup["bill"]["id"]
    payment_line_id = setup["payment_line_id"]

    offset = _create_offset(client, auth_headers, payment_line_id, bill_id, "500.00")

    # First reversal should succeed
    resp1 = client.post(f"{OFFSETS_URL}/{offset['id']}/reverse", headers=auth_headers)
    assert resp1.status_code == 200

    # Second reversal should fail with 400
    resp2 = client.post(f"{OFFSETS_URL}/{offset['id']}/reverse", headers=auth_headers)
    assert resp2.status_code == 400
    error_data = resp2.json()
    assert "OFFSET_ALREADY_REVERSED" in str(error_data) or "already" in str(error_data).lower()


# ---------------------------------------------------------------------------
# T6 — Offset not found
# ---------------------------------------------------------------------------
def test_offset_not_found(client, auth_headers):
    """Reverse with non-existent offset ID → 404."""
    fake_id = str(uuid.uuid4())
    resp = client.post(f"{OFFSETS_URL}/{fake_id}/reverse", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# T7 — Payment line balance restored after reversal
# ---------------------------------------------------------------------------
def test_payment_line_balance_restored(client, auth_headers, session_factory):
    """After reversal, payment_line.allocated_amt decreased, balance_amt increased."""
    setup = _setup_full_billing_chain(client, auth_headers, fee_amount="500.00")
    bill_id = setup["bill"]["id"]
    payment_line_id = setup["payment_line_id"]

    # Create offset
    offset = _create_offset(client, auth_headers, payment_line_id, bill_id, "500.00")

    # Verify payment line after offset (allocated=500, balance=0)
    db: Session = session_factory()
    try:
        pl = db.query(PaymentLine).filter(PaymentLine.id == payment_line_id).first()
        assert pl is not None
        assert pl.allocated_amt == Decimal("500.00")
        assert pl.balance_amt == Decimal("0")
    finally:
        db.close()

    # Reverse offset
    resp = client.post(f"{OFFSETS_URL}/{offset['id']}/reverse", headers=auth_headers)
    assert resp.status_code == 200

    # Verify payment line after reversal (allocated=0, balance=500)
    db2: Session = session_factory()
    try:
        pl2 = db2.query(PaymentLine).filter(PaymentLine.id == payment_line_id).first()
        assert pl2 is not None
        assert pl2.allocated_amt == Decimal("0")
        assert pl2.balance_amt == Decimal("500.00")
    finally:
        db2.close()


# ---------------------------------------------------------------------------
# T8 — CaseReceipt received_amt reversed
# ---------------------------------------------------------------------------
def test_receipt_received_amt_reversed(client, auth_headers, session_factory):
    """Offset → CaseReceipt.received_amt increased. Reversal → decreased back."""
    setup = _setup_full_billing_chain(client, auth_headers, fee_amount="500.00")
    bill_id = setup["bill"]["id"]
    case_id = setup["case"]["id"]
    payment_line_id = setup["payment_line_id"]

    # Create offset — this should allocate to CaseReceipt via _allocate_offset_to_receipts
    offset = _create_offset(client, auth_headers, payment_line_id, bill_id, "500.00")

    # Verify CaseReceipt.received_amt increased
    db: Session = session_factory()
    try:
        receipt = db.query(CaseReceipt).filter(CaseReceipt.case_id == case_id).first()
        assert receipt is not None, "CaseReceipt should exist after offset allocation"
        received_after_offset = receipt.received_amt
        assert received_after_offset > Decimal("0"), (
            f"received_amt should be positive after offset, got {received_after_offset}"
        )
    finally:
        db.close()

    # Reverse offset
    resp = client.post(f"{OFFSETS_URL}/{offset['id']}/reverse", headers=auth_headers)
    assert resp.status_code == 200

    # Verify CaseReceipt.received_amt decreased back to 0
    db2: Session = session_factory()
    try:
        receipt2 = db2.query(CaseReceipt).filter(CaseReceipt.case_id == case_id).first()
        assert receipt2 is not None
        assert receipt2.received_amt == Decimal("0"), (
            f"received_amt should be 0 after reversal, got {receipt2.received_amt}"
        )
    finally:
        db2.close()
