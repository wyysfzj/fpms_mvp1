from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.fees.models import FeeDraft, T_GrantFeeTask
from app.modules.tasks.models import Task
from app.modules.tasks.task_generation_service import TaskGenerationService


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"ADDGAP-ATOMIC-{uuid4().hex[:8].upper()}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": "文档创建事务原子性测试案件",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _get_grant_notice_template(client: TestClient, auth_headers: dict[str, str]) -> dict:
    response = client.get(
        "/api/v1/doc-templates",
        headers=auth_headers,
        params={"q": "GRANT_NOTICE", "page_size": 100},
    )
    assert response.status_code == 200, response.text
    matches = [item for item in response.json()["items"] if item["code"] == "GRANT_NOTICE"]
    assert len(matches) == 1
    return matches[0]


def test_document_create_rolls_back_record_and_required_side_effects(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    case_data = _create_case(client, auth_headers)
    template = _get_grant_notice_template(client, auth_headers)
    ref_no = f"ADDGAP-ATOMIC-REF-{uuid4().hex[:8].upper()}"
    partial_task_title = f"ADDGAP-ATOMIC-TASK-{uuid4().hex[:8].upper()}"

    def fail_after_partial_task(
        _service: TaskGenerationService,
        db: Session,
        document: Document,
    ) -> list[Task]:
        db.add(
            Task(
                id=str(uuid4()),
                case_id=document.case_id,
                document_id=document.id,
                title=partial_task_title,
                status="OPEN",
            )
        )
        db.flush()
        raise RuntimeError("forced task generation failure")

    monkeypatch.setattr(
        TaskGenerationService,
        "generate_from_document",
        fail_after_partial_task,
    )

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        json={
            "case_id": case_data["id"],
            "doc_template_id": template["id"],
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-07-10",
            "title": "授权通知书事务回滚测试",
            "ref_no": ref_no,
            "official_due_date": "2026-10-08",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )

    assert response.status_code == 409, response.text
    assert "forced task generation failure" in response.text

    with session_factory() as db:
        document = db.execute(
            select(Document).where(Document.ref_no == ref_no)
        ).scalar_one_or_none()
        partial_task = db.execute(
            select(Task).where(Task.title == partial_task_title)
        ).scalar_one_or_none()
        grant_task = db.execute(
            select(T_GrantFeeTask).where(T_GrantFeeTask.case_id == case_data["id"])
        ).scalar_one_or_none()
        fee_draft = db.execute(
            select(FeeDraft).where(FeeDraft.case_id == case_data["id"])
        ).scalar_one_or_none()
        case = db.execute(select(Case).where(Case.id == case_data["id"])).scalar_one()

        assert document is None
        assert partial_task is None
        assert grant_task is None
        assert fee_draft is None
        assert case.status == "NOT_FILED"
