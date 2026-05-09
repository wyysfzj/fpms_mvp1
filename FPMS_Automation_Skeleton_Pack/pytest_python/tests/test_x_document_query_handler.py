from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_002, handle_tc_x_003


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
        self.documents: list[dict[str, Any]] = []

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
        if path.startswith("/cases/"):
            case_id = path.removeprefix("/cases/")
            for item in self.cases:
                if item["id"] == case_id:
                    return FakeResponse(200, item)
        if path == "/documents":
            return self._list_response(self._filter_documents(params))
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
        if path == "/documents":
            item = {"id": f"document-{len(self.documents) + 1}", **payload}
            self.documents.append(item)
            return FakeResponse(201, item)
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _filter_documents(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        items = list(self.documents)
        if params.get("case_id"):
            items = [item for item in items if item["case_id"] == params["case_id"]]
        if params.get("direction"):
            items = [item for item in items if item["direction"] == params["direction"]]
        if params.get("q"):
            items = [item for item in items if params["q"] in item["title"]]
        if params.get("case_no"):
            case_ids = {
                item["id"]
                for item in self.cases
                if params["case_no"] in item.get("case_no", "")
            }
            items = [item for item in items if item["case_id"] in case_ids]
        if params.get("client_id"):
            case_ids = {
                item["id"]
                for item in self.cases
                if item.get("client_id") == params["client_id"]
            }
            items = [item for item in items if item["case_id"] in case_ids]
        if params.get("doc_type"):
            doc_types = params["doc_type"]
            if isinstance(doc_types, str):
                doc_types = [doc_types]
            items = [item for item in items if item["doc_type"] in doc_types]
        if params.get("date_from"):
            items = [item for item in items if item["doc_date"] >= params["date_from"]]
        if params.get("date_to"):
            items = [item for item in items if item["doc_date"] <= params["date_to"]]
        return items


class FakeDb:
    def enabled(self) -> bool:
        return False


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-X-003",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="中间文件查询与清单导出",
        stage_code=None,
        stage_name="中间文件查询与清单导出",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_003_handler_queries_documents_by_supported_filters() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-DOCQ",
        api=FakeApi(),
        db=FakeDb(),
    )

    handle_tc_x_003(runtime, _case())  # type: ignore[arg-type]

    assert len(runtime.api.documents) == 1
    query_params = [
        call["kwargs"].get("params", {})
        for call in runtime.api.calls
        if call.get("path") == "/documents" and call["method"] == "GET"
    ]
    assert any("q" in params for params in query_params)
    assert any("case_no" in params for params in query_params)
    assert any(params.get("doc_type") == ["CLIENT_OUT"] for params in query_params)


def test_tc_x_003_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_003, "_is_skeleton", False)
    assert getattr(handle_tc_x_002, "_is_skeleton", False) is True
