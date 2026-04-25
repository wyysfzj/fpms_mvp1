from __future__ import annotations

import json
import uuid
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.commission.models import CommissionRule
from tests.test_b3_fee_linking import _create_doc_template, _create_document_raw
from tests.test_commission_waitpay_threshold import (
    _commission_rows,
    _create_agent_user,
    _create_case,
    _create_client,
    _seed_applicant,
)


def _create_oa_fee_draft_for_case(
    client: TestClient,
    auth_headers: dict[str, str],
    case_id: str,
) -> str:
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
        code=f"OA-COM-{uuid.uuid4().hex[:8].upper()}",
        name="OA提成模板",
        direction="OUT",
        fee_draft_type="OA_FEE",
        fee_item_list=fee_items_json,
    )
    document_response = _create_document_raw(
        client,
        auth_headers,
        case_id,
        direction="OUT",
        doc_template_id=template["id"],
        title="OA提成答复",
    )
    assert document_response.status_code == 201, document_response.text
    draft_id = document_response.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None
    return draft_id


def _create_oa_commission_rule(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/commission/rules",
        json={
            "rule_name": f"OA提成规则-{uuid.uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "fee_type": "SERVICE",
            "flow_dir": "CN_DOMESTIC",
            "patent_category": "INV",
            "s1_rate": "0.10",
            "s2_rate": "0.05",
            "s1_fixed_amount": "0",
            "s2_fixed_amount": "0",
            "wait_pay": False,
            "force_settle": False,
            "enabled": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_oa_service_fee_bill_enters_commission_pipeline(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    main_agent_id = _create_agent_user(session_factory, "oa-main")
    co_agent_id = _create_agent_user(session_factory, "oa-co")
    rule_id = _create_oa_commission_rule(client, auth_headers)
    case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        main_agent_id=main_agent_id,
        co_agent_id=co_agent_id,
    )
    draft_id = _create_oa_fee_draft_for_case(client, auth_headers, case["id"])

    bill_response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [draft_id], "bill_no": f"OA-COM-BILL-{uuid.uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text

    rows = _commission_rows(client, auth_headers, case["id"])
    assert {row["rule_id"] for row in rows} == {rule_id}
    assert {row["agent_id"] for row in rows} == {main_agent_id, co_agent_id}
    assert {row["fee_type"] for row in rows} == {"SERVICE"}
    assert {Decimal(row["base_fee"]) for row in rows} == {Decimal("560.00"), Decimal("240.00")}
    assert {row["is_settleable"] for row in rows} == {True}
    assert all("OA" not in (row.get("remark") or "") or row["base_fee"] for row in rows)

    with session_factory() as db:
        db.query(CommissionRule).filter(CommissionRule.id == rule_id).update(
            {"enabled": False}, synchronize_session=False
        )
        db.commit()
