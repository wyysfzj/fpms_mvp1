from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from importlib import import_module, util
from inspect import Parameter, signature
from typing import get_type_hints
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy import event, false, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import Select

from app.core.errors import BusinessError
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import Document
from app.modules.fees.models import FeeObligation as FeeObligationModel
from app.modules.fees.models import FeeObligationLine as FeeObligationLineModel
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationLine,
    FeeObligationLineInput,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentStatus,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
    RecognizeFeeObligationResult,
)

SERVICE_MODULE = "app.modules.fees.obligation_service"
SERVICE_SPEC = util.find_spec(SERVICE_MODULE)

CASE_A = "case-fee-recognize-a"
CASE_B = "case-fee-recognize-b"
SOURCE_A = "source-fee-recognize-a"
SOURCE_B = "source-fee-recognize-b"
SOURCE_C = "source-fee-recognize-c"
DOCUMENT_A = "document-fee-recognize-a"
DOCUMENT_B = "document-fee-recognize-b"
ACTOR_ID = "actor-fee-recognize"
EFFECTIVE_AT = datetime(2026, 7, 13, 10, 0)
OCCURRED_AT = datetime(2026, 7, 13, 9, 55)
CAPTURED_AT = datetime(2026, 7, 13, 9, 50)

OPEN_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)


def _case(*, case_id: str = CASE_A, revision: int = 1) -> Case:
    return Case(
        id=case_id,
        case_no=f"NO-{case_id}",
        status="OPEN",
        business_stage=OPEN_PROJECTION.business_stage.value,
        official_procedure_stage=OPEN_PROJECTION.official_procedure_stage.value,
        legal_status=OPEN_PROJECTION.legal_status.value,
        lifecycle_verification_status=(OPEN_PROJECTION.lifecycle_verification_status.value),
        lifecycle_revision=revision,
    )


def _seed_source(
    transaction: Session,
    *,
    source_id: str = SOURCE_A,
    case_id: str = CASE_A,
    sequence: int = 1,
    confirmation_status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
    evidence: tuple[EvidenceReference, ...] | None = None,
) -> CaseActivityEvent:
    if evidence is None:
        evidence = (
            EvidenceReference(
                case_id=case_id,
                evidence_kind="DOCUMENT",
                object_type="DocumentEvidenceVersion",
                object_id=f"evidence-{source_id}",
                content_hash=f"sha256:{source_id}",
                captured_at=CAPTURED_AT,
            ),
        )
    source = CaseActivityEvent(
        id=source_id,
        case_id=case_id,
        sequence=sequence,
        lane=ActivityLane.DOCUMENT.value,
        activity_type="OFFICIAL_FEE_SOURCE_CONFIRMED",
        occurred_at=OCCURRED_AT,
        effective_at=EFFECTIVE_AT,
        confirmation_status=confirmation_status.value,
        old_business_stage=OPEN_PROJECTION.business_stage.value,
        new_business_stage=OPEN_PROJECTION.business_stage.value,
        old_official_procedure_stage=OPEN_PROJECTION.official_procedure_stage.value,
        new_official_procedure_stage=OPEN_PROJECTION.official_procedure_stage.value,
        old_legal_status=OPEN_PROJECTION.legal_status.value,
        new_legal_status=OPEN_PROJECTION.legal_status.value,
        actor_id=ACTOR_ID,
        reviewer_id="reviewer-fee-recognize",
        idempotency_key=f"source:{source_id}",
        payload_json='{"source":"real"}',
    )
    transaction.add(source)
    transaction.add_all(
        CaseActivityEventEvidence(
            id=f"link-{sequence}-{index}-{case_id}",
            case_id=case_id,
            activity_id=source_id,
            evidence_kind=reference.evidence_kind,
            object_type=reference.object_type,
            object_id=reference.object_id,
            content_hash=reference.content_hash,
            captured_at=reference.captured_at,
        )
        for index, reference in enumerate(evidence)
    )
    return source


def _seed_case_source_document(
    transaction: Session,
    *,
    case_id: str = CASE_A,
    source_id: str = SOURCE_A,
    document_id: str | None = DOCUMENT_A,
    confirmation_status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
    evidence: tuple[EvidenceReference, ...] | None = None,
) -> None:
    transaction.add(_case(case_id=case_id))
    _seed_source(
        transaction,
        source_id=source_id,
        case_id=case_id,
        confirmation_status=confirmation_status,
        evidence=evidence,
    )
    if document_id is not None:
        transaction.add(Document(id=document_id, case_id=case_id, direction="IN"))
    transaction.commit()


def _add_source(
    transaction: Session,
    *,
    source_id: str,
    confirmation_status: ConfirmationStatus = ConfirmationStatus.CONFIRMED,
    evidence: tuple[EvidenceReference, ...] = (),
) -> None:
    case = transaction.get(Case, CASE_A)
    assert case is not None
    result = append_case_activity(
        LifecycleEventCommand(
            case_id=CASE_A,
            event_type="OFFICIAL_FEE_SOURCE_CONFIRMED",
            lane=ActivityLane.DOCUMENT,
            effective_at=EFFECTIVE_AT,
            occurred_at=OCCURRED_AT,
            evidence_refs=evidence,
            actor_id=ACTOR_ID,
            reviewer_id="reviewer-fee-recognize",
            idempotency_key=f"source:{source_id}",
            confirmation_status=confirmation_status,
            payload={"source": "real"},
        ),
        transaction,
        previous_projection=OPEN_PROJECTION,
        current_projection=OPEN_PROJECTION,
        legacy_case_status=case.status,
        conflict_codes=(),
    )
    transaction.execute(
        CaseActivityEvent.__table__.update()
        .where(CaseActivityEvent.id == result.activity_id)
        .values(id=source_id)
    )
    transaction.flush()


def _line(
    *,
    fee_code: str = "GOV-FILING",
    fee_name: str = "申请费",
    fee_year_key: int = 0,
    official_full_amount: Decimal | None = Decimal("900.00"),
    reduction_ratio: Decimal = Decimal("0.8500"),
    payable_amount: Decimal = Decimal("135.00"),
    source_amount: Decimal | None = Decimal("135.00"),
    source_date: date | None = date(2026, 7, 13),
    difference_review_state: FeeDifferenceReviewState = FeeDifferenceReviewState.MATCHED,
) -> FeeObligationLineInput:
    return FeeObligationLineInput(
        fee_code=fee_code,
        fee_name=fee_name,
        fee_year_key=fee_year_key,
        official_full_amount=official_full_amount,
        reduction_ratio=reduction_ratio,
        payable_amount=payable_amount,
        source_amount=source_amount,
        source_date=source_date,
        difference_review_state=difference_review_state,
    )


def _command(
    *,
    case_id: str = CASE_A,
    source_activity_id: str = SOURCE_A,
    source_document_id: str | None = DOCUMENT_A,
    fee_domain: FeeDomain = FeeDomain.GOV,
    obligation_type: str = "PATENT_APPLICATION",
    due_date: date | None = date(2026, 8, 13),
    currency: str = "CNY",
    source_status: FeeSourceStatus = FeeSourceStatus.VERIFIED,
    lines: tuple[FeeObligationLineInput, ...] | None = None,
    actor_id: str = ACTOR_ID,
    idempotency_key: str = "recognize-fee-1",
    supersedes_obligation_id: str | None = None,
    supersede_reason: str | None = None,
) -> RecognizeFeeObligationCommand:
    if lines is None:
        lines = (
            _line(
                fee_code="GOV-EXAM",
                fee_name="实质审查费",
                payable_amount=Decimal("375.00"),
                source_amount=Decimal("375.00"),
            ),
            _line(),
        )
    return RecognizeFeeObligationCommand(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_document_id=source_document_id,
        fee_domain=fee_domain,
        obligation_type=obligation_type,
        due_date=due_date,
        currency=currency,
        source_status=source_status,
        lines=lines,
        actor_id=actor_id,
        idempotency_key=idempotency_key,
        supersedes_obligation_id=supersedes_obligation_id,
        supersede_reason=supersede_reason,
    )


def _recognize(
    command: RecognizeFeeObligationCommand,
    transaction: Session,
) -> RecognizeFeeObligationResult:
    assert SERVICE_SPEC is not None, (
        "missing frozen behavior: obligation_service.py must expose recognize_obligation()"
    )
    recognize_obligation = import_module(SERVICE_MODULE).recognize_obligation
    return recognize_obligation(command, transaction)


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


def _identity(case_id: str, source_id: str, fee_code: str, year: int) -> str:
    raw = f"{case_id}|{source_id}|{fee_code}|{year}".encode()
    return hashlib.sha256(raw).hexdigest()


def _counts(transaction: Session) -> tuple[int, int, int, int]:
    return (
        int(transaction.scalar(select(func.count()).select_from(FeeObligationModel)) or 0),
        int(transaction.scalar(select(func.count()).select_from(FeeObligationLineModel)) or 0),
        int(transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) or 0),
        int(transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)) or 0),
    )


def _fee_activities(transaction: Session) -> list[CaseActivityEvent]:
    return list(
        transaction.scalars(
            select(CaseActivityEvent)
            .where(CaseActivityEvent.lane == ActivityLane.FEE.value)
            .order_by(CaseActivityEvent.sequence)
        )
    )


def _assert_no_pending_fee_rows(transaction: Session) -> None:
    assert not any(
        isinstance(row, (FeeObligationModel, FeeObligationLineModel)) for row in transaction.new
    )


def test_service_exposes_the_exact_frozen_public_callable() -> None:
    assert SERVICE_SPEC is not None, (
        "missing frozen behavior: obligation_service.py must expose recognize_obligation()"
    )
    recognize_obligation = import_module(SERVICE_MODULE).recognize_obligation
    parameters = tuple(signature(recognize_obligation).parameters.values())
    hints = get_type_hints(recognize_obligation)

    assert tuple(parameter.name for parameter in parameters) == ("command", "transaction")
    assert tuple(parameter.kind for parameter in parameters) == (
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_OR_KEYWORD,
    )
    assert hints == {
        "command": RecognizeFeeObligationCommand,
        "transaction": Session,
        "return": RecognizeFeeObligationResult,
    }


def test_verified_gov_creates_sorted_header_lines_and_exact_lane_only_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        command = _command()

        result = _recognize(command, transaction)

        assert type(result) is RecognizeFeeObligationResult
        assert type(result.obligation) is FeeObligation
        assert all(type(line) is FeeObligationLine for line in result.obligation.lines)
        assert result.reused is False
        assert result.idempotency_key == command.idempotency_key
        assert result.superseded_obligation_id is None
        assert UUID(result.obligation.id)
        assert result.obligation.case_id == CASE_A
        assert result.obligation.source.source_activity_id == SOURCE_A
        assert result.obligation.source.source_document_id == DOCUMENT_A
        assert result.obligation.source.status is FeeSourceStatus.VERIFIED
        assert result.obligation.fee_domain is FeeDomain.GOV
        assert result.obligation.obligation_type == "PATENT_APPLICATION"
        assert result.obligation.due_date == date(2026, 8, 13)
        assert result.obligation.currency == "CNY"
        assert result.obligation.statuses.estimate_status is None
        assert result.obligation.statuses.obligation_status is FeeObligationStatus.RECOGNIZED
        assert (
            result.obligation.statuses.client_instruction_status
            is FeeClientInstructionStatus.PENDING
        )
        assert result.obligation.statuses.draft_status is FeeObligationDraftStatus.NOT_CREATED
        assert result.obligation.statuses.pay_list_status is FeePayListStatus.NOT_CREATED
        assert result.obligation.statuses.payment_status is FeePaymentStatus.UNPAID
        assert (
            result.obligation.statuses.official_evidence_status is FeeOfficialEvidenceStatus.PENDING
        )
        assert [line.fee_code for line in result.obligation.lines] == [
            "GOV-EXAM",
            "GOV-FILING",
        ]
        assert [line.current_identity_key for line in result.obligation.lines] == [
            _identity(CASE_A, SOURCE_A, "GOV-EXAM", 0),
            _identity(CASE_A, SOURCE_A, "GOV-FILING", 0),
        ]

        activities = _fee_activities(transaction)
        assert len(activities) == 1
        activity = activities[0]
        assert activity.id == result.activity_id
        assert activity.activity_type == "FEE_OBLIGATION_RECOGNIZED"
        assert activity.source_activity_id == SOURCE_A
        assert activity.effective_at == EFFECTIVE_AT
        assert activity.occurred_at == OCCURRED_AT
        assert activity.actor_id == ACTOR_ID
        assert activity.reviewer_id == "reviewer-fee-recognize"
        assert activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        assert activity.old_business_stage == activity.new_business_stage
        assert activity.old_official_procedure_stage == activity.new_official_procedure_stage
        assert activity.old_legal_status == activity.new_legal_status
        payload = json.loads(activity.payload_json)
        assert payload == {
            "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            "obligation_id": result.obligation.id,
            "obligation": {
                "actor_id": ACTOR_ID,
                "case_id": CASE_A,
                "currency": "CNY",
                "due_date": "2026-08-13",
                "fee_domain": "GOV",
                "lines": [
                    {
                        "difference_review_state": "MATCHED",
                        "fee_code": "GOV-EXAM",
                        "fee_name": "实质审查费",
                        "fee_year_key": 0,
                        "official_full_amount": "900.00",
                        "payable_amount": "375.00",
                        "reduction_ratio": "0.8500",
                        "source_amount": "375.00",
                        "source_date": "2026-07-13",
                    },
                    {
                        "difference_review_state": "MATCHED",
                        "fee_code": "GOV-FILING",
                        "fee_name": "申请费",
                        "fee_year_key": 0,
                        "official_full_amount": "900.00",
                        "payable_amount": "135.00",
                        "reduction_ratio": "0.8500",
                        "source_amount": "135.00",
                        "source_date": "2026-07-13",
                    },
                ],
                "obligation_type": "PATENT_APPLICATION",
                "source_activity_id": SOURCE_A,
                "source_document_id": DOCUMENT_A,
                "source_status": "VERIFIED",
                "supersede_reason": None,
                "supersedes_obligation_id": None,
            },
        }
        assert activity.payload_json == json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        assert transaction.get(Case, CASE_A).lifecycle_revision == 2


def test_service_never_commits_and_caller_rollback_removes_complete_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        with (
            patch.object(transaction, "commit", wraps=transaction.commit) as commit_spy,
            patch.object(transaction, "rollback", wraps=transaction.rollback) as rollback_spy,
        ):
            result = _recognize(_command(), transaction)
            assert _counts(transaction) == (1, 2, 2, 2)
            assert commit_spy.call_count == 0
            assert rollback_spy.call_count == 0
        transaction.rollback()

    with session_factory() as observer:
        assert _counts(observer) == (0, 0, 1, 1)
        assert observer.get(Case, CASE_A).lifecycle_revision == 1
        assert observer.get(FeeObligationModel, result.obligation.id) is None


def test_service_domain_statuses_and_exact_frozen_results(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        gov = _recognize(_command(lines=(_line(),)), transaction)
        transaction.commit()

        _add_source(transaction, source_id=SOURCE_B)
        service = _recognize(
            _command(
                source_activity_id=SOURCE_B,
                source_document_id=None,
                fee_domain=FeeDomain.SERVICE,
                obligation_type="SERVICE_FEE",
                lines=(
                    _line(
                        fee_code="SERVICE-DRAFTING",
                        fee_name="撰写服务费",
                        official_full_amount=None,
                        reduction_ratio=Decimal("0.0000"),
                        payable_amount=Decimal("3000.00"),
                        source_amount=Decimal("3000.00"),
                    ),
                ),
                idempotency_key="recognize-service-1",
            ),
            transaction,
        )

        assert type(gov) is type(service) is RecognizeFeeObligationResult
        assert gov.obligation.statuses.official_evidence_status is FeeOfficialEvidenceStatus.PENDING
        assert (
            service.obligation.statuses.official_evidence_status
            is FeeOfficialEvidenceStatus.NOT_APPLICABLE
        )
        for result in (gov, service):
            assert result.obligation.statuses.estimate_status is None
            assert result.obligation.statuses.pay_list_status is FeePayListStatus.NOT_CREATED


def test_exact_replay_stays_read_only_after_later_activity_and_after_supersede(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        original_command = _command()
        original = _recognize(original_command, transaction)
        transaction.commit()

        _add_source(transaction, source_id=SOURCE_B)
        transaction.commit()
        before_later_replay = (
            _counts(transaction),
            transaction.get(Case, CASE_A).lifecycle_revision,
        )
        later_replay = _recognize(original_command, transaction)
        assert later_replay == replace(original, reused=True)
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == (
            before_later_replay
        )

        replacement = _recognize(
            _command(
                source_activity_id=SOURCE_B,
                lines=(_line(fee_code="GOV-FILING", payable_amount=Decimal("150.00")),),
                idempotency_key="recognize-fee-correction",
                supersedes_obligation_id=original.obligation.id,
                supersede_reason="官方更正",
            ),
            transaction,
        )
        transaction.commit()
        before_historical_replay = (
            _counts(transaction),
            transaction.get(Case, CASE_A).lifecycle_revision,
        )

        historical = _recognize(original_command, transaction)

        assert historical.activity_id == original.activity_id
        assert historical.obligation.id == original.obligation.id
        assert historical.obligation.statuses.obligation_status is FeeObligationStatus.SUPERSEDED
        assert all(line.current_identity_key is None for line in historical.obligation.lines)
        assert historical.reused is True
        assert historical.superseded_obligation_id is None
        assert replacement.superseded_obligation_id == original.obligation.id
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == (
            before_historical_replay
        )


@pytest.mark.parametrize("mutation", ("actor", "line", "source_evidence"))
def test_same_key_with_changed_command_line_or_evidence_is_exact_conflict(
    session_factory: sessionmaker,
    mutation: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        original = _command()
        _recognize(original, transaction)
        transaction.commit()
        changed = original
        if mutation == "actor":
            changed = replace(original, actor_id="different-actor")
        elif mutation == "line":
            changed = replace(
                original,
                lines=(
                    replace(original.lines[0], payable_amount=Decimal("376.00")),
                    original.lines[1],
                ),
            )
        else:
            source_link = transaction.scalar(
                select(CaseActivityEventEvidence).where(
                    CaseActivityEventEvidence.activity_id == SOURCE_A
                )
            )
            assert source_link is not None
            source_link.content_hash = "sha256:changed-real-source"
            transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)

        _expect_error(
            "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
            409,
            lambda: _recognize(changed, transaction),
        )
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before
        _assert_no_pending_fee_rows(transaction)


@pytest.mark.parametrize(
    ("requested_lines", "expected_code"),
    (
        (
            (
                _line(fee_code="GOV-EXAM", fee_name="实质审查费", payable_amount=Decimal("375.00")),
                _line(),
            ),
            "FEE_OBLIGATION_IDENTITY_CONFLICT",
        ),
        (
            (
                _line(),
                _line(fee_code="GOV-NEW", fee_name="新增费", payable_amount=Decimal("1.00")),
            ),
            "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        ),
    ),
)
def test_different_key_all_or_partial_current_identities_fail_without_partial_write(
    session_factory: sessionmaker,
    requested_lines: tuple[FeeObligationLineInput, ...],
    expected_code: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        _recognize(_command(), transaction)
        transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)

        _expect_error(
            expected_code,
            409,
            lambda: _recognize(
                _command(lines=requested_lines, idempotency_key="recognize-fee-other"),
                transaction,
            ),
        )
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before


def test_different_key_identities_owned_by_multiple_headers_use_mixed_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        _recognize(_command(lines=(_line(fee_code="FEE-A"),)), transaction)
        transaction.commit()
        _recognize(
            _command(
                lines=(_line(fee_code="FEE-B"),),
                idempotency_key="recognize-fee-b",
            ),
            transaction,
        )
        transaction.commit()
        before = _counts(transaction)

        _expect_error(
            "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
            409,
            lambda: _recognize(
                _command(
                    lines=(_line(fee_code="FEE-A"), _line(fee_code="FEE-B")),
                    idempotency_key="recognize-fee-combined",
                ),
                transaction,
            ),
        )
        assert _counts(transaction) == before


@pytest.mark.parametrize(
    ("command", "expected_code", "expected_field"),
    (
        (_command(lines=()), "FEE_OBLIGATION_COMMAND_INVALID", "lines"),
        (
            _command(lines=(_line(), _line())),
            "FEE_OBLIGATION_LINE_DUPLICATE",
            "lines[1]",
        ),
        (
            _command(lines=(_line(payable_amount=Decimal("1.001")),)),
            "FEE_OBLIGATION_LINE_INVALID",
            "lines[0].payable_amount",
        ),
        (
            _command(lines=(_line(reduction_ratio=Decimal("1.0001")),)),
            "FEE_OBLIGATION_LINE_INVALID",
            "lines[0].reduction_ratio",
        ),
        (
            _command(lines=(_line(source_date=datetime(2026, 7, 13, 1, 0)),)),
            "FEE_OBLIGATION_LINE_INVALID",
            "lines[0].source_date",
        ),
        (
            _command(lines=(_line(fee_year_key=True),)),
            "FEE_OBLIGATION_LINE_INVALID",
            "lines[0].fee_year_key",
        ),
        (_command(currency="cny"), "FEE_OBLIGATION_CURRENCY_INVALID", "currency"),
    ),
)
def test_line_and_command_validation_is_strict_and_writes_nothing(
    session_factory: sessionmaker,
    command: RecognizeFeeObligationCommand,
    expected_code: str,
    expected_field: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        before = _counts(transaction)

        error = _expect_error(expected_code, 400, lambda: _recognize(command, transaction))

        assert error.details == {"field": expected_field}
        assert _counts(transaction) == before


def test_incomplete_supersede_pair_is_409_and_precedes_source_reads(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        before = _counts(transaction)
        _expect_error(
            "FEE_OBLIGATION_SUPERSEDE_PAIR_INVALID",
            409,
            lambda: _recognize(
                _command(
                    case_id="missing-case",
                    source_activity_id="missing-source",
                    supersedes_obligation_id="missing-prior",
                ),
                transaction,
            ),
        )
        assert _counts(transaction) == before


@pytest.mark.parametrize(
    ("setup", "command", "expected_code", "status_code"),
    (
        ("none", _command(case_id="missing-case"), "CASE_NOT_FOUND", 404),
        (
            "base",
            _command(source_activity_id="missing-source"),
            "FEE_OBLIGATION_SOURCE_ACTIVITY_NOT_FOUND",
            409,
        ),
        (
            "cross_source",
            _command(source_activity_id=SOURCE_B),
            "FEE_OBLIGATION_SOURCE_ACTIVITY_CASE_MISMATCH",
            409,
        ),
        (
            "unconfirmed",
            _command(),
            "FEE_OBLIGATION_SOURCE_NOT_CONFIRMED",
            409,
        ),
        (
            "base",
            _command(source_document_id=None),
            "FEE_OBLIGATION_GOV_SOURCE_DOCUMENT_REQUIRED",
            409,
        ),
        (
            "base",
            _command(source_document_id="missing-document"),
            "FEE_OBLIGATION_SOURCE_DOCUMENT_NOT_FOUND",
            409,
        ),
        (
            "cross_document",
            _command(source_document_id=DOCUMENT_B),
            "FEE_OBLIGATION_SOURCE_DOCUMENT_CASE_MISMATCH",
            409,
        ),
    ),
)
def test_case_source_and_document_validation_order_is_exact_and_read_only(
    session_factory: sessionmaker,
    setup: str,
    command: RecognizeFeeObligationCommand,
    expected_code: str,
    status_code: int,
) -> None:
    with session_factory() as transaction:
        if setup != "none":
            _seed_case_source_document(
                transaction,
                confirmation_status=(
                    ConfirmationStatus.NEEDS_REVIEW
                    if setup == "unconfirmed"
                    else ConfirmationStatus.CONFIRMED
                ),
            )
        if setup in {"cross_source", "cross_document"}:
            transaction.add(_case(case_id=CASE_B))
            _seed_source(
                transaction,
                source_id=SOURCE_B,
                case_id=CASE_B,
                confirmation_status=ConfirmationStatus.CONFIRMED,
            )
            if setup == "cross_document":
                transaction.add(Document(id=DOCUMENT_B, case_id=CASE_B, direction="IN"))
            transaction.commit()
        before = _counts(transaction)

        _expect_error(expected_code, status_code, lambda: _recognize(command, transaction))

        assert _counts(transaction) == before
        _assert_no_pending_fee_rows(transaction)


def test_dirty_session_is_rejected_before_any_service_write(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        case = transaction.get(Case, CASE_A)
        assert case is not None
        case.title_cn = "caller dirty"

        _expect_error(
            "FEE_OBLIGATION_TRANSACTION_DIRTY",
            409,
            lambda: _recognize(_command(), transaction),
        )
        assert case in transaction.dirty
        assert _counts(transaction) == (0, 0, 1, 1)


def test_whole_header_supersede_rotates_all_keys_and_links_recognition_activities(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        prior = _recognize(_command(), transaction)
        transaction.commit()
        _add_source(transaction, source_id=SOURCE_B)
        transaction.commit()

        replacement = _recognize(
            _command(
                source_activity_id=SOURCE_B,
                lines=(
                    _line(fee_code="GOV-FILING", payable_amount=Decimal("150.00")),
                    _line(fee_code="GOV-PUBLICATION", fee_name="公布费"),
                ),
                idempotency_key="recognize-fee-correction",
                supersedes_obligation_id=prior.obligation.id,
                supersede_reason="官方更正",
            ),
            transaction,
        )

        stored_prior = transaction.get(FeeObligationModel, prior.obligation.id)
        assert stored_prior.obligation_status == FeeObligationStatus.SUPERSEDED.value
        prior_lines = transaction.scalars(
            select(FeeObligationLineModel).where(
                FeeObligationLineModel.obligation_id == prior.obligation.id
            )
        ).all()
        assert len(prior_lines) == 2
        assert all(line.current_identity_key is None for line in prior_lines)
        stored_replacement = transaction.get(FeeObligationModel, replacement.obligation.id)
        assert stored_replacement.obligation_status == FeeObligationStatus.RECOGNIZED.value
        assert stored_replacement.supersedes_obligation_id == prior.obligation.id
        assert replacement.superseded_obligation_id == prior.obligation.id
        activities = _fee_activities(transaction)
        assert len(activities) == 2
        assert activities[1].supersedes_event_id == activities[0].id == prior.activity_id


def test_forced_late_supersede_failure_rolls_back_only_nested_savepoint(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        prior = _recognize(_command(), transaction)
        transaction.commit()
        _add_source(transaction, source_id=SOURCE_B)
        transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)

        def fail_when_replacement_line_is_flushed(
            session: Session,
            _flush_context: object,
            _instances: object,
        ) -> None:
            if any(
                isinstance(row, FeeObligationLineModel) and row.fee_code == "FORCED-FAIL"
                for row in session.new
            ):
                raise RuntimeError("forced late persistence failure")

        event.listen(transaction, "before_flush", fail_when_replacement_line_is_flushed)
        try:
            with pytest.raises(RuntimeError, match="forced late persistence failure"):
                _recognize(
                    _command(
                        source_activity_id=SOURCE_B,
                        lines=(_line(fee_code="FORCED-FAIL"),),
                        idempotency_key="recognize-fee-forced-failure",
                        supersedes_obligation_id=prior.obligation.id,
                        supersede_reason="测试回滚",
                    ),
                    transaction,
                )
        finally:
            event.remove(transaction, "before_flush", fail_when_replacement_line_is_flushed)
        transaction.expire_all()

        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before
        stored_prior = transaction.get(FeeObligationModel, prior.obligation.id)
        assert stored_prior.obligation_status == FeeObligationStatus.RECOGNIZED.value
        assert all(
            line.current_identity_key is not None
            for line in transaction.scalars(
                select(FeeObligationLineModel).where(
                    FeeObligationLineModel.obligation_id == prior.obligation.id
                )
            )
        )
        assert transaction.scalar(select(func.count()).select_from(Case)) >= 1


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    (
        ("already_superseded", "FEE_OBLIGATION_SUPERSEDED_NOT_CURRENT"),
        ("scope", "FEE_OBLIGATION_SUPERSEDE_SCOPE_MISMATCH"),
        ("missing_prior_activity", "FEE_OBLIGATION_PRIOR_ACTIVITY_INVALID"),
        ("malformed_prior_activity", "FEE_OBLIGATION_PRIOR_ACTIVITY_INVALID"),
    ),
)
def test_supersede_prior_state_scope_and_activity_linkage_fail_closed(
    session_factory: sessionmaker,
    mutation: str,
    expected_code: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        prior = _recognize(_command(), transaction)
        transaction.commit()
        _add_source(transaction, source_id=SOURCE_B)
        transaction.commit()
        stored_prior = transaction.get(FeeObligationModel, prior.obligation.id)
        prior_activity = transaction.get(CaseActivityEvent, prior.activity_id)
        if mutation == "already_superseded":
            stored_prior.obligation_status = FeeObligationStatus.SUPERSEDED.value
        elif mutation == "missing_prior_activity":
            transaction.query(CaseActivityEventEvidence).filter(
                CaseActivityEventEvidence.activity_id == prior.activity_id
            ).delete(synchronize_session=False)
            transaction.delete(prior_activity)
        elif mutation == "malformed_prior_activity":
            prior_activity.payload_json = "{}"
        transaction.commit()
        command = _command(
            source_activity_id=SOURCE_B,
            obligation_type=("DIFFERENT_TYPE" if mutation == "scope" else "PATENT_APPLICATION"),
            lines=(_line(fee_code="REPLACEMENT"),),
            idempotency_key=f"supersede-{mutation}",
            supersedes_obligation_id=prior.obligation.id,
            supersede_reason="更正",
        )
        before = _counts(transaction)

        _expect_error(expected_code, 409, lambda: _recognize(command, transaction))

        assert _counts(transaction) == before


def test_supersede_rejects_missing_cross_case_and_unrelated_current_identity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        prior = _recognize(_command(lines=(_line(fee_code="PRIOR"),)), transaction)
        transaction.commit()
        _add_source(transaction, source_id=SOURCE_B)
        transaction.commit()

        _expect_error(
            "FEE_OBLIGATION_SUPERSEDED_NOT_FOUND",
            409,
            lambda: _recognize(
                _command(
                    source_activity_id=SOURCE_B,
                    lines=(_line(fee_code="NEW"),),
                    idempotency_key="supersede-missing",
                    supersedes_obligation_id="missing-obligation",
                    supersede_reason="更正",
                ),
                transaction,
            ),
        )

        transaction.add(_case(case_id=CASE_B))
        _seed_source(transaction, source_id=SOURCE_C, case_id=CASE_B)
        transaction.commit()
        cross_prior = FeeObligationModel(
            id="cross-case-obligation",
            case_id=CASE_B,
            source_activity_id=SOURCE_C,
            fee_domain=FeeDomain.GOV.value,
            obligation_type="PATENT_APPLICATION",
            obligation_status=FeeObligationStatus.RECOGNIZED.value,
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED.value,
            client_instruction_status=FeeClientInstructionStatus.PENDING.value,
            draft_status=FeeObligationDraftStatus.NOT_CREATED.value,
            payment_status=FeePaymentStatus.UNPAID.value,
            official_evidence_status=FeeOfficialEvidenceStatus.PENDING.value,
        )
        transaction.add(cross_prior)
        transaction.commit()
        _expect_error(
            "FEE_OBLIGATION_SUPERSEDED_CASE_MISMATCH",
            409,
            lambda: _recognize(
                _command(
                    source_activity_id=SOURCE_B,
                    lines=(_line(fee_code="NEW"),),
                    idempotency_key="supersede-cross",
                    supersedes_obligation_id=cross_prior.id,
                    supersede_reason="更正",
                ),
                transaction,
            ),
        )

        _add_source(transaction, source_id="source-fee-recognize-d")
        transaction.commit()
        _recognize(
            _command(
                source_activity_id="source-fee-recognize-d",
                lines=(_line(fee_code="UNRELATED"),),
                idempotency_key="unrelated-current",
            ),
            transaction,
        )
        transaction.commit()
        before = _counts(transaction)
        _expect_error(
            "FEE_OBLIGATION_IDENTITY_CONFLICT",
            409,
            lambda: _recognize(
                _command(
                    source_activity_id="source-fee-recognize-d",
                    lines=(_line(fee_code="UNRELATED"),),
                    idempotency_key="supersede-unrelated-key",
                    supersedes_obligation_id=prior.obligation.id,
                    supersede_reason="更正",
                ),
                transaction,
            ),
        )
        assert _counts(transaction) == before


def _hide_preflight_rows_until_unique_failure(
    transaction: Session,
    action: Callable[[], object],
) -> object:
    original_execute = transaction.execute
    original_flush = transaction.flush
    state = {"hidden": True, "saw_unique": False}

    def execute_with_hidden_competitor(statement, *args, **kwargs):
        predicate = str(statement.whereclause).lower() if isinstance(statement, Select) else ""
        hide_activity = (
            "t_case_activity_event.case_id" in predicate
            and "t_case_activity_event.idempotency_key" in predicate
        )
        hide_identity = "t_fee_obligation_line.current_identity_key" in predicate
        if state["hidden"] and isinstance(statement, Select) and (hide_activity or hide_identity):
            return original_execute(statement.where(false()), *args, **kwargs)
        return original_execute(statement, *args, **kwargs)

    def flush_and_reveal(*args, **kwargs):
        try:
            return original_flush(*args, **kwargs)
        except IntegrityError:
            state["hidden"] = False
            state["saw_unique"] = True
            raise

    with (
        patch.object(transaction, "execute", side_effect=execute_with_hidden_competitor),
        patch.object(transaction, "flush", side_effect=flush_and_reveal),
    ):
        result = action()
    assert state["saw_unique"] is True
    return result


def _hide_only_initial_fee_preflight(
    transaction: Session,
    action: Callable[[], object],
) -> object:
    original_execute = transaction.execute
    hidden = {"activity": False, "identity": False}

    def execute_with_toctou_competitor(statement, *args, **kwargs):
        predicate = str(statement.whereclause).lower() if isinstance(statement, Select) else ""
        is_activity_key = (
            "t_case_activity_event.case_id" in predicate
            and "t_case_activity_event.idempotency_key" in predicate
        )
        is_current_identity = "t_fee_obligation_line.current_identity_key" in predicate
        if isinstance(statement, Select) and is_activity_key and not hidden["activity"]:
            hidden["activity"] = True
            return original_execute(statement.where(false()), *args, **kwargs)
        if isinstance(statement, Select) and is_current_identity and not hidden["identity"]:
            hidden["identity"] = True
            return original_execute(statement.where(false()), *args, **kwargs)
        return original_execute(statement, *args, **kwargs)

    with patch.object(
        transaction,
        "execute",
        side_effect=execute_with_toctou_competitor,
    ):
        result = action()
    assert hidden == {"activity": True, "identity": True}
    return result


@pytest.mark.parametrize("mutation", ("exact", "different_fact"))
def test_same_key_toctou_at_lifecycle_append_recovers_fee_replay_or_conflict(
    session_factory: sessionmaker,
    mutation: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        original_command = _command(lines=(_line(),))
        original = _recognize(original_command, transaction)
        transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)
        supplied = original_command
        if mutation == "different_fact":
            supplied = replace(
                original_command,
                lines=(replace(original_command.lines[0], payable_amount=Decimal("136.00")),),
            )

        if mutation == "exact":
            result = _hide_only_initial_fee_preflight(
                transaction,
                lambda: _recognize(supplied, transaction),
            )
            assert result == replace(original, reused=True)
        else:
            _expect_error(
                "FEE_OBLIGATION_IDEMPOTENCY_CONFLICT",
                409,
                lambda: _hide_only_initial_fee_preflight(
                    transaction,
                    lambda: _recognize(supplied, transaction),
                ),
            )
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before


def test_recognized_activity_unique_race_rereads_and_recovers_exact_replay(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        command = _command(lines=(_line(),))
        original = _recognize(command, transaction)
        transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)

        replay = _hide_preflight_rows_until_unique_failure(
            transaction,
            lambda: _recognize(command, transaction),
        )

        assert replay == replace(original, reused=True)
        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before


@pytest.mark.parametrize(
    ("requested_lines", "expected_code"),
    (
        ((_line(),), "FEE_OBLIGATION_IDENTITY_CONFLICT"),
        (
            (_line(), _line(fee_code="RACE-NEW")),
            "FEE_OBLIGATION_MIXED_IDENTITY_CONFLICT",
        ),
    ),
)
def test_recognized_line_unique_race_rereads_identity_or_mixed_conflict(
    session_factory: sessionmaker,
    requested_lines: tuple[FeeObligationLineInput, ...],
    expected_code: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        _recognize(_command(lines=(_line(),)), transaction)
        transaction.commit()
        before = (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision)

        _expect_error(
            expected_code,
            409,
            lambda: _hide_preflight_rows_until_unique_failure(
                transaction,
                lambda: _recognize(
                    _command(
                        lines=requested_lines,
                        idempotency_key=f"race-{expected_code}",
                    ),
                    transaction,
                ),
            ),
        )

        assert (_counts(transaction), transaction.get(Case, CASE_A).lifecycle_revision) == before
        assert transaction.scalar(select(func.count()).select_from(Case)) >= 1


@pytest.mark.parametrize("path", ("replay", "prior_link"))
def test_non_finite_stored_recognition_payload_fails_closed(
    session_factory: sessionmaker,
    path: str,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        original_command = _command(lines=(_line(),))
        original = _recognize(original_command, transaction)
        transaction.commit()
        activity = transaction.get(CaseActivityEvent, original.activity_id)
        assert activity is not None
        activity.payload_json = activity.payload_json[:-1] + ',"non_finite":NaN}'
        transaction.commit()

        supplied = original_command
        if path == "prior_link":
            _add_source(transaction, source_id=SOURCE_B)
            transaction.commit()
            supplied = _command(
                source_activity_id=SOURCE_B,
                lines=(_line(fee_code="REPLACEMENT"),),
                idempotency_key="supersede-non-finite-prior",
                supersedes_obligation_id=original.obligation.id,
                supersede_reason="更正",
            )

        _expect_error(
            "FEE_OBLIGATION_STORED_STATE_INVALID",
            409,
            lambda: _recognize(supplied, transaction),
        )


def test_not_yet_visible_recognized_unique_race_uses_concurrency_conflict(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        original_flush = transaction.flush
        raised = False

        def raise_recognized_unique_once(*args, **kwargs):
            nonlocal raised
            if not raised and any(
                isinstance(row, (CaseActivityEvent, FeeObligationLineModel))
                and (
                    getattr(row, "activity_type", None) == "FEE_OBLIGATION_RECOGNIZED"
                    or isinstance(row, FeeObligationLineModel)
                )
                for row in transaction.new
            ):
                raised = True
                raise IntegrityError(
                    "INSERT",
                    {},
                    sqlite3.IntegrityError(
                        "UNIQUE constraint failed: t_fee_obligation_line.current_identity_key"
                    ),
                )
            return original_flush(*args, **kwargs)

        with patch.object(transaction, "flush", side_effect=raise_recognized_unique_once):
            _expect_error(
                "FEE_OBLIGATION_CONCURRENCY_CONFLICT",
                409,
                lambda: _recognize(_command(lines=(_line(),)), transaction),
            )

        assert raised is True
        assert _counts(transaction) == (0, 0, 1, 1)
        assert transaction.get(Case, CASE_A).lifecycle_revision == 1
        assert transaction.scalar(select(func.count()).select_from(Case)) >= 1


@pytest.mark.parametrize(
    ("source_status", "source_confirmation", "fee_confirmation"),
    (
        (
            FeeSourceStatus.REVIEW_REQUIRED,
            ConfirmationStatus.CONFIRMED,
            ConfirmationStatus.NEEDS_REVIEW,
        ),
        (
            FeeSourceStatus.LEGACY_UNVERIFIED,
            ConfirmationStatus.LEGACY_UNVERIFIED,
            ConfirmationStatus.LEGACY_UNVERIFIED,
        ),
    ),
)
def test_source_status_maps_confirmation_and_copies_exact_evidence_without_adjacent_access(
    session_factory: sessionmaker,
    source_status: FeeSourceStatus,
    source_confirmation: ConfirmationStatus,
    fee_confirmation: ConfirmationStatus,
) -> None:
    evidence = (
        EvidenceReference(
            case_id=CASE_A,
            evidence_kind="TASK",
            object_type="Task",
            object_id="task-real-fee-source",
            content_hash="sha256:task-real-fee-source",
            captured_at=datetime(2026, 7, 13, 9, 52),
        ),
        EvidenceReference(
            case_id=CASE_A,
            evidence_kind="DOCUMENT",
            object_type="DocumentEvidenceVersion",
            object_id="document-real-fee-source",
            content_hash="sha256:document-real-fee-source",
            captured_at=CAPTURED_AT,
        ),
    )
    with session_factory() as transaction:
        _seed_case_source_document(
            transaction,
            confirmation_status=source_confirmation,
            evidence=evidence,
        )
        statements: list[str] = []

        def capture_sql(
            _conn: object,
            _clauseelement: object,
            _multiparams: object,
            _params: object,
            _execution_options: object,
        ) -> None:
            statements.append(str(_clauseelement).lower())

        event.listen(transaction.bind, "before_execute", capture_sql)
        try:
            result = _recognize(
                _command(source_status=source_status, lines=(_line(),)), transaction
            )
        finally:
            event.remove(transaction.bind, "before_execute", capture_sql)

        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity.confirmation_status == fee_confirmation.value
        copied = transaction.scalars(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == result.activity_id)
            .order_by(
                CaseActivityEventEvidence.evidence_kind,
                CaseActivityEventEvidence.object_type,
                CaseActivityEventEvidence.object_id,
            )
        ).all()
        assert [
            (
                row.evidence_kind,
                row.object_type,
                row.object_id,
                row.content_hash,
                row.captured_at,
            )
            for row in copied
        ] == [
            (
                reference.evidence_kind,
                reference.object_type,
                reference.object_id,
                reference.content_hash,
                reference.captured_at,
            )
            for reference in sorted(
                evidence,
                key=lambda item: (
                    item.evidence_kind,
                    item.object_type,
                    item.object_id,
                ),
            )
        ]
        sql = "\n".join(statements)
        for prohibited_table in (
            "t_fee_rate ",
            "t_fee_rate_book",
            "t_fee_draft",
            "t_fee_item",
            "t_pay_list",
            "t_gov_payment",
            "t_payment ",
        ):
            assert prohibited_table not in sql


def test_estimates_rates_drafts_paylists_and_payments_are_not_created(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_case_source_document(transaction)
        before_tables = {
            table: transaction.scalar(select(func.count()).select_from(table))
            for table in (
                import_module("app.modules.fees.models").FeeRate.__table__,
                import_module("app.modules.fees.models").OfficialRateBook.__table__,
                import_module("app.modules.fees.models").FeeDraft.__table__,
                import_module("app.modules.fees.models").FeeItem.__table__,
                import_module("app.modules.annuity.models").PayList.__table__,
                import_module("app.modules.annuity.models").GovPayment.__table__,
            )
        }

        _recognize(_command(), transaction)

        assert {
            table: transaction.scalar(select(func.count()).select_from(table))
            for table in before_tables
        } == before_tables
