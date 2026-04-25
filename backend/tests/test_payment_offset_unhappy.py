from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"POU-CL-{uuid4().hex[:8]}",
            "name_cn": "付款校验客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _assert_error(response, expected_code: str) -> None:
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["error"]["code"] == expected_code


def test_payment_rejects_duplicate_client_pay_no(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)
    pay_no = f"POU-PAY-{uuid4().hex[:8]}"
    payload = {
        "client_id": client_id,
        "amount": "100.00",
        "pay_no": pay_no,
        "pay_date": "2026-04-17",
        "currency": "CNY",
    }

    first = client.post("/api/v1/payments", json=payload, headers=auth_headers)
    assert first.status_code == 201, first.text

    duplicate = client.post("/api/v1/payments", json=payload, headers=auth_headers)
    _assert_error(duplicate, "PAYMENT_PAY_NO_DUPLICATE")


def test_payment_rejects_future_pay_date(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)

    response = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": "100.00",
            "pay_no": f"POU-FUT-{uuid4().hex[:8]}",
            "pay_date": "2100-01-01",
            "currency": "CNY",
        },
        headers=auth_headers,
    )

    _assert_error(response, "PAYMENT_DATE_INVALID")


def test_payment_rejects_negative_amount(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)

    response = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": "-1.00",
            "pay_no": f"POU-NEG-{uuid4().hex[:8]}",
            "pay_date": "2026-04-17",
            "currency": "CNY",
        },
        headers=auth_headers,
    )

    _assert_error(response, "PAYMENT_AMOUNT_INVALID")
