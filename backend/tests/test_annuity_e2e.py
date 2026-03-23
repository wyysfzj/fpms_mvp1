from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

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
        pay_lists = db.execute(select(PayList)).scalars().all()
        gov_payments = db.execute(select(GovPayment)).scalars().all()

    assert len(pay_lists) == 1
    assert pay_lists[0].client_id == client_id
    assert pay_lists[0].currency == "USD"
    assert pay_lists[0].planned_pay_date == date(2026, 8, 15)
    assert pay_lists[0].remark == "历史清单"
    assert len(gov_payments) == 0


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
