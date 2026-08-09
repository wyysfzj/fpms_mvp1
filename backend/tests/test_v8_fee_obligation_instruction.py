from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from importlib import import_module, util
from inspect import Parameter, signature
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import patch

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
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.fees.models import FeeObligation as FeeObligationModel
from app.modules.fees.models import FeeObligationLine as FeeObligationLineModel
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
    RecordFeeObligationInstructionCommand,
    RecordFeeObligationInstructionResult,
)

SERVICE_MODULE = "app.modules.fees.obligation_service"
SERVICE_SPEC = util.find_spec(SERVICE_MODULE)

CASE_ID = "case-fee-instruction"
GRANT_SOURCE_ID = "grant-source-fee-instruction"
RECOGNITION_ID = "recognition-fee-instruction"
OBLIGATION_ID = "obligation-fee-instruction"
LINE_ID = "line-fee-instruction"
ACTOR_ID = "actor-fee-instruction"


def _seed_recognized_obligation(transaction: Session) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="NO-FEE-INSTRUCTION",
            status="OPEN",
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            legal_status=LegalStatus.APPLICATION_PENDING.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=1,
        )
    )
    transaction.add(
        CaseActivityEvent(
            id=RECOGNITION_ID,
            case_id=CASE_ID,
            sequence=1,
            lane=ActivityLane.FEE.value,
            activity_type="FEE_OBLIGATION_RECOGNIZED",
            source_activity_id=None,
            occurred_at=datetime(2026, 7, 13, 9, 55),
            effective_at=datetime(2026, 7, 13, 10, 0),
            confirmation_status=ConfirmationStatus.CONFIRMED.value,
            old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            old_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
            new_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
            old_legal_status=LegalStatus.APPLICATION_PENDING.value,
            new_legal_status=LegalStatus.APPLICATION_PENDING.value,
            actor_id=ACTOR_ID,
            reviewer_id=None,
            idempotency_key="recognize:fee-instruction",
            supersedes_event_id=None,
            payload_json=json.dumps(
                {
                    "obligation_id": OBLIGATION_ID,
                    "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    )
    transaction.add(
        FeeObligationModel(
            id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=RECOGNITION_ID,
            source_document_id=None,
            fee_domain="SERVICE",
            obligation_type="PATENT_APPLICATION",
            obligation_status=FeeObligationStatus.RECOGNIZED.value,
            due_date=date(2026, 8, 13),
            currency="CNY",
            source_status="VERIFIED",
            client_instruction_status=FeeClientInstructionStatus.PENDING.value,
            draft_status=FeeObligationDraftStatus.NOT_CREATED.value,
            payment_status=FeePaymentStatus.UNPAID.value,
            official_evidence_status=FeeOfficialEvidenceStatus.NOT_APPLICABLE.value,
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    transaction.add(
        FeeObligationLineModel(
            id=LINE_ID,
            obligation_id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=RECOGNITION_ID,
            fee_code="SERVICE-FILING",
            fee_name="申请服务费",
            fee_year_key=0,
            official_full_amount=None,
            reduction_ratio=Decimal("0.0000"),
            payable_amount=Decimal("1000.00"),
            source_amount=Decimal("1000.00"),
            source_date=date(2026, 7, 13),
            difference_review_state=FeeDifferenceReviewState.MATCHED.value,
            current_identity_key="instruction-line-identity",
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    transaction.commit()


def _command(
    instruction: FeeClientInstruction = FeeClientInstruction.PAY,
    *,
    actor_id: str = ACTOR_ID,
    idempotency_key: str = "instruction:pay",
) -> RecordFeeObligationInstructionCommand:
    return RecordFeeObligationInstructionCommand(
        obligation_id=OBLIGATION_ID,
        instruction=instruction,
        actor_id=actor_id,
        idempotency_key=idempotency_key,
    )


def _record(
    command: RecordFeeObligationInstructionCommand,
    transaction: Session,
) -> RecordFeeObligationInstructionResult:
    assert SERVICE_SPEC is not None
    return import_module(SERVICE_MODULE).record_client_instruction(command, transaction)


def _expect_error(
    code: str,
    status_code: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.code == code
    assert captured.value.status_code == status_code
    return captured.value


def _instruction_activities(transaction: Session) -> list[CaseActivityEvent]:
    return list(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED")
            .order_by(CaseActivityEvent.sequence)
        )
    )


@pytest.mark.parametrize(
    "instruction",
    (
        FeeClientInstruction.PAY,
        FeeClientInstruction.HOLD,
        FeeClientInstruction.ABANDON,
    ),
)
def test_service_exposes_exact_callable_and_records_each_instruction_fact(
    session_factory: sessionmaker,
    instruction: FeeClientInstruction,
) -> None:
    assert SERVICE_SPEC is not None
    record_client_instruction = import_module(SERVICE_MODULE).record_client_instruction
    parameters = tuple(signature(record_client_instruction).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == ("command", "transaction")
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
    )
    assert get_type_hints(record_client_instruction) == {
        "command": RecordFeeObligationInstructionCommand,
        "transaction": Session,
        "return": RecordFeeObligationInstructionResult,
    }

    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        result = _record(
            _command(
                instruction,
                idempotency_key=f"instruction:{instruction.value.lower()}",
            ),
            transaction,
        )

        assert type(result) is RecordFeeObligationInstructionResult
        assert result.reused is False
        assert result.idempotency_key == f"instruction:{instruction.value.lower()}"
        assert result.obligation.statuses.client_instruction_status is FeeClientInstructionStatus(
            instruction.value
        )
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        assert header.client_instruction_status == instruction.value
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        assert activity.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED"
        assert activity.lane == ActivityLane.FEE.value
        assert activity.source_activity_id == RECOGNITION_ID
        assert activity.supersedes_event_id is None
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert json.loads(activity.payload_json) == {
            "actor_id": ACTOR_ID,
            "instruction": instruction.value,
            "obligation_id": OBLIGATION_ID,
            "previous_instruction_status": "PENDING",
            "schema": "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1",
        }
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 2
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert (
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.status,
        ) == (
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            ConfirmationStatus.CONFIRMED.value,
            "OPEN",
        )


def test_changed_instruction_supersedes_immediately_previous_fact(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        first = _record(_command(), transaction)
        second = _record(
            _command(FeeClientInstruction.HOLD, idempotency_key="instruction:hold"),
            transaction,
        )

        assert second.reused is False
        activities = _instruction_activities(transaction)
        assert [item.id for item in activities] == [first.activity_id, second.activity_id]
        assert activities[1].source_activity_id == RECOGNITION_ID
        assert activities[1].supersedes_event_id == first.activity_id
        assert json.loads(activities[1].payload_json)["previous_instruction_status"] == "PAY"
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        assert header.client_instruction_status == "HOLD"


def test_replay_returns_original_fact_after_later_instruction_and_lock(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        first = _record(_command(), transaction)
        _record(
            _command(FeeClientInstruction.HOLD, idempotency_key="instruction:hold"),
            transaction,
        )
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        header.payment_status = FeePaymentStatus.PAID.value
        transaction.commit()
        before = (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.get(Case, CASE_ID).lifecycle_revision,
        )

        replay = _record(_command(), transaction)

        assert replay.reused is True
        assert replay.activity_id == first.activity_id
        assert (
            replay.obligation.statuses.client_instruction_status is FeeClientInstructionStatus.HOLD
        )
        assert replay.obligation.statuses.payment_status is FeePaymentStatus.PAID
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.get(Case, CASE_ID).lifecycle_revision,
        ) == before


def test_replay_rejects_corrupted_immediately_previous_instruction_fact(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        pay = _record(_command(), transaction)
        hold_command = _command(
            FeeClientInstruction.HOLD,
            idempotency_key="instruction:hold",
        )
        hold = _record(hold_command, transaction)
        transaction.commit()

        prior = transaction.get(CaseActivityEvent, pay.activity_id)
        current = transaction.get(CaseActivityEvent, hold.activity_id)
        assert prior is not None and current is not None
        assert current.supersedes_event_id == prior.id
        assert current.sequence == prior.sequence + 1
        assert prior.case_id == current.case_id == CASE_ID
        assert prior.lane == current.lane == ActivityLane.FEE.value
        assert prior.activity_type == current.activity_type == ("FEE_CLIENT_INSTRUCTION_RECORDED")
        assert prior.source_activity_id == current.source_activity_id == RECOGNITION_ID
        assert (
            prior.confirmation_status
            == current.confirmation_status
            == (ConfirmationStatus.CONFIRMED.value)
        )
        assert prior.actor_id == json.loads(prior.payload_json)["actor_id"]
        assert prior.reviewer_id is None
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == prior.id)
            )
            == 0
        )

        prior.activity_type = "CORRUPTED_NOT_AN_INSTRUCTION"
        transaction.commit()
        before = (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.get(Case, CASE_ID).lifecycle_revision,
            transaction.get(FeeObligationModel, OBLIGATION_ID).client_instruction_status,
        )

        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(hold_command, transaction),
        )

        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            transaction.get(Case, CASE_ID).lifecycle_revision,
            transaction.get(FeeObligationModel, OBLIGATION_ID).client_instruction_status,
        ) == before


def test_same_state_with_new_key_is_not_a_replay(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        _record(_command(), transaction)
        before = len(_instruction_activities(transaction))

        error = _expect_error(
            "FEE_CLIENT_INSTRUCTION_SAME_STATE",
            409,
            lambda: _record(_command(idempotency_key="instruction:pay:new"), transaction),
        )

        assert error.message == "客户费用指示已处于目标状态"
        assert len(_instruction_activities(transaction)) == before


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("obligation_status", FeeObligationStatus.SUPERSEDED.value),
        ("draft_status", FeeObligationDraftStatus.CREATED.value),
        ("payment_status", FeePaymentStatus.PAID.value),
        ("official_evidence_status", FeeOfficialEvidenceStatus.VERIFIED.value),
    ),
)
def test_downstream_or_supersede_state_locks_instruction(
    session_factory: sessionmaker,
    field: str,
    value: str,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        setattr(header, field, value)
        transaction.commit()

        error = _expect_error(
            "FEE_CLIENT_INSTRUCTION_LOCKED",
            409,
            lambda: _record(_command(), transaction),
        )

        assert error.message == "当前费用义务已锁定，不能修改客户指示"
        assert error.details == {
            "obligation_id": OBLIGATION_ID,
            "obligation_status": header.obligation_status,
            "draft_status": header.draft_status,
            "payment_status": header.payment_status,
            "official_evidence_status": header.official_evidence_status,
        }
        assert _instruction_activities(transaction) == []


@pytest.mark.parametrize(
    ("command", "field"),
    (
        (object(), "command"),
        (replace(_command(), obligation_id=""), "obligation_id"),
        (replace(_command(), obligation_id="x" * 37), "obligation_id"),
        (replace(_command(), instruction="PAY"), "instruction"),
        (replace(_command(), actor_id=" "), "actor_id"),
        (replace(_command(), actor_id="x" * 37), "actor_id"),
        (replace(_command(), idempotency_key=""), "idempotency_key"),
        (replace(_command(), idempotency_key="x" * 129), "idempotency_key"),
    ),
)
def test_command_validation_is_strict_and_ordered(
    session_factory: sessionmaker,
    command: object,
    field: str,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        error = _expect_error(
            "FEE_CLIENT_INSTRUCTION_COMMAND_INVALID",
            400,
            lambda: _record(command, transaction),  # type: ignore[arg-type]
        )
        assert error.message == "客户费用指示命令无效"
        assert error.details == {"field": field}
        assert _instruction_activities(transaction) == []


def test_malformed_recognition_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
        assert recognition is not None
        recognition.payload_json = '{"schema":"wrong"}'
        transaction.commit()
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID",
            409,
            lambda: _record(_command(), transaction),
        )


def test_cross_linked_recognition_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        transaction.add(
            Case(
                id="cross-linked-recognition-case",
                case_no="CROSS-LINKED-RECOGNITION",
                status="OPEN",
                business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                legal_status=LegalStatus.APPLICATION_PENDING.value,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
                lifecycle_revision=1,
            )
        )
        transaction.flush()
        recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
        assert recognition is not None
        recognition.payload_json = json.dumps(
            {
                "obligation_id": "other-obligation",
                "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.add(
            CaseActivityEvent(
                id="cross-linked-recognition",
                case_id="cross-linked-recognition-case",
                sequence=1,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                source_activity_id=None,
                occurred_at=datetime(2026, 7, 13, 10, 5),
                effective_at=datetime(2026, 7, 13, 10, 5),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                old_official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                new_official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                old_legal_status=LegalStatus.APPLICATION_PENDING.value,
                new_legal_status=LegalStatus.APPLICATION_PENDING.value,
                actor_id=ACTOR_ID,
                reviewer_id=None,
                idempotency_key="recognize:cross-linked",
                supersedes_event_id=None,
                payload_json=json.dumps(
                    {
                        "obligation_id": OBLIGATION_ID,
                        "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        )
        transaction.commit()

        _expect_error(
            "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID",
            409,
            lambda: _record(_command(), transaction),
        )
        assert _instruction_activities(transaction) == []


def test_instruction_accepts_payload_linked_recognition_child_of_header_source(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
        case = transaction.get(Case, CASE_ID)
        assert recognition is not None and case is not None
        recognition.sequence = 2
        case.lifecycle_revision = 2
        transaction.commit()

        transaction.add(
            CaseActivityEvent(
                id=GRANT_SOURCE_ID,
                case_id=CASE_ID,
                sequence=1,
                lane=ActivityLane.LIFECYCLE.value,
                activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
                source_activity_id=None,
                occurred_at=datetime(2026, 7, 13, 9, 45),
                effective_at=datetime(2026, 7, 13, 9, 50),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                old_official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                new_official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                old_legal_status=LegalStatus.APPLICATION_PENDING.value,
                new_legal_status=LegalStatus.APPLICATION_PENDING.value,
                actor_id=ACTOR_ID,
                reviewer_id=None,
                idempotency_key="grant-source:fee-instruction",
                supersedes_event_id=None,
                payload_json="{}",
            )
        )
        transaction.flush()
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        line = transaction.get(FeeObligationLineModel, LINE_ID)
        assert header is not None and line is not None
        recognition.source_activity_id = GRANT_SOURCE_ID
        header.source_activity_id = GRANT_SOURCE_ID
        line.source_activity_id = GRANT_SOURCE_ID
        transaction.commit()

        result = _record(_command(), transaction)

        instruction = transaction.get(CaseActivityEvent, result.activity_id)
        assert result.reused is False
        assert instruction is not None
        assert instruction.source_activity_id == RECOGNITION_ID
        assert header.source_activity_id == GRANT_SOURCE_ID
        assert recognition.source_activity_id == GRANT_SOURCE_ID

        transaction.commit()
        before_replay = (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            case.lifecycle_revision,
        )

        replay = _record(_command(), transaction)

        replayed_instruction = transaction.get(CaseActivityEvent, replay.activity_id)
        assert replay.reused is True
        assert replay.activity_id == result.activity_id
        assert replayed_instruction is not None
        assert replayed_instruction.source_activity_id == RECOGNITION_ID
        assert header.source_activity_id == GRANT_SOURCE_ID
        assert recognition.source_activity_id == GRANT_SOURCE_ID
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
            case.lifecycle_revision,
        ) == before_replay


def test_duplicate_recognition_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        duplicate = CaseActivityEvent(
            id="recognition-fee-instruction-dup",
            case_id=CASE_ID,
            sequence=2,
            lane=ActivityLane.FEE.value,
            activity_type="FEE_OBLIGATION_RECOGNIZED",
            source_activity_id=None,
            occurred_at=datetime(2026, 7, 13, 10, 5),
            effective_at=datetime(2026, 7, 13, 10, 5),
            confirmation_status=ConfirmationStatus.CONFIRMED.value,
            old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            old_official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            new_official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            old_legal_status=LegalStatus.APPLICATION_PENDING.value,
            new_legal_status=LegalStatus.APPLICATION_PENDING.value,
            actor_id=ACTOR_ID,
            reviewer_id=None,
            idempotency_key="recognize:fee-instruction:dup",
            supersedes_event_id=None,
            payload_json=json.dumps(
                {
                    "obligation_id": OBLIGATION_ID,
                    "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        transaction.add(duplicate)
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        case.lifecycle_revision = 2
        transaction.commit()
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID",
            409,
            lambda: _record(_command(), transaction),
        )


def test_inconsistent_instruction_header_and_activity_fail_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        header.client_instruction_status = FeeClientInstructionStatus.PAY.value
        transaction.commit()
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_STORED_STATE_INVALID",
            409,
            lambda: _record(
                _command(FeeClientInstruction.HOLD, idempotency_key="instruction:hold"),
                transaction,
            ),
        )


def test_caller_rollback_removes_header_activity_and_revision(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        _record(_command(), transaction)
        transaction.rollback()

    with session_factory() as verification:
        header = verification.get(FeeObligationModel, OBLIGATION_ID)
        case = verification.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.client_instruction_status == FeeClientInstructionStatus.PENDING.value
        assert case.lifecycle_revision == 1
        assert _instruction_activities(verification) == []


def test_missing_obligation_and_dirty_entry_fail_before_any_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _expect_error(
            "FEE_OBLIGATION_NOT_FOUND",
            404,
            lambda: _record(_command(), transaction),
        )

    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        transaction.add(Case(id="pending-case", case_no="PENDING-CASE", status="OPEN"))
        _expect_error(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            409,
            lambda: _record(_command(), transaction),
        )
        assert _instruction_activities(transaction) == []


def test_same_key_with_changed_command_or_stored_activity_is_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        result = _record(_command(), transaction)
        transaction.commit()

        actor_error = _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(_command(actor_id="different-actor"), transaction),
        )
        assert actor_error.message == "幂等键已用于不同的客户费用指示事实"

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        activity.reviewer_id = "unexpected-reviewer"
        transaction.commit()
        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(_command(), transaction),
        )


@pytest.mark.parametrize("mutation", ("timestamp", "recognition_source"))
def test_replay_rejects_changed_timestamp_or_recognition_source_fact(
    session_factory: sessionmaker,
    mutation: str,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        result = _record(_command(), transaction)
        transaction.commit()
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
        assert activity is not None and recognition is not None
        if mutation == "timestamp":
            activity.effective_at += timedelta(seconds=1)
        else:
            recognition.activity_type = "NOT_A_RECOGNITION_FACT"
        transaction.commit()

        _expect_error(
            "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _record(_command(), transaction),
        )


def test_same_key_same_fact_race_recovers_as_exact_replay(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        first = _record(_command(), transaction)
        transaction.commit()
        original_lookup = service._activity_by_key
        lookup_count = 0

        def stale_then_visible(*args, **kwargs):
            nonlocal lookup_count
            lookup_count += 1
            if lookup_count == 1:
                return None
            return original_lookup(*args, **kwargs)

        with (
            patch.object(service, "_activity_by_key", side_effect=stale_then_visible),
            patch.object(
                service,
                "_instruction_stored_chain",
                return_value=(FeeClientInstructionStatus.PENDING, None),
            ),
        ):
            replay = _record(_command(), transaction)

        assert replay.reused is True
        assert replay.activity_id == first.activity_id
        assert len(_instruction_activities(transaction)) == 1
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None


def test_same_key_different_fact_race_recovers_as_idempotency_conflict(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        _record(_command(), transaction)
        transaction.commit()
        original_lookup = service._activity_by_key
        lookup_count = 0

        def stale_then_visible(*args, **kwargs):
            nonlocal lookup_count
            lookup_count += 1
            if lookup_count == 1:
                return None
            return original_lookup(*args, **kwargs)

        with patch.object(service, "_activity_by_key", side_effect=stale_then_visible):
            _expect_error(
                "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT",
                409,
                lambda: _record(
                    _command(FeeClientInstruction.HOLD),
                    transaction,
                ),
            )
        assert len(_instruction_activities(transaction)) == 1
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None


def test_not_yet_visible_activity_race_is_retryable_without_outer_rollback(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        hidden_race = BusinessError(
            code="LIFECYCLE_IDEMPOTENCY_CONFLICT",
            message="simulated hidden race",
            status_code=409,
        )
        with patch.object(service, "append_case_activity", side_effect=hidden_race):
            error = _expect_error(
                "FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT",
                409,
                lambda: _record(_command(), transaction),
            )
        assert error.message == "并发客户费用指示尚不可见，请重试完整事务"
        assert _instruction_activities(transaction) == []
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None


def test_different_target_header_cas_loss_is_conflict_and_rolls_back_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        _record(_command(), transaction)
        transaction.commit()
        original_execute = transaction.execute

        def miss_obligation_update(statement, *args, **kwargs):
            table = getattr(statement, "table", None)
            if getattr(table, "name", None) == FeeObligationModel.__tablename__:
                return SimpleNamespace(rowcount=0)
            return original_execute(statement, *args, **kwargs)

        with patch.object(transaction, "execute", side_effect=miss_obligation_update):
            _expect_error(
                "FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT",
                409,
                lambda: _record(
                    _command(
                        FeeClientInstruction.HOLD,
                        idempotency_key="instruction:hold",
                    ),
                    transaction,
                ),
            )
        assert len(_instruction_activities(transaction)) == 1
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None


def test_downstream_lock_cas_loss_reports_locked_and_rolls_back_activity(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        header.payment_status = FeePaymentStatus.PAID.value
        transaction.commit()
        original_eligible = service._instruction_eligible
        call_count = 0

        def stale_then_locked(current_header):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return None
            return original_eligible(current_header)

        with patch.object(
            service,
            "_instruction_eligible",
            side_effect=stale_then_locked,
        ):
            _expect_error(
                "FEE_CLIENT_INSTRUCTION_LOCKED",
                409,
                lambda: _record(_command(), transaction),
            )
        assert _instruction_activities(transaction) == []
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None


def test_forced_failure_after_append_rolls_back_all_service_writes(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    original_append = service.append_case_activity

    def append_then_fail(*args, **kwargs):
        original_append(*args, **kwargs)
        raise RuntimeError("forced after append")

    with session_factory() as transaction:
        _seed_recognized_obligation(transaction)
        with patch.object(service, "append_case_activity", side_effect=append_then_fail):
            with pytest.raises(RuntimeError, match="forced after append"):
                _record(_command(), transaction)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        case = transaction.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.client_instruction_status == FeeClientInstructionStatus.PENDING.value
        assert case.lifecycle_revision == 1
        assert _instruction_activities(transaction) == []
        assert transaction.scalar(select(func.count()).select_from(Case)) is not None
