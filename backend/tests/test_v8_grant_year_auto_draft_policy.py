from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest
import test_v8_grant_official_fee_manual_review as manual
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.annuity.service import create_pay_list_from_fee_items
from app.modules.auth.models import T_User
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import FeeDraft, FeeItem, FeeObligation
from app.modules.fees.obligation_contracts import (
    FeeDraftAuthority,
    PrepareFeeObligationDraftCommand,
)
from app.modules.fees.obligation_service import get_fee_obligation, prepare_draft
from app.modules.grant_fees import service as grant_fee_service
from app.modules.masterdata.clients.models import Client
from app.modules.system.decision_gate_service import DecisionGateCode
from app.modules.system.models import CustomerDecisionGate

DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
AS_OF = datetime(2026, 8, 10, 13, 0)


def _seed_ready(transaction: Session, *, gate: bool = True):
    seed = manual._seed(transaction, label="GRANT-YEAR-AUTO-DRAFT")
    if seed[0].client_id is None:
        transaction.add(
            Client(
                id="client-grant-year-auto-draft",
                client_code="GRANT-AUTO",
                name_cn="授权年费草单客户",
            )
        )
        transaction.flush()
        seed[0].client_id = "client-grant-year-auto-draft"
        transaction.commit()
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


@pytest.mark.parametrize(
    "gate_state",
    ("missing", "revoked", "future", "wrong-source", "wrong-version", "corrupt", "fallback"),
)
def test_unusable_gate_is_409_before_draft_write(
    session_factory: sessionmaker,
    gate_state: str,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction, gate=gate_state != "missing")
        gate = transaction.get(CustomerDecisionGate, "gate-grant-year-auto-draft")
        if gate is not None:
            if gate_state == "revoked":
                gate.decision_status = "REVOKED"
            elif gate_state == "future":
                gate.effective_at = AS_OF + timedelta(seconds=1)
            elif gate_state == "wrong-source":
                gate.source_reference = "wrong-source"
            elif gate_state == "wrong-version":
                gate.source_version = "wrong-version"
            elif gate_state == "corrupt":
                gate.decision_value = ""
            elif gate_state == "fallback":
                gate.scope_key = f"case:{seed[0].id}"
                gate.current_identity_key = f"DG-FEE-GRANT-YEAR-DRAFT|case:{seed[0].id}"
            transaction.commit()
        with pytest.raises(BusinessError) as raised:
            grant_fee_service.apply_grant_year_auto_draft_policy(
                transaction=transaction,
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                actor_id=review.actor_id,
                as_of=AS_OF,
            )
        assert raised.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeItem)) == 0


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
        with pytest.raises(BusinessError) as pre_pay:
            create_pay_list_from_fee_items(
                transaction,
                fee_item_ids=[link.fee_item_id for link in result.draft.links],
                actor_id=review.actor_id,
            )
        assert pre_pay.value.code == "PAY_LIST_CLIENT_INSTRUCTION_REQUIRED"
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
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
        calls: list[str] = []
        monkeypatch.setattr(
            grant_fee_service,
            "resolve_decision_gate",
            lambda *_args, **_kwargs: calls.append("gate"),
        )
        monkeypatch.setattr(
            grant_fee_service,
            "_grant_year_policy_recognition",
            lambda **_kwargs: calls.append("recognition"),
        )
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
        assert calls == []
        transaction.rollback()

        monkeypatch.undo()

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


def test_direct_deep_authority_rejects_corrupt_review_graph(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        activity = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "GRANT_YEAR_OFFICIAL_FEE_REVIEW_CONFIRMED"
            )
        )
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["after_lines"][0]["official_full_amount"] = "2222.00"
        activity.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.commit()

        with pytest.raises(BusinessError) as corrupt:
            prepare_draft(
                PrepareFeeObligationDraftCommand(
                    obligation_id=seed[-2].id,
                    actor_id=review.actor_id,
                    idempotency_key=(f"grant-year-auto-draft:{seed[2].id}:{seed[4].activity_id}"),
                    authority=FeeDraftAuthority.REVIEWED_GRANT_YEAR_NOTICE,
                ),
                transaction,
            )
        assert corrupt.value.code == "FEE_OBLIGATION_DRAFT_STORED_STATE_INVALID"
        assert corrupt.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_successful_policy_remains_caller_owned_and_rolls_back(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed, review = _seed_ready(transaction)
        grant_fee_service.apply_grant_year_auto_draft_policy(
            transaction=transaction,
            grant_fee_task_id=seed[2].id,
            source_activity_id=seed[4].activity_id,
            actor_id=review.actor_id,
            as_of=AS_OF,
        )
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        transaction.rollback()
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeItem)) == 0


def test_draft_only_read_rejects_non_pay_instruction_state(
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
        obligation = transaction.get(FeeObligation, result.recognition.obligation.id)
        assert obligation is not None
        obligation.client_instruction_status = "HOLD"
        transaction.commit()

        with pytest.raises(BusinessError) as corrupt:
            get_fee_obligation(obligation.id, transaction)
        assert corrupt.value.code == "FEE_OBLIGATION_STORED_STATE_INVALID"
        assert corrupt.value.status_code == 409


def test_draft_only_read_requires_pending_official_evidence(
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
        obligation = transaction.get(FeeObligation, result.recognition.obligation.id)
        assert obligation is not None
        obligation.official_evidence_status = "NOT_APPLICABLE"
        transaction.commit()

        with pytest.raises(BusinessError) as corrupt:
            get_fee_obligation(obligation.id, transaction)
        assert corrupt.value.code == "FEE_OBLIGATION_STORED_STATE_INVALID"
        assert corrupt.value.status_code == 409
