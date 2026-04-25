from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_009, handle_tc_a_010


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> Any:
        return self._payload


class FakeApi:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.clients: dict[str, dict[str, Any]] = {}
        self.applicants: dict[str, dict[str, Any]] = {}
        self.cases: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            item = self.clients.get(kwargs.get("params", {}).get("q"))
            return FakeResponse(200, _items([item] if item else []))
        if path == "/applicants":
            item = self.applicants.get(kwargs.get("params", {}).get("q"))
            return FakeResponse(200, _items([item] if item else []))
        if path.startswith("/cases/"):
            case_id = path.rsplit("/", 1)[-1]
            case = next((item for item in self.cases if item["id"] == case_id), None)
            return FakeResponse(200, case)
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            item = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients[payload["client_code"]] = item
            return FakeResponse(201, item)
        if path == "/applicants":
            item = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants[payload["code"]] = item
            return FakeResponse(201, item)
        if path == "/cases":
            if any(int(payload.get(field, 0)) < 0 for field in _SPEC_FIELDS):
                return FakeResponse(422, {"detail": [{"loc": ["body", "spec_pages"]}]})
            discount = Decimal(str(payload.get("discount_rate", "0")))
            if discount < Decimal("0") or discount > Decimal("1"):
                return FakeResponse(
                    422, {"detail": [{"loc": ["body", "discount_rate"]}]}
                )
            item = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                **payload,
                "discount_rate": f"{discount:.4f}",
            }
            self.cases.append(item)
            return FakeResponse(201, item)
        return FakeResponse(404, {"message": "not found"})


class FakeDb:
    def __init__(self, enabled: bool = False) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._enabled = enabled

    def enabled(self) -> bool:
        return self._enabled

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((table, where))
        return {"id": "row-id", **where}


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def test_tc_a_009_accepts_boundaries_and_rejects_schema_invalid_values() -> None:
    runtime = FakeRuntime("admin", "pw", "RUN-A9", FakeApi(), FakeDb(enabled=True))

    handle_tc_a_009(runtime, _case())  # type: ignore[arg-type]

    case_payloads = [
        c["kwargs"]["json"]
        for c in runtime.api.calls
        if c["method"] == "POST" and c["path"] == "/cases"
    ]
    assert [payload["case_no"] for payload in case_payloads] == [
        "A009-RUN-A9-ZERO",
        "A009-RUN-A9-ONE",
        "A009-RUN-A9-NEG",
        "A009-RUN-A9-LOW",
        "A009-RUN-A9-HIGH",
    ]
    assert case_payloads[0]["discount_rate"] == "0"
    assert case_payloads[1]["discount_rate"] == "1"
    assert case_payloads[1]["spec_pages"] == 999
    assert len(runtime.api.cases) == 2
    assert runtime.db.calls == [
        ("t_case", {"case_no": "A009-RUN-A9-ZERO"}),
        ("t_case", {"case_no": "A009-RUN-A9-ONE"}),
    ]


def test_tc_a_009_is_implemented_and_unrelated_boundary_remains_skeleton() -> None:
    assert not getattr(handle_tc_a_009, "_is_skeleton", False)
    assert not getattr(handle_tc_a_010, "_is_skeleton", False)


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-009",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P1",
        categories=["Boundary"],
        topic="A1 规格/费减/折扣边界",
        stage_code="A1",
        stage_name="规格费减折扣",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-FM-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-005"],
    )


def _items(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


_SPEC_FIELDS = [
    "spec_pages",
    "draw_pages",
    "claim_count",
    "claim_pages",
    "manuscript_words",
]
