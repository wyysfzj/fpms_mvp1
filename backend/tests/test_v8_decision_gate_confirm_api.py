from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi import Response
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.system import api as system_api
from app.modules.system.decision_gate_schemas import (
    DecisionGateRecordIn,
    DecisionGateRecordOut,
)
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateRecordDisposition,
    DecisionGateRecordResult,
    DecisionGateStatus,
    RecordDecisionGateCommand,
)

PATH = "/api/v1/system/decision-gates"
ROUTER_PATH = "/system/decision-gates"
ACTOR_ID = "actor-1"
EFFECTIVE_AT = datetime(2026, 7, 15, 9, 30)

INPUT_FIELDS = (
    "gate_code",
    "scope_key",
    "decision_value",
    "decision_status",
    "source_reference",
    "source_version",
    "effective_at",
    "idempotency_key",
    "expected_current_gate_id",
)
OUTPUT_FIELDS = (
    "gate_id",
    "gate_code",
    "scope_key",
    "decision_value",
    "decision_status",
    "source_reference",
    "source_version",
    "confirmed_by",
    "effective_at",
    "supersedes_gate_id",
    "decision_snapshot",
    "idempotency_key",
    "current_identity_key",
    "disposition",
)


class RecordingSession:
    def __init__(self, *, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollback_calls += 1

    def refresh(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("decision-gate adapter called refresh")

    def execute(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("decision-gate adapter issued a second SELECT")


def _request_data(
    *,
    decision_status: str = "CONFIRMED",
    decision_value: str | None = "APPROVED",
    idempotency_key: str = "idem-1",
    expected_current_gate_id: str | None = None,
) -> dict[str, object]:
    return {
        "gate_code": "DG-FEE-APPLICATION-DRAFT",
        "scope_key": "case:CASE-1",
        "decision_value": decision_value,
        "decision_status": decision_status,
        "source_reference": "customer-answer-20260715.docx",
        "source_version": "2026-07-15",
        "effective_at": "2026-07-15T09:30:00",
        "idempotency_key": idempotency_key,
        "expected_current_gate_id": expected_current_gate_id,
    }


def _result(
    *,
    disposition: DecisionGateRecordDisposition = DecisionGateRecordDisposition.CREATED,
    gate_id: str = "gate-1",
    decision_status: DecisionGateStatus = DecisionGateStatus.CONFIRMED,
    decision_value: str | None = "APPROVED",
    supersedes_gate_id: str | None = None,
    current_identity_key: str | None = "DG-FEE-APPLICATION-DRAFT|case:CASE-1",
    idempotency_key: str = "idem-1",
) -> DecisionGateRecordResult:
    return DecisionGateRecordResult(
        gate_id=gate_id,
        gate_code=DecisionGateCode.FEE_APPLICATION_DRAFT,
        scope_key="case:CASE-1",
        decision_value=decision_value,
        decision_status=decision_status,
        source_reference="customer-answer-20260715.docx",
        source_version="2026-07-15",
        confirmed_by=ACTOR_ID,
        effective_at=EFFECTIVE_AT,
        supersedes_gate_id=supersedes_gate_id,
        decision_snapshot=f"snapshot-{idempotency_key}",
        idempotency_key=idempotency_key,
        current_identity_key=current_identity_key,
        disposition=disposition,
    )


def _route() -> APIRoute:
    matching = [
        route
        for route in system_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == ROUTER_PATH
        and route.methods == {"POST"}
    ]
    assert len(matching) == 1
    return matching[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_result: DecisionGateRecordResult | None = None,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession]:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)

    def service(command: RecordDecisionGateCommand, transaction: object):
        assert transaction is session
        if service_error is not None:
            raise service_error
        assert service_result is not None
        return service_result

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(system_api, "record_decision_gate", service)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session


def test_frozen_schemas_have_exact_order_annotations_and_strict_required_input() -> None:
    assert tuple(DecisionGateRecordIn.model_fields) == INPUT_FIELDS
    assert get_type_hints(DecisionGateRecordIn) == {
        "gate_code": DecisionGateCode,
        "scope_key": str,
        "decision_value": str | None,
        "decision_status": DecisionGateStatus,
        "source_reference": str,
        "source_version": str,
        "effective_at": datetime,
        "idempotency_key": str,
        "expected_current_gate_id": str | None,
    }
    assert DecisionGateRecordIn.model_config["extra"] == "forbid"
    assert all(field.is_required() for field in DecisionGateRecordIn.model_fields.values())

    assert tuple(DecisionGateRecordOut.model_fields) == OUTPUT_FIELDS
    assert get_type_hints(DecisionGateRecordOut) == {
        "gate_id": str,
        "gate_code": DecisionGateCode,
        "scope_key": str,
        "decision_value": str | None,
        "decision_status": DecisionGateStatus,
        "source_reference": str,
        "source_version": str,
        "confirmed_by": str,
        "effective_at": datetime,
        "supersedes_gate_id": str | None,
        "decision_snapshot": str,
        "idempotency_key": str,
        "current_identity_key": str | None,
        "disposition": DecisionGateRecordDisposition,
    }

    for missing_nullable in ("decision_value", "expected_current_gate_id"):
        invalid = _request_data()
        invalid.pop(missing_nullable)
        with pytest.raises(ValidationError):
            DecisionGateRecordIn.model_validate(invalid)

    with pytest.raises(ValidationError):
        DecisionGateRecordIn.model_validate({**_request_data(), "confirmed_by": "client-actor"})


def test_route_is_single_post_with_injected_permission_actor_and_direct_response_model() -> None:
    route = _route()

    assert route.methods == {"POST"}
    assert route.response_model is DecisionGateRecordOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "SystemParam.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    assert not any(
        isinstance(item, APIRoute)
        and item.path in {f"{ROUTER_PATH}/confirm", f"{ROUTER_PATH}/revoke"}
        for item in system_api.router.routes
    )


@pytest.mark.parametrize(
    ("request_data", "service_result"),
    [
        (_request_data(), _result()),
        (
            _request_data(
                decision_status="REVOKED",
                decision_value=None,
                idempotency_key="idem-2",
                expected_current_gate_id="gate-1",
            ),
            _result(
                gate_id="gate-2",
                decision_status=DecisionGateStatus.REVOKED,
                decision_value=None,
                supersedes_gate_id="gate-1",
                current_identity_key=None,
                idempotency_key="idem-2",
            ),
        ),
        (
            _request_data(
                idempotency_key="idem-3",
                expected_current_gate_id="gate-2",
            ),
            _result(
                gate_id="gate-3",
                supersedes_gate_id="gate-2",
                idempotency_key="idem-3",
            ),
        ),
    ],
)
def test_confirmation_revocation_and_reconfirmation_use_same_server_owned_adapter(
    monkeypatch: pytest.MonkeyPatch,
    request_data: dict[str, object],
    service_result: DecisionGateRecordResult,
) -> None:
    payload = DecisionGateRecordIn.model_validate(request_data)
    session = RecordingSession()
    response = Response()
    actor = SimpleNamespace(id=ACTOR_ID)
    captured: list[RecordDecisionGateCommand] = []

    def service(command: RecordDecisionGateCommand, transaction: object):
        assert transaction is session
        captured.append(command)
        return service_result

    monkeypatch.setattr(system_api, "record_decision_gate", service)

    actual = system_api.create_decision_gate_record(
        payload=payload,
        response=response,
        _perm=None,
        current_user=actor,
        db=session,
    )

    assert captured == [
        RecordDecisionGateCommand(
            gate_code=payload.gate_code,
            scope_key=payload.scope_key,
            decision_value=payload.decision_value,
            decision_status=payload.decision_status,
            source_reference=payload.source_reference,
            source_version=payload.source_version,
            confirmed_by=ACTOR_ID,
            effective_at=payload.effective_at,
            idempotency_key=payload.idempotency_key,
            expected_current_gate_id=payload.expected_current_gate_id,
        )
    ]
    assert actual == DecisionGateRecordOut.model_validate(service_result, from_attributes=True)
    assert response.status_code == 201
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    [
        (DecisionGateRecordDisposition.CREATED, 201),
        (DecisionGateRecordDisposition.REUSED, 200),
    ],
)
def test_created_and_reused_return_full_direct_body_and_commit_once(
    monkeypatch: pytest.MonkeyPatch,
    disposition: DecisionGateRecordDisposition,
    expected_status: int,
) -> None:
    result = _result(disposition=disposition)
    client, session = _client(monkeypatch, service_result=result)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == expected_status
    assert response.json() == DecisionGateRecordOut.model_validate(
        result, from_attributes=True
    ).model_dump(mode="json")
    assert "data" not in response.json()
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_service_business_error_rolls_back_once_and_is_reraised_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = BusinessError(
        "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        "conflict",
        details={"actual_current_gate_id": "gate-other"},
        status_code=409,
    )
    session = RecordingSession()

    def service(*_args: object, **_kwargs: object) -> None:
        raise error

    monkeypatch.setattr(system_api, "record_decision_gate", service)
    with pytest.raises(BusinessError) as exc_info:
        system_api.create_decision_gate_record(
            payload=DecisionGateRecordIn.model_validate(_request_data()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_commit_failure_rolls_back_once_and_reraises_original_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = RuntimeError("commit failed")
    session = RecordingSession(commit_error=error)
    monkeypatch.setattr(system_api, "record_decision_gate", lambda *_args: _result())

    with pytest.raises(RuntimeError) as exc_info:
        system_api.create_decision_gate_record(
            payload=DecisionGateRecordIn.model_validate(_request_data()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


@pytest.mark.parametrize(
    ("status_code", "code"),
    [
        (400, "DECISION_GATE_INVALID"),
        (404, "DECISION_GATE_ACTOR_NOT_FOUND"),
        (409, "DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT"),
        (409, "DECISION_GATE_CURRENT_NOT_FOUND"),
        (409, "DECISION_GATE_ALREADY_REVOKED"),
        (409, "DECISION_GATE_CURRENT_IDENTITY_CONFLICT"),
        (409, "DECISION_GATE_WRITE_CONFLICT"),
    ],
)
def test_service_business_errors_pass_through_http_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    error = BusinessError(code, "service error", details={"marker": code}, status_code=status_code)
    client, session = _client(monkeypatch, service_error=error)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "service error",
            "details": {"marker": code},
        }
    }
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_authentication_and_permission_dependencies_preserve_401_and_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: RecordingSession()
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        unauthenticated = client.post(PATH, json=_request_data())

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "SystemParam.Edit"},
        status_code=403,
    )
    client, session = _client(monkeypatch, permission_error=forbidden)
    response = client.post(PATH, json=_request_data())

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "SystemParam.Edit"},
        }
    }
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    "invalid",
    [
        {key: value for key, value in _request_data().items() if key != "decision_value"},
        {key: value for key, value in _request_data().items() if key != "expected_current_gate_id"},
        {**_request_data(), "confirmed_by": "client-actor"},
        {**_request_data(), "decision_status": "UNKNOWN"},
        {**_request_data(), "gate_code": "UNKNOWN"},
        {**_request_data(), "effective_at": "not-a-datetime"},
    ],
)
def test_request_shape_type_enum_and_datetime_failures_return_422(
    monkeypatch: pytest.MonkeyPatch,
    invalid: dict[str, object],
) -> None:
    client, session = _client(monkeypatch, service_result=_result())

    response = client.post(PATH, json=invalid)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_confirm_and_revoke_secondary_routes_do_not_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _session = _client(monkeypatch, service_result=_result())

    assert client.post(f"{PATH}/confirm", json=_request_data()).status_code == 404
    assert client.post(f"{PATH}/revoke", json=_request_data()).status_code == 404
