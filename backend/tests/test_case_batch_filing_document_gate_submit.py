from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.masterdata.applicants.models import Applicant
from app.modules.tasks.models import Task


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        json={
            "client_code": f"CASEBF-SUBGATE-{uuid4().hex[:8]}",
            "name_cn": "批量递交硬阻止客户",
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
                code=f"CASEBF-SUBGATE-AP-{uuid4().hex[:8]}",
                name_cn=f"批量递交硬阻止申请人-{uuid4().hex[:8]}",
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
) -> dict:
    response = client.post(
        "/api/v1/cases",
        json={
            "case_no": f"CASEBF-SUBGATE-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": "批量递交硬阻止测试案件",
            "status": "NOT_FILED",
            "recv_date": "2026-04-05",
            "no_power": True,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": "批量递交硬阻止申请人",
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_batch_filing_submit_rejects_hard_block_case_without_mutations(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory,
) -> None:
    client_id = _create_client(client, auth_headers)
    applicant_id = _seed_applicant(session_factory)
    case_data = _create_case(
        client,
        auth_headers,
        client_id=client_id,
        applicant_id=applicant_id,
    )

    response = client.post(
        "/api/v1/cases/batch-filing/submit",
        json={
            "selected_case_ids": [case_data["id"]],
            "submitted_date": "2026-04-06",
            "apply_exam_now": False,
            "generate_list": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "CASE_BATCH_FILING_MATERIAL_GATE_BLOCKED"

    with session_factory() as db:
        refreshed_case = db.query(Case).filter(Case.id == case_data["id"]).one()
        assert refreshed_case.status == "NOT_FILED"
        assert refreshed_case.submitted_date is None
        assert (
            db.query(Document)
            .filter(Document.case_id == case_data["id"], Document.title.like("%批量递交清单%"))
            .all()
            == []
        )
        assert db.query(Task).filter(Task.case_id == case_data["id"]).all() == []
