from __future__ import annotations

from datetime import datetime, timezone
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
from app.modules.system import api as system_api
from app.modules.system.grant_manual_review_role_schemas import (
    GrantManualReviewRoleConfigOut,
    PublishGrantManualReviewRoleConfigIn,
    RevokeGrantManualReviewRoleConfigIn,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleConfigResult,
    GrantManualReviewRoleDisposition,
    PublishGrantManualReviewRoleConfigCommand,
    RevokeGrantManualReviewRoleConfigCommand,
)

ACTOR_ID = "11111111-1111-4111-8111-111111111111"
ROLE_IDS = (
    "21111111-1111-4111-8111-111111111111",
    "31111111-1111-4111-8111-111111111111",
    "41111111-1111-4111-8111-111111111111",
    "51111111-1111-4111-8111-111111111111",
    "61111111-1111-4111-8111-111111111111",
)
CONFIG_ID = "71111111-1111-4111-8111-111111111111"
OTHER_CONFIG_ID = "81111111-1111-4111-8111-111111111111"
EFFECTIVE_FROM = datetime(2026, 8, 10, 9, 0)
EFFECTIVE_TO = datetime(2027, 8, 10, 9, 0)
NOW = datetime(2026, 8, 10, 10, 30, 0, 123456)


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
        raise AssertionError("role configuration API queried carrier tables")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("role configuration API flushed before delegation")


def _result(
    disposition: GrantManualReviewRoleDisposition,
    *,
    status: str = "ACTIVE",
) -> GrantManualReviewRoleConfigResult:
    return GrantManualReviewRoleConfigResult(
        config_id=CONFIG_ID,
        config_status=status,
        config_snapshot_hash="a" * 64,
        current_identity_key="DG-GRANT-MANUAL-REVIEW|GLOBAL",
        disposition=disposition,
    )


def _publish_body() -> dict[str, object]:
    return {
        "official_copy_acquirer_role_id": ROLE_IDS[0],
        "first_verifier_role_id": ROLE_IDS[1],
        "second_verifier_role_id": ROLE_IDS[2],
        "manual_review_proposer_role_id": ROLE_IDS[3],
        "manual_review_second_reviewer_role_id": ROLE_IDS[4],
        "config_version": "grant-manual-review-role-v1",
        "effective_from": EFFECTIVE_FROM.isoformat(),
        "effective_to": EFFECTIVE_TO.isoformat(),
        "expected_current_config_id": None,
        "idempotency_key": "publish-grant-manual-review-role-v1",
    }


def _revoke_body() -> dict[str, object]:
    return {
        "config_version": "grant-manual-review-role-v2-revoked",
        "effective_from": EFFECTIVE_FROM.isoformat(),
        "expected_current_config_id": CONFIG_ID,
        "idempotency_key": "revoke-grant-manual-review-role-v2",
    }


def _route(path: str) -> APIRoute:
    routes = [
        route
        for route in system_api.router.routes
        if isinstance(route, APIRoute) and route.path == path and route.methods == {"POST"}
    ]
    assert len(routes) == 1
    return routes[0]


def _permission_dependency(path: str) -> object:
    dependency = next(item for item in _route(path).dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    route_path: str,
    service_name: str,
    service: Callable[[object, object], GrantManualReviewRoleConfigResult],
    session: RecordingSession | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = session or RecordingSession()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(system_api, service_name, service)
    monkeypatch.setattr(system_api, "_utc_now", lambda: NOW)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency(route_path)] = permission
    return TestClient(app), transaction


def test_request_and_response_schemas_are_strict_and_exact() -> None:
    assert tuple(PublishGrantManualReviewRoleConfigIn.model_fields) == (
        "official_copy_acquirer_role_id",
        "first_verifier_role_id",
        "second_verifier_role_id",
        "manual_review_proposer_role_id",
        "manual_review_second_reviewer_role_id",
        "config_version",
        "effective_from",
        "effective_to",
        "expected_current_config_id",
        "idempotency_key",
    )
    assert tuple(RevokeGrantManualReviewRoleConfigIn.model_fields) == (
        "config_version",
        "effective_from",
        "expected_current_config_id",
        "idempotency_key",
    )
    assert tuple(GrantManualReviewRoleConfigOut.model_fields) == (
        "config_id",
        "config_status",
        "config_snapshot_hash",
        "current_identity_key",
        "disposition",
    )
    for schema in (PublishGrantManualReviewRoleConfigIn, RevokeGrantManualReviewRoleConfigIn):
        assert schema.model_config["extra"] == "forbid"
        assert all(field.is_required() for field in schema.model_fields.values())
    PublishGrantManualReviewRoleConfigIn.model_validate(_publish_body())
    for change in (
        {"confirmed_by": ACTOR_ID},
        {"official_copy_acquirer_role_id": "not-a-uuid"},
        {"effective_from": datetime.now(timezone.utc)},
        {"effective_to": EFFECTIVE_FROM},
        {"config_version": " bad"},
    ):
        with pytest.raises(ValidationError):
            PublishGrantManualReviewRoleConfigIn.model_validate(_publish_body() | change)


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantManualReviewRoleDisposition.CREATED, 201),
        (GrantManualReviewRoleDisposition.REUSED, 200),
    ),
)
def test_publish_maps_exact_command_actor_time_and_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantManualReviewRoleDisposition,
    expected_status: int,
) -> None:
    captured: list[PublishGrantManualReviewRoleConfigCommand] = []

    def service(command: object, transaction: object) -> GrantManualReviewRoleConfigResult:
        assert isinstance(command, PublishGrantManualReviewRoleConfigCommand)
        captured.append(command)
        return _result(disposition)

    path = "/system/grant-manual-review-role-configurations"
    client, session = _client(
        monkeypatch,
        route_path=path,
        service_name="publish_grant_manual_review_role_config",
        service=service,
    )
    response = client.post(f"/api/v1{path}", json=_publish_body())
    assert response.status_code == expected_status
    assert captured == [
        PublishGrantManualReviewRoleConfigCommand(
            official_copy_acquirer_role_id=ROLE_IDS[0],
            first_verifier_role_id=ROLE_IDS[1],
            second_verifier_role_id=ROLE_IDS[2],
            manual_review_proposer_role_id=ROLE_IDS[3],
            manual_review_second_reviewer_role_id=ROLE_IDS[4],
            config_version="grant-manual-review-role-v1",
            effective_from=EFFECTIVE_FROM,
            effective_to=EFFECTIVE_TO,
            confirmed_by=ACTOR_ID,
            published_at=NOW,
            expected_current_config_id=None,
            idempotency_key="publish-grant-manual-review-role-v1",
        )
    ]
    assert response.json() == GrantManualReviewRoleConfigOut.model_validate(
        _result(disposition), from_attributes=True
    ).model_dump(mode="json")
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantManualReviewRoleDisposition.CREATED, 201),
        (GrantManualReviewRoleDisposition.REUSED, 200),
    ),
)
def test_revoke_maps_exact_command_and_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantManualReviewRoleDisposition,
    expected_status: int,
) -> None:
    captured: list[RevokeGrantManualReviewRoleConfigCommand] = []

    def service(command: object, transaction: object) -> GrantManualReviewRoleConfigResult:
        assert isinstance(command, RevokeGrantManualReviewRoleConfigCommand)
        captured.append(command)
        return _result(disposition, status="REVOKED")

    route = "/system/grant-manual-review-role-configurations/{config_id}/revoke"
    client, session = _client(
        monkeypatch,
        route_path=route,
        service_name="revoke_grant_manual_review_role_config",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-manual-review-role-configurations/{CONFIG_ID}/revoke",
        json=_revoke_body(),
    )
    assert response.status_code == expected_status
    assert captured == [
        RevokeGrantManualReviewRoleConfigCommand(
            config_version="grant-manual-review-role-v2-revoked",
            effective_from=EFFECTIVE_FROM,
            confirmed_by=ACTOR_ID,
            published_at=NOW,
            expected_current_config_id=CONFIG_ID,
            idempotency_key="revoke-grant-manual-review-role-v2",
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_revoke_rejects_path_body_mismatch_before_service_or_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def service(command: object, transaction: object) -> GrantManualReviewRoleConfigResult:
        calls.append(command)
        return _result(GrantManualReviewRoleDisposition.CREATED)

    route = "/system/grant-manual-review-role-configurations/{config_id}/revoke"
    client, session = _client(
        monkeypatch,
        route_path=route,
        service_name="revoke_grant_manual_review_role_config",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-manual-review-role-configurations/{OTHER_CONFIG_ID}/revoke",
        json=_revoke_body(),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert calls == []
    assert (session.commit_calls, session.rollback_calls) == (0, 0)


def test_permission_and_transaction_failures_never_commit_product_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def service(command: object, transaction: object) -> GrantManualReviewRoleConfigResult:
        calls.append(command)
        raise BusinessError("TEST_CONFLICT", "test", status_code=409)

    path = "/system/grant-manual-review-role-configurations"
    client, session = _client(
        monkeypatch,
        route_path=path,
        service_name="publish_grant_manual_review_role_config",
        service=service,
    )
    response = client.post(f"/api/v1{path}", json=_publish_body())
    assert response.status_code == 409
    assert len(calls) == 1
    assert (session.commit_calls, session.rollback_calls) == (0, 1)

    calls.clear()
    denied_client, denied_session = _client(
        monkeypatch,
        route_path=path,
        service_name="publish_grant_manual_review_role_config",
        service=lambda command, transaction: _result(
            GrantManualReviewRoleDisposition.CREATED
        ),
        permission_error=BusinessError("FORBIDDEN", "forbidden", status_code=403),
    )
    denied = denied_client.post(f"/api/v1{path}", json=_publish_body())
    assert denied.status_code == 403
    assert (denied_session.commit_calls, denied_session.rollback_calls) == (0, 0)

    failing_session = RecordingSession(commit_error=RuntimeError("commit failed"))
    monkeypatch.setattr(
        system_api,
        "publish_grant_manual_review_role_config",
        lambda command, transaction: _result(GrantManualReviewRoleDisposition.CREATED),
    )
    with pytest.raises(RuntimeError, match="commit failed"):
        system_api.create_grant_manual_review_role_configuration(
            payload=PublishGrantManualReviewRoleConfigIn.model_validate(_publish_body()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=failing_session,
        )
    assert (failing_session.commit_calls, failing_session.rollback_calls) == (1, 1)
