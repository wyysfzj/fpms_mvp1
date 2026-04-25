from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str], label: str) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"A7-{label}-{uuid4().hex[:8]}",
            "name_cn": f"A7 {label} 客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_address(
    client: TestClient, auth_headers: dict[str, str], client_id: str, address_type: str
) -> str:
    response = client.post(
        f"/api/v1/clients/{client_id}/addresses",
        json={"address_type": address_type, "address_line1": f"A7 {address_type} 地址"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory) -> str:
    applicant_id = str(uuid4())
    suffix = uuid4().hex[:8]
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"A7-AP-{suffix}",
                name_cn=f"A7 申请人 {suffix}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _case_payload(
    *,
    case_no: str,
    client_id: str,
    applicant_id: str,
    doc_address_id: str | None = None,
    bill_address_id: str | None = None,
) -> dict:
    return {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "doc_address_id": doc_address_id,
        "bill_address_id": bill_address_id,
        "title_cn": "A7 发明人与地址",
        "recv_date": "2026-03-01",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": "A7 申请人",
            }
        ],
        "inventors": [],
    }


def test_a7_no_inventor_and_valid_addresses_follow_mvp_contract(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, "MAIN")
    applicant_id = _seed_applicant(session_factory)
    doc_address_id = _create_address(client, auth_headers, client_id, "MAILING")
    bill_address_id = _create_address(client, auth_headers, client_id, "BILLING")

    no_inventor_response = client.post(
        "/api/v1/cases",
        json=_case_payload(
            case_no=f"A7-NO-{uuid4().hex[:8]}",
            client_id=client_id,
            applicant_id=applicant_id,
        ),
        headers=auth_headers,
    )
    assert no_inventor_response.status_code == 201, no_inventor_response.text
    no_inventor_detail = client.get(
        f"/api/v1/cases/{no_inventor_response.json()['id']}", headers=auth_headers
    ).json()
    assert no_inventor_detail["inventors"] == []

    valid_address_response = client.post(
        "/api/v1/cases",
        json=_case_payload(
            case_no=f"A7-ADDR-{uuid4().hex[:8]}",
            client_id=client_id,
            applicant_id=applicant_id,
            doc_address_id=doc_address_id,
            bill_address_id=bill_address_id,
        ),
        headers=auth_headers,
    )
    assert valid_address_response.status_code == 201, valid_address_response.text
    valid_detail = client.get(
        f"/api/v1/cases/{valid_address_response.json()['id']}", headers=auth_headers
    ).json()
    assert valid_detail["doc_address_id"] == doc_address_id
    assert valid_detail["bill_address_id"] == bill_address_id


def test_a7_rejects_address_owned_by_another_client(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, "MAIN")
    other_client_id = _create_client(client, auth_headers, "OTHER")
    applicant_id = _seed_applicant(session_factory)
    other_address_id = _create_address(client, auth_headers, other_client_id, "MAILING")

    response = client.post(
        "/api/v1/cases",
        json=_case_payload(
            case_no=f"A7-WRONG-{uuid4().hex[:8]}",
            client_id=client_id,
            applicant_id=applicant_id,
            doc_address_id=other_address_id,
        ),
        headers=auth_headers,
    )
    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "CASE_ADDRESS_CLIENT_MISMATCH"
