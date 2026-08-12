from __future__ import annotations

import inspect
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError, raise_business_error
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api

NOW = datetime(2026, 8, 13, 14, 0)
LATER = NOW + timedelta(days=365)
ACTOR_ID = "00000000-0000-4000-8000-000000000227"
PRICE_BOOK_ID = "11111111-1111-4111-8111-111111111227"
PREDECESSOR_ID = "22222222-2222-4222-8222-222222222227"


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


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "approval_reason": "客户完整价格版本已独立复核",
        "expected_current_price_book_id": PREDECESSOR_ID,
    }
    payload.update(overrides)
    return payload


def _result(disposition: str = "ACTIVATED"):
    from app.modules.fees.service_price_book import ActivateServicePriceBookResult

    return ActivateServicePriceBookResult(
        price_book_id=PRICE_BOOK_ID,
        source_classification="PRODUCTION",
        book_version="2026.08",
        scope_key="GLOBAL",
        source_content_hash="a" * 64,
        item_snapshot_hash="b" * 64,
        item_count=2,
        status="ACTIVE",
        effective_from=NOW,
        effective_to=LATER,
        approved_by=ACTOR_ID,
        approved_at=NOW,
        activated_by=ACTOR_ID,
        activated_at=NOW,
        current_identity_key="GLOBAL",
        supersedes_price_book_id=PREDECESSOR_ID,
        disposition=disposition,
    )


def _route() -> APIRoute:
    matches = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/fees/service-price-books/{price_book_id}/activate"
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    return next(item.call for item in _route().dependant.dependencies if item.name == "_perm")


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    permission_error: BusinessError | None = None,
    authenticated: bool = True,
    commit_error: Exception | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession(commit_error=commit_error)

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    monkeypatch.setattr(fees_api, "_service_price_book_runtime_profile", lambda: "production")
    monkeypatch.setattr(fees_api, "_service_price_book_utcnow", lambda: NOW)
    return TestClient(app), transaction


def test_route_freezes_strict_request_direct_response_and_fee_edit() -> None:
    from app.modules.fees.service_price_book_schemas import (
        ServicePriceBookActivationIn,
        ServicePriceBookActivationOut,
    )

    assert tuple(ServicePriceBookActivationIn.model_fields) == (
        "approval_reason",
        "expected_current_price_book_id",
    )
    assert ServicePriceBookActivationIn.model_fields[
        "expected_current_price_book_id"
    ].annotation == (UUID | None)
    assert all(field.is_required() for field in ServicePriceBookActivationIn.model_fields.values())
    assert ServicePriceBookActivationIn.model_config["extra"] == "forbid"
    assert tuple(ServicePriceBookActivationOut.model_fields) == (
        "price_book_id",
        "source_classification",
        "book_version",
        "scope_key",
        "source_content_hash",
        "item_snapshot_hash",
        "item_count",
        "status",
        "effective_from",
        "effective_to",
        "approved_by",
        "approved_at",
        "activated_by",
        "activated_at",
        "current_identity_key",
        "supersedes_price_book_id",
        "disposition",
    )
    route = _route()
    assert route.response_model is ServicePriceBookActivationOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Edit"
    assert not any(
        isinstance(item, APIRoute) and item.path == "/fees/service-price-books/activate"
        for item in fees_api.router.routes
    )


@pytest.mark.parametrize("disposition", ["ACTIVATED", "REUSED"])
def test_activation_supplies_server_context_commits_and_returns_200(
    monkeypatch: pytest.MonkeyPatch,
    disposition: str,
) -> None:
    from app.modules.fees.service_price_book import ActivateServicePriceBookCommand

    commands: list[ActivateServicePriceBookCommand] = []

    def activate(transaction, command: ActivateServicePriceBookCommand):
        assert isinstance(transaction, RecordingSession)
        commands.append(command)
        return _result(disposition)

    monkeypatch.setattr(fees_api, "activate_service_price_book", activate)
    client, transaction = _client(monkeypatch)
    response = client.post(
        f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
        json=_payload(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "price_book_id": PRICE_BOOK_ID,
        "source_classification": "PRODUCTION",
        "book_version": "2026.08",
        "scope_key": "GLOBAL",
        "source_content_hash": "a" * 64,
        "item_snapshot_hash": "b" * 64,
        "item_count": 2,
        "status": "ACTIVE",
        "effective_from": NOW.isoformat(),
        "effective_to": LATER.isoformat(),
        "approved_by": ACTOR_ID,
        "approved_at": NOW.isoformat(),
        "activated_by": ACTOR_ID,
        "activated_at": NOW.isoformat(),
        "current_identity_key": "GLOBAL",
        "supersedes_price_book_id": PREDECESSOR_ID,
        "disposition": disposition,
    }
    assert commands == [
        ActivateServicePriceBookCommand(
            price_book_id=PRICE_BOOK_ID,
            approval_reason="客户完整价格版本已独立复核",
            actor_id=ACTOR_ID,
            at=NOW,
            expected_current_price_book_id=PREDECESSOR_ID,
            runtime_profile="production",
        )
    ]
    assert transaction.commit_calls == 1
    assert transaction.rollback_calls == 0


def test_service_and_commit_errors_roll_back_and_preserve_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject(_transaction, _command):
        raise_business_error(
            "SERVICE_PRICE_BOOK_ACTIVATION_CONFLICT",
            "rejected",
            status_code=409,
        )

    monkeypatch.setattr(fees_api, "activate_service_price_book", reject)
    client, transaction = _client(monkeypatch)
    response = client.post(
        f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
        json=_payload(),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SERVICE_PRICE_BOOK_ACTIVATION_CONFLICT"
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1

    monkeypatch.setattr(fees_api, "activate_service_price_book", lambda *_args: _result())
    failing, transaction = _client(monkeypatch, commit_error=RuntimeError("commit failed"))
    response = failing.post(
        f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
        json=_payload(),
    )
    assert response.status_code == 500
    assert transaction.commit_calls == 1
    assert transaction.rollback_calls == 1


def test_auth_permission_path_and_request_shape_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    anonymous, transaction = _client(monkeypatch, authenticated=False)
    response = anonymous.post(
        f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
        json=_payload(),
    )
    assert response.status_code == 401
    assert transaction.commit_calls == transaction.rollback_calls == 0

    forbidden, transaction = _client(
        monkeypatch,
        permission_error=BusinessError("FORBIDDEN", "denied", status_code=403),
    )
    response = forbidden.post(
        f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
        json=_payload(),
    )
    assert response.status_code == 403
    assert transaction.commit_calls == transaction.rollback_calls == 0

    allowed, transaction = _client(monkeypatch)
    for path, payload in (
        (
            f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
            _payload(actor_id=ACTOR_ID, at=NOW.isoformat(), runtime_profile="production"),
        ),
        ("/api/v1/fees/service-price-books/not-a-uuid/activate", _payload()),
        (
            f"/api/v1/fees/service-price-books/{PRICE_BOOK_ID}/activate",
            {"approval_reason": "reviewed"},
        ),
    ):
        assert allowed.post(path, json=payload).status_code == 422
    assert transaction.commit_calls == transaction.rollback_calls == 0
