from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import select

import app.api.deps as deps
from app.modules.masterdata.countries.models import Country


def _seed_country(
    session_factory,
    *,
    code: str,
    name_cn: str,
    name_en: str | None = None,
    is_active: bool = True,
) -> str:
    country_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Country(
                id=country_id,
                code=code,
                name_cn=name_cn,
                name_en=name_en,
                is_active=is_active,
            )
        )
        db.commit()
    return country_id


def test_create_country_returns_list_shape_and_defaults_active(client, auth_headers) -> None:
    code = f"CTY-{uuid4().hex[:8].upper()}"
    payload = {
        "code": code,
        "name_cn": "测试国家甲",
        "name_en": "Test Country A",
    }

    response = client.post("/api/v1/countries", json=payload, headers=auth_headers)

    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    assert set(body) == {"id", "code", "name_cn", "name_en", "is_active"}
    assert body["code"] == code
    assert body["name_cn"] == "测试国家甲"
    assert body["name_en"] == "Test Country A"
    assert body["is_active"] is True


@pytest.mark.parametrize(
    ("method", "path", "json_payload"),
    [
        ("post", "/api/v1/countries", {"code": "DENY-C1", "name_cn": "拒绝国家"}),
        (
            "put",
            "/api/v1/countries/deny-country",
            {"code": "DENY-C2", "name_cn": "拒绝国家二"},
        ),
        ("put", "/api/v1/countries/deny-country/deactivate", None),
    ],
)
def test_country_write_endpoints_require_country_write_permission(
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
    assert body["error"]["details"]["required_perm"] == "Country.Write"


@pytest.mark.parametrize(
    ("seed_field", "payload_field", "duplicate_error_code"),
    [
        ("code", "code", "COUNTRY_CODE_DUPLICATE"),
        ("name_cn", "name_cn", "COUNTRY_NAME_CN_DUPLICATE"),
    ],
)
def test_create_country_rejects_duplicate_unique_fields(
    client,
    auth_headers,
    session_factory,
    seed_field: str,
    payload_field: str,
    duplicate_error_code: str,
) -> None:
    unique = uuid4().hex[:8].upper()
    seed_kwargs = {
        "code": f"CTY-{unique}",
        "name_cn": f"测试国家{unique}",
        "name_en": f"Test Country {unique}",
    }
    seed_value = seed_kwargs[seed_field]
    _seed_country(session_factory, **seed_kwargs)

    create_payload = {
        "code": f"NEW-{unique}",
        "name_cn": f"新国家{unique}",
        "name_en": f"New Country {unique}",
    }
    create_payload[payload_field] = seed_value

    response = client.post("/api/v1/countries", json=create_payload, headers=auth_headers)

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == duplicate_error_code


def test_update_country_and_deactivate_country_roundtrip(
    client,
    auth_headers,
    session_factory,
) -> None:
    country_id = _seed_country(
        session_factory,
        code="CTY-OLD",
        name_cn="测试国家旧",
        name_en="Old Country",
    )
    _seed_country(
        session_factory,
        code="CTY-TAKEN",
        name_cn="测试国家已占用",
        name_en="Taken Country",
    )

    update_response = client.put(
        f"/api/v1/countries/{country_id}",
        json={
            "code": "CTY-NEW",
            "name_cn": "测试国家新",
            "name_en": "New Country",
            "is_active": False,
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    updated_body: dict[str, Any] = update_response.json()
    assert updated_body["code"] == "CTY-NEW"
    assert updated_body["name_cn"] == "测试国家新"
    assert updated_body["name_en"] == "New Country"
    assert updated_body["is_active"] is False

    deactivate_response = client.put(
        f"/api/v1/countries/{country_id}/deactivate",
        headers=auth_headers,
    )

    assert deactivate_response.status_code == 200
    assert deactivate_response.json() == {"status": "ok"}

    with session_factory() as db:
        country = db.execute(select(Country).where(Country.id == country_id)).scalar_one()
        assert country.is_active is False


def test_update_country_rejects_unique_conflicts(
    client,
    auth_headers,
    session_factory,
) -> None:
    country_id = _seed_country(
        session_factory,
        code="CTY-A",
        name_cn="测试国家A",
        name_en="Country A",
    )
    _seed_country(
        session_factory,
        code="CTY-B",
        name_cn="测试国家B",
        name_en="Country B",
    )

    code_conflict = client.put(
        f"/api/v1/countries/{country_id}",
        json={"code": "CTY-B"},
        headers=auth_headers,
    )
    assert code_conflict.status_code == 400
    assert code_conflict.json()["error"]["code"] == "COUNTRY_CODE_DUPLICATE"

    name_conflict = client.put(
        f"/api/v1/countries/{country_id}",
        json={"name_cn": "测试国家B"},
        headers=auth_headers,
    )
    assert name_conflict.status_code == 400
    assert name_conflict.json()["error"]["code"] == "COUNTRY_NAME_CN_DUPLICATE"

