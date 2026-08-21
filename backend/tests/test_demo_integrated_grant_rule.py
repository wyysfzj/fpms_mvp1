from __future__ import annotations

import hashlib
import json
from datetime import datetime

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_rules import get_lifecycle_rule

CONTENT_HASH = f"sha256:{'a' * 64}"
REVIEWED_AT = datetime(2026, 8, 11, 10, 0)


def _empty_snapshot() -> str:
    return json.dumps(
        {
            "schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
            "source_document_id": "grant-document-1",
            "reviewed_evidence_version_id": "grant-evidence-1",
            "reviewed_evidence_content_hash": CONTENT_HASH,
            "lines": [],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _command() -> LifecycleEventCommand:
    snapshot = _empty_snapshot()
    evidence_refs = (
        EvidenceReference(
            case_id="case-grant-demo",
            evidence_kind="SOURCE_DOCUMENT",
            object_type="Document",
            object_id="grant-document-1",
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        ),
        EvidenceReference(
            case_id="case-grant-demo",
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id="grant-evidence-1",
            content_hash=CONTENT_HASH,
            captured_at=REVIEWED_AT,
        ),
    )
    return LifecycleEventCommand(
        case_id="case-grant-demo",
        event_type="GRANT_REGISTRATION_NOTICE_RECORDED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=datetime(2026, 8, 11, 9, 0),
        occurred_at=datetime(2026, 8, 11, 9, 0),
        evidence_refs=evidence_refs,
        actor_id="demo-operator",
        reviewer_id="demo-reviewer",
        idempotency_key="grant-registration-notice:demo-empty-fee",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={
            "schema": "FPMS_GRANT_REGISTRATION_NOTICE_RECORDED_V1",
            "case_id": "case-grant-demo",
            "grant_fee_task_id": "grant-task-1",
            "source_document_id": "grant-document-1",
            "reviewed_evidence_version_id": "grant-evidence-1",
            "reviewed_evidence_content_hash": CONTENT_HASH,
            "reviewed_at": REVIEWED_AT.isoformat(),
            "grant_fee_lines_schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
            "grant_fee_lines_snapshot": snapshot,
            "grant_fee_lines_snapshot_hash": hashlib.sha256(snapshot.encode()).hexdigest(),
            "due_date": "2026-11-23",
            "deadline_source": "IMPORTED_OFFICIAL_NOTICE",
            "deadline_confirmed_at": "2026-08-11T09:00:00",
            "predecessor_grant_fee_task_id": None,
            "supersedes_activity_id": None,
        },
    )


def _prior_projection() -> LifecycleProjection:
    return LifecycleProjection(
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
        official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        legal_status=LegalStatus.APPLICATION_PENDING,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    )


def test_exact_local_demo_accepts_hashed_empty_fee_snapshot(monkeypatch) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")

    decision = get_lifecycle_rule("GRANT_REGISTRATION_NOTICE_RECORDED")(
        _command(), _prior_projection(), object()
    )

    assert decision is not None
    assert decision.current_projection == LifecycleProjection(
        business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
        official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
        legal_status=LegalStatus.APPLICATION_PENDING,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    )


def test_non_demo_still_rejects_identical_empty_fee_snapshot(monkeypatch) -> None:
    monkeypatch.setenv("FPMS_ENV", "dev")
    monkeypatch.delenv("FPMS_DEMO_SCOPE", raising=False)

    assert (
        get_lifecycle_rule("GRANT_REGISTRATION_NOTICE_RECORDED")(
            _command(), _prior_projection(), object()
        )
        is None
    )
