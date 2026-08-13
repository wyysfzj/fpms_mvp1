from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.fees.models import FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"POR-CL-{uuid4().hex[:8]}",
            "name_cn": "付款冲销客户",
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
                code=f"POR-AP-{uuid4().hex[:8]}",
                name_cn=f"付款冲销申请人-{uuid4().hex[:8]}",
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
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"POR-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "付款冲销测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "付款冲销申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_bill(client: TestClient, auth_headers: dict[str, str], case_id: str) -> dict:
    draft_response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert draft_response.status_code == 201, draft_response.text
    draft = draft_response.json()
    bill_response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [draft["id"]], "bill_no": f"POR-BILL-{uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text
    return bill_response.json()


def _create_payment(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    amount: str,
) -> tuple[dict, str]:
    response = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": amount,
            "pay_no": f"POR-PAY-{uuid4().hex[:8]}",
            "pay_date": "2026-04-20",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    payment = response.json()
    detail_response = client.get(f"/api/v1/payments/{payment['id']}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    line = detail_response.json()["payment_lines"][0]
    return payment, line["id"]


def test_payment_offset_updates_bill_and_case_receipts(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    bill = _create_bill(client, auth_headers, case_data["id"])
    payment, payment_line_id = _create_payment(
        client,
        auth_headers,
        client_id=client_id,
        amount="300.00",
    )

    offset_response = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line_id,
            "bill_id": bill["id"],
            "offset_amt": "300.00",
            "offset_date": "2026-04-21",
        },
        headers=auth_headers,
    )
    assert offset_response.status_code == 201, offset_response.text
    offset = offset_response.json()
    assert offset["bill_id"] == bill["id"]
    assert offset["payment_line_id"] == payment_line_id
    assert offset["offset_amt"] == "300.00"
    assert offset["is_reversed"] is False

    bill_detail_response = client.get(f"/api/v1/bills/{bill['id']}", headers=auth_headers)
    assert bill_detail_response.status_code == 200, bill_detail_response.text
    bill_detail = bill_detail_response.json()
    assert bill_detail["status"] == "PARTIALLY_SETTLED"
    assert bill_detail["amount"] == "1250.00"
    assert bill_detail["balance"] == "950.00"

    payment_detail_response = client.get(f"/api/v1/payments/{payment['id']}", headers=auth_headers)
    assert payment_detail_response.status_code == 200, payment_detail_response.text
    payment_line = payment_detail_response.json()["payment_lines"][0]
    assert payment_line["allocated_amt"] == "300.00"
    assert payment_line["balance_amt"] == "0.00"

    offsets_response = client.get(
        "/api/v1/offsets",
        params={"bill_id": bill["id"], "is_reversed": False},
        headers=auth_headers,
    )
    assert offsets_response.status_code == 200, offsets_response.text
    assert any(item["id"] == offset["id"] for item in offsets_response.json()["items"])

    receipt_response = client.get(f"/api/v1/cases/{case_data['id']}/receipts", headers=auth_headers)
    assert receipt_response.status_code == 200, receipt_response.text
    receipt = receipt_response.json()
    assert receipt["currency"] == "CNY"
    assert receipt["received_amt"] == "300.00"
    assert receipt["last_receipt_date"] == "2026-04-21"
    assert Decimal(receipt["receivable_amt"]) == Decimal("1250.00")
    assert Decimal(receipt["receivable_amt"]) > Decimal(receipt["received_amt"])
    assert receipt["bills"][0]["id"] == bill["id"]
