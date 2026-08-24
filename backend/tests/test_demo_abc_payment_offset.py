from __future__ import annotations

import hashlib
import json
import runpy
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import event, func, select

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
from app.modules.billing.schemas import DemoBankReceiptRequest, DemoFullOffsetRequest
from app.modules.billing.service import (
    create_demo_bank_receipt,
    reserve_demo_finance_command,
)
from app.modules.fees.models import FeeDraft, FeeItem


def _demo_bill(client, auth_headers, session_factory, tmp_path, monkeypatch):
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_service_adjustment.py"))
    )
    case_id, _obligation_id, draft_id = helpers["_create_open_service_draft"](
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        draft = transaction.get(FeeDraft, draft_id)
        adjustable = transaction.scalar(
            select(FeeItem).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        client_id = draft.client_id
        adjustable_id = adjustable.id
    adjusted = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "demo-payment-service-adjustment",
        },
        headers=auth_headers,
    )
    assert adjusted.status_code == 201, adjusted.text
    locked = client.post(
        f"/api/v1/fees/drafts/{draft_id}/lock",
        headers=auth_headers,
    )
    assert locked.status_code == 200, locked.text
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


def test_demo_two_receipts_and_offsets_settle_multiline_service_bill(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    client_id, case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    first_receipt_command = {
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
    first_receipt_response = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=first_receipt_command,
        headers=auth_headers,
    )
    assert first_receipt_response.status_code == 201, first_receipt_response.text
    first_receipt = first_receipt_response.json()
    assert first_receipt["payment"]["client_id"] == client_id
    assert first_receipt["bill"]["status"] == "UNSETTLED"
    assert first_receipt["bill"]["balance"] == "1800.00"

    first_offset_command = {
        "payment_line_id": first_receipt["line"]["id"],
        "bill_id": bill_id,
        "offset_amt": "1200.00",
        "offset_date": "2026-08-16",
        "idempotency_key": "demo-offset-intent-1",
    }
    first_offset_response = client.post(
        "/api/v1/offsets/demo-full",
        json=first_offset_command,
        headers=auth_headers,
    )
    assert first_offset_response.status_code == 201, first_offset_response.text
    first_offset = first_offset_response.json()
    assert first_offset["bill"]["status"] == "PARTIALLY_SETTLED"
    assert first_offset["bill"]["balance"] == "600.00"
    assert first_offset["line"]["status"] == "FULLY_ALLOCATED"

    second_receipt_command = {
        **first_receipt_command,
        "amount": "600.00",
        "pay_no": "DEMO-PAY-0002",
        "bank_ref_no": "DEMO-BANK-REF-0002",
        "idempotency_key": "demo-payment-intent-2",
    }
    second_receipt_response = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=second_receipt_command,
        headers=auth_headers,
    )
    assert second_receipt_response.status_code == 201, second_receipt_response.text
    second_receipt = second_receipt_response.json()
    assert second_receipt["bill"]["status"] == "PARTIALLY_SETTLED"
    assert second_receipt["bill"]["balance"] == "600.00"
    second_offset_command = {
        "payment_line_id": second_receipt["line"]["id"],
        "bill_id": bill_id,
        "offset_amt": "600.00",
        "offset_date": "2026-08-17",
        "idempotency_key": "demo-offset-intent-2",
    }
    second_offset_response = client.post(
        "/api/v1/offsets/demo-full",
        json=second_offset_command,
        headers=auth_headers,
    )
    assert second_offset_response.status_code == 201, second_offset_response.text
    second_offset = second_offset_response.json()
    assert second_offset["bill"]["status"] == "SETTLED"
    assert second_offset["bill"]["balance"] == "0.00"
    assert second_offset["line"]["status"] == "FULLY_ALLOCATED"
    assert second_offset["case_receipt"]["case_id"] == case_id
    assert second_offset["case_receipt"]["receivable_amt"] == "1800.00"
    assert second_offset["case_receipt"]["received_amt"] == "1800.00"

    for path, command, object_key in (
        ("/api/v1/payments/demo-bank-receipts", first_receipt_command, "payment"),
        ("/api/v1/payments/demo-bank-receipts", second_receipt_command, "payment"),
        ("/api/v1/offsets/demo-full", first_offset_command, "offset"),
        ("/api/v1/offsets/demo-full", second_offset_command, "offset"),
    ):
        replay = client.post(path, json=command, headers=auth_headers)
        assert replay.status_code == 201, replay.text
        assert replay.json()["reused"] is True
        assert replay.json()[object_key]["id"]

    third = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            **second_receipt_command,
            "pay_no": "DEMO-PAY-0003",
            "bank_ref_no": "DEMO-BANK-REF-0003",
            "idempotency_key": "demo-payment-intent-3",
        },
        headers=auth_headers,
    )
    assert third.status_code == 409

    with session_factory() as db:
        assert db.query(Payment).count() == 2
        assert db.query(PaymentLine).count() == 2
        assert db.query(Offset).filter_by(is_reversed=False).count() == 2
        assert db.query(DemoFinanceCommand).count() == 5
        assert {row.state for row in db.query(DemoFinanceCommand).all()} == {"COMPLETED"}
        assert all(row.result_snapshot for row in db.query(DemoFinanceCommand).all())
        assert db.query(CaseReceipt).count() == 1
        case_receipt = db.query(CaseReceipt).one()
        assert case_receipt.receivable_amt == 1800
        assert case_receipt.received_amt == 1800
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
        pending_payload = {
            **command,
            "pay_no": "DEMO-PAY-STILL-PENDING",
            "bank_ref_no": "DEMO-BANK-STILL-PENDING",
            "idempotency_key": "demo-payment-still-pending",
        }
        pending_snapshot = json.dumps(
            {
                "actor_id": actor_id,
                "operation": "PAYMENT",
                "payload": pending_payload,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        db.add(
            DemoFinanceCommand(
                operation="PAYMENT",
                idempotency_key="demo-payment-still-pending",
                state="IN_PROGRESS",
                command_hash=hashlib.sha256(pending_snapshot.encode("utf-8")).hexdigest(),
                command_snapshot=pending_snapshot,
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


@pytest.mark.parametrize("drift", ["bill_status", "line_allocation"])
def test_demo_offset_reconciliation_rejects_settlement_drift(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
    drift,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": "1200.00",
            "pay_no": "DEMO-PAY-DRIFT",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-DRIFT",
            "idempotency_key": "demo-payment-drift",
        },
        headers=auth_headers,
    )
    assert payment.status_code == 201, payment.text
    line_id = payment.json()["line"]["id"]
    offset_body = {
        "payment_line_id": line_id,
        "bill_id": bill_id,
        "offset_amt": "1200.00",
        "offset_date": "2026-08-16",
        "idempotency_key": "demo-offset-drift",
    }
    offset = client.post(
        "/api/v1/offsets/demo-full",
        json=offset_body,
        headers=auth_headers,
    )
    assert offset.status_code == 201, offset.text

    with session_factory() as transaction:
        command = transaction.scalar(
            select(DemoFinanceCommand).where(
                DemoFinanceCommand.operation == "OFFSET",
                DemoFinanceCommand.idempotency_key == offset_body["idempotency_key"],
            )
        )
        command.state = "IN_PROGRESS"
        command.result_snapshot = None
        if drift == "bill_status":
            transaction.get(Bill, bill_id).status = "SETTLED"
        else:
            line = transaction.get(PaymentLine, line_id)
            line.allocated_amt = 0
            line.balance_amt = line.raw_amount
        transaction.commit()

    recovered = client.get(
        f"/api/v1/offsets/idempotency/{offset_body['idempotency_key']}",
        headers=auth_headers,
    )
    assert recovered.status_code == 409, recovered.text
    with session_factory() as transaction:
        command = transaction.scalar(
            select(DemoFinanceCommand).where(
                DemoFinanceCommand.operation == "OFFSET",
                DemoFinanceCommand.idempotency_key == offset_body["idempotency_key"],
            )
        )
        assert command.state == "IN_PROGRESS"


def test_demo_payment_sequence_is_owned_by_bill_across_actors(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    first_body = {
        "target_bill_id": bill_id,
        "amount": "1200.00",
        "pay_no": "DEMO-PAY-OTHER-ACTOR",
        "pay_date": "2026-08-16",
        "currency": "CNY",
        "pay_method": "BANK_TRANSFER",
        "bank_ref_no": "DEMO-BANK-OTHER-ACTOR",
        "remark": None,
        "idempotency_key": "demo-payment-other-actor",
    }
    actor_id = str(uuid4())
    with session_factory() as transaction:
        reserve_demo_finance_command(
            transaction,
            operation="PAYMENT",
            idempotency_key=first_body["idempotency_key"],
            actor_id=actor_id,
            payload=first_body,
        )
        create_demo_bank_receipt(
            transaction,
            DemoBankReceiptRequest.model_validate(first_body),
            actor_id=actor_id,
        )

    second = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            **first_body,
            "pay_no": "DEMO-PAY-CURRENT-ACTOR",
            "bank_ref_no": "DEMO-BANK-CURRENT-ACTOR",
            "idempotency_key": "demo-payment-current-actor",
        },
        headers=auth_headers,
    )
    assert second.status_code == 409, second.text
    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(Payment)) == 1


def test_demo_offset_postcondition_failure_rolls_back_domain_writes(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json={
            "target_bill_id": bill_id,
            "amount": "1200.00",
            "pay_no": "DEMO-PAY-ROLLBACK",
            "pay_date": "2026-08-16",
            "currency": "CNY",
            "pay_method": "BANK_TRANSFER",
            "bank_ref_no": "DEMO-BANK-ROLLBACK",
            "idempotency_key": "demo-payment-rollback",
        },
        headers=auth_headers,
    )
    assert payment.status_code == 201, payment.text
    line_id = payment.json()["line"]["id"]
    with session_factory() as transaction:
        transaction.add_all(
            CaseReceipt(
                id=str(uuid4()),
                case_id=case_id,
                fee_type="SERVICE",
                currency="CNY",
                receivable_amt=1800,
                received_amt=0,
            )
            for _ in range(2)
        )
        transaction.commit()

    response = client.post(
        "/api/v1/offsets/demo-full",
        json={
            "payment_line_id": line_id,
            "bill_id": bill_id,
            "offset_amt": "1200.00",
            "offset_date": "2026-08-16",
            "idempotency_key": "demo-offset-rollback",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409, response.text
    with session_factory() as transaction:
        bill = transaction.get(Bill, bill_id)
        line = transaction.get(PaymentLine, line_id)
        assert transaction.scalar(select(func.count()).select_from(Offset)) == 0
        assert bill.status == "UNSETTLED"
        assert bill.balance == 1800
        assert line.allocated_amt == 0
        assert line.balance_amt == 1200


def test_demo_payment_and_offset_lock_conflicts_are_retryable_without_domain_writes(
    client,
    auth_headers,
    session_factory,
    engine,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    payment_body = {
        "target_bill_id": bill_id,
        "amount": "1200.00",
        "pay_no": "DEMO-PAY-LOCK",
        "pay_date": "2026-08-16",
        "currency": "CNY",
        "pay_method": "BANK_TRANSFER",
        "bank_ref_no": "DEMO-BANK-LOCK",
        "idempotency_key": "demo-payment-lock",
    }
    with session_factory() as transaction:
        actor_id = transaction.scalar(
            select(DemoFinanceCommand.created_by).where(
                DemoFinanceCommand.operation == "BILL"
            )
        )
        reserve_demo_finance_command(
            transaction,
            operation="PAYMENT",
            idempotency_key=payment_body["idempotency_key"],
            actor_id=actor_id,
            payload=DemoBankReceiptRequest.model_validate(payment_body).model_dump(
                mode="json"
            ),
        )

    def fast_lock_failure(dbapi_connection, *_args):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA busy_timeout=1")
        cursor.close()

    event.listen(engine, "checkout", fast_lock_failure)
    try:
        with engine.connect() as locker:
            locker.exec_driver_sql("BEGIN IMMEDIATE")
            locked_payment = client.post(
                "/api/v1/payments/demo-bank-receipts",
                json=payment_body,
                headers=auth_headers,
            )
            locker.rollback()
    finally:
        event.remove(engine, "checkout", fast_lock_failure)
    assert locked_payment.status_code == 409, locked_payment.text
    assert locked_payment.json()["error"]["code"] == "DEMO_FINANCE_WRITE_BUSY"
    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(Payment)) == 0
        assert transaction.scalar(select(func.count()).select_from(PaymentLine)) == 0
        command = transaction.scalar(
            select(DemoFinanceCommand).where(
                DemoFinanceCommand.operation == "PAYMENT",
                DemoFinanceCommand.idempotency_key == payment_body["idempotency_key"],
            )
        )
        assert command.state == "IN_PROGRESS"

    retried_payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=payment_body,
        headers=auth_headers,
    )
    assert retried_payment.status_code == 201, retried_payment.text
    line_id = retried_payment.json()["line"]["id"]
    offset_body = {
        "payment_line_id": line_id,
        "bill_id": bill_id,
        "offset_amt": "1200.00",
        "offset_date": "2026-08-16",
        "idempotency_key": "demo-offset-lock",
    }
    with session_factory() as transaction:
        reserve_demo_finance_command(
            transaction,
            operation="OFFSET",
            idempotency_key=offset_body["idempotency_key"],
            actor_id=actor_id,
            payload=DemoFullOffsetRequest.model_validate(offset_body).model_dump(
                mode="json"
            ),
        )

    event.listen(engine, "checkout", fast_lock_failure)
    try:
        with engine.connect() as locker:
            locker.exec_driver_sql("BEGIN IMMEDIATE")
            locked_offset = client.post(
                "/api/v1/offsets/demo-full",
                json=offset_body,
                headers=auth_headers,
            )
            locker.rollback()
    finally:
        event.remove(engine, "checkout", fast_lock_failure)
    assert locked_offset.status_code == 409, locked_offset.text
    assert locked_offset.json()["error"]["code"] == "DEMO_FINANCE_WRITE_BUSY"
    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(Offset)) == 0
        bill = transaction.get(Bill, bill_id)
        line = transaction.get(PaymentLine, line_id)
        assert bill.status == "UNSETTLED"
        assert bill.balance == 1800
        assert line.allocated_amt == 0
        assert line.balance_amt == 1200

    retried_offset = client.post(
        "/api/v1/offsets/demo-full",
        json=offset_body,
        headers=auth_headers,
    )
    assert retried_offset.status_code == 201, retried_offset.text
    assert retried_offset.json()["bill"]["status"] == "PARTIALLY_SETTLED"


def test_demo_offset_rejects_payment_line_already_used_by_another_bill(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    client_id, _case_id, bill_id = _demo_bill(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    payment_body = {
        "target_bill_id": bill_id,
        "amount": "1200.00",
        "pay_no": "DEMO-PAY-CROSS-BILL",
        "pay_date": "2026-08-16",
        "currency": "CNY",
        "pay_method": "BANK_TRANSFER",
        "bank_ref_no": "DEMO-BANK-CROSS-BILL",
        "idempotency_key": "demo-payment-cross-bill",
    }
    payment = client.post(
        "/api/v1/payments/demo-bank-receipts",
        json=payment_body,
        headers=auth_headers,
    )
    assert payment.status_code == 201, payment.text
    line_id = payment.json()["line"]["id"]
    offset_body = {
        "payment_line_id": line_id,
        "bill_id": bill_id,
        "offset_amt": "1200.00",
        "offset_date": "2026-08-16",
        "idempotency_key": "demo-offset-cross-bill",
    }
    with session_factory() as transaction:
        actor_id = transaction.scalar(
            select(DemoFinanceCommand.created_by).where(
                DemoFinanceCommand.operation == "BILL"
            )
        )
        other_bill = Bill(
            id=str(uuid4()),
            bill_no="DEMO-AR-OTHER-BILL",
            client_id=client_id,
            currency="CNY",
            direction="AR",
            status="UNSETTLED",
            total_service=1200,
            amount=1200,
            balance=1200,
        )
        transaction.add(other_bill)
        transaction.flush()
        transaction.add(
            Offset(
                id=str(uuid4()),
                payment_line_id=line_id,
                bill_id=other_bill.id,
                offset_amt=1200,
                offset_date=date(2026, 8, 15),
                is_reversed=False,
            )
        )
        transaction.commit()
        reserve_demo_finance_command(
            transaction,
            operation="OFFSET",
            idempotency_key=offset_body["idempotency_key"],
            actor_id=actor_id,
            payload=DemoFullOffsetRequest.model_validate(offset_body).model_dump(
                mode="json"
            ),
        )

    response = client.post(
        "/api/v1/offsets/demo-full",
        json=offset_body,
        headers=auth_headers,
    )
    assert response.status_code == 409, response.text
    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(Offset)) == 1
        bill = transaction.get(Bill, bill_id)
        line = transaction.get(PaymentLine, line_id)
        assert bill.status == "UNSETTLED"
        assert bill.balance == 1800
        assert line.allocated_amt == 0
        assert line.balance_amt == 1200

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
            "amount": "1800.00",
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


def test_demo_offset_rejects_cross_domain_bill_item_without_write(
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
        item = db.query(BillItem).filter(BillItem.bill_id == bill_id).first()
        item.fee_type = "GOV"
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
