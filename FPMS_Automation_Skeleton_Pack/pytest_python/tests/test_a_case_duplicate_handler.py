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
    def __init__(
        self, duplicate_status: int = 400, baseline_exists: bool = False
    ) -> None:
        self.calls: list[dict[str, Any]] = []
        self.duplicate_status = duplicate_status
        self.client: dict[str, Any] | None = None
        self.applicant: dict[str, Any] | None = None
        self.case: dict[str, Any] | None = None
        if baseline_exists:
            self.case = {
                "id": "case-001",
                "case_no": "CASE-A-RUN-A-DUP-001",
                "status": "NOT_FILED",
                "case_type": "NORMAL",
                "patent_category": "INV",
                "flow_dir": "CN_DOMESTIC",
                "from_country": "CN",
                "client_id": "client-existing",
                "title_cn": "Existing RUN-A-DUP",
            }

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            return FakeResponse(200, _list_response(self.client))
        if path == "/applicants":
            return FakeResponse(200, _list_response(self.applicant))
        if path == "/cases":
            return FakeResponse(200, _list_response(self.case))
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            self.client = {"id": "client-001", **payload}
            return FakeResponse(201, self.client)
        if path == "/applicants":
            self.applicant = {"id": "applicant-001", **payload}
            return FakeResponse(201, self.applicant)
        if path == "/cases":
            if self.case is None:
                self.case = {
                    "id": "case-001",
                    "status": "NOT_FILED",
                    **payload,
                }
                return FakeResponse(201, self.case)
            return FakeResponse(
                self.duplicate_status,
                {
                    "error": {
                        "code": "CASE_NO_DUPLICATE",
                        "message": f"Case number {payload['case_no']} already exists",
                    }
                },
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


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-003",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Unhappy"],
        topic="A1 案卷号唯一",
        stage_code="A1",
        stage_name="案卷号唯一",
        coverage_ids=["FR-CM-01", "FR-CM-02", "V-A-01"],
        requirement_ids=["FR-CM-01", "FR-CM-02"],
        validation_ids=["V-A-01"],
        preconditions="系统中已存在 CASE-A-${RUN_ID}-001。",
        steps_summary="再次创建新案并使用同一 CaseNo 保存。",
        expected="保存被拒绝；提示 CaseNo 已存在；数据库不新增重复 T_Case 记录。",
        automation_recommendation="API+UI；唯一索引/服务校验双断言。",
        data_refs=[],
        dynamic_refs=["CASE-A-${RUN_ID}-001"],
    )


def test_tc_a_003_creates_baseline_then_rejects_duplicate_case_number() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DUP",
        api=FakeApi(duplicate_status=400),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_003(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }
    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == ["/clients", "/applicants", "/cases", "/cases"]

    first_case_payload, duplicate_payload = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ]
    assert first_case_payload["case_no"] == "CASE-A-RUN-A-DUP-001"
    assert duplicate_payload["case_no"] == "CASE-A-RUN-A-DUP-001"
    assert duplicate_payload["title_cn"].endswith("RUN-A-DUP")
    assert duplicate_payload["case_type"] == "NORMAL"
    assert duplicate_payload["patent_category"] == "INV"
    assert duplicate_payload["flow_dir"] == "CN_DOMESTIC"
    assert duplicate_payload["from_country"] == "CN"

    case_gets = [
        call
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/cases"
    ]
    assert len(case_gets) == 2
    assert all(
        call["kwargs"]["params"]["case_no"] == "CASE-A-RUN-A-DUP-001"
        for call in case_gets
    )


def test_tc_a_003_reuses_existing_baseline_and_accepts_409_duplicate() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DUP",
        api=FakeApi(duplicate_status=409, baseline_exists=True),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_003(runtime, _case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == ["/cases"]
    duplicate_payload = _last_post_payload(runtime.api.calls, "/cases")
    assert duplicate_payload["case_no"] == "CASE-A-RUN-A-DUP-001"


def test_tc_a_003_runs_db_count_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DUP",
        api=FakeApi(duplicate_status=400, baseline_exists=True),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_003(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.counts == [("t_case", {"case_no": "CASE-A-RUN-A-DUP-001"}, 1)]


def test_a_handlers_keep_expected_state_through_tc_a_005() -> None:
    assert not getattr(handle_tc_a_001, "_is_skeleton", False)
    assert not getattr(handle_tc_a_002, "_is_skeleton", False)
    assert not getattr(handle_tc_a_003, "_is_skeleton", False)
    assert not getattr(handle_tc_a_004, "_is_skeleton", False)
    assert not getattr(handle_tc_a_005, "_is_skeleton", False)
    assert not getattr(handle_tc_a_006, "_is_skeleton", False)


def _last_post_payload(calls: list[dict[str, Any]], path: str) -> dict[str, Any]:
    for call in reversed(calls):
        if call["method"] == "POST" and call["path"] == path:
            return call["kwargs"]["json"]
    raise AssertionError(f"Missing POST call for {path}")
