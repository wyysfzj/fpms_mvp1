from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_014, handle_tc_x_015


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
        params = kwargs.get("params") or {}
        if path == "/clients":
            q = params.get("q")
            return self._list_response(
                [item for item in self.clients if item.get("client_code") == q]
            )
        if path.startswith("/bills/"):
            bill_id = path.removeprefix("/bills/")
            for bill in self.bills:
                if bill["id"] == bill_id:
                    return FakeResponse(200, bill)
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            item = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients.append(item)
            return FakeResponse(201, item)
        if path == "/bills/manual":
            bill = {
                "id": f"bill-{len(self.bills) + 1}",
                "client_id": payload["client_id"],
                "case_id": payload.get("case_id"),
                "currency": payload["currency"],
                "direction": payload["direction"],
                "status": payload["status"],
                "amount": "300.00",
                "balance": "300.00",
                "items": [
                    {
                        "id": "bill-item-1",
                        "bill_id": "bill-1",
                        "case_id": payload.get("case_id"),
                        "description": payload["items"][0]["description"],
                        "quantity": payload["items"][0]["quantity"],
                        "unit_price": payload["items"][0]["unit_price"],
                        "amount": "300.00",
                    }
                ],
            }
            self.bills.append(bill)
            return FakeResponse(201, bill)
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
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
        id="TC-X-015",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="非案件账单",
        stage_code=None,
        stage_name="非案件账单",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_015_handler_creates_non_case_manual_bill() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-NCB",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_015(runtime, _case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == ["/clients", "/bills/manual"]
    bill = runtime.api.bills[0]
    assert bill["case_id"] is None
    assert bill["items"][0]["case_id"] is None
    assert bill["amount"] == "300.00"
    assert runtime.db.rows == []


def test_tc_x_015_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-NCB-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_015(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [("t_bill_item", {"bill_id": "bill-1", "case_id": None})]


def test_tc_x_015_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_015, "_is_skeleton", False)
    assert getattr(handle_tc_x_014, "_is_skeleton", False) is True
