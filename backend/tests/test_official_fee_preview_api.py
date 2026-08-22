from __future__ import annotations

import hashlib
import json
from collections.abc import Generator
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.billing.models import Payment, PaymentLine
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees import service as legacy_fee_service
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
    FeeRate,
    OfficialRateBook,
)
from app.modules.masterdata.applicants.models import Applicant

EFFECTIVE_ON = date(2026, 7, 13)
PATH = "/api/v1/fees/official-fee-preview"
BOOK_ID = "BOOK-OFFICIAL-FEE-PREVIEW-1"
BOOK_CODE = "SYNTHETIC-OFFICIAL-FEE-PREVIEW"
BOOK_VERSION = "SYNTHETIC-2026-07-13"
SOURCE_REFERENCE = "https://www.cnipa.gov.cn/art/2026/7/13/synthetic-preview-fixture.html"

FILING_RATES = (
    ("RATE-OFP-APPLICATION", "CN_INV_APPLICATION_FEE", "发明申请费", "900.00", "FIXED"),
    ("RATE-OFP-CLAIM", "CN_EXCESS_CLAIM_FEE", "权利要求附加费", "150.00", "PER_CLAIM"),
    ("RATE-OFP-PUBLICATION", "CN_PUBLICATION_PRINT_FEE", "公布印刷费", "50.00", "FIXED"),
    ("RATE-OFP-EXAM", "CN_SUBSTANTIVE_EXAM_FEE", "发明实审费", "2500.00", "FIXED"),
)

EXPECTED_TOP_LEVEL_KEYS = {
    "case_id",
    "estimate_status",
    "trigger_context",
    "currency",
    "candidates",
    "total_payable_amount",
}
EXPECTED_LINE_KEYS = {
    "fee_code",
    "fee_name",
    "fee_year_key",
    "official_full_amount",
    "reduction_ratio",
    "payable_amount",
    "source_amount",
    "source_date",
    "difference_review_state",
}
EXPECTED_SOURCE_KEYS = {
    "rate_id",
    "source_document_id",
    "source_doc",
    "source_url",
    "source_policy",
    "source_version",
    "status",
}


class _NoWriteRequestSession(Session):
    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("official fee preview handler called flush")

    def commit(self) -> None:
        raise AssertionError("official fee preview handler called commit")

    def rollback(self) -> None:
        raise AssertionError("official fee preview handler called rollback")


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"OFP-CL-{uuid4().hex[:8]}",
            "name_cn": "官费预览客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory: sessionmaker) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"OFP-AP-{uuid4().hex[:8]}",
                name_cn=f"官费预览申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"OFP-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "官费预览测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "has_exam_request": True,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "官费预览申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _case_fixture(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> dict[str, object]:
    return _create_case(
        client,
        auth_headers,
        client_id=_create_client(client, auth_headers),
        applicant_id=_seed_applicant(session_factory),
    )


def _seed_verified_book(session_factory: sessionmaker) -> None:
    snapshot = _canonical(
        {
            "schema_version": "CNIPA_RATE_SOURCE_V1",
            "sources": [
                {
                    "content_sha256": "a" * 64,
                    "document_no": None,
                    "published_on": EFFECTIVE_ON.isoformat(),
                    "retrieved_at": "2026-07-13T00:00:00Z",
                    "title": "Synthetic official-fee preview fixture — not a legal rate source",
                    "url": SOURCE_REFERENCE,
                }
            ],
        }
    )
    with session_factory() as db:
        actor = db.scalar(select(T_User).where(T_User.username == "admin"))
        assert actor is not None
        book = OfficialRateBook(
            id=BOOK_ID,
            book_code=BOOK_CODE,
            version_code=BOOK_VERSION,
            source_authority="CNIPA",
            source_reference=SOURCE_REFERENCE,
            source_version="SYNTHETIC-CNIPA-PREVIEW-FIXTURE",
            source_published_on=EFFECTIVE_ON,
            source_snapshot=snapshot,
            source_snapshot_hash=hashlib.sha256(snapshot.encode("utf-8")).hexdigest(),
            approval_status="APPROVED",
            approved_by=actor.id,
            approved_at=datetime(2026, 7, 13, 8, 0),
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 12, 31),
            activation_status="ACTIVE",
            activated_by=actor.id,
            activated_at=datetime(2026, 7, 13, 9, 0),
            current_identity_key=f"CNIPA|{BOOK_CODE}",
        )
        db.add(book)
        db.commit()


def _seed_rate(
    session_factory: sessionmaker,
    *,
    rate_id: str,
    fee_code: str,
    fee_name: str,
    amount: str,
    calc_mode: str,
    official_rate_book_id: str | None = BOOK_ID,
    effective_from: date = EFFECTIVE_ON,
    effective_to: date | None = EFFECTIVE_ON,
) -> None:
    with session_factory() as db:
        db.add(
            FeeRate(
                id=rate_id,
                fee_code=fee_code,
                fee_name=fee_name,
                fee_type="GOV",
                currency="CNY",
                default_amount=Decimal(amount),
                enabled=True,
                calc_mode=calc_mode,
                allow_reduction=True,
                effective_from=effective_from,
                effective_to=effective_to,
                source_doc="Synthetic official-fee preview fixture",
                source_status="CONFIRMED",
                official_rate_book_id=official_rate_book_id,
            )
        )
        db.commit()


def _seed_filing_rates(session_factory: sessionmaker) -> None:
    for rate_id, fee_code, fee_name, amount, calc_mode in FILING_RATES:
        _seed_rate(
            session_factory,
            rate_id=rate_id,
            fee_code=fee_code,
            fee_name=fee_name,
            amount=amount,
            calc_mode=calc_mode,
        )


def _strict_payload(
    case_id: str,
    *,
    trigger: str = "FILING_ACCEPTED",
    source_document_id: str | None = "DOC-OFP-1",
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "trigger_context": {
            "trigger": trigger,
            "source_document_id": source_document_id,
        },
        "currency": "CNY",
        "rate_effective_on": EFFECTIVE_ON.isoformat(),
    }


def _carrier_counts(session_factory: sessionmaker) -> tuple[int, ...]:
    carriers = (
        FeeDraft,
        FeeItem,
        FeeObligation,
        FeeObligationLine,
        FeeObligationPaymentEvidenceLink,
        CaseActivityEvent,
        PayList,
        GovPayment,
        Payment,
        PaymentLine,
    )
    with session_factory() as db:
        return tuple(db.scalar(select(func.count()).select_from(model)) or 0 for model in carriers)


def _post_without_business_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    payload: dict[str, object],
):
    app = client.app
    assert isinstance(app, FastAPI)
    original_override = app.dependency_overrides[get_db]
    request_session_factory = sessionmaker(
        class_=_NoWriteRequestSession,
        autocommit=False,
        autoflush=False,
        bind=session_factory.kw["bind"],
    )

    def override_get_db() -> Generator[Session, None, None]:
        with request_session_factory() as db:
            yield db

    before = _carrier_counts(session_factory)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(PATH, json=payload, headers=auth_headers)
    finally:
        app.dependency_overrides[get_db] = original_override
    assert _carrier_counts(session_factory) == before
    return response


def _assert_direct_response(
    body: dict[str, object],
    *,
    case_id: str,
    trigger: str,
    source_document_id: str | None,
    expected: tuple[tuple[str, str, str, str], ...],
) -> None:
    assert set(body) == EXPECTED_TOP_LEVEL_KEYS
    assert body["case_id"] == case_id
    assert body["estimate_status"] == "ESTIMATE"
    assert body["trigger_context"] == {
        "trigger": trigger,
        "source_document_id": source_document_id,
    }
    assert body["currency"] == "CNY"
    assert body["total_payable_amount"] == format(
        sum((Decimal(amount) for _, _, amount, _ in expected), Decimal("0.00")),
        ".2f",
    )

    candidates = body["candidates"]
    assert isinstance(candidates, list)
    assert [candidate["line"]["fee_code"] for candidate in candidates] == [
        fee_code for fee_code, _, _, _ in expected
    ]
    for candidate, (fee_code, fee_name, amount, rate_id) in zip(candidates, expected, strict=True):
        assert set(candidate) == {"line", "source"}
        line = candidate["line"]
        source = candidate["source"]
        assert set(line) == EXPECTED_LINE_KEYS
        assert set(source) == EXPECTED_SOURCE_KEYS
        assert line["fee_code"] == fee_code
        assert line["fee_name"] == fee_name
        assert line["fee_year_key"] == 0
        assert line["official_full_amount"] == amount
        assert line["reduction_ratio"] == "0.0000"
        assert line["payable_amount"] == amount
        assert line["source_amount"] is None
        assert line["source_date"] == EFFECTIVE_ON.isoformat()
        assert line["difference_review_state"] == "SOURCE_PENDING"
        assert source == {
            "rate_id": rate_id,
            "source_document_id": source_document_id,
            "source_doc": "SYNTHETIC-CNIPA-PREVIEW-FIXTURE",
            "source_url": SOURCE_REFERENCE,
            "source_policy": BOOK_CODE,
            "source_version": BOOK_VERSION,
            "status": "VERIFIED",
        }


def test_official_fee_preview_returns_verified_filing_projection_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_verified_book(session_factory)
    _seed_filing_rates(session_factory)
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])

    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        _strict_payload(case_id),
    )

    assert response.status_code == 200, response.text
    _assert_direct_response(
        response.json(),
        case_id=case_id,
        trigger="FILING_ACCEPTED",
        source_document_id="DOC-OFP-1",
        expected=(
            ("CN_INV_APPLICATION_FEE", "发明申请费", "900.00", "RATE-OFP-APPLICATION"),
            ("CN_EXCESS_CLAIM_FEE", "权利要求附加费", "300.00", "RATE-OFP-CLAIM"),
            ("CN_PUBLICATION_PRINT_FEE", "公布印刷费", "50.00", "RATE-OFP-PUBLICATION"),
            ("CN_SUBSTANTIVE_EXAM_FEE", "发明实审费", "2500.00", "RATE-OFP-EXAM"),
        ),
    )


def test_official_fee_preview_uses_only_rate_effective_on_fixed_date(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_verified_book(session_factory)
    _seed_filing_rates(session_factory)
    _seed_rate(
        session_factory,
        rate_id="RATE-OFP-APPLICATION-EXPIRED",
        fee_code="CN_INV_APPLICATION_FEE",
        fee_name="过期发明申请费",
        amount="800.00",
        calc_mode="FIXED",
        effective_from=date(2025, 1, 1),
        effective_to=date(2026, 7, 12),
    )
    _seed_rate(
        session_factory,
        rate_id="RATE-OFP-APPLICATION-FUTURE",
        fee_code="CN_INV_APPLICATION_FEE",
        fee_name="未来发明申请费",
        amount="1900.00",
        calc_mode="FIXED",
        effective_from=date(2026, 7, 14),
        effective_to=date(2026, 12, 31),
    )
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])

    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        _strict_payload(case_id, source_document_id=None),
    )

    assert response.status_code == 200, response.text
    _assert_direct_response(
        response.json(),
        case_id=case_id,
        trigger="FILING_ACCEPTED",
        source_document_id=None,
        expected=(
            ("CN_INV_APPLICATION_FEE", "发明申请费", "900.00", "RATE-OFP-APPLICATION"),
            ("CN_EXCESS_CLAIM_FEE", "权利要求附加费", "300.00", "RATE-OFP-CLAIM"),
            ("CN_PUBLICATION_PRINT_FEE", "公布印刷费", "50.00", "RATE-OFP-PUBLICATION"),
            ("CN_SUBSTANTIVE_EXAM_FEE", "发明实审费", "2500.00", "RATE-OFP-EXAM"),
        ),
    )
    serialized = response.text
    assert "RATE-OFP-APPLICATION-EXPIRED" not in serialized
    assert "RATE-OFP-APPLICATION-FUTURE" not in serialized
    assert '"800.00"' not in serialized
    assert '"1900.00"' not in serialized


def test_official_fee_preview_never_falls_back_to_enabled_unlinked_rate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_verified_book(session_factory)
    _seed_filing_rates(session_factory)
    _seed_rate(
        session_factory,
        rate_id="RATE-OFP-UNLINKED-LEGACY",
        fee_code="CN_INV_APPLICATION_FEE",
        fee_name="未关联旧费率",
        amount="9999.00",
        calc_mode="FIXED",
        official_rate_book_id=None,
    )
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])

    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        _strict_payload(case_id),
    )

    assert response.status_code == 200, response.text
    _assert_direct_response(
        response.json(),
        case_id=case_id,
        trigger="FILING_ACCEPTED",
        source_document_id="DOC-OFP-1",
        expected=(
            ("CN_INV_APPLICATION_FEE", "发明申请费", "900.00", "RATE-OFP-APPLICATION"),
            ("CN_EXCESS_CLAIM_FEE", "权利要求附加费", "300.00", "RATE-OFP-CLAIM"),
            ("CN_PUBLICATION_PRINT_FEE", "公布印刷费", "50.00", "RATE-OFP-PUBLICATION"),
            ("CN_SUBSTANTIVE_EXAM_FEE", "发明实审费", "2500.00", "RATE-OFP-EXAM"),
        ),
    )
    assert "RATE-OFP-UNLINKED-LEGACY" not in response.text
    assert '"9999.00"' not in response.text
    assert all(
        candidate["source"]["status"] == "VERIFIED" for candidate in response.json()["candidates"]
    )


def test_official_fee_preview_returns_verified_reexamination_projection_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_verified_book(session_factory)
    _seed_rate(
        session_factory,
        rate_id="RATE-OFP-REEXAM-INV",
        fee_code="CN_REEXAM_FEE_INV",
        fee_name="发明专利复审费",
        amount="1000.00",
        calc_mode="FIXED",
    )
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])

    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        _strict_payload(
            case_id,
            trigger="REEXAM_REQUESTED",
            source_document_id="DOC-REJECTION-1",
        ),
    )

    assert response.status_code == 200, response.text
    _assert_direct_response(
        response.json(),
        case_id=case_id,
        trigger="REEXAM_REQUESTED",
        source_document_id="DOC-REJECTION-1",
        expected=(("CN_REEXAM_FEE_INV", "发明专利复审费", "1000.00", "RATE-OFP-REEXAM-INV"),),
    )


def test_official_fee_preview_rejects_unsupported_strict_trigger_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])

    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        _strict_payload(case_id, trigger="RESTORE_RIGHT_REQUESTED"),
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "FEE_ESTIMATE_TRIGGER_UNSUPPORTED"


def test_official_fee_preview_rejects_complete_legacy_shape_before_fallback(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_id = str(_case_fixture(client, auth_headers, session_factory)["id"])
    legacy_calls: list[object] = []

    def legacy_preview(*args: object, **kwargs: object) -> None:
        legacy_calls.append((args, kwargs))

    monkeypatch.setattr(legacy_fee_service, "preview_official_fee_candidates", legacy_preview)
    response = _post_without_business_writes(
        client,
        auth_headers,
        session_factory,
        {
            "case_id": case_id,
            "currency": "CNY",
            "trigger_event": "FILING_ACCEPTED",
            "source_document_id": "DOC-OFP-1",
        },
    )

    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert legacy_calls == []
