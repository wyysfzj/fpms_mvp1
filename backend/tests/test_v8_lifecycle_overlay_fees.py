from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core import demo_bundle
from app.core.errors import BusinessError
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.auth.models import T_User
from app.modules.cases import lifecycle_overlay_service as overlay_service
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.models import Document
from app.modules.fees import demo_service
from app.modules.fees.models import (
    FeeDraft,
    FeeItem,
    FeeObligation,
    FeeObligationDraftItemLink,
    FeeObligationLine,
    FeeObligationPaymentEvidenceLink,
)
from app.modules.fees.obligation_service import get_fee_obligation
from app.modules.masterdata.clients.models import Client
from tests.test_demo_abc_runtime_bundle import _valid_v6_bundle
from tests.test_demo_abc_runtime_service_draft import _seed_case

CASE_ID = "case-overlay-fees"
SOURCE_ACTIVITY_ID = "activity-overlay-fees-source"
RECOGNITION_ACTIVITY_ID = "activity-overlay-fees-recognition"
OBLIGATION_ID = "obligation-overlay-fees"
LINE_ID = "line-overlay-fees"
ACTOR_ID = "actor-overlay-fees"
DOCUMENT_ID = "document-overlay-fees"
CLIENT_ID = "client-overlay-fees"
USER_ID = "user-overlay-fees"
DRAFT_ID = "draft-overlay-fees"
ITEM_ID = "item-overlay-fees"


def _identity() -> str:
    return hashlib.sha256(f"{CASE_ID}|{SOURCE_ACTIVITY_ID}|APPLICATION|1".encode()).hexdigest()


def _payload() -> str:
    return json.dumps(
        {
            "obligation_id": OBLIGATION_ID,
            "obligation": {
                "actor_id": ACTOR_ID,
                "case_id": CASE_ID,
                "currency": "CNY",
                "due_date": "2026-08-20",
                "fee_domain": "GOV",
                "lines": [
                    {
                        "difference_review_state": "MATCHED",
                        "fee_code": "APPLICATION",
                        "fee_name": "申请费",
                        "fee_year_key": 1,
                        "official_full_amount": "900.00",
                        "payable_amount": "135.00",
                        "reduction_ratio": "0.1500",
                        "source_amount": "135.00",
                        "source_date": "2026-08-01",
                    }
                ],
                "obligation_type": "PATENT_APPLICATION",
                "source_activity_id": SOURCE_ACTIVITY_ID,
                "source_document_id": DOCUMENT_ID,
                "source_status": "VERIFIED",
                "supersede_reason": None,
                "supersedes_obligation_id": None,
            },
            "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _seed(transaction: Session) -> None:
    transaction.add(Client(id=CLIENT_ID, client_code="OVERLAY-FEE", name_cn="费用视图客户"))
    transaction.flush()
    transaction.add(
        Case(
            id=CASE_ID,
            case_no="OVERLAY-FEES",
            client_id=CLIENT_ID,
            status="NOT_FILED",
            business_stage=BusinessStage.NEW_CASE.value,
            official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
            legal_status=LegalStatus.NOT_ESTABLISHED.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=2,
        )
    )
    transaction.flush()
    transaction.add_all(
        (
            CaseActivityEvent(
                id=SOURCE_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=1,
                lane=ActivityLane.LIFECYCLE.value,
                activity_type="CASE_OPENED",
                occurred_at=datetime(2026, 8, 1, 9, 0),
                effective_at=datetime(2026, 8, 1, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                new_business_stage=BusinessStage.NEW_CASE.value,
                new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                actor_id=ACTOR_ID,
                idempotency_key="overlay-fees-source",
                payload_json="{}",
                conflict_lineage_version="V1",
                conflict_code_count=0,
                conflict_codes_sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            ),
            Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"),
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligation(
            id=OBLIGATION_ID,
            case_id=CASE_ID,
            source_activity_id=SOURCE_ACTIVITY_ID,
            source_document_id=DOCUMENT_ID,
            fee_domain="GOV",
            obligation_type="PATENT_APPLICATION",
            obligation_status="RECOGNIZED",
            due_date=date(2026, 8, 20),
            currency="CNY",
            source_status="VERIFIED",
            client_instruction_status="PAY",
            draft_status="CREATED",
            payment_status="PAID",
            official_evidence_status="VERIFIED",
        )
    )
    transaction.flush()
    transaction.add_all(
        (
            FeeObligationLine(
                id=LINE_ID,
                obligation_id=OBLIGATION_ID,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                fee_code="APPLICATION",
                fee_name="申请费",
                fee_year_key=1,
                official_full_amount=Decimal("900.00"),
                reduction_ratio=Decimal("0.1500"),
                payable_amount=Decimal("135.00"),
                source_amount=Decimal("135.00"),
                source_date=date(2026, 8, 1),
                difference_review_state="MATCHED",
                current_identity_key=_identity(),
            ),
            CaseActivityEvent(
                id=RECOGNITION_ACTIVITY_ID,
                case_id=CASE_ID,
                sequence=2,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                occurred_at=datetime(2026, 8, 1, 9, 0),
                effective_at=datetime(2026, 8, 1, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.NEW_CASE.value,
                new_business_stage=BusinessStage.NEW_CASE.value,
                old_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                old_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                actor_id=ACTOR_ID,
                idempotency_key="overlay-fees-recognition",
                payload_json=_payload(),
                conflict_lineage_version="V1",
                conflict_code_count=0,
                conflict_codes_sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            ),
        )
    )
    transaction.commit()


def _canonical(payload: dict[str, object]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _fee_activity(
    *,
    activity_id: str,
    sequence: int,
    activity_type: str,
    source_activity_id: str | None,
    payload: dict[str, object],
) -> CaseActivityEvent:
    return CaseActivityEvent(
        id=activity_id,
        case_id=CASE_ID,
        sequence=sequence,
        lane=ActivityLane.FEE.value,
        activity_type=activity_type,
        source_activity_id=source_activity_id,
        occurred_at=datetime(2026, 8, 1, 9, sequence),
        effective_at=datetime(2026, 8, 1, 9, sequence),
        confirmation_status=ConfirmationStatus.CONFIRMED.value,
        old_business_stage=BusinessStage.NEW_CASE.value,
        new_business_stage=BusinessStage.NEW_CASE.value,
        old_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
        new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
        old_legal_status=LegalStatus.NOT_ESTABLISHED.value,
        new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
        actor_id=ACTOR_ID,
        idempotency_key=f"overlay-fees-{activity_id}",
        payload_json=_canonical(payload),
        conflict_lineage_version="V1",
        conflict_code_count=0,
        conflict_codes_sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    )


def _seed_full_fee_chain(transaction: Session) -> tuple[int, int]:
    transaction.add(T_User(id=USER_ID, username="overlay-fees", password_hash="test"))
    transaction.add(
        FeeDraft(
            id=DRAFT_ID,
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            draft_type="GENERIC",
            currency="CNY",
            status="OPEN",
            amount=Decimal("135.00"),
            total_gov=Decimal("135.00"),
        )
    )
    transaction.flush()
    transaction.add(
        FeeItem(
            id=ITEM_ID,
            draft_id=DRAFT_ID,
            case_id=CASE_ID,
            fee_code="APPLICATION",
            fee_name="申请费",
            fee_type="GOV",
            year_no=1,
            amount=Decimal("135.00"),
        )
    )
    transaction.flush()
    transaction.add(
        FeeObligationDraftItemLink(
            id="link-overlay-fees",
            obligation_line_id=LINE_ID,
            fee_item_id=ITEM_ID,
        )
    )
    pay_list = PayList(
        client_id=CLIENT_ID,
        status="DRAFT",
        currency="CNY",
        total_amount=Decimal("135.00"),
    )
    transaction.add(pay_list)
    transaction.flush()
    payment = GovPayment(
        pay_list_id=pay_list.id,
        case_id=CASE_ID,
        fee_item_id=ITEM_ID,
        status="RECORDED",
        currency="CNY",
        paid_amount=Decimal("135.00"),
    )
    transaction.add(payment)
    transaction.flush()
    transaction.add(
        FeeObligationPaymentEvidenceLink(
            id="payment-link-overlay-fees",
            obligation_line_id=LINE_ID,
            gov_payment_id=payment.id,
        )
    )
    transaction.add(
        PayListExportArtifact(
            id="artifact-overlay-fees",
            pay_list_id=pay_list.id,
            kind="INTERNAL_XLSX",
            status="GENERATED",
            content_sha256="a" * 64,
            managed_storage_path="managed/overlay-fees.xlsx",
            generated_by=USER_ID,
            generated_at=datetime(2026, 8, 1, 9, 6),
            idempotency_key="export-overlay-fees",
        )
    )
    instruction_id = "activity-overlay-fees-instruction"
    transaction.add_all(
        (
            _fee_activity(
                activity_id=instruction_id,
                sequence=3,
                activity_type="FEE_CLIENT_INSTRUCTION_RECORDED",
                source_activity_id=RECOGNITION_ACTIVITY_ID,
                payload={
                    "actor_id": ACTOR_ID,
                    "instruction": "PAY",
                    "obligation_id": OBLIGATION_ID,
                    "previous_instruction_status": "PENDING",
                    "schema": "FPMS_FEE_CLIENT_INSTRUCTION_RECORDED_V1",
                },
            ),
            _fee_activity(
                activity_id="activity-overlay-fees-draft",
                sequence=4,
                activity_type="FEE_DRAFT_CREATED",
                source_activity_id=instruction_id,
                payload={
                    "actor_id": ACTOR_ID,
                    "center_changes": {},
                    "draft_id": DRAFT_ID,
                    "links": [{"fee_item_id": ITEM_ID, "obligation_line_id": LINE_ID}],
                    "obligation_id": OBLIGATION_ID,
                    "schema": "FPMS_FEE_DRAFT_CREATED_V1",
                },
            ),
            _fee_activity(
                activity_id="activity-overlay-fees-pay-list",
                sequence=5,
                activity_type="PAY_LIST_CREATED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                payload={
                    "actor_id": ACTOR_ID,
                    "center_changes": {},
                    "fee_item_ids": [ITEM_ID],
                    "obligation_ids": [OBLIGATION_ID],
                    "obligation_line_ids": [LINE_ID],
                    "pay_list_id": pay_list.id,
                    "schema": "FPMS_PAY_LIST_CREATED_V1",
                },
            ),
            _fee_activity(
                activity_id="activity-overlay-fees-export",
                sequence=6,
                activity_type="PAY_LIST_INTERNAL_EXPORTED",
                source_activity_id=None,
                payload={
                    "artifact_id": "artifact-overlay-fees",
                    "content_sha256": "a" * 64,
                    "managed_storage_path": "managed/overlay-fees.xlsx",
                    "pay_list_id": pay_list.id,
                },
            ),
            _fee_activity(
                activity_id="activity-overlay-fees-payment",
                sequence=7,
                activity_type="PAYMENT_RECORDED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                payload={
                    "gov_payment_id": payment.id,
                    "obligation_id": OBLIGATION_ID,
                    "obligation_line_ids": [LINE_ID],
                    "schema": "FPMS_GOV_PAYMENT_RECORDED_V1",
                },
            ),
            _fee_activity(
                activity_id="activity-overlay-fees-official",
                sequence=8,
                activity_type="OFFICIAL_PAYMENT_EVIDENCE_VERIFIED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                payload={
                    "gov_payment_id": payment.id,
                    "invoice_no": None,
                    "obligation_id": OBLIGATION_ID,
                    "obligation_line_ids": [LINE_ID],
                    "official_receipt_no": None,
                    "schema": "FPMS_GOV_PAYMENT_OFFICIAL_EVIDENCE_VERIFIED_V1",
                    "voucher_no": None,
                },
            ),
        )
    )
    case = transaction.get(Case, CASE_ID)
    assert case is not None
    case.lifecycle_revision = 8
    transaction.commit()
    return pay_list.id, payment.id


def test_overlay_projects_recognized_fee_obligation_with_exact_money_and_statuses(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

    obligation = result.milestones[1].fee_obligations[0]
    assert obligation.obligation_id == OBLIGATION_ID
    assert obligation.statuses.client_instruction_status.value == "PAY"
    assert obligation.statuses.draft_status.value == "CREATED"
    assert obligation.statuses.pay_list_status.value == "NOT_CREATED"
    assert obligation.statuses.payment_status.value == "PAID"
    assert obligation.statuses.official_evidence_status.value == "VERIFIED"
    assert obligation.lines[0].official_full_amount == "900.00"
    assert obligation.lines[0].reduction_ratio == "0.1500"
    assert obligation.lines[0].payable_amount == "135.00"
    assert obligation.lines[0].source_amount == "135.00"


def test_overlay_projects_every_fee_activity_family_once_and_without_writes(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        pay_list_id, payment_id = _seed_full_fee_chain(transaction)
        calls: list[str] = []

        def _deep_read(obligation_id: str, session: Session):
            calls.append(obligation_id)
            return get_fee_obligation(obligation_id, session)

        monkeypatch.setattr(overlay_service, "get_fee_obligation", _deep_read)

        def _write_forbidden(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("overlay read attempted a write")

        for name in ("add", "add_all", "delete", "flush", "commit", "rollback"):
            monkeypatch.setattr(transaction, name, _write_forbidden)

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

        by_type = {milestone.activity_type: milestone for milestone in result.milestones}
        assert calls == [OBLIGATION_ID]
        assert by_type["FEE_CLIENT_INSTRUCTION_RECORDED"].fee_obligations[0].related_facts == ()
        assert [
            (fact.kind.value, fact.object_id, fact.status)
            for fact in by_type["FEE_DRAFT_CREATED"].fee_obligations[0].related_facts
        ] == [("DRAFT", DRAFT_ID, "OPEN")]
        for activity_type in ("PAY_LIST_CREATED", "PAY_LIST_INTERNAL_EXPORTED"):
            assert [
                (fact.kind.value, fact.object_id, fact.status)
                for fact in by_type[activity_type].fee_obligations[0].related_facts
            ] == [("PAY_LIST", str(pay_list_id), "DRAFT")]
        assert [
            (fact.kind.value, fact.object_id, fact.status)
            for fact in by_type["PAYMENT_RECORDED"].fee_obligations[0].related_facts
        ] == [("PAYMENT", str(payment_id), "RECORDED")]
        assert [
            (fact.kind.value, fact.object_id, fact.status)
            for fact in by_type["OFFICIAL_PAYMENT_EVIDENCE_VERIFIED"]
            .fee_obligations[0]
            .related_facts
        ] == [("OFFICIAL_EVIDENCE", str(payment_id), "VERIFIED")]
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_unknown_fee_activity_does_not_fuzzily_attach_case_fee(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        activity = transaction.get(CaseActivityEvent, RECOGNITION_ACTIVITY_ID)
        assert activity is not None
        activity.activity_type = "UNRECOGNIZED_FEE_NOTE"
        activity.payload_json = _canonical(
            {"amount": "135.00", "fee_name": "申请费", "obligation_id": OBLIGATION_ID}
        )
        transaction.commit()

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

    assert result.milestones[1].fee_obligations == ()


@pytest.mark.parametrize(
    "payload_json",
    (
        "not-json",
        '{"obligation_id":"obligation-overlay-fees","schema":"FPMS_FEE_OBLIGATION_RECOGNIZED_V1", "unexpected":true}',
        _canonical(
            {
                "obligation_id": "missing-obligation",
                "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
            }
        ),
    ),
)
def test_known_fee_activity_payload_failures_are_409(
    session_factory: sessionmaker,
    payload_json: str,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        activity = transaction.get(CaseActivityEvent, RECOGNITION_ACTIVITY_ID)
        assert activity is not None
        activity.payload_json = payload_json
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            read_lifecycle_overlay(
                case_id=CASE_ID,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

    assert raised.value.code == "LIFECYCLE_OVERLAY_FEE_CONFLICT"
    assert raised.value.status_code == 409


def test_declared_draft_links_must_equal_persisted_graph(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        _seed_full_fee_chain(transaction)
        activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-draft")
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["links"][0]["fee_item_id"] = "unrelated-item"
        activity.payload_json = _canonical(payload)
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            read_lifecycle_overlay(
                case_id=CASE_ID,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

    assert raised.value.code == "LIFECYCLE_OVERLAY_FEE_CONFLICT"
    assert raised.value.status_code == 409


def test_reviewed_notice_draft_schema_projects_with_recognition_predecessor(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        _seed_full_fee_chain(transaction)
        activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-draft")
        assert activity is not None
        activity.source_activity_id = RECOGNITION_ACTIVITY_ID
        activity.payload_json = _canonical(
            {
                "actor_id": ACTOR_ID,
                "authority": "REVIEWED_APPLICATION_FEE_NOTICE",
                "center_changes": {},
                "draft_id": DRAFT_ID,
                "links": [{"fee_item_id": ITEM_ID, "obligation_line_id": LINE_ID}],
                "obligation_id": OBLIGATION_ID,
                "schema": "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1",
            }
        )
        transaction.commit()

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

    draft_fact = next(
        milestone
        for milestone in result.milestones
        if milestone.activity_type == "FEE_DRAFT_CREATED"
    )
    assert [
        (fact.object_id, fact.status) for fact in draft_fact.fee_obligations[0].related_facts
    ] == [(DRAFT_ID, "OPEN")]


@pytest.mark.parametrize(
    ("schema", "source_activity_id", "authority"),
    (
        ("FPMS_FEE_DRAFT_CREATED_V1", RECOGNITION_ACTIVITY_ID, None),
        (
            "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1",
            "activity-overlay-fees-instruction",
            "REVIEWED_APPLICATION_FEE_NOTICE",
        ),
        (
            "FPMS_FEE_DRAFT_CREATED_FROM_REVIEWED_APPLICATION_NOTICE_V1",
            RECOGNITION_ACTIVITY_ID,
            "CLIENT_PAY_INSTRUCTION",
        ),
    ),
)
def test_draft_schema_and_predecessor_branches_cannot_be_crossed(
    session_factory: sessionmaker,
    schema: str,
    source_activity_id: str,
    authority: str | None,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        _seed_full_fee_chain(transaction)
        activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-draft")
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["schema"] = schema
        if authority is not None:
            payload["authority"] = authority
        activity.source_activity_id = source_activity_id
        activity.payload_json = _canonical(payload)
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            read_lifecycle_overlay(
                case_id=CASE_ID,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

    assert raised.value.code == "LIFECYCLE_OVERLAY_FEE_CONFLICT"
    assert raised.value.status_code == 409


def test_pay_list_projects_multiple_obligations_in_id_order(
    session_factory: sessionmaker,
) -> None:
    second_obligation_id = "obligation-overlay-fees-z"
    second_line_id = "line-overlay-fees-z"
    second_item_id = "item-overlay-fees-z"
    with session_factory() as transaction:
        _seed(transaction)
        second_line = FeeObligationLine(
            id=second_line_id,
            obligation_id=second_obligation_id,
            case_id=CASE_ID,
            source_activity_id=SOURCE_ACTIVITY_ID,
            fee_code="SECOND",
            fee_name="第二费用",
            fee_year_key=2,
            official_full_amount=Decimal("200.00"),
            reduction_ratio=Decimal("1.0000"),
            payable_amount=Decimal("200.00"),
            source_amount=Decimal("200.00"),
            source_date=date(2026, 8, 1),
            difference_review_state="MATCHED",
            current_identity_key=hashlib.sha256(
                f"{CASE_ID}|{SOURCE_ACTIVITY_ID}|SECOND|2".encode()
            ).hexdigest(),
        )
        transaction.add(
            FeeObligation(
                id=second_obligation_id,
                case_id=CASE_ID,
                source_activity_id=SOURCE_ACTIVITY_ID,
                source_document_id=DOCUMENT_ID,
                fee_domain="GOV",
                obligation_type="PATENT_APPLICATION",
                obligation_status="RECOGNIZED",
                due_date=date(2026, 8, 20),
                currency="CNY",
                source_status="VERIFIED",
                client_instruction_status="PAY",
                draft_status="CREATED",
                payment_status="PAID",
                official_evidence_status="VERIFIED",
            )
        )
        transaction.flush()
        transaction.add(second_line)
        transaction.flush()
        transaction.add(
            CaseActivityEvent(
                id="activity-overlay-fees-recognition-z",
                case_id=CASE_ID,
                sequence=3,
                lane=ActivityLane.FEE.value,
                activity_type="FEE_OBLIGATION_RECOGNIZED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                occurred_at=datetime(2026, 8, 1, 9, 0),
                effective_at=datetime(2026, 8, 1, 9, 0),
                confirmation_status=ConfirmationStatus.CONFIRMED.value,
                old_business_stage=BusinessStage.NEW_CASE.value,
                new_business_stage=BusinessStage.NEW_CASE.value,
                old_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                new_official_procedure_stage=OfficialProcedureStage.NOT_SUBMITTED.value,
                old_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                new_legal_status=LegalStatus.NOT_ESTABLISHED.value,
                actor_id=ACTOR_ID,
                idempotency_key="overlay-fees-recognition-z",
                payload_json=_canonical(
                    {
                        "obligation": {
                            "actor_id": ACTOR_ID,
                            "case_id": CASE_ID,
                            "currency": "CNY",
                            "due_date": "2026-08-20",
                            "fee_domain": "GOV",
                            "lines": [
                                {
                                    "difference_review_state": "MATCHED",
                                    "fee_code": "SECOND",
                                    "fee_name": "第二费用",
                                    "fee_year_key": 2,
                                    "official_full_amount": "200.00",
                                    "payable_amount": "200.00",
                                    "reduction_ratio": "1.0000",
                                    "source_amount": "200.00",
                                    "source_date": "2026-08-01",
                                }
                            ],
                            "obligation_type": "PATENT_APPLICATION",
                            "source_activity_id": SOURCE_ACTIVITY_ID,
                            "source_document_id": DOCUMENT_ID,
                            "source_status": "VERIFIED",
                            "supersede_reason": None,
                            "supersedes_obligation_id": None,
                        },
                        "obligation_id": second_obligation_id,
                        "schema": "FPMS_FEE_OBLIGATION_RECOGNIZED_V1",
                    }
                ),
                conflict_lineage_version="V1",
                conflict_code_count=0,
                conflict_codes_sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            )
        )
        draft = FeeDraft(
            id="draft-overlay-fees-multi",
            case_id=CASE_ID,
            client_id=CLIENT_ID,
            draft_type="GENERIC",
            currency="CNY",
            status="OPEN",
        )
        transaction.add(draft)
        transaction.flush()
        items = (
            FeeItem(
                id="item-overlay-fees-a",
                draft_id=draft.id,
                case_id=CASE_ID,
                fee_code="APPLICATION",
                fee_name="申请费",
                fee_type="GOV",
                year_no=1,
                amount=Decimal("135.00"),
            ),
            FeeItem(
                id=second_item_id,
                draft_id=draft.id,
                case_id=CASE_ID,
                fee_code="SECOND",
                fee_name="第二费用",
                fee_type="GOV",
                year_no=2,
                amount=Decimal("200.00"),
            ),
        )
        transaction.add_all(items)
        transaction.flush()
        transaction.add_all(
            (
                FeeObligationDraftItemLink(
                    id="link-overlay-fees-a",
                    obligation_line_id=LINE_ID,
                    fee_item_id=items[0].id,
                ),
                FeeObligationDraftItemLink(
                    id="link-overlay-fees-z",
                    obligation_line_id=second_line_id,
                    fee_item_id=items[1].id,
                ),
            )
        )
        pay_list = PayList(
            client_id=CLIENT_ID,
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("335.00"),
        )
        transaction.add(pay_list)
        transaction.flush()
        transaction.add_all(
            (
                GovPayment(
                    pay_list_id=pay_list.id,
                    case_id=CASE_ID,
                    fee_item_id=items[0].id,
                    status="RECORDED",
                    currency="CNY",
                    paid_amount=Decimal("135.00"),
                ),
                GovPayment(
                    pay_list_id=pay_list.id,
                    case_id=CASE_ID,
                    fee_item_id=items[1].id,
                    status="RECORDED",
                    currency="CNY",
                    paid_amount=Decimal("200.00"),
                ),
            )
        )
        transaction.flush()
        transaction.add(
            _fee_activity(
                activity_id="activity-overlay-fees-pay-list-multi",
                sequence=4,
                activity_type="PAY_LIST_CREATED",
                source_activity_id=SOURCE_ACTIVITY_ID,
                payload={
                    "actor_id": ACTOR_ID,
                    "center_changes": {},
                    "fee_item_ids": [items[0].id, items[1].id],
                    "obligation_ids": [second_obligation_id, OBLIGATION_ID],
                    "obligation_line_ids": [LINE_ID, second_line_id],
                    "pay_list_id": pay_list.id,
                    "schema": "FPMS_PAY_LIST_CREATED_V1",
                },
            )
        )
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        case.lifecycle_revision = 4
        transaction.commit()

        result = read_lifecycle_overlay(
            case_id=CASE_ID,
            after_sequence=0,
            limit=25,
            as_of_revision=None,
            transaction=transaction,
        )

    assert [item.obligation_id for item in result.milestones[-1].fee_obligations] == [
        OBLIGATION_ID,
        second_obligation_id,
    ]


@pytest.mark.parametrize(
    "corruption",
    (
        "pay_list_declared_item",
        "payment_declared_line",
        "export_artifact_identity",
        "ambiguous_persisted_relation",
        "broken_draft_predecessor",
        "cross_case_payment_graph",
    ),
)
def test_fee_activity_relation_corruption_fails_closed(
    session_factory: sessionmaker,
    corruption: str,
) -> None:
    with session_factory() as transaction:
        _seed(transaction)
        pay_list_id, payment_id = _seed_full_fee_chain(transaction)
        if corruption == "pay_list_declared_item":
            activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-pay-list")
            assert activity is not None
            payload = json.loads(activity.payload_json)
            payload["fee_item_ids"] = ["unrelated-item"]
            activity.payload_json = _canonical(payload)
        elif corruption == "payment_declared_line":
            activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-payment")
            assert activity is not None
            payload = json.loads(activity.payload_json)
            payload["obligation_line_ids"] = ["unrelated-line"]
            activity.payload_json = _canonical(payload)
        elif corruption == "export_artifact_identity":
            activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-export")
            assert activity is not None
            payload = json.loads(activity.payload_json)
            payload["content_sha256"] = "b" * 64
            activity.payload_json = _canonical(payload)
        elif corruption == "ambiguous_persisted_relation":
            extra_item = FeeItem(
                id="item-overlay-fees-ambiguous",
                draft_id=DRAFT_ID,
                case_id=CASE_ID,
                fee_code="APPLICATION",
                fee_name="申请费重复项",
                fee_type="GOV",
                year_no=1,
                amount=Decimal("135.00"),
            )
            transaction.add(extra_item)
            transaction.flush()
            transaction.add_all(
                (
                    FeeObligationDraftItemLink(
                        id="link-overlay-fees-ambiguous",
                        obligation_line_id=LINE_ID,
                        fee_item_id=extra_item.id,
                    ),
                    GovPayment(
                        pay_list_id=pay_list_id,
                        case_id=CASE_ID,
                        fee_item_id=extra_item.id,
                        status="RECORDED",
                        currency="CNY",
                        paid_amount=Decimal("135.00"),
                    ),
                )
            )
        elif corruption == "broken_draft_predecessor":
            activity = transaction.get(CaseActivityEvent, "activity-overlay-fees-draft")
            assert activity is not None
            activity.source_activity_id = RECOGNITION_ACTIVITY_ID
        else:
            other_case_id = "case-overlay-fees-other"
            transaction.add(Case(id=other_case_id, case_no="OVERLAY-FEES-OTHER"))
            transaction.flush()
            payment = transaction.get(GovPayment, payment_id)
            assert payment is not None
            payment.case_id = other_case_id
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            read_lifecycle_overlay(
                case_id=CASE_ID,
                after_sequence=0,
                limit=25,
                as_of_revision=None,
                transaction=transaction,
            )

    assert raised.value.code == "LIFECYCLE_OVERLAY_FEE_CONFLICT"
    assert raised.value.status_code == 409


def _create_adjusted_service_draft(
    client,
    auth_headers,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> tuple[str, str, str, str, str]:
    bundle, _manifest, manifest_sha = _valid_v6_bundle(tmp_path)
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    monkeypatch.setenv("FPMS_DEMO_RUN_PROFILE", "TECHNICAL_REHEARSAL")
    monkeypatch.setenv("FPMS_DEMO_BUNDLE_PATH", str(bundle))
    monkeypatch.setenv("FPMS_DEMO_EXPECTED_MANIFEST_SHA256", manifest_sha)
    monkeypatch.setenv(
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256",
        hashlib.sha256((bundle / "authority.json").read_bytes()).hexdigest(),
    )
    monkeypatch.setenv(
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION", "SYNTHETIC_TEST_ONLY"
    )
    monkeypatch.setattr(demo_bundle, "_current_demo_date", lambda: date(2026, 8, 21))

    client_id, case_id = _seed_case(session_factory)
    created = client.post(
        "/api/v1/fees/demo-service-obligations",
        json={"case_id": case_id, "idempotency_key": "overlay-service-source-1"},
        headers=auth_headers,
    )
    assert created.status_code == 201, created.text
    original_obligation_id = created.json()["obligation"]["id"]
    instruction = client.post(
        f"/api/v1/fees/obligations/{original_obligation_id}/instruction",
        json={"instruction": "PAY", "idempotency_key": "overlay-service-pay-1"},
        headers=auth_headers,
    )
    assert instruction.status_code == 200, instruction.text
    draft = client.post(
        "/api/v1/fees/drafts",
        json={
            "case_id": case_id,
            "client_id": client_id,
            "draft_type": "GENERIC",
            "currency": "CNY",
            "obligation_id": original_obligation_id,
        },
        headers=auth_headers,
    )
    assert draft.status_code == 201, draft.text
    draft_id = draft.json()["id"]
    with session_factory() as transaction:
        adjustable_item_id = transaction.scalar(
            select(FeeItem.id).where(
                FeeItem.draft_id == draft_id,
                FeeItem.fee_code == "FWSQDJ002",
            )
        )
        assert adjustable_item_id is not None

    adjusted = client.post(
        f"/api/v1/fees/drafts/{draft_id}/demo-service-adjustment",
        json={
            "item_id": adjustable_item_id,
            "expected_quantity": 1,
            "new_quantity": 2,
            "reason": "客户确认增加一份附加文件处理",
            "idempotency_key": "overlay-service-adjustment-1",
        },
        headers=auth_headers,
    )
    assert adjusted.status_code == 201, adjusted.text
    replacement_obligation_id = adjusted.json()["superseding_obligation_id"]
    return (
        case_id,
        original_obligation_id,
        replacement_obligation_id,
        draft_id,
        adjusted.json()["adjustment_activity_id"],
    )


def _overlay_obligations(result) -> tuple[object, ...]:
    return tuple(
        obligation
        for milestone in result.milestones
        for obligation in milestone.fee_obligations
    )


def test_adjusted_service_draft_reads_without_runtime_bundle(
    client,
    auth_headers,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    (
        case_id,
        original_obligation_id,
        replacement_obligation_id,
        draft_id,
        _adjustment_activity_id,
    ) = _create_adjusted_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    for key in (
        "FPMS_ENV",
        "FPMS_DEMO_SCOPE",
        "FPMS_DEMO_RUN_PROFILE",
        "FPMS_DEMO_BUNDLE_PATH",
        "FPMS_DEMO_EXPECTED_MANIFEST_SHA256",
        "FPMS_DEMO_EXPECTED_AUTHORITY_SHA256",
        "FPMS_DEMO_EXPECTED_AUTHORITY_CLASSIFICATION",
    ):
        monkeypatch.delenv(key)

    with session_factory() as transaction:
        result = read_lifecycle_overlay(
            case_id=case_id,
            after_sequence=0,
            limit=200,
            as_of_revision=None,
            transaction=transaction,
        )
    obligations = _overlay_obligations(result)
    assert {original_obligation_id, replacement_obligation_id} <= {
        obligation.obligation_id for obligation in obligations
    }
    assert any(
        fact.kind.value == "DRAFT" and fact.object_id == draft_id
        for obligation in obligations
        if obligation.obligation_id == replacement_obligation_id
        for fact in obligation.related_facts
    )
    assert all(
        fact.kind.value != "DRAFT"
        for obligation in obligations
        if obligation.obligation_id == original_obligation_id
        for fact in obligation.related_facts
    )


def test_adjusted_service_draft_preserves_pre_adjustment_revision(
    client,
    auth_headers,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    (
        case_id,
        original_obligation_id,
        replacement_obligation_id,
        draft_id,
        adjustment_activity_id,
    ) = _create_adjusted_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    with session_factory() as transaction:
        adjustment = transaction.get(CaseActivityEvent, adjustment_activity_id)
        assert adjustment is not None
        result = read_lifecycle_overlay(
            case_id=case_id,
            after_sequence=0,
            limit=200,
            as_of_revision=adjustment.sequence - 1,
            transaction=transaction,
        )

    obligations = _overlay_obligations(result)
    assert replacement_obligation_id not in {
        obligation.obligation_id for obligation in obligations
    }
    assert any(
        fact.kind.value == "DRAFT" and fact.object_id == draft_id
        for obligation in obligations
        if obligation.obligation_id == original_obligation_id
        for fact in obligation.related_facts
    )


def test_adjusted_service_draft_validation_runs_once_per_overlay_read(
    client,
    auth_headers,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
) -> None:
    case_id, *_rest = _create_adjusted_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )
    calls = 0
    original = demo_service._validated_service_adjustment_activity

    def counted(transaction, activity):
        nonlocal calls
        calls += 1
        return original(transaction, activity)

    monkeypatch.setattr(
        demo_service,
        "validate_persisted_demo_service_adjustment",
        counted,
        raising=False,
    )
    with session_factory() as transaction:
        read_lifecycle_overlay(
            case_id=case_id,
            after_sequence=0,
            limit=200,
            as_of_revision=None,
            transaction=transaction,
        )

    assert calls == 1


@pytest.mark.parametrize(
    "corruption",
    ("historical_draft_payload", "replacement_link", "adjustment_payload"),
)
def test_adjusted_service_draft_corruption_fails_closed(
    client,
    auth_headers,
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch,
    corruption: str,
) -> None:
    (
        case_id,
        original_obligation_id,
        _replacement_obligation_id,
        draft_id,
        adjustment_activity_id,
    ) = _create_adjusted_service_draft(
        client, auth_headers, session_factory, tmp_path, monkeypatch
    )

    raised: pytest.ExceptionInfo[BusinessError]
    with session_factory() as transaction:
        if corruption == "historical_draft_payload":
            activity = next(
                activity
                for activity in transaction.scalars(
                    select(CaseActivityEvent).where(
                        CaseActivityEvent.case_id == case_id,
                        CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED",
                    )
                )
                if json.loads(activity.payload_json).get("draft_id") == draft_id
            )
            payload = json.loads(activity.payload_json)
            payload["links"][0]["obligation_line_id"] = "unrelated-line"
            activity.payload_json = _canonical(payload)
        elif corruption == "replacement_link":
            item = transaction.scalar(
                select(FeeItem).where(FeeItem.draft_id == draft_id).limit(1)
            )
            assert item is not None
            original_line_id = transaction.scalar(
                select(FeeObligationLine.id).where(
                    FeeObligationLine.obligation_id == original_obligation_id,
                    FeeObligationLine.fee_code == item.fee_code,
                )
            )
            link = transaction.scalar(
                select(FeeObligationDraftItemLink).where(
                    FeeObligationDraftItemLink.fee_item_id == item.id
                )
            )
            assert original_line_id is not None and link is not None
            link.obligation_line_id = original_line_id
        else:
            activity = transaction.get(CaseActivityEvent, adjustment_activity_id)
            assert activity is not None
            payload = json.loads(activity.payload_json)
            payload["original_obligation_id"] = "unrelated-obligation"
            activity.payload_json = _canonical(payload)
        transaction.commit()

        with pytest.raises(BusinessError) as raised:
            read_lifecycle_overlay(
                case_id=case_id,
                after_sequence=0,
                limit=200,
                as_of_revision=None,
                transaction=transaction,
            )

    assert raised.value.code == "LIFECYCLE_OVERLAY_FEE_CONFLICT"
    assert raised.value.status_code == 409
