from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import handle_tc_w0_011, handle_tc_w0_012


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
        self.templates: list[dict[str, Any]] = []
        self.letterheads: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/templates":
            template = {
                "id": f"tpl-{len(self.templates) + 1}",
                "created_at": "2026-05-09T00:00:00",
                **payload,
            }
            self.templates.append(template)
            return FakeResponse(201, template)

        if path == "/letterheads":
            if payload.get("is_default"):
                for item in self.letterheads:
                    if item.get("locale") == payload.get("locale"):
                        item["is_default"] = False
            item = {
                "id": len(self.letterheads) + 1,
                "created_at": "2026-05-09T00:00:00",
                "updated_at": "2026-05-09T00:00:00",
                **payload,
            }
            self.letterheads.append(item)
            return FakeResponse(201, item)

        return FakeResponse(404, {"message": "not found"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        params = kwargs.get("params") or {}
        if path == "/templates":
            group = params.get("group")
            items = [
                {
                    "id": template["id"],
                    "name": template["name"],
                    "group": template["group"],
                    "language": template["language"],
                    "enabled": template["enabled"],
                }
                for template in self.templates
                if template["group"] == group
            ]
            return FakeResponse(
                200,
                {"items": items, "page": 1, "page_size": 20, "total": len(items)},
            )

        if path == "/letterheads":
            locale = params.get("locale")
            items = [item for item in self.letterheads if item.get("locale") == locale]
            return FakeResponse(200, items)

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
        id="TC-W0-012",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="文档模板与信头",
        stage_code=None,
        stage_name="文档模板与信头",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM"],
    )


def test_tc_w0_012_handler_configures_template_sources_and_letterheads() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-TLH",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_012(runtime, _case())  # type: ignore[arg-type]

    login_calls = [call for call in runtime.api.calls if call["method"] == "LOGIN"]
    assert login_calls == [
        {"method": "LOGIN", "username": "admin", "password": "dummy-password"},
        {"method": "LOGIN", "username": "admin", "password": "dummy-password"},
    ]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/templates",
        "/templates",
        "/letterheads",
        "/letterheads",
        "/letterheads",
    ]
    assert [call["kwargs"]["json"]["name"] for call in post_calls[:2]] == [
        "OA_IN_RUN-W0-TLH",
        "bill_standard_RUN-W0-TLH",
    ]
    assert [call["kwargs"]["json"]["name"] for call in post_calls[2:]] == [
        "中文默认信头-RUN-W0-TLH",
        "English Default Letterhead-RUN-W0-TLH",
        "中文默认信头-RUN-W0-TLH-替换",
    ]

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == [
        "/templates",
        "/templates",
        "/letterheads",
    ]
    assert runtime.db.rows == []


def test_tc_w0_012_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-TLH-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_012(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_template",
            {
                "name": "OA_IN_RUN-W0-TLH-DB",
                "group": "DOC_TEMPLATE",
                "file_path": "templates/doc_oa_in_RUN-W0-TLH-DB.docx",
                "enabled": True,
            },
        ),
        (
            "t_template",
            {
                "name": "bill_standard_RUN-W0-TLH-DB",
                "group": "BILL_TEMPLATE",
                "file_path": "templates/bill_standard_RUN-W0-TLH-DB.docx",
                "enabled": True,
            },
        ),
        (
            "t_letter_head",
            {"name": "中文默认信头-RUN-W0-TLH-DB", "is_default": False},
        ),
        (
            "t_letter_head",
            {"name": "中文默认信头-RUN-W0-TLH-DB-替换", "is_default": True},
        ),
        (
            "t_letter_head",
            {
                "name": "English Default Letterhead-RUN-W0-TLH-DB",
                "is_default": True,
            },
        ),
    ]


def test_tc_w0_012_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_w0_012, "_is_skeleton", False)
    assert getattr(handle_tc_w0_011, "_is_skeleton", False) is True
