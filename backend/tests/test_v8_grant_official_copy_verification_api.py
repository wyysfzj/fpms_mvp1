from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import Callable

import pytest
from fastapi import Response
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.documents import api as documents_api
from app.modules.documents.grant_official_copy_verification_schemas import (
    GrantOfficialCopyEventIn,
    GrantOfficialCopyEventOut,
)
from app.modules.documents.grant_official_copy_verification_service import (
    GrantOfficialCopyDisposition,
    GrantOfficialCopyEventResult,
    GrantOfficialCopyEventType,
    RecordGrantOfficialCopyEventCommand,
)
from app.modules.system.grant_evidence_source_service import GrantEvidenceScope

PATH = "/documents/evidence-versions/{evidence_version_id}/grant-official-copy-events"
EVIDENCE_ID = "11111111-1111-4111-8111-111111111111"
ACTOR_ID = "21111111-1111-4111-8111-111111111111"
CURRENT_ID = "31111111-1111-4111-8111-111111111111"
EVENT_ID = "41111111-1111-4111-8111-111111111111"
SOURCE_CONFIG_ID = "51111111-1111-4111-8111-111111111111"
SOURCE_RECORD_ID = "61111111-1111-4111-8111-111111111111"
ROLE_CONFIG_ID = "71111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 10, 18, 0, 0, 123456)


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

    def execute(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("official-copy API queried product tables")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("official-copy API flushed before delegation")


def _body(
    event_type: GrantOfficialCopyEventType = GrantOfficialCopyEventType.ACQUIRED,
) -> dict[str, object]:
    return {
        "evidence_scope": GrantEvidenceScope.GRANT_ANNOUNCEMENT.value,
        "event_type": event_type.value,
        "reason": f"TEST {event_type.value}",
        "original_reference": (
            "CNIPA-TEST-REFERENCE"
            if event_type is GrantOfficialCopyEventType.ACQUIRED
            else None
        ),
        "expected_current_event_id": (
            None if event_type is GrantOfficialCopyEventType.ACQUIRED else CURRENT_ID
        ),
        "idempotency_key": f"test-{event_type.value.lower()}",
    }


def _result(disposition: GrantOfficialCopyDisposition) -> GrantOfficialCopyEventResult:
    return GrantOfficialCopyEventResult(
        event_id=EVENT_ID,
        evidence_version_id=EVIDENCE_ID,
        evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        event_type=GrantOfficialCopyEventType.ACQUIRED,
        source_config_id=SOURCE_CONFIG_ID,
        source_record_id=SOURCE_RECORD_ID,
        role_config_id=ROLE_CONFIG_ID,
        event_snapshot_hash="a" * 64,
        current_identity_key=f"GRANT_OFFICIAL_COPY|{EVIDENCE_ID}",
        disposition=disposition,
    )


def _route() -> APIRoute:
    routes = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute) and route.path == PATH and route.methods == {"POST"}
    ]
    assert len(routes) == 1
    return routes[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    service: Callable[[object, object], GrantOfficialCopyEventResult],
    *,
    session: RecordingSession | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = session or RecordingSession()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(documents_api, "record_grant_official_copy_event", service)
    monkeypatch.setattr(documents_api, "_utc_now", lambda: NOW)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), transaction


def test_request_response_and_route_contract_are_exact() -> None:
    assert tuple(GrantOfficialCopyEventIn.model_fields) == (
        "evidence_scope",
        "event_type",
        "reason",
        "original_reference",
        "expected_current_event_id",
        "idempotency_key",
    )
    assert tuple(GrantOfficialCopyEventOut.model_fields) == (
        "event_id",
        "evidence_version_id",
        "evidence_scope",
        "event_type",
        "source_config_id",
        "source_record_id",
        "role_config_id",
        "event_snapshot_hash",
        "current_identity_key",
        "disposition",
    )
    assert GrantOfficialCopyEventIn.model_config["extra"] == "forbid"
    assert all(field.is_required() for field in GrantOfficialCopyEventIn.model_fields.values())
    route = _route()
    assert route.status_code == 201
    assert route.response_model is GrantOfficialCopyEventOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert len(
        [
            candidate
            for candidate in documents_api.router.routes
            if isinstance(candidate, APIRoute)
            and "grant-official-copy-events" in candidate.path
        ]
    ) == 1


def test_strict_stage_shapes_reject_client_actor_time_and_malformed_values() -> None:
    GrantOfficialCopyEventIn.model_validate(_body())
    GrantOfficialCopyEventIn.model_validate(_body(GrantOfficialCopyEventType.FIRST_VERIFIED))
    for change in (
        {"actor_id": ACTOR_ID},
        {"action_at": NOW.isoformat()},
        {"event_type": "OTHER"},
        {"reason": " bad"},
        {"original_reference": None},
        {"expected_current_event_id": CURRENT_ID},
        {"idempotency_key": ""},
    ):
        with pytest.raises(ValidationError):
            GrantOfficialCopyEventIn.model_validate(_body() | change)
    for change in (
        {"original_reference": "not-null"},
        {"expected_current_event_id": None},
        {"expected_current_event_id": "not-a-uuid"},
    ):
        with pytest.raises(ValidationError):
            GrantOfficialCopyEventIn.model_validate(
                _body(GrantOfficialCopyEventType.SECOND_VERIFIED) | change
            )


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantOfficialCopyDisposition.CREATED, 201),
        (GrantOfficialCopyDisposition.REUSED, 200),
    ),
)
def test_route_injects_path_actor_one_server_time_and_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantOfficialCopyDisposition,
    expected_status: int,
) -> None:
    captured: list[tuple[RecordGrantOfficialCopyEventCommand, object]] = []

    def service(command: object, transaction: object) -> GrantOfficialCopyEventResult:
        assert isinstance(command, RecordGrantOfficialCopyEventCommand)
        captured.append((command, transaction))
        return _result(disposition)

    client, session = _client(monkeypatch, service)
    response = client.post(
        f"/api/v1/documents/evidence-versions/{EVIDENCE_ID}/grant-official-copy-events",
        json=_body(),
    )
    assert response.status_code == expected_status
    assert captured == [
        (
            RecordGrantOfficialCopyEventCommand(
                evidence_version_id=EVIDENCE_ID,
                evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                event_type=GrantOfficialCopyEventType.ACQUIRED,
                actor_id=ACTOR_ID,
                action_at=NOW,
                reason="TEST ACQUIRED",
                original_reference="CNIPA-TEST-REFERENCE",
                expected_current_event_id=None,
                idempotency_key="test-acquired",
            ),
            session,
        )
    ]
    assert response.json() == GrantOfficialCopyEventOut.model_validate(
        _result(disposition), from_attributes=True
    ).model_dump(mode="json")
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_validation_permission_and_service_failures_never_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def conflict(command: object, transaction: object) -> GrantOfficialCopyEventResult:
        calls.append(command)
        raise BusinessError("TEST_CONFLICT", "test", status_code=409)

    client, session = _client(monkeypatch, conflict)
    response = client.post(
        f"/api/v1/documents/evidence-versions/{EVIDENCE_ID}/grant-official-copy-events",
        json=_body(),
    )
    assert response.status_code == 409
    assert len(calls) == 1
    assert (session.commit_calls, session.rollback_calls) == (0, 1)

    calls.clear()
    malformed = client.post(
        "/api/v1/documents/evidence-versions/not-a-uuid/grant-official-copy-events",
        json=_body(),
    )
    assert malformed.status_code == 422
    assert calls == []

    denied_client, denied_session = _client(
        monkeypatch,
        lambda command, transaction: _result(GrantOfficialCopyDisposition.CREATED),
        permission_error=BusinessError("FORBIDDEN", "forbidden", status_code=403),
    )
    denied = denied_client.post(
        f"/api/v1/documents/evidence-versions/{EVIDENCE_ID}/grant-official-copy-events",
        json=_body(),
    )
    assert denied.status_code == 403
    assert (denied_session.commit_calls, denied_session.rollback_calls) == (0, 0)


def test_commit_failure_rolls_back_and_direct_route_has_no_queries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = RecordingSession(commit_error=RuntimeError("commit failed"))
    monkeypatch.setattr(documents_api, "_utc_now", lambda: NOW)
    monkeypatch.setattr(
        documents_api,
        "record_grant_official_copy_event",
        lambda command, transaction: _result(GrantOfficialCopyDisposition.CREATED),
    )
    with pytest.raises(RuntimeError, match="commit failed"):
        documents_api.record_grant_official_copy_verification_event(
            evidence_version_id=EVIDENCE_ID,
            payload=GrantOfficialCopyEventIn.model_validate(_body()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )
    assert (session.commit_calls, session.rollback_calls) == (1, 1)
