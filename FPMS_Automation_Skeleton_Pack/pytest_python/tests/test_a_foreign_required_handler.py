from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_005, handle_tc_a_006


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
        self.clients: dict[str, dict[str, Any]] = {}
        self.case: dict[str, Any] | None = None

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            code = kwargs.get("params", {}).get("q")
            client = self.clients.get(code)
            return FakeResponse(200, _list_response(client))
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            if self.case and self.case.get("case_no") == case_no:
                return FakeResponse(200, _list_response(self.case))
            return FakeResponse(200, _list_response(None))
        if self.case is not None and path == f"/cases/{self.case['id']}":
            return FakeResponse(200, self.case)
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            client = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients[payload["client_code"]] = client
            return FakeResponse(201, client)
        if path == "/cases":
            return self._post_case(payload)
        return FakeResponse(404, {"message": "not found"})

    def _post_case(self, payload: dict[str, Any]) -> FakeResponse:
        if payload["flow_dir"] in {"CN_OUTBOUND", "FOREIGN_INBOUND"}:
            if not payload.get("to_country"):
                return _business_error(
                    "CASE_TO_COUNTRY_REQUIRED",
                    {"field": "to_country"},
                )
            if not payload.get("foreign_agent_id"):
                return _business_error(
                    "CASE_FOREIGN_AGENT_REQUIRED",
                    {"field": "foreign_agent_id"},
                )
            agent = _client_by_id(self.clients, payload["foreign_agent_id"])
            if agent is None or agent.get("client_type") != "AGENT":
                return _business_error(
                    "CASE_FOREIGN_AGENT_INVALID_TYPE",
                    {"field": "foreign_agent_id"},
                )

        self.case = {"id": "case-foreign-001", "status": "NOT_FILED", **payload}
        return FakeResponse(201, self.case)


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
        id="TC-A-005",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Unhappy"],
        topic="A1 涉外必填项",
        stage_code="A1",
        stage_name="涉外必填项",
        coverage_ids=["FR-CM-02", "FR-CM-03", "V-A-03", "V-B-01", "V-B-02"],
        requirement_ids=["FR-CM-02", "FR-CM-03"],
        validation_ids=["V-A-03", "V-B-01", "V-B-02"],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-CL-002", "DS-CL-003", "DS-U-FM-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-003"],
    )


def test_tc_a_005_rejects_foreign_missing_fields_then_creates_valid_case() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-FGN",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_005(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }

    client_payloads = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/clients"
    ]
    assert [payload["client_type"] for payload in client_payloads] == [
        "CLIENT",
        "AGENT",
    ]

    case_payloads = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ]
    assert [payload["case_no"] for payload in case_payloads] == [
        "CASE-A-FGN-RUN-A-FGN-003-NO-TO",
        "CASE-A-FGN-RUN-A-FGN-003-NO-AG",
        "CASE-A-FGN-RUN-A-FGN-003-BAD-AG",
        "CASE-A-FGN-RUN-A-FGN-003-OK",
    ]
    assert all(payload["flow_dir"] == "CN_OUTBOUND" for payload in case_payloads)
    assert all(payload["case_type"] == "NORMAL" for payload in case_payloads)
    assert all(payload["patent_category"] == "INV" for payload in case_payloads)
    assert all(payload["from_country"] == "CN" for payload in case_payloads)

    assert "to_country" not in case_payloads[0]
    assert case_payloads[1]["to_country"] == "US"
    assert "foreign_agent_id" not in case_payloads[1]
    assert case_payloads[2]["foreign_agent_id"] == "client-1"
    assert case_payloads[3]["foreign_agent_id"] == "client-2"
    assert case_payloads[3]["to_country"] == "US"

    get_case_calls = [
        call
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/cases"
    ]
    assert get_case_calls[-1]["kwargs"]["params"]["case_no"] == (
        "CASE-A-FGN-RUN-A-FGN-003-OK"
    )


def test_tc_a_005_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-FGN-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_005(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_case",
            {
                "case_no": "CASE-A-FGN-RUN-A-FGN-DB-003-OK",
                "flow_dir": "CN_OUTBOUND",
            },
        )
    ]


def test_tc_a_005_is_unskeletoned_and_tc_a_006_stays_skeleton() -> None:
    assert not getattr(handle_tc_a_005, "_is_skeleton", False)
    assert not getattr(handle_tc_a_006, "_is_skeleton", False)


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _business_error(code: str, details: dict[str, Any]) -> FakeResponse:
    return FakeResponse(
        400,
        {
            "error": {
                "code": code,
                "message": code,
                "details": details,
            }
        },
    )


def _client_by_id(
    clients: dict[str, dict[str, Any]], client_id: str
) -> dict[str, Any] | None:
    for client in clients.values():
        if client.get("id") == client_id:
            return client
    return None
