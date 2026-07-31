from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

import scripts.seed_dev as seed_dev
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents import fee_linking_service, official_notice_catalog
from app.modules.documents.evidence_contracts import EvidenceReviewState, EvidenceVersionState
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType
from app.modules.fees.fee_reduction_approval_service import (
    FeeReductionApprovalRecordDisposition,
    RecordFeeReductionApprovalCommand,
)
from app.modules.fees.models import FeeDraft, FeeObligation, FeeReductionApproval
from app.modules.tasks.models import Task

PRIOR_EXECUTABLE_CODES = {
    "OFFICIAL_NOTICE_001",
    "OFFICIAL_NOTICE_003",
    "OFFICIAL_NOTICE_005",
    "OFFICIAL_NOTICE_009",
    "OFFICIAL_NOTICE_021",
    "OFFICIAL_NOTICE_024",
    "OFFICIAL_NOTICE_029",
    "OFFICIAL_NOTICE_034",
}
TARGET_CODE = "OFFICIAL_NOTICE_031"
EXPECTED_EXECUTABLE_CODES = PRIOR_EXECUTABLE_CODES | {TARGET_CODE}
CONTENT_HASH = "sha256:" + "a" * 64


def _seed_fee_reduction_catalog(db: Session) -> int:
    seed = getattr(
        official_notice_catalog,
        "seed_fee_reduction_approval_official_notice_catalog",
        None,
    )
    assert callable(seed), "fee-reduction-approval official-notice seeder is missing"
    return seed(db)


def _catalog_rows(db: Session) -> list[DocTemplate]:
    return list(
        db.scalars(
            select(DocTemplate)
            .where(DocTemplate.code.like("OFFICIAL_NOTICE_%"))
            .order_by(DocTemplate.code.asc())
        )
    )


def _assert_target_state(rows: list[DocTemplate]) -> None:
    assert len(rows) == len(official_notice_catalog.OFFICIAL_NOTICE_CATALOG) == 60
    executable_codes = {
        row.code
        for row in rows
        if json.loads(row.input_fields or "{}")["catalog_status"] == "EXECUTABLE"
    }
    assert executable_codes == EXPECTED_EXECUTABLE_CODES

    target = next(row for row in rows if row.code == TARGET_CODE)
    metadata = json.loads(target.input_fields or "{}")
    assert target.name == "费用减缓审批通知书"
    assert metadata["official_doc_codes"] == ["200021"]
    assert metadata["execution_behavior"] == "FEE_REDUCTION_APPROVAL_NOTICE"
    assert metadata["canonical_template_code"] == "FEE_REDUCTION_APPROVAL_NOTICE"
    assert metadata["deadline_source_policy"] is None
    assert metadata["completion_event"] is None
    assert metadata["archive_status_restore"] is None
    assert target.status_effect is None
    assert target.deadline_template_code is None
    assert target.fee_draft_type is None
    assert target.need_reply is False
    assert target.reply_to_template_code is None

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


def test_target_state_adds_only_row_31_and_seed_dev_is_idempotent(
    monkeypatch,
    session_factory: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(seed_dev, "seed_official_letter_out_catalog", lambda _db: 0)
    monkeypatch.setattr(seed_dev, "seed_grant_fee_notice_template_source", lambda _db: False)
    monkeypatch.setattr(seed_dev, "seed_format_letter_mappings", lambda _db: 0)

    with session_factory() as db:
        seed_dev.seed_doc_templates(db)
        first_rows = _catalog_rows(db)
        _assert_target_state(first_rows)
        first_snapshot = [(row.id, row.code, row.input_fields) for row in first_rows]

        seed_dev.seed_doc_templates(db)
        second_rows = _catalog_rows(db)
        _assert_target_state(second_rows)
        assert [(row.id, row.code, row.input_fields) for row in second_rows] == first_snapshot


def test_reviewed_notice_records_exactly_one_approval_without_other_side_effects(
    session_factory: sessionmaker[Session],
) -> None:
    case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    evidence_id = str(uuid4())
    applicant_id = str(uuid4())
    reviewer_id = str(uuid4())
    creator_id = str(uuid4())
    confirmed_at = datetime(2026, 7, 12, 9, 30)

    with session_factory() as db:
        _seed_fee_reduction_catalog(db)
        db.add(
            Case(
                id=case_id,
                case_no=f"FEE-REDUCTION-{uuid4().hex[:8].upper()}",
                status="ACCEPTED",
            )
        )
        db.add(Document(id=document_id, case_id=case_id))
        db.flush()
        db.add(
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name="fee-reduction-approval.pdf",
                file_path="/evidence/fee-reduction-approval.pdf",
            )
        )
        db.flush()
        db.add(
            DocumentEvidenceVersion(
                id=evidence_id,
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                lineage_key="fee-reduction-approval-notice",
                role="OFFICIAL_NOTICE",
                version_number=1,
                state=EvidenceVersionState.FINAL.value,
                creator_id=creator_id,
                review_state=EvidenceReviewState.APPROVED.value,
                reviewer_id=reviewer_id,
                reviewed_at=confirmed_at,
                final_submitted_at=confirmed_at,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{case_id}|fee-reduction-approval-notice",
            )
        )
        db.commit()

        template = db.scalar(select(DocTemplate).where(DocTemplate.code == TARGET_CODE))
        assert template is not None
        command = RecordFeeReductionApprovalCommand(
            case_id=case_id,
            scope_type=FeeReductionApprovalScopeType.CASE,
            applicant_ids=(applicant_id,),
            eligibility_attributes_version="reviewed-notice-v1",
            eligibility_attributes_json=json.dumps(
                {applicant_id: {"kind": "个人"}},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            reduction_ratio=Decimal("0.85"),
            fee_codes=("CN_INV_APPLICATION_FEE", "CN_ANNUITY_FEE_INV"),
            fee_year_from=1,
            fee_year_to=10,
            effective_from=date(2026, 7, 1),
            effective_to=date(2036, 6, 30),
            source_evidence_version_id=evidence_id,
            expected_source_content_hash=CONTENT_HASH,
            confirmed_at=confirmed_at,
            confirmed_by=reviewer_id,
        )
        before = {
            "activities": db.scalar(select(func.count()).select_from(CaseActivityEvent)),
            "documents": db.scalar(select(func.count()).select_from(Document)),
            "drafts": db.scalar(select(func.count()).select_from(FeeDraft)),
            "obligations": db.scalar(select(func.count()).select_from(FeeObligation)),
            "tasks": db.scalar(select(func.count()).select_from(Task)),
        }

        created = fee_linking_service.maybe_record_fee_reduction_approval_notice(
            transaction=db,
            template=template,
            command=command,
        )
        replay = fee_linking_service.maybe_record_fee_reduction_approval_notice(
            transaction=db,
            template=template,
            command=command,
        )

        assert created is not None
        assert replay is not None
        assert created.disposition is FeeReductionApprovalRecordDisposition.CREATED
        assert replay.disposition is FeeReductionApprovalRecordDisposition.REUSED
        assert replay.approval_id == created.approval_id
        assert db.scalar(select(func.count()).select_from(FeeReductionApproval)) == 1
        approval = db.get(FeeReductionApproval, created.approval_id)
        assert approval is not None
        assert approval.source_evidence_version_id == evidence_id
        assert approval.scope_type == FeeReductionApprovalScopeType.CASE.value
        assert approval.reduction_ratio == Decimal("0.8500")
        assert json.loads(approval.fee_scope_snapshot)["fee_codes"] == [
            "CN_ANNUITY_FEE_INV",
            "CN_INV_APPLICATION_FEE",
        ]
        assert db.get(Case, case_id).status == "ACCEPTED"
        after = {
            "activities": db.scalar(select(func.count()).select_from(CaseActivityEvent)),
            "documents": db.scalar(select(func.count()).select_from(Document)),
            "drafts": db.scalar(select(func.count()).select_from(FeeDraft)),
            "obligations": db.scalar(select(func.count()).select_from(FeeObligation)),
            "tasks": db.scalar(select(func.count()).select_from(Task)),
        }
        assert after == before
