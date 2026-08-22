from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.cases.models import Case
from app.modules.masterdata.applicants.models import Applicant
from tests.test_v8_batch_filing_lifecycle_adapter import (
    _seed_filing_evidence_for_case,
    _start_filing_preparation,
)


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name_cn: str) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASEBF-ACT-{uuid4().hex[:8]}",
            "name_cn": name_cn,
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _seed_applicant(session_factory, *, name_cn: str = "批件递交申请人") -> str:
    applicant_id = str(uuid4())
    with session_factory() as db:
        db.add(
            Applicant(
                id=applicant_id,
                code=f"CASEBF-ACT-AP-{uuid4().hex[:8]}",
                name_cn=f"{name_cn}-{uuid4().hex[:8]}",
                applicant_type="ENTITY",
                is_active=True,
            )
        )
        db.commit()
    return applicant_id


def _create_required_documents(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
) -> None:
    for title in ("发明专利请求书", "说明书", "权利要求书", "摘要"):
        response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            json={
                "case_id": case_id,
                "doc_template_id": None,
                "doc_type": "CLIENT_IN",
                "direction": "IN",
                "doc_date": "2026-03-01",
                "title": title,
            },
        )
        assert response.status_code == 201, response.text


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    applicant_id: str,
    case_no_prefix: str,
    recv_date: str,
    has_exam_request: bool | None = None,
) -> dict:
    payload = {
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
                "name_cn": "批件递交申请人",
            }
        ],
    }
    if has_exam_request is not None:
        payload["has_exam_request"] = has_exam_request
    response = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    case_data = response.json()
    _create_required_documents(client, auth_headers, case_id=case_data["id"])
    return case_data


def test_batch_filing_action_updates_status_submitted_date_and_exam_request(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批件递交动作客户")
    applicant_id = _seed_applicant(session_factory)
    case_a = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-A1",
        recv_date="2026-03-01",
    )
    case_b = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-A2",
        recv_date="2026-03-05",
        has_exam_request=False,
    )
    _start_filing_preparation(client, auth_headers, case_id=case_a["id"])
    with session_factory() as db:
        _seed_filing_evidence_for_case(db, case_id=case_a["id"], marker="action-a")
    _start_filing_preparation(client, auth_headers, case_id=case_b["id"])
    with session_factory() as db:
        _seed_filing_evidence_for_case(db, case_id=case_b["id"], marker="action-b")

    response = client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": [case_a["id"], case_b["id"]],
            "submitted_date": "2026-03-10",
            "apply_exam_now": True,
            "generate_list": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success_count"] == 2
    assert payload["failure_count"] == 0
    assert set(payload["updated_case_ids"]) == {case_a["id"], case_b["id"]}

    with session_factory() as session:
        refreshed_cases = (
            session.query(Case).filter(Case.id.in_([case_a["id"], case_b["id"]])).all()
        )
        assert len(refreshed_cases) == 2
        for refreshed_case in refreshed_cases:
            assert refreshed_case.status == "WAITING_RECEIPT"
            assert str(refreshed_case.submitted_date) == "2026-03-10"
            assert refreshed_case.has_exam_request is True


def test_batch_filing_action_rejects_submitted_date_before_recv_date(
    client: TestClient, auth_headers: dict[str, str], session_factory
) -> None:
    client_id = _create_client(client, auth_headers, name_cn="批件递交校验客户")
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
        case_no_prefix="CASEBF-V1",
        recv_date="2026-03-20",
    )

    response = client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": [case_data["id"]],
            "submitted_date": "2026-03-10",
            "apply_exam_now": False,
            "generate_list": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert "submitted_date" in response.text
