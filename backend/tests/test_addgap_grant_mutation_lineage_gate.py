from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

import app.modules.grant_fees.service as grant_fee_service
from app.core.errors import BusinessError
from app.modules.cases.models import Case
from app.modules.documents.models import DocTemplate, Document
from app.modules.fees.models import FeeDraft, FeeItem, T_GrantFeeTask
from app.modules.grant_fees.service import (
    apply_grant_fee_batch_instruction,
    generate_grant_fee_draft,
    generate_grant_fee_notice_documents,
)
from app.modules.templates.models import Template


def _source_document(db: Session, *, case_id: str, title: str) -> Document:
    document = Document(
        case_id=case_id,
        doc_type="OFFICIAL",
        direction="IN",
        doc_date=date(2026, 4, 1),
        title=title,
    )
    db.add(document)
    db.flush()
    return document


def _task(
    db: Session,
    *,
    case_id: str,
    lineage: str,
    workflow: str,
) -> T_GrantFeeTask:
    source_document_id = None
    deadline_source = None
    deadline_confirmed_at = None
    superseded_by_task_id = None

    if lineage in {"CONFIRMED", "SUPERSEDED"}:
        source = _source_document(
            db,
            case_id=case_id,
            title=f"授权通知书-{lineage}-{uuid4().hex[:6]}",
        )
        source_document_id = source.id
        deadline_source = "MANUAL_OFFICIAL_NOTICE"
        deadline_confirmed_at = datetime(2026, 4, 1, 9, 0)

    if lineage == "SUPERSEDED":
        replacement_source = _source_document(
            db,
            case_id=case_id,
            title=f"更正授权通知书-{uuid4().hex[:6]}",
        )
        replacement = T_GrantFeeTask(
            case_id=case_id,
            due_date=date(2026, 8, 31),
            source_document_id=replacement_source.id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=datetime(2026, 4, 2, 9, 0),
            gov_fee_amt=Decimal("100.00"),
            service_fee_amt=Decimal("0.00"),
            currency="CNY",
            client_instruction="NONE",
            notify_count=0,
            draft_generated=False,
            notice_sent=False,
            is_overdue=False,
        )
        db.add(replacement)
        db.flush()
        superseded_by_task_id = replacement.id

    workflow_values = {
        "READY_TO_DRAFT": {"client_instruction": "PAY", "notify_count": 2, "notice_sent": True},
        "WAITING_CLIENT": {"client_instruction": "NONE", "notify_count": 1, "notice_sent": True},
        "OPEN": {"client_instruction": "NONE", "notify_count": 0, "notice_sent": False},
    }[workflow]
    task = T_GrantFeeTask(
        case_id=case_id,
        due_date=date(2026, 7, 31),
        source_document_id=source_document_id,
        deadline_source=deadline_source,
        deadline_confirmed_at=deadline_confirmed_at,
        superseded_by_task_id=superseded_by_task_id,
        gov_fee_amt=Decimal("900.00"),
        service_fee_amt=Decimal("0.00"),
        currency="CNY",
        client_instruction=workflow_values["client_instruction"],
        notify_count=workflow_values["notify_count"],
        draft_generated=False,
        notice_sent=workflow_values["notice_sent"],
        is_overdue=False,
    )
    db.add(task)
    db.flush()
    return task


def _case(db: Session) -> Case:
    case = Case(
        case_no=f"GFMG-{uuid4().hex[:8].upper()}",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="授权费 mutation lineage gate 测试",
    )
    db.add(case)
    db.flush()
    return case


def _existing_draft(db: Session, *, task: T_GrantFeeTask) -> FeeDraft:
    draft = FeeDraft(
        id=str(uuid4()),
        case_id=task.case_id,
        client_id=None,
        draft_type="GRANT_FEE",
        currency="CNY",
        status="OPEN",
        total_gov=Decimal("900.00"),
        total_service=Decimal("0.00"),
        total_misc=Decimal("0.00"),
        amount=Decimal("900.00"),
    )
    db.add(draft)
    db.flush()
    db.add(
        FeeItem(
            id=str(uuid4()),
            draft_id=draft.id,
            case_id=task.case_id,
            fee_code="GRANT_FEE_GOV",
            fee_name="授权官费",
            fee_type="GOV",
            quantity=Decimal("1"),
            unit_price=Decimal("900.00"),
            amount=Decimal("900.00"),
            remark=f"GRANT_FEE_TASK:{task.id}",
        )
    )
    db.flush()
    return draft


def _assert_blocked(error: BusinessError, *, task_id: str, lineage: str) -> None:
    assert error.status_code == 409
    assert error.code == "GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE"
    assert error.details == {"task_id": task_id, "lineage_status": lineage}


@pytest.mark.parametrize("lineage", ["LEGACY_UNVERIFIED", "SUPERSEDED"])
def test_draft_reuse_requires_actionable_lineage(
    session_factory: sessionmaker,
    lineage: str,
) -> None:
    with session_factory() as db:
        case = _case(db)
        blocked = _task(db, case_id=case.id, lineage=lineage, workflow="READY_TO_DRAFT")
        confirmed = _task(db, case_id=case.id, lineage="CONFIRMED", workflow="READY_TO_DRAFT")
        blocked_draft = _existing_draft(db, task=blocked)
        confirmed_draft = _existing_draft(db, task=confirmed)
        db.commit()
        blocked_id = blocked.id
        confirmed_id = confirmed.id
        blocked_draft_id = blocked_draft.id
        confirmed_draft_id = confirmed_draft.id

        with pytest.raises(BusinessError) as exc_info:
            generate_grant_fee_draft(db, task_id=blocked_id, actor_id=None)

        _assert_blocked(exc_info.value, task_id=blocked_id, lineage=lineage)
        db.expire_all()
        assert db.get(T_GrantFeeTask, blocked_id).draft_generated is False
        assert db.get(FeeDraft, blocked_draft_id).amount == Decimal("900.00")

        confirmed_result = generate_grant_fee_draft(db, task_id=confirmed_id, actor_id=None)
        assert confirmed_result["reused"] is True
        assert confirmed_result["draft_id"] == confirmed_draft_id
        assert db.get(T_GrantFeeTask, confirmed_id).draft_generated is True


@pytest.mark.parametrize("lineage", ["LEGACY_UNVERIFIED", "SUPERSEDED"])
def test_batch_instruction_validates_all_lineage_before_mutation(
    session_factory: sessionmaker,
    lineage: str,
) -> None:
    with session_factory() as db:
        case = _case(db)
        confirmed = _task(db, case_id=case.id, lineage="CONFIRMED", workflow="WAITING_CLIENT")
        blocked = _task(db, case_id=case.id, lineage=lineage, workflow="WAITING_CLIENT")
        db.commit()
        confirmed_id = confirmed.id
        blocked_id = blocked.id

        with pytest.raises(BusinessError) as exc_info:
            apply_grant_fee_batch_instruction(
                db,
                task_ids=[confirmed_id, blocked_id],
                action="record_pay_instruction",
            )

        _assert_blocked(exc_info.value, task_id=blocked_id, lineage=lineage)
        db.expire_all()
        assert db.get(T_GrantFeeTask, confirmed_id).client_instruction == "NONE"
        assert db.get(T_GrantFeeTask, blocked_id).client_instruction == "NONE"

        result = apply_grant_fee_batch_instruction(
            db,
            task_ids=[confirmed_id],
            action="record_pay_instruction",
        )
        assert result["updated_task_ids"] == [confirmed_id]
        assert db.get(T_GrantFeeTask, confirmed_id).client_instruction == "PAY"


def _configure_notice_template(db: Session, *, template_path: Path) -> None:
    doc_template = db.execute(
        select(DocTemplate).where(DocTemplate.code == "GRANT_FEE_NOTICE")
    ).scalar_one_or_none()
    if doc_template is None:
        doc_template = DocTemplate(
            code="GRANT_FEE_NOTICE",
            name="授权费通知函",
            direction="OUT",
            enabled=True,
        )
        db.add(doc_template)
    else:
        doc_template.enabled = True

    render_template = db.execute(
        select(Template).where(
            Template.name == "GRANT_FEE_NOTICE",
            Template.group == "DOC_TEMPLATE",
        )
    ).scalar_one_or_none()
    if render_template is None:
        db.add(
            Template(
                id=str(uuid4()),
                name="GRANT_FEE_NOTICE",
                group="DOC_TEMPLATE",
                language="zh-CN",
                file_path=str(template_path),
                enabled=True,
            )
        )
    else:
        render_template.file_path = str(template_path)
        render_template.enabled = True
    db.flush()


@pytest.mark.parametrize("lineage", ["LEGACY_UNVERIFIED", "SUPERSEDED"])
def test_batch_notice_validates_all_lineage_before_render_or_document_creation(
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
    lineage: str,
) -> None:
    template_path = tmp_path / "grant_fee_notice.docx"
    template_path.write_bytes(b"template")
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    monkeypatch.setattr(grant_fee_service, "_backend_storage_dir", lambda: storage_dir)
    monkeypatch.setattr(
        "app.modules.templates.render.TemplateRenderer.render_template_docx_bytes",
        lambda self, *, template_path, context: b"generated-docx",
    )

    with session_factory() as db:
        case = _case(db)
        confirmed = _task(db, case_id=case.id, lineage="CONFIRMED", workflow="OPEN")
        blocked = _task(db, case_id=case.id, lineage=lineage, workflow="OPEN")
        _configure_notice_template(db, template_path=template_path)
        db.commit()
        confirmed_id = confirmed.id
        blocked_id = blocked.id
        document_count = db.scalar(select(func.count()).select_from(Document))

        with pytest.raises(BusinessError) as exc_info:
            generate_grant_fee_notice_documents(
                db,
                task_ids=[confirmed_id, blocked_id],
            )

        _assert_blocked(exc_info.value, task_id=blocked_id, lineage=lineage)
        db.expire_all()
        assert db.scalar(select(func.count()).select_from(Document)) == document_count
        assert db.get(T_GrantFeeTask, confirmed_id).notify_count == 0
        assert db.get(T_GrantFeeTask, blocked_id).notify_count == 0

        result = generate_grant_fee_notice_documents(db, task_ids=[confirmed_id])
        assert result["success_count"] == 1
        assert db.get(T_GrantFeeTask, confirmed_id).notify_count == 1
        assert db.scalar(select(func.count()).select_from(Document)) == document_count + 1
