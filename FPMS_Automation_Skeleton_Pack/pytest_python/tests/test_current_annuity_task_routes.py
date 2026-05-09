from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _annuity_case_no(runtime: Any, slot: int) -> str:
    return unique_code("ANN-CASE", runtime.run_id, f"{slot:03d}")


def _find_case(runtime: Any, case_no: str) -> dict[str, Any] | None:
    payload = wave_x._json_or_assert(
        runtime.api.get(
            "/cases",
            params={"case_no": case_no, "page": 1, "page_size": 20},
        ),
        "search annuity route smoke case",
    )
    return wave_x._find_item(payload, "case_no", case_no)


def _create_granted_annuity_case(
    runtime: Any,
    client: dict[str, Any],
    slot: int,
) -> dict[str, Any]:
    return wave_x._json_or_assert(
        runtime.api.post(
            "/cases",
            json={
                "case_no": _annuity_case_no(runtime, slot),
                "case_type": "NORMAL",
                "patent_category": "INV",
                "flow_dir": "CN_DOMESTIC",
                "status": "GRANTED",
                "client_id": client["id"],
                "title_cn": f"年费任务路由烟测案卷 {runtime.run_id}-{slot:03d}",
                "app_no": unique_code("ANN-APP", runtime.run_id, f"{slot:03d}"),
                "filing_date": "2020-06-15",
                "pub_no": unique_code("ANN-PUB", runtime.run_id, f"{slot:03d}"),
                "pub_date": "2021-01-15",
                "grant_no": unique_code("ANN-GRANT", runtime.run_id, f"{slot:03d}"),
                "grant_date": "2023-05-09",
                "first_annuity_year": 3,
                "valid_until": "2040-06-15",
                "from_country": "CN",
            },
        ),
        "create annuity route smoke granted case",
        expected_statuses={201},
    )


def _list_annuity_tasks(runtime: Any, case_id: str) -> dict[str, Any]:
    return wave_x._json_or_assert(
        runtime.api.get(
            "/annuity/tasks",
            params={"case_id": case_id, "page": 1, "page_size": 100},
        ),
        "list annuity route smoke tasks",
    )


def _first_draftable_task(payload: dict[str, Any]) -> dict[str, Any] | None:
    items = wave_x._items_or_assert(payload, "annuity tasks")
    for item in items:
        if (
            item.get("status") == "OPEN"
            and item.get("client_instruction") in (None, "", "NONE", "PAY")
            and item.get("draft_generated") is not True
        ):
            return item
    return None


def _ensure_annuity_task_without_draft(
    runtime: Any,
    client: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    for slot in range(1, 51):
        case_no = _annuity_case_no(runtime, slot)
        case_data = _find_case(runtime, case_no)
        if case_data is None:
            case_data = _create_granted_annuity_case(runtime, client, slot)

        wave_x._json_or_assert(
            runtime.api.post(
                "/annuity/tasks/generate",
                json={"case_id": case_data["id"]},
            ),
            "generate annuity route smoke tasks",
            expected_statuses={201},
        )
        tasks = _list_annuity_tasks(runtime, case_data["id"])
        task = _first_draftable_task(tasks)
        if task is not None:
            return case_data, task
    raise AssertionError("No annuity route smoke task slot without generated draft")


def test_annuity_task_routes_generate_update_and_generate_draft(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "ANN")
        case_data, task = _ensure_annuity_task_without_draft(runtime, client)
        task_id = task["id"]

        updated = wave_x._json_or_assert(
            runtime.api.put(
                f"/annuity/tasks/{task_id}/instruction",
                json={"instruction": "PAY", "instruction_date": "2026-05-09"},
            ),
            "update annuity route smoke instruction",
        )
        if updated.get("client_instruction") != "PAY":
            raise AssertionError(f"Annuity instruction was not updated: {updated}")

        draft_result = wave_x._json_or_assert(
            runtime.api.post(
                "/annuity/tasks/generate-drafts",
                json={"task_ids": [task_id], "currency": "CNY"},
            ),
            "generate annuity route smoke draft",
        )
        summary = draft_result.get("summary")
        if not isinstance(summary, dict) or summary.get("success") != 1:
            raise AssertionError(f"Annuity draft generation failed: {draft_result}")

        refreshed = _list_annuity_tasks(runtime, case_data["id"])
        items = wave_x._items_or_assert(refreshed, "refreshed annuity tasks")
        matched = next((item for item in items if item.get("id") == task_id), None)
        if matched is None:
            raise AssertionError(f"Generated annuity task was not listed: {refreshed}")
        if matched.get("draft_generated") is not True:
            raise AssertionError(f"Annuity task draft flag was not updated: {matched}")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for annuity task route smoke: {exc}")
