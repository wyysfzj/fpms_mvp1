from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import select

import app.api.deps as deps
from app.modules.auth.models import T_Role, T_RolePerm
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.countries.models import Country


@pytest.mark.parametrize(
    ("path", "required_perm"),
    [
        ("/api/v1/applicants", "Applicant.Read"),
        ("/api/v1/countries", "Country.Read"),
    ],
)
def test_masterdata_prereq_list_contract(
    client,
    auth_headers,
    monkeypatch,
    session_factory,
    path: str,
    required_perm: str,
) -> None:
    code = uuid4().hex[:10].upper()
    with session_factory() as db:
        if path.endswith("/applicants"):
            db.add(
                Applicant(
                    code=f"APP-{code}",
                    name_cn="申请人甲",
                    name_en="Applicant A",
                    is_active=True,
                )
            )
        else:
            db.add(
                Country(
                    code=f"CTY-{code}",
                    name_cn="国家甲",
                    name_en="Country A",
                    is_active=True,
                )
            )
        db.commit()

    response = client.get(path, headers=auth_headers)
    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    for key in ("items", "page", "page_size", "total"):
        assert key in payload

    items = payload["items"]
    assert isinstance(items, list)
    seeded_code = f"APP-{code}" if path.endswith("/applicants") else f"CTY-{code}"
    seeded_items = [item for item in items if item["code"] == seeded_code]
    assert seeded_items
    expected_fields = {"id", "code", "name_cn", "name_en", "is_active"}
    if path.endswith("/applicants"):
        expected_fields.add("applicant_type")
        expected_fields.add("total_power_of_attorney_no")
    assert expected_fields == set(seeded_items[0])

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    forbidden = client.get(path, headers=auth_headers)
    assert forbidden.status_code == 403
    body = forbidden.json()
    assert body["error"]["details"]["required_perm"] == required_perm


def test_applicant_and_country_contract_shapes_match(client, auth_headers) -> None:
    applicant_payload = client.get("/api/v1/applicants", headers=auth_headers).json()
    country_payload = client.get("/api/v1/countries", headers=auth_headers).json()

    applicant_items = applicant_payload["items"]
    country_items = country_payload["items"]

    if applicant_items and country_items:
        assert set(applicant_items[0]) == set(country_items[0]) | {
            "applicant_type",
            "total_power_of_attorney_no",
        }


def test_masterdata_permission_namespaces_are_frozen(session_factory) -> None:
    with session_factory() as db:
        admin_role = db.execute(select(T_Role).where(T_Role.code == "Admin")).scalar_one()
        perm_codes = {
            row[0]
            for row in db.execute(
                select(T_RolePerm.perm_code).where(T_RolePerm.role_id == admin_role.id)
            ).all()
        }

    assert {
        "Applicant.Read",
        "Applicant.Write",
        "Country.Read",
        "Country.Write",
        "Department.Read",
        "Department.Write",
    }.issubset(perm_codes)
    assert "Applicant.Create" not in perm_codes
    assert "Applicant.Edit" not in perm_codes
    assert "Applicant.Action" not in perm_codes
    assert "Country.Create" not in perm_codes
    assert "Country.Edit" not in perm_codes
    assert "Country.Action" not in perm_codes
    assert "Department.Create" not in perm_codes
    assert "Department.Edit" not in perm_codes
    assert "Department.Action" not in perm_codes
