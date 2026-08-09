from __future__ import annotations

import json
from datetime import date, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.models import Document
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees import service

CASE_ID = "case-grant-fee-done"
DOCUMENT_ID = "document-grant-fee-done"
TASK_ID = "task-grant-fee-done"
ACTOR_ID = "actor-grant-fee-done"


def _seed_done_context(
    session_factory: sessionmaker[Session],
    *,
    actor_id: str | None = ACTOR_ID,
) -> None:
    with session_factory.begin() as transaction:
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="V8-GRANT-FEE-DONE",
                status="GRANT_PENDING",
                business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
                official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION.value,
                legal_status=LegalStatus.APPLICATION_PENDING.value,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
                lifecycle_revision=0,
                app_no="CN202610000001",
                filing_date=date(2026, 3, 20),
                pub_no="CN202610000001A",
                pub_date=date(2026, 4, 1),
                grant_no="CN202610000001B",
                grant_date=date(2026, 7, 24),
                first_annuity_year=3,
                valid_until=date(2046, 3, 20),
            )
        )
        transaction.add(
            Document(
                id=DOCUMENT_ID,
                case_id=CASE_ID,
                doc_type="OFFICIAL_NOTICE",
                direction="IN",
                doc_date=date(2026, 7, 25),
                title="办理登记手续通知书",
            )
        )
        transaction.flush()
        transaction.add(
            T_GrantFeeTask(
                id=TASK_ID,
                case_id=CASE_ID,
                due_date=date(2026, 8, 25),
                source_document_id=DOCUMENT_ID,
                deadline_source="OFFICIAL_NOTICE",
                deadline_confirmed_at=datetime(2026, 7, 25, 9, 0),
                gov_fee_amt=900,
                service_fee_amt=0,
                currency="CNY",
                client_instruction="PAY",
                notify_count=3,
                draft_generated=True,
                notice_sent=True,
                is_overdue=False,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )


def _case_projection(case: Case) -> tuple[object, ...]:
    return (
        case.status,
        case.business_stage,
        case.official_procedure_stage,
        case.legal_status,
        case.lifecycle_verification_status,
        case.lifecycle_revision,
    )


def test_mark_done_appends_one_fee_activity_without_granting_case(
    session_factory: sessionmaker[Session],
) -> None:
    _seed_done_context(session_factory)

    with session_factory() as transaction:
        result = service.apply_grant_fee_task_action(
            transaction,
            task_id=TASK_ID,
            action="mark_done",
        )

    assert result["state"] == "DONE"
    with session_factory() as verification:
        task = verification.get(T_GrantFeeTask, TASK_ID)
        case = verification.get(Case, CASE_ID)
        activities = verification.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == CASE_ID)
        ).all()

        assert task is not None and task.notify_count == 4
        assert case is not None
        assert _case_projection(case) == (
            "GRANT_PENDING",
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
            OfficialProcedureStage.GRANT_REGISTRATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            1,
        )
        assert len(activities) == 1
        activity = activities[0]
        assert (
            activity.sequence,
            activity.lane,
            activity.activity_type,
            activity.actor_id,
            activity.confirmation_status,
            activity.idempotency_key,
        ) == (
            1,
            ActivityLane.FEE.value,
            "GRANT_FEE_TASK_DONE",
            ACTOR_ID,
            ConfirmationStatus.CONFIRMED.value,
            f"grant-fee-task:{TASK_ID}:done",
        )
        assert activity.occurred_at == activity.effective_at
        assert activity.occurred_at is not None and activity.occurred_at.tzinfo is None
        assert (
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
        ) == (
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
            OfficialProcedureStage.GRANT_REGISTRATION.value,
            OfficialProcedureStage.GRANT_REGISTRATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            LegalStatus.APPLICATION_PENDING.value,
        )
        assert json.loads(activity.payload_json) == {"center_changes": {}}

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as captured:
            service.apply_grant_fee_task_action(
                transaction,
                task_id=TASK_ID,
                action="mark_done",
            )
        assert captured.value.code == "GRANT_FEE_STATE_TRANSITION_INVALID"
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == CASE_ID)
            )
            == 1
        )


def test_mark_done_fails_closed_without_audit_actor(
    session_factory: sessionmaker[Session],
) -> None:
    _seed_done_context(session_factory, actor_id=None)

    with session_factory() as transaction:
        with pytest.raises(BusinessError) as captured:
            service.apply_grant_fee_task_action(
                transaction,
                task_id=TASK_ID,
                action="mark_done",
            )

        assert captured.value.code == "GRANT_FEE_TASK_DONE_ACTOR_REQUIRED"
        assert captured.value.status_code == 409
        assert captured.value.message == "授权费任务完成活动缺少可追溯操作者"

    with session_factory() as verification:
        task = verification.get(T_GrantFeeTask, TASK_ID)
        case = verification.get(Case, CASE_ID)
        assert task is not None and task.notify_count == 3
        assert case is not None
        assert _case_projection(case) == (
            "GRANT_PENDING",
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
            OfficialProcedureStage.GRANT_REGISTRATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            0,
        )
        assert verification.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0


def test_mark_done_rolls_back_task_when_activity_append_fails(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_done_context(session_factory)

    def fail_append(*_args, **_kwargs):
        raise RuntimeError("injected activity append failure")

    monkeypatch.setattr(service, "append_case_activity", fail_append, raising=False)
    with session_factory() as transaction:
        with pytest.raises(RuntimeError, match="injected activity append failure"):
            service.apply_grant_fee_task_action(
                transaction,
                task_id=TASK_ID,
                action="mark_done",
            )
        task = transaction.get(T_GrantFeeTask, TASK_ID)
        case = transaction.get(Case, CASE_ID)
        assert task is not None and task.notify_count == 3
        assert case is not None
        assert _case_projection(case) == (
            "GRANT_PENDING",
            BusinessStage.GRANT_REGISTRATION_IN_PROGRESS.value,
            OfficialProcedureStage.GRANT_REGISTRATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            0,
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0

    with session_factory() as verification:
        task = verification.get(T_GrantFeeTask, TASK_ID)
        case = verification.get(Case, CASE_ID)
        assert task is not None and task.notify_count == 3
        assert case is not None and case.lifecycle_revision == 0
        assert verification.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
