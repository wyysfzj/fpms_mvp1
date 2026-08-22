from __future__ import annotations

from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    RecordFeeObligationInstructionCommand,
)
from app.modules.fees.obligation_service import record_client_instruction
from tests.test_v8_application_auto_draft_policy import REVIEWER_ID, _apply, _seed_authority


def test_zero_government_payment_returns_business_error(
    client,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        result = _apply(transaction)
        record_client_instruction(
            RecordFeeObligationInstructionCommand(
                obligation_id=result.recognition.obligation.id,
                instruction=FeeClientInstruction.PAY,
                actor_id=REVIEWER_ID,
                idempotency_key="application-paylist-validation:pay",
            ),
            transaction,
        )
        gov_item_ids = [link.fee_item_id for link in result.draft.links]
        transaction.commit()

    pay_list_response = client.post(
        "/api/v1/pay-lists/from-fee-items",
        json={
            "fee_item_ids": gov_item_ids,
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
            "fee_item_id": gov_item_ids[0],
            "paid_date": "2026-04-11",
            "paid_amount": "0.00",
        },
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "GOV_PAYMENT_INVALID"
