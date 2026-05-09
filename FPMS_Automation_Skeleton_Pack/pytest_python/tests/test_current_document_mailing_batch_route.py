from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _ensure_outbound_document(runtime: Any, case_id: str) -> dict[str, Any]:
    title = unique_code("MAIL-OUT-DOC", runtime.run_id, "001")
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
            "search mailing outbound document",
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
                "extra_data": "document mailing route smoke",
            },
        ),
        "create mailing outbound document",
        expected_statuses={201},
    )


def test_document_mailing_batch_register_route_returns_document(runtime: Any) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "MAIL")
        applicant = wave_x._ensure_x_applicant(runtime, "MAIL")
        case_data = wave_x._ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="MAIL",
            title_label="寄送登记路由烟测案卷",
        )
        document = _ensure_outbound_document(runtime, case_data["id"])
        outgoing_reg_no = unique_code("MAIL-REG", runtime.run_id, "001")

        payload = wave_x._json_or_assert(
            runtime.api.post(
                "/documents/dispatch/mailing/batch-register",
                json={
                    "selected_document_ids": [document["id"]],
                    "outgoing_reg_no": outgoing_reg_no,
                    "forward_date": "2026-05-09",
                },
            ),
            "register document mailing batch",
        )
        items = payload.get("items")
        if not isinstance(items, list):
            raise AssertionError(f"Mailing batch response missing items: {payload}")
        if not any(
            isinstance(item, dict)
            and item.get("document_id") == document["id"]
            and item.get("outgoing_reg_no") == outgoing_reg_no
            for item in items
        ):
            raise AssertionError(
                f"Mailing batch response did not include document {document['id']}: {payload}"
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for document mailing route smoke: {exc}")
