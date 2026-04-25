from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import handle_tc_w0_001, handle_tc_w0_007, handle_tc_w0_008


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
        self.rates: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/fees/rates":
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        rate = {"id": f"rate-{len(self.rates) + 1}", **payload}
        self.rates.append(rate)
        return FakeResponse(201, rate)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/fees/rates":
            return FakeResponse(404, {"message": "not found"})
        fee_code = (kwargs.get("params") or {}).get("fee_code")
        items = [rate for rate in self.rates if rate["fee_code"] == fee_code]
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )


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
        id="TC-W0-007",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy"],
        topic="业务参数-费率固定金额",
        stage_code=None,
        stage_name="业务参数-费率固定金额",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-FI-01"],
    )


def test_tc_w0_007_handler_creates_two_fixed_apply_fee_rates_via_api() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-FEE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_007(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }
    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == ["/fees/rates", "/fees/rates"]

    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["fee_code"] for payload in payloads] == [
        "CN_APPL_BASE-RUN-W0-FEE",
        "CN_APPL_SERVICE_BASE-RUN-W0-FEE",
    ]
    assert [payload["fee_type"] for payload in payloads] == ["GOV", "SERVICE"]
    assert [payload["default_amount"] for payload in payloads] == ["950.00", "3000.00"]
    assert [payload["allow_reduction"] for payload in payloads] == [True, False]
    for payload in payloads:
        assert payload["currency"] == "CNY"
        assert payload["enabled"] is True
        assert payload["rate_group"] == "APPLY"
        assert payload["country_code"] == "CN"
        assert payload["case_type"] == "NORMAL"
        assert payload["patent_category"] == "INV"
        assert payload["calc_mode"] == "FIXED"

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == ["/fees/rates", "/fees/rates"]
    assert [call["kwargs"]["params"]["fee_code"] for call in get_calls] == [
        "CN_APPL_BASE-RUN-W0-FEE",
        "CN_APPL_SERVICE_BASE-RUN-W0-FEE",
    ]
    assert runtime.db.rows == []


def test_tc_w0_007_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_007(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_fee_rate",
            {
                "fee_code": "CN_APPL_BASE-RUN-W0-DB",
                "fee_type": "GOV",
                "rate_group": "APPLY",
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "CN_APPL_SERVICE_BASE-RUN-W0-DB",
                "fee_type": "SERVICE",
                "rate_group": "APPLY",
            },
        ),
    ]


def test_only_tc_w0_007_is_newly_unskeletoned() -> None:
    assert not getattr(handle_tc_w0_001, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_007, "_is_skeleton", False)
    assert getattr(handle_tc_w0_008, "_is_skeleton", False) is True
