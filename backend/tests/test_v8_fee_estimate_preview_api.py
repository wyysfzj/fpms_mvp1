from __future__ import annotations

import inspect
from contextlib import nullcontext
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import event, func, select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.core.security import get_password_hash
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees import api as fees_api
from app.modules.fees.fee_reduction import FeeReductionErrorCode, FeeReductionValidationError
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
    PreviewFeeEstimateCommand,
)
from app.modules.fees.obligation_service import (
    FeeEstimatePreviewError,
    FeeEstimatePreviewErrorCode,
)
from app.modules.fees.schemas import OfficialFeePreviewIn, OfficialFeePreviewOut

PATH = "/api/v1/fees/official-fee-preview"


class _ScalarResult:
    def __init__(self, value: object | None) -> None:
        self._value = value

    def scalar_one_or_none(self) -> object | None:
        return self._value


class _ReadOnlySession:
    def __init__(self, case: Case | None) -> None:
        self.case = case
        self.execute_calls: list[object] = []
        self.no_autoflush = nullcontext()

    def execute(self, statement: object) -> _ScalarResult:
        self.execute_calls.append(statement)
        return _ScalarResult(self.case)

    def _write_forbidden(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("preview adapter attempted a transaction write")

    add = delete = flush = commit = rollback = _write_forbidden


def _payload(case_id: str = "CASE-1") -> OfficialFeePreviewIn:
    return OfficialFeePreviewIn.model_validate(
        {
            "case_id": case_id,
            "trigger_context": {
                "trigger": "FILING_ACCEPTED",
                "source_document_id": None,
            },
            "currency": "CNY",
            "rate_effective_on": "2026-07-13",
        }
    )


def _estimate(case_id: str = "CASE-1") -> FeeEstimate:
    return FeeEstimate(
        case_id=case_id,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=FeeEstimateContext(
            trigger="FILING_ACCEPTED",
            source_document_id=None,
        ),
        currency="CNY",
        candidates=(
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="FEE-B",
                    fee_name="费用乙",
                    fee_year_key=0,
                    official_full_amount=Decimal("900"),
                    reduction_ratio=Decimal("0.85"),
                    payable_amount=Decimal("135"),
                    source_amount=None,
                    source_date=date(2026, 7, 13),
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=FeeEstimateSource(
                    rate_id="RATE-B",
                    source_document_id=None,
                    source_doc="SOURCE-DOC",
                    source_url="SOURCE-URL",
                    source_policy="SOURCE-POLICY",
                    source_version="SOURCE-VERSION",
                    status=FeeSourceStatus.VERIFIED,
                ),
            ),
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="FEE-A",
                    fee_name="费用甲",
                    fee_year_key=1,
                    official_full_amount=Decimal("20.5"),
                    reduction_ratio=Decimal("0"),
                    payable_amount=Decimal("20.5"),
                    source_amount=Decimal("20.5"),
                    source_date=None,
                    difference_review_state=FeeDifferenceReviewState.MATCHED,
                ),
                source=FeeEstimateSource(
                    rate_id="RATE-A",
                    source_document_id="DOC-1",
                    source_doc=None,
                    source_url=None,
                    source_policy=None,
                    source_version=None,
                    status=FeeSourceStatus.VERIFIED,
                ),
            ),
        ),
        total_payable_amount=Decimal("155.5"),
    )


def _carrier_counts(session_factory: sessionmaker) -> dict[str, int]:
    carriers = {
        "fee_obligation": FeeObligation,
        "fee_obligation_line": FeeObligationLine,
        "fee_obligation_draft_item_link": FeeObligationDraftItemLink,
        "fee_obligation_payment_evidence_link": FeeObligationPaymentEvidenceLink,
        "fee_draft": FeeDraft,
        "fee_item": FeeItem,
        "case_activity_event": CaseActivityEvent,
        "pay_list": PayList,
        "gov_payment": GovPayment,
    }
    with session_factory() as db:
        return {
            name: db.execute(select(func.count()).select_from(model)).scalar_one()
            for name, model in carriers.items()
        }


def _seed_case(session_factory: sessionmaker) -> str:
    case_id = str(uuid4())
    with session_factory() as db:
        db.add(Case(id=case_id, case_no=f"V8-HTTP-{uuid4().hex[:8]}"))
        db.commit()
    return case_id


def _restricted_headers(client: TestClient, session_factory: sessionmaker) -> dict[str, str]:
    username = f"v8-preview-no-perm-{uuid4().hex[:8]}"
    with session_factory() as db:
        db.add(
            T_User(
                id=str(uuid4()),
                username=username,
                display_name="No fee permission",
                password_hash=get_password_hash("secret123"),
                is_active=True,
            )
        )
        db.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "secret123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_preview_request_requires_frozen_nested_shape_and_explicit_date() -> None:
    payload = OfficialFeePreviewIn.model_validate(
        {
            "case_id": "CASE-1",
            "trigger_context": {
                "trigger": "FILING_ACCEPTED",
                "source_document_id": None,
            },
            "currency": "CNY",
            "rate_effective_on": "2026-07-13",
        }
    )

    assert payload.rate_effective_on == date(2026, 7, 13)
    assert payload.trigger_context.source_document_id is None

    with pytest.raises(ValidationError):
        OfficialFeePreviewIn.model_validate(
            {
                "case_id": "CASE-1",
                "trigger_event": "FILING_ACCEPTED",
                "currency": "CNY",
                "source_document_id": None,
            }
        )


@pytest.mark.parametrize(
    "invalid",
    [
        {},
        {
            "case_id": "CASE-1",
            "trigger_context": {"trigger": "FILING_ACCEPTED"},
            "currency": "CNY",
            "rate_effective_on": "2026-07-13",
        },
        {
            "case_id": "CASE-1",
            "trigger_context": {"trigger": "FILING_ACCEPTED", "source_document_id": None},
            "currency": "USD",
            "rate_effective_on": "2026-07-13",
        },
        {
            "case_id": "CASE-1",
            "trigger_context": {"trigger": "FILING_ACCEPTED", "source_document_id": None},
            "currency": "CNY",
            "rate_effective_on": "2026-07-13T00:00:00",
        },
        {
            "case_id": "CASE-1",
            "trigger_context": {
                "trigger": "FILING_ACCEPTED",
                "source_document_id": None,
                "extra": True,
            },
            "currency": "CNY",
            "rate_effective_on": "2026-07-13",
        },
    ],
)
def test_preview_request_rejects_missing_wrong_or_extra_values(invalid: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        OfficialFeePreviewIn.model_validate(invalid)


def test_route_keeps_exact_permission_and_direct_response_contract() -> None:
    route = next(
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == "/fees/official-fee-preview"
    )
    signature = inspect.signature(fees_api.preview_official_fee_candidates)

    assert route.methods == {"POST"}
    assert route.status_code == 200
    assert route.response_model is OfficialFeePreviewOut
    assert list(signature.parameters) == ["payload", "_perm", "db"]
    assert signature.parameters["_perm"].default.dependency.__name__ == "_perm_checker"
    assert (
        signature.parameters["_perm"].default.dependency.__closure__[0].cell_contents == "Fee.Read"
    )
    source = inspect.getsource(fees_api)
    assert "include_router" not in source
    assert "preview_official_fee_candidates as preview_official_fee_service" not in source


def test_handler_calls_frozen_service_once_with_exact_command_date_and_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = Case(id="CASE-1", case_no="CASE-NO-1")
    db = _ReadOnlySession(case)
    provider_calls: list[object] = []
    service_calls: list[dict[str, object]] = []

    class Provider:
        def __init__(self, transaction: object) -> None:
            provider_calls.append(transaction)

    def preview(**kwargs: object) -> FeeEstimate:
        service_calls.append(kwargs)
        return _estimate()

    monkeypatch.setattr(fees_api, "SqlAlchemyOfficialFeeEstimateRateProvider", Provider)
    monkeypatch.setattr(fees_api, "preview_estimate", preview)
    monkeypatch.setattr(
        fees_api,
        "preview_official_fee_service",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("legacy fallback called")),
        raising=False,
    )

    result = fees_api.preview_official_fee_candidates(_payload(), None, db)  # type: ignore[arg-type]

    assert len(db.execute_calls) == 1
    assert provider_calls == [db]
    assert len(service_calls) == 1
    assert service_calls[0]["command"] == PreviewFeeEstimateCommand(
        case_id="CASE-1",
        trigger_context=FeeEstimateContext(
            trigger="FILING_ACCEPTED",
            source_document_id=None,
        ),
        currency="CNY",
    )
    assert service_calls[0]["rate_effective_on"] == date(2026, 7, 13)
    assert isinstance(service_calls[0]["rate_provider"], Provider)
    assert result.model_dump(mode="json") == {
        "case_id": "CASE-1",
        "estimate_status": "ESTIMATE",
        "trigger_context": {"trigger": "FILING_ACCEPTED", "source_document_id": None},
        "currency": "CNY",
        "candidates": [
            {
                "line": {
                    "fee_code": "FEE-B",
                    "fee_name": "费用乙",
                    "fee_year_key": 0,
                    "official_full_amount": "900.00",
                    "reduction_ratio": "0.8500",
                    "payable_amount": "135.00",
                    "source_amount": None,
                    "source_date": "2026-07-13",
                    "difference_review_state": "SOURCE_PENDING",
                },
                "source": {
                    "rate_id": "RATE-B",
                    "source_document_id": None,
                    "source_doc": "SOURCE-DOC",
                    "source_url": "SOURCE-URL",
                    "source_policy": "SOURCE-POLICY",
                    "source_version": "SOURCE-VERSION",
                    "status": "VERIFIED",
                },
            },
            {
                "line": {
                    "fee_code": "FEE-A",
                    "fee_name": "费用甲",
                    "fee_year_key": 1,
                    "official_full_amount": "20.50",
                    "reduction_ratio": "0.0000",
                    "payable_amount": "20.50",
                    "source_amount": "20.50",
                    "source_date": None,
                    "difference_review_state": "MATCHED",
                },
                "source": {
                    "rate_id": "RATE-A",
                    "source_document_id": "DOC-1",
                    "source_doc": None,
                    "source_url": None,
                    "source_policy": None,
                    "source_version": None,
                    "status": "VERIFIED",
                },
            },
        ],
        "total_payable_amount": "155.50",
    }


def test_case_not_found_precedes_provider_and_service(monkeypatch: pytest.MonkeyPatch) -> None:
    db = _ReadOnlySession(None)
    monkeypatch.setattr(
        fees_api,
        "SqlAlchemyOfficialFeeEstimateRateProvider",
        lambda *_args: (_ for _ in ()).throw(AssertionError("provider constructed")),
    )
    monkeypatch.setattr(
        fees_api,
        "preview_estimate",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("service called")),
    )

    with pytest.raises(BusinessError) as caught:
        fees_api.preview_official_fee_candidates(_payload(), None, db)  # type: ignore[arg-type]

    assert caught.value.status_code == 404
    assert caught.value.code == "CASE_NOT_FOUND"


def test_case_gate_does_not_autoflush_caller_pending_state(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_id = str(uuid4())
    existing = Case(id=existing_id, case_no=f"V8-EXISTING-{uuid4().hex[:8]}")
    pending = Case(id=str(uuid4()), case_no=f"V8-PENDING-{uuid4().hex[:8]}")
    statements: list[str] = []

    def capture_dml(
        _connection: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: bool,
    ) -> None:
        if statement.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            statements.append(statement)

    class Provider:
        def __init__(self, _transaction: object) -> None:
            pass

    monkeypatch.setattr(fees_api, "SqlAlchemyOfficialFeeEstimateRateProvider", Provider)
    monkeypatch.setattr(fees_api, "preview_estimate", lambda **_kwargs: _estimate(existing_id))

    autoflush_factory = sessionmaker(
        autocommit=False,
        autoflush=True,
        bind=session_factory.kw["bind"],
    )
    with autoflush_factory() as db:
        db.add(existing)
        db.commit()
        db.add(pending)
        event.listen(db.bind, "before_cursor_execute", capture_dml)
        try:
            fees_api.preview_official_fee_candidates(_payload(existing_id), None, db)
            assert pending in db.new
            assert statements == []
        finally:
            event.remove(db.bind, "before_cursor_execute", capture_dml)
            db.rollback()


@pytest.mark.parametrize("code", list(FeeEstimatePreviewErrorCode))
def test_preview_errors_preserve_code_details_and_status(
    monkeypatch: pytest.MonkeyPatch,
    code: FeeEstimatePreviewErrorCode,
) -> None:
    details = {"field": "frozen", "attempt": 1}
    db = _ReadOnlySession(Case(id="CASE-1", case_no="CASE-NO-1"))

    def fail(**_kwargs: object) -> FeeEstimate:
        raise FeeEstimatePreviewError(code, details)

    monkeypatch.setattr(fees_api, "preview_estimate", fail)
    monkeypatch.setattr(fees_api, "SqlAlchemyOfficialFeeEstimateRateProvider", lambda _db: object())

    with pytest.raises(BusinessError) as caught:
        fees_api.preview_official_fee_candidates(_payload(), None, db)  # type: ignore[arg-type]

    expected_status = (
        400
        if code
        in {
            FeeEstimatePreviewErrorCode.INVALID_COMMAND,
            FeeEstimatePreviewErrorCode.TRIGGER_UNSUPPORTED,
        }
        else 409
    )
    assert (caught.value.status_code, caught.value.code, caught.value.details) == (
        expected_status,
        code.value,
        details,
    )
    details["field"] = "mutated"
    assert caught.value.details == {"field": "frozen", "attempt": 1}


@pytest.mark.parametrize("code", list(FeeReductionErrorCode))
def test_fee_reduction_errors_are_exact_409(
    monkeypatch: pytest.MonkeyPatch,
    code: FeeReductionErrorCode,
) -> None:
    details = {"field": "reduction_ratio"}
    db = _ReadOnlySession(Case(id="CASE-1", case_no="CASE-NO-1"))

    def fail(**_kwargs: object) -> FeeEstimate:
        raise FeeReductionValidationError(code, details)

    monkeypatch.setattr(fees_api, "preview_estimate", fail)
    monkeypatch.setattr(fees_api, "SqlAlchemyOfficialFeeEstimateRateProvider", lambda _db: object())

    with pytest.raises(BusinessError) as caught:
        fees_api.preview_official_fee_candidates(_payload(), None, db)  # type: ignore[arg-type]

    assert (caught.value.status_code, caught.value.code, caught.value.details) == (
        409,
        code.value,
        details,
    )


def test_http_auth_and_validation_fail_before_preview_service(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fees_api,
        "preview_estimate",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("service called")),
    )
    valid = _payload().model_dump(mode="json")

    unauthenticated = client.post(PATH, json=valid)
    legacy_shape = client.post(
        PATH,
        json={
            "case_id": "CASE-1",
            "trigger_event": "FILING_ACCEPTED",
            "source_document_id": None,
            "currency": "CNY",
        },
        headers=auth_headers,
    )

    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"
    assert legacy_shape.status_code == 422
    assert legacy_shape.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    ("scenario", "expected_status", "expected_code"),
    [
        ("success", 200, None),
        ("invalid_command", 400, "FEE_ESTIMATE_INVALID_COMMAND"),
        ("unauthenticated", 401, "AUTH_REQUIRED"),
        ("forbidden", 403, "FORBIDDEN"),
        ("missing_case", 404, "CASE_NOT_FOUND"),
        ("missing_rate", 409, "FEE_ESTIMATE_RATE_MISSING"),
        ("top_level_extra", 422, "VALIDATION_ERROR"),
    ],
)
def test_http_status_envelopes_preserve_all_carrier_counts(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    scenario: str,
    expected_status: int,
    expected_code: str | None,
) -> None:
    case_id = "MISSING-CASE"
    headers = auth_headers
    if scenario in {"success", "invalid_command", "missing_rate"}:
        case_id = _seed_case(session_factory)
    elif scenario == "forbidden":
        headers = _restricted_headers(client, session_factory)
    elif scenario == "unauthenticated":
        headers = {}

    class Provider:
        def __init__(self, _transaction: object) -> None:
            pass

    def preview(**_kwargs: object) -> FeeEstimate:
        if scenario == "invalid_command":
            raise FeeEstimatePreviewError(
                FeeEstimatePreviewErrorCode.INVALID_COMMAND,
                {"field": "case_id"},
            )
        if scenario == "missing_rate":
            raise FeeEstimatePreviewError(
                FeeEstimatePreviewErrorCode.RATE_MISSING,
                {"rate_effective_on": "2026-07-13"},
            )
        return _estimate(case_id)

    monkeypatch.setattr(fees_api, "SqlAlchemyOfficialFeeEstimateRateProvider", Provider)
    monkeypatch.setattr(fees_api, "preview_estimate", preview)
    request_json = _payload(case_id).model_dump(mode="json")
    if scenario == "top_level_extra":
        request_json["unexpected"] = True

    before = _carrier_counts(session_factory)
    response = client.post(PATH, json=request_json, headers=headers)
    after = _carrier_counts(session_factory)

    assert response.status_code == expected_status, response.text
    assert after == before
    if expected_status == 200:
        assert set(response.json()) == {
            "case_id",
            "estimate_status",
            "trigger_context",
            "currency",
            "candidates",
            "total_payable_amount",
        }
        assert response.json()["total_payable_amount"] == "155.50"
    else:
        assert response.json()["error"]["code"] == expected_code
    if scenario == "invalid_command":
        assert response.json()["error"]["details"] == {"field": "case_id"}
    if scenario == "missing_rate":
        assert response.json()["error"]["details"] == {"rate_effective_on": "2026-07-13"}


def test_http_authenticated_user_without_fee_read_gets_403(
    client: TestClient,
    session_factory: sessionmaker,
) -> None:
    response = client.post(
        PATH,
        json=_payload().model_dump(mode="json"),
        headers=_restricted_headers(client, session_factory),
    )

    assert response.status_code == 403
    assert response.json()["error"] == {
        "code": "FORBIDDEN",
        "message": "Permission denied",
        "details": {"required_perm": "Fee.Read"},
    }
