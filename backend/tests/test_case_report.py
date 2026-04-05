from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.session import get_db


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _db_session(client: TestClient):
    db_gen = client.app.dependency_overrides[get_db]()
    db = next(db_gen)
    return db, db_gen


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
    case_type: str,
    patent_category: str,
    status: str,
    filing_date: str | None = None,
    recv_date: str | None = None,
    app_no: str | None = None,
    country: str | None = None,
    primary_agent_id: str | None = None,
    second_agent_id: str | None = None,
) -> dict:
    payload: dict[str, object] = {
        "case_no": _uid("CASE-RPT"),
        "case_type": case_type,
        "patent_category": patent_category,
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "Case Report Fixture",
        "status": status,
        "applicants": [{"seq": 1, "is_first": True, "name_cn": "测试申请人"}],
    }
    if filing_date is not None:
        payload["filing_date"] = filing_date
    if recv_date is not None:
        payload["recv_date"] = recv_date
    if app_no is not None:
        payload["app_no"] = app_no
    if country is not None:
        payload["from_country"] = country
    if primary_agent_id is not None:
        payload["primary_agent_id"] = primary_agent_id
    if second_agent_id is not None:
        payload["second_agent_id"] = second_agent_id

    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _set_case_terminal_dates(
    client: TestClient,
    *,
    case_id: str,
    filing_date: str | None = None,
    grant_date: str | None = None,
    terminated_date: str | None = None,
    invalidated_date: str | None = None,
    withdrawn_date: str | None = None,
    abandoned_date: str | None = None,
) -> None:
    db, db_gen = _db_session(client)
    try:
        from app.modules.cases.models import Case

        case = db.query(Case).filter(Case.id == case_id).one()
        case.filing_date = date.fromisoformat(filing_date) if filing_date else case.filing_date
        case.grant_date = date.fromisoformat(grant_date) if grant_date else case.grant_date
        case.terminated_date = date.fromisoformat(terminated_date) if terminated_date else None
        case.invalidated_date = date.fromisoformat(invalidated_date) if invalidated_date else None
        case.withdrawn_date = date.fromisoformat(withdrawn_date) if withdrawn_date else None
        case.abandoned_date = date.fromisoformat(abandoned_date) if abandoned_date else None
        db.commit()
    finally:
        db_gen.close()


def test_get_cases_returns_case_report_summary_and_preserves_list_contract(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-A")

    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="NOT_FILED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="DES",
        status="PENDING",
        filing_date="2026-01-10",
        app_no="CASE-RPT-001",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="SEARCH",
        patent_category="INV",
        status="GRANTED",
        filing_date="2026-02-10",
        app_no="CASE-RPT-002",
    )

    resp = client.get(
        "/api/v1/cases",
        params={"client_id": client_a, "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    assert set(payload) >= {"items", "page", "page_size", "total", "summary"}
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 3

    summary = payload["summary"]
    assert summary["total_case_count"] == 3
    assert {item["key"]: item["count"] for item in summary["status_counts"]} == {
        "NOT_FILED": 1,
        "PENDING": 1,
        "GRANTED": 1,
    }
    assert {item["key"]: item["count"] for item in summary["case_type_counts"]} == {
        "NORMAL": 2,
        "SEARCH": 1,
    }
    assert len(payload["items"]) == 3
    assert all("case_no" in item and "client_id" in item for item in payload["items"])


def test_get_cases_supports_case_report_filters(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-B")
    client_b = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-C")
    agent_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    agent_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    today = date.today()

    c1 = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="NOT_FILED",
        recv_date=(today - timedelta(days=20)).isoformat(),
        app_no="CASE-RPT-010",
        country="CN",
        primary_agent_id=agent_a,
    )
    c2 = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="SEARCH",
        patent_category="DES",
        status="PENDING",
        recv_date=(today - timedelta(days=10)).isoformat(),
        app_no="CASE-RPT-011",
        country="US",
        second_agent_id=agent_a,
    )
    c3 = _create_case(
        client,
        auth_headers,
        client_id=client_b,
        case_type="NORMAL",
        patent_category="INV",
        status="GRANTED",
        recv_date=(today - timedelta(days=2)).isoformat(),
        app_no="CASE-RPT-012",
        country="JP",
        primary_agent_id=agent_b,
    )

    agent_filtered = client.get(
        "/api/v1/cases",
        params={"agent_id": agent_a, "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert agent_filtered.status_code == 200, agent_filtered.text
    agent_payload = agent_filtered.json()
    assert agent_payload["total"] == 2
    assert {item["id"] for item in agent_payload["items"]} == {c1["id"], c2["id"]}

    country_filtered = client.get(
        "/api/v1/cases",
        params={"country": "CN", "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert country_filtered.status_code == 200, country_filtered.text
    country_payload = country_filtered.json()
    assert country_payload["total"] == 1
    assert [item["id"] for item in country_payload["items"]] == [c1["id"]]

    date_filtered = client.get(
        "/api/v1/cases",
        params={
            "date_from": (today - timedelta(days=12)).isoformat(),
            "date_to": (today - timedelta(days=1)).isoformat(),
            "page": 1,
            "page_size": 20,
        },
        headers=auth_headers,
    )
    assert date_filtered.status_code == 200, date_filtered.text
    date_payload = date_filtered.json()
    assert date_payload["total"] == 2
    assert {item["id"] for item in date_payload["items"]} == {c2["id"], c3["id"]}


def test_get_cases_returns_country_and_agent_grouped_summaries(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-D")
    agent_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    agent_b = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="NOT_FILED",
        country="CN",
        primary_agent_id=agent_a,
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="SEARCH",
        patent_category="INV",
        status="PENDING",
        country="US",
        primary_agent_id=agent_a,
        second_agent_id=agent_b,
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="DES",
        status="GRANTED",
        second_agent_id=agent_b,
    )

    resp = client.get(
        "/api/v1/cases",
        params={"client_id": client_a, "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    summary = payload["summary"]
    assert {item["key"]: item["count"] for item in summary["country_counts"]} == {
        "CN": 1,
        "US": 1,
        "未填写": 1,
    }
    assert {item["key"]: item["count"] for item in summary["agent_counts"]} == {
        agent_a: 2,
        agent_b: 2,
    }


def test_get_cases_returns_client_grouped_summaries_with_case_type_breakdown(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-F")
    client_b = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-G")

    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="NOT_FILED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="SEARCH",
        patent_category="INV",
        status="PENDING",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_b,
        case_type="NORMAL",
        patent_category="DES",
        status="GRANTED",
    )

    resp = client.get(
        "/api/v1/cases",
        params={"page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    summary = payload["summary"]
    client_counts = {item["key"]: item for item in summary["client_counts"]}
    assert client_counts[client_a]["count"] == 2
    assert {item["key"]: item["count"] for item in client_counts[client_a]["case_type_counts"]} == {
        "NORMAL": 1,
        "SEARCH": 1,
    }
    assert client_counts[client_b]["count"] == 1
    assert {item["key"]: item["count"] for item in client_counts[client_b]["case_type_counts"]} == {
        "NORMAL": 1,
    }


def test_get_cases_returns_grant_rate_metrics(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-E")

    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="GRANTED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="TERMINATED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="INVALIDATED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="EXPIRED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="REJECTED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="WITHDRAWN",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="ABANDONED",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="PENDING",
    )
    _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="OA1",
    )

    resp = client.get(
        "/api/v1/cases",
        params={"client_id": client_a, "page": 1, "page_size": 30},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()

    summary = payload["summary"]
    assert summary["granted_count"] == 4
    assert summary["terminated_count"] == 1
    assert summary["invalidated_count"] == 1
    assert summary["in_prosecution_count"] == 2
    assert summary["grant_rate"] == 4 / 7


def test_get_cases_returns_year_and_month_trend_metrics(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_a = _create_client(client, auth_headers, name_prefix="CASE-RPT-CLI-TREND")

    pending_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="PENDING",
        app_no="CASE-RPT-TREND-000",
    )
    _set_case_terminal_dates(client, case_id=pending_case["id"], filing_date="2026-01-10")

    granted_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="GRANTED",
        app_no="CASE-RPT-TREND-001",
    )
    _set_case_terminal_dates(
        client,
        case_id=granted_case["id"],
        filing_date="2025-01-10",
        grant_date="2026-02-12",
    )

    terminated_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="TERMINATED",
    )
    _set_case_terminal_dates(client, case_id=terminated_case["id"], terminated_date="2026-03-05")

    invalidated_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="INVALIDATED",
    )
    _set_case_terminal_dates(client, case_id=invalidated_case["id"], invalidated_date="2026-03-20")

    withdrawn_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="WITHDRAWN",
    )
    _set_case_terminal_dates(client, case_id=withdrawn_case["id"], withdrawn_date="2026-02-28")

    abandoned_case = _create_case(
        client,
        auth_headers,
        client_id=client_a,
        case_type="NORMAL",
        patent_category="INV",
        status="ABANDONED",
    )
    _set_case_terminal_dates(client, case_id=abandoned_case["id"], abandoned_date="2026-01-30")

    resp = client.get(
        "/api/v1/cases",
        params={"client_id": client_a, "page": 1, "page_size": 50},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    summary = payload["summary"]

    year_trends = {item["key"]: item for item in summary["year_trends"]}
    assert year_trends["2026"] == {
        "key": "2026",
        "label": "2026",
        "new_case_count": 1,
        "granted_count": 1,
        "terminated_count": 1,
        "invalidated_count": 1,
        "withdrawn_count": 1,
        "abandoned_count": 1,
    }

    month_trends = {item["key"]: item for item in summary["month_trends"]}
    assert month_trends["2026-01"] == {
        "key": "2026-01",
        "label": "2026-01",
        "new_case_count": 1,
        "granted_count": 0,
        "terminated_count": 0,
        "invalidated_count": 0,
        "withdrawn_count": 0,
        "abandoned_count": 1,
    }
    assert month_trends["2026-02"] == {
        "key": "2026-02",
        "label": "2026-02",
        "new_case_count": 0,
        "granted_count": 1,
        "terminated_count": 0,
        "invalidated_count": 0,
        "withdrawn_count": 1,
        "abandoned_count": 0,
    }
    assert month_trends["2026-03"] == {
        "key": "2026-03",
        "label": "2026-03",
        "new_case_count": 0,
        "granted_count": 0,
        "terminated_count": 1,
        "invalidated_count": 1,
        "withdrawn_count": 0,
        "abandoned_count": 0,
    }
