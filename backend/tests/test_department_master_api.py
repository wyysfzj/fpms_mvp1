from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import select

import app.api.deps as deps
from app.modules.auth.models import T_Role, T_RolePerm
from app.modules.masterdata.departments.models import Department


def _seed_department(
    session_factory,
    *,
    department_code: str,
    name_cn: str,
    is_active: bool = True,
) -> str:
    department_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Department(
                id=department_id,
                department_code=department_code,
                name_cn=name_cn,
                is_active=is_active,
            )
        )
        db.commit()
    return department_id


def test_department_list_create_update_deactivate_roundtrip(
    client,
    auth_headers,
    session_factory,
) -> None:
    created = client.post(
        "/api/v1/departments",
        headers=auth_headers,
        json={"department_code": f"DEPT-{uuid4().hex[:8].upper()}", "name_cn": "流程部门"},
    )
    assert created.status_code == 201, created.text
    created_body: dict[str, Any] = created.json()
    assert set(created_body) == {"id", "department_code", "name_cn", "is_active"}
    department_id = created_body["id"]

    listed = client.get("/api/v1/departments", headers=auth_headers)
    assert listed.status_code == 200, listed.text
    payload = listed.json()
    assert {"items", "page", "page_size", "total"} == set(payload)
    assert any(item["id"] == department_id for item in payload["items"])

    updated = client.put(
        f"/api/v1/departments/{department_id}",
        headers=auth_headers,
        json={"department_code": "DEPT-UPDATED", "name_cn": "更新部门", "is_active": False},
    )
    assert updated.status_code == 200, updated.text
    updated_body = updated.json()
    assert updated_body["department_code"] == "DEPT-UPDATED"
    assert updated_body["name_cn"] == "更新部门"
    assert updated_body["is_active"] is False

    deactivated = client.put(
        f"/api/v1/departments/{department_id}/deactivate",
        headers=auth_headers,
    )
    assert deactivated.status_code == 200, deactivated.text
    assert deactivated.json() == {"status": "ok"}

    with session_factory() as db:
        department = db.execute(
            select(Department).where(Department.id == department_id)
        ).scalar_one()
        assert department.is_active is False


@pytest.mark.parametrize(
    ("method", "path", "json_payload", "required_perm"),
    [
        ("get", "/api/v1/departments", None, "Department.Read"),
        (
            "post",
            "/api/v1/departments",
            {"department_code": "DENY-DEPT", "name_cn": "拒绝部门"},
            "Department.Write",
        ),
        (
            "put",
            "/api/v1/departments/deny-dept",
            {"name_cn": "拒绝更新部门"},
            "Department.Write",
        ),
        ("put", "/api/v1/departments/deny-dept/deactivate", None, "Department.Write"),
    ],
)
def test_department_permissions_are_enforced(
    client,
    auth_headers,
    monkeypatch,
    method: str,
    path: str,
    json_payload: dict[str, Any] | None,
    required_perm: str,
) -> None:
    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    request_kwargs: dict[str, Any] = {"headers": auth_headers}
    if json_payload is not None:
        request_kwargs["json"] = json_payload

    response = getattr(client, method)(path, **request_kwargs)

    assert response.status_code == 403
    body = response.json()
    assert body["error"]["details"]["required_perm"] == required_perm


def test_department_rejects_duplicate_code_and_name(
    client,
    auth_headers,
    session_factory,
) -> None:
    unique = uuid4().hex[:8].upper()
    _seed_department(
        session_factory,
        department_code=f"DEPT-{unique}",
        name_cn=f"部门{unique}",
    )

    duplicate_code = client.post(
        "/api/v1/departments",
        headers=auth_headers,
        json={"department_code": f"DEPT-{unique}", "name_cn": f"新部门{unique}"},
    )
    assert duplicate_code.status_code == 400
    assert duplicate_code.json()["error"]["code"] == "DEPARTMENT_CODE_DUPLICATE"

    duplicate_name = client.post(
        "/api/v1/departments",
        headers=auth_headers,
        json={"department_code": f"DEPT-NEW-{unique}", "name_cn": f"部门{unique}"},
    )
    assert duplicate_name.status_code == 400
    assert duplicate_name.json()["error"]["code"] == "DEPARTMENT_NAME_DUPLICATE"


def test_department_permissions_seeded_for_admin(session_factory) -> None:
    with session_factory() as db:
        admin_role = db.execute(select(T_Role).where(T_Role.code == "Admin")).scalar_one()
        perm_codes = {
            row[0]
            for row in db.execute(
                select(T_RolePerm.perm_code).where(T_RolePerm.role_id == admin_role.id)
            ).all()
        }

    assert {"Department.Read", "Department.Write"}.issubset(perm_codes)
