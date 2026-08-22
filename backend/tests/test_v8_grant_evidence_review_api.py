from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import Callable

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.documents import api as documents_api
from app.modules.documents import grant_evidence_schemas as grant_schemas
from app.modules.documents.grant_evidence_review_service import (
    GrantEvidenceReviewDecision,
    GrantEvidenceReviewDisposition,
    ReviewGrantEvidenceCandidateCommand,
    ReviewGrantEvidenceCandidateResult,
)

PATH = "/documents/grant-evidence-candidates/{candidate_id}/review"
CANDIDATE_ID = "11111111-1111-4111-8111-111111111111"
EVIDENCE_ID = "21111111-1111-4111-8111-111111111111"
REVIEWER_ID = "31111111-1111-4111-8111-111111111111"
ROLE_CONFIG_ID = "41111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 11, 11, 0, 0, 123456)


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
        raise AssertionError("review API queried product tables before delegation")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("review API flushed before delegation")


def _body(decision: str = "APPROVED") -> dict[str, object]:
    return {"decision": decision, "reason": "second-person review"}


def _result(
    *,
    review_status: str = "APPROVED",
    disposition: GrantEvidenceReviewDisposition = GrantEvidenceReviewDisposition.CHANGED,
) -> ReviewGrantEvidenceCandidateResult:
    return ReviewGrantEvidenceCandidateResult(
        candidate_id=CANDIDATE_ID,
        evidence_version_id=EVIDENCE_ID,
        review_status=review_status,
        reviewer_id=REVIEWER_ID,
        reviewed_at=NOW,
        candidate_snapshot_hash="a" * 64,
        review_role_config_id=ROLE_CONFIG_ID,
        review_role_config_snapshot_hash="b" * 64,
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
    review_service: Callable[[object, object], ReviewGrantEvidenceCandidateResult],
    *,
    session: RecordingSession | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession, list[datetime]]:
    transaction = session or RecordingSession()
    clock_calls: list[datetime] = []

    def now() -> datetime:
        clock_calls.append(NOW)
        return NOW

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(
        documents_api,
        "review_grant_evidence_candidate",
        review_service,
        raising=False,
    )
    monkeypatch.setattr(documents_api, "_utc_now", now)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=REVIEWER_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), transaction, clock_calls


def test_schema_route_and_permission_contract_are_exact() -> None:
    review_in = grant_schemas.GrantEvidenceReviewIn
    review_out = grant_schemas.GrantEvidenceReviewOut
    assert tuple(review_in.model_fields) == ("decision", "reason")
    assert tuple(review_out.model_fields) == (
        "candidate_id",
        "evidence_version_id",
        "review_status",
        "reviewer_id",
        "reviewed_at",
        "candidate_snapshot_hash",
        "review_role_config_id",
        "review_role_config_snapshot_hash",
        "disposition",
    )
    assert review_in.model_config["extra"] == "forbid"
    assert review_out.model_config["extra"] == "forbid"
    assert review_out.model_config["from_attributes"] is True
    route = _route()
    assert route.status_code == 200
    assert route.response_model is review_out
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert (
        len(
            [
                candidate
                for candidate in documents_api.router.routes
                if isinstance(candidate, APIRoute)
                and candidate.path == PATH
                and candidate.methods == {"POST"}
            ]
        )
        == 1
    )


@pytest.mark.parametrize(
    ("decision", "review_status", "disposition"),
    (
        (
            GrantEvidenceReviewDecision.APPROVED,
            "APPROVED",
            GrantEvidenceReviewDisposition.CHANGED,
        ),
        (
            GrantEvidenceReviewDecision.APPROVED,
            "APPROVED",
            GrantEvidenceReviewDisposition.REUSED,
        ),
        (
            GrantEvidenceReviewDecision.REJECTED,
            "REJECTED",
            GrantEvidenceReviewDisposition.CHANGED,
        ),
    ),
)
def test_route_injects_path_reviewer_one_server_time_and_commits_once(
    monkeypatch,
    decision,
    review_status,
    disposition,
) -> None:
    captured: list[tuple[ReviewGrantEvidenceCandidateCommand, object]] = []
    result = _result(review_status=review_status, disposition=disposition)

    def review_service(command: object, transaction: object) -> ReviewGrantEvidenceCandidateResult:
        assert type(command) is ReviewGrantEvidenceCandidateCommand
        captured.append((command, transaction))
        return result

    client, session, clock_calls = _client(monkeypatch, review_service)
    response = client.post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body(decision.value),
    )
    assert response.status_code == 200
    assert captured == [
        (
            ReviewGrantEvidenceCandidateCommand(
                candidate_id=CANDIDATE_ID,
                decision=decision,
                reviewer_id=REVIEWER_ID,
                reviewed_at=NOW,
                reason="second-person review",
            ),
            session,
        )
    ]
    assert clock_calls == [NOW]
    assert response.json() == grant_schemas.GrantEvidenceReviewOut.model_validate(
        result, from_attributes=True
    ).model_dump(mode="json")
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


@pytest.mark.parametrize(
    "change",
    (
        {"decision": "UNKNOWN"},
        {"reason": " "},
        {"reason": "x" * 4097},
        {"reviewer_id": REVIEWER_ID},
        {"reviewed_at": NOW.isoformat()},
        {"candidate_id": CANDIDATE_ID},
    ),
)
def test_strict_payload_and_path_validation_return_422_before_service(monkeypatch, change) -> None:
    calls: list[object] = []

    def review_service(command: object, _transaction: object) -> ReviewGrantEvidenceCandidateResult:
        calls.append(command)
        return _result()

    client, session, clock_calls = _client(monkeypatch, review_service)
    response = client.post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body() | change,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert calls == []
    assert clock_calls == []
    assert (session.commit_calls, session.rollback_calls) == (0, 0)

    invalid_path = client.post(
        "/api/v1/documents/grant-evidence-candidates/not-a-uuid/review",
        json=_body(),
    )
    assert invalid_path.status_code == 422
    assert calls == []


@pytest.mark.parametrize(
    "error",
    (
        BusinessError("GRANT_EVIDENCE_REVIEW_INPUT_INVALID", "invalid", status_code=400),
        BusinessError("GRANT_EVIDENCE_REVIEW_NOT_FOUND", "missing", status_code=404),
        BusinessError("GRANT_EVIDENCE_REVIEW_ROLE_CONFLICT", "role", status_code=409),
        BusinessError("GRANT_ANNOUNCEMENT_EVIDENCE_CONFLICT", "source", status_code=409),
        BusinessError("GRANT_EVIDENCE_REVIEW_CONFLICT", "conflict", status_code=409),
    ),
)
def test_service_errors_preserve_status_envelope_and_rollback(
    monkeypatch, error: BusinessError
) -> None:
    calls: list[object] = []

    def fail(command: object, _transaction: object) -> ReviewGrantEvidenceCandidateResult:
        calls.append(command)
        raise error

    client, session, clock_calls = _client(monkeypatch, fail)
    response = client.post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body(),
    )
    assert response.status_code == error.status_code
    assert response.json() == {
        "error": {"code": error.code, "message": error.message, "details": None}
    }
    assert len(calls) == 1
    assert clock_calls == [NOW]
    assert (session.commit_calls, session.rollback_calls) == (0, 1)


def test_unknown_candidate_uses_real_service_not_found_envelope(session_factory) -> None:
    with session_factory() as transaction:
        app = create_app()
        app.dependency_overrides[get_db] = lambda: transaction
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=REVIEWER_ID)
        app.dependency_overrides[_permission_dependency()] = lambda: None
        response = TestClient(app).post(
            f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
            json=_body(),
        )
        assert response.status_code == 404
        assert response.json() == {
            "error": {
                "code": "GRANT_EVIDENCE_REVIEW_NOT_FOUND",
                "message": "未找到授权证据复核候选记录",
                "details": None,
            }
        }


def test_auth_permission_and_commit_failures_are_fail_closed(monkeypatch) -> None:
    calls: list[object] = []

    def review_service(command: object, _transaction: object) -> ReviewGrantEvidenceCandidateResult:
        calls.append(command)
        return _result()

    denied_client, denied_session, denied_clock = _client(
        monkeypatch,
        review_service,
        permission_error=BusinessError("FORBIDDEN", "forbidden", status_code=403),
    )
    denied = denied_client.post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body(),
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "FORBIDDEN"
    assert calls == []
    assert denied_clock == []
    assert (denied_session.commit_calls, denied_session.rollback_calls) == (0, 0)

    anonymous_session = RecordingSession()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: anonymous_session
    anonymous = TestClient(app).post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body(),
    )
    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "AUTH_REQUIRED"
    assert (anonymous_session.commit_calls, anonymous_session.rollback_calls) == (0, 0)

    commit_error = RuntimeError("commit failed")
    failing_session = RecordingSession(commit_error=commit_error)
    failing_client, failing_session, _clock = _client(
        monkeypatch,
        review_service,
        session=failing_session,
    )
    failed_commit = failing_client.post(
        f"/api/v1/documents/grant-evidence-candidates/{CANDIDATE_ID}/review",
        json=_body(),
    )
    assert failed_commit.status_code == 500
    assert failed_commit.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert (failing_session.commit_calls, failing_session.rollback_calls) == (1, 1)
