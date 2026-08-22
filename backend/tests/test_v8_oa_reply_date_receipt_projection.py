from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from test_addgap_oa_out_keeps_task_open import _case_tasks, _template
from test_addgap_oa_receipt_archive_event import _archive, _create_archive_fixture

from app.modules.cases.models import CaseActivityEvent
from app.modules.documents.models import Document
from app.modules.official_workflows.models import OfficialWorkPackageReceipt


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    suffix = uuid4().hex[:8].upper()
    applicant_response = client.post(
        "/api/v1/applicants",
        headers=auth_headers,
        json={
            "code": f"OA-PROJECTION-AP-{suffix}",
            "name_cn": f"OA答复投影测试申请人-{suffix}",
            "applicant_type": "ENTITY",
            "is_active": True,
        },
    )
    assert applicant_response.status_code == 201, applicant_response.text
    applicant = applicant_response.json()
    case_response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"OA-PROJECTION-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "title_cn": "OA答复投影测试案件",
            "fee_reduction": "0",
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant["id"],
                    "name_cn": applicant["name_cn"],
                }
            ],
        },
    )
    assert case_response.status_code == 201, case_response.text
    return case_response.json()


def test_oa_out_leaves_reply_date_for_receipt_projection(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    case = _create_case(client, auth_headers)
    oa_in = _template(client, auth_headers, "OA_IN")
    incoming_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": oa_in["id"],
            "direction": "IN",
            "doc_date": "2026-01-15",
            "title": "第一次审查意见通知书",
            "official_due_date": "2026-04-15",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert incoming_response.status_code == 201, incoming_response.text
    incoming = incoming_response.json()

    reply_response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case["id"],
            "doc_template_id": _template(client, auth_headers, "OA_OUT")["id"],
            "direction": "OUT",
            "doc_date": "2026-03-01",
            "title": "第一次审查意见答复文件",
            "reply_to_id": incoming["id"],
        },
    )

    assert reply_response.status_code == 201, reply_response.text
    source_response = client.get(
        f"/api/v1/documents/{incoming['id']}",
        headers=auth_headers,
    )
    assert source_response.status_code == 200, source_response.text
    assert source_response.json()["reply_date"] is None
    source_tasks = [
        task
        for task in _case_tasks(client, auth_headers, case["id"])
        if task["document_id"] == incoming["id"]
    ]
    assert len(source_tasks) == 1
    assert source_tasks[0]["status"] == "OPEN"


def test_valid_owned_receipt_sets_reply_date_once(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory, lifecycle_ready=True)
    received_at = datetime(2026, 7, 12, 10, 30)
    with session_factory() as db:
        receipt = db.get(OfficialWorkPackageReceipt, ids["receipt_id"])
        assert receipt is not None
        receipt.received_at = received_at
        db.commit()

    first = _archive(client, auth_headers, ids["package_id"])
    repeated = _archive(client, auth_headers, ids["package_id"])

    assert first.status_code == 200, first.text
    assert repeated.status_code == 200, repeated.text
    with session_factory() as db:
        source = db.get(Document, ids["source_document_id"])
        assert source is not None
        assert source.reply_date == received_at.date()
        activities = db.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == ids["case_id"],
                CaseActivityEvent.activity_type == "OA_RECEIPT_ARCHIVED",
            )
        ).all()
        assert len(activities) == 1
