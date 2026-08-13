from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.db.session import get_db
from app.main import create_app
from app.modules.annuity import api as annuity_api

ACTOR_ID = "00000000-0000-4000-8000-000000000283"


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


def _route() -> APIRoute:
    matches = [
        route
        for route in annuity_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/annuity/tasks/generate-drafts"
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _client(*, commit_error: Exception | None = None) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession(commit_error=commit_error)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    permission = next(item.call for item in _route().dependant.dependencies if item.name == "_perm")
    app.dependency_overrides[permission] = lambda: None
    return TestClient(app), transaction


def test_authenticated_actor_is_forwarded_and_success_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def generate(
        transaction: object,
        *,
        task_ids: list[int],
        pay_next_year: bool,
        currency: str,
        actor_id: str,
    ) -> dict[str, object]:
        captured.update(
            transaction=transaction,
            task_ids=task_ids,
            pay_next_year=pay_next_year,
            currency=currency,
            actor_id=actor_id,
        )
        return {
            "summary": {"requested": 1, "targets": 1, "success": 1, "failed": 0},
            "success": [],
            "failed": [],
        }

    monkeypatch.setattr(annuity_api, "generate_fee_drafts_from_annuity_tasks", generate)
    client, transaction = _client()
    response = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        json={"task_ids": [17], "pay_next_year": True, "currency": "cny"},
    )

    assert response.status_code == 200, response.text
    assert captured == {
        "transaction": transaction,
        "task_ids": [17],
        "pay_next_year": True,
        "currency": "cny",
        "actor_id": ACTOR_ID,
    }
    assert transaction.commit_calls == 1
    assert transaction.rollback_calls == 0


def test_service_failure_rolls_back_once(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("draft failure")

    monkeypatch.setattr(annuity_api, "generate_fee_drafts_from_annuity_tasks", fail)
    client, transaction = _client()
    response = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        json={"task_ids": [17]},
    )

    assert response.status_code == 500
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1


def test_commit_failure_rolls_back_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        annuity_api,
        "generate_fee_drafts_from_annuity_tasks",
        lambda *_args, **_kwargs: {"summary": {}, "success": [], "failed": []},
    )
    client, transaction = _client(commit_error=RuntimeError("commit failure"))
    response = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        json={"task_ids": [17]},
    )

    assert response.status_code == 500
    assert transaction.commit_calls == 1
    assert transaction.rollback_calls == 1
