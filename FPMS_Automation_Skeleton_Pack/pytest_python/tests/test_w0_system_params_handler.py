from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import handle_tc_w0_013, handle_tc_w0_cfg_001


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
        self.params: dict[str, dict[str, Any]] = {}

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        prefix = "/system/params/"
        if not path.startswith(prefix):
            return FakeResponse(404, {"message": "not found"})

        key = path.removeprefix(prefix)
        payload = kwargs["json"]
        self.params[key] = {
            "param_key": key,
            "param_value": payload["param_value"],
            "value_type": payload.get("value_type", "string"),
            "description": payload.get("description"),
            "is_secret": bool(payload.get("is_secret")),
            "created_at": "2026-05-09T00:00:00",
            "updated_at": "2026-05-09T00:00:00",
        }
        return FakeResponse(200, {"status": "ok"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/system/params":
            return FakeResponse(404, {"message": "not found"})

        items = []
        for item in self.params.values():
            visible = dict(item)
            if visible["is_secret"]:
                visible["param_value"] = "******"
            items.append(visible)
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
        id="TC-W0-CFG-001",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy", "Security"],
        topic="系统参数 API 与 UI 元数据",
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
            "DS-U-ADM",
            "DS-CFG-SYS-DEFAULT-CURRENCY",
            "DS-CFG-SYS-BILL-TEMPLATE",
            "DS-CFG-SYS-SECRET-SAMPLE",
        ],
    )


def test_tc_w0_cfg_001_handler_upserts_and_lists_system_param_metadata() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-SYS",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }

    put_calls = [call for call in runtime.api.calls if call["method"] == "PUT"]
    assert [call["path"] for call in put_calls] == [
        "/system/params/default_currency_RUN_W0_SYS",
        "/system/params/bill_template_path_RUN_W0_SYS",
        "/system/params/external_storage_token_RUN_W0_SYS",
    ]

    payloads = [call["kwargs"]["json"] for call in put_calls]
    assert payloads[0] == {
        "param_value": "CNY",
        "value_type": "string",
        "description": "默认币种",
        "is_secret": False,
    }
    assert payloads[1]["param_value"] == "templates/bill_standard_RUN-W0-SYS.docx"
    assert payloads[1]["description"] == "账单打印模板路径"
    assert payloads[2] == {
        "param_value": "secret-RUN-W0-SYS",
        "value_type": "string",
        "description": "密文遮蔽测试参数",
        "is_secret": True,
    }

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == ["/system/params"]
    assert runtime.db.rows == []


def test_tc_w0_cfg_001_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_system_param",
            {"param_key": "default_currency_RUN_W0_DB", "is_secret": False},
        ),
        (
            "t_system_param",
            {"param_key": "bill_template_path_RUN_W0_DB", "is_secret": False},
        ),
        (
            "t_system_param",
            {"param_key": "external_storage_token_RUN_W0_DB", "is_secret": True},
        ),
    ]


def test_tc_w0_cfg_001_is_unskeletoned_only_for_system_params_slice() -> None:
    assert not getattr(handle_tc_w0_cfg_001, "_is_skeleton", False)
    assert getattr(handle_tc_w0_013, "_is_skeleton", False) is True
