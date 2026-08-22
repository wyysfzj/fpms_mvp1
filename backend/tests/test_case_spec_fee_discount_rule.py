from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant
from tests.test_v8_case_create_fee_reduction import _seed_approval_record


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"A9-CL-{uuid4().hex[:8]}",
            "name_cn": "A9 规格折扣客户",
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
    suffix = uuid4().hex[:8]
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"A9-AP-{suffix}",
                name_cn=f"A9 申请人 {suffix}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _payload(
    *,
    client_id: str,
    applicant_id: str,
    suffix: str,
    spec_pages: int = 0,
    draw_pages: int = 0,
    claim_count: int = 0,
    claim_pages: int = 0,
    manuscript_words: int = 0,
    discount_rate: str = "0",
    fee_reduction: str = "0",
) -> dict:
    return {
        "case_no": f"A9-{suffix}-{uuid4().hex[:8]}",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client_id,
        "title_cn": "A9 规格费减折扣",
        "recv_date": "2026-03-01",
        "spec_pages": spec_pages,
        "draw_pages": draw_pages,
        "claim_count": claim_count,
        "claim_pages": claim_pages,
        "manuscript_words": manuscript_words,
        "discount_rate": discount_rate,
        "fee_reduction": fee_reduction,
        "applicant_kind": "ENTITY",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": "A9 申请人",
            }
        ],
    }


def test_a9_accepts_zero_and_safe_large_spec_discount_boundaries(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    _seed_approval_record(session_factory, applicant_ids=(applicant_id,), ratio="0.85")

    zero_response = client.post(
        "/api/v1/cases",
        json=_payload(client_id=client_id, applicant_id=applicant_id, suffix="ZERO"),
        headers=auth_headers,
    )
    assert zero_response.status_code == 201, zero_response.text
    zero_detail = client.get(
        f"/api/v1/cases/{zero_response.json()['id']}", headers=auth_headers
    ).json()
    assert zero_detail["spec_pages"] == 0
    assert zero_detail["draw_pages"] == 0
    assert zero_detail["claim_count"] == 0
    assert zero_detail["claim_pages"] == 0
    assert zero_detail["manuscript_words"] == 0
    assert zero_detail["discount_rate"] == "0.0000"
    assert zero_detail["fee_reduction"] == "0"

    maximum_response = client.post(
        "/api/v1/cases",
        json=_payload(
            client_id=client_id,
            applicant_id=applicant_id,
            suffix="MAXIMUM",
            spec_pages=999,
            draw_pages=888,
            claim_count=777,
            claim_pages=666,
            manuscript_words=123456,
            discount_rate="1",
            fee_reduction="0.85",
        ),
        headers=auth_headers,
    )
    assert maximum_response.status_code == 201, maximum_response.text
    maximum_detail = client.get(
        f"/api/v1/cases/{maximum_response.json()['id']}", headers=auth_headers
    ).json()
    assert maximum_detail["spec_pages"] == 999
    assert maximum_detail["draw_pages"] == 888
    assert maximum_detail["claim_count"] == 777
    assert maximum_detail["claim_pages"] == 666
    assert maximum_detail["manuscript_words"] == 123456
    assert maximum_detail["discount_rate"] == "1.0000"
    assert maximum_detail["fee_reduction"] == "0.85"


def test_a9_rejects_negative_spec_fields_and_out_of_range_discount_rate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)

    negative_response = client.post(
        "/api/v1/cases",
        json=_payload(
            client_id=client_id,
            applicant_id=applicant_id,
            suffix="NEG",
            spec_pages=-1,
        ),
        headers=auth_headers,
    )
    assert negative_response.status_code == 422, negative_response.text

    low_discount_response = client.post(
        "/api/v1/cases",
        json=_payload(
            client_id=client_id,
            applicant_id=applicant_id,
            suffix="LOW",
            discount_rate="-0.01",
        ),
        headers=auth_headers,
    )
    assert low_discount_response.status_code == 422, low_discount_response.text

    high_discount_response = client.post(
        "/api/v1/cases",
        json=_payload(
            client_id=client_id,
            applicant_id=applicant_id,
            suffix="HIGH",
            discount_rate="1.01",
        ),
        headers=auth_headers,
    )
    assert high_discount_response.status_code == 422, high_discount_response.text
