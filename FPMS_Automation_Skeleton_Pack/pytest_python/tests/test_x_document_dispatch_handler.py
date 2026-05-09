from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_019, handle_tc_x_020


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
        self.dispatches: list[dict[str, Any]] = []

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
            case_id = params.get("case_id")
            direction = params.get("direction")
            q = params.get("q")
            return self._list_response(
                [
                    item
                    for item in self.documents
                    if item.get("case_id") == case_id
                    and item.get("direction") == direction
                    and item.get("title") == q
                ]
            )
        if path.startswith("/documents/dispatches/"):
            dispatch_id = path.removeprefix("/documents/dispatches/")
            for dispatch in self.dispatches:
                if dispatch["id"] == dispatch_id:
                    return FakeResponse(200, dispatch)
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
        if path == "/documents/dispatches":
            dispatch = {
                "id": f"dispatch-{len(self.dispatches) + 1}",
                "client_id": payload["client_id"],
                "dispatch_date": payload["dispatch_date"],
                "remark": payload.get("remark"),
                "lines": [
                    {"document_id": document_id, "dispatch_id": "dispatch-1"}
                    for document_id in payload["selected_document_ids"]
                ],
            }
            self.dispatches.append(dispatch)
            return FakeResponse(201, dispatch)
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )


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
        id="TC-X-019",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="文件交接单",
        stage_code=None,
        stage_name="文件交接单",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_019_handler_creates_dispatch_with_outbound_document_line() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-DSP",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_019(runtime, _case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == [
        "/clients",
        "/applicants",
        "/cases",
        "/documents",
        "/documents/dispatches",
    ]
    assert runtime.api.documents[0]["title"] == "X-OUT-DOC-RUN-X-DSP-019"
    assert runtime.api.dispatches[0]["lines"] == [
        {"document_id": "document-1", "dispatch_id": "dispatch-1"}
    ]
    assert runtime.db.rows == []


def test_tc_x_019_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-DSP-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_019(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_doc_dispatch_line",
            {"dispatch_id": "dispatch-1", "document_id": "document-1"},
        )
    ]


def test_tc_x_019_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_019, "_is_skeleton", False)
    assert getattr(handle_tc_x_020, "_is_skeleton", False) is True
