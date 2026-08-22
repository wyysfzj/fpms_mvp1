from __future__ import annotations

import json
from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.documents.models import DocTemplate, Document
from app.modules.tasks.enums import TaskRemindBase
from app.modules.tasks.models import Task, TaskLog, TaskTemplate

DOCUMENT_BASE = "/api/v1/documents"


def _create_case(client: TestClient, auth_headers: dict[str, str]) -> str:
    suffix = uuid4().hex[:8].upper()
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"DDL-SYNC-{suffix}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": f"历史期限任务同步案件-{suffix}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _configure_oa_template(
    db,
    *,
    invalid_reminder_config: bool = False,
) -> tuple[DocTemplate, TaskTemplate]:
    document_template = db.execute(
        select(DocTemplate).where(DocTemplate.code == "OA_IN")
    ).scalar_one()
    task_template = db.execute(
        select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY")
    ).scalar_one()
    task_template.inner_offset_days = None if invalid_reminder_config else 10
    task_template.remind_base = TaskRemindBase.INNER
    task_template.remind_1_offset_days = 1
    task_template.remind_2_offset_days = 3
    task_template.remind_3_offset_days = 5
    task_template.daily_remind = True
    return document_template, task_template


def _seed_oa_document(
    session_factory: sessionmaker,
    case_id: str,
    *,
    raw_extra_data: str,
    task_count: int,
    include_grant_task: bool = False,
    invalid_reminder_config: bool = False,
) -> tuple[str, list[str], str | None]:
    with session_factory() as db:
        document_template, task_template = _configure_oa_template(
            db,
            invalid_reminder_config=invalid_reminder_config,
        )
        document = Document(
            id=str(uuid4()),
            case_id=case_id,
            doc_template_id=document_template.id,
            direction="IN",
            doc_date=date(2026, 7, 11),
            title="待确认历史 OA 期限",
            extra_data=raw_extra_data,
            need_reply=True,
        )
        db.add(document)

        task_ids: list[str] = []
        for index in range(task_count):
            task = Task(
                id=str(uuid4()),
                case_id=case_id,
                document_id=document.id,
                task_template_id=task_template.id,
                title=f"历史 OA 任务-{index + 1}",
                base_date=date(2026, 7, 11),
                due_date=date(2026, 12, 31),
                internal_due_date=date(2026, 12, 20),
                remind1=date(2026, 12, 19),
                remind2=date(2026, 12, 17),
                remind3=date(2026, 12, 15),
                daily_remind_from=date(2026, 12, 15),
                daily_remind=True,
                status="OPEN",
            )
            db.add(task)
            task_ids.append(task.id)

        grant_task_id = None
        if include_grant_task:
            grant_template = db.execute(
                select(TaskTemplate).where(TaskTemplate.code == "GRANT_FEE")
            ).scalar_one()
            grant_task = Task(
                id=str(uuid4()),
                case_id=case_id,
                document_id=document.id,
                task_template_id=grant_template.id,
                title="不属于本次同步的授权任务",
                due_date=date(2027, 1, 15),
                internal_due_date=date(2027, 1, 8),
                status="OPEN",
            )
            db.add(grant_task)
            grant_task_id = grant_task.id

        db.commit()
        return document.id, task_ids, grant_task_id


def _confirm_deadline(
    client: TestClient,
    auth_headers: dict[str, str],
    document_id: str,
    due_date: date,
):
    return client.put(
        f"{DOCUMENT_BASE}/{document_id}",
        headers=auth_headers,
        json={
            "official_due_date": due_date.isoformat(),
            "official_due_date_source": "IMPORTED_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )


def test_put_confirmation_recalculates_one_oa_task_and_records_audit_evidence(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    missing_due = date(2026, 10, 20)
    legacy_due = date(2026, 11, 21)
    missing_id, missing_task_ids, _ = _seed_oa_document(
        session_factory,
        case_id,
        raw_extra_data='{"description":"待确认","unknown":{"keep":true}}',
        task_count=1,
    )
    legacy_id, legacy_task_ids, grant_task_id = _seed_oa_document(
        session_factory,
        case_id,
        raw_extra_data=json.dumps(
            {
                "OfficialDueDate": legacy_due.isoformat(),
                "description": "历史官文期限",
                "unknown": {"preserved": True},
            },
            ensure_ascii=False,
        ),
        task_count=1,
        include_grant_task=True,
    )

    missing_response = _confirm_deadline(
        client,
        auth_headers,
        missing_id,
        missing_due,
    )
    legacy_response = _confirm_deadline(
        client,
        auth_headers,
        legacy_id,
        legacy_due,
    )

    assert missing_response.status_code == 200, missing_response.text
    assert legacy_response.status_code == 200, legacy_response.text
    assert json.loads(missing_response.json()["extra_data"])["unknown"] == {"keep": True}
    assert json.loads(legacy_response.json()["extra_data"])["unknown"] == {"preserved": True}

    with session_factory() as db:
        tasks = (
            db.execute(select(Task).where(Task.id.in_(missing_task_ids + legacy_task_ids)))
            .scalars()
            .all()
        )
        task_by_id = {task.id: task for task in tasks}
        for task_id, due_date in (
            (missing_task_ids[0], missing_due),
            (legacy_task_ids[0], legacy_due),
        ):
            task = task_by_id[task_id]
            internal_due = due_date - timedelta(days=10)
            assert task.due_date == due_date
            assert task.internal_due_date == internal_due
            assert task.remind1 == internal_due - timedelta(days=1)
            assert task.remind2 == internal_due - timedelta(days=3)
            assert task.remind3 == internal_due - timedelta(days=5)
            assert task.daily_remind_from == internal_due - timedelta(days=5)

        logs = (
            db.execute(
                select(TaskLog).where(TaskLog.task_id.in_(missing_task_ids + legacy_task_ids))
            )
            .scalars()
            .all()
        )
        assert len(logs) == 2
        for log in logs:
            assert log.action == "UPDATE"
            evidence = json.loads(log.remark)
            assert evidence["event"] == "OFFICIAL_DEADLINE_CONFIRMED"
            assert evidence["source_document_id"] in {missing_id, legacy_id}
            assert evidence["task_template_code"] == "OA_REPLY"
            assert evidence["updated"]["due_date"] in {
                missing_due.isoformat(),
                legacy_due.isoformat(),
            }

        grant_task = db.execute(select(Task).where(Task.id == grant_task_id)).scalar_one()
        assert grant_task.due_date == date(2027, 1, 15)
        assert grant_task.internal_due_date == date(2027, 1, 8)
        assert (
            db.execute(select(TaskLog).where(TaskLog.task_id == grant_task_id)).scalars().all()
            == []
        )


def test_put_confirmation_uses_subsequent_oa_identity_and_ignores_decoys(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    due_date = date(2026, 11, 30)
    with session_factory() as db:
        subsequent_template = TaskTemplate(
            id=str(uuid4()),
            code="OA_REPLY_SUBSEQUENT",
            name="后续审查意见答复期限",
            inner_offset_days=8,
            remind_base=TaskRemindBase.DEADLINE,
            remind_1_offset_days=2,
            remind_2_offset_days=4,
            remind_3_offset_days=6,
            daily_remind=True,
        )
        document_template = DocTemplate(
            id=str(uuid4()),
            code=f"OFFICIAL_NOTICE_SUBSEQUENT_{uuid4().hex[:8].upper()}",
            name="第二次审查意见通知书",
            direction="IN",
            status_effect="OA2",
            status_restore="SUB_EXAM",
            deadline_template_code="OA_REPLY_SUBSEQUENT",
            need_reply=True,
            input_fields=json.dumps(
                {
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "catalog_status": "EXECUTABLE",
                    "execution_behavior": "OA_REPLY",
                    "canonical_template_code": "OA_IN",
                    "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                    "archive_status_restore": "SUB_EXAM",
                    "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                }
            ),
        )
        document = Document(
            id=str(uuid4()),
            case_id=case_id,
            doc_template_id=document_template.id,
            direction="IN",
            doc_date=date(2026, 7, 11),
            title="待确认后续 OA 期限",
            extra_data=json.dumps(
                {"OfficialDueDate": due_date.isoformat(), "unknown": "keep"},
                separators=(",", ":"),
            ),
            need_reply=True,
        )
        oa_reply_template = db.execute(
            select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY")
        ).scalar_one()
        grant_template = db.execute(
            select(TaskTemplate).where(TaskTemplate.code == "GRANT_FEE")
        ).scalar_one()
        db.add_all([subsequent_template, document_template])
        db.flush()
        db.add(document)
        db.flush()
        subsequent_task = Task(
            id=str(uuid4()),
            case_id=case_id,
            document_id=document.id,
            task_template_id=subsequent_template.id,
            title="后续 OA 任务",
            due_date=date(2026, 12, 31),
            internal_due_date=date(2026, 12, 20),
            status="OPEN",
        )
        oa_reply_decoy = Task(
            id=str(uuid4()),
            case_id=case_id,
            document_id=document.id,
            task_template_id=oa_reply_template.id,
            title="首次 OA 身份干扰任务",
            due_date=date(2027, 1, 10),
            status="OPEN",
        )
        grant_decoy = Task(
            id=str(uuid4()),
            case_id=case_id,
            document_id=document.id,
            task_template_id=grant_template.id,
            title="授权干扰任务",
            due_date=date(2027, 2, 10),
            status="OPEN",
        )
        db.add_all(
            [
                subsequent_task,
                oa_reply_decoy,
                grant_decoy,
            ]
        )
        document_id = document.id
        db.commit()
        subsequent_task_id = subsequent_task.id
        oa_reply_decoy_id = oa_reply_decoy.id
        grant_decoy_id = grant_decoy.id

    response = _confirm_deadline(
        client,
        auth_headers,
        document_id,
        due_date,
    )

    assert response.status_code == 200, response.text
    with session_factory() as db:
        subsequent_task = db.execute(select(Task).where(Task.id == subsequent_task_id)).scalar_one()
        oa_reply_decoy = db.execute(select(Task).where(Task.id == oa_reply_decoy_id)).scalar_one()
        grant_decoy = db.execute(select(Task).where(Task.id == grant_decoy_id)).scalar_one()
        assert subsequent_task.due_date == due_date
        assert subsequent_task.internal_due_date == due_date - timedelta(days=8)
        assert subsequent_task.remind1 == due_date - timedelta(days=2)
        assert subsequent_task.remind2 == due_date - timedelta(days=4)
        assert subsequent_task.remind3 == due_date - timedelta(days=6)
        assert subsequent_task.daily_remind_from == due_date - timedelta(days=6)
        assert oa_reply_decoy.due_date == date(2027, 1, 10)
        assert grant_decoy.due_date == date(2027, 2, 10)

        logs = (
            db.execute(
                select(TaskLog).where(
                    TaskLog.task_id.in_([subsequent_task_id, oa_reply_decoy_id, grant_decoy_id])
                )
            )
            .scalars()
            .all()
        )
        assert len(logs) == 1
        assert logs[0].task_id == subsequent_task_id
        evidence = json.loads(logs[0].remark)
        assert evidence["task_template_code"] == "OA_REPLY_SUBSEQUENT"
        assert evidence["event"] == "OFFICIAL_DEADLINE_CONFIRMED"


@pytest.mark.parametrize("task_count", [0, 2])
def test_put_confirmation_rejects_zero_or_multiple_matching_oa_tasks_without_writes(
    task_count: int,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    legacy_due = date(2026, 12, 10)
    raw_extra_data = json.dumps(
        {
            "OfficialDueDate": legacy_due.isoformat(),
            "unknown": {"keep": True},
        },
        separators=(",", ":"),
    )
    document_id, task_ids, _ = _seed_oa_document(
        session_factory,
        case_id,
        raw_extra_data=raw_extra_data,
        task_count=task_count,
    )

    response = _confirm_deadline(
        client,
        auth_headers,
        document_id,
        legacy_due,
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_DEADLINE_TASK_MATCH_INVALID"
    with session_factory() as db:
        document = db.execute(select(Document).where(Document.id == document_id)).scalar_one()
        assert document.extra_data == raw_extra_data
        tasks = db.execute(select(Task).where(Task.id.in_(task_ids))).scalars().all()
        assert all(task.due_date == date(2026, 12, 31) for task in tasks)
        assert (
            db.execute(select(TaskLog).where(TaskLog.task_id.in_(task_ids))).scalars().all() == []
        )


def test_put_confirmation_rejects_task_reminder_conflict_without_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(client, auth_headers)
    legacy_due = date(2026, 12, 20)
    raw_extra_data = json.dumps(
        {"OfficialDueDate": legacy_due.isoformat(), "unknown": "keep"},
        separators=(",", ":"),
    )
    document_id, task_ids, _ = _seed_oa_document(
        session_factory,
        case_id,
        raw_extra_data=raw_extra_data,
        task_count=1,
        invalid_reminder_config=True,
    )

    response = _confirm_deadline(
        client,
        auth_headers,
        document_id,
        legacy_due,
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_DEADLINE_TASK_SYNC_CONFLICT"
    with session_factory() as db:
        document = db.execute(select(Document).where(Document.id == document_id)).scalar_one()
        task = db.execute(select(Task).where(Task.id == task_ids[0])).scalar_one()
        assert document.extra_data == raw_extra_data
        assert task.due_date == date(2026, 12, 31)
        assert task.internal_due_date == date(2026, 12, 20)
        assert db.execute(select(TaskLog).where(TaskLog.task_id == task.id)).scalars().all() == []
