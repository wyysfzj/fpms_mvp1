from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import AnnuityTask
from app.modules.fees.models import FeeItem


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


def test_annuity_generate_drafts_pay_list_gov_payment_chain(
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
