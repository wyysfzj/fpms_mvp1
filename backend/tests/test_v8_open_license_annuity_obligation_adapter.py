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
from sqlalchemy.orm.attributes import set_committed_value

from app.core.errors import BusinessError
from app.modules.annuity.models import AnnuityTask, FutureAnnuityReductionLineage
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import evidence_service, fee_linking_service
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.cnipa_annuity_rate_candidate import CNIPA_ANNUITY_SOURCE_SNAPSHOT
from app.modules.fees.models import (
    FeeObligation,
    FeeObligationLine,
    FeeRate,
    FeeReductionApproval,
    OfficialRateBook,
)
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
)
from app.modules.fees.obligation_service import recognize_obligation
from app.modules.masterdata.clients.models import Client

CASE_ID = "00000000-0000-0000-0000-000000000001"
WRONG_CASE_ID = "00000000-0000-0000-0000-000000000002"
CLIENT_ID = "00000000-0000-0000-0000-000000000003"
ANNUITY_DOCUMENT_ID = "00000000-0000-0000-0000-000000000100"
ANNUITY_ACTIVITY_ID = "00000000-0000-0000-0000-000000000101"
ANNUITY_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000102"
ANNUITY_EVIDENCE_ID = "00000000-0000-0000-0000-000000000103"
ANNUITY_RATE_BOOK_ID = "00000000-0000-0000-0000-000000000104"
ANNUITY_RATE_ID = "00000000-0000-0000-0000-000000000105"
ANNUITY_REDUCTION_APPROVAL_ID = "00000000-0000-0000-0000-000000000107"
ANNUITY_APPROVAL_EVIDENCE_ID = "00000000-0000-0000-0000-000000000108"
ANNUITY_APPROVAL_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000109"
OPEN_DOCUMENT_ID = "00000000-0000-0000-0000-000000000200"
OPEN_ATTACHMENT_ID = "00000000-0000-0000-0000-000000000201"
OPEN_EVIDENCE_ID = "00000000-0000-0000-0000-000000000202"
CREATOR_ID = "00000000-0000-0000-0000-000000000800"
REVIEWER_ID = "00000000-0000-0000-0000-000000000900"
ANNUITY_EVIDENCE_REVIEWER_ID = "00000000-0000-0000-0000-000000000901"
LINEAGE_KEY = "open-license-implementation-period"
CONTENT_HASH = f"sha256:{'2' * 64}"
ANNUITY_CONTENT_HASH = f"sha256:{'1' * 64}"
REVIEWED_AT = datetime(2026, 7, 26, 10)
DUE_DATE = date(2027, 8, 1)
ANNUITY_CALC_PARAMS = {
    "CN_ANNUITY_FEE_DES": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10},'
        '{"amount":"3000.00","from":11,"to":15}]}'
    ),
    "CN_ANNUITY_FEE_INV": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"900.00","from":1,"to":3},'
        '{"amount":"1200.00","from":4,"to":6},'
        '{"amount":"2000.00","from":7,"to":9},'
        '{"amount":"4000.00","from":10,"to":12},'
        '{"amount":"6000.00","from":13,"to":15},'
        '{"amount":"8000.00","from":16,"to":20}]}'
    ),
    "CN_ANNUITY_FEE_UM": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10}]}'
    ),
}
ALTERED_ANNUITY_CALC_PARAMS = {
    "CN_ANNUITY_FEE_DES": ANNUITY_CALC_PARAMS["CN_ANNUITY_FEE_DES"].replace(
        '"amount":"900.00","from":4',
        '"amount":"1000.00","from":4',
    ),
    "CN_ANNUITY_FEE_INV": ANNUITY_CALC_PARAMS["CN_ANNUITY_FEE_INV"].replace(
        '"amount":"1200.00","from":4',
        '"amount":"1300.00","from":4',
    ),
    "CN_ANNUITY_FEE_UM": ANNUITY_CALC_PARAMS["CN_ANNUITY_FEE_UM"].replace(
        '"amount":"900.00","from":4',
        '"amount":"1000.00","from":4',
    ),
}


def _seed_reduction_approval(
    transaction: Session,
    *,
    ratio: Decimal,
    fee_code: str,
    fee_year_key: int,
) -> None:
    fee_scope_snapshot = (
        f'{{"fee_codes":["{fee_code}"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}}'
    )
    eligibility_snapshot = '{"schema":"TEST_ELIGIBILITY_V1"}'
    transaction.add(
        FeeReductionApproval(
            id=ANNUITY_REDUCTION_APPROVAL_ID,
            scope_type="CASE",
            case_id=CASE_ID,
            applicant_set_key=None,
            reduction_ratio=ratio,
            fee_scope_snapshot=fee_scope_snapshot,
            fee_scope_hash=sha256(fee_scope_snapshot.encode()).hexdigest(),
            fee_year_from=fee_year_key,
            fee_year_to=fee_year_key,
            effective_from=date(2026, 1, 1),
            effective_to=None,
            source_evidence_version_id=ANNUITY_APPROVAL_EVIDENCE_ID,
            confirmation_status="CONFIRMED",
            confirmed_at=datetime(2026, 8, 2, 9),
            confirmed_by=CREATOR_ID,
            eligibility_snapshot=eligibility_snapshot,
            eligibility_snapshot_hash=sha256(eligibility_snapshot.encode()).hexdigest(),
            approval_identity_key=f"approval:{ANNUITY_REDUCTION_APPROVAL_ID}",
        )
    )


def _boundary():
    command_type = getattr(
        fee_linking_service,
        "RecognizeOpenLicenseAnnuityObligationCommand",
        None,
    )
    recognize = getattr(
        fee_linking_service,
        "recognize_open_license_annuity_obligation",
        None,
    )
    assert command_type is not None
    assert recognize is not None
    return command_type, recognize


def _period_facts(
    *,
    period_start: date = date(2027, 1, 1),
    period_end: date = date(2027, 12, 31),
) -> str:
    return json.dumps(
        {
            "OpenLicenseImplementationPeriod": {
                "schema": "FPMS_OPEN_LICENSE_IMPLEMENTATION_PERIOD_V1",
                "period_end": period_end.isoformat(),
                "period_start": period_start.isoformat(),
            }
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _seed(
    transaction: Session,
    *,
    existing_reduction_ratio: Decimal = Decimal("0.0000"),
    due_date: date = DUE_DATE,
    period_facts: str | None = None,
    accepted_future_annuity_lineage: bool = True,
    include_reduction_lineage: bool = True,
    lineage_provenance: str = "EXPLICIT_ENTRY",
    lineage_has_approval: bool = False,
    patent_category: str | None = "INV",
    fee_code: str = "CN_ANNUITY_FEE_INV",
    fee_year_key: int = 4,
    full_amount: Decimal = Decimal("1200.00"),
    rate_calc_params: str | None = None,
) -> str:
    admin = transaction.scalar(select(T_User).where(T_User.username == "admin"))
    assert admin is not None
    transaction.add(
        Client(
            id=CLIENT_ID,
            client_code="OPEN-LICENSE-ANNUITY",
            name_cn="开放许可年费测试客户",
        )
    )
    transaction.flush()
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="OPEN-LICENSE-ANNUITY",
            client_id=CLIENT_ID,
            case_type="NORMAL",
            patent_category=patent_category,
            flow_dir="CN_DOMESTIC",
            status="GRANTED",
            business_stage="POST_GRANT_MAINTENANCE",
            official_procedure_stage="GRANT_ANNOUNCED",
            legal_status="PATENT_IN_FORCE",
            lifecycle_revision=1,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.add(
        Case(
            id=WRONG_CASE_ID,
            case_no="OPEN-LICENSE-ANNUITY-WRONG",
            client_id=CLIENT_ID,
            case_type="NORMAL",
            patent_category=patent_category,
            flow_dir="CN_DOMESTIC",
            status="GRANTED",
            business_stage="POST_GRANT_MAINTENANCE",
            official_procedure_stage="GRANT_ANNOUNCED",
            legal_status="PATENT_IN_FORCE",
            lifecycle_revision=1,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.add_all(
        [
            Document(
                id=ANNUITY_DOCUMENT_ID,
                case_id=CASE_ID,
                direction="IN",
                doc_date=date(2026, 8, 1),
            ),
            Document(
                id=OPEN_DOCUMENT_ID,
                case_id=CASE_ID,
                direction="IN",
                doc_date=date(2026, 12, 20),
                extra_data=period_facts if period_facts is not None else _period_facts(),
            ),
        ]
    )
    transaction.flush()
    transaction.add(
        CaseActivityEvent(
            id=ANNUITY_ACTIVITY_ID,
            case_id=CASE_ID,
            sequence=1,
            lane="LIFECYCLE",
            activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
            occurred_at=datetime(2026, 8, 1, 9),
            effective_at=datetime(2026, 8, 1, 9),
            confirmation_status="CONFIRMED",
            old_business_stage="POST_GRANT_MAINTENANCE",
            new_business_stage="POST_GRANT_MAINTENANCE",
            old_official_procedure_stage="GRANT_ANNOUNCED",
            new_official_procedure_stage="GRANT_ANNOUNCED",
            old_legal_status="PATENT_IN_FORCE",
            new_legal_status="PATENT_IN_FORCE",
            actor_id=CREATOR_ID,
            reviewer_id=REVIEWER_ID,
            idempotency_key="ordinary-annuity-source",
            payload_json="{}",
        )
    )
    transaction.add_all(
        [
            DocAttachment(
                id=ANNUITY_ATTACHMENT_ID,
                document_id=ANNUITY_DOCUMENT_ID,
                file_name="grant-announcement.pdf",
                file_path="/evidence/grant-announcement.pdf",
                content_hash=ANNUITY_CONTENT_HASH,
            ),
            DocAttachment(
                id=OPEN_ATTACHMENT_ID,
                document_id=OPEN_DOCUMENT_ID,
                file_name="open-license-period.pdf",
                file_path="/evidence/open-license-period.pdf",
                content_hash=CONTENT_HASH,
            ),
            DocAttachment(
                id=ANNUITY_APPROVAL_ATTACHMENT_ID,
                document_id=ANNUITY_DOCUMENT_ID,
                file_name="fee-reduction-approval.pdf",
                file_path="/evidence/fee-reduction-approval.pdf",
                content_hash=ANNUITY_CONTENT_HASH,
            ),
        ]
    )
    transaction.flush()
    transaction.add_all(
        [
            DocumentEvidenceVersion(
                id=ANNUITY_EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=ANNUITY_DOCUMENT_ID,
                attachment_id=ANNUITY_ATTACHMENT_ID,
                lineage_key="grant-announcement",
                role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id=CREATOR_ID,
                review_state=EvidenceReviewState.APPROVED.value,
                reviewer_id=ANNUITY_EVIDENCE_REVIEWER_ID,
                reviewed_at=datetime(2026, 7, 31, 16),
                content_hash=ANNUITY_CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|grant-announcement",
            ),
            DocumentEvidenceVersion(
                id=ANNUITY_APPROVAL_EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=ANNUITY_DOCUMENT_ID,
                attachment_id=ANNUITY_APPROVAL_ATTACHMENT_ID,
                lineage_key="fee-reduction-approval",
                role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id=CREATOR_ID,
                review_state=EvidenceReviewState.APPROVED.value,
                reviewer_id=ANNUITY_EVIDENCE_REVIEWER_ID,
                reviewed_at=datetime(2026, 8, 2, 8),
                content_hash=ANNUITY_CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|fee-reduction-approval",
            ),
            DocumentEvidenceVersion(
                id=OPEN_EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=OPEN_DOCUMENT_ID,
                attachment_id=OPEN_ATTACHMENT_ID,
                lineage_key=LINEAGE_KEY,
                role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id=CREATOR_ID,
                review_state=EvidenceReviewState.PENDING.value,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|{LINEAGE_KEY}",
            ),
        ]
    )
    transaction.flush()
    transaction.add(
        CaseActivityEventEvidence(
            id="00000000-0000-0000-0000-000000000106",
            case_id=CASE_ID,
            activity_id=ANNUITY_ACTIVITY_ID,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=ANNUITY_EVIDENCE_ID,
            content_hash=ANNUITY_CONTENT_HASH,
            captured_at=datetime(2026, 8, 1, 9),
        )
    )
    transaction.add(
        OfficialRateBook(
            id=ANNUITY_RATE_BOOK_ID,
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
            approved_at=datetime(2026, 7, 19, 10),
            effective_from=date(2026, 3, 30),
            activation_status="ACTIVE",
            activated_by=admin.id,
            activated_at=datetime(2026, 7, 19, 10, 5),
            current_identity_key="CNIPA|CNIPA_PATENT_ANNUITY_20260330",
        )
    )
    transaction.flush()
    transaction.add(
        FeeRate(
            id=ANNUITY_RATE_ID,
            fee_code="CN_ANNUITY_FEE_INV",
            fee_name=None,
            fee_type="GOV",
            currency="CNY",
            enabled=True,
            calc_mode="TIER",
            calc_params=(
                ANNUITY_CALC_PARAMS[fee_code] if rate_calc_params is None else rate_calc_params
            ),
            allow_reduction=True,
            effective_from=date(2026, 3, 30),
            source_doc="专利和集成电路布图设计缴费服务指南",
            source_url=("https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"),
            source_version="2026-03-30",
            source_status="PENDING_CONFIRMATION",
            official_rate_book_id=ANNUITY_RATE_BOOK_ID,
        )
    )
    transaction.commit()

    existing = recognize_obligation(
        RecognizeFeeObligationCommand(
            case_id=CASE_ID,
            source_activity_id=ANNUITY_ACTIVITY_ID,
            source_document_id=ANNUITY_DOCUMENT_ID,
            fee_domain=FeeDomain.GOV,
            obligation_type="FUTURE_ANNUITY",
            due_date=due_date,
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED,
            lines=(
                FeeObligationLineInput(
                    fee_code=fee_code,
                    fee_name="年费",
                    fee_year_key=fee_year_key,
                    official_full_amount=full_amount,
                    reduction_ratio=existing_reduction_ratio,
                    payable_amount=(
                        full_amount * (Decimal("1") - existing_reduction_ratio)
                    ).quantize(Decimal("0.01")),
                    source_amount=None,
                    source_date=due_date,
                    difference_review_state=FeeDifferenceReviewState.MATCHED,
                ),
            ),
            actor_id=CREATOR_ID,
            idempotency_key="ordinary-annuity-recognized",
            supersedes_obligation_id=None,
            supersede_reason=None,
        ),
        transaction,
    )
    if accepted_future_annuity_lineage:
        existing_line = existing.obligation.lines[0]
        if lineage_has_approval:
            _seed_reduction_approval(
                transaction,
                ratio=existing_reduction_ratio,
                fee_code=fee_code,
                fee_year_key=fee_year_key,
            )
        task = AnnuityTask(
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            year_no=fee_year_key,
            due_date=due_date,
            status="OPEN",
            source_activity_id=ANNUITY_ACTIVITY_ID,
            source_document_id=ANNUITY_DOCUMENT_ID,
            source_evidence_version_id=ANNUITY_EVIDENCE_ID,
            source_evidence_content_hash=ANNUITY_CONTENT_HASH,
            fee_obligation_id=existing.obligation.id,
            grant_fee_year_key=fee_year_key,
        )
        transaction.add(task)
        transaction.flush()
        if include_reduction_lineage:
            transaction.add(
                FutureAnnuityReductionLineage(
                    annuity_task_id=task.id,
                    fee_obligation_line_id=existing_line.id,
                    reduction_input_provenance=lineage_provenance,
                    reduction_approval_id=(
                        ANNUITY_REDUCTION_APPROVAL_ID if lineage_has_approval else None
                    ),
                )
            )
    transaction.commit()
    return existing.obligation.id


def _review(transaction: Session) -> str:
    result = evidence_service.review_evidence_version(
        evidence_service.ReviewEvidenceVersionCommand(
            case_id=CASE_ID,
            evidence_version_id=OPEN_EVIDENCE_ID,
            reviewer_id=REVIEWER_ID,
            decision=evidence_service.EvidenceReviewDecision.APPROVE,
            reviewed_at=REVIEWED_AT,
            idempotency_key="open-license-period-review",
        ),
        transaction,
    )
    transaction.commit()
    return result.activity_id


def _command(source_activity_id: str, obligation_id: str, *, case_id: str = CASE_ID):
    command_type, _ = _boundary()
    return command_type(
        case_id=case_id,
        source_activity_id=source_activity_id,
        source_evidence_version_id=OPEN_EVIDENCE_ID,
        existing_obligation_id=obligation_id,
    )


def _counts(transaction: Session) -> tuple[int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationLine)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.lane == "FEE")
        )
        or 0,
    )


@pytest.mark.parametrize(
    (
        "existing_ratio",
        "lineage_provenance",
        "lineage_has_approval",
        "expected_ratio",
        "expected_payable",
    ),
    (
        (
            Decimal("0.0000"),
            "EXPLICIT_ENTRY",
            False,
            Decimal("0.1500"),
            Decimal("1020.00"),
        ),
        (
            Decimal("0.7000"),
            "EXPLICIT_ENTRY",
            True,
            Decimal("0.7000"),
            Decimal("360.00"),
        ),
        (
            Decimal("0.8500"),
            "CONFIRMED_MIGRATION",
            True,
            Decimal("0.8500"),
            Decimal("180.00"),
        ),
    ),
)
def test_reviewed_period_supersedes_only_existing_ordinary_annuity_with_best_benefit(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    existing_ratio: Decimal,
    lineage_provenance: str,
    lineage_has_approval: bool,
    expected_ratio: Decimal,
    expected_payable: Decimal,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            existing_reduction_ratio=existing_ratio,
            lineage_provenance=lineage_provenance,
            lineage_has_approval=lineage_has_approval,
        )
        grant_activity = transaction.get(CaseActivityEvent, ANNUITY_ACTIVITY_ID)
        grant_evidence = transaction.get(
            DocumentEvidenceVersion,
            ANNUITY_EVIDENCE_ID,
        )
        assert grant_activity is not None
        assert grant_evidence is not None
        assert grant_evidence.reviewer_id != grant_activity.reviewer_id
        assert grant_evidence.reviewed_at != grant_activity.effective_at
        source_activity_id = _review(transaction)
        _, recognize = _boundary()

        commit = Mock(side_effect=AssertionError("service must not commit"))
        rollback = Mock(side_effect=AssertionError("service must not roll back"))
        close = Mock(side_effect=AssertionError("service must not close"))
        with monkeypatch.context() as patch:
            patch.setattr(transaction, "commit", commit)
            patch.setattr(transaction, "rollback", rollback)
            patch.setattr(transaction, "close", close)
            result = recognize(_command(source_activity_id, existing_id), transaction)
            replay = recognize(_command(source_activity_id, existing_id), transaction)

        assert result.reused is False
        assert replay == replace(result, reused=True)
        assert commit.call_count == rollback.call_count == close.call_count == 0
        transaction.commit()

        assert _counts(transaction) == (2, 2, 2)
        prior = transaction.get(FeeObligation, existing_id)
        replacement = transaction.get(FeeObligation, result.obligation.id)
        assert prior is not None
        assert replacement is not None
        assert prior.obligation_status == "SUPERSEDED"
        assert replacement.supersedes_obligation_id == existing_id
        task = transaction.scalar(select(AnnuityTask).where(AnnuityTask.case_id == CASE_ID))
        assert task is not None
        assert replacement.supersedes_obligation_id == task.fee_obligation_id
        assert replacement.source_activity_id == source_activity_id
        assert replacement.source_document_id == OPEN_DOCUMENT_ID
        assert replacement.obligation_type == "FUTURE_ANNUITY"
        assert replacement.due_date == DUE_DATE

        prior_line = transaction.scalar(
            select(FeeObligationLine).where(FeeObligationLine.obligation_id == existing_id)
        )
        replacement_line = transaction.scalar(
            select(FeeObligationLine).where(FeeObligationLine.obligation_id == replacement.id)
        )
        assert prior_line is not None
        assert replacement_line is not None
        assert prior_line.current_identity_key is None
        assert replacement_line.current_identity_key is not None
        assert replacement_line.official_full_amount == Decimal("1200.00")
        assert replacement_line.reduction_ratio == expected_ratio
        assert replacement_line.payable_amount == expected_payable

        fee_activities = tuple(
            transaction.scalars(
                select(CaseActivityEvent)
                .where(CaseActivityEvent.lane == "FEE")
                .order_by(CaseActivityEvent.sequence)
            )
        )
        assert fee_activities[1].activity_type == "FEE_OBLIGATION_RECOGNIZED"
        assert fee_activities[1].source_activity_id == source_activity_id
        assert fee_activities[1].supersedes_event_id == fee_activities[0].id
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    "mutation",
    (
        "stale",
        "unconfirmed",
        "wrong_case",
        "wrong_ratio",
        "fee_code_out_of_scope",
        "fee_year_out_of_scope",
        "due_date_out_of_scope",
    ),
)
def test_invalid_reduced_approval_is_409_with_no_write(
    session_factory: sessionmaker[Session],
    mutation: str,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            existing_reduction_ratio=Decimal("0.7000"),
            lineage_provenance="EXPLICIT_ENTRY",
            lineage_has_approval=True,
        )
        source_activity_id = _review(transaction)
        approval = transaction.get(
            FeeReductionApproval,
            ANNUITY_REDUCTION_APPROVAL_ID,
        )
        assert approval is not None
        if mutation == "stale":
            approval_evidence = transaction.get(
                DocumentEvidenceVersion,
                ANNUITY_APPROVAL_EVIDENCE_ID,
            )
            assert approval_evidence is not None
            approval_evidence.current_identity_key = None
        elif mutation == "unconfirmed":
            approval.confirmation_status = "PENDING"
        elif mutation == "wrong_case":
            approval.case_id = WRONG_CASE_ID
        elif mutation == "wrong_ratio":
            approval.reduction_ratio = Decimal("0.8500")
        elif mutation == "fee_code_out_of_scope":
            fee_scope_snapshot = (
                '{"fee_codes":["CN_ANNUITY_FEE_UM"],"schema":"FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}'
            )
            approval.fee_scope_snapshot = fee_scope_snapshot
            approval.fee_scope_hash = sha256(fee_scope_snapshot.encode()).hexdigest()
        elif mutation == "fee_year_out_of_scope":
            approval.fee_year_from = 5
            approval.fee_year_to = 5
        elif mutation == "due_date_out_of_scope":
            approval.effective_to = date(2027, 7, 31)
        transaction.commit()

        _, recognize = _boundary()
        before = _counts(transaction)
        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, existing_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "existing_obligation"}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    ("patent_category", "fee_code", "altered_amount"),
    (
        ("INV", "CN_ANNUITY_FEE_INV", Decimal("1300.00")),
        ("UM", "CN_ANNUITY_FEE_UM", Decimal("1000.00")),
        ("DES", "CN_ANNUITY_FEE_DES", Decimal("1000.00")),
    ),
)
def test_canonical_but_altered_official_rate_and_matching_obligation_are_409_no_write(
    session_factory: sessionmaker[Session],
    patent_category: str,
    fee_code: str,
    altered_amount: Decimal,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            patent_category=patent_category,
            fee_code=fee_code,
            full_amount=altered_amount,
            rate_calc_params=ALTERED_ANNUITY_CALC_PARAMS[fee_code],
        )
        source_activity_id = _review(transaction)
        _, recognize = _boundary()
        before = _counts(transaction)

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, existing_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "existing_obligation"}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    ("patent_category", "fee_code", "official_amount"),
    (
        ("INV", "CN_ANNUITY_FEE_UM", Decimal("900.00")),
        ("UM", "CN_ANNUITY_FEE_DES", Decimal("900.00")),
        ("DES", "CN_ANNUITY_FEE_INV", Decimal("1200.00")),
        ("UNKNOWN", "CN_ANNUITY_FEE_INV", Decimal("1200.00")),
        (None, "CN_ANNUITY_FEE_INV", Decimal("1200.00")),
    ),
)
def test_future_annuity_fee_code_must_match_case_patent_category_409_no_write(
    session_factory: sessionmaker[Session],
    patent_category: str | None,
    fee_code: str,
    official_amount: Decimal,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            patent_category=patent_category,
            fee_code=fee_code,
            full_amount=official_amount,
        )
        source_activity_id = _review(transaction)
        if patent_category is None:
            case = transaction.get(Case, CASE_ID)
            assert case is not None
            set_committed_value(case, "patent_category", None)
            assert case not in transaction.dirty
        _, recognize = _boundary()
        before = _counts(transaction)

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, existing_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "existing_obligation"}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    (
        "existing_ratio",
        "lineage_provenance",
        "lineage_has_approval",
        "include_reduction_lineage",
    ),
    (
        (Decimal("0.0000"), "EXPLICIT_ENTRY", True, True),
        (Decimal("0.7000"), "EXPLICIT_ENTRY", False, True),
        (Decimal("0.0000"), "CONFIRMED_MIGRATION", True, True),
        (Decimal("0.0000"), "EXPLICIT_ENTRY", False, False),
    ),
)
def test_missing_or_illegal_future_annuity_reduction_lineage_is_409_with_no_write(
    session_factory: sessionmaker[Session],
    existing_ratio: Decimal,
    lineage_provenance: str,
    lineage_has_approval: bool,
    include_reduction_lineage: bool,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            existing_reduction_ratio=existing_ratio,
            include_reduction_lineage=include_reduction_lineage,
            lineage_provenance=lineage_provenance,
            lineage_has_approval=lineage_has_approval,
        )
        source_activity_id = _review(transaction)
        _, recognize = _boundary()
        before = _counts(transaction)

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, existing_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "existing_obligation"}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


def test_generic_shallow_future_annuity_is_409_with_no_write(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(transaction, accepted_future_annuity_lineage=False)
        source_activity_id = _review(transaction)
        _, recognize = _boundary()
        before = _counts(transaction)

        with pytest.raises(BusinessError) as captured:
            recognize(_command(source_activity_id, existing_id), transaction)

        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": "existing_obligation"}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


@pytest.mark.parametrize(
    ("mutation", "expected_field"),
    (
        ("outside_period", "period"),
        ("missing_obligation", "existing_obligation"),
        ("wrong_case", "source"),
        ("noncurrent_evidence", "source_evidence"),
        ("post_review_mutation", "source_snapshot"),
    ),
)
def test_conflicting_source_or_missing_existing_annuity_is_409_with_no_write(
    session_factory: sessionmaker[Session],
    mutation: str,
    expected_field: str,
) -> None:
    transaction = session_factory()
    try:
        existing_id = _seed(
            transaction,
            due_date=date(2028, 1, 1) if mutation == "outside_period" else DUE_DATE,
        )
        source_activity_id = _review(transaction)
        if mutation == "noncurrent_evidence":
            evidence = transaction.get(DocumentEvidenceVersion, OPEN_EVIDENCE_ID)
            assert evidence is not None
            evidence.current_identity_key = None
            transaction.commit()
        elif mutation == "post_review_mutation":
            document = transaction.get(Document, OPEN_DOCUMENT_ID)
            assert document is not None
            document.extra_data = _period_facts(period_end=date(2028, 12, 31))
            transaction.commit()

        _, recognize = _boundary()
        command = _command(
            source_activity_id,
            "missing-obligation" if mutation == "missing_obligation" else existing_id,
            case_id=WRONG_CASE_ID if mutation == "wrong_case" else CASE_ID,
        )
        before = _counts(transaction)
        with pytest.raises(BusinessError) as captured:
            recognize(command, transaction)
        assert captured.value.status_code == 409
        assert captured.value.code == "OPEN_LICENSE_ANNUITY_SOURCE_CONFLICT"
        assert captured.value.details == {"field": expected_field}
        assert _counts(transaction) == before == (1, 1, 1)
    finally:
        transaction.rollback()
        transaction.close()


def test_review_captures_canonical_period_snapshot(
    session_factory: sessionmaker[Session],
) -> None:
    transaction = session_factory()
    try:
        _seed(transaction)
        source_activity_id = _review(transaction)
        activity = transaction.get(CaseActivityEvent, source_activity_id)
        assert activity is not None
        payload = json.loads(activity.payload_json)
        snapshot = payload["source_snapshot"]
        assert snapshot == {
            "case_id": CASE_ID,
            "evidence_content_hash": CONTENT_HASH,
            "evidence_version_id": OPEN_EVIDENCE_ID,
            "period_end": "2027-12-31",
            "period_start": "2027-01-01",
            "schema": "FPMS_OPEN_LICENSE_IMPLEMENTATION_PERIOD_V1",
            "source_document_id": OPEN_DOCUMENT_ID,
        }
        expected_hash = f"sha256:{sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}"
        assert payload["source_snapshot_hash"] == expected_hash
        reference = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == source_activity_id
            )
        )
        assert reference is not None
        assert reference.content_hash == expected_hash
    finally:
        transaction.rollback()
        transaction.close()
