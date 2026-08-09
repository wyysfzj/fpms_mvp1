from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from dataclasses import fields, is_dataclass, replace
from datetime import date
from decimal import Decimal
from typing import Any, get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker
from test_v8_grant_notice_lifecycle_adapter import (
    _dispatch,
    _grant_fixture,
    _replacement_fixture,
)

from app.core.errors import BusinessError, raise_business_error
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import Document, DocumentEvidenceVersion
from app.modules.fees.models import (
    FeeDraft,
    FeeObligation,
    FeeObligationLine,
    T_GrantFeeTask,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    RecordFeeObligationInstructionCommand,
)
from app.modules.grant_fees import service as grant_fee_service

RecordGrantFeeTaskInstructionCommand = getattr(
    grant_fee_service,
    "RecordGrantFeeTaskInstructionCommand",
    None,
)
RecordGrantFeeTaskInstructionResult = getattr(
    grant_fee_service,
    "RecordGrantFeeTaskInstructionResult",
    None,
)
record_grant_fee_task_instruction = getattr(
    grant_fee_service,
    "record_grant_fee_task_instruction",
    None,
)


def _seed_chain(
    transaction: Session,
    *,
    label: str,
) -> tuple[str, str, str, str, str]:
    case, document, task, evidence = _grant_fixture(transaction, label=label)
    lifecycle = _dispatch(
        transaction,
        task=task,
        document=document,
        evidence=evidence,
        idempotency_key=f"grant-instruction-source:{label}:{uuid4()}",
    )
    recognition = grant_fee_service.recognize_grant_year_annuity_obligation(
        grant_fee_service.RecognizeGrantYearAnnuityObligationCommand(
            grant_fee_task_id=task.id,
            source_activity_id=lifecycle.activity_id,
            actor_id=str(uuid4()),
            idempotency_key=f"grant-instruction-recognition:{label}:{uuid4()}",
        ),
        transaction,
    )
    transaction.commit()
    return case.id, document.id, task.id, lifecycle.activity_id, recognition.obligation.id


def _command(task_id: str, activity_id: str, **changes: object) -> Any:
    assert RecordGrantFeeTaskInstructionCommand is not None
    values: dict[str, object] = {
        "grant_fee_task_id": task_id,
        "source_activity_id": activity_id,
        "instruction": "PAY",
        "actor_id": "grant-instruction-actor",
        "idempotency_key": "grant-instruction:pay",
    }
    values.update(changes)
    return RecordGrantFeeTaskInstructionCommand(**values)


def _record(command: object, transaction: Session) -> Any:
    assert record_grant_fee_task_instruction is not None
    return record_grant_fee_task_instruction(command, transaction)


def _expect_error(
    code: str,
    status_code: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        action()
    assert caught.value.code == code
    assert caught.value.status_code == status_code
    return caught.value


def _instruction_activities(transaction: Session) -> tuple[CaseActivityEvent, ...]:
    return tuple(
        transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED"
            )
        )
    )


def _recognition(transaction: Session, obligation_id: str) -> CaseActivityEvent:
    matches = []
    for activity in transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.activity_type == "FEE_OBLIGATION_RECOGNIZED"
        )
    ):
        payload = json.loads(activity.payload_json)
        if payload.get("obligation_id") == obligation_id:
            matches.append(activity)
    assert len(matches) == 1
    return matches[0]


def _snapshot(
    transaction: Session,
    *,
    case_id: str,
    document_id: str,
    task_id: str,
    obligation_id: str,
) -> tuple[object, ...]:
    case = transaction.get(Case, case_id)
    document = transaction.get(Document, document_id)
    task = transaction.get(T_GrantFeeTask, task_id)
    obligation = transaction.get(FeeObligation, obligation_id)
    evidence = transaction.scalar(
        select(DocumentEvidenceVersion).where(DocumentEvidenceVersion.document_id == document_id)
    )
    assert all(value is not None for value in (case, document, task, obligation, evidence))
    return (
        task.client_instruction,
        task.notify_count,
        task.draft_generated,
        task.notice_sent,
        task.is_overdue,
        task.due_date,
        task.deadline_source,
        task.deadline_confirmed_at,
        task.gov_fee_amt,
        task.service_fee_amt,
        task.currency,
        task.source_document_id,
        document.title,
        document.extra_data,
        evidence.content_hash,
        evidence.current_identity_key,
        case.status,
        case.business_stage,
        case.official_procedure_stage,
        case.legal_status,
        case.lifecycle_verification_status,
        obligation.client_instruction_status,
        transaction.scalar(select(func.count()).select_from(FeeDraft)),
        transaction.scalar(select(func.count()).select_from(PayList)),
        transaction.scalar(select(func.count()).select_from(GovPayment)),
        transaction.scalar(select(func.count()).select_from(Document)),
        transaction.scalar(select(func.count()).select_from(DocumentEvidenceVersion)),
        transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
    )


def test_public_contract_is_exact_frozen_slotted_and_typed() -> None:
    assert RecordGrantFeeTaskInstructionCommand is not None
    assert RecordGrantFeeTaskInstructionResult is not None
    assert record_grant_fee_task_instruction is not None
    assert is_dataclass(RecordGrantFeeTaskInstructionCommand)
    assert RecordGrantFeeTaskInstructionCommand.__dataclass_params__.frozen is True
    assert RecordGrantFeeTaskInstructionCommand.__slots__ == (
        "grant_fee_task_id",
        "source_activity_id",
        "instruction",
        "actor_id",
        "idempotency_key",
    )
    assert tuple(field.name for field in fields(RecordGrantFeeTaskInstructionCommand)) == (
        "grant_fee_task_id",
        "source_activity_id",
        "instruction",
        "actor_id",
        "idempotency_key",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(RecordGrantFeeTaskInstructionCommand).parameters.values()
    )
    assert list(inspect.signature(record_grant_fee_task_instruction).parameters) == [
        "command",
        "transaction",
    ]
    assert get_type_hints(record_grant_fee_task_instruction) == {
        "command": RecordGrantFeeTaskInstructionCommand,
        "transaction": Session,
        "return": RecordGrantFeeTaskInstructionResult,
    }


@pytest.mark.parametrize("instruction", ["PAY", "HOLD", "ABANDON"])
def test_exact_mapping_delegates_once_and_preserves_every_non_goal(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    instruction: str,
) -> None:
    delegated: list[tuple[RecordFeeObligationInstructionCommand, Session]] = []
    original = grant_fee_service.record_client_instruction

    def record_once(
        command: RecordFeeObligationInstructionCommand,
        transaction: Session,
    ) -> object:
        delegated.append((command, transaction))
        return original(command, transaction)

    monkeypatch.setattr(grant_fee_service, "record_client_instruction", record_once)
    with session_factory() as transaction:
        case_id, document_id, task_id, activity_id, obligation_id = _seed_chain(
            transaction,
            label=f"MAP-{instruction}",
        )
        before = _snapshot(
            transaction,
            case_id=case_id,
            document_id=document_id,
            task_id=task_id,
            obligation_id=obligation_id,
        )
        key = f"grant-instruction:{instruction.lower()}"
        result = _record(
            _command(
                task_id,
                activity_id,
                instruction=instruction,
                idempotency_key=key,
            ),
            transaction,
        )
        after = _snapshot(
            transaction,
            case_id=case_id,
            document_id=document_id,
            task_id=task_id,
            obligation_id=obligation_id,
        )
        assert type(result) is RecordGrantFeeTaskInstructionResult
        assert result.grant_fee_task_id == task_id
        assert result.fee_obligation_id == obligation_id
        assert result.instruction is FeeClientInstruction(instruction)
        assert result.idempotency_key == key
        assert result.reused is False
        assert len(delegated) == 1
        delegated_command, delegated_transaction = delegated[0]
        assert delegated_transaction is transaction
        assert delegated_command == RecordFeeObligationInstructionCommand(
            obligation_id=obligation_id,
            instruction=FeeClientInstruction(instruction),
            actor_id="grant-instruction-actor",
            idempotency_key=key,
        )
        assert before[:21] == after[:21]
        assert before[22:] == after[22:]
        assert after[21] == instruction
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        assert activity.source_activity_id == _recognition(transaction, obligation_id).id
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == result.activity_id)
            )
            == 0
        )


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"grant_fee_task_id": ""}, "grant_fee_task_id"),
        ({"grant_fee_task_id": " task"}, "grant_fee_task_id"),
        ({"grant_fee_task_id": "x" * 37}, "grant_fee_task_id"),
        ({"source_activity_id": "\x00"}, "source_activity_id"),
        ({"instruction": "pay"}, "instruction"),
        ({"instruction": "DEFER"}, "instruction"),
        ({"instruction": FeeClientInstruction.PAY}, "instruction"),
        ({"actor_id": " actor"}, "actor_id"),
        ({"actor_id": "x" * 37}, "actor_id"),
        ({"idempotency_key": ""}, "idempotency_key"),
        ({"idempotency_key": "x" * 129}, "idempotency_key"),
    ],
)
def test_command_validation_is_strict_ordered_and_query_free(
    session_factory: sessionmaker,
    changes: dict[str, object],
    field: str,
) -> None:
    with session_factory() as transaction:
        error = _expect_error(
            "GRANT_INSTRUCTION_COMMAND_INVALID",
            400,
            lambda: _record(_command("task", "activity", **changes), transaction),
        )
        assert error.details == {"field": field}
        assert _instruction_activities(transaction) == ()


def test_wrong_command_type_and_dirty_transaction_fail_before_lookup(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        error = _expect_error(
            "GRANT_INSTRUCTION_COMMAND_INVALID",
            400,
            lambda: _record(object(), transaction),
        )
        assert error.details == {"field": "command"}
    with session_factory() as transaction:
        transaction.add(Case(id=str(uuid4()), case_no=str(uuid4()), status="OPEN"))
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command("task", "activity"), transaction),
        )


def test_named_task_and_activity_are_selected_instead_of_latest(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        first = _seed_chain(transaction, label="NAMED-FIRST")
        second = _seed_chain(transaction, label="NAMED-SECOND")
        result = _record(_command(first[2], first[3]), transaction)
        assert result.grant_fee_task_id == first[2]
        assert result.fee_obligation_id == first[4]
        assert transaction.get(FeeObligation, first[4]).client_instruction_status == "PAY"
        assert transaction.get(FeeObligation, second[4]).client_instruction_status == "PENDING"
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(
                _command(
                    first[2],
                    second[3],
                    idempotency_key="grant-instruction:cross-named",
                ),
                transaction,
            ),
        )


def test_missing_task_activity_obligation_or_recognition_is_404(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _expect_error(
            "GRANT_INSTRUCTION_TASK_NOT_FOUND",
            404,
            lambda: _record(_command("missing-task", "missing-activity"), transaction),
        )
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="MISSING-ACTIVITY")
        _expect_error(
            "GRANT_INSTRUCTION_LINK_NOT_FOUND",
            404,
            lambda: _record(_command(chain[2], "missing-activity"), transaction),
        )
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="MISSING-OBLIGATION")
        obligation = transaction.get(FeeObligation, chain[4])
        assert obligation is not None
        for line in tuple(
            transaction.scalars(
                select(FeeObligationLine).where(FeeObligationLine.obligation_id == obligation.id)
            )
        ):
            transaction.delete(line)
        transaction.delete(obligation)
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINK_NOT_FOUND",
            404,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="MISSING-RECOGNITION")
        _recognition(transaction, chain[4]).activity_type = "OTHER_FEE_ACTIVITY"
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINK_NOT_FOUND",
            404,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )


def test_multiple_obligations_or_recognitions_are_409_without_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(grant_fee_service, "record_client_instruction", calls.append)
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="MULTIPLE-OBLIGATIONS")
        original = transaction.get(FeeObligation, chain[4])
        assert original is not None
        transaction.add(
            FeeObligation(
                id=str(uuid4()),
                case_id=original.case_id,
                source_activity_id=original.source_activity_id,
                source_document_id=original.source_document_id,
                fee_domain=original.fee_domain,
                obligation_type=original.obligation_type,
                obligation_status=original.obligation_status,
                due_date=original.due_date,
                currency=original.currency,
                source_status=original.source_status,
                client_instruction_status="PENDING",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="PENDING",
            )
        )
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="MULTIPLE-RECOGNITIONS")
        original = _recognition(transaction, chain[4])
        duplicate = CaseActivityEvent(
            id=str(uuid4()),
            case_id=original.case_id,
            sequence=original.sequence + 1,
            lane=original.lane,
            activity_type=original.activity_type,
            source_activity_id=original.source_activity_id,
            occurred_at=original.occurred_at,
            effective_at=original.effective_at,
            confirmation_status=original.confirmation_status,
            old_business_stage=original.old_business_stage,
            new_business_stage=original.new_business_stage,
            old_official_procedure_stage=original.old_official_procedure_stage,
            new_official_procedure_stage=original.new_official_procedure_stage,
            old_legal_status=original.old_legal_status,
            new_legal_status=original.new_legal_status,
            actor_id=original.actor_id,
            reviewer_id=original.reviewer_id,
            idempotency_key=str(uuid4()),
            supersedes_event_id=original.supersedes_event_id,
            payload_json=original.payload_json,
        )
        transaction.add(duplicate)
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []


@pytest.mark.parametrize(
    ("target", "field", "value"),
    [
        ("task", "type", "OTHER"),
        ("task", "due_date", date(2026, 9, 28)),
        ("activity", "confirmation_status", "PENDING"),
        ("obligation", "fee_domain", "SERVICE"),
        ("obligation", "currency", "USD"),
        ("obligation", "source_status", "REVIEW_REQUIRED"),
        ("obligation", "source_document_id", None),
        ("obligation", "due_date", date(2026, 9, 28)),
        ("line", "fee_code", "WRONG"),
        ("line", "fee_name", "错误年费"),
        ("line", "official_full_amount", Decimal("900.00")),
        ("line", "reduction_ratio", Decimal("0.7000")),
        ("line", "payable_amount", Decimal("901.00")),
        ("line", "source_amount", Decimal("901.00")),
        ("line", "source_date", date(2026, 9, 27)),
        ("line", "difference_review_state", "MATCHED"),
        ("line", "current_identity_key", None),
    ],
)
def test_every_notice_and_row130_projection_divergence_fails_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    field: str,
    value: object,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(grant_fee_service, "record_client_instruction", calls.append)
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label=f"DIVERGENCE-{target}-{field}")
        selected: object
        if target == "task":
            selected = transaction.get(T_GrantFeeTask, chain[2])
        elif target == "activity":
            selected = transaction.get(CaseActivityEvent, chain[3])
        elif target == "obligation":
            selected = transaction.get(FeeObligation, chain[4])
        else:
            selected = transaction.scalar(
                select(FeeObligationLine).where(FeeObligationLine.obligation_id == chain[4])
            )
        assert selected is not None
        setattr(selected, field, value)
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []


def test_notice_snapshot_evidence_and_direct_correction_lineage_are_revalidated(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    monkeypatch.setattr(grant_fee_service, "record_client_instruction", calls.append)
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="NOTICE-HASH")
        activity = transaction.get(CaseActivityEvent, chain[3])
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["grant_fee_lines_snapshot_hash"] = "b" * 64
        activity.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="NOTICE-EVIDENCE")
        link = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == chain[3]
            )
        )
        assert link is not None
        link.content_hash = f"sha256:{'b' * 64}"
        transaction.commit()
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []


def test_current_correction_and_historical_exact_replay_resolve_exact_identity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case_id, document_id, task_id, activity_id, obligation_id = _seed_chain(
            transaction,
            label="CORRECTION-ORIGINAL",
        )
        original_command = _command(task_id, activity_id)
        original_instruction = _record(original_command, transaction)
        transaction.commit()
        case = transaction.get(Case, case_id)
        original_task = transaction.get(T_GrantFeeTask, task_id)
        assert case is not None and original_task is not None
        corrected_document, corrected_task, corrected_evidence = _replacement_fixture(
            transaction,
            case=case,
            predecessor_task=original_task,
            label="INSTRUCTION",
        )
        corrected_lifecycle = _dispatch(
            transaction,
            task=corrected_task,
            document=corrected_document,
            evidence=corrected_evidence,
            idempotency_key="grant-instruction-correction-source",
        )
        corrected_recognition = grant_fee_service.recognize_grant_year_annuity_obligation(
            grant_fee_service.RecognizeGrantYearAnnuityObligationCommand(
                grant_fee_task_id=corrected_task.id,
                source_activity_id=corrected_lifecycle.activity_id,
                actor_id=str(uuid4()),
                idempotency_key="grant-instruction-correction-recognition",
            ),
            transaction,
        )
        transaction.commit()
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(
                _command(corrected_task.id, corrected_lifecycle.activity_id),
                transaction,
            ),
        )
        corrected_instruction = _record(
            _command(
                corrected_task.id,
                corrected_lifecycle.activity_id,
                instruction="HOLD",
                idempotency_key="grant-instruction:correction-hold",
            ),
            transaction,
        )
        historical_replay = _record(original_command, transaction)
        assert corrected_instruction.fee_obligation_id == corrected_recognition.obligation.id
        assert corrected_instruction.instruction is FeeClientInstruction.HOLD
        assert historical_replay.reused is True
        assert historical_replay.activity_id == original_instruction.activity_id
        assert historical_replay.fee_obligation_id == obligation_id
        assert document_id != corrected_document.id


def test_broken_historical_correction_identity_is_409_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="BROKEN-CORRECTION")
        case = transaction.get(Case, chain[0])
        original_task = transaction.get(T_GrantFeeTask, chain[2])
        assert case is not None and original_task is not None
        corrected_document, corrected_task, corrected_evidence = _replacement_fixture(
            transaction,
            case=case,
            predecessor_task=original_task,
            label="BROKEN",
        )
        corrected_lifecycle = _dispatch(
            transaction,
            task=corrected_task,
            document=corrected_document,
            evidence=corrected_evidence,
            idempotency_key="grant-instruction-broken-source",
        )
        grant_fee_service.recognize_grant_year_annuity_obligation(
            grant_fee_service.RecognizeGrantYearAnnuityObligationCommand(
                grant_fee_task_id=corrected_task.id,
                source_activity_id=corrected_lifecycle.activity_id,
                actor_id=str(uuid4()),
                idempotency_key="grant-instruction-broken-recognition",
            ),
            transaction,
        )
        transaction.commit()
        original_task.superseded_by_task_id = None
        transaction.commit()
        calls: list[object] = []
        monkeypatch.setattr(grant_fee_service, "record_client_instruction", calls.append)
        _expect_error(
            "GRANT_INSTRUCTION_LINEAGE_CONFLICT",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert calls == []


def test_replay_collisions_and_new_key_same_state_preserve_deep_codes(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="REPLAY")
        command = _command(chain[2], chain[3])
        created = _record(command, transaction)
        transaction.commit()
        replay = _record(command, transaction)
        assert replay.reused is True
        assert replay.activity_id == created.activity_id
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(replace(command, actor_id="different-actor"), transaction),
        )
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(replace(command, instruction="HOLD"), transaction),
        )
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_SAME_STATE",
            409,
            lambda: _record(
                replace(command, idempotency_key="grant-instruction:pay:new"),
                transaction,
            ),
        )


def test_caller_rollback_and_forced_deep_failure_are_write_free(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="ROLLBACK")
        case = transaction.get(Case, chain[0])
        obligation = transaction.get(FeeObligation, chain[4])
        assert case is not None and obligation is not None
        revision = case.lifecycle_revision
        _record(_command(chain[2], chain[3]), transaction)
        transaction.rollback()
    with session_factory() as verification:
        case = verification.get(Case, chain[0])
        obligation = verification.get(FeeObligation, chain[4])
        assert case is not None and obligation is not None
        assert case.lifecycle_revision == revision
        assert obligation.client_instruction_status == "PENDING"
        assert _instruction_activities(verification) == ()

    def fail_deep(*_args: object, **_kwargs: object) -> object:
        raise_business_error(
            "FORCED_DEEP_FAILURE",
            "强制深层失败",
            details={"preserved": "yes"},
            status_code=409,
        )

    monkeypatch.setattr(grant_fee_service, "record_client_instruction", fail_deep)
    with session_factory() as transaction:
        chain = _seed_chain(transaction, label="DEEP-FAILURE")
        before = _snapshot(
            transaction,
            case_id=chain[0],
            document_id=chain[1],
            task_id=chain[2],
            obligation_id=chain[4],
        )
        error = _expect_error(
            "FORCED_DEEP_FAILURE",
            409,
            lambda: _record(_command(chain[2], chain[3]), transaction),
        )
        assert error.details == {"preserved": "yes"}
        assert (
            _snapshot(
                transaction,
                case_id=chain[0],
                document_id=chain[1],
                task_id=chain[2],
                obligation_id=chain[4],
            )
            == before
        )
