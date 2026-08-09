from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases import lifecycle_overlay_service as overlay_service
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateReadResult,
    ResolveDecisionGateCommand,
)

AXES = (
    BusinessStage.NEW_CASE.value,
    OfficialProcedureStage.NOT_SUBMITTED.value,
    LegalStatus.NOT_ESTABLISHED.value,
)


def _add_activity(
    transaction: Session,
    *,
    case: Case,
    sequence: int,
    actor_id: str,
) -> None:
    at = datetime(2026, 8, 1) + timedelta(seconds=sequence)
    transaction.add(
        CaseActivityEvent(
            id=str(uuid4()),
            case_id=case.id,
            sequence=sequence,
            lane=ActivityLane.LIFECYCLE.value,
            activity_type=f"EVENT_{sequence}",
            source_activity_id=None,
            occurred_at=at,
            effective_at=at,
            recorded_at=at,
            confirmation_status=ConfirmationStatus.CONFIRMED.value,
            old_business_stage=None if sequence == 1 else AXES[0],
            new_business_stage=AXES[0],
            old_official_procedure_stage=None if sequence == 1 else AXES[1],
            new_official_procedure_stage=AXES[1],
            old_legal_status=None if sequence == 1 else AXES[2],
            new_legal_status=AXES[2],
            actor_id=actor_id,
            idempotency_key=f"overlay-pagination:{case.id}:{sequence}",
            payload_json="{}",
        )
    )


def _read(
    transaction: Session,
    *,
    case_id: str,
    after_sequence: int,
    as_of_revision: int | None,
):
    return overlay_service.read_lifecycle_overlay(
        case_id=case_id,
        after_sequence=after_sequence,
        limit=50,
        as_of_revision=as_of_revision,
        transaction=transaction,
    )


def _expected_gate_identities(case_id: str) -> list[tuple[DecisionGateCode, str]]:
    return [
        (code, f"case:{case_id}")
        for code in (
            DecisionGateCode.FEE_APPLICATION_DRAFT,
            DecisionGateCode.FEE_GRANT_YEAR_DRAFT,
            DecisionGateCode.FEE_FUTURE_ANNUITY,
            DecisionGateCode.GRANT_EVIDENCE_SOURCE,
            DecisionGateCode.GRANT_MANUAL_REVIEW,
            DecisionGateCode.PAYMENT_WORKBOOK,
            DecisionGateCode.SERVICE_RATE_VERSION,
        )
    ] + [(DecisionGateCode.LEGACY_FORM_CLASS, f"form-{number:03d}") for number in range(1, 23)]


def test_overlay_keyset_freezes_revision_and_keeps_complete_gate_snapshot_on_every_page(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = Case(
            id=str(uuid4()),
            case_no=f"OVERLAY-PAGINATION-{uuid4().hex}",
            status="NOT_FILED",
            business_stage=AXES[0],
            official_procedure_stage=AXES[1],
            legal_status=AXES[2],
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=121,
        )
        transaction.add(case)
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert actor_id is not None
        for sequence in range(1, 122):
            _add_activity(transaction, case=case, sequence=sequence, actor_id=actor_id)
        transaction.commit()

        timestamps = [datetime(2026, 8, 10, 12, 0, 0, number) for number in range(1, 5)]
        commands: list[ResolveDecisionGateCommand] = []

        def resolver(
            command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            assert actual is transaction
            commands.append(command)
            return DecisionGateReadResult(
                gate_id=f"gate:{command.scope_key}",
                gate_code=command.gate_code,
                requested_scope_key=command.scope_key,
                resolved_scope_key=(
                    "ALL-22" if command.scope_key == "form-001" else command.scope_key
                ),
                decision_value=(
                    "HISTORICAL" if command.scope_key == "form-001" else "CURRENT_OFFICIAL"
                ),
                source_reference="customer-answer:2026-07-14",
                source_version="v2",
                confirmed_by="customer-actor",
                effective_at=datetime(2026, 8, 1, 9, 0),
            )

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: timestamps.pop(0))
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver)

        first = _read(
            transaction,
            case_id=case.id,
            after_sequence=0,
            as_of_revision=None,
        )
        _add_activity(transaction, case=case, sequence=122, actor_id=actor_id)
        transaction.commit()
        second = _read(
            transaction,
            case_id=case.id,
            after_sequence=first.next_cursor or 0,
            as_of_revision=first.lifecycle_revision,
        )
        third = _read(
            transaction,
            case_id=case.id,
            after_sequence=second.next_cursor or 0,
            as_of_revision=first.lifecycle_revision,
        )
        empty = _read(
            transaction,
            case_id=case.id,
            after_sequence=121,
            as_of_revision=first.lifecycle_revision,
        )

        assert (
            first.lifecycle_revision == second.lifecycle_revision == third.lifecycle_revision == 121
        )
        assert [item.sequence for item in first.milestones] == list(range(1, 51))
        assert [item.sequence for item in second.milestones] == list(range(51, 101))
        assert [item.sequence for item in third.milestones] == list(range(101, 122))
        assert empty.milestones == ()
        assert (first.has_more, first.next_cursor) == (True, 50)
        assert (second.has_more, second.next_cursor) == (True, 100)
        assert (third.has_more, third.next_cursor) == (False, None)
        assert (empty.has_more, empty.next_cursor) == (False, None)
        assert [
            item.sequence for page in (first, second, third) for item in page.milestones
        ] == list(range(1, 122))
        expected = _expected_gate_identities(case.id)
        for page in (first, second, third, empty):
            assert [
                (gate.gate_code, gate.requested_scope_key) for gate in page.decision_gates
            ] == expected
            assert len(page.decision_gates) == 29
            assert page.decision_gates[7].requested_scope_key == "form-001"
            assert page.decision_gates[7].resolved_scope_key == "ALL-22"
            assert all(gate.requested_scope_key != "ALL-22" for gate in page.decision_gates)
        assert len(commands) == 116
        for index, page in enumerate((first, second, third, empty)):
            page_commands = commands[index * 29 : (index + 1) * 29]
            assert [command.as_of for command in page_commands] == [page.generated_at] * 29
            assert [(command.gate_code, command.scope_key) for command in page_commands] == expected
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted
