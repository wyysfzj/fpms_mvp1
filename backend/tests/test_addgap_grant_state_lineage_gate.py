from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.cases.models import Case
from app.modules.documents.models import Document
from app.modules.fees.models import T_GrantFeeTask

STATE_BASE = "/api/v1/grant-fee-tasks"


def _new_task(
    *,
    case_id: str,
    source_document_id: str | None = None,
    deadline_source: str | None = None,
    deadline_confirmed_at: datetime | None = None,
    superseded_by_task_id: str | None = None,
) -> T_GrantFeeTask:
    return T_GrantFeeTask(
        case_id=case_id,
        due_date=date(2026, 7, 31),
        source_document_id=source_document_id,
        deadline_source=deadline_source,
        deadline_confirmed_at=deadline_confirmed_at,
        superseded_by_task_id=superseded_by_task_id,
        gov_fee_amt=0,
        service_fee_amt=0,
        currency="CNY",
        client_instruction="NONE",
        notify_count=0,
        draft_generated=False,
        notice_sent=False,
        is_overdue=False,
        remark=None,
    )


def test_grant_state_lineage_gates_actions_without_changing_workflow_state(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    confirmed_at = datetime(2026, 4, 2, 9, 30)

    with session_factory() as db:
        case = Case(
            case_no=f"GFSG-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="授权费状态 lineage gate 测试",
        )
        db.add(case)
        db.flush()

        documents = [
            Document(
                case_id=case.id,
                doc_type="OFFICIAL",
                direction="IN",
                doc_date=date(2026, 4, day),
                title=f"授权通知书-{day}",
            )
            for day in (1, 2, 3)
        ]
        db.add_all(documents)
        db.flush()

        replacement = _new_task(
            case_id=case.id,
            source_document_id=documents[2].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
        )
        db.add(replacement)
        db.flush()

        legacy = _new_task(case_id=case.id)
        confirmed = _new_task(
            case_id=case.id,
            source_document_id=documents[0].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
        )
        superseded = _new_task(
            case_id=case.id,
            source_document_id=documents[1].id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=confirmed_at,
            superseded_by_task_id=replacement.id,
        )
        db.add_all([legacy, confirmed, superseded])
        db.commit()

        legacy_id = legacy.id
        confirmed_id = confirmed.id
        superseded_id = superseded.id
        confirmed_source_id = documents[0].id
        superseded_source_id = documents[1].id

    expected_get = {
        legacy_id: ("OPEN", "LEGACY_UNVERIFIED", None, None, None, []),
        confirmed_id: (
            "OPEN",
            "CONFIRMED",
            confirmed_source_id,
            "MANUAL_OFFICIAL_NOTICE",
            "2026-04-02T09:30:00",
            ["mark_waiting_client"],
        ),
        superseded_id: (
            "OPEN",
            "SUPERSEDED",
            superseded_source_id,
            "MANUAL_OFFICIAL_NOTICE",
            "2026-04-02T09:30:00",
            [],
        ),
    }

    for task_id, expected_projection in expected_get.items():
        response = client.get(f"{STATE_BASE}/{task_id}/state", headers=auth_headers)
        assert response.status_code == 200, response.text
        payload = response.json()
        assert (
            payload["state"],
            payload["lineage_status"],
            payload["source_document_id"],
            payload["deadline_source"],
            payload["deadline_confirmed_at"],
            payload["allowed_actions"],
        ) == expected_projection

    for task_id, lineage_status in (
        (legacy_id, "LEGACY_UNVERIFIED"),
        (superseded_id, "SUPERSEDED"),
    ):
        blocked = client.put(
            f"{STATE_BASE}/{task_id}/state",
            headers=auth_headers,
            json={"action": "mark_waiting_client"},
        )
        assert blocked.status_code == 409, blocked.text
        assert blocked.json()["error"] == {
            "code": "GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE",
            "message": "Grant fee task lineage is not actionable",
            "details": {"task_id": task_id, "lineage_status": lineage_status},
        }

    invalid = client.put(
        f"{STATE_BASE}/{confirmed_id}/state",
        headers=auth_headers,
        json={"action": "mark_done"},
    )
    assert invalid.status_code == 400, invalid.text
    assert invalid.json()["error"]["code"] == "GRANT_FEE_STATE_TRANSITION_INVALID"

    advanced = client.put(
        f"{STATE_BASE}/{confirmed_id}/state",
        headers=auth_headers,
        json={"action": "mark_waiting_client"},
    )
    assert advanced.status_code == 200, advanced.text
    assert (
        advanced.json()["state"],
        advanced.json()["lineage_status"],
        advanced.json()["allowed_actions"],
    ) == (
        "WAITING_CLIENT",
        "CONFIRMED",
        ["record_pay_instruction", "record_abandon_instruction"],
    )

    with session_factory() as db:
        tasks = {
            task.id: task
            for task in db.execute(
                select(T_GrantFeeTask).where(
                    T_GrantFeeTask.id.in_([legacy_id, confirmed_id, superseded_id])
                )
            ).scalars()
        }

    for blocked_id in (legacy_id, superseded_id):
        assert tasks[blocked_id].client_instruction == "NONE"
        assert tasks[blocked_id].notify_count == 0
        assert tasks[blocked_id].notice_sent is False
        assert tasks[blocked_id].draft_generated is False

    assert tasks[confirmed_id].client_instruction == "NONE"
    assert tasks[confirmed_id].notify_count == 1
    assert tasks[confirmed_id].notice_sent is True
    assert tasks[confirmed_id].draft_generated is False
