from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.billing.models import Bill


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert "error" in payload, payload
    assert payload["error"].get("code") == error_code, payload
    assert payload["error"].get("message")
    return payload


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("COL-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _insert_bill(
    session_factory: sessionmaker,
    *,
    client_id: str,
    amount: Decimal,
    balance: Decimal,
    due_date: date,
    status: str = "UNSETTLED",
    currency: str = "CNY",
) -> str:
    with session_factory() as db:
        bill = Bill(
            id=str(uuid4()),
            bill_no=_uid("BILL"),
            client_id=client_id,
            currency=currency,
            direction="AR",
            status=status,
            bill_date=due_date,
            due_date=due_date,
            total_gov=Decimal("0"),
            total_service=amount,
            total_misc=Decimal("0"),
            amount=amount,
            balance=balance,
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill.id


def test_collections_dunning_generation_idempotency_and_conflicts(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("100.00"),
        balance=Decimal("100.00"),
        due_date=date(2026, 1, 10),
    )
    _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("50.00"),
        balance=Decimal("10.00"),
        due_date=date(2026, 1, 12),
    )

    payload = {"to_date": "2026-01-31", "client_id": client_id}
    create_resp = client.post("/api/v1/dunning", headers=auth_headers, json=payload)
    assert create_resp.status_code == 200, create_resp.text
    create_payload = create_resp.json()
    assert {"summary", "batches"}.issubset(create_payload)
    assert create_payload["summary"]["created"] == 1
    assert create_payload["summary"]["reused"] == 0
    assert len(create_payload["batches"]) == 1
    assert create_payload["batches"][0]["line_count"] >= 2

    reused_resp = client.post("/api/v1/dunning", headers=auth_headers, json=payload)
    assert reused_resp.status_code == 200, reused_resp.text
    reused_payload = reused_resp.json()
    assert reused_payload["summary"]["created"] == 0
    assert reused_payload["summary"]["reused"] == 1
    assert reused_payload["batches"][0]["reused"] is True

    strict_conflict_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={**payload, "strict_conflict": True},
    )
    _assert_error(strict_conflict_resp, 409, "DUNNING_BATCH_STATE_INVALID")

    invalid_scope_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={
            "to_date": "2026-01-31",
            "include_statuses": ["UNSETTLED"],
            "exclude_statuses": ["UNSETTLED"],
        },
    )
    _assert_error(invalid_scope_resp, 400, "DUNNING_BATCH_STATE_INVALID")

    missing_scope_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={"to_date": "2026-01-31", "client_id": str(uuid4())},
    )
    _assert_error(missing_scope_resp, 404, "DUNNING_BATCH_NOT_FOUND")

    validation_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={"client_id": client_id},
    )
    _assert_error(validation_resp, 422, "VALIDATION_ERROR")


def test_collections_dunning_list_and_bad_debt_lifecycle(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("200.00"),
        balance=Decimal("200.00"),
        due_date=date(2026, 2, 1),
    )

    create_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={"to_date": "2026-02-28", "client_id": client_id},
    )
    assert create_resp.status_code == 200, create_resp.text

    list_resp = client.get(
        "/api/v1/dunning",
        headers=auth_headers,
        params={
            "round_no": 1,
            "status": "DRAFT",
            "client_id": client_id,
            "page": 1,
            "page_size": 1,
        },
    )
    assert list_resp.status_code == 200, list_resp.text
    list_payload = list_resp.json()
    assert set(list_payload) == {"items", "page", "page_size", "total"}
    assert list_payload["page"] == 1
    assert list_payload["page_size"] == 1
    assert list_payload["total"] >= 1
    assert all(item["client_id"] == client_id for item in list_payload["items"])

    list_validation_resp = client.get(
        "/api/v1/dunning",
        headers=auth_headers,
        params={"page_size": 101},
    )
    _assert_error(list_validation_resp, 422, "VALIDATION_ERROR")

    mark_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    assert mark_resp.status_code == 200, mark_resp.text
    mark_payload = mark_resp.json()
    assert mark_payload["id"] == bill_id
    assert mark_payload["status"] == "BAD_DEBT"

    duplicate_mark_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt", headers=auth_headers)
    _assert_error(duplicate_mark_resp, 409, "BAD_DEBT_ALREADY_MARKED")

    restore_resp = client.post(f"/api/v1/bills/{bill_id}/bad-debt/restore", headers=auth_headers)
    assert restore_resp.status_code == 200, restore_resp.text
    restore_payload = restore_resp.json()
    assert restore_payload["id"] == bill_id
    assert restore_payload["status"] == "UNSETTLED"

    restore_conflict_resp = client.post(
        f"/api/v1/bills/{bill_id}/bad-debt/restore",
        headers=auth_headers,
    )
    _assert_error(restore_conflict_resp, 409, "BAD_DEBT_RESTORE_INVALID")

    missing_bill_resp = client.post(
        f"/api/v1/bills/{uuid4()}/bad-debt",
        headers=auth_headers,
    )
    _assert_error(missing_bill_resp, 404, "BILL_NOT_FOUND")

    zero_balance_bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("300.00"),
        balance=Decimal("0.00"),
        due_date=date(2026, 2, 2),
    )
    ineligible_resp = client.post(
        f"/api/v1/bills/{zero_balance_bill_id}/bad-debt",
        headers=auth_headers,
    )
    _assert_error(ineligible_resp, 400, "BAD_DEBT_NOT_ALLOWED")


def test_collections_dunning_detail_includes_lines(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    bill_id = _insert_bill(
        session_factory,
        client_id=client_id,
        amount=Decimal("120.00"),
        balance=Decimal("120.00"),
        due_date=date(2026, 3, 1),
    )

    create_resp = client.post(
        "/api/v1/dunning",
        headers=auth_headers,
        json={"to_date": "2026-03-31", "client_id": client_id},
    )
    assert create_resp.status_code == 200, create_resp.text
    create_payload = create_resp.json()
    assert create_payload["summary"]["created"] >= 1
    batch = create_payload["batches"][0]

    detail_resp = client.get(f"/api/v1/dunning/{batch['id']}", headers=auth_headers)
    assert detail_resp.status_code == 200, detail_resp.text
    detail_payload = detail_resp.json()
    assert detail_payload["id"] == batch["id"]
    assert detail_payload["round_no"] == batch["round_no"]
    assert "lines" in detail_payload
    assert isinstance(detail_payload["lines"], list)
    assert len(detail_payload["lines"]) >= 1
    assert any(line["bill_id"] == bill_id for line in detail_payload["lines"])
