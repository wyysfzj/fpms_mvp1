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
from app.modules.documents.grant_evidence_ingestion_service import (
    GrantEvidenceConflict,
    GrantEvidenceFact,
    IngestGrantEvidenceCandidateCommand,
    IngestGrantEvidenceCandidateResult,
)
from app.modules.documents.grant_evidence_schemas import (
    GrantEvidenceCandidateIn,
    GrantEvidenceCandidateOut,
    GrantEvidenceConflictIn,
    GrantEvidenceFactIn,
)
from app.modules.system.grant_evidence_source_service import GrantEvidenceScope

PATH = "/documents/{document_id}/grant-evidence-candidates"
DOCUMENT_ID = "11111111-1111-4111-8111-111111111111"
CASE_ID = "21111111-1111-4111-8111-111111111111"
EVIDENCE_ID = "31111111-1111-4111-8111-111111111111"
TERMINAL_ID = "41111111-1111-4111-8111-111111111111"
ACTOR_ID = "51111111-1111-4111-8111-111111111111"
CANDIDATE_ID = "61111111-1111-4111-8111-111111111111"
SOURCE_CONFIG_ID = "71111111-1111-4111-8111-111111111111"
SOURCE_RECORD_ID = "81111111-1111-4111-8111-111111111111"
ROLE_CONFIG_ID = "91111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 11, 9, 0, 0, 123456)


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
        raise AssertionError("ingestion API queried product tables")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("ingestion API flushed before delegation")


def _body() -> dict[str, object]:
    return {
        "case_id": CASE_ID,
        "evidence_version_id": EVIDENCE_ID,
        "evidence_scope": "GRANT_ANNOUNCEMENT",
        "expected_terminal_event_id": TERMINAL_ID,
        "facts": [
            {"name": "grant_number", "raw_value": "CN-TEST-001"},
            {"name": "status", "raw_value": "GRANTED"},
        ],
        "conflicts": [],
    }


def _result(disposition: str) -> IngestGrantEvidenceCandidateResult:
    return IngestGrantEvidenceCandidateResult(
        candidate_id=CANDIDATE_ID,
        evidence_version_id=EVIDENCE_ID,
        terminal_event_id=TERMINAL_ID,
        source_config_id=SOURCE_CONFIG_ID,
        source_record_id=SOURCE_RECORD_ID,
        proposal_role_config_id=ROLE_CONFIG_ID,
        evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        acquisition_snapshot_hash="a" * 64,
        candidate_snapshot_hash="b" * 64,
        review_status="PENDING",
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
    service: Callable[[object, object], IngestGrantEvidenceCandidateResult],
    *,
    session: RecordingSession | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = session or RecordingSession()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(documents_api, "ingest_grant_evidence_candidate", service)
    monkeypatch.setattr(documents_api, "_utc_now", lambda: NOW)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), transaction


def test_schema_route_and_permission_contract_are_exact() -> None:
    assert tuple(GrantEvidenceFactIn.model_fields) == ("name", "raw_value")
    assert tuple(GrantEvidenceConflictIn.model_fields) == ("name", "raw_values")
    assert tuple(GrantEvidenceCandidateIn.model_fields) == (
        "case_id",
        "evidence_version_id",
        "evidence_scope",
        "expected_terminal_event_id",
        "facts",
        "conflicts",
    )
    assert tuple(GrantEvidenceCandidateOut.model_fields) == (
        "candidate_id",
        "evidence_version_id",
        "terminal_event_id",
        "source_config_id",
        "source_record_id",
        "proposal_role_config_id",
        "evidence_scope",
        "acquisition_snapshot_hash",
        "candidate_snapshot_hash",
        "review_status",
        "disposition",
    )
    for model in (
        GrantEvidenceFactIn,
        GrantEvidenceConflictIn,
        GrantEvidenceCandidateIn,
    ):
        assert model.model_config["extra"] == "forbid"
    assert GrantEvidenceCandidateIn.model_fields["conflicts"].default == ()
    route = _route()
    assert route.status_code == 201
    assert route.response_model is GrantEvidenceCandidateOut
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
    "change",
    (
        {"proposed_by": ACTOR_ID},
        {"proposed_at": NOW.isoformat()},
        {"case_id": "not-a-uuid"},
        {"facts": []},
        {
            "facts": [
                {"name": "status", "raw_value": "GRANTED"},
                {"name": "grant_number", "raw_value": "CN-TEST-001"},
            ]
        },
        {
            "facts": [
                {"name": "status", "raw_value": "A"},
                {"name": "status", "raw_value": "B"},
            ]
        },
        {
            "conflicts": [
                {"name": "status", "raw_values": ["same", "same"]},
            ]
        },
        {
            "conflicts": [
                {"name": "unknown", "raw_values": ["A", "B"]},
            ]
        },
    ),
)
def test_strict_payload_rejects_forged_malformed_or_noncanonical_input(change) -> None:
    with pytest.raises(ValidationError):
        GrantEvidenceCandidateIn.model_validate(_body() | change)


@pytest.mark.parametrize(("disposition", "expected_status"), (("CREATED", 201), ("REUSED", 200)))
def test_route_injects_path_actor_one_server_time_and_maps_dynamic_status(
    monkeypatch: pytest.MonkeyPatch,
    disposition: str,
    expected_status: int,
) -> None:
    captured: list[tuple[IngestGrantEvidenceCandidateCommand, object]] = []

    def service(command: object, transaction: object) -> IngestGrantEvidenceCandidateResult:
        assert isinstance(command, IngestGrantEvidenceCandidateCommand)
        captured.append((command, transaction))
        return _result(disposition)

    client, session = _client(monkeypatch, service)
    response = client.post(
        f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates",
        json=_body(),
    )
    assert response.status_code == expected_status
    assert captured == [
        (
            IngestGrantEvidenceCandidateCommand(
                case_id=CASE_ID,
                document_id=DOCUMENT_ID,
                evidence_version_id=EVIDENCE_ID,
                evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
                expected_terminal_event_id=TERMINAL_ID,
                proposed_by=ACTOR_ID,
                proposed_at=NOW,
                facts=(
                    GrantEvidenceFact(name="grant_number", raw_value="CN-TEST-001"),
                    GrantEvidenceFact(name="status", raw_value="GRANTED"),
                ),
                conflicts=(),
            ),
            session,
        )
    ]
    assert response.json() == GrantEvidenceCandidateOut.model_validate(
        _result(disposition), from_attributes=True
    ).model_dump(mode="json")
    assert (session.commit_calls, session.rollback_calls) == (1, 0)


def test_conflicts_are_mapped_exactly_and_preserve_raw_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[IngestGrantEvidenceCandidateCommand] = []

    def service(command: object, _transaction: object) -> IngestGrantEvidenceCandidateResult:
        assert isinstance(command, IngestGrantEvidenceCandidateCommand)
        captured.append(command)
        return _result("CREATED")

    body = _body()
    body["conflicts"] = [{"name": "status", "raw_values": ["GRANTED", "UNKNOWN"]}]
    client, _session = _client(monkeypatch, service)
    assert (
        client.post(
            f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates", json=body
        ).status_code
        == 201
    )
    assert captured[0].conflicts == (
        GrantEvidenceConflict(name="status", raw_values=("GRANTED", "UNKNOWN")),
    )


def test_validation_permission_service_and_commit_failures_never_leak_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def conflict(command: object, _transaction: object) -> IngestGrantEvidenceCandidateResult:
        calls.append(command)
        raise BusinessError("GRANT_EVIDENCE_CANDIDATE_CONFLICT", "conflict", status_code=409)

    client, session = _client(monkeypatch, conflict)
    response = client.post(
        f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates", json=_body()
    )
    assert response.status_code == 409
    assert len(calls) == 1
    assert (session.commit_calls, session.rollback_calls) == (0, 1)

    malformed = client.post("/api/v1/documents/not-a-uuid/grant-evidence-candidates", json=_body())
    assert malformed.status_code == 422
    assert len(calls) == 1

    denied_client, denied_session = _client(
        monkeypatch,
        lambda _command, _transaction: _result("CREATED"),
        permission_error=BusinessError("FORBIDDEN", "forbidden", status_code=403),
    )
    denied = denied_client.post(
        f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates", json=_body()
    )
    assert denied.status_code == 403
    assert (denied_session.commit_calls, denied_session.rollback_calls) == (0, 0)

    invalid_client, invalid_session = _client(
        monkeypatch,
        lambda _command, _transaction: _result("OTHER"),
    )
    invalid = invalid_client.post(
        f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates", json=_body()
    )
    assert invalid.status_code == 500
    assert (invalid_session.commit_calls, invalid_session.rollback_calls) == (0, 1)

    failing = RecordingSession(commit_error=RuntimeError("commit failed"))
    monkeypatch.setattr(
        documents_api,
        "ingest_grant_evidence_candidate",
        lambda _command, _transaction: _result("CREATED"),
    )
    with pytest.raises(RuntimeError, match="commit failed"):
        documents_api.create_grant_evidence_candidate(
            document_id=DOCUMENT_ID,
            payload=GrantEvidenceCandidateIn.model_validate(_body()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=failing,
        )
    assert (failing.commit_calls, failing.rollback_calls) == (1, 1)
