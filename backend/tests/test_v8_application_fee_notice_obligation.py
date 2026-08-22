from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import fee_linking_service
from app.modules.documents.application_fee_notice_contracts import (
    ApplicationFeeNotice,
    ApplicationFeeNoticeEvidence,
    ApplicationFeeNoticeItem,
    ApplicationFeeNoticePct,
    ApplicationFeeNoticeSource,
    ApplicationFeeNoticeSourceError,
)
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import FeeObligation
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
)
from app.modules.fees.pct_policy import (
    ConfirmedPctEvidence,
    EvaluatePctNationalStageFeePolicyCommand,
    EvaluatePctNationalStageFeePolicyResult,
    PctFeePolicyDisposition,
)

CASE_ID = "case-application-fee"
DOCUMENT_ID = "document-application-fee-notice"
EVIDENCE_VERSION_ID = "evidence-application-fee-notice-v1"
REVIEW_ACTIVITY_ID = "activity-app-fee-notice-review"
REVIEWER_ID = "reviewer-application-fee-notice"
CREATOR_ID = "creator-application-fee-notice"
ATTACHMENT_ID = "attachment-application-fee-notice"
LINEAGE_KEY = "application-fee-notice"
SOURCE_DATE = date(2026, 7, 1)
DUE_DATE = date(2026, 7, 16)
REVIEWED_AT = datetime(2026, 7, 2, 10, 30)
CONTENT_HASH = f"sha256:{'a' * 64}"
PCT_ENTRY_DATE = date(2026, 6, 20)
PCT_EXEMPTIBLE_CODES = (
    "CN_INV_APPLICATION_FEE",
    "CN_UM_APPLICATION_FEE",
    "CN_EXCESS_CLAIM_FEE",
    "CN_SPEC_PAGE_31_300_FEE",
    "CN_SPEC_PAGE_301_PLUS_FEE",
)


def _review_payload() -> dict[str, str]:
    return {
        "creator_id": CREATOR_ID,
        "decision": "APPROVE",
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "previous_review_state": "PENDING",
        "review_state": "APPROVED",
        "reviewer_id": REVIEWER_ID,
    }


@pytest.fixture
def reviewed_transaction(
    session_factory: sessionmaker[Session],
) -> Session:
    transaction = session_factory()
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="APPLICATION-FEE-NOTICE",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            status="ACCEPTED",
            business_stage="PROSECUTION_MANAGEMENT",
            official_procedure_stage="ACCEPTED",
            legal_status="APPLICATION_PENDING",
            lifecycle_revision=1,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.add(
        Document(
            id=DOCUMENT_ID,
            case_id=CASE_ID,
            direction="IN",
            doc_date=SOURCE_DATE,
        )
    )
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=ATTACHMENT_ID,
            document_id=DOCUMENT_ID,
            file_name="application-fee-notice.pdf",
            file_path="/evidence/application-fee-notice.pdf",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=EVIDENCE_VERSION_ID,
            case_id=CASE_ID,
            document_id=DOCUMENT_ID,
            attachment_id=ATTACHMENT_ID,
            lineage_key=LINEAGE_KEY,
            role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            final_submitted_at=None,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|{LINEAGE_KEY}",
        )
    )
    transaction.add(
        CaseActivityEvent(
            id=REVIEW_ACTIVITY_ID,
            case_id=CASE_ID,
            sequence=1,
            lane="DOCUMENT",
            activity_type="DOCUMENT_EVIDENCE_REVIEW_DECIDED",
            source_activity_id=None,
            occurred_at=REVIEWED_AT,
            effective_at=REVIEWED_AT,
            confirmation_status="CONFIRMED",
            old_business_stage="PROSECUTION_MANAGEMENT",
            new_business_stage="PROSECUTION_MANAGEMENT",
            old_official_procedure_stage="ACCEPTED",
            new_official_procedure_stage="ACCEPTED",
            old_legal_status="APPLICATION_PENDING",
            new_legal_status="APPLICATION_PENDING",
            actor_id=REVIEWER_ID,
            reviewer_id=REVIEWER_ID,
            idempotency_key="document-evidence-review:application-fee-notice",
            supersedes_event_id=None,
            payload_json=json.dumps(
                _review_payload(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ),
        )
    )
    transaction.flush()
    transaction.add(
        CaseActivityEventEvidence(
            id="reference-app-fee-notice-review",
            case_id=CASE_ID,
            activity_id=REVIEW_ACTIVITY_ID,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=EVIDENCE_VERSION_ID,
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        )
    )
    transaction.commit()
    try:
        yield transaction
    finally:
        transaction.rollback()
        transaction.close()


def _canonical_bytes(notice: ApplicationFeeNotice) -> bytes:
    payload: dict[str, object] = {
        "schema": notice.schema,
        "currency": notice.currency,
        "total_amount": format(notice.total_amount, ".2f"),
        "items": [
            {
                "fee_code": item.fee_code,
                "fee_name": item.fee_name,
                "source_amount": format(item.source_amount, ".2f"),
            }
            for item in notice.items
        ],
    }
    if notice.pct is not None:
        payload["pct"] = {
            "national_stage_entry_date": notice.pct.national_stage_entry_date.isoformat(),
            "evidence": [
                {
                    "evidence_version_id": item.evidence_version_id,
                    "source_document_id": item.source_document_id,
                    "content_hash": item.content_hash,
                    "lineage_key": item.lineage_key,
                    "issuer": item.issuer,
                    "document_type": item.document_type,
                    "issued_on": item.issued_on.isoformat(),
                    "role": item.role,
                }
                for item in notice.pct.evidence
            ],
        }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def test_canonical_notice_maps_exactly_and_delegates_replay_idempotency(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
) -> None:
    adapter = getattr(
        fee_linking_service,
        "recognize_application_fee_notice_obligation",
        None,
    )
    assert callable(adapter), (
        "missing frozen behavior: fee_linking_service.py must expose "
        "recognize_application_fee_notice_obligation()"
    )

    notice = ApplicationFeeNotice(
        schema="FPMS_APPLICATION_FEE_NOTICE_V1",
        currency="CNY",
        total_amount=Decimal("980.00"),
        items=(
            ApplicationFeeNoticeItem(
                fee_code="CN_INV_APPLICATION_FEE",
                fee_name="发明专利申请费",
                source_amount=Decimal("900.00"),
            ),
            ApplicationFeeNoticeItem(
                fee_code="CN_PRIORITY_CLAIM_FEE",
                fee_name="优先权要求费",
                source_amount=Decimal("80.00"),
            ),
        ),
        pct=None,
    )
    canonical_bytes = _canonical_bytes(notice)
    source = ApplicationFeeNoticeSource(
        document_id=DOCUMENT_ID,
        case_id=CASE_ID,
        source_date=SOURCE_DATE,
        due_date=DUE_DATE,
        due_date_source="MANUAL_OFFICIAL_NOTICE",
        due_date_status="CONFIRMED",
        notice=notice,
        canonical_bytes=canonical_bytes,
        canonical_sha256=sha256(canonical_bytes).hexdigest(),
    )
    preview = FeeEstimate(
        case_id=CASE_ID,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=FeeEstimateContext(
            trigger="APPLICATION_FEE_NOTICE",
            source_document_id=DOCUMENT_ID,
        ),
        currency="CNY",
        candidates=(
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="CN_INV_APPLICATION_FEE",
                    fee_name="发明专利申请费",
                    fee_year_key=0,
                    official_full_amount=Decimal("900.00"),
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=Decimal("900.00"),
                    source_amount=None,
                    source_date=None,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=FeeEstimateSource(
                    rate_id="rate-application",
                    source_document_id=None,
                    source_doc="official-rate-book",
                    source_url=None,
                    source_policy=None,
                    source_version="2026-07-01",
                    status=FeeSourceStatus.VERIFIED,
                ),
            ),
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code="CN_PRIORITY_CLAIM_FEE",
                    fee_name="优先权要求费",
                    fee_year_key=0,
                    official_full_amount=Decimal("100.00"),
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=Decimal("100.00"),
                    source_amount=None,
                    source_date=None,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=FeeEstimateSource(
                    rate_id="rate-priority",
                    source_document_id=None,
                    source_doc="official-rate-book",
                    source_url=None,
                    source_policy=None,
                    source_version="2026-07-01",
                    status=FeeSourceStatus.VERIFIED,
                ),
            ),
        ),
        total_payable_amount=Decimal("1000.00"),
    )
    transaction = reviewed_transaction
    recognized = object()
    calls: list[tuple[RecognizeFeeObligationCommand, object]] = []

    def recognize_spy(
        command: RecognizeFeeObligationCommand,
        received_transaction: object,
    ) -> object:
        calls.append((command, received_transaction))
        return recognized

    def forbidden_draft(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("application-fee notice adapter must not create a draft")

    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        recognize_spy,
        raising=False,
    )
    monkeypatch.setattr(
        fee_linking_service,
        "maybe_create_fee_draft",
        forbidden_draft,
    )
    for side_effect_name in (
        "append_case_activity",
        "create_task",
        "create_reply",
        "update_document_status",
    ):
        monkeypatch.setattr(
            fee_linking_service,
            side_effect_name,
            forbidden_draft,
            raising=False,
        )

    result = adapter(
        transaction=transaction,
        source=source,
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=preview,
    )
    replay = adapter(
        transaction=transaction,
        source=source,
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=preview,
    )

    assert result is recognized
    assert replay is recognized
    assert len(calls) == 2
    assert calls[1] == calls[0]
    command, received_transaction = calls[0]
    assert received_transaction is transaction
    assert command == RecognizeFeeObligationCommand(
        case_id=CASE_ID,
        source_activity_id=REVIEW_ACTIVITY_ID,
        source_document_id=DOCUMENT_ID,
        fee_domain=FeeDomain.GOV,
        obligation_type="APPLICATION_FEE",
        due_date=DUE_DATE,
        currency="CNY",
        source_status=FeeSourceStatus.VERIFIED,
        lines=(
            FeeObligationLineInput(
                fee_code="CN_INV_APPLICATION_FEE",
                fee_name="发明专利申请费",
                fee_year_key=0,
                official_full_amount=Decimal("900.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("900.00"),
                source_amount=Decimal("900.00"),
                source_date=SOURCE_DATE,
                difference_review_state=FeeDifferenceReviewState.MATCHED,
            ),
            FeeObligationLineInput(
                fee_code="CN_PRIORITY_CLAIM_FEE",
                fee_name="优先权要求费",
                fee_year_key=0,
                official_full_amount=Decimal("100.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("80.00"),
                source_amount=Decimal("80.00"),
                source_date=SOURCE_DATE,
                difference_review_state=FeeDifferenceReviewState.REVIEW_REQUIRED,
            ),
        ),
        actor_id=REVIEWER_ID,
        idempotency_key=(f"application-fee-notice:{EVIDENCE_VERSION_ID}:MANUAL_OFFICIAL_NOTICE"),
        supersedes_obligation_id=None,
        supersede_reason=None,
    )
    assert len(command.lines) == len(source.notice.items)


def _adapter():
    adapter = getattr(
        fee_linking_service,
        "recognize_application_fee_notice_obligation",
        None,
    )
    assert callable(adapter), (
        "missing frozen behavior: fee_linking_service.py must expose "
        "recognize_application_fee_notice_obligation()"
    )
    return adapter


def _pct_reference(
    document_type: str,
    ordinal: int,
) -> ApplicationFeeNoticeEvidence:
    return ApplicationFeeNoticeEvidence(
        evidence_version_id=f"pct-evidence-{ordinal}",
        source_document_id=f"pct-document-{ordinal}",
        content_hash=f"sha256:{str(ordinal) * 64}",
        lineage_key=f"pct-lineage-{ordinal}",
        issuer="CNIPA",
        document_type=document_type,
        issued_on=date(2026, 6, ordinal),
        role="OFFICIAL_FINAL_PDF",
    )


def _confirmed_pct_evidence(
    reference: ApplicationFeeNoticeEvidence,
) -> ConfirmedPctEvidence:
    return ConfirmedPctEvidence(
        case_id=CASE_ID,
        source_document_id=reference.source_document_id,
        evidence_version_id=reference.evidence_version_id,
        content_hash=reference.content_hash,
        lineage_key=reference.lineage_key,
        current_identity_key=f"{CASE_ID}|{reference.lineage_key}",
        issuer=reference.issuer,
        document_type=reference.document_type,
        issued_on=reference.issued_on,
        role=reference.role,
        state="FINAL",
        review_state="APPROVED",
        creator_id=f"creator-{reference.evidence_version_id}",
        reviewer_id=f"reviewer-{reference.evidence_version_id}",
        reviewed_at=datetime(2026, 6, 21, 12, 0),
    )


def _source(
    fee_codes: tuple[str, ...],
    *,
    pct: ApplicationFeeNoticePct | None = None,
) -> ApplicationFeeNoticeSource:
    items = tuple(
        ApplicationFeeNoticeItem(
            fee_code=fee_code,
            fee_name=f"费用-{fee_code}",
            source_amount=Decimal("100.00"),
        )
        for fee_code in fee_codes
    )
    notice = ApplicationFeeNotice(
        schema="FPMS_APPLICATION_FEE_NOTICE_V1",
        currency="CNY",
        total_amount=Decimal("100.00") * len(items),
        items=items,
        pct=pct,
    )
    canonical_bytes = _canonical_bytes(notice)
    return ApplicationFeeNoticeSource(
        document_id=DOCUMENT_ID,
        case_id=CASE_ID,
        source_date=SOURCE_DATE,
        due_date=DUE_DATE,
        due_date_source="MANUAL_OFFICIAL_NOTICE",
        due_date_status="CONFIRMED",
        notice=notice,
        canonical_bytes=canonical_bytes,
        canonical_sha256=sha256(canonical_bytes).hexdigest(),
    )


def _preview(fee_codes: tuple[str, ...]) -> FeeEstimate:
    candidates = tuple(
        FeeEstimateCandidate(
            line=FeeObligationLineInput(
                fee_code=fee_code,
                fee_name=f"费用-{fee_code}",
                fee_year_key=0,
                official_full_amount=Decimal("100.00"),
                reduction_ratio=Decimal("0.0000"),
                payable_amount=Decimal("100.00"),
                source_amount=None,
                source_date=None,
                difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
            ),
            source=FeeEstimateSource(
                rate_id=f"rate-{fee_code}",
                source_document_id=None,
                source_doc="official-rate-book",
                source_url=None,
                source_policy=None,
                source_version="2026-07-01",
                status=FeeSourceStatus.VERIFIED,
            ),
        )
        for fee_code in fee_codes
    )
    return FeeEstimate(
        case_id=CASE_ID,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=FeeEstimateContext(
            trigger="APPLICATION_FEE_NOTICE",
            source_document_id=DOCUMENT_ID,
        ),
        currency="CNY",
        candidates=candidates,
        total_payable_amount=Decimal("100.00") * len(candidates),
    )


def test_ro_plus_isr_exempts_only_the_five_pct_application_fee_codes(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
) -> None:
    adapter = _adapter()
    references = (
        _pct_reference("CNIPA_RO_RECEIPT", 1),
        _pct_reference("CNIPA_ISR", 2),
    )
    confirmed = tuple(_confirmed_pct_evidence(item) for item in references)
    non_exempt_code = "CN_PRIORITY_CLAIM_FEE"
    fee_codes = (*PCT_EXEMPTIBLE_CODES, non_exempt_code)
    source = _source(
        fee_codes,
        pct=ApplicationFeeNoticePct(
            national_stage_entry_date=PCT_ENTRY_DATE,
            evidence=references,
        ),
    )
    policy_calls: list[EvaluatePctNationalStageFeePolicyCommand] = []
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    recognized = object()

    def evaluate_spy(
        command: EvaluatePctNationalStageFeePolicyCommand,
    ) -> EvaluatePctNationalStageFeePolicyResult:
        policy_calls.append(command)
        return EvaluatePctNationalStageFeePolicyResult(
            rule_code="CN_PCT_NATIONAL_STAGE_POLICY_594",
            source_reference="accepted-pct-policy",
            effective_from=date(2024, 7, 27),
            effective_to=None,
            evaluated_on=command.effective_on,
            fee_code=command.fee_code,
            disposition=PctFeePolicyDisposition.EXEMPT,
            evidence_document_ids=tuple(item.source_document_id for item in command.evidence),
            evidence_version_ids=tuple(item.evidence_version_id for item in command.evidence),
            full_amount=command.full_amount,
            reduction_ratio=Decimal("1.0000"),
            payable_ratio=Decimal("0.0000"),
            payable_amount=Decimal("0.00"),
        )

    def recognize_spy(
        command: RecognizeFeeObligationCommand,
        received_transaction: object,
    ) -> object:
        assert received_transaction is transaction
        recognition_calls.append(command)
        return recognized

    transaction = reviewed_transaction
    monkeypatch.setattr(
        fee_linking_service,
        "evaluate_pct_national_stage_fee_policy",
        evaluate_spy,
        raising=False,
    )
    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        recognize_spy,
        raising=False,
    )

    result = adapter(
        transaction=transaction,
        source=source,
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=_preview(fee_codes),
        confirmed_pct_evidence=confirmed,
    )

    assert result is recognized
    assert tuple(call.fee_code for call in policy_calls) == PCT_EXEMPTIBLE_CODES
    assert all(
        call.case_id == CASE_ID
        and call.effective_on == PCT_ENTRY_DATE
        and call.evidence == confirmed
        and call.reduction_context is None
        for call in policy_calls
    )
    assert len(recognition_calls) == 1
    lines = {line.fee_code: line for line in recognition_calls[0].lines}
    for fee_code in PCT_EXEMPTIBLE_CODES:
        assert lines[fee_code].official_full_amount == Decimal("100.00")
        assert lines[fee_code].reduction_ratio == Decimal("1.0000")
        assert lines[fee_code].payable_amount == Decimal("100.00")
        assert lines[fee_code].source_amount == Decimal("100.00")
        assert lines[fee_code].difference_review_state is FeeDifferenceReviewState.REVIEW_REQUIRED
    assert lines[non_exempt_code].reduction_ratio == Decimal("0.0000")
    assert lines[non_exempt_code].payable_amount == Decimal("100.00")
    assert lines[non_exempt_code].difference_review_state is FeeDifferenceReviewState.MATCHED


@pytest.mark.parametrize("pct_evidence_kind", ("none", "iprp"))
def test_absent_or_iprp_only_evidence_does_not_exempt_application_fee(
    monkeypatch: pytest.MonkeyPatch,
    pct_evidence_kind: str,
    reviewed_transaction: Session,
) -> None:
    adapter = _adapter()
    references: tuple[ApplicationFeeNoticeEvidence, ...] = ()
    pct = None
    if pct_evidence_kind == "iprp":
        references = (_pct_reference("CNIPA_IPRP", 3),)
        pct = ApplicationFeeNoticePct(
            national_stage_entry_date=PCT_ENTRY_DATE,
            evidence=references,
        )
    confirmed = tuple(_confirmed_pct_evidence(item) for item in references)
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    recognized = object()

    def recognize_spy(
        command: RecognizeFeeObligationCommand,
        _transaction: object,
    ) -> object:
        recognition_calls.append(command)
        return recognized

    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        recognize_spy,
        raising=False,
    )

    result = adapter(
        transaction=reviewed_transaction,
        source=_source(("CN_INV_APPLICATION_FEE",), pct=pct),
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
        confirmed_pct_evidence=confirmed,
    )

    assert result is recognized
    assert len(recognition_calls) == 1
    line = recognition_calls[0].lines[0]
    assert line.reduction_ratio == Decimal("0.0000")
    assert line.payable_amount == Decimal("100.00")
    assert line.source_amount == Decimal("100.00")
    assert line.difference_review_state is FeeDifferenceReviewState.MATCHED


@pytest.mark.parametrize(
    ("review_activity_id", "evidence_version_id"),
    (
        ("unrelated-review-activity", EVIDENCE_VERSION_ID),
        (REVIEW_ACTIVITY_ID, "unrelated-evidence-version"),
    ),
)
def test_unrelated_review_activity_or_evidence_is_409_with_no_obligation(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
    review_activity_id: str,
    evidence_version_id: str,
) -> None:
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        lambda command, _transaction: recognition_calls.append(command),
    )

    with pytest.raises(BusinessError) as captured:
        _adapter()(
            transaction=reviewed_transaction,
            source=_source(("CN_INV_APPLICATION_FEE",)),
            review_activity_id=review_activity_id,
            reviewed_evidence_version_id=evidence_version_id,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
        )

    assert captured.value.status_code == 409
    assert captured.value.code == "APPLICATION_FEE_NOTICE_SOURCE_CONFLICT"
    assert recognition_calls == []
    assert reviewed_transaction.scalar(select(func.count()).select_from(FeeObligation)) == 0


@pytest.mark.parametrize(
    ("carrier", "field", "value"),
    (
        ("evidence", "state", EvidenceVersionState.DRAFT.value),
        ("evidence", "review_state", EvidenceReviewState.PENDING.value),
        ("evidence", "reviewer_id", "unrelated-reviewer"),
        ("evidence", "reviewed_at", datetime(2026, 7, 2, 11, 0)),
        ("activity", "confirmation_status", "PENDING"),
        ("activity", "reviewer_id", "unrelated-reviewer"),
    ),
)
def test_nonfinal_or_mismatched_review_graph_is_409_with_no_obligation(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
    carrier: str,
    field: str,
    value: object,
) -> None:
    target = (
        reviewed_transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        if carrier == "evidence"
        else reviewed_transaction.get(CaseActivityEvent, REVIEW_ACTIVITY_ID)
    )
    assert target is not None
    setattr(target, field, value)
    reviewed_transaction.commit()
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        lambda command, _transaction: recognition_calls.append(command),
    )

    with pytest.raises(BusinessError) as captured:
        _adapter()(
            transaction=reviewed_transaction,
            source=_source(("CN_INV_APPLICATION_FEE",)),
            review_activity_id=REVIEW_ACTIVITY_ID,
            reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
        )

    assert captured.value.status_code == 409
    assert captured.value.code == "APPLICATION_FEE_NOTICE_SOURCE_CONFLICT"
    assert recognition_calls == []
    assert reviewed_transaction.scalar(select(func.count()).select_from(FeeObligation)) == 0


@pytest.mark.parametrize("carrier", ("payload", "reference"))
def test_mismatched_review_payload_or_reference_is_409_with_no_obligation(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
    carrier: str,
) -> None:
    if carrier == "payload":
        activity = reviewed_transaction.get(CaseActivityEvent, REVIEW_ACTIVITY_ID)
        assert activity is not None
        payload = _review_payload()
        payload["evidence_version_id"] = "unrelated-evidence-version"
        activity.payload_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    else:
        reference = reviewed_transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == REVIEW_ACTIVITY_ID
            )
        )
        assert reference is not None
        reference.object_id = "unrelated-evidence-version"
    reviewed_transaction.commit()
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        lambda command, _transaction: recognition_calls.append(command),
    )

    with pytest.raises(BusinessError) as captured:
        _adapter()(
            transaction=reviewed_transaction,
            source=_source(("CN_INV_APPLICATION_FEE",)),
            review_activity_id=REVIEW_ACTIVITY_ID,
            reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
        )

    assert captured.value.status_code == 409
    assert captured.value.code == "APPLICATION_FEE_NOTICE_SOURCE_CONFLICT"
    assert recognition_calls == []
    assert reviewed_transaction.scalar(select(func.count()).select_from(FeeObligation)) == 0


def test_changed_confirmed_due_source_is_409_and_does_not_duplicate_obligation(
    reviewed_transaction: Session,
) -> None:
    source = _source(("CN_INV_APPLICATION_FEE",))
    result = _adapter()(
        transaction=reviewed_transaction,
        source=source,
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
    )
    assert result.reused is False
    reviewed_transaction.commit()
    assert reviewed_transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1

    with pytest.raises(BusinessError) as captured:
        _adapter()(
            transaction=reviewed_transaction,
            source=replace(source, due_date_source="IMPORTED_OFFICIAL_NOTICE"),
            review_activity_id=REVIEW_ACTIVITY_ID,
            reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
        )

    assert captured.value.status_code == 409
    assert reviewed_transaction.scalar(select(func.count()).select_from(FeeObligation)) == 1


def _malformed_sources() -> tuple[tuple[str, object], ...]:
    valid = _source(("CN_INV_APPLICATION_FEE",))
    unknown_notice = replace(
        valid.notice,
        items=(
            ApplicationFeeNoticeItem(
                fee_code="UNKNOWN_APPLICATION_FEE",
                fee_name="未知费用",
                source_amount=Decimal("100.00"),
            ),
        ),
    )
    duplicate_item = valid.notice.items[0]
    duplicate_notice = replace(
        valid.notice,
        total_amount=Decimal("200.00"),
        items=(duplicate_item, duplicate_item),
    )
    return (
        ("missing-carrier", None),
        ("missing-source-date", replace(valid, source_date=None)),
        ("missing-due-date", replace(valid, due_date=None)),
        ("missing-due-source", replace(valid, due_date_source="")),
        (
            "unreachable-due-source",
            replace(valid, due_date_source="OFFICIAL_DUE_DATE"),
        ),
        ("canonical-bytes-not-bytes", replace(valid, canonical_bytes="not-bytes")),
        (
            "canonical-hash-mismatch",
            replace(valid, canonical_sha256="0" * 64),
        ),
        ("unknown-fee-code", replace(valid, notice=unknown_notice)),
        ("duplicate-fee-code", replace(valid, notice=duplicate_notice)),
        (
            "total-mismatch",
            replace(valid, notice=replace(valid.notice, total_amount=Decimal("99.00"))),
        ),
    )


@pytest.mark.parametrize(
    ("_case_name", "source"),
    _malformed_sources(),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_malformed_carrier_fails_before_recognition(
    monkeypatch: pytest.MonkeyPatch,
    _case_name: str,
    source: object,
    reviewed_transaction: Session,
) -> None:
    adapter = _adapter()
    recognition_calls: list[RecognizeFeeObligationCommand] = []

    def recognize_spy(
        command: RecognizeFeeObligationCommand,
        _transaction: object,
    ) -> None:
        recognition_calls.append(command)

    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        recognize_spy,
        raising=False,
    )

    with pytest.raises(ApplicationFeeNoticeSourceError):
        adapter(
            transaction=reviewed_transaction,
            source=source,
            review_activity_id=REVIEW_ACTIVITY_ID,
            reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
            confirmed_pct_evidence=(),
        )

    assert recognition_calls == []


def test_mirrored_but_unapproved_pct_evidence_fails_before_recognition(
    monkeypatch: pytest.MonkeyPatch,
    reviewed_transaction: Session,
) -> None:
    reference = replace(_pct_reference("CNIPA_IPRP", 3), issuer="UNAPPROVED")
    source = _source(
        ("CN_INV_APPLICATION_FEE",),
        pct=ApplicationFeeNoticePct(
            national_stage_entry_date=PCT_ENTRY_DATE,
            evidence=(reference,),
        ),
    )
    confirmed = (_confirmed_pct_evidence(reference),)
    recognition_calls: list[RecognizeFeeObligationCommand] = []
    monkeypatch.setattr(
        fee_linking_service,
        "recognize_obligation",
        lambda command, _transaction: recognition_calls.append(command),
        raising=False,
    )

    with pytest.raises(ApplicationFeeNoticeSourceError):
        _adapter()(
            transaction=reviewed_transaction,
            source=source,
            review_activity_id=REVIEW_ACTIVITY_ID,
            reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
            reviewer_id=REVIEWER_ID,
            official_preview=_preview(("CN_INV_APPLICATION_FEE",)),
            confirmed_pct_evidence=confirmed,
        )

    assert recognition_calls == []
