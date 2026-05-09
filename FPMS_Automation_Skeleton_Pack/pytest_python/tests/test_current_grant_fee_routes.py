from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _assert_error_code(response: Any, expected_status: int, expected_code: str) -> None:
    if response.status_code != expected_status:
        raise AssertionError(
            f"Expected status {expected_status}, got {response.status_code}: "
            f"{getattr(response, 'text', '')}"
        )
    payload = response.json()
    code = payload.get("error", {}).get("code")
    if code != expected_code:
        raise AssertionError(f"Expected error code {expected_code}: {payload}")


def _assert_contract(payload: dict[str, Any]) -> None:
    if payload.get("module") != "grant_fees":
        raise AssertionError(f"Grant-fee contract module mismatch: {payload}")
    if payload.get("status") != "ok":
        raise AssertionError(f"Grant-fee contract status mismatch: {payload}")
    permission_codes = payload.get("permission_codes")
    if (
        not isinstance(permission_codes, list)
        or "GrantFeeTask.Read" not in permission_codes
    ):
        raise AssertionError(f"Grant-fee contract permission mismatch: {payload}")


def test_grant_fee_routes_return_contract_list_and_not_found_envelopes(
    runtime: Any,
) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        missing_task_id = unique_code("MISSING-GRANT-FEE", runtime.run_id, "001")

        read_contract = wave_x._json_or_assert(
            runtime.api.get("/grant-fee-tasks"),
            "get grant-fee route smoke contract",
        )
        _assert_contract(read_contract)

        write_contract = wave_x._json_or_assert(
            runtime.api.post("/grant-fee-tasks"),
            "post grant-fee route smoke contract",
        )
        _assert_contract(write_contract)

        task_list = wave_x._json_or_assert(
            runtime.api.get(
                "/grant-fee-tasks/list",
                params={"page": 1, "page_size": 20},
            ),
            "list grant-fee route smoke tasks",
        )
        wave_x._items_or_assert(task_list, "grant-fee task list")

        _assert_error_code(
            runtime.api.get(f"/grant-fee-tasks/{missing_task_id}/state"),
            404,
            "GRANT_FEE_TASK_NOT_FOUND",
        )
        _assert_error_code(
            runtime.api.put(
                f"/grant-fee-tasks/{missing_task_id}/state",
                json={"action": "mark_waiting_client"},
            ),
            404,
            "GRANT_FEE_TASK_NOT_FOUND",
        )
        _assert_error_code(
            runtime.api.post(
                "/grant-fee-tasks/batch-instruction",
                json={
                    "task_ids": [missing_task_id],
                    "action": "record_pay_instruction",
                },
            ),
            404,
            "GRANT_FEE_TASK_NOT_FOUND",
        )
        _assert_error_code(
            runtime.api.post(
                "/grant-fee-tasks/generate-notices",
                json={"task_ids": [missing_task_id]},
            ),
            404,
            "GRANT_FEE_TASK_NOT_FOUND",
        )
        _assert_error_code(
            runtime.api.post(f"/grant-fee-tasks/{missing_task_id}/generate-draft"),
            404,
            "GRANT_FEE_TASK_NOT_FOUND",
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for grant-fee route smoke: {exc}")
