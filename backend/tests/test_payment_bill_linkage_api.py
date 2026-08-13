from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"PBL-CL-{uuid4().hex[:8]}",
            "name_cn": "账单回款客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"PBL-AP-{uuid4().hex[:8]}",
                name_cn=f"账单回款申请人-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
) -> str:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"PBL-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "账单回款链路测试案",
            "recv_date": "2026-03-01",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "账单回款申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_manual_bill(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_id: str,
) -> dict:
    response = client.post(
        "/api/v1/bills/manual",
        json={
            "client_id": client_id,
            "case_id": case_id,
            "currency": "CNY",
            "direction": "AR",
            "status": "UNSETTLED",
            "items": [
                {
                    "description": "授权官费",
                    "quantity": 1,
                    "unit_price": "680.00",
                    "fee_type": "GOV",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_payment_created_from_bill_keeps_bill_case_linkage_for_list_and_offset(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_id = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )
    bill = _create_manual_bill(
        client,
        auth_headers,
        client_id=client_id,
        case_id=case_id,
    )

    linked_payment_response = client.post(
        "/api/v1/payments",
        json={
            "bill_id": bill["id"],
            "amount": "680.00",
            "pay_no": f"PBL-PAY-{uuid4().hex[:8]}",
            "pay_date": "2026-05-10",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert linked_payment_response.status_code == 201, linked_payment_response.text
    linked_payment = linked_payment_response.json()
    assert linked_payment["client_id"] == client_id
    assert linked_payment["bill_id"] == bill["id"]

    unrelated_payment_response = client.post(
        "/api/v1/payments",
        json={
            "client_id": client_id,
            "amount": "100.00",
            "pay_no": f"PBL-UNRELATED-{uuid4().hex[:8]}",
            "pay_date": "2026-05-10",
            "currency": "CNY",
        },
        headers=auth_headers,
    )
    assert unrelated_payment_response.status_code == 201, unrelated_payment_response.text

    payment_list_response = client.get(
        "/api/v1/payments",
        params={"bill_id": bill["id"]},
        headers=auth_headers,
    )
    assert payment_list_response.status_code == 200, payment_list_response.text
    payment_list = payment_list_response.json()
    assert payment_list["total"] == 1
    assert payment_list["items"][0]["id"] == linked_payment["id"]
    assert payment_list["items"][0]["bill_id"] == bill["id"]

    payment_detail_response = client.get(
        f"/api/v1/payments/{linked_payment['id']}",
        headers=auth_headers,
    )
    assert payment_detail_response.status_code == 200, payment_detail_response.text
    payment_line = payment_detail_response.json()["payment_lines"][0]
    assert payment_line["case_id"] == case_id

    offset_response = client.post(
        "/api/v1/offsets",
        json={
            "payment_line_id": payment_line["id"],
            "bill_id": bill["id"],
            "offset_amt": "680.00",
            "offset_date": "2026-05-10",
        },
        headers=auth_headers,
    )
    assert offset_response.status_code == 201, offset_response.text
    assert offset_response.json()["bill_id"] == bill["id"]
