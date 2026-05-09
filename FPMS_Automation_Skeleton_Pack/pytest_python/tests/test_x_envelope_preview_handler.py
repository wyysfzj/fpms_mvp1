from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_020, handle_tc_x_021


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
        self.addresses: list[dict[str, Any]] = []
        self.cases: list[dict[str, Any]] = []
        self.documents: list[dict[str, Any]] = []
        self.preview_sources: list[str] = []

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
        if path.endswith("/addresses") and path.startswith("/clients/"):
            client_id = path.split("/")[2]
            return FakeResponse(
                200,
                [
                    address
                    for address in self.addresses
                    if address.get("client_id") == client_id
                ],
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
        if path.startswith("/documents/") and path.endswith("/envelope-preview"):
            document_id = path.removeprefix("/documents/").removesuffix(
                "/envelope-preview"
            )
            return FakeResponse(200, self._envelope_preview(document_id))
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
        if path.endswith("/addresses") and path.startswith("/clients/"):
            client_id = path.split("/")[2]
            item = {
                "id": f"address-{len(self.addresses) + 1}",
                "client_id": client_id,
                **payload,
            }
            self.addresses.append(item)
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

    def _envelope_preview(self, document_id: str) -> dict[str, Any]:
        document = next(item for item in self.documents if item["id"] == document_id)
        case = next(item for item in self.cases if item["id"] == document["case_id"])
        client_id = case.get("client_id")
        client = next(item for item in self.clients if item["id"] == client_id)
        source = "MANUAL_REQUIRED"
        address: str | None = None

        doc_address_id = case.get("doc_address_id")
        if doc_address_id:
            doc_address = next(
                item for item in self.addresses if item["id"] == doc_address_id
            )
            source = "CASE_DOC_ADDRESS"
            address = doc_address["address_line1"]
        else:
            default_address = next(
                (
                    item
                    for item in self.addresses
                    if item["client_id"] == client_id and item.get("is_default") is True
                ),
                None,
            )
            if default_address is not None:
                source = "CLIENT_DEFAULT_ADDRESS"
                address = default_address["address_line1"]
            else:
                applicants = case.get("applicants") or []
                first_applicant = applicants[0] if applicants else {}
                if first_applicant.get("address_cn"):
                    source = "FIRST_APPLICANT_ADDRESS"
                    address = first_applicant["address_cn"]

        self.preview_sources.append(source)
        return {
            "document_id": document_id,
            "case_id": case["id"],
            "case_no": case["case_no"],
            "client_id": client_id,
            "client_name": client["name_cn"],
            "recipient_name": client["name_cn"] if address else None,
            "recipient_address": address,
            "address_source": source,
        }


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
        id="TC-X-020",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy", "Boundary"],
        topic="信封打印地址优先级",
        stage_code=None,
        stage_name="信封打印地址优先级",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_020_handler_verifies_envelope_preview_priority_sources() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-ENV",
        api=FakeApi(),
        db=FakeDb(),
    )

    handle_tc_x_020(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.preview_sources == [
        "CASE_DOC_ADDRESS",
        "CLIENT_DEFAULT_ADDRESS",
        "FIRST_APPLICANT_ADDRESS",
        "MANUAL_REQUIRED",
    ]
    assert len(runtime.api.documents) == 4
    assert [address["is_default"] for address in runtime.api.addresses] == [
        False,
        True,
    ]


def test_tc_x_020_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_020, "_is_skeleton", False)
    assert getattr(handle_tc_x_021, "_is_skeleton", False) is True
