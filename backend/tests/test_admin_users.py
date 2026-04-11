from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def test_admin_created_user_can_login(client: TestClient, auth_headers: dict[str, str]) -> None:
    username = f"qa_finance_{uuid4().hex[:8]}"
    password = "Password123!"

    create_response = client.post(
        "/api/v1/admin/users",
        headers=auth_headers,
        json={
            "username": username,
            "password": password,
            "roles": ["Admin"],
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["username"] == username
    assert "password" not in create_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
