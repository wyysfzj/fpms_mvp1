from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

import scripts.seed_dev as seed_dev
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import fee_linking_service, official_notice_catalog
from app.modules.documents.application_fee_notice_contracts import (
    ApplicationFeeNotice,
    ApplicationFeeNoticeItem,
    ApplicationFeeNoticeSource,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.documents.schemas import DocumentCreateIn
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.documents.service import create_document
from app.modules.fees.models import FeeDraft, FeeObligation
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
)
from app.modules.tasks.models import Task

PRIOR_EXECUTABLE_CODES = {
    "OFFICIAL_NOTICE_001",
    "OFFICIAL_NOTICE_003",
    "OFFICIAL_NOTICE_005",
    "OFFICIAL_NOTICE_009",
    "OFFICIAL_NOTICE_021",
    "OFFICIAL_NOTICE_024",
    "OFFICIAL_NOTICE_029",
}
APPLICATION_FEE_NOTICE_CODE = "OFFICIAL_NOTICE_034"
EXPECTED_EXECUTABLE_CODES = PRIOR_EXECUTABLE_CODES | {APPLICATION_FEE_NOTICE_CODE}


def _seed_application_fee_catalog(db: Session) -> int:
    seed = getattr(
        official_notice_catalog,
        "seed_application_fee_official_notice_catalog",
        None,
    )
    assert callable(seed), "application-fee-activated official-notice catalog seeder is missing"
    return seed(db)


def _catalog_rows(db: Session) -> list[DocTemplate]:
    return list(
        db.scalars(
            select(DocTemplate)
            .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
            .order_by(DocTemplate.code.asc())
        )
    )


def _assert_application_fee_target_state(rows: list[DocTemplate]) -> None:
    assert len(rows) == len(official_notice_catalog.OFFICIAL_NOTICE_CATALOG) == 60
    executable_codes = {
        row.code
        for row in rows
        if json.loads(row.input_fields or "{}")["catalog_status"] == "EXECUTABLE"
    }
    assert executable_codes == EXPECTED_EXECUTABLE_CODES

    target = next(row for row in rows if row.code == APPLICATION_FEE_NOTICE_CODE)
    metadata = json.loads(target.input_fields or "{}")
    assert target.name == "缴纳申请费通知书"
    assert metadata["official_doc_codes"] == ["200103"]
    assert target.status_effect is None
    assert target.deadline_template_code is None
    assert target.fee_draft_type == "APPLICATION_FEE"
    assert target.need_reply is False
    assert metadata["execution_behavior"] == "APPLICATION_FEE_NOTICE"
    assert metadata["canonical_template_code"] == "APPLICATION_FEE_NOTICE"
    assert metadata["deadline_source_policy"] == "EXPLICIT_OFFICIAL_DUE_REQUIRED"
    assert metadata["completion_event"] is None
    assert metadata["archive_status_restore"] is None

    for row in rows:
        if row.code in EXPECTED_EXECUTABLE_CODES:
            continue
        metadata = json.loads(row.input_fields or "{}")
        assert metadata["catalog_status"] == "REFERENCE_ONLY"
        assert metadata["execution_behavior"] is None
        assert metadata["canonical_template_code"] is None
        assert metadata["deadline_source_policy"] is None
        assert row.status_effect is None
        assert row.deadline_template_code is None
        assert row.fee_draft_type is None
        assert row.need_reply is False


def test_application_fee_target_state_adds_only_row_34_and_is_idempotent(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as db:
        assert _seed_application_fee_catalog(db) == 60
        db.commit()
        rows = _catalog_rows(db)
        _assert_application_fee_target_state(rows)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in rows]

        assert _seed_application_fee_catalog(db) == 0
        db.commit()
        second_rows = _catalog_rows(db)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot


def test_seed_dev_uses_application_fee_target_state_idempotently(
    monkeypatch,
    session_factory: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(seed_dev, "seed_official_letter_out_catalog", lambda _db: 0)
    monkeypatch.setattr(seed_dev, "seed_grant_fee_notice_template_source", lambda _db: False)
    monkeypatch.setattr(seed_dev, "seed_format_letter_mappings", lambda _db: 0)

    with session_factory() as db:
        seed_dev.seed_doc_templates(db)
        first_rows = _catalog_rows(db)
        _assert_application_fee_target_state(first_rows)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in first_rows]

        seed_dev.seed_doc_templates(db)
        second_rows = _catalog_rows(db)
        _assert_application_fee_target_state(second_rows)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot


def _canonical_notice_bytes(notice: ApplicationFeeNotice) -> bytes:
    return json.dumps(
        {
            "currency": notice.currency,
            "items": [
                {
                    "fee_code": item.fee_code,
                    "fee_name": item.fee_name,
                    "source_amount": format(item.source_amount, ".2f"),
                }
                for item in notice.items
            ],
            "schema": notice.schema,
            "total_amount": format(notice.total_amount, ".2f"),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def _application_fee_preview(case_id: str, document_id: str) -> FeeEstimate:
    line = FeeObligationLineInput(
        fee_code="CN_INV_APPLICATION_FEE",
        fee_name="发明专利申请费",
        fee_year_key=0,
        official_full_amount=Decimal("900.00"),
        reduction_ratio=Decimal("0.0000"),
        payable_amount=Decimal("900.00"),
        source_amount=None,
        source_date=None,
        difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
    )
    return FeeEstimate(
        case_id=case_id,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=FeeEstimateContext(
            trigger="APPLICATION_FEE_NOTICE",
            source_document_id=document_id,
        ),
        currency="CNY",
        candidates=(
            FeeEstimateCandidate(
                line=line,
                source=FeeEstimateSource(
                    rate_id="rate-application-fee",
                    source_document_id=None,
                    source_doc="official-rate-book",
                    source_url=None,
                    source_policy=None,
                    source_version="2026-07-01",
                    status=FeeSourceStatus.VERIFIED,
                ),
            ),
        ),
        total_payable_amount=Decimal("900.00"),
    )


def test_reviewed_real_create_path_reaches_one_obligation_without_other_side_effects(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = f"case-app-fee-activation-{uuid4().hex[:8]}"
    attachment_id = f"attachment-app-fee-{uuid4().hex[:8]}"
    evidence_id = f"evidence-app-fee-{uuid4().hex[:8]}"
    review_activity_id = f"review-app-fee-{uuid4().hex[:8]}"
    reviewer_id = f"reviewer-{uuid4().hex[:8]}"
    creator_id = f"creator-{uuid4().hex[:8]}"
    reviewed_at = datetime(2026, 7, 22, 10, 30)
    source_date = date(2026, 7, 21)
    due_date = date(2026, 8, 5)
    content_hash = f"sha256:{'b' * 64}"

    with session_factory() as db:
        _seed_application_fee_catalog(db)
        db.flush()
        template = db.scalar(
            select(DocTemplate).where(DocTemplate.code == APPLICATION_FEE_NOTICE_CODE)
        )
        assert template is not None
        semantics = resolve_document_semantics(template)
        assert semantics.execution_behavior == "APPLICATION_FEE_NOTICE"
        assert semantics.deadline_source_policy == "EXPLICIT_OFFICIAL_DUE_REQUIRED"

        case = Case(
            id=case_id,
            case_no=f"APP-FEE-ACT-{uuid4().hex[:8].upper()}",
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
        db.add(case)
        db.flush()
        document = create_document(
            db,
            DocumentCreateIn(
                case_id=case_id,
                doc_template_id=template.id,
                direction="IN",
                doc_date=source_date,
                title="缴纳申请费通知书",
                official_due_date=due_date,
                official_due_date_source="MANUAL_OFFICIAL_NOTICE",
                official_due_date_status="CONFIRMED",
            ),
        )
        assert fee_linking_service.maybe_create_fee_draft(db, document, template) is None
        db.add(
            DocAttachment(
                id=attachment_id,
                document_id=document.id,
                file_name="application-fee-notice.pdf",
                file_path="/evidence/application-fee-notice.pdf",
                content_hash=content_hash,
            )
        )
        db.flush()
        db.add(
            DocumentEvidenceVersion(
                id=evidence_id,
                case_id=case_id,
                document_id=document.id,
                attachment_id=attachment_id,
                lineage_key="application-fee-notice",
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id=creator_id,
                review_state="APPROVED",
                reviewer_id=reviewer_id,
                reviewed_at=reviewed_at,
                final_submitted_at=None,
                content_hash=content_hash,
                current_identity_key=f"{case_id}|application-fee-notice",
            )
        )
        review_payload = {
            "creator_id": creator_id,
            "decision": "APPROVE",
            "evidence_version_id": evidence_id,
            "previous_review_state": "PENDING",
            "review_state": "APPROVED",
            "reviewer_id": reviewer_id,
        }
        db.add(
            CaseActivityEvent(
                id=review_activity_id,
                case_id=case_id,
                sequence=1,
                lane="DOCUMENT",
                activity_type="DOCUMENT_EVIDENCE_REVIEW_DECIDED",
                source_activity_id=None,
                occurred_at=reviewed_at,
                effective_at=reviewed_at,
                confirmation_status="CONFIRMED",
                old_business_stage="PROSECUTION_MANAGEMENT",
                new_business_stage="PROSECUTION_MANAGEMENT",
                old_official_procedure_stage="ACCEPTED",
                new_official_procedure_stage="ACCEPTED",
                old_legal_status="APPLICATION_PENDING",
                new_legal_status="APPLICATION_PENDING",
                actor_id=reviewer_id,
                reviewer_id=reviewer_id,
                idempotency_key=f"document-evidence-review:{evidence_id}",
                supersedes_event_id=None,
                payload_json=json.dumps(
                    review_payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ),
            )
        )
        db.flush()
        db.add(
            CaseActivityEventEvidence(
                id=f"reference-{uuid4().hex[:8]}",
                case_id=case_id,
                activity_id=review_activity_id,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=evidence_id,
                content_hash=content_hash,
                captured_at=reviewed_at,
            )
        )
        db.flush()

        notice = ApplicationFeeNotice(
            schema="FPMS_APPLICATION_FEE_NOTICE_V1",
            currency="CNY",
            total_amount=Decimal("900.00"),
            items=(
                ApplicationFeeNoticeItem(
                    fee_code="CN_INV_APPLICATION_FEE",
                    fee_name="发明专利申请费",
                    source_amount=Decimal("900.00"),
                ),
            ),
            pct=None,
        )
        canonical_bytes = _canonical_notice_bytes(notice)
        source = ApplicationFeeNoticeSource(
            document_id=document.id,
            case_id=case_id,
            source_date=source_date,
            due_date=due_date,
            due_date_source="MANUAL_OFFICIAL_NOTICE",
            due_date_status="CONFIRMED",
            notice=notice,
            canonical_bytes=canonical_bytes,
            canonical_sha256=sha256(canonical_bytes).hexdigest(),
        )
        preview = _application_fee_preview(case_id, document.id)

        created = fee_linking_service.recognize_application_fee_notice_obligation(
            transaction=db,
            source=source,
            review_activity_id=review_activity_id,
            reviewed_evidence_version_id=evidence_id,
            reviewer_id=reviewer_id,
            official_preview=preview,
        )
        replay = fee_linking_service.recognize_application_fee_notice_obligation(
            transaction=db,
            source=source,
            review_activity_id=review_activity_id,
            reviewed_evidence_version_id=evidence_id,
            reviewer_id=reviewer_id,
            official_preview=preview,
        )

        assert created.reused is False
        assert replay.reused is True
        assert replay.obligation.id == created.obligation.id
        assert db.scalar(select(func.count()).select_from(FeeObligation)) == 1
        assert db.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert db.scalar(select(func.count()).select_from(Task)) == 0
        assert db.scalar(select(func.count()).select_from(Document)) == 1
        assert document.need_reply is False
        assert document.reply_to_id is None
        assert db.get(Case, case_id).status == "ACCEPTED"
