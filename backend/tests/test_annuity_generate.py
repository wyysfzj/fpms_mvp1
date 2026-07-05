"""Tests for AnnuityTask multi-year generation (FR-FE-06)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import AnnuityTask
from app.modules.cases.models import Case
from app.modules.fees.models import FeeItem, FeeRate


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


@pytest.fixture
def client_id(client: TestClient, auth_headers: dict) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("GEN-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def granted_case_id(
    client: TestClient, auth_headers: dict, client_id: str, session_factory: sessionmaker
) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Annuity Gen Test",
            "filing_date": "2020-06-15",
            "status": "GRANTED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    # Set first_annuity_year directly in DB (no API for this field yet)
    with session_factory() as db:
        case = db.query(Case).filter(Case.id == case_id).first()
        case.first_annuity_year = 3
        db.commit()

    return case_id


@pytest.fixture
def not_granted_case_id(client: TestClient, auth_headers: dict, client_id: str) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-NG"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Not Granted Case",
            "status": "NOT_FILED",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def granted_no_year_case_id(client: TestClient, auth_headers: dict, client_id: str) -> str:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("GEN-NY"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Granted No Year",
            "status": "GRANTED",
            "filing_date": "2020-01-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _seed_annuity_rates(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/fees/rates",
        json={
            "fee_code": f"CN-INV-ANNUITY-{uuid4().hex[:6]}",
            "fee_name": "发明年费",
            "fee_type": "GOV",
            "currency": "CNY",
            "default_amount": "0.00",
            "enabled": True,
            "rate_group": "ANNUITY",
            "patent_category": "INV",
            "calc_mode": "TIER",
            "calc_params": (
                '{"tiers":['
                '{"from":1,"to":3,"amount":"900.00"},'
                '{"from":4,"to":6,"amount":"1200.00"},'
                '{"from":7,"to":20,"amount":"2000.00"}'
                "]}"
            ),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text

    service_resp = client.post(
        "/api/v1/fees/rates",
        json={
            "fee_code": f"ANN-GEN-SERVICE-{uuid4().hex[:6]}",
            "fee_name": "旧服务年费",
            "fee_type": "SERVICE",
            "currency": "CNY",
            "default_amount": "50.00",
            "enabled": True,
            "rate_group": "ANNUITY",
        },
        headers=auth_headers,
    )
    assert service_resp.status_code == 201, service_resp.text


def _seed_annuity_rates_with_effective_windows(session_factory: sessionmaker) -> None:
    today = date.today()
    rows = [
        (
            "过期发明年费",
            today - timedelta(days=730),
            today - timedelta(days=1),
            '{"tiers":[{"from":1,"to":3,"amount":"700.00"},{"from":4,"to":6,"amount":"1000.00"}]}',
        ),
        (
            "发明年费",
            today - timedelta(days=1),
            today + timedelta(days=1),
            '{"tiers":[{"from":1,"to":3,"amount":"900.00"},{"from":4,"to":6,"amount":"1200.00"}]}',
        ),
        (
            "未来发明年费",
            today + timedelta(days=1),
            None,
            '{"tiers":[{"from":1,"to":3,"amount":"1900.00"},{"from":4,"to":6,"amount":"2200.00"}]}',
        ),
    ]
    with session_factory() as db:
        for fee_name, effective_from, effective_to, calc_params in rows:
            db.add(
                FeeRate(
                    id=str(uuid4()),
                    fee_code=f"CN-INV-ANNUITY-{uuid4().hex[:6]}",
                    fee_name=fee_name,
                    fee_type="GOV",
                    currency="CNY",
                    default_amount=Decimal("0.00"),
                    enabled=True,
                    rate_group="ANNUITY",
                    patent_category="INV",
                    calc_mode="TIER",
                    calc_params=calc_params,
                    effective_from=effective_from,
                    effective_to=effective_to,
                )
            )
        db.commit()


# --- GENERATE ---


def test_generate_annuity_tasks_success(
    client: TestClient, auth_headers: dict, granted_case_id: str
):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tasks_created"] > 0
    assert data["first_year"] == 3


def test_generate_case_not_found(client: TestClient, auth_headers: dict):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": "nonexistent-id"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_generate_case_not_granted(
    client: TestClient, auth_headers: dict, not_granted_case_id: str
):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": not_granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_generate_no_first_annuity_year(
    client: TestClient, auth_headers: dict, granted_no_year_case_id: str
):
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_no_year_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_generate_idempotent(client: TestClient, auth_headers: dict, granted_case_id: str):
    resp1 = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp1.status_code == 201
    created_first = resp1.json()["tasks_created"]

    resp2 = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp2.status_code == 201
    assert resp2.json()["tasks_created"] == 0
    assert resp2.json()["tasks_skipped"] == created_first


def test_generate_prefills_fee_amounts(
    client: TestClient, auth_headers: dict, granted_case_id: str
):
    _seed_annuity_rates(client, auth_headers)

    # Re-generate (delete old tasks first via direct DB or just use new case)
    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    # Check list for fee amounts
    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) > 0
    by_year = {item["year_no"]: item for item in items}
    assert Decimal(by_year[3]["gov_fee_amt"]) == Decimal("900.00")
    assert Decimal(by_year[4]["gov_fee_amt"]) == Decimal("1200.00")
    assert {Decimal(item["service_fee_amt"]) for item in items} == {Decimal("0.00")}


def test_generate_prefills_fee_amounts_from_current_effective_rate(
    client: TestClient,
    auth_headers: dict,
    granted_case_id: str,
    session_factory: sessionmaker,
):
    _seed_annuity_rates_with_effective_windows(session_factory)

    resp = client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201

    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id},
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    by_year = {item["year_no"]: item for item in list_resp.json()["items"]}
    assert Decimal(by_year[3]["gov_fee_amt"]) == Decimal("900.00")
    assert Decimal(by_year[4]["gov_fee_amt"]) == Decimal("1200.00")


# --- LIST NEW FIELDS ---


def test_list_includes_new_fields(client: TestClient, auth_headers: dict, granted_case_id: str):
    client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    resp = client.get("/api/v1/annuity/tasks", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) > 0
    item = items[0]
    for field in (
        "gov_fee_amt",
        "service_fee_amt",
        "notify_count",
        "pay_next_year",
        "draft_generated",
        "notice_sent",
        "is_overdue",
        "trigger_rule",
        "deadline_rule",
        "fee_basis",
        "fee_node_explanation",
    ):
        assert field in item, f"Missing field: {field}"
    assert item["trigger_rule"] == "年费节点到期"
    assert (
        item["deadline_rule"]
        == "以年费任务到期日为准；滞纳金按每超过规定缴费时间 1 个月加收当年全额年费 5% 提示"
    )
    assert item["fee_basis"] == f"第{item['year_no']}年度年费，按专利类型和年度阶梯费率预估"
    assert (
        item["fee_node_explanation"]
        == "年费费用节点：客户指示缴费后生成官费草单，进入官费清单并登记官方缴费回执。"
    )


def test_list_is_overdue_computed(
    client: TestClient, auth_headers: dict, granted_case_id: str, session_factory: sessionmaker
):
    with session_factory() as db:
        task = AnnuityTask(
            case_id=granted_case_id,
            client_id=db.query(Case).filter(Case.id == granted_case_id).first().client_id,
            year_no=99,
            due_date=date.today() - timedelta(days=30),
            status="OPEN",
        )
        db.add(task)
        db.commit()

    resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id, "status": "OPEN"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    overdue_items = [i for i in resp.json()["items"] if i["year_no"] == 99]
    assert len(overdue_items) == 1
    assert overdue_items[0]["is_overdue"] is True


def test_list_is_overdue_false_when_done(
    client: TestClient, auth_headers: dict, granted_case_id: str, session_factory: sessionmaker
):
    with session_factory() as db:
        task = AnnuityTask(
            case_id=granted_case_id,
            client_id=db.query(Case).filter(Case.id == granted_case_id).first().client_id,
            year_no=98,
            due_date=date.today() - timedelta(days=30),
            status="DONE",
        )
        db.add(task)
        db.commit()

    resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id, "status": "DONE"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    done_items = [i for i in resp.json()["items"] if i["year_no"] == 98]
    assert len(done_items) == 1
    assert done_items[0]["is_overdue"] is False


# --- DRAFT GENERATED FLAG ---


def test_draft_generated_flag_set(client: TestClient, auth_headers: dict, granted_case_id: str):
    _seed_annuity_rates(client, auth_headers)

    client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )

    # Get task IDs
    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id},
        headers=auth_headers,
    )
    items = list_resp.json()["items"]
    task_ids = [i["id"] for i in items[:1]]  # just one

    if task_ids:
        # Update instruction to PAY first
        client.put(
            f"/api/v1/annuity/tasks/{task_ids[0]}/instruction",
            json={"instruction": "PAY"},
            headers=auth_headers,
        )

        # Generate drafts
        draft_resp = client.post(
            "/api/v1/annuity/tasks/generate-drafts",
            json={"task_ids": task_ids},
            headers=auth_headers,
        )
        assert draft_resp.status_code in (200, 201)

        # Check flag
        list_resp2 = client.get(
            "/api/v1/annuity/tasks",
            params={"case_id": granted_case_id},
            headers=auth_headers,
        )
        for item in list_resp2.json()["items"]:
            if item["id"] == task_ids[0]:
                assert item["draft_generated"] is True


def test_annuity_draft_generation_creates_gov_only_items(
    client: TestClient,
    auth_headers: dict,
    granted_case_id: str,
    session_factory: sessionmaker,
):
    _seed_annuity_rates(client, auth_headers)
    client.post(
        "/api/v1/annuity/tasks/generate",
        json={"case_id": granted_case_id},
        headers=auth_headers,
    )
    list_resp = client.get(
        "/api/v1/annuity/tasks",
        params={"case_id": granted_case_id, "annuity_year": 3},
        headers=auth_headers,
    )
    assert list_resp.status_code == 200, list_resp.text
    task = list_resp.json()["items"][0]

    client.put(
        f"/api/v1/annuity/tasks/{task['id']}/instruction",
        json={"instruction": "PAY"},
        headers=auth_headers,
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        json={"task_ids": [task["id"]]},
        headers=auth_headers,
    )
    assert draft_resp.status_code in (200, 201), draft_resp.text
    payload = draft_resp.json()
    assert payload["summary"]["success"] == 1

    with session_factory() as db:
        items = (
            db.query(FeeItem).filter(FeeItem.draft_id == payload["success"][0]["draft_id"]).all()
        )

    assert len(items) == 1
    assert items[0].fee_type == "GOV"
    assert items[0].fee_code == "ANNUITY_GOV"
    assert Decimal(items[0].amount) == Decimal("900.00")


# --- PERMISSIONS ---


def test_permissions_generate(client: TestClient):
    resp = client.post("/api/v1/annuity/tasks/generate", json={"case_id": "x"})
    assert resp.status_code == 401
