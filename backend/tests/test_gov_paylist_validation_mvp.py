from __future__ import annotations

from test_apply_gov_paylist_readiness import (
    _create_case,
    _create_client,
    _generate_apply_fee_draft,
    _seed_applicant,
    _seed_apply_fee_rates,
)

from tests.test_v8_case_create_fee_reduction import _seed_approval_record


def test_zero_government_payment_returns_business_error(
    client,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    _seed_apply_fee_rates(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    _seed_approval_record(session_factory, applicant_ids=(applicant_id,), ratio="0.85")
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    draft_id = _generate_apply_fee_draft(client, auth_headers, case_data["id"])

    items_response = client.get(f"/api/v1/fees/drafts/{draft_id}/items", headers=auth_headers)
    assert items_response.status_code == 200, items_response.text
    gov_item = next(item for item in items_response.json() if item["fee_type"] == "GOV")

    pay_list_response = client.post(
        "/api/v1/pay-lists/from-fee-items",
        json={
            "fee_item_ids": [gov_item["id"]],
            "planned_pay_date": "2026-04-10",
        },
        headers=auth_headers,
    )
    assert pay_list_response.status_code == 200, pay_list_response.text
    pay_list = pay_list_response.json()["pay_list"]

    response = client.post(
        "/api/v1/gov-payments",
        json={
            "pay_list_id": pay_list["id"],
            "fee_item_id": gov_item["id"],
            "paid_date": "2026-04-11",
            "paid_amount": "0.00",
        },
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "GOV_PAYMENT_INVALID"
