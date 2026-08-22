from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant
from tests.test_v8_case_create_fee_reduction import _seed_approval_record


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"A2-CL-{uuid4().hex[:8]}",
            "name_cn": "A2 完整字段客户",
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
        json={"address_type": address_type, "address_line1": f"{address_type} 地址"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory, *, applicant_type: str, label: str) -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"A2-AP-{label}-{uuid4().hex[:8]}",
                name_cn=f"A2 申请人 {label}",
                applicant_type=applicant_type,
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def test_a2_full_fields_mvp_surface_persists_and_exposes_detail(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    doc_address_id = _create_address(client, auth_headers, client_id, "MAILING")
    bill_address_id = _create_address(client, auth_headers, client_id, "BILLING")
    first_applicant_id = _seed_applicant(session_factory, applicant_type="ENTITY", label="ENTITY")
    second_applicant_id = _seed_applicant(session_factory, applicant_type="INDIVIDUAL", label="IND")
    _seed_approval_record(
        session_factory,
        applicant_ids=(first_applicant_id, second_applicant_id),
        ratio="0.85",
    )
    case_no = f"A2-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": case_no,
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "doc_address_id": doc_address_id,
            "bill_address_id": bill_address_id,
            "title_cn": "A2 完整字段中文标题",
            "title_en": "A2 Full Field Title",
            "recv_date": "2026-03-01",
            "spec_pages": 10,
            "draw_pages": 2,
            "claim_count": 12,
            "claim_pages": 4,
            "manuscript_words": 12345,
            "fee_reduction": "0.85",
            "discount_rate": "0.8000",
            "applicant_kind": "ENTITY",
            "no_power": True,
            "no_prio_text": False,
            "require_hk": True,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": first_applicant_id,
                    "name_cn": "A2 第一申请人",
                },
                {
                    "seq": 2,
                    "is_first": False,
                    "applicant_id": second_applicant_id,
                    "name_cn": "A2 第二申请人",
                },
            ],
            "inventors": [{"seq": 1, "name_cn": "A2 发明人"}],
            "priorities": [
                {"seq": 1, "country_code": "CN", "prio_no": "P1", "prio_date": "2026-02-10"},
                {"seq": 2, "country_code": "US", "prio_no": "P2", "prio_date": "2026-01-20"},
            ],
            "bio_deposits": [
                {
                    "seq": 1,
                    "deposit_no": "BIO-001",
                    "deposit_unit_name": "CGMCC",
                    "deposit_date": "2026-01-15",
                    "name": "A2 菌种",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    case_id = response.json()["id"]

    detail_response = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["case_no"] == case_no
    assert detail["doc_address_id"] == doc_address_id
    assert detail["bill_address_id"] == bill_address_id
    assert detail["spec_pages"] == 10
    assert detail["draw_pages"] == 2
    assert detail["claim_count"] == 12
    assert detail["claim_pages"] == 4
    assert detail["manuscript_words"] == 12345
    assert detail["fee_reduction"] == "0.85"
    assert detail["discount_rate"] == "0.8000"
    assert detail["no_power"] is True
    assert detail["no_prio_text"] is False
    assert detail["require_hk"] is True
    assert len(detail["applicants"]) == 2
    assert len(detail["inventors"]) == 1
    assert len(detail["priorities"]) == 2
    assert len(detail["bio_deposits"]) == 1
    earliest_priority = min(row["prio_date"] for row in detail["priorities"])
    assert earliest_priority == "2026-01-20"
    assert detail["created_at"]
    assert detail["updated_at"]

    search_response = client.get(
        "/api/v1/cases",
        params={"case_no": case_no, "page": 1, "page_size": 20},
        headers=auth_headers,
    )
    assert search_response.status_code == 200, search_response.text
    assert any(item["id"] == case_id for item in search_response.json()["items"])
