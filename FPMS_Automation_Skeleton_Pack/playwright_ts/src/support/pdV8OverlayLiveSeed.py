from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator

from sqlalchemy import delete, or_, select, text
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.modules.auth.models import T_User  # noqa: E402
from app.modules.cases.lifecycle_contracts import (  # noqa: E402
    ActivityLane,
    ConfirmationStatus,
    LegalStatus,
)
from app.modules.cases.models import (  # noqa: E402
    Case,
    CaseActivityEvent,
    CaseActivityEventConflict,
    CaseActivityEventEvidence,
)
from app.modules.system.decision_gate_service import DecisionGateCode  # noqa: E402
from app.modules.system.models import CustomerDecisionGate  # noqa: E402

CASE_ID = "CASE-V8-OVERLAY-LIVE"
CASE_NO = "V8-OVERLAY-LIVE"
NAMESPACE = "V8OVL-LIVE"
GATE_ID_PREFIX = f"{NAMESPACE}-GATE-"
ACTOR_ID = f"{NAMESPACE}-ACTOR"
ACTOR_USERNAME = "v8-overlay-live-actor"
ACTIVITY_COUNT = 401
LOCK_DIR = Path("/tmp/fpms_v8_sqlite.lockdir")
SAFE_FPMS_ENVS = {"dev", "development", "local", "test", "demo"}
ATTESTATION_VERSION = "V1"
LEGACY_CONFLICTS = ("LEGACY_STATUS_UNVERIFIED", "NO_REVERSE_MAPPING_AUTHORITY")


def _digest(codes: tuple[str, ...]) -> str:
    canonical = json.dumps(codes, ensure_ascii=False, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


EMPTY_CONFLICT_DIGEST = _digest(())
LEGACY_CONFLICT_DIGEST = _digest(LEGACY_CONFLICTS)


@contextmanager
def sqlite_fixture_lock() -> Iterator[None]:
    try:
        LOCK_DIR.mkdir(mode=0o700)
    except FileExistsError as error:
        raise RuntimeError(f"V8 SQLite fixture lock is already held: {LOCK_DIR}") from error
    try:
        yield
    finally:
        LOCK_DIR.rmdir()


def assert_safe_environment() -> None:
    settings = get_settings()
    environment = (settings.fpms_env or "").strip().lower()
    database_url = (settings.database_url or "").strip().lower()
    if environment not in SAFE_FPMS_ENVS:
        raise RuntimeError(
            f"V8 overlay seed is blocked for FPMS_ENV={settings.fpms_env!r}; "
            f"allowed values are {sorted(SAFE_FPMS_ENVS)}"
        )
    if not database_url.startswith("sqlite"):
        raise RuntimeError("V8 overlay seed is blocked for non-SQLite DATABASE_URL")


def _assert_sqlite_contract(transaction: Session) -> None:
    if transaction.get_bind().dialect.name != "sqlite":
        raise RuntimeError("V8 overlay seed requires SQLite")
    if transaction.scalar(text("PRAGMA foreign_keys")) != 1:
        raise RuntimeError("V8 overlay seed requires PRAGMA foreign_keys=ON")


def _activity_id(sequence: int) -> str:
    return f"{NAMESPACE}-ACT-{sequence:04d}"


def _legacy_payload() -> str:
    return json.dumps(
        {
            "case_id": CASE_ID,
            "legacy_status": "NOT_FILED",
            "reverse_mapping": "NONE",
            "schema": "FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _gate_id(label: str) -> str:
    return f"{GATE_ID_PREFIX}{label}"


def _desired_gate_identities() -> frozenset[str]:
    case_scope = f"case:{CASE_ID}"
    nonlegacy = {
        f"{code.value}|{case_scope}"
        for code in DecisionGateCode
        if code is not DecisionGateCode.LEGACY_FORM_CLASS
        and code is not DecisionGateCode.FEE_GRANT_YEAR_DRAFT
    }
    direct_forms = {"form-001", "form-002", "form-003", "form-007", "form-008", "form-009"}
    legacy = {
        f"{DecisionGateCode.LEGACY_FORM_CLASS.value}|{scope}"
        for scope in (*sorted(direct_forms), "ALL-22")
    }
    return frozenset(nonlegacy | legacy)


def _preflight_current_identity_ownership(transaction: Session) -> None:
    rows = transaction.execute(
        select(CustomerDecisionGate.id, CustomerDecisionGate.current_identity_key).where(
            CustomerDecisionGate.current_identity_key.in_(_desired_gate_identities())
        )
    ).all()
    foreign = [identity for gate_id, identity in rows if not gate_id.startswith(GATE_ID_PREFIX)]
    if foreign:
        raise RuntimeError(
            "V8 overlay seed refuses to replace non-namespaced current decision gates: "
            + ", ".join(sorted(identity for identity in foreign if identity is not None))
        )


def _clear_fixture(transaction: Session) -> None:
    activity_ids = tuple(
        transaction.scalars(
            select(CaseActivityEvent.id).where(CaseActivityEvent.case_id == CASE_ID)
        )
    )
    if activity_ids:
        transaction.execute(
            delete(CaseActivityEventConflict).where(
                CaseActivityEventConflict.activity_id.in_(activity_ids)
            )
        )
        transaction.execute(
            delete(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id.in_(activity_ids)
            )
        )
        transaction.execute(
            delete(CaseActivityEvent).where(CaseActivityEvent.id.in_(activity_ids))
        )
    transaction.execute(delete(Case).where(Case.id == CASE_ID))
    transaction.execute(
        delete(CustomerDecisionGate).where(CustomerDecisionGate.id.like(f"{GATE_ID_PREFIX}%"))
    )
    transaction.execute(
        delete(T_User).where(
            or_(T_User.id == ACTOR_ID, T_User.username == ACTOR_USERNAME)
        )
    )


def _seed_actor(transaction: Session) -> str:
    transaction.add(
        T_User(
            id=ACTOR_ID,
            username=ACTOR_USERNAME,
            display_name="V8 Overlay Live Fixture Actor",
            password_hash="fixture-not-login-capable",
            is_active=False,
        )
    )
    transaction.flush()
    return ACTOR_ID


def _seed_case_and_activities(transaction: Session, actor_id: str) -> None:
    transaction.add(
        Case(
            id=CASE_ID,
            case_no=CASE_NO,
            status="NOT_FILED",
            legal_status=LegalStatus.UNKNOWN.value,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            lifecycle_revision=ACTIVITY_COUNT,
        )
    )
    transaction.flush()
    base_time = datetime(2026, 8, 10, 8, 0)
    activities: list[CaseActivityEvent] = []
    for sequence in range(1, ACTIVITY_COUNT + 1):
        if sequence == 1:
            lane = ActivityLane.LIFECYCLE
            event_type = "LEGACY_IMPORT"
            confirmation = ConfirmationStatus.LEGACY_UNVERIFIED
            idempotency_key = f"v8-legacy-lifecycle-import:{CASE_ID}"
            payload_json = _legacy_payload()
            count = len(LEGACY_CONFLICTS)
            digest = LEGACY_CONFLICT_DIGEST
        else:
            lane = (
                ActivityLane.DOCUMENT
                if sequence % 3 == 2
                else ActivityLane.FEE
                if sequence % 3 == 0
                else ActivityLane.LIFECYCLE
            )
            event_type = f"V8_OVERLAY_{lane.value}_{sequence:04d}"
            confirmation = (
                ConfirmationStatus.NEEDS_REVIEW
                if sequence == 2
                else ConfirmationStatus.CONFIRMED
            )
            idempotency_key = f"{NAMESPACE.lower()}:{sequence:04d}"
            payload_json = "{}"
            count = 0
            digest = EMPTY_CONFLICT_DIGEST
        occurred_at = base_time.replace(minute=(sequence // 60) % 60, second=sequence % 60)
        activities.append(
            CaseActivityEvent(
                id=_activity_id(sequence),
                case_id=CASE_ID,
                sequence=sequence,
                lane=lane.value,
                activity_type=event_type,
                occurred_at=occurred_at,
                effective_at=occurred_at,
                recorded_at=occurred_at,
                confirmation_status=confirmation.value,
                old_legal_status=None if sequence == 1 else LegalStatus.UNKNOWN.value,
                new_legal_status=LegalStatus.UNKNOWN.value,
                actor_id=actor_id,
                idempotency_key=idempotency_key,
                payload_json=payload_json,
                conflict_lineage_version=ATTESTATION_VERSION,
                conflict_code_count=count,
                conflict_codes_sha256=digest,
            )
        )
    transaction.add_all(activities)
    transaction.add_all(
        CaseActivityEventConflict(
            case_id=CASE_ID,
            activity_id=_activity_id(1),
            code=code,
        )
        for code in LEGACY_CONFLICTS
    )
    transaction.flush()


def _all_22_value() -> str:
    values = {
        f"form-{number:03d}": (
            "CURRENT_OFFICIAL"
            if number % 3 == 1
            else "HISTORICAL"
            if number % 3 == 2
            else "INTERNAL_ONLY"
        )
        for number in range(1, 23)
    }
    values.update(
        {
            "form-004": "CURRENT_OFFICIAL",
            "form-005": "HISTORICAL",
            "form-006": "INTERNAL_ONLY",
        }
    )
    return json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _gate(
    *,
    label: str,
    code: DecisionGateCode,
    scope: str,
    actor_id: str,
    decision_value: str | None,
    status: str = "CONFIRMED",
    effective_at: datetime = datetime(2026, 8, 1, 9, 0),
    source: str = "v8-overlay-live-direct",
) -> CustomerDecisionGate:
    return CustomerDecisionGate(
        id=_gate_id(label),
        gate_code=code.value,
        scope_key=scope,
        decision_value=decision_value,
        decision_status=status,
        source_reference=source,
        source_version="2026-08-10",
        confirmed_by=actor_id,
        effective_at=effective_at,
        decision_snapshot="{}",
        idempotency_key=f"{NAMESPACE.lower()}-gate:{label}",
        current_identity_key=f"{code.value}|{scope}",
    )


def _seed_gates(transaction: Session, actor_id: str) -> None:
    case_scope = f"case:{CASE_ID}"
    rows = [
        _gate(
            label="APP",
            code=DecisionGateCode.FEE_APPLICATION_DRAFT,
            scope=case_scope,
            actor_id=actor_id,
            decision_value="PAY",
        ),
        _gate(
            label="ANNUITY-REVOKED",
            code=DecisionGateCode.FEE_FUTURE_ANNUITY,
            scope=case_scope,
            actor_id=actor_id,
            decision_value=None,
            status="REVOKED",
        ),
        _gate(
            label="EVIDENCE-FUTURE",
            code=DecisionGateCode.GRANT_EVIDENCE_SOURCE,
            scope=case_scope,
            actor_id=actor_id,
            decision_value="DOCUMENT",
            effective_at=datetime(2099, 1, 1),
        ),
        _gate(
            label="MANUAL-CORRUPT",
            code=DecisionGateCode.GRANT_MANUAL_REVIEW,
            scope=case_scope,
            actor_id=actor_id,
            decision_value="",
        ),
        _gate(
            label="WORKBOOK",
            code=DecisionGateCode.PAYMENT_WORKBOOK,
            scope=case_scope,
            actor_id=actor_id,
            decision_value="OFFICIAL",
        ),
        _gate(
            label="SERVICE",
            code=DecisionGateCode.SERVICE_RATE_VERSION,
            scope=case_scope,
            actor_id=actor_id,
            decision_value="V8-LIVE",
        ),
        _gate(
            label="FORM-001",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-001",
            actor_id=actor_id,
            decision_value="CURRENT_OFFICIAL",
        ),
        _gate(
            label="FORM-002",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-002",
            actor_id=actor_id,
            decision_value="HISTORICAL",
        ),
        _gate(
            label="FORM-003",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-003",
            actor_id=actor_id,
            decision_value="INTERNAL_ONLY",
        ),
        _gate(
            label="FORM-007-REVOKED",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-007",
            actor_id=actor_id,
            decision_value=None,
            status="REVOKED",
        ),
        _gate(
            label="FORM-008-FUTURE",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-008",
            actor_id=actor_id,
            decision_value="CURRENT_OFFICIAL",
            effective_at=datetime(2099, 1, 1),
        ),
        _gate(
            label="FORM-009-CORRUPT",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="form-009",
            actor_id=actor_id,
            decision_value="BROKEN",
        ),
        _gate(
            label="ALL-22",
            code=DecisionGateCode.LEGACY_FORM_CLASS,
            scope="ALL-22",
            actor_id=actor_id,
            decision_value=_all_22_value(),
            source="v8-overlay-live-all-22",
        ),
    ]
    transaction.add_all(rows)
    transaction.flush()


def seed_live_fixture(session_factory: Callable[[], Session] | None = None) -> dict[str, object]:
    assert_safe_environment()
    if session_factory is None:
        from app.db.session import SessionLocal  # noqa: PLC0415

        session_factory = SessionLocal
    with sqlite_fixture_lock():
        transaction = session_factory()
        try:
            _assert_sqlite_contract(transaction)
            _preflight_current_identity_ownership(transaction)
            _clear_fixture(transaction)
            actor_id = _seed_actor(transaction)
            _seed_case_and_activities(transaction, actor_id)
            _seed_gates(transaction, actor_id)
            transaction.commit()
            return {
                "activityCount": ACTIVITY_COUNT,
                "caseId": CASE_ID,
                "caseNo": CASE_NO,
                "gateCount": 29,
                "namespace": NAMESPACE,
            }
        except Exception:
            transaction.rollback()
            raise
        finally:
            transaction.close()


def main() -> None:
    print(json.dumps(seed_live_fixture(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
