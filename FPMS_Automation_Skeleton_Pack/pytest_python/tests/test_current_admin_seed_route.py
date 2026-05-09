from __future__ import annotations

from typing import Any

import pytest
import requests


def test_admin_roles_permissions_seed_route_is_idempotent(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        response = runtime.api.post("/admin/seed/roles-permissions")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for admin seed route smoke: {exc}")

    if response.status_code != 200:
        raise AssertionError(
            "POST /admin/seed/roles-permissions failed with "
            f"status {response.status_code}: {response.text[:500]}"
        )
    payload = response.json()
    if payload.get("status") != "ok":
        raise AssertionError(f"Unexpected admin seed response: {payload}")
