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
            "client_code": f"FIV-CL-{uuid4().hex[:8]}",
            "name_cn": "费用校验客户",
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
                code=f"FIV-AP-{uuid4().hex[:8]}",
                name_cn=f"费用校验申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _seed_apply_fee_rates(session_factory) -> str:
    rate_id = ""
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
            if fee_code == "CN_INV_APPLICATION_FEE":
                rate_id = rate.id
        db.commit()
    return rate_id


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
            "case_no": f"FIV-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "费用校验测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "费用校验申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_draft(client: TestClient, auth_headers: dict[str, str], case_id: str) -> dict:
    response = client.post(
        "/api/v1/fees/drafts/apply-fee/generate",
        json={"case_id": case_id, "currency": "CNY"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _arrange_draft(client, auth_headers, session_factory) -> tuple[dict, str]:
    rate_id = _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    return _create_draft(client, auth_headers, case_data["id"]), rate_id


def _assert_error(response, expected_code: str) -> None:
    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == expected_code


def test_fee_draft_rejects_blank_currency(client, auth_headers, session_factory) -> None:
    draft, _rate_id = _arrange_draft(client, auth_headers, session_factory)

    response = client.put(
        f"/api/v1/fees/drafts/{draft['id']}",
        json={"currency": ""},
        headers=auth_headers,
    )

    _assert_error(response, "FEE_DRAFT_CURRENCY_REQUIRED")


def test_fee_item_rejects_negative_quantity_and_unit_price(
    client,
    auth_headers,
    session_factory,
) -> None:
    draft, rate_id = _arrange_draft(client, auth_headers, session_factory)

    create_response = client.post(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        json={"rate_id": rate_id, "quantity": "-1", "unit_price": "100.00"},
        headers=auth_headers,
    )
    _assert_error(create_response, "FEE_ITEM_AMOUNT_INVALID")

    items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        headers=auth_headers,
    )
    assert items_response.status_code == 200, items_response.text
    item_id = items_response.json()[0]["id"]

    update_response = client.put(
        f"/api/v1/fees/drafts/{draft['id']}/items/{item_id}",
        json={"unit_price": "-1.00"},
        headers=auth_headers,
    )
    _assert_error(update_response, "FEE_ITEM_AMOUNT_INVALID")


def test_fee_item_delete_rejects_empty_billable_draft(
    client,
    auth_headers,
    session_factory,
) -> None:
    draft, _rate_id = _arrange_draft(client, auth_headers, session_factory)
    items_response = client.get(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        headers=auth_headers,
    )
    assert items_response.status_code == 200, items_response.text
    items = items_response.json()
    assert len(items) >= 2

    for item in items[:-1]:
        delete_response = client.delete(
            f"/api/v1/fees/items/{item['id']}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204, delete_response.text

    last_delete = client.delete(
        f"/api/v1/fees/items/{items[-1]['id']}",
        headers=auth_headers,
    )
    _assert_error(last_delete, "FEE_DRAFT_ITEM_REQUIRED")
