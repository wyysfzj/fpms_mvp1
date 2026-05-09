from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _consulting_case_no(runtime: Any, slot: int) -> str:
    return unique_code("CONS-CASE", runtime.run_id, f"{slot:03d}")


def _find_consulting_case(runtime: Any, case_no: str) -> dict[str, Any] | None:
    payload = wave_x._json_or_assert(
        runtime.api.get(
            "/cases",
            params={"case_no": case_no, "page": 1, "page_size": 20},
        ),
        "search consulting route smoke case",
    )
    return wave_x._find_item(payload, "case_no", case_no)


def _has_fee_draft(runtime: Any, case_id: str) -> bool:
    payload = wave_x._json_or_assert(
        runtime.api.get(
            "/fees/drafts",
            params={"case_id": case_id, "page": 1, "page_size": 20},
        ),
        "search consulting route smoke fee drafts",
    )
    items = wave_x._items_or_assert(payload, "consulting route smoke fee drafts")
    return any(item.get("case_id") == case_id for item in items)


def _ensure_consulting_case_without_draft(
    runtime: Any,
    client: dict[str, Any],
) -> dict[str, Any]:
    for slot in range(1, 51):
        case_no = _consulting_case_no(runtime, slot)
        existing = _find_consulting_case(runtime, case_no)
        if existing is not None:
            if not _has_fee_draft(runtime, existing["id"]):
                return existing
            continue

        return wave_x._json_or_assert(
            runtime.api.post(
                "/consulting/cases",
                json={
                    "case_no": case_no,
                    "case_type": "CONSULTING",
                    "client_id": client["id"],
                    "title_cn": f"咨询路由烟测案卷 {runtime.run_id}-{slot:03d}",
                    "recv_date": "2026-05-09",
                },
            ),
            "create consulting route smoke case",
            expected_statuses={201},
        )
    raise AssertionError("No consulting route smoke case slot without a fee draft")


def _decimal_value(payload: dict[str, Any], field: str) -> Decimal:
    value = payload.get(field)
    if value is None:
        raise AssertionError(f"Missing decimal field {field}: {payload}")
    return Decimal(str(value))


def test_consulting_case_and_fee_draft_routes_create_fixed_fee_draft(
    runtime: Any,
) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "CONS")
        case_data = _ensure_consulting_case_without_draft(runtime, client)

        draft = wave_x._json_or_assert(
            runtime.api.post(
                "/consulting/fee-drafts",
                json={
                    "case_id": case_data["id"],
                    "mode": "FIXED",
                    "currency": "CNY",
                    "fixed_fee": "1200.00",
                },
            ),
            "create consulting route smoke fee draft",
            expected_statuses={201},
        )

        totals = draft.get("totals")
        if not isinstance(totals, dict):
            raise AssertionError(f"Consulting draft missing totals: {draft}")
        if draft.get("mode") != "FIXED":
            raise AssertionError(f"Consulting draft mode mismatch: {draft}")
        if draft.get("currency") != "CNY":
            raise AssertionError(f"Consulting draft currency mismatch: {draft}")
        if draft.get("created_line_count") != 1:
            raise AssertionError(f"Consulting draft line count mismatch: {draft}")
        if _decimal_value(totals, "amount") != Decimal("1200.00"):
            raise AssertionError(f"Consulting draft amount mismatch: {draft}")

        items = draft.get("items")
        if not isinstance(items, list) or len(items) != 1:
            raise AssertionError(f"Consulting draft items mismatch: {draft}")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for consulting route smoke: {exc}")
