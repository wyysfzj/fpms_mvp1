from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.core.security import get_password_hash
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.cases.models import T_CaseAgentSplit
from app.modules.commission.models import Commission, CommissionSettlement
from app.modules.commission.service import apply_commission_for_bill


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert "error" in payload, payload
    assert payload["error"].get("code") == error_code, payload
    assert payload["error"].get("message")
    return payload


def _create_client_case_with_agent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> tuple[str, str, str]:
    cli_resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("COM-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert cli_resp.status_code == 201, cli_resp.text
    client_id = cli_resp.json()["id"]

    agent_id = _uid("AGT")
    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("COM-CASE"),
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Commission E2E Case",
            "primary_agent_id": agent_id,
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    return client_id, case_resp.json()["id"], agent_id


def _create_agent_user(session_factory: sessionmaker, username_prefix: str) -> str:
    with session_factory() as db:
        role = db.query(T_Role).filter(T_Role.code == "Agent").first()
        assert role is not None, "Agent role should exist"

        user = T_User(
            id=str(uuid4()),
            username=f"{username_prefix}-{uuid4().hex[:8]}",
            display_name="Agent User",
            password_hash=get_password_hash("password123"),
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(T_UserRole(user_id=user.id, role_id=role.id))
        db.commit()
        return user.id


def _insert_commission(
    session_factory: sessionmaker,
    *,
    case_id: str,
    agent_id: str,
    settleable_date: date,
) -> int:
    with session_factory() as db:
        commission = Commission(
            case_id=case_id,
            agent_id=agent_id,
            rule_id=None,
            fee_type="SERVICE",
            base_fee=Decimal("1000.00"),
            s1_rate=Decimal("0.10"),
            s1_amount=Decimal("100.00"),
            s1_done=False,
            s2_rate=Decimal("0.05"),
            s2_amount=Decimal("50.00"),
            s2_done=False,
            wait_pay=False,
            force_settle=False,
            status="OPEN",
            is_settleable=True,
            settleable_date=settleable_date,
        )
        db.add(commission)
        db.commit()
        db.refresh(commission)
        return commission.id


def test_commission_rule_lifecycle_and_error_matrix(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "rule_name": _uid("RULE"),
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
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "remark": "base rule",
    }

    create_resp = client.post("/api/v1/commission/rules", headers=auth_headers, json=payload)
    assert create_resp.status_code == 201, create_resp.text
    create_data = create_resp.json()
    rule_id = create_data["id"]
    assert create_data["rule_name"] == payload["rule_name"]

    list_resp = client.get(
        "/api/v1/commission/rules",
        headers=auth_headers,
        params={
            "enabled": True,
            "case_type": "NORMAL",
            "fee_type": "SERVICE",
            "q": payload["rule_name"],
            "page": 1,
            "page_size": 20,
        },
    )
    assert list_resp.status_code == 200, list_resp.text
    list_payload = list_resp.json()
    assert set(list_payload) == {"items", "page", "page_size", "total"}
    assert any(item["id"] == rule_id for item in list_payload["items"])

    update_resp = client.put(
        f"/api/v1/commission/rules/{rule_id}",
        headers=auth_headers,
        json={"enabled": False, "remark": "updated", "s1_rate": "0.08"},
    )
    assert update_resp.status_code == 200, update_resp.text
    update_data = update_resp.json()
    assert update_data["id"] == rule_id
    assert update_data["enabled"] is False
    assert str(update_data["s1_rate"]) == "0.0800"

    conflict_resp = client.post(
        "/api/v1/commission/rules",
        headers=auth_headers,
        json={**payload, "rule_name": _uid("RULE-CONFLICT")},
    )
    _assert_error(conflict_resp, 409, "COMMISSION_RULE_CONFLICT")

    invalid_resp = client.post(
        "/api/v1/commission/rules",
        headers=auth_headers,
        json={
            **payload,
            "rule_name": _uid("RULE-BAD"),
            "s1_rate": "-0.01",
            "effective_from": "2028-01-01",
            "effective_to": "2028-12-31",
        },
    )
    _assert_error(invalid_resp, 400, "COMMISSION_RULE_INVALID")

    missing_resp = client.put(
        "/api/v1/commission/rules/99999999",
        headers=auth_headers,
        json={"remark": "missing"},
    )
    _assert_error(missing_resp, 404, "COMMISSION_RULE_NOT_FOUND")

    validation_resp = client.post(
        "/api/v1/commission/rules",
        headers=auth_headers,
        json={"case_type": "NORMAL"},
    )
    _assert_error(validation_resp, 422, "VALIDATION_ERROR")


def test_commission_settlement_generate_lines_idempotency_and_reports(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _client_id, case_id, agent_id = _create_client_case_with_agent(client, auth_headers)
    commission_id = _insert_commission(
        session_factory,
        case_id=case_id,
        agent_id=agent_id,
        settleable_date=date(2026, 3, 10),
    )

    create_settlement_resp = client.post(
        "/api/v1/commission/settlements",
        headers=auth_headers,
        json={
            "agent_id": agent_id,
            "period_from": "2026-03-01",
            "period_to": "2026-03-31",
            "currency": "cny",
            "remark": "March settlement",
        },
    )
    assert create_settlement_resp.status_code == 201, create_settlement_resp.text
    settlement_payload = create_settlement_resp.json()
    settlement_id = settlement_payload["id"]
    assert settlement_payload["status"] == "DRAFT"
    assert settlement_payload["line_count"] == 0

    conflict_settlement_resp = client.post(
        "/api/v1/commission/settlements",
        headers=auth_headers,
        json={
            "agent_id": agent_id,
            "period_from": "2026-03-01",
            "period_to": "2026-03-31",
            "currency": "CNY",
        },
    )
    _assert_error(conflict_settlement_resp, 409, "COMMISSION_SETTLEMENT_CONFLICT")

    invalid_settlement_resp = client.post(
        "/api/v1/commission/settlements",
        headers=auth_headers,
        json={
            "agent_id": agent_id,
            "period_from": "2026-04-01",
            "period_to": "2026-03-01",
            "currency": "CNY",
        },
    )
    _assert_error(invalid_settlement_resp, 400, "COMMISSION_SETTLEMENT_INVALID")

    generate_resp = client.post(
        f"/api/v1/commission/settlements/{settlement_id}/generate-lines",
        headers=auth_headers,
    )
    assert generate_resp.status_code == 200, generate_resp.text
    generate_payload = generate_resp.json()
    assert generate_payload["settlement_id"] == settlement_id
    assert generate_payload["line_count"] >= 1
    assert generate_payload["created_count"] >= 1
    assert generate_payload["status"] == "GENERATED"

    with session_factory() as db:
        generated_commission = db.execute(
            select(Commission).where(Commission.id == commission_id)
        ).scalar_one()
        assert generated_commission.s1_done is True
        assert generated_commission.s2_done is True
        assert generated_commission.status == "SETTLED"

    repeat_generate_resp = client.post(
        f"/api/v1/commission/settlements/{settlement_id}/generate-lines",
        headers=auth_headers,
    )
    assert repeat_generate_resp.status_code == 200, repeat_generate_resp.text
    repeat_generate_payload = repeat_generate_resp.json()
    assert repeat_generate_payload["settlement_id"] == settlement_id
    assert repeat_generate_payload["line_count"] >= 1
    assert repeat_generate_payload["created_count"] == 0

    commission_list_resp = client.get(
        "/api/v1/commission",
        headers=auth_headers,
        params={
            "agent_id": agent_id,
            "case_id": case_id,
            "status": "SETTLED",
            "settleable_date_from": "2026-03-01",
            "settleable_date_to": "2026-03-31",
            "page": 1,
            "page_size": 20,
        },
    )
    assert commission_list_resp.status_code == 200, commission_list_resp.text
    commission_list_payload = commission_list_resp.json()
    assert set(commission_list_payload) == {"items", "page", "page_size", "total"}
    assert any(item["id"] == commission_id for item in commission_list_payload["items"])

    invalid_commission_filter_resp = client.get(
        "/api/v1/commission",
        headers=auth_headers,
        params={"created_at_from": "2026-05-01", "created_at_to": "2026-04-01"},
    )
    _assert_error(invalid_commission_filter_resp, 400, "COMMISSION_FILTER_INVALID")

    today = date.today()
    report_resp = client.get(
        "/api/v1/commission/reports/settlement",
        headers=auth_headers,
        params={
            "agent_id": agent_id,
            "date_from": (today - timedelta(days=2)).isoformat(),
            "date_to": (today + timedelta(days=2)).isoformat(),
            "time_field": "line_created_at",
        },
    )
    assert report_resp.status_code == 200, report_resp.text
    report_payload = report_resp.json()
    assert "totals" in report_payload
    assert "details" in report_payload
    assert report_payload["totals"]["line_count"] >= 1
    detail = report_payload["details"][0]
    assert "s1_done" in detail
    assert "s2_done" in detail
    assert "is_settleable" in detail

    invalid_report_resp = client.get(
        "/api/v1/commission/reports/settlement",
        headers=auth_headers,
        params={"time_field": "invalid"},
    )
    _assert_error(invalid_report_resp, 400, "COMMISSION_REPORT_INVALID")

    missing_settlement_resp = client.post(
        "/api/v1/commission/settlements/99999999/generate-lines",
        headers=auth_headers,
    )
    _assert_error(missing_settlement_resp, 404, "COMMISSION_SETTLEMENT_NOT_FOUND")

    with session_factory() as db:
        settlement = db.execute(
            select(CommissionSettlement).where(CommissionSettlement.id == settlement_id)
        ).scalar_one()
        settlement.status = "CLOSED"
        db.commit()

    closed_state_resp = client.post(
        f"/api/v1/commission/settlements/{settlement_id}/generate-lines",
        headers=auth_headers,
    )
    _assert_error(closed_state_resp, 409, "COMMISSION_SETTLEMENT_CONFLICT")


def test_manual_bill_creation_triggers_commission_auto_generation(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id, case_id, agent_id = _create_client_case_with_agent(client, auth_headers)

    rule_resp = client.post(
        "/api/v1/commission/rules",
        headers=auth_headers,
        json={
            "rule_name": _uid("RULE-MANUAL"),
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
            "effective_from": "2027-01-01",
            "effective_to": "2027-12-31",
        },
    )
    assert rule_resp.status_code == 201, rule_resp.text

    manual_bill_resp = client.post(
        "/api/v1/bills/manual",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "case_id": case_id,
            "currency": "CNY",
            "direction": "AR",
            "status": "UNSETTLED",
            "bill_date": "2027-03-12",
            "items": [
                {
                    "description": "Manual service bill",
                    "quantity": 1,
                    "unit_price": "1000.00",
                    "fee_type": "SERVICE",
                }
            ],
        },
    )
    assert manual_bill_resp.status_code == 201, manual_bill_resp.text

    commission_list_resp = client.get(
        "/api/v1/commission",
        headers=auth_headers,
        params={
            "agent_id": agent_id,
            "case_id": case_id,
            "page": 1,
            "page_size": 20,
        },
    )
    assert commission_list_resp.status_code == 200, commission_list_resp.text
    items = commission_list_resp.json()["items"]
    assert len(items) == 1, items
    assert items[0]["case_id"] == case_id
    assert items[0]["agent_id"] == agent_id
    assert Decimal(str(items[0]["base_fee"])) == Decimal("1000.00")


def test_manual_bill_split_commission_rewrite_removes_stale_rows(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("COM-SPLIT-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]

    agent_one_id = _create_agent_user(session_factory, "commission-split-a")
    agent_two_id = _create_agent_user(session_factory, "commission-split-b")

    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("COM-SPLIT-CASE"),
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "分摊提成案件",
            "primary_agent_id": agent_one_id,
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    update_case_resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "agent_splits": [
                {"agent_id": agent_one_id, "role": "Agent", "share_ratio": "33.3333"},
                {"agent_id": agent_two_id, "role": "Agent", "share_ratio": "66.6667"},
            ],
        },
        headers=auth_headers,
    )
    assert update_case_resp.status_code == 200, update_case_resp.text

    rule_resp = client.post(
        "/api/v1/commission/rules",
        headers=auth_headers,
        json={
            "rule_name": _uid("RULE-SPLIT"),
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
            "effective_from": "2028-01-01",
            "effective_to": "2028-12-31",
        },
    )
    assert rule_resp.status_code == 201, rule_resp.text
    rule_id = rule_resp.json()["id"]

    bill_resp = client.post(
        "/api/v1/bills/manual",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "case_id": case_id,
            "currency": "CNY",
            "direction": "AR",
            "status": "UNSETTLED",
            "bill_date": "2028-03-12",
            "items": [
                {
                    "description": "Split service bill",
                    "quantity": 1,
                    "unit_price": "1000.00",
                    "fee_type": "SERVICE",
                }
            ],
        },
    )
    assert bill_resp.status_code == 201, bill_resp.text
    bill_id = bill_resp.json()["id"]

    with session_factory() as db:
        commissions = (
            db.execute(
                select(Commission)
                .where(
                    Commission.case_id == case_id,
                    Commission.rule_id == rule_id,
                    Commission.fee_type == "SERVICE",
                )
                .order_by(Commission.agent_id.asc())
            )
            .scalars()
            .all()
        )
        assert len(commissions) == 2, commissions
        by_agent = {row.agent_id: row for row in commissions}
        assert Decimal(str(by_agent[agent_one_id].base_fee)) == Decimal("333.33")
        assert Decimal(str(by_agent[agent_two_id].base_fee)) == Decimal("666.67")
        assert Decimal(str(by_agent[agent_one_id].s1_amount)) == Decimal("33.33")
        assert Decimal(str(by_agent[agent_one_id].s2_amount)) == Decimal("16.67")
        assert Decimal(str(by_agent[agent_two_id].s1_amount)) == Decimal("66.67")
        assert Decimal(str(by_agent[agent_two_id].s2_amount)) == Decimal("33.33")

    with session_factory() as db:
        db.query(T_CaseAgentSplit).filter(T_CaseAgentSplit.case_id == case_id).delete()
        db.add(
            T_CaseAgentSplit(
                id=str(uuid4()),
                case_id=case_id,
                agent_id=agent_one_id,
                role="Agent",
                share_ratio=Decimal("100"),
            )
        )
        db.commit()

    with session_factory() as db:
        apply_commission_for_bill(db, bill_id=bill_id, strict=True)

    with session_factory() as db:
        commissions = (
            db.execute(
                select(Commission)
                .where(
                    Commission.case_id == case_id,
                    Commission.rule_id == rule_id,
                    Commission.fee_type == "SERVICE",
                )
                .order_by(Commission.agent_id.asc())
            )
            .scalars()
            .all()
        )
        assert len(commissions) == 1, commissions
        by_agent = {row.agent_id: row for row in commissions}
        assert by_agent[agent_one_id].agent_id == agent_one_id
