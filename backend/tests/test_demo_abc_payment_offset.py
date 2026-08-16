from __future__ import annotations

import runpy
from pathlib import Path

import pytest

from app.modules.billing.models import (
    Bill,
    BillItem,
    CaseReceipt,
    DemoFinanceCommand,
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

    payment_reconciled = client.get(
        f"/api/v1/payments/idempotency/{receipt_command['idempotency_key']}",
        headers=auth_headers,
    )
    assert payment_reconciled.status_code == 200, payment_reconciled.text
    assert payment_reconciled.json()["reused"] is True
    assert payment_reconciled.json()["payment"]["id"] == payment_id

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

    second_intent = dict(
        receipt_command,
        idempotency_key="demo-payment-second-intent",
        pay_no="DEMO-PAY-0003",
        bank_ref_no="DEMO-BANK-REF-0003",
    )
    second_payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=second_intent,
        headers=auth_headers,
    )
    assert second_payment.status_code == 409, second_payment.text

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
    exact_receipt_id = allocated["case_receipt"]["id"]

    offset_reconciled = client.get(
        f"/api/v1/offsets/idempotency/{offset_command['idempotency_key']}",
        headers=auth_headers,
    )
    assert offset_reconciled.status_code == 200, offset_reconciled.text
    assert offset_reconciled.json()["reused"] is True
    assert offset_reconciled.json()["case_receipt"]["id"] == exact_receipt_id

    offset_replay = client.post(
        "/api/v1/offsets/demo-full", json=offset_command, headers=auth_headers
    )
    assert offset_replay.status_code == 201, offset_replay.text
    assert offset_replay.json()["reused"] is True
    assert offset_replay.json()["offset"]["id"] == offset_id
    assert offset_replay.json()["case_receipt"]["id"] == exact_receipt_id

    immutable_payment = client.get(
        f"/api/v1/payments/idempotency/{receipt_command['idempotency_key']}",
        headers=auth_headers,
    )
    assert immutable_payment.status_code == 200, immutable_payment.text
    assert immutable_payment.json()["reused"] is True
    assert immutable_payment.json()["line"]["allocated_amt"] == "0.00"
    assert immutable_payment.json()["line"]["balance_amt"] == "1200.00"
    assert immutable_payment.json()["bill"]["status"] == "UNSETTLED"
    assert immutable_payment.json()["bill"]["balance"] == "1200.00"

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
        assert db.query(DemoFinanceCommand).count() == 3
        assert {row.state for row in db.query(DemoFinanceCommand).all()} == {"COMPLETED"}
        assert all(row.result_snapshot for row in db.query(DemoFinanceCommand).all())
        assert db.query(CaseReceipt).count() == 1
        payment_command = db.query(DemoPaymentCommand).one()
        assert payment_command.target_bill_id == bill_id
        offset_command_row = db.query(DemoOffsetCommand).one()
        assert offset_command_row.receipt_id == exact_receipt_id
        case_receipt = db.query(CaseReceipt).one()
        assert case_receipt.receipt_key == f"{case_id}|DEMO_SERVICE_1|SERVICE|-|CNY"
        bill = db.get(Bill, bill_id)
        assert bill.balance == 0
        assert bill.status == "SETTLED"


def test_demo_command_reconciliation_distinguishes_pending_absent_and_heals_commit_gap(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    command = {
        "target_bill_id": bill_id,
        "amount": "1200.00",
        "pay_no": "DEMO-PAY-PENDING",
        "pay_date": "2026-08-16",
        "currency": "CNY",
        "pay_method": "BANK_TRANSFER",
        "bank_ref_no": "DEMO-BANK-PENDING",
        "idempotency_key": "demo-payment-pending",
    }
    created = client.post(
        "/api/v1/payments/demo-bank-receipts", json=command, headers=auth_headers
    )
    assert created.status_code == 201, created.text
    expected = created.json()

    with session_factory() as db:
        durable = (
            db.query(DemoFinanceCommand)
            .filter_by(operation="PAYMENT", idempotency_key=command["idempotency_key"])
            .one()
        )
        durable.state = "IN_PROGRESS"
        durable.result_snapshot = None
        db.commit()

    healed = client.get(
        f"/api/v1/payments/idempotency/{command['idempotency_key']}",
        headers=auth_headers,
    )
    assert healed.status_code == 200, healed.text
    assert healed.json()["payment"]["id"] == expected["payment"]["id"]
    assert healed.json()["line"]["balance_amt"] == "1200.00"

    with session_factory() as db:
        actor_id = db.query(DemoFinanceCommand.created_by).first()[0]
        db.add(
            DemoFinanceCommand(
                operation="PAYMENT",
                idempotency_key="demo-payment-still-pending",
                state="IN_PROGRESS",
                command_hash="1" * 64,
                command_snapshot='{"pending":true}',
                result_snapshot=None,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )
        db.commit()

    pending = client.get(
        "/api/v1/payments/idempotency/demo-payment-still-pending",
        headers=auth_headers,
    )
    assert pending.status_code == 202, pending.text
    assert pending.json() == {
        "idempotency_key": "demo-payment-still-pending",
        "status": "IN_PROGRESS",
    }

    absent = client.get(
        "/api/v1/payments/idempotency/demo-payment-absent",
        headers=auth_headers,
    )
    assert absent.status_code == 404, absent.text

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


@pytest.mark.parametrize("amount", [1200, "1200.0", " 1200.00"])
def test_demo_payment_rejects_coerced_or_noncanonical_money(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
    amount,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    response = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": amount,
            "pay_no": "DEMO-PAY-STRICT",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-STRICT",
            "idempotency_key": "demo-payment-strict",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422, response.text
    with session_factory() as db:
        assert db.query(Payment).count() == 0


def test_demo_payment_and_offset_use_404_and_400_semantics(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    missing_id = "00000000-0000-0000-0000-000000000000"
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    missing = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": missing_id,
            "amount": "1200.00",
            "pay_no": "DEMO-PAY-MISSING",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-MISSING",
            "idempotency_key": "demo-payment-missing",
        },
        headers=auth_headers,
    )
    assert missing.status_code == 404, missing.text

    wrong_amount = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": "1100.00",
            "pay_no": "DEMO-PAY-WRONG",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-WRONG",
            "idempotency_key": "demo-payment-wrong",
        },
        headers=auth_headers,
    )
    assert wrong_amount.status_code == 400, wrong_amount.text

    missing_offset = client.post(
        "/api/v1/offsets/demo-full",
        json={
            "payment_line_id": missing_id,
            "bill_id": missing_id,
            "offset_amt": "1200.00",
            "offset_date": "2026-08-16",
            "idempotency_key": "demo-offset-missing",
        },
        headers=auth_headers,
    )
    assert missing_offset.status_code == 404, missing_offset.text


def test_demo_offset_rejects_ambiguous_receipt_key_component_without_write(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": "1200.00",
            "pay_no": "DEMO-PAY-KEY",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-KEY",
            "idempotency_key": "demo-payment-key",
        },
        headers=auth_headers,
    )
    assert payment.status_code == 201, payment.text
    line_id = payment.json()["line"]["id"]
    with session_factory() as db:
        item = db.query(BillItem).filter(BillItem.bill_id == bill_id).one()
        item.fee_code = "BAD|CODE"
        db.commit()

    response = client.post(
        "/api/v1/offsets/demo-full",
        json={
            "payment_line_id": line_id,
            "bill_id": bill_id,
            "offset_amt": "1200.00",
            "offset_date": "2026-08-16",
            "idempotency_key": "demo-offset-key",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400, response.text
    with session_factory() as db:
        assert db.query(Offset).count() == 0
        assert db.query(CaseReceipt).count() == 0
        assert db.query(DemoOffsetCommand).count() == 0
