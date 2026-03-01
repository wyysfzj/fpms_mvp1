from __future__ import annotations

from typing import Any

import app.api.deps as deps


def test_login_success_returns_token(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("access_token")


def test_auth_required_returns_401_error_envelope(client) -> None:
    response = client.get("/api/v1/documents")
    assert response.status_code == 401
    payload = response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("code")
    assert payload["error"].get("message")


def test_forbidden_returns_403_error_envelope(client, auth_headers, monkeypatch) -> None:
    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = client.get("/api/v1/documents", headers=auth_headers)
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["details"]["required_perm"] == "Doc.Read"


def test_pagination_shape_on_list_endpoint(client, auth_headers) -> None:
    response = client.get("/api/v1/clients", headers=auth_headers)
    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    for key in ("items", "page", "page_size", "total"):
        assert key in payload
