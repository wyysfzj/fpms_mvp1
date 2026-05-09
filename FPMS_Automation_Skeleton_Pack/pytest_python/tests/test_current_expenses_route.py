from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _items_or_assert(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Response missing items: {payload}")
    if not all(isinstance(item, dict) for item in items):
        raise AssertionError(f"Response contains non-object item: {payload}")
    return items


def test_expense_create_and_list_routes_return_created_row(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "EXP")
        applicant = wave_x._ensure_x_applicant(runtime, "EXP")
        case_data = wave_x._ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="EXP",
            title_label="报销路由烟测案卷",
        )
        expense_no = unique_code("EXP-SMOKE", runtime.run_id, "001")
        created = wave_x._json_or_assert(
            runtime.api.post(
                "/expenses",
                json={
                    "case_id": case_data["id"],
                    "client_id": client["id"],
                    "expense_no": expense_no,
                    "category": "TRANSPORT",
                    "expense_date": "2026-05-09",
                    "amount": "88.80",
                    "currency": "CNY",
                    "vendor_name": "Skeleton Pack",
                    "remark": "expense route smoke",
                },
            ),
            "create expense route smoke row",
            expected_statuses={201},
        )

        payload = wave_x._json_or_assert(
            runtime.api.get(
                "/expenses",
                params={
                    "case_id": case_data["id"],
                    "category": "TRANSPORT",
                    "status": "DRAFT",
                    "page": 1,
                    "page_size": 20,
                },
            ),
            "list expense route smoke rows",
        )
        items = _items_or_assert(payload)
        if not any(item.get("id") == created["id"] for item in items):
            raise AssertionError(
                f"Expense list did not return expense {created['id']}: {payload}"
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for expense route smoke: {exc}")
