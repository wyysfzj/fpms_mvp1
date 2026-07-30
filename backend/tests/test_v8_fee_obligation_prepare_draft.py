from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from importlib import import_module, util
from inspect import Parameter, signature
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
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligationDraftItemLink,
)
from app.modules.fees.models import FeeObligation as FeeObligationModel
from app.modules.fees.models import FeeObligationLine as FeeObligationLineModel
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDraftItemLinkResult,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
    FeeSourceStatus,
    PrepareFeeObligationDraftCommand,
    PrepareFeeObligationDraftResult,
)

SERVICE_MODULE = "app.modules.fees.obligation_service"
SERVICE_SPEC = util.find_spec(SERVICE_MODULE)

CASE_ID = "case-fee-prepare-draft"
RECOGNITION_ID = "recognition-fee-draft"
INSTRUCTION_ID = "instruction-fee-draft-pay"
OBLIGATION_ID = "obligation-fee-draft"
ACTOR_ID = "actor-fee-draft"
LINE_IDS = ("line-fee-draft-a", "line-fee-draft-b")


def _identity_key(fee_code: str, fee_year_key: int) -> str:
    return hashlib.sha256(
        f"{CASE_ID}|{RECOGNITION_ID}|{fee_code}|{fee_year_key}".encode()
    ).hexdigest()


def _seed_actionable_obligation(
    transaction: Session,
    *,
    instruction: FeeClientInstructionStatus = FeeClientInstructionStatus.PAY,
    source_status: FeeSourceStatus = FeeSourceStatus.VERIFIED,
    line_review_state: FeeDifferenceReviewState = FeeDifferenceReviewState.MATCHED,
    current_line_identity: bool = True,
) -> None:
    has_instruction = instruction is not FeeClientInstructionStatus.PENDING
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="NO-FEE-PREPARE-DRAFT",
            status="OPEN",
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            legal_status=LegalStatus.APPLICATION_PENDING.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=2 if has_instruction else 1,
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
            idempotency_key="recognize:fee-draft",
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
    if has_instruction:
        transaction.add(
            CaseActivityEvent(
                id=INSTRUCTION_ID,
                case_id=CASE_ID,
                sequence=2,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_CLIENT_INSTRUCTION_RECORDED",
                source_activity_id=RECOGNITION_ID,
                occurred_at=datetime(2026, 7, 13, 10, 5),
                effective_at=datetime(2026, 7, 13, 10, 5),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                new_business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                old_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
                new_official_procedure_stage=(OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value),
                old_legal_status=LegalStatus.APPLICATION_PENDING.value,
                new_legal_status=LegalStatus.APPLICATION_PENDING.value,
                actor_id=ACTOR_ID,
                reviewer_id=None,
                idempotency_key=f"instruction:{instruction.value.lower()}",
                supersedes_event_id=None,
                payload_json=json.dumps(
                    {
                        "actor_id": ACTOR_ID,
                        "instruction": instruction.value,
                        "obligation_id": OBLIGATION_ID,
                        "previous_instruction_status": "PENDING",
                        "schema": "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1",
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
            source_status=source_status.value,
            client_instruction_status=instruction.value,
            draft_status=FeeObligationDraftStatus.NOT_CREATED.value,
            payment_status=FeePaymentStatus.UNPAID.value,
            official_evidence_status=FeeOfficialEvidenceStatus.NOT_APPLICABLE.value,
            created_by=ACTOR_ID,
            updated_by=ACTOR_ID,
        )
    )
    for line_id, fee_code, fee_name, amount in (
        (LINE_IDS[0], "SERVICE-FILING", "申请服务费", Decimal("1000.00")),
        (LINE_IDS[1], "SERVICE-REVIEW", "审核服务费", Decimal("200.00")),
    ):
        transaction.add(
            FeeObligationLineModel(
                id=line_id,
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=RECOGNITION_ID,
                fee_code=fee_code,
                fee_name=fee_name,
                fee_year_key=0,
                official_full_amount=None,
                reduction_ratio=Decimal("0.0000"),
                payable_amount=amount,
                source_amount=amount,
                source_date=date(2026, 7, 13),
                difference_review_state=line_review_state.value,
                current_identity_key=(
                    _identity_key(fee_code, 0) if current_line_identity else None
                ),
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            )
        )
    transaction.commit()


def _command(
    *,
    actor_id: str = ACTOR_ID,
    idempotency_key: str = "draft:fee-obligation",
) -> PrepareFeeObligationDraftCommand:
    return PrepareFeeObligationDraftCommand(
        obligation_id=OBLIGATION_ID,
        actor_id=actor_id,
        idempotency_key=idempotency_key,
    )


def _prepare(
    command: PrepareFeeObligationDraftCommand,
    transaction: Session,
) -> PrepareFeeObligationDraftResult:
    assert SERVICE_SPEC is not None
    service = import_module(SERVICE_MODULE)
    if not hasattr(service, "prepare_draft"):
        pytest.skip("prepare_draft is the intentional RED")
    return service.prepare_draft(command, transaction)


def _expect_error(
    status_code: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.status_code == status_code
    return captured.value


def _draft_activities(transaction: Session) -> list[CaseActivityEvent]:
    return list(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED")
            .order_by(CaseActivityEvent.sequence)
        )
    )


def _downstream_counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeItem)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationDraftItemLink)) or 0,
        len(_draft_activities(transaction)),
    )


def test_prepare_draft_exposes_exact_callable_and_creates_one_atomic_draft(
    session_factory: sessionmaker,
) -> None:
    assert SERVICE_SPEC is not None
    service = import_module(SERVICE_MODULE)
    assert hasattr(service, "prepare_draft"), (
        "missing frozen behavior: obligation_service.py must expose prepare_draft()"
    )
    prepare_draft = service.prepare_draft
    parameters = tuple(signature(prepare_draft).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == ("command", "transaction")
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
    )
    assert get_type_hints(prepare_draft) == {
        "command": PrepareFeeObligationDraftCommand,
        "transaction": Session,
        "return": PrepareFeeObligationDraftResult,
    }

    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        result = _prepare(_command(), transaction)

        assert type(result) is PrepareFeeObligationDraftResult
        assert result.obligation_id == OBLIGATION_ID
        assert result.idempotency_key == "draft:fee-obligation"
        assert result.activity_reused is False
        assert len(result.links) == 2
        assert all(type(link) is FeeDraftItemLinkResult for link in result.links)
        assert tuple(link.obligation_line_id for link in result.links) == LINE_IDS
        assert all(link.reused is False for link in result.links)

        draft = transaction.get(FeeDraft, result.draft_id)
        assert draft is not None
        assert (
            draft.case_id,
            draft.currency,
            draft.status,
            draft.total_gov,
            draft.total_service,
            draft.total_misc,
            draft.amount,
        ) == (
            CASE_ID,
            "CNY",
            "OPEN",
            Decimal("0.00"),
            Decimal("1200.00"),
            Decimal("0.00"),
            Decimal("1200.00"),
        )
        items = tuple(
            transaction.scalars(
                select(FeeItem).where(FeeItem.draft_id == draft.id).order_by(FeeItem.fee_code)
            )
        )
        assert tuple(
            (
                item.id,
                item.case_id,
                item.fee_code,
                item.fee_name,
                item.fee_type,
                item.year_no,
                item.amount,
            )
            for item in items
        ) == (
            (
                result.links[0].fee_item_id,
                CASE_ID,
                "SERVICE-FILING",
                "申请服务费",
                "SERVICE",
                0,
                Decimal("1000.00"),
            ),
            (
                result.links[1].fee_item_id,
                CASE_ID,
                "SERVICE-REVIEW",
                "审核服务费",
                "SERVICE",
                0,
                Decimal("200.00"),
            ),
        )
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        assert header.draft_status == FeeObligationDraftStatus.CREATED.value
        assert header.updated_by == ACTOR_ID

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        assert activity.activity_type == "FEE_DRAFT_CREATED"
        assert activity.lane == ActivityLane.FEE.value
        assert activity.source_activity_id == INSTRUCTION_ID
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert activity.supersedes_event_id is None
        assert json.loads(activity.payload_json) == {
            "actor_id": ACTOR_ID,
            "center_changes": {},
            "draft_id": result.draft_id,
            "links": [
                {
                    "fee_item_id": link.fee_item_id,
                    "obligation_line_id": link.obligation_line_id,
                }
                for link in result.links
            ],
            "obligation_id": OBLIGATION_ID,
            "schema": "FPMS_FEE_DRAFT_CREATED_V1",
        }
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert (
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.status,
            case.lifecycle_revision,
        ) == (
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            "OPEN",
            3,
        )


def test_same_command_reuses_exact_links_draft_and_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        first = _prepare(_command(), transaction)
        transaction.commit()
        before = _downstream_counts(transaction)

        replay = _prepare(_command(), transaction)

        assert replay == replace(
            first,
            links=tuple(replace(link, reused=True) for link in first.links),
            activity_reused=True,
        )
        assert _downstream_counts(transaction) == before


@pytest.mark.parametrize(
    ("instruction", "source_status", "line_review_state"),
    (
        (
            FeeClientInstructionStatus.PENDING,
            FeeSourceStatus.VERIFIED,
            FeeDifferenceReviewState.MATCHED,
        ),
        (
            FeeClientInstructionStatus.HOLD,
            FeeSourceStatus.VERIFIED,
            FeeDifferenceReviewState.MATCHED,
        ),
        (
            FeeClientInstructionStatus.ABANDON,
            FeeSourceStatus.VERIFIED,
            FeeDifferenceReviewState.MATCHED,
        ),
        (
            FeeClientInstructionStatus.PAY,
            FeeSourceStatus.REVIEW_REQUIRED,
            FeeDifferenceReviewState.MATCHED,
        ),
        (
            FeeClientInstructionStatus.PAY,
            FeeSourceStatus.VERIFIED,
            FeeDifferenceReviewState.SOURCE_PENDING,
        ),
    ),
)
def test_non_actionable_instruction_source_or_line_policy_creates_nothing(
    session_factory: sessionmaker,
    instruction: FeeClientInstructionStatus,
    source_status: FeeSourceStatus,
    line_review_state: FeeDifferenceReviewState,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(
            transaction,
            instruction=instruction,
            source_status=source_status,
            line_review_state=line_review_state,
        )

        _expect_error(409, lambda: _prepare(_command(), transaction))

        assert _downstream_counts(transaction) == (0, 0, 0, 0)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        assert header.draft_status == FeeObligationDraftStatus.NOT_CREATED.value


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("obligation_status", FeeObligationStatus.SUPERSEDED.value),
        ("payment_status", FeePaymentStatus.PAID.value),
        ("official_evidence_status", FeeOfficialEvidenceStatus.VERIFIED.value),
    ),
)
def test_locked_obligation_state_creates_nothing(
    session_factory: sessionmaker,
    field: str,
    value: str,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        assert header is not None
        setattr(header, field, value)
        transaction.commit()

        _expect_error(409, lambda: _prepare(_command(), transaction))

        assert _downstream_counts(transaction) == (0, 0, 0, 0)


def test_invalid_current_line_identity_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction, current_line_identity=False)

        _expect_error(409, lambda: _prepare(_command(), transaction))

        assert _downstream_counts(transaction) == (0, 0, 0, 0)


def test_changed_command_or_new_key_after_creation_is_not_replay(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        _prepare(_command(), transaction)
        transaction.commit()

        _expect_error(
            409,
            lambda: _prepare(_command(actor_id="different-actor"), transaction),
        )
        _expect_error(
            409,
            lambda: _prepare(
                _command(idempotency_key="draft:fee-obligation:new"),
                transaction,
            ),
        )
        assert _downstream_counts(transaction) == (1, 2, 2, 1)


@pytest.mark.parametrize(
    ("command", "expected_status"),
    (
        (object(), 400),
        (replace(_command(), obligation_id=""), 400),
        (replace(_command(), obligation_id="x" * 37), 400),
        (replace(_command(), actor_id=" "), 400),
        (replace(_command(), actor_id="x" * 37), 400),
        (replace(_command(), idempotency_key=""), 400),
        (replace(_command(), idempotency_key="x" * 129), 400),
        (replace(_command(), obligation_id="missing-obligation"), 404),
    ),
)
def test_invalid_command_or_missing_obligation_writes_nothing(
    session_factory: sessionmaker,
    command: object,
    expected_status: int,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)

        _expect_error(
            expected_status,
            lambda: _prepare(command, transaction),  # type: ignore[arg-type]
        )

        assert _downstream_counts(transaction) == (0, 0, 0, 0)


def test_dirty_entry_fails_before_any_write(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        transaction.add(Case(id="pending-case", case_no="PENDING-CASE", status="OPEN"))

        _expect_error(409, lambda: _prepare(_command(), transaction))

        assert _downstream_counts(transaction) == (0, 0, 0, 0)


def test_caller_rollback_removes_draft_items_links_activity_and_header_change(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        _prepare(_command(), transaction)
        transaction.rollback()

    with session_factory() as verification:
        assert _downstream_counts(verification) == (0, 0, 0, 0)
        header = verification.get(FeeObligationModel, OBLIGATION_ID)
        case = verification.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.draft_status == FeeObligationDraftStatus.NOT_CREATED.value
        assert case.lifecycle_revision == 2


def test_failure_after_append_rolls_back_every_service_write(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    if not hasattr(service, "prepare_draft"):
        pytest.skip("prepare_draft is the intentional RED")
    original_append = service.append_case_activity

    def append_then_fail(*args, **kwargs):
        original_append(*args, **kwargs)
        raise RuntimeError("forced after append")

    with session_factory() as transaction:
        _seed_actionable_obligation(transaction)
        with patch.object(service, "append_case_activity", side_effect=append_then_fail):
            with pytest.raises(RuntimeError, match="forced after append"):
                _prepare(_command(), transaction)

        assert _downstream_counts(transaction) == (0, 0, 0, 0)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        case = transaction.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.draft_status == FeeObligationDraftStatus.NOT_CREATED.value
        assert case.lifecycle_revision == 2
        assert transaction.scalar(select(func.count()).select_from(Case)) == 1
