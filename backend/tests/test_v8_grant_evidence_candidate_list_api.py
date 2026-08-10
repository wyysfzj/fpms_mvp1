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
from app.modules.documents.grant_evidence_ingestion_service import (
    GrantEvidenceCandidateRead,
    GrantEvidenceConflict,
    GrantEvidenceFact,
    ListGrantEvidenceCandidatesCommand,
)
from app.modules.documents.grant_evidence_schemas import (
    GrantEvidenceCandidateReadOut,
    GrantEvidenceConflictOut,
    GrantEvidenceFactOut,
)
from app.modules.system.grant_evidence_source_service import GrantEvidenceScope

PATH = "/documents/{document_id}/grant-evidence-candidates"
DOCUMENT_ID = "11111111-1111-4111-8111-111111111111"
CASE_ID = "21111111-1111-4111-8111-111111111111"
EVIDENCE_ID = "31111111-1111-4111-8111-111111111111"
CANDIDATE_IDS = (
    "41111111-1111-4111-8111-111111111111",
    "42111111-1111-4111-8111-111111111111",
)
TERMINAL_ID = "51111111-1111-4111-8111-111111111111"
SOURCE_CONFIG_ID = "61111111-1111-4111-8111-111111111111"
SOURCE_RECORD_ID = "71111111-1111-4111-8111-111111111111"
ROLE_CONFIG_ID = "81111111-1111-4111-8111-111111111111"
PROPOSER_ID = "91111111-1111-4111-8111-111111111111"
REVIEWER_ID = "a1111111-1111-4111-8111-111111111111"
NOW = datetime(2026, 8, 11, 10, 0, 0, 123456)


class ReadOnlySession:
    def execute(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("candidate-list API queried product tables")

    def scalar(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("candidate-list API queried product tables")

    def scalars(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("candidate-list API queried product tables")

    def get(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("candidate-list API queried product tables")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("candidate-list API flushed")

    def commit(self) -> None:
        raise AssertionError("candidate-list API committed")

    def rollback(self) -> None:
        raise AssertionError("candidate-list API rolled back")

    def close(self) -> None:
        raise AssertionError("candidate-list API closed the caller session")


def _result(index: int = 0) -> GrantEvidenceCandidateRead:
    reviewed = index == 1
    return GrantEvidenceCandidateRead(
        candidate_id=CANDIDATE_IDS[index],
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_ID,
        terminal_event_id=TERMINAL_ID,
        source_config_id=SOURCE_CONFIG_ID,
        source_record_id=SOURCE_RECORD_ID,
        source_version="cnipa-v1",
        original_reference="CNIPA-TEST-REFERENCE",
        acquisition_method="CONTROLLED_DOWNLOAD",
        acquired_at=NOW,
        evidence_scope=GrantEvidenceScope.GRANT_ANNOUNCEMENT,
        proposal_role_config_id=ROLE_CONFIG_ID,
        proposed_by=PROPOSER_ID,
        proposed_at=NOW,
        review_status="APPROVED" if reviewed else "PENDING",
        reviewer_id=REVIEWER_ID if reviewed else None,
        reviewed_at=NOW if reviewed else None,
        review_reason="保留原始冲突。" if reviewed else None,
        acquisition_snapshot_hash="a" * 64,
        candidate_snapshot_hash="b" * 64,
        facts=(
            GrantEvidenceFact(name="grant_number", raw_value="CN-TEST-001"),
            GrantEvidenceFact(name="status", raw_value="公告：授权"),
        ),
        conflicts=(
            GrantEvidenceConflict(
                name="status",
                raw_values=("公告：授权", "登记簿：待确认"),
            ),
        ),
    )


def _route(method: str) -> APIRoute:
    matches = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute) and route.path == PATH and route.methods == {method}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route("GET").dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    read_service: Callable[[object, object], tuple[GrantEvidenceCandidateRead, ...]],
    *,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, ReadOnlySession, list[datetime]]:
    transaction = ReadOnlySession()
    clock_calls: list[datetime] = []

    def now() -> datetime:
        clock_calls.append(NOW)
        return NOW

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(documents_api, "list_grant_evidence_candidates", read_service)
    monkeypatch.setattr(documents_api, "_utc_now", now)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=REVIEWER_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), transaction, clock_calls


def test_output_schema_route_and_permission_contract_are_exact() -> None:
    assert tuple(GrantEvidenceFactOut.model_fields) == ("name", "raw_value")
    assert tuple(GrantEvidenceConflictOut.model_fields) == ("name", "raw_values")
    assert tuple(GrantEvidenceCandidateReadOut.model_fields) == (
        "candidate_id",
        "case_id",
        "document_id",
        "evidence_version_id",
        "terminal_event_id",
        "source_config_id",
        "source_record_id",
        "source_version",
        "original_reference",
        "acquisition_method",
        "acquired_at",
        "evidence_scope",
        "proposal_role_config_id",
        "proposed_by",
        "proposed_at",
        "review_status",
        "reviewer_id",
        "reviewed_at",
        "review_reason",
        "acquisition_snapshot_hash",
        "candidate_snapshot_hash",
        "facts",
        "conflicts",
    )
    for model in (GrantEvidenceFactOut, GrantEvidenceConflictOut, GrantEvidenceCandidateReadOut):
        assert model.model_config["extra"] == "forbid"
        assert model.model_config["strict"] is True
        assert model.model_config["from_attributes"] is True

    route = _route("GET")
    assert route.status_code == 200
    assert route.response_model == list[GrantEvidenceCandidateReadOut]
    assert route.body_field is None
    assert route.dependant.query_params == []
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Read"
    assert _route("POST").status_code == 201


def test_get_delegates_once_with_path_and_one_server_time_preserving_order_and_raw_truth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[ListGrantEvidenceCandidatesCommand, object]] = []

    def read_service(
        command: object, transaction: object
    ) -> tuple[GrantEvidenceCandidateRead, ...]:
        assert type(command) is ListGrantEvidenceCandidatesCommand
        captured.append((command, transaction))
        return (_result(0), _result(1))

    client, transaction, clock_calls = _client(monkeypatch, read_service)
    response = client.get(f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates")
    assert response.status_code == 200
    assert captured == [
        (
            ListGrantEvidenceCandidatesCommand(document_id=DOCUMENT_ID, read_at=NOW),
            transaction,
        )
    ]
    assert clock_calls == [NOW]
    assert response.json() == [
        GrantEvidenceCandidateReadOut.model_validate(item, from_attributes=True).model_dump(
            mode="json"
        )
        for item in (_result(0), _result(1))
    ]
    assert response.json()[0]["conflicts"] == [
        {"name": "status", "raw_values": ["公告：授权", "登记簿：待确认"]}
    ]
    assert [item["candidate_id"] for item in response.json()] == list(CANDIDATE_IDS)


def test_empty_result_is_exact_200_list(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []

    def read_service(
        command: object, _transaction: object
    ) -> tuple[GrantEvidenceCandidateRead, ...]:
        calls.append(command)
        return ()

    client, _transaction, clock_calls = _client(monkeypatch, read_service)
    response = client.get(f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates")
    assert (response.status_code, response.json()) == (200, [])
    assert len(calls) == 1
    assert clock_calls == [NOW]


@pytest.mark.parametrize(
    ("error", "expected_status"),
    (
        (BusinessError("GRANT_EVIDENCE_DOCUMENT_NOT_FOUND", "missing", status_code=404), 404),
        (BusinessError("GRANT_EVIDENCE_CANDIDATE_CONFLICT", "conflict", status_code=409), 409),
    ),
)
def test_service_errors_preserve_status_without_transaction_close(
    monkeypatch: pytest.MonkeyPatch,
    error: BusinessError,
    expected_status: int,
) -> None:
    calls: list[object] = []

    def fail(command: object, _transaction: object) -> tuple[GrantEvidenceCandidateRead, ...]:
        calls.append(command)
        raise error

    client, _transaction, clock_calls = _client(monkeypatch, fail)
    response = client.get(f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates")
    assert response.status_code == expected_status
    assert len(calls) == 1
    assert clock_calls == [NOW]


def test_permission_and_uuid_validation_fail_before_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []

    def read_service(
        command: object, _transaction: object
    ) -> tuple[GrantEvidenceCandidateRead, ...]:
        calls.append(command)
        return ()

    client, _transaction, clock_calls = _client(monkeypatch, read_service)
    invalid = client.get("/api/v1/documents/not-a-uuid/grant-evidence-candidates")
    assert invalid.status_code == 422
    assert calls == []
    assert clock_calls == []

    denied_client, _transaction, denied_clock = _client(
        monkeypatch,
        read_service,
        permission_error=BusinessError("FORBIDDEN", "forbidden", status_code=403),
    )
    denied = denied_client.get(f"/api/v1/documents/{DOCUMENT_ID}/grant-evidence-candidates")
    assert denied.status_code == 403
    assert calls == []
    assert denied_clock == []
