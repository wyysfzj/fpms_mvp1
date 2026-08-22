"""Tests for case agent split contract (FRCOM03-BE-CASE-01)."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.security import get_password_hash
from app.db.base import Base
from app.main import create_app
from app.models import *  # noqa: F401, F403 - register ORM models for create_all
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.rbac.service import seed_default_roles_perms


@pytest.fixture
def session_factory(tmp_path) -> sessionmaker:
    db_path = tmp_path / "case_agent_split.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    with session_maker() as db:
        seed_default_roles_perms(db)
        admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
        assert admin_role is not None, "Admin role should exist after seeding"
        admin_user = T_User(
            id=str(uuid4()),
            username="admin",
            display_name="Administrator",
            password_hash=get_password_hash("admin123"),
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        db.add(T_UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db.commit()

    try:
        yield session_maker
    finally:
        engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker) -> TestClient:
    app = create_app()

    def override_get_db() -> Session:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CASE-SPLIT-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "案件分摊测试",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_agent_user(session_factory: sessionmaker, username: str) -> str:
    with session_factory() as db:
        role = db.query(T_Role).filter(T_Role.code == "Agent").first()
        assert role is not None, "Agent role should exist in seeded data"

        user = T_User(
            id=str(uuid4()),
            username=username,
            display_name=username,
            password_hash=get_password_hash("password123"),
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(T_UserRole(user_id=user.id, role_id=role.id))
        db.commit()
        return user.id


def test_get_case_returns_empty_agent_splits_when_unconfigured(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    case_id = _create_case(client, auth_headers)

    resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["agent_splits"] == []


def test_put_case_persists_agent_splits_and_roundtrips(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    agent_one_id = _create_agent_user(session_factory, f"agent-one-{uuid4().hex[:8]}")
    agent_two_id = _create_agent_user(session_factory, f"agent-two-{uuid4().hex[:8]}")

    update_resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": agent_one_id, "role": "Agent", "share_ratio": "60.0000"},
                {"agent_id": agent_two_id, "role": "Agent", "share_ratio": "40.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    update_data = update_resp.json()
    assert len(update_data["agent_splits"]) == 2
    assert {row["agent_id"] for row in update_data["agent_splits"]} == {
        agent_one_id,
        agent_two_id,
    }
    assert Decimal(str(update_data["agent_splits"][0]["share_ratio"])) + Decimal(
        str(update_data["agent_splits"][1]["share_ratio"])
    ) == Decimal("100")

    detail_resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert detail_resp.status_code == 200, detail_resp.text
    detail_data = detail_resp.json()
    assert len(detail_data["agent_splits"]) == 2
    assert {row["agent_id"] for row in detail_data["agent_splits"]} == {
        agent_one_id,
        agent_two_id,
    }


def test_put_case_rejects_duplicate_agent_split_members(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    agent_id = _create_agent_user(session_factory, f"agent-dup-{uuid4().hex[:8]}")

    resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": agent_id, "role": "Agent", "share_ratio": "50.0000"},
                {"agent_id": agent_id, "role": "Agent", "share_ratio": "50.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text


def test_put_case_rejects_non_agent_split_member(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    with session_factory() as db:
        user = T_User(
            id=str(uuid4()),
            username=f"user-{uuid4().hex[:8]}",
            display_name="普通用户",
            password_hash=get_password_hash("password123"),
            is_active=True,
        )
        db.add(user)
        db.commit()
        user_id = user.id

    resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": user_id, "role": "Agent", "share_ratio": "100.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text


def test_put_case_rejects_split_ratio_not_100(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    agent_one_id = _create_agent_user(session_factory, f"agent-a-{uuid4().hex[:8]}")
    agent_two_id = _create_agent_user(session_factory, f"agent-b-{uuid4().hex[:8]}")

    resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": agent_one_id, "role": "Agent", "share_ratio": "55.0000"},
                {"agent_id": agent_two_id, "role": "Agent", "share_ratio": "40.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text


def test_put_case_rejects_invalid_per_row_share_ratio(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    agent_one_id = _create_agent_user(session_factory, f"agent-c-{uuid4().hex[:8]}")
    agent_two_id = _create_agent_user(session_factory, f"agent-d-{uuid4().hex[:8]}")

    resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": agent_one_id, "role": "Agent", "share_ratio": "150.0000"},
                {"agent_id": agent_two_id, "role": "Agent", "share_ratio": "-50.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text
