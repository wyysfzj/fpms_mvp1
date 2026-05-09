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


def test_list_system_params_includes_metadata(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /system/params includes operator-facing metadata."""
    key = "test_param_metadata"
    resp = client.put(
        f"/api/v1/system/params/{key}",
        json={
            "param_value": "hello",
            "value_type": "string",
            "description": "Metadata description",
            "is_secret": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    list_resp = client.get("/api/v1/system/params", headers=auth_headers)
    assert list_resp.status_code == 200
    param = next(p for p in list_resp.json() if p["param_key"] == key)

    assert param["description"] == "Metadata description"
    assert param["created_at"]
    assert param["updated_at"]


def test_config_readiness_reports_missing_seed_config(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """GET /system/config-readiness reports counts and hard blockers."""
    resp = client.get("/api/v1/system/config-readiness", headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "BLOCKED"
    assert data["hard_blocked"] is True

    counts = {item["key"]: item["count"] for item in data["counts"]}
    assert counts["fee_rate"] == 0
    assert counts["commission_rule"] == 0
    assert counts["template"] == 0
    assert counts["letter_head"] == 0
    assert counts["country"] == 0
    assert counts["department"] == 0
    assert counts["doc_template"] >= 1
    assert counts["task_template"] >= 1

    missing = {item["key"]: item for item in data["missing"]}
    assert "system_param.default_currency" in missing
    assert "system_param.bill_template_path" in missing
    assert "fee_rate.apply" in missing
    assert "commission_rule.enabled" in missing
    assert "template.enabled" in missing
    assert "letter_head.default" in missing
    assert "country.active" in missing
    assert "department.active" in missing


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
