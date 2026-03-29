from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_Role, T_RolePerm
from app.modules.billing.models import BadDebtRecovery, BadDebtVoucher


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


def _grant_bad_debt_perms(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None, "Admin role should exist"

        existing_perm_codes = {
            row.perm_code
            for row in db.query(T_RolePerm.perm_code)
            .filter(T_RolePerm.role_id == admin_role.id)
            .all()
        }
        for perm_code in ("Billing.BadDebtMark", "Billing.BadDebtRecover"):
            if perm_code in existing_perm_codes:
                continue
            db.add(
                T_RolePerm(
                    id=str(uuid4()),
                    role_id=admin_role.id,
                    perm_code=perm_code,
                )
            )
        db.commit()


def test_recovery_writes_rows_and_tracks_remaining_amount(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _grant_bad_debt_perms(session_factory)
    client_id = _create_client(client, auth_headers)
    bill_id = _create_ar_bill(client, auth_headers, client_id)

    mark_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    assert mark_resp.status_code == 200, mark_resp.text

    first_resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt/recover",
        json={
            "recovery_amount": "120.00",
            "recovery_date": "2026-06-01",
            "remark": "first recovery",
        },
        headers=auth_headers,
    )
    assert first_resp.status_code == 200, first_resp.text
    first_payload = first_resp.json()
    assert first_payload["bad_debt_status"] == "OPEN"
    assert first_payload["bad_debt_substatus"] == "PARTIAL_RECOVERY"
    assert Decimal(str(first_payload["bad_debt_voucher"]["recovered_amount"])) == Decimal("120.00")
    assert Decimal(str(first_payload["bad_debt_total_recovered"])) == Decimal("120.00")
    assert Decimal(str(first_payload["bad_debt_remaining_amount"])) == Decimal("380.00")
    assert len(first_payload["bad_debt_recoveries"]) == 1
    assert first_payload["bad_debt_recoveries"][0]["remark"] == "first recovery"

    second_resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt/recover",
        json={
            "recovery_amount": "380.00",
            "recovery_date": "2026-06-15",
            "remark": "second recovery",
        },
        headers=auth_headers,
    )
    assert second_resp.status_code == 200, second_resp.text
    second_payload = second_resp.json()
    assert second_payload["bad_debt_status"] == "CLOSED"
    assert second_payload["bad_debt_substatus"] == "FULLY_RECOVERED"
    assert second_payload["bad_debt_voucher"]["status"] == "CLOSED"
    assert Decimal(str(second_payload["bad_debt_voucher"]["recovered_amount"])) == Decimal("500.00")
    assert Decimal(str(second_payload["bad_debt_total_recovered"])) == Decimal("500.00")
    assert Decimal(str(second_payload["bad_debt_remaining_amount"])) == Decimal("0")
    assert len(second_payload["bad_debt_recoveries"]) == 2
    assert second_payload["bad_debt_recoveries"][1]["remark"] == "second recovery"

    with session_factory() as db:
        assert db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).count() == 1
        voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).first()
        assert voucher is not None
        assert (
            db.query(BadDebtRecovery).filter(BadDebtRecovery.voucher_id == voucher.id).count() == 2
        )


def test_recovery_rejects_amounts_over_remaining_balance(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _grant_bad_debt_perms(session_factory)
    client_id = _create_client(client, auth_headers)
    bill_id = _create_ar_bill(client, auth_headers, client_id)

    mark_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    assert mark_resp.status_code == 200, mark_resp.text

    resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt/recover",
        json={"recovery_amount": "600.00", "remark": "too much"},
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "BAD_DEBT_RECOVERY_EXCEEDS_REMAINING"

    with session_factory() as db:
        voucher = db.query(BadDebtVoucher).filter(BadDebtVoucher.bill_id == bill_id).first()
        assert voucher is not None
        assert Decimal(str(voucher.recovered_amount)) == Decimal("0")
        assert (
            db.query(BadDebtRecovery).filter(BadDebtRecovery.voucher_id == voucher.id).count() == 0
        )
