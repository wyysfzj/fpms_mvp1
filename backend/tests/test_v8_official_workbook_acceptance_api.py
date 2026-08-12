from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError, raise_business_error
from app.db.session import get_db
from app.main import create_app
from app.modules.annuity import api as annuity_api

NOW = datetime(2026, 8, 13, 16, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000220"
ARTIFACT_ID = "11111111-1111-4111-8111-111111111220"
PATH = "/api/v1/pay-lists/7/official-workbook/acceptance"


class RecordingSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollbacks += 1


def _route() -> APIRoute:
    matches = [
        route
        for route in annuity_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/pay-lists/{pay_list_id}/official-workbook/acceptance"
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    return next(item.call for item in _route().dependant.dependencies if item.name == "_perm")


def _payload(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_id": ARTIFACT_ID,
        "evidence_ref": "official-site/acceptance/receipt-220",
        "evidence_sha256": "a" * 64,
        "accepted_at": "2026-08-13T16:00:00",
        "idempotency_key": "official-workbook-acceptance-http-220",
    }
    payload.update(changes)
    return payload


def _result(disposition: str = "CREATED") -> object:
    return SimpleNamespace(
        artifact_id=ARTIFACT_ID,
        pay_list_id=7,
        evidence_ref="official-site/acceptance/receipt-220",
        evidence_sha256="a" * 64,
        accepted_at=NOW,
        activity_id="22222222-2222-4222-8222-222222222220",
        status="OFFICIAL_SITE_ACCEPTED",
        accepted=True,
        paid=False,
        ticket_verified=False,
        idempotency_key="official-workbook-acceptance-http-220",
        disposition=disposition,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    commit_error: Exception | None = None,
    authenticated: bool = True,
    permitted: bool = True,
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession(commit_error)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    if permitted:
        app.dependency_overrides[_permission_dependency()] = lambda: None
    elif authenticated:

        def forbidden() -> None:
            raise_business_error("FORBIDDEN", "Permission denied", status_code=403)

        app.dependency_overrides[_permission_dependency()] = forbidden
    monkeypatch.setattr(annuity_api, "_official_workbook_utcnow", lambda: NOW)
    monkeypatch.setattr(annuity_api, "_official_workbook_runtime_profile", lambda: "production")
    return TestClient(app, raise_server_exceptions=False), transaction


def test_exact_route_permission_command_created_envelope_and_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, object]] = []

    def record(command: object, transaction: object) -> object:
        calls.append((command, transaction))
        return _result()

    monkeypatch.setattr(annuity_api, "record_official_workbook_acceptance", record)
    client, transaction = _client(monkeypatch)
    response = client.post(PATH, json=_payload())

    assert response.status_code == 201
    assert response.json() == {
        "artifact_id": ARTIFACT_ID,
        "pay_list_id": 7,
        "evidence_ref": "official-site/acceptance/receipt-220",
        "evidence_sha256": "a" * 64,
        "accepted_at": "2026-08-13T16:00:00",
        "activity_id": "22222222-2222-4222-8222-222222222220",
        "status": "OFFICIAL_SITE_ACCEPTED",
        "accepted": True,
        "paid": False,
        "ticket_verified": False,
        "idempotency_key": "official-workbook-acceptance-http-220",
        "disposition": "CREATED",
    }
    command, supplied_transaction = calls[0]
    assert supplied_transaction is transaction
    assert command.pay_list_id == 7
    assert command.artifact_id == ARTIFACT_ID
    assert command.evidence_ref == "official-site/acceptance/receipt-220"
    assert command.evidence_sha256 == "a" * 64
    assert command.accepted_at == NOW
    assert command.actor_id == ACTOR_ID
    assert command.idempotency_key == "official-workbook-acceptance-http-220"
    assert command.runtime_profile == "production"
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Edit"
    assert transaction.commits == 1 and transaction.rollbacks == 0


def test_reused_is_200_and_commit_failure_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        annuity_api,
        "record_official_workbook_acceptance",
        lambda *_args: _result("REUSED"),
    )
    client, transaction = _client(monkeypatch)
    response = client.post(PATH, json=_payload())
    assert response.status_code == 200
    assert response.json()["disposition"] == "REUSED"
    assert transaction.commits == 1 and transaction.rollbacks == 0

    client, transaction = _client(monkeypatch, commit_error=RuntimeError("commit failed"))
    assert client.post(PATH, json=_payload()).status_code == 500
    assert transaction.commits == 1 and transaction.rollbacks == 1


@pytest.mark.parametrize(
    ("status_code", "code"),
    (
        (400, "OFFICIAL_WORKBOOK_ACCEPTANCE_INPUT_INVALID"),
        (404, "OFFICIAL_WORKBOOK_ARTIFACT_NOT_FOUND"),
        (409, "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED"),
    ),
)
def test_service_error_envelope_and_rollback(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    def reject(*_args: object) -> object:
        raise BusinessError(code, "rejected", status_code=status_code)

    monkeypatch.setattr(annuity_api, "record_official_workbook_acceptance", reject)
    client, transaction = _client(monkeypatch)
    response = client.post(PATH, json=_payload())
    assert response.status_code == status_code
    assert response.json() == {"error": {"code": code, "message": "rejected", "details": None}}
    assert transaction.commits == 0 and transaction.rollbacks == 1


def test_request_auth_and_permission_failures_do_not_call_service_or_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected(*_args: object) -> object:
        raise AssertionError("service must not be called")

    monkeypatch.setattr(annuity_api, "record_official_workbook_acceptance", unexpected)
    invalid_payloads = (
        {},
        _payload(pay_list_id=7),
        _payload(artifact_id=""),
        _payload(evidence_sha256="A" * 64),
        _payload(accepted_at="not-a-date"),
    )
    for payload in invalid_payloads:
        client, transaction = _client(monkeypatch)
        response = client.post(PATH, json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
        assert transaction.commits == transaction.rollbacks == 0

    anonymous, transaction = _client(monkeypatch, authenticated=False, permitted=False)
    response = anonymous.post(PATH, json=_payload())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
    assert transaction.commits == transaction.rollbacks == 0

    forbidden, transaction = _client(monkeypatch, permitted=False)
    response = forbidden.post(PATH, json=_payload())
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert transaction.commits == transaction.rollbacks == 0
