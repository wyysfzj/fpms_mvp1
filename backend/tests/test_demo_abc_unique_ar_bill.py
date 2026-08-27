from __future__ import annotations

import runpy
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.billing.models import Bill, BillDraftSource, BillItem, DemoFinanceCommand
from app.modules.fees.models import FeeDraft


def _runtime_helpers():
    return runpy.run_path(
        str(Path(__file__).with_name("test_demo_abc_runtime_service_draft.py"))
    )


def _locked_demo_draft(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
) -> tuple[str, str, str]:
    helpers = _runtime_helpers()
    helpers["_configure_bundle"](tmp_path, monkeypatch, integrated=True)
    client_id, case_id = helpers["_seed_case"](session_factory)
    intent = uuid4().hex
    obligation_response = client.post(
        "/api/v1/fees/demo-service-obligations",
        json={
            "case_id": case_id,
            "idempotency_key": f"bill-source-{intent}",
        },
        headers=auth_headers,
    )
    assert obligation_response.status_code == 201, obligation_response.text
    obligation_id = obligation_response.json()["obligation"]["id"]
    instruction_response = client.post(
        f"/api/v1/fees/obligations/{obligation_id}/instruction",
        json={"instruction": "PAY", "idempotency_key": f"bill-pay-{intent}"},
        headers=auth_headers,
    )
    assert instruction_response.status_code == 200, instruction_response.text
    draft_response = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "GENERIC",
            "currency": "CNY",
            "obligation_id": obligation_id,
        },
        headers=auth_headers,
    )
    assert draft_response.status_code == 201, draft_response.text
    draft_id = draft_response.json()["id"]
    lock_response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers
    )
    assert lock_response.status_code == 200, lock_response.text
    return client_id, case_id, draft_id


def test_demo_bill_requires_locked_draft_and_creates_no_rows(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, draft_id = _locked_demo_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as db:
        db.get(FeeDraft, draft_id).status = "OPEN"
        db.commit()

    response = client.post(
        "/api/v1/bills/demo-from-draft",
        json={
            "draft_id": draft_id,
            "bill_no": "DEMO-AR-OPEN",
            "bill_date": "2026-08-16",
            "due_date": "2026-08-31",
            "idempotency_key": "demo-bill-open-1",
        },
        headers=auth_headers,
    )
    assert response.status_code == 409, response.text
    with session_factory() as db:
        assert db.query(Bill).count() == 0
        assert db.query(BillItem).count() == 0
        assert db.query(BillDraftSource).count() == 0


def test_demo_bill_is_exactly_once_and_billed_draft_cannot_unlock(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    client_id, case_id, draft_id = _locked_demo_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    command = {
        "draft_id": draft_id,
        "bill_no": "DEMO-AR-0001",
        "bill_date": "2026-08-16",
        "due_date": "2026-08-31",
        "idempotency_key": "demo-bill-intent-1",
    }

    created_response = client.post(
        "/api/v1/bills/demo-from-draft", json=command, headers=auth_headers
    )
    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    bill_id = created["bill"]["id"]
    assert created["reused"] is False
    assert created["idempotency_key"] == command["idempotency_key"]
    assert created["bill"]["client_id"] == client_id
    assert created["bill"]["case_id"] == case_id
    assert created["bill"]["currency"] == "CNY"
    assert created["bill"]["direction"] == "AR"
    assert created["bill"]["status"] == "UNSETTLED"
    assert created["bill"]["bill_date"] == "2026-08-16"
    assert created["bill"]["due_date"] == "2026-08-31"
    assert created["bill"]["amount"] == "1500.00"
    assert created["bill"]["balance"] == "1500.00"
    assert created["bill"]["total_service"] == "1500.00"
    assert created["bill"]["total_gov"] == "0.00"
    assert created["bill"]["source_draft_ids"] == [draft_id]
    assert len(created["bill"]["items"]) == 2
    assert all(item["fee_type"] == "SERVICE" for item in created["bill"]["items"])

    replay_response = client.post(
        "/api/v1/bills/demo-from-draft", json=command, headers=auth_headers
    )
    assert replay_response.status_code == 201, replay_response.text
    assert replay_response.json()["reused"] is True
    assert replay_response.json()["bill"]["id"] == bill_id

    reconciled = client.get(
        f"/api/v1/bills/from-drafts/idempotency/{command['idempotency_key']}",
        headers=auth_headers,
    )
    assert reconciled.status_code == 200, reconciled.text
    assert reconciled.json()["reused"] is True
    assert reconciled.json()["bill"]["id"] == bill_id

    drifted = dict(command, due_date="2026-09-01")
    drift_response = client.post(
        "/api/v1/bills/demo-from-draft", json=drifted, headers=auth_headers
    )
    assert drift_response.status_code == 409, drift_response.text

    second_key = dict(command, idempotency_key="demo-bill-intent-2")
    consumed_response = client.post(
        "/api/v1/bills/demo-from-draft", json=second_key, headers=auth_headers
    )
    assert consumed_response.status_code == 409, consumed_response.text

    unlock_response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/unlock", headers=auth_headers
    )
    assert unlock_response.status_code == 409, unlock_response.text

    with session_factory() as db:
        assert db.query(Bill).count() == 1
        assert db.query(BillItem).count() == 2
        assert db.query(BillDraftSource).count() == 1
        assert db.query(DemoFinanceCommand).count() == 1
        durable = db.query(DemoFinanceCommand).one()
        assert durable.operation == "BILL"
        assert durable.state == "COMPLETED"
        assert durable.result_snapshot
        source = db.query(BillDraftSource).one()
        assert source.bill_id == bill_id
        assert source.draft_id == draft_id
        assert source.command_hash

        db.add(
            BillDraftSource(
                id=str(uuid4()),
                bill_id=bill_id,
                draft_id=draft_id,
                idempotency_key="direct-duplicate",
                command_hash="0" * 64,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()


def test_demo_bill_dates_are_explicit_and_ordered(
    client,
    auth_headers,
    session_factory,
    tmp_path,
    monkeypatch,
):
    _client_id, _case_id, draft_id = _locked_demo_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    response = client.post(
        "/api/v1/bills/demo-from-draft",
        json={
            "draft_id": draft_id,
            "bill_date": date(2026, 8, 16).isoformat(),
            "due_date": date(2026, 8, 15).isoformat(),
            "idempotency_key": "demo-bill-date-1",
        },
        headers=auth_headers,
    )
    assert response.status_code == 422, response.text
    with session_factory() as db:
        assert db.query(Bill).count() == 0

    whitespace_id = client.post(
        "/api/v1/bills/demo-from-draft",
        json={
            "draft_id": f" {draft_id}",
            "bill_date": "2026-08-16",
            "idempotency_key": "demo-bill-whitespace",
        },
        headers=auth_headers,
    )
    assert whitespace_id.status_code == 422, whitespace_id.text

    datetime_value = client.post(
        "/api/v1/bills/demo-from-draft",
        json={
            "draft_id": draft_id,
            "bill_date": "2026-08-16T00:00:00",
            "idempotency_key": "demo-bill-datetime",
        },
        headers=auth_headers,
    )
    assert datetime_value.status_code == 422, datetime_value.text
