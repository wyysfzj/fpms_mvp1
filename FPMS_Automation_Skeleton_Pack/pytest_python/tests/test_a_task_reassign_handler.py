from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_a import handle_tc_a_014


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
        self.clients: dict[str, dict[str, Any]] = {}
        self.applicants: dict[str, dict[str, Any]] = {}
        self.cases: dict[str, dict[str, Any]] = {}
        self.templates: list[dict[str, Any]] = []
        self.tasks: dict[str, dict[str, Any]] = {}
        self.logs: dict[str, list[dict[str, Any]]] = {}

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/clients":
            code = kwargs.get("params", {}).get("q")
            return FakeResponse(200, _list_response(self.clients.get(code)))
        if path == "/applicants":
            code = kwargs.get("params", {}).get("q")
            return FakeResponse(200, _list_response(self.applicants.get(code)))
        if path == "/cases":
            case_no = kwargs.get("params", {}).get("case_no")
            case = next(
                (item for item in self.cases.values() if item["case_no"] == case_no),
                None,
            )
            return FakeResponse(200, _list_response(case))
        if path == "/task-templates":
            return FakeResponse(200, self.templates)
        if path == "/tasks":
            case_id = kwargs.get("params", {}).get("case_id")
            items = [
                task
                for task in self.tasks.values()
                if task.get("case_id") == case_id and task.get("status") == "OPEN"
            ]
            return FakeResponse(200, {"items": items, "total": len(items)})
        if path.startswith("/tasks/") and path.endswith("/logs"):
            task_id = path.split("/")[-2]
            return FakeResponse(200, self.logs.get(task_id, []))
        if path.startswith("/tasks/"):
            task_id = path.rsplit("/", 1)[-1]
            return FakeResponse(200, self.tasks[task_id])
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path == "/clients":
            client = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients[payload["client_code"]] = client
            return FakeResponse(201, client)
        if path == "/applicants":
            applicant = {"id": f"applicant-{len(self.applicants) + 1}", **payload}
            self.applicants[payload["code"]] = applicant
            return FakeResponse(201, applicant)
        if path == "/cases":
            case = {
                "id": f"case-{len(self.cases) + 1}",
                "status": "NOT_FILED",
                **payload,
            }
            self.cases[case["id"]] = case
            return FakeResponse(201, case)
        if path == "/task-templates":
            template = {"id": f"template-{len(self.templates) + 1}", **payload}
            self.templates.append(template)
            return FakeResponse(201, template)
        if path == "/cases/batch-filing/submit":
            return self._submit_batch(payload)
        return FakeResponse(404, {"message": "not found"})

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        payload = kwargs["json"]
        if path.startswith("/task-templates/"):
            template_id = path.rsplit("/", 1)[-1]
            template = next(
                item for item in self.templates if item["id"] == template_id
            )
            template.update(payload)
            return FakeResponse(200, template)
        if path.startswith("/cases/"):
            case_id = path.rsplit("/", 1)[-1]
            self.cases[case_id].update(payload)
            return FakeResponse(200, self.cases[case_id])
        return FakeResponse(404, {"message": "not found"})

    def _submit_batch(self, payload: dict[str, Any]) -> FakeResponse:
        template = next(
            item for item in self.templates if item["code"] == "APPLY_FEE_LIMIT"
        )
        updated_case_ids = payload["selected_case_ids"]
        created_task_ids = []
        for case_id in updated_case_ids:
            case = self.cases[case_id]
            case["status"] = "WAITING_RECEIPT"
            deadline_base = template["deadline_base"]
            base_date = (
                case["filing_date"]
                if deadline_base == "FILING_DATE"
                else payload["submitted_date"]
            )
            task = _build_task(
                task_id=f"task-{len(self.tasks) + 1}",
                case_id=case_id,
                base_date=base_date,
                template=template,
            )
            self.tasks[task["id"]] = task
            self.logs[task["id"]] = [{"action": "AUTO_CREATE"}]
            created_task_ids.append(task["id"])
        return FakeResponse(
            200,
            {
                "success_count": len(updated_case_ids),
                "failure_count": 0,
                "updated_case_ids": updated_case_ids,
                "created_task_ids": created_task_ids,
            },
        )


class FakeDb:
    def __init__(self, enabled: bool = False) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self._enabled = enabled

    def enabled(self) -> bool:
        return self._enabled

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((table, where))
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
        id="TC-A-014",
        wave="A",
        wave_title="A 新案申请",
        context="",
        priority="P1",
        categories=["Happy", "Boundary"],
        topic="A3 时限基准与提醒",
        stage_code="A3",
        stage_name="时限基准与提醒",
        coverage_ids=["FR-DL-01", "FR-DL-02", "V-TM-03", "V-TM-04"],
        requirement_ids=["FR-DL-01", "FR-DL-02"],
        validation_ids=["V-TM-03", "V-TM-04"],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
        dynamic_refs=[],
    )


def _list_response(record: dict[str, Any] | None) -> dict[str, Any]:
    items = [] if record is None else [record]
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _build_task(
    *, task_id: str, case_id: str, base_date: str, template: dict[str, Any]
) -> dict[str, Any]:
    base = date.fromisoformat(base_date)
    due = base + timedelta(days=template["add_days"])
    internal = due - timedelta(days=template["inner_offset_days"])
    remind_base = internal if template["remind_base"] == "INNER" else due
    remind_offsets = (
        template["remind_1_offset_days"],
        template["remind_2_offset_days"],
        template["remind_3_offset_days"],
    )
    return {
        "id": task_id,
        "case_id": case_id,
        "title": "申请费时限",
        "base_date": base.isoformat(),
        "due_date": due.isoformat(),
        "internal_due_date": internal.isoformat(),
        "remind1": (remind_base - timedelta(days=remind_offsets[0])).isoformat(),
        "remind2": (remind_base - timedelta(days=remind_offsets[1])).isoformat(),
        "remind3": (remind_base - timedelta(days=remind_offsets[2])).isoformat(),
        "daily_remind_from": (
            remind_base - timedelta(days=max(remind_offsets))
        ).isoformat(),
        "daily_remind": True,
        "status": "OPEN",
    }


def test_tc_a_014_checks_case_event_and_filing_date_task_schedules() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-TASK-BASE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_a_014(runtime, _case())  # type: ignore[arg-type]

    template_updates = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "PUT" and call["path"].startswith("/task-templates/")
    ]
    assert template_updates[0]["deadline_base"] == "FILING_DATE"
    assert template_updates[0]["remind_base"] == "INNER"

    created_tasks = list(runtime.api.tasks.values())
    assert created_tasks[0]["base_date"] == "2026-04-05"
    assert created_tasks[0]["daily_remind_from"] == "2026-04-19"
    assert created_tasks[1]["base_date"] == "2026-03-08"
    assert created_tasks[1]["daily_remind_from"] == "2026-03-17"


def test_tc_a_014_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="pw",
        run_id="RUN-A-TASK-BASE-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_a_014(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.calls == [
        ("t_task", {"id": "task-2", "status": "OPEN"}),
    ]
