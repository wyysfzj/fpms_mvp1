from __future__ import annotations

import json
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import GovPayment, PayList
from tests.test_b3_fee_linking import (
    _create_case,
    _create_client,
    _create_doc_template,
    _create_document_raw,
)


def _create_oa_fee_draft(client: TestClient, auth_headers: dict[str, str]) -> tuple[dict, str]:
    fee_items_json = json.dumps(
        [
            {
                "fee_code": "OA_SERVICE",
                "fee_name": "OA服务费",
                "fee_type": "SERVICE",
                "amount": "800.00",
            },
            {
                "fee_code": "OA_GOV",
                "fee_name": "OA官费",
                "fee_type": "GOV",
                "amount": "120.00",
            },
        ],
        ensure_ascii=False,
    )
    template = _create_doc_template(
        client,
        auth_headers,
        code=f"OA-BILL-{uuid.uuid4().hex[:8].upper()}",
        name="OA账单收款模板",
        direction="OUT",
        fee_draft_type="OA_FEE",
        fee_item_list=fee_items_json,
    )
    client_data = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_data["id"])
    document_response = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=template["id"],
        title="OA账单收款答复",
    )
    assert document_response.status_code == 201, document_response.text
    draft_id = document_response.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None
    return case, draft_id


def test_oa_fee_draft_fails_closed_for_gov_paylist_and_supports_bill_receipt(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case, draft_id = _create_oa_fee_draft(client, auth_headers)

    items_response = client.get(f"/api/v1/fees/drafts/{draft_id}/items", headers=auth_headers)
    assert items_response.status_code == 200, items_response.text
    items = items_response.json()
    gov_items = [item for item in items if item["fee_type"] == "GOV"]
    service_items = [item for item in items if item["fee_type"] == "SERVICE"]
    assert len(gov_items) == 1
    assert len(service_items) == 1

    pay_list_response = client.post(
        "/api/v1/pay-lists/from-fee-items",
        json={
            "fee_item_ids": [item["id"] for item in gov_items],
            "planned_pay_date": "2026-04-10",
            "remark": "TC-B-010 readiness",
        },
        headers=auth_headers,
    )
    assert pay_list_response.status_code == 409, pay_list_response.text
    assert pay_list_response.json()["error"] == {
        "code": "PAY_LIST_OBLIGATION_LINK_REQUIRED",
        "message": "Fee item must be linked to a fee obligation",
        "details": None,
    }
    with session_factory() as db:
        assert db.scalars(select(PayList)).all() == []
        assert db.scalars(select(GovPayment)).all() == []

    bill_response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [draft_id], "bill_no": f"OA-BILL-{uuid.uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text
    bill = bill_response.json()
    assert bill["status"] == "UNSETTLED"

    bill_detail_response = client.get(f"/api/v1/bills/{bill['id']}", headers=auth_headers)
    assert bill_detail_response.status_code == 200, bill_detail_response.text
    bill_detail = bill_detail_response.json()
    assert bill_detail["amount"] == "920.00"
    assert bill_detail["balance"] == "920.00"
    assert {item["fee_code"] for item in bill_detail["items"]} == {"OA_GOV", "OA_SERVICE"}

    payment_response = client.post(
        "/api/v1/payments",
        json={
            "client_id": bill["client_id"],
            "amount": "920.00",
            "pay_no": f"OA-PAY-{uuid.uuid4().hex[:8]}",
            "pay_date": "2026-04-20",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert payment_response.status_code == 201, payment_response.text
    payment = payment_response.json()
    payment_detail_response = client.get(f"/api/v1/payments/{payment['id']}", headers=auth_headers)
    assert payment_detail_response.status_code == 200, payment_detail_response.text
    payment_line = payment_detail_response.json()["payment_lines"][0]

    offset_response = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line["id"],
            "bill_id": bill["id"],
            "offset_amt": "920.00",
            "offset_date": "2026-04-21",
        },
        headers=auth_headers,
    )
    assert offset_response.status_code == 201, offset_response.text

    settled_bill_response = client.get(f"/api/v1/bills/{bill['id']}", headers=auth_headers)
    assert settled_bill_response.status_code == 200, settled_bill_response.text
    settled_bill = settled_bill_response.json()
    assert settled_bill["status"] == "SETTLED"
    assert settled_bill["balance"] == "0.00"

    receipt_response = client.get(f"/api/v1/cases/{case['id']}/receipts", headers=auth_headers)
    assert receipt_response.status_code == 200, receipt_response.text
    receipt = receipt_response.json()
    assert receipt["received_amt"] == "920.00"
    assert receipt["receivable_amt"] == "920.00"
    assert receipt["last_receipt_date"] == "2026-04-21"
