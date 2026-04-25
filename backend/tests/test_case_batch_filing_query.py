from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.cases.models import Case
from app.modules.masterdata.applicants.models import Applicant


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_cn: str) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASEBF-{uuid4().hex[:8]}",
            "name_cn": name_cn,
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory, *, name_cn: str = "批件递交候选申请人") -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"CASEBF-AP-{uuid4().hex[:8]}",
                name_cn=f"{name_cn}-{uuid4().hex[:8]}",
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
    status: str,
    recv_date: str,
    case_type: str = "NORMAL",
    flow_dir: str = "CN_DOMESTIC",
    patent_category: str = "INV",
    primary_agent_id: str | None = None,
    has_exam_request: bool | None = None,
) -> dict:
    payload = {
        "case_no": f"{case_no_prefix}-{uuid4().hex[:8]}",
        "case_type": case_type,
        "patent_category": patent_category,
        "flow_dir": flow_dir,
        "client_id": client_id,
        "title_cn": f"{case_no_prefix} 标题",
        "status": status,
        "recv_date": recv_date,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": "批件递交候选申请人",
            }
        ],
    }
    if primary_agent_id is not None:
        payload["primary_agent_id"] = primary_agent_id
    if has_exam_request is not None:
        payload["has_exam_request"] = has_exam_request
    response = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_batch_filing_query_returns_not_filed_candidates_with_minimal_fields(
    client: TestClient, auth_headers: dict[str, str], session_factory
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批件递交客户")
    applicant_id = _seed_applicant(session_factory)
    _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-Q1",
        status="NOT_FILED",
        recv_date="2026-03-01",
        flow_dir="CN_DOMESTIC",
        patent_category="INV",
        has_exam_request=False,
    )
    non_candidate_case = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-Q2",
        status="NOT_FILED",
        recv_date="2026-03-02",
        flow_dir="CN_DOMESTIC",
        patent_category="INV",
        has_exam_request=True,
    )
    with session_factory() as db:
        case = db.query(Case).filter(Case.id == non_candidate_case["id"]).one()
        case.status = "WAITING_RECEIPT"
        case.app_no = f"CASEBFQ2{uuid4().hex[:6].upper()}"
        case.filing_date = case.recv_date
        db.commit()

    response = client.get(
        "/api/v1/cases/batch-filing/candidates",
        params={
            "client_id": client_id,
            "case_type": "NORMAL",
            "flow_dir": "CN_DOMESTIC",
            "status": "NOT_FILED",
            "recv_date_from": "2026-03-01",
            "recv_date_to": "2026-03-31",
            "patent_category": "INV",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1

    item = payload["items"][0]
    assert item["status"] == "NOT_FILED"
    assert item["client_name"] == "批件递交客户"
    assert item["flow_dir"] == "CN_DOMESTIC"
    assert item["recv_date"] == "2026-03-01"
    assert item["has_exam_request"] is False
    assert set(item.keys()) == {
        "id",
        "case_no",
        "title_cn",
        "client_name",
        "case_type",
        "patent_category",
        "flow_dir",
        "recv_date",
        "status",
        "has_exam_request",
    }
