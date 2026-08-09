from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256
from uuid import uuid4

import pytest
from sqlalchemy import delete, event, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_activity_service import (
    append_case_activity,
    read_activity_conflict_codes,
)
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
)
from app.modules.cases.lifecycle_overlay_schemas import OverlayWarningKind
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventConflict

EMPTY = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=None,
    lifecycle_verification_status=None,
)
LEGACY = LifecycleProjection(
    business_stage=None,
    official_procedure_stage=None,
    legal_status=LegalStatus.UNKNOWN,
    lifecycle_verification_status=ConfirmationStatus.LEGACY_UNVERIFIED,
)
CONFLICTS = ("LEGACY_STATUS_UNVERIFIED", "NO_REVERSE_MAPPING_AUTHORITY")
AT = datetime(2026, 8, 10, 9, 0)


def _actor(transaction: Session) -> str:
    value = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert value is not None
    return value


def _case(transaction: Session, *, status: str = "NOT_FILED") -> Case:
    value = uuid4().hex
    case = Case(id=str(uuid4()), case_no=f"LINEAGE-{value}", status=status)
    transaction.add(case)
    transaction.flush()
    return case


def _command(case: Case, actor_id: str, *, key: str | None = None) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=case.id,
        event_type="LEGACY_IMPORT",
        lane=ActivityLane.LIFECYCLE,
        effective_at=AT,
        evidence_refs=(),
        actor_id=actor_id,
        idempotency_key=key or f"v8-legacy-lifecycle-import:{case.id}",
        confirmation_status=ConfirmationStatus.LEGACY_UNVERIFIED,
        payload={
            "case_id": case.id,
            "legacy_status": case.status,
            "reverse_mapping": "NONE",
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1",
        },
        occurred_at=AT,
    )


def _read(transaction: Session, case_id: str):
    return read_lifecycle_overlay(
        case_id=case_id,
        after_sequence=0,
        limit=25,
        as_of_revision=None,
        transaction=transaction,
    )


def _error(code: str, action) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.status_code == 409
    assert captured.value.code == code
    return captured.value


def test_append_replay_and_overlay_preserve_exact_conflict_lineage(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        command = _command(case, _actor(transaction))
        first = append_case_activity(
            command,
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        transaction.commit()

        activity = transaction.get(CaseActivityEvent, first.activity_id)
        assert activity is not None
        canonical = json.dumps(CONFLICTS, ensure_ascii=False, separators=(",", ":"))
        assert activity.conflict_lineage_version == "V1"
        assert activity.conflict_code_count == 2
        assert activity.conflict_codes_sha256 == sha256(canonical.encode()).hexdigest()
        assert tuple(
            transaction.scalars(
                select(CaseActivityEventConflict.code)
                .where(CaseActivityEventConflict.activity_id == activity.id)
                .order_by(CaseActivityEventConflict.code)
            )
        ) == CONFLICTS

        replay = append_case_activity(
            command,
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        assert replay.reused is True
        assert replay.conflict_codes == CONFLICTS
        _error(
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            lambda: append_case_activity(
                command,
                transaction,
                previous_projection=EMPTY,
                current_projection=LEGACY,
                legacy_case_status=case.status,
                conflict_codes=("LEGACY_STATUS_UNVERIFIED",),
            ),
        )

        statements: list[str] = []

        def capture(_conn, _cursor, statement, _params, _context, _many) -> None:
            statements.append(statement.lstrip().split(None, 1)[0].upper())

        event.listen(transaction.get_bind(), "before_cursor_execute", capture)
        try:
            overlay = _read(transaction, case.id)
        finally:
            event.remove(transaction.get_bind(), "before_cursor_execute", capture)

        milestone = overlay.milestones[0]
        assert [warning.kind for warning in milestone.warnings] == [
            OverlayWarningKind.UNVERIFIED,
            OverlayWarningKind.CONFLICT,
            OverlayWarningKind.CONFLICT,
        ]
        assert [warning.code for warning in milestone.warnings] == [
            "LEGACY_ACTIVITY_UNVERIFIED",
            *CONFLICTS,
        ]
        assert all(warning.activity_id == activity.id for warning in milestone.warnings)
        assert overlay.warnings[:3] == milestone.warnings
        assert len(overlay.warnings) == 32
        gate_warnings = overlay.warnings[3:]
        assert [warning.kind for warning in gate_warnings] == [
            OverlayWarningKind.CUSTOMER_DECISION_GATE
        ] * 29
        assert [warning.code for warning in gate_warnings] == [
            "DECISION_GATE_NOT_FOUND"
        ] * 29
        assert [warning.source_object_id for warning in gate_warnings] == [
            f"{gate.gate_code.value}:{gate.requested_scope_key}"
            for gate in overlay.decision_gates
        ]
        assert [item.code for item in overlay.legacy_conflicts] == list(CONFLICTS)
        assert all(item.activity_id == activity.id for item in overlay.legacy_conflicts)
        assert set(statements) == {"SELECT"}
        assert not transaction.new and not transaction.dirty and not transaction.deleted


def test_missing_or_corrupt_attestation_fails_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        command = _command(case, _actor(transaction))
        result = append_case_activity(
            command,
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        transaction.commit()

        transaction.execute(
            update(CaseActivityEvent)
            .where(CaseActivityEvent.id == result.activity_id)
            .values(conflict_codes_sha256="0" * 64)
        )
        transaction.commit()
        _error("LIFECYCLE_CONFLICT_LINEAGE_INVALID", lambda: _read(transaction, case.id))

        transaction.execute(
            update(CaseActivityEvent)
            .where(CaseActivityEvent.id == result.activity_id)
            .values(
                conflict_lineage_version=None,
                conflict_code_count=None,
                conflict_codes_sha256=None,
            )
        )
        transaction.commit()
        _error("LIFECYCLE_CONFLICT_LINEAGE_MISSING", lambda: _read(transaction, case.id))


def test_conflict_child_cannot_cross_case(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        other = _case(transaction)
        result = append_case_activity(
            _command(case, _actor(transaction)),
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        transaction.commit()

        transaction.add(
            CaseActivityEventConflict(
                case_id=other.id,
                activity_id=result.activity_id,
                code="CROSS_CASE",
            )
        )
        with pytest.raises(IntegrityError):
            transaction.flush()
        transaction.rollback()


def test_attestation_and_child_corruption_matrix_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        result = append_case_activity(
            _command(case, _actor(transaction)),
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        transaction.commit()
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None

        for values in ({"conflict_lineage_version": "V2"}, {"conflict_code_count": None}):
            for field, value in values.items():
                setattr(activity, field, value)
            with pytest.raises(IntegrityError):
                transaction.flush()
            transaction.rollback()
            activity = transaction.get(CaseActivityEvent, result.activity_id)
            assert activity is not None

        activity.conflict_lineage_version = None
        assert read_activity_conflict_codes(transaction, (activity,))[activity.id] == CONFLICTS
        assert activity in transaction.dirty
        transaction.rollback()
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None

        activity.conflict_code_count = 1
        transaction.commit()
        _error(
            "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
            lambda: read_activity_conflict_codes(transaction, (activity,)),
        )
        activity.conflict_code_count = 2
        transaction.commit()

        cached_version = activity.conflict_lineage_version
        transaction.connection().execute(
            text(
                "UPDATE t_case_activity_event SET conflict_lineage_version = NULL, "
                "conflict_code_count = NULL, conflict_codes_sha256 = NULL WHERE id = :id"
            ),
            {"id": activity.id},
        )
        assert activity.conflict_lineage_version == cached_version == "V1"
        _error(
            "LIFECYCLE_CONFLICT_LINEAGE_MISSING",
            lambda: read_activity_conflict_codes(transaction, (activity,)),
        )
        transaction.rollback()
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None

        transaction.execute(
            delete(CaseActivityEventConflict).where(
                CaseActivityEventConflict.activity_id == activity.id,
                CaseActivityEventConflict.code == CONFLICTS[0],
            )
        )
        transaction.commit()
        _error(
            "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
            lambda: read_activity_conflict_codes(transaction, (activity,)),
        )

    with session_factory() as transaction:
        case = _case(transaction)
        result = append_case_activity(
            _command(case, _actor(transaction)),
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        transaction.commit()
        activity = transaction.get(CaseActivityEvent, result.activity_id)
        assert activity is not None
        transaction.add(
            CaseActivityEventConflict(
                case_id=case.id,
                activity_id=activity.id,
                code="ZZ_EXTRA",
            )
        )
        transaction.commit()
        _error(
            "LIFECYCLE_CONFLICT_LINEAGE_INVALID",
            lambda: read_activity_conflict_codes(transaction, (activity,)),
        )

        transaction.add(
            CaseActivityEventConflict(
                case_id=case.id,
                activity_id=activity.id,
                code="X" * 129,
            )
        )
        with pytest.raises(IntegrityError):
            transaction.flush()
        transaction.rollback()
        transaction.add(
            CaseActivityEventConflict(
                case_id=case.id,
                activity_id=activity.id,
                code=CONFLICTS[0],
            )
        )
        with pytest.raises(IntegrityError):
            transaction.flush()
        transaction.rollback()


def test_needs_review_nonlegacy_conflict_stays_out_of_legacy_projection(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        case.lifecycle_revision = 1
        case.lifecycle_verification_status = ConfirmationStatus.NEEDS_REVIEW.value
        activity = CaseActivityEvent(
            id=str(uuid4()),
            case_id=case.id,
            sequence=1,
            lane=ActivityLane.LIFECYCLE.value,
            activity_type="MANUAL_REVIEW_PENDING",
            occurred_at=AT,
            effective_at=AT,
            confirmation_status=ConfirmationStatus.NEEDS_REVIEW.value,
            actor_id=_actor(transaction),
            idempotency_key=f"manual-review:{case.id}",
            payload_json="{}",
            conflict_lineage_version="V1",
            conflict_code_count=1,
            conflict_codes_sha256=sha256(b'["NON_LEGACY_CONFLICT"]').hexdigest(),
        )
        transaction.add(activity)
        transaction.add(
            CaseActivityEventConflict(
                case_id=case.id,
                activity_id=activity.id,
                code="NON_LEGACY_CONFLICT",
            )
        )
        transaction.commit()

        overlay = _read(transaction, case.id)
        assert [warning.code for warning in overlay.milestones[0].warnings] == [
            "LIFECYCLE_ACTIVITY_NEEDS_REVIEW",
            "NON_LEGACY_CONFLICT",
        ]
        assert overlay.legacy_conflicts == ()


def test_activity_warnings_and_legacy_conflicts_are_page_local(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        actor_id = _actor(transaction)
        append_case_activity(
            _command(case, actor_id),
            transaction,
            previous_projection=EMPTY,
            current_projection=LEGACY,
            legacy_case_status=case.status,
            conflict_codes=CONFLICTS,
        )
        confirmed = LifecycleProjection(
            business_stage=None,
            official_procedure_stage=None,
            legal_status=LegalStatus.UNKNOWN,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        append_case_activity(
            LifecycleEventCommand(
                case_id=case.id,
                event_type="LEGACY_REVIEW_CONFIRMED",
                lane=ActivityLane.LIFECYCLE,
                effective_at=AT,
                evidence_refs=(),
                actor_id=actor_id,
                idempotency_key=f"legacy-review:{case.id}",
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={},
                occurred_at=AT,
            ),
            transaction,
            previous_projection=LEGACY,
            current_projection=confirmed,
            legacy_case_status=case.status,
            conflict_codes=(),
        )
        transaction.commit()

        first = read_lifecycle_overlay(
            case_id=case.id,
            after_sequence=0,
            limit=1,
            as_of_revision=2,
            transaction=transaction,
        )
        second = read_lifecycle_overlay(
            case_id=case.id,
            after_sequence=1,
            limit=1,
            as_of_revision=2,
            transaction=transaction,
        )
        assert [warning.code for warning in first.milestones[0].warnings] == [
            "LEGACY_ACTIVITY_UNVERIFIED",
            *CONFLICTS,
        ]
        assert [item.code for item in first.legacy_conflicts] == list(CONFLICTS)
        assert second.milestones[0].warnings == ()
        assert second.legacy_conflicts == ()
        assert first.warnings[-29:] == second.warnings
