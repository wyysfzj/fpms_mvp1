from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import T_CaseAgentSplit
from app.modules.fees.models import FeeDraft, FeeItem
from app.modules.fees.service import recalc_fee_draft_totals

FEE_DRAFTS_URL = "/api/v1/fees/drafts"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client, auth_headers, *, name_prefix: str) -> dict:
    resp = client.post(
        "/api/v1/clients",
        json={
            "name_cn": _uid(name_prefix),
            "name_en": f"{name_prefix}-EN",
            "client_type": "CORPORATE",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client,
    auth_headers,
    *,
    client_id: str,
    case_tag: str,
    case_type: str = "NORMAL",
    from_country: str | None = None,
    to_country: str | None = None,
    primary_agent_id: str | None = None,
) -> dict:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid(case_tag),
            "case_type": case_type,
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": f"{case_tag} 案件",
            "from_country": from_country,
            "to_country": to_country,
            "primary_agent_id": primary_agent_id,
            "applicants": [{"seq": 1, "is_first": True, "name_cn": f"{case_tag} 申请人"}],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_case_agent_splits(
    session_factory: sessionmaker,
    *,
    case_id: str,
    rows: list[tuple[str, str | None, str]],
) -> None:
    with session_factory() as db:
        for agent_id, role, share_ratio in rows:
            db.add(
                T_CaseAgentSplit(
                    case_id=case_id,
                    agent_id=agent_id,
                    role=role,
                    share_ratio=Decimal(share_ratio),
                )
            )
        db.commit()


def _create_bill_from_drafts(client, auth_headers, *, draft_ids: list[str]) -> dict:
    resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": draft_ids, "bill_no": _uid("BILL")},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_manual_bill(
    client,
    auth_headers,
    *,
    client_id: str,
    case_id: str | None,
    currency: str,
    amount: str,
) -> dict:
    resp = client.post(
        "/api/v1/bills/manual",
        json={
            "client_id": client_id,
            "case_id": case_id,
            "currency": currency,
            "direction": "AR",
            "status": "UNSETTLED",
            "bill_date": "2026-03-29",
            "due_date": "2026-04-15",
            "items": [
                {
                    "description": "手工账单项",
                    "quantity": 1,
                    "unit_price": amount,
                    "fee_type": "SERVICE",
                }
            ],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_payment(client, auth_headers, *, client_id: str, amount: str, currency: str) -> dict:
    resp = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": amount,
            "pay_date": "2026-03-30",
            "pay_no": _uid("PAY"),
            "currency": currency,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_payment_line_id(client, auth_headers, *, payment_id: str) -> str:
    resp = client.get(f"/api/v1/payments/{payment_id}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    lines = resp.json()["payment_lines"]
    assert lines, "expected payment lines"
    return lines[0]["id"]


def _create_offset(
    client,
    auth_headers,
    *,
    payment_line_id: str,
    bill_id: str,
    amount: str,
) -> dict:
    resp = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line_id,
            "bill_id": bill_id,
            "offset_amt": amount,
            "offset_date": "2026-03-30",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_fee_draft(
    session_factory: sessionmaker,
    *,
    case_id: str,
    client_id: str,
    draft_type: str,
    currency: str,
    status: str,
    created_at: datetime,
    lines: list[tuple[str, str]],
) -> str:
    with session_factory() as db:
        draft = FeeDraft(
            id=str(uuid4()),
            case_id=case_id,
            client_id=client_id,
            draft_type=draft_type,
            currency=currency,
            status=status,
            total_gov=Decimal("0"),
            total_service=Decimal("0"),
            total_misc=Decimal("0"),
            amount=Decimal("0"),
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(draft)
        db.flush()

        for index, (fee_type, amount_text) in enumerate(lines, start=1):
            amount = Decimal(amount_text)
            db.add(
                FeeItem(
                    id=str(uuid4()),
                    draft_id=draft.id,
                    case_id=case_id,
                    rate_id=None,
                    fee_code=_uid(f"FEE-{fee_type}-{index}"),
                    fee_name=f"{fee_type} fee {index}",
                    fee_type=fee_type,
                    quantity=Decimal("1"),
                    unit_price=amount,
                    amount=amount,
                    created_at=created_at,
                    updated_at=created_at,
                )
            )

        db.flush()
        recalc_fee_draft_totals(db, draft_id=draft.id)
        return draft.id


def test_fee_drafts_report_returns_summary_and_retains_list_contract(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="FEE-RPT-CLI-A")
    client_b = _create_client(client, auth_headers, name_prefix="FEE-RPT-CLI-B")
    case_a = _create_case(client, auth_headers, client_id=client_a["id"], case_tag="FEE-RPT-CASE-A")
    case_b = _create_case(client, auth_headers, client_id=client_b["id"], case_tag="FEE-RPT-CASE-B")

    service_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="SERVICE_REPORT",
        currency="CNY",
        status="OPEN",
        created_at=datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "100.00"), ("MISC", "10.00")],
    )
    gov_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="GOV_REPORT",
        currency="CNY",
        status="LOCKED",
        created_at=datetime(2026, 3, 5, 9, 0, tzinfo=timezone.utc),
        lines=[("GOV", "80.00")],
    )
    mixed_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_b["id"],
        client_id=client_b["id"],
        draft_type="MIXED_REPORT",
        currency="USD",
        status="OPEN",
        created_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "60.00"), ("GOV", "40.00"), ("MISC", "10.00")],
    )

    _create_bill_from_drafts(client, auth_headers, draft_ids=[service_draft_id])

    resp = client.get(FEE_DRAFTS_URL, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 3
    assert set(payload) >= {"items", "page", "page_size", "total", "summary"}

    summary = payload["summary"]
    assert summary["total_draft_count"] == 3
    assert Decimal(str(summary["government_fee_amount"])) == Decimal("120.00")
    assert Decimal(str(summary["service_fee_amount"])) == Decimal("160.00")
    assert Decimal(str(summary["income_amount"])) == Decimal("300.00")

    assert {item["id"] for item in payload["items"]} == {
        service_draft_id,
        gov_draft_id,
        mixed_draft_id,
    }


def test_fee_drafts_report_supports_approved_filters(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="FEE-RPT-FLT-A")
    client_b = _create_client(client, auth_headers, name_prefix="FEE-RPT-FLT-B")
    case_a = _create_case(client, auth_headers, client_id=client_a["id"], case_tag="FEE-FLT-CASE-A")
    case_b = _create_case(client, auth_headers, client_id=client_b["id"], case_tag="FEE-FLT-CASE-B")

    service_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="SERVICE_REPORT",
        currency="CNY",
        status="OPEN",
        created_at=datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "100.00")],
    )
    gov_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="GOV_REPORT",
        currency="CNY",
        status="LOCKED",
        created_at=datetime(2026, 3, 5, 9, 0, tzinfo=timezone.utc),
        lines=[("GOV", "80.00")],
    )
    mixed_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_b["id"],
        client_id=client_b["id"],
        draft_type="MIXED_REPORT",
        currency="USD",
        status="OPEN",
        created_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "60.00"), ("GOV", "40.00"), ("MISC", "10.00")],
    )

    _create_bill_from_drafts(client, auth_headers, draft_ids=[service_draft_id])

    client_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"client_id": client_a["id"]},
        headers=auth_headers,
    )
    assert client_filtered.status_code == 200, client_filtered.text
    client_payload = client_filtered.json()
    assert client_payload["total"] == 2
    assert client_payload["summary"]["total_draft_count"] == 2
    assert {item["id"] for item in client_payload["items"]} == {
        service_draft_id,
        gov_draft_id,
    }

    case_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"case_id": case_b["id"]},
        headers=auth_headers,
    )
    assert case_filtered.status_code == 200, case_filtered.text
    case_payload = case_filtered.json()
    assert case_payload["total"] == 1
    assert case_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in case_payload["items"]] == [mixed_draft_id]

    service_fee_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"fee_type": "SERVICE", "client_id": client_b["id"]},
        headers=auth_headers,
    )
    assert service_fee_filtered.status_code == 200, service_fee_filtered.text
    service_fee_payload = service_fee_filtered.json()
    assert service_fee_payload["total"] == 1
    assert service_fee_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in service_fee_payload["items"]] == [mixed_draft_id]

    currency_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"currency": "usd", "client_id": client_b["id"]},
        headers=auth_headers,
    )
    assert currency_filtered.status_code == 200, currency_filtered.text
    currency_payload = currency_filtered.json()
    assert currency_payload["total"] == 1
    assert currency_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in currency_payload["items"]] == [mixed_draft_id]

    draft_status_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"draft_status": "LOCKED", "client_id": client_a["id"]},
        headers=auth_headers,
    )
    assert draft_status_filtered.status_code == 200, draft_status_filtered.text
    draft_status_payload = draft_status_filtered.json()
    assert draft_status_payload["total"] == 1
    assert draft_status_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in draft_status_payload["items"]] == [gov_draft_id]

    bill_status_filtered = client.get(
        FEE_DRAFTS_URL,
        params={"bill_status": "UNSETTLED", "client_id": client_a["id"]},
        headers=auth_headers,
    )
    assert bill_status_filtered.status_code == 200, bill_status_filtered.text
    bill_status_payload = bill_status_filtered.json()
    assert bill_status_payload["total"] == 1
    assert bill_status_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in bill_status_payload["items"]] == [service_draft_id]

    date_filtered = client.get(
        FEE_DRAFTS_URL,
        params={
            "date_from": "2026-03-02",
            "date_to": "2026-03-08",
            "client_id": client_a["id"],
        },
        headers=auth_headers,
    )
    assert date_filtered.status_code == 200, date_filtered.text
    date_payload = date_filtered.json()
    assert date_payload["total"] == 1
    assert date_payload["summary"]["total_draft_count"] == 1
    assert [item["id"] for item in date_payload["items"]] == [gov_draft_id]


def test_fee_drafts_report_returns_grouped_amount_summaries(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="FEE-RPT-GRP-A")
    client_b = _create_client(client, auth_headers, name_prefix="FEE-RPT-GRP-B")
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-GRP-CASE-A",
        case_type="NORMAL",
        from_country="CN",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_b["id"],
        case_tag="FEE-GRP-CASE-B",
        case_type="SEARCH",
        to_country="US",
    )
    case_c = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-GRP-CASE-C",
        case_type="NORMAL",
    )

    _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="SERVICE_REPORT",
        currency="JPY",
        status="OPEN",
        created_at=datetime(2026, 3, 12, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "100.00"), ("GOV", "30.00")],
    )
    _insert_fee_draft(
        session_factory,
        case_id=case_b["id"],
        client_id=client_b["id"],
        draft_type="SEARCH_REPORT",
        currency="JPY",
        status="OPEN",
        created_at=datetime(2026, 3, 13, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "80.00"), ("GOV", "20.00"), ("MISC", "10.00")],
    )
    _insert_fee_draft(
        session_factory,
        case_id=case_c["id"],
        client_id=client_a["id"],
        draft_type="GOV_REPORT",
        currency="JPY",
        status="LOCKED",
        created_at=datetime(2026, 3, 14, 9, 0, tzinfo=timezone.utc),
        lines=[("GOV", "50.00")],
    )

    resp = client.get(
        FEE_DRAFTS_URL,
        params={
            "currency": "JPY",
            "date_from": "2026-03-12",
            "date_to": "2026-03-14",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    summary = payload["summary"]

    client_amounts = {item["key"]: item for item in summary["client_amounts"]}
    assert Decimal(str(client_amounts[client_a["id"]]["service_fee_amount"])) == Decimal("100.00")
    assert Decimal(str(client_amounts[client_a["id"]]["government_fee_amount"])) == Decimal("80.00")
    assert Decimal(str(client_amounts[client_a["id"]]["income_amount"])) == Decimal("180.00")
    assert client_amounts[client_a["id"]]["draft_count"] == 2
    assert Decimal(str(client_amounts[client_b["id"]]["service_fee_amount"])) == Decimal("80.00")
    assert Decimal(str(client_amounts[client_b["id"]]["government_fee_amount"])) == Decimal("20.00")
    assert Decimal(str(client_amounts[client_b["id"]]["income_amount"])) == Decimal("110.00")
    assert client_amounts[client_b["id"]]["draft_count"] == 1

    case_type_amounts = {item["key"]: item for item in summary["case_type_amounts"]}
    assert Decimal(str(case_type_amounts["NORMAL"]["service_fee_amount"])) == Decimal("100.00")
    assert Decimal(str(case_type_amounts["NORMAL"]["government_fee_amount"])) == Decimal("80.00")
    assert Decimal(str(case_type_amounts["NORMAL"]["income_amount"])) == Decimal("180.00")
    assert case_type_amounts["NORMAL"]["draft_count"] == 2
    assert Decimal(str(case_type_amounts["SEARCH"]["service_fee_amount"])) == Decimal("80.00")
    assert Decimal(str(case_type_amounts["SEARCH"]["government_fee_amount"])) == Decimal("20.00")
    assert Decimal(str(case_type_amounts["SEARCH"]["income_amount"])) == Decimal("110.00")
    assert case_type_amounts["SEARCH"]["draft_count"] == 1

    country_amounts = {item["key"]: item for item in summary["country_amounts"]}
    assert Decimal(str(country_amounts["CN"]["income_amount"])) == Decimal("130.00")
    assert country_amounts["CN"]["draft_count"] == 1
    assert Decimal(str(country_amounts["US"]["income_amount"])) == Decimal("110.00")
    assert country_amounts["US"]["draft_count"] == 1
    assert Decimal(str(country_amounts["未填写"]["income_amount"])) == Decimal("50.00")
    assert country_amounts["未填写"]["draft_count"] == 1


def test_fee_drafts_report_returns_agent_service_amount_summaries(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="FEE-RPT-AGENT-A")
    client_b = _create_client(client, auth_headers, name_prefix="FEE-RPT-AGENT-B")
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-AGENT-CASE-A",
        primary_agent_id="AGENT-FALLBACK",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_b["id"],
        case_tag="FEE-AGENT-CASE-B",
        primary_agent_id="AGENT-PRIMARY-CONTEXT",
    )
    _insert_case_agent_splits(
        session_factory,
        case_id=case_b["id"],
        rows=[
            ("AGENT-SPLIT-A", "PRIMARY", "60"),
            ("AGENT-SPLIT-B", "SECONDARY", "40"),
        ],
    )

    _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="SERVICE_REPORT",
        currency="KRW",
        status="OPEN",
        created_at=datetime(2026, 3, 21, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "100.00"), ("GOV", "20.00")],
    )
    _insert_fee_draft(
        session_factory,
        case_id=case_b["id"],
        client_id=client_b["id"],
        draft_type="SERVICE_REPORT",
        currency="KRW",
        status="OPEN",
        created_at=datetime(2026, 3, 22, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "80.00"), ("MISC", "5.00")],
    )

    resp = client.get(
        FEE_DRAFTS_URL,
        params={
            "currency": "KRW",
            "date_from": "2026-03-21",
            "date_to": "2026-03-22",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    summary = resp.json()["summary"]

    agent_amounts = {item["key"]: item for item in summary["agent_service_amounts"]}
    assert Decimal(str(agent_amounts["AGENT-FALLBACK"]["service_fee_amount"])) == Decimal("100.00")
    assert agent_amounts["AGENT-FALLBACK"]["draft_count"] == 1
    assert Decimal(str(agent_amounts["AGENT-SPLIT-A"]["service_fee_amount"])) == Decimal("48.00")
    assert agent_amounts["AGENT-SPLIT-A"]["draft_count"] == 1
    assert Decimal(str(agent_amounts["AGENT-SPLIT-B"]["service_fee_amount"])) == Decimal("32.00")
    assert agent_amounts["AGENT-SPLIT-B"]["draft_count"] == 1
    assert "AGENT-PRIMARY-CONTEXT" not in agent_amounts


def test_fee_drafts_report_returns_balance_metrics_from_bill_lineage(
    client,
    auth_headers,
    session_factory: sessionmaker,
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="FEE-RPT-BAL-A")
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-BAL-CASE-A",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-BAL-CASE-B",
    )
    case_c = _create_case(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_tag="FEE-BAL-CASE-C",
    )

    settled_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a["id"],
        draft_type="BAL_SERVICE",
        currency="SGD",
        status="OPEN",
        created_at=datetime(2026, 3, 25, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "100.00")],
    )
    partial_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_b["id"],
        client_id=client_a["id"],
        draft_type="BAL_SERVICE",
        currency="SGD",
        status="OPEN",
        created_at=datetime(2026, 3, 26, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "200.00")],
    )
    unpaid_draft_id = _insert_fee_draft(
        session_factory,
        case_id=case_c["id"],
        client_id=client_a["id"],
        draft_type="BAL_SERVICE",
        currency="SGD",
        status="OPEN",
        created_at=datetime(2026, 3, 27, 9, 0, tzinfo=timezone.utc),
        lines=[("SERVICE", "300.00")],
    )

    settled_bill = _create_bill_from_drafts(client, auth_headers, draft_ids=[settled_draft_id])
    partial_bill = _create_bill_from_drafts(client, auth_headers, draft_ids=[partial_draft_id])
    _create_bill_from_drafts(client, auth_headers, draft_ids=[unpaid_draft_id])

    manual_bill = _create_manual_bill(
        client,
        auth_headers,
        client_id=client_a["id"],
        case_id=case_a["id"],
        currency="SGD",
        amount="999.00",
    )

    settled_payment = _create_payment(
        client,
        auth_headers,
        client_id=client_a["id"],
        amount="100.00",
        currency="SGD",
    )
    settled_payment_line_id = _get_payment_line_id(
        client, auth_headers, payment_id=settled_payment["id"]
    )
    _create_offset(
        client,
        auth_headers,
        payment_line_id=settled_payment_line_id,
        bill_id=settled_bill["id"],
        amount="100.00",
    )

    partial_payment = _create_payment(
        client,
        auth_headers,
        client_id=client_a["id"],
        amount="80.00",
        currency="SGD",
    )
    partial_payment_line_id = _get_payment_line_id(
        client, auth_headers, payment_id=partial_payment["id"]
    )
    _create_offset(
        client,
        auth_headers,
        payment_line_id=partial_payment_line_id,
        bill_id=partial_bill["id"],
        amount="80.00",
    )

    resp = client.get(
        FEE_DRAFTS_URL,
        params={
            "currency": "SGD",
            "date_from": "2026-03-25",
            "date_to": "2026-03-27",
            "client_id": client_a["id"],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    summary = resp.json()["summary"]

    assert Decimal(str(summary["billed_amount"])) == Decimal("600.00")
    assert Decimal(str(summary["received_amount"])) == Decimal("180.00")
    assert Decimal(str(summary["unpaid_balance_amount"])) == Decimal("420.00")
    assert summary["partially_received_bill_count"] == 1
    assert manual_bill["amount"] == "999.00"
