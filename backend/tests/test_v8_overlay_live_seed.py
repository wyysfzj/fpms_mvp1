from __future__ import annotations

from importlib import util
from pathlib import Path
from types import ModuleType

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import ActivityLane
from app.modules.cases.lifecycle_overlay_service import read_lifecycle_overlay
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.system.decision_gate_service import DecisionGateCode
from app.modules.system.models import CustomerDecisionGate

SEED_PATH = (
    Path(__file__).resolve().parents[2]
    / "FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdV8OverlayLiveSeed.py"
)


def _seed_module() -> ModuleType:
    spec = util.spec_from_file_location("pd_v8_overlay_live_seed", SEED_PATH)
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _approve_environment(monkeypatch: pytest.MonkeyPatch, test_db_url: str) -> None:
    monkeypatch.setenv("FPMS_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    get_settings.cache_clear()


def _overlay_pages(transaction, case_id: str):
    pages = []
    after = 0
    revision = None
    while True:
        page = read_lifecycle_overlay(
            case_id=case_id,
            after_sequence=after,
            limit=200,
            as_of_revision=revision,
            transaction=transaction,
        )
        pages.append(page)
        revision = page.lifecycle_revision
        if not page.has_more:
            break
        assert page.next_cursor is not None
        after = page.next_cursor
    return tuple(pages)


def _expected_gate_identities(case_id: str) -> list[tuple[str, str]]:
    nonlegacy = [
        code
        for code in DecisionGateCode
        if code is not DecisionGateCode.LEGACY_FORM_CLASS
    ]
    return [(code.value, f"case:{case_id}") for code in nonlegacy] + [
        (DecisionGateCode.LEGACY_FORM_CLASS.value, f"form-{number:03d}")
        for number in range(1, 23)
    ]


def test_seed_is_idempotent_preserves_p1_and_projects_real_three_page_fixture(
    monkeypatch: pytest.MonkeyPatch,
    test_db_url: str,
    session_factory: sessionmaker,
) -> None:
    _approve_environment(monkeypatch, test_db_url)
    seed = _seed_module()
    with session_factory() as transaction:
        transaction.add(Case(id="CASE-PD-P1-LIVE", case_no="P1-PRESERVED", status="NOT_FILED"))
        transaction.commit()

    first = seed.seed_live_fixture(session_factory)
    second = seed.seed_live_fixture(session_factory)
    assert first == second == {
        "activityCount": 401,
        "caseId": seed.CASE_ID,
        "caseNo": seed.CASE_NO,
        "gateCount": 29,
        "namespace": seed.NAMESPACE,
    }
    assert not seed.LOCK_DIR.exists()

    with session_factory() as transaction:
        assert transaction.get(Case, "CASE-PD-P1-LIVE") is not None
        assert transaction.scalar(
            select(func.count()).select_from(Case).where(Case.id == seed.CASE_ID)
        ) == 1
        activities = tuple(
            transaction.scalars(
                select(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == seed.CASE_ID)
                .order_by(CaseActivityEvent.sequence)
            )
        )
        assert len(activities) == 401
        assert [activity.sequence for activity in activities] == list(range(1, 402))
        assert {activity.lane for activity in activities} == {
            ActivityLane.LIFECYCLE.value,
            ActivityLane.DOCUMENT.value,
            ActivityLane.FEE.value,
        }
        assert activities[0].confirmation_status == "LEGACY_UNVERIFIED"
        assert activities[1].confirmation_status == "NEEDS_REVIEW"

        pages = _overlay_pages(transaction, seed.CASE_ID)
        assert [len(page.milestones) for page in pages] == [200, 200, 1]
        assert [page.next_cursor for page in pages] == [200, 400, None]
        assert [page.lifecycle_revision for page in pages] == [401, 401, 401]
        assert [
            milestone.sequence for page in pages for milestone in page.milestones
        ] == list(range(1, 402))

        expected = _expected_gate_identities(seed.CASE_ID)
        snapshots = []
        for page in pages:
            identities = [
                (gate.gate_code.value, gate.requested_scope_key)
                for gate in page.decision_gates
            ]
            assert identities == expected
            assert len(identities) == len(set(identities)) == 29
            assert all(scope != "ALL-22" for _code, scope in identities)
            snapshots.append(
                [
                    (
                        gate.gate_code.value,
                        gate.requested_scope_key,
                        gate.resolution_status.value,
                        gate.resolved_scope_key,
                        gate.decision_value,
                        gate.unresolved_reason,
                    )
                    for gate in page.decision_gates
                ]
            )
        assert snapshots[0] == snapshots[1] == snapshots[2]

        by_identity = {
            (gate.gate_code.value, gate.requested_scope_key): gate
            for gate in pages[0].decision_gates
        }
        case_scope = f"case:{seed.CASE_ID}"
        assert by_identity[
            (DecisionGateCode.FEE_GRANT_YEAR_DRAFT.value, case_scope)
        ].unresolved_reason == "DECISION_GATE_NOT_FOUND"
        assert by_identity[
            (DecisionGateCode.FEE_FUTURE_ANNUITY.value, case_scope)
        ].unresolved_reason == "DECISION_GATE_REVOKED"
        assert by_identity[
            (DecisionGateCode.GRANT_EVIDENCE_SOURCE.value, case_scope)
        ].unresolved_reason == "DECISION_GATE_NOT_EFFECTIVE"
        assert by_identity[
            (DecisionGateCode.GRANT_MANUAL_REVIEW.value, case_scope)
        ].unresolved_reason == "DECISION_GATE_CURRENT_ROW_CORRUPT"

        legacy_code = DecisionGateCode.LEGACY_FORM_CLASS.value
        admin_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert admin_id is not None
        direct = by_identity[(legacy_code, "form-001")]
        assert direct.gate_id == seed._gate_id("FORM-001")
        assert direct.resolved_scope_key == "form-001"
        assert direct.decision_value == "CURRENT_OFFICIAL"
        assert direct.source_reference == "v8-overlay-live-direct"
        assert direct.source_version == "2026-08-10"
        assert direct.confirmed_by == admin_id
        assert direct.effective_at.isoformat() == "2026-08-01T09:00:00"
        assert by_identity[(legacy_code, "form-002")].decision_value == "HISTORICAL"
        assert by_identity[(legacy_code, "form-003")].decision_value == "INTERNAL_ONLY"
        for scope, classification in (
            ("form-004", "CURRENT_OFFICIAL"),
            ("form-005", "HISTORICAL"),
            ("form-006", "INTERNAL_ONLY"),
        ):
            fallback = by_identity[(legacy_code, scope)]
            assert fallback.requested_scope_key == scope
            assert fallback.resolved_scope_key == "ALL-22"
            assert fallback.decision_value == classification
            assert fallback.gate_id == seed._gate_id("ALL-22")
            assert fallback.source_reference == "v8-overlay-live-all-22"
            assert fallback.source_version == "2026-08-10"
            assert fallback.confirmed_by == admin_id
            assert fallback.effective_at.isoformat() == "2026-08-01T09:00:00"
        assert by_identity[(legacy_code, "form-007")].unresolved_reason == (
            "DECISION_GATE_REVOKED"
        )
        assert by_identity[(legacy_code, "form-008")].unresolved_reason == (
            "DECISION_GATE_NOT_EFFECTIVE"
        )
        assert by_identity[(legacy_code, "form-009")].unresolved_reason == (
            "DECISION_GATE_CURRENT_ROW_CORRUPT"
        )

        assert [item.code for item in pages[0].legacy_conflicts] == list(
            seed.LEGACY_CONFLICTS
        )
        assert pages[1].legacy_conflicts == pages[2].legacy_conflicts == ()
        assert [warning.code for warning in pages[0].milestones[0].warnings] == [
            "LEGACY_ACTIVITY_UNVERIFIED",
            *seed.LEGACY_CONFLICTS,
        ]
        assert [warning.code for warning in pages[0].milestones[1].warnings] == [
            "LIFECYCLE_ACTIVITY_NEEDS_REVIEW"
        ]
        reference_warnings = [
            warning
            for warning in pages[0].warnings
            if warning.kind.value == "REFERENCE_ONLY"
        ]
        assert reference_warnings
        assert all(warning.code == "DECISION_GATE_REFERENCE_ONLY" for warning in reference_warnings)
        assert all(warning.message == "该客户决策分类仅供参考，不得激活" for warning in reference_warnings)
        assert all(warning.activity_id is None for warning in reference_warnings)
        assert all(
            warning.source_object_type == "CUSTOMER_DECISION_GATE"
            and warning.source_object_id is not None
            and warning.source_object_id.endswith(
                (
                    seed._gate_id("FORM-002"),
                    seed._gate_id("FORM-003"),
                    seed._gate_id("ALL-22"),
                )
            )
            for warning in reference_warnings
        )
        assert not transaction.new and not transaction.dirty and not transaction.deleted


def test_seed_rolls_back_atomically_on_gate_failure(
    monkeypatch: pytest.MonkeyPatch,
    test_db_url: str,
    session_factory: sessionmaker,
) -> None:
    _approve_environment(monkeypatch, test_db_url)
    seed = _seed_module()

    def fail_after_activities(_transaction, _actor_id) -> None:
        raise RuntimeError("injected gate failure")

    monkeypatch.setattr(seed, "_seed_gates", fail_after_activities)
    with pytest.raises(RuntimeError, match="injected gate failure"):
        seed.seed_live_fixture(session_factory)
    assert not seed.LOCK_DIR.exists()
    with session_factory() as transaction:
        assert transaction.get(Case, seed.CASE_ID) is None
        assert transaction.scalar(
            select(func.count())
            .select_from(CustomerDecisionGate)
            .where(CustomerDecisionGate.id.like(f"{seed.GATE_ID_PREFIX}%"))
        ) == 0


def test_seed_fails_before_mutation_for_environment_and_lock_conflicts(
    monkeypatch: pytest.MonkeyPatch,
    test_db_url: str,
    session_factory: sessionmaker,
) -> None:
    seed = _seed_module()
    monkeypatch.setenv("FPMS_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="blocked for FPMS_ENV"):
        seed.seed_live_fixture(session_factory)
    assert not seed.LOCK_DIR.exists()

    _approve_environment(monkeypatch, test_db_url)
    seed.LOCK_DIR.mkdir(mode=0o700)
    try:
        with pytest.raises(RuntimeError, match="lock is already held"):
            seed.seed_live_fixture(session_factory)
    finally:
        seed.LOCK_DIR.rmdir()
    with session_factory() as transaction:
        assert transaction.get(Case, seed.CASE_ID) is None
