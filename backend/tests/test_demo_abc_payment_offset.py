from __future__ import annotations

import runpy
from pathlib import Path

from app.modules.billing.models import (
    Bill,
    CaseReceipt,
    DemoOffsetCommand,
    DemoPaymentCommand,
    Offset,
    Payment,
    PaymentLine,
)


def _bill_helpers():
    return runpy.run_path(str(Path(__file__).with_name("test_demo_abc_unique_ar_bill.py")))


def _demo_bill(client, auth_headers, session_factory, tmp_path, monkeypatch):
    helpers = _bill_helpers()
    client_id, case_id, draft_id = helpers["_locked_demo_draft"](
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    response = client.post(
        "/api/v1/bills/demo-from-draft",
        json={
            "draft_id": draft_id,
            "bill_no": "DEMO-AR-PAY-1",
            "bill_date": "2026-08-16",
            "due_date": "2026-08-31",
            "idempotency_key": "demo-bill-for-payment-1",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return client_id, case_id, response.json()["bill"]["id"]


def test_demo_bank_receipt_then_full_offset_is_exact_and_idempotent(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    client_id, case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    receipt_command = {
        "target_bill_id": bill_id,
        "amount": "1200.00",
        "pay_no": "DEMO-PAY-0001",
        "pay_date": "2026-08-16",
        "currency": "CNY",
        "pay_method": "BANK_TRANSFER",
        "bank_ref_no": "DEMO-BANK-REF-0001",
        "remark": "ABC 演示客户回款",
        "idempotency_key": "demo-payment-intent-1",
    }
    receipt_response = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=receipt_command,
        headers=auth_headers,
    )
    assert receipt_response.status_code == 201, receipt_response.text
    receipt = receipt_response.json()
    payment_id = receipt["payment"]["id"]
    line_id = receipt["line"]["id"]
    assert receipt["reused"] is False
    assert receipt["target_bill_id"] == bill_id
    assert receipt["payment"]["client_id"] == client_id
    assert receipt["payment"]["amount"] == "1200.00"
    assert receipt["payment"]["pay_method"] == "BANK_TRANSFER"
    assert receipt["payment"]["bank_ref_no"] == "DEMO-BANK-REF-0001"
    assert receipt["line"]["raw_amount"] == "1200.00"
    assert receipt["line"]["allocated_amt"] == "0.00"
    assert receipt["line"]["balance_amt"] == "1200.00"
    assert receipt["line"]["status"] == "UNALLOCATED"
    assert receipt["bill"]["status"] == "UNSETTLED"
    assert receipt["bill"]["balance"] == "1200.00"

    replay = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=receipt_command,
        headers=auth_headers,
    )
    assert replay.status_code == 201, replay.text
    assert replay.json()["reused"] is True
    assert replay.json()["payment"]["id"] == payment_id

    drifted = dict(receipt_command, amount="1100.00")
    drift = client.post(
        "/api/v1/payments/demo-bank-receipts", json=drifted, headers=auth_headers
    )
    assert drift.status_code == 409, drift.text

    duplicate_reference = dict(
        receipt_command,
        idempotency_key="demo-payment-intent-2",
        pay_no="DEMO-PAY-0002",
    )
    duplicate = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=duplicate_reference,
        headers=auth_headers,
    )
    assert duplicate.status_code == 409, duplicate.text

    offset_command = {
        "payment_line_id": line_id,
        "bill_id": bill_id,
        "offset_amt": "1200.00",
        "offset_date": "2026-08-16",
        "idempotency_key": "demo-offset-intent-1",
    }
    offset_response = client.post(
        "/api/v1/offsets/demo-full", json=offset_command, headers=auth_headers
    )
    assert offset_response.status_code == 201, offset_response.text
    allocated = offset_response.json()
    offset_id = allocated["offset"]["id"]
    assert allocated["reused"] is False
    assert allocated["bill"]["status"] == "SETTLED"
    assert allocated["bill"]["balance"] == "0.00"
    assert allocated["line"]["allocated_amt"] == "1200.00"
    assert allocated["line"]["balance_amt"] == "0.00"
    assert allocated["line"]["status"] == "FULLY_ALLOCATED"
    assert allocated["case_receipt"]["case_id"] == case_id
    assert allocated["case_receipt"]["fee_type"] == "SERVICE"
    assert allocated["case_receipt"]["receivable_amt"] == "1200.00"
    assert allocated["case_receipt"]["received_amt"] == "1200.00"

    offset_replay = client.post(
        "/api/v1/offsets/demo-full", json=offset_command, headers=auth_headers
    )
    assert offset_replay.status_code == 201, offset_replay.text
    assert offset_replay.json()["reused"] is True
    assert offset_replay.json()["offset"]["id"] == offset_id

    second_offset = dict(offset_command, idempotency_key="demo-offset-intent-2")
    second = client.post(
        "/api/v1/offsets/demo-full", json=second_offset, headers=auth_headers
    )
    assert second.status_code == 409, second.text

    with session_factory() as db:
        assert db.query(Payment).count() == 1
        assert db.query(PaymentLine).count() == 1
        assert db.query(DemoPaymentCommand).count() == 1
        assert db.query(Offset).count() == 1
        assert db.query(DemoOffsetCommand).count() == 1
        assert db.query(CaseReceipt).count() == 1
        bill = db.get(Bill, bill_id)
        assert bill.balance == 0
        assert bill.status == "SETTLED"


def test_demo_payment_and_offset_reject_invalid_money_without_partial_write(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    invalid_receipt = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": "0.00",
            "pay_no": "DEMO-PAY-ZERO",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-ZERO",
            "idempotency_key": "demo-payment-zero",
        },
        headers=auth_headers,
    )
    assert invalid_receipt.status_code == 422, invalid_receipt.text
    with session_factory() as db:
        assert db.query(Payment).count() == 0
        assert db.query(PaymentLine).count() == 0
        assert db.query(DemoPaymentCommand).count() == 0
