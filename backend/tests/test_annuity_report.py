from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.annuity.models import AnnuityTask


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
) -> int:
    with session_factory() as db:
        task = AnnuityTask(
            case_id=case_id,
            client_id=client_id,
            year_no=year_no,
            due_date=due_date,
            status=status,
            notice_status=notice_status,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id


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
    assert payment_status_payload["total"] == baseline_total

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
