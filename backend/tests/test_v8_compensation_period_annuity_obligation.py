from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import PayList
from app.modules.billing.models import Payment
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service, fee_linking_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeDraft, FeeObligation, FeeObligationLine

CASE_ID = "00000000-0000-0000-0000-000000000001"
WRONG_CASE_ID = "00000000-0000-0000-0000-000000000002"
DOCUMENT_ID = "00000000-0000-0000-0000-000000000100"
ATTACHMENT_ID = "00000000-0000-0000-0000-000000000101"
EVIDENCE_ID = "00000000-0000-0000-0000-000000000102"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
LINEAGE_KEY = "term-compensation-grant-decision"
DECISION_DATE = date(2026, 7, 25)
DUE_DATE = date(2026, 12, 31)
REVIEWED_AT = datetime(2026, 7, 26, 10)
CONTENT_HASH = f"sha256:{'1' * 64}"


def _boundary():
    command_type = getattr(
        fee_linking_service,
        "RecognizeCompensationPeriodAnnuityObligationCommand",
        None,
    )
    recognize = getattr(
        fee_linking_service,
        "recognize_compensation_period_annuity_obligation",
        None,
    )
    assert command_type is not None
    assert recognize is not None
    return command_type, recognize


def _period_facts(*, complete_years: int = 2) -> str:
    return json.dumps(
        {
            "OfficialDueDate": DUE_DATE.isoformat(),
            "OfficialDueDateSource": "IMPORTED_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "TermCompensationGrant": {
                "schema": "FPMS_TERM_COMPENSATION_GRANTED_V1",
                "period_start": "2026-01-15",
                "period_end": "2028-06-14",
                "complete_years": complete_years,
            },
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _expected_snapshot(*, complete_years: int = 2) -> dict[str, object]:
    return {
        "case_id": CASE_ID,
        "complete_years": complete_years,
        "decision_date": DECISION_DATE.isoformat(),
        "due_date": DUE_DATE.isoformat(),
        "due_date_source": "IMPORTED_OFFICIAL_NOTICE",
        "due_date_status": "CONFIRMED",
        "evidence_content_hash": CONTENT_HASH,
        "evidence_version_id": EVIDENCE_ID,
        "period_end": "2028-06-14",
        "period_start": "2026-01-15",
        "schema": "FPMS_TERM_COMPENSATION_GRANTED_V1",
        "source_document_id": DOCUMENT_ID,
    }


def _snapshot_hash(snapshot: dict[str, object]) -> str:
    canonical = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return f"sha256:{sha256(canonical).hexdigest()}"


def _seed_source(
    transaction: Session,
    *,
    extra_data: str | None = None,
) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="TERM-COMPENSATION-GRANTED",
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
    transaction.add(
        Document(
            id=DOCUMENT_ID,
            case_id=CASE_ID,
            direction="IN",
            doc_date=DECISION_DATE,
            extra_data=extra_data if extra_data is not None else _period_facts(),
        )
    )
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=ATTACHMENT_ID,
            document_id=DOCUMENT_ID,
            file_name="term-compensation-grant.pdf",
            file_path="/evidence/term-compensation-grant.pdf",
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
            lineage_key=LINEAGE_KEY,
            role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.PENDING.value,
            reviewer_id=None,
            reviewed_at=None,
            final_submitted_at=None,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|{LINEAGE_KEY}",
        )
    )
    transaction.commit()


def _review_source(transaction: Session) -> str:
    result = evidence_service.review_evidence_version(
        evidence_service.ReviewEvidenceVersionCommand(
            case_id=CASE_ID,
            evidence_version_id=EVIDENCE_ID,
            reviewer_id=REVIEWER_ID,
            decision=evidence_service.EvidenceReviewDecision.APPROVE,
            reviewed_at=REVIEWED_AT,
            idempotency_key="term-compensation-grant-review",
        ),
        transaction,
    )
    transaction.commit()
    return result.activity_id


def _command(source_activity_id: str, *, case_id: str = CASE_ID):
    command_type, _ = _boundary()
    return command_type(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_evidence_version_id=EVIDENCE_ID,
    )


def _fee_counts(transaction: Session) -> tuple[int, ...]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(PayList)) or 0,
        transaction.scalar(select(func.count()).select_from(Payment)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.lane == "FEE")
        )
        or 0,
    )


def test_reviewed_official_decision_forms_and_reuses_one_complete_year_obligation(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction)
        source_activity_id = _review_source(transaction)
        _, recognize = _boundary()

        review_activity = transaction.get(CaseActivityEvent, source_activity_id)
        assert review_activity is not None
        review_payload = json.loads(review_activity.payload_json)
        snapshot = _expected_snapshot()
        assert review_payload["source_snapshot"] == snapshot
        assert review_payload["source_snapshot_hash"] == _snapshot_hash(snapshot)
        review_reference = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == source_activity_id
            )
        )
        assert review_reference is not None
        assert review_reference.content_hash == _snapshot_hash(snapshot)

        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(side_effect=AssertionError("service must not close"))
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", commit)
            patch.setattr(transaction, "rollback", rollback)
            patch.setattr(transaction, "close", close)
            result = recognize(_command(source_activity_id), transaction)
            replay = recognize(_command(source_activity_id), transaction)

        assert result.reused is False
        assert replay == replace(result, reused=True)
        assert commit.call_count == rollback.call_count == close.call_count == 0
        transaction.commit()

        assert _fee_counts(transaction) == (1, 2, 0, 0, 0, 1)
        obligation = transaction.scalar(select(FeeObligation))
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
            obligation.created_by,
        ) == (
            CASE_ID,
            source_activity_id,
            DOCUMENT_ID,
            "GOV",
            "TERM_COMPENSATION_GRANTED",
            DUE_DATE,
            "CNY",
            "VERIFIED",
            REVIEWER_ID,
        )

        lines = tuple(
            transaction.scalars(select(FeeObligationLine).order_by(FeeObligationLine.fee_year_key))
        )
        assert {
            (
                line.fee_code,
                line.fee_name,
                line.fee_year_key,
                line.official_full_amount,
                line.reduction_ratio,
                line.payable_amount,
                line.source_amount,
                line.source_date,
                line.difference_review_state,
            )
            for line in lines
        } == {
            (
                "CN_COMPENSATION_PERIOD_ANNUITY_FEE",
                "专利权补偿期年费",
                year,
                Decimal("8000.00"),
                Decimal("0.0000"),
                Decimal("8000.00"),
                None,
                DECISION_DATE,
                "MATCHED",
            )
            for year in (1, 2)
        }
        assert all(line.current_identity_key is not None for line in lines)

        fee_activities = tuple(
            transaction.scalars(select(CaseActivityEvent).where(CaseActivityEvent.lane == "FEE"))
        )
        assert len(fee_activities) == 1
        assert fee_activities[0].activity_type == "FEE_OBLIGATION_RECOGNIZED"
        assert fee_activities[0].source_activity_id == source_activity_id
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    ("extra_data", "field"),
    (
        (None, "period"),
        (
            json.dumps(
                {
                    "TermCompensationGrant": {
                        "schema": "FPMS_TERM_COMPENSATION_GRANTED_V1",
                        "period_end": "2028-06-14",
                        "complete_years": 2,
                    }
                }
            ),
            "period",
        ),
        (
            json.dumps(
                {
                    "TermCompensationGrant": {
                        "schema": "FPMS_TERM_COMPENSATION_GRANTED_V1",
                        "period_start": "2026-01-15",
                        "period_end": "2028-06-14",
                    }
                }
            ),
            "complete_years",
        ),
    ),
)
def test_missing_period_or_complete_year_facts_is_409_with_no_fee_write(
    session_factory: sessionmaker[Session],
    extra_data: str | None,
    field: str,
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction, extra_data=extra_data or "{}")
        with pytest.raises(BusinessError) as captured:
            _review_source(transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": field}
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    ("carrier", "value"),
    (
        ("evidence", ("current_identity_key", None)),
        ("evidence", ("state", EvidenceVersionState.DRAFT.value)),
        ("evidence", ("role", EvidenceRole.RAW_ATTACHMENT.value)),
        ("evidence", ("reviewer_id", CREATOR_ID)),
        ("document", ("direction", "OUT")),
    ),
)
def test_noncurrent_nonfinal_nonindependent_or_nonofficial_source_is_409_no_write(
    session_factory: sessionmaker[Session],
    carrier: str,
    value: tuple[str, object],
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction)
        source_activity_id = _review_source(transaction)
        target = (
            transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
            if carrier == "evidence"
            else transaction.get(Document, DOCUMENT_ID)
        )
        assert target is not None
        setattr(target, value[0], value[1])
        transaction.commit()

        _, recognize = _boundary()
        before = _fee_counts(transaction)
        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id), transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT"
        assert _fee_counts(transaction) == before == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()


def test_wrong_case_is_409_with_no_fee_write(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction)
        source_activity_id = _review_source(transaction)
        _, recognize = _boundary()

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, case_id=WRONG_CASE_ID), transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT"
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    "mutate",
    (
        "decision_date",
        "period",
        "complete_years",
        "due_date",
        "noncanonical",
    ),
)
def test_post_review_source_mutation_is_409_with_no_fee_write(
    session_factory: sessionmaker[Session],
    mutate: str,
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction)
        source_activity_id = _review_source(transaction)
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        fields = json.loads(document.extra_data)
        if mutate == "decision_date":
            document.doc_date = date(2026, 7, 26)
        elif mutate == "period":
            fields["TermCompensationGrant"]["period_end"] = "2028-07-14"
            document.extra_data = json.dumps(
                fields,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        elif mutate == "complete_years":
            fields["TermCompensationGrant"]["complete_years"] = 3
            document.extra_data = json.dumps(
                fields,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        elif mutate == "due_date":
            fields["OfficialDueDate"] = "2027-01-01"
            document.extra_data = json.dumps(
                fields,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        else:
            document.extra_data = json.dumps(fields, ensure_ascii=False, indent=2)
        transaction.commit()

        _, recognize = _boundary()
        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id), transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT"
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    "deadline_fields",
    (
        {},
        {
            "OfficialDueDate": "2026-12-31",
            "OfficialDueDateSource": "IMPORTED_OFFICIAL_NOTICE",
        },
        {
            "OfficialDueDate": "2026-12-31",
            "OfficialDueDateSource": "IMPORTED_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "NEEDS_CONFIRMATION",
        },
    ),
)
def test_missing_or_inconsistent_evidence_deadline_is_409_with_no_write(
    session_factory: sessionmaker[Session],
    deadline_fields: dict[str, str],
) -> None:
    transaction = session_factory()
    try:
        fields = json.loads(_period_facts())
        for key in (
            "OfficialDueDate",
            "OfficialDueDateSource",
            "OfficialDueDateStatus",
        ):
            fields.pop(key)
        fields.update(deadline_fields)
        extra_data = json.dumps(
            fields,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        _seed_source(transaction, extra_data=extra_data)

        with pytest.raises(BusinessError) as captured:
            _review_source(transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "COMPENSATION_PERIOD_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "deadline"}
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()


def test_partial_only_period_creates_no_zero_value_obligation_or_line(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        _seed_source(transaction, extra_data=_period_facts(complete_years=0))
        source_activity_id = _review_source(transaction)
        _, recognize = _boundary()

        result = recognize(_command(source_activity_id), transaction)

        assert result is None
        assert _fee_counts(transaction) == (0, 0, 0, 0, 0, 0)
    finally:
        transaction.rollback()
        transaction.close()
