from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _list_item(
    runtime: Any, path: str, field: str, value: str
) -> dict[str, Any] | None:
    return wave_x._find_item(
        wave_x._json_or_assert(
            runtime.api.get(path, params={"q": value, "page": 1, "page_size": 20}),
            f"search {path} {value}",
        ),
        field,
        value,
    )


def _ensure_country(runtime: Any) -> dict[str, Any]:
    code = unique_code("MD-CTY", runtime.run_id, "001")
    existing = _list_item(runtime, "/countries", "code", code)
    if existing is not None:
        return existing
    return wave_x._json_or_assert(
        runtime.api.post(
            "/countries",
            json={
                "code": code,
                "name_cn": f"主数据停用国家-{runtime.run_id}",
                "name_en": f"Deactivate Country {runtime.run_id}",
                "is_active": True,
            },
        ),
        "create country for deactivate route",
        expected_statuses={201},
    )


def _ensure_department(runtime: Any) -> dict[str, Any]:
    code = unique_code("MD-DEPT", runtime.run_id, "001")
    existing = _list_item(runtime, "/departments", "department_code", code)
    if existing is not None:
        return existing
    return wave_x._json_or_assert(
        runtime.api.post(
            "/departments",
            json={
                "department_code": code,
                "name_cn": f"主数据停用部门-{runtime.run_id}",
                "is_active": True,
            },
        ),
        "create department for deactivate route",
        expected_statuses={201},
    )


def _assert_inactive(runtime: Any, path: str, field: str, value: str) -> None:
    payload = wave_x._json_or_assert(
        runtime.api.get(
            path,
            params={"q": value, "is_active": False, "page": 1, "page_size": 20},
        ),
        f"list inactive {path}",
    )
    item = wave_x._find_item(payload, field, value)
    if item is None:
        raise AssertionError(f"{path} did not include inactive {value}: {payload}")
    if item.get("is_active") is not False:
        raise AssertionError(f"{path} item was not inactive: {item}")


def test_masterdata_deactivate_routes_mark_records_inactive(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        applicant = wave_x._ensure_x_applicant(runtime, "DEACT")
        country = _ensure_country(runtime)
        department = _ensure_department(runtime)

        for path in (
            f"/applicants/{applicant['id']}/deactivate",
            f"/countries/{country['id']}/deactivate",
            f"/departments/{department['id']}/deactivate",
        ):
            payload = wave_x._json_or_assert(
                runtime.api.put(path), f"deactivate {path}"
            )
            if payload.get("status") != "ok":
                raise AssertionError(
                    f"Unexpected deactivate response for {path}: {payload}"
                )

        _assert_inactive(runtime, "/applicants", "code", applicant["code"])
        _assert_inactive(runtime, "/countries", "code", country["code"])
        _assert_inactive(
            runtime,
            "/departments",
            "department_code",
            department["department_code"],
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for masterdata deactivate smoke: {exc}")
