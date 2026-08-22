from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime
from decimal import Decimal
from typing import get_type_hints
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import PayList
from app.modules.auth.models import T_User
from app.modules.billing.models import Payment
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_workflow_service as evidence_workflow
from app.modules.documents import fee_linking_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.cnipa_layout_rate_candidate import materialize_cnipa_layout_246
from app.modules.fees.models import (
    FeeDraft,
    FeeObligation,
    FeeObligationLine,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeSourceStatus,
    RecognizeFeeObligationResult,
)
from app.modules.fees.official_rate_book import (
    ActivateOfficialRateBookCommand,
    activate_official_rate_book,
)

CASE_ID = "00000000-0000-0000-0000-000000000001"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000100"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000101"
EVIDENCE_ID = "00000000-0000-0000-0000-000000000002"
ACTOR_ID = "00000000-0000-0000-0000-000000000700"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
CONTENT_HASH = f"sha256:{'a' * 64}"
SUBMITTED_AT = datetime(2026, 7, 24, 9, 30)
REVIEWED_AT = datetime(2026, 7, 24, 9)
LINEAGE_KEY = "ic-layout-registration-submission"


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _boundary():
    command_type = getattr(
        fee_linking_service,
        "RecognizeIcLayoutRegistrationFiledObligationCommand",
        None,
    )
    recognize = getattr(
        fee_linking_service,
        "recognize_ic_layout_registration_filed_obligation",
        None,
    )
    if command_type is None or recognize is None:
        pytest.skip("IC-layout registration-filed recognition seam is not implemented")
    return command_type, recognize


def _command(
    *,
    case_id: str = CASE_ID,
    source_activity_id: str,
    source_evidence_version_id: str = EVIDENCE_ID,
):
    command_type, _ = _boundary()
    return command_type(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_evidence_version_id=source_evidence_version_id,
    )


def _activate_layout_rate(transaction: Session) -> None:
    created = materialize_cnipa_layout_246(transaction)
    admin = transaction.scalar(select(T_User).where(T_User.username == "admin"))
    assert admin is not None
    activate_official_rate_book(
        ActivateOfficialRateBookCommand(
            rate_book_id=created.rate_book_id,
            approved_by=admin.id,
            approved_at=datetime(2026, 7, 24, 8),
            activated_by=admin.id,
            activated_at=datetime(2026, 7, 24, 8, 1),
            expected_current_rate_book_id=None,
        ),
        transaction,
    )


def _seed_evidence(
    transaction: Session,
    *,
    document_id: str = DOCUMENT_ID,
    attachment_id: str = ATTACHMENT_ID,
    evidence_id: str = EVIDENCE_ID,
    lineage_key: str = LINEAGE_KEY,
) -> None:
    transaction.add(Document(id=document_id, case_id=CASE_ID, direction="OUT"))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"{lineage_key}.xml",
            file_path=f"/evidence/{lineage_key}.xml",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=CASE_ID,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=lineage_key,
            role=EvidenceRole.SUBMITTED_XML.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|{lineage_key}",
        )
    )


def _seed_case_and_rate(transaction: Session) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="IC-LAYOUT-REGISTRATION-FILED",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            status="ACCEPTED",
            business_stage="PROSECUTION_MANAGEMENT",
            official_procedure_stage="ACCEPTED",
            legal_status="APPLICATION_PENDING",
            lifecycle_revision=0,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.flush()
    _seed_evidence(transaction)
    _activate_layout_rate(transaction)
    transaction.commit()


def _finalize(
    transaction: Session,
    *,
    evidence_id: str = EVIDENCE_ID,
    idempotency_key: str = "ic-layout-submission-1",
) -> str:
    result = evidence_workflow.finalize_external_submission(
        evidence_workflow.FinalizeExternalSubmissionCommand(
            case_id=CASE_ID,
            evidence_version_id=evidence_id,
            actor_id=ACTOR_ID,
            submitted_at=SUBMITTED_AT,
            idempotency_key=idempotency_key,
        ),
        transaction,
    )
    transaction.commit()
    return result.activity_id


def _seed_finalized_source(transaction: Session) -> str:
    _seed_case_and_rate(transaction)
    return _finalize(transaction)


def _counts(transaction: Session) -> tuple[int, ...]:
    return (
        transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) or 0,
        transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(PayList)) or 0,
        transaction.scalar(select(func.count()).select_from(Payment)) or 0,
    )


def _expect_conflict(callable_: object) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        callable_()  # type: ignore[operator]
    assert captured.value.status_code == 409
    return captured.value


def test_public_seam_is_exact_frozen_slotted_keyword_only_and_typed() -> None:
    expected = (
        "RecognizeIcLayoutRegistrationFiledObligationCommand",
        "recognize_ic_layout_registration_filed_obligation",
    )
    missing = tuple(name for name in expected if not hasattr(fee_linking_service, name))
    assert missing == ()

    command_type, recognize = _boundary()
    assert is_dataclass(command_type)
    assert command_type.__dataclass_params__.frozen is True
    assert "__slots__" in command_type.__dict__
    type_hints = get_type_hints(command_type)
    assert tuple((field.name, type_hints[field.name]) for field in fields(command_type)) == (
        ("case_id", str),
        ("source_activity_id", str),
        ("source_evidence_version_id", str),
    )
    assert all(field.kw_only for field in fields(command_type))
    assert tuple(inspect.signature(recognize).parameters) == ("command", "transaction")
    assert get_type_hints(recognize) == {
        "command": command_type,
        "transaction": Session,
        "return": RecognizeFeeObligationResult,
    }

    command = command_type(
        case_id=CASE_ID,
        source_activity_id=_id(10),
        source_evidence_version_id=EVIDENCE_ID,
    )
    with pytest.raises(FrozenInstanceError):
        command.case_id = "changed"  # type: ignore[misc]


def test_explicit_recognition_writes_exact_obligation_and_only_owned_fee_activity(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, recognize = _boundary()
    transaction = session_factory()
    try:
        source_activity_id = _seed_finalized_source(transaction)
        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(side_effect=AssertionError("service must not close"))
        original_begin_nested = transaction.begin_nested
        begin_nested = Mock(wraps=original_begin_nested)
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", commit)
            patch.setattr(transaction, "rollback", rollback)
            patch.setattr(transaction, "close", close)
            patch.setattr(transaction, "begin_nested", begin_nested)

            result = recognize(
                _command(source_activity_id=source_activity_id),
                transaction,
            )

        assert isinstance(result, RecognizeFeeObligationResult)
        assert result.reused is False
        assert result.idempotency_key == "ic-layout-registration-filed"
        assert result.superseded_obligation_id is None
        assert commit.call_count == rollback.call_count == close.call_count == 0
        assert begin_nested.call_count == 1

        obligation = transaction.get(FeeObligation, result.obligation.id)
        assert obligation is not None
        assert (
            obligation.case_id,
            obligation.source_activity_id,
            obligation.source_document_id,
            obligation.fee_domain,
            obligation.obligation_type,
            obligation.due_date,
            obligation.currency,
            obligation.source_status,
            obligation.supersedes_obligation_id,
            obligation.supersede_reason,
            obligation.created_by,
        ) == (
            CASE_ID,
            source_activity_id,
            DOCUMENT_ID,
            FeeDomain.GOV.value,
            "IC_LAYOUT_REGISTRATION_FILED",
            None,
            "CNY",
            FeeSourceStatus.VERIFIED.value,
            None,
            None,
            ACTOR_ID,
        )
        line = transaction.scalars(select(FeeObligationLine)).one()
        assert (
            line.obligation_id,
            line.case_id,
            line.source_activity_id,
            line.fee_code,
            line.fee_name,
            line.fee_year_key,
            line.official_full_amount,
            line.reduction_ratio,
            line.payable_amount,
            line.source_amount,
            line.source_date,
            line.difference_review_state,
        ) == (
            obligation.id,
            CASE_ID,
            source_activity_id,
            "IC_LAYOUT_REGISTRATION_FEE",
            "布图设计登记费",
            0,
            Decimal("1000.00"),
            Decimal("0.0000"),
            Decimal("1000.00"),
            None,
            SUBMITTED_AT.date(),
            FeeDifferenceReviewState.MATCHED.value,
        )
        activities = transaction.scalars(
            select(CaseActivityEvent).order_by(CaseActivityEvent.sequence)
        ).all()
        assert [activity.activity_type for activity in activities] == [
            "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            "FEE_OBLIGATION_RECOGNIZED",
        ]
        assert activities[1].source_activity_id == source_activity_id
        assert activities[1].actor_id == ACTOR_ID
        assert activities[1].supersedes_event_id is None
        assert _counts(transaction) == (2, 2, 1, 1, 0, 0, 0)
    finally:
        transaction.close()


def test_exact_replay_reuses_same_obligation_and_activity_without_extra_write(
    session_factory: sessionmaker[Session],
) -> None:
    _, recognize = _boundary()
    with session_factory() as transaction:
        source_activity_id = _seed_finalized_source(transaction)
        command = _command(source_activity_id=source_activity_id)
        created = recognize(command, transaction)
        transaction.commit()
        before = _counts(transaction)

        replay = recognize(command, transaction)

        assert replay == replace(created, reused=True)
        assert _counts(transaction) == before
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


@pytest.mark.parametrize(
    ("target", "field", "value"),
    (
        ("activity", "activity_type", "FILING_EXTERNAL_SUBMISSION_RECORDED"),
        ("activity", "lane", "LIFECYCLE"),
        ("activity", "confirmation_status", "NEEDS_REVIEW"),
        ("activity", "source_activity_id", "__SELF__"),
        ("activity", "supersedes_event_id", _id(51)),
        ("activity", "new_legal_status", "PATENT_IN_FORCE"),
        (
            "activity",
            "payload_json",
            json.dumps(
                {
                    "evidence_version_id": EVIDENCE_ID,
                    "lineage_key": LINEAGE_KEY,
                    "role": EvidenceRole.SUBMITTED_XML.value,
                    "submitted_at": SUBMITTED_AT.isoformat(),
                    "unexpected": True,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        ),
        ("activity", "occurred_at", datetime(2026, 7, 24, 9, 31)),
        ("activity", "reviewer_id", _id(901)),
        ("evidence", "role", EvidenceRole.OFFICIAL_FINAL_PDF.value),
        ("evidence", "state", EvidenceVersionState.DRAFT.value),
        ("evidence", "review_state", EvidenceReviewState.PENDING.value),
        ("evidence", "current_identity_key", None),
        ("evidence", "creator_id", REVIEWER_ID),
        ("evidence", "content_hash", f"sha256:{'b' * 64}"),
        ("evidence", "final_submitted_at", datetime(2026, 7, 24, 9, 31)),
        ("reference", "object_type", "Document"),
        ("reference", "content_hash", f"sha256:{'b' * 64}"),
        ("reference", "captured_at", datetime(2026, 7, 24, 9, 31)),
    ),
)
def test_corrupt_source_carrier_is_409_without_write(
    session_factory: sessionmaker[Session],
    target: str,
    field: str,
    value: object,
) -> None:
    _, recognize = _boundary()
    with session_factory() as transaction:
        source_activity_id = _seed_finalized_source(transaction)
        activity = transaction.get(CaseActivityEvent, source_activity_id)
        evidence = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
        reference = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == source_activity_id
            )
        ).one()
        assert activity is not None
        assert evidence is not None
        row = {"activity": activity, "evidence": evidence, "reference": reference}[target]
        setattr(row, field, source_activity_id if value == "__SELF__" else value)
        transaction.commit()
        before = _counts(transaction)

        _expect_conflict(
            lambda: recognize(
                _command(source_activity_id=source_activity_id),
                transaction,
            )
        )

        assert _counts(transaction) == before
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_rejects_wrong_or_dirty_transaction_before_source_reads(
    session_factory: sessionmaker[Session],
) -> None:
    _, recognize = _boundary()
    command = _command(source_activity_id=_id(10))
    with pytest.raises(BusinessError) as wrong:
        recognize(command, object())
    assert wrong.value.status_code == 400

    with session_factory() as transaction:
        source_activity_id = _seed_finalized_source(transaction)
        pending = Case(id=_id(99), case_no="UNFLUSHED")
        transaction.add(pending)
        before = _counts(transaction)

        _expect_conflict(
            lambda: recognize(
                _command(source_activity_id=source_activity_id),
                transaction,
            )
        )

        assert _counts(transaction) == before
        assert pending in transaction.new


def test_extra_source_reference_or_document_case_drift_is_409_without_write(
    session_factory: sessionmaker[Session],
) -> None:
    _, recognize = _boundary()
    with session_factory() as transaction:
        source_activity_id = _seed_finalized_source(transaction)
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(80),
                case_id=CASE_ID,
                activity_id=source_activity_id,
                evidence_kind="UNEXPECTED",
                object_type="DocumentEvidenceVersion",
                object_id=EVIDENCE_ID,
                content_hash=CONTENT_HASH,
                captured_at=SUBMITTED_AT,
            )
        )
        transaction.commit()
        before = _counts(transaction)

        _expect_conflict(
            lambda: recognize(
                _command(source_activity_id=source_activity_id),
                transaction,
            )
        )
        assert _counts(transaction) == before

    with session_factory() as transaction:
        extra = transaction.get(CaseActivityEventEvidence, _id(80))
        assert extra is not None
        transaction.delete(extra)
        transaction.add(Case(id=_id(81), case_no="OTHER-CASE"))
        transaction.flush()
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        document.case_id = _id(81)
        transaction.commit()
        before = _counts(transaction)

        _expect_conflict(
            lambda: recognize(
                _command(source_activity_id=source_activity_id),
                transaction,
            )
        )
        assert _counts(transaction) == before


def test_distinct_second_finalized_source_is_409_with_zero_writes(
    session_factory: sessionmaker[Session],
) -> None:
    _, recognize = _boundary()
    with session_factory() as transaction:
        first_activity_id = _seed_finalized_source(transaction)
        recognize(_command(source_activity_id=first_activity_id), transaction)
        transaction.commit()

        _seed_evidence(
            transaction,
            document_id=_id(110),
            attachment_id=_id(111),
            evidence_id=_id(12),
            lineage_key="ic-layout-registration-submission-second",
        )
        transaction.commit()
        second_activity_id = _finalize(
            transaction,
            evidence_id=_id(12),
            idempotency_key="ic-layout-submission-2",
        )
        before = _counts(transaction)

        _expect_conflict(
            lambda: recognize(
                _command(
                    source_activity_id=second_activity_id,
                    source_evidence_version_id=_id(12),
                ),
                transaction,
            )
        )

        assert _counts(transaction) == before
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_generic_external_finalization_never_auto_invokes_fee_recognition(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _boundary()
    with session_factory() as transaction:
        _seed_case_and_rate(transaction)
        recognize = Mock(side_effect=AssertionError("recognition must be explicit"))
        monkeypatch.setattr(
            fee_linking_service,
            "recognize_ic_layout_registration_filed_obligation",
            recognize,
        )

        _finalize(transaction)

        assert recognize.call_count == 0
        assert transaction.scalar(select(func.count()).select_from(FeeObligation)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeObligationLine)) == 0
