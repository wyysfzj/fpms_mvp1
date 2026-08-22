from __future__ import annotations

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
from app.modules.system import api as system_api
from app.modules.system.grant_evidence_source_schemas import (
    ActivateGrantEvidenceSourceIn,
    GrantEvidenceSourceConfigOut,
    GrantEvidenceSourceRecordOut,
    PublishGrantEvidenceSourceConfigIn,
    RegisterGrantEvidenceSourceIn,
    RetireGrantEvidenceSourceIn,
    ReviewGrantEvidenceSourceIn,
    RevokeGrantEvidenceSourceConfigIn,
)
from app.modules.system.grant_evidence_source_service import (
    ActivateGrantEvidenceSourceCommand,
    GrantEvidenceScope,
    GrantEvidenceSourceConfigResult,
    GrantEvidenceSourceDisposition,
    GrantEvidenceSourceRecordResult,
    GrantEvidenceSourceReferenceKind,
    GrantEvidenceSourceReviewDecision,
    PublishGrantEvidenceSourceConfigCommand,
    RegisterGrantEvidenceSourceCommand,
    RetireGrantEvidenceSourceCommand,
    ReviewGrantEvidenceSourceCommand,
    RevokeGrantEvidenceSourceConfigCommand,
)

ACTOR_ID = "11111111-1111-4111-8111-111111111111"
SOURCE_ID = "22222222-2222-4222-8222-222222222222"
OTHER_SOURCE_ID = "33333333-3333-4333-8333-333333333333"
CONFIG_ID = "44444444-4444-4444-8444-444444444444"
OTHER_CONFIG_ID = "55555555-5555-4555-8555-555555555555"
EFFECTIVE_FROM = datetime(2026, 8, 10, 9, 0)
EFFECTIVE_TO = datetime(2027, 8, 10, 9, 0)
NOW = datetime(2026, 8, 10, 10, 30)


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
        raise AssertionError("source API queried carrier tables")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("source API flushed before service delegation")


def _record_result(
    disposition: GrantEvidenceSourceDisposition = GrantEvidenceSourceDisposition.CHANGED,
) -> GrantEvidenceSourceRecordResult:
    return GrantEvidenceSourceRecordResult(
        source_record_id=SOURCE_ID,
        review_status="APPROVED",
        activation_status="ACTIVE",
        source_snapshot_hash="a" * 64,
        current_identity_key="CNIPA|GRANT_ANNOUNCEMENT|CNIPA-GRANT",
        disposition=disposition,
    )


def _config_result(
    disposition: GrantEvidenceSourceDisposition = GrantEvidenceSourceDisposition.CREATED,
) -> GrantEvidenceSourceConfigResult:
    return GrantEvidenceSourceConfigResult(
        config_id=CONFIG_ID,
        config_status="ACTIVE",
        config_snapshot_hash="b" * 64,
        current_identity_key="DG-GRANT-EVIDENCE-SOURCE|GLOBAL|GRANT_ANNOUNCEMENT",
        disposition=disposition,
    )


def _register_body() -> dict[str, object]:
    return {
        "source_code": "CNIPA-GRANT",
        "source_version": "2026-08-10",
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "source_reference_kind": "QUERY_CHANNEL",
        "source_reference_value": "CNIPA reviewed query channel",
        "acquisition_method": "controlled download",
        "effective_from": EFFECTIVE_FROM.isoformat(),
        "effective_to": EFFECTIVE_TO.isoformat(),
        "supersedes_source_id": None,
        "idempotency_key": "register-source-1",
    }


def _publish_body() -> dict[str, object]:
    return {
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "source_record_id": SOURCE_ID,
        "config_version": "grant-source-config-v1",
        "effective_from": EFFECTIVE_FROM.isoformat(),
        "effective_to": EFFECTIVE_TO.isoformat(),
        "selection_reason": "机构管理员选择已审核来源",
        "expected_current_config_id": None,
        "idempotency_key": "publish-source-config-1",
    }


def _revoke_body() -> dict[str, object]:
    return {
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "config_version": "grant-source-config-v2-revoked",
        "effective_from": EFFECTIVE_FROM.isoformat(),
        "selection_reason": "机构管理员撤销当前来源",
        "expected_current_config_id": CONFIG_ID,
        "idempotency_key": "revoke-source-config-1",
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
    service: Callable[[object, object], object],
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
    assert tuple(RegisterGrantEvidenceSourceIn.model_fields) == (
        "source_code",
        "source_version",
        "evidence_scope",
        "source_reference_kind",
        "source_reference_value",
        "acquisition_method",
        "effective_from",
        "effective_to",
        "supersedes_source_id",
        "idempotency_key",
    )
    assert tuple(ReviewGrantEvidenceSourceIn.model_fields) == ("decision", "reason")
    assert tuple(ActivateGrantEvidenceSourceIn.model_fields) == ("expected_current_source_id",)
    assert tuple(RetireGrantEvidenceSourceIn.model_fields) == ("expected_current_source_id",)
    assert tuple(PublishGrantEvidenceSourceConfigIn.model_fields) == (
        "evidence_scope",
        "source_record_id",
        "config_version",
        "effective_from",
        "effective_to",
        "selection_reason",
        "expected_current_config_id",
        "idempotency_key",
    )
    assert tuple(RevokeGrantEvidenceSourceConfigIn.model_fields) == (
        "evidence_scope",
        "config_version",
        "effective_from",
        "selection_reason",
        "expected_current_config_id",
        "idempotency_key",
    )
    assert tuple(GrantEvidenceSourceRecordOut.model_fields) == (
        "source_record_id",
        "review_status",
        "activation_status",
        "source_snapshot_hash",
        "current_identity_key",
        "disposition",
    )
    assert tuple(GrantEvidenceSourceConfigOut.model_fields) == (
        "config_id",
        "config_status",
        "config_snapshot_hash",
        "current_identity_key",
        "disposition",
    )
    for schema in (
        RegisterGrantEvidenceSourceIn,
        ReviewGrantEvidenceSourceIn,
        ActivateGrantEvidenceSourceIn,
        RetireGrantEvidenceSourceIn,
        PublishGrantEvidenceSourceConfigIn,
        RevokeGrantEvidenceSourceConfigIn,
    ):
        assert schema.model_config["extra"] == "forbid"
        assert all(field.is_required() for field in schema.model_fields.values())


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantEvidenceSourceDisposition.CREATED, 201),
        (GrantEvidenceSourceDisposition.REUSED, 200),
    ),
)
def test_register_maps_exact_command_actor_and_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantEvidenceSourceDisposition,
    expected_status: int,
) -> None:
    captured: list[RegisterGrantEvidenceSourceCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceRecordResult:
        assert isinstance(command, RegisterGrantEvidenceSourceCommand)
        captured.append(command)
        return _record_result(disposition)

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources",
        service_name="register_grant_evidence_source",
        service=service,
    )
    response = client.post("/api/v1/system/grant-evidence-sources", json=_register_body())
    assert response.status_code == expected_status
    assert captured == [
        RegisterGrantEvidenceSourceCommand(
            source_code="CNIPA-GRANT",
            source_version="2026-08-10",
            evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
            source_reference_kind=GrantEvidenceSourceReferenceKind.QUERY_CHANNEL,
            source_reference_value="CNIPA reviewed query channel",
            acquisition_method="controlled download",
            effective_from=EFFECTIVE_FROM,
            effective_to=EFFECTIVE_TO,
            supersedes_source_id=None,
            actor_id=ACTOR_ID,
            idempotency_key="register-source-1",
        )
    ]
    assert response.json() == GrantEvidenceSourceRecordOut.model_validate(
        _record_result(disposition), from_attributes=True
    ).model_dump(mode="json")
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_review_maps_path_actor_and_single_server_time(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[ReviewGrantEvidenceSourceCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceRecordResult:
        assert isinstance(command, ReviewGrantEvidenceSourceCommand)
        captured.append(command)
        return _record_result()

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources/{source_record_id}/review",
        service_name="review_grant_evidence_source",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-evidence-sources/{SOURCE_ID}/review",
        json={"decision": "APPROVED", "reason": "独立复核通过"},
    )
    assert response.status_code == 200
    assert captured == [
        ReviewGrantEvidenceSourceCommand(
            source_record_id=SOURCE_ID,
            decision=GrantEvidenceSourceReviewDecision.APPROVED,
            reviewer_id=ACTOR_ID,
            reviewed_at=NOW,
            reason="独立复核通过",
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_activate_passes_different_predecessor_without_path_rejection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[ActivateGrantEvidenceSourceCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceRecordResult:
        assert isinstance(command, ActivateGrantEvidenceSourceCommand)
        captured.append(command)
        return _record_result()

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources/{source_record_id}/activate",
        service_name="activate_grant_evidence_source",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-evidence-sources/{SOURCE_ID}/activate",
        json={"expected_current_source_id": OTHER_SOURCE_ID},
    )
    assert response.status_code == 200
    assert captured == [
        ActivateGrantEvidenceSourceCommand(
            source_record_id=SOURCE_ID,
            actor_id=ACTOR_ID,
            activated_at=NOW,
            expected_current_source_id=OTHER_SOURCE_ID,
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_retire_requires_path_body_identity_and_maps_exact_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[RetireGrantEvidenceSourceCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceRecordResult:
        assert isinstance(command, RetireGrantEvidenceSourceCommand)
        captured.append(command)
        return _record_result()

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources/{source_record_id}/retire",
        service_name="retire_grant_evidence_source",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-evidence-sources/{SOURCE_ID}/retire",
        json={"expected_current_source_id": SOURCE_ID},
    )
    assert response.status_code == 200
    assert captured == [
        RetireGrantEvidenceSourceCommand(
            source_record_id=SOURCE_ID,
            actor_id=ACTOR_ID,
            retired_at=NOW,
            expected_current_source_id=SOURCE_ID,
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantEvidenceSourceDisposition.CREATED, 201),
        (GrantEvidenceSourceDisposition.REUSED, 200),
    ),
)
def test_publish_config_maps_exact_command_actor_time_and_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantEvidenceSourceDisposition,
    expected_status: int,
) -> None:
    captured: list[PublishGrantEvidenceSourceConfigCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceConfigResult:
        assert isinstance(command, PublishGrantEvidenceSourceConfigCommand)
        captured.append(command)
        return _config_result(disposition)

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-source-configurations",
        service_name="publish_grant_evidence_source_config",
        service=service,
    )
    response = client.post(
        "/api/v1/system/grant-evidence-source-configurations", json=_publish_body()
    )
    assert response.status_code == expected_status
    assert captured == [
        PublishGrantEvidenceSourceConfigCommand(
            evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
            source_record_id=SOURCE_ID,
            config_version="grant-source-config-v1",
            effective_from=EFFECTIVE_FROM,
            effective_to=EFFECTIVE_TO,
            selected_by=ACTOR_ID,
            published_at=NOW,
            selection_reason="机构管理员选择已审核来源",
            expected_current_config_id=None,
            idempotency_key="publish-source-config-1",
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


@pytest.mark.parametrize(
    ("disposition", "expected_status"),
    (
        (GrantEvidenceSourceDisposition.CREATED, 201),
        (GrantEvidenceSourceDisposition.REUSED, 200),
    ),
)
def test_revoke_config_requires_identity_and_maps_exact_success(
    monkeypatch: pytest.MonkeyPatch,
    disposition: GrantEvidenceSourceDisposition,
    expected_status: int,
) -> None:
    captured: list[RevokeGrantEvidenceSourceConfigCommand] = []

    def service(command: object, transaction: object) -> GrantEvidenceSourceConfigResult:
        assert isinstance(command, RevokeGrantEvidenceSourceConfigCommand)
        captured.append(command)
        return _config_result(disposition)

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-source-configurations/{config_id}/revoke",
        service_name="revoke_grant_evidence_source_config",
        service=service,
    )
    response = client.post(
        f"/api/v1/system/grant-evidence-source-configurations/{CONFIG_ID}/revoke",
        json=_revoke_body(),
    )
    assert response.status_code == expected_status
    assert captured == [
        RevokeGrantEvidenceSourceConfigCommand(
            evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
            config_version="grant-source-config-v2-revoked",
            effective_from=EFFECTIVE_FROM,
            selected_by=ACTOR_ID,
            published_at=NOW,
            selection_reason="机构管理员撤销当前来源",
            expected_current_config_id=CONFIG_ID,
            idempotency_key="revoke-source-config-1",
        )
    ]
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


@pytest.mark.parametrize(
    ("path", "route_path", "service_name", "body"),
    (
        (
            f"/api/v1/system/grant-evidence-sources/{SOURCE_ID}/retire",
            "/system/grant-evidence-sources/{source_record_id}/retire",
            "retire_grant_evidence_source",
            {"expected_current_source_id": OTHER_SOURCE_ID},
        ),
        (
            f"/api/v1/system/grant-evidence-source-configurations/{CONFIG_ID}/revoke",
            "/system/grant-evidence-source-configurations/{config_id}/revoke",
            "revoke_grant_evidence_source_config",
            {**_revoke_body(), "expected_current_config_id": OTHER_CONFIG_ID},
        ),
    ),
)
def test_path_body_mismatch_is_422_before_service_or_transaction(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    route_path: str,
    service_name: str,
    body: dict[str, object],
) -> None:
    calls = 0

    def service(command: object, transaction: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("service must not be called")

    client, session = _client(
        monkeypatch,
        route_path=route_path,
        service_name=service_name,
        service=service,
    )
    response = client.post(path, json=body)
    assert response.status_code == 422
    assert calls == 0
    assert (session.commit_calls, session.rollback_calls) == (0, 0)


@pytest.mark.parametrize(
    ("schema", "body"),
    (
        (ReviewGrantEvidenceSourceIn, {"decision": "UNKNOWN", "reason": "r"}),
        (ReviewGrantEvidenceSourceIn, {"decision": "APPROVED", "reason": " "}),
        (
            RegisterGrantEvidenceSourceIn,
            {**_register_body(), "effective_to": EFFECTIVE_FROM.isoformat()},
        ),
        (RegisterGrantEvidenceSourceIn, {**_register_body(), "idempotency_key": ""}),
        (RegisterGrantEvidenceSourceIn, {**_register_body(), "source_code": "x" * 65}),
        (RegisterGrantEvidenceSourceIn, {**_register_body(), "actor_id": ACTOR_ID}),
        (PublishGrantEvidenceSourceConfigIn, {**_publish_body(), "config_version": " "}),
        (PublishGrantEvidenceSourceConfigIn, {**_publish_body(), "published_at": NOW}),
        (RevokeGrantEvidenceSourceConfigIn, {**_revoke_body(), "selected_by": ACTOR_ID}),
    ),
)
def test_invalid_or_client_owned_authority_fields_are_rejected(
    schema: type[object], body: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        schema.model_validate(body)  # type: ignore[attr-defined]


def test_malformed_path_uuid_is_422_before_service(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def service(command: object, transaction: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("service must not be called")

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources/{source_record_id}/review",
        service_name="review_grant_evidence_source",
        service=service,
    )
    response = client.post(
        "/api/v1/system/grant-evidence-sources/not-a-uuid/review",
        json={"decision": "APPROVED", "reason": "valid reason"},
    )
    assert response.status_code == 422
    assert calls == 0
    assert (session.commit_calls, session.rollback_calls) == (0, 0)


def test_service_conflict_is_preserved_with_one_rollback(monkeypatch: pytest.MonkeyPatch) -> None:
    conflict = BusinessError(
        "GRANT_EVIDENCE_SOURCE_CONFLICT",
        "Grant evidence source conflict",
        status_code=409,
    )

    def service(command: object, transaction: object) -> object:
        raise conflict

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources",
        service_name="register_grant_evidence_source",
        service=service,
    )
    response = client.post("/api/v1/system/grant-evidence-sources", json=_register_body())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "GRANT_EVIDENCE_SOURCE_CONFLICT"
    assert (session.commit_calls, session.rollback_calls) == (0, 1)


def test_commit_failure_rolls_back_once_and_is_not_converted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = RuntimeError("commit failed")
    session = RecordingSession(commit_error=failure)

    def service(command: object, transaction: object) -> GrantEvidenceSourceRecordResult:
        return _record_result(GrantEvidenceSourceDisposition.CREATED)

    monkeypatch.setattr(system_api, "register_grant_evidence_source", service)
    with pytest.raises(RuntimeError) as raised:
        system_api.create_grant_evidence_source(
            payload=RegisterGrantEvidenceSourceIn.model_validate(_register_body()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )
    assert raised.value is failure
    assert (session.commit_calls, session.rollback_calls) == (1, 1)


def test_permission_failure_precedes_service_and_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def service(command: object, transaction: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("service must not be called")

    client, session = _client(
        monkeypatch,
        route_path="/system/grant-evidence-sources",
        service_name="register_grant_evidence_source",
        service=service,
        permission_error=BusinessError("FORBIDDEN", "Forbidden", status_code=403),
    )
    response = client.post("/api/v1/system/grant-evidence-sources", json=_register_body())
    assert response.status_code == 403
    assert calls == 0
    assert (session.commit_calls, session.rollback_calls) == (0, 0)


def test_missing_authentication_is_401_before_service_or_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    session = RecordingSession()

    def service(command: object, transaction: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("service must not be called")

    monkeypatch.setattr(system_api, "register_grant_evidence_source", service)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[
        _permission_dependency("/system/grant-evidence-sources")
    ] = lambda: None
    response = TestClient(app).post(
        "/api/v1/system/grant-evidence-sources",
        json=_register_body(),
    )
    assert response.status_code == 401
    assert calls == 0
    assert (session.commit_calls, session.rollback_calls) == (0, 0)
