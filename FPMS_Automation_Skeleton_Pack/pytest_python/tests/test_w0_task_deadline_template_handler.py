from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_009, handle_tc_w0_cfg_008


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
        self.task_templates: list[dict[str, Any]] = []
        self.doc_templates: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/task-templates":
            item = {"id": f"task-{len(self.task_templates) + 1}", **payload}
            self.task_templates.append(item)
            return FakeResponse(201, item)
        if path == "/doc-templates":
            item = {"id": f"doc-{len(self.doc_templates) + 1}", **payload}
            self.doc_templates.append(item)
            return FakeResponse(201, item)
        return FakeResponse(404, {"message": "not found"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/task-templates":
            return FakeResponse(200, self.task_templates)
        if path == "/doc-templates":
            q = (kwargs.get("params") or {}).get("q")
            items = [item for item in self.doc_templates if item["code"] == q]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
            )
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
        id="TC-W0-CFG-008",
        wave="W0",
        wave_title="W0 基础配置",
        context="时限模板和自动任务",
        priority="P0",
        categories=["Happy", "Boundary"],
        topic="时限模板-起算基准、内部期限、提醒",
        stage_code=None,
        stage_name="业务参数-时限模板",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM", "DS-CFG-TASK-OA-REPLY", "DS-CFG-DOC-OA-IN"],
    )


def test_tc_w0_cfg_008_handler_creates_linked_deadline_templates() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DL",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_008(runtime, _case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/task-templates",
        "/doc-templates",
    ]
    task_payload = post_calls[0]["kwargs"]["json"]
    assert task_payload["code"] == "OA_REPLY_RUN-W0-DL"
    assert task_payload["deadline_base"] == "DISPATCH_DATE"
    assert task_payload["add_days"] == 120
    assert task_payload["inner_offset_days"] == 14
    assert task_payload["daily_remind"] is True

    doc_payload = post_calls[1]["kwargs"]["json"]
    assert doc_payload["code"] == "OA_IN_RUN-W0-DL"
    assert doc_payload["deadline_template_code"] == "OA_REPLY_RUN-W0-DL"
    assert doc_payload["need_reply"] is True
    assert doc_payload["status_effect"] == "OA1"

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == ["/task-templates", "/doc-templates"]
    assert runtime.db.rows == []


def test_tc_w0_cfg_008_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DL-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_008(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_task_template",
            {"code": "OA_REPLY_RUN-W0-DL-DB", "deadline_base": "DISPATCH_DATE"},
        ),
        (
            "t_doc_template",
            {
                "code": "OA_IN_RUN-W0-DL-DB",
                "deadline_template_code": "OA_REPLY_RUN-W0-DL-DB",
                "enabled": True,
            },
        ),
    ]


def test_tc_w0_009_and_cfg_008_are_registered_as_real_handlers() -> None:
    assert HANDLERS["TC-W0-009"] is handle_tc_w0_009
    assert HANDLERS["TC-W0-CFG-008"] is handle_tc_w0_cfg_008
    assert not getattr(handle_tc_w0_009, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_cfg_008, "_is_skeleton", False)
