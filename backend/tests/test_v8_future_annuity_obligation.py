from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity import service as annuity_service
from app.modules.annuity.models import AnnuityTask, FutureAnnuityReductionLineage
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.cnipa_annuity_rate_candidate import CNIPA_ANNUITY_SOURCE_SNAPSHOT
from app.modules.fees.fee_reduction import FeeReductionInput, FeeReductionInputProvenance
from app.modules.fees.models import (
    FeeObligation,
    FeeObligationLine,
    FeeRate,
    FeeReductionApproval,
    OfficialRateBook,
)
from app.modules.fees.obligation_contracts import FeeClientInstructionStatus
from app.modules.masterdata.clients.models import Client

FutureAnnuityObligationError = getattr(annuity_service, "FutureAnnuityObligationError", None)
FutureAnnuityObligationErrorCode = getattr(
    annuity_service, "FutureAnnuityObligationErrorCode", None
)
RecognizeFutureAnnuityObligationCommand = getattr(
    annuity_service, "RecognizeFutureAnnuityObligationCommand", None
)
RecognizeFutureAnnuityObligationResult = getattr(
    annuity_service, "RecognizeFutureAnnuityObligationResult", None
)
recognize_future_annuity_obligation = getattr(
    annuity_service, "recognize_future_annuity_obligation", None
)

CASE_ID = "future-annuity-case"
CLIENT_ID = "future-annuity-client"
ACTIVITY_ID = "future-annuity-grant-activity"
DOCUMENT_ID = "future-annuity-grant-document"
ATTACHMENT_ID = "future-annuity-grant-attachment"
EVIDENCE_ID = "future-annuity-grant-evidence"
ACTOR_ID = "future-annuity-actor"
HASH = f"sha256:{'a' * 64}"
EFFECTIVE_AT = datetime(2026, 8, 1, 9, 0)
DUE_DATE = date(2027, 8, 1)
IDEMPOTENCY_KEY = "future-annuity:case:year-4"
CALC_PARAMS = (
    '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
    '{"amount":"900.00","from":1,"to":3},'
    '{"amount":"1200.00","from":4,"to":6},'
    '{"amount":"2000.00","from":7,"to":9},'
    '{"amount":"4000.00","from":10,"to":12},'
    '{"amount":"6000.00","from":13,"to":15},'
    '{"amount":"8000.00","from":16,"to":20}]}'
)


def _seed(session_factory: sessionmaker) -> int:
    with session_factory() as transaction:
        admin = transaction.scalar(select(T_User).where(T_User.username == "admin"))
        assert admin is not None
        transaction.add_all(
            [
                T_User(
                    id=ACTOR_ID,
                    username=f"future-annuity-{uuid4()}",
                    password_hash="not-used",
                    is_active=True,
                ),
                Client(id=CLIENT_ID, client_code="FUTURE-ANNUITY", name_cn="年费测试客户"),
            ]
        )
        transaction.flush()
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="FUTURE-ANNUITY-CASE",
                client_id=CLIENT_ID,
                patent_category="INV",
                status="GRANTED",
                business_stage="POST_GRANT_MAINTENANCE",
                official_procedure_stage="GRANT_ANNOUNCED",
                legal_status="PATENT_IN_FORCE",
                lifecycle_verification_status="CONFIRMED",
                lifecycle_revision=1,
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
                content_hash=HASH,
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
                creator_id="future-annuity-creator",
                review_state="APPROVED",
                reviewer_id="future-annuity-reviewer",
                reviewed_at=EFFECTIVE_AT,
                content_hash=HASH,
                current_identity_key=f"{CASE_ID}|grant-announcement",
            )
        )
        transaction.add(
            CaseActivityEvent(
                id=ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane="LIFECYCLE",
                activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
                occurred_at=EFFECTIVE_AT,
                effective_at=EFFECTIVE_AT,
                confirmation_status="CONFIRMED",
                old_business_stage="GRANT_REGISTRATION_IN_PROGRESS",
                new_business_stage="POST_GRANT_MAINTENANCE",
                old_official_procedure_stage="GRANT_REGISTRATION",
                new_official_procedure_stage="GRANT_ANNOUNCED",
                old_legal_status="APPLICATION_PENDING",
                new_legal_status="PATENT_IN_FORCE",
                actor_id=ACTOR_ID,
                reviewer_id="future-annuity-reviewer",
                idempotency_key="grant-announcement-confirmed",
                payload_json="{}",
            )
        )
        transaction.flush()
        transaction.add(
            CaseActivityEventEvidence(
                id="future-annuity-grant-link",
                case_id=CASE_ID,
                activity_id=ACTIVITY_ID,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=EVIDENCE_ID,
                content_hash=HASH,
                captured_at=EFFECTIVE_AT,
            )
        )
        task = AnnuityTask(
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            year_no=4,
            due_date=DUE_DATE,
            client_instruction="ABANDON",
            pay_next_year=False,
            status="OPEN",
        )
        transaction.add(task)
        transaction.flush()
        book = OfficialRateBook(
            id="future-annuity-rate-book",
            book_code="CNIPA_PATENT_ANNUITY_20260330",
            version_code="2026-03-30",
            source_authority="CNIPA",
            source_reference=(
                "https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"
            ),
            source_version="2026-03-30",
            source_published_on=date(2026, 3, 30),
            source_snapshot=CNIPA_ANNUITY_SOURCE_SNAPSHOT,
            source_snapshot_hash=sha256(CNIPA_ANNUITY_SOURCE_SNAPSHOT.encode()).hexdigest(),
            approval_status="APPROVED",
            approved_by=admin.id,
            approved_at=datetime(2026, 7, 19, 10, 0),
            effective_from=date(2026, 3, 30),
            activation_status="ACTIVE",
            activated_by=admin.id,
            activated_at=datetime(2026, 7, 19, 10, 5),
            current_identity_key="CNIPA|CNIPA_PATENT_ANNUITY_20260330",
        )
        transaction.add(book)
        transaction.flush()
        transaction.add(
            FeeRate(
                id="future-annuity-inv-rate",
                fee_code="CN_ANNUITY_FEE_INV",
                fee_name=None,
                fee_type="GOV",
                currency="CNY",
                enabled=True,
                calc_mode="TIER",
                calc_params=CALC_PARAMS,
                allow_reduction=True,
                effective_from=date(2026, 3, 30),
                source_doc="专利和集成电路布图设计缴费服务指南",
                source_url=book.source_reference,
                source_version="2026-03-30",
                source_status="PENDING_CONFIRMATION",
                official_rate_book_id=book.id,
            )
        )
        transaction.commit()
        return task.id


def _seed_reduction_approval(
    session_factory: sessionmaker,
    approval_id: str,
    *,
    ratio: Decimal = Decimal("0.7000"),
) -> None:
    fee_scope_snapshot = (
        '{"fee_codes":["CN_ANNUITY_FEE_INV"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}'
    )
    eligibility_snapshot = '{"schema":"TEST_ELIGIBILITY_V1"}'
    with session_factory() as transaction:
        transaction.add(
            FeeReductionApproval(
                id=approval_id,
                scope_type="CASE",
                case_id=CASE_ID,
                applicant_set_key=None,
                reduction_ratio=ratio,
                fee_scope_snapshot=fee_scope_snapshot,
                fee_scope_hash=sha256(fee_scope_snapshot.encode()).hexdigest(),
                fee_year_from=4,
                fee_year_to=4,
                effective_from=date(2026, 1, 1),
                effective_to=None,
                source_evidence_version_id=EVIDENCE_ID,
                confirmation_status="CONFIRMED",
                confirmed_at=EFFECTIVE_AT,
                confirmed_by=ACTOR_ID,
                eligibility_snapshot=eligibility_snapshot,
                eligibility_snapshot_hash=sha256(eligibility_snapshot.encode()).hexdigest(),
                approval_identity_key=f"{CASE_ID}|{approval_id}",
            )
        )
        transaction.commit()


def _command(task_id: int, **changes: object) -> RecognizeFutureAnnuityObligationCommand:
    values: dict[str, object] = {
        "annuity_task_id": task_id,
        "source_activity_id": ACTIVITY_ID,
        "source_document_id": DOCUMENT_ID,
        "source_evidence_version_id": EVIDENCE_ID,
        "source_evidence_content_hash": HASH,
        "grant_fee_year_key": 4,
        "rate_effective_on": DUE_DATE,
        "reduction_input": FeeReductionInput(
            reduction_ratio=Decimal("0"),
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        "reduction_approval_id": None,
        "actor_id": ACTOR_ID,
        "idempotency_key": IDEMPOTENCY_KEY,
    }
    values.update(changes)
    return RecognizeFutureAnnuityObligationCommand(**values)


def _expect_error(
    code: FutureAnnuityObligationErrorCode,
    status_code: int,
    action,
) -> FutureAnnuityObligationError:
    with pytest.raises(FutureAnnuityObligationError) as captured:
        action()
    assert captured.value.code is code
    assert captured.value.status_code == status_code
    return captured.value


def test_public_contract_is_exact_frozen_slotted_and_typed() -> None:
    assert is_dataclass(RecognizeFutureAnnuityObligationCommand)
    assert RecognizeFutureAnnuityObligationCommand.__dataclass_params__.frozen is True
    assert RecognizeFutureAnnuityObligationCommand.__slots__ == (
        "annuity_task_id",
        "source_activity_id",
        "source_document_id",
        "source_evidence_version_id",
        "source_evidence_content_hash",
        "grant_fee_year_key",
        "rate_effective_on",
        "reduction_input",
        "reduction_approval_id",
        "actor_id",
        "idempotency_key",
    )
    assert tuple(field.name for field in fields(RecognizeFutureAnnuityObligationResult)) == (
        "annuity_task_id",
        "fee_obligation_id",
        "fee_obligation_line_id",
        "source_activity_id",
        "source_document_id",
        "source_evidence_version_id",
        "source_evidence_content_hash",
        "grant_fee_year_key",
        "fee_code",
        "due_date",
        "official_full_amount",
        "reduction_ratio",
        "payable_amount",
        "late_fee_base",
        "client_instruction_status",
        "activity_id",
        "idempotency_key",
        "reused",
    )
    assert issubclass(FutureAnnuityObligationErrorCode, Enum)
    assert list(inspect.signature(recognize_future_annuity_obligation).parameters) == [
        "command",
        "transaction",
    ]
    assert get_type_hints(recognize_future_annuity_obligation) == {
        "command": RecognizeFutureAnnuityObligationCommand,
        "transaction": Session,
        "return": RecognizeFutureAnnuityObligationResult,
    }

    command = _command(1)
    with pytest.raises(FrozenInstanceError):
        command.actor_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"annuity_task_id": True}, "annuity_task_id"),
        ({"grant_fee_year_key": 0}, "grant_fee_year_key"),
        ({"source_activity_id": " source"}, "source_activity_id"),
        ({"source_document_id": "x" * 37}, "source_document_id"),
        ({"source_evidence_content_hash": f"sha256:{'A' * 64}"}, "source_evidence_content_hash"),
        ({"rate_effective_on": datetime(2027, 8, 1)}, "rate_effective_on"),
        ({"reduction_input": object()}, "reduction_input"),
        ({"reduction_approval_id": ""}, "reduction_approval_id"),
        ({"idempotency_key": " "}, "idempotency_key"),
    ],
)
def test_invalid_typed_command_fails_before_transaction_access(
    changes: dict[str, object],
    field: str,
) -> None:
    error = _expect_error(
        FutureAnnuityObligationErrorCode.INVALID_COMMAND,
        400,
        lambda: recognize_future_annuity_obligation(_command(1, **changes), object()),  # type: ignore[arg-type]
    )
    assert error.details == {"field": field}


def test_fresh_recognition_writes_one_sourced_obligation_and_six_field_carrier(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        result = recognize_future_annuity_obligation(_command(task_id), transaction)

        assert result == RecognizeFutureAnnuityObligationResult(
            annuity_task_id=task_id,
            fee_obligation_id=result.fee_obligation_id,
            fee_obligation_line_id=result.fee_obligation_line_id,
            source_activity_id=ACTIVITY_ID,
            source_document_id=DOCUMENT_ID,
            source_evidence_version_id=EVIDENCE_ID,
            source_evidence_content_hash=HASH,
            grant_fee_year_key=4,
            fee_code="CN_ANNUITY_FEE_INV",
            due_date=DUE_DATE,
            official_full_amount=Decimal("1200.00"),
            reduction_ratio=Decimal("0.0000"),
            payable_amount=Decimal("1200.00"),
            late_fee_base=Decimal("1200.00"),
            client_instruction_status=FeeClientInstructionStatus.PENDING,
            activity_id=result.activity_id,
            idempotency_key=IDEMPOTENCY_KEY,
            reused=False,
        )
        task = transaction.get(AnnuityTask, task_id)
        assert task is not None
        assert (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        ) == (
            ACTIVITY_ID,
            DOCUMENT_ID,
            EVIDENCE_ID,
            HASH,
            result.fee_obligation_id,
            4,
        )
        assert task.client_instruction == "ABANDON"
        assert task.pay_next_year is False
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 1
        lineage = transaction.get(FutureAnnuityReductionLineage, task_id)
        assert lineage is not None
        assert (
            lineage.annuity_task_id,
            lineage.fee_obligation_line_id,
            lineage.reduction_input_provenance,
            lineage.reduction_approval_id,
        ) == (
            task_id,
            result.fee_obligation_line_id,
            FeeReductionInputProvenance.EXPLICIT_ENTRY.value,
            None,
        )
        assert not any(
            activity.activity_type in {"FEE_DRAFT_CREATED", "FEE_CLIENT_INSTRUCTION_RECORDED"}
            for activity in transaction.scalars(select(CaseActivityEvent))
        )


def test_exact_replay_precedes_later_evidence_current_replacement(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        created = recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    with session_factory() as transaction:
        evidence = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
        assert evidence is not None
        evidence.current_identity_key = None
        transaction.commit()

    with session_factory() as transaction:
        replay = recognize_future_annuity_obligation(_command(task_id), transaction)
        assert replay == replace(created, reused=True)
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 1


def test_durable_reduction_lineage_absence_fails_closed_without_write(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    with session_factory() as transaction:
        transaction.execute(
            delete(FutureAnnuityReductionLineage).where(
                FutureAnnuityReductionLineage.annuity_task_id == task_id
            )
        )
        transaction.commit()

    with session_factory() as transaction:
        activity_count = transaction.scalar(select(func.count()).select_from(CaseActivityEvent))
        _expect_error(
            FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 1
        assert (
            transaction.scalar(select(func.count()).select_from(FutureAnnuityReductionLineage)) == 0
        )
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent))
            == activity_count
        )
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_exact_reduced_replay_uses_durable_facts_after_current_state_drift(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    approval_id = "future-annuity-approval-a"
    _seed_reduction_approval(session_factory, approval_id)
    command = _command(
        task_id,
        reduction_input=FeeReductionInput(
            reduction_ratio=Decimal("0.7"),
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        reduction_approval_id=approval_id,
    )
    with session_factory() as transaction:
        created = recognize_future_annuity_obligation(command, transaction)
        transaction.commit()

    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        rate = transaction.get(FeeRate, "future-annuity-inv-rate")
        evidence = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
        approval = transaction.get(FeeReductionApproval, approval_id)
        assert case is not None
        assert rate is not None
        assert evidence is not None
        assert approval is not None
        case.patent_category = "DES"
        rate.enabled = False
        evidence.current_identity_key = None
        approval.confirmation_status = "NEEDS_REVIEW"
        transaction.commit()

    with session_factory() as transaction:
        replay = recognize_future_annuity_obligation(command, transaction)
        assert replay == replace(created, reused=True)
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 1
        assert (
            transaction.scalar(select(func.count()).select_from(FutureAnnuityReductionLineage)) == 1
        )
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_same_ratio_provenance_or_approval_drift_is_idempotency_conflict(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    approval_a = "future-annuity-approval-a"
    approval_b = "future-annuity-approval-b"
    _seed_reduction_approval(session_factory, approval_a)
    _seed_reduction_approval(session_factory, approval_b)
    original = _command(
        task_id,
        reduction_input=FeeReductionInput(
            reduction_ratio=Decimal("0.7"),
            provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
        ),
        reduction_approval_id=approval_a,
    )
    with session_factory() as transaction:
        recognize_future_annuity_obligation(original, transaction)
        transaction.commit()

    changed_commands = (
        replace(
            original,
            reduction_input=FeeReductionInput(
                reduction_ratio=Decimal("0.7"),
                provenance=FeeReductionInputProvenance.CONFIRMED_MIGRATION,
            ),
        ),
        replace(original, reduction_approval_id=approval_b),
    )
    for changed in changed_commands:
        with session_factory() as transaction:
            _expect_error(
                FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT,
                409,
                lambda changed=changed: recognize_future_annuity_obligation(changed, transaction),
            )
            assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1
            assert (
                transaction.scalar(select(func.count()).select_from(FutureAnnuityReductionLineage))
                == 1
            )


@pytest.mark.parametrize("corruption", ["cross_link", "illegal_zero_approval"])
def test_cross_linked_or_illegal_stored_reduction_lineage_fails_closed(
    session_factory: sessionmaker,
    corruption: str,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    if corruption == "cross_link":
        with session_factory() as transaction:
            transaction.add(
                FeeObligation(
                    id="future-annuity-wrong-obligation",
                    case_id=CASE_ID,
                    source_activity_id=ACTIVITY_ID,
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
                    supersedes_obligation_id=None,
                    supersede_reason=None,
                )
            )
            transaction.flush()
            transaction.add(
                FeeObligationLine(
                    id="future-annuity-wrong-line",
                    obligation_id="future-annuity-wrong-obligation",
                    case_id=CASE_ID,
                    source_activity_id=ACTIVITY_ID,
                    fee_code="CN_ANNUITY_FEE_INV",
                    fee_name="年费",
                    fee_year_key=4,
                    official_full_amount=Decimal("1200.00"),
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=Decimal("1200.00"),
                    source_amount=None,
                    source_date=DUE_DATE,
                    difference_review_state="MATCHED",
                    current_identity_key=None,
                )
            )
            transaction.flush()
            transaction.execute(
                update(FutureAnnuityReductionLineage)
                .where(FutureAnnuityReductionLineage.annuity_task_id == task_id)
                .values(fee_obligation_line_id="future-annuity-wrong-line")
            )
            transaction.commit()
    else:
        approval_id = "future-annuity-illegal-zero-approval"
        _seed_reduction_approval(session_factory, approval_id)
        with session_factory() as transaction:
            transaction.execute(
                update(FutureAnnuityReductionLineage)
                .where(FutureAnnuityReductionLineage.annuity_task_id == task_id)
                .values(reduction_approval_id=approval_id)
            )
            transaction.commit()

    with session_factory() as transaction:
        before = transaction.scalar(select(func.count()).select_from(CaseActivityEvent))
        _expect_error(
            FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == before
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


@pytest.mark.parametrize("payload_mode", ["malformed", "line_divergent"])
def test_generic_replay_payload_conflicts_map_to_lineage_conflict(
    session_factory: sessionmaker,
    payload_mode: str,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        created = recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    with session_factory() as transaction:
        activity = transaction.get(CaseActivityEvent, created.activity_id)
        assert activity is not None
        if payload_mode == "malformed":
            activity.payload_json = "{"
        else:
            payload = json.loads(activity.payload_json)
            payload["obligation"]["lines"][0]["fee_name"] = "不同年费"
            activity.payload_json = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        transaction.commit()

    with session_factory() as transaction:
        error = _expect_error(
            FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert error.details["cause"] in {
            "FEE_OBLIGATION_STORED_STATE_INVALID",
            "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
        }


@pytest.mark.parametrize("wrong_result", ["obligation", "activity", "line"])
def test_wrong_generic_reused_result_is_lineage_conflict(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    wrong_result: str,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    original_recognize = annuity_service.recognize_obligation

    def wrong_recognize(command, transaction):
        delegated = original_recognize(command, transaction)
        if wrong_result == "obligation":
            return replace(
                delegated,
                obligation=replace(delegated.obligation, id="wrong-obligation"),
            )
        if wrong_result == "activity":
            return replace(delegated, activity_id="wrong-activity")
        return replace(
            delegated,
            obligation=replace(
                delegated.obligation,
                lines=(replace(delegated.obligation.lines[0], id="wrong-line"),),
            ),
        )

    monkeypatch.setattr(annuity_service, "recognize_obligation", wrong_recognize)
    with session_factory() as transaction:
        _expect_error(
            FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )


def test_other_generic_replay_error_remains_obligation_conflict(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    def fail_recognize(_command, _transaction):
        raise BusinessError(
            code="FEE_OBLIGATION_UNEXPECTED_TEST_CONFLICT",
            message="test",
            status_code=409,
        )

    monkeypatch.setattr(annuity_service, "recognize_obligation", fail_recognize)
    with session_factory() as transaction:
        error = _expect_error(
            FutureAnnuityObligationErrorCode.OBLIGATION_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert error.details == {"cause": "FEE_OBLIGATION_UNEXPECTED_TEST_CONFLICT"}


def test_same_key_source_or_reduction_change_conflicts_without_partial_write(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        recognize_future_annuity_obligation(_command(task_id), transaction)
        transaction.commit()

    changed = (
        {"source_evidence_content_hash": f"sha256:{'b' * 64}"},
        {
            "reduction_input": FeeReductionInput(
                reduction_ratio=Decimal("0.7"),
                provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
            ),
            "reduction_approval_id": "missing-approval",
        },
    )
    for changes in changed:
        with session_factory() as transaction:
            _expect_error(
                FutureAnnuityObligationErrorCode.IDEMPOTENCY_CONFLICT,
                409,
                lambda changes=changes: recognize_future_annuity_obligation(
                    _command(task_id, **changes), transaction
                ),
            )
            assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1


def test_fresh_projection_rate_and_reduction_fail_closed(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        case.official_procedure_stage = "GRANT_REGISTRATION"
        transaction.commit()
    with session_factory() as transaction:
        _expect_error(
            FutureAnnuityObligationErrorCode.PROJECTION_CONFLICT,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )

    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        case.official_procedure_stage = "GRANT_ANNOUNCED"
        rate = transaction.get(FeeRate, "future-annuity-inv-rate")
        assert rate is not None
        rate.calc_params = json.dumps({"schema": "CNIPA_ANNUITY_TIER_V1", "tiers": []})
        transaction.commit()
    with session_factory() as transaction:
        _expect_error(
            FutureAnnuityObligationErrorCode.RATE_INVALID,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )

    with session_factory() as transaction:
        rate = transaction.get(FeeRate, "future-annuity-inv-rate")
        assert rate is not None
        rate.calc_params = CALC_PARAMS
        transaction.commit()
    with session_factory() as transaction:
        _expect_error(
            FutureAnnuityObligationErrorCode.REDUCTION_INVALID,
            400,
            lambda: recognize_future_annuity_obligation(
                _command(
                    task_id,
                    reduction_input=FeeReductionInput(
                        reduction_ratio=Decimal("0.7"),
                        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
                    ),
                    reduction_approval_id=None,
                ),
                transaction,
            ),
        )


def test_exact_canonical_rate_amount_drift_fails_without_obligation_or_carrier_write(
    session_factory: sessionmaker,
) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        rate = transaction.get(FeeRate, "future-annuity-inv-rate")
        assert rate is not None
        rate.calc_params = CALC_PARAMS.replace(
            '"amount":"1200.00","from":4',
            '"amount":"1201.00","from":4',
        )
        transaction.commit()

    with session_factory() as transaction:
        _expect_error(
            FutureAnnuityObligationErrorCode.RATE_INVALID,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 0
        task = transaction.get(AnnuityTask, task_id)
        assert task is not None
        assert (
            task.source_activity_id,
            task.source_document_id,
            task.source_evidence_version_id,
            task.source_evidence_content_hash,
            task.fee_obligation_id,
            task.grant_fee_year_key,
        ) == (None, None, None, None, None, None)


def test_dirty_transaction_fails_before_read_or_write(session_factory: sessionmaker) -> None:
    task_id = _seed(session_factory)
    with session_factory() as transaction:
        transaction.add(Client(id="pending-client", name_cn="未刷新客户"))
        _expect_error(
            FutureAnnuityObligationErrorCode.TRANSACTION_DIRTY,
            409,
            lambda: recognize_future_annuity_obligation(_command(task_id), transaction),
        )
        assert transaction.get(AnnuityTask, task_id).fee_obligation_id is None
