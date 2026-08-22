from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.annuity.models import AnnuityTask
from app.modules.annuity.service import (
    RecognizeFutureAnnuityObligationCommand,
    RecordAnnuityTaskInstructionCommand,
    recognize_future_annuity_obligation,
    record_annuity_task_instruction,
)
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.cnipa_annuity_rate_candidate import CNIPA_ANNUITY_SOURCE_SNAPSHOT
from app.modules.fees.fee_reduction import FeeReductionInput, FeeReductionInputProvenance
from app.modules.fees.models import FeeRate, OfficialRateBook

_EFFECTIVE_FROM = date(2026, 3, 30)
_BOOK_CODE = "CNIPA_PATENT_ANNUITY_20260330"
_SOURCE_REFERENCE = "https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"
_CALC_PARAMS = (
    '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
    '{"amount":"900.00","from":1,"to":3},'
    '{"amount":"1200.00","from":4,"to":6},'
    '{"amount":"2000.00","from":7,"to":9},'
    '{"amount":"4000.00","from":10,"to":12},'
    '{"amount":"6000.00","from":13,"to":15},'
    '{"amount":"8000.00","from":16,"to":20}]}'
)


def _official_book(transaction: Session, actor_id: str) -> None:
    book = transaction.scalar(
        select(OfficialRateBook).where(OfficialRateBook.book_code == _BOOK_CODE)
    )
    if book is None:
        book = OfficialRateBook(
            id=uuid4().hex,
            book_code=_BOOK_CODE,
            version_code="2026-03-30",
            source_authority="CNIPA",
            source_reference=_SOURCE_REFERENCE,
            source_version="2026-03-30",
            source_published_on=_EFFECTIVE_FROM,
            source_snapshot=CNIPA_ANNUITY_SOURCE_SNAPSHOT,
            source_snapshot_hash=sha256(CNIPA_ANNUITY_SOURCE_SNAPSHOT.encode()).hexdigest(),
            approval_status="APPROVED",
            approved_by=actor_id,
            approved_at=datetime(2026, 7, 19, 10, 0),
            effective_from=_EFFECTIVE_FROM,
            activation_status="ACTIVE",
            activated_by=actor_id,
            activated_at=datetime(2026, 7, 19, 10, 5),
            current_identity_key="CNIPA|CNIPA_PATENT_ANNUITY_20260330",
        )
        transaction.add(book)
        transaction.flush()
    if (
        transaction.scalar(
            select(FeeRate).where(
                FeeRate.official_rate_book_id == book.id,
                FeeRate.fee_code == "CN_ANNUITY_FEE_INV",
            )
        )
        is None
    ):
        transaction.add(
            FeeRate(
                id=uuid4().hex,
                fee_code="CN_ANNUITY_FEE_INV",
                fee_name="发明专利年费",
                fee_type="GOV",
                currency="CNY",
                enabled=True,
                calc_mode="TIER",
                calc_params=_CALC_PARAMS,
                allow_reduction=True,
                effective_from=_EFFECTIVE_FROM,
                source_doc="专利和集成电路布图设计缴费服务指南",
                source_url=_SOURCE_REFERENCE,
                source_version="2026-03-30",
                source_status="PENDING_CONFIRMATION",
                official_rate_book_id=book.id,
            )
        )


def _grant_source(
    transaction: Session,
    case: Case,
    actor_id: str,
) -> tuple[str, str, str, str]:
    key = f"annuity-test-lineage:{case.id}"
    existing = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case.id,
            CaseActivityEvent.idempotency_key == key,
        )
    )
    if existing is not None:
        link = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == existing.id
            )
        )
        assert link is not None
        evidence = transaction.get(DocumentEvidenceVersion, link.object_id)
        assert evidence is not None
        return existing.id, evidence.document_id, evidence.id, evidence.content_hash

    token = uuid4().hex
    occurred_at = datetime(2026, 3, 30, 9, 0)
    content_hash = f"sha256:{sha256(f'annuity:{case.id}'.encode()).hexdigest()}"
    document_id, attachment_id, evidence_id, activity_id = (uuid4().hex for _ in range(4))
    sequence = int(case.lifecycle_revision or 0) + 1
    transaction.add(Document(id=document_id, case_id=case.id, direction="IN"))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name="grant-announcement.pdf",
            file_path=f"/evidence/{token}.pdf",
            content_hash=content_hash,
        )
    )
    transaction.flush()
    transaction.add(
        DocumentEvidenceVersion(
            id=evidence_id,
            case_id=case.id,
            document_id=document_id,
            attachment_id=attachment_id,
            lineage_key=f"grant-announcement-{token}",
            role="OFFICIAL_FINAL_PDF",
            version_number=1,
            state="FINAL",
            creator_id="annuity-lineage-creator",
            review_state="APPROVED",
            reviewer_id="annuity-lineage-reviewer",
            reviewed_at=occurred_at,
            content_hash=content_hash,
            current_identity_key=f"{case.id}|grant-announcement-{token}",
        )
    )
    transaction.add(
        CaseActivityEvent(
            id=activity_id,
            case_id=case.id,
            sequence=sequence,
            lane="LIFECYCLE",
            activity_type="GRANT_ANNOUNCEMENT_CONFIRMED",
            occurred_at=occurred_at,
            effective_at=occurred_at,
            confirmation_status="CONFIRMED",
            old_business_stage=case.business_stage,
            new_business_stage="POST_GRANT_MAINTENANCE",
            old_official_procedure_stage=case.official_procedure_stage,
            new_official_procedure_stage="GRANT_ANNOUNCED",
            old_legal_status=case.legal_status,
            new_legal_status="PATENT_IN_FORCE",
            actor_id=actor_id,
            reviewer_id="annuity-lineage-reviewer",
            idempotency_key=key,
            payload_json="{}",
        )
    )
    transaction.flush()
    transaction.add(
        CaseActivityEventEvidence(
            id=uuid4().hex,
            case_id=case.id,
            activity_id=activity_id,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=evidence_id,
            content_hash=content_hash,
            captured_at=occurred_at,
        )
    )
    case.status = "GRANTED"
    case.business_stage = "POST_GRANT_MAINTENANCE"
    case.official_procedure_stage = "GRANT_ANNOUNCED"
    case.legal_status = "PATENT_IN_FORCE"
    case.lifecycle_verification_status = "CONFIRMED"
    case.lifecycle_revision = sequence
    return activity_id, document_id, evidence_id, content_hash


def seed_annuity_obligations_with_pay_instruction(
    session_factory: sessionmaker,
    task_ids: Iterable[int],
) -> None:
    with session_factory() as transaction:
        admin = transaction.scalar(select(T_User).where(T_User.username == "admin"))
        assert admin is not None
        actor_id = str(admin.id)
        _official_book(transaction, actor_id)
        transaction.commit()
        for task_id in task_ids:
            task = transaction.get(AnnuityTask, task_id)
            assert task is not None and task.due_date >= _EFFECTIVE_FROM
            case = transaction.get(Case, task.case_id)
            assert case is not None
            activity_id, document_id, evidence_id, content_hash = _grant_source(
                transaction, case, actor_id
            )
            year_no, due_date = task.year_no, task.due_date
            transaction.commit()
            recognize_future_annuity_obligation(
                RecognizeFutureAnnuityObligationCommand(
                    annuity_task_id=task_id,
                    source_activity_id=activity_id,
                    source_document_id=document_id,
                    source_evidence_version_id=evidence_id,
                    source_evidence_content_hash=content_hash,
                    grant_fee_year_key=year_no,
                    rate_effective_on=due_date,
                    reduction_input=FeeReductionInput(
                        reduction_ratio=Decimal("0"),
                        provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
                    ),
                    reduction_approval_id=None,
                    actor_id=actor_id,
                    idempotency_key=f"annuity-test-recognition:{task_id}",
                ),
                transaction,
            )
            transaction.commit()
            record_annuity_task_instruction(
                RecordAnnuityTaskInstructionCommand(
                    annuity_task_id=task_id,
                    instruction="PAY",
                    actor_id=actor_id,
                    idempotency_key=f"annuity-test-instruction:{task_id}",
                ),
                transaction,
            )
            transaction.commit()
