from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_025, handle_tc_x_026


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
        self.applicants: list[dict[str, Any]] = []
        self.cases: list[dict[str, Any]] = []
        self.receipts: list[dict[str, Any]] = []

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
        if path == "/applicants":
            q = params.get("q")
            return self._list_response(
                [item for item in self.applicants if item.get("code") == q]
            )
        if path == "/cases":
            case_no = params.get("case_no")
            return self._list_response(
                [item for item in self.cases if item.get("case_no") == case_no]
            )
        if path.startswith("/cases/") and path.endswith("/receipts"):
            case_id = path.removeprefix("/cases/").removesuffix("/receipts")
            return FakeResponse(200, self._receipt_summary(case_id))
        if path.startswith("/cases/"):
            case_id = path.removeprefix("/cases/")
            for item in self.cases:
                if item["id"] == case_id:
                    return FakeResponse(200, item)
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            item = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients.append(item)
            return FakeResponse(201, item)
        if path == "/applicants":
            item = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants.append(item)
            return FakeResponse(201, item)
        if path == "/cases":
            item = {"id": f"case-{len(self.cases) + 1}", **payload}
            self.cases.append(item)
            return FakeResponse(201, item)
        if path == "/case-receipts":
            receipt = {"id": f"receipt-{len(self.receipts) + 1}", **payload}
            receivable = Decimal(str(receipt["receivable_amt"]))
            received = Decimal(str(receipt["received_amt"]))
            if receipt.get("is_arrears") is None and received < receivable:
                receipt["is_arrears"] = True
            if receipt.get("is_prepayment") is None and received > receivable:
                receipt["is_prepayment"] = True
            self.receipts.append(receipt)
            return FakeResponse(201, receipt)
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _receipt_summary(self, case_id: str) -> dict[str, Any]:
        receipts = [item for item in self.receipts if item["case_id"] == case_id]
        receivable = sum(
            (Decimal(str(item["receivable_amt"])) for item in receipts), Decimal("0")
        )
        received = sum(
            (Decimal(str(item["received_amt"])) for item in receipts), Decimal("0")
        )
        return {
            "id": receipts[0]["id"],
            "case_id": case_id,
            "fee_type": "SERVICE",
            "currency": "CNY",
            "receivable_amt": str(receivable),
            "received_amt": str(received),
            "is_arrears": receivable > received,
            "is_commissionable": True,
            "bills": [],
        }


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
        id="TC-X-025",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="个案收款手工登记",
        stage_code=None,
        stage_name="个案收款手工登记",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_025_handler_creates_arrears_and_prepayment_receipts() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-RCPT",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_025(runtime, _case())  # type: ignore[arg-type]

    assert len(runtime.api.receipts) == 2
    assert runtime.api.receipts[0]["is_arrears"] is True
    assert runtime.api.receipts[1]["is_prepayment"] is True
    assert runtime.api.receipts[0]["invoice_no"].startswith("INV-X25")
    assert runtime.db.rows == []


def test_tc_x_025_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-RCPT-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_025(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_case_receipt", {"id": "receipt-2", "is_prepayment": True})
    ]


def test_tc_x_025_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_025, "_is_skeleton", False)
    assert getattr(handle_tc_x_026, "_is_skeleton", False) is True
