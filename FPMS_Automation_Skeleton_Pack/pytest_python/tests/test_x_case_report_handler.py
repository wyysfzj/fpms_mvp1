from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_007


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
        if path == "/cases" and params.get("case_no"):
            case_no = params.get("case_no")
            return self._list_response(
                [item for item in self.cases if item.get("case_no") == case_no]
            )
        if path == "/cases":
            client_id = params.get("client_id")
            items = [
                item
                for item in self.cases
                if not client_id or item["client_id"] == client_id
            ]
            return FakeResponse(
                200,
                {
                    "items": items,
                    "page": 1,
                    "page_size": params.get("page_size", 20),
                    "total": len(items),
                    "summary": self._summary(items),
                },
            )
        if path.startswith("/cases/"):
            case_id = path.removeprefix("/cases/")
            for item in self.cases:
                if item["id"] == case_id:
                    return FakeResponse(200, item)
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
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _summary(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "total_case_count": len(items),
            "status_counts": self._counts(items, "status"),
            "case_type_counts": self._counts(items, "case_type"),
            "client_counts": [
                {
                    "key": client_id,
                    "label": client_id,
                    "count": count,
                    "case_type_counts": [],
                }
                for client_id, count in self._count_pairs(items, "client_id").items()
            ],
            "country_counts": [
                {"key": country, "count": count}
                for country, count in self._country_counts(items).items()
            ],
            "agent_counts": [],
            "year_trends": [],
            "month_trends": [],
            "granted_count": self._count_pairs(items, "status").get("GRANTED", 0),
            "terminated_count": self._count_pairs(items, "status").get("TERMINATED", 0),
            "invalidated_count": 0,
            "in_prosecution_count": self._count_pairs(items, "status").get(
                "PENDING", 0
            ),
        }

    def _counts(self, items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
        return [
            {"key": key, "count": count}
            for key, count in self._count_pairs(items, field).items()
        ]

    def _count_pairs(self, items: list[dict[str, Any]], field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            key = str(item.get(field) or "UNSPECIFIED")
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _country_counts(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            key = str(item.get("to_country") or item.get("from_country") or "未填写")
            counts[key] = counts.get(key, 0) + 1
        return counts


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
        id="TC-X-007",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="案件统计报表",
        stage_code=None,
        stage_name="案件统计报表",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_007_handler_verifies_case_report_summary() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-CASE-RPT",
        api=FakeApi(),
        db=FakeDb(),
    )

    handle_tc_x_007(runtime, _case())  # type: ignore[arg-type]

    assert [item["status"] for item in runtime.api.cases] == [
        "GRANTED",
        "TERMINATED",
        "PENDING",
    ]
    granted_case = runtime.api.cases[0]
    assert granted_case["pub_no"] == "PUB-RUN-X-CASE-RPT-007G"
    assert granted_case["pub_date"] == "2026-04-15"
    assert granted_case["grant_no"] == "GRANT-RUN-X-CASE-RPT-007G"
    assert granted_case["grant_date"] == "2026-05-01"
    assert granted_case["first_annuity_year"] == 1
    assert granted_case["valid_until"] == "2046-05-01"
    report_calls = [
        call
        for call in runtime.api.calls
        if call.get("path") == "/cases"
        and call["kwargs"].get("params", {}).get("client_id") == "client-1"
    ]
    assert len(report_calls) == 1


def test_tc_x_007_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_007, "_is_skeleton", False)
