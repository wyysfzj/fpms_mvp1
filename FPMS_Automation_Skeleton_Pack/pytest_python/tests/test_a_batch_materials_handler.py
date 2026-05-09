from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from handlers.wave_a import _arrange_batch2_cases


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

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        params = kwargs.get("params") or {}
        if path == "/clients":
            return self._list_response(self._filter_by_q(self.clients, params))
        if path == "/applicants":
            return self._list_response(self._filter_by_q(self.applicants, params))
        if path == "/cases":
            return self._list_response(
                [
                    item
                    for item in self.cases
                    if item.get("case_no") == params.get("case_no")
                ]
            )
        if path == "/documents":
            return self._list_response(self._filter_documents(params))
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = dict(kwargs["json"])
        if path == "/clients":
            item = {"id": "client-1", **payload}
            self.clients.append(item)
            return FakeResponse(201, item)
        if path == "/applicants":
            item = {"id": "applicant-1", **payload}
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
            200,
            {"items": items, "page": 1, "page_size": 20, "total": len(items)},
        )

    def _filter_by_q(
        self, items: list[dict[str, Any]], params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        q = params.get("q")
        if not q:
            return list(items)
        return [
            item
            for item in items
            if q in str(item.get("client_code", ""))
            or q in str(item.get("code", ""))
            or q in str(item.get("name_cn", ""))
        ]

    def _filter_documents(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        items = list(self.documents)
        if params.get("case_id"):
            items = [item for item in items if item.get("case_id") == params["case_id"]]
        if params.get("direction"):
            items = [
                item for item in items if item.get("direction") == params["direction"]
            ]
        if params.get("q"):
            items = [item for item in items if params["q"] in item.get("title", "")]
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


def test_arrange_batch2_cases_creates_required_material_documents() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-A-BATCH-MATERIALS",
        api=FakeApi(),
        db=FakeDb(),
    )

    arranged = _arrange_batch2_cases(
        runtime,  # type: ignore[arg-type]
        case_suffixes=("011-INV", "011-DES"),
        patent_categories=("INVENTION", "DESIGN"),
    )

    case_ids = [case["id"] for case in arranged["cases"]]
    documents_by_case = {
        case_id: [
            document["title"]
            for document in runtime.api.documents
            if document["case_id"] == case_id
        ]
        for case_id in case_ids
    }
    assert documents_by_case[case_ids[0]] == [
        "申请请求书",
        "说明书",
        "权利要求书",
        "摘要",
    ]
    assert documents_by_case[case_ids[1]] == ["申请请求书", "外观设计图片"]
    assert {document["doc_type"] for document in runtime.api.documents} == {"CLIENT_IN"}
    assert {document["direction"] for document in runtime.api.documents} == {"IN"}
