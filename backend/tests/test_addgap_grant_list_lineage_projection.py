from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.fees.models import T_GrantFeeTask

WORKLIST_BASE = "/api/v1/grant-fee-tasks/list"


def _new_task(
    *,
    case_id: str,
    due_date: date,
    source_document_id: str | None = None,
    deadline_source: str | None = None,
    deadline_confirmed_at: datetime | None = None,
    superseded_by_task_id: str | None = None,
    client_instruction: str = "NONE",
    notify_count: int = 0,
    draft_generated: bool = False,
    notice_sent: bool = False,
) -> T_GrantFeeTask:
    return T_GrantFeeTask(
        case_id=case_id,
        due_date=due_date,
        source_document_id=source_document_id,
        deadline_source=deadline_source,
        deadline_confirmed_at=deadline_confirmed_at,
        superseded_by_task_id=superseded_by_task_id,
        gov_fee_amt=0,
        service_fee_amt=0,
        currency="CNY",
        client_instruction=client_instruction,
        notify_count=notify_count,
        draft_generated=draft_generated,
        notice_sent=notice_sent,
        is_overdue=False,
        remark=None,
    )


def test_grant_list_projects_lineage_separately_from_workflow_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    confirmed_at = datetime(2026, 4, 2, 9, 30)

    with session_factory() as db:
        case = Case(
            case_no=f"GFLP-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="授权费 lineage 投影测试",
        )
        db.add(case)
        db.flush()

        source_documents = [
            Document(
                case_id=case.id,
                doc_type="OFFICIAL",
                direction="IN",
                doc_date=date(2026, 4, day),
                title=f"授权通知书-{day}",
            )
            for day in (1, 2, 3)
        ]
        db.add_all(source_documents)
        db.flush()

        replacement = _new_task(
            case_id=case.id,
            due_date=date(2026, 7, 3),
            source_document_id=source_documents[2].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
            draft_generated=True,
        )
        db.add(replacement)
        db.flush()

        legacy = _new_task(case_id=case.id, due_date=date(2026, 7, 1))
        confirmed = _new_task(
            case_id=case.id,
            due_date=date(2026, 7, 2),
            source_document_id=source_documents[0].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
            notify_count=1,
            notice_sent=True,
        )
        superseded = _new_task(
            case_id=case.id,
            due_date=date(2026, 7, 4),
            source_document_id=source_documents[1].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
            superseded_by_task_id=replacement.id,
            client_instruction="PAY",
        )
        db.add_all([legacy, confirmed, superseded])
        db.commit()

        case_id = case.id
        expected = {
            legacy.id: ("OPEN", "LEGACY_UNVERIFIED", None, None, None),
            confirmed.id: (
                "WAITING_CLIENT",
                "CONFIRMED",
                source_documents[0].id,
                "MANUAL_OFFICIAL_NOTICE",
                "2026-04-02T09:30:00",
            ),
            replacement.id: (
                "DRAFT_GENERATED",
                "CONFIRMED",
                source_documents[2].id,
                "MANUAL_OFFICIAL_NOTICE",
                "2026-04-02T09:30:00",
            ),
            superseded.id: (
                "READY_TO_DRAFT",
                "SUPERSEDED",
                source_documents[1].id,
                "MANUAL_OFFICIAL_NOTICE",
                "2026-04-02T09:30:00",
            ),
        }

    response = client.get(
        WORKLIST_BASE,
        params={"case_id": case_id, "page_size": 100},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 4
    assert payload["page"] == 1
    assert payload["page_size"] == 100

    items = {item["task_id"]: item for item in payload["items"]}
    assert set(items) == set(expected)
    assert {item["lineage_status"] for item in items.values()} == {
        "CONFIRMED",
        "LEGACY_UNVERIFIED",
        "SUPERSEDED",
    }

    for task_id, expected_projection in expected.items():
        item = items[task_id]
        assert (
            item["status"],
            item["lineage_status"],
            item["source_document_id"],
            item["deadline_source"],
            item["deadline_confirmed_at"],
        ) == expected_projection
