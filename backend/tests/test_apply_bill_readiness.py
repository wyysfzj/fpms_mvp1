from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.billing.models import BillItem
from app.modules.fees.models import FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"ABL-CL-{uuid4().hex[:8]}",
            "name_cn": "申请费账单客户",
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
                code=f"ABL-AP-{uuid4().hex[:8]}",
                name_cn=f"申请费账单申请人-{uuid4().hex[:8]}",
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
            "case_no": f"ABL-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "申请费账单测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "申请费账单申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _generate_apply_fee_draft(
    client: TestClient, auth_headers: dict[str, str], case_id: str
) -> dict:
    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_apply_fee_draft_generates_unsettled_ar_bill_with_bound_items(
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
    draft = _generate_apply_fee_draft(client, auth_headers, case_data["id"])
    draft_items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items", headers=auth_headers
    )
    assert draft_items_response.status_code == 200, draft_items_response.text
    draft_items = draft_items_response.json()
    draft_item_ids = {item["id"] for item in draft_items}

    bill_response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [draft["id"]], "bill_no": f"ABL-BILL-{uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text
    bill = bill_response.json()
    assert bill["client_id"] == client_id
    assert bill["direction"] == "AR"
    assert bill["status"] == "UNSETTLED"

    detail_response = client.get(f"/api/v1/bills/{bill['id']}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["status"] == "UNSETTLED"
    assert detail["source_draft_ids"] == [draft["id"]]
    assert detail["total_gov"] == "485.00"
    assert detail["total_service"] == "0.00"
    assert detail["total_misc"] == "0.00"
    assert detail["amount"] == "485.00"
    assert detail["balance"] == "485.00"
    assert {item["draft_id"] for item in detail["items"]} == {draft["id"]}
    assert {item["case_id"] for item in detail["items"]} == {case_data["id"]}
    assert {item["fee_code"] for item in detail["items"]} == {
        "CN_INV_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_PUBLICATION_PRINT_FEE",
    }

    with session_factory() as db:
        rows = db.query(BillItem.fee_item_id).filter(BillItem.bill_id == bill["id"]).all()
    assert {row.fee_item_id for row in rows} == draft_item_ids
