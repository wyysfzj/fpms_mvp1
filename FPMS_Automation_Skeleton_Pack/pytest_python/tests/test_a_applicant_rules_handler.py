from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_006


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
    ):
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
        self.applicants: dict[str, dict[str, Any]] = {}
        self.cases: list[dict[str, Any]] = []
        self.case_counter = 0
        self.error_access_log: list[tuple[str, str]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/applicants":
            code = kwargs.get("params", {}).get("q")
            applicant = self.applicants.get(code)
            return FakeResponse(200, _list_response(applicant))
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            case = next(
                (item for item in self.cases if item["case_no"] == case_no), None
            )
            return FakeResponse(200, _list_response(case))
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/applicants":
            applicant = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants[payload["code"]] = applicant
            return FakeResponse(201, applicant)
        if path == "/cases":
            return self._post_case(payload)
        return FakeResponse(404, {"message": "not found"})

    def _post_case(self, payload: dict[str, Any]) -> FakeResponse:
        applicants = payload.get("applicants") or []
        if not applicants:
            return _business_error(
                self.error_access_log,
                "CASE_APPLICANT_REQUIRED",
                "At least one applicant is required",
            )

        first_count = sum(1 for applicant in applicants if applicant.get("is_first"))
        if first_count == 0:
            return _business_error(
                self.error_access_log,
                "CASE_FIRST_APPLICANT_REQUIRED",
                "Exactly one applicant must be marked as first",
            )
        if first_count > 1:
            return _business_error(
                self.error_access_log,
                "CASE_DUPLICATE_FIRST_APPLICANT",
                "Only one applicant can be marked as first",
            )

        seqs = [applicant.get("seq") for applicant in applicants]
        if len(seqs) != len(set(seqs)):
            return _business_error(
                self.error_access_log,
                "CASE_DUPLICATE_APPLICANT_SEQ",
                "Applicant seq values must be unique",
            )

        first_applicant_id = next(
            (
                applicant.get("applicant_id")
                for applicant in applicants
                if applicant.get("is_first")
            ),
            None,
        )
        normalized_kind = (payload.get("applicant_kind") or "").strip().upper()
        if normalized_kind and first_applicant_id:
            first_applicant = _applicant_by_id(self.applicants, first_applicant_id)
            first_type = (
                (first_applicant or {}).get("applicant_type", "").strip().upper()
            )
            if first_type == "INDIVIDUAL" and normalized_kind != "INDIVIDUAL":
                return _business_error(
                    self.error_access_log,
                    "CASE_APPLICANT_KIND_MISMATCH",
                    "applicant_kind does not match the first applicant type",
                    {
                        "applicant_kind": normalized_kind,
                        "first_applicant_type": first_type,
                        "first_applicant_id": first_applicant_id,
                    },
                )
            if first_type in {"ENTITY", "UNIV", "GOV"} and normalized_kind not in {
                "ENTITY",
                "UNIV",
                "GOV",
            }:
                return _business_error(
                    self.error_access_log,
                    "CASE_APPLICANT_KIND_MISMATCH",
                    "applicant_kind does not match the first applicant type",
                    {
                        "applicant_kind": normalized_kind,
                        "first_applicant_type": first_type,
                        "first_applicant_id": first_applicant_id,
                    },
                )

        self.case_counter += 1
        case = {
            "id": f"case-{self.case_counter}",
            "status": "NOT_FILED",
            **payload,
        }
        self.cases.append(case)
        return FakeResponse(201, case)


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
        id="TC-A-006",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Unhappy", "Boundary"],
        topic="A1 申请人列表规则",
        stage_code="A1",
        stage_name="申请人列表规则",
        coverage_ids=["FR-CM-02", "V-C-01", "V-C-02", "V-C-03"],
        requirement_ids=["FR-CM-02"],
        validation_ids=["V-C-01", "V-C-02", "V-C-03"],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-AP-001", "DS-AP-002", "DS-U-FM-01"],
        dynamic_refs=[],
    )


def test_tc_a_006_rejects_empty_duplicate_first_and_kind_mismatch_then_accepts() -> (
    None
):
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-APP-RULES",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_006(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "pw",
    }

    case_payloads = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ]
    assert [payload["case_no"] for payload in case_payloads] == [
        "A6-RUN-A-APP-RULES-NOAPP",
        "A6-RUN-A-APP-RULES-DUP",
        "A6-RUN-A-APP-RULES-KIND",
        "A6-RUN-A-APP-RULES-OK",
    ]

    assert case_payloads[0]["applicants"] == []
    assert case_payloads[1]["applicants"][0]["is_first"] is True
    assert case_payloads[1]["applicants"][1]["is_first"] is True
    assert case_payloads[2]["applicant_kind"] == "ENTITY"
    assert case_payloads[3]["applicant_kind"] == "INDIVIDUAL"

    assert runtime.api.error_access_log.count(("payload", "error")) >= 3
    assert ("error", "code") in runtime.api.error_access_log
    assert ("error", "details") in runtime.api.error_access_log

    created_case = runtime.api.cases[-1]
    assert created_case["case_no"] == "A6-RUN-A-APP-RULES-OK"
    assert created_case["applicant_kind"] == "INDIVIDUAL"

    case_gets = [
        call
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/cases"
    ]
    assert case_gets[-1]["kwargs"]["params"]["case_no"] == created_case["case_no"]

    assert runtime.db.calls == []


def test_tc_a_006_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-APP-RULES-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_006(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.calls == [
        (
            "t_case",
            {
                "case_no": "A6-RUN-A-APP-RULES-DB-OK",
                "status": "NOT_FILED",
            },
        ),
        (
            "t_case_applicant",
            {
                "case_id": "case-1",
            },
        ),
    ]


def test_tc_a_006_is_no_longer_skeleton() -> None:
    assert not getattr(handle_tc_a_006, "_is_skeleton", False)


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _business_error(
    access_log: list[tuple[str, str]],
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> FakeResponse:
    payload = TrackingDict(
        access_log,
        "payload",
        {
            "error": TrackingDict(
                access_log,
                "error",
                {"code": code, "message": message, "details": details},
            )
        },
    )
    return FakeResponse(400, payload)


def _applicant_by_id(
    applicants: dict[str, dict[str, Any]], applicant_id: str | None
) -> dict[str, Any] | None:
    if applicant_id is None:
        return None
    for applicant in applicants.values():
        if applicant.get("id") == applicant_id:
            return applicant
    return None
