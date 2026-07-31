from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from importlib import import_module
from inspect import Parameter, signature
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
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
    FeeSourceStatus,
)
from app.modules.fees.schemas import FeeDraftCreateIn

SERVICE_MODULE = "app.modules.fees.service"

CASE_ID = "case-generic-draft-adapter"
OTHER_CASE_ID = "case-generic-draft-other"
RECOGNITION_ID = "recognition-generic-draft"
INSTRUCTION_ID = "instruction-generic-draft"
OBLIGATION_ID = "obligation-generic-draft"
LINE_ID = "line-generic-draft"
ACTOR_ID = "actor-generic-draft"


def _identity_key() -> str:
    return hashlib.sha256(
        f"{CASE_ID}|{RECOGNITION_ID}|SERVICE-FILING|0".encode()
    ).hexdigest()


def _seed_obligation(
    transaction: Session,
    *,
    instruction: FeeClientInstructionStatus = FeeClientInstructionStatus.PAY,
) -> None:
    transaction.add_all(
        (
            Case(
                id=CASE_ID,
                case_no="NO-GENERIC-DRAFT-ADAPTER",
                status="OPEN",
                business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                official_procedure_stage=(
                    OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value
                ),
                legal_status=LegalStatus.APPLICATION_PENDING.value,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
                lifecycle_revision=2,
            ),
            Case(
                id=OTHER_CASE_ID,
                case_no="NO-GENERIC-DRAFT-OTHER",
                status="OPEN",
            ),
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
                idempotency_key="recognize:generic-draft",
                supersedes_event_id=None,
                payload_json=json.dumps(
                    {
                        "obligation_id": OBLIGATION_ID,
                        "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
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
            ),
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
                source_status=FeeSourceStatus.VERIFIED.value,
                client_instruction_status=instruction.value,
                draft_status=FeeObligationDraftStatus.NOT_CREATED.value,
                payment_status=FeePaymentStatus.UNPAID.value,
                official_evidence_status=(
                    FeeOfficialEvidenceStatus.NOT_APPLICABLE.value
                ),
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            ),
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
                current_identity_key=_identity_key(),
                created_by=ACTOR_ID,
                updated_by=ACTOR_ID,
            ),
        )
    )
    transaction.commit()


def _data(
    *,
    case_id: str = CASE_ID,
    client_id: str | None = None,
    draft_type: str | None = None,
    currency: str = "CNY",
) -> FeeDraftCreateIn:
    return FeeDraftCreateIn(
        case_id=case_id,
        client_id=client_id,
        draft_type=draft_type,
        currency=currency,
    )


def _create_linked(
    transaction: Session,
    *,
    data: FeeDraftCreateIn | None = None,
    actor_id: str | None = ACTOR_ID,
) -> FeeDraft:
    service = import_module(SERVICE_MODULE)
    if "obligation_id" not in signature(service.create_fee_draft).parameters:
        pytest.skip("explicit obligation_id adapter is the intentional RED")
    return service.create_fee_draft(
        transaction,
        data=data or _data(),
        actor_id=actor_id,
        obligation_id=OBLIGATION_ID,
    )


def _expect_error(
    status_code: int,
    action: Callable[[], object],
) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.status_code == status_code
    return captured.value


def _counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeItem)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationDraftItemLink))
        or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED")
        )
        or 0,
    )


def test_linked_generic_entrypoint_delegates_to_prepare_draft_without_second_activity(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    parameters = tuple(signature(service.create_fee_draft).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "db",
        "data",
        "actor_id",
        "obligation_id",
    )
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.KEYWORD_ONLY,
        Parameter.KEYWORD_ONLY,
        Parameter.KEYWORD_ONLY,
    )
    assert parameters[-1].annotation == "str | None"
    assert parameters[-1].default is None

    with session_factory() as transaction:
        _seed_obligation(transaction)
        draft = _create_linked(transaction)

        activity = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED"
            )
        )
        link = transaction.scalar(select(FeeObligationDraftItemLink))
        assert activity is not None and link is not None
        assert draft.id == transaction.get(FeeItem, link.fee_item_id).draft_id
        assert activity.source_activity_id == INSTRUCTION_ID
        assert activity.idempotency_key == f"generic-fee-draft:{OBLIGATION_ID}"
        assert json.loads(activity.payload_json)["draft_id"] == draft.id
        assert _counts(transaction) == (1, 1, 1, 1)


def test_linked_entrypoint_reuses_deep_draft_link_and_activity_identity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_obligation(transaction)
        first = _create_linked(transaction)
        transaction.commit()
        before = _counts(transaction)

        replay = _create_linked(transaction)

        assert replay.id == first.id
        assert _counts(transaction) == before == (1, 1, 1, 1)


def test_non_pay_instruction_does_not_create_generic_draft_or_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_obligation(
            transaction,
            instruction=FeeClientInstructionStatus.HOLD,
        )

        _expect_error(409, lambda: _create_linked(transaction))

        assert _counts(transaction) == (0, 0, 0, 0)


@pytest.mark.parametrize(
    "data",
    (
        _data(case_id=OTHER_CASE_ID),
        _data(client_id="different-client"),
        _data(draft_type="SPECIAL"),
        _data(currency="USD"),
    ),
)
def test_linked_request_mismatch_rolls_back_deep_writes(
    session_factory: sessionmaker,
    data: FeeDraftCreateIn,
) -> None:
    with session_factory() as transaction:
        _seed_obligation(transaction)

        _expect_error(409, lambda: _create_linked(transaction, data=data))

        assert _counts(transaction) == (0, 0, 0, 0)
        header = transaction.get(FeeObligationModel, OBLIGATION_ID)
        case = transaction.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.draft_status == FeeObligationDraftStatus.NOT_CREATED.value
        assert case.lifecycle_revision == 2


def test_linked_request_requires_actor_before_calling_deep_seam(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        _seed_obligation(transaction)
        if "obligation_id" not in signature(service.create_fee_draft).parameters:
            pytest.skip("explicit obligation_id adapter is the intentional RED")
        with patch.object(
            service,
            "prepare_draft",
            side_effect=AssertionError("deep seam must not run without actor"),
        ):
            _expect_error(
                409,
                lambda: _create_linked(transaction, actor_id=None),
            )
        assert _counts(transaction) == (0, 0, 0, 0)


def test_caller_rollback_removes_linked_draft_and_deep_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_obligation(transaction)
        _create_linked(transaction)
        transaction.rollback()

    with session_factory() as verification:
        assert _counts(verification) == (0, 0, 0, 0)
        header = verification.get(FeeObligationModel, OBLIGATION_ID)
        case = verification.get(Case, CASE_ID)
        assert header is not None and case is not None
        assert header.draft_status == FeeObligationDraftStatus.NOT_CREATED.value
        assert case.lifecycle_revision == 2


def test_legacy_unlinked_draft_keeps_historical_path(
    session_factory: sessionmaker,
) -> None:
    service = import_module(SERVICE_MODULE)
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="NO-LEGACY-GENERIC-DRAFT",
                status="OPEN",
            )
        )
        transaction.commit()
        with patch.object(
            service,
            "prepare_draft",
            side_effect=AssertionError("legacy path must not call prepare_draft"),
            create=True,
        ):
            draft = service.create_fee_draft(
                transaction,
                data=_data(),
                actor_id=None,
            )
        assert draft.case_id == CASE_ID
        assert draft.amount == Decimal("0.00")

    with session_factory() as verification:
        assert verification.scalar(select(func.count()).select_from(FeeDraft)) == 1
        assert _counts(verification) == (1, 0, 0, 0)
