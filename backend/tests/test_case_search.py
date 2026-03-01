"""Tests for A5 — Advanced Case Search filter parameters."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.session import get_db

_COUNTER = 0


def _unique_case_no(prefix: str = "A5") -> str:
    global _COUNTER
    _COUNTER += 1
    return f"{prefix}_SEARCH_{_COUNTER:04d}"


_MINIMAL_APPLICANT = [{"seq": 1, "is_first": True, "name_cn": "测试申请人"}]


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_type: str = "NORMAL",
    patent_category: str = "INV",
    flow_dir: str = "CN_DOMESTIC",
    primary_agent_id: str | None = None,
    **extra: object,
) -> dict:
    """Helper to create a case with specific attributes."""
    payload = {
        "case_no": _unique_case_no(),
        "case_type": case_type,
        "patent_category": patent_category,
        "flow_dir": flow_dir,
        "applicants": _MINIMAL_APPLICANT,
    }
    if primary_agent_id:
        payload["primary_agent_id"] = primary_agent_id
    payload.update(extra)
    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"Create failed: {resp.text}"
    return resp.json()


def _set_filing_date(client: TestClient, case_id: str, filing_date_str: str) -> None:
    """Set filing_date directly via ORM since it's not exposed in create/update API."""
    from datetime import date as date_type

    from app.modules.cases.models import Case

    app = client.app
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        case.filing_date = date_type.fromisoformat(filing_date_str)
        db.commit()
    finally:
        db_gen.close()


def test_filter_by_case_type(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Filter by case_type returns only matching cases."""
    c1 = _create_case(client, auth_headers, case_type="NORMAL")
    c2 = _create_case(client, auth_headers, case_type="PCT_INTL")

    resp = client.get(
        "/api/v1/cases",
        params={"case_type": "PCT_INTL", "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c2["id"] in ids
    assert c1["id"] not in ids


def test_filter_by_patent_category(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Filter by patent_category returns only matching cases."""
    c1 = _create_case(client, auth_headers, patent_category="INV")
    c2 = _create_case(client, auth_headers, patent_category="DES")

    resp = client.get(
        "/api/v1/cases",
        params={"patent_category": "DES", "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c2["id"] in ids
    assert c1["id"] not in ids


def test_filter_by_flow_dir(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Filter by flow_dir returns only matching cases."""
    c1 = _create_case(client, auth_headers, flow_dir="CN_DOMESTIC")
    c2 = _create_case(client, auth_headers, flow_dir="FOREIGN_INBOUND")

    resp = client.get(
        "/api/v1/cases",
        params={"flow_dir": "FOREIGN_INBOUND", "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c2["id"] in ids
    assert c1["id"] not in ids


def test_filter_by_primary_agent_id(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Filter by primary_agent_id returns only matching cases."""
    agent_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    c1 = _create_case(client, auth_headers, primary_agent_id=agent_id)
    c2 = _create_case(client, auth_headers)

    resp = client.get(
        "/api/v1/cases",
        params={"primary_agent_id": agent_id, "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c1["id"] in ids
    assert c2["id"] not in ids


def test_filter_by_filing_date_range(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Filter by filing_date_from and filing_date_to returns cases in range."""
    c1 = _create_case(client, auth_headers)
    c2 = _create_case(client, auth_headers)
    c3 = _create_case(client, auth_headers)

    _set_filing_date(client, c1["id"], "2025-01-15")
    _set_filing_date(client, c2["id"], "2025-06-15")
    _set_filing_date(client, c3["id"], "2025-12-15")

    # Range: March to September 2025
    resp = client.get(
        "/api/v1/cases",
        params={
            "filing_date_from": "2025-03-01",
            "filing_date_to": "2025-09-30",
            "page_size": 100,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c2["id"] in ids
    assert c1["id"] not in ids
    assert c3["id"] not in ids


def test_combined_filters(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Multiple filters combine with AND logic."""
    c1 = _create_case(client, auth_headers, case_type="NORMAL", patent_category="INV")
    c2 = _create_case(client, auth_headers, case_type="NORMAL", patent_category="DES")
    c3 = _create_case(client, auth_headers, case_type="PCT_INTL", patent_category="INV")

    resp = client.get(
        "/api/v1/cases",
        params={"case_type": "NORMAL", "patent_category": "INV", "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c1["id"] in ids
    assert c2["id"] not in ids
    assert c3["id"] not in ids


def test_export_filters_match(client: TestClient, auth_headers: dict[str, str]) -> None:
    """GET /cases/export supports the same filters as GET /cases."""
    c1 = _create_case(client, auth_headers, case_type="PCT_INTL")

    resp = client.get(
        "/api/v1/cases/export",
        params={"case_type": "PCT_INTL", "page_size": 100},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert c1["id"] in ids
