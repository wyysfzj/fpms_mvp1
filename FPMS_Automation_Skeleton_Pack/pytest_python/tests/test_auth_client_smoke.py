from __future__ import annotations

import os
from typing import Any

import pytest
import requests

from framework.api_client import ApiClient, ApiClientAuthError


class FakeResponse:
    def __init__(
        self, status_code: int, payload: dict[str, Any] | None = None, text: str = ""
    ) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self._payload

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        url = kwargs["url"]
        if url.endswith("/auth/login"):
            return FakeResponse(
                200, {"access_token": "unit-token", "token_type": "bearer"}
            )
        if url.endswith("/auth/me"):
            return FakeResponse(
                200, {"user": {"username": "admin"}, "roles": [], "permissions": []}
            )
        return FakeResponse(404, text="not found")


class FailingLoginSession:
    def request(self, **kwargs: Any) -> FakeResponse:
        return FakeResponse(
            401, {"code": "AUTH_INVALID", "message": "Invalid username or password"}
        )


def test_login_stores_token_and_authorizes_followup_requests() -> None:
    api = ApiClient("http://localhost:8000/api/v1/")
    fake_session = FakeSession()
    api.session = fake_session  # type: ignore[assignment]

    token = api.login("admin", "admin123")
    response = api.get("/auth/me")

    assert token == "unit-token"
    assert api.access_token == "unit-token"
    assert response.status_code == 200
    assert fake_session.calls[0]["url"] == "http://localhost:8000/api/v1/auth/login"
    assert fake_session.calls[1]["headers"]["Authorization"] == "Bearer unit-token"


def test_legacy_api_base_url_is_normalized_without_duplicate_v1() -> None:
    legacy_api = ApiClient("http://localhost:8000/api")
    versioned_api = ApiClient("http://localhost:8000/api/v1")
    legacy_session = FakeSession()
    versioned_session = FakeSession()
    legacy_api.session = legacy_session  # type: ignore[assignment]
    versioned_api.session = versioned_session  # type: ignore[assignment]

    legacy_api.login("admin", "admin123")
    versioned_api.login("admin", "admin123")

    assert legacy_session.calls[0]["url"] == "http://localhost:8000/api/v1/auth/login"
    assert (
        versioned_session.calls[0]["url"] == "http://localhost:8000/api/v1/auth/login"
    )


def test_request_preserves_explicit_headers_when_adding_authorization() -> None:
    api = ApiClient("http://localhost:8000/api/v1")
    fake_session = FakeSession()
    api.session = fake_session  # type: ignore[assignment]

    api.login("admin", "admin123")
    api.get("/auth/me", headers={"X-Test": "kept"})

    headers = fake_session.calls[-1]["headers"]
    assert headers["X-Test"] == "kept"
    assert headers["Authorization"] == "Bearer unit-token"


def test_login_failure_raises_sanitized_auth_error() -> None:
    api = ApiClient("http://localhost:8000/api/v1")
    api.session = FailingLoginSession()  # type: ignore[assignment]

    with pytest.raises(ApiClientAuthError) as exc_info:
        api.login("admin", "wrong-password")

    message = str(exc_info.value)
    assert "401" in message
    assert "AUTH_INVALID" in message
    assert "wrong-password" not in message


def test_real_backend_login_and_me_smoke() -> None:
    api_url = os.getenv("FPMS_API_URL", "http://127.0.0.1:8000/api/v1")
    username = os.getenv("FPMS_USERNAME", "admin")
    password = os.getenv("FPMS_PASSWORD", "admin123")
    if "127.0.0.1" not in api_url and os.getenv("FPMS_AUTH_SMOKE") != "1":
        pytest.skip(
            "Set FPMS_API_URL with 127.0.0.1 or FPMS_AUTH_SMOKE=1 to run real auth smoke"
        )

    api = ApiClient(api_url, timeout=5)

    try:
        api.login(username, password)
        response = api.get("/auth/me")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for auth smoke: {exc}")
    except ApiClientAuthError as exc:
        pytest.fail(f"Real backend auth contract failed: {exc}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["username"] == username
