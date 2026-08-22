from __future__ import annotations

from uuid import uuid4


def test_happy_path_clients_cases_tasks_fees(client, auth_headers) -> None:
    client_payload = {
        "client_code": f"C-{uuid4().hex[:8]}",
        "name_cn": "Test Client",
        "name_en": "Test Client EN",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    response = client.post("/api/v1/clients", json=client_payload, headers=auth_headers)
    assert response.status_code == 201
    client_id = response.json().get("id")
    assert client_id

    case_payload = {
        "case_no": f"CASE-{uuid4().hex[:8]}",
        "fee_reduction": "0",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
    }
    response = client.post("/api/v1/cases", json=case_payload, headers=auth_headers)
    assert response.status_code == 201
    case_id = response.json().get("id")
    assert case_id

    task_payload = {
        "case_id": case_id,
        "title": "Initial Task",
        "due_date": "2026-02-01",
    }
    response = client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    assert response.status_code == 201
    task_id = response.json().get("id")
    assert task_id

    fee_rate_payload = {
        "fee_code": f"FEE-{uuid4().hex[:6]}",
        "fee_name": "Service Fee",
        "fee_type": "SERVICE",
        "currency": "CNY",
        "default_amount": "100.00",
        "enabled": True,
    }
    response = client.post("/api/v1/fees/rates", json=fee_rate_payload, headers=auth_headers)
    assert response.status_code == 201
    rate_id = response.json().get("id")
    assert rate_id

    fee_draft_payload = {
        "case_id": case_id,
        "client_id": client_id,
        "draft_type": "GENERIC",
        "currency": "CNY",
    }
    response = client.post("/api/v1/fees/drafts", json=fee_draft_payload, headers=auth_headers)
    assert response.status_code == 201
    draft_id = response.json().get("id")
    assert draft_id

    fee_item_payload = {
        "rate_id": rate_id,
        "quantity": "1",
        "unit_price": "100.00",
    }
    response = client.post(
        f"/api/v1/fees/drafts/{draft_id}/items",
        json=fee_item_payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    item_id = response.json().get("id")
    assert item_id

    response = client.post(f"/api/v1/fees/drafts/{draft_id}/lock", headers=auth_headers)
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
