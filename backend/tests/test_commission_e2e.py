from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.commission.models import Commission, CommissionSettlement


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
            "effective_from": "2027-01-01",
            "effective_to": "2027-12-31",
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
            "status": "OPEN",
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
