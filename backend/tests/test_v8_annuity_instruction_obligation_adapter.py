from __future__ import annotations

import hashlib
import inspect
import json
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, get_type_hints

import pytest
import test_v8_future_annuity_obligation as future_annuity
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity import service as annuity_service
from app.modules.annuity.models import AnnuityTask
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeObligation, FeeObligationLine
from app.modules.masterdata.clients.models import Client

RecordAnnuityTaskInstructionCommand = getattr(
    annuity_service,
    "RecordAnnuityTaskInstructionCommand",
    None,
)
RecordAnnuityTaskInstructionResult = getattr(
    annuity_service,
    "RecordAnnuityTaskInstructionResult",
    None,
)
record_annuity_task_instruction = getattr(
    annuity_service,
    "record_annuity_task_instruction",
    None,
)

CASE_ID = "annuity-instruction-case"
OTHER_CASE_ID = "annuity-instruction-other-case"
CLIENT_ID = "annuity-instruction-client"
SOURCE_ACTIVITY_ID = "annuity-instruction-source"
RECOGNITION_ID = "annuity-instruction-recognition"
DOCUMENT_ID = "annuity-instruction-document"
ATTACHMENT_ID = "annuity-instruction-attachment"
EVIDENCE_ID = "annuity-instruction-evidence"
OBLIGATION_ID = "annuity-instruction-obligation"
LINE_ID = "annuity-instruction-line"
ACTOR_ID = "annuity-instruction-actor"
CONTENT_HASH = f"sha256:{'a' * 64}"
DUE_DATE = date(2027, 8, 1)
OCCURRED_AT = datetime(2026, 8, 1, 9, 0)
IDEMPOTENCY_KEY = "annuity-instruction:pay"


def _identity_key(*, year: int, obligation_id: str = OBLIGATION_ID) -> str:
    source = f"{CASE_ID}|{SOURCE_ACTIVITY_ID}|CN_ANNUITY_FEE_INV|{year}"
    assert obligation_id
    return hashlib.sha256(source.encode()).hexdigest()


def _recognition_payload(
    obligation_id: str,
    *,
    year: int = 4,
    due_date: date = DUE_DATE,
) -> str:
    return json.dumps(
        {
            "obligation_id": obligation_id,
            "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            "obligation": {
                "actor_id": ACTOR_ID,
                "case_id": CASE_ID,
                "currency": "CNY",
                "due_date": due_date.isoformat(),
                "fee_domain": "GOV",
                "lines": [
                    {
                        "difference_review_state": "MATCHED",
                        "fee_code": "CN_ANNUITY_FEE_INV",
                        "fee_name": "发明专利年费",
                        "fee_year_key": year,
                        "official_full_amount": "1200.00",
                        "payable_amount": "1200.00",
                        "reduction_ratio": "0.0000",
                        "source_amount": None,
                        "source_date": due_date.isoformat(),
                    }
                ],
                "obligation_type": "FUTURE_ANNUITY",
                "source_activity_id": SOURCE_ACTIVITY_ID,
                "source_document_id": DOCUMENT_ID,
                "source_status": "VERIFIED",
                "supersede_reason": None,
                "supersedes_obligation_id": None,
            },
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _seed(session_factory: sessionmaker) -> int:
    with session_factory() as transaction:
        transaction.add(
            Client(
                id=CLIENT_ID,
                client_code="ANNUITY-INSTRUCTION",
                name_cn="年费指示测试客户",
            )
        )
        transaction.flush()
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="ANNUITY-INSTRUCTION-CASE",
                client_id=CLIENT_ID,
                patent_category="INV",
                status="GRANTED",
                business_stage="POST_GRANT_MAINTENANCE",
                official_procedure_stage="GRANT_ANNOUNCED",
                legal_status="PATENT_IN_FORCE",
                lifecycle_verification_status="CONFIRMED",
                lifecycle_revision=2,
            )
        )
        transaction.flush()
        transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"))
        transaction.flush()
        transaction.add(
            DocAttachment(
                id=ATTACHMENT_ID,
                document_id=DOCUMENT_ID,
                file_name="grant-announcement.pdf",
                file_path="/evidence/grant-announcement.pdf",
                content_hash=CONTENT_HASH,
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=DOCUMENT_ID,
                attachment_id=ATTACHMENT_ID,
                lineage_key="grant-announcement",
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id="annuity-instruction-creator",
                review_state="APPROVED",
                reviewer_id="annuity-instruction-reviewer",
                reviewed_at=OCCURRED_AT,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|grant-announcement",
            )
        )
        transaction.add(
            CaseActivityEvent(
                id=SOURCE_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane="LIFECYCLE",
                activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
                source_activity_id=None,
                occurred_at=OCCURRED_AT,
                effective_at=OCCURRED_AT,
                confirmation_status="CONFIRMED",
                old_business_stage="GRANT_REGISTRATION_IN_PROGRESS",
                new_business_stage="POST_GRANT_MAINTENANCE",
                old_official_procedure_stage="GRANT_REGISTRATION",
                new_official_procedure_stage="GRANT_ANNOUNCED",
                old_legal_status="APPLICATION_PENDING",
                new_legal_status="PATENT_IN_FORCE",
                actor_id=ACTOR_ID,
                reviewer_id="annuity-instruction-reviewer",
                idempotency_key="annuity-instruction:source",
                supersedes_event_id=None,
                payload_json="{}",
            )
        )
        transaction.flush()
        transaction.add(
            CaseActivityEventEvidence(
                id="annuity-instruction-source-link",
                case_id=CASE_ID,
                activity_id=SOURCE_ACTIVITY_ID,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=EVIDENCE_ID,
                content_hash=CONTENT_HASH,
                captured_at=OCCURRED_AT,
            )
        )
        transaction.add(
            CaseActivityEvent(
                id=RECOGNITION_ID,
                case_id=CASE_ID,
                sequence=2,
                lane="FEE",
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                occurred_at=OCCURRED_AT,
                effective_at=OCCURRED_AT,
                confirmation_status="CONFIRMED",
                old_business_stage="POST_GRANT_MAINTENANCE",
                new_business_stage="POST_GRANT_MAINTENANCE",
                old_official_procedure_stage="GRANT_ANNOUNCED",
                new_official_procedure_stage="GRANT_ANNOUNCED",
                old_legal_status="PATENT_IN_FORCE",
                new_legal_status="PATENT_IN_FORCE",
                actor_id=ACTOR_ID,
                reviewer_id="annuity-instruction-reviewer",
                idempotency_key="annuity-instruction:recognition",
                supersedes_event_id=None,
                payload_json=_recognition_payload(OBLIGATION_ID),
            )
        )
        transaction.flush()
        transaction.add(
            FeeObligation(
                id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                source_document_id=DOCUMENT_ID,
                fee_domain="GOV",
                obligation_type="FUTURE_ANNUITY",
                obligation_status="RECOGNIZED",
                due_date=DUE_DATE,
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PENDING",
                draft_status="NOT_CREATED",
                payment_status="UNPAID",
                official_evidence_status="PENDING",
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        transaction.flush()
        transaction.add(
            FeeObligationLine(
                id=LINE_ID,
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_code="CN_ANNUITY_FEE_INV",
                fee_name="发明专利年费",
                fee_year_key=4,
                official_full_amount=Decimal("1200.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("1200.00"),
                source_amount=None,
                source_date=DUE_DATE,
                difference_review_state="MATCHED",
                current_identity_key=_identity_key(year=4),
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
        transaction.flush()
        task = AnnuityTask(
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            year_no=4,
            due_date=DUE_DATE,
            client_instruction="DEFER",
            pay_next_year=False,
            status="OPEN",
            source_activity_id=SOURCE_ACTIVITY_ID,
            source_document_id=DOCUMENT_ID,
            source_evidence_version_id=EVIDENCE_ID,
            source_evidence_content_hash=CONTENT_HASH,
            fee_obligation_id=OBLIGATION_ID,
            grant_fee_year_key=4,
        )
        transaction.add(task)
        transaction.commit()
        return task.id


def _seed_second_task(transaction: Session) -> int:
    obligation_id = "annuity-instruction-obligation-2"
    recognition_id = "annuity-instruction-recognition-2"
    line_id = "annuity-instruction-line-2"
    transaction.add(
        CaseActivityEvent(
            id=recognition_id,
            case_id=CASE_ID,
            sequence=3,
            lane="FEE",
            activity_type="FEE_OBLIGATION_RECOGNIZED",
            source_activity_id=SOURCE_ACTIVITY_ID,
            occurred_at=OCCURRED_AT,
            effective_at=OCCURRED_AT,
            confirmation_status="CONFIRMED",
            old_business_stage="POST_GRANT_MAINTENANCE",
            new_business_stage="POST_GRANT_MAINTENANCE",
            old_official_procedure_stage="GRANT_ANNOUNCED",
            new_official_procedure_stage="GRANT_ANNOUNCED",
            old_legal_status="PATENT_IN_FORCE",
            new_legal_status="PATENT_IN_FORCE",
            actor_id=ACTOR_ID,
            reviewer_id="annuity-instruction-reviewer",
            idempotency_key="annuity-instruction:recognition-2",
            supersedes_event_id=None,
            payload_json=_recognition_payload(
                obligation_id,
                year=5,
                due_date=date(2028, 8, 1),
            ),
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligation(
            id=obligation_id,
            case_id=CASE_ID,
            source_activity_id=SOURCE_ACTIVITY_ID,
            source_document_id=DOCUMENT_ID,
            fee_domain="GOV",
            obligation_type="FUTURE_ANNUITY",
            obligation_status="RECOGNIZED",
            due_date=date(2028, 8, 1),
            currency="CNY",
            source_status="VERIFIED",
            client_instruction_status="PENDING",
            draft_status="NOT_CREATED",
            payment_status="UNPAID",
            official_evidence_status="PENDING",
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligationLine(
            id=line_id,
            obligation_id=obligation_id,
            case_id=CASE_ID,
            source_activity_id=SOURCE_ACTIVITY_ID,
            fee_code="CN_ANNUITY_FEE_INV",
            fee_name="发明专利年费",
            fee_year_key=5,
            official_full_amount=Decimal("1200.00"),
            reduction_ratio=Decimal("0.0000"),
            payable_amount=Decimal("1200.00"),
            source_amount=None,
            source_date=date(2028, 8, 1),
            difference_review_state="MATCHED",
            current_identity_key=_identity_key(year=5, obligation_id=obligation_id),
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    task = AnnuityTask(
        case_id=CASE_ID,
        client_id=CLIENT_ID,
        year_no=5,
        due_date=date(2028, 8, 1),
        client_instruction=None,
        status="OPEN",
        source_activity_id=SOURCE_ACTIVITY_ID,
        source_document_id=DOCUMENT_ID,
        source_evidence_version_id=EVIDENCE_ID,
        source_evidence_content_hash=CONTENT_HASH,
        fee_obligation_id=obligation_id,
        grant_fee_year_key=5,
    )
    transaction.add(task)
    case = transaction.get(Case, CASE_ID)
    assert case is not None
    case.lifecycle_revision = 3
    transaction.commit()
    return task.id


def _command(task_id: int, **changes: object) -> Any:
    assert RecordAnnuityTaskInstructionCommand is not None
    values: dict[str, object] = {
        "annuity_task_id": task_id,
        "instruction": "PAY",
        "actor_id": ACTOR_ID,
        "idempotency_key": IDEMPOTENCY_KEY,
    }
    values.update(changes)
    return RecordAnnuityTaskInstructionCommand(**values)


def _record(command: object, transaction: Session) -> Any:
    assert record_annuity_task_instruction is not None
    return record_annuity_task_instruction(command, transaction)


def _expect_status(status_code: int, action: Callable[[], object]) -> Exception:
    try:
        action()
    except (BusinessError, ValueError) as exc:
        assert getattr(exc, "status_code", None) == status_code
        return exc
    pytest.fail(f"expected {status_code} error")


def _instruction_activities(transaction: Session) -> tuple[CaseActivityEvent, ...]:
    return tuple(
        transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "FEE_CLIENT_INSTRUCTION_RECORDED"
            )
        )
    )


def _snapshot(transaction: Session, task_id: int) -> tuple[object, ...]:
    task = transaction.get(AnnuityTask, task_id)
    obligation = transaction.get(FeeObligation, OBLIGATION_ID)
    case = transaction.get(Case, CASE_ID)
    assert task is not None and obligation is not None and case is not None
    return (
        task.client_instruction,
        task.pay_next_year,
        task.source_activity_id,
        task.source_document_id,
        task.source_evidence_version_id,
        task.source_evidence_content_hash,
        task.fee_obligation_id,
        task.grant_fee_year_key,
        obligation.client_instruction_status,
        case.status,
        case.lifecycle_revision,
        transaction.scalar(select(func.count()).select_from(CaseActivityEvent)),
        transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)),
    )


def _corrupt_task(transaction: Session, task_id: int, **values: object) -> None:
    transaction.execute(text("PRAGMA ignore_check_constraints = ON"))
    transaction.execute(update(AnnuityTask).where(AnnuityTask.id == task_id).values(**values))
    transaction.commit()
    transaction.execute(text("PRAGMA ignore_check_constraints = OFF"))


def test_public_contract_is_exact_frozen_slotted_and_typed() -> None:
    assert RecordAnnuityTaskInstructionCommand is not None
    assert RecordAnnuityTaskInstructionResult is not None
    assert record_annuity_task_instruction is not None
    assert is_dataclass(RecordAnnuityTaskInstructionCommand)
    assert RecordAnnuityTaskInstructionCommand.__dataclass_params__.frozen is True
    assert RecordAnnuityTaskInstructionCommand.__slots__ == (
        "annuity_task_id",
        "instruction",
        "actor_id",
        "idempotency_key",
    )
    assert tuple(field.name for field in fields(RecordAnnuityTaskInstructionCommand)) == (
        "annuity_task_id",
        "instruction",
        "actor_id",
        "idempotency_key",
    )
    assert list(inspect.signature(record_annuity_task_instruction).parameters) == [
        "command",
        "transaction",
    ]
    assert get_type_hints(record_annuity_task_instruction) == {
        "command": RecordAnnuityTaskInstructionCommand,
        "transaction": Session,
        "return": RecordAnnuityTaskInstructionResult,
    }


def test_current_future_annuity_recognition_composes_with_instruction(
    session_factory: sessionmaker,
) -> None:
    task_id = future_annuity._seed(session_factory)
    with session_factory() as transaction:
        recognition = future_annuity.recognize_future_annuity_obligation(
            future_annuity._command(task_id), transaction
        )
        transaction.commit()

    with session_factory() as transaction:
        result = _record(
            RecordAnnuityTaskInstructionCommand(
                annuity_task_id=task_id,
                instruction="PAY",
                actor_id=future_annuity.ACTOR_ID,
                idempotency_key="annuity-current-recognition:pay",
            ),
            transaction,
        )

        assert result.annuity_task_id == task_id
        assert result.fee_obligation_id == recognition.fee_obligation_id
        assert result.instruction.value == "PAY"
        assert result.reused is False


def test_obsolete_two_field_recognition_payload_is_rejected(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
        assert recognition is not None
        recognition.payload_json = json.dumps(
            {
                "obligation_id": OBLIGATION_ID,
                "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        transaction.commit()

        monkeypatch.setattr(
            annuity_service,
            "record_client_instruction",
            lambda *_args, **_kwargs: pytest.fail("invalid payload delegated"),
        )
        error = _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert getattr(error, "code", None) == "ANNUITY_INSTRUCTION_LINEAGE_CONFLICT"


@pytest.mark.parametrize("instruction", ["PAY", "HOLD", "ABANDON"])
def test_identity_mapping_delegates_once_and_preserves_legacy_task(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    instruction: str,
) -> None:
    task_id = _seed(session_factory)
    delegated: list[tuple[object, Session]] = []
    original = annuity_service.record_client_instruction

    def record_once(command: object, transaction: Session) -> object:
        delegated.append((command, transaction))
        return original(command, transaction)

    monkeypatch.setattr(annuity_service, "record_client_instruction", record_once)
    with session_factory() as transaction:
        instruction_key = f"annuity-instruction:{instruction.lower()}"
        result = _record(
            _command(
                task_id,
                instruction=instruction,
                idempotency_key=instruction_key,
            ),
            transaction,
        )
        task = transaction.get(AnnuityTask, task_id)
        obligation = transaction.get(FeeObligation, OBLIGATION_ID)
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert type(result) is RecordAnnuityTaskInstructionResult
        assert task is not None and obligation is not None and activity is not None
        assert result.annuity_task_id == task_id
        assert result.fee_obligation_id == OBLIGATION_ID
        assert result.instruction.value == instruction
        assert result.reused is False
        assert len(delegated) == 1
        delegated_command, delegated_transaction = delegated[0]
        assert delegated_transaction is transaction
        assert delegated_command.obligation_id == OBLIGATION_ID
        assert delegated_command.instruction.value == instruction
        assert delegated_command.actor_id == ACTOR_ID
        assert delegated_command.idempotency_key == instruction_key
        assert obligation.client_instruction_status == instruction
        assert activity.source_activity_id == RECOGNITION_ID
        assert task.client_instruction == "DEFER"
        assert task.pay_next_year is False
        assert (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        ) == (
            SOURCE_ACTIVITY_ID,
            DOCUMENT_ID,
            EVIDENCE_ID,
            CONTENT_HASH,
            OBLIGATION_ID,
            4,
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == activity.id)
            )
            == 0
        )


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"annuity_task_id": True}, "annuity_task_id"),
        ({"annuity_task_id": 0}, "annuity_task_id"),
        ({"annuity_task_id": 1.0}, "annuity_task_id"),
        ({"instruction": "DEFER"}, "instruction"),
        ({"instruction": "pay"}, "instruction"),
        ({"instruction": " PAY"}, "instruction"),
        ({"instruction": None}, "instruction"),
        ({"actor_id": ""}, "actor_id"),
        ({"actor_id": " actor"}, "actor_id"),
        ({"idempotency_key": ""}, "idempotency_key"),
        ({"idempotency_key": " key"}, "idempotency_key"),
    ],
)
def test_command_validation_is_strict_and_precedes_lookup(
    session_factory: sessionmaker,
    changes: dict[str, object],
    field: str,
) -> None:
    with session_factory() as transaction:
        command = _command(999, **changes)
        error = _expect_status(400, lambda: _record(command, transaction))
        assert getattr(error, "details", {}).get("field") == field
        assert _instruction_activities(transaction) == ()


def test_wrong_command_type_is_400_before_lookup(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        error = _expect_status(400, lambda: _record(object(), transaction))
        assert getattr(error, "details", {}).get("field") == "command"


def test_named_task_is_resolved_instead_of_latest(session_factory: sessionmaker) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        other_task_id = _seed_second_task(transaction)
    with session_factory() as transaction:
        result = _record(_command(task_id), transaction)
        target = transaction.get(FeeObligation, OBLIGATION_ID)
        other_task = transaction.get(AnnuityTask, other_task_id)
        other = transaction.get(FeeObligation, other_task.fee_obligation_id)
        assert result.annuity_task_id == task_id
        assert target is not None and other is not None
        assert target.client_instruction_status == "PAY"
        assert other.client_instruction_status == "PENDING"


def test_missing_task_or_unlinked_carrier_is_404(session_factory: sessionmaker) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        _expect_status(404, lambda: _record(_command(task_id + 100), transaction))
    with session_factory() as transaction:
        _corrupt_task(
            transaction,
            task_id,
            source_activity_id=None,
            source_document_id=None,
            source_evidence_version_id=None,
            source_evidence_content_hash=None,
            fee_obligation_id=None,
            grant_fee_year_key=None,
        )
        _expect_status(404, lambda: _record(_command(task_id), transaction))


@pytest.mark.parametrize(
    "values",
    [
        {"source_activity_id": None},
        {"source_document_id": None},
        {"source_evidence_version_id": None},
        {"source_evidence_content_hash": None},
        {"fee_obligation_id": None},
        {"grant_fee_year_key": None},
    ],
)
def test_partial_six_field_carrier_is_409_without_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    values: dict[str, object],
) -> None:
    task_id = _seed(session_factory)
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        _corrupt_task(transaction, task_id, **values)
        _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert calls == []


@pytest.mark.parametrize(
    "content_hash",
    [
        "a" * 64,
        f"sha256:{'A' * 64}",
        f"sha256:{'g' * 64}",
        f"sha256:{'a' * 63}",
    ],
)
def test_malformed_carrier_hash_is_409_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    content_hash: str,
) -> None:
    task_id = _seed(session_factory)
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        _corrupt_task(transaction, task_id, source_evidence_content_hash=content_hash)
        _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert calls == []


@pytest.mark.parametrize("conflict", ["case", "type", "year", "line_year"])
def test_cross_case_wrong_type_or_year_is_409_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    conflict: str,
) -> None:
    task_id = _seed(session_factory)
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        if conflict == "case":
            transaction.add(
                Case(id=OTHER_CASE_ID, case_no="ANNUITY-OTHER", client_id=CLIENT_ID, status="OPEN")
            )
            transaction.commit()
            transaction.execute(
                update(AnnuityTask)
                .where(AnnuityTask.id == task_id)
                .values(case_id=OTHER_CASE_ID)
            )
        elif conflict == "type":
            transaction.execute(
                update(FeeObligation)
                .where(FeeObligation.id == OBLIGATION_ID)
                .values(obligation_type="OTHER")
            )
        elif conflict == "year":
            transaction.execute(
                update(AnnuityTask).where(AnnuityTask.id == task_id).values(year_no=5)
            )
        else:
            transaction.execute(
                update(FeeObligationLine)
                .where(FeeObligationLine.id == LINE_ID)
                .values(fee_year_key=5)
            )
        transaction.commit()
        _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert calls == []


@pytest.mark.parametrize("conflict", ["activity", "document", "evidence", "hash"])
def test_source_document_and_evidence_identity_mismatch_is_409(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    conflict: str,
) -> None:
    task_id = _seed(session_factory)
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        if conflict == "activity":
            recognition = transaction.get(CaseActivityEvent, RECOGNITION_ID)
            assert recognition is not None
            recognition.source_activity_id = None
        elif conflict == "document":
            obligation = transaction.get(FeeObligation, OBLIGATION_ID)
            assert obligation is not None
            obligation.source_document_id = None
        elif conflict == "evidence":
            evidence = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
            assert evidence is not None
            transaction.add(
                Document(
                    id="annuity-instruction-wrong-document",
                    case_id=CASE_ID,
                    direction="IN",
                )
            )
            transaction.flush()
            evidence.document_id = "annuity-instruction-wrong-document"
        else:
            link = transaction.get(CaseActivityEventEvidence, "annuity-instruction-source-link")
            assert link is not None
            link.content_hash = f"sha256:{'b' * 64}"
        transaction.commit()
        _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert calls == []


@pytest.mark.parametrize("cardinality", [0, 2])
def test_source_evidence_link_cardinality_is_404_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    cardinality: int,
) -> None:
    task_id = _seed(session_factory)
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        if cardinality == 0:
            link = transaction.get(
                CaseActivityEventEvidence,
                "annuity-instruction-source-link",
            )
            assert link is not None
            transaction.delete(link)
        else:
            transaction.add(
                CaseActivityEventEvidence(
                    id="annuity-instruction-extra-link",
                    case_id=CASE_ID,
                    activity_id=SOURCE_ACTIVITY_ID,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id="annuity-instruction-other-evidence",
                    content_hash=CONTENT_HASH,
                    captured_at=OCCURRED_AT,
                )
            )
        transaction.commit()
        _expect_status(404, lambda: _record(_command(task_id), transaction))
        assert calls == []


def test_exact_replay_reuses_original_result_without_write(session_factory: sessionmaker) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        created = _record(_command(task_id), transaction)
        transaction.commit()
        before = _snapshot(transaction, task_id)
        replay = _record(_command(task_id), transaction)
        assert replay.reused is True
        assert replay.activity_id == created.activity_id
        assert replay.fee_obligation_id == created.fee_obligation_id == OBLIGATION_ID
        assert _snapshot(transaction, task_id) == before


@pytest.mark.parametrize(
    "change",
    [
        {"instruction": "HOLD"},
        {"actor_id": "annuity-instruction-other-actor"},
    ],
)
def test_same_key_changed_instruction_or_actor_is_409_without_write(
    session_factory: sessionmaker,
    change: dict[str, object],
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        _record(_command(task_id), transaction)
        transaction.commit()
        before = _snapshot(transaction, task_id)
        _expect_status(409, lambda: _record(_command(task_id, **change), transaction))
        assert _snapshot(transaction, task_id) == before


def test_same_key_changed_task_is_409_without_second_instruction(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        second_task_id = _seed_second_task(transaction)
    with session_factory() as transaction:
        _record(_command(task_id), transaction)
        transaction.commit()
        before = len(_instruction_activities(transaction))
        _expect_status(409, lambda: _record(_command(second_task_id), transaction))
        assert len(_instruction_activities(transaction)) == before


def test_same_key_lineage_drift_is_409_before_delegation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        created = _record(_command(task_id), transaction)
        transaction.commit()
        assert created.reused is False
    calls: list[object] = []
    monkeypatch.setattr(annuity_service, "record_client_instruction", calls.append, raising=False)
    with session_factory() as transaction:
        link = transaction.get(CaseActivityEventEvidence, "annuity-instruction-source-link")
        assert link is not None
        link.content_hash = f"sha256:{'b' * 64}"
        transaction.commit()
        _expect_status(409, lambda: _record(_command(task_id), transaction))
        assert calls == []


def test_new_key_for_current_instruction_preserves_deep_same_state_409(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        _record(_command(task_id), transaction)
        transaction.commit()
        before = _snapshot(transaction, task_id)
        _expect_status(
            409,
            lambda: _record(
                _command(task_id, idempotency_key="annuity-instruction:pay:new"),
                transaction,
            ),
        )
        assert _snapshot(transaction, task_id) == before


def test_caller_rollback_removes_header_activity_and_revision(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        before = _snapshot(transaction, task_id)
        _record(_command(task_id), transaction)
        transaction.rollback()
    with session_factory() as verification:
        assert _snapshot(verification, task_id) == before
        assert _instruction_activities(verification) == ()
