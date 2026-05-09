from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_002


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
        self.clients: list[dict[str, Any]] = []
        self.bills: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/system/config-readiness":
            return FakeResponse(
                200,
                {
                    "status": "BLOCKED",
                    "hard_blocked": True,
                    "checked_at": "2026-05-09T00:00:00",
                    "counts": [],
                    "missing": [
                        {
                            "key": "system_param.bill_template_path",
                            "label": "账单打印模板路径",
                            "table": "t_system_param",
                            "severity": "hard_block",
                            "message": "缺少 bill_template_path",
                        }
                    ],
                },
            )
        if path == "/bills/bill-1/print":
            return FakeResponse(
                409,
                {
                    "error": {
                        "code": "BILL_TEMPLATE_NOT_CONFIGURED",
                        "message": "Bill template not configured",
                    }
                },
            )
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path == "/clients":
            payload = kwargs["json"]
            item = {"id": "client-1", **payload}
            self.clients.append(item)
            return FakeResponse(201, item)
        if path == "/bills/manual":
            payload = kwargs["json"]
            item = {"id": "bill-1", **payload}
            self.bills.append(item)
            return FakeResponse(201, item)
        return FakeResponse(404, {"message": "not found"})


class FakeDb:
    def enabled(self) -> bool:
        return False


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-002",
        wave="W0",
        wave_title="W0 基础配置",
        context="账单打印模板路径参数",
        priority="P0",
        categories=["Happy", "Unhappy"],
        topic="系统参数-bill_template_path 控制账单打印",
        stage_code=None,
        stage_name="系统参数",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-FI-01",
            "DS-CFG-SYS-BILL-TEMPLATE",
            "DS-CFG-TEMPLATE-BILL-CN",
        ],
    )


def test_tc_w0_cfg_002_handler_asserts_missing_bill_template_guard() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-BILLTPL",
        api=FakeApi(),
        db=FakeDb(),
    )

    handle_tc_w0_cfg_002(runtime, _case())  # type: ignore[arg-type]

    assert [call["method"] for call in runtime.api.calls] == [
        "LOGIN",
        "GET",
        "POST",
        "POST",
        "GET",
    ]
    assert [call.get("path") for call in runtime.api.calls[1:]] == [
        "/system/config-readiness",
        "/clients",
        "/bills/manual",
        "/bills/bill-1/print",
    ]
    assert runtime.api.clients[0]["client_code"] == "CL-CFG-RUN-W0-BILLTPL"
    assert runtime.api.bills[0]["client_id"] == "client-1"
    assert runtime.api.bills[0]["items"][0]["fee_type"] == "SERVICE"


def test_tc_w0_cfg_002_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-002"] is handle_tc_w0_cfg_002
    assert not getattr(handle_tc_w0_cfg_002, "_is_skeleton", False)
