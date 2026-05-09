from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_018, handle_tc_x_019


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
        if path == "/documents/dispatch/mailing/batch-register":
            items = []
            for document_id in payload["selected_document_ids"]:
                document = self._document(document_id)
                document["outgoing_reg_no"] = payload["outgoing_reg_no"]
                document["forward_date"] = payload.get("forward_date")
                items.append(
                    {
                        "document_id": document_id,
                        "outgoing_reg_no": document["outgoing_reg_no"],
                        "forward_date": document["forward_date"],
                    }
                )
            return FakeResponse(200, {"items": items})
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _document(self, document_id: str) -> dict[str, Any]:
        for document in self.documents:
            if document["id"] == document_id:
                return document
        raise AssertionError(f"Document not found: {document_id}")


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
        id="TC-X-018",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="邮寄信息登记",
        stage_code=None,
        stage_name="邮寄信息登记",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_018_handler_registers_outgoing_document_mailing() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-MAIL",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_018(runtime, _case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == [
        "/clients",
        "/applicants",
        "/cases",
        "/documents",
        "/documents/dispatch/mailing/batch-register",
    ]
    document = runtime.api.documents[0]
    assert document["title"] == "X-OUT-DOC-RUN-X-MAIL-018"
    assert document["direction"] == "OUT"
    assert document["outgoing_reg_no"] == "X18-REG-RUN-X-MAIL-001"
    assert document["forward_date"] == "2026-05-09"
    assert runtime.db.rows == []


def test_tc_x_018_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-MAIL-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_018(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_document",
            {
                "id": "document-1",
                "outgoing_reg_no": "X18-REG-RUN-X-MAIL-DB-001",
            },
        )
    ]


def test_tc_x_018_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_018, "_is_skeleton", False)
    assert getattr(handle_tc_x_019, "_is_skeleton", False) is True
