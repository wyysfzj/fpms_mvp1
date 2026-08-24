from __future__ import annotations

import hashlib
import json
import runpy
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.api import deps
from app.modules.annuity import service as annuity_service
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.billing.models import DemoFinanceCommand
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.grant_fees import demo_official_fee
from app.modules.masterdata.clients.models import Client


@pytest.fixture
def runtime_bundle(tmp_path: Path, monkeypatch):
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_grant_official_fee.py"))
    )
    runtime = helpers["runtime_bundle"].__wrapped__(tmp_path, monkeypatch)
    bundle = next(runtime)
    yield bundle
    try:
        next(runtime)
    except StopIteration:
        pass


def _gov_pay_list(
    session_factory, runtime_bundle: Path
) -> tuple[int, list[tuple[str, Decimal]]]:
    helpers = runpy.run_path(
        str(Path(__file__).with_name("test_demo_v6_grant_official_fee.py"))
    )
    with session_factory() as transaction:
        _case, _document, task, evidence, _book = helpers["_seed"](
            transaction, label="GOV-PAYMENT"
        )
        preview = demo_official_fee.preview_grant_official_fees(
            transaction, grant_fee_task_id=task.id
        )
        confirmed = demo_official_fee.confirm_grant_official_fees(
            helpers["_command"](task, evidence, preview), transaction
        )
        draft = transaction.get(FeeDraft, confirmed.draft_id)
        client_id = transaction.scalar(select(Client.id).order_by(Client.id))
        if client_id is None:
            client = Client(
                id=str(uuid4()),
                client_code="CYIP-GOV-PAYMENT",
                name_cn="北京中云知识产权代理有限公司",
                default_currency="CNY",
            )
            transaction.add(client)
            transaction.flush()
            client_id = client.id
        draft.client_id = client_id
        transaction.commit()
        items = list(
            transaction.scalars(
                select(FeeItem)
                .where(FeeItem.draft_id == confirmed.draft_id)
                .order_by(FeeItem.fee_code)
            )
        )
        created = annuity_service.create_pay_list_from_fee_items(
            transaction,
            fee_item_ids=[item.id for item in items],
            planned_pay_date=date(2026, 8, 24),
            remark="授权登记官费清单",
            actor_id=items[0].created_by,
        )
        assert created["pay_list"] is not None, created
        item_facts = [(item.id, item.amount) for item in items]
        transaction.commit()
        return created["pay_list"]["id"], item_facts


def _command(
    pay_list_id: int,
    item: tuple[str, Decimal],
    key: str,
) -> dict[str, object]:
    return {
        "pay_list_id": pay_list_id,
        "fee_item_id": item[0],
        "paid_date": "2026-08-24",
        "paid_amount": format(item[1], ".2f"),
        "official_receipt_no": None,
        "voucher_no": None,
        "invoice_no": None,
        "remark": "已登记，待官方凭证核验",
        "idempotency_key": key,
    }


def test_demo_gov_payment_is_recoverable_pending_evidence_and_idempotent(
    client,
    auth_headers,
    session_factory,
    runtime_bundle,
) -> None:
    pay_list_id, items = _gov_pay_list(session_factory, runtime_bundle)
    body = _command(pay_list_id, items[0], "demo-v6-gov-payment-1")
    path = "/api/v1/gov-payments/demo-command"

    first = client.post(path, json=body, headers=auth_headers)
    assert first.status_code == 201, first.text
    payload = first.json()
    assert payload["reused"] is False
    assert payload["fact_status"] == "REGISTERED_PENDING_OFFICIAL_EVIDENCE"
    assert payload["gov_payment"]["fee_item_id"] == items[0][0]
    assert payload["gov_payment"]["paid_amount"] == format(items[0][1], ".2f")
    assert payload["gov_payment"]["official_receipt_no"] is None
    assert payload["gov_payment"]["voucher_no"] is None
    assert payload["gov_payment"]["invoice_no"] is None

    replay = client.post(path, json=body, headers=auth_headers)
    assert replay.status_code == 200, replay.text
    assert replay.json() == {**payload, "reused": True}

    with session_factory() as transaction:
        command = transaction.scalar(
            select(DemoFinanceCommand).where(
                DemoFinanceCommand.operation == "GOV_PAYMENT",
                DemoFinanceCommand.idempotency_key == body["idempotency_key"],
            )
        )
        command.state = "IN_PROGRESS"
        command.result_snapshot = None
        transaction.commit()
    recovered = client.get(
        f"/api/v1/gov-payments/idempotency/{body['idempotency_key']}",
        headers=auth_headers,
    )
    assert recovered.status_code == 200, recovered.text
    assert recovered.json()["gov_payment"]["id"] == payload["gov_payment"]["id"]
    assert recovered.json()["reused"] is True

    second_body = _command(pay_list_id, items[1], "demo-v6-gov-payment-2")
    second = client.post(path, json=second_body, headers=auth_headers)
    assert second.status_code == 201, second.text
    assert second.json()["fact_status"] == "REGISTERED_PENDING_OFFICIAL_EVIDENCE"
    assert client.get(
        f"/api/v1/gov-payments/idempotency/{body['idempotency_key']}",
        headers=auth_headers,
    ).status_code == 200

    drifted = {**body, "paid_amount": "1.00"}
    assert client.post(path, json=drifted, headers=auth_headers).status_code == 409
    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 2
        pay_list = transaction.get(PayList, pay_list_id)
        assert pay_list.status == "PAID"
        assert transaction.scalar(select(func.sum(GovPayment.paid_amount))) == pay_list.total_amount
        first_payment = transaction.scalar(
            select(GovPayment).where(GovPayment.fee_item_id == items[0][0])
        )
        first_payment.remark = "被篡改的登记事实"
        transaction.commit()

    assert client.get(
        f"/api/v1/gov-payments/idempotency/{body['idempotency_key']}",
        headers=auth_headers,
    ).status_code == 409
    assert client.post(path, json=body, headers=auth_headers).status_code == 409


def test_demo_gov_payment_http_and_scope_boundaries(
    client,
    auth_headers,
    session_factory,
    runtime_bundle,
    monkeypatch,
) -> None:
    pay_list_id, items = _gov_pay_list(session_factory, runtime_bundle)
    body = _command(pay_list_id, items[0], "demo-v6-gov-payment-boundary")
    path = "/api/v1/gov-payments/demo-command"
    assert client.post(path, json=body).status_code == 401
    assert client.get("/api/v1/gov-payments/idempotency/absent").status_code == 401
    original_permissions = deps.get_user_permissions
    monkeypatch.setattr(deps, "get_user_permissions", lambda _db, _user_id: set())
    assert client.post(path, json=body, headers=auth_headers).status_code == 403
    assert client.get(
        "/api/v1/gov-payments/idempotency/absent",
        headers=auth_headers,
    ).status_code == 403
    monkeypatch.setattr(deps, "get_user_permissions", original_permissions)

    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        pending_body = _command(pay_list_id, items[1], "demo-v6-gov-payment-pending")
        pending_snapshot = json.dumps(
            {
                "actor_id": actor_id,
                "operation": "GOV_PAYMENT",
                "payload": pending_body,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        transaction.add(
            DemoFinanceCommand(
                id=str(uuid4()),
                operation="GOV_PAYMENT",
                idempotency_key=pending_body["idempotency_key"],
                state="IN_PROGRESS",
                command_hash=hashlib.sha256(pending_snapshot.encode("utf-8")).hexdigest(),
                command_snapshot=pending_snapshot,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )
        transaction.commit()
    assert client.get(
        "/api/v1/gov-payments/idempotency/demo-v6-gov-payment-pending",
        headers=auth_headers,
    ).status_code == 202

    assert client.post(path, json={**body, "pay_list_id": 999999}, headers=auth_headers).status_code == 404
    assert client.post(path, json={**body, "paid_amount": "1.00"}, headers=auth_headers).status_code == 409
    assert client.post(path, json={**body, "official_receipt_no": "R-1"}, headers=auth_headers).status_code == 422
    assert client.post(path, json={**body, "unexpected": True}, headers=auth_headers).status_code == 422
    assert client.get(
        f"/api/v1/gov-payments/idempotency/{'x' * 97}",
        headers=auth_headers,
    ).status_code == 422
    assert client.get(
        "/api/v1/gov-payments/idempotency/absent",
        headers=auth_headers,
    ).status_code == 404
