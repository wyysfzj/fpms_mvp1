from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import sessionmaker

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


def _create_case(client, auth_headers, *, client_id: str, case_tag: str) -> dict:
    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid(case_tag),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": f"{case_tag} 案件",
            "applicants": [{"seq": 1, "is_first": True, "name_cn": f"{case_tag} 申请人"}],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_bill_from_drafts(client, auth_headers, *, draft_ids: list[str]) -> dict:
    resp = client.post(
        "/api/v1/bills/from-drafts",
        json={"draft_ids": draft_ids, "bill_no": _uid("BILL")},
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
