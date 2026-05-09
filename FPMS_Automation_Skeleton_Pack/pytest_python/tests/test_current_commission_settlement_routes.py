from __future__ import annotations

from typing import Any

import pytest
import requests

from handlers import wave_x

_EXPORT_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _current_user_id(runtime: Any) -> str:
    payload = wave_x._json_or_assert(runtime.api.get("/auth/me"), "get current user")
    user = payload.get("user") if isinstance(payload, dict) else None
    user_id = user.get("id") if isinstance(user, dict) else None
    if not isinstance(user_id, str) or not user_id:
        raise AssertionError(f"Current user response missing id: {payload}")
    return user_id


def _create_settlement(runtime: Any, agent_id: str) -> dict[str, Any]:
    last_conflict: dict[str, Any] | None = None
    for slot in range(1, 29):
        response = runtime.api.post(
            "/commission/settlements",
            json={
                "agent_id": agent_id,
                "period_from": f"2026-05-{slot:02d}",
                "period_to": f"2026-05-{slot:02d}",
                "currency": "CNY",
                "remark": f"commission settlement route smoke {slot:02d}",
            },
        )
        if response.status_code == 201:
            return response.json()
        if response.status_code == 409:
            last_conflict = response.json()
            continue
        wave_x._json_or_assert(
            response,
            "create commission settlement route smoke batch",
            expected_statuses={201},
        )
    raise AssertionError(
        f"No commission settlement slot was available: {last_conflict}"
    )


def _assert_excel_response(response: Any) -> None:
    if getattr(response, "status_code", None) != 200:
        raise AssertionError(f"Commission export failed: {response!r}")
    content_type = str(response.headers.get("content-type", "")).lower()
    if _EXPORT_MIME_TYPE not in content_type:
        raise AssertionError(
            f"Unexpected commission export content type: {content_type}"
        )
    if not getattr(response, "content", b""):
        raise AssertionError("Commission export response body was empty")


def test_commission_settlement_report_routes_create_generate_and_export(
    runtime: Any,
) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        agent_id = _current_user_id(runtime)
        settlement = _create_settlement(runtime, agent_id)

        generated = wave_x._json_or_assert(
            runtime.api.post(
                f"/commission/settlements/{settlement['id']}/generate-lines"
            ),
            "generate commission settlement route smoke lines",
        )
        if generated.get("settlement_id") != settlement["id"]:
            raise AssertionError(f"Settlement generation id mismatch: {generated}")
        if "line_count" not in generated or "status" not in generated:
            raise AssertionError(f"Settlement generation shape mismatch: {generated}")

        report = wave_x._json_or_assert(
            runtime.api.get(
                "/commission/reports/settlement",
                params={
                    "agent_id": agent_id,
                    "currency": "CNY",
                    "date_from": "2026-05-01",
                    "date_to": "2026-05-31",
                    "time_field": "settlement_period",
                },
            ),
            "get commission settlement route smoke report",
        )
        summary = report.get("summary")
        if not isinstance(summary, dict) or "line_count" not in summary:
            raise AssertionError(
                f"Commission settlement report shape mismatch: {report}"
            )

        export_response = runtime.api.get(
            "/commission/reports/settlement/export",
            params={
                "agent_id": agent_id,
                "currency": "CNY",
                "date_from": "2026-05-01",
                "date_to": "2026-05-31",
                "time_field": "settlement_period",
            },
        )
        _assert_excel_response(export_response)
    except requests.RequestException as exc:
        pytest.skip(
            f"Real backend unavailable for commission settlement route smoke: {exc}"
        )
