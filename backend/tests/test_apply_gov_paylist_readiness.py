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
            "client_code": f"GPL-CL-{uuid4().hex[:8]}",
            "name_cn": "官费清单客户",
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
                code=f"GPL-AP-{uuid4().hex[:8]}",
                name_cn=f"官费清单申请人-{uuid4().hex[:8]}",
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
            "case_no": f"GPL-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "官费清单测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "官费清单申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _generate_apply_fee_draft(
    client: TestClient, auth_headers: dict[str, str], case_id: str
) -> str:
    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_apply_fee_gov_items_can_be_planned_and_paid(
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
    draft_id = _generate_apply_fee_draft(client, auth_headers, case_data["id"])

    items_response = client.get(f"/api/v1/fees/drafts/{draft_id}/items", headers=auth_headers)
    assert items_response.status_code == 200, items_response.text
    gov_items = [item for item in items_response.json() if item["fee_type"] == "GOV"]
    assert {item["fee_code"] for item in gov_items} == {
        "CN_INV_APPLICATION_FEE",
        "CN_EXCESS_CLAIM_FEE",
        "CN_PUBLICATION_PRINT_FEE",
    }

    pay_list_response = client.post(
        "/api/v1/pay-lists/from-fee-items",
        json={
            "fee_item_ids": [item["id"] for item in gov_items],
            "planned_pay_date": "2026-04-10",
            "remark": "TC-A-017 readiness",
        },
        headers=auth_headers,
    )
    assert pay_list_response.status_code == 200, pay_list_response.text
    pay_list_payload = pay_list_response.json()
    assert pay_list_payload["summary"]["pay_list_created"] is True
    assert pay_list_payload["summary"]["success"] == len(gov_items)
    pay_list = pay_list_payload["pay_list"]
    assert pay_list["status"] == "DRAFT"
    assert pay_list["planned_pay_date"] == "2026-04-10"
    assert Decimal(pay_list["total_amount"]) == sum(Decimal(item["amount"]) for item in gov_items)

    for item in gov_items:
        payment_response = client.post(
            "/api/v1/gov-payments",
            json={
                "pay_list_id": pay_list["id"],
                "fee_item_id": item["id"],
                "paid_date": "2026-04-12",
            },
            headers=auth_headers,
        )
        assert payment_response.status_code == 200, payment_response.text
        payment_payload = payment_response.json()["gov_payment"]
        assert payment_payload["status"] == "PAID"
        assert Decimal(payment_payload["paid_amount"]) == Decimal(item["amount"])

    detail_response = client.get(f"/api/v1/pay-lists/{pay_list['id']}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["pay_list"]["status"] == "PAID"
    assert detail["pay_list"]["paid_date"] == "2026-04-12"
    assert len(detail["gov_payments"]) == len(gov_items)

    list_response = client.get(
        "/api/v1/pay-lists",
        params={"status": "PAID", "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert list_response.status_code == 200, list_response.text
    assert any(item["id"] == pay_list["id"] for item in list_response.json()["items"])
