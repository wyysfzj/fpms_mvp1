from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_x import handle_tc_x_012, handle_tc_x_013


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
        self.tasks: list[dict[str, Any]] = []
        self.logs: dict[str, list[dict[str, Any]]] = {}

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        params = kwargs.get("params") or {}
        if path == "/auth/me":
            return FakeResponse(200, {"user": {"id": "user-1", "username": "admin"}})
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
        if path == "/tasks":
            case_id = params.get("case_id")
            status = params.get("status")
            items = [
                item
                for item in self.tasks
                if item.get("case_id") == case_id
                and (status is None or item.get("status") == status)
            ]
            return self._list_response(items)
        if path.endswith("/logs") and path.startswith("/tasks/"):
            task_id = path.split("/")[2]
            return FakeResponse(200, self.logs.get(task_id, []))
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
        if path == "/tasks":
            item = {
                "id": f"task-{len(self.tasks) + 1}",
                "status": "OPEN",
                **payload,
            }
            self.tasks.append(item)
            self._append_log(item["id"], "CREATE", None, "OPEN", payload.get("remark"))
            return FakeResponse(201, item)
        if path.startswith("/tasks/"):
            task_id, action = path.split("/")[2:4]
            task = self._task(task_id)
            if action == "assign":
                task["worker_id"] = payload.get("worker_id")
                task["supervisor_id"] = payload.get("supervisor_id")
                self._append_log(
                    task_id,
                    "ASSIGN",
                    task["status"],
                    task["status"],
                    payload.get("remark"),
                )
                return FakeResponse(200, {"status": "ok"})
            if action == "close":
                from_status = task["status"]
                task["status"] = "DONE"
                self._append_log(
                    task_id, "CLOSE", from_status, "DONE", payload.get("remark")
                )
                return FakeResponse(200, {"status": "ok"})
            if action == "reopen":
                from_status = task["status"]
                task["status"] = "OPEN"
                self._append_log(
                    task_id, "REOPEN", from_status, "OPEN", payload.get("remark")
                )
                return FakeResponse(200, {"status": "ok"})
            if action == "cancel":
                from_status = task["status"]
                task["status"] = "CANCELLED"
                self._append_log(
                    task_id, "CANCEL", from_status, "CANCELLED", payload.get("remark")
                )
                return FakeResponse(200, {"status": "ok"})
        return FakeResponse(404, {"message": "not found"})

    def _list_response(self, items: list[dict[str, Any]]) -> FakeResponse:
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def _task(self, task_id: str) -> dict[str, Any]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        raise AssertionError(f"Task not found: {task_id}")

    def _append_log(
        self,
        task_id: str,
        action: str,
        from_status: str | None,
        to_status: str | None,
        remark: str | None,
    ) -> None:
        rows = self.logs.setdefault(task_id, [])
        rows.append(
            {
                "id": f"log-{len(rows) + 1}",
                "task_id": task_id,
                "action": action,
                "from_status": from_status,
                "to_status": to_status,
                "remark": remark,
                "created_at": "2026-05-09T00:00:00",
            }
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
        id="TC-X-012",
        wave="X",
        wave_title="X 查询统计与辅助功能",
        context="",
        priority="P1",
        categories=["Happy"],
        topic="任务操作日志",
        stage_code=None,
        stage_name="任务操作日志",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[],
    )


def test_tc_x_012_handler_records_current_task_log_actions() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-LOG",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_x_012(runtime, _case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == [
        "/clients",
        "/applicants",
        "/cases",
        "/tasks",
        "/tasks/task-1/assign",
        "/tasks/task-1/close",
        "/tasks/task-1/reopen",
        "/tasks/task-1/cancel",
    ]
    assert [log["action"] for log in runtime.api.logs["task-1"]] == [
        "CREATE",
        "ASSIGN",
        "CLOSE",
        "REOPEN",
        "CANCEL",
    ]
    assert runtime.api.tasks[0]["status"] == "CANCELLED"
    assert runtime.db.rows == []


def test_tc_x_012_handler_runs_db_assert_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-X-LOG-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_x_012(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [("t_task_log", {"task_id": "task-1"})]


def test_tc_x_012_is_registered_as_real_handler() -> None:
    assert not getattr(handle_tc_x_012, "_is_skeleton", False)
    assert getattr(handle_tc_x_013, "_is_skeleton", False) is True
