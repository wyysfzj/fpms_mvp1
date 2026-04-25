from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_010


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
        self.users: dict[str, dict[str, Any]] = {}
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
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            return FakeResponse(
                200, _items([case for case in self.cases if case["case_no"] == case_no])
            )
        if path == "/admin/users":
            return FakeResponse(200, _items(list(self.users.values())))
        if path in {"/tasks", "/fees/drafts"}:
            return FakeResponse(200, _items([]))
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
        if path == "/admin/users":
            item = {"id": f"user-{len(self.users) + 1}", **payload}
            self.users[payload["username"]] = item
            return FakeResponse(201, item)
        if path == "/cases":
            item = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                "filing_date": None,
                "app_no": None,
                "updated_at": "2026-04-18T00:00:00",
                **payload,
            }
            self.cases.append(item)
            return FakeResponse(201, item)
        if path.endswith("/limited-edit"):
            case_id = path.split("/")[2]
            case = next(item for item in self.cases if item["id"] == case_id)
            for field in [
                "title_cn",
                "title_en",
                "spec_pages",
                "draw_pages",
                "claim_count",
                "claim_pages",
                "manuscript_words",
                "inventors",
            ]:
                if field in payload:
                    case[field] = payload[field]
            case["updated_at"] = "2026-04-18T00:01:00"
            return FakeResponse(200, dict(case))
        return FakeResponse(404, {"message": "not found"})

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        if path.startswith("/cases/"):
            return FakeResponse(403, {"error": {"code": "FORBIDDEN"}})
        if path.startswith("/admin/users/"):
            return FakeResponse(200, kwargs["json"])
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


def test_tc_a_010_limited_edit_whitelist_blacklist_and_side_effect_surface() -> None:
    runtime = FakeRuntime("admin", "pw", "RUN-A10", FakeApi(), FakeDb(enabled=True))

    handle_tc_a_010(runtime, _case())  # type: ignore[arg-type]

    assert not getattr(handle_tc_a_010, "_is_skeleton", False)
    login_users = [
        call["username"] for call in runtime.api.calls if call["method"] == "LOGIN"
    ]
    assert login_users == ["admin", "limited-a010-RUN-A10", "admin"]

    limited_payload = next(
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"].endswith("/limited-edit")
    )
    assert limited_payload["title_cn"] == "A1 限制修改新标题 RUN-A10"
    assert limited_payload["case_no"] == "A10-SHOULD-NOT-CHANGE"

    case = runtime.api.cases[0]
    assert case["case_no"] == "A010-RUN-A10"
    assert case["status"] == "NOT_FILED"
    assert case["filing_date"] is None
    assert case["app_no"] is None
    assert case["title_cn"] == "A1 限制修改新标题 RUN-A10"
    assert case["draw_pages"] == 3
    assert [row["name_cn"] for row in case["inventors"]] == [
        "A10 发明人一 RUN-A10",
        "A10 发明人二 RUN-A10",
    ]
    assert ("t_case_inventor", {"case_id": "case-1"}) in runtime.db.calls


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-A-010",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P0",
        categories=["Happy", "Unhappy"],
        topic="A1 限制修改视图",
        stage_code="A1",
        stage_name="新案立案",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-LMT-01"],
        dynamic_refs=["CASE-A-${RUN_ID}-001"],
    )


def _items(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}
