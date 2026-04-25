from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_002, handle_tc_a_010


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
        self.addresses: dict[str, list[dict[str, Any]]] = {}
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
        if path.endswith("/addresses"):
            client_id = path.split("/")[2]
            return FakeResponse(200, self.addresses.get(client_id, []))
        if path == "/applicants":
            item = self.applicants.get(kwargs.get("params", {}).get("q"))
            return FakeResponse(200, _items([item] if item else []))
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            return FakeResponse(
                200, _items([c for c in self.cases if c["case_no"] == case_no])
            )
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
        if path.endswith("/addresses"):
            client_id = path.split("/")[2]
            item = {
                "id": f"addr-{sum(len(v) for v in self.addresses.values()) + 1}",
                **payload,
            }
            self.addresses.setdefault(client_id, []).append(item)
            return FakeResponse(201, item)
        if path == "/applicants":
            item = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants[payload["code"]] = item
            return FakeResponse(201, item)
        if path == "/cases":
            item = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                "created_at": "2026-04-18T00:00:00",
                "updated_at": "2026-04-18T00:00:00",
                **payload,
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


def test_tc_a_002_creates_full_field_case_and_checks_detail_surface() -> None:
    runtime = FakeRuntime("admin", "pw", "RUN-A2", FakeApi(), FakeDb(enabled=True))

    handle_tc_a_002(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0]["method"] == "LOGIN"
    case_payloads = [
        c["kwargs"]["json"]
        for c in runtime.api.calls
        if c["method"] == "POST" and c["path"] == "/cases"
    ]
    assert len(case_payloads) == 1
    payload = case_payloads[0]
    assert payload["case_no"] == "A002-RUN-A2"
    assert payload["doc_address_id"] == "addr-1"
    assert payload["bill_address_id"] == "addr-2"
    assert payload["spec_pages"] == 10
    assert payload["claim_count"] == 12
    assert payload["fee_reduction"] == "0.15"
    assert payload["discount_rate"] == "0.8000"
    assert payload["no_power"] is True
    assert len(payload["applicants"]) == 2
    assert len(payload["inventors"]) == 1
    assert [p["prio_date"] for p in payload["priorities"]] == [
        "2026-02-10",
        "2026-01-20",
    ]
    assert len(payload["bio_deposits"]) == 1
    assert runtime.db.calls == [
        ("t_case", {"id": "case-1", "case_no": "A002-RUN-A2"}),
        ("t_case_priority", {"case_id": "case-1"}),
        ("t_case_bio_deposit", {"case_id": "case-1"}),
    ]


def test_tc_a_002_is_implemented_and_unrelated_boundary_remains_skeleton() -> None:
    assert not getattr(handle_tc_a_002, "_is_skeleton", False)
    assert not getattr(handle_tc_a_010, "_is_skeleton", False)


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-002",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="A1 新案立案-完整字段",
        stage_code="A1",
        stage_name="新案立案",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-AP-001", "DS-AP-003", "DS-CL-001"],
        dynamic_refs=["CASE-A-${RUN_ID}-002"],
    )


def _items(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}
