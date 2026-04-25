from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.masterdata.applicants.models import Applicant


def _case_no(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _assert_error(response, status_code: int, error_code: str) -> dict:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["error"]["code"] == error_code
    assert payload["error"]["message"]
    return payload


def _seed_applicant(
    session_factory: sessionmaker,
    *,
    applicant_type: str = "ENTITY",
) -> str:
    applicant_id = str(uuid4())
    unique = uuid4().hex[:8].upper()
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"DATE-AP-{unique}",
                name_cn=f"日期规则申请人-{unique}",
                applicant_type=applicant_type,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _applicants_payload(applicant_id: str) -> list[dict[str, object]]:
    return [
        {
            "seq": 1,
            "is_first": True,
            "applicant_id": applicant_id,
            "name_cn": "日期规则申请人",
        }
    ]


def _case_payload(session_factory: sessionmaker, **overrides) -> dict:
    applicant_id = _seed_applicant(session_factory)
    payload = {
        "case_no": _case_no("DATERULE"),
        "applicants": _applicants_payload(applicant_id),
    }
    payload.update(overrides)
    return payload


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    *,
    payload: dict | None = None,
) -> dict:
    body = _case_payload(session_factory)
    if payload:
        body.update(payload)
    response = client.post("/api/v1/cases", headers=auth_headers, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def _create_case_with_priority(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    *,
    prio_date: str = "2026-03-15",
) -> dict:
    return _create_case(
        client,
        auth_headers,
        session_factory,
        payload={
            "priorities": [
                {
                    "seq": 1,
                    "country_code": "CN",
                    "prio_no": "202610000001",
                    "prio_date": prio_date,
                }
            ]
        },
    )


def test_create_rejects_published_missing_required_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            session_factory,
            case_no=_case_no("PUBLISHED"),
            status="PUBLISHED",
        ),
    )

    payload = _assert_error(response, 400, "CASE_PUBLISHED_FIELDS_REQUIRED")
    details = payload["error"]["details"]
    assert details["status"] == "PUBLISHED"
    assert details["missing_fields"] == ["app_no", "filing_date", "pub_no", "pub_date"]


def test_create_rejects_granted_missing_required_fields(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            session_factory,
            case_no=_case_no("GRANTED"),
            status="GRANTED",
        ),
    )

    payload = _assert_error(response, 400, "CASE_GRANTED_FIELDS_REQUIRED")
    details = payload["error"]["details"]
    assert details["status"] == "GRANTED"
    assert details["missing_fields"] == [
        "app_no",
        "filing_date",
        "pub_no",
        "pub_date",
        "grant_no",
        "grant_date",
        "first_annuity_year",
        "valid_until",
    ]


def test_create_preserves_priority_structural_errors(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            session_factory,
            case_no=_case_no("PRIORITY"),
            status="PUBLISHED",
            priorities=[{"seq": 1, "country_code": "CN", "prio_no": "202610000002"}],
        ),
    )

    _assert_error(response, 400, "CASE_PRIORITY_INCOMPLETE")


@pytest.mark.parametrize("app_no", ["   ", "CN20261000\n01"])
def test_update_rejects_invalid_app_no_when_required(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    app_no: str,
) -> None:
    case = _create_case(client, auth_headers, session_factory)

    response = client.put(
        f"/api/v1/cases/{case['id']}",
        headers=auth_headers,
        json={
            "status": "PUBLISHED",
            "filing_date": "2026-03-15",
            "app_no": app_no,
            "pub_no": "CN202610000001A",
            "pub_date": "2026-04-01",
        },
    )

    payload = _assert_error(response, 400, "CASE_APP_NO_INVALID")
    assert payload["error"]["details"]["app_no"] == app_no


def test_update_rejects_filing_before_priority(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case_with_priority(
        client,
        auth_headers,
        session_factory,
        prio_date="2026-03-15",
    )

    response = client.put(
        f"/api/v1/cases/{case['id']}",
        headers=auth_headers,
        json={
            "status": "PUBLISHED",
            "filing_date": "2026-03-14",
            "app_no": "CN202610000003",
            "pub_no": "CN202610000003A",
            "pub_date": "2026-04-01",
        },
    )

    payload = _assert_error(response, 400, "CASE_FILING_BEFORE_PRIORITY")
    details = payload["error"]["details"]
    assert details["filing_date"] == "2026-03-14"
    assert details["earliest_priority_date"] == "2026-03-15"


def test_update_allows_filing_equal_priority_and_trims_app_no(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case_with_priority(
        client,
        auth_headers,
        session_factory,
        prio_date="2026-03-15",
    )

    response = client.put(
        f"/api/v1/cases/{case['id']}",
        headers=auth_headers,
        json={
            "status": "PUBLISHED",
            "filing_date": "2026-03-15",
            "app_no": "  CN202610000004  ",
            "pub_no": "CN202610000004A",
            "pub_date": "2026-04-01",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "PUBLISHED"
    assert data["filing_date"] == "2026-03-15"
    assert data["app_no"] == "CN202610000004"


def test_update_allows_minimal_granted_payload(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case = _create_case(client, auth_headers, session_factory)

    response = client.put(
        f"/api/v1/cases/{case['id']}",
        headers=auth_headers,
        json={
            "status": "GRANTED",
            "filing_date": "2026-03-20",
            "app_no": "CN202610000005",
            "pub_no": "CN202610000005A",
            "pub_date": "2026-04-01",
            "grant_no": "CN202610000005B",
            "grant_date": "2026-08-01",
            "first_annuity_year": 3,
            "valid_until": "2046-03-20",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "GRANTED"
    assert data["app_no"] == "CN202610000005"
    assert data["grant_no"] == "CN202610000005B"
    assert data["first_annuity_year"] == 3
    assert data["valid_until"] == "2046-03-20"
