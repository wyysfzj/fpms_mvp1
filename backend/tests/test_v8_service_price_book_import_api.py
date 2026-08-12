from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace

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
ACTOR_ID = "00000000-0000-4000-8000-000000000225"
PRICE_BOOK_ID = "11111111-1111-4111-8111-111111111225"
SOURCE_REFERENCE = "managed://service-price-books/customer-approved-2026-08.json"
SOURCE_CONTENT = '{"version":"2026.08","controlled_upload":true}'


class RecordingSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1


def _source_hash() -> str:
    snapshot = json.dumps(
        {
            "source_content": SOURCE_CONTENT,
            "source_reference": SOURCE_REFERENCE,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(snapshot.encode()).hexdigest()


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "source_classification": "PRODUCTION",
        "book_version": "2026.08",
        "scope_key": "GLOBAL",
        "currency": "CNY",
        "tax_policy": "EXCLUSIVE",
        "discount_policy": "NONE",
        "source_reference": SOURCE_REFERENCE,
        "source_content": SOURCE_CONTENT,
        "expected_source_content_hash": _source_hash(),
        "items": [
            {"item_code": "SEARCH|STANDARD", "unit_price": "1200.00"},
            {"item_code": "FILING:STANDARD", "unit_price": "5000.50"},
        ],
        "effective_from": NOW.isoformat(),
        "effective_to": LATER.isoformat(),
        "idempotency_key": "service-price-book-import-2026-08",
    }
    payload.update(overrides)
    return payload


def _result(disposition: str = "CREATED"):
    from app.modules.fees.service_price_book import ImportServicePriceBookResult

    return ImportServicePriceBookResult(
        price_book_id=PRICE_BOOK_ID,
        source_classification="PRODUCTION",
        book_version="2026.08",
        scope_key="GLOBAL",
        currency="CNY",
        tax_policy="EXCLUSIVE",
        discount_policy="NONE",
        source_reference=SOURCE_REFERENCE,
        source_content_hash=_source_hash(),
        item_snapshot_hash="b" * 64,
        item_count=2,
        status="DRAFT",
        effective_from=NOW,
        effective_to=LATER,
        created_by=ACTOR_ID,
        disposition=disposition,
    )


def _route() -> APIRoute:
    matches = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/fees/service-price-books/import"
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
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    monkeypatch.setattr(fees_api, "_service_price_book_runtime_profile", lambda: "production")
    return TestClient(app), transaction


def test_route_freezes_strict_request_safe_response_and_fee_edit() -> None:
    from app.modules.fees.service_price_book_schemas import (
        ServicePriceBookImportIn,
        ServicePriceBookImportItemIn,
        ServicePriceBookImportOut,
    )

    assert tuple(ServicePriceBookImportItemIn.model_fields) == ("item_code", "unit_price")
    assert tuple(ServicePriceBookImportIn.model_fields) == (
        "source_classification",
        "book_version",
        "scope_key",
        "currency",
        "tax_policy",
        "discount_policy",
        "source_reference",
        "source_content",
        "expected_source_content_hash",
        "items",
        "effective_from",
        "effective_to",
        "idempotency_key",
    )
    assert "actor_id" not in ServicePriceBookImportIn.model_fields
    assert "runtime_profile" not in ServicePriceBookImportIn.model_fields
    assert "source_content" not in ServicePriceBookImportOut.model_fields
    dependency = _permission_dependency()
    assert inspect.getclosurevars(dependency).nonlocals["code"] == "Fee.Edit"


def test_import_supplies_server_context_commits_and_returns_201_or_200_replay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.fees.service_price_book import ImportServicePriceBookCommand

    commands: list[ImportServicePriceBookCommand] = []

    def import_book(transaction, command: ImportServicePriceBookCommand):
        assert isinstance(transaction, RecordingSession)
        commands.append(command)
        return _result("CREATED" if len(commands) == 1 else "REUSED")

    monkeypatch.setattr(fees_api, "import_service_price_book", import_book)
    client, transaction = _client(monkeypatch)
    first = client.post("/api/v1/fees/service-price-books/import", json=_payload())
    second = client.post("/api/v1/fees/service-price-books/import", json=_payload())

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json() == {
        "price_book_id": PRICE_BOOK_ID,
        "source_classification": "PRODUCTION",
        "book_version": "2026.08",
        "scope_key": "GLOBAL",
        "currency": "CNY",
        "tax_policy": "EXCLUSIVE",
        "discount_policy": "NONE",
        "source_reference": SOURCE_REFERENCE,
        "source_content_hash": _source_hash(),
        "item_snapshot_hash": "b" * 64,
        "item_count": 2,
        "status": "DRAFT",
        "effective_from": NOW.isoformat(),
        "effective_to": LATER.isoformat(),
        "created_by": ACTOR_ID,
        "disposition": "CREATED",
    }
    assert commands[0].actor_id == ACTOR_ID
    assert commands[0].runtime_profile == "production"
    assert commands[0].items[0].unit_price == Decimal("1200.00")
    assert transaction.commit_calls == 2
    assert transaction.rollback_calls == 0


@pytest.mark.parametrize(
    ("code", "status_code"),
    [
        ("SERVICE_PRICE_BOOK_IMPORT_INVALID", 400),
        ("SERVICE_PRICE_BOOK_IMPORT_CONFLICT", 409),
    ],
)
def test_service_errors_roll_back_and_preserve_status(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
    status_code: int,
) -> None:
    def reject(_transaction, _command):
        raise_business_error(code, "rejected", status_code=status_code)

    monkeypatch.setattr(fees_api, "import_service_price_book", reject)
    client, transaction = _client(monkeypatch)
    response = client.post("/api/v1/fees/service-price-books/import", json=_payload())
    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1


def test_auth_permission_and_request_shape_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    anonymous, _ = _client(monkeypatch, authenticated=False)
    assert (
        anonymous.post("/api/v1/fees/service-price-books/import", json=_payload()).status_code
        == 401
    )

    forbidden, transaction = _client(
        monkeypatch,
        permission_error=BusinessError("FORBIDDEN", "denied", status_code=403),
    )
    assert (
        forbidden.post("/api/v1/fees/service-price-books/import", json=_payload()).status_code
        == 403
    )
    assert transaction.commit_calls == transaction.rollback_calls == 0

    allowed, transaction = _client(monkeypatch)
    extra = allowed.post(
        "/api/v1/fees/service-price-books/import",
        json=_payload(actor_id="client-controlled", runtime_profile="test"),
    )
    assert extra.status_code == 422
    assert transaction.commit_calls == transaction.rollback_calls == 0
