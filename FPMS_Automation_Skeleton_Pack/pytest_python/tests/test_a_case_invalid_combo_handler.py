from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import (
    handle_tc_a_001,
    handle_tc_a_002,
    handle_tc_a_003,
    handle_tc_a_004,
    handle_tc_a_005,
    handle_tc_a_006,
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
        self.rejected_case_no: str | None = None

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/applicants":
            return FakeResponse(
                201,
                {
                    "id": "applicant-1",
                    "code": payload["code"],
                    "name_cn": payload["name_cn"],
                    "applicant_type": payload["applicant_type"],
                },
            )
        if path == "/cases":
            self.rejected_case_no = payload["case_no"]
            return FakeResponse(
                400,
                {
                    "error": {
                        "code": "CASE_TYPE_COMBO_INVALID",
                        "message": "case_type and patent_category are not a valid combination",
                        "details": {
                            "case_type": "SEARCH",
                            "patent_category": "DES",
                        },
                    }
                },
            )
        return FakeResponse(404, {"message": "not found"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/applicants":
            return FakeResponse(
                200,
                {"items": [], "page": 1, "page_size": 20, "total": 0},
            )
        if path == "/cases":
            return FakeResponse(
                200,
                {"items": [], "page": 1, "page_size": 20, "total": 0},
            )
        return FakeResponse(404, {"message": "not found"})


class FakeDb:
    def __init__(self, enabled: bool = False) -> None:
        self.counts: list[tuple[str, dict[str, Any] | None, int | None]] = []
        self._enabled = enabled

    def enabled(self) -> bool:
        return self._enabled

    def assert_count(
        self,
        table: str,
        where: dict[str, Any] | None = None,
        expected: int | None = None,
    ) -> int:
        self.counts.append((table, where, expected))
        return expected or 0


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-004",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P1",
        categories=["Unhappy"],
        topic="A1 案件类型组合非法",
        stage_code="A1",
        stage_name="案件类型组合非法",
        coverage_ids=["FR-CM-01", "V-A-02"],
        requirement_ids=["FR-CM-01"],
        validation_ids=["V-A-02"],
        preconditions="DS-U-FM-01；配置中存在禁止的 CaseType+PatentCategory 组合。",
        steps_summary="创建新案时选择被配置禁止的组合并保存。",
        expected="系统阻止保存并说明非法组合。",
        automation_recommendation="API negative smoke.",
        data_refs=["DS-U-FM-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-001"],
    )


def test_tc_a_004_rejects_invalid_case_type_patent_category_combo() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-COMBO",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_004(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }
    post_payload = _post_payload(runtime.api.calls, "/cases")
    assert post_payload["case_no"] == "CASE-A-INVCOMBO-RUN-A-COMBO-001"
    assert post_payload["title_cn"].endswith("RUN-A-COMBO")
    assert post_payload["case_type"] == "SEARCH"
    assert post_payload["patent_category"] == "DES"
    assert post_payload["flow_dir"] == "CN_DOMESTIC"

    case_get = _get_call(runtime.api.calls, "/cases")
    assert case_get["kwargs"]["params"]["case_no"] == post_payload["case_no"]


def test_tc_a_004_runs_db_count_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-COMBO",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_004(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.counts == [
        (
            "t_case",
            {"case_no": "CASE-A-INVCOMBO-RUN-A-COMBO-001"},
            0,
        )
    ]


def test_a_handlers_keep_expected_state_through_tc_a_005() -> None:
    assert not getattr(handle_tc_a_001, "_is_skeleton", False)
    assert not getattr(handle_tc_a_002, "_is_skeleton", False)
    assert not getattr(handle_tc_a_003, "_is_skeleton", False)
    assert not getattr(handle_tc_a_004, "_is_skeleton", False)
    assert not getattr(handle_tc_a_005, "_is_skeleton", False)
    assert not getattr(handle_tc_a_006, "_is_skeleton", False)


def _post_payload(calls: list[dict[str, Any]], path: str) -> dict[str, Any]:
    for call in calls:
        if call["method"] == "POST" and call["path"] == path:
            return call["kwargs"]["json"]
    raise AssertionError(f"Missing POST call for {path}")


def _get_call(calls: list[dict[str, Any]], path: str) -> dict[str, Any]:
    for call in calls:
        if call["method"] == "GET" and call["path"] == path:
            return call
    raise AssertionError(f"Missing GET call for {path}")
