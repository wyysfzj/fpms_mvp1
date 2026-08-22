from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, fields
from datetime import timedelta
from typing import get_type_hints
from unittest.mock import patch
from uuid import uuid4

import pytest
import test_v8_future_annuity_obligation as obligation_seed
from sqlalchemy import delete, event, func, select, update
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity import service as annuity_service
from app.modules.annuity.models import AnnuityTask, GovPayment, PayList
from app.modules.auth.models import T_Role, T_RolePerm, T_UserRole
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import Document, DocumentEvidenceVersion
from app.modules.fees import obligation_service as fee_obligation_service
from app.modules.fees.models import FeeDraft, FeeItem, FeeObligation
from app.modules.fees.obligation_contracts import (
    FeeDraftAuthority,
    PrepareFeeObligationDraftCommand,
)
from app.modules.fees.obligation_service import prepare_draft
from app.modules.system import future_annuity_exception_authority_service as exception_service
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateStatus,
    RecordDecisionGateCommand,
    record_decision_gate,
)
from app.modules.system.future_annuity_exception_authority_service import (
    FutureAnnuityExceptionScope,
    PublishFutureAnnuityExceptionCommand,
    RevokeFutureAnnuityExceptionCommand,
    publish_future_annuity_exception,
    revoke_future_annuity_exception,
)
from app.modules.system.models import CustomerDecisionGate, FutureAnnuityDraftExceptionRecord

AS_OF = obligation_seed.datetime(2026, 8, 10, 12, 0, 0, 123456)
DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"


@dataclass(frozen=True)
class Ready:
    task_id: int
    case_id: str
    client_id: str
    actor_id: str
    obligation_id: str
    recognition_activity_id: str
    gate_id: str
    publication_id: str | None
    publication_hash: str | None


def _seed_ready(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    *,
    publish_exception: bool = True,
    scope_type: FutureAnnuityExceptionScope = FutureAnnuityExceptionScope.CLIENT,
) -> Ready:
    ids = {
        "CASE_ID": str(uuid4()),
        "CLIENT_ID": str(uuid4()),
        "ACTIVITY_ID": str(uuid4()),
        "DOCUMENT_ID": str(uuid4()),
        "ATTACHMENT_ID": str(uuid4()),
        "EVIDENCE_ID": str(uuid4()),
        "ACTOR_ID": str(uuid4()),
        "IDEMPOTENCY_KEY": f"future-annuity:{uuid4()}",
    }
    for name, value in ids.items():
        monkeypatch.setattr(obligation_seed, name, value)
    task_id = obligation_seed._seed(session_factory)
    with session_factory() as transaction:
        recognition = obligation_seed.recognize_future_annuity_obligation(
            obligation_seed._command(task_id), transaction
        )
        transaction.commit()

    role_id = str(uuid4())
    with session_factory() as transaction:
        transaction.add(
            T_Role(id=role_id, code=f"annuity-exception-{uuid4()}", name="年费例外管理员")
        )
        transaction.flush()
        transaction.add_all(
            [
                T_UserRole(user_id=ids["ACTOR_ID"], role_id=role_id),
                T_RolePerm(
                    id=str(uuid4()), role_id=role_id, perm_code="SystemParam.Edit"
                ),
            ]
        )
        transaction.commit()

    with session_factory() as transaction:
        gate = record_decision_gate(
            RecordDecisionGateCommand(
                gate_code=DecisionGateCode.FEE_FUTURE_ANNUITY,
                scope_key="GLOBAL",
                decision_value="APPROVED_POLICY",
                decision_status=DecisionGateStatus.CONFIRMED,
                source_reference=DECISION_SOURCE,
                source_version=DECISION_VERSION,
                confirmed_by=ids["ACTOR_ID"],
                effective_at=AS_OF - timedelta(days=1),
                idempotency_key=f"gate-{uuid4()}",
                expected_current_gate_id=None,
            ),
            transaction,
        )
        transaction.commit()

    publication_id = None
    publication_hash = None
    if publish_exception:
        with session_factory() as transaction:
            publication = publish_future_annuity_exception(
                PublishFutureAnnuityExceptionCommand(
                    scope_type=scope_type,
                    scope_id=(
                        ids["CLIENT_ID"]
                        if scope_type is FutureAnnuityExceptionScope.CLIENT
                        else ids["CASE_ID"]
                    ),
                    effective_from=AS_OF - timedelta(hours=1),
                    effective_to=AS_OF + timedelta(days=30),
                    record_version=f"exception-{uuid4()}",
                    source_reference="客户年费例外授权单",
                    source_version="2026-08-10-v1",
                    reason="限定期间允许生成内部草单",
                    confirmed_by=ids["ACTOR_ID"],
                    published_at=AS_OF - timedelta(minutes=30),
                    effective_at=AS_OF - timedelta(minutes=15),
                    idempotency_key=f"publish-{uuid4()}",
                ),
                transaction,
            )
            publication_id = publication.record_id
            publication_hash = publication.record_snapshot_hash
            transaction.commit()

    return Ready(
        task_id=task_id,
        case_id=ids["CASE_ID"],
        client_id=ids["CLIENT_ID"],
        actor_id=ids["ACTOR_ID"],
        obligation_id=recognition.fee_obligation_id,
        recognition_activity_id=recognition.activity_id,
        gate_id=gate.gate_id,
        publication_id=publication_id,
        publication_hash=publication_hash,
    )


def _apply(ready: Ready, transaction, *, as_of=AS_OF):
    return annuity_service.apply_future_annuity_auto_draft_policy(
        transaction=transaction,
        annuity_task_id=ready.task_id,
        actor_id=ready.actor_id,
        as_of=as_of,
    )


def _direct_draft_command(
    ready: Ready,
    *,
    task_id: int | None = None,
    publication_hash: str | None = None,
) -> PrepareFeeObligationDraftCommand:
    assert ready.publication_id is not None
    assert ready.publication_hash is not None
    return PrepareFeeObligationDraftCommand(
        obligation_id=ready.obligation_id,
        actor_id=ready.actor_id,
        idempotency_key=(
            "future-annuity-exception-auto-draft:"
            f"{ready.task_id if task_id is None else task_id}:{ready.publication_id}"
        ),
        authority=FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
        exception_gate_id=ready.gate_id,
        exception_gate_source_reference=DECISION_SOURCE,
        exception_gate_source_version=DECISION_VERSION,
        exception_publication_id=ready.publication_id,
        exception_publication_snapshot_hash=(
            ready.publication_hash if publication_hash is None else publication_hash
        ),
        exception_attested_at=AS_OF,
    )


def test_public_seam_is_exact_frozen_and_typed() -> None:
    result_type = annuity_service.FutureAnnuityAutoDraftPolicyResult
    assert tuple(field.name for field in fields(result_type)) == (
        "annuity_task_id",
        "fee_obligation_id",
        "exception_attestation",
        "draft",
    )
    assert list(
        inspect.signature(annuity_service.apply_future_annuity_auto_draft_policy).parameters
    ) == ["transaction", "annuity_task_id", "actor_id", "as_of"]
    assert get_type_hints(annuity_service.apply_future_annuity_auto_draft_policy)["return"] is result_type


def test_malformed_policy_input_and_enum_only_authority_fail_before_query(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        with patch.object(
            transaction,
            "get",
            side_effect=AssertionError("input validation reached a query"),
        ) as get_spy:
            with pytest.raises(annuity_service.FutureAnnuityObligationError) as malformed:
                annuity_service.apply_future_annuity_auto_draft_policy(
                    transaction=transaction,
                    annuity_task_id=1,
                    actor_id=" invalid-actor",
                    as_of=AS_OF,
                )
            assert (
                malformed.value.code
                is annuity_service.FutureAnnuityObligationErrorCode.INVALID_COMMAND
            )
            assert malformed.value.status_code == 400
            get_spy.assert_not_called()

        enum_only = PrepareFeeObligationDraftCommand(
            obligation_id=str(uuid4()),
            actor_id=str(uuid4()),
            idempotency_key="future-annuity-exception-auto-draft:1:missing",
            authority=FeeDraftAuthority.FUTURE_ANNUITY_EXCEPTION,
        )
        with patch.object(
            transaction,
            "connection",
            side_effect=AssertionError("command validation reached a connection"),
        ) as connection_spy:
            with pytest.raises(BusinessError) as missing_carrier:
                prepare_draft(enum_only, transaction)
            assert missing_carrier.value.code == "FEE_OBLIGATION_DRAFT_COMMAND_INVALID"
            assert missing_carrier.value.status_code == 400
            connection_spy.assert_not_called()


def test_exception_creates_one_pending_internal_draft_replays_and_rolls_back(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        created = _apply(ready, transaction)
        replay = _apply(ready, transaction)
        obligation = transaction.get(FeeObligation, ready.obligation_id)
        activity = transaction.get(CaseActivityEvent, created.draft.activity_id)
        assert obligation is not None and activity is not None
        assert replay.draft.draft_id == created.draft.draft_id
        assert replay.draft.activity_reused is True
        assert created.exception_attestation.gate_id == ready.gate_id
        assert created.exception_attestation.publication_id == ready.publication_id
        assert obligation.client_instruction_status == "PENDING"
        assert obligation.draft_status == "CREATED"
        assert obligation.payment_status == "UNPAID"
        assert obligation.official_evidence_status == "PENDING"
        payload = json.loads(activity.payload_json)
        assert set(payload) == {
            "actor_id",
            "authority",
            "center_changes",
            "draft_id",
            "exception_attested_at",
            "exception_gate_id",
            "exception_gate_source_reference",
            "exception_gate_source_version",
            "exception_publication_id",
            "exception_publication_snapshot_hash",
            "links",
            "obligation_id",
            "schema",
        }
        assert payload["authority"] == "FUTURE_ANNUITY_EXCEPTION"
        assert payload["exception_gate_id"] == ready.gate_id
        assert payload["exception_publication_id"] == ready.publication_id
        assert payload["exception_publication_snapshot_hash"] == ready.publication_hash
        assert payload["exception_attested_at"] == AS_OF.isoformat(timespec="microseconds")
        assert payload["center_changes"] == {}
        assert payload["links"] == [
            {
                "fee_item_id": created.draft.links[0].fee_item_id,
                "obligation_line_id": created.draft.links[0].obligation_line_id,
            }
        ]
        assert activity.source_activity_id == ready.recognition_activity_id
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == activity.id)
            )
            == 0
        )
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        assert transaction.scalar(select(func.count()).select_from(FeeItem)) == 1
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0
        transaction.rollback()

    with session_factory() as transaction:
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_case_scope_exception_creates_one_internal_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(
        session_factory,
        monkeypatch,
        scope_type=FutureAnnuityExceptionScope.CASE,
    )
    with session_factory() as transaction:
        result = _apply(ready, transaction)
        assert result.exception_attestation.scope_type is FutureAnnuityExceptionScope.CASE
        assert result.exception_attestation.scope_id == ready.case_id
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        transaction.rollback()


def test_dirty_caller_fails_before_exception_lookup(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch, publish_exception=False)
    with session_factory() as transaction:
        transaction.add(
            T_Role(id=str(uuid4()), code=f"dirty-{uuid4()}", name="未刷新的调用方变更")
        )
        with pytest.raises(annuity_service.FutureAnnuityObligationError) as dirty:
            _apply(ready, transaction)
        assert dirty.value.code is annuity_service.FutureAnnuityObligationErrorCode.TRANSACTION_DIRTY
        assert dirty.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_deep_authority_rejects_forged_publication_hash(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        command = _direct_draft_command(ready, publication_hash="b" * 64)
        with pytest.raises(BusinessError) as forged:
            prepare_draft(command, transaction)
        assert forged.value.code == "FEE_OBLIGATION_DRAFT_STORED_STATE_INVALID"
        assert forged.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_deep_authority_rejects_fake_task_key(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        command = _direct_draft_command(ready, task_id=ready.task_id + 100_000)
        with pytest.raises(BusinessError) as fake_task:
            prepare_draft(command, transaction)
        assert fake_task.value.code == "FEE_OBLIGATION_DRAFT_STORED_STATE_INVALID"
        assert fake_task.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_missing_exception_fails_without_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch, publish_exception=False)
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as missing:
            _apply(ready, transaction)
        assert missing.value.code == "FUTURE_ANNUITY_EXCEPTION_NOT_FOUND"
        assert missing.value.status_code == 404
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_expired_exception_and_corrupt_gate_fail_without_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as expired:
            _apply(ready, transaction, as_of=AS_OF + timedelta(days=31))
        assert expired.value.code == "FUTURE_ANNUITY_EXCEPTION_NOT_FOUND"
        assert expired.value.status_code == 404
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0

    with session_factory() as transaction:
        gate = transaction.get(CustomerDecisionGate, ready.gate_id)
        assert gate is not None
        gate.source_version = "wrong-customer-decision-version"
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as corrupt_gate:
            _apply(ready, transaction)
        assert corrupt_gate.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_absent_gate_fails_without_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        gate = transaction.get(CustomerDecisionGate, ready.gate_id)
        assert gate is not None
        transaction.delete(gate)
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as absent_gate:
            _apply(ready, transaction)
        assert absent_gate.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_ambiguous_exception_fails_without_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    command = PublishFutureAnnuityExceptionCommand(
        scope_type=FutureAnnuityExceptionScope.CASE,
        scope_id=ready.case_id,
        effective_from=AS_OF - timedelta(hours=1),
        effective_to=AS_OF + timedelta(days=30),
        record_version=f"ambiguous-{uuid4()}",
        source_reference="案件级重叠授权测试记录",
        source_version="2026-08-10-ambiguous",
        reason="仅用于证明损坏的重叠记录会失败关闭",
        confirmed_by=ready.actor_id,
        published_at=AS_OF - timedelta(minutes=30),
        effective_at=AS_OF - timedelta(minutes=15),
        idempotency_key=f"ambiguous-{uuid4()}",
    )
    snapshot, digest = exception_service._canonical(
        exception_service._published_payload(command)
    )
    with session_factory() as transaction:
        transaction.add(
            FutureAnnuityDraftExceptionRecord(
                id=str(uuid4()),
                record_type="PUBLISHED",
                scope_type="CASE",
                client_id=None,
                case_id=ready.case_id,
                effective_from=command.effective_from,
                effective_to=command.effective_to,
                target_publication_id=None,
                record_version=command.record_version,
                source_reference=command.source_reference,
                source_version=command.source_version,
                reason=command.reason,
                record_snapshot=snapshot,
                record_snapshot_hash=digest,
                confirmed_by=command.confirmed_by,
                published_at=command.published_at,
                effective_at=command.effective_at,
                idempotency_key=command.idempotency_key,
            )
        )
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as ambiguous:
            _apply(ready, transaction)
        assert ambiguous.value.code == "FUTURE_ANNUITY_EXCEPTION_CONFLICT"
        assert ambiguous.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_revoked_exception_before_creation_fails_without_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    assert ready.publication_id is not None
    with session_factory() as transaction:
        revoke_future_annuity_exception(
            RevokeFutureAnnuityExceptionCommand(
                target_publication_id=ready.publication_id,
                record_version=f"revoke-{uuid4()}",
                reason="草单创建前终止例外授权",
                confirmed_by=ready.actor_id,
                published_at=AS_OF,
                effective_at=AS_OF,
                idempotency_key=f"revoke-{uuid4()}",
            ),
            transaction,
        )
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as revoked:
            _apply(ready, transaction)
        assert revoked.value.code == "FUTURE_ANNUITY_EXCEPTION_NOT_FOUND"
        assert revoked.value.status_code == 404
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        transaction.execute(
            delete(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.target_publication_id
                == ready.publication_id
            )
        )
        transaction.execute(
            delete(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.id == ready.publication_id
            )
        )
        transaction.commit()


def test_corrupt_task_lineage_and_injected_fault_leave_no_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        task = transaction.get(AnnuityTask, ready.task_id)
        assert task is not None
        original_hash = task.source_evidence_content_hash
        task.source_evidence_content_hash = f"sha256:{'b' * 64}"
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(annuity_service.FutureAnnuityObligationError) as corrupt:
            _apply(ready, transaction)
        assert (
            corrupt.value.code
            is annuity_service.FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT
        )
        assert corrupt.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
    with session_factory() as transaction:
        task = transaction.get(AnnuityTask, ready.task_id)
        assert task is not None
        task.source_evidence_content_hash = original_hash
        transaction.commit()

    def fail_after_draft_flush(*_args, **_kwargs):
        raise RuntimeError("injected draft activity failure")

    monkeypatch.setattr(
        fee_obligation_service,
        "append_case_activity",
        fail_after_draft_flush,
    )
    with session_factory() as transaction:
        with pytest.raises(RuntimeError, match="injected draft activity failure"):
            _apply(ready, transaction)
        obligation = transaction.get(FeeObligation, ready.obligation_id)
        assert obligation is not None
        assert obligation.draft_status == "NOT_CREATED"
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0
        assert transaction.scalar(select(func.count()).select_from(FeeItem)) == 0
        transaction.rollback()


def test_missing_recognition_preserves_404(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        transaction.connection().exec_driver_sql("PRAGMA foreign_keys = OFF")
        transaction.execute(
            delete(CaseActivityEvent).where(
                CaseActivityEvent.id == ready.recognition_activity_id
            )
        )
        transaction.commit()
        transaction.connection().exec_driver_sql("PRAGMA foreign_keys = ON")
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(annuity_service.FutureAnnuityObligationError) as missing:
            _apply(ready, transaction)
        assert (
            missing.value.code
            is annuity_service.FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT
        )
        assert missing.value.status_code == 404
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_cross_case_document_lineage_is_409(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    other_case_id = str(uuid4())
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=other_case_id,
                case_no=f"CROSS-CASE-{uuid4()}",
                status="NOT_FILED",
            )
        )
        document = transaction.get(Document, obligation_seed.DOCUMENT_ID)
        assert document is not None
        document.case_id = other_case_id
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(annuity_service.FutureAnnuityObligationError) as cross_case:
            _apply(ready, transaction)
        assert (
            cross_case.value.code
            is annuity_service.FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT
        )
        assert cross_case.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_deep_authority_rejects_mutually_corrupted_evidence_hashes(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    corrupt_hash = "mutually-corrupt"
    with session_factory() as transaction:
        transaction.connection().exec_driver_sql("PRAGMA ignore_check_constraints = ON")
        transaction.execute(
            update(AnnuityTask)
            .where(AnnuityTask.id == ready.task_id)
            .values(source_evidence_content_hash=corrupt_hash)
        )
        transaction.execute(
            update(DocumentEvidenceVersion)
            .where(DocumentEvidenceVersion.id == obligation_seed.EVIDENCE_ID)
            .values(content_hash=corrupt_hash)
        )
        transaction.execute(
            update(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == obligation_seed.ACTIVITY_ID)
            .values(content_hash=corrupt_hash)
        )
        transaction.commit()
        transaction.connection().exec_driver_sql("PRAGMA ignore_check_constraints = OFF")
        transaction.commit()

        with pytest.raises(BusinessError) as corrupt:
            prepare_draft(_direct_draft_command(ready), transaction)
        assert corrupt.value.code == "FEE_OBLIGATION_DRAFT_STORED_STATE_INVALID"
        assert corrupt.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 0


def test_sqlite_draft_serializes_before_current_authority_reads(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    statements: list[str] = []

    def capture_statement(
        _connection,
        _cursor,
        statement: str,
        _parameters,
        _context,
        _executemany,
    ) -> None:
        statements.append(statement.strip())

    with session_factory() as transaction:
        engine = transaction.get_bind()
        event.listen(engine, "before_cursor_execute", capture_statement)
        try:
            prepare_draft(_direct_draft_command(ready), transaction)
        finally:
            event.remove(engine, "before_cursor_execute", capture_statement)
        assert statements
        assert statements[0] == "BEGIN IMMEDIATE"
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        transaction.rollback()


def test_pre_pay_draft_cannot_create_pay_list(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        _apply(ready, transaction)
        item_id = transaction.scalar(select(FeeItem.id))
        assert item_id is not None
        with pytest.raises(BusinessError) as pre_pay:
            annuity_service.create_pay_list_from_fee_items(
                transaction,
                fee_item_ids=[item_id],
                actor_id=ready.actor_id,
            )
        assert pre_pay.value.code == "PAY_LIST_CLIENT_INSTRUCTION_REQUIRED"
        assert pre_pay.value.status_code == 409
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0
        transaction.rollback()


def test_corrupt_historical_attestation_is_controlled_409(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        created = _apply(ready, transaction)
        activity = transaction.get(CaseActivityEvent, created.draft.activity_id)
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["exception_attested_at"] = "not-an-iso-datetime"
        activity.payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        transaction.commit()
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as corrupt:
            annuity_service.record_annuity_task_instruction(
                annuity_service.RecordAnnuityTaskInstructionCommand(
                    annuity_task_id=ready.task_id,
                    instruction="PAY",
                    actor_id=ready.actor_id,
                    idempotency_key=f"future-annuity-pay-{uuid4()}",
                ),
                transaction,
            )
        assert corrupt.value.code == "FEE_CLIENT_INSTRUCTION_STORED_STATE_INVALID"
        assert corrupt.value.status_code == 409
        obligation = transaction.get(FeeObligation, ready.obligation_id)
        assert obligation is not None
        assert obligation.client_instruction_status == "PENDING"


def test_historical_replay_survives_revocation_and_later_pay_reuses_draft(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    assert ready.publication_id is not None
    with session_factory() as transaction:
        original = _apply(ready, transaction)
        transaction.commit()
    with session_factory() as transaction:
        revoke_future_annuity_exception(
            RevokeFutureAnnuityExceptionCommand(
                target_publication_id=ready.publication_id,
                record_version=f"revoke-{uuid4()}",
                reason="终止例外授权",
                confirmed_by=ready.actor_id,
                published_at=AS_OF,
                effective_at=AS_OF,
                idempotency_key=f"revoke-{uuid4()}",
            ),
            transaction,
        )
        transaction.commit()


    with session_factory() as transaction:
        replay = _apply(ready, transaction)
        assert replay.draft.draft_id == original.draft.draft_id
        assert replay.draft.activity_reused is True
        with pytest.raises(annuity_service.FutureAnnuityObligationError) as changed_time:
            _apply(ready, transaction, as_of=AS_OF + timedelta(seconds=1))
        assert (
            changed_time.value.code
            is annuity_service.FutureAnnuityObligationErrorCode.LINEAGE_CONFLICT
        )
        paid = annuity_service.record_annuity_task_instruction(
            annuity_service.RecordAnnuityTaskInstructionCommand(
                annuity_task_id=ready.task_id,
                instruction="PAY",
                actor_id=ready.actor_id,
                idempotency_key=f"future-annuity-pay-{uuid4()}",
            ),
            transaction,
        )
        obligation = transaction.get(FeeObligation, ready.obligation_id)
        assert obligation is not None
        assert paid.instruction.value == "PAY"
        assert obligation.client_instruction_status == "PAY"
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.activity_type == "FEE_DRAFT_CREATED")
            )
            == 1
        )
        assert transaction.scalar(select(func.count()).select_from(PayList)) == 0
        assert transaction.scalar(select(func.count()).select_from(GovPayment)) == 0
        transaction.execute(
            delete(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.target_publication_id
                == ready.publication_id
            )
        )
        transaction.execute(
            delete(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.id == ready.publication_id
            )
        )
        transaction.commit()


@pytest.mark.parametrize("instruction", ["HOLD", "ABANDON"])
def test_exception_draft_rejects_non_pay_instruction(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    instruction: str,
) -> None:
    ready = _seed_ready(session_factory, monkeypatch)
    with session_factory() as transaction:
        _apply(ready, transaction)
        with pytest.raises(BusinessError) as rejected:
            annuity_service.record_annuity_task_instruction(
                annuity_service.RecordAnnuityTaskInstructionCommand(
                    annuity_task_id=ready.task_id,
                    instruction=instruction,
                    actor_id=ready.actor_id,
                    idempotency_key=f"future-annuity-{instruction.lower()}-{uuid4()}",
                ),
                transaction,
            )
        assert rejected.value.status_code == 409
        obligation = transaction.get(FeeObligation, ready.obligation_id)
        assert obligation is not None
        assert obligation.client_instruction_status == "PENDING"
        assert transaction.scalar(select(func.count()).select_from(FeeDraft)) == 1
        transaction.rollback()
