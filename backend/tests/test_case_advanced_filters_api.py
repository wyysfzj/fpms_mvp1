from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.modules.billing.models import Bill, BillItem, Payment, PaymentLine
from app.modules.fees.models import FeeDraft
from app.modules.masterdata.applicants.models import Applicant


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _db_session(client: TestClient):
    db_gen = client.app.dependency_overrides[get_db]()
    db = next(db_gen)
    return db, db_gen


def _create_applicant(client: TestClient, *, name_prefix: str) -> Applicant:
    db, db_gen = _db_session(client)
    try:
        applicant = Applicant(
            code=_uid(f"{name_prefix}-CODE"),
            name_cn=_uid(f"{name_prefix}-NAME"),
            name_en=f"{name_prefix}-EN",
            is_active=True,
        )
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
        return applicant
    finally:
        db_gen.close()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    applicant_id: str | None = None,
    patent_no: str | None = None,
) -> dict:
    payload: dict[str, object] = {
        "case_no": _uid("CASEFILTER"),
        "fee_reduction": "0",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "title_cn": "高级案件查询增强测试案",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": "测试申请人",
            }
        ],
    }
    if patent_no is not None:
        payload["patent_no"] = patent_no
    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_prefix: str) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid(name_prefix), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _seed_fee_draft(client: TestClient, *, case_id: str) -> None:
    db, db_gen = _db_session(client)
    try:
        db.add(
            FeeDraft(
                case_id=case_id,
                client_id=None,
                draft_type="GENERIC",
                currency="CNY",
                status="OPEN",
            )
        )
        db.commit()
    finally:
        db_gen.close()


def _seed_billed_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
) -> None:
    db, db_gen = _db_session(client)
    try:
        bill = Bill(
            client_id=_create_client(client, auth_headers, name_prefix="CASEFILTER-BILL"),
            currency="CNY",
            direction="AR",
            status="UNSETTLED",
        )
        db.add(bill)
        db.flush()
        db.add(
            BillItem(
                bill_id=bill.id,
                case_id=case_id,
                amount=100,
            )
        )
        db.commit()
    finally:
        db_gen.close()


def _seed_paid_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
) -> None:
    db, db_gen = _db_session(client)
    try:
        payment = Payment(
            client_id=_create_client(client, auth_headers, name_prefix="CASEFILTER-PAY"),
            currency="CNY",
            amount=100,
        )
        db.add(payment)
        db.flush()
        db.add(
            PaymentLine(
                payment_id=payment.id,
                case_id=case_id,
                raw_amount=100,
                allocated_amt=100,
                balance_amt=0,
            )
        )
        db.commit()
    finally:
        db_gen.close()


def test_get_cases_filters_by_applicant_id(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    applicant_a = _create_applicant(client, name_prefix="CASEFILTER-A")
    applicant_b = _create_applicant(client, name_prefix="CASEFILTER-B")
    case_a = _create_case(client, auth_headers, applicant_id=applicant_a.id)
    case_b = _create_case(client, auth_headers, applicant_id=applicant_b.id)

    resp = client.get(
        "/api/v1/cases",
        params={"applicant_id": applicant_a.id, "page_size": 100},
        headers=auth_headers,
    )

    assert resp.status_code == 200, resp.text
    ids = {item["id"] for item in resp.json()["items"]}
    assert case_a["id"] in ids
    assert case_b["id"] not in ids


def test_get_cases_filters_by_patent_no_with_normalization(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    matching_case = _create_case(client, auth_headers, patent_no="CN 12-AB 345")
    other_case = _create_case(client, auth_headers, patent_no="US-998877")

    resp = client.get(
        "/api/v1/cases",
        params={"patent_no": "cn12ab345", "page_size": 100},
        headers=auth_headers,
    )

    assert resp.status_code == 200, resp.text
    ids = {item["id"] for item in resp.json()["items"]}
    assert matching_case["id"] in ids
    assert other_case["id"] not in ids


def test_get_cases_filters_by_minimal_fee_status(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    draft_case = _create_case(client, auth_headers)
    billed_case = _create_case(client, auth_headers)
    paid_case = _create_case(client, auth_headers)

    _seed_fee_draft(client, case_id=draft_case["id"])
    _seed_billed_case(client, auth_headers, case_id=billed_case["id"])
    _seed_paid_case(client, auth_headers, case_id=paid_case["id"])

    draft_resp = client.get(
        "/api/v1/cases",
        params={"fee_status": "DRAFT", "page_size": 100},
        headers=auth_headers,
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_ids = {item["id"] for item in draft_resp.json()["items"]}
    assert draft_case["id"] in draft_ids
    assert billed_case["id"] not in draft_ids
    assert paid_case["id"] not in draft_ids

    billed_resp = client.get(
        "/api/v1/cases",
        params={"fee_status": "BILLED", "page_size": 100},
        headers=auth_headers,
    )
    assert billed_resp.status_code == 200, billed_resp.text
    billed_ids = {item["id"] for item in billed_resp.json()["items"]}
    assert billed_case["id"] in billed_ids
    assert draft_case["id"] not in billed_ids
    assert paid_case["id"] not in billed_ids

    paid_resp = client.get(
        "/api/v1/cases",
        params={"fee_status": "PAID", "page_size": 100},
        headers=auth_headers,
    )
    assert paid_resp.status_code == 200, paid_resp.text
    paid_ids = {item["id"] for item in paid_resp.json()["items"]}
    assert paid_case["id"] in paid_ids
    assert draft_case["id"] not in paid_ids
    assert billed_case["id"] not in paid_ids


def test_get_cases_rejects_unknown_fee_status(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    resp = client.get(
        "/api/v1/cases",
        params={"fee_status": "UNKNOWN"},
        headers=auth_headers,
    )

    assert resp.status_code == 400, resp.text
    payload = resp.json()
    assert payload["error"]["code"] == "CASE_FEE_STATUS_INVALID"
