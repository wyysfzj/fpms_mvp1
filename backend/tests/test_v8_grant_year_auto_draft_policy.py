from __future__ import annotations

import json
from datetime import datetime

import pytest
import test_v8_grant_official_fee_manual_review as manual
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.auth.models import T_User
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import FeeDraft, FeeItem, FeeObligation
from app.modules.grant_fees import service as grant_fee_service
from app.modules.system.decision_gate_service import DecisionGateCode
from app.modules.system.models import CustomerDecisionGate

DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
AS_OF = datetime(2026, 8, 10, 13, 0)


def _seed_ready(transaction: Session, *, gate: bool = True):
    seed = manual._seed(transaction, label="GRANT-YEAR-AUTO-DRAFT")
    review = manual._command(seed)
    grant_fee_service.confirm_grant_official_fees(review, transaction)
    admin_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert admin_id is not None
    if gate:
        transaction.add(
            CustomerDecisionGate(
                id="gate-grant-year-auto-draft",
                gate_code=DecisionGateCode.FEE_GRANT_YEAR_DRAFT.value,
                scope_key="GLOBAL",
                decision_value="APPROVED_POLICY",
                decision_status="CONFIRMED",
                source_reference=DECISION_SOURCE,
                source_version=DECISION_VERSION,
                confirmed_by=admin_id,
                effective_at=datetime(2026, 8, 10, 0, 0),
                supersedes_gate_id=None,
                decision_snapshot="{}",
                idempotency_key="gate:grant-year-auto-draft",
                current_identity_key="DG-FEE-GRANT-YEAR-DRAFT|GLOBAL",
            )
        )
    transaction.commit()
    return seed, review


def test_reviewed_grant_notice_creates_pending_internal_draft_and_replays(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        policy = getattr(grant_fee_service, "apply_grant_year_auto_draft_policy", None)
        assert callable(policy), "missing reviewed-notice grant-year auto-draft policy"

        command = {
            "transaction": transaction,
            "grant_fee_task_id": seed[2].id,
            "source_activity_id": seed[4].activity_id,
            "actor_id": review.actor_id,
            "as_of": AS_OF,
        }
        result = policy(**command)
        replay = policy(**command)

        obligation = transaction.get(FeeObligation, result.recognition.obligation.id)
        draft = transaction.get(FeeDraft, result.draft.draft_id)
        activity = transaction.get(CaseActivityEvent, result.draft.activity_id)
        assert obligation is not None and draft is not None and activity is not None
        assert result.recognition.obligation.id == seed[-2].id
        assert replay.recognition.reused is True
        assert replay.draft.draft_id == result.draft.draft_id
        assert replay.draft.activity_reused is True
        assert obligation.client_instruction_status == "PENDING"
        assert obligation.draft_status == "CREATED"
        assert obligation.payment_status == "UNPAID"
        assert draft.status == "OPEN"
        assert json.loads(activity.payload_json)["authority"] == "REVIEWED_GRANT_YEAR_NOTICE"
        assert (
            json.loads(activity.payload_json)["schema"]
            == "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_GRANT_YEAR_NOTICE_V1"
        )
        assert activity.source_activity_id == result.recognition.activity_id
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED")
            )
            == 0
        )
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0


def test_missing_or_wrong_gate_is_409_before_draft_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction, gate=False)
        with pytest.raises(BusinessError) as missing:
            grant_fee_service.apply_grant_year_auto_draft_policy(
                transaction=transaction,
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                actor_id=review.actor_id,
                as_of=AS_OF,
            )
        assert missing.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeItem)) == 0

    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        gate = transaction.get(CustomerDecisionGate, "gate-grant-year-auto-draft")
        assert gate is not None
        gate.source_version = "wrong-version"
        transaction.commit()
        with pytest.raises(BusinessError) as wrong:
            grant_fee_service.apply_grant_year_auto_draft_policy(
                transaction=transaction,
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                actor_id=review.actor_id,
                as_of=AS_OF,
            )
        assert wrong.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_later_pay_instruction_consumes_reviewed_draft_without_rebuilding(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        result = grant_fee_service.apply_grant_year_auto_draft_policy(
            transaction=transaction,
            grant_fee_task_id=seed[2].id,
            source_activity_id=seed[4].activity_id,
            actor_id=review.actor_id,
            as_of=AS_OF,
        )
        before = (
            result.draft.draft_id,
            result.draft.activity_id,
            tuple((link.id, link.fee_item_id) for link in result.draft.links),
        )
        instruction = grant_fee_service.record_grant_fee_task_instruction(
            grant_fee_service.RecordGrantFeeTaskInstructionCommand(
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                instruction="PAY",
                actor_id="grant-year-client-instruction",
                idempotency_key="grant-year-auto-draft:pay",
            ),
            transaction,
        )
        assert instruction.instruction.value == "PAY"
        replay = grant_fee_service.apply_grant_year_auto_draft_policy(
            transaction=transaction,
            grant_fee_task_id=seed[2].id,
            source_activity_id=seed[4].activity_id,
            actor_id=review.actor_id,
            as_of=AS_OF,
        )
        assert before == (
            replay.draft.draft_id,
            replay.draft.activity_id,
            tuple((link.id, link.fee_item_id) for link in replay.draft.links),
        )
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1


def test_dirty_input_and_post_validation_fault_leave_no_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        transaction.add(FeeDraft(id="dirty-grant-year-policy"))
        with pytest.raises(BusinessError) as dirty:
            grant_fee_service.apply_grant_year_auto_draft_policy(
                transaction=transaction,
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                actor_id=review.actor_id,
                as_of=AS_OF,
            )
        assert dirty.value.status_code == 409
        transaction.rollback()

        monkeypatch.setattr(
            grant_fee_service,
            "prepare_draft",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("draft fault")),
        )
        with pytest.raises(RuntimeError, match="draft fault"):
            grant_fee_service.apply_grant_year_auto_draft_policy(
                transaction=transaction,
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                actor_id=review.actor_id,
                as_of=AS_OF,
            )
        transaction.rollback()
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
