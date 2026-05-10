from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case

TARGET_CASE_NO = "RUI202605100035"


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        headers=auth_headers,
        json={"name_cn": _uid("ANN-TGT-CLI"), "default_currency": "CNY"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_no: str,
) -> str:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": case_no,
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "年费定向生成测试",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _set_case_grant_fields(
    session_factory: sessionmaker,
    *,
    case_id: str,
    status: str,
) -> None:
    with session_factory() as db:
        case = db.execute(select(Case).where(Case.id == case_id)).scalar_one()
        case.status = status
        case.app_no = _uid("CNAPP")
        case.filing_date = date(2020, 3, 20)
        case.pub_no = _uid("CNPUB")
        case.pub_date = date(2021, 4, 1)
        case.grant_no = _uid("CNGRANT")
        case.grant_date = date(2026, 8, 1)
        case.first_annuity_year = 3
        case.valid_until = date(2040, 3, 20)
        db.commit()


def test_generate_annuity_tasks_accepts_case_number_and_list_filters_by_case_number(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers)
    case_id = _create_case(client, auth_headers, client_id=client_id, case_no=TARGET_CASE_NO)
    _set_case_grant_fields(session_factory, case_id=case_id, status="GRANTED")

    generate_response = client.post(
        "/api/v1/annuity/tasks/generate",
        headers=auth_headers,
        json={"case_id": TARGET_CASE_NO},
    )

    assert generate_response.status_code == 201, generate_response.text
    generated = generate_response.json()
    assert generated["case_id"] == case_id
    assert generated["case_no"] == TARGET_CASE_NO
    assert generated["first_year"] == 3
    assert generated["tasks_created"] > 0

    list_response = client.get(
        "/api/v1/annuity/tasks",
        headers=auth_headers,
        params={"case_no": TARGET_CASE_NO, "page": 1, "page_size": 100},
    )

    assert list_response.status_code == 200, list_response.text
    payload = list_response.json()
    assert payload["total"] == generated["tasks_created"]
    assert {item["case_id"] for item in payload["items"]} == {case_id}
    assert {item["case_no"] for item in payload["items"]} == {TARGET_CASE_NO}


def test_generate_annuity_tasks_by_case_number_keeps_granted_prerequisite(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_no = _uid("ANN-TGT")
    client_id = _create_client(client, auth_headers)
    case_id = _create_case(client, auth_headers, client_id=client_id, case_no=case_no)
    _set_case_grant_fields(session_factory, case_id=case_id, status="GRANT_PENDING")

    response = client.post(
        "/api/v1/annuity/tasks/generate",
        headers=auth_headers,
        json={"case_id": case_no},
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "CASE_NOT_GRANTED"
