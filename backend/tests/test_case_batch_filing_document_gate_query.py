from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASEBF-GATE-{uuid4().hex[:8]}",
            "name_cn": "批量递交门禁客户",
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
                code=f"CASEBF-GATE-AP-{uuid4().hex[:8]}",
                name_cn=f"批量递交门禁申请人-{uuid4().hex[:8]}",
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
    case_no_prefix: str,
    recv_date: str,
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"{case_no_prefix}-{uuid4().hex[:8]}",
            "fee_reduction": "0",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": f"{case_no_prefix} 标题",
            "recv_date": recv_date,
            "no_power": True,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "批量递交门禁申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    title: str,
) -> None:
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": None,
            "doc_type": "CLIENT_IN",
            "direction": "IN",
            "doc_date": "2026-04-04",
            "title": title,
        },
    )
    assert response.status_code == 201, response.text


def test_batch_filing_candidates_include_final_material_gate(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    blocked_case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-GATE-BLOCK",
        recv_date="2026-04-01",
    )
    pass_case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-GATE-PASS",
        recv_date="2026-04-02",
    )
    for title in ("发明专利请求书", "说明书", "权利要求书", "摘要"):
        _create_document(client, auth_headers, case_id=pass_case["id"], title=title)

    response = client.get(
        "/api/v1/cases/batch-filing/candidates",
        params={
            "client_id": client_id,
            "status": "NOT_FILED",
            "page_size": 20,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    items_by_id = {item["id"]: item for item in response.json()["items"]}
    blocked_gate = items_by_id[blocked_case["id"]]["final_material_gate"]
    pass_gate = items_by_id[pass_case["id"]]["final_material_gate"]

    assert blocked_gate["conclusion"] == "BLOCKED"
    assert blocked_gate["hard_block"] is True
    assert blocked_gate["material_count"] == 0
    assert blocked_gate["execution_preview"][0]["kind"] == "BLOCK_SUBMIT"
    assert blocked_gate["execution_preview"][0]["enabled"] is False

    assert pass_gate["conclusion"] == "PASS"
    assert pass_gate["hard_block"] is False
    assert pass_gate["afterfill_audit_required"] is False
    assert pass_gate["material_count"] == 4
    assert pass_gate["missing_items"] == []
    assert [item["kind"] for item in pass_gate["execution_preview"]] == [
        "CASE_STATUS",
        "DOCUMENT",
        "TASK",
    ]
