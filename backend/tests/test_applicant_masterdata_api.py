from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import select

import app.api.deps as deps
from app.modules.annuity.models import PayList  # noqa: F401
from app.modules.masterdata.applicants.models import Applicant


def _seed_applicant(
    session_factory,
    *,
    code: str,
    name_cn: str,
    name_en: str | None = None,
    applicant_type: str = "ENTITY",
    is_active: bool = True,
) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=code,
                name_cn=name_cn,
                name_en=name_en,
                applicant_type=applicant_type,
                is_active=is_active,
            )
        )
        db.commit()
    return applicant_id


def test_create_applicant_returns_object_shape_and_defaults_active(
    client,
    auth_headers,
) -> None:
    code = f"APP-{uuid4().hex[:8].upper()}"
    payload = {
        "code": code,
        "name_cn": "测试申请人甲",
        "name_en": "Applicant A",
    }

    response = client.post("/api/v1/applicants", json=payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "id",
        "code",
        "name_cn",
        "name_en",
        "total_power_of_attorney_no",
        "is_active",
        "applicant_type",
    }
    assert body["code"] == code
    assert body["name_cn"] == "测试申请人甲"
    assert body["name_en"] == "Applicant A"
    assert body["total_power_of_attorney_no"] is None
    assert body["is_active"] is True
    assert body["applicant_type"] == "ENTITY"


def test_create_applicant_accepts_explicit_applicant_type(client, auth_headers) -> None:
    code = f"APP-{uuid4().hex[:8].upper()}"
    payload = {
        "code": code,
        "name_cn": "测试申请人乙",
        "name_en": "Applicant B",
        "applicant_type": "INDIVIDUAL",
    }

    response = client.post("/api/v1/applicants", json=payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == code
    assert body["applicant_type"] == "INDIVIDUAL"


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        ("post", "/api/v1/applicants", {"code": "DENY-A1", "name_cn": "拒绝申请人一"}),
        (
            "put",
            "/api/v1/applicants/deny-applicant",
            {"code": "DENY-A2", "name_cn": "拒绝申请人二"},
        ),
        ("put", "/api/v1/applicants/deny-applicant/deactivate", None),
    ],
)
def test_applicant_write_endpoints_require_applicant_write_permission(
    client,
    auth_headers,
    monkeypatch,
    method: str,
    path: str,
    json_payload: dict[str, Any] | None,
) -> None:
    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)

    response = getattr(client, method)(path, json=json_payload, headers=auth_headers)

    assert response.status_code == 403
    body = response.json()
    assert body["error"]["details"]["required_perm"] == "Applicant.Write"


def test_update_applicant_and_deactivate_applicant_roundtrip(
    client,
    auth_headers,
    session_factory,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        code="APP-OLD",
        name_cn="测试申请人旧",
        name_en="Old Applicant",
    )
    _seed_applicant(
        session_factory,
        code="APP-TAKEN",
        name_cn="测试申请人已占用",
        name_en="Taken Applicant",
    )

    update_response = client.put(
        f"/api/v1/applicants/{applicant_id}",
        json={
            "code": "APP-NEW",
            "name_cn": "测试申请人新",
            "name_en": "New Applicant",
            "applicant_type": "INDIVIDUAL",
            "is_active": False,
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    updated_body: dict[str, Any] = update_response.json()
    assert updated_body["code"] == "APP-NEW"
    assert updated_body["name_cn"] == "测试申请人新"
    assert updated_body["name_en"] == "New Applicant"
    assert updated_body["applicant_type"] == "INDIVIDUAL"
    assert updated_body["is_active"] is False

    deactivate_response = client.put(
        f"/api/v1/applicants/{applicant_id}/deactivate",
        headers=auth_headers,
    )

    assert deactivate_response.status_code == 200
    assert deactivate_response.json() == {"status": "ok"}

    with session_factory() as db:
        applicant = db.execute(select(Applicant).where(Applicant.id == applicant_id)).scalar_one()
        assert applicant.is_active is False


@pytest.mark.parametrize(
    ("seed_field", "payload_field", "duplicate_error_code"),
    [
        ("code", "code", "APPLICANT_CODE_DUPLICATE"),
        ("name_cn", "name_cn", "APPLICANT_NAME_CN_DUPLICATE"),
    ],
)
def test_create_applicant_rejects_duplicate_unique_fields(
    client,
    auth_headers,
    session_factory,
    seed_field: str,
    payload_field: str,
    duplicate_error_code: str,
) -> None:
    unique = uuid4().hex[:8].upper()
    seed_kwargs = {
        "code": f"APP-{unique}",
        "name_cn": f"测试申请人{unique}",
        "name_en": f"Applicant {unique}",
    }
    seed_value = seed_kwargs[seed_field]
    _seed_applicant(session_factory, **seed_kwargs)

    create_payload = {
        "code": f"NEW-{unique}",
        "name_cn": f"新申请人{unique}",
        "name_en": f"New Applicant {unique}",
    }
    create_payload[payload_field] = seed_value

    response = client.post("/api/v1/applicants", json=create_payload, headers=auth_headers)

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == duplicate_error_code


def test_update_applicant_rejects_unique_conflicts(
    client,
    auth_headers,
    session_factory,
) -> None:
    applicant_id = _seed_applicant(
        session_factory,
        code="APP-A",
        name_cn="测试申请人A",
        name_en="Applicant A",
    )
    _seed_applicant(
        session_factory,
        code="APP-B",
        name_cn="测试申请人B",
        name_en="Applicant B",
    )

    code_conflict = client.put(
        f"/api/v1/applicants/{applicant_id}",
        json={"code": "APP-B"},
        headers=auth_headers,
    )
    assert code_conflict.status_code == 400
    assert code_conflict.json()["error"]["code"] == "APPLICANT_CODE_DUPLICATE"

    name_conflict = client.put(
        f"/api/v1/applicants/{applicant_id}",
        json={"name_cn": "测试申请人B"},
        headers=auth_headers,
    )
    assert name_conflict.status_code == 400
    assert name_conflict.json()["error"]["code"] == "APPLICANT_NAME_CN_DUPLICATE"
