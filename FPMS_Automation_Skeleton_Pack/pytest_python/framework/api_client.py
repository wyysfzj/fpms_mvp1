from __future__ import annotations

from typing import Any

import requests


class ApiClientAuthError(RuntimeError):
    """Authentication failed without exposing credentials or tokens."""


class ApiClient:
    """Minimal API client for the real FPMS backend contract."""

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = self._normalize_base_url(base_url)
        self.timeout = timeout
        self.session = requests.Session()
        self.access_token: str | None = None

    def _normalize_base_url(self, base_url: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/api"):
            return f"{normalized}/v1"
        return normalized

    def login(self, username: str, password: str) -> str:
        response = self.post(
            "/auth/login",
            json={"username": username, "password": password},
            auth_required=False,
        )
        if not response.ok:
            raise ApiClientAuthError(
                f"Login failed with status {response.status_code}: {self._response_summary(response)}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiClientAuthError(
                f"Login failed with invalid JSON response: status {response.status_code}"
            ) from exc

        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise ApiClientAuthError(
                f"Login response missing access_token: status {response.status_code}"
            )

        self.access_token = token
        return token

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        auth_required = kwargs.pop("auth_required", True)
        if auth_required and self.access_token:
            headers = dict(kwargs.pop("headers", {}) or {})
            headers.setdefault("Authorization", f"Bearer {self.access_token}")
            kwargs["headers"] = headers
        return self.session.request(method=method.upper(), url=url, **kwargs)

    def _response_summary(self, response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            payload = response.text
        summary = str(payload)
        if self.access_token:
            summary = summary.replace(self.access_token, "<redacted>")
        return summary[:500]

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
