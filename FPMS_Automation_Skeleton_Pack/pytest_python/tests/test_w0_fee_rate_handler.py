from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import (
    handle_tc_w0_001,
    handle_tc_w0_007,
    handle_tc_w0_008,
    handle_tc_w0_cfg_003,
    handle_tc_w0_cfg_004,
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


def _cfg_case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-003",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy", "Unhappy"],
        topic="费率-申请费必备三项配置与缺失阻断",
        stage_code=None,
        stage_name="业务参数-费率",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-FI-01",
            "DS-CFG-RATE-APPLY-BASE-GOV",
            "DS-CFG-RATE-APPLY-EXCESS-CLAIM",
            "DS-CFG-RATE-APPLY-SERVICE",
        ],
    )


def _cfg_calc_mode_case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-004",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P1",
        categories=["Boundary", "Unhappy"],
        topic="费率-calc_mode 覆盖与当前实现差距",
        stage_code=None,
        stage_name="业务参数-费率",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-FI-01",
            "DS-CFG-RATE-APPLY-BASE-GOV",
            "DS-CFG-RATE-APPLY-EXCESS-CLAIM",
            "DS-CFG-RATE-ANNUITY-GOV-Y1",
            "DS-CFG-RATE-BY-PAGES",
            "DS-CFG-RATE-COMPOSITE",
        ],
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


def test_tc_w0_cfg_003_handler_creates_apply_fee_required_rates() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-CFG-FEE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_003(runtime, _cfg_case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/fees/rates",
        "/fees/rates",
        "/fees/rates",
    ]

    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["fee_code"] for payload in payloads] == [
        "APPLY_BASE_GOV-RUN-W0-CFG-FEE",
        "APPLY_EXCESS_CLAIM-RUN-W0-CFG-FEE",
        "APPLY_SERVICE-RUN-W0-CFG-FEE",
    ]
    assert [payload["fee_type"] for payload in payloads] == ["GOV", "GOV", "SERVICE"]
    assert [payload["calc_mode"] for payload in payloads] == [
        "FIXED",
        "PER_CLAIM",
        "FIXED",
    ]
    assert [payload["default_amount"] for payload in payloads] == [
        "1000.00",
        "150.00",
        "500.00",
    ]
    assert [payload["allow_reduction"] for payload in payloads] == [True, True, False]
    assert all(payload["enabled"] is True for payload in payloads)
    assert all(payload["currency"] == "CNY" for payload in payloads)
    assert all(payload["rate_group"] == "APPLY" for payload in payloads)

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["kwargs"]["params"]["fee_code"] for call in get_calls] == [
        "APPLY_BASE_GOV-RUN-W0-CFG-FEE",
        "APPLY_EXCESS_CLAIM-RUN-W0-CFG-FEE",
        "APPLY_SERVICE-RUN-W0-CFG-FEE",
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_004_handler_preserves_calc_mode_metadata() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-CFG-CALC",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_004(runtime, _cfg_calc_mode_case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["fee_code"] for payload in payloads] == [
        "APPLY_BASE_GOV-RUN-W0-CFG-CALC",
        "APPLY_EXCESS_CLAIM-RUN-W0-CFG-CALC",
        "ANNUITY_GOV-RUN-W0-CFG-CALC",
        "SPEC_PAGE_SURCHARGE-RUN-W0-CFG-CALC",
        "APPLY_COMPOSITE_SAMPLE-RUN-W0-CFG-CALC",
    ]
    assert [payload["calc_mode"] for payload in payloads] == [
        "FIXED",
        "PER_CLAIM",
        "BY_YEAR",
        "BY_PAGES",
        "COMPOSITE",
    ]
    assert [payload["calc_params"] for payload in payloads] == [
        None,
        '{"base_claims":10}',
        '{"year_no":1}',
        '{"base_pages":30}',
        '{"fixed":"100","per_claim":"20","base_claims":10}',
    ]

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["kwargs"]["params"]["fee_code"] for call in get_calls] == [
        "APPLY_BASE_GOV-RUN-W0-CFG-CALC",
        "APPLY_EXCESS_CLAIM-RUN-W0-CFG-CALC",
        "ANNUITY_GOV-RUN-W0-CFG-CALC",
        "SPEC_PAGE_SURCHARGE-RUN-W0-CFG-CALC",
        "APPLY_COMPOSITE_SAMPLE-RUN-W0-CFG-CALC",
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


def test_tc_w0_cfg_003_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-CFG-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_003(runtime, _cfg_case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_BASE_GOV-RUN-W0-CFG-DB",
                "rate_group": "APPLY",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_EXCESS_CLAIM-RUN-W0-CFG-DB",
                "rate_group": "APPLY",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_SERVICE-RUN-W0-CFG-DB",
                "rate_group": "APPLY",
                "enabled": True,
            },
        ),
    ]


def test_tc_w0_cfg_004_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-CFG-CALC-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_004(runtime, _cfg_calc_mode_case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_BASE_GOV-RUN-W0-CFG-CALC-DB",
                "calc_mode": "FIXED",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_EXCESS_CLAIM-RUN-W0-CFG-CALC-DB",
                "calc_mode": "PER_CLAIM",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "ANNUITY_GOV-RUN-W0-CFG-CALC-DB",
                "calc_mode": "BY_YEAR",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "SPEC_PAGE_SURCHARGE-RUN-W0-CFG-CALC-DB",
                "calc_mode": "BY_PAGES",
                "enabled": True,
            },
        ),
        (
            "t_fee_rate",
            {
                "fee_code": "APPLY_COMPOSITE_SAMPLE-RUN-W0-CFG-CALC-DB",
                "calc_mode": "COMPOSITE",
                "enabled": True,
            },
        ),
    ]


def test_only_tc_w0_007_is_newly_unskeletoned() -> None:
    assert not getattr(handle_tc_w0_001, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_007, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_cfg_003, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_cfg_004, "_is_skeleton", False)
    assert getattr(handle_tc_w0_008, "_is_skeleton", False) is True
