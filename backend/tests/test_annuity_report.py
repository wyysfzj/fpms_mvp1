from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import AnnuityTask, GovPayment, PayList
from app.modules.billing.models import CaseReceipt
from app.modules.fees.models import FeeDraft, FeeItem


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_prefix: str) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={"name_cn": _uid(name_prefix), "default_currency": "CNY"},
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_no_prefix: str,
    from_country: str | None = None,
    to_country: str | None = None,
) -> dict:
    payload: dict[str, object] = {
        "case_no": _uid(case_no_prefix),
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "年费统计测试案件",
        "applicants": [{"seq": 1, "is_first": True, "name_cn": "测试申请人"}],
    }
    if from_country is not None:
        payload["from_country"] = from_country
    if to_country is not None:
        payload["to_country"] = to_country

    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_annuity_task(
    session_factory: sessionmaker,
    *,
    case_id: str,
    client_id: str,
    year_no: int,
    due_date: date,
    status: str,
    notice_status: str = "PENDING",
    gov_fee_amt: Decimal = Decimal("0"),
    service_fee_amt: Decimal = Decimal("0"),
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
            gov_fee_amt=gov_fee_amt,
            service_fee_amt=service_fee_amt,
            client_instruction=client_instruction,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


def _insert_pay_list(
    session_factory: sessionmaker,
    *,
    client_id: str,
    total_amount: Decimal,
) -> int:
    with session_factory() as db:
        pay_list = PayList(client_id=client_id, currency="CNY", total_amount=total_amount)
        db.add(pay_list)
        db.commit()
        db.refresh(pay_list)
        return pay_list.id


def _insert_gov_payment(
    session_factory: sessionmaker,
    *,
    pay_list_id: int,
    case_id: str,
    paid_amount: Decimal,
    paid_date: date,
    fee_item_id: str | None = None,
) -> int:
    with session_factory() as db:
        payment = GovPayment(
            pay_list_id=pay_list_id,
            case_id=case_id,
            paid_amount=paid_amount,
            paid_date=paid_date,
            currency="CNY",
            status="PAID",
            fee_item_id=fee_item_id,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment.id


def _insert_fee_item_with_draft(
    session_factory: sessionmaker,
    *,
    case_id: str,
    client_id: str,
    year_no: int,
    amount: Decimal,
) -> str:
    with session_factory() as db:
        draft = FeeDraft(
            case_id=case_id,
            client_id=client_id,
            draft_type="ANNUITY_FEE",
            currency="CNY",
            total_gov=amount,
            amount=amount,
        )
        db.add(draft)
        db.flush()
        item = FeeItem(
            draft_id=draft.id,
            case_id=case_id,
            fee_type="GOV",
            year_no=year_no,
            amount=amount,
            fee_code=f"ANN-GOV-{year_no}",
            fee_name=f"年费官费 {year_no}",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id


def _insert_case_receipt(
    session_factory: sessionmaker,
    *,
    case_id: str,
    year_no: int,
    received_amt: Decimal,
) -> str:
    with session_factory() as db:
        receipt = CaseReceipt(
            case_id=case_id,
            year_no=year_no,
            received_amt=received_amt,
            receivable_amt=received_amt,
            currency="CNY",
            fee_type="ANNUITY",
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt.id


def test_get_annuity_tasks_returns_report_summary_and_keeps_list_shape(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_a = _create_client(client, auth_headers, name_prefix="ANN-RPT-CLI-A")
    client_b = _create_client(client, auth_headers, name_prefix="ANN-RPT-CLI-B")
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_no_prefix="ANN-RPT-CASE-A",
        from_country="CN",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_b,
        case_no_prefix="ANN-RPT-CASE-B",
        to_country="US",
    )

    task_a = _insert_annuity_task(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a,
        year_no=1,
        due_date=today - timedelta(days=10),
        status="OPEN",
    )
    task_b = _insert_annuity_task(
        session_factory,
        case_id=case_a["id"],
        client_id=client_a,
        year_no=2,
        due_date=today + timedelta(days=10),
        status="DONE",
        notice_status="SENT",
    )
    task_c = _insert_annuity_task(
        session_factory,
        case_id=case_b["id"],
        client_id=client_b,
        year_no=1,
        due_date=today + timedelta(days=30),
        status="OPEN",
    )

    resp = client.get(
        "/api/v1/annuity/tasks", headers=auth_headers, params={"page": 1, "page_size": 20}
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert set(payload) >= {"items", "page", "page_size", "total", "summary"}
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 3

    summary = payload["summary"]
    assert summary["total_task_count"] == 3
    assert summary["open_task_count"] == 2
    assert summary["done_task_count"] == 1
    assert summary["overdue_task_count"] == 1
    assert {item["key"]: item["count"] for item in summary["status_counts"]} == {
        "OPEN": 2,
        "DONE": 1,
    }
    assert {item["key"]: item["count"] for item in summary["year_counts"]} == {
        "1": 2,
        "2": 1,
    }

    returned_ids = {item["id"] for item in payload["items"]}
    assert returned_ids == {task_a, task_b, task_c}


def test_get_annuity_tasks_supports_report_filters(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_a = _create_client(client, auth_headers, name_prefix="ANN-RPT-FLT-A")
    client_b = _create_client(client, auth_headers, name_prefix="ANN-RPT-FLT-B")
    case_cn = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_no_prefix="ANN-RPT-FLT-CASE-CN",
        from_country="CN",
    )
    case_us = _create_case(
        client,
        auth_headers,
        client_id=client_b,
        case_no_prefix="ANN-RPT-FLT-CASE-US",
        from_country="US",
    )

    cn_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_cn["id"],
        client_id=client_a,
        year_no=1,
        due_date=today - timedelta(days=3),
        status="OPEN",
    )
    us_done_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_us["id"],
        client_id=client_b,
        year_no=2,
        due_date=today + timedelta(days=15),
        status="DONE",
    )
    us_open_task_id = _insert_annuity_task(
        session_factory,
        case_id=case_us["id"],
        client_id=client_b,
        year_no=3,
        due_date=today + timedelta(days=45),
        status="OPEN",
    )

    baseline_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"page": 1, "page_size": 20},
    )
    assert baseline_resp.status_code == 200, baseline_resp.text
    baseline_total = baseline_resp.json()["total"]

    client_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={
            "client_id": client_b,
            "page": 1,
            "page_size": 20,
        },
    )
    assert client_filtered.status_code == 200, client_filtered.text
    client_payload = client_filtered.json()
    assert client_payload["total"] == 2
    assert {item["id"] for item in client_payload["items"]} == {us_done_task_id, us_open_task_id}
    assert client_payload["summary"]["total_task_count"] == 2
    assert client_payload["summary"]["done_task_count"] == 1

    case_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"case_id": case_cn["id"], "page": 1, "page_size": 20},
    )
    assert case_filtered.status_code == 200, case_filtered.text
    case_payload = case_filtered.json()
    assert case_payload["total"] == 1
    assert [item["id"] for item in case_payload["items"]] == [cn_task_id]

    country_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"country": "CN", "page": 1, "page_size": 20},
    )
    assert country_filtered.status_code == 200, country_filtered.text
    country_payload = country_filtered.json()
    assert country_payload["total"] == baseline_total

    payment_status_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"payment_status": "PAID", "page": 1, "page_size": 20},
    )
    assert payment_status_filtered.status_code == 200, payment_status_filtered.text
    payment_status_payload = payment_status_filtered.json()
    assert payment_status_payload["total"] == 0
    assert payment_status_payload["summary"]["official_paid_task_count"] == 0
    assert payment_status_payload["summary"]["client_received_task_count"] == 0

    year_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"client_id": client_b, "annuity_year": 2, "page": 1, "page_size": 20},
    )
    assert year_filtered.status_code == 200, year_filtered.text
    year_payload = year_filtered.json()
    assert year_payload["total"] == 1
    assert [item["id"] for item in year_payload["items"]] == [us_done_task_id]

    task_status_filtered = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={
            "client_id": client_b,
            "task_status": "DONE",
            "date_from": (today + timedelta(days=1)).isoformat(),
            "date_to": (today + timedelta(days=30)).isoformat(),
            "page": 1,
            "page_size": 20,
        },
    )
    assert task_status_filtered.status_code == 200, task_status_filtered.text
    task_status_payload = task_status_filtered.json()
    assert task_status_payload["total"] == 1
    assert [item["id"] for item in task_status_payload["items"]] == [us_done_task_id]
    assert task_status_payload["summary"]["done_task_count"] == 1


def test_get_annuity_tasks_returns_grouped_amount_summaries(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    country_a = f"C{uuid4().hex[:3].upper()}"
    country_b = f"U{uuid4().hex[:3].upper()}"
    client_a = _create_client(client, auth_headers, name_prefix="ANN-AMT-CLI-A")
    client_b = _create_client(client, auth_headers, name_prefix="ANN-AMT-CLI-B")
    case_cn = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_no_prefix="ANN-AMT-CASE-CN",
        from_country=country_a,
    )
    case_us = _create_case(
        client,
        auth_headers,
        client_id=client_b,
        case_no_prefix="ANN-AMT-CASE-US",
        to_country=country_b,
    )

    _insert_annuity_task(
        session_factory,
        case_id=case_cn["id"],
        client_id=client_a,
        year_no=101,
        due_date=today + timedelta(days=10),
        status="OPEN",
        gov_fee_amt=Decimal("60.00"),
        service_fee_amt=Decimal("40.00"),
    )
    _insert_annuity_task(
        session_factory,
        case_id=case_cn["id"],
        client_id=client_a,
        year_no=202,
        due_date=today + timedelta(days=40),
        status="DONE",
        gov_fee_amt=Decimal("110.00"),
        service_fee_amt=Decimal("90.00"),
    )
    _insert_annuity_task(
        session_factory,
        case_id=case_us["id"],
        client_id=client_b,
        year_no=101,
        due_date=today + timedelta(days=20),
        status="OPEN",
        gov_fee_amt=Decimal("40.00"),
        service_fee_amt=Decimal("20.00"),
    )

    pay_list_a = _insert_pay_list(
        session_factory, client_id=client_a, total_amount=Decimal("300.00")
    )
    pay_list_b = _insert_pay_list(
        session_factory, client_id=client_b, total_amount=Decimal("60.00")
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_a,
        case_id=case_cn["id"],
        paid_amount=Decimal("300.00"),
        paid_date=today,
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_b,
        case_id=case_us["id"],
        paid_amount=Decimal("60.00"),
        paid_date=today,
    )
    _insert_case_receipt(
        session_factory,
        case_id=case_cn["id"],
        year_no=101,
        received_amt=Decimal("150.00"),
    )
    _insert_case_receipt(
        session_factory,
        case_id=case_cn["id"],
        year_no=202,
        received_amt=Decimal("230.00"),
    )
    _insert_case_receipt(
        session_factory,
        case_id=case_us["id"],
        year_no=101,
        received_amt=Decimal("70.00"),
    )

    resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"page": 1, "page_size": 20},
    )
    assert resp.status_code == 200, resp.text
    summary = resp.json()["summary"]

    client_amounts = {item["key"]: item for item in summary["client_amounts"]}
    assert client_amounts[client_a]["task_count"] == 2
    assert client_amounts[client_a]["payable_amount"] == "300.00"
    assert client_amounts[client_a]["official_paid_amount"] == "300.00"
    assert client_amounts[client_a]["client_received_amount"] == "380.00"
    assert client_amounts[client_a]["label"]
    assert client_amounts[client_b]["task_count"] == 1
    assert client_amounts[client_b]["payable_amount"] == "60.00"
    assert client_amounts[client_b]["official_paid_amount"] == "60.00"
    assert client_amounts[client_b]["client_received_amount"] == "70.00"
    assert client_amounts[client_b]["label"]
    country_amounts = {item["key"]: item for item in summary["country_amounts"]}
    assert country_amounts[country_a]["label"] == country_a
    assert country_amounts[country_a]["task_count"] == 2
    assert country_amounts[country_a]["payable_amount"] == "300.00"
    assert country_amounts[country_a]["official_paid_amount"] == "300.00"
    assert country_amounts[country_a]["client_received_amount"] == "380.00"
    assert country_amounts[country_b]["label"] == country_b
    assert country_amounts[country_b]["task_count"] == 1
    assert country_amounts[country_b]["payable_amount"] == "60.00"
    assert country_amounts[country_b]["official_paid_amount"] == "60.00"
    assert country_amounts[country_b]["client_received_amount"] == "70.00"

    year_amounts = {item["key"]: item for item in summary["year_amounts"]}
    assert year_amounts["101"]["label"] == "第 101 年"
    assert year_amounts["101"]["task_count"] == 2
    assert year_amounts["101"]["payable_amount"] == "160.00"
    assert year_amounts["101"]["official_paid_amount"] == "160.00"
    assert year_amounts["101"]["client_received_amount"] == "220.00"
    assert year_amounts["202"]["label"] == "第 202 年"
    assert year_amounts["202"]["task_count"] == 1
    assert year_amounts["202"]["payable_amount"] == "200.00"
    assert year_amounts["202"]["official_paid_amount"] == "200.00"
    assert year_amounts["202"]["client_received_amount"] == "230.00"


def test_get_annuity_tasks_returns_success_rate_metrics(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_id = _create_client(client, auth_headers, name_prefix="ANN-SUC-CLI")
    case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        case_no_prefix="ANN-SUC-CASE",
        from_country=f"S{uuid4().hex[:3].upper()}",
    )

    _insert_annuity_task(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=301,
        due_date=today + timedelta(days=10),
        status="OPEN",
        client_instruction="PAY",
    )
    _insert_annuity_task(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=302,
        due_date=today + timedelta(days=10),
        status="OPEN",
        client_instruction="PAY",
    )
    _insert_annuity_task(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=303,
        due_date=today + timedelta(days=10),
        status="OPEN",
        client_instruction="PAY",
    )
    _insert_annuity_task(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=304,
        due_date=today + timedelta(days=10),
        status="OPEN",
        client_instruction="ABANDON",
    )

    on_time_item_id = _insert_fee_item_with_draft(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=301,
        amount=Decimal("100.00"),
    )
    late_item_id = _insert_fee_item_with_draft(
        session_factory,
        case_id=case["id"],
        client_id=client_id,
        year_no=302,
        amount=Decimal("120.00"),
    )
    pay_list_id = _insert_pay_list(
        session_factory,
        client_id=client_id,
        total_amount=Decimal("220.00"),
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_id,
        case_id=case["id"],
        paid_amount=Decimal("100.00"),
        paid_date=today + timedelta(days=5),
        fee_item_id=on_time_item_id,
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_id,
        case_id=case["id"],
        paid_amount=Decimal("120.00"),
        paid_date=today + timedelta(days=20),
        fee_item_id=late_item_id,
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_id,
        case_id=case["id"],
        paid_amount=Decimal("50.00"),
        paid_date=today + timedelta(days=2),
        fee_item_id=None,
    )

    resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"page": 1, "page_size": 20},
    )
    assert resp.status_code == 200, resp.text
    summary = resp.json()["summary"]

    assert summary["monitored_task_count"] == 3
    assert summary["on_time_paid_count"] == 1
    assert summary["late_paid_count"] == 1
    assert summary["success_rate"] == 1 / 3


def test_get_annuity_tasks_applies_payment_status_truth_and_summary(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    today = date.today()
    client_id = _create_client(client, auth_headers, name_prefix="ANN-PAY-CLI")
    case_a = _create_case(client, auth_headers, client_id=client_id, case_no_prefix="ANN-PAY-A")
    case_b = _create_case(client, auth_headers, client_id=client_id, case_no_prefix="ANN-PAY-B")
    case_c = _create_case(client, auth_headers, client_id=client_id, case_no_prefix="ANN-PAY-C")
    case_d = _create_case(client, auth_headers, client_id=client_id, case_no_prefix="ANN-PAY-D")

    task_paid = _insert_annuity_task(
        session_factory,
        case_id=case_a["id"],
        client_id=client_id,
        year_no=401,
        due_date=today + timedelta(days=30),
        status="OPEN",
        gov_fee_amt=Decimal("100.00"),
        service_fee_amt=Decimal("50.00"),
    )
    task_collected_only = _insert_annuity_task(
        session_factory,
        case_id=case_b["id"],
        client_id=client_id,
        year_no=402,
        due_date=today + timedelta(days=40),
        status="OPEN",
        gov_fee_amt=Decimal("120.00"),
        service_fee_amt=Decimal("30.00"),
    )
    task_unpaid = _insert_annuity_task(
        session_factory,
        case_id=case_c["id"],
        client_id=client_id,
        year_no=403,
        due_date=today + timedelta(days=50),
        status="OPEN",
        gov_fee_amt=Decimal("80.00"),
        service_fee_amt=Decimal("20.00"),
    )
    task_official_only = _insert_annuity_task(
        session_factory,
        case_id=case_d["id"],
        client_id=client_id,
        year_no=404,
        due_date=today + timedelta(days=60),
        status="OPEN",
        gov_fee_amt=Decimal("90.00"),
        service_fee_amt=Decimal("10.00"),
    )

    paid_item_id = _insert_fee_item_with_draft(
        session_factory,
        case_id=case_a["id"],
        client_id=client_id,
        year_no=401,
        amount=Decimal("100.00"),
    )
    official_only_item_id = _insert_fee_item_with_draft(
        session_factory,
        case_id=case_d["id"],
        client_id=client_id,
        year_no=404,
        amount=Decimal("90.00"),
    )
    pay_list_id = _insert_pay_list(
        session_factory,
        client_id=client_id,
        total_amount=Decimal("190.00"),
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_id,
        case_id=case_a["id"],
        paid_amount=Decimal("100.00"),
        paid_date=today + timedelta(days=5),
        fee_item_id=paid_item_id,
    )
    _insert_gov_payment(
        session_factory,
        pay_list_id=pay_list_id,
        case_id=case_d["id"],
        paid_amount=Decimal("90.00"),
        paid_date=today + timedelta(days=6),
        fee_item_id=official_only_item_id,
    )
    _insert_case_receipt(
        session_factory,
        case_id=case_a["id"],
        year_no=401,
        received_amt=Decimal("150.00"),
    )
    _insert_case_receipt(
        session_factory,
        case_id=case_b["id"],
        year_no=402,
        received_amt=Decimal("150.00"),
    )

    paid_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"client_id": client_id, "payment_status": "PAID", "page": 1, "page_size": 20},
    )
    assert paid_resp.status_code == 200, paid_resp.text
    paid_payload = paid_resp.json()
    assert {item["id"] for item in paid_payload["items"]} == {task_paid, task_official_only}
    paid_summary = paid_payload["summary"]
    assert paid_summary["official_paid_task_count"] == 2
    assert paid_summary["client_received_task_count"] == 1
    assert paid_summary["collected_not_paid_task_count"] == 0
    assert paid_summary["outstanding_task_count"] == 0

    unpaid_resp = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"client_id": client_id, "payment_status": "UNPAID", "page": 1, "page_size": 20},
    )
    assert unpaid_resp.status_code == 200, unpaid_resp.text
    unpaid_payload = unpaid_resp.json()
    assert {item["id"] for item in unpaid_payload["items"]} == {task_collected_only, task_unpaid}
    unpaid_summary = unpaid_payload["summary"]
    assert unpaid_summary["official_paid_task_count"] == 0
    assert unpaid_summary["client_received_task_count"] == 1
    assert unpaid_summary["collected_not_paid_task_count"] == 1
    assert unpaid_summary["outstanding_task_count"] == 1
