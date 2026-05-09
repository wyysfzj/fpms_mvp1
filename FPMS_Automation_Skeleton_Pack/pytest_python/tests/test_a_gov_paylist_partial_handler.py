from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from handlers import wave_a
from handlers.wave_a import handle_tc_a_018


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> Any:
        return self._payload


class FakeApi:
    def __init__(self) -> None:
        self.paid_fee_item_ids: set[str] = set()

    def login(self, username: str, password: str) -> None:
        assert username == "admin"
        assert password == "dummy-password"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        payload = dict(kwargs.get("json") or {})
        if path == "/pay-lists/from-fee-items":
            return FakeResponse(201, {"pay_list": {"id": "pay-list-1"}})
        if path == "/gov-payments":
            return self._post_gov_payment(payload)
        if path == "/pay-lists/pay-list-1/mark-paid":
            return FakeResponse(
                409, {"error": {"code": "PAY_LIST_STATE_CONFLICT"}}
            )
        return FakeResponse(404, {"message": "not found"})

    def _post_gov_payment(self, payload: dict[str, Any]) -> FakeResponse:
        fee_item_id = str(payload.get("fee_item_id"))
        if payload.get("paid_amount") == "0.00":
            return FakeResponse(400, {"error": {"code": "GOV_PAYMENT_INVALID"}})
        if fee_item_id in self.paid_fee_item_ids:
            return FakeResponse(409, {"error": {"code": "GOV_PAYMENT_DUPLICATE"}})
        self.paid_fee_item_ids.add(fee_item_id)
        return FakeResponse(
            201,
            {
                "gov_payment": {"id": "gov-payment-1", "status": "PAID"},
                "pay_list": {"id": "pay-list-1", "status": "PARTIAL"},
            },
        )


class FakeDb:
    def enabled(self) -> bool:
        return True

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        expected = {"id": "pay-list-1", "status": "PARTIAL"}
        assert table == "t_pay_list"
        assert where == expected
        return expected


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


@pytest.fixture
def tc_a_018_fee_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        wave_a,
        "_arrange_apply_fee_draft",
        lambda runtime, suffix: {"id": "draft-1"},
    )
    monkeypatch.setattr(
        wave_a,
        "_get_fee_items",
        lambda runtime, draft_id: [
            {
                "id": "fee-gov-base",
                "fee_type": "GOV",
                "fee_code": "APPLY_BASE_GOV",
                "amount": "150.00",
            },
            {
                "id": "fee-gov-excess",
                "fee_type": "GOV",
                "fee_code": "APPLY_EXCESS_CLAIM",
                "amount": "45.00",
            },
        ],
    )


def test_tc_a_018_expects_partial_pay_list_after_single_gov_payment(
    tc_a_018_fee_setup: None,
) -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-A18-PARTIAL",
        api=FakeApi(),
        db=FakeDb(),
    )

    handle_tc_a_018(runtime, case={})  # type: ignore[arg-type]
