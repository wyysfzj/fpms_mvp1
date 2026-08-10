from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList
from app.modules.annuity.service import create_pay_list_from_fee_items
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import fee_linking_service
from app.modules.documents.application_fee_notice_contracts import (
    ApplicationFeeNotice,
    ApplicationFeeNoticeItem,
    ApplicationFeeNoticeSource,
    ApplicationFeeNoticeSourceError,
)
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
)
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeDifferenceReviewState,
    FeeEstimate,
    FeeEstimateCandidate,
    FeeEstimateContext,
    FeeEstimateSource,
    FeeEstimateStatus,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecordFeeObligationInstructionCommand,
)
from app.modules.fees.obligation_service import record_client_instruction
from app.modules.masterdata.clients.models import Client
from app.modules.system.decision_gate_service import DecisionGateCode
from app.modules.system.models import CustomerDecisionGate

CASE_ID = "case-application-auto-draft"
CLIENT_ID = "client-application-auto-draft"
DOCUMENT_ID = "document-application-auto-draft"
ATTACHMENT_ID = "attachment-application-auto-draft"
EVIDENCE_VERSION_ID = "evidence-application-auto-draft-v1"
REVIEW_ACTIVITY_ID = "activity-app-auto-draft-review"
REVIEWER_ID = "reviewer-application-auto-draft"
CREATOR_ID = "creator-application-auto-draft"
SOURCE_DATE = date(2026, 8, 10)
DUE_DATE = date(2026, 8, 25)
AS_OF = datetime(2026, 8, 11, 8, 30)
REVIEWED_AT = datetime(2026, 8, 10, 16, 0)
CONTENT_HASH = f"sha256:{'a' * 64}"
DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"


def _canonical(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _canonical_notice_bytes(notice: ApplicationFeeNotice) -> bytes:
    return _canonical(
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
        }
    ).encode()


def _source() -> ApplicationFeeNoticeSource:
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
    canonical_bytes = _canonical_notice_bytes(notice)
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


def _preview() -> FeeEstimate:
    lines = (
        ("CN_INV_APPLICATION_FEE", "发明专利申请费", Decimal("900.00")),
        ("CN_PRIORITY_CLAIM_FEE", "优先权要求费", Decimal("100.00")),
    )
    return FeeEstimate(
        case_id=CASE_ID,
        estimate_status=FeeEstimateStatus.ESTIMATE,
        trigger_context=FeeEstimateContext(
            trigger="APPLICATION_FEE_NOTICE",
            source_document_id=DOCUMENT_ID,
        ),
        currency="CNY",
        candidates=tuple(
            FeeEstimateCandidate(
                line=FeeObligationLineInput(
                    fee_code=fee_code,
                    fee_name=fee_name,
                    fee_year_key=0,
                    official_full_amount=official_amount,
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=official_amount,
                    source_amount=None,
                    source_date=None,
                    difference_review_state=FeeDifferenceReviewState.SOURCE_PENDING,
                ),
                source=FeeEstimateSource(
                    rate_id=f"rate-{fee_code}",
                    source_document_id=None,
                    source_doc="reviewed-rate-book",
                    source_url=None,
                    source_policy="CURRENT_OFFICIAL",
                    source_version="2026-03-30",
                    status=FeeSourceStatus.VERIFIED,
                ),
            )
            for fee_code, fee_name, official_amount in lines
        ),
        total_payable_amount=Decimal("1000.00"),
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


def _seed_authority(transaction: Session, *, gate: bool = True) -> None:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    transaction.add(Client(id=CLIENT_ID, client_code="APP-AUTO", name_cn="申请草单客户"))
    transaction.flush()
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="APPLICATION-AUTO-DRAFT",
            client_id=CLIENT_ID,
            status="ACCEPTED",
            business_stage="PROSECUTION_MANAGEMENT",
            official_procedure_stage="ACCEPTED",
            legal_status="APPLICATION_PENDING",
            lifecycle_revision=1,
            lifecycle_verification_status="CONFIRMED",
        )
    )
    transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN", doc_date=SOURCE_DATE))
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
            lineage_key="application-auto-draft",
            role=EvidenceRole.OFFICIAL_FINAL_PDF.value,
            version_number=1,
            state=EvidenceVersionState.FINAL.value,
            creator_id=CREATOR_ID,
            review_state=EvidenceReviewState.APPROVED.value,
            reviewer_id=REVIEWER_ID,
            reviewed_at=REVIEWED_AT,
            content_hash=CONTENT_HASH,
            current_identity_key=f"{CASE_ID}|application-auto-draft",
        )
    )
    transaction.add(
        CaseActivityEvent(
            id=REVIEW_ACTIVITY_ID,
            case_id=CASE_ID,
            sequence=1,
            lane="DOCUMENT",
            activity_type="DOCUMENT_EVIDENCE_REVIEW_DECIDED",
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
            idempotency_key="review:application-auto-draft",
            payload_json=_canonical(_review_payload()),
        )
    )
    transaction.flush()
    transaction.add(
        CaseActivityEventEvidence(
            id="reference-application-auto-draft",
            case_id=CASE_ID,
            activity_id=REVIEW_ACTIVITY_ID,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=EVIDENCE_VERSION_ID,
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        )
    )
    if gate:
        transaction.add(
            CustomerDecisionGate(
                id="gate-application-auto-draft",
                gate_code=DecisionGateCode.FEE_APPLICATION_DRAFT.value,
                scope_key="GLOBAL",
                decision_value="APPROVED_POLICY",
                decision_status="CONFIRMED",
                source_reference=DECISION_SOURCE,
                source_version=DECISION_VERSION,
                confirmed_by=actor_id,
                effective_at=datetime(2026, 8, 10, 0, 0),
                supersedes_gate_id=None,
                decision_snapshot="{}",
                idempotency_key="gate:application-auto-draft",
                current_identity_key="DG-FEE-APPLICATION-DRAFT|GLOBAL",
            )
        )
    transaction.commit()


def _policy():
    policy = getattr(fee_linking_service, "apply_application_fee_auto_draft_policy", None)
    assert callable(policy), "missing reviewed-notice application auto-draft policy"
    return policy


def _apply(transaction: Session):
    return _policy()(
        transaction=transaction,
        source=_source(),
        review_activity_id=REVIEW_ACTIVITY_ID,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        reviewer_id=REVIEWER_ID,
        official_preview=_preview(),
        as_of=AS_OF,
    )


def _counts(transaction: Session) -> tuple[int, int, int, int, int]:
    return (
        transaction.scalar(select(func.count()).select_from(FeeObligation)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeDraft)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeItem)) or 0,
        transaction.scalar(select(func.count()).select_from(FeeObligationDraftItemLink)) or 0,
        transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED")
        )
        or 0,
    )


def test_reviewed_notice_policy_creates_one_pending_internal_draft_and_replays(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        result = _apply(transaction)
        replay = _apply(transaction)

        assert replay.recognition.obligation.id == result.recognition.obligation.id
        assert replay.draft.draft_id == result.draft.draft_id
        assert replay.recognition.reused is True
        assert replay.draft.activity_reused is True
        assert _counts(transaction) == (1, 1, 2, 2, 1)
        obligation = transaction.get(FeeObligation, result.recognition.obligation.id)
        draft = transaction.get(FeeDraft, result.draft.draft_id)
        assert obligation is not None and draft is not None
        assert obligation.client_instruction_status == "PENDING"
        assert obligation.payment_status == "UNPAID"
        assert obligation.official_evidence_status == "PENDING"
        assert draft.status == "OPEN"
        assert draft.draft_type == "GENERIC"
        assert draft.amount == Decimal("980.00")
        assert {
            line.difference_review_state.value for line in result.recognition.obligation.lines
        } == {
            "MATCHED",
            "REVIEW_REQUIRED",
        }
        items = transaction.scalars(select(FeeItem).order_by(FeeItem.fee_code)).all()
        assert [item.amount for item in items] == [Decimal("900.00"), Decimal("80.00")]
        activity = transaction.get(CaseActivityEvent, result.draft.activity_id)
        assert activity is not None
        payload = json.loads(activity.payload_json)
        assert set(payload) == {
            "actor_id",
            "authority",
            "center_changes",
            "draft_id",
            "links",
            "obligation_id",
            "schema",
        }
        assert payload["authority"] == "REVIEWED_APPLICATION_FEE_NOTICE"
        assert payload["schema"] == "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1"
        assert activity.source_activity_id == result.recognition.activity_id


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_value", "REJECTED"),
        ("source_reference", "wrong-source"),
        ("source_version", "wrong-version"),
        ("scope_key", "case:wrong"),
    ),
)
def test_wrong_gate_authority_is_409_before_business_writes(
    session_factory: sessionmaker,
    field: str,
    value: str,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        gate = transaction.get(CustomerDecisionGate, "gate-application-auto-draft")
        assert gate is not None
        setattr(gate, field, value)
        if field == "scope_key":
            gate.current_identity_key = "DG-FEE-APPLICATION-DRAFT|case:wrong"
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            _apply(transaction)

        assert raised.value.status_code == 409
        assert _counts(transaction) == (0, 0, 0, 0, 0)


def test_malformed_carrier_stays_400_and_dirty_state_precedes_gate_and_writers(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        source = _source()
        with pytest.raises(ApplicationFeeNoticeSourceError) as malformed:
            _policy()(
                transaction=transaction,
                source=replace(source, canonical_sha256="wrong"),
                review_activity_id=REVIEW_ACTIVITY_ID,
                reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
                reviewer_id=REVIEWER_ID,
                official_preview=_preview(),
                as_of=AS_OF,
            )
        assert malformed.value.status_code == 400

        calls: list[str] = []
        monkeypatch.setattr(
            fee_linking_service,
            "resolve_decision_gate",
            lambda *_args, **_kwargs: calls.append("gate"),
            raising=False,
        )
        monkeypatch.setattr(
            fee_linking_service,
            "recognize_application_fee_notice_obligation",
            lambda **_kwargs: calls.append("recognize"),
        )
        monkeypatch.setattr(
            fee_linking_service,
            "prepare_draft",
            lambda *_args, **_kwargs: calls.append("draft"),
            raising=False,
        )
        transaction.add(Case(id="dirty-application-auto-draft", case_no="DIRTY-AUTO-DRAFT"))
        with pytest.raises(BusinessError) as dirty:
            _apply(transaction)
        assert dirty.value.code == "FEE_OBLIGATION_TRANSACTION_DIRTY"
        assert dirty.value.status_code == 409
        assert calls == []


def test_fault_after_recognition_and_caller_rollback_leave_no_policy_residue(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        monkeypatch.setattr(
            fee_linking_service,
            "prepare_draft",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("draft fault")),
            raising=False,
        )
        with pytest.raises(RuntimeError, match="draft fault"):
            _apply(transaction)
        transaction.rollback()
        assert _counts(transaction) == (0, 0, 0, 0, 0)


def test_payment_requires_later_explicit_pay_and_preserves_existing_draft_graph(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        result = _apply(transaction)
        item_ids = [link.fee_item_id for link in result.draft.links]
        frozen_graph = (
            result.draft.draft_id,
            tuple(
                (link.id, link.obligation_line_id, link.fee_item_id) for link in result.draft.links
            ),
            result.draft.activity_id,
        )

        with pytest.raises(BusinessError) as pre_pay:
            create_pay_list_from_fee_items(
                transaction,
                fee_item_ids=item_ids,
                actor_id=REVIEWER_ID,
            )
        assert pre_pay.value.code == "PAY_LIST_CLIENT_INSTRUCTION_REQUIRED"
        assert pre_pay.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0

        instruction = record_client_instruction(
            RecordFeeObligationInstructionCommand(
                obligation_id=result.recognition.obligation.id,
                instruction=FeeClientInstruction.PAY,
                actor_id=REVIEWER_ID,
                idempotency_key="application-auto-draft:pay",
            ),
            transaction,
        )
        assert instruction.obligation.statuses.client_instruction_status.value == "PAY"
        payment = create_pay_list_from_fee_items(
            transaction,
            fee_item_ids=item_ids,
            actor_id=REVIEWER_ID,
        )
        assert payment["summary"]["pay_list_created"] is True
        assert frozen_graph == (
            result.draft.draft_id,
            tuple(
                (link.id, link.obligation_line_id, link.fee_item_id) for link in result.draft.links
            ),
            result.draft.activity_id,
        )


def test_no_pay_after_reviewed_notice_draft_remains_locked(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        result = _apply(transaction)
        with pytest.raises(BusinessError) as raised:
            record_client_instruction(
                RecordFeeObligationInstructionCommand(
                    obligation_id=result.recognition.obligation.id,
                    instruction=FeeClientInstruction.HOLD,
                    actor_id=REVIEWER_ID,
                    idempotency_key="application-auto-draft:hold",
                ),
                transaction,
            )
        assert raised.value.code == "FEE_CLIENT_INSTRUCTION_LOCKED"
        assert raised.value.status_code == 409


def test_reviewed_notice_draft_replay_observes_but_never_rewinds_later_state(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        result = _apply(transaction)
        record_client_instruction(
            RecordFeeObligationInstructionCommand(
                obligation_id=result.recognition.obligation.id,
                instruction=FeeClientInstruction.PAY,
                actor_id=REVIEWER_ID,
                idempotency_key="application-auto-draft:later-pay",
            ),
            transaction,
        )
        obligation = transaction.get(FeeObligation, result.recognition.obligation.id)
        assert obligation is not None
        obligation.payment_status = "PAID"
        obligation.official_evidence_status = "VERIFIED"
        transaction.commit()

        before = _counts(transaction)
        replay = _apply(transaction)
        transaction.refresh(obligation)
        assert replay.draft.draft_id == result.draft.draft_id
        assert replay.draft.activity_reused is True
        assert obligation.client_instruction_status == "PAY"
        assert obligation.payment_status == "PAID"
        assert obligation.official_evidence_status == "VERIFIED"
        assert _counts(transaction) == before


def test_policy_resolves_exact_global_gate_with_caller_as_of(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _seed_authority(transaction)
        commands: list[object] = []

        def resolve(command: object, received: Session) -> object:
            assert received is transaction
            commands.append(command)
            return SimpleNamespace(
                resolved_scope_key="GLOBAL",
                decision_value="APPROVED_POLICY",
                source_reference=DECISION_SOURCE,
                source_version=DECISION_VERSION,
            )

        monkeypatch.setattr(fee_linking_service, "resolve_decision_gate", resolve, raising=False)
        _apply(transaction)
        assert len(commands) == 1
        command = commands[0]
        assert command.gate_code is DecisionGateCode.FEE_APPLICATION_DRAFT
        assert command.scope_key == "GLOBAL"
        assert command.as_of is AS_OF
