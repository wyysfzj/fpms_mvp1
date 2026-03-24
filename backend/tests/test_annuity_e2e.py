from __future__ import annotations

import io
import zipfile
from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import app.api.deps as deps
from app.modules.annuity.models import AnnuityTask, GovPayment, PayList
from app.modules.billing.models import Bill, BillItem, CaseReceipt
from app.modules.cases.models import Case
from app.modules.fees.models import FeeItem, FeeRate
from app.modules.fees.service import calculate_fee_amount


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert "error" in payload, payload
    assert payload["error"].get("code") == error_code, payload
    assert payload["error"].get("message")
    return payload


def _create_client_and_case(client: TestClient, auth_headers: dict[str, str]) -> tuple[str, str]:
    cli_resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid("ANN-CLI"), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert cli_resp.status_code == 201, cli_resp.text
    client_id = cli_resp.json()["id"]

    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("ANN-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Annuity E2E Case",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    return client_id, case_resp.json()["id"]


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_no: str,
    app_no: str | None = None,
) -> str:
    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "Annuity E2E Case",
    }
    if app_no is not None:
        payload["app_no"] = app_no

    case_resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert case_resp.status_code == 201, case_resp.text
    return case_resp.json()["id"]


def _insert_annuity_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    client_id: str,
    year_no: int,
    due_date: date,
    status: str = "OPEN",
    notice_status: str = "PENDING",
    client_instruction: str | None = None,
) -> int:
    with session_factory() as db:
        task = AnnuityTask(
            case_id=case_id,
            client_id=client_id,
            year_no=year_no,
            due_date=due_date,
            status=status,
            notice_status=notice_status,
            client_instruction=client_instruction,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _create_annuity_rates(client: TestClient, auth_headers: dict[str, str], tag: str) -> None:
    for fee_type, amount in (("GOV", "100.00"), ("SERVICE", "20.00")):
        resp = client.post(
            "/api/v1/fees/rates",
            json={
                "fee_code": f"ANN-{fee_type}-{tag}",
                "fee_name": f"Annuity {fee_type} {tag}",
                "fee_type": fee_type,
                "currency": "CNY",
                "default_amount": amount,
                "enabled": True,
                "rate_group": "ANNUITY",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text


def _first_fee_item_id_by_type(
    session_factory: sessionmaker,
    draft_id: str,
    fee_type: str,
) -> str:
    with session_factory() as db:
        fee_item = (
            db.execute(
                select(FeeItem)
                .where(
                    FeeItem.draft_id == draft_id,
                    FeeItem.fee_type == fee_type,
                )
                .order_by(FeeItem.id.asc())
            )
            .scalars()
            .first()
        )
        assert fee_item is not None
        return fee_item.id


def test_annuity_tasks_filters_and_instruction_status_matrix(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)

    open_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 1, 15),
        status="OPEN",
        notice_status="PENDING",
    )
    _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=2,
        due_date=date(2026, 1, 20),
        status="DONE",
        notice_status="SENT",
    )

    list_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={
            "due_from": "2026-01-01",
            "due_to": "2026-01-31",
            "status": "OPEN",
            "pending_mode": "pending",
            "case_id": case_id,
            "client_id": client_id,
            "notice_status": "PENDING",
            "page": 1,
            "page_size": 10,
        },
    )
    assert list_resp.status_code == 200, list_resp.text
    list_payload = list_resp.json()
    assert set(list_payload) == {"items", "page", "page_size", "total"}
    assert list_payload["page"] == 1
    assert list_payload["page_size"] == 10
    returned_ids = {item["id"] for item in list_payload["items"]}
    assert open_task_id in returned_ids

    range_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"due_from": "2026-02-01", "due_to": "2026-01-01"},
    )
    _assert_error(range_resp, 400, "ANNUITY_DATE_RANGE_INVALID")

    page_size_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"page_size": 101},
    )
    _assert_error(page_size_resp, 422, "VALIDATION_ERROR")

    update_resp = client.put(
        f"/api/v1/annuity/tasks/{open_task_id}/instruction",
        headers=auth_headers,
        json={"instruction": "PAY"},
    )
    assert update_resp.status_code == 200, update_resp.text
    update_payload = update_resp.json()
    assert update_payload["id"] == open_task_id
    assert update_payload["client_instruction"] == "PAY"
    assert update_payload["instruction_date"] is not None

    transition_resp = client.put(
        f"/api/v1/annuity/tasks/{open_task_id}/instruction",
        headers=auth_headers,
        json={"instruction": "DEFER"},
    )
    _assert_error(transition_resp, 400, "ANNUITY_INSTRUCTION_INVALID")

    missing_resp = client.put(
        "/api/v1/annuity/tasks/99999999/instruction",
        headers=auth_headers,
        json={"instruction": "PAY"},
    )
    _assert_error(missing_resp, 404, "ANNUITY_TASK_NOT_FOUND")

    terminal_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=9,
        due_date=date(2026, 2, 1),
        status="DONE",
    )
    terminal_resp = client.put(
        f"/api/v1/annuity/tasks/{terminal_task_id}/instruction",
        headers=auth_headers,
        json={"instruction": "PAY"},
    )
    _assert_error(terminal_resp, 409, "ANNUITY_STATE_CONFLICT")


def test_gov_payment_register_generated_planned_chain(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    task_1 = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 3, 1),
    )
    _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=2,
        due_date=date(2027, 3, 1),
    )
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    generate_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_1], "pay_next_year": True, "currency": "CNY"},
    )
    assert generate_resp.status_code == 200, generate_resp.text
    generate_payload = generate_resp.json()
    assert {"summary", "success", "failed"}.issubset(generate_payload)
    assert generate_payload["summary"]["success"] == 2
    assert generate_payload["summary"]["failed"] == 0

    repeat_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_1], "pay_next_year": True, "currency": "CNY"},
    )
    assert repeat_resp.status_code == 200, repeat_resp.text
    repeat_payload = repeat_resp.json()
    assert repeat_payload["summary"]["success"] == 0
    assert repeat_payload["summary"]["failed"] >= 1
    assert all(row["code"] == "ANNUITY_DRAFT_ALREADY_GENERATED" for row in repeat_payload["failed"])

    draft_id = generate_payload["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")
    service_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "SERVICE")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id]},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_payload = pay_list_resp.json()
    assert pay_list_payload["summary"]["success"] == 1
    assert pay_list_payload["pay_list"]["status"] == "DRAFT"
    pay_list_id = pay_list_payload["pay_list"]["id"]

    pay_list_repeat_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id]},
    )
    assert pay_list_repeat_resp.status_code == 200, pay_list_repeat_resp.text
    pay_list_repeat_payload = pay_list_repeat_resp.json()
    assert pay_list_repeat_payload["summary"]["success"] == 0
    assert pay_list_repeat_payload["summary"]["failed"] >= 1
    assert pay_list_repeat_payload["failed"][0]["code"] == "GOV_PAYMENT_DUPLICATE"

    register_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={
            "pay_list_id": pay_list_id,
            "fee_item_id": gov_fee_item_id,
            "paid_date": "2026-04-01",
            "paid_amount": "120.00",
            "official_receipt_no": _uid("OCR"),
        },
    )
    assert register_resp.status_code == 200, register_resp.text
    register_payload = register_resp.json()
    assert register_payload["gov_payment"]["fee_item_id"] == gov_fee_item_id
    assert register_payload["pay_list"]["status"] == "PAID"

    duplicate_register = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={"pay_list_id": pay_list_id, "fee_item_id": gov_fee_item_id},
    )
    _assert_error(duplicate_register, 409, "GOV_PAYMENT_DUPLICATE")

    invalid_amount_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={
            "pay_list_id": pay_list_id,
            "fee_item_id": service_fee_item_id,
            "paid_amount": "100.00",
        },
    )
    _assert_error(invalid_amount_resp, 400, "PAY_LIST_SCOPE_INVALID")

    zero_amount_task = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=3,
        due_date=date(2028, 3, 1),
    )
    zero_amount_generate_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [zero_amount_task], "pay_next_year": False, "currency": "CNY"},
    )
    assert zero_amount_generate_resp.status_code == 200, zero_amount_generate_resp.text
    zero_amount_draft_id = zero_amount_generate_resp.json()["success"][0]["draft_id"]
    zero_amount_gov_fee_item_id = _first_fee_item_id_by_type(
        session_factory, zero_amount_draft_id, "GOV"
    )

    with session_factory() as db:
        zero_amount_fee_item = (
            db.execute(select(FeeItem).where(FeeItem.id == zero_amount_gov_fee_item_id))
            .scalars()
            .one()
        )
        zero_amount_fee_item.amount = Decimal("0.00")
        db.commit()

    zero_default_amount_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={
            "pay_list_id": pay_list_id,
            "fee_item_id": zero_amount_gov_fee_item_id,
        },
    )
    _assert_error(zero_default_amount_resp, 400, "GOV_PAYMENT_INVALID")

    missing_pay_list_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={"pay_list_id": 9999999, "fee_item_id": gov_fee_item_id},
    )
    _assert_error(missing_pay_list_resp, 404, "PAY_LIST_NOT_FOUND")

    validation_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": []},
    )
    _assert_error(validation_resp, 422, "VALIDATION_ERROR")


def test_gov_payment_register_keeps_exported_pay_list_exported(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 6, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-06-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    export_resp = client.post(f"/api/v1/pay-lists/{pay_list_id}/export", headers=auth_headers)
    assert export_resp.status_code == 200, export_resp.text

    register_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={
            "pay_list_id": pay_list_id,
            "fee_item_id": gov_fee_item_id,
            "paid_date": "2026-06-20",
            "paid_amount": "100.00",
            "official_receipt_no": _uid("OCR"),
        },
    )
    assert register_resp.status_code == 200, register_resp.text
    register_payload = register_resp.json()
    assert register_payload["pay_list"]["status"] == "EXPORTED"

    with session_factory() as db:
        pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one()

    assert pay_list.status == "EXPORTED"
    assert pay_list.paid_date is None


def test_pay_list_from_fee_items_rejects_mixed_scope_selection_without_persistence(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    other_client_id, other_client_case_id = _create_client_and_case(client, auth_headers)

    other_case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": _uid("ANN-CASE"),
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "Annuity E2E Case USD",
        },
        headers=auth_headers,
    )
    assert other_case_resp.status_code == 201, other_case_resp.text
    other_case_id = other_case_resp.json()["id"]

    same_client_cny_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 7, 1),
    )
    usd_task_id = _insert_annuity_task(
        session_factory,
        case_id=other_case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 7, 2),
    )
    other_client_cny_task_id = _insert_annuity_task(
        session_factory,
        case_id=other_client_case_id,
        client_id=other_client_id,
        year_no=1,
        due_date=date(2026, 7, 3),
    )
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    cny_draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [same_client_cny_task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert cny_draft_resp.status_code == 200, cny_draft_resp.text
    usd_draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [usd_task_id], "pay_next_year": False, "currency": "USD"},
    )
    assert usd_draft_resp.status_code == 200, usd_draft_resp.text
    other_client_cny_draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [other_client_cny_task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert other_client_cny_draft_resp.status_code == 200, other_client_cny_draft_resp.text

    same_client_cny_fee_item_id = _first_fee_item_id_by_type(
        session_factory,
        cny_draft_resp.json()["success"][0]["draft_id"],
        "GOV",
    )
    same_client_usd_fee_item_id = _first_fee_item_id_by_type(
        session_factory,
        usd_draft_resp.json()["success"][0]["draft_id"],
        "GOV",
    )
    other_client_cny_fee_item_id = _first_fee_item_id_by_type(
        session_factory,
        other_client_cny_draft_resp.json()["success"][0]["draft_id"],
        "GOV",
    )

    requested_ids = [
        same_client_cny_fee_item_id,
        same_client_usd_fee_item_id,
        other_client_cny_fee_item_id,
    ]

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": requested_ids},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_payload = pay_list_resp.json()
    assert pay_list_payload["summary"]["success"] == 0
    assert pay_list_payload["summary"]["failed"] == len(requested_ids)
    assert pay_list_payload["pay_list"] is None
    assert pay_list_payload["success"] == []

    failed_ids = {row["fee_item_id"] for row in pay_list_payload["failed"]}
    assert failed_ids == set(requested_ids)
    assert all(row["code"] == "PAY_LIST_SCOPE_INVALID" for row in pay_list_payload["failed"])

    with session_factory() as db:
        assert db.execute(select(PayList)).scalars().all() == []
        assert db.execute(select(GovPayment)).scalars().all() == []


def test_pay_list_from_fee_items_keeps_valid_same_scope_candidates_when_other_items_fail(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 7, 10),
    )
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]

    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")
    service_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "SERVICE")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id, service_fee_item_id]},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_payload = pay_list_resp.json()
    assert pay_list_payload["summary"]["success"] == 1
    assert pay_list_payload["summary"]["failed"] == 1
    assert pay_list_payload["pay_list"] is not None
    assert pay_list_payload["success"][0]["fee_item_id"] == gov_fee_item_id
    assert pay_list_payload["failed"][0]["fee_item_id"] == service_fee_item_id
    assert pay_list_payload["failed"][0]["code"] == "PAY_LIST_SCOPE_INVALID"

    with session_factory() as db:
        pay_lists = db.execute(select(PayList)).scalars().all()
        gov_payments = db.execute(select(GovPayment)).scalars().all()

    assert len(pay_lists) == 1
    assert pay_lists[0].client_id == client_id
    assert pay_lists[0].currency == "CNY"
    assert len(gov_payments) == 1
    assert gov_payments[0].fee_item_id == gov_fee_item_id


def test_historical_pay_list_create_requires_client_and_round_trips_supported_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    missing_client_resp = client.post(
        "/api/v1/pay-lists",
        headers=auth_headers,
        json={"currency": "USD"},
    )
    _assert_error(missing_client_resp, 400, "PAY_LIST_CLIENT_REQUIRED")

    client_id, _case_id = _create_client_and_case(client, auth_headers)
    create_resp = client.post(
        "/api/v1/pay-lists",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "currency": "USD",
            "planned_pay_date": "2026-08-15",
            "remark": "历史清单",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    payload = create_resp.json()
    assert payload["client_id"] == client_id
    assert payload["currency"] == "USD"
    assert payload["planned_pay_date"] == "2026-08-15"
    assert payload["remark"] == "历史清单"
    assert payload["status"] == "DRAFT"
    assert payload["total_amount"] == "0.00"
    assert payload["pay_list_no"]
    assert payload["created_by"] is not None

    with session_factory() as db:
        pay_list = db.execute(
            select(PayList).where(
                PayList.id == payload["id"],
                PayList.pay_list_no == payload["pay_list_no"],
                PayList.client_id == client_id,
            )
        ).scalar_one()
        gov_payments = (
            db.execute(select(GovPayment).where(GovPayment.pay_list_id == pay_list.id))
            .scalars()
            .all()
        )

    assert pay_list.client_id == client_id
    assert pay_list.currency == "USD"
    assert pay_list.planned_pay_date == date(2026, 8, 15)
    assert pay_list.remark == "历史清单"
    assert pay_list.created_by == payload["created_by"]
    assert pay_list.updated_by == payload["updated_by"]
    assert len(gov_payments) == 0


def test_pay_list_manual_item_accepts_null_fee_item_id_and_updates_total_amount(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)

    historical_resp = client.post(
        "/api/v1/pay-lists",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "currency": "CNY",
            "planned_pay_date": "2026-08-15",
            "remark": "手工补录",
        },
    )
    assert historical_resp.status_code == 201, historical_resp.text
    pay_list_id = historical_resp.json()["id"]

    manual_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/manual-items",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "paid_amount": "88.50",
            "paid_date": "2026-08-20",
            "remark": "历史补录",
        },
    )

    assert manual_resp.status_code == 200, manual_resp.text
    payload = manual_resp.json()
    assert payload["gov_payment"]["fee_item_id"] is None
    assert payload["gov_payment"]["case_id"] == case_id
    assert payload["gov_payment"]["paid_amount"] == "88.50"
    assert payload["pay_list"]["id"] == pay_list_id
    assert payload["pay_list"]["total_amount"] == "88.50"

    with session_factory() as db:
        gov_payment = (
            db.execute(
                select(GovPayment).where(
                    GovPayment.pay_list_id == pay_list_id,
                    GovPayment.case_id == case_id,
                )
            )
            .scalars()
            .one()
        )

    assert gov_payment.fee_item_id is None
    assert gov_payment.remark == "历史补录"


def test_pay_list_manual_item_requires_authentication(client: TestClient) -> None:
    unauth_resp = client.post(
        "/api/v1/pay-lists/1/manual-items",
        json={
            "case_id": "CASE-001",
            "paid_amount": "10.00",
            "paid_date": "2026-08-20",
        },
    )
    _assert_error(unauth_resp, 401, "AUTH_REQUIRED")


def test_pay_list_manual_item_returns_not_found_for_missing_header(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    missing_resp = client.post(
        "/api/v1/pay-lists/999999/manual-items",
        headers=auth_headers,
        json={
            "case_id": "CASE-001",
            "paid_amount": "10.00",
            "paid_date": "2026-08-20",
        },
    )
    _assert_error(missing_resp, 404, "PAY_LIST_NOT_FOUND")


def test_pay_list_manual_item_rejects_non_draft_header(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)

    historical_resp = client.post(
        "/api/v1/pay-lists",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "currency": "CNY",
            "planned_pay_date": "2026-08-15",
            "remark": "手工补录",
        },
    )
    assert historical_resp.status_code == 201, historical_resp.text
    pay_list_id = historical_resp.json()["id"]

    with session_factory() as db:
        pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one()
        pay_list.status = "EXPORTED"
        db.commit()

    conflict_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/manual-items",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "paid_amount": "10.00",
            "paid_date": "2026-08-20",
        },
    )
    _assert_error(conflict_resp, 409, "PAY_LIST_STATE_CONFLICT")


def test_pay_list_manual_item_rejects_generated_draft_pay_list(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 8, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-08-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    conflict_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/manual-items",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "paid_amount": "10.00",
            "paid_date": "2026-08-20",
        },
    )
    payload = _assert_error(conflict_resp, 409, "PAY_LIST_STATE_CONFLICT")
    assert payload["error"]["details"]["reason"] == "PAY_LIST_ALREADY_HAS_ROWS"


def test_pay_list_query_filters_supported_headers_and_case_join_semantics(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    client_name = _uid("ANN-CLI")
    client_resp = client.post(
        "/api/v1/clients",
        json={"name_cn": client_name, "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert client_resp.status_code == 201, client_resp.text
    client_id = client_resp.json()["id"]

    case_one_no = _uid("ANN-CASE-A")
    case_two_no = _uid("ANN-CASE-B")
    case_one_id = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        case_no=case_one_no,
        app_no="APP-0001",
    )
    case_two_id = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        case_no=case_two_no,
        app_no="APP-0002",
    )

    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_one_id = _insert_annuity_task(
        session_factory,
        case_id=case_one_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 8, 1),
    )
    task_two_id = _insert_annuity_task(
        session_factory,
        case_id=case_two_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 8, 2),
    )

    draft_one_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_one_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_one_resp.status_code == 200, draft_one_resp.text
    draft_two_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_two_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_two_resp.status_code == 200, draft_two_resp.text

    draft_one_id = draft_one_resp.json()["success"][0]["draft_id"]
    draft_two_id = draft_two_resp.json()["success"][0]["draft_id"]
    fee_item_one_id = _first_fee_item_id_by_type(session_factory, draft_one_id, "GOV")
    fee_item_two_id = _first_fee_item_id_by_type(session_factory, draft_two_id, "GOV")

    generated_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={
            "fee_item_ids": [fee_item_one_id, fee_item_two_id],
            "planned_pay_date": "2026-08-15",
            "remark": "组合查询",
        },
    )
    assert generated_resp.status_code == 200, generated_resp.text
    generated_payload = generated_resp.json()
    assert generated_payload["summary"]["success"] == 2
    generated_pay_list = generated_payload["pay_list"]
    assert generated_pay_list is not None

    historical_resp = client.post(
        "/api/v1/pay-lists",
        headers=auth_headers,
        json={
            "client_id": client_id,
            "currency": "USD",
            "planned_pay_date": "2026-09-01",
            "remark": "历史清单",
        },
    )
    assert historical_resp.status_code == 201, historical_resp.text

    page_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={"page": 1, "page_size": 1},
    )
    assert page_resp.status_code == 200, page_resp.text
    page_payload = page_resp.json()
    assert page_payload["page"] == 1
    assert page_payload["page_size"] == 1
    assert page_payload["total"] == 2
    assert len(page_payload["items"]) == 1

    filtered_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={
            "pay_list_no": generated_pay_list["pay_list_no"],
            "client_id": client_id,
            "status": "DRAFT",
            "currency": "CNY",
            "planned_pay_date_from": "2026-08-01",
            "planned_pay_date_to": "2026-08-31",
            "page": 1,
            "page_size": 20,
        },
    )
    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_payload = filtered_resp.json()
    assert filtered_payload["total"] == 1
    assert len(filtered_payload["items"]) == 1
    item = filtered_payload["items"][0]
    assert item["pay_list_no"] == generated_pay_list["pay_list_no"]
    assert item["client_id"] == client_id
    assert item["client_name"] == client_name
    assert item["status"] == "DRAFT"
    assert item["currency"] == "CNY"
    assert item["planned_pay_date"] == "2026-08-15"
    assert item["total_amount"] == "200.00"

    explicit_range_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={
            "planned_pay_date_from": "2026-08-01",
            "planned_pay_date_to": "2026-08-31",
            "page": 1,
            "page_size": 20,
        },
    )
    assert explicit_range_resp.status_code == 200, explicit_range_resp.text
    explicit_range_payload = explicit_range_resp.json()
    assert explicit_range_payload["total"] == 1
    assert [row["id"] for row in explicit_range_payload["items"]] == [generated_pay_list["id"]]

    invalid_range_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={
            "planned_pay_date_from": "2026-08-31",
            "planned_pay_date_to": "2026-08-01",
            "page": 1,
            "page_size": 20,
        },
    )
    _assert_error(invalid_range_resp, 400, "PAY_LIST_DATE_RANGE_INVALID")

    invalid_page_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={"page": 0, "page_size": 20},
    )
    assert invalid_page_resp.status_code == 422, invalid_page_resp.text

    unauthenticated_resp = client.get("/api/v1/pay-lists", params={"page": 1, "page_size": 20})
    assert unauthenticated_resp.status_code == 401, unauthenticated_resp.text

    same_row_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={
            "case_no": case_one_no,
            "app_no": "APP-0002",
            "page": 1,
            "page_size": 20,
        },
    )
    assert same_row_resp.status_code == 200, same_row_resp.text
    same_row_payload = same_row_resp.json()
    assert same_row_payload["total"] == 0
    assert same_row_payload["items"] == []

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)
    forbidden_resp = client.get(
        "/api/v1/pay-lists",
        headers=auth_headers,
        params={"page": 1, "page_size": 20},
    )
    _assert_error(forbidden_resp, 403, "FORBIDDEN")
    assert forbidden_resp.json()["error"]["details"]["required_perm"] == "PayList.Read"


def test_pay_list_detail_returns_header_and_associated_gov_payments(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 8, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-08-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    detail_resp = client.get(f"/api/v1/pay-lists/{pay_list_id}", headers=auth_headers)
    assert detail_resp.status_code == 200, detail_resp.text
    payload = detail_resp.json()
    assert set(payload) == {"pay_list", "gov_payments"}
    pay_list_payload = payload["pay_list"]
    gov_payment_payload = payload["gov_payments"][0]
    assert set(pay_list_payload) == {
        "id",
        "pay_list_no",
        "client_id",
        "status",
        "currency",
        "planned_pay_date",
        "paid_date",
        "total_amount",
        "remark",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }
    assert pay_list_payload["id"] == pay_list_id
    assert pay_list_payload["pay_list_no"]
    assert pay_list_payload["client_id"] == client_id
    assert pay_list_payload["status"] == "DRAFT"
    assert pay_list_payload["currency"] == "CNY"
    assert pay_list_payload["planned_pay_date"] == "2026-08-15"
    assert pay_list_payload["paid_date"] is None
    assert pay_list_payload["total_amount"] == "100.00"
    assert len(payload["gov_payments"]) == 1
    assert set(gov_payment_payload) == {
        "id",
        "pay_list_id",
        "case_id",
        "fee_item_id",
        "status",
        "currency",
        "paid_date",
        "paid_amount",
        "official_receipt_no",
        "remark",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    }
    assert gov_payment_payload["fee_item_id"] == gov_fee_item_id
    assert gov_payment_payload["pay_list_id"] == pay_list_id
    assert gov_payment_payload["case_id"] == case_id
    assert gov_payment_payload["status"] == "PLANNED"
    assert gov_payment_payload["currency"] == "CNY"
    assert gov_payment_payload["paid_date"] is None
    assert gov_payment_payload["paid_amount"] == "100.00"
    assert gov_payment_payload["official_receipt_no"] is None

    not_found_resp = client.get("/api/v1/pay-lists/999999", headers=auth_headers)
    _assert_error(not_found_resp, 404, "PAY_LIST_NOT_FOUND")

    unauthenticated_resp = client.get(f"/api/v1/pay-lists/{pay_list_id}")
    assert unauthenticated_resp.status_code == 401, unauthenticated_resp.text

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)
    forbidden_resp = client.get(f"/api/v1/pay-lists/{pay_list_id}", headers=auth_headers)
    _assert_error(forbidden_resp, 403, "FORBIDDEN")
    assert forbidden_resp.json()["error"]["details"]["required_perm"] == "PayList.Read"


def test_pay_list_export_generates_xlsx_and_advances_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 10, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-10-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]
    pay_list_no = pay_list_resp.json()["pay_list"]["pay_list_no"]

    export_resp = client.post(f"/api/v1/pay-lists/{pay_list_id}/export", headers=auth_headers)
    assert export_resp.status_code == 200, export_resp.text
    assert (
        export_resp.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment;" in export_resp.headers["content-disposition"]
    assert pay_list_no in export_resp.headers["content-disposition"]
    assert export_resp.content.startswith(b"PK")

    with zipfile.ZipFile(io.BytesIO(export_resp.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "官费清单" in sheet_xml
    assert pay_list_no in sheet_xml
    assert "清单编号" in sheet_xml
    assert "状态" in sheet_xml
    assert "EXPORTED" in sheet_xml
    assert "DRAFT" not in sheet_xml
    assert "缴费金额" in sheet_xml
    assert "100.00" in sheet_xml

    with session_factory() as db:
        pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one()

    assert pay_list.status == "EXPORTED"
    assert pay_list.paid_date is None

    repeat_resp = client.post(f"/api/v1/pay-lists/{pay_list_id}/export", headers=auth_headers)
    _assert_error(repeat_resp, 409, "PAY_LIST_STATE_CONFLICT")


def test_pay_list_export_requires_permission_and_existing_header(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 11, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-11-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)
    forbidden_resp = client.post(f"/api/v1/pay-lists/{pay_list_id}/export", headers=auth_headers)
    _assert_error(forbidden_resp, 403, "FORBIDDEN")
    assert forbidden_resp.json()["error"]["details"]["required_perm"] == "PayList.Export"


def test_pay_list_export_returns_not_found_for_missing_header(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    not_found_resp = client.post("/api/v1/pay-lists/999999/export", headers=auth_headers)
    _assert_error(not_found_resp, 404, "PAY_LIST_NOT_FOUND")


def test_pay_list_export_requires_authentication(client: TestClient) -> None:
    unauth_resp = client.post("/api/v1/pay-lists/1/export")
    _assert_error(unauth_resp, 401, "AUTH_REQUIRED")


def test_pay_list_export_openapi_declares_excel_binary_response(client: TestClient) -> None:
    operation = client.app.openapi()["paths"]["/api/v1/pay-lists/{pay_list_id}/export"]["post"]
    response_200 = operation["responses"]["200"]["content"]

    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response_200


def test_pay_list_mark_paid_can_follow_exported_gov_payment_flow(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 12, 1),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-12-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    export_resp = client.post(f"/api/v1/pay-lists/{pay_list_id}/export", headers=auth_headers)
    assert export_resp.status_code == 200, export_resp.text

    register_resp = client.post(
        "/api/v1/gov-payments",
        headers=auth_headers,
        json={
            "pay_list_id": pay_list_id,
            "fee_item_id": gov_fee_item_id,
            "paid_date": "2026-12-20",
            "paid_amount": "100.00",
            "official_receipt_no": _uid("OCR"),
        },
    )
    assert register_resp.status_code == 200, register_resp.text
    assert register_resp.json()["pay_list"]["status"] == "EXPORTED"

    mark_paid_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/mark-paid",
        headers=auth_headers,
        json={"paid_date": "2026-12-21"},
    )

    assert mark_paid_resp.status_code == 200, mark_paid_resp.text
    assert mark_paid_resp.json()["pay_list"]["status"] == "PAID"
    assert mark_paid_resp.json()["pay_list"]["paid_date"] == "2026-12-21"

    with session_factory() as db:
        pay_list = db.execute(select(PayList).where(PayList.id == pay_list_id)).scalar_one()
    assert pay_list.status == "PAID"
    assert pay_list.paid_date.isoformat() == "2026-12-21"


def test_pay_list_mark_paid_requires_authentication(client: TestClient) -> None:
    unauth_resp = client.post(
        "/api/v1/pay-lists/1/mark-paid",
        json={"paid_date": "2026-12-21"},
    )
    _assert_error(unauth_resp, 401, "AUTH_REQUIRED")


def test_pay_list_mark_paid_rejects_draft_state(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 12, 2),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-12-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    draft_mark_paid_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/mark-paid",
        headers=auth_headers,
        json={"paid_date": "2026-12-21"},
    )
    _assert_error(draft_mark_paid_resp, 409, "PAY_LIST_STATE_CONFLICT")


def test_pay_list_mark_paid_rejects_forbidden_and_missing_header(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 12, 3),
    )
    draft_resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "CNY"},
    )
    assert draft_resp.status_code == 200, draft_resp.text
    draft_id = draft_resp.json()["success"][0]["draft_id"]
    gov_fee_item_id = _first_fee_item_id_by_type(session_factory, draft_id, "GOV")

    pay_list_resp = client.post(
        "/api/v1/pay-lists/from-fee-items",
        headers=auth_headers,
        json={"fee_item_ids": [gov_fee_item_id], "planned_pay_date": "2026-12-15"},
    )
    assert pay_list_resp.status_code == 200, pay_list_resp.text
    pay_list_id = pay_list_resp.json()["pay_list"]["id"]

    def _no_perms(_db, _user_id) -> set[str]:
        return set()

    monkeypatch.setattr(deps, "get_user_permissions", _no_perms)
    forbidden_resp = client.post(
        f"/api/v1/pay-lists/{pay_list_id}/mark-paid",
        headers=auth_headers,
        json={"paid_date": "2026-12-21"},
    )
    _assert_error(forbidden_resp, 403, "FORBIDDEN")
    assert forbidden_resp.json()["error"]["details"]["required_perm"] == "Billing.Edit"


def test_pay_list_mark_paid_returns_not_found_for_missing_header(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    missing_resp = client.post(
        "/api/v1/pay-lists/999999/mark-paid",
        headers=auth_headers,
        json={"paid_date": "2026-12-21"},
    )
    _assert_error(missing_resp, 404, "PAY_LIST_NOT_FOUND")


def test_calculate_fee_amount_per_claim_with_reduction_and_discount() -> None:
    rate = FeeRate(
        fee_code=_uid("RATE"),
        fee_name="PER CLAIM RATE",
        fee_type="SERVICE",
        currency="CNY",
        default_amount=Decimal("100.00"),
        calc_mode="PER_CLAIM",
        calc_params='{"per_claim_amount":"50","discount_pct":"10","reduction_pct":"20"}',
        allow_reduction=True,
    )
    case = Case(
        case_no=_uid("CASE"),
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        claim_count=3,
    )

    amount = calculate_fee_amount(rate, case)

    # 50 * 3 = 150; reduction 20% => 120; discount 10% => 108
    assert amount == Decimal("108.00")


def test_case_receipt_endpoint_returns_batch3_receipt_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)

    with session_factory() as db:
        receipt = CaseReceipt(
            case_id=case_id,
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("500.00"),
            received_amt=Decimal("300.00"),
            last_receipt_date=date(2026, 4, 1),
            fee_code="ANN-SERVICE",
            year_no=2,
            is_arrears=True,
            invoice_no=_uid("INV"),
            is_commissionable=True,
        )
        db.add(receipt)
        db.commit()

    resp = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["case_id"] == case_id
    assert payload["currency"] == "CNY"
    assert payload["receivable_amt"] == "500.00"
    assert payload["received_amt"] == "300.00"
    assert payload["fee_code"] == "ANN-SERVICE"
    assert payload["year_no"] == 2
    assert payload["is_arrears"] is True
    assert payload["invoice_no"].startswith("INV-")
    assert payload["is_commissionable"] is True


def test_case_receipt_endpoint_includes_bills_overview_list(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)

    with session_factory() as db:
        receipt = CaseReceipt(
            case_id=case_id,
            fee_type="SERVICE",
            currency="CNY",
            receivable_amt=Decimal("200.00"),
            received_amt=Decimal("80.00"),
            last_receipt_date=date(2026, 5, 1),
            fee_code="ANN-SERVICE",
            year_no=1,
            is_arrears=True,
            invoice_no=_uid("INV"),
            is_commissionable=False,
        )
        db.add(receipt)

        bill = Bill(
            bill_no=_uid("BILL"),
            client_id=client_id,
            currency="CNY",
            direction="AR",
            status="UNSETTLED",
            bill_date=date(2026, 5, 2),
            total_service=Decimal("200.00"),
            amount=Decimal("200.00"),
            balance=Decimal("120.00"),
        )
        db.add(bill)
        db.flush()

        # same bill has two lines for this case; receipt overview should deduplicate bills
        db.add_all(
            [
                BillItem(
                    bill_id=bill.id,
                    case_id=case_id,
                    fee_code="ANN-SVC-A",
                    fee_name="Service A",
                    fee_type="SERVICE",
                    amount=Decimal("120.00"),
                ),
                BillItem(
                    bill_id=bill.id,
                    case_id=case_id,
                    fee_code="ANN-SVC-B",
                    fee_name="Service B",
                    fee_type="SERVICE",
                    amount=Decimal("80.00"),
                ),
            ]
        )
        db.commit()

    resp = client.get(f"/api/v1/cases/{case_id}/receipts", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert "bills" in payload
    assert len(payload["bills"]) == 1
    assert payload["bills"][0]["bill_no"].startswith("BILL-")
    assert payload["bills"][0]["status"] == "UNSETTLED"
    assert payload["bills"][0]["amount"] == "200.00"
    assert payload["bills"][0]["balance"] == "120.00"


def test_annuity_generate_drafts_normalizes_currency_case(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id, case_id = _create_client_and_case(client, auth_headers)
    task_id = _insert_annuity_task(
        session_factory,
        case_id=case_id,
        client_id=client_id,
        year_no=1,
        due_date=date(2026, 6, 1),
    )
    _create_annuity_rates(client, auth_headers, tag=uuid4().hex[:6].upper())

    resp = client.post(
        "/api/v1/annuity/tasks/generate-drafts",
        headers=auth_headers,
        json={"task_ids": [task_id], "pay_next_year": False, "currency": "cny"},
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["summary"]["success"] == 1
    assert payload["summary"]["failed"] == 0
    assert payload["success"][0]["currency"] == "CNY"
    assert payload["success"][0]["amount"] == "120.00"
