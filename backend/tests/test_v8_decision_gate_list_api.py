from __future__ import annotations

import inspect
from contextlib import AbstractContextManager
from datetime import datetime
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.sql import Select

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.system import api as system_api
from app.modules.system import decision_gate_schemas, decision_gate_service
from app.modules.system.decision_gate_service import DecisionGateCode, DecisionGateStatus

PATH = "/api/v1/system/decision-gates"
ROUTER_PATH = "/system/decision-gates"

AUDIT_FIELDS = (
    "gate_id",
    "gate_code",
    "scope_key",
    "decision_value",
    "decision_status",
    "source_reference",
    "source_version",
    "confirmed_by",
    "effective_at",
    "recorded_at",
    "supersedes_gate_id",
    "current_identity_key",
)
DecisionGateAuditOut = getattr(decision_gate_schemas, "DecisionGateAuditOut", None)


class NoAutoflushSpy(AbstractContextManager[None]):
    def __init__(self, session: AuditSessionSpy) -> None:
        self.session = session

    def __enter__(self) -> None:
        self.session.no_autoflush_enters += 1

    def __exit__(self, *_args: object) -> None:
        self.session.no_autoflush_exits += 1


class MappingResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def all(self) -> list[dict[str, object]]:
        return self.rows


class ExecuteResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def mappings(self) -> MappingResult:
        return MappingResult(self.rows)


class AuditSessionSpy:
    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self.rows = rows or []
        self.statements: list[Select[tuple[object, ...]]] = []
        self.no_autoflush_enters = 0
        self.no_autoflush_exits = 0

    @property
    def no_autoflush(self) -> NoAutoflushSpy:
        return NoAutoflushSpy(self)

    def execute(self, statement: Select[tuple[object, ...]]) -> ExecuteResult:
        self.statements.append(statement)
        return ExecuteResult(self.rows)

    def add(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit list route called add")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit list route called flush")

    def refresh(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit list route called refresh")

    def expire(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit list route called expire")

    def commit(self) -> None:
        raise AssertionError("audit list route called commit")

    def rollback(self) -> None:
        raise AssertionError("audit list route called rollback")


def _route() -> APIRoute:
    matches = [
        route
        for route in system_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"GET"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _row(
    gate_id: str,
    *,
    gate_code: str = "DG-FEE-APPLICATION-DRAFT",
    scope_key: str = "case:CASE-1",
    decision_value: str | None = "APPROVED",
    decision_status: str = "CONFIRMED",
    source_reference: str = "customer-answer.docx",
    source_version: str = "2026-07-15",
    confirmed_by: str = "actor-1",
    effective_at: datetime = datetime(2026, 7, 15, 9, 0),
    recorded_at: datetime = datetime(2026, 7, 15, 10, 0),
    supersedes_gate_id: str | None = None,
    current_identity_key: str | None = "DG-FEE-APPLICATION-DRAFT|case:CASE-1",
) -> dict[str, object]:
    return {
        "gate_id": gate_id,
        "gate_code": gate_code,
        "scope_key": scope_key,
        "decision_value": decision_value,
        "decision_status": decision_status,
        "source_reference": source_reference,
        "source_version": source_version,
        "confirmed_by": confirmed_by,
        "effective_at": effective_at,
        "recorded_at": recorded_at,
        "supersedes_gate_id": supersedes_gate_id,
        "current_identity_key": current_identity_key,
    }


def _client(
    session: AuditSessionSpy,
    *,
    permission_error: BusinessError | None = None,
) -> TestClient:
    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app)


def test_audit_dto_preserves_exact_persisted_facts() -> None:
    assert DecisionGateAuditOut is not None
    assert tuple(DecisionGateAuditOut.model_fields) == AUDIT_FIELDS
    assert get_type_hints(DecisionGateAuditOut) == {
        "gate_id": str,
        "gate_code": DecisionGateCode,
        "scope_key": str,
        "decision_value": str | None,
        "decision_status": DecisionGateStatus,
        "source_reference": str,
        "source_version": str,
        "confirmed_by": str,
        "effective_at": datetime,
        "recorded_at": datetime,
        "supersedes_gate_id": str | None,
        "current_identity_key": str | None,
    }


def test_route_is_bodyless_parameterless_get_with_read_permission_and_bare_list() -> None:
    route = _route()
    operation = create_app().openapi()["paths"][PATH]["get"]

    assert route.response_model == list[DecisionGateAuditOut]
    assert route.dependant.body_params == []
    assert route.dependant.path_params == []
    assert route.dependant.query_params == []
    assert "requestBody" not in operation
    assert operation.get("parameters", []) == []
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "SystemParam.Read"


def test_empty_audit_history_returns_200_bare_empty_list() -> None:
    session = AuditSessionSpy()

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 200
    assert response.json() == []
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1
    assert len(session.statements) == 1


def test_all_history_is_visible_in_stable_order_via_one_explicit_read_only_select(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = [
        _row(
            "gate-1",
            recorded_at=datetime(2026, 7, 15, 10, 0),
            current_identity_key=None,
        ),
        _row(
            "gate-2",
            decision_status="REVOKED",
            decision_value=None,
            recorded_at=datetime(2026, 7, 15, 10, 0),
            supersedes_gate_id="gate-1",
            current_identity_key=None,
        ),
        _row(
            "gate-3",
            gate_code="DG-FEE-GRANT-YEAR-DRAFT",
            scope_key="case:CASE-2",
            source_reference="customer-followup.docx",
            source_version="2026-07-16",
            confirmed_by="actor-2",
            effective_at=datetime(2027, 1, 1),
            recorded_at=datetime(2026, 7, 16, 8, 0),
            current_identity_key="DG-FEE-GRANT-YEAR-DRAFT|case:CASE-2",
        ),
    ]
    session = AuditSessionSpy(rows)

    def resolver_forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("audit list route called resolve_decision_gate")

    monkeypatch.setattr(
        decision_gate_service,
        "resolve_decision_gate",
        resolver_forbidden,
    )
    monkeypatch.setattr(
        system_api,
        "resolve_decision_gate",
        resolver_forbidden,
        raising=False,
    )

    with _client(session) as client:
        response = client.get(PATH)

    assert response.status_code == 200
    assert response.json() == [
        DecisionGateAuditOut.model_validate(row).model_dump(mode="json") for row in rows
    ]
    assert all(tuple(item) == AUDIT_FIELDS for item in response.json())
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1
    assert len(session.statements) == 1

    statement = session.statements[0]
    assert isinstance(statement, Select)
    assert tuple(statement.selected_columns.keys()) == AUDIT_FIELDS
    assert statement.whereclause is None
    sql = " ".join(str(statement).split())
    assert (
        "ORDER BY t_customer_decision_gate.recorded_at ASC, t_customer_decision_gate.id ASC"
    ) in sql


def test_authentication_and_permission_errors_remain_401_and_403() -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: AuditSessionSpy()
    with TestClient(app) as client:
        unauthenticated = client.get(PATH)

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "SystemParam.Read"},
        status_code=403,
    )
    session = AuditSessionSpy()
    with _client(session, permission_error=forbidden) as client:
        response = client.get(PATH)

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "SystemParam.Read"},
        }
    }
    assert session.statements == []
