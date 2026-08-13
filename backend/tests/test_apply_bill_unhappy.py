from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.fees.models import FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str], label: str) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"ABU-{label}-{uuid4().hex[:8]}",
            "name_cn": f"账单非法客户{label}",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"ABU-AP-{uuid4().hex[:8]}",
                name_cn=f"账单非法申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _seed_apply_fee_rates(session_factory) -> None:
    rows = [
        ("CN_INV_APPLICATION_FEE", "发明申请费", "GOV", Decimal("900.00"), "FIXED", True),
        ("CN_EXCESS_CLAIM_FEE", "权利要求附加费", "GOV", Decimal("150.00"), "PER_CLAIM", False),
        ("CN_PUBLICATION_PRINT_FEE", "公布印刷费", "GOV", Decimal("50.00"), "FIXED", False),
    ]
    with session_factory() as db:
        for fee_code, fee_name, fee_type, amount, calc_mode, allow_reduction in rows:
            rate = db.query(FeeRate).filter(FeeRate.fee_code == fee_code).one_or_none()
            if rate is None:
                rate = FeeRate(id=str(uuid4()), fee_code=fee_code)
                db.add(rate)
            rate.fee_name = fee_name
            rate.fee_type = fee_type
            rate.currency = "CNY"
            rate.default_amount = amount
            rate.enabled = True
            rate.calc_mode = calc_mode
            rate.allow_reduction = allow_reduction
        db.commit()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    suffix: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"ABU-{suffix}-{uuid4().hex[:6]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "账单非法组合测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "账单非法申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_apply_fee_draft(client: TestClient, auth_headers: dict[str, str], case_id: str) -> dict:
    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _assert_error(response, expected_code: str) -> None:
    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == expected_code


def test_bill_from_drafts_rejects_mixed_clients(client, auth_headers, session_factory) -> None:
    _seed_apply_fee_rates(session_factory)
    applicant_id = _seed_applicant(session_factory)
    first_client_id = _create_client(client, auth_headers, "A")
    second_client_id = _create_client(client, auth_headers, "B")
    first_case = _create_case(
        client,
        auth_headers,
        client_id=first_client_id,
        applicant_id=applicant_id,
        suffix="A",
    )
    second_case = _create_case(
        client,
        auth_headers,
        client_id=second_client_id,
        applicant_id=applicant_id,
        suffix="B",
    )
    first_draft = _create_apply_fee_draft(client, auth_headers, first_case["id"])
    second_draft = _create_apply_fee_draft(client, auth_headers, second_case["id"])

    response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [first_draft["id"], second_draft["id"]]},
        headers=auth_headers,
    )

    _assert_error(response, "BILL_SINGLE_CLIENT_REQUIRED")


def test_bill_from_drafts_rejects_mixed_currencies_and_empty_draft(
    client,
    auth_headers,
    session_factory,
) -> None:
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers, "C")
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        suffix="C",
    )
    cny_draft = _create_apply_fee_draft(client, auth_headers, case_data["id"])
    usd_response = client.post(
        "/api/v1/fees/drafts",
        json={"case_id": case_data["id"], "client_id": client_id, "currency": "USD"},
        headers=auth_headers,
    )
    assert usd_response.status_code == 201, usd_response.text
    usd_draft = usd_response.json()

    mixed = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [cny_draft["id"], usd_draft["id"]]},
        headers=auth_headers,
    )
    _assert_error(mixed, "BILL_CURRENCY_MISMATCH")

    empty = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [usd_draft["id"]]},
        headers=auth_headers,
    )
    _assert_error(empty, "BILL_ITEM_REQUIRED")


def test_manual_bill_rejects_negative_total(client, auth_headers) -> None:
    client_id = _create_client(client, auth_headers, "M")

    response = client.post(
        "/api/v1/bills/manual",
        json={
            "client_id": client_id,
            "currency": "CNY",
            "items": [
                {
                    "description": "负数应收",
                    "quantity": 1,
                    "unit_price": "-1.00",
                    "fee_type": "SERVICE",
                }
            ],
        },
        headers=auth_headers,
    )

    _assert_error(response, "BILL_MANUAL_TOTAL_INVALID")
