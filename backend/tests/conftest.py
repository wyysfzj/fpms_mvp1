from __future__ import annotations

import os
from pathlib import Path
from typing import Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.models import *  # noqa: F401, F403  — ensure full ORM registry before any query
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.documents.models import DocTemplate
from app.modules.rbac.service import seed_default_roles_perms
from app.modules.tasks.models import TaskTemplate


@pytest.fixture(scope="session")
def test_db_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    return f"sqlite:///{db_path}"


@pytest.fixture(scope="session")
def migrated_db(test_db_url: str) -> str:
    os.environ["DATABASE_URL"] = test_db_url
    get_settings.cache_clear()

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(config, "head")
    return test_db_url


@pytest.fixture(scope="session")
def engine(migrated_db: str):
    engine = create_engine(
        migrated_db,
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    @event.listens_for(engine, "checkout")
    def restore_sqlite_pragma(dbapi_connection, _connection_record, _connection_proxy):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def seed_data(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        _seed_baseline(db)
        db.commit()


@pytest.fixture(autouse=True)
def _reset_test_data(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        _seed_baseline(db)
        db.commit()


def _seed_baseline(db: Session) -> None:
    seed_default_roles_perms(db)
    admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
    if not admin_role:
        raise RuntimeError("Admin role 'Admin' not found after seeding.")

    admin_user = db.query(T_User).filter(T_User.username == "admin").first()
    if not admin_user:
        admin_user = T_User(
            id=str(uuid4()),
            username="admin",
            display_name="Administrator",
            password_hash=get_password_hash("admin123"),
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

    existing_binding = (
        db.query(T_UserRole)
        .filter(
            T_UserRole.user_id == admin_user.id,
            T_UserRole.role_id == admin_role.id,
        )
        .first()
    )
    if not existing_binding:
        db.add(T_UserRole(user_id=admin_user.id, role_id=admin_role.id))

    _seed_task_templates(db)
    _seed_doc_templates(db)


def _seed_task_templates(db: Session) -> None:
    """Seed starter task templates into the test DB. Idempotent."""
    templates = [
        {"code": "OA_REPLY", "name": "OA答复期限", "add_days": 120, "inner_offset_days": 14},
        {"code": "GRANT_FEE", "name": "授权登记费", "add_days": 60, "inner_offset_days": 7},
    ]
    for t in templates:
        existing = db.query(TaskTemplate).filter(TaskTemplate.code == t["code"]).first()
        if not existing:
            db.add(TaskTemplate(id=str(uuid4()), **t))


def _seed_doc_templates(db: Session) -> None:
    """Seed doc templates into the test DB. Idempotent."""
    templates = [
        {
            "code": "OA_IN",
            "name": "OA收文",
            "direction": "IN",
            "need_reply": True,
            "deadline_template_code": "OA_REPLY",
            "status_effect": "OA1",
        },
        {
            "code": "OA_OUT",
            "name": "OA答复",
            "direction": "OUT",
            "reply_to_template_code": "OA_IN",
        },
        {
            "code": "ACCEPTANCE_NOTICE",
            "name": "受理通知书",
            "direction": "IN",
            "status_effect": "ACCEPTED",
        },
        {
            "code": "GRANT_NOTICE",
            "name": "授权通知书",
            "direction": "IN",
            "status_effect": "GRANT_PENDING",
            "fee_draft_type": "GRANT_FEE",
        },
        {
            "code": "CLIENT_IN",
            "name": "客户来函",
            "direction": "IN",
            "need_reply": False,
        },
    ]
    for t in templates:
        existing = db.query(DocTemplate).filter(DocTemplate.code == t["code"]).first()
        if not existing:
            db.add(DocTemplate(id=str(uuid4()), **t))


@pytest.fixture
def client(
    session_factory: sessionmaker, _reset_test_data: None
) -> Generator[TestClient, None, None]:
    from app.main import app

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
