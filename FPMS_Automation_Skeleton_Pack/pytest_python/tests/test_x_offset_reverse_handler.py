from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_013


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
        self.payments: list[dict[str, Any]] = []
        self.offsets: list[dict[str, Any]] = []

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
        if path.startswith("/payments/"):
            payment_id = path.removeprefix("/payments/")
            for payment in self.payments:
                if payment["id"] == payment_id:
                    return FakeResponse(200, payment)
        if path == "/offsets":
            bill_id = params.get("bill_id")
            is_reversed = params.get("is_reversed")
            return self._list_response(
                [
                    item
                    for item in self.offsets
                    if item.get("bill_id") == bill_id
                    and item.get("is_reversed") is is_reversed
                ]
            )
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs.get("json") or {}
        if path == "/clients":
            item = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients.append(item)
            return FakeResponse(201, item)
        if path == "/bills/manual":
            bill = {
                "id": f"bill-{len(self.bills) + 1}",
                "client_id": payload["client_id"],
                "direction": payload["direction"],
                "status": "UNSETTLED",
                "amount": "500.00",
                "balance": "500.00",
                "items": [
                    {
                        "id": "bill-item-1",
                        "bill_id": "bill-1",
                        "amount": "500.00",
                    }
                ],
            }
            self.bills.append(bill)
            return FakeResponse(201, bill)
        if path == "/payments":
            payment = {
                "id": f"payment-{len(self.payments) + 1}",
                "client_id": payload["client_id"],
                "amount": "500.00",
                "payment_lines": [
                    {
                        "id": "payment-line-1",
                        "payment_id": "payment-1",
                        "amount": "500.00",
                        "allocated_amt": "0.00",
                        "balance_amt": "500.00",
                    }
                ],
            }
            self.payments.append(payment)
            return FakeResponse(201, payment)
        if path == "/offsets":
            offset = {
                "id": f"offset-{len(self.offsets) + 1}",
                "payment_line_id": payload["payment_line_id"],
                "bill_id": payload["bill_id"],
                "offset_amt": payload["offset_amt"],
                "is_reversed": False,
            }
            self.offsets.append(offset)
            self._apply_offset(offset)
            return FakeResponse(201, offset)
        if path.startswith("/offsets/") and path.endswith("/reverse"):
            offset_id = path.removeprefix("/offsets/").removesuffix("/reverse")
            offset = next(item for item in self.offsets if item["id"] == offset_id)
            if offset["is_reversed"] is True:
                return FakeResponse(400, {"code": "OFFSET_ALREADY_REVERSED"})
            offset["is_reversed"] = True
            self._reverse_offset(offset)
            return FakeResponse(200, offset)
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _apply_offset(self, offset: dict[str, Any]) -> None:
        bill = next(item for item in self.bills if item["id"] == offset["bill_id"])
        bill["balance"] = "0.00"
        bill["status"] = "SETTLED"
        line = self._payment_line(offset["payment_line_id"])
        line["allocated_amt"] = "500.00"
        line["balance_amt"] = "0.00"

    def _reverse_offset(self, offset: dict[str, Any]) -> None:
        bill = next(item for item in self.bills if item["id"] == offset["bill_id"])
        bill["balance"] = "500.00"
        bill["status"] = "UNSETTLED"
        line = self._payment_line(offset["payment_line_id"])
        line["allocated_amt"] = "0.00"
        line["balance_amt"] = "500.00"

    def _payment_line(self, payment_line_id: str) -> dict[str, Any]:
        for payment in self.payments:
            for line in payment["payment_lines"]:
                if line["id"] == payment_line_id:
                    return line
        raise AssertionError(f"Missing payment line {payment_line_id}")


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
        id="TC-X-013",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy", "Unhappy"],
        topic="反冲销",
        stage_code=None,
        stage_name="反冲销",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_013_handler_reverses_offset_and_rejects_duplicate() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-OFFREV",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_013(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.offsets[0]["is_reversed"] is True
    assert runtime.api.bills[0]["balance"] == "500.00"
    assert runtime.api.bills[0]["status"] == "UNSETTLED"
    assert runtime.api.payments[0]["payment_lines"][0]["balance_amt"] == "500.00"
    reverse_calls = [
        call
        for call in runtime.api.calls
        if str(call.get("path", "")).endswith("/reverse")
    ]
    assert len(reverse_calls) == 2
    assert runtime.db.rows == []


def test_tc_x_013_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-OFFREV-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_013(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [("t_offset", {"id": "offset-1", "is_reversed": True})]


def test_tc_x_013_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_013, "_is_skeleton", False)
