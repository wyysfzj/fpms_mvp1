from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _create_client(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    name_cn: str,
    client_type: str = "CLIENT",
) -> str:
    resp = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASEFLD-{uuid4().hex[:8]}",
            "name_cn": name_cn,
            "client_type": client_type,
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_client_address(
    client: TestClient, auth_headers: dict[str, str], client_id: str, *, address_type: str
) -> str:
    resp = client.post(
        f"/api/v1/clients/{client_id}/addresses",
        json={
            "address_type": address_type,
            "address_line1": f"{address_type} 地址",
            "country_code": "CN",
            "is_default": False,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_create_case_roundtrips_missing_fields_into_detail(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="案卷字段客户")
    foreign_agent_id = _create_client(
        client, auth_headers, name_cn="外方代理所", client_type="AGENT"
    )
    doc_address_id = _create_client_address(client, auth_headers, client_id, address_type="MAILING")
    bill_address_id = _create_client_address(
        client, auth_headers, client_id, address_type="BILLING"
    )

    payload = {
        "case_no": f"CASEFLD-{uuid4().hex[:8]}",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_OUTBOUND",
        "client_id": client_id,
        "foreign_agent_id": foreign_agent_id,
        "title_cn": "案卷字段补齐测试",
        "recv_date": "2026-03-01",
        "draw_pages": 8,
        "claim_pages": 4,
        "manuscript_words": 12000,
        "discount_rate": "0.7500",
        "no_power": True,
        "no_prio_text": False,
        "require_hk": True,
        "from_country": "CN",
        "to_country": "US",
        "doc_address_id": doc_address_id,
        "bill_address_id": bill_address_id,
        "issue_date": "2026-06-01",
        "cert_no": "CERT-001",
        "first_annuity_year": 1,
    }
    create_resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201, create_resp.text
    data = create_resp.json()
    case_id = data["id"]

    for key, expected in {
        "recv_date": "2026-03-01",
        "draw_pages": 8,
        "claim_pages": 4,
        "manuscript_words": 12000,
        "discount_rate": "0.7500",
        "no_power": True,
        "no_prio_text": False,
        "require_hk": True,
        "from_country": "CN",
        "to_country": "US",
        "doc_address_id": doc_address_id,
        "bill_address_id": bill_address_id,
        "issue_date": "2026-06-01",
        "cert_no": "CERT-001",
        "first_annuity_year": 1,
    }.items():
        assert data[key] == expected

    detail_resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
    assert detail_resp.status_code == 200, detail_resp.text
    detail = detail_resp.json()
    assert detail["to_country"] == "US"
    assert detail["doc_address_id"] == doc_address_id
    assert detail["bill_address_id"] == bill_address_id
    assert detail["issue_date"] == "2026-06-01"
    assert detail["cert_no"] == "CERT-001"


def test_put_case_updates_missing_fields(client: TestClient, auth_headers: dict[str, str]) -> None:
    client_id = _create_client(client, auth_headers, name_cn="更新客户")
    doc_address_id = _create_client_address(client, auth_headers, client_id, address_type="MAILING")
    bill_address_id = _create_client_address(
        client, auth_headers, client_id, address_type="BILLING"
    )
    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CASEFLD-UP-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "更新前案件",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={
            "recv_date": "2026-01-02",
            "draw_pages": 5,
            "claim_pages": 3,
            "manuscript_words": 9000,
            "discount_rate": "0.6000",
            "no_power": False,
            "no_prio_text": True,
            "require_hk": False,
            "from_country": "CN",
            "to_country": "JP",
            "doc_address_id": doc_address_id,
            "bill_address_id": bill_address_id,
            "issue_date": "2026-05-01",
            "cert_no": "CERT-UPDATE-001",
            "first_annuity_year": 2,
        },
        headers=auth_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    updated = update_resp.json()
    assert updated["manuscript_words"] == 9000
    assert updated["discount_rate"] == "0.6000"
    assert updated["to_country"] == "JP"
    assert updated["first_annuity_year"] == 2


def test_create_foreign_case_requires_to_country(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="涉外客户")
    foreign_agent_id = _create_client(
        client, auth_headers, name_cn="涉外代理所", client_type="AGENT"
    )

    resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CASEFLD-ERR-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_OUTBOUND",
            "client_id": client_id,
            "foreign_agent_id": foreign_agent_id,
            "title_cn": "缺少进入国家",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400, resp.text
    assert "to_country" in resp.text


def test_put_case_rejects_address_owned_by_other_client(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    owner_client_id = _create_client(client, auth_headers, name_cn="主客户")
    other_client_id = _create_client(client, auth_headers, name_cn="其他客户")
    other_address_id = _create_client_address(
        client, auth_headers, other_client_id, address_type="MAILING"
    )
    case_resp = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CASEFLD-ADDR-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": owner_client_id,
            "title_cn": "地址归属测试",
        },
        headers=auth_headers,
    )
    assert case_resp.status_code == 201, case_resp.text
    case_id = case_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/cases/{case_id}",
        json={"doc_address_id": other_address_id},
        headers=auth_headers,
    )
    assert update_resp.status_code == 400, update_resp.text
    assert "address" in update_resp.text.lower()
