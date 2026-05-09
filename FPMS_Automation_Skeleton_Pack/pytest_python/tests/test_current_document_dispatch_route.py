from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _ensure_outbound_document(runtime: Any, case_id: str) -> dict[str, Any]:
    title = unique_code("DSP-OUT-DOC", runtime.run_id, "001")
    existing = wave_x._find_item(
        wave_x._json_or_assert(
            runtime.api.get(
                "/documents",
                params={
                    "case_id": case_id,
                    "direction": "OUT",
                    "q": title,
                    "page": 1,
                    "page_size": 20,
                },
            ),
            "search dispatch outbound document",
        ),
        "title",
        title,
    )
    if existing is not None:
        return existing
    return wave_x._json_or_assert(
        runtime.api.post(
            "/documents",
            json={
                "case_id": case_id,
                "doc_template_id": None,
                "doc_type": "CLIENT_OUT",
                "direction": "OUT",
                "doc_date": "2026-05-09",
                "title": title,
                "extra_data": "document dispatch route smoke",
            },
        ),
        "create dispatch outbound document",
        expected_statuses={201},
    )


def test_document_dispatch_create_and_detail_routes_return_line(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "DSP")
        applicant = wave_x._ensure_x_applicant(runtime, "DSP")
        case_data = wave_x._ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="DSP",
            title_label="文档派送路由烟测案卷",
        )
        document = _ensure_outbound_document(runtime, case_data["id"])

        dispatch = wave_x._json_or_assert(
            runtime.api.post(
                "/documents/dispatches",
                json={
                    "client_id": client["id"],
                    "dispatch_date": "2026-05-09",
                    "selected_document_ids": [document["id"]],
                    "remark": "document dispatch route smoke",
                },
            ),
            "create document dispatch",
            expected_statuses={201},
        )
        detail = wave_x._json_or_assert(
            runtime.api.get(f"/documents/dispatches/{dispatch['id']}"),
            "get document dispatch",
        )
        lines = detail.get("lines")
        if not isinstance(lines, list):
            raise AssertionError(f"Dispatch detail missing lines: {detail}")
        if not any(
            isinstance(line, dict) and line.get("document_id") == document["id"]
            for line in lines
        ):
            raise AssertionError(
                f"Dispatch detail did not include document {document['id']}: {detail}"
            )
    except requests.RequestException as exc:
        pytest.skip(
            f"Real backend unavailable for document dispatch route smoke: {exc}"
        )
