"""Tests for CaseReceipt manual CRUD (FR-FE-07)."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def case_id(client: TestClient, auth_headers: dict) -> str:
    """Create a test case and return its ID."""
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CR-TEST-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "Test Case for Receipt",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# --- CREATE ---


def test_create_case_receipt_success(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "fee_type": "SERVICE",
            "fee_code": "SVC-001",
            "fee_name": "服务费",
            "currency": "CNY",
            "receivable_amt": "1000.00",
            "received_amt": "1000.00",
            "last_receipt_date": "2026-03-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["case_id"] == case_id
    assert data["fee_type"] == "SERVICE"
    assert data["fee_name"] == "服务费"
    assert Decimal(str(data["receivable_amt"])) == Decimal("1000.00")


def test_create_case_receipt_invalid_case(client: TestClient, auth_headers: dict):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": "nonexistent-id",
            "receivable_amt": "100.00",
            "received_amt": "100.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_create_case_receipt_negative_amt(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "-10.00",
            "received_amt": "100.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_auto_arrears(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_arrears"] is True


def test_create_auto_prepayment(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "500.00",
            "received_amt": "1000.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_prepayment"] is True


def test_create_user_override_arrears(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
            "is_arrears": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_arrears"] is False


def test_create_user_override_prepayment(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "500.00",
            "received_amt": "1000.00",
            "is_prepayment": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["is_prepayment"] is False


# --- UPDATE ---


def test_update_case_receipt_success(client: TestClient, auth_headers: dict, case_id: str):
    create_resp = client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    receipt_id = create_resp.json()["id"]

    resp = client.put(
        f"/api/v1/case-receipts/{receipt_id}",
        json={"remark": "已核实", "invoice_no": "INV-001"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["remark"] == "已核实"
    assert resp.json()["invoice_no"] == "INV-001"


def test_update_recompute_flags(client: TestClient, auth_headers: dict, case_id: str):
    create_resp = client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    receipt_id = create_resp.json()["id"]

    resp = client.put(
        f"/api/v1/case-receipts/{receipt_id}",
        json={"received_amt": "50.00"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_arrears"] is True


def test_update_not_found(client: TestClient, auth_headers: dict):
    resp = client.put(
        "/api/v1/case-receipts/nonexistent-id",
        json={"remark": "test"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# --- LIST ---


def test_list_case_receipts_no_filter(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={"case_id": case_id, "receivable_amt": "100.00", "received_amt": "100.00"},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/case-receipts", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 1


def test_list_filter_by_client(client: TestClient, auth_headers: dict):
    resp = client.get(
        "/api/v1/case-receipts",
        params={"client_id": "nonexistent"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_list_filter_by_arrears(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "1000.00",
            "received_amt": "500.00",
        },
        headers=auth_headers,
    )
    resp = client.get(
        "/api/v1/case-receipts",
        params={"is_arrears": "true"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["is_arrears"] is True


def test_list_filter_by_date_range(client: TestClient, auth_headers: dict, case_id: str):
    client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "receivable_amt": "100.00",
            "received_amt": "100.00",
            "last_receipt_date": "2026-03-15",
        },
        headers=auth_headers,
    )
    resp = client.get(
        "/api/v1/case-receipts",
        params={"date_from": "2026-03-01", "date_to": "2026-03-31"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_list_pagination(client: TestClient, auth_headers: dict):
    resp = client.get(
        "/api/v1/case-receipts",
        params={"page": 1, "page_size": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["page"] == 1
    assert resp.json()["page_size"] == 2
    assert len(resp.json()["items"]) <= 2


# --- PERMISSIONS ---


def test_permissions_create(client: TestClient):
    resp = client.post(
        "/api/v1/case-receipts", json={"case_id": "x", "receivable_amt": "1", "received_amt": "1"}
    )
    assert resp.status_code == 401


def test_permissions_update(client: TestClient):
    resp = client.put("/api/v1/case-receipts/some-id", json={"remark": "x"})
    assert resp.status_code == 401


# --- INTEGRATION ---


def test_manual_receipt_no_conflict_with_auto(client: TestClient, auth_headers: dict, case_id: str):
    resp = client.post(
        "/api/v1/case-receipts",
        json={
            "case_id": case_id,
            "fee_type": "MISC",
            "receivable_amt": "200.00",
            "received_amt": "200.00",
            "remark": "手工录入",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    get_resp = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)
    assert get_resp.status_code in (200, 404)
