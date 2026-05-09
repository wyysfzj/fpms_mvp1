from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import handle_tc_w0_002, handle_tc_w0_003


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
        self.applicants: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/applicants":
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        applicant = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
        self.applicants.append(applicant)
        return FakeResponse(201, applicant)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/applicants":
            return FakeResponse(404, {"message": "not found"})
        q = (kwargs.get("params") or {}).get("q")
        items = [item for item in self.applicants if item.get("code") == q]
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
        id="TC-W0-003",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="主数据-申请人",
        stage_code=None,
        stage_name="主数据-申请人",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-AP-001", "DS-AP-002", "DS-U-ADM"],
    )


def test_tc_w0_003_handler_creates_entity_and_individual_applicants_via_api() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-AP",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_003(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }
    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == ["/applicants", "/applicants"]

    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["code"] for payload in payloads] == [
        "AP-W0-003-ENTITY-RUN-W0-AP",
        "AP-W0-003-IND-RUN-W0-AP",
    ]
    assert [payload["name_cn"] for payload in payloads] == [
        "北京创新科技有限公司-RUN-W0-AP",
        "张三-RUN-W0-AP",
    ]
    assert [payload["applicant_type"] for payload in payloads] == [
        "ENTITY",
        "INDIVIDUAL",
    ]
    assert all(payload["is_active"] is True for payload in payloads)

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == ["/applicants", "/applicants"]
    assert [call["kwargs"]["params"]["q"] for call in get_calls] == [
        "AP-W0-003-ENTITY-RUN-W0-AP",
        "AP-W0-003-IND-RUN-W0-AP",
    ]
    assert runtime.db.rows == []


def test_tc_w0_003_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-AP-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_003(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_applicant",
            {
                "code": "AP-W0-003-ENTITY-RUN-W0-AP-DB",
                "applicant_type": "ENTITY",
                "is_active": True,
            },
        ),
        (
            "t_applicant",
            {
                "code": "AP-W0-003-IND-RUN-W0-AP-DB",
                "applicant_type": "INDIVIDUAL",
                "is_active": True,
            },
        ),
    ]


def test_tc_w0_003_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_w0_003, "_is_skeleton", False)
    assert getattr(handle_tc_w0_002, "_is_skeleton", False) is True
