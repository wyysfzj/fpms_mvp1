"""Tests for client address and contact sub-resource endpoints (A2 batch)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

API = "/api/v1"


@pytest.fixture
def client_id(client: TestClient, auth_headers: dict[str, str]) -> str:
    """Create a test client and return its ID."""
    code = f"A2_{uuid4().hex[:8]}"
    resp = client.post(
        f"{API}/clients",
        json={"name_cn": "A2测试客户", "client_code": code},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ── Address tests ─────────────────────────────────────────


def test_create_address_billing(
    client: TestClient, auth_headers: dict[str, str], client_id: str
) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/addresses",
        json={
            "address_type": "BILLING",
            "address_line1": "100 Finance Road",
            "city": "Shanghai",
            "province": "Shanghai",
            "postal_code": "200000",
            "country_code": "CN",
            "is_default": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["address_type"] == "BILLING"
    assert data["address_line1"] == "100 Finance Road"
    assert data["city"] == "Shanghai"
    assert data["is_default"] is True
    assert data["client_id"] == client_id
    assert len(data["id"]) == 36  # UUID


def test_create_address_mailing(
    client: TestClient, auth_headers: dict[str, str], client_id: str
) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/addresses",
        json={
            "address_type": "MAILING",
            "address_line1": "200 Delivery Lane",
            "city": "Beijing",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["address_type"] == "MAILING"


def test_list_addresses(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    # Create two addresses first
    client.post(
        f"{API}/clients/{client_id}/addresses",
        json={"address_type": "BILLING", "address_line1": "Addr1"},
        headers=auth_headers,
    )
    client.post(
        f"{API}/clients/{client_id}/addresses",
        json={"address_type": "MAILING", "address_line1": "Addr2"},
        headers=auth_headers,
    )
    resp = client.get(
        f"{API}/clients/{client_id}/addresses",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 2


def test_update_address(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    # Create
    resp = client.post(
        f"{API}/clients/{client_id}/addresses",
        json={"address_type": "BILLING", "address_line1": "Old Street"},
        headers=auth_headers,
    )
    addr_id = resp.json()["id"]

    # Update
    resp = client.put(
        f"{API}/clients/{client_id}/addresses/{addr_id}",
        json={"address_line1": "New Street", "city": "Guangzhou"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["address_line1"] == "New Street"
    assert data["city"] == "Guangzhou"


def test_delete_address(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/addresses",
        json={"address_type": "BILLING", "address_line1": "To Delete"},
        headers=auth_headers,
    )
    addr_id = resp.json()["id"]

    del_resp = client.delete(
        f"{API}/clients/{client_id}/addresses/{addr_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 204

    # Verify removed
    list_resp = client.get(
        f"{API}/clients/{client_id}/addresses",
        headers=auth_headers,
    )
    ids = [a["id"] for a in list_resp.json()]
    assert addr_id not in ids


# ── Contact tests ─────────────────────────────────────────


def test_create_contact(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/contacts",
        json={
            "contact_name": "Zhang Wei",
            "title": "Director",
            "phone": "021-12345678",
            "mobile": "13800138000",
            "email": "zhang@example.com",
            "is_primary": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["contact_name"] == "Zhang Wei"
    assert data["mobile"] == "13800138000"
    assert data["is_primary"] is True
    assert data["client_id"] == client_id


def test_create_second_contact(
    client: TestClient, auth_headers: dict[str, str], client_id: str
) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "Li Ming", "email": "li@example.com"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["contact_name"] == "Li Ming"


def test_list_contacts(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "Contact A"},
        headers=auth_headers,
    )
    client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "Contact B"},
        headers=auth_headers,
    )
    resp = client.get(
        f"{API}/clients/{client_id}/contacts",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_update_contact(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "Old Name"},
        headers=auth_headers,
    )
    contact_id = resp.json()["id"]

    resp = client.put(
        f"{API}/clients/{client_id}/contacts/{contact_id}",
        json={"contact_name": "New Name", "title": "Manager"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["contact_name"] == "New Name"
    assert data["title"] == "Manager"


def test_delete_contact(client: TestClient, auth_headers: dict[str, str], client_id: str) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "To Remove"},
        headers=auth_headers,
    )
    contact_id = resp.json()["id"]

    del_resp = client.delete(
        f"{API}/clients/{client_id}/contacts/{contact_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 204

    list_resp = client.get(
        f"{API}/clients/{client_id}/contacts",
        headers=auth_headers,
    )
    ids = [c["id"] for c in list_resp.json()]
    assert contact_id not in ids


# ── Cross-client 404 tests ────────────────────────────────


def test_address_404_wrong_client(
    client: TestClient, auth_headers: dict[str, str], client_id: str
) -> None:
    # Create address on real client
    resp = client.post(
        f"{API}/clients/{client_id}/addresses",
        json={"address_type": "BILLING", "address_line1": "Test"},
        headers=auth_headers,
    )
    addr_id = resp.json()["id"]

    # Try to access via fake client ID
    resp = client.put(
        f"{API}/clients/00000000-0000-0000-0000-000000000000/addresses/{addr_id}",
        json={"city": "Hack"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_contact_404_wrong_client(
    client: TestClient, auth_headers: dict[str, str], client_id: str
) -> None:
    resp = client.post(
        f"{API}/clients/{client_id}/contacts",
        json={"contact_name": "Real Contact"},
        headers=auth_headers,
    )
    contact_id = resp.json()["id"]

    resp = client.put(
        f"{API}/clients/00000000-0000-0000-0000-000000000000/contacts/{contact_id}",
        json={"contact_name": "Hacked"},
        headers=auth_headers,
    )
    assert resp.status_code == 404
