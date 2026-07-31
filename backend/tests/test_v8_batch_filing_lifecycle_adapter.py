from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

import app.modules.cases.service as case_service
from app.core.errors import BusinessError
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_workflow_service import (
    FinalizeExternalSubmissionCommand,
    finalize_external_submission,
)
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)
from app.modules.tasks.models import Task

SUBMITTED_DATE = date(2026, 7, 18)
SUBMITTED_AT = datetime(2026, 7, 18)
ACTOR_ID = "batch-filing-actor"
CREATOR_ID = "evidence-creator"
REVIEWER_ID = "evidence-reviewer"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _seed_case_evidence(
    transaction: Session,
    *,
    marker: str,
    role: str = "SUBMITTED_XML",
    bad_manifest_hash: bool = False,
) -> dict[str, str]:
    case_id = str(uuid4())
    document_id = str(uuid4())
    attachment_id = str(uuid4())
    version_id = str(uuid4())
    package_id = str(uuid4())
    content_hash = f"sha256:{hashlib.sha256(marker.encode()).hexdigest()}"
    reviewed_at = datetime(2026, 7, 17, 9, len(marker))
    lineage_key = f"filing-{marker}"

    transaction.add(
        Case(
            id=case_id,
            case_no=f"V8-BATCH-{marker}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="批量递交生命周期证据适配测试案件",
            status="NOT_FILED",
            business_stage="FILING_PREPARATION",
            official_procedure_stage="NOT_SUBMITTED",
            legal_status="NOT_ESTABLISHED",
            lifecycle_revision=0,
            lifecycle_verification_status="CONFIRMED",
            recv_date=date(2026, 7, 1),
            has_exam_request=False,
            no_power=True,
        )
    )
    transaction.add(
        Document(
            id=document_id,
            case_id=case_id,
            doc_type="OFFICIAL_OUT",
            direction="OUT",
            title=f"最终递交证据-{marker}",
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
            role=role,
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
            content_hash=(f"sha256:{'f' * 64}" if bad_manifest_hash else content_hash),
            present=True,
        )
    )
    transaction.commit()
    return {
        "case_id": case_id,
        "package_id": package_id,
        "version_id": version_id,
        "content_hash": content_hash,
        "reviewed_at": reviewed_at.isoformat(),
        "lineage_key": lineage_key,
        "role": role,
    }


def _allow_material_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_service,
        "_evaluate_batch_final_material_gate",
        lambda _transaction, _case: SimpleNamespace(hard_block=False),
    )


def _execute(
    transaction: Session,
    case_ids: list[str],
    *,
    generate_list: bool = True,
) -> object:
    return case_service.execute_batch_filing(
        transaction,
        selected_case_ids=case_ids,
        submitted_date=SUBMITTED_DATE,
        apply_exam_now=True,
        generate_list=generate_list,
        user_id=ACTOR_ID,
    )


def _activity(
    transaction: Session,
    *,
    case_id: str,
    activity_type: str,
) -> CaseActivityEvent:
    return transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.activity_type == activity_type,
        )
    )


def test_batch_filing_uses_exact_evidence_and_lifecycle_seams_in_stable_deduplicated_order(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        first = _seed_case_evidence(transaction, marker="first", role="OFFICIAL_FINAL_PDF")
        second = _seed_case_evidence(transaction, marker="second")
        commit_count = 0
        original_commit = transaction.commit

        def counted_commit() -> None:
            nonlocal commit_count
            commit_count += 1
            original_commit()

        monkeypatch.setattr(transaction, "commit", counted_commit)
        result = _execute(
            transaction,
            [second["case_id"], first["case_id"], second["case_id"]],
        )

        assert commit_count == 1
        assert result.updated_case_ids == [second["case_id"], first["case_id"]]
        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.document_ids) == 2
        assert len(result.created_task_ids) == 2

    with session_factory() as transaction:
        for seeded in (second, first):
            case_id = seeded["case_id"]
            case = transaction.get(Case, case_id)
            assert case is not None
            assert case.status == "WAITING_RECEIPT"
            assert case.business_stage == "WAITING_EXTERNAL_RECEIPT"
            assert case.official_procedure_stage == "SUBMITTED_WAITING_RECEIPT"
            assert case.legal_status == "NOT_ESTABLISHED"
            assert case.lifecycle_verification_status == "CONFIRMED"
            assert case.lifecycle_revision == 2
            assert case.submitted_date == SUBMITTED_DATE
            assert case.has_exam_request is True
            assert case.updated_by == ACTOR_ID

            version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
            assert version is not None
            assert version.final_submitted_at == SUBMITTED_AT

            document_activity = _activity(
                transaction,
                case_id=case_id,
                activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            )
            assert document_activity is not None
            assert document_activity.sequence == 1
            assert document_activity.actor_id == ACTOR_ID
            assert document_activity.reviewer_id == REVIEWER_ID
            assert document_activity.effective_at == SUBMITTED_AT
            assert document_activity.occurred_at == SUBMITTED_AT
            assert document_activity.idempotency_key == (
                f"document-external-submission:batch-filing:{case_id}:{SUBMITTED_DATE.isoformat()}"
            )
            expected_payload = {
                "evidence_version_id": seeded["version_id"],
                "lineage_key": seeded["lineage_key"],
                "role": seeded["role"],
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
                case_id,
                "DOCUMENT_EVIDENCE_VERSION",
                "DocumentEvidenceVersion",
                seeded["version_id"],
                seeded["content_hash"],
                SUBMITTED_AT,
            )

            snapshot = {
                "activity_id": document_activity.id,
                "activity_type": "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
                "actor_id": ACTOR_ID,
                "case_id": case_id,
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
            snapshot_hash = (
                "sha256:" + hashlib.sha256(_canonical_json(snapshot).encode("utf-8")).hexdigest()
            )

            lifecycle_activity = _activity(
                transaction,
                case_id=case_id,
                activity_type="FILING_EXTERNAL_SUBMISSION_RECORDED",
            )
            assert lifecycle_activity is not None
            assert lifecycle_activity.sequence == 2
            assert lifecycle_activity.actor_id == ACTOR_ID
            assert lifecycle_activity.effective_at == SUBMITTED_AT
            assert lifecycle_activity.occurred_at == SUBMITTED_AT
            assert lifecycle_activity.idempotency_key == (
                f"batch-filing-lifecycle:{case_id}:{SUBMITTED_DATE.isoformat()}"
            )
            assert lifecycle_activity.payload_json == "{}"

            lifecycle_evidence = transaction.scalars(
                select(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.activity_id == lifecycle_activity.id)
                .order_by(CaseActivityEventEvidence.evidence_kind)
            ).all()
            assert len(lifecycle_evidence) == 2
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
                    case_id,
                    "FINAL_SUBMISSION_VERSION",
                    "DocumentEvidenceVersion",
                    seeded["version_id"],
                    seeded["content_hash"],
                    datetime.fromisoformat(seeded["reviewed_at"]),
                ),
                (
                    case_id,
                    "MANUAL_EXTERNAL_SUBMISSION_RECORD",
                    "CaseActivityEvent",
                    document_activity.id,
                    snapshot_hash,
                    SUBMITTED_AT,
                ),
            ]


def test_exact_replay_reuses_activities_and_creates_no_duplicate_side_effects(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        seeded = _seed_case_evidence(transaction, marker="replay")
        first = _execute(transaction, [seeded["case_id"]])
        replay = _execute(transaction, [seeded["case_id"], seeded["case_id"]])

        assert first.success_count == replay.success_count == 1
        assert replay.updated_case_ids == [seeded["case_id"]]
        assert replay.document_ids == []
        assert replay.created_task_ids == []

    with session_factory() as transaction:
        case_id = seeded["case_id"]
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            )
            == 2
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == case_id)
            )
            == 3
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(Document)
                .where(
                    Document.case_id == case_id,
                    Document.title == f"批量递交清单-{SUBMITTED_DATE.isoformat()}",
                )
            )
            == 1
        )
        assert (
            transaction.scalar(
                select(func.count()).select_from(Task).where(Task.case_id == case_id)
            )
            == 1
        )


def test_document_replay_without_lifecycle_state_fails_without_new_writes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        seeded = _seed_case_evidence(transaction, marker="document-only")
        finalize_external_submission(
            FinalizeExternalSubmissionCommand(
                case_id=seeded["case_id"],
                evidence_version_id=seeded["version_id"],
                actor_id=ACTOR_ID,
                submitted_at=SUBMITTED_AT,
                idempotency_key=(f"batch-filing:{seeded['case_id']}:{SUBMITTED_DATE.isoformat()}"),
            ),
            transaction,
        )
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            _execute(transaction, [seeded["case_id"]])

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
        )
        transaction.rollback()

    with session_factory() as transaction:
        case_id = seeded["case_id"]
        case = transaction.get(Case, case_id)
        version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
        assert case is not None
        assert version is not None
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.lifecycle_revision,
        ) == (
            "NOT_FILED",
            "FILING_PREPARATION",
            "NOT_SUBMITTED",
            "NOT_ESTABLISHED",
            "CONFIRMED",
            1,
        )
        assert version.final_submitted_at == SUBMITTED_AT
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            )
            == 1
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == case_id)
            )
            == 1
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(Document)
                .where(
                    Document.case_id == case_id,
                    Document.title == f"批量递交清单-{SUBMITTED_DATE.isoformat()}",
                )
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count()).select_from(Task).where(Task.case_id == case_id)
            )
            == 0
        )


def test_waiting_receipt_projection_without_exact_replay_fails_without_new_writes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        seeded = _seed_case_evidence(transaction, marker="projection-only")
        case = transaction.get(Case, seeded["case_id"])
        assert case is not None
        case.status = "WAITING_RECEIPT"
        case.business_stage = "WAITING_EXTERNAL_RECEIPT"
        case.official_procedure_stage = "SUBMITTED_WAITING_RECEIPT"
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            _execute(transaction, [seeded["case_id"]])

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
        )
        transaction.rollback()

    with session_factory() as transaction:
        case_id = seeded["case_id"]
        case = transaction.get(Case, case_id)
        version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
        assert case is not None
        assert version is not None
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_verification_status,
            case.lifecycle_revision,
        ) == (
            "WAITING_RECEIPT",
            "WAITING_EXTERNAL_RECEIPT",
            "SUBMITTED_WAITING_RECEIPT",
            "NOT_ESTABLISHED",
            "CONFIRMED",
            0,
        )
        assert version.final_submitted_at is None
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == case_id)
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(Document)
                .where(
                    Document.case_id == case_id,
                    Document.title == f"批量递交清单-{SUBMITTED_DATE.isoformat()}",
                )
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count()).select_from(Task).where(Task.case_id == case_id)
            )
            == 0
        )


def test_later_provenance_failure_rolls_back_the_whole_batch(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        first = _seed_case_evidence(transaction, marker="rollback-first")
        second = _seed_case_evidence(
            transaction,
            marker="rollback-second",
            bad_manifest_hash=True,
        )

        with pytest.raises(BusinessError) as exc_info:
            _execute(transaction, [first["case_id"], second["case_id"]])

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "FILING_FINAL_EVIDENCE_CONFLICT",
            409,
        )
        transaction.rollback()

    with session_factory() as transaction:
        for seeded in (first, second):
            case = transaction.get(Case, seeded["case_id"])
            version = transaction.get(DocumentEvidenceVersion, seeded["version_id"])
            assert case is not None
            assert version is not None
            assert case.status == "NOT_FILED"
            assert case.submitted_date is None
            assert case.has_exam_request is False
            assert case.lifecycle_revision == 0
            assert version.final_submitted_at is None
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
                    .select_from(Document)
                    .where(
                        Document.case_id == seeded["case_id"],
                        Document.title == f"批量递交清单-{SUBMITTED_DATE.isoformat()}",
                    )
                )
                == 0
            )
            assert (
                transaction.scalar(
                    select(func.count()).select_from(Task).where(Task.case_id == seeded["case_id"])
                )
                == 0
            )


def test_replay_rejects_changed_document_activity_provenance_without_new_writes(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _allow_material_gate(monkeypatch)
    with session_factory() as transaction:
        seeded = _seed_case_evidence(transaction, marker="provenance")
        _execute(transaction, [seeded["case_id"]], generate_list=False)
        activity = _activity(
            transaction,
            case_id=seeded["case_id"],
            activity_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
        )
        assert activity is not None
        payload = json.loads(activity.payload_json)
        payload["submitted_at"] = datetime(2026, 7, 19).isoformat()
        activity.payload_json = _canonical_json(payload)
        transaction.commit()

        with pytest.raises(BusinessError) as exc_info:
            _execute(transaction, [seeded["case_id"]], generate_list=False)

        assert (exc_info.value.code, exc_info.value.status_code) == (
            "FILING_FINAL_EVIDENCE_CONFLICT",
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
