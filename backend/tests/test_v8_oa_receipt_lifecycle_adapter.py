from __future__ import annotations

import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker
from test_addgap_oa_receipt_archive_event import (
    _archive,
    _create_archive_fixture,
)

from app.modules.auth.models import T_User
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageReceipt,
)
from app.modules.tasks.models import Task, TaskLog


def _set_oa_response_projection(
    session_factory: sessionmaker,
    *,
    case_id: str,
) -> None:
    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        assert case is not None
        case.business_stage = "OA_REPLY_IN_PROGRESS"
        case.official_procedure_stage = "OFFICE_ACTION_RESPONSE"
        case.legal_status = "APPLICATION_PENDING"
        case.lifecycle_revision = 0
        case.lifecycle_verification_status = "CONFIRMED"
        transaction.commit()


def _receipt_content_hash(receipt: OfficialWorkPackageReceipt) -> str:
    snapshot = {
        "archive_status": receipt.archive_status,
        "id": receipt.id,
        "note": receipt.note,
        "package_id": receipt.package_id,
        "received_at": receipt.received_at.isoformat() if receipt.received_at else None,
        "received_file_list": receipt.received_file_list,
        "receipt_attachment_id": receipt.receipt_attachment_id,
        "receipt_kind": receipt.receipt_kind,
        "receiving_case_no": receipt.receiving_case_no,
        "submitter": receipt.submitter,
    }
    canonical = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def test_archive_calls_oa_receipt_lifecycle_once_and_closes_exact_task_once(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    ids = _create_archive_fixture(session_factory)
    _set_oa_response_projection(
        session_factory,
        case_id=ids["case_id"],
    )

    created = _archive(client, auth_headers, ids["package_id"])
    replayed = _archive(client, auth_headers, ids["package_id"])

    assert created.status_code == 200, created.text
    assert replayed.status_code == 200, replayed.text
    with session_factory() as transaction:
        case = transaction.get(Case, ids["case_id"])
        package = transaction.get(OfficialWorkPackage, ids["package_id"])
        receipt = transaction.get(OfficialWorkPackageReceipt, ids["receipt_id"])
        matched_task = transaction.get(Task, ids["matching_task_ids"][0])
        decoy_task = transaction.get(Task, ids["decoy_task_id"])
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert case is not None
        assert package is not None
        assert receipt is not None
        assert matched_task is not None
        assert decoy_task is not None
        assert actor_id is not None

        activities = transaction.scalars(
            select(CaseActivityEvent).where(
                CaseActivityEvent.case_id == case.id,
                CaseActivityEvent.activity_type == "OA_RECEIPT_ARCHIVED",
            )
        ).all()
        assert len(activities) == 1
        activity = activities[0]
        assert (
            activity.sequence,
            activity.lane,
            activity.confirmation_status,
            activity.actor_id,
            activity.idempotency_key,
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
            activity.payload_json,
        ) == (
            1,
            "LIFECYCLE",
            "CONFIRMED",
            actor_id,
            f"oa-receipt-archived:{receipt.id}",
            "OA_REPLY_IN_PROGRESS",
            "PROSECUTION_MANAGEMENT",
            "OFFICE_ACTION_RESPONSE",
            "SUBSTANTIVE_EXAMINATION",
            "APPLICATION_PENDING",
            "APPLICATION_PENDING",
            "{}",
        )
        evidence = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert len(evidence) == 1
        assert (
            evidence[0].case_id,
            evidence[0].evidence_kind,
            evidence[0].object_type,
            evidence[0].object_id,
            evidence[0].content_hash,
            evidence[0].captured_at,
        ) == (
            case.id,
            "OA_RECEIPT",
            "OfficialWorkPackageReceipt",
            receipt.id,
            _receipt_content_hash(receipt),
            receipt.created_at,
        )

        assert package.status == "ARCHIVED"
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
            case.lifecycle_verification_status,
        ) == (
            "SUB_EXAM",
            "PROSECUTION_MANAGEMENT",
            "SUBSTANTIVE_EXAMINATION",
            "APPLICATION_PENDING",
            1,
            "CONFIRMED",
        )
        assert matched_task.status == "DONE"
        assert matched_task.done_at is not None
        assert decoy_task.status == "OPEN"
        assert decoy_task.done_at is None
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(TaskLog)
                .where(
                    TaskLog.task_id == matched_task.id,
                    TaskLog.action == "CLOSE",
                )
            )
            == 1
        )


def test_lifecycle_failure_rolls_back_task_case_package_and_activity(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.modules.official_workflows.service as service

    ids = _create_archive_fixture(session_factory)
    _set_oa_response_projection(
        session_factory,
        case_id=ids["case_id"],
    )

    def fail_lifecycle(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("injected OA receipt lifecycle failure")

    monkeypatch.setattr(
        service,
        "apply_lifecycle_event",
        fail_lifecycle,
        raising=False,
    )

    response = _archive(client, auth_headers, ids["package_id"])

    assert response.status_code == 500, response.text
    with session_factory() as transaction:
        case = transaction.get(Case, ids["case_id"])
        package = transaction.get(OfficialWorkPackage, ids["package_id"])
        matched_task = transaction.get(Task, ids["matching_task_ids"][0])
        assert case is not None
        assert package is not None
        assert matched_task is not None
        assert package.status == "WAITING_RECEIPT"
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
            case.lifecycle_verification_status,
        ) == (
            ids["case_initial_status"],
            "OA_REPLY_IN_PROGRESS",
            "OFFICE_ACTION_RESPONSE",
            "APPLICATION_PENDING",
            0,
            "CONFIRMED",
        )
        assert matched_task.status == "OPEN"
        assert matched_task.done_at is None
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(TaskLog)
                .where(
                    TaskLog.task_id == matched_task.id,
                    TaskLog.action == "CLOSE",
                )
            )
            == 0
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case.id)
            )
            == 0
        )
