from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import (
    handle_tc_w0_001,
    handle_tc_w0_007,
    handle_tc_w0_010,
    handle_tc_w0_013,
    handle_tc_w0_014,
    handle_tc_w0_cfg_013,
)


ROLE_PERMISSIONS = {
    "Admin": {
        "AdminUser.Create",
        "AdminUser.Edit",
        "AdminUser.Read",
        "Case.Create",
        "Case.Edit",
        "Case.EditLimited",
        "Billing.Edit",
        "DocTemplate.Create",
        "CommissionRule.Read",
        "Country.Read",
        "Department.Read",
        "DocTemplate.Read",
        "FeeRate.Read",
        "LetterHead.Read",
        "SystemParam.Read",
        "TaskTemplate.Read",
        "Template.Read",
        "FeeRate.Create",
    },
    "Formalities": {
        "Case.Create",
        "Case.Edit",
        "Doc.Create",
        "Task.Edit",
    },
    "Agent": {
        "Case.Read",
        "Case.EditLimited",
        "Doc.Read",
        "Task.Read",
    },
    "Finance": {
        "Billing.Edit",
        "Payment.Create",
        "PayList.Read",
        "PayList.Export",
    },
}


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
        self.users: dict[str, dict[str, Any]] = {
            "admin": {
                "id": "user-admin",
                "username": "admin",
                "password": "dummy-password",
                "roles": ["Admin"],
                "is_active": True,
            }
        }
        self.current_username: str | None = None

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        user = self.users.get(username)
        if user is None or user["password"] != password:
            raise AssertionError(f"Unexpected login for fake user: {username}")
        self.current_username = username
        return f"fake-token-{username}"

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append(
            {
                "method": "GET",
                "path": path,
                "kwargs": kwargs,
                "as_user": self.current_username,
            }
        )
        if path == "/admin/users":
            if not self._has_permission("AdminUser.Read"):
                return FakeResponse(
                    403,
                    {
                        "error": {
                            "details": {"required_perm": "AdminUser.Read"},
                        }
                    },
                )
            items = [
                {
                    "id": user["id"],
                    "username": user["username"],
                    "is_active": user["is_active"],
                    "roles": user["roles"],
                }
                for user in self.users.values()
            ]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 100, "total": len(items)}
            )
        if path == "/auth/me":
            user = self.users[self.current_username or ""]
            roles = list(user["roles"])
            permissions = sorted(
                {
                    permission
                    for role in roles
                    for permission in ROLE_PERMISSIONS.get(role, set())
                }
            )
            return FakeResponse(
                200,
                {
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "is_active": user["is_active"],
                    },
                    "roles": roles,
                    "permissions": permissions,
                },
            )
        if path == "/cases":
            if not self._has_permission("Case.Read"):
                return FakeResponse(
                    403, {"error": {"details": {"required_perm": "Case.Read"}}}
                )
            return FakeResponse(
                200, {"items": [], "page": 1, "page_size": 1, "total": 0}
            )
        config_permission_by_path = {
            "/system/config-readiness": "SystemParam.Read",
            "/fees/rates": "FeeRate.Read",
            "/commission/rules": "CommissionRule.Read",
            "/task-templates": "TaskTemplate.Read",
            "/doc-templates": "DocTemplate.Read",
            "/templates": "Template.Read",
            "/letterheads": "LetterHead.Read",
            "/countries": "Country.Read",
            "/departments": "Department.Read",
        }
        required_perm = config_permission_by_path.get(path)
        if required_perm is not None:
            if not self._has_permission(required_perm):
                return FakeResponse(
                    403, {"error": {"details": {"required_perm": required_perm}}}
                )
            return FakeResponse(
                200, {"items": [], "page": 1, "page_size": 1, "total": 0}
            )
        return FakeResponse(404, {"message": "not found"})

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path != "/admin/users":
            return FakeResponse(404, {"message": "not found"})
        payload = kwargs["json"]
        username = payload["username"]
        user = {
            "id": f"user-{len(self.users) + 1}",
            "username": username,
            "password": payload["password"],
            "roles": payload["roles"],
            "is_active": payload.get("is_active", True),
        }
        self.users[username] = user
        return FakeResponse(
            201,
            {
                "id": user["id"],
                "username": username,
                "is_active": user["is_active"],
                "roles": user["roles"],
            },
        )

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        prefix = "/admin/users/"
        if not path.startswith(prefix):
            return FakeResponse(404, {"message": "not found"})
        user_id = path.removeprefix(prefix)
        payload = kwargs["json"]
        for user in self.users.values():
            if user["id"] == user_id:
                user["roles"] = payload["roles"]
                user["is_active"] = payload["is_active"]
                return FakeResponse(
                    200,
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "is_active": user["is_active"],
                        "roles": user["roles"],
                    },
                )
        return FakeResponse(404, {"message": "not found"})

    def _has_permission(self, permission: str) -> bool:
        if self.current_username is None:
            return False
        roles = self.users[self.current_username]["roles"]
        return any(permission in ROLE_PERMISSIONS.get(role, set()) for role in roles)


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
        id="TC-W0-014",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy", "Unhappy"],
        topic="权限矩阵",
        stage_code=None,
        stage_name="权限矩阵",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM", "DS-U-AG-01", "DS-U-FI-01", "DS-U-FM-01", "DS-U-LMT-01"],
    )


def _cfg_case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-013",
        wave="W0",
        wave_title="W0 基础配置",
        context="RBAC 配置与保护端点",
        priority="P0",
        categories=["Security", "Happy", "Unhappy"],
        topic="权限-配置端点和菜单可见性",
        stage_code=None,
        stage_name="权限",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=["DS-U-ADM", "DS-U-FI-01", "DS-U-FM-01", "DS-U-LMT-01"],
    )


def test_tc_w0_014_handler_prepares_users_and_checks_permission_matrix() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-PERM",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_014(runtime, _case())  # type: ignore[arg-type]

    assert runtime.api.calls[0] == {
        "method": "LOGIN",
        "username": "admin",
        "password": "dummy-password",
    }

    post_users = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/admin/users"
    ]
    assert [payload["username"] for payload in post_users] == [
        "formalities-w0perm-RUN-W0-PERM",
        "agent-w0perm-RUN-W0-PERM",
        "finance-w0perm-RUN-W0-PERM",
        "limited-w0perm-RUN-W0-PERM",
    ]
    assert [payload["roles"] for payload in post_users] == [
        ["Formalities"],
        ["Agent"],
        ["Finance"],
        ["Agent"],
    ]
    assert all(payload["is_active"] is True for payload in post_users)

    login_users = [
        call["username"] for call in runtime.api.calls if call["method"] == "LOGIN"
    ]
    assert login_users[0] == "admin"
    for username in (
        "formalities-w0perm-RUN-W0-PERM",
        "agent-w0perm-RUN-W0-PERM",
        "finance-w0perm-RUN-W0-PERM",
        "limited-w0perm-RUN-W0-PERM",
    ):
        assert username in login_users

    auth_me_users = [
        call["as_user"]
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/auth/me"
    ]
    assert auth_me_users == [
        "admin",
        "formalities-w0perm-RUN-W0-PERM",
        "agent-w0perm-RUN-W0-PERM",
        "finance-w0perm-RUN-W0-PERM",
        "limited-w0perm-RUN-W0-PERM",
    ]

    admin_user_checks = [
        call["as_user"]
        for call in runtime.api.calls
        if call["method"] == "GET" and call["path"] == "/admin/users"
    ]
    assert "admin" in admin_user_checks
    assert "agent-w0perm-RUN-W0-PERM" in admin_user_checks
    assert "finance-w0perm-RUN-W0-PERM" in admin_user_checks
    assert runtime.db.rows == []


def test_tc_w0_cfg_013_handler_checks_config_endpoint_permissions() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-CFG-RBAC",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_013(runtime, _cfg_case())  # type: ignore[arg-type]

    login_users = [
        call["username"] for call in runtime.api.calls if call["method"] == "LOGIN"
    ]
    assert login_users == ["admin", "finance-w0perm-RUN-W0-CFG-RBAC"]

    config_checks = [
        call
        for call in runtime.api.calls
        if call["method"] == "GET"
        and call["path"]
        in {
            "/system/config-readiness",
            "/fees/rates",
            "/commission/rules",
            "/task-templates",
            "/doc-templates",
            "/templates",
            "/letterheads",
            "/countries",
            "/departments",
        }
    ]
    assert [call["as_user"] for call in config_checks] == [
        "finance-w0perm-RUN-W0-CFG-RBAC",
    ] * 9
    assert [call["path"] for call in config_checks] == [
        "/system/config-readiness",
        "/fees/rates",
        "/commission/rules",
        "/task-templates",
        "/doc-templates",
        "/templates",
        "/letterheads",
        "/countries",
        "/departments",
    ]
    assert runtime.db.rows == []


def test_tc_w0_014_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_014(runtime, _case())  # type: ignore[arg-type]

    assert ("t_user", {"username": "formalities-w0perm-RUN-W0-DB"}) in runtime.db.rows
    assert ("t_user", {"username": "agent-w0perm-RUN-W0-DB"}) in runtime.db.rows
    assert ("t_user", {"username": "finance-w0perm-RUN-W0-DB"}) in runtime.db.rows
    assert ("t_user", {"username": "limited-w0perm-RUN-W0-DB"}) in runtime.db.rows
    assert ("t_role", {"code": "Formalities"}) in runtime.db.rows
    assert ("t_role", {"code": "Agent"}) in runtime.db.rows
    assert ("t_role", {"code": "Finance"}) in runtime.db.rows
    assert ("t_role_perm", {"perm_code": "Case.EditLimited"}) in runtime.db.rows


def test_only_tc_w0_014_is_newly_unskeletoned() -> None:
    assert not getattr(handle_tc_w0_001, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_007, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_010, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_014, "_is_skeleton", False)
    assert not getattr(handle_tc_w0_cfg_013, "_is_skeleton", False)
    assert getattr(handle_tc_w0_013, "_is_skeleton", False) is True
