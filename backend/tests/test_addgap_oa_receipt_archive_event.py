from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.enums import DocumentDirection
from app.modules.documents.models import DocAttachment, DocTemplate, Document
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
    OfficialWorkPackageOverride,
    OfficialWorkPackageReceipt,
)
from app.modules.tasks.models import Task, TaskLog, TaskTemplate

BASE = "/api/v1/official-work-packages"
EVENT_ITEM_CODE = "OFFICIAL_RECEIPT_ARCHIVED"


def _oa2_template(db) -> tuple[DocTemplate, TaskTemplate]:
    task_template = TaskTemplate(
        id=str(uuid4()),
        code="OA_REPLY_SUBSEQUENT",
        name="后续审查意见答复期限",
        enabled=True,
        add_days=60,
        inner_offset_days=7,
    )
    template = DocTemplate(
        id=str(uuid4()),
        code=f"OA2_ARCHIVE_{uuid4().hex[:8].upper()}",
        name="第二次审查意见通知书",
        direction="IN",
        status_effect="OA2",
        deadline_template_code=task_template.code,
        need_reply=True,
        input_fields=json.dumps(
            {
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "EXECUTABLE",
                "execution_behavior": "OA_REPLY",
                "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                "archive_status_restore": "SUB_EXAM",
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "canonical_template_code": "OA_IN",
            },
            ensure_ascii=False,
        ),
    )
    db.add_all([task_template, template])
    return template, task_template


def _create_archive_fixture(
    session_factory: sessionmaker,
    *,
    semantic_status: str = "OA1",
    case_status: str | None = None,
    matching_task_count: int = 1,
    receipt_mode: str = "valid",
    lifecycle_ready: bool = False,
) -> dict[str, object]:
    with session_factory() as db:
        case = Case(
            id=str(uuid4()),
            case_no=f"OA-ARCHIVE-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="OA官方回执事件测试案件",
            status=case_status or semantic_status,
        )
        if lifecycle_ready:
            case.business_stage = "OA_REPLY_IN_PROGRESS"
            case.official_procedure_stage = "OFFICE_ACTION_RESPONSE"
            case.legal_status = "APPLICATION_PENDING"
            case.lifecycle_verification_status = "CONFIRMED"
            case.lifecycle_revision = 0
        other_case = Case(
            id=str(uuid4()),
            case_no=f"OA-ARCHIVE-X-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="OA官方回执跨案测试案件",
            status="OA1",
        )
        db.add_all([case, other_case])
        db.flush()

        if semantic_status == "OA2":
            source_template, matching_template = _oa2_template(db)
        else:
            source_template = db.execute(
                select(DocTemplate).where(DocTemplate.code == "OA_IN")
            ).scalar_one()
            matching_template = db.execute(
                select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY")
            ).scalar_one()
        db.flush()

        source_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=source_template.id,
            doc_type="OFFICIAL_NOTICE",
            direction=DocumentDirection.IN,
            doc_date=date(2026, 5, 10),
            title=f"{semantic_status}审查意见通知书",
            need_reply=True,
        )
        reply_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title=f"{semantic_status}审查意见答复",
            reply_to_id=source_document.id,
        )
        same_case_other_document = Document(
            id=str(uuid4()),
            case_id=case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="同案其他文档",
        )
        cross_case_document = Document(
            id=str(uuid4()),
            case_id=other_case.id,
            direction=DocumentDirection.OUT,
            doc_date=date(2026, 7, 11),
            title="跨案回执文档",
        )
        db.add_all(
            [
                source_document,
                reply_document,
                same_case_other_document,
                cross_case_document,
            ]
        )
        db.flush()

        content_attachment = DocAttachment(
            id=str(uuid4()),
            document_id=reply_document.id,
            file_name="意见陈述书.pdf",
            file_path=f"attachments/{reply_document.id}/statement.pdf",
            official_file_role="OA_STATEMENT_PDF",
            content_hash="sha256:statement",
        )
        receipt_attachments = {
            "valid": DocAttachment(
                id=str(uuid4()),
                document_id=reply_document.id,
                file_name="有效电子申请回执.pdf",
                file_path=f"attachments/{reply_document.id}/receipt.pdf",
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "invalid_source": DocAttachment(
                id=str(uuid4()),
                document_id=same_case_other_document.id,
                file_name="无效来源电子申请回执.pdf",
                file_path=f"attachments/{same_case_other_document.id}/receipt.pdf",
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
            "cross_case": DocAttachment(
                id=str(uuid4()),
                document_id=cross_case_document.id,
                file_name="跨案电子申请回执.pdf",
                file_path=f"attachments/{cross_case_document.id}/receipt.pdf",
                official_file_role="ELECTRONIC_RECEIPT",
                is_archive_evidence=True,
                is_receipt_evidence=True,
            ),
        }
        db.add_all([content_attachment, *receipt_attachments.values()])

        package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="OA_REPLY",
            status="WAITING_RECEIPT",
            source_document_id=source_document.id,
            reply_document_id=reply_document.id,
            resolve_key=f"OA_REPLY:{source_document.id}",
            external_system="CNIPA_WEB",
        )
        foreign_package = OfficialWorkPackage(
            id=str(uuid4()),
            case_id=case.id,
            package_kind="FILING_PREP",
            status="WAITING_RECEIPT",
            resolve_key=f"FILING_PREP:FOREIGN:{case.id}",
        )
        db.add_all([package, foreign_package])
        db.flush()

        db.add_all(
            [
                OfficialWorkPackageChecklist(
                    id=str(uuid4()),
                    package_id=package.id,
                    section_code="OFFICIAL_PAGE",
                    item_code="PREVIEW_CONFIRMED",
                    item_label="官方页面预览已确认",
                    status="DONE",
                    required=True,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=package.id,
                    attachment_id=content_attachment.id,
                    official_file_role="OA_STATEMENT_PDF",
                    required=True,
                    present=True,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=package.id,
                    attachment_id=receipt_attachments["invalid_source"].id,
                    official_file_role="OA_ADDITIONAL_FILE",
                    required=False,
                    present=False,
                ),
                OfficialWorkPackageManifest(
                    id=str(uuid4()),
                    package_id=foreign_package.id,
                    attachment_id=receipt_attachments["invalid_source"].id,
                    official_file_role="FILING_MERGED_PDF",
                    required=False,
                    present=True,
                ),
            ]
        )

        matching_task_ids: list[str] = []
        for index in range(matching_task_count):
            task = Task(
                id=str(uuid4()),
                case_id=case.id,
                document_id=source_document.id,
                task_template_id=matching_template.id,
                title=f"{matching_template.name}-{index + 1}",
                due_date=date(2026, 9, 10),
                status="OPEN",
            )
            db.add(task)
            matching_task_ids.append(task.id)

        decoy_template = TaskTemplate(
            id=str(uuid4()),
            code=f"OA_ARCHIVE_DECOY_{uuid4().hex[:8].upper()}",
            name="同文档非OA任务",
            enabled=True,
        )
        db.add(decoy_template)
        db.flush()
        decoy_task = Task(
            id=str(uuid4()),
            case_id=case.id,
            document_id=source_document.id,
            task_template_id=decoy_template.id,
            title="不得被回执事件关闭的任务",
            due_date=date(2026, 10, 10),
            status="OPEN",
        )
        db.add(decoy_task)

        receipt_id = None
        if receipt_mode != "missing":
            receipt_attachment = receipt_attachments[receipt_mode]
            receipt = OfficialWorkPackageReceipt(
                id=str(uuid4()),
                package_id=package.id,
                receipt_kind="ELECTRONIC_APPLICATION_RECEIPT",
                receipt_attachment_id=receipt_attachment.id,
                receiving_case_no="202607110017",
                submitter="流程人员A",
                archive_status="ARCHIVED",
                received_file_list='["意见陈述书","权利要求书"]',
            )
            db.add(receipt)
            receipt_id = receipt.id

        db.commit()
        return {
            "case_id": case.id,
            "case_initial_status": case.status,
            "source_document_id": source_document.id,
            "package_id": package.id,
            "matching_task_ids": matching_task_ids,
            "decoy_task_id": decoy_task.id,
            "receipt_id": receipt_id,
        }


def _archive(
    client: TestClient,
    auth_headers: dict[str, str],
    package_id: str,
    payload: dict[str, object] | None = None,
):
    return client.post(
        f"{BASE}/{package_id}/archive",
        headers=auth_headers,
        json=payload or {},
    )


def _assert_event_not_written(
    session_factory: sessionmaker,
    ids: dict[str, object],
) -> None:
    with session_factory() as db:
        case = db.get(Case, ids["case_id"])
        package = db.get(OfficialWorkPackage, ids["package_id"])
        tasks = (
            db.execute(
                select(Task).where(Task.id.in_([*ids["matching_task_ids"], ids["decoy_task_id"]]))
            )
            .scalars()
            .all()
        )
        close_logs = (
            db.execute(
                select(TaskLog).where(
                    TaskLog.task_id.in_([task.id for task in tasks]),
                    TaskLog.action == "CLOSE",
                )
            )
            .scalars()
            .all()
        )
        event_checklist = db.execute(
            select(OfficialWorkPackageChecklist).where(
                OfficialWorkPackageChecklist.package_id == ids["package_id"],
                OfficialWorkPackageChecklist.item_code == EVENT_ITEM_CODE,
            )
        ).scalar_one_or_none()

        assert case.status == ids["case_initial_status"]
        assert package.status == "WAITING_RECEIPT"
        assert all(task.status == "OPEN" and task.done_at is None for task in tasks)
        assert close_logs == []
        assert event_checklist is None


@pytest.mark.parametrize("semantic_status", ["OA1", "OA2"])
def test_valid_receipt_archive_closes_exact_task_and_restores_case(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    semantic_status: str,
) -> None:
    ids = _create_archive_fixture(
        session_factory,
        semantic_status=semantic_status,
        lifecycle_ready=True,
    )

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 200, response.text
    assert set(response.json()) == {"package", "evaluation"}
    assert response.json()["package"]["status"] == "ARCHIVED"
    assert response.json()["evaluation"]["can_archive"] is True

    with session_factory() as db:
        case = db.get(Case, ids["case_id"])
        package = db.get(OfficialWorkPackage, ids["package_id"])
        matched_task = db.get(Task, ids["matching_task_ids"][0])
        decoy_task = db.get(Task, ids["decoy_task_id"])
        close_log = db.execute(
            select(TaskLog).where(
                TaskLog.task_id == matched_task.id,
                TaskLog.action == "CLOSE",
            )
        ).scalar_one()
        event_checklist = db.execute(
            select(OfficialWorkPackageChecklist).where(
                OfficialWorkPackageChecklist.package_id == package.id,
                OfficialWorkPackageChecklist.item_code == EVENT_ITEM_CODE,
            )
        ).scalar_one()
        admin = db.execute(select(T_User).where(T_User.username == "admin")).scalar_one()

        assert package.status == "ARCHIVED"
        assert case.status == "SUB_EXAM"
        assert matched_task.status == "DONE"
        assert matched_task.done_at is not None
        assert decoy_task.status == "OPEN"
        assert decoy_task.done_at is None
        assert close_log.from_status == "OPEN"
        assert close_log.to_status == "DONE"
        evidence = json.loads(event_checklist.evidence_note)
        assert event_checklist.status == "DONE"
        assert event_checklist.required is False
        assert evidence == {
            "actor_id": admin.id,
            "case_transition": {
                "from_status": semantic_status,
                "to_status": "SUB_EXAM",
            },
            "closed_task_id": matched_task.id,
            "event": "OFFICIAL_RECEIPT_ARCHIVED",
            "receipt_ids": [ids["receipt_id"]],
            "source_document_id": ids["source_document_id"],
        }


def test_archive_without_receipt_returns_409_without_event_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory, receipt_mode="missing")

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED"
    _assert_event_not_written(session_factory, ids)


@pytest.mark.parametrize("receipt_mode", ["cross_case", "invalid_source"])
def test_archive_revalidates_historical_receipt_ownership_before_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    receipt_mode: str,
) -> None:
    ids = _create_archive_fixture(session_factory, receipt_mode=receipt_mode)

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_RECEIPT_ARCHIVE_EVIDENCE_INVALID"
    _assert_event_not_written(session_factory, ids)


@pytest.mark.parametrize("matching_task_count", [0, 2])
def test_archive_requires_exactly_one_matching_open_oa_task_before_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    matching_task_count: int,
) -> None:
    ids = _create_archive_fixture(
        session_factory,
        matching_task_count=matching_task_count,
    )

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_RECEIPT_ARCHIVE_TASK_MATCH_INVALID"
    assert response.json()["error"]["details"]["matching_open_task_count"] == (matching_task_count)
    _assert_event_not_written(session_factory, ids)


def test_archive_requires_case_state_to_match_source_oa_semantics_before_writes(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory, semantic_status="OA1", case_status="OA2")

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "OA_RECEIPT_ARCHIVE_CASE_STATE_INVALID"
    _assert_event_not_written(session_factory, ids)


def test_complete_override_never_emits_receipt_archive_event(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory, receipt_mode="missing")

    response = _archive(
        client,
        auth_headers,
        ids["package_id"],
        {
            "override_reason": "官方回执暂时无法下载，负责人批准后续补归档",
            "follow_up_owner": "formalities-user",
            "follow_up_note": "次日补传电子申请回执",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["package"]["status"] == "OVERRIDE"
    with session_factory() as db:
        case = db.get(Case, ids["case_id"])
        package = db.get(OfficialWorkPackage, ids["package_id"])
        matched_task = db.get(Task, ids["matching_task_ids"][0])
        override = db.execute(
            select(OfficialWorkPackageOverride).where(
                OfficialWorkPackageOverride.package_id == package.id
            )
        ).scalar_one()
        close_logs = (
            db.execute(
                select(TaskLog).where(
                    TaskLog.task_id == matched_task.id,
                    TaskLog.action == "CLOSE",
                )
            )
            .scalars()
            .all()
        )
        assert package.status == "OVERRIDE"
        assert case.status == "OA1"
        assert matched_task.status == "OPEN"
        assert matched_task.done_at is None
        assert override.override_action == "ARCHIVE_WITHOUT_RECEIPT"
        assert close_logs == []


def test_repeated_archive_is_idempotent_without_duplicate_logs_or_evidence(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory, lifecycle_ready=True)

    first = _archive(client, auth_headers, ids["package_id"])
    repeated = _archive(client, auth_headers, ids["package_id"])

    assert first.status_code == 200, first.text
    assert repeated.status_code == 200, repeated.text
    assert repeated.json()["package"]["status"] == "ARCHIVED"
    with session_factory() as db:
        task_id = ids["matching_task_ids"][0]
        close_logs = (
            db.execute(
                select(TaskLog).where(
                    TaskLog.task_id == task_id,
                    TaskLog.action == "CLOSE",
                )
            )
            .scalars()
            .all()
        )
        evidence_rows = (
            db.execute(
                select(OfficialWorkPackageChecklist).where(
                    OfficialWorkPackageChecklist.package_id == ids["package_id"],
                    OfficialWorkPackageChecklist.item_code == EVENT_ITEM_CODE,
                )
            )
            .scalars()
            .all()
        )
        assert len(close_logs) == 1
        assert len(evidence_rows) == 1
        assert db.get(Task, task_id).status == "DONE"
        assert db.get(Case, ids["case_id"]).status == "SUB_EXAM"
