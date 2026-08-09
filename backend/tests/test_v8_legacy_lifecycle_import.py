from __future__ import annotations

import importlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from types import ModuleType

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.enums import CaseStatus
from app.modules.cases.lifecycle_contracts import (
    ConfirmationStatus,
    LegalStatus,
)
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence

RECORDED_AT = datetime(2026, 8, 9, 16, 0)


def _id(value: int) -> str:
    return f"00000000-0000-0000-0000-{value:012d}"


def _api() -> ModuleType:
    try:
        return importlib.import_module("scripts.backfill_v8_lifecycle")
    except ModuleNotFoundError:
        pytest.fail("legacy lifecycle importer public seam is missing")


def _actor_id(transaction: Session) -> str:
    actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
    assert actor_id is not None
    return actor_id


def _case(
    value: int,
    *,
    status: str = "NOT_FILED",
    business_stage: str | None = None,
    official_stage: str | None = None,
    legal_status: str | None = None,
    verification_status: str | None = None,
    revision: int | None = 0,
) -> Case:
    return Case(
        id=_id(value),
        case_no=f"LEGACY-LIFECYCLE-{value}",
        status=status,
        business_stage=business_stage,
        official_procedure_stage=official_stage,
        legal_status=legal_status,
        lifecycle_verification_status=verification_status,
        lifecycle_revision=revision,
    )


def _prior_activity(transaction: Session, case: Case, actor_id: str) -> None:
    case.lifecycle_revision = 1
    transaction.add(
        CaseActivityEvent(
            id=_id(9000),
            case_id=case.id,
            sequence=1,
            lane="LIFECYCLE",
            activity_type="CASE_OPENED",
            occurred_at=RECORDED_AT,
            effective_at=RECORDED_AT,
            confirmation_status="CONFIRMED",
            actor_id=actor_id,
            idempotency_key="legacy-existing-history",
            payload_json="{}",
        )
    )


def _run(
    api: ModuleType,
    transaction: Session,
    *,
    dry_run: bool,
    expected_plan_sha256: str | None = None,
    actor_id: str | None = None,
    recorded_at: datetime = RECORDED_AT,
):
    return api.import_legacy_lifecycle(
        transaction=transaction,
        actor_id=actor_id or _actor_id(transaction),
        recorded_at=recorded_at,
        dry_run=dry_run,
        expected_plan_sha256=expected_plan_sha256,
    )


def _expect_error(code: str, action) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        action()
    assert captured.value.code == code
    assert captured.value.status_code == 409
    return captured.value


def test_public_contract_is_exact_frozen_keyword_only_and_synchronous() -> None:
    api = _api()
    signature = inspect.signature(api.import_legacy_lifecycle)
    assert tuple(signature.parameters) == (
        "transaction",
        "actor_id",
        "recorded_at",
        "dry_run",
        "expected_plan_sha256",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert signature.parameters["expected_plan_sha256"].default is None
    assert not inspect.iscoroutinefunction(api.import_legacy_lifecycle)
    assert api.__all__ == (
        "LegacyLifecycleImportRowResult",
        "LegacyLifecycleImportResult",
        "import_legacy_lifecycle",
    )
    expected = {
        api.LegacyLifecycleImportRowResult: (
            "case_id",
            "legacy_status",
            "classification",
            "planned_write",
            "activity_id",
        ),
        api.LegacyLifecycleImportResult: (
            "scanned",
            "imported",
            "unchanged",
            "conflicts",
            "invalid",
            "planned_writes",
            "input_sha256",
            "plan_sha256",
            "output_sha256",
            "rows",
        ),
    }
    for result_type, names in expected.items():
        assert is_dataclass(result_type)
        assert tuple(field.name for field in fields(result_type)) == names
        assert result_type.__slots__ == names
        assert all(field.kw_only for field in fields(result_type))
    row = api.LegacyLifecycleImportRowResult(
        case_id=_id(1),
        legacy_status="GRANTED",
        classification="IMPORT",
        planned_write=True,
        activity_id=None,
    )
    with pytest.raises(FrozenInstanceError):
        row.classification = "INVALID"


def test_dry_run_classifies_without_reverse_mapping_or_writes(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        transaction.add_all(
            (
                _case(1, status="NOT_FILED"),
                _case(2, status="GRANTED"),
                _case(3, status="BROKEN"),
                _case(4, status="PENDING", business_stage="PROSECUTION_MANAGEMENT"),
            )
        )
        history = _case(5, status="OA1")
        transaction.add(history)
        transaction.flush()
        _prior_activity(transaction, history, _actor_id(transaction))
        transaction.commit()

        before_cases = tuple(
            transaction.execute(
                select(
                    Case.id,
                    Case.status,
                    Case.business_stage,
                    Case.official_procedure_stage,
                    Case.legal_status,
                    Case.lifecycle_verification_status,
                    Case.lifecycle_revision,
                ).order_by(Case.id)
            ).all()
        )
        before_activities = transaction.scalar(select(func.count()).select_from(CaseActivityEvent))
        first = _run(api, transaction, dry_run=True)
        second = _run(api, transaction, dry_run=True)

        assert first == second
        assert (
            first.scanned,
            first.imported,
            first.unchanged,
            first.conflicts,
            first.invalid,
            first.planned_writes,
        ) == (5, 2, 0, 2, 1, 2)
        assert [row.classification for row in first.rows] == [
            "IMPORT",
            "IMPORT",
            "INVALID",
            "CONFLICT",
            "CONFLICT",
        ]
        assert all(row.activity_id is None for row in first.rows)
        assert (
            tuple(
                transaction.execute(
                    select(
                        Case.id,
                        Case.status,
                        Case.business_stage,
                        Case.official_procedure_stage,
                        Case.legal_status,
                        Case.lifecycle_verification_status,
                        Case.lifecycle_revision,
                    ).order_by(Case.id)
                ).all()
            )
            == before_cases
        )
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEvent))
            == before_activities
        )


@pytest.mark.parametrize("legacy_status", tuple(status.value for status in CaseStatus))
def test_apply_imports_every_known_status_as_unknown_unverified_without_commit(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    legacy_status: str,
) -> None:
    api = _api()
    with session_factory() as transaction:
        case = _case(10, status=legacy_status)
        transaction.add(case)
        transaction.commit()
        plan = _run(api, transaction, dry_run=True)
        rollback = transaction.rollback
        monkeypatch.setattr(transaction, "commit", lambda: pytest.fail("commit called"))
        monkeypatch.setattr(transaction, "rollback", lambda: pytest.fail("rollback called"))

        result = _run(
            api,
            transaction,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )

        imported = transaction.get(Case, case.id)
        assert imported is not None
        assert (
            imported.status,
            imported.business_stage,
            imported.official_procedure_stage,
            imported.legal_status,
            imported.lifecycle_verification_status,
            imported.lifecycle_revision,
        ) == (
            legacy_status,
            None,
            None,
            LegalStatus.UNKNOWN.value,
            ConfirmationStatus.LEGACY_UNVERIFIED.value,
            1,
        )
        activity = transaction.scalar(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case.id)
        )
        assert activity is not None
        assert {
            "sequence": activity.sequence,
            "lane": activity.lane,
            "activity_type": activity.activity_type,
            "confirmation_status": activity.confirmation_status,
            "old_business_stage": activity.old_business_stage,
            "new_business_stage": activity.new_business_stage,
            "old_official_procedure_stage": activity.old_official_procedure_stage,
            "new_official_procedure_stage": activity.new_official_procedure_stage,
            "old_legal_status": activity.old_legal_status,
            "new_legal_status": activity.new_legal_status,
            "reviewer_id": activity.reviewer_id,
            "source_activity_id": activity.source_activity_id,
            "supersedes_event_id": activity.supersedes_event_id,
            "idempotency_key": activity.idempotency_key,
            "payload": json.loads(activity.payload_json),
        } == {
            "sequence": 1,
            "lane": "LIFECYCLE",
            "activity_type": "LEGACY_IMPORT",
            "confirmation_status": "LEGACY_UNVERIFIED",
            "old_business_stage": None,
            "new_business_stage": None,
            "old_official_procedure_stage": None,
            "new_official_procedure_stage": None,
            "old_legal_status": None,
            "new_legal_status": "UNKNOWN",
            "reviewer_id": None,
            "source_activity_id": None,
            "supersedes_event_id": None,
            "idempotency_key": f"v8-legacy-lifecycle-import:{case.id}",
            "payload": {
                "case_id": case.id,
                "legacy_status": legacy_status,
                "reverse_mapping": "NONE",
                "schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1",
            },
        }
        assert (result.imported, result.planned_writes) == (1, 1)
        assert result.rows[0].activity_id == activity.id
        monkeypatch.setattr(transaction, "rollback", rollback)
        transaction.rollback()


def test_exact_existing_import_is_unchanged_and_idempotent(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        transaction.add(_case(20, status="GRANTED"))
        transaction.commit()
        first_plan = _run(api, transaction, dry_run=True)
        first = _run(
            api,
            transaction,
            dry_run=False,
            expected_plan_sha256=first_plan.plan_sha256,
        )
        transaction.commit()
        second_plan = _run(api, transaction, dry_run=True)
        second = _run(
            api,
            transaction,
            dry_run=False,
            expected_plan_sha256=second_plan.plan_sha256,
        )

        assert (first.imported, second.unchanged, second.planned_writes) == (1, 1, 0)
        assert first.rows[0].activity_id == second.rows[0].activity_id
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 1
        case = transaction.get(Case, _id(20))
        assert case is not None
        assert (case.status, case.legal_status, case.lifecycle_verification_status) == (
            "GRANTED",
            "UNKNOWN",
            "LEGACY_UNVERIFIED",
        )


def test_existing_import_with_evidence_is_a_conflict(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        transaction.add(_case(25, status="GRANTED"))
        transaction.commit()
        plan = _run(api, transaction, dry_run=True)
        imported = _run(
            api,
            transaction,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )
        activity_id = imported.rows[0].activity_id
        assert activity_id is not None
        transaction.add(
            CaseActivityEventEvidence(
                id=_id(9025),
                case_id=_id(25),
                activity_id=activity_id,
                evidence_kind="DOCUMENT",
                object_type="DocumentEvidenceVersion",
                object_id=_id(8025),
                content_hash="sha256:" + "a" * 64,
                captured_at=RECORDED_AT,
            )
        )
        transaction.commit()

        report = _run(api, transaction, dry_run=True)

        assert (report.conflicts, report.unchanged, report.planned_writes) == (1, 0, 0)
        assert report.rows[0].classification == "CONFLICT"


def test_apply_requires_exact_current_plan_and_rolls_back_nested_work(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        case = _case(30, status="PENDING")
        transaction.add(case)
        transaction.commit()
        plan = _run(api, transaction, dry_run=True)
        case.status = "OA1"
        transaction.commit()

        _expect_error(
            "LEGACY_LIFECYCLE_IMPORT_PLAN_CONFLICT",
            lambda: _run(
                api,
                transaction,
                dry_run=False,
                expected_plan_sha256=plan.plan_sha256,
            ),
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        stored = transaction.get(Case, case.id)
        assert stored is not None and stored.legal_status is None


def test_caller_rollback_removes_imported_projection_and_activity(
    session_factory: sessionmaker[Session],
) -> None:
    api = _api()
    with session_factory() as transaction:
        case = _case(40, status="REJECTED")
        transaction.add(case)
        transaction.commit()
        plan = _run(api, transaction, dry_run=True)
        _run(
            api,
            transaction,
            dry_run=False,
            expected_plan_sha256=plan.plan_sha256,
        )
        transaction.rollback()

        stored = transaction.get(Case, case.id)
        assert stored is not None
        assert (
            stored.status,
            stored.business_stage,
            stored.official_procedure_stage,
            stored.legal_status,
            stored.lifecycle_verification_status,
            stored.lifecycle_revision,
        ) == ("REJECTED", None, None, None, None, 0)
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0


@pytest.mark.parametrize(
    ("actor_id", "recorded_at"),
    (
        ("missing-actor", RECORDED_AT),
        (_id(1), RECORDED_AT.replace(tzinfo=UTC)),
    ),
)
def test_invalid_actor_or_recorded_time_fails_closed(
    session_factory: sessionmaker[Session],
    actor_id: str,
    recorded_at: datetime,
) -> None:
    api = _api()
    with session_factory() as transaction:
        transaction.add(_case(50))
        transaction.commit()
        if actor_id == _id(1):
            actor_id = _actor_id(transaction)

        _expect_error(
            "LEGACY_LIFECYCLE_IMPORT_CONFLICT",
            lambda: _run(
                api,
                transaction,
                dry_run=True,
                actor_id=actor_id,
                recorded_at=recorded_at,
            ),
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
