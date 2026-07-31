from __future__ import annotations

import inspect
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api
from app.modules.fees.enums import FeeDraftStatus
from app.modules.fees.schemas import FeeDraftCreateIn, FeeDraftOut

PATH = "/api/v1/fees/drafts"
ROUTER_PATH = "/fees/drafts"
ACTOR_ID = "actor-1"
OBLIGATION_ID = "obligation-1"


class RecordingSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0
        self.refreshed: list[object] = []

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1

    def refresh(self, value: object) -> None:
        self.refreshed.append(value)


def _route() -> APIRoute:
    matches = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    return next(item.call for item in _route().dependant.dependencies if item.name == "_perm")


def _request_data(*, obligation_id: object = OBLIGATION_ID) -> dict[str, object]:
    data: dict[str, object] = {
        "case_id": "case-1",
        "client_id": None,
        "draft_type": None,
        "currency": "CNY",
    }
    if obligation_id is not ...:
        data["obligation_id"] = obligation_id
    return data


def _draft() -> SimpleNamespace:
    timestamp = datetime(2026, 7, 20, 9, 0)
    return SimpleNamespace(
        id="draft-1",
        case_id="case-1",
        case_no=None,
        client_id=None,
        client_name=None,
        draft_type="GENERIC",
        currency="CNY",
        status=FeeDraftStatus.OPEN,
        total_gov=Decimal("0.00"),
        total_service=Decimal("1000.00"),
        total_misc=Decimal("0.00"),
        amount=Decimal("1000.00"),
        official_fee_reduction_note=None,
        official_template_status=None,
        official_template_version=None,
        official_template_note=None,
        created_at=timestamp,
        updated_at=timestamp,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession, list[tuple[FeeDraftCreateIn, str | None, str]]]:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)
    captured: list[tuple[FeeDraftCreateIn, str | None, str]] = []

    def service(
        transaction: object,
        *,
        data: FeeDraftCreateIn,
        actor_id: str,
        obligation_id: str | None = None,
    ) -> SimpleNamespace:
        assert transaction is session
        captured.append((data, obligation_id, actor_id))
        if service_error is not None:
            raise service_error
        return _draft()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(fees_api, "create_fee_draft_service", service)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session, captured


def test_schema_adds_one_optional_nullable_string_without_changing_existing_fields() -> None:
    assert tuple(FeeDraftCreateIn.model_fields) == (
        "case_id",
        "client_id",
        "draft_type",
        "currency",
        "obligation_id",
    )
    assert get_type_hints(FeeDraftCreateIn) == {
        "case_id": str,
        "client_id": str | None,
        "draft_type": str | None,
        "currency": str,
        "obligation_id": str | None,
    }
    assert FeeDraftCreateIn.model_fields["obligation_id"].default is None
    assert FeeDraftCreateIn.model_validate(_request_data(obligation_id=...)).obligation_id is None
    assert FeeDraftCreateIn.model_validate(_request_data(obligation_id=None)).obligation_id is None
    with pytest.raises(ValidationError):
        FeeDraftCreateIn.model_validate(_request_data(obligation_id={"id": OBLIGATION_ID}))


def test_existing_route_keeps_one_post_201_direct_envelope_and_fee_create_permission() -> None:
    route = _route()

    assert route.methods == {"POST"}
    assert route.status_code == 201
    assert route.response_model is FeeDraftOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Create"
    assert list(inspect.signature(fees_api.create_fee_draft).parameters) == [
        "payload",
        "_perm",
        "current_user",
        "db",
    ]


def test_linked_request_passes_obligation_and_commits_before_direct_201(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session, captured = _client(monkeypatch)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == 201
    assert response.json() == {
        "id": "draft-1",
        "case_id": "case-1",
        "case_no": None,
        "client_id": None,
        "client_name": None,
        "draft_type": "GENERIC",
        "currency": "CNY",
        "status": "OPEN",
        "total_gov": "0.00",
        "total_service": "1000.00",
        "total_misc": "0.00",
        "amount": "1000.00",
        "official_fee_reduction_note": None,
        "official_template_status": None,
        "official_template_version": None,
        "official_template_note": None,
        "created_at": "2026-07-20T09:00:00",
        "updated_at": "2026-07-20T09:00:00",
    }
    assert len(captured) == 1
    assert captured[0][0].obligation_id == OBLIGATION_ID
    assert captured[0][1:] == (OBLIGATION_ID, ACTOR_ID)
    assert session.commit_calls == 1
    assert len(session.refreshed) == 1
    assert session.rollback_calls == 0


@pytest.mark.parametrize("obligation_id", [..., None])
def test_legacy_missing_or_null_obligation_keeps_historical_service_owned_path(
    monkeypatch: pytest.MonkeyPatch,
    obligation_id: object,
) -> None:
    client, session, captured = _client(monkeypatch)

    response = client.post(PATH, json=_request_data(obligation_id=obligation_id))

    assert response.status_code == 201
    assert len(captured) == 1
    assert captured[0][0].obligation_id is None
    assert captured[0][1:] == (None, ACTOR_ID)
    assert session.commit_calls == 0
    assert session.refreshed == []
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    (
        (
            BusinessError(
                "FEE_OBLIGATION_NOT_FOUND",
                "费用义务不存在",
                status_code=404,
            ),
            409,
        ),
        (
            BusinessError(
                "FEE_OBLIGATION_DRAFT_NOT_ACTIONABLE",
                "当前费用义务不可生成请款草稿",
                status_code=409,
            ),
            409,
        ),
        (
            BusinessError(
                "FEE_DRAFT_OBLIGATION_LINK_MISMATCH",
                "费用草稿与费用义务关联不一致",
                status_code=409,
            ),
            409,
        ),
    ),
)
def test_linked_seam_errors_are_409_and_rollback_without_partial_draft(
    monkeypatch: pytest.MonkeyPatch,
    service_error: BusinessError,
    expected_status: int,
) -> None:
    client, session, captured = _client(monkeypatch, service_error=service_error)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == expected_status
    assert response.json() == {
        "error": {
            "code": service_error.code,
            "message": service_error.message,
            "details": None,
        }
    }
    assert len(captured) == 1
    assert session.commit_calls == 0
    assert session.refreshed == []
    assert session.rollback_calls == 1


def test_fee_create_permission_failure_keeps_service_and_transaction_untouched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    permission_error = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "Fee.Create"},
        status_code=403,
    )
    client, session, captured = _client(
        monkeypatch,
        permission_error=permission_error,
    )

    response = client.post(PATH, json=_request_data())

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Fee.Create"},
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.refreshed == []
    assert session.rollback_calls == 0
