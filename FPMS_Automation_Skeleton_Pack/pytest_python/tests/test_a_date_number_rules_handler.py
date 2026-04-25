from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_008


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


class TrackingDict(dict[str, Any]):
    def __init__(
        self, access_log: list[tuple[str, str]], label: str, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self._access_log = access_log
        self._label = label

    def get(self, key: str, default: Any = None) -> Any:
        self._access_log.append((self._label, key))
        return super().get(key, default)

    def __getitem__(self, key: str) -> Any:
        self._access_log.append((self._label, key))
        return super().__getitem__(key)


class FakeApi:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.clients: dict[str, dict[str, Any]] = {}
        self.applicants: dict[str, dict[str, Any]] = {}
        self.cases: list[dict[str, Any]] = []
        self.error_access_log: list[tuple[str, str]] = []

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
        if path == "/applicants":
            code = kwargs.get("params", {}).get("q")
            applicant = self.applicants.get(code)
            return FakeResponse(200, _list_response(applicant))
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            if case_no is None:
                return FakeResponse(200, _list_response_many(self.cases))
            matches = [case for case in self.cases if case["case_no"] == case_no]
            return FakeResponse(200, _list_response_many(matches))
        if path.startswith("/cases/"):
            case_id = path.rsplit("/", 1)[-1]
            case = next((item for item in self.cases if item["id"] == case_id), None)
            return (
                FakeResponse(200, case)
                if case is not None
                else FakeResponse(404, {"message": "not found"})
            )
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            client = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients[payload["client_code"]] = client
            return FakeResponse(201, client)
        if path == "/applicants":
            applicant = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants[payload["code"]] = applicant
            return FakeResponse(201, applicant)
        if path == "/cases":
            case = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                **payload,
            }
            self.cases.append(case)
            return FakeResponse(201, case)
        return FakeResponse(404, {"message": "not found"})

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if not path.startswith("/cases/"):
            return FakeResponse(404, {"message": "not found"})
        case_id = path.rsplit("/", 1)[-1]
        case = next((item for item in self.cases if item["id"] == case_id), None)
        if case is None:
            return FakeResponse(404, {"message": "not found"})

        status = (
            str(payload.get("status", case.get("status", "NOT_FILED"))).strip().upper()
        )
        app_no = payload.get("app_no")
        filing_date = payload.get("filing_date")
        priorities = payload.get("priorities", case.get("priorities"))

        if status == "PUBLISHED":
            missing = [
                field
                for field in ["pub_no", "pub_date"]
                if _is_missing(payload.get(field))
            ]
            if missing:
                return _business_error(
                    self.error_access_log,
                    "CASE_PUBLISHED_FIELDS_REQUIRED",
                    "Status PUBLISHED requires publication fields",
                    {"status": "PUBLISHED", "missing_fields": missing},
                )
        if status == "GRANTED":
            missing = [
                field
                for field in [
                    "grant_no",
                    "grant_date",
                    "first_annuity_year",
                    "valid_until",
                ]
                if _is_missing(payload.get(field))
            ]
            if missing:
                return _business_error(
                    self.error_access_log,
                    "CASE_GRANTED_FIELDS_REQUIRED",
                    "Status GRANTED requires grant fields",
                    {"status": "GRANTED", "missing_fields": missing},
                )

        if status in {"PUBLISHED", "GRANTED"} and _app_no_is_invalid(app_no):
            return _business_error(
                self.error_access_log,
                "CASE_APP_NO_INVALID",
                "app_no is invalid",
                {"app_no": app_no},
            )

        if status in {"PUBLISHED", "GRANTED"} and filing_date is not None:
            earliest_priority = _earliest_priority_date(priorities)
            if earliest_priority is not None and str(filing_date) < earliest_priority:
                return _business_error(
                    self.error_access_log,
                    "CASE_FILING_BEFORE_PRIORITY",
                    "filing_date is before the earliest priority date",
                    {
                        "filing_date": str(filing_date),
                        "earliest_priority_date": earliest_priority,
                    },
                )

        case.update(payload)
        case["status"] = status
        if isinstance(app_no, str):
            case["app_no"] = app_no.strip()
        return FakeResponse(200, case)


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


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-008",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Unhappy", "Boundary"],
        topic="A1 日期与编号一致性",
        stage_code="A1",
        stage_name="日期与编号一致性",
        coverage_ids=["FR-CM-02", "V-D-01", "V-D-02", "V-D-03", "V-D-04", "V-A-04"],
        requirement_ids=["FR-CM-02"],
        validation_ids=["V-D-01", "V-D-02", "V-D-03", "V-D-04", "V-A-04"],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-FM-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-004"],
    )


def test_tc_a_008_rejects_date_and_app_no_rule_violations_then_accepts_equal_priority_case() -> (
    None
):
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DATE-RULES",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_008(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }

    client_payload = _post_payload(runtime.api.calls, "/clients")
    assert client_payload["client_code"] == "CL-A-001-RUN-A-DATE-RULES"
    assert client_payload["client_type"] == "CLIENT"

    applicant_payload = _post_payload(runtime.api.calls, "/applicants")
    assert applicant_payload["code"] == "AP-A-008-ENTITY-RUN-A-DATE-RULES"
    assert applicant_payload["applicant_type"] == "ENTITY"

    case_posts = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ]
    assert len(case_posts) == 1
    assert case_posts[0]["case_no"] == "A8-RUN-A-DATE-RULES-BASE"
    assert "status" not in case_posts[0]
    assert "app_no" not in case_posts[0]
    assert "filing_date" not in case_posts[0]
    assert case_posts[0]["priorities"][0]["prio_date"] == "2026-03-15"

    case_puts = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "PUT" and call["path"] == "/cases/case-1"
    ]
    assert [payload["status"] for payload in case_puts] == [
        "PUBLISHED",
        "GRANTED",
        "PUBLISHED",
        "PUBLISHED",
        "PUBLISHED",
    ]
    assert case_puts[0]["filing_date"] == "2026-03-15"
    assert case_puts[0]["app_no"] == "A8APP-RUN-A-DATE-RULES-PUB"
    assert "pub_no" not in case_puts[0]
    assert "pub_date" not in case_puts[0]

    assert case_puts[1]["pub_no"] == "PUB-RUN-A-DATE-RULES-001"
    assert case_puts[1]["pub_date"] == "2026-04-01"
    assert "grant_no" not in case_puts[1]
    assert "grant_date" not in case_puts[1]
    assert "first_annuity_year" not in case_puts[1]
    assert "valid_until" not in case_puts[1]

    assert case_puts[2]["filing_date"] == "2026-03-14"
    assert case_puts[2]["pub_no"] == "PUB-RUN-A-DATE-RULES-002"

    assert case_puts[3]["app_no"].strip() == "A8APP-RUN-A-DATE-RULES-EQ"
    assert case_puts[3]["filing_date"] == "2026-03-15"

    assert case_puts[4]["app_no"] == "CNRUN-A-DATE-RULES\n01"

    assert ("payload", "error") in runtime.api.error_access_log
    assert ("error", "code") in runtime.api.error_access_log
    assert ("error", "details") in runtime.api.error_access_log

    created_case = runtime.api.cases[-1]
    assert created_case["case_no"] == "A8-RUN-A-DATE-RULES-BASE"
    assert created_case["app_no"] == "A8APP-RUN-A-DATE-RULES-EQ"
    assert created_case["status"] == "PUBLISHED"

    case_gets = [
        call
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/cases"
    ]
    assert case_gets[-1]["kwargs"]["params"]["case_no"] == "A8-RUN-A-DATE-RULES-BASE"

    assert runtime.db.calls == []


def test_tc_a_008_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-DATE-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_008(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.calls == [("t_case", {"case_no": "A8-RUN-A-DATE-DB-BASE"})]
    assert not getattr(handle_tc_a_008, "_is_skeleton", False)


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _list_response_many(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": records, "page": 1, "page_size": 20, "total": len(records)}


def _business_error(
    access_log: list[tuple[str, str]],
    code: str,
    message: str,
    details: dict[str, Any] | None,
) -> FakeResponse:
    error = TrackingDict(access_log, "error", code=code, message=message)
    if details is not None:
        error["details"] = TrackingDict(access_log, "details", **details)
    else:
        error["details"] = None
    payload = TrackingDict(access_log, "payload", error=error)
    return FakeResponse(400, payload)


def _is_missing(value: Any) -> bool:
    return value in (None, "")


def _app_no_is_invalid(value: Any) -> bool:
    if not isinstance(value, str):
        return True
    trimmed = value.strip()
    if not trimmed:
        return True
    if any(ord(ch) < 32 for ch in value):
        return True
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./-")
    return any(ch not in allowed for ch in trimmed)


def _earliest_priority_date(priorities: Any) -> str | None:
    if not isinstance(priorities, list):
        return None
    dates = [
        str(priority["prio_date"])
        for priority in priorities
        if isinstance(priority, dict) and priority.get("prio_date")
    ]
    if not dates:
        return None
    return min(dates)


def _post_payload(calls: list[dict[str, Any]], path: str) -> dict[str, Any]:
    for call in calls:
        if call["method"] == "POST" and call["path"] == path:
            return call["kwargs"]["json"]
    raise AssertionError(f"Missing POST call for {path}")
