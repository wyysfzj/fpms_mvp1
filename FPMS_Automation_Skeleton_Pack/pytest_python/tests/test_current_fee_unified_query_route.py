from __future__ import annotations

from typing import Any

import pytest
import requests

from handlers import wave_x


def _items_or_assert(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Response missing items: {payload}")
    if not all(isinstance(item, dict) for item in items):
        raise AssertionError(f"Response contains non-object item: {payload}")
    return items


def test_fee_unified_query_returns_receipt_side_row(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "FUQ")
        applicant = wave_x._ensure_x_applicant(runtime, "FUQ")
        case_data = wave_x._ensure_x_fee_overview_case(runtime, client, applicant)
        receipt = wave_x._ensure_x_case_receipt(runtime, case_data["id"])

        payload = wave_x._json_or_assert(
            runtime.api.get(
                "/fee-unified-query",
                params={
                    "record_type": "RECEIPT",
                    "case_id": case_data["id"],
                    "page": 1,
                    "page_size": 20,
                },
            ),
            "query fee unified receipt rows",
        )
        items = _items_or_assert(payload)
        if not any(
            item.get("record_type") == "RECEIPT"
            and item.get("record_id") == receipt["id"]
            for item in items
        ):
            raise AssertionError(
                f"Unified fee query did not return receipt {receipt['id']}: {payload}"
            )
    except requests.RequestException as exc:
        pytest.skip(
            f"Real backend unavailable for fee unified query route smoke: {exc}"
        )
