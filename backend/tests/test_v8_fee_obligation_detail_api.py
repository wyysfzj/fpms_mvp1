from __future__ import annotations

import inspect
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api
from app.modules.fees import obligation_schemas
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeEstimateStatus,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationLine,
    FeeObligationSource,
    FeeObligationStatus,
    FeeObligationStatuses,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentStatus,
    FeeSourceStatus,
)

PATH = "/api/v1/fees/obligations/obligation-1"
ROUTER_PATH = "/fees/obligations/{obligation_id}"
OBLIGATION_ID = "obligation-1"

SOURCE_FIELDS = (
    "source_activity_id",
    "source_document_id",
    "status",
)
STATUS_FIELDS = (
    "estimate_status",
    "obligation_status",
    "client_instruction_status",
    "draft_status",
    "pay_list_status",
    "payment_status",
    "official_evidence_status",
)
LINE_FIELDS = (
    "id",
    "obligation_id",
    "case_id",
    "source_activity_id",
    "fee_code",
    "fee_name",
    "fee_year_key",
    "official_full_amount",
    "reduction_ratio",
    "payable_amount",
    "source_amount",
    "source_date",
    "difference_review_state",
    "current_identity_key",
)
DETAIL_FIELDS = (
    "id",
    "case_id",
    "source",
    "fee_domain",
    "obligation_type",
    "due_date",
    "currency",
    "statuses",
    "lines",
    "supersedes_obligation_id",
    "supersede_reason",
)


class RecordingSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1
        raise AssertionError("detail adapter must not commit")

    def rollback(self) -> None:
        self.rollback_calls += 1
        raise AssertionError("detail adapter must not roll back")

    def _forbidden(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("detail adapter performed an extra database operation")

    add = add_all = delete = execute = flush = get = query = refresh = expire = _forbidden


def _detail() -> FeeObligation:
    return FeeObligation(
        id=OBLIGATION_ID,
        case_id="case-1",
        source=FeeObligationSource(
            source_activity_id="source-activity-1",
            source_document_id="document-1",
            status=FeeSourceStatus.VERIFIED,
        ),
        fee_domain=FeeDomain.GOV,
        obligation_type="APPLICATION_FEE",
        due_date=date(2026, 8, 15),
        currency="CNY",
        statuses=FeeObligationStatuses(
            estimate_status=None,
            obligation_status=FeeObligationStatus.RECOGNIZED,
            client_instruction_status=FeeClientInstructionStatus.PAY,
            draft_status=FeeObligationDraftStatus.CREATED,
            pay_list_status=FeePayListStatus.CREATED,
            payment_status=FeePaymentStatus.PAID,
            official_evidence_status=FeeOfficialEvidenceStatus.VERIFIED,
        ),
        lines=(
            FeeObligationLine(
                id="line-1",
                obligation_id=OBLIGATION_ID,
                case_id="case-1",
                source_activity_id="source-activity-1",
                fee_code="APPLICATION",
                fee_name="申请费",
                fee_year_key=0,
                official_full_amount=Decimal("900.00"),
                reduction_ratio=Decimal("0.8500"),
                payable_amount=Decimal("135.00"),
                source_amount=Decimal("135.00"),
                source_date=date(2026, 7, 15),
                difference_review_state=FeeDifferenceReviewState.MATCHED,
                current_identity_key="case-1|source-activity-1|APPLICATION|0",
            ),
        ),
        supersedes_obligation_id=None,
        supersede_reason=None,
    )


def _route() -> APIRoute:
    matching = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"GET"}
    ]
    assert len(matching) == 1
    return matching[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_result: FeeObligation | None = None,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession, list[tuple[str, object]]]:
    session = RecordingSession()
    captured: list[tuple[str, object]] = []

    def service(obligation_id: str, transaction: object) -> FeeObligation:
        captured.append((obligation_id, transaction))
        if service_error is not None:
            raise service_error
        assert service_result is not None
        return service_result

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(fees_api, "get_fee_obligation", service, raising=False)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session, captured


def test_detail_response_schemas_preserve_exact_frozen_contract_shape() -> None:
    source_schema = obligation_schemas.FeeObligationSourceOut
    statuses_schema = obligation_schemas.FeeObligationStatusesOut
    line_schema = obligation_schemas.FeeObligationLineOut
    detail_schema = obligation_schemas.FeeObligationDetailOut

    assert tuple(source_schema.model_fields) == SOURCE_FIELDS
    assert get_type_hints(source_schema) == {
        "source_activity_id": str,
        "source_document_id": str | None,
        "status": FeeSourceStatus,
    }
    assert tuple(statuses_schema.model_fields) == STATUS_FIELDS
    assert get_type_hints(statuses_schema) == {
        "estimate_status": FeeEstimateStatus | None,
        "obligation_status": FeeObligationStatus,
        "client_instruction_status": FeeClientInstructionStatus,
        "draft_status": FeeObligationDraftStatus,
        "pay_list_status": FeePayListStatus,
        "payment_status": FeePaymentStatus,
        "official_evidence_status": FeeOfficialEvidenceStatus,
    }
    assert tuple(line_schema.model_fields) == LINE_FIELDS
    assert get_type_hints(line_schema) == {
        "id": str,
        "obligation_id": str,
        "case_id": str,
        "source_activity_id": str,
        "fee_code": str,
        "fee_name": str,
        "fee_year_key": int,
        "official_full_amount": Decimal | None,
        "reduction_ratio": Decimal,
        "payable_amount": Decimal,
        "source_amount": Decimal | None,
        "source_date": date | None,
        "difference_review_state": FeeDifferenceReviewState,
        "current_identity_key": str | None,
    }
    assert tuple(detail_schema.model_fields) == DETAIL_FIELDS
    assert get_type_hints(detail_schema) == {
        "id": str,
        "case_id": str,
        "source": source_schema,
        "fee_domain": FeeDomain,
        "obligation_type": str,
        "due_date": date | None,
        "currency": str,
        "statuses": statuses_schema,
        "lines": tuple[line_schema, ...],
        "supersedes_obligation_id": str | None,
        "supersede_reason": str | None,
    }
    assert all(
        schema.model_config["from_attributes"] is True
        for schema in (source_schema, statuses_schema, line_schema, detail_schema)
    )


def test_route_is_one_bodyless_get_with_fee_read_and_only_path_id() -> None:
    route = _route()
    operation = create_app().openapi()["paths"][f"/api/v1{ROUTER_PATH}"]["get"]

    assert route.status_code == 200
    assert route.response_model is obligation_schemas.FeeObligationDetailOut
    assert route.dependant.body_params == []
    assert [item.name for item in route.dependant.path_params] == ["obligation_id"]
    assert route.dependant.query_params == []
    assert "requestBody" not in operation
    assert [item["name"] for item in operation["parameters"]] == ["obligation_id"]
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Read"
    assert list(inspect.signature(route.endpoint).parameters) == [
        "obligation_id",
        "_perm",
        "db",
    ]


def test_handler_delegates_once_and_returns_exact_typed_detail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    detail = _detail()
    session = RecordingSession()
    captured: list[tuple[str, object]] = []

    def service(obligation_id: str, transaction: object) -> FeeObligation:
        captured.append((obligation_id, transaction))
        return detail

    monkeypatch.setattr(fees_api, "get_fee_obligation", service, raising=False)

    actual = fees_api.get_fee_obligation_detail(
        obligation_id=OBLIGATION_ID,
        _perm=None,
        db=session,
    )

    assert captured == [(OBLIGATION_ID, session)]
    assert actual == obligation_schemas.FeeObligationDetailOut.model_validate(detail)
    source = inspect.getsource(fees_api.get_fee_obligation_detail)
    assert source.count("get_fee_obligation(") == 1
    for forbidden in (
        ".commit(",
        ".rollback(",
        ".execute(",
        ".flush(",
        ".refresh(",
        "current_user",
    ):
        assert forbidden not in source


def test_success_returns_direct_exact_detail_with_decimal_strings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    detail = _detail()
    client, session, captured = _client(monkeypatch, service_result=detail)

    response = client.get(PATH)

    assert response.status_code == 200
    assert response.json() == {
        "id": OBLIGATION_ID,
        "case_id": "case-1",
        "source": {
            "source_activity_id": "source-activity-1",
            "source_document_id": "document-1",
            "status": "VERIFIED",
        },
        "fee_domain": "GOV",
        "obligation_type": "APPLICATION_FEE",
        "due_date": "2026-08-15",
        "currency": "CNY",
        "statuses": {
            "estimate_status": None,
            "obligation_status": "RECOGNIZED",
            "client_instruction_status": "PAY",
            "draft_status": "CREATED",
            "pay_list_status": "CREATED",
            "payment_status": "PAID",
            "official_evidence_status": "VERIFIED",
        },
        "lines": [
            {
                "id": "line-1",
                "obligation_id": OBLIGATION_ID,
                "case_id": "case-1",
                "source_activity_id": "source-activity-1",
                "fee_code": "APPLICATION",
                "fee_name": "申请费",
                "fee_year_key": 0,
                "official_full_amount": "900.00",
                "reduction_ratio": "0.8500",
                "payable_amount": "135.00",
                "source_amount": "135.00",
                "source_date": "2026-07-15",
                "difference_review_state": "MATCHED",
                "current_identity_key": "case-1|source-activity-1|APPLICATION|0",
            }
        ],
        "supersedes_obligation_id": None,
        "supersede_reason": None,
    }
    assert "data" not in response.json()
    assert captured == [(OBLIGATION_ID, session)]
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    ("status_code", "code"),
    (
        (400, "FEE_OBLIGATION_DETAIL_INVALID"),
        (404, "FEE_OBLIGATION_NOT_FOUND"),
        (409, "FEE_OBLIGATION_STORED_STATE_INVALID"),
    ),
)
def test_service_errors_pass_through_unchanged_without_transaction_action(
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

    response = client.get(PATH)

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "service error",
            "details": {"marker": code},
        }
    }
    assert captured == [(OBLIGATION_ID, session)]
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_authentication_and_fee_read_permission_preserve_401_and_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unauthenticated_session = RecordingSession()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: unauthenticated_session
    with TestClient(app) as client:
        unauthenticated = client.get(PATH)

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "Fee.Read"},
        status_code=403,
    )
    client, session, captured = _client(
        monkeypatch,
        service_result=_detail(),
        permission_error=forbidden,
    )
    response = client.get(PATH)

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Fee.Read"},
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_invalid_path_returns_422_before_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session, captured = _client(monkeypatch, service_result=_detail())

    response = client.get("/api/v1/fees/obligations/" + "x" * 37)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_no_second_detail_route_or_body_owned_id_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    route = _route()
    client, _session, captured = _client(monkeypatch, service_result=_detail())

    detail_routes = [
        item
        for item in fees_api.router.routes
        if isinstance(item, APIRoute)
        and item.methods == {"GET"}
        and item.path.startswith("/fees/obligations")
    ]
    assert detail_routes == [route]
    assert client.get(f"{PATH}/detail").status_code == 404
    assert (
        client.request(
            "GET",
            "/api/v1/fees/obligations",
            json={"obligation_id": OBLIGATION_ID},
        ).status_code
        == 404
    )
    assert captured == []
