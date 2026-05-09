from __future__ import annotations

from typing import Any

import pytest
import requests

from framework.helpers import unique_code
from handlers import wave_x


def _ensure_doc_template(runtime: Any) -> dict[str, Any]:
    code = unique_code("ATTACH-PREVIEW", runtime.run_id, "001")
    existing = wave_x._find_item(
        wave_x._json_or_assert(
            runtime.api.get(
                "/doc-templates",
                params={"q": code, "page": 1, "page_size": 20},
            ),
            "search attachment preview doc template",
        ),
        "code",
        code,
    )
    if existing is not None:
        return existing
    return wave_x._json_or_assert(
        runtime.api.post(
            "/doc-templates",
            json={
                "code": code,
                "name": "附件预览烟测模板",
                "direction": "OUT",
                "enabled": True,
            },
        ),
        "create attachment preview doc template",
        expected_statuses={201},
    )


def test_document_wizard_attachment_preview_route_returns_candidate(
    runtime: Any,
) -> None:
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = wave_x._ensure_x_client(runtime, "ATT")
        applicant = wave_x._ensure_x_applicant(runtime, "ATT")
        case_data = wave_x._ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="ATT",
            title_label="附件预览路由烟测案卷",
        )
        template = _ensure_doc_template(runtime)

        payload = wave_x._json_or_assert(
            runtime.api.post(
                "/documents/wizard/attachment-preview",
                json={
                    "defaults": {
                        "doc_template_id": template["id"],
                        "direction": "OUT",
                        "doc_date": "2026-05-09",
                    },
                    "rows": [
                        {
                            "case_id": case_data["id"],
                            "title": "附件预览烟测文档",
                        }
                    ],
                },
            ),
            "preview document wizard attachments",
        )
        items = payload.get("items")
        if not isinstance(items, list) or len(items) != 1:
            raise AssertionError(f"Attachment preview expected one item: {payload}")
        item = items[0]
        if (
            item.get("case_id") != case_data["id"]
            or item.get("template_code") != template["code"]
        ):
            raise AssertionError(f"Unexpected attachment preview item: {payload}")
    except requests.RequestException as exc:
        pytest.skip(
            f"Real backend unavailable for document attachment preview route smoke: {exc}"
        )
