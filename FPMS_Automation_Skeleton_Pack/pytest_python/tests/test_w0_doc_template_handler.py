from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import (
    handle_tc_w0_001,
    handle_tc_w0_007,
    handle_tc_w0_010,
    handle_tc_w0_011,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self) -> Any:
        return self._payload


class FakeApi:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.templates: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/doc-templates":
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        template = {"id": f"doc-tpl-{len(self.templates) + 1}", **payload}
        self.templates.append(template)
        return FakeResponse(201, template)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/doc-templates":
            code = (kwargs.get("params") or {}).get("q")
            items = [
                template for template in self.templates if template["code"] == code
            ]
            return FakeResponse(
                200,
                {"items": items, "page": 1, "page_size": 20, "total": len(items)},
            )
        prefix = "/doc-templates/"
        if path.startswith(prefix):
            template_id = path.removeprefix(prefix)
            for template in self.templates:
                if template["id"] == template_id:
                    return FakeResponse(200, template)
        return FakeResponse(404, {"message": "not found"})


class FakeDb:
    def __init__(self, enabled: bool = False) -> None:
        self.rows: list[tuple[str, dict[str, Any]]] = []
        self._enabled = enabled

    def enabled(self) -> bool:
        return self._enabled

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        self.rows.append((table, where))
        return {"id": "row-id", **where}


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-010",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy"],
        topic="业务参数-文档模板配置",
        stage_code=None,
        stage_name="业务参数-文档模板配置",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM"],
    )


def test_tc_w0_010_handler_creates_doc_templates_via_api() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-TPL",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_010(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }
    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/doc-templates",
        "/doc-templates",
        "/doc-templates",
        "/doc-templates",
    ]

    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["code"] for payload in payloads] == [
        "OA_NOTICE-RUN-W0-TPL",
        "OA_REPLY-RUN-W0-TPL",
        "GRANT_NOTICE-RUN-W0-TPL",
        "ANNUITY_NOTICE-RUN-W0-TPL",
    ]
    assert all("RUN-W0-TPL" in payload["name"] for payload in payloads)
    assert [payload["direction"] for payload in payloads] == ["IN", "OUT", "IN", "OUT"]
    assert all(payload["enabled"] is True for payload in payloads)

    oa_notice, oa_reply, grant_notice, annuity_notice = payloads
    assert oa_notice["status_effect"] == "OA1"
    assert oa_notice["deadline_template_code"] == "OA_REPLY_LIMIT"
    assert oa_notice["need_reply"] is True

    assert oa_reply["status_restore"] == "SUB_EXAM"
    assert oa_reply["reply_to_template_code"] == "OA_NOTICE-RUN-W0-TPL"
    assert oa_reply["need_reply"] is False

    assert grant_notice["status_effect"] == "GRANTED"
    assert grant_notice["fee_draft_type"] == "GRANT_FEE"
    assert isinstance(grant_notice["input_fields"], str)
    assert json.loads(grant_notice["input_fields"]) == [
        "IssueDate",
        "GrantDate",
        "GrantNo",
        "FirstAnnuityYear",
        "ValidUntil",
    ]

    assert annuity_notice["fee_draft_type"] == "ANNUITY_FEE"
    assert isinstance(annuity_notice["input_fields"], str)
    assert json.loads(annuity_notice["input_fields"]) == [
        "AnnuityYear",
        "DueDate",
        "Amount",
        "Currency",
    ]

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == [
        "/doc-templates",
        "/doc-templates/doc-tpl-1",
        "/doc-templates",
        "/doc-templates/doc-tpl-2",
        "/doc-templates",
        "/doc-templates/doc-tpl-3",
        "/doc-templates",
        "/doc-templates/doc-tpl-4",
    ]
    assert [call["kwargs"]["params"]["q"] for call in get_calls[::2]] == [
        "OA_NOTICE-RUN-W0-TPL",
        "OA_REPLY-RUN-W0-TPL",
        "GRANT_NOTICE-RUN-W0-TPL",
        "ANNUITY_NOTICE-RUN-W0-TPL",
    ]
    assert runtime.db.rows == []


def test_tc_w0_010_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_010(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_doc_template",
            {
                "code": "OA_NOTICE-RUN-W0-DB",
                "direction": "IN",
                "enabled": True,
            },
        ),
        (
            "t_doc_template",
            {
                "code": "OA_REPLY-RUN-W0-DB",
                "direction": "OUT",
                "enabled": True,
            },
        ),
        (
            "t_doc_template",
            {
                "code": "GRANT_NOTICE-RUN-W0-DB",
                "direction": "IN",
                "enabled": True,
            },
        ),
        (
            "t_doc_template",
            {
                "code": "ANNUITY_NOTICE-RUN-W0-DB",
                "direction": "OUT",
                "enabled": True,
            },
        ),
    ]


def test_only_tc_w0_010_is_newly_unskeletoned() -> None:
    assert not getattr(handle_tc_w0_001, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_007, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_010, "_is_skeleton", False)
    assert getattr(handle_tc_w0_011, "_is_skeleton", False) is True
