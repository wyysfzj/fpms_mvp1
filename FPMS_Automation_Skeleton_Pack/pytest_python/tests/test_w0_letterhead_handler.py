from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_011


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
        self.letterheads: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/letterheads":
            return FakeResponse(404, {"message": "not found"})

        payload = kwargs["json"]
        if payload.get("is_default"):
            for item in self.letterheads:
                if item.get("locale") == payload.get("locale"):
                    item["is_default"] = False
        item = {
            "id": len(self.letterheads) + 1,
            "created_at": "2026-05-09T00:00:00",
            "updated_at": "2026-05-09T00:00:00",
            **payload,
        }
        self.letterheads.append(item)
        return FakeResponse(201, item)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/letterheads":
            return FakeResponse(404, {"message": "not found"})
        locale = (kwargs.get("params") or {}).get("locale")
        items = [item for item in self.letterheads if item.get("locale") == locale]
        return FakeResponse(200, items)


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
        id="TC-W0-CFG-011",
        wave="W0",
        wave_title="W0 基础配置",
        context="信头配置",
        priority="P1",
        categories=["Happy", "Boundary"],
        topic="信头-默认信头唯一性和账单打印引用",
        stage_code=None,
        stage_name="信头",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM", "DS-CFG-LETTERHEAD-CN", "DS-CFG-LETTERHEAD-EN"],
    )


def test_tc_w0_cfg_011_handler_replaces_default_letterhead_by_locale() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-LH",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_011(runtime, _case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/letterheads",
        "/letterheads",
        "/letterheads",
    ]
    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["name"] for payload in payloads] == [
        "中文默认信头-RUN-W0-LH",
        "English Default Letterhead-RUN-W0-LH",
        "中文默认信头-RUN-W0-LH-替换",
    ]
    assert [payload["locale"] for payload in payloads] == ["zh-CN", "en-US", "zh-CN"]
    assert all(payload["is_default"] is True for payload in payloads)

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert get_calls == [
        {
            "method": "GET",
            "path": "/letterheads",
            "kwargs": {"params": {"locale": "zh-CN"}},
        }
    ]
    defaults = [
        item for item in runtime.api.letterheads if item.get("locale") == "zh-CN"
    ]
    assert [(item["name"], item["is_default"]) for item in defaults] == [
        ("中文默认信头-RUN-W0-LH", False),
        ("中文默认信头-RUN-W0-LH-替换", True),
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_011_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-LH-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_011(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_letter_head", {"name": "中文默认信头-RUN-W0-LH-DB", "is_default": False}),
        (
            "t_letter_head",
            {"name": "中文默认信头-RUN-W0-LH-DB-替换", "is_default": True},
        ),
        (
            "t_letter_head",
            {"name": "English Default Letterhead-RUN-W0-LH-DB", "is_default": True},
        ),
    ]


def test_tc_w0_cfg_011_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-011"] is handle_tc_w0_cfg_011
    assert not getattr(handle_tc_w0_cfg_011, "_is_skeleton", False)
