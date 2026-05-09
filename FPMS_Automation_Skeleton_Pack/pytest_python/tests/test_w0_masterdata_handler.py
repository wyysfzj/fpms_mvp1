from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_012


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
        self.records: dict[str, list[dict[str, Any]]] = {
            "/countries": [],
            "/departments": [],
            "/clients": [],
            "/applicants": [],
        }

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path not in self.records:
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        item = {"id": f"{path}-{len(self.records[path]) + 1}", **payload}
        self.records[path].append(item)
        return FakeResponse(201, item)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path not in self.records:
            return FakeResponse(404, {"message": "not found"})
        q = (kwargs.get("params") or {}).get("q")
        identity_fields = ("code", "department_code", "client_code")
        items = [
            item
            for item in self.records[path]
            if any(item.get(field) == q for field in identity_fields)
        ]
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
        id="TC-W0-CFG-012",
        wave="W0",
        wave_title="W0 基础配置",
        context="主数据配置",
        priority="P1",
        categories=["Happy", "Unhappy"],
        topic="主数据-国家、部门、申请人和客户引用",
        stage_code=None,
        stage_name="主数据",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-ADM",
            "DS-CFG-COUNTRY-CN",
            "DS-CFG-DEPT-PATENT",
            "DS-CFG-CLIENT-ACTIVE",
            "DS-CFG-APPLICANT-ENTITY",
        ],
    )


def test_tc_w0_cfg_012_handler_creates_masterdata_records() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-MD",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_012(runtime, _case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/countries",
        "/departments",
        "/clients",
        "/applicants",
    ]
    assert post_calls[0]["kwargs"]["json"]["code"] == "CN"
    assert post_calls[1]["kwargs"]["json"]["department_code"] == "PATENT"
    assert post_calls[2]["kwargs"]["json"]["client_code"] == "CL-CFG-RUN-W0-MD"
    assert post_calls[3]["kwargs"]["json"]["code"] == "AP-CFG-RUN-W0-MD"

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == [
        "/countries",
        "/departments",
        "/clients",
        "/applicants",
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_012_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-MD-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_012(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_country", {"code": "CN", "is_active": True}),
        ("t_department", {"department_code": "PATENT", "is_active": True}),
        ("t_client", {"client_code": "CL-CFG-RUN-W0-MD-DB", "is_active": True}),
        ("t_applicant", {"code": "AP-CFG-RUN-W0-MD-DB", "is_active": True}),
    ]


def test_tc_w0_cfg_012_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-012"] is handle_tc_w0_cfg_012
    assert not getattr(handle_tc_w0_cfg_012, "_is_skeleton", False)
