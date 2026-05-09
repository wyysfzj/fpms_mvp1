from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import HANDLERS, handle_tc_w0_cfg_009


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
        self.cases: list[dict[str, Any]] = []
        self.task_templates: list[dict[str, Any]] = []
        self.doc_templates: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/cases":
            item = {"id": f"case-{len(self.cases) + 1}", **payload}
            self.cases.append(item)
            return FakeResponse(201, item)
        if path == "/task-templates":
            item = {"id": f"task-{len(self.task_templates) + 1}", **payload}
            self.task_templates.append(item)
            return FakeResponse(201, item)
        if path == "/doc-templates":
            item = {"id": f"doc-template-{len(self.doc_templates) + 1}", **payload}
            self.doc_templates.append(item)
            return FakeResponse(201, item)
        if path == "/documents/impact-preview":
            case_id = payload["case_id"]
            template = self.doc_templates[-1]
            return FakeResponse(
                200,
                {
                    "case_id": case_id,
                    "case_no": self.cases[-1]["case_no"],
                    "template_code": template["code"],
                    "status_impacts": [
                        {
                            "kind": "CASE_STATUS",
                            "title": "案件状态影响",
                            "effect": template["status_effect"],
                        }
                    ],
                    "deadline_impacts": [
                        {
                            "kind": "DEADLINE_TEMPLATE",
                            "title": "期限模板影响",
                            "effect": template["deadline_template_code"],
                        }
                    ],
                    "task_impacts": [
                        {
                            "kind": "AUTO_TASK",
                            "title": "任务影响",
                            "effect": template["deadline_template_code"],
                        }
                    ],
                    "fee_impacts": [
                        {
                            "kind": "FEE_DRAFT",
                            "title": "费用影响",
                            "effect": template["fee_draft_type"],
                        }
                    ],
                    "file_status_impacts": [
                        {
                            "kind": "NEED_REPLY",
                            "title": "文件状态影响",
                            "effect": "NEED_REPLY",
                        }
                    ],
                    "confirmation_required": True,
                    "confirmation_items": [
                        "案件状态将受模板影响",
                        "期限任务将受模板影响",
                        "费用草稿将受模板影响",
                    ],
                    "risk_tips": [],
                },
            )
        return FakeResponse(404, {"message": "not found"})

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/task-templates":
            return FakeResponse(200, self.task_templates)
        if path == "/doc-templates":
            q = (kwargs.get("params") or {}).get("q")
            items = [item for item in self.doc_templates if item["code"] == q]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
            )
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
        id="TC-W0-CFG-009",
        wave="W0",
        wave_title="W0 基础配置",
        context="文件模板默认值、状态和费用影响",
        priority="P0",
        categories=["Happy"],
        topic="文件模板-状态影响、回复链、费用草单预览",
        stage_code=None,
        stage_name="业务参数-文档模板",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-ADM",
            "DS-CFG-DOC-OA-IN",
            "DS-CFG-TASK-OA-REPLY",
            "DS-CFG-CASE-NORMAL-INV",
        ],
    )


def test_tc_w0_cfg_009_handler_calls_document_impact_preview() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-IMPACT",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_009(runtime, _case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/cases",
        "/task-templates",
        "/doc-templates",
        "/documents/impact-preview",
    ]
    case_payload = post_calls[0]["kwargs"]["json"]
    assert case_payload["case_no"] == "CASE-CFG-RUN-W0-IMPACT-001"
    assert "agent_splits" not in case_payload
    assert "primary_agent_id" not in case_payload

    doc_payload = post_calls[2]["kwargs"]["json"]
    assert doc_payload["code"] == "OA_IN_RUN-W0-IMPACT"
    assert doc_payload["status_effect"] == "OA1"
    assert doc_payload["fee_draft_type"] == "OA_SERVICE"

    preview_payload = post_calls[3]["kwargs"]["json"]
    assert preview_payload["case_id"] == "case-1"
    assert preview_payload["doc_template_id"] == "doc-template-1"
    assert preview_payload["direction"] == "IN"
    assert runtime.db.rows == []


def test_tc_w0_cfg_009_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-IMPACT-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_009(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_case", {"case_no": "CASE-CFG-RUN-W0-IMPACT-DB-001"}),
        (
            "t_doc_template",
            {"code": "OA_IN_RUN-W0-IMPACT-DB", "fee_draft_type": "OA_SERVICE"},
        ),
    ]


def test_tc_w0_cfg_009_is_registered_as_real_handler() -> None:
    assert HANDLERS["TC-W0-CFG-009"] is handle_tc_w0_cfg_009
    assert not getattr(handle_tc_w0_cfg_009, "_is_skeleton", False)
