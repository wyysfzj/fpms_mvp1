from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.billing.models import CaseReceipt
from app.modules.commission.models import CommissionRule
from app.modules.commission.service import recompute_commission_settleable
from app.modules.fees.models import FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_agent_user(session_factory: sessionmaker, username_prefix: str) -> str:
    with session_factory() as db:
        role = db.query(T_Role).filter(T_Role.code == "Agent").first()
        assert role is not None
        user = T_User(
            id=str(uuid4()),
            username=f"{username_prefix}-{uuid4().hex[:8]}",
            display_name="提成阈值代理人",
            password_hash="test-hash",
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(T_UserRole(user_id=user.id, role_id=role.id))
        db.commit()
        return user.id


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CWT-CL-{uuid4().hex[:8]}",
            "name_cn": "提成阈值客户",
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
                code=f"CWT-AP-{uuid4().hex[:8]}",
                name_cn=f"提成阈值申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _seed_service_fee_rate(session_factory) -> str:
    with session_factory() as db:
        rate = db.query(FeeRate).filter(FeeRate.fee_code == "SERVICE_APPLICATION").one_or_none()
        if rate is None:
            rate = FeeRate(id=str(uuid4()), fee_code="SERVICE_APPLICATION")
            db.add(rate)
        rate.fee_name = "申请服务费"
        rate.fee_type = "SERVICE"
        rate.currency = "CNY"
        rate.default_amount = Decimal("500.00")
        rate.enabled = True
        rate.calc_mode = "FIXED"
        rate.allow_reduction = False
        db.commit()
        return rate.id


def _create_rule(client, auth_headers, *, wait_pay: bool, force_settle: bool) -> int:
    response = client.post(
        "/api/v1/commission/rules",
        json={
            "rule_name": f"提成阈值规则-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "fee_type": "SERVICE",
            "flow_dir": "CN_DOMESTIC",
            "patent_category": "INV",
            "s1_rate": "0.10",
            "s2_rate": "0.05",
            "s1_fixed_amount": "0",
            "s2_fixed_amount": "0",
            "wait_pay": wait_pay,
            "force_settle": force_settle,
            "enabled": True,
            "effective_from": "2026-01-01",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_case(
    client,
    auth_headers,
    *,
    client_id: str,
    applicant_id: str,
    main_agent_id: str,
    co_agent_id: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CWT-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "提成阈值测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "primary_agent_id": main_agent_id,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "提成阈值申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    case_data = response.json()
    update_response = client.put(
        f"/api/v1/cases/{case_data['id']}",
        json={
            "agent_splits": [
                {"agent_id": main_agent_id, "role": "Agent", "share_ratio": "70.0000"},
                {"agent_id": co_agent_id, "role": "Agent", "share_ratio": "30.0000"},
            ],
        },
        headers=auth_headers,
    )
    assert update_response.status_code == 200, update_response.text
    return case_data


def _create_bill(
    client,
    auth_headers,
    *,
    case_id: str,
    client_id: str,
    service_rate_id: str,
) -> dict:
    draft_response = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "SERVICE_FEE",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert draft_response.status_code == 201, draft_response.text
    draft = draft_response.json()
    item_response = client.post(
        f"/api/v1/fees/drafts/{draft['id']}/items",
        json={"rate_id": service_rate_id, "quantity": "1", "unit_price": "500.00"},
        headers=auth_headers,
    )
    assert item_response.status_code == 201, item_response.text
    bill_response = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": [draft["id"]], "bill_no": f"CWT-BILL-{uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text
    return bill_response.json()


def _set_service_receipt(session_factory, case_id: str, received_amt: Decimal) -> None:
    with session_factory() as db:
        receipt = (
            db.query(CaseReceipt)
            .filter(CaseReceipt.case_id == case_id, CaseReceipt.fee_type == "SERVICE")
            .one_or_none()
        )
        if receipt is None:
            receipt = CaseReceipt(
                id=str(uuid4()),
                case_id=case_id,
                fee_type="SERVICE",
                currency="CNY",
            )
            db.add(receipt)
        receipt.receivable_amt = Decimal("500.00")
        receipt.received_amt = received_amt
        db.commit()
        recompute_commission_settleable(
            db,
            case_ids=[case_id],
            as_of_date=None,
        )


def _commission_rows(client, auth_headers, case_id: str) -> list[dict]:
    response = client.get(
        "/api/v1/commission",
        params={"case_id": case_id, "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    rows = response.json()["items"]
    assert len(rows) == 2
    return rows


def _assert_all_settleable(rows: list[dict], expected: bool) -> None:
    assert {row["is_settleable"] for row in rows} == {expected}


def test_waitpay_threshold_and_force_settle_readiness(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    service_rate_id = _seed_service_fee_rate(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    main_agent_id = _create_agent_user(session_factory, "wait-main")
    co_agent_id = _create_agent_user(session_factory, "wait-co")

    wait_rule_id = _create_rule(client, auth_headers, wait_pay=True, force_settle=False)
    wait_case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        main_agent_id=main_agent_id,
        co_agent_id=co_agent_id,
    )
    _create_bill(
        client,
        auth_headers,
        case_id=wait_case["id"],
        client_id=client_id,
        service_rate_id=service_rate_id,
    )
    rows = _commission_rows(client, auth_headers, wait_case["id"])
    assert {row["rule_id"] for row in rows} == {wait_rule_id}
    _assert_all_settleable(rows, False)

    for received_amt in [Decimal("250.00"), Decimal("450.00")]:
        _set_service_receipt(session_factory, wait_case["id"], received_amt)
        _assert_all_settleable(_commission_rows(client, auth_headers, wait_case["id"]), False)

    _set_service_receipt(session_factory, wait_case["id"], Decimal("500.00"))
    _assert_all_settleable(_commission_rows(client, auth_headers, wait_case["id"]), True)

    force_rule_id = _create_rule(client, auth_headers, wait_pay=True, force_settle=True)
    force_case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        main_agent_id=main_agent_id,
        co_agent_id=co_agent_id,
    )
    _create_bill(
        client,
        auth_headers,
        case_id=force_case["id"],
        client_id=client_id,
        service_rate_id=service_rate_id,
    )
    force_rows = _commission_rows(client, auth_headers, force_case["id"])
    assert {row["rule_id"] for row in force_rows} == {force_rule_id}
    _assert_all_settleable(force_rows, True)

    with session_factory() as db:
        db.query(CommissionRule).filter(
            CommissionRule.id.in_([wait_rule_id, force_rule_id])
        ).update({"enabled": False}, synchronize_session=False)
        db.commit()
