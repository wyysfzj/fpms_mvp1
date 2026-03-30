from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import select

import app.api.deps as deps
from app.modules.auth.models import T_Role, T_RolePerm
from app.modules.rbac.service import ROLE_PERMISSIONS

GRANT_FEE_PATH = "/api/v1/grant-fee-tasks"


@pytest.mark.parametrize(
    ("method", "required_perm"),
    [
        ("get", "GrantFeeTask.Read"),
        ("post", "GrantFeeTask.Write"),
    ],
)
def test_grant_fee_module_requires_frozen_permissions(
    client,
    auth_headers,
    monkeypatch,
    method: str,
    required_perm: str,
) -> None:
    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = getattr(client, method)(GRANT_FEE_PATH, headers=auth_headers)

    assert response.status_code == 403
    body: dict[str, Any] = response.json()
    assert body["error"]["details"]["required_perm"] == required_perm


def test_grant_fee_module_contract_shape_and_rbac_freeze(
    client,
    auth_headers,
    session_factory,
) -> None:
    response = client.get(GRANT_FEE_PATH, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "module": "grant_fees",
        "permission_namespace": "GrantFeeTask",
        "permission_codes": ["GrantFeeTask.Read", "GrantFeeTask.Write"],
        "status": "ok",
    }

    write_response = client.post(GRANT_FEE_PATH, headers=auth_headers)
    assert write_response.status_code == 200
    assert write_response.json() == body

    with session_factory() as db:
        admin_role = db.execute(select(T_Role).where(T_Role.code == "Admin")).scalar_one()
        perm_codes = {
            row[0]
            for row in db.execute(
                select(T_RolePerm.perm_code).where(T_RolePerm.role_id == admin_role.id)
            ).all()
        }

    grant_fee_perm_codes = {
        code for perm_list in ROLE_PERMISSIONS.values() for code in perm_list if code.startswith("GrantFeeTask.")
    }
    assert grant_fee_perm_codes == {"GrantFeeTask.Read", "GrantFeeTask.Write"}
    assert {code for code in perm_codes if code.startswith("GrantFeeTask.")} == {
        "GrantFeeTask.Read",
        "GrantFeeTask.Write",
    }
