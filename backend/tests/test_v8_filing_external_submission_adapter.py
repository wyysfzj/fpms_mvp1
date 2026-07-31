from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_workflow_service import (
    FinalizeExternalSubmissionCommand,
    finalize_external_submission,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)

BASE = "/api/v1/official-work-packages"
SUBMITTED_AT = datetime(2026, 7, 21, 14, 30)
CREATOR_ID = "filing-evidence-creator"
REVIEWER_ID = "filing-evidence-reviewer"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _seed_filing_evidence(
    session_factory: sessionmaker[Session],
    *,
    marker: str,
) -> dict[str, str]:
    case_id = str(uuid4())
    package_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    version_id = str(uuid4())
    lineage_key = f"filing-{marker}"
    content_hash = f"sha256:{hashlib.sha256(marker.encode()).hexdigest()}"
    reviewed_at = datetime(2026, 7, 20, 9, 15)

    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"V8-FILING-EXTERNAL-{marker}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="递交外部操作适配测试案件",
                status="NOT_FILED",
                business_stage="FILING_PREPARATION",
                official_procedure_stage="NOT_SUBMITTED",
                legal_status="NOT_ESTABLISHED",
                lifecycle_revision=0,
                lifecycle_verification_status="CONFIRMED",
                recv_date=date(2026, 7, 1),
                no_power=True,
            )
        )
        transaction.add(
            Document(
                id=document_id,
                case_id=case_id,
                doc_type="OFFICIAL_OUT",
                direction="OUT",
                title="最终递交证据",
            )
        )
        transaction.flush()
        transaction.add(
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name=f"{marker}.xml",
                file_path=f"/evidence/{marker}.xml",
                content_hash=content_hash,
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=version_id,
                case_id=case_id,
                document_id=document_id,
                attachment_id=attachment_id,
                lineage_key=lineage_key,
                role="SUBMITTED_XML",
                version_number=1,
                state="FINAL",
                creator_id=CREATOR_ID,
                review_state="APPROVED",
                reviewer_id=REVIEWER_ID,
                reviewed_at=reviewed_at,
                final_submitted_at=None,
                content_hash=content_hash,
                current_identity_key=f"{case_id}|{lineage_key}",
            )
        )
        transaction.add(
            OfficialWorkPackage(
                id=package_id,
                case_id=case_id,
                package_kind="FILING_PREP",
                resolve_key=f"FILING_PREP:{case_id}",
            )
        )
        transaction.flush()
        transaction.add(
            OfficialWorkPackageManifest(
                id=str(uuid4()),
                package_id=package_id,
                attachment_id=attachment_id,
                evidence_version_id=version_id,
                content_hash=content_hash,
                present=True,
            )
        )
        transaction.commit()

    return {
        "case_id": case_id,
        "package_id": package_id,
        "version_id": version_id,
        "lineage_key": lineage_key,
        "content_hash": content_hash,
        "reviewed_at": reviewed_at.isoformat(),
    }


def _activity(
    transaction: Session,
    *,
    case_id: str,
    activity_type: str,
) -> CaseActivityEvent:
    activity = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.activity_type == activity_type,
        )
    )
    assert activity is not None
    return activity


def test_api_external_submission_uses_exact_seams_actor_keys_and_evidence(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.modules.official_workflows.service as service

    seeded = _seed_filing_evidence(session_factory, marker="exact")
    calls: list[tuple[str, object]] = []
    original_resolve = service.resolve_filing_final_evidence
    original_finalize = service.finalize_external_submission
    original_apply = service.apply_lifecycle_event

    def resolve(package_id: str, transaction: Session) -> object:
        calls.append(("resolve", package_id))
        return original_resolve(package_id, transaction)

    def finalize(command: object, transaction: Session) -> object:
        calls.append(("finalize", command))
        return original_finalize(command, transaction)

    def apply(command: object, transaction: Session) -> object:
        calls.append(("apply", command))
        return original_apply(command, transaction)

    monkeypatch.setattr(service, "resolve_filing_final_evidence", resolve)
    monkeypatch.setattr(service, "finalize_external_submission", finalize)
    monkeypatch.setattr(service, "apply_lifecycle_event", apply)

    response = client.post(
        f"{BASE}/{seeded['package_id']}/filing-preparation/external-operations",
        headers=auth_headers,
        json={
            "operation_code": "  external_submission_recorded  ",
            "occurred_at": SUBMITTED_AT.isoformat(),
            "note": "已在官方系统完成人工递交",
        },
    )

    assert response.status_code == 200, response.text
    assert [name for name, _value in calls] == ["resolve", "finalize", "resolve", "apply"]
    assert calls[0][1] == calls[2][1] == seeded["package_id"]

    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        case = transaction.get(Case, seeded["case_id"])
        version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
        assert actor_id is not None
        assert case is not None
        assert version is not None
        assert version.final_submitted_at == SUBMITTED_AT
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
        ) == (
            "WAITING_RECEIPT",
            "WAITING_EXTERNAL_RECEIPT",
            "SUBMITTED_WAITING_RECEIPT",
            "NOT_ESTABLISHED",
            2,
        )

        document_activity = _activity(
            transaction,
            case_id=seeded["case_id"],
            activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
        )
        lifecycle_activity = _activity(
            transaction,
            case_id=seeded["case_id"],
            activity_type="FILING_EXTERNAL_SUBMISSION_RECORDED",
        )
        adapter_key = (
            f"filing-external:{seeded['package_id']}:{SUBMITTED_AT.isoformat()}"
        )
        assert document_activity.actor_id == lifecycle_activity.actor_id == actor_id
        assert document_activity.idempotency_key == f"document-external-submission:{adapter_key}"
        assert lifecycle_activity.idempotency_key == (
            f"filing-external-lifecycle:{seeded['package_id']}:{SUBMITTED_AT.isoformat()}"
        )
        assert document_activity.effective_at == document_activity.occurred_at == SUBMITTED_AT
        assert lifecycle_activity.effective_at == lifecycle_activity.occurred_at == SUBMITTED_AT

        expected_payload = {
            "evidence_version_id": seeded["version_id"],
            "lineage_key": seeded["lineage_key"],
            "role": "SUBMITTED_XML",
            "submitted_at": SUBMITTED_AT.isoformat(),
        }
        assert document_activity.payload_json == _canonical_json(expected_payload)
        document_evidence = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == document_activity.id
            )
        ).all()
        assert len(document_evidence) == 1
        assert (
            document_evidence[0].case_id,
            document_evidence[0].evidence_kind,
            document_evidence[0].object_type,
            document_evidence[0].object_id,
            document_evidence[0].content_hash,
            document_evidence[0].captured_at,
        ) == (
            seeded["case_id"],
            "DOCUMENT_EVIDENCE_VERSION",
            "DocumentEvidenceVersion",
            seeded["version_id"],
            seeded["content_hash"],
            SUBMITTED_AT,
        )
        snapshot = {
            "activity_id": document_activity.id,
            "activity_type": "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            "actor_id": actor_id,
            "case_id": seeded["case_id"],
            "confirmation_status": "CONFIRMED",
            "effective_at": SUBMITTED_AT.isoformat(),
            "evidence": [
                {
                    "captured_at": SUBMITTED_AT.isoformat(),
                    "content_hash": seeded["content_hash"],
                    "evidence_kind": "DOCUMENT_EVIDENCE_VERSION",
                    "object_id": seeded["version_id"],
                    "object_type": "DocumentEvidenceVersion",
                }
            ],
            "idempotency_key": document_activity.idempotency_key,
            "lane": "DOCUMENT",
            "occurred_at": SUBMITTED_AT.isoformat(),
            "payload": expected_payload,
            "reviewer_id": REVIEWER_ID,
        }
        submission_activity_hash = (
            "sha256:" + hashlib.sha256(_canonical_json(snapshot).encode()).hexdigest()
        )
        lifecycle_evidence = transaction.scalars(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == lifecycle_activity.id)
            .order_by(CaseActivityEventEvidence.evidence_kind)
        ).all()
        assert [
            (
                evidence.case_id,
                evidence.evidence_kind,
                evidence.object_type,
                evidence.object_id,
                evidence.content_hash,
                evidence.captured_at,
            )
            for evidence in lifecycle_evidence
        ] == [
            (
                seeded["case_id"],
                "FINAL_SUBMISSION_VERSION",
                "DocumentEvidenceVersion",
                seeded["version_id"],
                seeded["content_hash"],
                datetime.fromisoformat(seeded["reviewed_at"]),
            ),
            (
                seeded["case_id"],
                "MANUAL_EXTERNAL_SUBMISSION_RECORD",
                "CaseActivityEvent",
                document_activity.id,
                submission_activity_hash,
                SUBMITTED_AT,
            ),
        ]

        checklist = transaction.scalar(
            select(OfficialWorkPackageChecklist).where(
                OfficialWorkPackageChecklist.package_id == seeded["package_id"],
                OfficialWorkPackageChecklist.item_code == "EXTERNAL_SUBMISSION_RECORDED",
            )
        )
        assert checklist is not None
        assert checklist.status == "DONE"
        assert checklist.evidence_note == (
            f"occurred_at={SUBMITTED_AT.isoformat()}; note=已在官方系统完成人工递交"
        )


def test_exact_replay_reuses_events_and_changed_actor_fails_closed(
    session_factory: sessionmaker[Session],
) -> None:
    from app.modules.official_workflows.service import (
        record_filing_preparation_external_operation,
    )

    seeded = _seed_filing_evidence(session_factory, marker="replay")
    with session_factory() as transaction:
        commit_count = 0
        original_commit = transaction.commit

        def counted_commit() -> None:
            nonlocal commit_count
            commit_count += 1
            original_commit()

        transaction.commit = counted_commit
        first = record_filing_preparation_external_operation(
            transaction,
            package_id=seeded["package_id"],
            operation_code="EXTERNAL_SUBMISSION_RECORDED",
            occurred_at=SUBMITTED_AT,
            actor_id="server-actor",
        )
        replay = record_filing_preparation_external_operation(
            transaction,
            package_id=seeded["package_id"],
            operation_code="external_submission_recorded",
            occurred_at=SUBMITTED_AT,
            actor_id="server-actor",
        )

        assert commit_count == 2
        assert replay.id == first.id

        with pytest.raises(BusinessError) as exc_info:
            record_filing_preparation_external_operation(
                transaction,
                package_id=seeded["package_id"],
                operation_code="EXTERNAL_SUBMISSION_RECORDED",
                occurred_at=SUBMITTED_AT,
                actor_id="different-server-actor",
            )
        assert (exc_info.value.code, exc_info.value.status_code) == (
            "LIFECYCLE_IDEMPOTENCY_CONFLICT",
            409,
        )
        transaction.rollback()

    with session_factory() as transaction:
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == seeded["case_id"])
            )
            == 2
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == seeded["case_id"])
            )
            == 3
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(OfficialWorkPackageChecklist)
                .where(
                    OfficialWorkPackageChecklist.package_id == seeded["package_id"],
                    OfficialWorkPackageChecklist.item_code
                    == "EXTERNAL_SUBMISSION_RECORDED",
                )
            )
            == 1
        )


def test_lifecycle_failure_rolls_back_document_and_checklist_writes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.modules.official_workflows.service as service

    seeded = _seed_filing_evidence(session_factory, marker="rollback")
    with session_factory() as transaction:
        commit_count = 0

        def reject_commit() -> None:
            nonlocal commit_count
            commit_count += 1

        def fail_lifecycle(*_args: object, **_kwargs: object) -> None:
            raise RuntimeError("injected lifecycle failure")

        monkeypatch.setattr(transaction, "commit", reject_commit)
        monkeypatch.setattr(service, "apply_lifecycle_event", fail_lifecycle)

        with pytest.raises(RuntimeError, match="injected lifecycle failure"):
            service.record_filing_preparation_external_operation(
                transaction,
                package_id=seeded["package_id"],
                operation_code="EXTERNAL_SUBMISSION_RECORDED",
                occurred_at=SUBMITTED_AT,
                actor_id="server-actor",
            )
        assert commit_count == 0

    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
        case = transaction.get(Case, seeded["case_id"])
        assert version is not None
        assert case is not None
        assert version.final_submitted_at is None
        assert case.status == "NOT_FILED"
        assert case.lifecycle_revision == 0
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == seeded["case_id"])
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(OfficialWorkPackageChecklist)
                .where(OfficialWorkPackageChecklist.package_id == seeded["package_id"])
            )
            == 0
        )


def test_document_only_replay_fails_closed_without_completing_partial_state(
    session_factory: sessionmaker[Session],
) -> None:
    from app.modules.official_workflows.service import (
        record_filing_preparation_external_operation,
    )

    seeded = _seed_filing_evidence(session_factory, marker="document-only")
    adapter_key = f"filing-external:{seeded['package_id']}:{SUBMITTED_AT.isoformat()}"
    with session_factory() as transaction:
        finalize_external_submission(
            FinalizeExternalSubmissionCommand(
                case_id=seeded["case_id"],
                evidence_version_id=seeded["version_id"],
                actor_id="server-actor",
                submitted_at=SUBMITTED_AT,
                idempotency_key=adapter_key,
            ),
            transaction,
        )
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            record_filing_preparation_external_operation(
                transaction,
                package_id=seeded["package_id"],
                operation_code="EXTERNAL_SUBMISSION_RECORDED",
                occurred_at=SUBMITTED_AT,
                actor_id="server-actor",
            )
        assert (exc_info.value.code, exc_info.value.status_code) == (
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
        )
        transaction.rollback()

    with session_factory() as transaction:
        case = transaction.get(Case, seeded["case_id"])
        assert case is not None
        assert case.status == "NOT_FILED"
        assert case.lifecycle_revision == 1
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == seeded["case_id"])
            )
            == 1
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(OfficialWorkPackageChecklist)
                .where(OfficialWorkPackageChecklist.package_id == seeded["package_id"])
            )
            == 0
        )
