from __future__ import annotations

import inspect
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
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
    RecognizeFeeObligationResult,
)
from app.modules.fees.obligation_service import CreateServiceReceivableObligationResult

NOW = datetime(2026, 8, 13, 17, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000229"
PRICE_BOOK_ID = "11111111-1111-4111-8111-111111111229"
CASE_ID = "22222222-2222-4222-8222-222222222229"
OBLIGATION_ID = "33333333-3333-4333-8333-333333333229"
SOURCE_ACTIVITY_ID = "44444444-4444-4444-8444-444444444229"
RECOGNITION_ACTIVITY_ID = "55555555-5555-4555-8555-555555555229"
PATH = "/api/v1/fees/service-receivables"


class RecordingSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollbacks += 1


def _route() -> APIRoute:
    matches = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/fees/service-receivables"
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency() -> object:
    return next(item.call for item in _route().dependant.dependencies if item.name == "_perm")


def _payload(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "price_book_version_id": PRICE_BOOK_ID,
        "item_code": "SEARCH|STANDARD",
        "case_id": CASE_ID,
        "idempotency_key": "service-receivable-http-229",
    }
    payload.update(changes)
    return payload


def _result(reused: bool = False) -> CreateServiceReceivableObligationResult:
    obligation = FeeObligation(
        id=OBLIGATION_ID,
        case_id=CASE_ID,
        source=FeeObligationSource(
            source_activity_id=SOURCE_ACTIVITY_ID,
            source_document_id=None,
            status=FeeSourceStatus.VERIFIED,
        ),
        fee_domain=FeeDomain.SERVICE,
        obligation_type="SERVICE_FEE",
        due_date=None,
        currency="CNY",
        statuses=FeeObligationStatuses(
            estimate_status=None,
            obligation_status=FeeObligationStatus.RECOGNIZED,
            client_instruction_status=FeeClientInstructionStatus.PENDING,
            draft_status=FeeObligationDraftStatus.NOT_CREATED,
            pay_list_status=FeePayListStatus.NOT_CREATED,
            payment_status=FeePaymentStatus.UNPAID,
            official_evidence_status=FeeOfficialEvidenceStatus.NOT_APPLICABLE,
        ),
        lines=(
            FeeObligationLine(
                id="66666666-6666-4666-8666-666666666229",
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_code="SEARCH|STANDARD",
                fee_name="SEARCH|STANDARD",
                fee_year_key=0,
                official_full_amount=None,
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("1200.00"),
                source_amount=Decimal("1200.00"),
                source_date=NOW.date(),
                difference_review_state=FeeDifferenceReviewState.MATCHED,
                current_identity_key=f"{CASE_ID}|SERVICE|SEARCH|STANDARD|0",
            ),
        ),
        supersedes_obligation_id=None,
        supersede_reason=None,
    )
    recognition = RecognizeFeeObligationResult(
        obligation=obligation,
        activity_id=RECOGNITION_ACTIVITY_ID,
        idempotency_key="service-receivable:service-receivable-http-229",
        reused=reused,
        superseded_obligation_id=None,
    )
    return CreateServiceReceivableObligationResult(
        recognition=recognition,
        price_book_version_id=PRICE_BOOK_ID,
        item_code="SEARCH|STANDARD",
        unit_price=Decimal("1200.00"),
        source_activity_id=SOURCE_ACTIVITY_ID,
        reused=reused,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    authenticated: bool = True,
    permission_error: BusinessError | None = None,
    commit_error: Exception | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession(commit_error)

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    app.dependency_overrides[_permission_dependency()] = permission
    monkeypatch.setattr(fees_api, "_service_price_book_utcnow", lambda: NOW)
    return TestClient(app, raise_server_exceptions=False), transaction


def test_route_freezes_exact_strict_body_direct_result_and_fee_edit() -> None:
    from app.modules.fees.obligation_schemas import (
        ServiceReceivableCreateIn,
        ServiceReceivableCreateOut,
    )

    assert tuple(ServiceReceivableCreateIn.model_fields) == (
        "price_book_version_id",
        "item_code",
        "case_id",
        "idempotency_key",
    )
    assert ServiceReceivableCreateIn.model_config["extra"] == "forbid"
    assert "actor_id" not in ServiceReceivableCreateIn.model_fields
    assert "recognized_at" not in ServiceReceivableCreateIn.model_fields
    assert _route().response_model is ServiceReceivableCreateOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Edit"


def test_create_supplies_server_context_commits_and_returns_201_or_200(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[object] = []

    def create(command: object, transaction: object) -> object:
        assert isinstance(transaction, RecordingSession)
        commands.append(command)
        return _result(reused=len(commands) == 2)

    monkeypatch.setattr(fees_api, "create_service_receivable_obligation", create)
    client, transaction = _client(monkeypatch)
    first = client.post(PATH, json=_payload())
    second = client.post(PATH, json=_payload())

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json() == {
        "recognition": {
            "obligation": {
                "id": OBLIGATION_ID,
                "case_id": CASE_ID,
                "source": {
                    "source_activity_id": SOURCE_ACTIVITY_ID,
                    "source_document_id": None,
                    "status": "VERIFIED",
                },
                "fee_domain": "SERVICE",
                "obligation_type": "SERVICE_FEE",
                "due_date": None,
                "currency": "CNY",
                "statuses": {
                    "estimate_status": None,
                    "obligation_status": "RECOGNIZED",
                    "client_instruction_status": "PENDING",
                    "draft_status": "NOT_CREATED",
                    "pay_list_status": "NOT_CREATED",
                    "payment_status": "UNPAID",
                    "official_evidence_status": "NOT_APPLICABLE",
                },
                "lines": [
                    {
                        "id": "66666666-6666-4666-8666-666666666229",
                        "obligation_id": OBLIGATION_ID,
                        "case_id": CASE_ID,
                        "source_activity_id": SOURCE_ACTIVITY_ID,
                        "fee_code": "SEARCH|STANDARD",
                        "fee_name": "SEARCH|STANDARD",
                        "fee_year_key": 0,
                        "official_full_amount": None,
                        "reduction_ratio": "0.0000",
                        "payable_amount": "1200.00",
                        "source_amount": "1200.00",
                        "source_date": "2026-08-13",
                        "difference_review_state": "MATCHED",
                        "current_identity_key": f"{CASE_ID}|SERVICE|SEARCH|STANDARD|0",
                    }
                ],
                "supersedes_obligation_id": None,
                "supersede_reason": None,
            },
            "activity_id": RECOGNITION_ACTIVITY_ID,
            "idempotency_key": "service-receivable:service-receivable-http-229",
            "reused": False,
            "superseded_obligation_id": None,
        },
        "price_book_version_id": PRICE_BOOK_ID,
        "item_code": "SEARCH|STANDARD",
        "unit_price": "1200.00",
        "source_activity_id": SOURCE_ACTIVITY_ID,
        "reused": False,
    }
    assert commands[0].price_book_version_id == PRICE_BOOK_ID
    assert commands[0].item_code == "SEARCH|STANDARD"
    assert commands[0].case_id == CASE_ID
    assert commands[0].actor_id == ACTOR_ID
    assert commands[0].recognized_at == NOW
    assert commands[0].idempotency_key == "service-receivable-http-229"
    assert transaction.commits == 2 and transaction.rollbacks == 0


@pytest.mark.parametrize(
    ("status_code", "code"),
    (
        (400, "SERVICE_RECEIVABLE_INVALID"),
        (404, "CASE_NOT_FOUND"),
        (409, "SERVICE_RECEIVABLE_CONFLICT"),
    ),
)
def test_service_errors_preserve_envelope_and_roll_back(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    def reject(*_args: object) -> object:
        raise BusinessError(code, "rejected", status_code=status_code)

    monkeypatch.setattr(fees_api, "create_service_receivable_obligation", reject)
    client, transaction = _client(monkeypatch)
    response = client.post(PATH, json=_payload())
    assert response.status_code == status_code
    assert response.json() == {"error": {"code": code, "message": "rejected", "details": None}}
    assert transaction.commits == 0 and transaction.rollbacks == 1


def test_commit_auth_permission_and_request_shape_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fees_api,
        "create_service_receivable_obligation",
        lambda *_args: _result(),
    )
    failing, transaction = _client(monkeypatch, commit_error=RuntimeError("commit failed"))
    assert failing.post(PATH, json=_payload()).status_code == 500
    assert transaction.commits == transaction.rollbacks == 1

    anonymous, transaction = _client(monkeypatch, authenticated=False)
    assert anonymous.post(PATH, json=_payload()).status_code == 401
    assert transaction.commits == transaction.rollbacks == 0

    forbidden, transaction = _client(
        monkeypatch,
        permission_error=BusinessError("FORBIDDEN", "denied", status_code=403),
    )
    assert forbidden.post(PATH, json=_payload()).status_code == 403
    assert transaction.commits == transaction.rollbacks == 0

    allowed, transaction = _client(monkeypatch)
    for payload in (
        {},
        _payload(actor_id=ACTOR_ID, recognized_at=NOW.isoformat()),
        _payload(price_book_version_id=""),
        _payload(item_code=""),
        _payload(case_id=""),
        _payload(idempotency_key=""),
    ):
        assert allowed.post(PATH, json=payload).status_code == 422
    assert transaction.commits == transaction.rollbacks == 0
