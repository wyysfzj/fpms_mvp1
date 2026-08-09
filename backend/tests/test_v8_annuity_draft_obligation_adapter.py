from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
import test_v8_annuity_instruction_obligation_adapter as task121
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.modules.annuity import service as annuity_service
from app.modules.annuity.models import AnnuityTask
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
)
from app.modules.fees.obligation_contracts import FeeObligationDraftStatus


def _prepare_pay_instruction(session_factory: sessionmaker) -> int:
    task_id = task121._seed(session_factory)
    with session_factory() as transaction:
        task121._record(task121._command(task_id), transaction)
        transaction.commit()
    return task_id


def _generate(
    transaction: Session,
    task_id: int,
) -> dict[str, Any]:
    return annuity_service.generate_fee_drafts_from_annuity_tasks(
        transaction,
        task_ids=[task_id],
        currency="CNY",
        actor_id=task121.ACTOR_ID,
    )


def _draft_counts(transaction: Session) -> tuple[int, int, int, int]:
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


def _forbid_prepare_draft() -> Callable[..., object]:
    def forbidden(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("invalid annuity selection must not reach prepare_draft")

    return forbidden


def test_selected_obligation_delegates_once_and_reuses_deep_identities(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _prepare_pay_instruction(session_factory)
    delegated: list[tuple[object, Session, object]] = []
    original = getattr(annuity_service, "prepare_draft", None)
    assert original is not None, "annuity draft adapter must import the deep prepare_draft seam"

    def capture(command: object, transaction: Session) -> object:
        result = original(command, transaction)
        delegated.append((command, transaction, result))
        return result

    monkeypatch.setattr(annuity_service, "prepare_draft", capture)
    with session_factory() as transaction:
        result = _generate(transaction, task_id)

        assert result["summary"] == {
            "requested": 1,
            "targets": 1,
            "success": 1,
            "failed": 0,
            "pay_next_year": False,
        }
        assert result["failed"] == []
        assert len(delegated) == 1
        command, delegated_transaction, deep_result = delegated[0]
        assert delegated_transaction is transaction
        assert command.obligation_id == task121.OBLIGATION_ID
        assert command.actor_id == task121.ACTOR_ID
        assert command.idempotency_key == (
            f"annuity-draft:{task_id}:{task121.OBLIGATION_ID}"
        )

        success = result["success"][0]
        assert success["obligation_id"] == deep_result.obligation_id
        assert success["draft_id"] == deep_result.draft_id
        assert success["activity_id"] == deep_result.activity_id
        assert success["activity_reused"] is deep_result.activity_reused is False
        assert success["idempotency_key"] == deep_result.idempotency_key
        assert success["links"] == [
            {
                "id": link.id,
                "obligation_line_id": link.obligation_line_id,
                "fee_item_id": link.fee_item_id,
                "reused": link.reused,
            }
            for link in deep_result.links
        ]
        assert _draft_counts(transaction) == (1, 1, 1, 1)
        task = transaction.get(AnnuityTask, task_id)
        assert task is not None
        assert task.draft_generated is False


def test_exact_replay_reuses_one_draft_link_and_activity(
    session_factory: sessionmaker,
) -> None:
    task_id = _prepare_pay_instruction(session_factory)
    with session_factory() as transaction:
        first = _generate(transaction, task_id)
        transaction.commit()
        before = _draft_counts(transaction)

        replay = _generate(transaction, task_id)

        first_success = first["success"][0]
        replay_success = replay["success"][0]
        assert replay_success["draft_id"] == first_success["draft_id"]
        assert replay_success["activity_id"] == first_success["activity_id"]
        assert [link["id"] for link in replay_success["links"]] == [
            link["id"] for link in first_success["links"]
        ]
        assert replay_success["activity_reused"] is True
        assert all(link["reused"] is True for link in replay_success["links"])
        assert _draft_counts(transaction) == before == (1, 1, 1, 1)


def test_caller_rollback_removes_draft_link_and_activity(
    session_factory: sessionmaker,
) -> None:
    task_id = _prepare_pay_instruction(session_factory)
    with session_factory() as transaction:
        result = _generate(transaction, task_id)
        assert result["summary"]["success"] == 1
        transaction.rollback()

    with session_factory() as verification:
        assert _draft_counts(verification) == (0, 0, 0, 0)
        obligation = verification.get(FeeObligation, task121.OBLIGATION_ID)
        task = verification.get(AnnuityTask, task_id)
        assert obligation is not None and task is not None
        assert obligation.draft_status == FeeObligationDraftStatus.NOT_CREATED.value
        assert task.draft_generated is False


def test_missing_obligation_selection_fails_closed_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _prepare_pay_instruction(session_factory)
    with session_factory() as transaction:
        task = transaction.get(AnnuityTask, task_id)
        assert task is not None
        (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        ) = (None, None, None, None, None, None)
        transaction.commit()

        monkeypatch.setattr(
            annuity_service,
            "prepare_draft",
            _forbid_prepare_draft(),
            raising=False,
        )
        result = _generate(transaction, task_id)

        assert result["summary"]["success"] == 0
        assert result["failed"][0]["code"] == "ANNUITY_INSTRUCTION_LINK_NOT_FOUND"
        assert _draft_counts(transaction) == (0, 0, 0, 0)


def test_mismatched_obligation_lineage_fails_closed_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _prepare_pay_instruction(session_factory)
    with session_factory() as transaction:
        transaction.execute(
            update(FeeObligationLine)
            .where(FeeObligationLine.id == task121.LINE_ID)
            .values(fee_year_key=5)
        )
        transaction.commit()

        monkeypatch.setattr(
            annuity_service,
            "prepare_draft",
            _forbid_prepare_draft(),
            raising=False,
        )
        result = _generate(transaction, task_id)

        assert result["summary"]["success"] == 0
        assert result["failed"][0]["code"] == "ANNUITY_INSTRUCTION_LINEAGE_CONFLICT"
        assert _draft_counts(transaction) == (0, 0, 0, 0)
