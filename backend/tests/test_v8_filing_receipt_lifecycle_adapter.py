from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
    OfficialWorkPackageReceipt,
)

EXTERNAL_PATH = "/api/v1/official-work-packages/{package_id}/filing-preparation/external-operations"
RECEIPT_PATH = "/api/v1/official-work-packages/{package_id}/receipts"
SUBMITTED_AT = datetime(2026, 7, 18, 10, 0)
RECEIVED_AT = datetime(2026, 7, 18, 11, 0)
FINAL_HASH = f"sha256:{'a' * 64}"
RECEIPT_BYTES = b"Task66 archived filing receipt evidence"
RECEIPT_HASH = f"sha256:{hashlib.sha256(RECEIPT_BYTES).hexdigest()}"


def _seed_filing_package(
    session_factory: sessionmaker,
    tmp_path: Path,
) -> tuple[str, str, str, str]:
    case_id = str(uuid4())
    package_id = str(uuid4())
    final_document_id = str(uuid4())
    final_attachment_id = str(uuid4())
    version_id = str(uuid4())
    receipt_document_id = str(uuid4())
    receipt_attachment_id = str(uuid4())
    receipt_file = tmp_path / "filing-receipt.pdf"
    receipt_file.write_bytes(RECEIPT_BYTES)
    lineage_key = "filing-final-submission"

    with session_factory() as transaction:
        transaction.add(
            Case(
                id=case_id,
                case_no=f"V8-FILING-RECEIPT-{uuid4().hex[:8].upper()}",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="归档回执生命周期适配测试案件",
                status="NOT_FILED",
                business_stage="FILING_PREPARATION",
                official_procedure_stage="NOT_SUBMITTED",
                legal_status="NOT_ESTABLISHED",
                lifecycle_revision=0,
                lifecycle_verification_status="CONFIRMED",
            )
        )
        transaction.flush()
        transaction.add_all(
            [
                Document(id=final_document_id, case_id=case_id, direction="OUT"),
                Document(id=receipt_document_id, case_id=case_id, direction="IN"),
            ]
        )
        transaction.flush()
        transaction.add_all(
            [
                DocAttachment(
                    id=final_attachment_id,
                    document_id=final_document_id,
                    file_name="filing-final.docx",
                    file_path="/evidence/filing-final.docx",
                    content_hash=FINAL_HASH,
                ),
                DocAttachment(
                    id=receipt_attachment_id,
                    document_id=receipt_document_id,
                    file_name="filing-receipt.pdf",
                    file_path=str(receipt_file),
                    content_hash=RECEIPT_HASH,
                ),
            ]
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=version_id,
                case_id=case_id,
                document_id=final_document_id,
                attachment_id=final_attachment_id,
                lineage_key=lineage_key,
                role="FILING_FULL_WORD",
                version_number=1,
                state="FINAL",
                creator_id="filing-evidence-creator",
                review_state="APPROVED",
                reviewer_id="filing-evidence-reviewer",
                reviewed_at=datetime(2026, 7, 18, 9, 0),
                content_hash=FINAL_HASH,
                current_identity_key=f"{case_id}|{lineage_key}",
            )
        )
        transaction.add(
            OfficialWorkPackage(
                id=package_id,
                case_id=case_id,
                package_kind="FILING_PREP",
                status="READY_FOR_EXTERNAL_SUBMIT",
                resolve_key=f"FILING_PREP:{case_id}",
            )
        )
        transaction.flush()
        transaction.add(
            OfficialWorkPackageManifest(
                package_id=package_id,
                attachment_id=final_attachment_id,
                evidence_version_id=version_id,
                content_hash=FINAL_HASH,
                present=True,
            )
        )
        transaction.commit()
    return case_id, package_id, version_id, receipt_attachment_id


def test_archived_filing_receipt_records_exact_lifecycle_evidence(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    case_id, package_id, version_id, receipt_attachment_id = _seed_filing_package(
        session_factory,
        tmp_path,
    )
    submitted = client.post(
        EXTERNAL_PATH.format(package_id=package_id),
        headers=auth_headers,
        json={
            "operation_code": "EXTERNAL_SUBMISSION_RECORDED",
            "occurred_at": SUBMITTED_AT.isoformat(),
        },
    )
    assert submitted.status_code == 200, submitted.text

    receipt_payload = {
        "receipt_kind": "ELECTRONIC_APPLICATION_RECEIPT",
        "receipt_attachment_id": receipt_attachment_id,
        "receiving_case_no": "202607180001",
        "submitter": "流程人员A",
        "received_at": RECEIVED_AT.isoformat(),
        "archive_status": "ARCHIVED",
        "note": "人工下载并上传电子申请回执",
    }
    response = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=receipt_payload,
    )
    replay = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=receipt_payload,
    )

    assert response.status_code == 201, response.text
    assert replay.status_code == 201, replay.text
    receipt_id = response.json()["id"]
    assert replay.json()["id"] == receipt_id
    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        case = transaction.get(Case, case_id)
        activity = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case_id,
                CaseActivityEvent.idempotency_key == f"filing-receipt-archived:{receipt_id}",
            )
        )
        assert actor_id is not None
        assert case is not None
        assert activity is not None
        assert activity.sequence == 3
        assert activity.lane == "LIFECYCLE"
        assert activity.activity_type == "FILING_RECEIPT_ARCHIVED"
        assert activity.confirmation_status == "CONFIRMED"
        assert activity.actor_id == actor_id
        assert activity.effective_at == activity.occurred_at == RECEIVED_AT
        assert (
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
        ) == (
            "WAITING_EXTERNAL_RECEIPT",
            "PROSECUTION_MANAGEMENT",
            "SUBMITTED_WAITING_RECEIPT",
            "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE",
            "NOT_ESTABLISHED",
            "APPLICATION_PENDING",
        )
        evidence = transaction.scalars(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == activity.id)
            .order_by(CaseActivityEventEvidence.evidence_kind)
        ).all()
        assert [
            (
                row.evidence_kind,
                row.object_type,
                row.object_id,
                row.content_hash,
                row.captured_at,
            )
            for row in evidence
        ] == [
            (
                "FINAL_SUBMISSION_VERSION",
                "DocumentEvidenceVersion",
                version_id,
                FINAL_HASH,
                datetime(2026, 7, 18, 9, 0),
            ),
            (
                "VALID_FILING_RECEIPT",
                "OfficialWorkPackageReceipt",
                receipt_id,
                RECEIPT_HASH,
                RECEIVED_AT,
            ),
        ]
        assert case.business_stage == "PROSECUTION_MANAGEMENT"
        assert case.official_procedure_stage == "SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE"
        assert case.legal_status == "APPLICATION_PENDING"
        assert case.status == "WAITING_RECEIPT"
        assert case.lifecycle_revision == 3
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(OfficialWorkPackageReceipt)
                .where(OfficialWorkPackageReceipt.package_id == package_id)
            )
            == 1
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            )
            == 3
        )


def test_receipt_lifecycle_failure_rolls_back_receipt_and_attachment_flags(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.modules.official_workflows.service as service

    case_id, package_id, _version_id, receipt_attachment_id = _seed_filing_package(
        session_factory,
        tmp_path,
    )
    submitted = client.post(
        EXTERNAL_PATH.format(package_id=package_id),
        headers=auth_headers,
        json={
            "operation_code": "EXTERNAL_SUBMISSION_RECORDED",
            "occurred_at": SUBMITTED_AT.isoformat(),
        },
    )
    assert submitted.status_code == 200, submitted.text

    def fail_lifecycle(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("injected filing receipt lifecycle failure")

    monkeypatch.setattr(service, "apply_lifecycle_event", fail_lifecycle)
    response = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json={
            "receipt_kind": "ELECTRONIC_APPLICATION_RECEIPT",
            "receipt_attachment_id": receipt_attachment_id,
            "received_at": RECEIVED_AT.isoformat(),
            "archive_status": "ARCHIVED",
        },
    )

    assert response.status_code == 500, response.text
    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        attachment = transaction.get(DocAttachment, receipt_attachment_id)
        assert case is not None
        assert attachment is not None
        assert case.business_stage == "WAITING_EXTERNAL_RECEIPT"
        assert case.lifecycle_revision == 2
        assert attachment.is_archive_evidence is False
        assert attachment.is_receipt_evidence is False
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(OfficialWorkPackageReceipt)
                .where(OfficialWorkPackageReceipt.package_id == package_id)
            )
            == 0
        )


def _submit_and_archive_filing_receipt(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    package_id: str,
    receipt_attachment_id: str,
) -> dict[str, object]:
    submitted = client.post(
        EXTERNAL_PATH.format(package_id=package_id),
        headers=auth_headers,
        json={
            "operation_code": "EXTERNAL_SUBMISSION_RECORDED",
            "occurred_at": SUBMITTED_AT.isoformat(),
        },
    )
    assert submitted.status_code == 200, submitted.text
    payload: dict[str, object] = {
        "receipt_kind": "ELECTRONIC_APPLICATION_RECEIPT",
        "receipt_attachment_id": receipt_attachment_id,
        "received_at": RECEIVED_AT.isoformat(),
        "archive_status": "ARCHIVED",
    }
    archived = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=payload,
    )
    assert archived.status_code == 201, archived.text
    return payload


def test_receipt_replay_rejects_stale_manual_submission_activity_link(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    case_id, package_id, _version_id, receipt_attachment_id = _seed_filing_package(
        session_factory,
        tmp_path,
    )
    payload = _submit_and_archive_filing_receipt(
        client,
        auth_headers,
        package_id=package_id,
        receipt_attachment_id=receipt_attachment_id,
    )
    with session_factory() as transaction:
        finalized = transaction.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case_id,
                CaseActivityEvent.activity_type
                == "DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
            )
        )
        assert finalized is not None
        finalized.actor_id = "different-valid-actor"
        transaction.commit()

    replay = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=payload,
    )
    assert replay.status_code == 409, replay.text


def test_receipt_replay_rejects_corrupt_current_case_projection(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    case_id, package_id, _version_id, receipt_attachment_id = _seed_filing_package(
        session_factory,
        tmp_path,
    )
    payload = _submit_and_archive_filing_receipt(
        client,
        auth_headers,
        package_id=package_id,
        receipt_attachment_id=receipt_attachment_id,
    )
    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        assert case is not None
        case.legal_status = "NOT_ESTABLISHED"
        transaction.commit()

    replay = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=payload,
    )
    assert replay.status_code == 409, replay.text


def test_receipt_replay_rejects_and_does_not_repair_cleared_attachment_flags(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    tmp_path: Path,
) -> None:
    _case_id, package_id, _version_id, receipt_attachment_id = _seed_filing_package(
        session_factory,
        tmp_path,
    )
    payload = _submit_and_archive_filing_receipt(
        client,
        auth_headers,
        package_id=package_id,
        receipt_attachment_id=receipt_attachment_id,
    )
    with session_factory() as transaction:
        attachment = transaction.get(DocAttachment, receipt_attachment_id)
        assert attachment is not None
        attachment.is_archive_evidence = False
        attachment.is_receipt_evidence = False
        transaction.commit()

    replay = client.post(
        RECEIPT_PATH.format(package_id=package_id),
        headers=auth_headers,
        json=payload,
    )
    assert replay.status_code == 409, replay.text
    with session_factory() as transaction:
        attachment = transaction.get(DocAttachment, receipt_attachment_id)
        assert attachment is not None
        assert attachment.is_archive_evidence is False
        assert attachment.is_receipt_evidence is False
