from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.documents import api as documents_api
from app.modules.documents.evidence_contracts import EvidenceReviewState
from app.modules.documents.evidence_service import (
    EvidenceReviewDecision,
    ReviewEvidenceVersionCommand,
    ReviewEvidenceVersionResult,
)

PATH = "/api/v1/documents/evidence-versions/evidence-1/review"
ROUTER_PATH = "/documents/evidence-versions/{evidence_version_id}/review"
EVIDENCE_VERSION_ID = "evidence-1"
ACTOR_ID = "reviewer-1"
REVIEWED_AT = datetime(2026, 7, 15, 10, 30)
INPUT_FIELDS = (
    "case_id",
    "decision",
    "reviewed_at",
    "idempotency_key",
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
        raise AssertionError("review adapter must return the direct service result")


def _request_data(
    *,
    decision: str = "APPROVE",
    idempotency_key: str = "review-1",
) -> dict[str, object]:
    return {
        "case_id": "case-1",
        "decision": decision,
        "reviewed_at": "2026-07-15T10:30:00",
        "idempotency_key": idempotency_key,
    }


def _result(
    *,
    decision: EvidenceReviewDecision = EvidenceReviewDecision.APPROVE,
    reused: bool = False,
    idempotency_key: str = "review-1",
) -> ReviewEvidenceVersionResult:
    return ReviewEvidenceVersionResult(
        case_id="case-1",
        evidence_version_id=EVIDENCE_VERSION_ID,
        creator_id="creator-1",
        reviewer_id=ACTOR_ID,
        decision=decision,
        review_state=(
            EvidenceReviewState.APPROVED
            if decision is EvidenceReviewDecision.APPROVE
            else EvidenceReviewState.REJECTED
        ),
        reviewed_at=REVIEWED_AT,
        activity_id="activity-1",
        activity_sequence=1,
        lifecycle_revision=1,
        idempotency_key=idempotency_key,
        reused=reused,
    )


def _route() -> APIRoute:
    matching = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"POST"}
    ]
    assert len(matching) == 1
    return matching[0]


def _payload_type() -> type[BaseModel]:
    payload_type = get_type_hints(_route().endpoint)["payload"]
    assert isinstance(payload_type, type)
    assert issubclass(payload_type, BaseModel)
    return payload_type


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_result: ReviewEvidenceVersionResult | None = None,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[
    TestClient,
    RecordingSession,
    list[ReviewEvidenceVersionCommand],
]:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)
    captured: list[ReviewEvidenceVersionCommand] = []

    def service(
        command: ReviewEvidenceVersionCommand,
        transaction: object,
    ) -> ReviewEvidenceVersionResult:
        assert transaction is session
        captured.append(command)
        if service_error is not None:
            raise service_error
        assert service_result is not None
        return service_result

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(documents_api, "review_evidence_version", service, raising=False)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session, captured


def test_strict_body_has_exact_order_types_and_only_required_client_fields() -> None:
    payload_type = _payload_type()

    assert tuple(payload_type.model_fields) == INPUT_FIELDS
    assert get_type_hints(payload_type) == {
        "case_id": str,
        "decision": EvidenceReviewDecision,
        "reviewed_at": datetime,
        "idempotency_key": str,
    }
    assert payload_type.model_config["extra"] == "forbid"
    assert all(field.is_required() for field in payload_type.model_fields.values())
    assert payload_type.model_validate(_request_data()).model_dump() == {
        "case_id": "case-1",
        "decision": EvidenceReviewDecision.APPROVE,
        "reviewed_at": REVIEWED_AT,
        "idempotency_key": "review-1",
    }

    for client_owned_field in ("evidence_version_id", "reviewer_id"):
        with pytest.raises(ValidationError):
            payload_type.model_validate({**_request_data(), client_owned_field: "client-owned"})


def test_route_is_one_post_with_doc_edit_server_actor_and_direct_service_result() -> None:
    route = _route()

    assert route.status_code == 200
    assert route.response_model is ReviewEvidenceVersionResult
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    assert list(inspect.signature(route.endpoint).parameters) == [
        "evidence_version_id",
        "payload",
        "_perm",
        "current_user",
        "db",
    ]


@pytest.mark.parametrize(
    ("decision", "reused", "idempotency_key"),
    (
        (EvidenceReviewDecision.APPROVE, False, "approve-fresh"),
        (EvidenceReviewDecision.APPROVE, True, "approve-replay"),
        (EvidenceReviewDecision.REJECT, False, "reject-fresh"),
        (EvidenceReviewDecision.REJECT, True, "reject-replay"),
    ),
)
def test_fresh_and_replay_delegate_once_commit_once_and_return_direct_200(
    monkeypatch: pytest.MonkeyPatch,
    decision: EvidenceReviewDecision,
    reused: bool,
    idempotency_key: str,
) -> None:
    result = _result(
        decision=decision,
        reused=reused,
        idempotency_key=idempotency_key,
    )
    client, session, captured = _client(monkeypatch, service_result=result)

    response = client.post(
        PATH,
        json=_request_data(
            decision=decision.value,
            idempotency_key=idempotency_key,
        ),
    )

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(result)
    assert "data" not in response.json()
    assert captured == [
        ReviewEvidenceVersionCommand(
            case_id="case-1",
            evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=ACTOR_ID,
            decision=decision,
            reviewed_at=REVIEWED_AT,
            idempotency_key=idempotency_key,
        )
    ]
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    ("status_code", "code"),
    (
        (400, "EVIDENCE_REVIEW_INVALID"),
        (400, "EVIDENCE_REVIEW_CASE_MISMATCH"),
        (404, "CASE_NOT_FOUND"),
        (404, "EVIDENCE_VERSION_NOT_FOUND"),
        (409, "EVIDENCE_REVIEW_STATE_CONFLICT"),
        (409, "EVIDENCE_REVIEW_SELF_REVIEW"),
        (409, "LIFECYCLE_IDEMPOTENCY_CONFLICT"),
        (409, "EVIDENCE_REVIEW_ALREADY_DECIDED"),
        (409, "EVIDENCE_REVIEW_CONCURRENCY_CONFLICT"),
        (409, "EVIDENCE_REVIEW_HISTORY_CONFLICT"),
    ),
)
def test_service_errors_pass_through_unchanged_and_roll_back_once(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    error = BusinessError(
        code,
        "service error",
        details={"marker": code},
        status_code=status_code,
    )
    client, session, captured = _client(monkeypatch, service_error=error)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "service error",
            "details": {"marker": code},
        }
    }
    assert len(captured) == 1
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_commit_failure_rolls_back_once_and_reraises_original_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = RuntimeError("commit failed")
    session = RecordingSession(commit_error=error)
    monkeypatch.setattr(
        documents_api,
        "review_evidence_version",
        lambda *_args: _result(),
        raising=False,
    )
    payload = _payload_type().model_validate(_request_data())

    with pytest.raises(RuntimeError) as exc_info:
        _route().endpoint(
            evidence_version_id=EVIDENCE_VERSION_ID,
            payload=payload,
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


def test_authentication_and_doc_edit_permission_preserve_401_and_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unauthenticated_session = RecordingSession()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: unauthenticated_session
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        unauthenticated = client.post(PATH, json=_request_data())

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"
    assert unauthenticated_session.commit_calls == 0
    assert unauthenticated_session.rollback_calls == 0

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "Doc.Edit"},
        status_code=403,
    )
    client, session, captured = _client(
        monkeypatch,
        service_result=_result(),
        permission_error=forbidden,
    )
    response = client.post(PATH, json=_request_data())

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Doc.Edit"},
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    "invalid",
    (
        {key: value for key, value in _request_data().items() if key != "case_id"},
        {key: value for key, value in _request_data().items() if key != "decision"},
        {key: value for key, value in _request_data().items() if key != "reviewed_at"},
        {key: value for key, value in _request_data().items() if key != "idempotency_key"},
        {**_request_data(), "unexpected": True},
        {**_request_data(), "evidence_version_id": EVIDENCE_VERSION_ID},
        {**_request_data(), "reviewer_id": "client-reviewer"},
        {**_request_data(), "decision": "UNKNOWN"},
        {**_request_data(), "case_id": 1},
        {**_request_data(), "idempotency_key": 1},
        {**_request_data(), "reviewed_at": "not-a-datetime"},
        {**_request_data(), "reviewed_at": "2026-07-15T10:30:00+08:00"},
    ),
)
def test_missing_extra_wrong_type_enum_and_datetime_inputs_return_422(
    monkeypatch: pytest.MonkeyPatch,
    invalid: dict[str, object],
) -> None:
    client, session, captured = _client(
        monkeypatch,
        service_result=_result(),
    )

    response = client.post(PATH, json=invalid)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_no_secondary_approve_reject_or_body_id_routes_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _session, _captured = _client(
        monkeypatch,
        service_result=_result(),
    )

    assert client.post(f"{PATH}/approve", json=_request_data()).status_code == 404
    assert client.post(f"{PATH}/reject", json=_request_data()).status_code == 404
    assert (
        client.post(
            "/api/v1/documents/evidence-versions/review",
            json={**_request_data(), "evidence_version_id": EVIDENCE_VERSION_ID},
        ).status_code
        == 404
    )
