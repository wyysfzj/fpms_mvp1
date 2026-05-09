from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_010


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

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/templates":
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        template = {
            "id": f"tpl-{len(self.templates) + 1}",
            "created_at": "2026-05-09T00:00:00",
            **payload,
        }
        self.templates.append(template)
        return FakeResponse(201, template)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path != "/templates":
            return FakeResponse(404, {"message": "not found"})
        group = (kwargs.get("params") or {}).get("group")
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
        id="TC-W0-CFG-010",
        wave="W0",
        wave_title="W0 基础配置",
        context="模板文件源",
        priority="P1",
        categories=["Happy", "Unhappy"],
        topic="模板仓库-DOC_TEMPLATE 文件路径与渲染缺口",
        stage_code=None,
        stage_name="模板文件源",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-ADM",
            "DS-CFG-TEMPLATE-DOC-OA-CN",
            "DS-CFG-TEMPLATE-BILL-CN",
        ],
    )


def test_tc_w0_cfg_010_handler_creates_and_lists_template_sources() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-TPLSRC",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_010(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == ["/templates", "/templates"]

    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert payloads == [
        {
            "name": "OA_IN_RUN-W0-TPLSRC",
            "group": "DOC_TEMPLATE",
            "language": "zh-CN",
            "file_path": "templates/doc_oa_in_RUN-W0-TPLSRC.docx",
            "enabled": True,
        },
        {
            "name": "bill_standard_RUN-W0-TPLSRC",
            "group": "BILL_TEMPLATE",
            "language": "zh-CN",
            "file_path": "templates/bill_standard_RUN-W0-TPLSRC.docx",
            "enabled": True,
        },
    ]

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["path"] for call in get_calls] == ["/templates", "/templates"]
    assert [call["kwargs"]["params"]["group"] for call in get_calls] == [
        "DOC_TEMPLATE",
        "BILL_TEMPLATE",
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_010_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-TPLSRC-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_010(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_template",
            {
                "name": "OA_IN_RUN-W0-TPLSRC-DB",
                "group": "DOC_TEMPLATE",
                "file_path": "templates/doc_oa_in_RUN-W0-TPLSRC-DB.docx",
                "enabled": True,
            },
        ),
        (
            "t_template",
            {
                "name": "bill_standard_RUN-W0-TPLSRC-DB",
                "group": "BILL_TEMPLATE",
                "file_path": "templates/bill_standard_RUN-W0-TPLSRC-DB.docx",
                "enabled": True,
            },
        ),
    ]


def test_tc_w0_cfg_010_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-010"] is handle_tc_w0_cfg_010
    assert not getattr(handle_tc_w0_cfg_010, "_is_skeleton", False)
