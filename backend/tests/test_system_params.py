"""Tests for SystemParam CRUD API."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_system_params(client: TestClient, auth_headers: dict[str, str]) -> None:
    """GET /system/params returns 200 with list."""
    resp = client.get("/api/v1/system/params", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_list_system_params_unauthorized(client: TestClient) -> None:
    """GET /system/params without token returns 401."""
    resp = client.get("/api/v1/system/params")
    assert resp.status_code == 401


def test_upsert_system_param_create(client: TestClient, auth_headers: dict[str, str]) -> None:
    """PUT creates a new param, then it appears in list."""
    key = "test_param_create"
    resp = client.put(
        f"/api/v1/system/params/{key}",
        json={"param_value": "hello", "value_type": "string", "is_secret": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Verify it appears in list
    list_resp = client.get("/api/v1/system/params", headers=auth_headers)
    keys = [p["param_key"] for p in list_resp.json()]
    assert key in keys


def test_upsert_system_param_update(client: TestClient, auth_headers: dict[str, str]) -> None:
    """PUT updates an existing param's value."""
    key = "test_param_update"
    # Create
    client.put(
        f"/api/v1/system/params/{key}",
        json={"param_value": "v1", "value_type": "string", "is_secret": False},
        headers=auth_headers,
    )
    # Update
    resp = client.put(
        f"/api/v1/system/params/{key}",
        json={"param_value": "v2"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # Verify updated value
    list_resp = client.get("/api/v1/system/params", headers=auth_headers)
    param = next(p for p in list_resp.json() if p["param_key"] == key)
    assert param["param_value"] == "v2"


def test_secret_masking(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Secret params show '******' in list endpoint."""
    key = "test_secret_param"
    client.put(
        f"/api/v1/system/params/{key}",
        json={"param_value": "super_secret", "value_type": "string", "is_secret": True},
        headers=auth_headers,
    )

    list_resp = client.get("/api/v1/system/params", headers=auth_headers)
    param = next(p for p in list_resp.json() if p["param_key"] == key)
    assert param["param_value"] == "******"
    assert param["is_secret"] is True


def test_upsert_system_param_forbidden(client: TestClient) -> None:
    """PUT without auth returns 401."""
    resp = client.put(
        "/api/v1/system/params/some_key",
        json={"param_value": "val"},
    )
    assert resp.status_code == 401
