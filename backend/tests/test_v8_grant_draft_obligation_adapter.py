from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass, replace
from typing import get_type_hints

import pytest
import test_v8_grant_official_fee_manual_review as manual
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    T_GrantFeeTask,
)
from app.modules.grant_fees import service as grant_fee_service


def _seed_ready(transaction: Session, *, label: str):
    seed = manual._seed(transaction, label=label)
    grant_fee_service.confirm_grant_official_fees(manual._command(seed), transaction)
    grant_fee_service.record_grant_fee_task_instruction(
        grant_fee_service.RecordGrantFeeTaskInstructionCommand(
            grant_fee_task_id=seed[2].id,
            source_activity_id=seed[4].activity_id,
            instruction="PAY",
            actor_id="grant-client-instruction-actor",
            idempotency_key=f"grant-draft-instruction:{label}",
        ),
        transaction,
    )
    transaction.commit()
    return seed


def _command(seed, **changes: object):
    values: dict[str, object] = {
        "grant_fee_task_id": seed[2].id,
        "source_activity_id": seed[4].activity_id,
        "actor_id": "grant-draft-actor",
        "idempotency_key": "grant-draft:one",
    }
    values.update(changes)
    return grant_fee_service.PrepareGrantFeeTaskDraftCommand(**values)


def _counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeItem)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationDraftItemLink)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED")
        )
        or 0,
    )


def _expect(code: str, status: int, action) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        action()
    assert caught.value.code == code
    assert caught.value.status_code == status
    return caught.value


def test_public_contract_is_exact_frozen_and_typed() -> None:
    command = grant_fee_service.PrepareGrantFeeTaskDraftCommand
    result = grant_fee_service.PrepareGrantFeeTaskDraftResult
    assert is_dataclass(command) and command.__dataclass_params__.frozen
    assert is_dataclass(result) and result.__dataclass_params__.frozen
    assert tuple(field.name for field in fields(command)) == (
        "grant_fee_task_id",
        "source_activity_id",
        "actor_id",
        "idempotency_key",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(command).parameters.values()
    )
    assert get_type_hints(grant_fee_service.prepare_grant_fee_task_draft) == {
        "command": command,
        "transaction": Session,
        "return": result,
    }


def test_exact_ready_obligation_delegates_once_and_reuses_deep_identities(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        seed = _seed_ready(transaction, label="SUCCESS")
        delegated: list[tuple[object, Session, object]] = []
        original = grant_fee_service.prepare_draft

        def capture(command: object, db: Session) -> object:
            result = original(command, db)
            delegated.append((command, db, result))
            return result

        monkeypatch.setattr(grant_fee_service, "prepare_draft", capture)
        command = _command(seed)
        result = grant_fee_service.prepare_grant_fee_task_draft(command, transaction)
        assert len(delegated) == 1
        deep_command, delegated_transaction, deep_result = delegated[0]
        assert delegated_transaction is transaction
        assert deep_command.obligation_id == seed[-2].id
        assert deep_command.actor_id == command.actor_id
        assert deep_command.idempotency_key == command.idempotency_key
        assert result.grant_fee_task_id == seed[2].id
        assert result.fee_obligation_id == deep_result.obligation_id
        assert result.draft_id == deep_result.draft_id
        assert result.links == deep_result.links
        assert result.activity_id == deep_result.activity_id
        assert result.activity_reused is False
        assert _counts(transaction) == (1, 1, 1, 1)
        task = transaction.get(T_GrantFeeTask, seed[2].id)
        assert task is not None and task.draft_generated is False

        transaction.commit()
        replay = grant_fee_service.prepare_grant_fee_task_draft(command, transaction)
        assert replay.draft_id == result.draft_id
        assert replay.activity_id == result.activity_id
        assert replay.activity_reused is True
        assert all(link.reused for link in replay.links)
        assert _counts(transaction) == (1, 1, 1, 1)


def test_missing_review_never_reaches_generic_writer(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        seed = manual._seed(transaction, label="NO-REVIEW")
        grant_fee_service.record_grant_fee_task_instruction(
            grant_fee_service.RecordGrantFeeTaskInstructionCommand(
                grant_fee_task_id=seed[2].id,
                source_activity_id=seed[4].activity_id,
                instruction="PAY",
                actor_id="grant-client-instruction-actor",
                idempotency_key="grant-draft-instruction:no-review",
            ),
            transaction,
        )
        transaction.commit()
        monkeypatch.setattr(
            grant_fee_service,
            "prepare_draft",
            lambda *_args: (_ for _ in ()).throw(AssertionError("must not delegate")),
        )
        _expect(
            "GRANT_DRAFT_LINEAGE_CONFLICT",
            409,
            lambda: grant_fee_service.prepare_grant_fee_task_draft(_command(seed), transaction),
        )
        assert _counts(transaction) == (0, 0, 0, 0)


def test_post_delegation_mismatch_rolls_back_adapter_savepoint(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        seed = _seed_ready(transaction, label="MISMATCH")
        original = grant_fee_service.prepare_draft

        def corrupt(command, db):
            result = original(command, db)
            return replace(result, draft_id="wrong-draft")

        monkeypatch.setattr(grant_fee_service, "prepare_draft", corrupt)
        _expect(
            "GRANT_DRAFT_LINK_NOT_FOUND",
            404,
            lambda: grant_fee_service.prepare_grant_fee_task_draft(_command(seed), transaction),
        )
        assert _counts(transaction) == (0, 0, 0, 0)
        obligation = transaction.get(FeeObligation, seed[-2].id)
        assert obligation is not None and obligation.draft_status == "NOT_CREATED"


def test_caller_rollback_removes_delegated_draft_without_legacy_task_mutation(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        seed = _seed_ready(transaction, label="ROLLBACK")
        task = transaction.get(T_GrantFeeTask, seed[2].id)
        assert task is not None
        before = (task.client_instruction, task.draft_generated, task.notify_count)
        grant_fee_service.prepare_grant_fee_task_draft(_command(seed), transaction)
        transaction.rollback()
        assert _counts(transaction) == (0, 0, 0, 0)
        task = transaction.get(T_GrantFeeTask, seed[2].id)
        obligation = transaction.get(FeeObligation, seed[-2].id)
        assert task is not None and obligation is not None
        assert (task.client_instruction, task.draft_generated, task.notify_count) == before
        assert obligation.draft_status == "NOT_CREATED"
