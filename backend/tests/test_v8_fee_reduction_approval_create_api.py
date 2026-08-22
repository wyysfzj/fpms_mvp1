from __future__ import annotations

import inspect
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi import Response
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api import deps as api_deps
from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.fee_reduction_approval_schemas import (
    FeeReductionApprovalCreateIn,
    FeeReductionApprovalCreateOut,
)
from app.modules.fees.fee_reduction_approval_service import (
    FeeReductionApprovalRecordDisposition,
    RecordFeeReductionApprovalCommand,
)

PATH = "/api/v1/fees/cases/case-1/reduction-approvals"
ROUTER_PATH = "/fees/cases/{case_id}/reduction-approvals"
ACTOR_ID = "actor-1"
CONFIRMED_AT = datetime(2026, 7, 14, 9, 30)
CONTENT_HASH = "sha256:" + "a" * 64
INPUT_FIELDS = (
    "case_id",
    "scope_type",
    "applicant_ids",
    "eligibility_attributes_version",
    "eligibility_attributes_json",
    "reduction_ratio",
    "fee_codes",
    "fee_year_from",
    "fee_year_to",
    "effective_from",
    "effective_to",
    "source_evidence_version_id",
    "expected_source_content_hash",
    "confirmed_at",
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


def _request_data() -> dict[str, object]:
    return {
        "case_id": "case-1",
        "scope_type": "CASE",
        "applicant_ids": ["applicant-1"],
        "eligibility_attributes_version": "customer-confirmation-v1",
        "eligibility_attributes_json": '{"applicant-1":{"kind":"个人"}}',
        "reduction_ratio": "0.85",
        "fee_codes": ["APPLICATION"],
        "fee_year_from": 1,
        "fee_year_to": 3,
        "effective_from": "2026-07-01",
        "effective_to": "2027-06-30",
        "source_evidence_version_id": "evidence-1",
        "expected_source_content_hash": CONTENT_HASH,
        "confirmed_at": "2026-07-14T09:30:00",
    }


def _result(
    *,
    disposition: FeeReductionApprovalRecordDisposition = (
        FeeReductionApprovalRecordDisposition.CREATED
    ),
    approval_id: str = "approval-1",
) -> SimpleNamespace:
    return SimpleNamespace(
        approval_id=approval_id,
        disposition=disposition,
    )


def _route() -> APIRoute:
    matching = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"POST"}
    ]
    assert len(matching) == 1
    return matching[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_result: SimpleNamespace | None = None,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession, list[RecordFeeReductionApprovalCommand]]:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)
    captured: list[RecordFeeReductionApprovalCommand] = []

    def service(
        command: RecordFeeReductionApprovalCommand,
        transaction: object,
    ) -> SimpleNamespace:
        assert transaction is session
        captured.append(command)
        if service_error is not None:
            raise service_error
        assert service_result is not None
        return service_result

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(
        fees_api,
        "record_fee_reduction_approval",
        service,
        raising=False,
    )
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session, captured


def test_frozen_schemas_have_exact_order_types_and_strict_required_input() -> None:
    assert tuple(FeeReductionApprovalCreateIn.model_fields) == INPUT_FIELDS
    assert get_type_hints(FeeReductionApprovalCreateIn) == {
        "case_id": str,
        "scope_type": FeeReductionApprovalScopeType,
        "applicant_ids": tuple[str, ...],
        "eligibility_attributes_version": str,
        "eligibility_attributes_json": str,
        "reduction_ratio": Decimal,
        "fee_codes": tuple[str, ...],
        "fee_year_from": int | None,
        "fee_year_to": int | None,
        "effective_from": date,
        "effective_to": date | None,
        "source_evidence_version_id": str,
        "expected_source_content_hash": str,
        "confirmed_at": datetime,
    }
    assert FeeReductionApprovalCreateIn.model_config["extra"] == "forbid"
    assert all(field.is_required() for field in FeeReductionApprovalCreateIn.model_fields.values())
    assert tuple(FeeReductionApprovalCreateOut.model_fields) == ("approval_id",)
    assert get_type_hints(FeeReductionApprovalCreateOut) == {"approval_id": str}


def test_route_is_one_post_with_fee_edit_server_actor_and_direct_response_model() -> None:
    route = _route()

    assert route.methods == {"POST"}
    assert route.status_code == 201
    assert route.response_model is FeeReductionApprovalCreateOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    assert list(inspect.signature(fees_api.create_fee_reduction_approval).parameters) == [
        "case_id",
        "payload",
        "response",
        "_perm",
        "current_user",
        "db",
    ]


def test_public_create_uses_fee_edit_server_actor_and_returns_direct_201(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)
    permission_calls: list[tuple[object, str]] = []
    captured: list[RecordFeeReductionApprovalCommand] = []

    def get_user_permissions(transaction: object, actor_id: str) -> set[str]:
        permission_calls.append((transaction, actor_id))
        return {"Fee.Edit"}

    def service(
        command: RecordFeeReductionApprovalCommand,
        transaction: object,
    ) -> SimpleNamespace:
        assert transaction is session
        captured.append(command)
        return SimpleNamespace(
            approval_id="approval-1",
            disposition=FeeReductionApprovalRecordDisposition.CREATED,
        )

    monkeypatch.setattr(api_deps, "get_user_permissions", get_user_permissions)
    monkeypatch.setattr(
        fees_api,
        "record_fee_reduction_approval",
        service,
        raising=False,
    )
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor

    with TestClient(app) as client:
        response = client.post(PATH, json=_request_data())

    assert response.status_code == 201
    assert response.json() == {"approval_id": "approval-1"}
    assert permission_calls == [(session, "actor-1")]
    assert captured == [
        RecordFeeReductionApprovalCommand(
            case_id="case-1",
            scope_type=FeeReductionApprovalScopeType.CASE,
            applicant_ids=("applicant-1",),
            eligibility_attributes_version="customer-confirmation-v1",
            eligibility_attributes_json='{"applicant-1":{"kind":"个人"}}',
            reduction_ratio=Decimal("0.85"),
            fee_codes=("APPLICATION",),
            fee_year_from=1,
            fee_year_to=3,
            effective_from=date(2026, 7, 1),
            effective_to=date(2027, 6, 30),
            source_evidence_version_id="evidence-1",
            expected_source_content_hash=CONTENT_HASH,
            confirmed_at=CONFIRMED_AT,
            confirmed_by=ACTOR_ID,
        )
    ]
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_public_reuse_returns_direct_200_and_commits_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session, captured = _client(
        monkeypatch,
        service_result=_result(
            disposition=FeeReductionApprovalRecordDisposition.REUSED,
            approval_id="approval-existing",
        ),
    )

    response = client.post(PATH, json=_request_data())

    assert response.status_code == 200
    assert response.json() == {"approval_id": "approval-existing"}
    assert "data" not in response.json()
    assert len(captured) == 1
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_path_body_case_mismatch_returns_400_before_service_with_both_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session, captured = _client(
        monkeypatch,
        service_result=_result(),
    )

    response = client.post(
        PATH,
        json={**_request_data(), "case_id": "case-other"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "FEE_REDUCTION_APPROVAL_CASE_MISMATCH",
            "message": "费用减免审批案件标识不匹配",
            "details": {
                "path_case_id": "case-1",
                "body_case_id": "case-other",
            },
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    ("status_code", "code", "details"),
    [
        pytest.param(
            400,
            "FEE_REDUCTION_APPROVAL_INVALID",
            {"field": "fee_codes"},
            id="invalid-command",
        ),
        pytest.param(
            400,
            "FEE_REDUCTION_APPROVAL_NOT_REQUIRED",
            {"field": "reduction_ratio"},
            id="approval-not-required",
        ),
        pytest.param(404, "CASE_NOT_FOUND", None, id="missing-case"),
        pytest.param(
            404,
            "EVIDENCE_VERSION_NOT_FOUND",
            None,
            id="missing-evidence",
        ),
        pytest.param(
            409,
            "FEE_REDUCTION_APPROVAL_CONFLICT",
            None,
            id="evidence-case-mismatch",
        ),
        pytest.param(
            409,
            "FEE_REDUCTION_APPROVAL_CONFLICT",
            None,
            id="other-accepted-conflict",
        ),
    ],
)
def test_service_business_errors_pass_through_http_and_roll_back_once(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
    details: dict[str, object] | None,
) -> None:
    error = BusinessError(
        code,
        "service error",
        details=details,
        status_code=status_code,
    )
    client, session, captured = _client(monkeypatch, service_error=error)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "service error",
            "details": details,
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
        fees_api,
        "record_fee_reduction_approval",
        lambda *_args: _result(),
        raising=False,
    )

    with pytest.raises(RuntimeError) as exc_info:
        fees_api.create_fee_reduction_approval(
            case_id="case-1",
            payload=FeeReductionApprovalCreateIn.model_validate(_request_data()),
            response=Response(),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


def test_authentication_and_permission_dependencies_preserve_401_and_403(
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
        details={"required_perm": "Fee.Edit"},
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
            "details": {"required_perm": "Fee.Edit"},
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    "invalid",
    [
        {key: value for key, value in _request_data().items() if key != "case_id"},
        {key: value for key, value in _request_data().items() if key != "fee_year_to"},
        {**_request_data(), "unexpected": True},
        {**_request_data(), "idempotency_key": "client-owned"},
        {**_request_data(), "scope_type": "UNKNOWN"},
        {**_request_data(), "applicant_ids": "applicant-1"},
        {**_request_data(), "reduction_ratio": "not-a-decimal"},
        {**_request_data(), "confirmed_at": "not-a-datetime"},
        {**_request_data(), "confirmed_at": "2026-07-14T09:30:00+08:00"},
    ],
)
def test_missing_extra_malformed_and_client_idempotency_input_return_422(
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
