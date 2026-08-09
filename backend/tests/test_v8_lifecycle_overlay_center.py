from __future__ import annotations

from datetime import datetime
from inspect import Parameter, signature
from typing import Any

import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_overlay_schemas import OverlayCenterAxis
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _actor_id(transaction: Session) -> str:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    return actor_id


def _add_case(
    transaction: Session,
    value: int,
    *,
    revision: int | None,
    business_stage: str | None,
    official_stage: str | None,
    legal_status: str | None,
    verification_status: str | None,
) -> Case:
    case = Case(
        id=_id(value),
        case_no=f"OVERLAY-{value}",
        status="FILED" if revision else "NOT_FILED",
        business_stage=business_stage,
        official_procedure_stage=official_stage,
        legal_status=legal_status,
        lifecycle_verification_status=verification_status,
        lifecycle_revision=revision,
    )
    transaction.add(case)
    transaction.flush()
    return case


def _add_activity(
    transaction: Session,
    *,
    case: Case,
    sequence: int,
    lane: str,
    old_axes: tuple[str | None, str | None, str | None] = (None, None, None),
    new_axes: tuple[str | None, str | None, str | None] = (None, None, None),
    confirmation_status: str = ConfirmationStatus.CONFIRMED.value,
) -> CaseActivityEvent:
    activity = CaseActivityEvent(
        id=_id(1000 + sequence),
        case_id=case.id,
        sequence=sequence,
        lane=lane,
        activity_type=f"EVENT_{sequence}",
        source_activity_id=_id(1000 + sequence - 1) if sequence > 1 else None,
        occurred_at=datetime(2026, 8, 1, 9, sequence),
        effective_at=datetime(2026, 8, 1, 10, sequence),
        recorded_at=datetime(2026, 8, 1, 11, sequence),
        confirmation_status=confirmation_status,
        old_business_stage=old_axes[0],
        new_business_stage=new_axes[0],
        old_official_procedure_stage=old_axes[1],
        new_official_procedure_stage=new_axes[1],
        old_legal_status=old_axes[2],
        new_legal_status=new_axes[2],
        actor_id=_actor_id(transaction),
        idempotency_key=f"overlay-{case.id}-{sequence}",
        payload_json="{}",
    )
    transaction.add(activity)
    transaction.flush()
    return activity


def _seed_three_lane_history(transaction: Session, value: int = 1) -> Case:
    current_axes = (
        BusinessStage.FILING_PREPARATION.value,
        OfficialProcedureStage.NOT_SUBMITTED.value,
        LegalStatus.APPLICATION_PENDING.value,
    )
    case = _add_case(
        transaction,
        value,
        revision=3,
        business_stage=current_axes[0],
        official_stage=current_axes[1],
        legal_status=current_axes[2],
        verification_status=ConfirmationStatus.CONFIRMED.value,
    )
    opened_axes = (
        BusinessStage.NEW_CASE.value,
        OfficialProcedureStage.NOT_SUBMITTED.value,
        LegalStatus.NOT_ESTABLISHED.value,
    )
    _add_activity(
        transaction,
        case=case,
        sequence=1,
        lane=ActivityLane.LIFECYCLE.value,
        new_axes=opened_axes,
    )
    document = _add_activity(
        transaction,
        case=case,
        sequence=2,
        lane=ActivityLane.DOCUMENT.value,
        old_axes=opened_axes,
        new_axes=opened_axes,
    )
    _add_activity(
        transaction,
        case=case,
        sequence=3,
        lane=ActivityLane.LIFECYCLE.value,
        old_axes=opened_axes,
        new_axes=current_axes,
    )
    transaction.add_all(
        (
            CaseActivityEventEvidence(
                id=_id(2002),
                case_id=case.id,
                activity_id=document.id,
                evidence_kind="B_KIND",
                object_type="DOCUMENT",
                object_id=_id(3002),
                content_hash="sha256:b",
                captured_at=datetime(2026, 8, 1, 8, 2),
            ),
            CaseActivityEventEvidence(
                id=_id(2001),
                case_id=case.id,
                activity_id=document.id,
                evidence_kind="A_KIND",
                object_type="ATTACHMENT",
                object_id=_id(3001),
                content_hash="sha256:a",
                captured_at=datetime(2026, 8, 1, 8, 1),
            ),
        )
    )
    transaction.flush()
    return case


def _read(transaction: Session, case_id: str, **overrides: Any):
    query = {"after_sequence": 0, "limit": 25, "as_of_revision": None}
    query.update(overrides)
    return read_lifecycle_overlay(case_id=case_id, transaction=transaction, **query)


def test_public_seam_is_exact_and_keyword_only() -> None:
    parameters = tuple(signature(read_lifecycle_overlay).parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "case_id",
        "after_sequence",
        "limit",
        "as_of_revision",
        "transaction",
    )
    assert all(parameter.kind is Parameter.KEYWORD_ONLY for parameter in parameters)


def test_reads_current_center_mixed_lanes_and_evidence_without_writing(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction)
        transaction.commit()
        statements: list[str] = []

        def capture_sql(_conn, _cursor, statement, _params, _context, _many) -> None:
            statements.append(statement.lstrip().split(None, 1)[0].upper())

        event.listen(transaction.get_bind(), "before_cursor_execute", capture_sql)
        try:
            result = _read(transaction, case.id, limit=1)
        finally:
            event.remove(transaction.get_bind(), "before_cursor_execute", capture_sql)

        assert result.case_id == case.id
        assert result.lifecycle_revision == 3
        assert result.center_snapshot.business_stage is BusinessStage.FILING_PREPARATION
        assert (
            result.center_snapshot.official_procedure_stage is OfficialProcedureStage.NOT_SUBMITTED
        )
        assert result.center_snapshot.legal_status is LegalStatus.APPLICATION_PENDING
        assert result.center_snapshot.source_event_id == _id(1003)
        assert result.center_snapshot.effective_at == datetime(2026, 8, 1, 10, 3)
        assert result.center_snapshot.verification_status is ConfirmationStatus.CONFIRMED
        assert result.generated_at.tzinfo is None
        assert [milestone.sequence for milestone in result.milestones] == [1, 2, 3]
        assert result.milestones[1].center_changes == {}
        assert [ref.evidence_kind for ref in result.milestones[1].evidence_summary] == [
            "A_KIND",
            "B_KIND",
        ]
        assert set(result.milestones[2].center_changes) == {
            OverlayCenterAxis.BUSINESS_STAGE,
            OverlayCenterAxis.LEGAL_STATUS,
        }
        assert result.milestones[0].document_evidence == ()
        assert result.milestones[0].work_packages == ()
        assert result.milestones[0].tasks == ()
        assert result.milestones[0].fee_obligations == ()
        assert len(result.decision_gates) == 29
        assert all(
            gate.resolution_status.value == "UNRESOLVED"
            and gate.unresolved_reason == "DECISION_GATE_NOT_FOUND"
            for gate in result.decision_gates
        )
        assert result.warnings == ()
        assert result.legacy_conflicts == ()
        assert result.has_more is False
        assert result.next_cursor is None
        assert statements and set(statements) == {"SELECT"}
        assert not transaction.new
        assert not transaction.dirty
        assert not transaction.deleted


def test_reads_historical_revision_without_comparing_current_case_projection(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction, value=2)
        transaction.commit()

        result = _read(transaction, case.id, after_sequence=1, as_of_revision=2)

        assert result.lifecycle_revision == 2
        assert result.center_snapshot.business_stage is BusinessStage.NEW_CASE
        assert result.center_snapshot.legal_status is LegalStatus.NOT_ESTABLISHED
        assert [milestone.sequence for milestone in result.milestones] == [2]


def test_historical_revision_is_not_invalidated_by_later_corrupt_activity(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction, value=6)
        transaction.get(CaseActivityEvent, _id(1003)).new_legal_status = "CORRUPT"
        transaction.commit()

        historical = _read(transaction, case.id, as_of_revision=2)

        assert historical.lifecycle_revision == 2
        assert historical.center_snapshot.legal_status is LegalStatus.NOT_ESTABLISHED
        with pytest.raises(BusinessError) as caught:
            _read(transaction, case.id)
        assert caught.value.code == "LIFECYCLE_OVERLAY_STATE_CONFLICT"


def test_current_read_rejects_activity_beyond_persisted_revision(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction, value=7)
        _add_activity(
            transaction,
            case=case,
            sequence=4,
            lane=ActivityLane.FEE.value,
            old_axes=(
                BusinessStage.FILING_PREPARATION.value,
                OfficialProcedureStage.NOT_SUBMITTED.value,
                LegalStatus.APPLICATION_PENDING.value,
            ),
            new_axes=(
                BusinessStage.FILING_PREPARATION.value,
                OfficialProcedureStage.NOT_SUBMITTED.value,
                LegalStatus.APPLICATION_PENDING.value,
            ),
        )
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            _read(transaction, case.id)

        assert caught.value.code == "LIFECYCLE_OVERLAY_STATE_CONFLICT"


def test_fully_unmanaged_legacy_case_reads_as_empty_revision_zero(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _add_case(
            transaction,
            3,
            revision=None,
            business_stage=None,
            official_stage=None,
            legal_status=None,
            verification_status=None,
        )
        transaction.commit()

        result = _read(transaction, case.id)

        assert result.lifecycle_revision == 0
        assert result.center_snapshot.business_stage is None
        assert result.center_snapshot.official_procedure_stage is None
        assert result.center_snapshot.legal_status is None
        assert result.center_snapshot.effective_at is None
        assert result.center_snapshot.verification_status is None
        assert result.center_snapshot.source_event_id is None
        assert result.milestones == ()


@pytest.mark.parametrize(
    ("overrides", "status_code"),
    (
        ({"after_sequence": -1}, 400),
        ({"limit": 0}, 400),
        ({"after_sequence": 4}, 400),
        ({"as_of_revision": -1}, 400),
        ({"as_of_revision": 4}, 400),
    ),
)
def test_invalid_query_fails_closed(
    session_factory: sessionmaker,
    overrides: dict[str, int],
    status_code: int,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction, value=4)
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            _read(transaction, case.id, **overrides)

        assert caught.value.code == "LIFECYCLE_OVERLAY_QUERY_INVALID"
        assert caught.value.status_code == status_code


@pytest.mark.parametrize("corruption", ("gap", "lane_axes", "bad_enum", "case_mismatch"))
def test_corrupt_or_unreconstructable_state_fails_closed(
    session_factory: sessionmaker,
    corruption: str,
) -> None:
    with session_factory() as transaction:
        case = _seed_three_lane_history(transaction, value=5)
        if corruption == "gap":
            transaction.get(CaseActivityEvent, _id(1002)).sequence = 4
        elif corruption == "lane_axes":
            transaction.get(
                CaseActivityEvent, _id(1002)
            ).new_legal_status = LegalStatus.APPLICATION_PENDING.value
        elif corruption == "bad_enum":
            transaction.get(CaseActivityEvent, _id(1003)).new_legal_status = "CORRUPT"
        else:
            case.legal_status = LegalStatus.PATENT_IN_FORCE.value
        transaction.commit()

        with pytest.raises(BusinessError) as caught:
            _read(transaction, case.id)

        assert caught.value.code == "LIFECYCLE_OVERLAY_STATE_CONFLICT"
        assert caught.value.status_code == 409


def test_missing_case_preserves_exact_not_found_contract(session_factory: sessionmaker) -> None:
    with session_factory() as transaction, pytest.raises(BusinessError) as caught:
        _read(transaction, _id(999999))

    assert caught.value.code == "CASE_NOT_FOUND"
    assert caught.value.status_code == 404
