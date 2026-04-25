from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_001, handle_tc_a_002


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
        self.client: dict[str, Any] | None = None
        self.applicant: dict[str, Any] | None = None
        self.case: dict[str, Any] | None = None

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            return FakeResponse(200, _list_response(self.client))
        if path == "/applicants":
            return FakeResponse(200, _list_response(self.applicant))
        if path == "/cases":
            return FakeResponse(200, _list_response(self.case))
        if self.case is not None and path == f"/cases/{self.case['id']}":
            return FakeResponse(200, self.case)
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            self.client = {"id": "client-001", **payload}
            return FakeResponse(201, self.client)
        if path == "/applicants":
            self.applicant = {"id": "applicant-001", **payload}
            return FakeResponse(201, self.applicant)
        if path == "/cases":
            self.case = {
                "id": "case-001",
                "status": "NOT_FILED",
                **payload,
            }
            return FakeResponse(201, self.case)
        return FakeResponse(404, {"message": "not found"})


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


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-001",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Happy"],
        topic="A1 新案立案-最小必填",
        stage_code="A1",
        stage_name="新案立案",
        coverage_ids=["FR-CM-01", "FR-CM-02"],
        requirement_ids=["FR-CM-01", "FR-CM-02"],
        validation_ids=["V-A-01", "V-C-01", "V-C-02"],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-AP-001", "DS-CL-001", "DS-CN", "DS-U-FM-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-001"],
    )


def test_tc_a_001_handler_creates_minimal_case_via_api() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-CASE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == ["/clients", "/applicants", "/cases"]

    client_payload = _post_payload(runtime.api.calls, "/clients")
    assert client_payload["client_code"] == "CL-A-001-RUN-A-CASE"
    assert client_payload["name_cn"].endswith("-RUN-A-CASE")
    assert client_payload["client_type"] == "CLIENT"

    applicant_payload = _post_payload(runtime.api.calls, "/applicants")
    assert applicant_payload["code"] == "AP-A-001-RUN-A-CASE"
    assert applicant_payload["name_cn"].endswith("-RUN-A-CASE")
    assert applicant_payload["is_active"] is True

    case_payload = _post_payload(runtime.api.calls, "/cases")
    assert case_payload["case_no"] == "CASE-A-RUN-A-CASE-001"
    assert case_payload["case_type"] == "NORMAL"
    assert case_payload["patent_category"] == "INV"
    assert case_payload["flow_dir"] == "CN_DOMESTIC"
    assert case_payload["from_country"] == "CN"
    assert case_payload["client_id"] == "client-001"
    assert case_payload["title_cn"].endswith("RUN-A-CASE")
    assert case_payload["recv_date"] == "2026-04-17"
    assert case_payload["applicants"] == [
        {
            "seq": 1,
            "is_first": True,
            "applicant_id": "applicant-001",
            "name_cn": "北京创新科技有限公司-RUN-A-CASE",
        }
    ]
    assert case_payload["inventors"] == []
    assert case_payload["priorities"] == []
    assert case_payload["bio_deposits"] == []

    get_paths = [call["path"] for call in runtime.api.calls if call["method"] == "GET"]
    assert get_paths == [
        "/clients",
        "/applicants",
        "/cases",
        "/cases/case-001",
    ]


def test_tc_a_001_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_case", {"case_no": "CASE-A-RUN-A-DB-001", "status": "NOT_FILED"}),
        ("t_case_applicant", {"case_id": "case-001"}),
    ]


def test_only_tc_a_001_is_no_longer_skeleton() -> None:
    assert not getattr(handle_tc_a_001, "_is_skeleton", False)
    assert not getattr(handle_tc_a_002, "_is_skeleton", False)


def _post_payload(calls: list[dict[str, Any]], path: str) -> dict[str, Any]:
    for call in calls:
        if call["method"] == "POST" and call["path"] == path:
            return call["kwargs"]["json"]
    raise AssertionError(f"Missing POST call for {path}")
