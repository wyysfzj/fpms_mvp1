from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_007, handle_tc_a_010


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
            client_id = payload.get("client_id")
            for address_field in ["doc_address_id", "bill_address_id"]:
                address_id = payload.get(address_field)
                if address_id and not self._address_belongs_to_client(
                    address_id, client_id
                ):
                    return FakeResponse(
                        400,
                        {
                            "error": {
                                "code": "CASE_ADDRESS_CLIENT_MISMATCH",
                                "details": {"field": address_field},
                            }
                        },
                    )
            item = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                **payload,
            }
            self.cases.append(item)
            return FakeResponse(201, item)
        return FakeResponse(404, {"message": "not found"})

    def _address_belongs_to_client(self, address_id: str, client_id: str) -> bool:
        return any(
            item["id"] == address_id for item in self.addresses.get(client_id, [])
        )


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


def test_tc_a_007_accepts_no_inventor_valid_addresses_and_rejects_wrong_client_address() -> (
    None
):
    runtime = FakeRuntime("admin", "pw", "RUN-A7", FakeApi(), FakeDb(enabled=False))

    handle_tc_a_007(runtime, _case())  # type: ignore[arg-type]

    case_payloads = [
        c["kwargs"]["json"]
        for c in runtime.api.calls
        if c["method"] == "POST" and c["path"] == "/cases"
    ]
    assert [payload["case_no"] for payload in case_payloads] == [
        "A007-RUN-A7-NOINV",
        "A007-RUN-A7-ADDR",
        "A007-RUN-A7-WRONG",
    ]
    assert case_payloads[0]["inventors"] == []
    assert "doc_address_id" not in case_payloads[0]
    assert case_payloads[1]["doc_address_id"] == "addr-1"
    assert case_payloads[1]["bill_address_id"] == "addr-2"
    assert case_payloads[2]["doc_address_id"] == "addr-3"
    assert len(runtime.api.cases) == 2


def test_tc_a_007_is_implemented_and_unrelated_boundary_remains_skeleton() -> None:
    assert not getattr(handle_tc_a_007, "_is_skeleton", False)
    assert not getattr(handle_tc_a_010, "_is_skeleton", False)


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-007",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P1",
        categories=["Boundary"],
        topic="A1 发明人与地址",
        stage_code="A1",
        stage_name="发明人与地址",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-CL-001", "DS-CL-004"],
        dynamic_refs=[],
    )


def _items(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}
