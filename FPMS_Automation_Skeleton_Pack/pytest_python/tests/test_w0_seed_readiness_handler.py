from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_014


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
    def __init__(self, payload: dict[str, Any]) -> None:
        self.calls: list[dict[str, Any]] = []
        self.payload = payload

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/system/config-readiness":
            return FakeResponse(404, {"message": "not found"})
        return FakeResponse(200, self.payload)


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
        id="TC-W0-CFG-014",
        wave="W0",
        wave_title="W0 基础配置",
        context="清理后种子库 readiness audit",
        priority="P0",
        categories=["Audit", "Unhappy"],
        topic="种子数据-配置缺口阻断业务 smoke",
        stage_code=None,
        stage_name="种子数据",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-CFG-SEED-EXPECTED-COUNTS"],
    )


def _readiness_payload() -> dict[str, Any]:
    count_keys = [
        "system_param",
        "fee_rate",
        "commission_rule",
        "template",
        "letter_head",
        "country",
        "department",
        "doc_template",
        "task_template",
    ]
    missing_keys = [
        ("fee_rate.apply", "t_fee_rate"),
        ("commission_rule.enabled", "t_commission_rule"),
        ("template.enabled", "t_template"),
        ("letter_head.default", "t_letter_head"),
        ("country.active", "t_country"),
        ("department.active", "t_department"),
        ("doc_template.enabled", "t_doc_template"),
        ("task_template.enabled", "t_task_template"),
    ]
    return {
        "status": "BLOCKED",
        "hard_blocked": True,
        "checked_at": "2026-05-09T00:00:00",
        "counts": [
            {"key": key, "label": f"{key} label", "count": 0} for key in count_keys
        ],
        "missing": [
            {
                "key": key,
                "label": f"{key} label",
                "table": table,
                "severity": "hard_block",
                "message": f"{key} missing",
            }
            for key, table in missing_keys
        ],
    }


def _stateful_readiness_payload() -> dict[str, Any]:
    payload = _readiness_payload()
    for item in payload["counts"]:
        if item["key"] != "system_param":
            item["count"] = 1
    payload["missing"] = [
        {
            "key": "system_param.bill_template_path",
            "label": "账单打印模板路径",
            "table": "t_system_param",
            "severity": "hard_block",
            "message": "缺少 bill_template_path",
        }
    ]
    return payload


def test_tc_w0_cfg_014_handler_reads_config_readiness() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-SEED",
        api=FakeApi(_readiness_payload()),
        db=FakeDb(),
    )

    handle_tc_w0_cfg_014(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls == [
        {"method": "LOGIN", "username": "admin", "password": "dummy-password"},
        {"method": "GET", "path": "/system/config-readiness", "kwargs": {}},
    ]


def test_tc_w0_cfg_014_handler_fails_when_hard_blocker_missing() -> None:
    payload = _readiness_payload()
    payload["missing"] = [
        item for item in payload["missing"] if item["key"] != "template.enabled"
    ]
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-SEED",
        api=FakeApi(payload),
        db=FakeDb(),
    )

    with pytest.raises(AssertionError, match="template.enabled"):
        handle_tc_w0_cfg_014(runtime, _case())  # type: ignore[arg-type]


def test_tc_w0_cfg_014_handler_accepts_full_wave_readiness_state() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-STATEFUL",
        api=FakeApi(_stateful_readiness_payload()),
        db=FakeDb(),
    )

    handle_tc_w0_cfg_014(runtime, _case())  # type: ignore[arg-type]


def test_tc_w0_cfg_014_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-014"] is handle_tc_w0_cfg_014
    assert not getattr(handle_tc_w0_cfg_014, "_is_skeleton", False)
