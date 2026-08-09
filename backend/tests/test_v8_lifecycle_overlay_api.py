from __future__ import annotations

import inspect
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.cases import api as cases_api
from app.modules.cases.lifecycle_overlay_schemas import (
    LifecycleOverlay,
    OverlayCenterSnapshot,
    OverlayDecisionGate,
    OverlayGateResolutionStatus,
)
from app.modules.system.decision_gate_service import DecisionGateCode

PATH = "/api/v1/cases/CASE-1/lifecycle-overlay"
OPENAPI_PATH = "/api/v1/cases/{case_id}/lifecycle-overlay"
ROUTER_PATH = "/cases/{case_id}/lifecycle-overlay"
CASE_ID = "CASE-1"
GENERATED_AT = datetime(2026, 7, 14, 9, 30, tzinfo=UTC)
CASE_CODES = tuple(
    code for code in DecisionGateCode if code is not DecisionGateCode.LEGACY_FORM_CLASS
)
PERMISSION_NAMES = ("_case_read", "_document_read", "_task_read", "_fee_read")
PERMISSION_CODES = ("Case.Read", "Doc.Read", "Task.Read", "Fee.Read")


def _route() -> APIRoute:
    matches = [
        route
        for route in cases_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"GET"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependencies() -> tuple[object, ...]:
    dependencies = {item.name: item.call for item in _route().dependant.dependencies}
    return tuple(dependencies[name] for name in PERMISSION_NAMES)


def _gates() -> tuple[OverlayDecisionGate, ...]:
    case_gates = tuple(
        OverlayDecisionGate(
            gate_code=code,
            requested_scope_key=f"case:{CASE_ID}",
            resolution_status=OverlayGateResolutionStatus.RESOLVED,
            gate_id=f"gate-{index}",
            resolved_scope_key=f"case:{CASE_ID}",
            decision_value="CONFIRMED",
            source_reference=f"source-{index}.docx",
            source_version="v1",
            confirmed_by="operator-1",
            effective_at=GENERATED_AT,
            unresolved_reason=None,
        )
        for index, code in enumerate(CASE_CODES, start=1)
    )
    legacy_gates = tuple(
        OverlayDecisionGate(
            gate_code=DecisionGateCode.LEGACY_FORM_CLASS,
            requested_scope_key=f"form-{index:03d}",
            resolution_status=OverlayGateResolutionStatus.RESOLVED,
            gate_id=f"legacy-{index}",
            resolved_scope_key="ALL-22" if index == 22 else f"form-{index:03d}",
            decision_value="HISTORICAL" if index == 22 else "CONFIRMED",
            source_reference=f"legacy-source-{index}.docx",
            source_version=f"legacy-v{index}",
            confirmed_by="operator-1",
            effective_at=GENERATED_AT,
            unresolved_reason=None,
        )
        for index in range(1, 23)
    )
    return case_gates + legacy_gates


def _overlay(*, after_sequence: int) -> LifecycleOverlay:
    return LifecycleOverlay(
        case_id=CASE_ID,
        lifecycle_revision=2,
        generated_at=GENERATED_AT,
        center_snapshot=OverlayCenterSnapshot(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=None,
            effective_at=None,
            verification_status=None,
            source_event_id=None,
        ),
        milestones=(),
        decision_gates=_gates(),
        warnings=(),
        legacy_conflicts=(),
        next_cursor=1 if after_sequence == 0 else None,
        has_more=after_sequence == 0,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_error: BusinessError | None = None,
    missing_permission: str | None = None,
) -> tuple[TestClient, list[dict[str, object]], object]:
    session = object()
    calls: list[dict[str, object]] = []

    def service(**kwargs: object) -> LifecycleOverlay:
        calls.append(kwargs)
        if service_error is not None:
            raise service_error
        return _overlay(after_sequence=kwargs["after_sequence"])

    def permission(required_permission: str):
        def check_permission() -> None:
            if missing_permission == required_permission:
                raise BusinessError(
                    "FORBIDDEN",
                    "Permission denied",
                    details={"required_perm": required_permission},
                    status_code=403,
                )

        return check_permission

    monkeypatch.setattr(cases_api, "read_lifecycle_overlay", service)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    for required_permission, dependency in zip(
        PERMISSION_CODES, _permission_dependencies(), strict=True
    ):
        app.dependency_overrides[dependency] = permission(required_permission)
    return TestClient(app), calls, session


def test_route_is_sole_bodyless_get_with_four_parameter_permissions() -> None:
    route = _route()
    operation = create_app().openapi()["paths"][OPENAPI_PATH]["get"]

    assert route.response_model is LifecycleOverlay
    assert route.dependant.body_params == []
    assert "requestBody" not in operation
    assert tuple(item.name for item in route.dependant.dependencies) == PERMISSION_NAMES + ("db",)
    assert (
        tuple(
            inspect.getclosurevars(dependency).nonlocals["code"]
            for dependency in _permission_dependencies()
        )
        == PERMISSION_CODES
    )
    assert {item["name"] for item in operation["parameters"]} == {
        "case_id",
        "after_sequence",
        "limit",
        "as_of_revision",
    }
    assert {item["name"]: item["required"] for item in operation["parameters"]} == {
        "case_id": True,
        "after_sequence": True,
        "limit": True,
        "as_of_revision": False,
    }


def test_two_cursor_pages_serialize_exact_overlay_and_complete_gate_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, calls, session = _client(monkeypatch)

    first = client.get(PATH, params={"after_sequence": 0, "limit": 1})
    second = client.get(PATH, params={"after_sequence": 1, "limit": 1, "as_of_revision": 2})

    assert first.status_code == second.status_code == 200
    assert calls == [
        {
            "case_id": CASE_ID,
            "after_sequence": 0,
            "limit": 1,
            "as_of_revision": None,
            "transaction": session,
        },
        {
            "case_id": CASE_ID,
            "after_sequence": 1,
            "limit": 1,
            "as_of_revision": 2,
            "transaction": session,
        },
    ]
    first_body, second_body = first.json(), second.json()
    assert "data" not in first_body
    assert first_body["generated_at"] == "2026-07-14T09:30:00Z"
    assert first_body["lifecycle_revision"] == 2
    assert (first_body["next_cursor"], first_body["has_more"]) == (1, True)
    assert (second_body["next_cursor"], second_body["has_more"]) == (None, False)
    assert first_body["decision_gates"] == second_body["decision_gates"]

    gates = first_body["decision_gates"]
    assert len(gates) == 29
    assert len({gate["gate_code"] for gate in gates}) == 8
    assert len({(gate["gate_code"], gate["requested_scope_key"]) for gate in gates}) == 29
    assert [gate["gate_code"] for gate in gates[:7]] == [code.value for code in CASE_CODES]
    assert [gate["requested_scope_key"] for gate in gates[:7]] == [f"case:{CASE_ID}"] * 7
    assert [gate["requested_scope_key"] for gate in gates[7:]] == [
        f"form-{index:03d}" for index in range(1, 23)
    ]
    assert all(gate["requested_scope_key"] != "ALL-22" for gate in gates)
    assert gates[-1] == {
        "gate_code": "DG-LEGACY-FORM-CLASS",
        "requested_scope_key": "form-022",
        "resolution_status": "RESOLVED",
        "gate_id": "legacy-22",
        "resolved_scope_key": "ALL-22",
        "decision_value": "HISTORICAL",
        "source_reference": "legacy-source-22.docx",
        "source_version": "legacy-v22",
        "confirmed_by": "operator-1",
        "effective_at": "2026-07-14T09:30:00Z",
        "unresolved_reason": None,
    }


def test_authentication_and_each_missing_permission_reject_the_whole_overlay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as client:
        unauthenticated = client.get(PATH, params={"after_sequence": 0, "limit": 1})

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    for required_perm in PERMISSION_CODES:
        client, calls, _session = _client(monkeypatch, missing_permission=required_perm)
        response = client.get(PATH, params={"after_sequence": 0, "limit": 1})

        assert response.status_code == 403
        assert response.json()["error"]["details"] == {"required_perm": required_perm}
        assert calls == []


@pytest.mark.parametrize(
    ("service_error", "expected_status", "expected_code"),
    [
        (BusinessError("CASE_NOT_FOUND", "案件不存在", status_code=404), 404, "CASE_NOT_FOUND"),
        (
            BusinessError("LIFECYCLE_OVERLAY_CONFLICT", "状态冲突", status_code=409),
            409,
            "LIFECYCLE_OVERLAY_CONFLICT",
        ),
    ],
)
def test_service_statuses_are_preserved_without_adapter_mapping(
    monkeypatch: pytest.MonkeyPatch,
    service_error: BusinessError,
    expected_status: int,
    expected_code: str,
) -> None:
    client, calls, _session = _client(monkeypatch, service_error=service_error)

    response = client.get(PATH, params={"after_sequence": 0, "limit": 1})

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
    assert len(calls) == 1


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 1},
        {"after_sequence": 0},
        {"after_sequence": "invalid", "limit": 1},
        {"after_sequence": 0, "limit": "invalid"},
        {"after_sequence": 0, "limit": 1, "as_of_revision": "invalid"},
    ],
)
def test_missing_or_non_integer_query_values_preserve_fastapi_422(
    monkeypatch: pytest.MonkeyPatch,
    params: dict[str, int | str],
) -> None:
    client, calls, _session = _client(monkeypatch)

    response = client.get(PATH, params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert calls == []
