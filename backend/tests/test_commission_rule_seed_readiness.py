from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.cases.models import T_CaseAgentSplit
from app.modules.commission.models import Commission
from app.modules.fees.models import FeeRate
from app.modules.masterdata.applicants.models import Applicant


def _create_agent_user(session_factory: sessionmaker, username_prefix: str) -> str:
    with session_factory() as db:
        role = db.query(T_Role).filter(T_Role.code == "Agent").first()
        assert role is not None
        user = T_User(
            id=str(uuid4()),
            username=f"{username_prefix}-{uuid4().hex[:8]}",
            display_name="提成测试代理人",
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
            "client_code": f"COM-CL-{uuid4().hex[:8]}",
            "name_cn": "提成客户",
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
                code=f"COM-AP-{uuid4().hex[:8]}",
                name_cn=f"提成申请人-{uuid4().hex[:8]}",
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


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    main_agent_id: str,
    co_agent_id: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"COM-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "提成测试案",
            "recv_date": "2026-03-01",
            "claim_count": 12,
            "fee_reduction": "0",
            "primary_agent_id": main_agent_id,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "提成申请人",
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


def _create_commission_rule(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/commission/rules",
        json={
            "rule_name": f"提成规则-{uuid4().hex[:8]}",
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


def _create_bill(
    client: TestClient,
    auth_headers: dict[str, str],
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
        json={"draft_ids": [draft["id"]], "bill_no": f"COM-BILL-{uuid4().hex[:8]}"},
        headers=auth_headers,
    )
    assert bill_response.status_code == 201, bill_response.text
    return bill_response.json()


def test_service_bill_generates_split_commission_readiness(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    service_rate_id = _seed_service_fee_rate(session_factory)
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    main_agent_id = _create_agent_user(session_factory, "commission-main")
    co_agent_id = _create_agent_user(session_factory, "commission-co")
    rule_id = _create_commission_rule(client, auth_headers)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        main_agent_id=main_agent_id,
        co_agent_id=co_agent_id,
    )

    bill = _create_bill(
        client,
        auth_headers,
        case_id=case_data["id"],
        client_id=client_id,
        service_rate_id=service_rate_id,
    )
    assert bill["status"] == "UNSETTLED"

    commission_response = client.get(
        "/api/v1/commission",
        params={"case_id": case_data["id"], "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert commission_response.status_code == 200, commission_response.text
    payload = commission_response.json()
    assert payload["total"] == 2
    by_agent = {row["agent_id"]: row for row in payload["items"]}
    assert set(by_agent) == {main_agent_id, co_agent_id}

    main_commission = by_agent[main_agent_id]
    co_commission = by_agent[co_agent_id]
    assert main_commission["rule_id"] == rule_id
    assert co_commission["rule_id"] == rule_id
    assert main_commission["fee_type"] == "SERVICE"
    assert co_commission["fee_type"] == "SERVICE"
    assert main_commission["base_fee"] == "350.00"
    assert co_commission["base_fee"] == "150.00"
    assert main_commission["s1_amount"] == "35.00"
    assert main_commission["s2_amount"] == "17.50"
    assert co_commission["s1_amount"] == "15.00"
    assert co_commission["s2_amount"] == "7.50"
    assert main_commission["wait_pay"] is False
    assert main_commission["force_settle"] is False
    assert main_commission["is_settleable"] is True

    settleable_response = client.get(
        "/api/v1/commission",
        params={
            "case_id": case_data["id"],
            "settleable_date_from": "2026-01-01",
            "settleable_date_to": "2026-12-31",
            "page": 1,
            "page_size": 20,
        },
        headers=auth_headers,
    )
    assert settleable_response.status_code == 200, settleable_response.text
    assert settleable_response.json()["total"] == 2

    with session_factory() as db:
        assert (
            db.query(T_CaseAgentSplit).filter(T_CaseAgentSplit.case_id == case_data["id"]).count()
            == 2
        )
        assert db.query(Commission).filter(Commission.case_id == case_data["id"]).count() == 2
