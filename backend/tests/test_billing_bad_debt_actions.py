from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_Role, T_RolePerm
from app.modules.billing.models import BadDebtVoucher


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


def _create_ar_bill(client: TestClient, auth_headers: dict[str, str], client_id: str) -> str:
    resp = client.post(
        "/api/v1/bills/manual",
        json={
            "client_id": client_id,
            "currency": "CNY",
            "direction": "AR",
            "status": "UNSETTLED",
            "items": [
                {
                    "description": "服务费",
                    "quantity": 1,
                    "unit_price": "500.00",
                    "fee_type": "SERVICE",
                }
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_payment_and_offset(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    bill_id: str,
    amount: Decimal,
) -> None:
    payment_resp = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": str(amount),
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert payment_resp.status_code == 201, payment_resp.text
    payment_id = payment_resp.json()["id"]

    payment_detail_resp = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert payment_detail_resp.status_code == 200, payment_detail_resp.text
    payment_lines = payment_detail_resp.json()["payment_lines"]
    assert len(payment_lines) == 1
    payment_line_id = payment_lines[0]["id"]

    offset_resp = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line_id,
            "bill_id": bill_id,
            "offset_amt": str(amount),
        },
        headers=auth_headers,
    )
    assert offset_resp.status_code == 201, offset_resp.text


def _grant_bad_debt_mark_perm(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None, "Admin role should exist"

        existing = (
            db.query(T_RolePerm)
            .filter(
                T_RolePerm.role_id == admin_role.id,
                T_RolePerm.perm_code == "Billing.BadDebtMark",
            )
            .first()
        )
        if existing:
            return

        db.add(
            T_RolePerm(
                id=str(uuid4()),
                role_id=admin_role.id,
                perm_code="Billing.BadDebtMark",
            )
        )
        db.commit()


def test_mark_bad_debt_is_idempotent_and_creates_single_voucher(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _grant_bad_debt_mark_perm(session_factory)
    client_id = _create_client(client, auth_headers)
    bill_id = _create_ar_bill(client, auth_headers, client_id)

    resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["id"] == bill_id
    assert payload["status"] == "BAD_DEBT"
    assert payload["bad_debt_status"] == "OPEN"
    assert payload["bad_debt_substatus"] == "MANUAL_MARK"
    assert payload["bad_debt_voucher"]["bill_id"] == bill_id
    assert Decimal(str(payload["bad_debt_voucher"]["bad_debt_amount"])) == Decimal("500.00")
    assert Decimal(str(payload["bad_debt_remaining_amount"])) == Decimal("500.00")

    second_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    assert second_resp.status_code == 200, second_resp.text
    second_payload = second_resp.json()
    assert second_payload["bad_debt_voucher"]["id"] == payload["bad_debt_voucher"]["id"]
    assert second_payload["bad_debt_substatus"] == "MANUAL_MARK"

    with session_factory() as db:
        assert db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).count() == 1


def test_partial_payment_transfer_uses_remaining_balance_only(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _grant_bad_debt_mark_perm(session_factory)
    client_id = _create_client(client, auth_headers)
    bill_id = _create_ar_bill(client, auth_headers, client_id)

    _create_payment_and_offset(
        client,
        auth_headers,
        client_id=client_id,
        bill_id=bill_id,
        amount=Decimal("350.00"),
    )

    resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt",
        json={"mode": "TRANSFER", "remark": "剩余部分转坏账"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["id"] == bill_id
    assert payload["status"] == "BAD_DEBT"
    assert payload["bad_debt_status"] == "OPEN"
    assert payload["bad_debt_substatus"] == "PARTIAL_TRANSFER"
    assert payload["bad_debt_voucher"]["bill_id"] == bill_id
    assert Decimal(str(payload["bad_debt_voucher"]["bad_debt_amount"])) == Decimal("150.00")
    assert Decimal(str(payload["bad_debt_remaining_amount"])) == Decimal("150.00")
    assert payload["bad_debt_voucher"]["remark"] == "剩余部分转坏账"

    second_resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt",
        json={"mode": "TRANSFER", "remark": "should reuse existing voucher"},
        headers=auth_headers,
    )
    assert second_resp.status_code == 200, second_resp.text
    second_payload = second_resp.json()
    assert second_payload["bad_debt_voucher"]["id"] == payload["bad_debt_voucher"]["id"]
    assert second_payload["bad_debt_substatus"] == "PARTIAL_TRANSFER"

    with session_factory() as db:
        assert db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).count() == 1
