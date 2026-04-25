from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import handle_tc_w0_001, handle_tc_w0_002


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
        self.client_id = "client-001"
        self.addresses: list[dict[str, Any]] = []
        self.contacts: list[dict[str, Any]] = []
        self.client: dict[str, Any] | None = None

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            self.client = {"id": self.client_id, **payload}
            return FakeResponse(201, self.client)
        if path == f"/clients/{self.client_id}/addresses":
            address = {
                "id": f"addr-{len(self.addresses) + 1}",
                "client_id": self.client_id,
                **payload,
            }
            self.addresses.append(address)
            return FakeResponse(201, address)
        if path == f"/clients/{self.client_id}/contacts":
            contact = {"id": "contact-1", "client_id": self.client_id, **payload}
            self.contacts.append(contact)
            return FakeResponse(201, contact)
        return FakeResponse(404, {"message": "not found"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            return FakeResponse(
                200,
                {
                    "items": [self.client],
                    "page": 1,
                    "page_size": 20,
                    "total": 1,
                },
            )
        if path == f"/clients/{self.client_id}":
            return FakeResponse(200, self.client)
        if path == f"/clients/{self.client_id}/addresses":
            return FakeResponse(200, self.addresses)
        if path == f"/clients/{self.client_id}/contacts":
            return FakeResponse(200, self.contacts)
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


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-001",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy"],
        topic="主数据-客户",
        stage_code=None,
        stage_name="主数据-客户",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-CL-001", "DS-U-ADM"],
    )


def test_tc_w0_001_handler_creates_client_addresses_and_contact_via_api() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="admin123",
        run_id="RUN-W0-001",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "admin123",
    }
    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == [
        "/clients",
        "/clients/client-001/addresses",
        "/clients/client-001/addresses",
        "/clients/client-001/contacts",
    ]
    client_payload = runtime.api.calls[1]["kwargs"]["json"]
    assert client_payload["client_code"] == "CL-W0-001-RUN-W0-001"
    assert client_payload["name_cn"].endswith("-RUN-W0-001")
    assert client_payload["client_type"] == "CLIENT"

    address_payloads = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"].endswith("/addresses")
    ]
    assert [payload["address_type"] for payload in address_payloads] == [
        "MAILING",
        "BILLING",
    ]
    assert all(payload["country_code"] == "CN" for payload in address_payloads)

    contact_payload = runtime.api.calls[4]["kwargs"]["json"]
    assert contact_payload["contact_name"] == "DS-CL-001 Contact RUN-W0-001"
    assert contact_payload["is_primary"] is True

    get_paths = [call["path"] for call in runtime.api.calls if call["method"] == "GET"]
    assert get_paths == [
        "/clients",
        "/clients/client-001",
        "/clients/client-001/addresses",
        "/clients/client-001/contacts",
    ]


def test_tc_w0_001_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="admin123",
        run_id="RUN-W0-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_001(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_client", {"client_code": "CL-W0-001-RUN-W0-DB"}),
        ("t_client_address", {"client_id": "client-001"}),
        ("t_client_contact", {"client_id": "client-001"}),
    ]


def test_only_tc_w0_001_is_no_longer_skeleton() -> None:
    assert not getattr(handle_tc_w0_001, "_is_skeleton", False)
    assert getattr(handle_tc_w0_002, "_is_skeleton", False) is True
