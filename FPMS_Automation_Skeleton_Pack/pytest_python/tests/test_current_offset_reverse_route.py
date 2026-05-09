from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import requests

from handlers import wave_x


def _decimal_value(payload: dict[str, Any], field: str) -> Decimal:
    value = payload.get(field)
    if value is None:
        raise AssertionError(f"Missing decimal field {field}: {payload}")
    return Decimal(str(value))


def _create_manual_bill(runtime: Any, client_id: str) -> dict[str, Any]:
    return wave_x._json_or_assert(
        runtime.api.post(
            "/bills/manual",
            json={
                "client_id": client_id,
                "currency": "CNY",
                "direction": "AR",
                "status": "UNSETTLED",
                "bill_date": "2026-05-09",
                "due_date": "2026-06-08",
                "items": [
                    {
                        "description": "冲销反向路由烟测服务费",
                        "quantity": 1,
                        "unit_price": "500.00",
                        "fee_type": "SERVICE",
                    }
                ],
            },
        ),
        "create offset reverse route smoke bill",
        expected_statuses={201},
    )


def _create_payment_line(runtime: Any, client_id: str) -> dict[str, Any]:
    payment = wave_x._json_or_assert(
        runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "500.00",
                "currency": "CNY",
                "pay_date": "2026-05-09",
                "remark": "offset reverse route smoke",
            },
        ),
        "create offset reverse route smoke payment",
        expected_statuses={200, 201},
    )
    detail = wave_x._json_or_assert(
        runtime.api.get(f"/payments/{payment['id']}"),
        "get offset reverse route smoke payment",
    )
    lines = detail.get("payment_lines")
    if not isinstance(lines, list) or not lines:
        raise AssertionError(f"Payment line missing: {detail}")
    return lines[0]


def _create_offset(runtime: Any, payment_line_id: str, bill_id: str) -> dict[str, Any]:
    return wave_x._json_or_assert(
        runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": payment_line_id,
                "bill_id": bill_id,
                "offset_amt": "500.00",
                "offset_date": "2026-05-09",
            },
        ),
        "create offset reverse route smoke offset",
        expected_statuses={201},
    )


def test_offset_reverse_route_marks_offset_reversed_and_restores_bill(
    runtime: Any,
) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "OFFREV")
        bill = _create_manual_bill(runtime, client["id"])
        payment_line = _create_payment_line(runtime, client["id"])
        offset = _create_offset(runtime, payment_line["id"], bill["id"])
        if offset.get("is_reversed") is not False:
            raise AssertionError(f"Offset should start unreversed: {offset}")

        reversed_offset = wave_x._json_or_assert(
            runtime.api.post(f"/offsets/{offset['id']}/reverse"),
            "reverse offset route smoke offset",
        )
        if reversed_offset.get("id") != offset["id"]:
            raise AssertionError(f"Reversed offset id mismatch: {reversed_offset}")
        if reversed_offset.get("is_reversed") is not True:
            raise AssertionError(f"Offset was not reversed: {reversed_offset}")

        reversed_list = wave_x._json_or_assert(
            runtime.api.get(
                "/offsets",
                params={
                    "bill_id": bill["id"],
                    "is_reversed": True,
                    "page": 1,
                    "page_size": 20,
                },
            ),
            "list reversed offset route smoke offsets",
        )
        items = wave_x._items_or_assert(reversed_list, "reversed offsets")
        if not any(item.get("id") == offset["id"] for item in items):
            raise AssertionError(
                f"Reversed offset {offset['id']} was not listed: {reversed_list}"
            )

        bill_detail = wave_x._json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"),
            "get offset reverse route smoke bill",
        )
        if _decimal_value(bill_detail, "balance") != Decimal("500.00"):
            raise AssertionError(f"Bill balance was not restored: {bill_detail}")
        if bill_detail.get("status") != "UNSETTLED":
            raise AssertionError(f"Bill status was not restored: {bill_detail}")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for offset reverse route smoke: {exc}")
